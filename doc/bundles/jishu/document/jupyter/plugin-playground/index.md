---
okf_version: "0.2"
---

# Plugin Playground 知识库

本知识包是 JupyterLab 插件快速原型工具 [Plugin Playground](https://github.com/jupyterlab/jupyterlab-plugin-playground) 的系统化中文教程，基于源码深度阅读生成，覆盖从 Hello World 到联邦扩展与CSS隔离的完整知识体系。所有内容均溯源至 plugin-playground 源码（`external/libs/jupyter/plugin-playground/src/` 目录核心模块），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [Plugin Playground 简介](concepts/00-introduction.md) — 什么是 Plugin Playground、安装方法、核心功能、与传统扩展开发的对比、使用场景。
* [整体架构与数据流](concepts/01-architecture-overview.md) — 三大核心类（PluginLoader/PluginTranspiler/ImportResolver）的职责划分、插件加载七步流程、模块解析四级回退链。
* [JupyterLab 插件基础结构](concepts/02-plugin-basics.md) — JupyterFrontEndPlugin 对象结构、id/autoStart/requires/optional/provides/activate 字段详解、插件数组、生命周期。

## 核心机制（concepts/）

* [浏览器端 TypeScript 转译](concepts/03-typescript-transpilation.md) — TypeScript 转 CommonJS 的完整流程、三个自定义 Transformer（export/import/default）、AsyncFunction 沙箱执行、旧格式回退机制。
* [模块解析系统](concepts/04-module-resolution.md) — 四级回退解析策略（已知模块→联邦扩展→本地文件→CDN RequireJS）、semver 版本协商、包名解析、index 文件自动解析。
* [插件加载流程](concepts/05-plugin-loader.md) — PluginLoader.load() 七步详解：转译→沙箱创建→代码执行→插件提取→Token解析→Schema发现→CSS样式发现、错误处理。
* [Token 依赖注入系统](concepts/06-token-system.md) — 双轨Token获取（import+Proxy拦截 vs 字符串名）、requires/optional/provides 参数顺序规则、默认导入合成、命令自动补全。

## 高级主题（concepts/）

* [联邦扩展与共享模块](concepts/07-federated-extensions.md) — Webpack Module Federation 共享作用域加载、window._JUPYTERLAB 容器、联邦扩展自动发现、semver 版本范围匹配、KNOWN_MODULES 注册表。
* [样式处理与CSS隔离](concepts/08-style-handling.md) — 动态style标签注入、CSS @import重写、快照栈事务机制（快照-提交-回滚）、package.json声明样式、多插件样式隔离。
* [导出、分享与工具栏集成](concepts/09-export-share.md) — ZIP/Wheel导出、链接分享、工具栏按钮、Run on Save、命令面板集成、侧边栏面板（Token/Example/LoadedPlugins）、AI辅助创建。

## 实战示例（examples/）

* [最小插件 Hello World](examples/01-hello-world.md) — 从零创建最简单的JupyterLab插件，理解插件基本结构和最小代码量。对应概念：[JupyterLab插件基础结构](concepts/02-plugin-basics.md)、[插件加载流程](concepts/05-plugin-loader.md)。
* [Token 依赖注入](examples/02-token-injection.md) — 使用requires/optional注入命令面板、启动器、文件浏览器等服务，掌握参数顺序和空值处理。对应概念：[Token依赖注入系统](concepts/06-token-system.md)、[联邦扩展与共享模块](concepts/07-federated-extensions.md)。
* [自定义命令与UI面板](examples/03-custom-command.md) — 创建包含自定义命令、ReactWidget主区域面板、侧边栏、键盘快捷键的完整插件。对应概念：[JupyterLab插件基础结构](concepts/02-plugin-basics.md)、[导出分享与工具栏集成](concepts/09-export-share.md)。
* [本地模块导入与CSS样式](examples/04-local-import.md) — 多文件插件开发、相对路径导入TypeScript模块、CSS样式注入、@import链重写、样式快照回滚。对应概念：[模块解析系统](concepts/04-module-resolution.md)、[样式处理与CSS隔离](concepts/08-style-handling.md)。

## 信源登记簿（references/）

* [Plugin Playground 源码索引](references/source-index.md) — 核心源码模块路径、模块职责、公开API映射表、辅助工具函数清单。
* [PluginLoader 与 PluginTranspiler API](references/loader-transpiler-api.md) — PluginLoader 和 PluginTranspiler 类的完整API签名、IPluginLoadResult/IResult接口、插件类型定义。
* [ImportResolver API](references/resolver-api.md) — ImportResolver 类的完整API签名、四级解析策略链、CSS处理方法、快照栈事务API、RequireJS隔离加载。

## 信任与生命周期说明

* **status 判定依据**：全部 17 个内容文档（10 个概念 + 4 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 plugin-playground 源码（`external/libs/jupyter/plugin-playground/src/` 目录）8个核心模块的逐行阅读与215条事实提取（F-001~F-215），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-02-22`（生成后6个月）。Plugin Playground 的核心架构（浏览器端TS转译+AsyncFunction沙箱+Proxy拦截+快照栈CSS）自JupyterLab 4.x以来相对稳定；6个月后需重新评估是否有JupyterLab大版本升级影响API兼容性。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-22）；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 17 个内容文档（10 个概念 + 4 个示例 + 3 个信源登记），另含 4 个子目录 index.md 与根 index.md、facts.md、insights.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
