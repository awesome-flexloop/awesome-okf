---
type: Reference
title: "《tkinter 手册》信源登记"
description: "简书博客集《tkinter 手册》21 篇博文的逐篇信源登记（F-THB-01 至 F-THB-21）、外部核验信源、抓取时效与图片本地化说明"
tags: [tkinter, gui, reference, source, jianshu]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinter-handbook-jianshu
    resource: https://www.jianshu.com/p/dd0e97484e81
    title: 简书博客集《tkinter 手册》（作者简书 uid 1114626，共 21 篇，2020-04 至 2021-02 发布）
---

# 《tkinter 手册》信源登记

本知识包基于简书博客集 **《tkinter 手册》**（共 21 篇）整理而成。该手册系统讲解 Python 标准库 **tkinter**（Tcl/Tk 的面向对象封装）的用法：微件体系与配置管理、样式、事件绑定、三种布局管理器、Canvas 绘图与交互（拖曳/缩放/图片）、Toplevel 多窗口与跨窗口传值、StringVar 变量追踪、对话框、tkinter.dnd 拖放以及 ttk 主题部件。所有内容文档中的关键事实均以脚注（编号形如 F-THB-01）溯源至本登记表。

## 博文逐篇登记

| F 编号 | 标题 | 原文链接 | 抓取日期 | 备注 |
|--------|------|----------|----------|------|
| F-THB-01 | tkinter 基本概念梳理 | https://www.jianshu.com/p/dd0e97484e81 | 2026-09-02 | 发布于 2020-05-07，博客集首篇（3510 字）。译介 effbot Tkinterbook：Tcl/Tk 与 tkinter 关系、18 种常用微件、Misc/Wm/Grid/Pack/Place Mixins 与委派机制、cget/config/keys 配置管理、颜色/字体/文本/边框/焦点高亮样式。含 4 张交互截图与 1 个公式图（delegation，已转写行内文本）。 |
| F-THB-02 | tkinter 事件与绑定 | https://www.jianshu.com/p/9c66c0090edb | 2026-09-02 | 发布于 2020-05-07（1907 字）。事件序列 `<modifier-type-detail>` 语法、鼠标/键盘/窗口事件表、Event 对象属性、bind/bind_class/bind_all 四级绑定与匹配顺序、WM_DELETE_WINDOW 协议。含 3 个公式图（type/modifier/detail，已转写行内文本），无截图。 |
| F-THB-03 | tkinter 布局管理 | https://www.jianshu.com/p/f53625382e30 | 2026-09-02 | 发布于 2020-05-16（1898 字）。Pack（anchor/expand/fill/pad/side + 多 Frame 容器嵌套）、Grid（row/column/columnspan/rowspan/sticky）、Place（x/y/relx/rely/relwidth/relheight/bordermode）三套布局管理器详解，含三个完整示例与 1 张 Pack 布局截图。 |
| F-THB-04 | tkinter 之对话框 | https://www.jianshu.com/p/5537937b12c1 | 2026-09-02 | 发布于 2020-05-15。短文（44 字），给出 `tkinter.dialog.Dialog` 的完整可运行示例（title/text/bitmap/default/strings 参数，d.num 获取按钮序号），含 1 张对话框截图。 |
| F-THB-05 | Canvas 相关参数简介 | https://www.jianshu.com/p/9ada3a496907 | 2026-09-02 | 发布于 2020-04-30（4418 字）。Canvas 选项表（bg/bd/closeenough/confine/scrollregion/highlightthickness 等）、item handles 与 tags 机制（含预定义 all/current）、40 余个 Canvas 方法（addtag_*/find_*/coords/move/scale/tag_bind/postscript/xview 等）、scan_mark/scan_dragto 拖曳、highlightthickness=0 去边框注意事项。含 1 张 scale 缩放示例截图与 7 个公式图（坐标元组，已转写行内文本）。 |
| F-THB-06 | 分组 Canvas 的画图函数 | https://www.jianshu.com/p/84ac277d0433 | 2026-09-02 | 发布于 2020-04-30（2113 字）。将 create_* 分为 graph/image/text/window 四组，系统梳理通用参数（state/tags/width/anchor/fill/outline/stipple/dash/joinstyle/smooth 等）与 create_window/create_image/create_bitmap/create_text/create_rectangle/create_oval/create_arc/create_line 各函数选项，含位图填充与 active/disabled 状态示例。含 3 张运行截图与 7 个公式图，已转写行内文本。 |
| F-THB-07 | tkinter 中 Canvas 创建图片的坑 | https://www.jianshu.com/p/6c54b3792b0d | 2026-09-02 | 发布于 2020-05-18（197 字）。PhotoImage 仅支持 PGM/PPM/GIF/PNG，需用 PIL.ImageTk.PhotoImage 载入 JPG；PhotoImage 在 mainloop 期间必须持有引用否则被垃圾回收导致图片不显示，给出实例属性持有引用的解法。无截图。 |
| F-THB-08 | tkinter 使用 Canvas 实现进度条 | https://www.jianshu.com/p/1ff4cdbb2aa0 | 2026-09-02 | 发布于 2020-05-18。**作者待更**：全文仅一段 Canvas 进度条代码（外框矩形 + coords 动态改变填充矩形宽度 + StringVar 百分比）与 1 张效果图，无文字讲解。代码完整可用，已并入示例文档并标注。 |
| F-THB-09 | tkinter.dnd.py 使用 | https://www.jianshu.com/p/e8839b18476c | 2026-09-02 | 发布于 2020-05-20。全文为标准库 `tkinter/dnd.py` 模块源码转载（含模块 docstring 与 Icon/Tester 跨窗口拖放演示），无作者叙述文字。docstring 完整定义了 dnd_start/dnd_accept/dnd_enter/dnd_motion/dnd_leave/dnd_commit/dnd_end 拖放协议，知识包据此提炼用法。无截图。 |
| F-THB-10 | Toplevel 创建多个窗口 | https://www.jianshu.com/p/55ccd1981923 | 2026-09-02 | 发布于 2020-05-23。短文（17 字），给出主窗口按钮创建两个 Toplevel 子窗口（Win2/Wen3 类、geometry 定位、destroy 关闭）的完整代码，含 1 张多窗口截图。 |
| F-THB-11 | tkinter 简单教程 | https://www.jianshu.com/p/774f8a33cd52 | 2026-09-02 | 发布于 2020-05-23（555 字）。Tk() 根窗口、title/geometry（`宽x高±x±y` 定位语法）、Frame 容器与背景色、Label 文本与图片（PhotoImage）四步入门，含 4 张运行截图。 |
| F-THB-12 | Python 设置 Canvas 背景图片且支持全屏显示 | https://www.jianshu.com/p/2e20fd55375b | 2026-09-02 | 发布于 2020-05-18。**付费文章**（简书定价 1000 简书币）：抓取内容为免费试读部分，含 PhotoImage 引用持有（CanvasMeta.set_photo）、create_image(anchor='nw') 铺背景图、grid + columnconfigure/rowconfigure(weight=1) 随窗口缩放的基础代码与 2 张截图；文章止于"添加图片全屏显示，随窗口大小改变而变"一句，**全屏缩放实现代码未获取**，知识包未臆造该部分。 |
| F-THB-13 | tkinter 之 StringVar 追踪 | https://www.jianshu.com/p/eb6bab093c12 | 2026-09-02 | 发布于 2020-05-24。短文（58 字），演示 `StringVar.trace("w", callback)` 追踪变量写入、Entry textvariable 绑定与跨部件传值，含 1 张传值效果截图。 |
| F-THB-14 | tkinter 创建只能出现一次的 Toplevel | https://www.jianshu.com/p/bcc92cf04f02 | 2026-09-02 | 发布于 2020-05-28（90 字）。用 `self.new.state() == "normal"` 探测子窗口是否存活：存活则 focus() 提至前台，异常（已销毁）才新建 Toplevel，实现单例子窗口。无截图。 |
| F-THB-15 | tkinter 跨窗口传递值 | https://www.jianshu.com/p/33d8a8be3b9b | 2026-09-02 | 发布于 2020-05-29（183 字）。两种跨窗口传值模式：①主窗口持有 ParamWindow 实例、关闭后 todict() 取值（含 ttk.Style 自定义 EntryStyle 示例）；②`transient()` + `wait_window()` 模态阻塞，点 OK 后直接回传 output 字典，无需关闭主窗口。含 2 张运行截图。 |
| F-THB-16 | tkinter Canvas 实现拖曳与缩放功能 | https://www.jianshu.com/p/4e77be43ac60 | 2026-09-02 | 发布于 2020-06-15（182 字）。scan_mark/scan_dragto 鼠标拖曳画布（含 Scrollbar + scrollregion 完整示例）；canvasx/canvasy 屏幕坐标转画布坐标；`<MouseWheel>`/`<Button-4>`/`<Button-5>` 滚轮事件配合 `canvas.scale("all", x, y, factor, factor)` 缩放并重设 scrollregion。含 1 张拖曳截图与 3 个公式图（坐标换算，已转写行内文本）。 |
| F-THB-17 | tkinter 实现图片的缩放与拖曳 | https://www.jianshu.com/p/c8a91b202725 | 2026-09-02 | 发布于 2020-06-15（134 字）。参考 StackOverflow "Tkinter canvas zoom + move/pan"，给出三版图片缩放拖曳实现：基础版（整图 resize，有内存溢出警告）、进阶版（按可视区域裁剪 tile 重绘，类 Google Maps）、图像金字塔版（适配数 GB 级 TIFF）；并给出 tkinter 内置 scan/scale 机制最小代码与 Ctrl/Shift 单轴缩放。无截图。 |
| F-THB-18 | Tk/Tcl 资源 | https://www.jianshu.com/p/f2e09b85d4b6 | 2026-09-02 | 发布于 2020-05-20。**作者待更**：仅列出 8 个资源名称（TkDocs Tutorial、Tklib 扩展仓库、effbot《An Introduction to Tkinter》、《Tkinter 8.5 reference》、tkDND、GUI Builder、Tk wm 命令、TIP 236），原文未附超链接；知识包按名称核对官方入口后在概念文档中给出，未杜撰原文链接。无截图。 |
| F-THB-19 | tkinter 基础教程 | https://www.jianshu.com/p/462858a67cdc | 2026-09-02 | 发布于 2020-08-31（1872 字）。Tk 跨平台工具包定位、GUI 四个基本编程任务（外观/行为/关联/等待输入）、Tk + mainloop 事件循环、Label/Button/Entry 常用部件、foreground/background 颜色与十六进制 RGB、width/height 文本单位机制。含 6 张运行截图。 |
| F-THB-20 | tkinter 深度解析 | https://www.jianshu.com/p/32d5612dbe70 | 2026-09-02 | 发布于 2020-09-02（538 字）。name 选项与 widget 路径名树（`str(widget)`/`widget._w`，`.` 分隔、`!toplevel.!frame2.!button`）、tk_setPalette 全局配色、update/after/after_idle/after_cancel 事件循环调度、clipboard_clear/append/get 剪贴板操作。含 2 张配色截图。 |
| F-THB-21 | tkinter.ttk.Widget 简介 | https://www.jianshu.com/p/5734f860558f | 2026-09-02 | 发布于 2021-02-02（1747 字，博客集最近更新）。ttk 主题部件思想（行为与外观分离，fg/bg 等选项改由 ttk.Style 管理）、18 种 ttk 部件（12 种同名 + Combobox/Notebook/Progressbar/Separator/Sizegrip/Treeview 6 种新增）、标准/可滚动/Label/兼容性选项、9 种状态标志（active/disabled/focus/pressed/selected/background/readonly/alternate/invalid）与 identify/instate/state 方法。无截图。 |

