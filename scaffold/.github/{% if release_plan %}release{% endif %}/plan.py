"""Select the verified commit and release using GitHub and the consumer's landed lockfile."""
import base64
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlencode


def require(ok, message):
    if not ok:
        raise ValueError(message)


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path]))


def check_run(run, repository, branch, workflow, sha):
    require(run.get("repository", {}).get("full_name") == repository, "wrong check repository")
    require(run.get("head_repository", {}).get("full_name") == repository, "wrong head repository")
    require(run.get("path") == ".github/workflows/" + workflow, "wrong workflow path")
    require(run.get("head_branch") == branch and run.get("head_sha") == sha, "wrong check commit")
    require(run.get("event") == "push" and run.get("status") == "completed"
            and run.get("conclusion") == "success", "landed push has no successful check")


def successful_run(repository, branch, workflow, sha):
    query = urlencode({"event": "push", "branch": branch, "head_sha": sha, "per_page": 100})
    path = f"repos/{repository}/actions/workflows/{workflow}/runs?{query}"
    for run in api(path)["workflow_runs"]:
        if run["status"] == "completed" and run["conclusion"] == "success":
            check_run(run, repository, branch, workflow, sha)
            return run
    raise ValueError(f"no successful {workflow} push for {repository}@{sha}")


def check_acceptance(repository, run, consumer):
    path = f"repos/{repository}/actions/runs/{run['id']}/attempts/{run['run_attempt']}/jobs?per_page=100"
    jobs = {job["name"]: job for job in api(path)["jobs"]}
    require(consumer["jobs"] and consumer["step"], "missing consumer acceptance obligations")
    for name in consumer["jobs"]:
        job = jobs.get(name, {})
        require(job.get("conclusion") == "success" and job.get("head_sha") == run["head_sha"],
                f"missing successful consumer on {name}")
        require(any(step["name"] == consumer["step"]
                    and step["conclusion"] == "success" for step in job.get("steps", [])),
                f"missing exercised product on {name}")


def sha_of(repository, ref):
    obj = api(f"repos/{repository}/git/ref/{ref}")["object"]
    require(obj["type"] == "commit" and re.fullmatch(r"[0-9a-f]{40}", obj["sha"]),
            f"{ref} must point directly to a commit")
    return obj["sha"]


def pin_manifest(repository, binary, version, tool):
    pin = tool["version"]
    require(re.fullmatch(re.escape(version) + r"-alpha\.[1-9][0-9]*", pin), "expected the planned preview")
    require(tool["bin"] == binary, "wrong installed executable")
    result = {}
    for key, suffix in [("linux-x64", "linux-x86_64"), ("macos-arm64", "macos-aarch64")]:
        asset = f"{binary}-{suffix}"
        platform = tool["platforms"][key]
        require(platform["url"] == f"https://github.com/{repository}/releases/download/v{pin}/{asset}",
                "consumer installs a different release asset")
        require(re.fullmatch("sha256:[a-f0-9]{64}", platform["checksum"]), "invalid checksum")
        result[asset] = platform["checksum"]
    return "v" + pin, result


def public_preview(repository, tag, checksums):
    release = api(f"repos/{repository}/releases/tags/{tag}")
    require(not release["draft"] and release["prerelease"] and release["tag_name"] == tag,
            "preview is not published")
    assets = release["assets"]
    require(all(asset["state"] == "uploaded" for asset in assets), "incomplete preview assets")
    if checksums is None:
        require(not assets, "unexpected uploaded assets for a Copier source release")
    else:
        digests = {asset["name"]: asset["digest"] for asset in assets}
        require(set(digests) == set(checksums) | {"SHA256SUMS"}, "missing or unexpected preview assets")
        require(all(digests[name] == val for name, val in checksums.items()), "consumer checksums differ")
    return release


