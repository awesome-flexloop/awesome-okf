---
type: Concept
title: "07 · 旗舰渲染器与视图模型的源码实现"
description: "PAGE_SPECS 四路由、SOURCE_RULES、mobile-routes、theme-button 的实现级细节；澄清「四种视图风格」实为设计期候选、四个顶层入口与群聊页三视图的层级关系"
tags: [wechat-intelligence-hub, source-code, report-renderer, view-model, ui-naming, 勘误]
---

# 07 · 旗舰渲染器与视图模型的源码实现

> 本篇是 [02-flagship-daily-report-and-four-views.md](02-flagship-daily-report-and-four-views.md) 的**源码级续篇**。首轮那篇因缺源码，把四入口名、四视图、明暗主题、移动端统一标注为「图注单源」；本篇用代码常量与运行时机制给出定论，并**修正一处首轮表述**。

## 1. 四个入口名：代码常量坐实

`report_bundle_flagship.py` 的 `PAGE_SPECS` 是一条 4 元组列表，逐字给出路由、文件名、标题与导航标签（F-080）：

| route | 文件 | title | nav_label | priority |
|-------|------|-------|-----------|----------|
| `overview` | `index.md` | 综合行动报告 | **综合行动** | 10 |
| `groups` | `groups.md` | 群聊日报 | **群聊日报** | 20 |
| `contacts` | `contacts.md` | 重点联系人 | **重点联系人** | 30 |
| `radar` | `radar.md` | 商单信号雷达 | **信号雷达** | 40 |

同文件内还有一段内嵌字符串逐字复述同一组名称（F-090）：

> 「交互 HTML 只保留综合行动、群聊日报、重点联系人和商单信号雷达四个入口。」

加上 `docs/USAGE.md` 的官方逐字列表，**三源一致**：代码常量 + 代码内嵌字符串 + 官方文档。首轮「四入口名为图注单源」的判断可以撤销——那是当时没读源码的保守结论，不是官方文档缺失。

注意 `radar` 的 title 与 nav_label 不同：页面标题是「商单信号雷达」，导航短标签是「信号雷达」。引用时应区分二者（这也是首轮容易含混的地方）。

## 2. ⚠️ 修正：所谓「四种视图风格」是设计期候选，不是运行时主题

这是本轮最重要的一处**方向性修正**（F-087~F-089）。

首轮 F-016/F-017 依据博文图注，把「同一份聊天数据渲染成四种视图风格」「A 综合行动总览 / B 群聊与话题日报 / C 重点联系人面板 / D 商单信号雷达」登记为博文声明。本轮源码给出的结论与之不同：

**证据 1**——A~D 四套风格的定义出自 `projects/wechat-intelligence-hub/docs/report-redesign-research-2026-08-28.md` 的「**四套待选视觉风格**」章节，各自带「定位 / 视觉 / 布局 / 组件 / 优点 / 缺点」六段设计说明（F-089）。

**证据 2**——该文档的最终结论是：

> 「采用 **A 作为主框架**，B 作为群聊话题和项目详情的阅读风格，D 作为未来历史档案/开源文档层。」
> 「不建议把 C 直接做成首页。」

**证据 3**——`docs/style-previews/` 目录含 **10** 个文件（style-a.png ~ style-d.png 四张预览图 + flagship-preview.html + report-style-preview.html + flagship-today.png + flagship-today-mobile.png + flagship-topic.png + flagship-relationship.png），但对全仓库做跨文件引用检索（`--include=*.py --include=*.sh --include=*.md`），**无任何运行时代码引用该目录**（F-088）。

**证据 4**——设计文档自身写明「明暗模式是颜色模式，**不作为另一套风格**」（F-089）。

**修正后的准确表述**：A~D 是 2026-08-28 的**视觉设计方案候选**，其中 A 被采纳为主框架；运行时并不存在「四套可切换风格」。博文的「四种视图风格」实际对应的更可能是**四个顶层入口**（综合行动 / 群聊日报 / 重点联系人 / 商单信号雷达）——两者名称高度重合，这正是首轮无法判断「同一套配置的两个说法，还是两层不同机制」的根因。

源码给出的层级关系是清晰的：

```
四个顶层路由入口        PAGE_SPECS = 4 条   → overview / groups / contacts / radar
  └─ 群聊页内的三视图    view-switcher      → 话题视角 / 重点群视角 / 群聊筛选
```

即 **4 个顶层入口 ≠ 4 种视图风格**；而群聊页内另有 3 个可切换视图（F-086）。

