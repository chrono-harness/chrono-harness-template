"""Publish only the exact selected tag and verified bytes; retry incomplete draft uploads."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from plan import require, sha_of


repo = os.environ["GITHUB_REPOSITORY"]


def request(path, **kwargs):
    req = Request("https://api.github.com/repos/" + repo + "/" + path,
                  headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                           "Content-Type": "application/json", "Accept": "application/vnd.github+json"}, **kwargs)
    with urlopen(req, timeout=45) as reply:
        return json.load(reply)


def optional(path):
    try:
        return request(path)
    except HTTPError as err:
        if err.code == 404:
            return None
        raise


def gh(*args):
    subprocess.run(["gh", *map(str, args), "--repo", repo], check=True)


def sums(directory, binary):
    names = [binary + "-macos-aarch64", binary + "-linux-x86_64"]
    expected = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}
    lines = (directory / "SHA256SUMS").read_text().splitlines()
    require(sorted(lines) == sorted(digest + "  " + name for name, digest in expected.items()),
            "asset checksums differ from SHA256SUMS")
    expected["SHA256SUMS"] = hashlib.sha256((directory / "SHA256SUMS").read_bytes()).hexdigest()
    return expected


def tag_at(tag, sha):
    ref = optional("git/ref/tags/" + tag)
    if ref is None:
        request("git/refs", method="POST", data=json.dumps({"ref": "refs/tags/" + tag, "sha": sha}).encode())
    require(sha_of(repo, "tags/" + tag) == sha, "tag points to different source")


def recorded(release, tag, prerelease):
    require(release["tag_name"] == tag and release["prerelease"] == prerelease, "different release kind")
    return {a["name"]: a["digest"].removeprefix("sha256:") for a in release["assets"] if a["state"] == "uploaded"}


def main():
    mode, tag, sha = (os.environ[k] for k in ("MODE", "TAG", "SOURCE_SHA"))
    config = json.loads(Path(".chrono-harness/release.json").read_text())
    binary = config.get("binary") if config["kind"] == "binary" else None
    dist = Path(os.environ["DIST"])
    dist.mkdir(exist_ok=True)
    stable = mode == "stable"
    release = optional("releases/tags/" + tag)
    if stable:
        parent = os.environ["PREVIEW"]
        require(sha_of(repo, "tags/" + parent) == sha, "preview tag moved")
        if binary:
            gh("release", "download", parent, "--dir", dist)
    elif release and not release["draft"]:
        # A retried build may produce different bytes. The original release is immutable.
        require(sha_of(repo, "tags/" + tag) == sha, "preview tag moved")
        with tempfile.TemporaryDirectory() as tmp:
            if binary:
                gh("release", "download", tag, "--dir", tmp)
            expected = sums(Path(tmp),binary) if binary else {}
            require(recorded(release, tag, True) == expected, "invalid published preview")
        return
    if not stable and binary:
        names = [binary + "-macos-aarch64", binary + "-linux-x86_64"]
        (dist / "SHA256SUMS").write_text("".join(hashlib.sha256((dist/name).read_bytes()).hexdigest()
                                                  + "  " + name + "\n" for name in names))
    digests = sums(dist, binary) if binary else {}
    if stable:
        require(recorded(request("releases/tags/" + parent), parent, True) == digests, "preview bytes changed")
        if release:
            require(sha_of(repo, "tags/" + tag) == sha, "stable tag points to a different source")
            if not release["draft"]:
                require(recorded(release, tag, False) == digests, "stable assets differ from verified preview")
                return
        # GitHub rejects a non-fast-forward update. Check again at the point of publication.
        if sha_of(repo, "heads/main") != sha:
            request("git/refs/heads/main", method="PATCH", data=json.dumps({"sha": sha, "force": False}).encode())
        require(sha_of(repo, "heads/main") == sha, "main differs from preview")
    tag_at(tag, sha)
    if release is None:
        notes = ("Verified preview " + os.environ["PREVIEW"] + "\nConsumer acceptance: " + os.environ["PROOF"]
                 if stable else "Preview of " + sha)
        flags = [] if stable else ["--prerelease"]
        gh("release", "create", tag, "--verify-tag", "--title", tag, "--notes", notes, "--draft", *flags)
    else:
        require(release["draft"], "expected an incomplete draft")
    if digests:
        gh("release", "upload", tag, *[dist / n for n in digests], "--clobber")
    draft = request("releases/tags/" + tag)
    require(draft["draft"] and recorded(draft, tag, not stable) == digests, "draft differs from checked assets")
    gh("release", "edit", tag, "--draft=false")


if __name__ == "__main__":
    main()
