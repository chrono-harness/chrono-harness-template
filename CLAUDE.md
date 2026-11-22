# 仓库工作说明

从本仓的 README 了解产品职责，按本仓的检查入口验证改动。安装所选工具及跟进 PR 的命令见 [.chrono-harness/USAGE.md](.chrono-harness/USAGE.md)。

在本仓的开发分支提交日常 PR，从 `main` 发布正式版。跨项目通过固定发行的命令或公开接口协作。等待任务和 CI 使用完成事件或通知。安装包与缓存放在工作树外，有长期用途的产物在清理窗口内转存。

## 本仓开发

修改 [scaffold](scaffold) 会影响下游生成的文件。[copier.yml](copier.yml) 定义工具选择。[模板检查](.github/workflows/template.yml) 给出空选、单选和全选三个生成命令，再由 [check.py](check.py) 核对结果。
