---
index_order: 7
title: 채용 메일을 Obsidian 기록으로 옮긴 개인 자동화
slug: job-process-automation-notes
excerpt: 중복 메일 확인부터 원문 보관과 발신자별 파싱, SQLite 및 Obsidian 기록까지 구현하고 직접 확인한 범위를 정리합니다.
---

# 채용 메일을 Obsidian 기록으로 옮긴 개인 자동화

채용 플랫폼마다 메일의 HTML 형식이 달라 원문을 확인하고 중복 여부를 판단한 뒤 공고와 지원 상태를 다시 기록해야 했습니다. 이 반복을 줄이려고 Gmail 메시지에서 공고 정보를 추출해 SQLite에 저장하고, Obsidian 문서를 만든 뒤 문서의 체크 상태를 DB의 `IN_PROGRESS`로 반영하는 개인 자동화를 시작했습니다.

메시지 ID로 이미 수집한 메일인지 확인해 중복 처리를 막고, 파싱에 필요한 원문과 HTML을 보관했습니다. 잡코리아, 사람인, 고용24 파서를 분리했습니다. URL과 필터를 확인한 뒤 Obsidian 문서와 지원 상태를 갱신했습니다.

아래 코드는 중복 메일을 먼저 걸러낸 뒤 파서를 고르기 전에 원문을 보관하는 순서를 보여줍니다. 파싱에 실패하거나 지원하지 않는 발신자여도 원문이 남아야 이후에 입력 형식과 파서 선택을 다시 확인할 수 있습니다.

```python
info = extract_message_info(message)
message_id = info["id"]

if exists_message(message_id):
    return

# 파싱 결과를 다시 살펴볼 수 있도록 원본을 먼저 보관합니다.
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

HTML이 없으면 이후 처리를 멈추고, 발신자에 맞는 파서가 없으면 보관한 원문과 HTML을 남긴 상태로 반환합니다. 이 순서는 파싱 성공 여부와 원문 보관을 분리해, 지원하지 않는 형식도 나중에 살펴볼 수 있게 합니다.

실제 메일로 수집, 원문 보관, 파서 선택, SQLite 저장, 문서 생성, 지원 상태 갱신까지 실행하고 결과를 직접 확인했습니다. 자동 테스트는 작성하지 않았고, 여러 메일 형식에서의 안정성도 검증하지 않았습니다. 교육에 참여하면서 개발을 중단했으며 운영 중인 서비스는 아닙니다.
