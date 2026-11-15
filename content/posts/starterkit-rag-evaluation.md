---
index_order: 9
title: 상속길잡이 스타터킷의 청킹 평가와 원문 보존
slug: starterkit-rag-evaluation
excerpt: 검색 결과의 순위가 높다고 해서 언제나 충분한 근거가 남는 것은 아닙니다. 한정된 질문과 512토큰의 입력 예산 안에서, 어떤 문장이 살아남고 어떤 맥락이 사라지는지 살펴봤습니다.
---

# 상속길잡이 스타터킷의 청킹 평가와 원문 보존

## 검색 순위와 입력 예산을 함께 확인했습니다

Source_V1.xlsx에서 출처가 연결된 27개 행에 네 가지 청킹 방식을 적용했습니다. Golden Set 45개 질문 중 근거를 연결할 수 있는 6개를 골라 EmbeddingGemma 2 임베딩과 메모리 내 cosine 검색으로 비교했습니다.

Wiki와 검증 문서 대부분은 AI의 도움을 받아 제가 직접 작성했습니다. 프로젝트 전체의 결과와 제 기여를 구분하고, 저장소 변경과 PR, 검증 기록으로 확인할 수 있는 범위만 적었습니다.

| 방식 | Recall@5 | MRR@10 | 512 토큰 안에서 사용 가능한 근거 |
|---|---:|---:|---:|
| Agentic, 행 단위 custom 처리 | 77.8% | 0.660 | 41.7% |
| Hybrid | 66.7% | 0.478 | 5.6% |
| LineBased | 66.7% | 0.478 | 5.6% |
| Hierarchical | 100% | 1.000 | 0%, 단일 6,971 토큰 청크 |

Recall@5는 정답 근거가 상위 5개 검색 결과에 포함된 비율이고, MRR@10은 정답 근거가 상위 10개 안에서 얼마나 앞에 나오는지를 반영하는 지표입니다. 당시에는 검색 순위와 함께 모델 입력 예산 안에서 근거를 사용할 수 있는지도 살폈습니다. 입력 예산을 다른 지표보다 우선했다고 단정할 근거는 없습니다. Hierarchical은 Recall@5가 100%였지만 검색 결과가 6,971 토큰짜리 단일 청크여서 512 토큰 예산에는 들어오지 않았습니다.

문장이나 단어 단위 방식보다 토큰 사이의 관계를 더 잘 이어줄 것이라는 기대를 바탕으로 Agentic을 MVP 1로 선택했습니다. 다만 이 XLSX 경로는 결정적인 custom 행 단위 처리였고 LLM을 호출하지 않았습니다. 관계가 더 잘 보존되는지도 별도 지표로 측정하지 않았습니다.

비교 대상은 근거가 연결된 6개 질문뿐입니다. Recall@3에서는 Agentic이 55.6%, Hybrid와 LineBased가 각각 58.3%였습니다. GS-04에서는 Hybrid와 LineBased가 더 나았고, GS-11에서는 어떤 방식도 상위 5개 안에서 근거를 찾지 못했습니다.

## PDF 토큰 초과 문제와 분할

PDF 처리에서 512 토큰을 초과한 청크가 만들어져 후속 검증과 색인 단계에서 오류가 발생했습니다. 일반 PDF 문서 요소를 토큰 상한에 맞춰 나누고, 원문의 범위와 순서를 유지하도록 수정했습니다. 분할 전후 해시를 대조해 문자가 빠지거나 중복되지 않는지도 검사했습니다.

아래 발췌는 토큰 상한을 넘지 않는 가장 긴 분할 지점을 찾고, 최종 조각들을 이어 붙였을 때 원문이 그대로 남는지 검사하는 부분입니다. 단순히 청크 길이를 줄이는 것만으로는 누락이나 순서 변경을 막았다고 할 수 없어 이 검증이 함께 필요했습니다.

