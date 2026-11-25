# 使用说明

在仓库根目录运行 `mise trust` 和 `mise run harness-setup`。每次在 `dev`、`feature/*` 和 `integration/*` 安装，都会重新查询所选工具的公开 GitHub Releases，按 GitHub 的公开发布时间选择最新测试版，并校验当前平台二进制的 SHA-256。缓存命中也要校验。查询或校验失败，安装命令会报错。在本轮开发通道试用中，`main` 的首次安装和重装使用模板随附的固定版本。Rust 和 Verus 按模板登记的配套版本安装。

安装完成后，运行 `mise current` 查看本次选中的版本，日常用 `mise exec -- <命令>`。本地解析结果由 Git 忽略。要停用某个工具，在 `.config/mise/conf.d/chrono-harness.toml` 的 `[settings]` 中设置例如 `disable_tools = ["http:chrono-cache"]`，然后重新运行安装。要为集成分支选定个别版本，用 Copier 的 `integration_tool_tags` 选项，例如 `{"integration/pr-trial":{"chrono-pr":"v0.1.11"}}`。手动检出到提交时，可用 `CHRONO_INSTALL_BRANCH=dev mise run harness-setup` 指定安装所用的分支策略。

首次准备宿主使用 Git、mise 和系统命令。模板会从 origin 识别 GitHub 仓库及其默认分支，再用本次核验过的 `chrono-host-bootstrap` 执行 `prepare-template`。若用户禁用该工具，首次准备仍会从随附配方临时安装一份，校验摘要并在用完后删除。

本仓默认接纳全部上游规则，可在 `.chrono-harness/rules.json` 按 ID 选择。安装后即可从根 [CLAUDE.md](../CLAUDE.md) 阅读本仓选中的规则与追加说明。

用 `mise exec -- chrono-pr pr-reminders` 查看本地提醒，再运行 `mise exec -- chrono-pr pr-status --pr NUMBER --head-sha SHA` 查询 GitHub。

chrono-pr 的仓库和目标分支来自 origin。平台提供的事件或 Git 远端 HEAD 决定默认分支。PR 查询的必需检查与时限可在 `.chrono-harness/pr-policy.json` 配置。

新建 GitHub Issue 即可使用随仓路线图。默认的 Issue 和里程碑工作流跟随本仓默认分支；登记 `.chrono-harness/release.json` 的 `version` 后，路线图可按该版本归集事项。

本地检查使用 runner 保管原件的仓库，可在首次 setup 并提交宿主配置后，从仓库根目录运行以下命令。选装后再次运行 `mise run harness-setup`，将生成的宿主保留策略提交到仓库。

```sh
uvx --from copier==9.19.1 copier update --defaults --vcs-ref :current: --answers-file .chrono-harness/template-answers.yml -d local_check_retention=true
```

若最后一次成功的本地完整检查报告也应到期，在同一条命令加上 `-d 'expire_local_check_slots=[".chrono-harness/state/collection/check.json"]'`，将示例路径换成本仓登记的实际报告路径。默认列表为空。需要长期使用的结果应在窗口内转入持久存储。
