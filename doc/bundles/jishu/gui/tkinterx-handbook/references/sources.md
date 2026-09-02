---
type: Reference
title: "《tkinterx 手册》信源登记"
description: "简书博客集《tkinterx 手册》5 篇博文的逐篇信源登记（F-TXH-01 至 F-TXH-05）、外部核验信源与图片本地化说明"
tags: [tkinter, tkinterx, gui, reference, source, jianshu]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinterx-handbook-jianshu
    resource: https://www.jianshu.com/nb/45403586
    title: 简书博客集《tkinterx 手册》（作者：水之心，共 5 篇）
  - id: tkinterx-pypi
    resource: https://pypi.org/project/tkinterx/
    title: PyPI 项目页 tkinterx（安装方式与项目元信息核验信源）
  - id: tkinterx-github
    resource: https://github.com/xinetzone/pychaos
    title: GitHub 仓库 xinetzone/pychaos（tkinterx 源码项目主页）
  - id: author-pypi
    resource: https://pypi.org/user/xinetzone/
    title: 作者 PyPI 主页 xinetzone
---

# 《tkinterx 手册》信源登记

本知识包基于简书博客集 **《tkinterx 手册》**（共 5 篇）整理而成。该手册由作者 **xinetzone**（简书笔名"水之心"）撰写，系统介绍其自研的 tkinter 扩展库 **tkinterx** 的安装与使用。所有内容文档中的关键事实均以脚注（如 F-TXH-01）溯源至本登记表。

## 博文逐篇登记

| F 编号 | 标题 | 原文链接 | 抓取日期 | 备注 |
|--------|------|----------|----------|------|
| F-TXH-01 | tkinter 的拓展包：tkinterx | https://www.jianshu.com/p/1a08da0a098f | 2026-09-02 | 博客集主文（首篇，发布于 2020-04-24）。介绍项目背景与 PyPI 安装，覆盖 CanvasMeta 统一画图接口、WindowMeta 可传值窗体、ParamDict 与按行/列批量绘图、canvas_design 图形设计工具、painter 几何画板。含 8 张运行截图与 3 个数学公式（公式已转写为行内文本）。 |
| F-TXH-02 | tkinter 界面常用颜色表单 | https://www.jianshu.com/p/480ff177b14b | 2026-09-02 | 发布于 2020-04-29。介绍 tkinterx.tools.colors.show_colors() 一键颜色表，以及使用 140 余条 color_dict 颜色字典自制 ttk 颜色表单。含 2 张运行截图。 |
| F-TXH-03 | tkinterx 之画图 | https://www.jianshu.com/p/9e63d9a88618 | 2026-09-02 | 发布于 2020-04-29。介绍 CanvasMeta 的 create_point / create_circle / create_square 接口，以及用 color_dict 绘制堆叠彩色方块/圆矩阵。含 3 张运行截图。 |
| F-TXH-04 | tkinterx 之抠图工具 | https://www.jianshu.com/p/e3cf7e72e126 | 2026-09-02 | 发布于 2020-05-16。**作者待更**：全文仅说明 tkinterx 实现了抠图操作、可运行 python draw_graph.py 查看效果，未随文提供 draw_graph.py 源码或 API 说明，内容不完整。仅含 1 张效果图，已并入[颜色工具与抠图工具](../concepts/06-tools-colors-matting.md)并标注待更，未臆造未发布内容。 |
| F-TXH-05 | tkinterx 模拟电子限速 | https://www.jianshu.com/p/9fe81ca6c0f7 | 2026-09-02 | 发布于 2020-05-26（博客集最近更新）。给出完整可运行示例：用 CanvasMeta 的 create_text / create_circle / create_square 绘制限速 90 的电子限速标志。含 1 张运行截图。 |

## 外部核验信源

| 信源 | 链接 | 核验内容 |
|------|------|----------|
| 简书博客集《tkinterx 手册》 | https://www.jianshu.com/nb/45403586 | 博客集共 5 篇、篇名与顺序、作者笔名"水之心"、最近更新 2020-05-26，与章节清单一致。 |
| PyPI 项目页 tkinterx | https://pypi.org/project/tkinterx/ | 核验 F-TXH-01 的安装声明：tkinterx 已发布至 PyPI，最新版 **0.0.9**（2020-05-30 发布），维护者为 **xinetzone**；安装命令 pip install tkinterx 与博文一致；项目主页（Homepage）指向 https://github.com/xinetzone/pychaos ；许可证 MPL 2.0；要求 Python >= 3.7；开发状态为 2 - Pre-Alpha；支持 Windows 7/10 与 Linux。PyPI 项目描述中明确链接本中文手册 https://www.jianshu.com/nb/45403586 ，并收录 F-TXH-01 的"个人信息登记窗"示例。 |
| GitHub 仓库 xinetzone/pychaos | https://github.com/xinetzone/pychaos | F-TXH-01 文中给出的项目仓库："以 tkinter 为基础研究如何使用 Python 开发 GUI 接口"。 |
| 作者 PyPI 主页 | https://pypi.org/user/xinetzone/ | tkinterx 包维护者主页。 |

**作者简书主页说明**：作者简书笔名为"水之心"，简书用户 uid 为 **1114626**（由全部截图图床路径 upload_images/1114626-* 可证）。其简书主页 /u/&lt;slug&gt; 链接未随本次抓取获得，为避免杜撰 URL，此处仅登记可核验入口：博客集页面（含作者主页入口）https://www.jianshu.com/nb/45403586 ，以及作者 GitHub（https://github.com/xinetzone ）与 PyPI 主页（https://pypi.org/user/xinetzone/ ）。

## 抓取与时效说明

- 5 篇博文均为公开免费文章（源稿 frontmatter paywall: False），抓取日期均为 **2026-09-02**。
- 博文集中第 4 篇（F-TXH-04）为作者待更状态，本知识包 status 仍标 stable，但在[颜色工具与抠图工具](../concepts/06-tools-colors-matting.md)正文与本登记表中均明示"作者待更，内容不完整"。
- tkinterx 为作者个人维护的早期项目（PyPI 开发状态 Pre-Alpha，最后发布于 2020-05-30），API 可能随仓库版本变化；本知识包内容对应博文写作时（2020 年 4-5 月）的接口形态。

## 图片本地化说明

- 本知识包全部截图来自简书图床 upload-images.jianshu.io（作者 uid 1114626），共 **15 张**，已本地化至文档中心静态资源目录 `_static/bundles/jishu/gui/tkinterx-handbook/images/`（bundle 文档以相对路径 `../../../../../_static/...` 引用），文件命名规则为 &lt;所在文章 slug&gt;-&lt;原图床文件名&gt;.webp（例：1a08da0a098f-1114626-8975fb2c9834b284.webp）；另含 1 张 Seedream 生成的装饰性封面 cover.jpg。
- F-TXH-01 中另有 3 个 math.jianshu.com 数学公式渲染图（方向向量 d = (x0, y0, x1, y1)、左上角坐标 (x0, y0)、右下角坐标 (x1, y1)），公式内容已转写为行内文本，信息无丢失。
- 各篇截图分布：F-TXH-01 → 8 张、F-TXH-02 → 2 张、F-TXH-03 → 3 张、F-TXH-04 → 1 张、F-TXH-05 → 1 张，合计 15 张，与源稿 frontmatter images 字段（11 + 2 + 3 + 1 + 1 = 18，含 3 个公式图）逐一核对一致。