## 3. 明暗主题：完整可运行机制

首轮 F-016 中的「明暗主题」部分被一并归入「图注单源」，本轮源码给出完整实现链（F-084、F-085）：

| 环节 | 实现 |
|------|------|
| 触发 | 工具栏 `<button id="theme-button" title="切换明暗主题">◐</button>` |
| 切换 | `document.documentElement.dataset.theme` 在 `'dark'` / `'light'` 间取反 |
| 持久化 | `localStorage.setItem('wechat-flagship-theme', next)` |
| 恢复 | 页面加载时 `localStorage.getItem('wechat-flagship-theme')` 回填 `dataset.theme` |
| 样式 | `html[data-theme="dark"]` 定义整套 CSS 变量（`--canvas:#171b20`、`--ink:#edf1f5`、`--green:#75d9c0`、`--coral:#ee806f` 等） |

同批实现的还有打印（`#print-button` → `window.print()`，配 `@media print` 规则隐藏侧栏与导航）与下载当前分区 Markdown（`#download-button`）。这坐实了首轮 F-015 中「可打印和导出当前分区」这条原本标 ⚠️ 的博主体验描述。

**设计观察**：主题偏好存在 `localStorage` 而非 Profile 文件——说明它是**阅读器侧偏好**（属于这台机器的这个浏览器），不是**数据侧画像**。这个区分在隐私上是有意义的：主题选择不进入可能随报告一起流转的数据资产。

## 4. 移动端：不是「另有视图」，而是同一份 HTML 的响应式分支

首轮 F-018「手机端有对应视图」标为图注单源。源码显示实现方式不同（F-083）：

- 导航元素 `<nav class="mobile-routes" aria-label="移动端报告目录">`，内容由 `mobile_nav_html` 按每个 page 的 `route` 与 `nav_label` 逐页生成 `<a href="#/{route}" data-route-link="{route}">`；
- 桌面端 `.mobile-routes { display:none; }`，在 `@media` 断点下切换为 `position:sticky; top:50px; overflow-x:auto` 的横向滚动条；
- 打印样式中 `.mobile-routes` 与 `.bottom-nav` 一并隐藏。

即移动端**不是另一套渲染产物**，而是同一份 HTML 在窄屏下的布局分支。目录里同时存在 `flagship-today-mobile.png` 与 `flagship-today.png` 两个截图，是同一页面的两种宽度取证。

这个实现选择对使用者的实际含义：手机上打开的是**同一份本地 HTML 文件**（或同一服务地址），不需要另找「移动版报告」。

## 5. 两个渲染器、两套 SOURCE_RULES

一个容易踩的计数坑（F-081、F-082）：仓库里有**两个**报告渲染器，各自定义 `SOURCE_RULES`，条数不同：

| 渲染器 | 文件 | `SOURCE_RULES` 条数 | kind 集合 |
|--------|------|--------------------|-----------|
| 旗舰 | `report_bundle_flagship.py` | **11** | overview / groups / contacts / radar / internal |
| HTML | `report_bundle_html.py` | **8** | overview / groups / contacts / actions / links / evidence / audit |

旗舰版多出的 5 条均为 `kind="internal"` 的 `collapsed=True` 折叠项（机器初筛、证据附录、价值矩阵等）——对应首轮 F-053 提到的「机器审计留在本地但不进入阅读导航」。

**引用纪律**：「11 条规则」只对旗舰渲染器成立，不可泛化为「项目有 11 条来源规则」。

## 6. 可迁移模式

**模式 M5：把「视图」拆成两层——内容路由层与视觉呈现层。**

本项目的渲染模型清晰地把两件事分开：

- **内容路由层**（`PAGE_SPECS`）：决定「有哪些内容分区、各自分到什么源文件」——这是**数据结构**，可被程序消费；
- **视觉呈现层**（CSS 变量 + `data-theme` + `@media`）：决定「怎么显示」——这是**表现参数**，可被用户偏好覆盖。

好处是二者可独立演进：加一个内容分区只需动 `PAGE_SPECS`；加一套配色只需加 CSS 变量块。而设计期候选（`style-previews/`）与运行时机制**物理分离**，也让「哪些是已实现的、哪些还在构想」在仓库结构上就一目了然——这是本轮能快速判定「四套风格非运行时能力」的结构性原因。

下一站：[08-source-code-architecture-and-counts.md](08-source-code-architecture-and-counts.md)。