## 外部核验信源

| 信源 | 链接 | 核验内容 |
|------|------|----------|
| Python 官方文档 tkinter.ttk | https://docs.python.org/zh-cn/3/library/tkinter.ttk.html | 核验 F-THB-21：ttk 18 种部件清单、标准选项、Widget States 状态标志、identify/instate/state 方法，与博文一致。 |
| Python 官方文档 tkinter | https://docs.python.org/3/library/tkinter.html | 核验 F-THB-01/19：tkinter 为 Tcl/Tk 的面向对象封装、_tkinter 二进制模块、Tk()/mainloop 事件循环模型。 |
| effbot Tkinterbook | https://effbot.org/tkinterbook/ | F-THB-01（微件表、Mixins、Styling）、F-THB-02（Events and Bindings、Protocols）、F-THB-05（Canvas 方法）的主要译介来源，博文内多处保留 effbot 链接。 |
| TkDocs | https://tkdocs.com/ | F-THB-18 所列首条资源 "TkDocs Tutorial" 的官方入口；核验 F-THB-19 所述 Tk 跨平台（Windows/macOS/Unix）定位。 |
| 标准库 tkinter/dnd.py | Python 标准库源码（tkinter/dnd.py） | 核验 F-THB-09：博文全文即该模块源码转载，dnd_start/dnd_accept/dnd_enter/dnd_motion/dnd_leave/dnd_commit/dnd_end 协议与标准库一致。 |

