# chrono-harness-template 使用说明

本仓维护供独立仓库选装工具的 Copier 模板。

开发分支为 `dev`。日常 PR 合入开发分支，正式版从 `main` 发布。

首次检出运行 `mise trust` 和 `mise run harness-setup`。工具版本见 [.config/mise/conf.d/chrono-harness.toml](../.config/mise/conf.d/chrono-harness.toml)。

开始每项任务时运行 `mise exec -- chrono-instructions rules --host-root .`，读取并遵循标准输出中的上游规则。完整规则和本仓开发步骤见根 [CLAUDE.md](../CLAUDE.md)。

用 `mise exec -- chrono-pr pr-reminders` 查看本地提醒，再运行 `mise exec -- chrono-pr pr-status --pr NUMBER --head-sha SHA` 查询 GitHub。

## 本仓验证

修改 `copier.yml` 配置选项，修改 `scaffold/` 改变新宿主的文件。按 `.github/workflows/template.yml` 的渲染命令分别生成默认、空选和单选宿主，再用 `check.py` 检查这些宿主。
