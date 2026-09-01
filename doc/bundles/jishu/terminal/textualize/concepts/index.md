# Textualize 概念文档索引

按学习路径排列的核心概念文档，从生态总览到 rich 渲染基石、textual 消息驱动模型，再到 7 个卫星工具：

| 序号 | 主题 | 说明 |
|------|------|------|
| 00 | [生态总览](00-ecosystem-overview.md) | Textualize 12 仓库依赖图谱与深度分层（rich → textual → 卫星） |
| 01 | [rich 渲染协议与控制台](01-rich-console-and-protocol.md) | 协议驱动递归归约：is_renderable/RichCast/Console.render 与 Segment 流 |
| 02 | [Text 对象与标记语言](02-rich-text-and-markup.md) | Text 核心对象、Span 区间样式与控制台 markup 语法 |
| 03 | [Style 样式系统](03-rich-style-system.md) | Style 位掩码存储、parse/from_color 工厂方法与 StyleStack |
| 04 | [Highlighter 体系](04-rich-highlighters.md) | 从 RegexHighlighter 到 ReprHighlighter 基于命名分组正则的着色 |
| 05 | [Segment 与 Measurement](05-rich-segment-and-measure.md) | Segment 渲染货币与 __rich_measure__ 测量协议 |
| 06 | [Table](06-rich-table.md) | Column/Row 数据模型与基于 Measurement 的自适应列宽计算 |
| 07 | [Panel 与 Box](07-rich-panel-and-box.md) | 32 字符盒模型、Panel 容器与 18 种边框常量 |
| 08 | [Markdown](08-rich-markdown.md) | MarkdownIt 令牌流到元素类的映射 |
| 09 | [Progress](09-rich-progress.md) | Task 采样窗口、滑动平均速度与列插件 ProgressColumn |
| 10 | [Live](10-rich-live.md) | 自动刷新线程与 RenderHook 拦截动态渲染 |
| 11 | [Layout](11-rich-layout.md) | row/column 分割器与 Region 区域映射 |
| 12 | [渲染管线深潜](12-rich-render-pipeline-and-export.md) | 递归渲染、Capture 捕获与 HTML/SVG 导出 |
| 13 | [App 入口](13-textual-app-entry.md) | App 类变量契约、run 循环与 notify 通知 |
| 14 | [消息系统](14-textual-message-system.md) | Message/MessagePump、派发约定与消息合并（textual 核心） |
| 15 | [Reactive](15-textual-reactive.md) | validate→watcher→compute→refresh 响应式链路 |
| 16 | [DOM/Widget/内置组件](16-textual-dom-widget-builtin.md) | DOMNode→Widget→Button/Input/DataTable/TextArea 继承链 |
| 17 | [事件与绑定](17-textual-events-bindings.md) | 事件体系、BINDINGS、@on 装饰器与冒泡声明 |
| 18 | [Screen 栈](18-textual-screen-stack.md) | push/pop/switch 屏幕栈、模态与模式管理 |
| 19 | [CSS/Worker/Driver](19-textual-css-worker-driver.md) | 样式表引擎、Worker 后台任务与五 Driver 抽象层 |
| 20 | [rich-cli](20-rich-cli.md) | rich 全能力的命令行暴露面 |
| 21 | [frogmouth](21-frogmouth.md) | 终端 Markdown 浏览器（omnibox/历史/书签） |
| 22 | [toolong](22-toolong.md) | mmap 日志扫描、时间戳自适应与双平台 watcher |
| 23 | [trogon](23-trogon.md) | Click 内省到 TUI 表单的自动生成 |
| 24 | [textual-dev](24-textual-dev.md) | devtools 控制台与 CLI 输出重定向 |
| 25 | [textual-serve](25-textual-serve.md) | 三行代码把 TUI 变成 Web 应用 |
| 26 | [textual-web](26-textual-web.md) | ganglion 客户端、包协议与托管发布 |

## 学习路径

```
阶段1 入门：00 → 01 → 02
阶段2 rich 核心：03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12
阶段3 textual 核心：13 → 14 → 15 → 16 → 17 → 18 → 19
阶段4 卫星工具：20 → 21 → 22 → 23 → 24 → 25 → 26
阶段5 生态整合：重读 00 与 /references/index.md
```

```{toctree}
:hidden:
:maxdepth: 2

00-ecosystem-overview
01-rich-console-and-protocol
02-rich-text-and-markup
03-rich-style-system
04-rich-highlighters
05-rich-segment-and-measure
06-rich-table
07-rich-panel-and-box
08-rich-markdown
09-rich-progress
10-rich-live
11-rich-layout
12-rich-render-pipeline-and-export
13-textual-app-entry
14-textual-message-system
15-textual-reactive
16-textual-dom-widget-builtin
17-textual-events-bindings
18-textual-screen-stack
19-textual-css-worker-driver
20-rich-cli
21-frogmouth
22-toolong
23-trogon
24-textual-dev
25-textual-serve
26-textual-web
```