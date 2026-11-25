# 使用说明

在仓库根目录运行 `mise trust` 和 `mise run harness-setup`。绿色模板默认在每次安装时为所选工具查询 GitHub Releases，按公开发布时间选择最新测试版，并校验当前平台的 SHA-256。安装通道适用于任意分支与直接检出的提交。Rust 和 Verus 使用模板登记的配套版本。

用 `CHRONO_TOOL_CHANNEL=stable mise run harness-setup` 只在本次选择最新正式版。`preview` 选择最新测试版，也可填完整标签，如 `v0.1.12`。每个选中的组织工具都需要提供对应发行。安装后用 `mise current` 查看实际版本，日常用 `mise exec -- <命令>`。

在 Copier 的 `tool_install_channels` 中保存项目默认通道。可选 `pinned` 使用 [.config/mise/conf.d/chrono-harness.toml](../.config/mise/conf.d/chrono-harness.toml) 中固定的配方，也可选 `stable`、`preview` 或完整标签。`tool_versions` 可以为单个命令指定精确标签，例如 `{"chrono-pr":"v0.1.12"}`。安装时依次采用本次环境变量、单工具标签和项目默认通道。在 mise 配置的 `[settings]` 中设置 `disable_tools = ["http:chrono-cache"]` 可停用对应工具，再次运行安装即生效。

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