```python
low = 1
high = len(remainder)
best = 0
while low <= high:
    middle = (low + high) // 2
    candidate = remainder[:middle]
    if _validate_token_count(count_tokens, candidate) <= target_tokens:
        best = middle
        low = middle + 1
    else:
        high = middle - 1

if best == 0:
    raise ChunkingError(
        "문자 하나도 목표 토큰 수 안에 담을 수 없어 원문을 안전하게 분할할 수 없습니다."
    )

boundary_floor = max(1, best - max(8, best // 8))
whitespace_boundary = max(
    remainder.rfind(" ", boundary_floor, best + 1),
    remainder.rfind("\t", boundary_floor, best + 1),
    remainder.rfind("\n", boundary_floor, best + 1),
    remainder.rfind("\r", boundary_floor, best + 1),
)
cut = whitespace_boundary + 1 if whitespace_boundary >= boundary_floor else best
if _validate_token_count(count_tokens, remainder[:cut]) > target_tokens:
    cut = best

piece = remainder[:cut]
pieces.append((piece, start, start + cut))
start += cut

# 색인 전에 원문의 누락, 변경 여부를 확인합니다.
if "".join(piece for piece, _, _ in pieces) != text:
    raise ChunkIntegrityError("토큰 분할 중 원문 문자가 누락되거나 바뀌었습니다.")
```

이 코드에서 이진 탐색은 토큰 상한 안에 들어오는 가장 긴 구간을 찾고, 그 안에서 공백 경계를 우선 사용합니다. 마지막 비교는 분할 조각을 다시 이어 붙여 원문과 일치하는지 확인합니다. 안전한 구간을 만들지 못하면 불완전한 결과를 색인하지 않고 오류로 중단합니다.

XLSX는 각 행이 하나의 정보 단위라고 보고 행 전체를 보존했습니다. 확인한 Source_V3에는 512 토큰을 넘는 행이 없었습니다. 이후 더 긴 행이 들어오면 입력 예산을 초과할 가능성이 있지만, 이는 관측된 오류가 아니라 잠재적 한계입니다.

청킹 단위 테스트 71개가 통과했고, 전체 pytest 기록에는 671개 통과와 28개 건너뜀이 남아 있습니다. PR 제출 시점의 CI 수치는 별도 실행 결과이므로 위 기록과 합산하지 않았습니다. 이 테스트는 코드 회귀와 원문 무결성을 확인하지만 검색 품질이나 최종 법률 답변의 정확도를 입증하지는 않습니다.

## PDF 검토와 게시 기준

재사용할 실업인정 PDF 3종에서 만든 339개 청크를 통합 전 기준선으로 기록했습니다. 검색을 16회 실행했고, 승인된 질문 14개에 근거 31개를 연결했습니다. Recall@3, Recall@5, Recall@10은 각각 0.4667, 0.6238, 0.7000이었으며 MRR@10은 0.5447이었습니다.

Docling으로 파싱한 뒤 사람이 원문을 검토하고, 승인한 콘텐츠의 해시를 원본 해시와 연결했습니다. 색인과 게시 전에는 청크 수, PDF 해시, 승인 해시, 출처 메타데이터가 일치하는지 확인합니다. 하나라도 다르면 작업을 중단합니다. 이 검토 절차에 시간이 더 들지만, 표나 OCR 변환 오류가 승인 없이 게시될 가능성을 줄이고 승인 후 원문이 바뀌었는지도 확인할 수 있습니다.

수정 뒤 동일한 14개 질문을 실제 데이터베이스에서 다시 평가하지 않았습니다. 따라서 기준선 수치를 검색 개선 성과로 해석하지 않습니다. PR 검증 기록은 코드와 계약, 오류 처리를 확인한 결과입니다.

## Evidence에서 원본 행까지 추적

Source_V1의 U-03 자료를 파싱하고 임베딩해 격리된 로컬 pgvector에 넣었습니다. 게시된 자료를 검색하고 Evidence에서 원본 행까지 추적했습니다. 대표 질문의 검색 점수는 0.781031이었고 원본 위치는 `Source_V1.xlsx#SU_링크기록(전체)!A84:H84`입니다.

Source_V3를 다시 색인할 때 검색 본문에는 Source ID와 제목, 발췌만 넣고 `condition`, `unverified`, `scope`, `caution` 내부 메모 필드는 제외했습니다.

기록에는 31개 항목 재색인 및 게시, 대표 검색 5/5, Evidence 25건, 구버전과 내부 메모 표제어 노출 0건이 남아 있습니다. 전체 임베딩을 대조하거나 Golden Set으로 검색 품질을 다시 평가한 것은 아닙니다. 공식 법률 원문의 정확성을 확인한 결과도 아닙니다.

## 관련 근거

- [스타터킷 저장소](https://github.com/ddalggagclick/starter-kit)
- 토큰 상한 Issue #244
- 무손실 분할 PR #245
- PDF 검토 및 게시 PR #135
- Evidence 추적 PR #64
- 내부 메모 제외 PR #204