**作者说明**：全部截图图床路径均为 `upload-images.jianshu.io/upload_images/1114626-*`，即作者简书 uid 为 **1114626**，与同域姊妹知识包《tkinterx 手册》（简书笔名"水之心"/xinetzone）为同一简书账号。本博客集的简书文集（/nb/）链接未随本次抓取获得，为避免杜撰 URL，仅登记 21 篇文章各自的 /p/ 永久链接。

## 抓取与时效说明

- 21 篇博文抓取日期均为 **2026-09-02**；其中 20 篇为公开免费文章（源稿 frontmatter paywall: False）。
- F-THB-12 为简书付费文章（retail_price: 1000 简书币），抓取内容为免费试读部分，全屏随窗口缩放图片的实现代码不在试读范围内，已在[画布图片](../concepts/09-canvas-images.md)与本登记表中显式标注，未臆造缺失代码。
- F-THB-08（仅代码与效果图）、F-THB-18（仅资源名称无链接）为作者待更状态，已在对应概念文档与本登记表中标注。
- tkinter 是 Python 标准库组件，API 稳定性高；本知识包对应 Python 3 / Tk 8.5+ 的接口形态（ttk 部件自 Tk 8.5 引入），stale_after 设为 2027-09-02（一年保守复核周期）。

## 图片本地化说明

