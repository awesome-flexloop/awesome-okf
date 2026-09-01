---
type: Concept
title: "frogmouth：终端 Markdown 浏览器（omnibox/历史/书签/forge 快览）"
description: 基于 Textual 的终端 Markdown 浏览器：复用 Rich 的 Markdown 渲染组件并对接 front-matter 解析器，以 16 项 omnibox 别名命令、256 条历史 deque 与 XDG 持久化书签驱动本地/远程文档浏览。
tags: [textualize, frogmouth]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources:
  - id: "frogmouth"
    resource: "/references/frogmouth.md"
    title: "Frogmouth 仓库信源登记"
---
# frogmouth：终端 Markdown 浏览器（omnibox/历史/书签/forge 快览）

## 概述

Frogmouth（`frogmouth.app.app:run`，版本 0.9.x，MIT，F-FM-01/02/04）是一个完全跑在 Textual 之上的终端 Markdown 文档浏览器。它把「浏览文档」这件事拆成三个可插拔的坐标：**omnibox 命令分派**（定位到哪）、**History/Bookmarks 持久化**（记到哪）、**forge 快览**（快速跳到 GitHub/GitLab/BitBucket/Codeberg 的 raw 文件）。文档的渲染则完全交给 Rich 的 `Markdown` 组件，只通过 `parser_factory` 注入 front-matter 插件，几乎不自己写渲染逻辑（F-FM-05）。

> 事实范围：F-FM-01..22（app + screens + widgets + data + utility）。

应用结构（F-FM-03）：`MarkdownViewer(App[None])` 在 `on_mount()` 中 `push_screen(Main(...))`，`Main(Screen)` 以 BINDINGS 挂 15 条快捷键（F-FM-11），在 `compose()` 中依次 yield `Omnibox`、`Horizontal(Navigation + Viewer)`、`Footer`（F-FM-12）。整套交互核心是「类型化位置 + 命令别名」的组合。

## 复用了哪些核心原语

Frogmouth 是本仓库生态中「复用胜过自研」的典例，几乎不自己实现任何渲染，而是把 Textual/Rich 的原语当作积木拼成产品：

- **Rich Markdown 组件 ↔ F-FM-05 ↔ F-R-061**：`Viewer.compose()` 直接 yield `Markdown(PLACEHOLDER, parser_factory=...)`（F-FM-05），其渲染管线完全来自 Rich 的 `Markdown(JupyterMixin)`（F-R-061）+ 令牌派发（F-R-057 `MarkdownElement`、F-R-060 `MarkdownContext`）。frogmouth 只补一个参数：用 `MarkdownIt("gfm-like").use(front_matter.front_matter_plugin)` 给解析期加 front-matter 前置元数据插件——解析器仍复用 Rich 的 MarkdownIt 构建器，只是自定义了 `parser_factory` 回调。
- **Textual Markdown 小部件的文档加载能力**：`document` 属性返回 `self.query_one(Markdown)`，本地/远程加载都落在 `Markdown.load()` 与 `Markdown.update()` 上（F-FM-08/09），文本更新后靠 `scroll_home`/`scroll_to_widget` 定位（F-FM-05），对应 Textual 滚动 API 原语 **F-T-051**。
- **Screen/App/消息系统原语**：`push_screen`（F-FM-03）、自定义消息 `LocationChanged`/`HistoryUpdated` 继承 `ViewerMessage`（F-FM-07）、`on_markdown_link_clicked` 事件处理（F-FM-13）、`@work(exclusive=True)` 后台任务（F-FM-08/09）——这些沿用 Textual 的 message pump 与 worker 基础设施，frogmouth 只做业务分派。
- **标准小部件组装**：`Omnibox(Input)`（F-FM-15）、`Navigation` 内的 `TabbedContent` 四面板、`FilteredDirectoryTree(DirectoryTree).filter_paths`（F-FM-22）——全部是开箱即用组件之上的薄包装。

## 本工具示范的独有机制

frogmouth 的真正价值不在渲染而在「命令/导航编排」，四组机制可独立复用到任何文档型 TUI：

- **16 项 omnibox 别名命令分派（F-FM-15/16/17）**：`Omnibox._ALIASES` 把 `a/b/bm/bb/c/cb/cd/cl/gh/gl/h/l/obs/toc/q/?` 映射到语义命令，分派靠 `getattr(self, f"command_{alias}")` 完成（F-FM-15）。输入按顺序判定：URL → `RemoteViewCommand`；存在的文件/目录 → `LocalViewCommand`/`LocalChdirCommand`；命令别名 → `_execute_command`；否则兜底当本地路径（F-FM-16）。它还内置两个命令正则 `_GUESS_BRANCH`/`_SPECIFIC_BRANCH` 解析 `<owner>/<repo> [file]` 或 `owner/repo:branch` 触发 forge 快览（F-FM-16）。
- **deque 历史 + XDG 持久化（F-FM-06/18/19）**：`History` 用 `deque(..., maxlen=256)` 天然限长，`remember`/`back`/`forward`/`__delitem__` 维护 `_current` 游标并与 `visit()` 的「先行加载、跳成功后落历史」协作成型（F-FM-06/10）。书签与历史各自落到 `xdg_data_home().../bookmarks.json|history.json`，靠 `JSONEncoder` 子类把 `Path`/`URL` 序列化为 `str`，读回时以 `is_likely_url` 重建类型（F-FM-19）；配置则以 `@lru_cache` 缓存 `load_config()`（F-FM-18）。
- **Forge 快览：raw URL 探测链（F-FM-17/21）**：`build_raw_forge_url` 缺省文件名 `README.md`，branch 未给时依次尝试 `("main", "master")` 的 `HEAD` 探测（`httpx` `client.head` + `raise_for_status`），命中即返回 `URL`——四家仓各自一套 URL 模板（F-FM-21）。`command_github`/`command_obsidian`/`command_discord` 等把别名派发到具体动作（F-FM-17）。
- **远程加载的 content-type 分流（F-FM-09/10）**：`_remote_load` 用 `AsyncClient().get(follow_redirects=True, ...)`，`text/plain|text/markdown|text/x-markdown` 开头才更新文档，否则转交 `open_url` 打开浏览器——区分「文档」与「非文档」两种远程资源。
- **链接点击的判定优先级（F-FM-13）**：依次尝试 `is_likely_url` → URL 相对解析 → 本地存在 → 相对父目录 → `#` 锚点 `goto_anchor` → 兜底 `ErrorDialog`，覆盖绝大多数 Markdown 跳转语义。

## 相关概念

- [08-rich-markdown.md](/concepts/08-rich-markdown.md)（Rich Markdown 渲染管线，frogmouth 的渲染后端）
- [00-ecosystem-overview.md](/concepts/00-ecosystem-overview.md)（Textual 卫星应用生态总览）