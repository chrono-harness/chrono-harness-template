#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node --test tests/roadmap.test.cjs
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python ">=3.11" --with PyYAML==6.0.3 python tests/test_release.py
stage=$(mktemp -d)
trap 'rm -rf -- "$stage"' EXIT
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD -d repository=chrono-harness/chrono-harness-template "$PWD" "$stage/default"
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD -d 'features=[]' -d manage_roadmap=false . "$stage/empty"
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
  -d 'features=["pr"]' -d repository=chrono-harness/chrono-harness-template \
  -d 'project_guide=业务源码位于 src/。' -d generate_check=true -d 'check_command=python3 check.py' . "$stage/selected"
# Render the self-hosted publisher and both choices of the host release contract.
source_plan=$(cat .chrono-harness/release.json)
binary_plan=$(python3 -c 'import json,sys; p=json.load(sys.stdin); p.update(kind="binary",version_policy="explicit",binary="demo",build="tools/build.sh"); print(json.dumps(p))' < .chrono-harness/release.json)
for kind in copier binary; do
  plan=$source_plan
  if [[ "$kind" == binary ]]; then plan=$binary_plan; fi
  uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
    -d 'features=[]' -d "release_plan=$plan" . "$stage/$kind"
  cmp .github/release/plan.py "$stage/$kind/.github/release/plan.py"
  cmp .github/release/publish.py "$stage/$kind/.github/release/publish.py"
done
cmp .github/workflows/release.yml "$stage/copier/.github/workflows/release.yml"
grep -q '^  build:' "$stage/binary/.github/workflows/release.yml"
test ! -e "$stage/empty/.github/workflows/release.yml"
test ! -e "$stage/empty/.github/release"
for tool in diagnostics host-bootstrap host-release inputs judge-routes judge-cost worktree judge-filemap judge-mixed judge-projects judge-ci judge-workflow test-git; do
  uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
    -d repository=chrono-harness/chrono-harness-template -d "features=[\"$tool\"]" . "$stage/$tool"
done
uv run --no-project --python ">=3.11" python tests/check_render.py "$stage/empty" "$stage/selected" "$stage/default" "$stage/diagnostics" "$stage/host-bootstrap" "$stage/host-release" "$stage/inputs" "$stage/judge-routes" "$stage/judge-cost" "$stage/worktree" "$stage/judge-filemap" "$stage/judge-mixed" "$stage/judge-projects" "$stage/judge-ci" "$stage/judge-workflow" "$stage/test-git"

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
    echo "Verify tool choice $choice"
    if [[ -n "$(git ls-files --unmerged)" ]]; then
      git diff --cc -- CLAUDE.md
      git ls-files --unmerged
      exit 1
    fi
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
