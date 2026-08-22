# jupyter-cache 概念文档

| 序号 | 文档 | 内容 |
|------|------|------|
| 00 | [简介](/concepts/00-introduction.md) | 功能定位、解决的问题、核心特性 |
| 01 | [快速开始](/concepts/01-getting-started.md) | 安装、CLI基本工作流、Python API快速开始 |
| 02 | [缓存架构设计](/concepts/02-architecture.md) | 双表数据库设计、内容哈希机制、文件布局、LRU淘汰 |
| 03 | [缓存API详解](/concepts/03-cache-api.md) | JupyterCacheBase核心Python API |
| 04 | [Notebook执行与插件](/concepts/04-notebook-execution.md) | 执行器体系、BasicExecutor实现 |
| 05 | [CLI命令详解](/concepts/05-cli-reference.md) | jcache命令行工具完整参考 |
| 06 | [读取器与执行器扩展](/concepts/06-readers-and-executors.md) | 自定义读取器/执行器开发、entry points插件 |
| 07 | [配置项参考](/concepts/07-configuration.md) | 缓存路径、大小限制、执行配置、数据库配置 |
