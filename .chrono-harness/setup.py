"""Bind rendered host settings to this checkout and refresh its selected rules."""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

host = Path(".chrono-harness")


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def identity():
    # Read the declared origin even when Git rewrites its transport using insteadOf.
    url = git("config", "--get", "remote.origin.url")
    if re.match(r"^(?:[^@:/]+@)?[^:/]+:", url) and "://" not in url:
        user_host, path = url.split(":", 1)
        hostname = user_host.split("@")[-1]
    else:
        parsed = urlsplit(url)
        hostname, path = parsed.hostname, parsed.path.lstrip("/")
    path = path.removesuffix(".git").rstrip("/")
    if hostname not in ("github.com", "ssh.github.com") or not re.fullmatch(r"[\w.-]+/[\w.-]+", path, re.ASCII):
        raise ValueError("origin must identify a GitHub owner/repository")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if os.environ.get("GITHUB_ACTIONS") == "true" and event_path:
        repo = json.loads(Path(event_path).read_text()).get("repository", {})
        if repo.get("full_name", "").casefold() == path.casefold() and repo.get("default_branch"):
            return path, repo["default_branch"]
    for line in git("ls-remote", "--symref", "origin", "HEAD").splitlines():
        match = re.fullmatch(r"ref: refs/heads/([^\s]+)\s+HEAD", line)
        if match:
            return path, match[1]
    raise ValueError("origin does not advertise a default branch")


def replace(path, text):
    if path.exists() and path.read_text() == text:
        return
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as tmp:
        tmp.write(text)
    os.replace(tmp.name, path)


def main():
    repository, branch = identity()
    tools = json.loads(subprocess.check_output(["mise", "ls", "--current", "--json"]))
    pr = host / "pr.json"
    if "http:chrono-pr" in tools:
        settings = json.loads((host / "pr-policy.json").read_text())
        settings.update(repository=repository, base=branch)
        replace(pr, json.dumps(settings, indent=2) + "\n")
    elif pr.exists():
        pr.unlink()
    answers = host / "template-answers.yml"
    text = answers.read_text()
    for key, value in [("repository", repository), ("dev_branch", branch)]:
        text, count = re.subn(rf"^{key}:.*$", lambda _: key + ": " + json.dumps(value), text, flags=re.M)
        if count != 1:
            raise ValueError(f"expected one {key} in {answers}")
    replace(answers, text)
    if "http:chrono-instructions" in tools:
        subprocess.run(["mise", "exec", "--", "chrono-instructions", "sync-rules", "--host-root", "."], check=True)
    print(f"Configured {repository} on {branch}")


if __name__ == "__main__":
    main()
