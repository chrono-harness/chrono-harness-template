# Chrono Harness 仓库起点

点击 GitHub 的 **Use this template → Create a new repository**，创建并克隆你的仓库。安装 mise 后，在仓库根目录执行以下命令。

```sh
mise trust
mise run harness-setup
```

模板默认在每次安装时为所选组织工具查找最新公开测试版，并校验当前平台的 SHA-256。所有分支和直接检出的提交使用同一默认通道。可用 Copier 为各工具分别保存正式版、测试版或精确标签，也可在单次安装时覆盖这些选择。[混合选版与单次覆盖示例](.chrono-harness/USAGE.md#保存各工具的版本选择) · [默认工具发行进度](https://github.com/chrono-harness/chrono-harness-main/issues/15)

首次安装会从 origin 识别 GitHub 仓库与默认分支。运行 `mise current` 查看实际采用的版本。AI 打开根目录的 AGENTS.md 或 CLAUDE.md 即可阅读默认工作规则。

GitHub Actions 依赖默认每日检查。频率、更新范围和自动合并可按仓库调整。[设置或停用 Dependabot](.chrono-harness/USAGE.md#依赖更新)

默认安装全部组件。工具选装、增补本仓指令和 Issue 路线图见[使用说明](.chrono-harness/USAGE.md)。已有项目使用 [Copier 配方](https://github.com/chrono-harness/chrono-harness-copier)。组件清单和开发入口见 [Chrono Harness](https://github.com/chrono-harness/chrono-harness-main)。
