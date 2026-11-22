# chrono-harness 仓库模板

在已有仓库的根目录运行 Copier。默认勾选全部 18 个 Chrono 命令和 Verus。用空格取消任意工具，也可以全部取消。工具从各自版本固定的发行下载，mise 按 SHA-256 校验，安装在工作树外。选中 Verus 会一并安装其依赖的 Rust 1.95.0。支持 Linux x86_64 和 macOS arm64。

```sh
uvx --from copier==9.19.1 copier copy --vcs-ref v0.1.0-alpha.8 gh:chrono-harness/chrono-harness-template .
mise trust
mise run harness-setup
```

每个仓库的 `AGENTS.md` 链接到本仓 `CLAUDE.md`。本仓只维护自己的说明。选装指令工具后，agent 在任务开始时运行 `mise exec -- chrono-instructions rules --host-root .`，读取上游当前已发布的规则。上游修改后，下次读取自动生效。

缺省接纳所有当前和以后新增的基础规则。需要定制时在本仓创建 `.chrono-harness/rules.json`。

| 需求 | 配置 |
| --- | --- |
| 全部接纳 | 省略文件或 `{"mode":"all"}` |
| 屏蔽个别 ID | `{"mode":"all","exclude":["job.wait"]}` |
| 仅接纳部分 ID | `{"mode":"only","include":["artifact.cleanup","job.wait"]}` |
| 关闭基础规则 | `{"mode":"off"}` |

查阅[上游规则及稳定 ID](https://raw.githubusercontent.com/chrono-harness/chrono-harness-instructions/published-rules/rules.json)。本地追加说明始终在 `CLAUDE.md`。启用继承需要网络和 curl；读取失败时命令报告失败。关闭继承可以离线工作。

选择生成业务检查时，填写项目现有的检查命令和运行平台。本地与 GitHub Actions 都会执行 `mise run harness-check`。已有登记式检查的项目可以沿用自己的工作流。

先提交工作树里的本地改动。要调整本仓安装的工具，运行下面的命令重新选择，然后运行 `mise run harness-setup`。取消选项后，本仓的安装清单会移除对应工具。共享缓存仍可能供其他仓库使用。

```sh
uvx --from copier==9.19.1 copier update --vcs-ref :current: --answers-file .chrono-harness/template-answers.yml
```

从 alpha.5 迁移时，先核对旧生成块、catalog、manifest 和 host-context 中的本地修改。将选择迁入 `.chrono-harness/rules.json`，把本仓追加说明放回 `CLAUDE.md`。确认继承结果后删除旧生成块和已经迁移的输入。

升级模板本身时，将 `:current:` 换为目标发行标签。Copier 将模板变更与本仓已提交的定制合并，重叠修改由本仓处理。审核生成的 diff 后提交。

全部工具和业务检查都取消时，可以跳过 mise 步骤。选择记录位于 `.chrono-harness/template-answers.yml`，规则取舍归宿主的 `.chrono-harness/rules.json`。
