# Chrono Harness 仓库起点

点击 GitHub 的 **Use this template → Create a new repository**，创建并克隆你的仓库。安装 mise 后，在仓库根目录执行以下命令。

```sh
mise trust
mise run harness-setup
```

模板默认在每次安装时为所选组织工具查找最新公开测试版，并校验当前平台的 SHA-256。所有分支和直接检出的提交使用同一默认通道。要在本次安装选择最新正式版，运行 `CHRONO_TOOL_CHANNEL=stable mise run harness-setup`。也可以用 `CHRONO_TOOL_CHANNEL` 指定完整发行标签，每个选中的工具都须发布该标签。[默认工具发行进度](https://github.com/chrono-harness/chrono-harness-main/issues/15)

首次安装会从 origin 识别 GitHub 仓库与默认分支。运行 `mise current` 查看实际采用的版本。AI 打开根目录的 AGENTS.md 或 CLAUDE.md 即可阅读默认工作规则。

默认安装全部组件。工具选装、增补本仓指令和 Issue 路线图见[使用说明](.chrono-harness/USAGE.md)。已有项目使用 [Copier 配方](https://github.com/chrono-harness/chrono-harness-copier)。组件清单和开发入口见 [Chrono Harness](https://github.com/chrono-harness/chrono-harness-main)。
