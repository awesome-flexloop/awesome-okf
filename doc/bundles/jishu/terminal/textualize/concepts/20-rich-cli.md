---
type: Concept
title: rich-cli：rich 全能力的命令行暴露面
description: 解析 rich-cli 如何用一条 `rich` 命令把 Rich 的渲染原语（Console/Text/Syntax/Panel/Table/JSON/Markdown）暴露为标准 CLI，并示范 pager、URL 抓取、Windows VT 等独有的命令行机制。
tags: [textualize, rich-cli, cli, rich]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "rich-cli", resource: "/references/rich-cli.md", title: "Rich CLI 仓库信源登记" }]
---

# rich-cli：rich 全能力的命令行暴露面

## 概述

`rich-cli`（版本 1.8.x，MIT，作者 Will McGugan）是挂在 Rich 之上的"命令行工具箱"（command line toolbox for fancy output），它把 Rich 的终端富输出能力汇总为一条 `rich` 命令（F-RC-01：`[project.scripts] rich = "rich_cli.__main__:run"`）。用户无需写 Python，即可用 `rich 某些资源 [格式开关] [渲染选项]` 对文件、URL 或直接传给命令的文本做高亮渲染。

内部结构极简：核心包 `src/rich_cli/` 仅有五个文件——`__main__.py`（CLI 主入口与渲染调度）、`markdown.py`（Markdown 渲染扩展、为其重挂 CodeBlock）、`pager.py`（分页器集成，基于 Textual 的 `PagerApp`）、`win_vt.py`（Windows 虚拟终端支持）、`__init__.py`（空文件，F-RC-02）。它是观察"一个第三方应用如何大规模复用 Rich 原语"以及"Rich 渲染管线对外如何被驱动"的最小标本。

## 复用了哪些核心原语

`rich-cli` 的实质是把 Rich 的渲染原语作为"运行时库"逐个取用，最终拼成一条命令。从依赖到渲染全链皆可直接在上游源码中核对。

- **依赖钉定（F-RC-01）**：`pyproject.toml` 声明 `rich (>=12.4.0,<13.0.0)`、`textual (>=0.1.18,<0.2.0)`，并配套 `click`、`requests`、`rich-rst`。注意这里 `rich-cli` 反过来依赖 `rich` 与 `textual`，与 [00-ecosystem-overview](/concepts/00-ecosystem-overview.md) 中"Rich 与 Textual 相互独立、CLI 工具位于其上"的生态定位一致。
- **终端句柄（F-RC-02）**：模块级 `console = Console()` 与 `error_console = Console(stderr=True)` 建立两条输出通道；错误信息走 `error_console`，正常渲染走 `console`。
- **事件循环、样式与文本原语（F-RC-04 / F-RC-07）**：`on_error` 用 `Text(message).stylize("bold red")` 生成错误文本；`blend_text` 对每字符用 `("#" + RGB) ` 逐字符 `text.stylize(color, index, index+1)` 做线性插值配色——复用 `Text`/`stylize` 的按段着色能力。
- **CLI 参数架（F-RC-09 / F-RC-10 / F-RC-11 / F-RC-12）**：`main` 命令由 `@click.command(cls=RichCommand)` 装配，`RichCommand` 是 click 命令的 Rich 增强子类；AUTO/SYNTAX/PRINT/MARKDOWN/RST/JSON/RULE/INSPECT/CSV/IPYNB 九个格式常量作为内部分派键（F-RC-03）。
- **按资源类型分派渲染（F-RC-13..16）**：这是全文最重的"复用点"：
  - `resource_format` 依 `--print/-p`、`--syntax`、`--json/-J`、`--markdown/-m` 等开关（F-RC-09）或扩展名（`.md/.json/.csv/.rst/.ipynb`）决定目标渲染器（F-RC-13）；
  - PRINT/RULE 分支复用 `Text`、`Text.from_markup` 与 `Rule`（F-RC-14）——`Text.from_markup(sys.stdin.read(), justify=justify, emoji=emoji)` 直接解析终端标记；
  - JSON/MARKDOWN/RST 分支分别复用 `rich.json.JSON as RichJSON`、`.markdown.Markdown`（扩展版）与 `rich_rst.RestructuredText`（F-RC-15）；
  - INSPECT 分支复用 `Inspect(inspect_data, help=False, dunder=False, all=False, methods=True)`；CSV/IPYNB 走自研 `render_csv`/`render_ipynb`；SYNTAX 分支复用 `Syntax(code, lexer, theme=..., line_numbers=..., indent_guides=..., word_wrap=..., line_range=...)`，而 `resource` 为空时打印 usage（F-RC-16）。
