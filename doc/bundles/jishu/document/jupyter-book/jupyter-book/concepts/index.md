# Jupyter Book CLI 概念文档

按学习路径编号排列。建议从 [00 v2 双层架构](00-v2-architecture.md) 开始阅读。

| 编号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [v2 双层架构](00-v2-architecture.md) | Python+TS 双层、白标设计、与 v1 的关系 |
| 01 | [Python 入口与 nodeenv](01-python-entry-nodeenv.md) | main() 执行流程、Node.js 查找/安装、平台适配 |
| 02 | [TS CLI 命令体系](02-ts-cli-commands.md) | commander 注册、clirun 执行器、init/build/start/clean/templates |
| 03 | [与 myst-cli 的关系](03-myst-cli-relationship.md) | 白标环境变量、代码复用比例、功能等价性 |
| 04 | [模板系统](04-template-system.md) | myst-templates 仓库、template.yml、jtex 渲染整合 |
| 05 | [从 v1 迁移](05-migration-from-v1.md) | _config.yml→myst.yml、Sphinx→myst-cli、指令兼容 |

```{toctree}
:hidden:
:maxdepth: 7

00-v2-architecture
01-python-entry-nodeenv
02-ts-cli-commands
03-myst-cli-relationship
04-template-system
05-migration-from-v1
```
