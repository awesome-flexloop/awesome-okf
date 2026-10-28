# 概念文档

本目录沉淀「WSL + Python 打造 Agent 插件体系」主题的核心概念，按「总架构 → 环境层（WSL/uv）→ 插件层（机制/形态/配方）」组织：

- [stack-architecture](00-stack-architecture.md)：技术栈总架构——环境自由三层栈 + 包可组合双轴的总体决策图与「三声明文件」最小集。
- [wsl-foundation](01-wsl-foundation.md)：WSL2 底座——双层配置体系、systemd、网络模式、GPU 准虚拟化、export/import 快照、文件系统双世界与布局纪律。
- [python-runtime-uv](02-python-runtime-uv.md)：Python 运行时层——uv 工具链定位、Python 版本管理、PEP 723 单文件脚本、workspace 多包单仓机制。
- [plugin-discovery](03-plugin-discovery.md)：插件发现机制四谱——entry points、pluggy、MCP 2026-07-28、Agent Skills 的机制对比与进程边界决策轴。
- [plugin-forms-matrix](04-plugin-forms-matrix.md)：插件三形态选型——Skills（知识）× Tools（执行）× Hooks（生命周期）的选型矩阵。
- [composable-recipe](05-composable-recipe.md)：可组合配方——workspace 成员 + entry points + extras 的完整插件包配方与 MCP 同构方案。

> 机制性事实均回源官方文档（Microsoft Learn / uv / MCP / Python 官方文档），社区经验类内容显式标注。首页见 [index](../index.md)。

```{toctree}
:hidden:
:maxdepth: 2

00-stack-architecture
01-wsl-foundation
02-python-runtime-uv
03-plugin-discovery
04-plugin-forms-matrix
05-composable-recipe
```
