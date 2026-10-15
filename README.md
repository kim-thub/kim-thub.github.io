# 김수빈 웹 포트폴리오

GitHub Pages용 정적 사이트입니다. 서버·패키지 설치·빌드 명령이 필요하지 않습니다.

## 제출처별 색상 변경

`site/assets/theme.css`의 `:root` 변수만 수정하세요. 모든 페이지의 배경, 글자, 카드, 버튼, 태그, 그래프가 이 값을 사용합니다.

| 변수 | 쓰임 |
| --- | --- |
| `--canvas`, `--surface`, `--surface-alt` | 바탕과 카드 |
| `--ink`, `--muted`, `--line` | 본문과 경계선 |
| `--accent`, `--accent-ink` | 링크·강조·버튼 대비. 연한 강조색은 자동 생성 |
| `--highlight`, `--highlight-ink` | 보조 강조 |
| `--chart-before`, `--chart-after` | 성능 비교 막대. `--accent`를 따라 자동 변경 |

예: 지원 회사의 브랜드색에 맞추려면 `--accent` 하나를 바꿉니다. 연한 강조색과 그래프 색도 함께 바뀝니다. 버튼 글자가 읽히지 않으면 `--accent-ink`도 조정하고 대비를 확인하세요. 다른 HTML 파일에서 색상 코드를 변경할 필요가 없습니다.

## 로컬 확인

```bash
cd site
python3 -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 엽니다. 파일로 직접 열 때도 상대 경로가 동작하지만, 로컬 서버로 확인하는 편이 링크 검증에 적합합니다.

내부 링크 검사는 저장소 루트에서 `python3 scripts/check_site.py`를 실행합니다. GitHub Actions에서도 게시 전에 같은 검사를 합니다.

## GitHub Pages 게시

1. 새 공개 저장소 `kim-thub.github.io`를 만듭니다. 동일 이름이 이미 있다면 다른 저장소 이름도 사용할 수 있지만, URL에 저장소 경로가 붙습니다.
2. 이 폴더의 `README.md`, `site/`, `.github/`를 저장소 루트에 커밋하고 `main`에 푸시합니다.
3. 저장소 **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
4. Actions의 `Deploy portfolio to GitHub Pages` 실행 성공과 실제 모바일·데스크톱 페이지를 확인합니다.

게시 전에는 팀 자료의 공개 가능 범위와 링크를 다시 확인하세요. SPOT RADAR의 팀 저장소와 GitHub Taskflow는 공개이고, 개인 Spring 저장소와 Webtoon Feedback 저장소는 비공개입니다. 이 사이트에는 비공개 저장소의 코드·커밋 링크를 공개 근거처럼 배치하지 않았습니다.

공개 이력서 PDF에는 전화번호가 있어 첫 버전에 포함하지 않았습니다. 홈의 버튼은 이메일로 이력서 PDF를 요청하도록 구성했습니다.
