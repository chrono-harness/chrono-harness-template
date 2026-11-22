"""Verify the two generated adopter configurations."""
import json
from pathlib import Path
import sys
import tomllib

empty, selected = map(Path, sys.argv[1:])
manifest = Path(".config/mise/conf.d/chrono-harness.toml")
assert not (empty / manifest).exists()
config = tomllib.loads((selected / manifest).read_text())
assert set(config["tools"]) == {"http:chrono-pr"}
assert json.loads((selected / ".chrono-harness/pr.json").read_text())["base"] == "dev"
assert (selected / ".github/workflows/harness-check.yml").is_file()
assert config["tasks"]["harness-check"]["run"] == "python3 check.py"
