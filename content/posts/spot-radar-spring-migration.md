---
index_order: 5
title: SPOT RADAR의 Spring Boot 마이그레이션과 조회 비용 개선
slug: spot-radar-spring-migration
excerpt: 기존 API 계약을 유지하면서 요청 시간과 SQL 실행 시간을 나눠 측정하고, 상권 기본 정보 조회와 반복 데이터 조회를 줄인 과정입니다.
---

# SPOT RADAR의 Spring Boot 마이그레이션과 조회 비용 개선

SPOT RADAR 팀 프로젝트의 초기 API는 FastAPI로 구현했습니다. 개인 후속 작업에서는 기존 화면과 데이터베이스를 계속 사용할 수 있도록 API 계약을 유지하며 Spring Boot로 옮겼습니다. 응답 지연의 원인을 SQL 실행 시간만으로 단정하지 않고, 요청 처리 구간과 저장소 구간을 나눠 확인했습니다.

팀 프로젝트에서는 서울 Open API 데이터 적재와 upsert, Gemini 인사이트 수치 검증, DB 연결과 예외 처리, 회귀 테스트를 맡았습니다. 설계와 API, 문제 분석을 다룬 Wiki 문서 대부분은 AI의 도움을 받아 제가 작성했습니다. 초기 UI 뼈대에는 Stitch 시안을 바탕으로 Google AI Studio가 생성한 코드가 포함되어 있습니다. 개인 마이그레이션 저장소와 성능 로그는 공개되어 있지 않습니다.

## API 계약을 유지한 마이그레이션

새 API 계약을 만드는 대신 React 화면과 Supabase PostgreSQL 데이터를 계속 사용할 수 있도록 기존 계약을 유지했습니다. 경로와 요청 파라미터, JSON 필드, `null`과 빈 배열의 의미, 분석 점수와 추천 정렬을 그대로 두었습니다.

요청은 React 화면에서 `/api/v1` 계약을 거쳐 Spring MVC, JPA, Native SQL로 이어집니다. Native SQL 결과를 `Object[]` 인덱스로 읽던 부분은 필드 이름으로 접근하는 Projection으로 바꿨습니다. 분기 계산, 퍼센타일, 순위, 숫자 형식은 함수로 분리했습니다. JUnit 5와 Mockito로 계산 경계와 `null` 처리, 응답 구성을 확인했습니다.

## 먼저 요청 시간과 SQL 시간을 분리했습니다

진단 당시 API 평균 응답 시간은 약 30초였지만, Supabase `EXPLAIN ANALYZE`에서 확인한 핵심 SQL 실행 시간은 약 1.27초였습니다. Servlet Filter와 AOP를 사용해 API 전체 시간과 Repository 구간을 나눠 측정했습니다. 이후 대량 데이터 전송과 같은 업종 및 분기의 모집단을 반복 조회하는 흐름을 원인 후보로 좁혔습니다. SQL 실행 시간만으로 전체 응답 지연을 설명하지 않았습니다.

## 상위 후보만 상권 기본 정보를 조회합니다

추천 점수를 계산한 뒤 상위 7개 상권 코드만 `findAllById`에 전달합니다. 저장소에서 확인한 변화는 기본 상권 정보 조회량이 평균 1,650건에서 7건으로 줄어든 점입니다. 지표 계산에 필요한 모집단 조회량까지 7건으로 줄었다는 뜻은 아닙니다. Overview 조회도 필요한 상권만 최대 약 21건 읽도록 제한했습니다.

아래 코드는 점수 계산에 필요한 모집단은 둔 채, 응답에 표시할 기본 상권 정보만 상위 후보로 제한하는 경계를 보여줍니다. `limit(7)` 뒤에 조회가 이어지기 때문에 조회량 감소가 실제 어느 단계에서 생기는지 확인할 수 있습니다.

