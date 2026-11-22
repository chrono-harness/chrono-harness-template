#!/usr/bin/env bash
set -euo pipefail
stage=$(mktemp -d)
trap 'rm -rf -- "$stage"' EXIT
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD -d repository=chrono-harness/chrono-harness-template "$PWD" "$stage/default"
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD -d 'features=[]' . "$stage/empty"
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
  -d 'features=["pr"]' -d repository=chrono-harness/chrono-harness-template \
  -d 'project_guide=业务源码位于 src/。' -d generate_check=true -d 'check_command=python3 check.py' . "$stage/selected"
for tool in host-bootstrap host-release inputs judge-routes judge-cost; do
  uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
    -d "features=[\"$tool\"]" . "$stage/$tool"
done
uv run --no-project --python ">=3.11" python check.py "$stage/empty" "$stage/selected" "$stage/default" "$stage/host-bootstrap" "$stage/host-release" "$stage/inputs" "$stage/judge-routes" "$stage/judge-cost"

# Exercise a real host that edits its guide and later changes its tool choices.
(
  cd "$stage/default"
  git init -q -b dev
  echo '保留这条宿主指令。' >> CLAUDE.md
  record_host() {
    git add .
    git -c user.name=Copier -c user.email=copier@example.invalid commit -qm 'Record local host inputs'
  }
  record_host
  for choice in '[]' '["instructions"]'; do
    uvx --from copier==9.19.1 copier update --defaults --vcs-ref HEAD \
      --answers-file .chrono-harness/template-answers.yml -d "features=$choice"
    test -z "$(git ls-files --unmerged)"
    grep -Fxq '保留这条宿主指令。' AGENTS.md
    if [[ "$choice" = '[]' ]]; then
      test ! -f docs/licenses/trureturing-Apache-2.0.txt
      if grep -Fq '<!-- chrono-instructions:begin -->' CLAUDE.md; then exit 1; fi
    else
      test -f docs/licenses/trureturing-Apache-2.0.txt
      grep -Fxq '## job.wait' CLAUDE.md
    fi
    record_host
  done
)
