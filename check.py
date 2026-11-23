"""Verify the default installation and explicit tool choices."""
import json
from pathlib import Path
import sys
import tomllib

empty, selected, full, bootstrap, release, inputs, routes, cost, worktree, filemap, mixed, projects, judge_ci, workflow = map(Path, sys.argv[1:])
manifest = Path(".config/mise/conf.d/chrono-harness.toml")
assert not (empty / manifest).exists()
config = tomllib.loads((selected / manifest).read_text())
assert set(config["tools"]) == {"http:chrono-pr"}
assert json.loads((selected / ".chrono-harness/pr.json").read_text())["base"] == "dev"
assert (selected / ".github/workflows/harness-check.yml").is_file()
assert config["tasks"]["harness-check"]["run"] == "python3 check.py"

for host in (empty, selected, full):
    assert (host / "AGENTS.md").readlink() == Path("CLAUDE.md")
    assert (host / "CLAUDE.md").is_file()
    guide = (host / "AGENTS.md").read_text()
    assert guide == (host / "CLAUDE.md").read_text()
    if host == full:
        assert json.loads((host / ".chrono-harness/rules.json").read_text()) == {"mode": "all"}
        assert "## job.wait" in guide and "## artifact.cleanup" in guide
        assert "mise run harness-setup" in guide
        assert (host / "docs/licenses/trureturing-Apache-2.0.txt").is_file()
    else:
        assert not (host / ".chrono-harness/rules.json").exists()
        assert "## job.wait" not in guide
        assert not (host / "docs/licenses/trureturing-Apache-2.0.txt").exists()
    assert not (host / ".chrono-harness/instructions").exists()
    usage = (host / ".chrono-harness/USAGE.md").read_text()
    assert ("刷新根指南" in usage) == (host == full)

expected = ['http:chrono-cache', 'http:chrono-ci', 'http:chrono-distribution', 'http:chrono-harness', 'http:chrono-host-bootstrap', 'http:chrono-host-release', 'http:chrono-inputs', 'http:chrono-instructions', 'http:chrono-judge-ci', 'http:chrono-judge-cost', 'http:chrono-judge-filemap', 'http:chrono-judge-mixed', 'http:chrono-judge-projects', 'http:chrono-judge-registration', 'http:chrono-judge-routes', 'http:chrono-judge-workflow', 'http:chrono-pr', 'http:chrono-worktree', 'http:verus']
default_config = tomllib.loads((full / manifest).read_text())
assert default_config["tasks"]["harness-setup"]["run"] == [
    "mise install", "mise exec -- chrono-instructions sync-rules --host-root ."
]
assert config["tasks"]["harness-setup"]["run"] == "mise install"
default_tools = default_config["tools"]
assert default_tools.pop("rust") == {"version": "1.95.0", "profile": "minimal"}
assert set(default_tools) == set(expected)
for tool in default_tools.values():
    assert set(tool["platforms"]) == {"linux-x64", "macos-arm64"}

assert "业务源码位于 src/。" in (selected / "AGENTS.md").read_text()
for host, commands in [
    (worktree, {"chrono-worktree", "chrono-judge-registration"}),
    (bootstrap, {"chrono-host-bootstrap", "chrono-judge-registration"}),
    (release, {"chrono-host-release", "chrono-host-bootstrap", "chrono-judge-registration"}),
    (inputs, {"chrono-inputs", "chrono-judge-registration", "chrono-judge-routes", "chrono-judge-filemap", "chrono-judge-mixed"}),
    (workflow, {"chrono-judge-workflow", "chrono-judge-projects", "chrono-judge-routes", "chrono-judge-registration"}),
    (projects, {"chrono-judge-projects", "chrono-judge-filemap"}),
    (judge_ci, {"chrono-judge-ci", "chrono-judge-projects", "chrono-judge-filemap", "chrono-judge-routes", "chrono-judge-mixed", "chrono-judge-registration"}),
    (mixed, {"chrono-judge-mixed", "chrono-judge-registration"}),
    (filemap, {"chrono-judge-filemap", "chrono-judge-mixed", "chrono-judge-registration"}),
    (routes, {"chrono-judge-routes", "chrono-judge-filemap"}),
    (cost, {"chrono-judge-cost", "chrono-judge-filemap", "chrono-judge-registration"}),
]:
    tools = tomllib.loads((host / manifest).read_text())["tools"]
    assert set(tools) == {"http:" + command for command in commands}
    for name, declaration in tools.items():
        assert declaration == default_tools[name]
