# Chrono Harness 仓库起点

点击 GitHub 的 **Use this template → Create a new repository**，创建并克隆你的仓库。安装 mise 后，在仓库根目录执行以下命令。

```sh
mise trust
mise run harness-setup
```

在开发分支上，每次安装都会从 GitHub Releases 选择所选组件的最新测试版，并校验当前平台的 SHA-256。首次安装会从 origin 识别 GitHub 仓库与默认分支。AI 打开根目录的 AGENTS.md 或 CLAUDE.md 即可阅读默认工作规则。

默认安装全部组件。工具选装、增补本仓指令和 Issue 路线图见[使用说明](.chrono-harness/USAGE.md)。已有项目使用 [Copier 配方](https://github.com/chrono-harness/chrono-harness-copier)。组件清单和开发入口见 [Chrono Harness](https://github.com/chrono-harness/chrono-harness-main)。
