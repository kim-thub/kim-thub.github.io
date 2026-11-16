# 김수빈 웹 포트폴리오

GitHub Pages로 배포하는 Paper Collage Archive입니다. 디자인과 인터랙션은 `index.html`에, 프로젝트 화면과 블로그 이미지 등 로컬 자료는 `assets/`에 있습니다.

## 프로젝트와 글 수정

- 프로젝트 원고는 `content/projects/`에서 수정합니다.
- 블로그 글은 `content/first-post.md`와 `content/posts/`에서 Markdown으로 관리합니다. 현재는 글 10개를 공개합니다.
- 프로젝트 원고 수정 뒤 `python3 scripts/build_projects.py`, 블로그 글 수정 뒤 `python3 scripts/build_blog.py`를 실행하면 `index.html`에 반영됩니다.
- 로컬 빌드는 `python3 -m pip install -r requirements-build.txt`로 준비합니다.
- 회귀 검사는 `python3 -m unittest discover -s tests -v`로 실행합니다.

## 공개 배포

원고를 바꾼 뒤 해당 빌드 스크립트를 실행하고 생성된 `index.html`을 함께 커밋합니다. `main`에 변경을 반영하면 `.github/workflows/pages.yml`이 회귀 검사를 실행한 뒤, 커밋된 `index.html`, `assets/`, 이전 프로젝트 주소용 리디렉션만 GitHub Pages에 배포합니다. 작업 문서와 원고 파일은 페이지 정적 산출물에 포함되지 않습니다.

기존 프로젝트 주소도 유지합니다. `/projects/spot-radar/`, `/projects/starter-kit/`, `/projects/inheritance-guide/`, `/projects/taskflow/`, `/projects/webtoon/`, `/projects/job-process-automation/`은 해당 프로젝트 상세 화면으로 이동합니다.
