# chrono-harness 仓库模板

在已有仓库的根目录运行 Copier。默认勾选全部 18 个 Chrono 命令和 Verus。用空格取消任意工具，也可以全部取消。工具从各自版本固定的发行下载，mise 按 SHA-256 校验，安装在工作树外。选中 Verus 会一并安装其依赖的 Rust 1.95.0。支持 Linux x86_64 和 macOS arm64。

```sh
uvx --from copier==9.19.1 copier copy --vcs-ref v0.1.0-alpha.4 gh:chrono-harness/chrono-harness-template .
mise trust
mise install
```

每个仓库的 `AGENTS.md` 都是指向本仓 `CLAUDE.md` 的相对符号链接。公共约定由模板维护，随版本放入本仓 `.chrono-harness/USAGE.md`。维护者可以直接在本仓 `CLAUDE.md` 末尾追加“本仓开发”，写明源码、测试和本地检查入口。该段由本仓维护，模板升级会合并已提交的定制。Agent 在本仓检出内即可读到两部分。

本仓选项保存在 `.chrono-harness/template-answers.yml`，本地命令见 `.chrono-harness/USAGE.md`。开发用 `dev`，通过验收的正式版从 `main` 发布。

选择生成业务检查时，填写项目现有的检查命令和运行平台。本地与 GitHub Actions 都会执行 `mise run harness-check`。已有登记式检查的项目可以沿用自己的工作流。

先提交工作树里的本地改动。要调整本仓安装的工具，运行下面的命令重新选择，然后运行 `mise install`。取消选项后，本仓的安装清单会移除对应工具。共享缓存仍可能供其他仓库使用。

```sh
uvx --from copier==9.19.1 copier update --vcs-ref :current: --answers-file .chrono-harness/template-answers.yml
```

升级公共指令和模板时，将 `:current:` 换为目标发行标签。Copier 将模板变更与本仓已提交的定制合并，重叠修改由本仓处理。审核生成的 diff 后提交。
