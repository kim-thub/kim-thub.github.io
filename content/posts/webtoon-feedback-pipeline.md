---
index_order: 8
title: 웹툰 댓글을 분석해 피드백으로 연결한 흐름
slug: webtoon-feedback-pipeline
excerpt: 크롤러 이후 Flask, NLP, Gemini, PocketBase로 이어지는 흐름과 서로 달랐던 라벨 범위를 바로잡은 기록입니다.
---

# 웹툰 댓글을 분석해 피드백으로 연결한 흐름

네이버 웹툰 작가가 작품을 등록하고 댓글 분석 결과를 확인해 저장하는 팀 프로젝트입니다. 팀 리더로 일정과 기능 범위를 조율했습니다. 화면 구현 폴더인 `static/`과 `templates/`, `toon_clawer` 크롤러, 최종 발표를 제외한 나머지 코드를 작성했습니다.

구현한 범위는 Flask 라우팅(`app.py`)과 분석 유스케이스(`Usecase.py`), PocketBase 연결(`db.py`), 라벨 분류, 감성과 유사도 분석, Gemini 피드백 생성과 저장, 데이터와 모델 리소스입니다. 댓글과 별점 크롤링, 최종 발표는 팀원이 맡았습니다. 저는 크롤러가 전달한 데이터부터 분석과 저장까지의 흐름을 연결했습니다.

## 라벨 범위 불일치 수정

분석 대상이 아닌 라벨 4가 라벨별 집계와 Gemini 입력에 포함되면 화면 통계와 생성된 요약이 서로 다른 댓글을 기준으로 만들어질 수 있었습니다. 두 경로에서 라벨 4를 함께 제외하도록 수정했습니다.

아래 코드는 화면 집계에 사용되는 댓글 그룹을 만드는 부분입니다. 이 예시에서는 라벨 4를 건너뛰는 조건이 핵심이며, 같은 제외 기준을 Gemini 입력에도 적용해야 화면 수치와 요약이 같은 댓글 범위를 가리킵니다.

```python
comments_by_label = {}
with open(
    f"Webtoon_label_nlp/label_comments_{title_id}.txt", "r", encoding="utf-8"
) as file:
    for line in file:
        comment, label = line.strip().split("\t")
        # 화면 집계와 Gemini 입력에서 제외 대상 라벨을 동일하게 뺍니다.
        if label == "4":
            continue
        if label in comments_by_label:
            comments_by_label[label].append(comment)
        else:
            comments_by_label[label] = [comment]

comments_count_by_label = {
    label: len(comments) for label, comments in comments_by_label.items()
}
```

따라서 `comments_count_by_label`은 필터를 통과한 댓글만 세고, 라벨 4는 집계 결과에 나타나지 않습니다. 코드 블록은 화면 집계 경로의 기준을 보여주는 발췌이며, Gemini 요청 구성 자체까지 이 코드가 보여주는 것은 아닙니다.

이미 처리한 최신 회차는 다시 분석하지 않도록 했고, 별점 크롤러가 만든 임시 레코드를 정리하도록 유스케이스를 수정했습니다. LLM 요청에서 예외가 발생하면 재시도하도록 처리했습니다.

## 확인 범위와 재현 조건

웹툰 등록과 삭제, 분석 화면 이동, NLP 결과 파일 생성, PocketBase 저장까지 직접 실행해 확인했습니다. 자동화 테스트나 처리 시간 비교 자료는 남아 있지 않습니다. 모델 경로와 실행 환경이 로컬 설정에 의존합니다. 다른 환경에서 같은 결과를 확인하려면 모델과 경로, 테스트 데이터를 준비해야 합니다. 팀 서비스 전체 성과를 개인 성과로 표시하지 않습니다.

- [Usecase.py](https://github.com/KIT452/webtoon_feedback)
- [웹툰 피드백 프로젝트 문서](https://curved-approach-a38.notion.site/Team-Project-30236972eb504556bd153638cb58cb51)
