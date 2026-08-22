# JupyterLab OKF Wiki 更新日志

## v0.1.0 - 2026-08-22

### 新增

**概念文档（10 篇）**：
- 00-introduction.md：概述与知识地图（项目定位、特性、架构哲学、学习路径）
- 01-architecture-overview.md：整体架构概览（Monorepo 结构、技术栈、五层架构、数据流）
- 02-application-shell.md：应用框架与 Shell 布局（JupyterFrontEnd、LabShell 8 区域、启动流程）
- 03-plugin-system.md：插件系统与依赖注入（Token、JupyterFrontEndPlugin、激活机制）
- 04-service-layer.md：服务层与后端通信（ServiceManager、12个子管理器、REST/WebSocket）
- 05-document-widget-system.md：文档注册与 Widget 工厂模式（DocumentRegistry、Context、文件类型链）
- 06-notebook-cells.md：Notebook 与 Cell 架构（三层 Widget 结构、Cell 类型、执行流程）
- 07-extension-ecosystem.md：扩展生态系统（Federated 扩展、Python 扩展管理器、CLI）
- 08-build-and-modes.md：构建系统与运行模式（Core/Dev/App 三模式、Rspack、jlpm）
- 09-key-subsystems.md：关键子系统（PageConfig、命令、Signal、Disposable、StateDB、Router）

**示例文档（2 篇）**：
- 01-minimal-extension.md：最小扩展 Hello World（命令注册、命令面板、菜单集成）
- 02-custom-file-type.md：自定义文件类型 .xyz 查看器（文件类型注册、Widget 工厂）

**参考资料（1 篇）**：
- source-code-map.md：JupyterLab 源码文件地图（Python 后端 + 前端 40+ 包路径索引）

**导航文件**：
- index.md：Wiki 首页与导航
- concepts/index.md、examples/index.md、references/index.md：各子目录索引

### 方法论

- 遵循七概念方法论（R→I→E→V→C）完成 R（事实采集）、I（架构洞察）、E（批量生成）阶段
- 遵循 source-code-to-okf-wiki 工作流：信源先行、分批生成（每批≤7）、Index 最后写
- 所有类名/API 名称均基于源码验证（ServiceManager、DocumentRegistry、JupyterLab、LabShell、NotebookPanel、Cell 等）