```java
List<String> topCodes = population.stream()
        .filter(row -> row.explorationScore() != null)
        .sorted(Comparator.comparing((MetricRow row) -> row.explorationScore())
                .reversed()
                .thenComparing(row -> row.tradeAreaCode()))
        .limit(7)
        .map(row -> row.tradeAreaCode())
        .toList();

// 모집단 계산 결과와 상권 기본 정보 조회 범위를 분리합니다.
areaByCode = areas.findAllById(topCodes).stream()
        .collect(Collectors.toMap(
                area -> area.getCode(),
                area -> area));
```

이렇게 점수 계산용 행과 추가 설명을 위해 읽는 상권 기본 정보를 분리했습니다. 따라서 1,650건에서 7건으로 줄어든 값은 기본 정보 조회량이며, 점수 계산에 필요한 모집단 전체가 줄었다는 의미는 아닙니다.

실제 코드: [AnalyticsService.recommendations()](https://github.com/kim-thub/seoul-data-analysis), SalesRepository Projection SQL

| 측정 항목 | 변경 전 | 변경 후 |
|---|---:|---:|
| 기본 추천 상권 정보 조회량 평균 | 1,650건 | 7건 |
| Repository 조회 구간 평균 | 3.73초 | 0.33초 |
| 추천 API 평균 응답 시간, 조회 범위 개선 전후 | 29.7초 | 9.4초 |
| 로컬 추천 API, 캐시 Cold → Hit | 9.055초 | 1.750초 |
| 로컬 Overview, 캐시 Cold → Hit | 4.192초 | 1.570초 |
| Render 배포, 동일 조건 Cold → Hit | 28.013초 | 1.877초 |

조회 범위 개선과 캐시 적용은 서로 다른 단계에서 측정했습니다. 캐시 Cold 응답에는 캐시 미적중 외에 서버 기동과 DB 연결 상태도 영향을 주었을 수 있습니다. 이 응답 시간은 TPS나 동시 처리량을 나타내지 않습니다.

## 메모리 캐시를 택한 이유와 감수한 점

초기 팀 작업에서는 일정이 촉박해 뷰 기반 방식과 Redis 같은 외부 캐시 중 무엇을 적용할지 충분히 검토하고 구현할 시간이 없었습니다. 그 결과 같은 업종과 분기의 데이터를 반복 조회하는 비용이 남았습니다.

개인 마이그레이션을 시작했을 때는 Redis 사용 경험이 많지 않았고, Render 무료 배포 환경에서 변경 범위를 작게 유지하고 싶었습니다. 그래서 Spring Cache의 메모리 구현을 적용했습니다. 실행 로그에서 `ConcurrentMapCacheManager → ConcurrentMapCache → ConcurrentHashMap` 구성을 확인했고, 다섯 분석 API가 별도 캐시 서버 없이 같은 모집단 데이터를 재사용하도록 했습니다.

프로세스 메모리 캐시는 애플리케이션이 재시작되면 비워집니다. 당시 구현에는 TTL과 크기 제한, 데이터 변경 후 캐시를 무효화하는 경로가 없습니다. Render 무료 배포는 인스턴스 하나만 사용할 수 있어, 당시에는 인스턴스 간 캐시 동기화를 다룰 필요가 없었습니다.

중복 로직을 함수로 묶으면 수정과 테스트가 쉬워집니다. 하지만 여러 API가 같은 데이터를 반복 조회한다면 함수를 공유하는 것만으로는 사용자의 대기 시간이 줄지 않습니다. 이번에는 캐시 적중 시 공통 모집단 데이터를 재사용해 반복 조회를 줄였습니다.

## 확인 가능한 팀 프로젝트 근거

- [적재와 upsert PR #49](https://github.com/team-ttobagi/seoul-data-analysis)
- AI 응답 검증 PR #68
- 인사이트 정책 PR #121
- 수치 검증과 DB 오류 PR #154
- 팀 저장소

개인 Spring Boot 마이그레이션 저장소와 성능 로그는 비공개입니다. 공개 PR은 팀 프로젝트 기여를, 성능 로그는 개인 후속 개선을 보여주는 자료로 구분합니다.