- 本知识包全部截图来自简书图床 upload-images.jianshu.io（作者 uid 1114626），共 **30 张**，已本地化至 `_static/bundles/jishu/gui/tkinter-handbook/images/` 目录，文件命名规则为 `<所在文章 slug>-1114626-<图床哈希>.webp`（例：`dd0e97484e81-1114626-db8cfe2275eba826.webp`）。
- 源稿 frontmatter images 字段合计 **51** 个图片引用，其中 30 个为 upload-images 截图（全部可在 image-map.json 中解析），另 **21 个**为 math.jianshu.com 公式渲染图，公式内容已全部转写为行内文本/代码，信息无丢失：F-THB-01 → 1 个（delegation）、F-THB-02 → 3 个（type/modifier/detail）、F-THB-05 → 7 个（坐标元组 (x, y)、(x0, y0, x1, y1) 等）、F-THB-06 → 7 个（位置坐标与箭头三元组 (a, b, c)）、F-THB-16 → 3 个（拖曳坐标换算公式）。
- 各篇截图分布：F-THB-01 → 4 张、F-THB-03 → 1 张、F-THB-04 → 1 张、F-THB-05 → 1 张、F-THB-06 → 3 张、F-THB-08 → 1 张、F-THB-10 → 1 张、F-THB-11 → 4 张、F-THB-12 → 2 张、F-THB-13 → 1 张、F-THB-15 → 2 张、F-THB-16 → 1 张、F-THB-19 → 6 张、F-THB-20 → 2 张，合计 30 张，与源稿逐一核对一致。
