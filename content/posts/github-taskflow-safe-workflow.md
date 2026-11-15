---
index_order: 6
title: Git 상태를 확인하고 안전하지 않으면 멈추는 Taskflow
slug: github-taskflow-safe-workflow
excerpt: stash/pop으로 변경사항을 옮기던 절차를 줄이고, 현재 변경사항이나 로컬 커밋이 다른 PR에 섞이지 않도록 실제 Git 저장소에서 확인한 기록입니다.
---

# Git 상태를 확인하고 안전하지 않으면 멈추는 Taskflow

팀에서 이슈와 PR을 만들 때 진행 중인 파일 변경을 stash와 pop으로 옮기는 절차가 반복됐습니다. staged, unstaged, untracked 변경이나 로컬 커밋이 남아 있으면 자동화가 기존 작업을 덮어쓰거나 잘못된 기준 브랜치에서 새 브랜치를 만들 수 있었습니다.

반복되는 시작 절차를 줄이기 위해 Python CLI를 만들고, 자동화를 멈춰야 하는 Git 상태를 먼저 구분했습니다. `--adopt`는 기준 브랜치에서만 동작하며, 현재 HEAD가 원격 기준 브랜치의 이력에 속하는지 확인합니다. 변경사항을 작업 브랜치로 옮긴 뒤에는 원래 기준 브랜치가 바뀌지 않았는지도 다시 확인합니다. 예상하지 못한 로컬 커밋이나 feature 브랜치를 만나면 GitHub 이슈를 만들기 전에 멈춥니다.

다음 코드는 이 안전 확인이 필요한 이유를 보여줍니다. 현재 HEAD가 원격 기준 브랜치의 이력에서 벗어나 있으면 자동화가 로컬 커밋까지 새 PR에 섞을 수 있어, 변경사항을 옮기기 전에 멈추도록 했습니다.

```python
remote_tip = f"refs/remotes/{remote}/{base_branch}"
remote_ref = _run_start_command(
    runner, ["git", "rev-parse", "--verify", f"{remote_tip}^{{commit}}"], root, io
)
if remote_ref is None:
    return False
if remote_ref.returncode != 0:
    io.write(f"기준 원격 브랜치를 찾을 수 없습니다: {remote_tip}. 작업 파일은 그대로입니다.")
    return False

# 현재 커밋이 기준 브랜치의 이력이 아닐 때는 자동으로 작업을 옮기지 않습니다.
ancestry = _run_start_command(
    runner, ["git", "merge-base", "--is-ancestor", "HEAD", remote_tip], root, io
)
if ancestry is None:
    return False
if ancestry.returncode != 0:
    io.write(
        f"현재 {current}의 HEAD가 {remote}/{base_branch}의 조상이 아닙니다. "
        "이미 dev/main에 커밋한 변경이나 다른 브랜치의 커밋이 PR에 섞일 수 있어 자동 이동하지 않습니다. "
        "기존 파일/Stage/커밋은 그대로 유지됩니다. 커밋 이력을 먼저 별도로 확인하세요."
    )
    return False
```

먼저 원격 기준 브랜치가 실제 커밋을 가리키는지 확인하고, 이어서 현재 HEAD가 그 이력에 속하는지 검사합니다. 두 번째 조건이 맞지 않으면 안내를 출력하고 `False`를 반환하므로 이후의 브랜치 전환이나 변경사항 이동으로 진행하지 않습니다. 이 발췌는 자동화가 무엇을 하는지보다 위험한 상태에서 어디서 멈추는지를 보여줍니다.

## 실제 Git 상태를 사용한 검증

임시 디렉터리에 실제 Git 저장소와 bare remote를 만들었습니다. 인덱스와 브랜치, 원격 기준은 Git 명령으로 확인하고, 사용자 계정에 영향을 주는 외부 GitHub 호출만 fake `gh`로 대체했습니다. staged, unstaged, untracked 변경 보존과 기준 브랜치 보호, 위험 상태에서의 중단을 다룬 테스트 18개와 Python 컴파일 검사가 2026년 9월 21일 GitHub Actions에서 통과했습니다.

이 테스트는 실제 Git 상태를 다뤘지만 GitHub 인증이나 네트워크 장애까지 검증하지는 않았습니다. 자동화의 신뢰성을 판단할 때는 설명보다 실제 저장소의 변경사항이 보존되는지를 확인했습니다.

관련 코드: [runtime/taskflow.py](https://github.com/kim-thub/github-taskflow-skill)
