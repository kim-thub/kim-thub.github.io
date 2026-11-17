---
index_order: 5
title: SPOT RADAR의 Spring Boot 마이그레이션과 조회 비용 개선
slug: spot-radar-spring-migration
excerpt: 기존 API 계약을 유지하면서 요청 시간과 SQL 실행 시간을 나눠 측정하고, 상권 기본 정보 조회와 반복 데이터 조회를 줄인 과정입니다.
---
# SPOT RADAR의 Spring Boot 마이그레이션과 조회 비용 개선

SPOT RADAR 팀 프로젝트의 초기 API는 FastAPI로 구현했습니다. 이후 개인 작업으로 기존 화면과 데이터베이스를 유지하면서 백엔드를 Spring Boot로 전환했습니다. 응답이 느려지는 원인을 찾기 위해 요청 처리 시간과 데이터 조회 시간을 나눠 측정하고, 불필요한 조회를 줄였습니다.

## API 계약을 유지한 마이그레이션

새 API 계약을 만드는 대신 React 화면과 Supabase PostgreSQL 데이터를 계속 사용할 수 있도록 기존 계약을 유지했습니다. 경로와 요청 파라미터, JSON 필드, `null`과 빈 배열의 의미, 분석 점수와 추천 정렬을 그대로 두었습니다.

요청은 React 화면에서 `/api/v1` 계약을 거쳐 Spring MVC, JPA, Native SQL로 이어집니다. SQL 조회 결과를 배열의 순서로 구분하던 방식에서, 각 항목의 이름으로 구분하는 방식으로 바꿨습니다. 분기 계산, 퍼센타일, 순위, 숫자 형식은 함수로 분리했습니다. JUnit 5와 Mockito로 계산 경계와 `null` 처리, 응답 구성을 확인했습니다.

## 요청 시간과 SQL 시간을 분리했습니다

진단 당시 API 평균 응답 시간은 약 30초였지만, Supabase `EXPLAIN ANALYZE`에서 확인한 핵심 SQL 실행 시간은 약 1.27초였습니다. API 요청부터 응답까지 걸린 전체 시간과, 데이터베이스에서 데이터를 조회하는 데 걸린 시간을 각각 측정했습니다. 이후 대량 데이터 전송과 같은 업종 및 분기의 모집단을 반복 조회하는 흐름을 원인 후보로 좁혔습니다.

## 상위 후보만 상권 기본 정보를 조회합니다

추천 점수는 전체 상권 데이터를 기준으로 계산하되, 화면에 표시할 기본 정보는 상위 7개 상권만 조회하도록 변경했습니다. 그 결과 기본 정보 조회량이 평균 1,650건에서 7건으로 줄었습니다.
```
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

이렇게 점수 계산용 행과 추가 설명을 위해 읽는 상권 기본 정보를 분리했습니다.

| 측정 항목                        | 변경 전    | 변경 후   |
| ---------------------------- | ------- | ------ |
| 기본 추천 상권 정보 조회량 평균           | 1,650건  | 7건     |
| Repository 조회 구간 평균          | 3.73초   | 0.33초  |
| 추천 API 평균 응답 시간, 조회 범위 개선 전후 | 29.7초   | 9.4초   |
| 로컬 추천 API, 캐시 Cold → Hit     | 9.055초  | 1.750초 |
| 로컬 Overview, 캐시 Cold → Hit   | 4.192초  | 1.570초 |
| Render 배포, 동일 조건 Cold → Hit  | 28.013초 | 1.877초 |

조회 범위 개선과 캐시 적용은 서로 다른 단계에서 측정했습니다. 캐시 Cold 응답에는 캐시 미적중 외에 서버 기동과 DB 연결 상태도 영향을 주었을 수 있습니다.

## 메모리 캐시를 택한 이유와 감수한 점

초기 팀 작업에서는 일정이 촉박해 뷰 기반 방식과 Redis 같은 외부 캐시를 검토해보았지만, 구현에 옮기지는 못했습니다. 그 결과 같은 업종과 분기의 데이터를 반복 조회하는 비용이 남았습니다.

개인 마이그레이션을 시작했을 때는 Redis 사용 경험이 적어 반려하고, Render 무료 인스턴스 하나에서 변경을 작게 유지하려고 Spring Cache의 메모리 구현을 택했습니다. 실행 로그에서 `ConcurrentMapCacheManager → ConcurrentMapCache → ConcurrentHashMap` 구성을 확인했고, 다섯 분석 API가 별도 캐시 서버 없이 같은 모집단 데이터를 재사용하도록 했습니다.

메모리 캐시는 별도 서버가 필요하지 않지만, 애플리케이션을 재시작하면 저장된 데이터가 사라집니다. 당시 구현에는 자동 만료나 데이터 변경 시 캐시를 갱신하는 기능도 없었습니다. 단일 인스턴스 환경이었기 때문에 서버 간 데이터 동기화는 고려하지 않았습니다.

중복 로직을 함수로 묶으면 수정과 테스트가 쉬워집니다. 하지만 여러 API가 같은 데이터를 반복 조회한다면 함수를 공유하는 것만으로는 사용자의 대기 시간이 줄지 않습니다. 이번에는 캐시 적중 시 공통 모집단 데이터를 재사용해 반복 조회를 줄였습니다.
