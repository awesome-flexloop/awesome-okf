# Textualize 示例文档索引

可直接复制运行的实战示例，覆盖 rich 渲染与 textual TUI 应用，以及卫星工具接入：

| 序号 | 示例 | 说明 |
|------|------|------|
| 01 | [rich Console.print 与标记样式](rich-console-markup.md) | Console.print 输出 markup 样式文本，Style.parse/from_color 构造 |
| 02 | [rich Table + Panel + box 组合](rich-table-panel.md) | 表格 + 面板 + 边框常量组合排版 |
| 03 | [rich track 一行进度条](rich-progress-track.md) | 模块级 track 与自定义 ProgressColumn 列 |
| 04 | [textual 最小 App](textual-minimal-app.md) | App 继承 + compose + @on 事件处理 |
| 05 | [textual reactive 计数器](textual-reactive-counter.md) | reactive 状态与 watch 回调自动刷新 |
| 06 | [textual 组件消息流](textual-widget-messages.md) | Button.Pressed / Input.Submitted 消息冒泡与 stop |
| 07 | [trogon @tui 装饰器](trogon-tui-decorator.md) | 为 Click CLI 自动生成 TUI 表单 |
| 08 | [textual-serve 3 行发布](textual-serve-hello.md) | Server("python -m textual").serve() 发布到浏览器 |
| 09 | [textual 屏幕栈与多模式](textual-screen-modes.md) | MODES 模式切换、push_screen 模态对话框与 dismiss 回调 |
| 10 | [textual Worker 后台任务](textual-worker.md) | @work 装饰 async/thread 任务与 StateChanged 状态消息 |
| 11 | [textual DataTable 数据表](textual-datatable.md) | 表格增删改查与 RowSelected/CellSelected 选择消息 |

## 运行要求

- rich 示例：需 `pip install rich`
- textual 示例：需 `pip install textual`
- trogon 示例：需 `pip install trogon`（typer 方式额外 `trogon[typer]`）
- textual-serve 示例：需 `pip install textual-serve` 及可运行的 textual App 模块

```{toctree}
:hidden:
:maxdepth: 2

rich-console-markup
rich-table-panel
rich-progress-track
textual-minimal-app
textual-reactive-counter
textual-widget-messages
trogon-tui-decorator
textual-serve-hello
textual-screen-modes
textual-worker
textual-datatable
```