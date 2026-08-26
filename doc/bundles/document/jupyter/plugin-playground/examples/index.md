# 实战示例

本目录包含 4 个完整的可运行示例，每个示例对应一个或多个核心概念，提供从简单到复杂的渐进式学习路径。所有示例代码均可直接在 Plugin Playground 中粘贴运行。

* [最小插件 Hello World](01-hello-world.md) — 从零创建最简单的JupyterLab插件，理解插件基本结构和最小代码量（不到20行代码）。对应概念：[JupyterLab插件基础结构](../concepts/02-plugin-basics.md)、[插件加载流程](../concepts/05-plugin-loader.md)。
* [Token 依赖注入](02-token-injection.md) — 使用requires/optional注入命令面板、启动器、文件浏览器等核心服务，掌握参数顺序规则、空值处理、provides服务提供、常用Token速查表。对应概念：[Token依赖注入系统](../concepts/06-token-system.md)、[联邦扩展与共享模块](../concepts/07-federated-extensions.md)。
* [自定义命令与UI面板](03-custom-command.md) — 创建包含自定义命令、ReactWidget主区域面板、侧边栏Widget、键盘快捷键的完整插件，涵盖isEnabled/isToggled状态管理、单例Widget模式。对应概念：[JupyterLab插件基础结构](../concepts/02-plugin-basics.md)、[导出分享与工具栏集成](../concepts/09-export-share.md)。
* [本地模块导入与CSS样式](04-local-import.md) — 多文件插件开发实战，包含TypeScript模块相对导入、CSS样式文件注入、@import链重写、样式快照回滚机制。对应概念：[模块解析系统](../concepts/04-module-resolution.md)、[样式处理与CSS隔离](../concepts/08-style-handling.md)。

## 建议学习路径

1. **新手入门**：从 [Hello World](01-hello-world.md) 开始，理解最基本的插件结构
2. **依赖注入**：学习 [Token依赖注入](02-token-injection.md)，掌握如何使用JupyterLab核心服务
3. **UI构建**：通过 [自定义命令与UI面板](03-custom-command.md)，学会创建丰富的用户界面
4. **多文件开发**：通过 [本地模块导入与CSS样式](04-local-import.md)，掌握生产级插件的组织方式

```{toctree}
:hidden:
:maxdepth: 7

01-hello-world
02-token-injection
03-custom-command
04-local-import
```
