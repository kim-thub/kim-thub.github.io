# 포스트 전용 GitHub Actions 및 상속길잡이 캡처 반영

## 변경 사항

- GitHub Actions 트리거를 `content/posts/*.md` 변경으로 한정했습니다.
- 수동 `workflow_dispatch`를 제거했습니다.
- `content/posts/`에 실제 Markdown 파일이 없으면 빌드와 배포 단계를 건너뜁니다.
- 테스트 스위트는 실행하지 않습니다.
- 상속길잡이 Wiki 외부 이미지 참조 대신 사용자가 제공한 실제 캡처 4개를 로컬 자산으로 추가했습니다.
- 상속길잡이 프로젝트 상세에 2열 화면 갤러리를 추가했습니다.
- 프로젝트 빌더와 블로그 빌더를 실행해 단일 `index.html`에 변경 내용을 반영했습니다.

## 추가한 이미지

1. `assets/projects/inheritance-guide/01-situation-modal.png`
2. `assets/projects/inheritance-guide/02-procedure-checklist.png`
3. `assets/projects/inheritance-guide/03-procedure-detail.png`
4. `assets/projects/inheritance-guide/04-source-grounded-chat.png`

모든 이미지는 사용자 제공 원본 캡처이며, 별도 재생성이나 원격 Wiki 참조를 사용하지 않습니다.

## 배포 동작

- 트리거: `main` 브랜치의 `content/posts/*.md` 변경
- 작업: Python 의존성 설치 → `build_blog.py` → Pages artifact 업로드 → Pages 배포
- 포스트 파일이 없으면 빌드 및 배포 단계 생략
- 테스트 단계 없음
- 프로젝트·디자인 파일 변경은 자동 배포 대상에서 제외

## 빌드 결과

- `build_projects.py`: 종료 코드 0, 프로젝트 6개 반영
- `build_blog.py`: 종료 코드 0, 블로그 7개 반영
- 생성된 `index.html`에 실제 캡처 4개 경로 포함 확인
- 이미지 파일 4개 모두 ZIP 내부 로컬 자산으로 포함
