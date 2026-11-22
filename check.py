"""Verify the default installation and explicit tool choices."""
import json
from pathlib import Path
import sys
import tomllib

empty, selected, full = map(Path, sys.argv[1:])
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
    assert not (host / ".chrono-harness/rules.json").exists()
    assert not (host / ".chrono-harness/instructions").exists()
    usage = (host / ".chrono-harness/USAGE.md").read_text()
    assert ("chrono-instructions rules --host-root ." in usage) == (host == full)

expected = ['http:chrono-cache', 'http:chrono-ci', 'http:chrono-distribution', 'http:chrono-harness', 'http:chrono-host-bootstrap', 'http:chrono-host-release', 'http:chrono-inputs', 'http:chrono-instructions', 'http:chrono-judge-ci', 'http:chrono-judge-cost', 'http:chrono-judge-filemap', 'http:chrono-judge-mixed', 'http:chrono-judge-projects', 'http:chrono-judge-registration', 'http:chrono-judge-routes', 'http:chrono-judge-workflow', 'http:chrono-pr', 'http:chrono-worktree', 'http:verus']
default_tools = tomllib.loads((full / manifest).read_text())["tools"]
assert default_tools.pop("rust") == {"version": "1.95.0", "profile": "minimal"}
assert set(default_tools) == set(expected)
for tool in default_tools.values():
    assert set(tool["platforms"]) == {"linux-x64", "macos-arm64"}
