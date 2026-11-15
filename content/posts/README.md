# 새 블로그 글 추가하기

글마다 Markdown 파일을 하나씩 만듭니다. 이 폴더의 `README.md`는 블로그 목록에 나타나지 않습니다.

1. 이 폴더에 `my-new-post.md` 파일을 만듭니다.
2. 파일 맨 위에 메타데이터를 적고, 아래 예시처럼 본문을 작성합니다.
3. GitHub 웹에서 커밋합니다.
4. GitHub Actions의 `Publish Markdown posts to GitHub Pages`가 자동으로 글을 빌드하고 배포합니다.

````markdown
---
title: 새 글 제목
slug: my-new-post
index_order: 1
excerpt: 목록에서 글의 내용을 소개하는 한두 문장
---

# 새 글 제목

본문을 Markdown으로 작성합니다.

## 소제목

- 목록
- 목록

```java
System.out.println("코드 블록도 지원합니다");
```
````

제목(`#`), 문단, 굵게와 기울임, 인라인 코드, 링크, 이미지, 인용, 목록, 구분선, 표, 언어별 코드 블록을 사용할 수 있습니다. 이미지는 Markdown 파일을 기준으로 상대 경로를 적고, 파일도 저장소에 추가합니다.

`index_order`는 목록 순서입니다. 숫자가 작을수록 위에 표시됩니다. 새 글을 최신순 맨 위에 넣으려면 기존 글의 순서를 한 칸씩 뒤로 조정하고 새 글에 `index_order: 1`을 지정합니다. `slug`는 글 상세 주소에 사용합니다. 영문 소문자와 하이픈으로 작성하고, 기존 글과 중복되지 않게 합니다. 중복된 `slug`가 있으면 빌드가 중단됩니다.

로컬에서 미리 확인하려면 `python3 scripts/build_blog.py`를 실행한 뒤 `index.html`을 엽니다. GitHub Pages 게시 과정은 `.github/workflows/publish-posts.yml`이 담당합니다.
