---
index_order: 8
title: 웹툰 댓글 분석에서 분류 기준을 통일하기까지
slug: webtoon-feedback-pipeline
excerpt: 댓글 분류 모델의 출력 범위와 서비스의 분류 범위가 달랐습니다. 화면 집계와 Gemini 피드백에 같은 기준을 적용한 과정을 기록합니다.
---

# 웹툰 댓글 분석에서 분류 기준을 통일하기까지

웹툰 댓글을 분석해 작가에게 피드백을 제공하는 서비스를 개발했습니다. 수집한 댓글을 주제별로 분류하고, 감성과 유사도를 분석한 뒤 Gemini로 피드백을 생성하는 팀 프로젝트였습니다.

저는 Flask를 중심으로 댓글 분석부터 피드백 저장까지 이어지는 기능을 구현했습니다. 구현 과정에서 모델이 분류한 댓글과 서비스가 실제로 사용하는 분류 범위가 다르다는 점을 발견했습니다.

## 모델에는 다섯 가지, 서비스에는 네 가지

댓글을 분석할 때는 먼저 주제별로 라벨을 부여했습니다.

모델의 분류 코드에는 다음과 같은 기준이 있었습니다.

| 라벨 | 분류 |
|---|---|
| 0 | 작화 |
| 1 | 스토리 |
| 2 | 분량 |
| 3 | 기타 |
| 4 | 디자인 |

라벨 4는 코드의 단어 사전에서 '디자인'으로 지정되어 있습니다. 다만 사전에 없는 댓글은 모델이 예측하므로 라벨 4의 모든 댓글이 디자인에 관한 내용이라고 단정할 수는 없습니다.

반면 화면에 표시하는 통계와 Gemini 피드백은 작화, 스토리, 분량, 기타의 네 가지 분류를 사용했습니다.

분류 모델은 라벨 4까지 생성할 수 있었지만, 서비스는 0~3번 라벨만 사용하도록 설계되어 있었습니다. 따라서 화면 집계와 Gemini 입력에서 라벨 4를 제외하는 기준이 필요했습니다.

## 같은 분류 범위로 집계하고 요약하기

먼저 화면 집계에서 라벨 4를 제외했습니다.

```python
comments_by_label = {}

with open(
    f"Webtoon_label_nlp/label_comments_{title_id}.txt",
    "r",
    encoding="utf-8"
) as file:
    for line in file:
        comment, label = line.strip().split("\t")

        if label == "4":
            continue

        if label in comments_by_label:
            comments_by_label[label].append(comment)
        else:
            comments_by_label[label] = [comment]

comments_count_by_label = {
    label: len(comments)
    for label, comments in comments_by_label.items()
}
```

라벨 4에 해당하는 댓글은 건너뛰고, 나머지 댓글만 주제별로 모아 개수를 계산하도록 했습니다.

Gemini에 전달하는 댓글도 같은 기준으로 제한했습니다.

```python
if label in ['0', '1', '2', '3']:
    if label in comments_by_label:
        comments_by_label[label].append(comment)
    else:
        comments_by_label[label] = [comment]
```

두 코드의 작성 방식은 다르지만, 처리 대상은 0~3번 라벨로 같습니다. 이렇게 화면 통계와 AI 피드백이 같은 **분류 범위**를 사용하도록 맞췄습니다. 다만 Gemini에는 분류별 댓글 전체가 아닌 일부가 전달되므로 두 결과의 댓글 수가 같다는 뜻은 아닙니다.

## 분석 결과가 이어지는 과정

댓글 분류 이후에는 주제별 데이터를 Gemini에 전달해 피드백을 생성했습니다.

각 분류에서 최대 40개의 댓글을 무작위로 선택하고, 이를 바탕으로 주제별 피드백을 작성하도록 요청했습니다. 이후 생성된 내용을 다시 Gemini에 전달해 종합 피드백을 만들고 PocketBase에 저장했습니다.

분석 결과가 화면에 표시되는 것으로 끝나지 않고, 작가가 다시 확인할 수 있는 기록으로 남도록 구성했습니다.

## 구현과 확인의 범위

웹툰 등록과 삭제, 분석 화면 이동, NLP 결과 파일 생성, PocketBase 저장까지 직접 실행하며 확인했습니다.

분석 과정에서는 이미 처리한 최신 회차를 다시 분석하지 않도록 했고, Gemini 요청 중 특정 예외가 발생했을 때 재시도하는 처리도 추가했습니다.

새로운 기능을 추가하는 것만큼 기존 기능이 같은 기준으로 작동하는지 확인하는 일도 중요했습니다. **모델이 결과를 만들어내는 것과 그 결과를 서비스에서 일관되게 사용하는 것은 별개의 문제였습니다.**

## 더 살펴보기

- [Webtoon Feedback 저장소](https://github.com/KIT452/webtoon_feedback)
- [프로젝트 문서](https://curved-approach-a38.notion.site/Team-Project-30236972eb504556bd153638cb58cb51)
