---
type: Concept
title: "toolong：mmap 日志扫描、时间戳自适应与双平台 watcher"
description: 基于 Textual 的终端日志查看器：复用 RegexHighlighter 的 _combine_regex/命名组做日志高亮，以 mmap 双向扫描断行与时间戳、自适应轮转 17 种时间戳格式，并用 Darwin/poll 双平台 watcher 驱动 tail。
tags: [textualize, toolong]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources:
  - id: "toolong"
    resource: "/references/toolong.md"
    title: "Toolong 仓库信源登记"
---
# toolong：mmap 日志扫描、时间戳自适应与双平台 watcher

## 概述

Toolong（`toolong.cli:run`，1.5.0，MIT，F-TL-01/02）是一个构建在 Textual 之上的终端日志查看/追踪/合并/搜索应用。它的三根支柱是：**mmap 驱动的断行与时间戳扫描**（`scan_line_breaks`/`scan_timestamps`，F-TL-10/11）、**时间戳格式的自适应轮转**（`TimestampFormat` + 17 种格式，F-TL-12/13）、以及**跨平台 watcher**（Darwin 的 selector 与其余平台的 poll 双实现，F-TL-14..16）。界面层则由 `LogLines(ScrollView)`、`LogView(Horizontal)`、`TabbedContent` + `Lazy` 组合而成（F-TL-17/20）。

> 事实范围：F-TL-01..24（cli + ui + log_file + timestamps + watcher + log_view + log_lines + format_parser + highlighter）。

入口行为（F-TL-02/03）：`@click.command()` 的 `run` 以 `sys.__stdin__.isatty()` 分流——有 tty 且有文件时进入 `UI(...).run()`；无文件仅 tty 时打印帮助；管道输入时则用 `NamedTemporaryFile` + `/dev/tty` + `subprocess.Popen` 把 stdin 实时灌给另一个 `tl` 子进程，父进程以 `SelectSelector()` 圆滑监听 stdin（F-TL-03）。

## 复用了哪些核心原语

toolong 不自己实现高亮，而是把 Rich 的 `RegexHighlighter` 当作白板直接改造：

- **LogHighlighter ↔ F-TL-23 ↔ F-R-016**：`LogHighlighter(RegexHighlighter)` 设 `base_style = "repr."`，`highlights` 用 `_combine_regex`（以 `"|"` 连接）拼出 `ipv4`/`ipv6`/`eui64`/`eui48`/`uuid`/`bool_true`/`bool_false`/`none`/`number`/`str`/`path` 等**命名组**正则，再对每个 highlight 调 `text.highlight_regex(re_highlight, style_prefix=self.base_style)`（F-TL-23）。这与 Rich 的 `ReprHighlighter(RegexHighlighter)`（F-R-016）在结构上完全同构——同样是 `base_style="repr."` + `_combine_regex` 组合命名组——toolong 只是换了一组面向日志语义的命名组，并刻意注释掉了 `url` 组、对 `>=10_000` 字符的文本直接 `return` 跳过（F-TL-23）。
- **Textual 扫描/渲染原语**：`LogLines(ScrollView, inherit_bindings=False)` 的 16 条滚动 BINDINGS（F-TL-20）、`@work(thread=True)` 的 `run_scan` 后台扫描（F-TL-21）、`data_bind(...)` 把 `LogView.tail/show_line_numbers/...` 绑定到子组件（F-TL-17）、`Lazy` 延迟挂载（F-TL-06）、`Suggester`/`Validator` 驱动的查找与输入校验（F-TL-19/24）、`ModalScreen`（`GotoScreen`/`HelpScreen`，F-TL-24）、`@rich.repr.auto(angular=True)` 的 repr 调试（F-TL-07）。
- **标准容器组装**：`TabbedContent` 承载每文件一个 `TabPane`（或合并视图单一 pane），配合 `Lazy(LogView(...))` 按需加载（F-TL-06），面板可见性由 `on_mount` 时 `query(TabPane)` 数量决定。

## 本工具示范的独有机制

toolong 面向「超大日志 + tail 实时性 + 跨格式」做了四个可复用的工程机制：

- **mmap 双向扫描 + 分批 yield（F-TL-10/11）**：`scan_line_breaks` 创建 `mmap.mmap`（Windows 用 `access=ACCESS_READ`、POSIX 用 `prot=PROT_READ`，F-TL-10），以 `rfind(b"\n", 0, position)` 从尾部向前收集断行；`scan_timestamps` 则以 `readline()` 逐行累计字节位置并 append `(line_no, position, timestamp)` 元组（F-TL-11）。两者都采用「每 1000 个且 `time.monotonic()-break_time > batch_time`(0.25s) 就 `yield` 一批」的节流策略，避免扫描时阻塞 UI。
- **时间戳格式自适应轮转（F-TL-12/13）**：`TIMESTAMP_FORMATS` 共 17 项（12 个 ISO-8601 变体 + 多国常见日志格式 + 毫秒/秒级 epoch，F-TL-12，数据注记取自 logmerger 项目）。`TimestampScanner.scan()` 对 `>10_000` 的超长行截取前 10000 字符，按序 `re.search`，一旦命中就把该 `TimestampFormat` 从原索引 `del` 再 `insert(0, ...)` 提到队首——让**命中率高的格式持续靠前**、逐步收敛到当前日志的实际格式（F-TL-13）。
- **双平台 watcher（F-TL-14..16）**：`get_watcher()` 在 Darwin 返回 `SelectorWatcher`、其余返回 `PollWatcher`（F-TL-14）。`PollWatcher.run()` 用 `lseek(fileno,0,SEEK_CUR)` + `read(fileno, 64*1024)` 逐描述符轮询，一轮无成功读取 `time.sleep(0.05)`（F-TL-15）；`SelectorWatcher` 则以 `DefaultSelector` + `EVENT_READ` 注册文件描述符，`select(timeout=0.1)` 事件驱动读取（F-TL-16）。两者共享 `WatcherBase` 的 `_file_descriptors`/`_thread`/`_exit_event` 与 `scan_chunk` 的断行定位（F-TL-14）。
- **日志格式解析轮转（F-TL-22）**：`FormatParser` 用 `FORMATS = [JSONLogFormat(), CommonLogFormat(), CombinedLogFormat()]`，命中后把该格式轮转到队首（`self._formats = [*self._formats[index:], *self._formats[:index]]`），未命中回退 `default_log_format`；`HTTP_GROUPS` 把 HTTP 状态码首数字映射到颜色（`4→red`、`5→reverse red` 等）。合并视图靠 `merge_log_files` 收集 `(timestamp, line_no, log_file)` 后 `sort(key=itemgetter(0,1))`（F-TL-21）。
- **自然排序 + 多级缓存（F-TL-05/20）**：`CompareTokens` 用 `@total_ordering` + `tokens = [int(token) if token.isdigit() else token.lower() ...]` 对文件路径做人类直觉排序（F-TL-05）；`LogLines` 用 4 个 `LRUCache`（`_render_line_cache`/`_search_index`/`_line_cache`/`_text_cache`）与 `LineReader(Thread)` + `Queue(maxsize=1000)` 按需异步读行（F-TL-19/20）。

## 相关概念

- [04-rich-highlighters.md](/concepts/04-rich-highlighters.md)（Highlighter 体系，`LogHighlighter` 的直接父级与 F-R-016 出处）
- [00-ecosystem-overview.md](/concepts/00-ecosystem-overview.md)（Textual 卫星应用生态总览）