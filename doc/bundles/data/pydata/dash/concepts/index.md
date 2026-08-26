# 概念索引

本目录包含 Dash 框架核心概念的中文教程，按学习路径排列。

## 入门概念

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | Dash简介：Plotly出品的Python Web应用框架，MIT许可证，React+Flask/FastAPI/Quart多后端，响应式编程模型，版本4.4.1 |
| [01-app-architecture.md](01-app-architecture.md) | 应用架构：前后端分离（Python后端+React前端dash-renderer）、布局树(Component Tree)、assets静态文件、pages多页面路由 |
| [02-callback-system.md](02-callback-system.md) | 回调系统：@callback装饰器、Input/Output/State依赖、callback_context、prevent_update/no_update、多输入多输出、回调链、背景回调 |
| [03-component-system.md](03-component-system.md) | 组件系统：dcc/html/dash_table组件包、Component基类、to_plotly_json()序列化、ComponentRegistry、MCP工具集成 |

## 建议学习路径

1. **新手入门**：00-introduction → 01-app-architecture → 运行 [examples/first-dash-app.md](../examples/first-dash-app.md) 中的 Hello World
2. **核心机制**：02-callback-system → 03-component-system → 运行交互式图表示例
3. **源码溯源**：阅读 [references/dash-app-init.md](../references/dash-app-init.md) 理解底层实现

```{toctree}
:maxdepth: 7

00-introduction
01-app-architecture
02-callback-system
03-component-system
```
