# 概念文档索引

本目录包含 repo2jupyterlite 的核心概念文档，按学习路径排序。

## 入门

- [00-repo2jupyterlite简介](00-introduction.md) — 项目是什么、核心能力、与JupyterLite/Binder的关系
- [01-快速开始](01-getting-started.md) — 安装CLI和BinderLite环境、第一个构建示例

## 核心概念

- [02-CLI命令使用详解](02-cli-usage.md) — CLI参数、fetch/build两阶段流程、ContentProvider检测机制
- [03-BinderLite Web应用](03-binderlite-web.md) — FastAPI路由、双重重定向、懒构建触发、slug编码
- [04-仓库提供者系统](04-repo-providers.md) — ContentProvider链、GitHubRepoProvider异步API、双层LRU缓存、认证
- [05-Publisher存储系统](05-publisher-system.md) — Publisher抽象接口、LocalFilesystemPublisher零拷贝、哨兵文件、HTTP缓存
- [06-构建流程与缓存策略](06-build-process.md) — CLI/BinderLite构建流程对比、JupyterLite CLI调用、缓存雪崩防护

## 高级主题

- [07-前端URL解析机制](07-frontend-detectors.md) — React应用、ParsedRepoURL、GitHub URL检测规则、Webpack构建
- [08-整体架构总结](08-architecture-summary.md) — 双模式架构全景、数据流图、设计决策、扩展点

```{toctree}
:hidden:

00-introduction
01-getting-started
02-cli-usage
03-binderlite-web
04-repo-providers
05-publisher-system
06-build-process
07-frontend-detectors
08-architecture-summary
```
