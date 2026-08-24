# 概念文档索引

- [sphinxext-rediraffe 简介](00-introduction.md) — 什么是rediraffe、核心特性、安装方法、与其他方案对比
- [5分钟快速上手](01-getting-started.md) — 3步完成配置：安装、添加extension、配置重定向、构建验证
- [架构概览](02-architecture-overview.md) — 整体架构图、三大核心组件、事件钩子机制、双Builder设计、数据流
- [重定向图模型](03-redirect-graph.md) — 有向图建模、create_graph解析、create_simple_redirects链式压缩、循环检测算法
- [配置项详解](04-configuration.md) — 4个配置项（redirects/branch/template/auto_redirect_perc）的类型、默认值、用法
- [Builder体系详解](05-builders.md) — html/dirhtml自动生成、rediraffecheckdiff CI检查、rediraffewritediff自动写入
- [Jinja2模板系统](06-jinja-templates.md) — 默认模板分析、5个模板变量、自定义模板、URL参数保留、三层降级
- [路径处理与跨平台兼容](07-path-and-cross-platform.md) — Windows/POSIX路径转换、dirhtml目录URL处理、增量JSON记录、冲突检测

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-redirect-graph
04-configuration
05-builders
06-jinja-templates
07-path-and-cross-platform
```
