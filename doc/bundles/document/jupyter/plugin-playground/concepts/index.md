# 概念文档

本目录包含 Plugin Playground 的 10 个核心概念文档，按学习路径排列：从入门基础到核心机制再到高级主题，逐步深入。

## 入门与基础

* [00-Plugin Playground 简介](00-introduction.md) — 什么是 Plugin Playground、安装方法、核心功能、与传统扩展开发的对比、使用场景。
* [01-整体架构与数据流](01-architecture-overview.md) — 三大核心类职责划分、插件加载七步流程、模块解析四级回退链、核心数据流。
* [02-JupyterLab 插件基础结构](02-plugin-basics.md) — JupyterFrontEndPlugin 对象、id/autoStart/requires/optional/provides/activate 字段、插件数组、插件生命周期。

## 核心机制

* [03-浏览器端 TypeScript 转译](03-typescript-transpilation.md) — TS→CommonJS转译流程、三个自定义Transformer、AsyncFunction沙箱执行、旧格式回退。
* [04-模块解析系统](04-module-resolution.md) — 四级回退解析策略（已知模块→联邦扩展→本地文件→CDN）、semver版本协商、index文件解析。
* [05-插件加载流程](05-plugin-loader.md) — PluginLoader.load()七步详解、沙箱创建、插件提取、Token解析、Schema发现、CSS发现、错误处理。
* [06-Token 依赖注入系统](06-token-system.md) — 双轨Token获取机制、Proxy属性拦截、requires/optional参数顺序、默认导入合成、命令自动补全。

## 高级主题

* [07-联邦扩展与共享模块](07-federated-extensions.md) — Webpack Module Federation、window._JUPYTERLAB容器、联邦扩展自动发现、共享作用域semver匹配。
* [08-样式处理与CSS隔离](08-style-handling.md) — 动态style标签注入、CSS @import重写、快照栈事务（快照-提交-回滚）、多插件样式隔离。
* [09-导出、分享与工具栏集成](09-export-share.md) — ZIP/Wheel导出、链接分享、工具栏按钮、Run on Save、命令面板、侧边栏面板、AI辅助。

```{toctree}
:hidden:

00-introduction
01-architecture-overview
02-plugin-basics
03-typescript-transpilation
04-module-resolution
05-plugin-loader
06-token-system
07-federated-extensions
08-style-handling
09-export-share
```
