# 使用说明

在仓库根目录运行 `mise trust` 和 `mise run harness-setup`。安装清单为 `.config/mise/conf.d/chrono-harness.toml`。其中 `[settings].disable_tools` 默认为空。要取消某项工具，把对应的 mise 工具名加入这个数组并提交。例如 `disable_tools = ["http:chrono-cache"]`。再次运行 setup 后，mise 会按本仓选择工作。

首次准备宿主需要 Git 和 mise。mise 根据自身的平台选择读取本仓清单中的 SHA-256。若取消安装 `chrono-host-bootstrap`，setup 通过 `mise install-into` 将同一发行安装到工作树外的临时目录，命令结束时删除。setup 将清单中的 `sha256:` 和 64 位小写十六进制摘要解码为一条校验记录，由系统 SHA-256 工具的检查模式读取已打开的程序文件。校验通过才运行 `prepare-template`。首次执行依赖 mise 的平台识别、PATH 中的系统工具，以及从核验到按原路径启动时文件保持稳定。

根 AGENTS.md 指向 CLAUDE.md。默认的 `.chrono-harness/rules.json` 采用 `{"mode":"all"}`，上游新增规则也会被采用。用 `{"mode":"all","exclude":["规则 ID"]}` 排除指定规则，或用 `{"mode":"only","include":["规则 ID"]}` 只采用所选规则。setup 会刷新根指南的规则正文，生成块之外可保留本仓指令。

chrono-pr 的仓库和目标分支来自 origin。平台提供的事件或 Git 远端 HEAD 决定默认分支。PR 查询的必需检查与时限可在 `.chrono-harness/pr-policy.json` 配置。用 `mise exec -- chrono-pr pr-reminders` 查看工作树的本地提醒。

新建 GitHub Issue 即可使用随仓路线图。默认的 Issue 和里程碑工作流跟随本仓默认分支；登记 `.chrono-harness/release.json` 的 `version` 后，路线图可按该版本归集事项。
