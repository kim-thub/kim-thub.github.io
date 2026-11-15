# Spring Boot로 쿠폰 발급의 잠금 대기를 추적한 경량 APM

쿠폰 발급 요청의 HTTP 응답 시간만으로는 애플리케이션 처리와 PostgreSQL 잠금 대기를 구분하기 어렵습니다. `HandlerInterceptor`로 요청을 추적하고, 느린 요청의 JVM 스택과 PostgreSQL의 잠금 상태를 각각 확인했습니다.

2026년 11월 10일 잠금 테스트에서는 요청 시작 541 ms 뒤에 `MONITOR` 스택을 수집했습니다. X-View에는 578 ms의 처리 시간이 기록됐고, PostgreSQL에서는 `wait_event_type=Lock`을 관찰했습니다.

세 값은 같은 잠금 테스트에서 각각 확인한 근거입니다. Java 추적 ID와 PostgreSQL PID를 자동으로 연결하지 않았으며, 스택만으로 DB 잠금 대기 시간을 계산하지도 않았습니다.

> **검증 범위:** `coupon-apm-lab-apm-review.zip`에 포함된 공개 검증 소스 244개 파일과 보존된 측정 자료를 바탕으로 작성했습니다. 코드 예시는 구현과 검증 범위를 설명하는 데 필요한 두 곳만 남겼습니다. 이 글을 다듬으면서 Java 빌드와 DB 통합 테스트를 다시 실행하지 않았으며, 기록된 2026년 11월 10일 결과를 인용합니다.

## 이 APM이 구분한 관측값

| 관측값 | 무엇을 나타내나 | 이 값만으로 알 수 없는 것 |
|---|---|---|
| `elapsedMs` | `HandlerInterceptor`가 측정한 Spring MVC Handler 처리 시간 | 네트워크를 포함한 전체 HTTP 지연 시간 |
| `SlowTrace` | 임계 시간을 넘긴 요청의 특정 시점 JVM 스레드 스택 | SQL별 실행 시간이나 정확한 DB 잠금 대기 시간 |
| X-View | 완료 요청 한 건의 Handler 처리 시간과 시작 시각, HTTP 상태 | 장기 보관된 전체 요청 이력 |
| Locust p95 | HTTP 201 응답 시간의 95백분위수 | APM 내부 Handler 처리 시간과 같은 측정 구간 |
| 성공 TPS | 60초 동안 DB에 정상 커밋된 쿠폰 발급 건수 ÷ 60초 | 단순 HTTP 응답 수 기준의 처리량 |

## 1. 어떤 요청을 계측했나

