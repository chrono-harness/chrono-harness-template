# chrono-harness 仓库模板

新建仓库时，在 GitHub 的 **Use this template** 中创建 `chrono-harness-<业务名>`。每个仓库的 `mise.toml` 固定基础工具的版本、所属仓库的发行地址，以及 Linux x86_64 和 macOS arm64 的 SHA-256。

本地安装 [mise](https://mise.jdx.dev/getting-started.html) 后，在仓库根目录运行：

```sh
mise trust
mise install
mise exec -- chrono-pr pr-reminders
```

安装的二进制由 mise 管理，位置在工作树外。升级某个工具时只改该工具的版本、下载地址和校验值；回退时使用该工具上一已验版本的数据。GitHub Actions 使用相同清单安装。业务工具及 Rust 等开发依赖由各仓库按需选择。
