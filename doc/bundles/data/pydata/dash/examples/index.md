# 示例索引

本目录包含 Dash 框架的可运行代码示例。

| 文档 | 说明 |
|------|------|
| [first-dash-app.md](first-dash-app.md) | Dash第一个应用：从Hello World到交互式散点图回调、输入框+下拉框联动、多输出回调、多页面应用（pages路由）、回调链实时更新，6个渐进式完整代码示例 |

## 示例列表

1. **Hello World**：最小Dash应用，html组件基本用法
2. **交互式散点图**：dcc.Dropdown + dcc.Graph + @callback + plotly.express
3. **表单联动**：多输入+State+按钮触发，生成样式卡片
4. **多输出回调**：一个回调同时更新图表和统计面板
5. **多页面应用**：use_pages + register_page + page_container + path_template动态路由
6. **回调链**：dcc.Interval实时更新 + 回调串联（图表→统计自动更新）

```{toctree}
:maxdepth: 7

first-dash-app
```
