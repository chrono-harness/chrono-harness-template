# 仓库工作说明

工作前阅读本仓的[公共约定和工具入口](.chrono-harness/USAGE.md)。产品职责见本仓 README。

## 本仓开发

修改 [scaffold](scaffold) 会影响下游生成的文件。[copier.yml](copier.yml) 定义工具选择。[模板检查](.github/workflows/template.yml) 给出空选、单选和全选三个生成命令，再由 [check.py](check.py) 核对结果。
