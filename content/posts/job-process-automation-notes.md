---
index_order: 1
title: 채용 메일을 Obsidian 기록으로 옮긴 개인 자동화
slug: job-process-automation-notes
excerpt: 채용 메일을 자동으로 수집하고 Obsidian에 정리했습니다. 반복 작업은 줄었지만, 지원할 회사를 결정하는 일은 여전히 제 몫이었습니다.
---

# 채용 메일을 Obsidian 기록으로 옮긴 개인 자동화

채용 공고를 확인하고 지원 결과를 정리하는 과정에는 반복 작업이 있었습니다. 이를 자동화하고 싶었지만, 채용 플랫폼을 직접 크롤링하는 방식은 법적 검토와 유지보수 부담이 있었습니다.

개인 비서형 AI 서비스가 지금처럼 널리 쓰이기 전이었습니다. 수신에 동의해 받은 채용 메일을 활용하면 별도의 플랫폼 수집 과정 없이 개인용 관리 도구를 만들 수 있다고 판단했습니다.

Gmail에서 공고 정보를 추출해 SQLite에 저장하고, Obsidian 문서로 정리하는 자동화를 시작했습니다.

## 메일 수집과 기록 처리

중복 수집을 막기 위해 Gmail 메시지 ID로 처리 여부를 확인했습니다. 이미 처리한 메일은 건너뛰고, 처음 수집한 메일만 다음 단계로 전달했습니다.

플랫폼별 HTML 구조에 대응하도록 잡코리아, 사람인, 고용24 파서를 분리했습니다. 메일 원문과 HTML을 보관한 뒤 발신자에 맞는 파서를 선택해 공고 정보를 추출했습니다.

추출한 정보는 SQLite에 저장하고 Obsidian 문서로 만들었습니다. 문서에서 지원 여부를 체크하면 데이터베이스 상태가 `IN_PROGRESS`로 변경되도록 연결했습니다.

파싱에 실패해도 원문은 보관하도록 했습니다.

```python
info = extract_message_info(message)
message_id = info["id"]

if exists_message(message_id):
    return

info["raw_path"] = save_raw_message(message)

html = extract_html(message["payload"])
if not html:
    return

info["html_path"] = save_html(message_id, html)

parser = parser_factory.get_parser(
    sender=info["sender"],
    subject=info["subject"],
)
if parser is None:
    return
```

지원하지 않는 메일 형식도 원문을 바탕으로 문제를 확인하고 파서를 보완할 수 있도록 구성했습니다.

## 자동화가 줄인 반복 작업

자동화 이후에는 채용 메일을 하나씩 열어 공고 정보를 정리하는 작업이 줄었습니다. Obsidian에 정리된 내용을 살펴보고 관심 있는 공고를 직접 골라 지원했습니다.

지원할 회사를 정하는 일은 자동화하지 않았습니다. 공고 정리와 기록은 프로그램이 처리하고, 지원 여부는 제가 결정했습니다.

실제 메일로 수집부터 원문 보관, 파싱, SQLite 저장, Obsidian 문서 생성과 지원 상태 갱신까지 확인했습니다. 자동 테스트는 작성하지 않았고, 다양한 메일 형식에서의 안정성도 검증하지 않았습니다.
