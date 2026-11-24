# 使用说明

在仓库根目录运行 `mise trust` 和 `mise run harness-setup`。安装清单为 `.config/mise/conf.d/chrono-harness.toml`。其中 `[settings].disable_tools` 默认为空。要取消某项工具，把对应的 mise 工具名加入这个数组并提交。例如 `disable_tools = ["http:chrono-cache"]`。再次运行 setup 后，mise 会按本仓选择工作。

首次准备宿主需要 Git 和 mise。若取消安装 `chrono-host-bootstrap`，setup 会从同一版本清单下载当前平台的临时程序，核对 SHA-256，完成仓库绑定后删除临时程序。

根 AGENTS.md 指向 CLAUDE.md。默认的 `.chrono-harness/rules.json` 采用 `{"mode":"all"}`，上游新增规则也会被采用。用 `{"mode":"all","exclude":["规则 ID"]}` 排除指定规则，或用 `{"mode":"only","include":["规则 ID"]}` 只采用所选规则。setup 会刷新根指南的规则正文，生成块之外可保留本仓指令。

chrono-pr 的仓库和目标分支来自 origin。平台提供的事件或 Git 远端 HEAD 决定默认分支。PR 查询的必需检查与时限可在 `.chrono-harness/pr-policy.json` 配置。用 `mise exec -- chrono-pr pr-reminders` 查看工作树的本地提醒。

新建 GitHub Issue 即可使用随仓路线图。默认的 Issue 和里程碑工作流跟随本仓默认分支；登记 `.chrono-harness/release.json` 的 `version` 后，路线图可按该版本归集事项。