def consumer_pin(config, repository, sha):
    consumer = config["consumer"]
    doc = api(f"repos/{consumer['repository']}/contents/{consumer['pin']}?ref={sha}")
    raw = base64.b64decode(doc["content"]).decode()
    if config["kind"] == "copier":
        import yaml
        answers = yaml.safe_load(raw)
        require(answers["_src_path"] in ("gh:" + repository, "https://github.com/" + repository,
                "https://github.com/" + repository + ".git"), "consumer uses another template")
        tag = answers["_commit"]
        require(re.fullmatch("v" + re.escape(config["version"]) + r"-alpha\.[1-9][0-9]*", tag),
                "consumer has not adopted this preview series")
        return tag, None
    import tomllib
    binary = config["binary"]
    tool = tomllib.loads(raw)["tools"]["http:" + binary]
    return pin_manifest(repository, binary, config["version"], tool)


def plan(config, repository, event, event_name):
    require(config["kind"] in ("copier", "binary"), "unsupported release product")
    check_workflow = config["check"]["file"]
    version = config["version"]
    require(re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version), "invalid release version")
    require(event["repository"]["full_name"] == repository, "wrong event repository")
    if event_name == "workflow_run":
        run = event["workflow_run"]
        sha, branch = run["head_sha"], run["head_branch"]
        require(branch in ("dev", "main"), "unsupported release branch")
        check_run(run, repository, branch, check_workflow, sha)
        if branch == "dev":
            require(re.fullmatch(r"[a-f0-9]{40}", sha), "invalid source commit")
            relation = api(f"repos/{repository}/compare/{sha}...dev")["status"]
            require(relation in ("identical", "ahead"), "development branch does not contain this check")
            stable_tag = "v" + version
            path = f"repos/{repository}/git/matching-refs/tags/{stable_tag}"
            if any(ref["ref"] == "refs/tags/" + stable_tag for ref in api(path)):
                stable = api(f"repos/{repository}/releases/tags/{stable_tag}")
                if not stable["draft"] and not stable["prerelease"]:
                    require(stable["tag_name"] == stable_tag, "different stable release")
                    released = sha_of(repository, "tags/" + stable_tag)
                    require(api(f"repos/{repository}/compare/{released}...main")["status"] in ("identical", "ahead"),
                            "main does not contain the published stable release")
                    return {"mode": "complete", "sha": released, "tag": stable_tag}
            return {"mode": "preview", "sha": sha, "tag": f"v{version}-alpha.{run['run_number']}"}
    else:
        require(event_name == "workflow_dispatch" and event["ref"] == "refs/heads/dev", "dispatch from dev")
        sha = None

    consumer = config["consumer"]
    downstream, branch = consumer["repository"], consumer["branch"]
    adopted = sha_of(downstream, "heads/" + branch)
    run = successful_run(downstream, branch, consumer["workflow"], adopted)
    check_acceptance(downstream, run, consumer)
    tag, checksums = consumer_pin(config, repository, adopted)
    selected = sha_of(repository, "tags/" + tag)
    require(sha is None or sha == selected, "main differs from the adopted preview")
    origin = successful_run(repository, "dev", check_workflow, selected)
    require(tag == f"v{version}-alpha.{origin['run_number']}", "tag differs from the verified dev run")
    require(api(f"repos/{repository}/compare/{selected}...dev")["status"] in ("identical", "ahead"),
            "preview is outside the development branch")
    require(api(f"repos/{repository}/compare/main...{selected}")["status"] in ("identical", "ahead"),
            "main cannot fast-forward to the preview")
    public_preview(repository, tag, checksums)
    return {"mode": "stable", "sha": selected, "tag": "v" + version, "preview": tag,
            "consumer": downstream, "adopted": adopted, "proof": run["html_url"]}


if __name__ == "__main__":
    result = plan(json.loads(Path(".chrono-harness/release.json").read_text()),
                  os.environ["GITHUB_REPOSITORY"], json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()),
                  os.environ["GITHUB_EVENT_NAME"])
    print(json.dumps(result))
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        for key, value in result.items():
            print(f"{key}={value}", file=output)
