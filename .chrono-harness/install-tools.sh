#!/bin/sh
# Run from the checkout root. Publish a complete, verified mise selection by rename.
set -eu
fail() { echo "$*" >&2; exit 1; }
dev_branch='dev'
branch=${CHRONO_INSTALL_BRANCH:-}
if [ -z "$branch" ]; then
    branch=$(git symbolic-ref --quiet --short HEAD) || {
        test "${GITHUB_ACTIONS:-}" = true && test "$(git rev-parse HEAD)" = "${GITHUB_SHA:-}" ||
            fail 'Detached checkout requires CHRONO_INSTALL_BRANCH.'
        case "${GITHUB_EVENT_NAME:-}" in
            pull_request)
                case "${GITHUB_HEAD_REF:-}" in
                    integration/*|main|"$dev_branch") branch=$GITHUB_HEAD_REF ;;
                    *) branch=${GITHUB_BASE_REF:?missing pull request base branch} ;;
                esac ;;
            *) case "${GITHUB_REF:-}" in
                   refs/heads/*) branch=${GITHUB_REF#refs/heads/} ;;
                   *) fail 'Set CHRONO_INSTALL_BRANCH for this deployment.' ;;
               esac ;;
        esac
    }
fi
case "$branch" in
    main) channel=pinned ;;
    "$dev_branch"|feature/*|integration/*) channel=preview ;;
    *) channel=pinned ;;
    
esac
case "$(uname -s)-$(uname -m)" in
    Linux-x86_64) platform=linux-x64; asset=linux-x86_64; seed_sha=be0575ae8ae2b3a8597498f610134a2a6394ca6a15dd085d91f7ec9edef96a1c ;;
    Darwin-arm64) platform=macos-arm64; asset=macos-aarch64; seed_sha=6fa5e57a6d8260fe18def416c6f5d57430b2d767d8f6a8d20109f11f7c182fe4 ;;
    *) fail 'Unsupported installation platform.' ;;
esac
verify() {
    if command -v sha256sum >/dev/null 2>&1; then digest=$(sha256sum < "$1")
    else digest=$(shasum -a 256 < "$1"); fi
    test "${digest%% *}" = "$2" || fail "SHA-256 mismatch for $1"
}
config_dir=$PWD/.config/mise/conf.d
work=$(mktemp -d "$config_dir/.chrono-install.XXXXXXXX")
downloads=
cleanup() {
    rm -rf -- "$work"
    if [ -n "$downloads" ]; then rm -rf -- "$downloads"; fi
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
manifest=$work/mise.toml
: > "$manifest"
disabled=$(mise settings get disable_tools)
enabled() {
    case "$disabled" in *\"http:$1\"*) return 1 ;; *) return 0 ;; esac
}
resolved=$config_dir/zz-chrono-harness-resolved.toml
export MISE_IGNORED_CONFIG_PATHS="${MISE_IGNORED_CONFIG_PATHS:+$MISE_IGNORED_CONFIG_PATHS:}$resolved"
export MISE_TRUSTED_CONFIG_PATHS="$work${MISE_TRUSTED_CONFIG_PATHS:+:$MISE_TRUSTED_CONFIG_PATHS}"
if [ "$channel" = pinned ]; then
    cp .chrono-harness/pinned-tools.toml "$manifest"
else
    while read -r command repository; do
        enabled "$command" || continue
        if [ -z "$downloads" ]; then
            temp_parent=$(cd "${TMPDIR:-/tmp}" && pwd -P)
            case "$temp_parent/" in "$(pwd -P)/"*) temp_parent=/tmp ;; esac
            downloads=$(mktemp -d "$temp_parent/chrono-install.XXXXXXXX")
            seed=$downloads/chrono-host-release
            curl --disable --proto '=https' --proto-redir '=https' --fail --silent --show-error --location \
                "https://github.com/chrono-harness/chrono-harness-host-release/releases/download/v0.1.0-alpha.26/chrono-host-release-$asset" -o "$seed"
            verify "$seed" "$seed_sha"
            chmod 700 "$seed"
        fi
        pages=$downloads/${repository#*/}
        if [ ! -d "$pages" ]; then
            mkdir "$pages"
            page=1
            while :; do
                set -- --disable --proto '=https' --fail --silent --show-error
                auth=
                if [ -n "${GITHUB_TOKEN:-}" ]; then
                    auth="Authorization: Bearer $GITHUB_TOKEN"
                    set -- "$@" -H @-
                fi
                if curl "$@" -D "$pages/headers" -o "$pages/$page.json" \
                    "https://api.github.com/repos/$repository/releases?per_page=100&page=$page" <<AUTH
$auth
AUTH
                then :
                else
                    fetch_status=$?
                    echo "Failed to read releases for $repository (page $page)." >&2
                    exit "$fetch_status"
                fi
                # Fetch the next numbered page only when GitHub advertises it.
                if grep -i '^link:' "$pages/headers" | grep -Fq 'rel="next"'; then page=$((page + 1))
                else break; fi
            done
        fi
        selector=$channel
"$seed" resolve-install-v1 --mise-tool "$command" "$repository" "$selector" \
            "$command-linux-x86_64" "$command-macos-aarch64" "$pages"/*.json >> "$manifest"
    done <<'TOOLS'
chrono-cache chrono-harness/chrono-harness-cache
chrono-ci chrono-harness/chrono-harness-ci
chrono-diagnostics chrono-harness/chrono-harness-diagnostics
chrono-distribution chrono-harness/chrono-harness-distribution
chrono-harness chrono-harness/chrono-harness-runner
chrono-host-bootstrap chrono-harness/chrono-harness-host-bootstrap
chrono-host-release chrono-harness/chrono-harness-host-release
chrono-inputs chrono-harness/chrono-harness-inputs
chrono-instructions chrono-harness/chrono-harness-instructions
chrono-judge-ci chrono-harness/chrono-harness-judge-ci
chrono-judge-cost chrono-harness/chrono-harness-judge-cost
chrono-judge-filemap chrono-harness/chrono-harness-judge-filemap
chrono-judge-mixed chrono-harness/chrono-harness-judge-mixed
chrono-judge-projects chrono-harness/chrono-harness-judge-projects
chrono-judge-registration chrono-harness/chrono-harness-judge-registration
chrono-judge-routes chrono-harness/chrono-harness-judge-routes
chrono-judge-workflow chrono-harness/chrono-harness-judge-workflow
chrono-pr chrono-harness/chrono-harness-pr
chrono-test-git chrono-harness/chrono-harness-test-git
chrono-test-git-profile chrono-harness/chrono-harness-test-git
chrono-worktree chrono-harness/chrono-harness-worktree
TOOLS
fi
# The nested config takes precedence over any previous checkout receipt.
# mise installs explicit versions and verifies fresh downloads. Also hash cache hits.
mise -C "$work" install
for command in chrono-cache chrono-ci chrono-diagnostics chrono-distribution chrono-harness chrono-host-bootstrap chrono-host-release chrono-inputs chrono-instructions chrono-judge-ci chrono-judge-cost chrono-judge-filemap chrono-judge-mixed chrono-judge-projects chrono-judge-registration chrono-judge-routes chrono-judge-workflow chrono-pr chrono-test-git chrono-test-git-profile chrono-worktree; do
    enabled "$command" || continue
    expected=$(mise config get --file "$manifest" "tools.\"http:$command\".platforms.$platform.checksum")
    executable=$(mise -C "$work" which "$command")
    verify "$executable" "${expected#sha256:}"
done
mv -f "$manifest" "$config_dir/.chrono-harness-installed"
