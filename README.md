# chrono-harness 仓库模板

在新仓库或已有仓库的根目录运行一次 Copier，选择这个项目实际使用的工具。可留空，可多选。选装工具的发行版本、平台地址和 SHA-256 都写入本仓配置。

```sh
uvx --from copier==9.19.1 copier copy --vcs-ref v0.1.0-alpha.1 gh:chrono-harness/chrono-harness-template .
mise trust
mise install
```

选择“生成业务检查”并填写项目现有的测试命令，模板会生成 GitHub Actions 和本地入口。维护者与 AI 都能运行 `mise run harness-check`。已有 CI 可以保留其入口，只选所需工具。

每个宿主的选择保存于 `.chrono-harness/template-answers.yml`，使用说明在 `.chrono-harness/USAGE.md`。先提交本仓的改动，再运行 `uvx --from copier==9.19.1 copier update --vcs-ref :current: --answers-file .chrono-harness/template-answers.yml` 调整选择。取消选项会移除模板管理的对应配置。工具由 mise 安装在工作树外。升级或回退某个工具，只需调整该仓对应的发行版本、地址及校验值。

开发分支为 `dev`。正式版使用从 `dev` 验收后晋升到 `main` 的提交。