쿠폰 발급 요청의 시작과 종료를 같은 추적 ID로 연결하는 것이 목표였습니다. 모든 Spring MVC 요청을 계측하면 관측 범위와 비용이 함께 커지므로 `@ApmTrace`가 붙은 Handler만 추적했습니다. 실제 URI 대신 Spring 경로 패턴을 기록해 쿠폰 ID가 달라도 같은 API 요청으로 묶었습니다. 구현은 [ApmInterceptor.java, L17–L26](https://github.com/kim-thub/coupon-apm-lab)에서 확인할 수 있습니다.

`afterCompletion()`은 요청에 저장한 ID로 `tracker.end()`를 호출하고, `finally`에서 request attribute를 정리합니다. APM을 끄면 설정에서 Interceptor 등록을 막습니다. Tracker Bean과 조회 API까지 비활성화하는 설정은 아닙니다.

`elapsedMs`는 Spring MVC Handler 처리 시간입니다. Locust의 전체 HTTP 응답 시간과 측정 구간이 다르므로 두 값을 같은 지표로 비교하지 않았습니다.

## 2. 100 ms 감시 주기의 사각지대를 어떻게 처리했나

`ApmMonitor`는 100 ms 간격의 `fixedDelay` 작업으로 실행 중인 요청을 확인하고, 500 ms 이상 걸린 요청의 스택을 수집합니다. 스택 프레임은 최대 64개로 제한하고 요청을 처리하는 스레드만 샘플링합니다. 수집 실패 여부와 이유, 수집 시점(`MONITOR` 또는 `COMPLETION_FALLBACK`)도 기록합니다.

예를 들어 요청이 490 ms 시점의 감시를 지난 뒤 550 ms에 끝나면 다음 감시 전에 종료될 수 있습니다. 이를 보완하기 위해 `end()`에서도 500 ms 임계값을 확인합니다. 아래 발췌는 종료 시점에 직접 스택을 수집할지, 이미 시작된 수집이 끝날 때까지 기다릴지를 결정하는 부분입니다. [ApmTracker.java, L68–L87](https://github.com/kim-thub/coupon-apm-lab)

```java
public void end(UUID id, int statusCode) {
    ActiveTransaction request = active.get(id);
    if (request == null) return;
    long elapsedNanos = Math.max(0, nanos.getAsLong() - request.startedNanos);
    var action = request.beginCompletion(elapsedNanos >= thresholdNanos);
    if (action == ActiveTransaction.CompletionAction.FALLBACK_CAPTURE) {
        capture(request, "COMPLETION_FALLBACK");
    } else if (action == ActiveTransaction.CompletionAction.WAIT_FOR_CAPTURE) {
        request.captureDone.join(); // 캡처 완료를 기다리는 동안 상태 잠금을 쥐지 않습니다.
    }
    try {
        TransactionSample sample = new TransactionSample(id, request.method, request.route,
                request.startedAt, elapsedNanos / 1_000_000L, statusCode);
        xview.add(sample);
        logJson("APM_TRANSACTION", sample);
    } finally {
        active.remove(id, request);
        request.close(); // 완료된 요청이 처리 스레드를 계속 참조하지 않게 합니다.
    }
}
```

코드의 분기는 감시 작업이 아직 시작되지 않은 경우와 이미 스택을 수집 중인 경우를 구분합니다. `ActiveTransaction`은 요청 생명주기(`ACTIVE → COMPLETING → CLOSED`)와 스택 캡처 상태를 따로 관리하고, 종료 뒤에는 Registry에서 요청을 제거해 처리 스레드의 강한 참조도 해제합니다. 이 예시는 감시 주기 사이에 요청이 끝날 때 보완 캡처가 왜 필요한지 보여줍니다.

경계 테스트에서는 490 ms에 감시를 실행한 뒤 요청을 550 ms에 종료했습니다. 이때 SlowTrace가 `COMPLETION_FALLBACK`으로 한 건 기록되는지 확인했습니다. 감시 주기 사이에 끝난 요청을 종료 시점에 포착한 사례입니다.

## 3. 완료된 요청은 X-View에 어떻게 남겼나

X-View의 점 하나는 요청 한 건을 나타냅니다. X축에는 요청 시작 시각, Y축에는 Spring MVC Handler 처리 시간(ms)을 표시하고 HTTP 상태 코드도 저장합니다. 완료 샘플은 최근 1,000건, SlowTrace는 최근 100건까지만 메모리에 보관합니다. 고정 크기 버퍼는 동시 접근을 동기화하며 조회 시 읽기 전용 복사본을 반환합니다. 메모리 사용량은 제한하지만 영구 보관 기능은 없습니다.

![2026년 11월 10일 요청 19건으로 재생성한 X-View](assets/xview-19-readable.png)

*그림 1. `xview-raw.json`의 요청 19건을 표시했습니다. 위 그래프는 전체 구간, 아래 그래프는 500 ms 미만 요청 18건의 0–40 ms 구간입니다. 두 그래프는 같은 시작 시각 축을 사용하며 원본 값을 바꾸지 않았습니다.*

기존 `xview.png`에는 2026년 11월 9일 실행에서 수집한 623 ms 요청 한 건이 담겨 있습니다. 이 글의 그래프는 11월 10일 실행 자료 19건으로 만들었으며, 그중에는 578 ms 요청이 포함됩니다. 서로 다른 실행의 값은 합치지 않았습니다. 확대 그래프는 보존한 원본 JSON을 별도 시각화 스크립트로 읽어 만들었습니다.

## 4. 실제 PostgreSQL 잠금 대기로 확인하기

JVM 스택만으로 DB 잠금을 단정하지 않도록 별도 DB 연결에서 쿠폰 행을 잠근 뒤, 잠금이 유지되는 동안 실제 HTTP 발급 요청을 보냈습니다. PostgreSQL의 `pg_stat_activity`와 `pg_blocking_pids()`에서 차단 상태를 확인했습니다. `CouponService`는 트랜잭션 연결에 `SET LOCAL lock_timeout = '3s'`를 적용합니다. 잠금 획득에 실패하면 HTTP 503 `COUPON_LOCK_TIMEOUT`을 반환합니다.

테스트는 `Thread.sleep()`으로 지연을 흉내 내지 않고 실제 DB에서 이 메서드가 조회하는 쿠폰 행을 잠급니다. [CouponRepository.java, L11–L13](https://github.com/kim-thub/coupon-apm-lab)

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("select c from Coupon c where c.id = :id")
Optional<Coupon> findLockedById(@Param("id") Long id);
```

이 선언은 발급 트랜잭션이 실제 쿠폰 행의 비관적 쓰기 잠금을 요청하게 합니다. 테스트의 별도 연결이 같은 행을 잠근 상태에서 요청을 보내므로, 관측한 대기가 PostgreSQL 잠금에서 비롯됐는지 확인할 수 있습니다.

2026년 11월 10일에 보존한 테스트 자료에서 다음 값을 확인했습니다.

| 확인 항목 | 관측값 |
|---|---|
| 요청 | `POST /api/coupons/{couponId}/issues` |
| 시작 시각 (UTC) | `2026-11-10T04:14:56.329343Z` |
| SlowTrace | `MONITOR`, 요청 시작 541 ms 뒤 |
| X-View | 578 ms, HTTP 201 |
| PostgreSQL | `wait_event_type=Lock`, `wait_event=transactionid` |
| PID | 차단 PID 124, 대기 PID 104 |

같은 테스트의 SlowTrace에는 JDBC 결과를 기다리는 호출이 관찰됐습니다. 대표 프레임은 `QueryExecutorImpl.processResults → PgPreparedStatement.executeQuery → DeferredResultSetAccess.executeQuery → CouponService.issueCoupon` 순서입니다. 이 프레임 목록은 `stackFrames`에서 필요한 항목만 골랐으며, 연속된 스택 구간은 아닙니다.

이 자료에서는 실제 DB 잠금 대기와 요청 처리 중의 JDBC 대기 호출을 함께 관찰했습니다.

## 5. APM이 응답 시간과 처리량에 준 영향

계측이 응답에 미치는 영향을 살피기 위해 Locust로 APM OFF와 ON을 각각 측정했습니다. 각 실행은 최대 사용자 100명, 초당 10명 증가, 준비 60초, 측정 60초 조건으로 진행했습니다. 실행마다 데이터베이스를 따로 준비했지만 같은 PostgreSQL 인스턴스의 CPU, WAL, I/O를 공유했습니다.

두 지표의 정의를 먼저 고정했습니다.

- **성공 p95:** HTTP 201 응답 시간을 Nearest-Rank 방식으로 계산한 95백분위수입니다.
- **성공 TPS:** 측정한 60초 동안 데이터베이스에 정상 커밋된 발급 건수를 60초로 나눈 값입니다. HTTP 응답 수만 세지 않았습니다.
- **판정:** 유효한 OFF 3회와 ON 3회의 중앙값을 비교했습니다. p95 증가와 성공 TPS 감소가 각각 15% 이하면 목표를 통과합니다.
- **편차:** 같은 모드에서 최댓값 ÷ 최솟값이 1.15를 넘으면 `REVIEW_REQUIRED`로 표시했습니다.

`VALID`는 실행 자료와 조건이 유효하다는 뜻이며, 성능 목표 통과(`PASS`)와는 다른 상태입니다.

![APM OFF와 ON의 HTTP 성공 p95 비교](assets/apm-off-on-p95.png)

*그림 2. 공식 1~3차와 추가 재측정의 HTTP 성공 p95 중앙값입니다.*

![APM OFF와 ON의 성공 TPS 비교](assets/apm-off-on-tps.png)

*그림 3. 같은 배치의 DB 커밋 기반 성공 TPS 중앙값입니다.*

| 구분 | p95 OFF | p95 ON | p95 변화 | 성공 TPS OFF → ON | 목표 판정 | 측정 편차 |
|---|---:|---:|---:|---:|---|---|
| 공식 1차 | 8.337 ms | 6.999 ms | −16.04% | 447.50 → 451.45 | PASS | REVIEW_REQUIRED |
| 공식 2차 | 5.582 ms | 22.872 ms | **+309.71%** | 451.67 → 445.90 | **FAIL** | REVIEW_REQUIRED |
| 공식 3차 | 5.340 ms | 5.399 ms | +1.11% | 452.13 → 454.00 | PASS | REVIEW_REQUIRED |
| 추가 재측정 | 5.004 ms | 4.543 ms | −9.21% | 452.55 → 454.78 | PASS | REVIEW_REQUIRED |

![공식 2차의 6회 p95 측정](assets/batch2-p95-runs.png)

*그림 4. 공식 2차의 ON 2회차와 6회차 p95가 약 23ms까지 상승했습니다.*

공식 2차 실험 자료는 유효했지만 성능 목표는 통과하지 못했습니다. OFF 3회의 p95는 약 5.3–5.6 ms였고, ON 3회 중 두 번은 약 23 ms, 한 번은 약 9.5 ms였습니다. 성공 TPS 변화는 비교적 작았지만 p95 꼬리 지연은 크게 늘었습니다. 추가 재측정 결과는 공식 1~3차에 합산하지 않았습니다.

후속 진단에서 동기 로깅과 비동기 로깅의 p95 차이는 0.38%였습니다. 이 결과만으로는 동기 로깅이 지연 급등의 주원인이라는 가설을 뒷받침할 수 없었습니다. 당시 호스트 전체 CPU 사용률과 다른 프로세스의 영향은 측정하지 않아 원인을 확정하지 못했습니다.

## 6. 테스트로 확인한 범위와 남은 한계

| 테스트 | 확인한 동작 |
|---|---|
| `ApmTrackerTest` | 499 ms와 500 ms 경계, 550 ms 보완 캡처, 중복 캡처 방지, 실패 기록 |
| `ActiveTransactionTest` | 정상, 보완, 실패 캡처 종료 때 `Thread` 참조 해제 |
| `BoundedBufferTest` | X-View 최신 1,000건, SlowTrace 최신 100건, 동시 쓰기와 읽기 |
| `PostgresLockWaitHttpIT` | 실제 PostgreSQL 잠금 대기, `MONITOR` 스택, 3초 타임아웃과 롤백 |
| `ApmEnabledCouponHttpIT`, `ApmDisabledCouponHttpIT` | APM ON/OFF 상태의 HTTP 발급 정합성 |

공개 ZIP의 2026년 11월 10일 기록에는 `./gradlew clean build`의 JUnit 테스트 11건, `./gradlew integrationTest`의 PostgreSQL 통합 테스트 12건, `make test-python`의 Python 테스트 6건이 통과한 것으로 남아 있습니다.

이 글을 다듬는 동안 Java 빌드와 DB 통합 테스트는 다시 실행하지 않았습니다. Python 단위 테스트 6건과 X-View 원본 19건은 Python 변환 및 시각화 스크립트로 다시 확인했습니다.

검증 결과의 범위는 다음과 같습니다.

1. Interceptor는 네트워크 전체 HTTP 지연이 아니라 Spring MVC Handler 구간을 측정합니다.
2. SlowTrace는 특정 시점의 스택 스냅샷이며 SQL별 실행 시간을 계산하지 않습니다.
3. 메모리에는 최근 X-View 1,000건과 SlowTrace 100건만 남습니다. 장기 원본은 로그와 별도 실험 자료에 의존합니다.
4. 실시간 통합 대시보드와 분산 추적은 구현하지 않았습니다.
5. APM OFF/ON 비교에는 실행 환경 편차가 남아 있어 안정적인 성능 수치로 일반화할 수 없습니다.
6. 공개 ZIP에는 요약 비교 JSON과 검증 기록이 있지만 요청별 대용량 CSV와 상세 DB 대조 원본은 포함되지 않습니다. 이 ZIP만으로 요청별 p95를 처음부터 다시 계산했다고 주장하지 않습니다.

## 마치며

이 작업에서는 느린 쿠폰 발급 요청에서 관측한 증거가 실제 DB 잠금 대기와 일치하는지 확인했습니다. 요청 단위 계측, 임계 시간 스택 캡처, PostgreSQL 잠금 상태를 각각 기록하고 측정 구간과 이들 사이의 연결에서 확인하지 못한 점도 함께 남겼습니다.

성능 비교에서는 평균 응답 시간 하나로 결론을 내리지 않았습니다. HTTP 201 응답의 p95와 데이터베이스 커밋 기반 성공 TPS를 따로 보고, 실험 자료의 유효성, 목표 판정, 측정 편차를 구분했습니다. 공식 2차의 목표 미달과 원인을 확정하지 못한 진단도 그대로 기록했습니다.

### 참고 자료

- [ApmInterceptor.java](https://github.com/kim-thub/coupon-apm-lab)
- [ApmTracker.java](https://github.com/kim-thub/coupon-apm-lab)
- [CouponRepository.java](https://github.com/kim-thub/coupon-apm-lab)
- [PostgresLockWaitHttpIT.java](https://github.com/kim-thub/coupon-apm-lab)
- [analysis.py](https://github.com/kim-thub/coupon-apm-lab)
- 기록 기준: 공개 검증 자료, 2026년 11월 10일