- **渲染后处理链（F-RC-17）**：同一 `renderable` 依次套 `Padding`、`Panel`（边框取自 `getattr(box, panel.upper())`）、`Styled` 与 `ForceWidth`——正是 Rich「渲染对象 → 后处理装饰 → console 输出」管线的 CLI 化复刻。
- **CRUD 与表格（F-RC-19 / F-RC-20）**：`render_csv` 复用 `Table(show_header=..., box=csv.Sniffer()...)、`box.HEAVY_HEAD`/`box.SQUARE`；`render_ipynb` 复用 `Panel`、`Syntax`、`Markdown`、`Text` 与 `Group`，最终返回 `Group(*cells)` 一次渲染整个笔记本。
- **范围行裁切（F-RC-16 尾部 / F-RC-21）**：`_line_range` 将 `--head/--tail` 换算为 `(start, end)` 区间传入 `Syntax(line_range=...)`，实现"只看文件头/尾"的能力。

## 本工具示范的独有机制

除复用上游原语外，`rich-cli` 还示范了几个"只在 CLI 场景才出现的独特机制"，值得单独辨识。

- **远程资源抓取（F-RC-05 / F-RC-06）**：`read_resource` 对 `http://`/`https://` 前缀用 `requests.get(path)` 抓取并以 `response.text`/`Content-Type` 推断 lexer；对本地路径用 `open(path, "rt", encoding="utf8", errors="replace")`；`"-"` 走 `sys.stdin.read()`。一条命令即可 `rich https://…` 渲染网页文本。
- **Markdown 的 CodeBlock 重挂（F-RC-22）**：`markdown.py` 的 `CodeBlock(TextElement)` 用 `Syntax(code, self.lexer_name, theme=..., word_wrap=True)` 实现代码块渲染，并在模块末尾 `Markdown.elements["code_block"] = CodeBlock` 把扩展注入 Rich 的 Markdown——这是"对 Rich 内置渲染器做子类化扩展"（[08-rich-markdown](/concepts/08-rich-markdown.md)）的落地范例。
- **强制宽度包装 `ForceWidth`（F-RC-07 / F-RC-17 / F-RC-21 尾部）**：`__rich_console__` 用 `options.update_width(self.width)` 取得 child_options 后 `yield from console.render(self.renderable, child_options)`，`__rich_measure__` 返回 `Measurement(self.width, self.width)`——在 `width > 0` 且非 pager 时强制居中输出到指定宽度。
- **导出富文本为 HTML/SVG（F-RC-12 / F-RC-18）**：`--export-html/-o` 与 `--export-svg` 会令 `Console(record=True)` 开启记录，渲染后 `console.save_html(...)` / `console.save_svg(..., clear=False)` 落盘，是 Rich 「录制→导出」能力在 CLI 的暴露（对照 [12-rich-render-pipeline-and-export](/concepts/12-rich-render-pipeline-and-export.md)）。
- **Pager 分页（F-RC-18 / F-RC-23）**：这是首个直接把 Textual 的 `App` 搬进 CLI 输出链路的用例——`pager.py` 定义 `PagerRenderable(lines, new_lines=False, width=80)`（逐行 yield segments）与 `PagerApp(App)`：`on_load` 绑定 `"q"→"quit"`，`on_key` 处理 `j/k/space/ctrl+u/ctrl+d`（`body.scroll_up()/scroll_down()/page_down()` 及 `animate("y", target_y, easing="out_cubic")`），`on_mount` 里 `body = ScrollView(auto_width=True)`、`await self.view.dock(body)`。非 pager 分支 `console.render_lines(renderable, options.update(width=width-1), new_lines=True)` 拿到字节段后交给 `PagerApp.run(...)`。
- **Windows 虚拟终端（F-RC-24）**：`win_vt.py` 用 `ctypes.WinDLL("kernel32")` 封装 `GetConsoleMode`/`SetConsoleMode`，把 `_ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004` 置位，提供 `enable_windows_virtual_terminal_processing()` 上下文管理器；非 Windows 分支为空操作——为 Windows 下获得完整 SGR 色彩/样式兜底。

```python
# 典型的 rich-cli 调用（bash 侧，唤起 Rich 各原语）
rich notebooks.ipynb -n -o out.html     # ipynb 渲染 + 行号 + 导出 HTML
rich https://example.com/api.json       # URL 抓取后按 json 渲染（F-RC-05/13）
rich some_md.md --pager                 # Markdown + Textual 分页器（F-RC-23）
rich -u --rule-style bright_red demo    # 打印 Rule（F-RC-14）
```

## 相关概念

- [/concepts/00-ecosystem-overview.md](/concepts/00-ecosystem-overview.md) — Textualize 生态总览，CLI 工具位于 Rich/Textual 之上
- [/concepts/01-rich-console-and-protocol.md](/concepts/01-rich-console-and-protocol.md) — `Console` 渲染管线与可渲染对象协议，`ForceWidth`/`PagerRenderable` 均实现该协议
- [/concepts/08-rich-markdown.md](/concepts/08-rich-markdown.md) — Rich 内置 Markdown 渲染，`CodeBlock` 扩展注入的宿主机制
- [/concepts/12-rich-render-pipeline-and-export.md](/concepts/12-rich-render-pipeline-and-export.md) — 渲染与 HTML/SVG 导出，对照 `console.save_html/save_svg`
- [/references/rich-cli.md](/references/rich-cli.md) — 信源信息、本地路径、commit 与核心模块清单