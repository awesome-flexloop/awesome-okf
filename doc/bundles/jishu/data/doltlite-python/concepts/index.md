# 概念索引（Concepts）

本目录收录 doltlite-python 的核心概念文档。

## 概念文件

| 文件 | 内容 |
|------|------|
| [doltlite-python 概述](00-overview.md) | 产品定位、符号劫持原理、包结构、关键设计约束 |
| [bootstrap() 加载机制](01-bootstrap-mechanism.md) | 幂等性设计、环境标记、库路径解析、异常类 |
| [跨平台符号劫持策略](02-platform-strategies.md) | Linux RTLD_GLOBAL vs macOS shim+re-exec 原理与对比 |
| [wheel tag 与构建系统](03-wheel-and-build.md) | py3-none 策略、cibuildwheel 配置、lockstep 版本管理、CI 流程 |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-bootstrap-mechanism
02-platform-strategies
03-wheel-and-build
```
