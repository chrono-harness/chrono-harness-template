# chrono-harness 仓库模板

组件的用途、开发仓库和示例见 [Chrono Harness 用户与开发者入口](https://github.com/chrono-harness/chrono-harness-main)。

在已有仓库的根目录运行 Copier。默认勾选全部可安装组件和 Verus。`test-git` 提供两个测试命令 `chrono-test-git` 和 `chrono-test-git-profile`。用空格取消任意工具，也可以全部取消。工具从各自版本固定的发行下载，mise 按 SHA-256 校验，安装在工作树外。选中 Verus 会一并安装其依赖的 Rust 1.95.0。 默认选中 diagnostics，也可单选用来回收宿主滚动日志。只选 worktree 的宿主若启用 `.chrono-harness/logging.json`，须同时选择 diagnostics；未启用日志的宿主可取消。选中 worktree、host-bootstrap 或 host-release 时会一并安装它查询项目登记所需的 chrono-judge-registration。选装 host-release 还会安装校验原始构建报告的 host-bootstrap。单选 judge-mixed 会安装 registration，用于原生判官协议。单选 judge-filemap 会安装 registration 和 mixed，分别解释两个提交的登记和变更内容，用于选择受影响的测试。单选 inputs 会为 capture 及带执行单元的 compose 安装 registration。带执行单元的 compose 还使用 routes、FILEMAP 和 mixed。pair 和无执行单元的 compose 可离线单独运行。单选 judge-projects 会安装 FILEMAP、routes 和 registration，用于读取受影响节点、校验计划和原始执行回执，以及解释退役测试。单选 judge-workflow 会安装 projects、routes 和 registration，分别读取项目结果、核对计划与回执、解释固定提交的登记。单选 judge-ci 会安装 FILEMAP 和 projects，用于按变更选择测试、核对项目配对，以及执行选中的计划并收集原始进程回执。完整调度和收集使用随装的 routes、mixed 与 registration。单选 routes 会安装 FILEMAP 和 registration，用于解读影响范围和退役测试。单选 judge-cost 会安装 FILEMAP 和 registration。只生成工作流的仓库可以单选 ci。需要按变更调度执行单元或汇总其报告时，同时选择 ci 和 judge-ci。支持 Linux x86_64 和 macOS arm64。

```sh
uvx --from copier==9.19.1 copier copy --prereleases gh:chrono-harness/chrono-harness-template .
mise trust
mise run harness-setup
```

首次安装选择最新的发布标签，包含预发行版。Copier 将选中的标签和本仓答案写入 `.chrono-harness/template-answers.yml`。

安装时可填写本仓职责、源码位置和验证命令，模板会将它们直接写入根指南。每个仓库的 `AGENTS.md` 链接到本仓的 `CLAUDE.md`。默认生成的根文件包含首次安装、PR 与验证入口，以及 chrono-harness-instructions 发布的默认规则全文。克隆仓库即可阅读。工具的版本和校验值在本仓的 mise 清单中。

模板安装的 `.chrono-harness/rules.json` 默认为 `{"mode":"all"}`，省略该文件同样接受全部当前和以后新增的规则。每次开始任务时，运行 `mise run harness-setup`。选装 instructions 的仓库会用本仓固定版本的 `chrono-instructions sync-rules --host-root .` 读取上游已发布的规则，按本仓选择更新根指南。成功后重新阅读指南。仓库自己的职责、源码位置和检查入口放在生成块之外。同步失败会保留原指南。

| 需求 | 配置 |
| --- | --- |
| 全部接纳 | 省略文件或 `{"mode":"all"}` |
| 屏蔽个别 ID | `{"mode":"all","exclude":["job.wait"]}` |
| 仅接纳部分 ID | `{"mode":"only","include":["artifact.cleanup","job.wait"]}` |
| 关闭基础规则 | `{"mode":"off"}` |

查阅[上游规则及稳定 ID](https://raw.githubusercontent.com/chrono-harness/chrono-harness-instructions/published-rules/rules.json)。本地说明可写在 `CLAUDE.md` 末尾的“本仓追加指令”一节。重新选择工具时，Copier 会保留这些说明。启用继承需要网络和 curl；读取失败时命令报告失败。关闭继承可以离线工作。

选择生成业务检查时，填写项目现有的检查命令和运行平台。本地与 GitHub Actions 都会执行 `mise run harness-check`。已有登记式检查的项目可以沿用自己的工作流。

先提交工作树里的本地改动。要调整本仓安装的工具，运行下面的命令重新选择，然后运行 `mise run harness-setup`。取消选项后，本仓的安装清单会移除对应工具。共享缓存仍可能供其他仓库使用。

```sh
uvx --from copier==9.19.1 copier update --vcs-ref :current: --answers-file .chrono-harness/template-answers.yml
```

从 alpha.5 迁移时，先核对旧生成块、catalog、manifest 和 host-context 中的本地修改。将选择迁入 `.chrono-harness/rules.json`，把本仓追加说明放回 `CLAUDE.md`。确认继承结果后删除旧生成块和已经迁移的输入。

升级模板本身时，将 `:current:` 换为目标发行标签。Copier 将模板变更与本仓已提交的定制合并，重叠修改由本仓处理。审核生成的 diff 后提交。

全部工具和业务检查都取消时，可以跳过 mise 步骤。选择记录位于 `.chrono-harness/template-answers.yml`，规则取舍归宿主的 `.chrono-harness/rules.json`。
