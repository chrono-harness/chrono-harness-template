# 使用说明

在仓库根目录运行 `mise trust` 和 `mise run harness-setup`。安装清单为 `.config/mise/conf.d/chrono-harness.toml`。其中 `[settings].disable_tools` 默认为空。要取消某项工具，把对应的 mise 工具名加入这个数组并提交。例如 `disable_tools = ["http:chrono-cache"]`。再次运行 setup 后，mise 会按本仓选择工作。

首次准备宿主需要 Git 和 mise。mise 根据自身的平台选择读取本仓清单中的 SHA-256。若取消安装 `chrono-host-bootstrap`，setup 通过 `mise install-into` 将同一发行安装到工作树外的临时目录，命令结束时删除。系统 SHA-256 工具读取所选文件，`cmp` 将实际摘要的 mise 编码与配置命令的完整输出按字节比较。该输出暂存于工作树外，setup 退出时删除。校验通过才运行 `prepare-template`。首次执行依赖 mise 的平台识别、PATH 中的系统工具，以及从核验到按原路径启动时文件保持稳定。

根 [CLAUDE.md](../CLAUDE.md) 包含本仓接纳的基础指令全文。规则选择在 `.chrono-harness/rules.json`。开始任务时运行 `mise run harness-setup` 刷新根指南，成功后重新阅读本仓的 `AGENTS.md` 或 `CLAUDE.md`。仓库追加说明见根 `CLAUDE.md`。




用 `mise exec -- chrono-pr pr-reminders` 查看本地提醒，再运行 `mise exec -- chrono-pr pr-status --pr NUMBER --head-sha SHA` 查询 GitHub。

chrono-pr 的仓库和目标分支来自 origin。平台提供的事件或 Git 远端 HEAD 决定默认分支。PR 查询的必需检查与时限可在 `.chrono-harness/pr-policy.json` 配置。

新建 GitHub Issue 即可使用随仓路线图。默认的 Issue 和里程碑工作流跟随本仓默认分支；登记 `.chrono-harness/release.json` 的 `version` 后，路线图可按该版本归集事项。

本地检查使用 runner 保管原件的仓库，可在首次 setup 并提交宿主配置后，从仓库根目录运行以下命令。选装后再次运行 `mise run harness-setup`，将生成的宿主保留策略提交到仓库。

```sh
uvx --from copier==9.19.1 copier update --defaults --vcs-ref :current: --answers-file .chrono-harness/template-answers.yml -d local_check_retention=true
```
