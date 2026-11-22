"""Exercise a new adopter with empty and selected profiles."""
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib

SOURCE = Path(__file__).resolve().parent
def render(destination, features, *answers):
    subprocess.run([
        "uvx", "--from", "copier==9.19.1", "copier", "copy",
        "--defaults", "--vcs-ref", "HEAD", "-d", "features=" + json.dumps(features),
        *answers, SOURCE.as_posix(), destination.as_posix(),
    ], check=True)

with tempfile.TemporaryDirectory() as scratch:
    root = Path(scratch)
    empty = root / "empty"
    render(empty, [])
    manifest = Path(".config/mise/conf.d/chrono-harness.toml")
    assert not (empty / manifest).exists()
    selected = root / "selected"
    render(selected, ["pr"], "-d", "repository=chrono-harness/chrono-harness-template",
           "-d", "generate_check=true", "-d", "check_command=python3 check.py")
    config = tomllib.loads((selected / manifest).read_text())
    assert set(config["tools"]) == {"http:chrono-pr"}
    assert json.loads((selected / ".chrono-harness/pr.json").read_text())["base"] == "dev"
    assert (selected / ".github/workflows/harness-check.yml").is_file()
    assert config["tasks"]["harness-check"]["run"] == "python3 check.py"
