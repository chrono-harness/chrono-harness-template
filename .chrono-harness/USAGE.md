# 使用说明

在仓库根目录运行 `mise trust` 和 `mise run harness-setup`。绿色模板默认在每次安装时为所选工具查询 GitHub Releases，按公开发布时间选择最新测试版，并校验当前平台的 SHA-256。安装通道适用于任意分支与直接检出的提交。Rust 和 Verus 使用模板登记的配套版本。 安装成功后取得的版本和 Linux、macOS SHA-256 存在 `.chrono-harness/state/tool-selection/versions.toml`。检出中的 `.config/mise/conf.d/selected-chrono-harness.toml` 为 mise 提供对应的下载地址。读取 GitHub 分页失败时，安装器退出并保留上次成功的选版。

### 保存各工具的版本选择

首次准备完成后，在干净的 Git 工作区运行 Copier 更新。下面的命令把仓库默认值设为最新测试版，让 `chrono-pr` 跟随最新正式版，并把 `chrono-diagnostics` 固定到 `v0.1.0`。其余已选工具跟随仓库默认值。

```sh
uvx --from copier==9.19.1 copier update --defaults --vcs-ref :current: \
  --answers-file .chrono-harness/template-answers.yml \
  -d tool_install_channels=preview \
  -d 'tool_versions={"chrono-pr":"stable","chrono-diagnostics":"v0.1.0"}'
mise run harness-setup
```

把 Copier 更新的答案和生成文件一并提交，其他检出和 CI 就会使用相同的选择。`tool_versions` 的键是工具命令名，每个值都可以是 `stable`、`preview` 或精确的发行标签。`tool_install_channels` 还支持 `pinned`，用来读取仓库的固定配方。[固定配方](../.config/mise/conf.d/chrono-harness.toml)

要临时让全部已选组织工具跟随最新测试版，在仓库根目录运行 `CHRONO_TOOL_CHANNEL=preview mise run harness-setup`。下次运行普通的 `mise run harness-setup` 会再次采用保存的逐工具选择和仓库默认值。`CHRONO_TOOL_CHANNEL` 也接受 `stable` 或完整标签；每个已选工具都须提供对应发行。用 `mise current` 查看实际安装的版本。

在 mise 配置的 `[settings]` 中设置 `disable_tools = ["http:chrono-cache"]` 可停用对应工具，再次运行安装即生效。

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
