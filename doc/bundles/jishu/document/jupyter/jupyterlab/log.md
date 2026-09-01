# JupyterLab OKF Wiki 更新日志

## v0.2.0 - 2026-08-23

### 完成

E 阶段文档全部生成完毕，bundle 从骨架升级为完整教程：

**概念文档（10 篇，约 17000 字）**：
- 00-introduction.md：概述与知识地图（已有）
- 01-architecture-overview.md：整体架构概览（Monorepo、五层架构、Mermaid图）
- 02-application-shell.md：应用框架与Shell布局（JupyterFrontEnd、ILabShell 8区域、启动时序）
- 03-plugin-system.md：插件系统与依赖注入（Token、JupyterFrontEndPlugin、DI拓扑激活）
- 04-service-layer.md：服务层与后端通信（ServiceManager、14个子管理器、REST/WS）
- 05-document-widget-system.md：文档注册与Widget工厂（DocumentRegistry、Factory模式、Context）
- 06-notebook-cells.md：Notebook与Cell架构（三层Widget、Cell类型、执行流程、窗口化）
- 07-extension-ecosystem.md：扩展生态系统（Federated扩展、ExtensionManager、entry point）
- 08-build-and-modes.md：构建系统与运行模式（Core/Dev/App三模式、Rspack、singletonPackages）
- 09-key-subsystems.md：关键子系统（PageConfig、CommandRegistry、StateDB、Router）

**示例文档（2 篇）**：
- 01-minimal-extension.md：最小扩展Hello World（完整package.json+TypeScript代码）
- 02-custom-file-type.md：自定义文件类型查看器（DocumentRegistry+WidgetFactory实战）

**参考资料（1 篇）**：
- source-code-map.md：源码文件地图（Python后端+103个前端包分类速查）

### 质量保证
- 所有API经Grep级源码验证（JupyterLab lab.ts:21、ILabShell shell.ts:75、ServiceManager manager.ts:48等）
- 所有内容文档frontmatter完整（type/title/description/tags/generated/verified/status/sources）
- 交叉链接使用`/`开头bundle-relative路径

## v0.1.0 - 2026-08-22

### R+I 阶段

- 完成 facts.md（167条事实，含源码路径和行号）
- 完成 insights.md（5个架构洞察+10个核心模式）
- 生成 00-introduction.md 规划10章结构
- 创建 bundle 目录骨架和导航索引
