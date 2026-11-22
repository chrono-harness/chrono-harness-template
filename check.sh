#!/usr/bin/env bash
set -euo pipefail
stage=$(mktemp -d)
trap 'rm -rf -- "$stage"' EXIT
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD -d repository=chrono-harness/chrono-harness-template . "$stage/default"
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD -d 'features=[]' . "$stage/empty"
uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
  -d 'features=["pr"]' -d repository=chrono-harness/chrono-harness-template \
  -d 'project_guide=业务源码位于 src/。' -d generate_check=true -d 'check_command=python3 check.py' . "$stage/selected"
for tool in host-bootstrap host-release inputs judge-routes judge-cost; do
  uvx --from copier==9.19.1 copier copy --defaults --vcs-ref HEAD \
    -d "features=[\"$tool\"]" . "$stage/$tool"
done
uv run --no-project --python ">=3.11" python check.py "$stage/empty" "$stage/selected" "$stage/default" "$stage/host-bootstrap" "$stage/host-release" "$stage/inputs" "$stage/judge-routes" "$stage/judge-cost"
