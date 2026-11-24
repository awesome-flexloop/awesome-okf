---
type: Report
title: "七概念对比报告：pydata-sphinx-theme vs sphinx-book-theme"
description: "对同组两个 Sphinx 主题知识包做全面学习、交叉洞察与逐维对比，含对抗审查、选型决策与迁移路径"
tags: [sphinx, theme, pydata, sphinx-book-theme, comparison, seven-concepts, report]
generated: { by: "main-agent/lobsterai", at: "2026-11-24T13:22:25+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T13:22:25+08:00" }
status: stable
stale_after: 2027-05-24
sources:
  - id: bundle-pst
    resource: projects/awesome-okf-xs/doc/bundles/jishu/document/sphinx/pydata-sphinx-theme
    title: pydata-sphinx-theme 知识包（88 事实 / 6 洞察 / 3 模式 / 9 修正）
  - id: bundle-sbt
    resource: projects/awesome-okf-xs/doc/bundles/jishu/document/sphinx/sphinx-book-theme
    title: sphinx-book-theme 知识包（185 事实 / 7 洞察）
  - id: method
    resource: .agents/commands/seven-concepts.md
    title: 七概念方法论编排指令集
scope: 两个知识包的源码事实、架构、能力边界与知识产品质量
---

# 七概念对比报告：pydata-sphinx-theme vs sphinx-book-theme

> **一句话结论**：这两个包不是"两个竞品"，而是**同一技术栈的上下游**——PST 是导航与布局的基础设施，SBT 是在其上做"书籍化"的产品层。选型问题因此不是"哪个更好"，而是"你要维护哪一类复杂度、接受哪种版本耦合"。

## 目录

- 摘要
- 方法与证据基线
- 全景解剖（PST / SBT）
- 十二维对比
- 洞察（6 条四元组）
- 模式萃取（3 个）
- 对抗审查（V 阶段）
- 选型决策与迁移路径
- 学习路径建议
- 附录（审计数据 / 对照 / 术语 / 复核方法）

---

## 0. 摘要

| 问题 | 结论 |
|---|---|
| 二者关系 | 继承关系：`sphinx-book-theme` → `pydata-sphinx-theme` → Sphinx `basic` |
| 代码量关系 | SBT 的 `layout.html` 只覆盖 3 个 block；组件 7 个 vs PST 23 个 |
| 配置面 | PST 约 50 个选项；SBT 自有 29 个 + 继承父主题约 50 个 |
| 复杂度位置 | PST 在"构建期导航/缓存/双主题 CSS"；SBT 在"URL 矩阵/文档树变换/父主题行为补丁" |
| 维护状态 | PST 活跃迭代（`0.25.0dev0`）；SBT 维护模式（`1.5.0.dev`，正式版 `1.4.0`） |
| 版本耦合 | SBT **精确锁定** `pydata-sphinx-theme==0.23.0`，落后 PST 知识包基线两个小版本 |
| 知识包质量 | PST 四件套齐全（facts/insights/patterns/review）；SBT 有 facts/insights，无 patterns、无 review |
| 选型建议 | 门户型/多版本文档 → PST；教程、教材、Notebook 叙事 → SBT 1.4.0 并锁父主题 |

三条核心判断：

1. **薄继承不等于低耦合**。SBT 用极少的模板代码换来 90% 的能力，代价是把父主题的 block 名、上下文变量与 DOM 结构变成事实上的公开契约。
2. **同名配置不同义**。`navbar_*`、`show_nav_level` 这类键在两个包里语义不同甚至失效，跨包抄配置是最高频的踩坑点。
3. **知识包的可信度看产物结构，不看事实条数**。SBT 的事实更多（185 vs 88），但缺少模式与审查记录，属于"高质量说明书"而非"可复用资产"。

---

## 1. 方法与证据基线

### 1.1 七概念链路

本次任务属于"知识分析/对比"，按方法论走 `R → I → E → V → C`：

| 阶段 | 本次落地 | 产出位置 |
|---|---|---|
| R 复盘/事实 | 通读两包 53 个 Markdown；复核源码事实编号；结构审计与断链检查 | 本文 §2、§9 附录 A |
| I 洞察 | 跨包提炼 6 条洞察，每条含陈述/证据/反常识/行动 | 本文 §4 |
| E 萃取 | 3 个可迁移模式，含触发场景/结构/步骤/反模式/迁移验证 | 本文 §5 |
| V 对抗审查 | 6 条质疑（含 4 条对自身初判的证伪）+ 4 条确认项 | 本文 §6 |
| C 原子提交 | 报告落盘 + 索引建议（未擅自改上游索引） | 输出文件 |

未执行 A（原子化）：本次交付物为单篇报告，无需拆分提交。

### 1.2 证据基线

| 项 | pydata-sphinx-theme | sphinx-book-theme |
|---|---|---|
| 源码版本 | `0.25.0dev0`（commit `73732a16`） | `1.5.0.dev`（正式版 `1.4.0`，2026-07-19） |
| 采集日期 | 2026-11-24 | 2026-11-24 |
| 事实条目 | 88（PST-F-001…088） | 185（SBT-F-001…185） |
| 证据编号约定 | 本文以 `PST-F-xxx` / `SBT-F-xxx` 引用 | 同左 |
| 声明状态 | `stable`，`stale_after: 2027-11-24` | `stable`，`stale_after: 2027-11-24` |

> 两个包同日生成、同一过期日，但描述的父主题版本不同（0.25.0dev0 vs 0.23.0）。这是本报告最重要的风险前提，见 §6 V-06 与风险 R1。

### 1.3 本次实际执行的核验

1. 全量读取两包 `index.md`、`spec/facts.md`、`spec/insights.md`、`spec/patterns.md`、`spec/review.md`、`log.md`。
2. 抽样精读核心机制文档：PST 导航与 toctree、品牌与暗色模式；SBT 页面分区、页眉按钮、边注与 margin。
3. 脚本审计 53 个 Markdown 的文件数、行数、标题数、表格行数、frontmatter 覆盖、内部链接可达性。
4. 交叉核对两包对同一事实的描述（版本、选项默认值、导航模型、按钮能力）。
5. 排除代码块后复核断链：**两包均为 0 断链**（SBT 初次报出的 1 处为 Jinja 代码被正则误判，见 V-04）。

---

## 2. 全景解剖

### 2.1 pydata-sphinx-theme：把主题做成"构建期应用"

**定位**：PyData 社区维护的 Sphinx HTML 主题，Bootstrap 5 骨架，服务 NumPy / pandas / SciPy / Matplotlib / Xarray 这类"文档即产品门面"的站点。

**规模指标**（均可回查）：

| 指标 | 值 | 证据 |
|---|---|---|
| 事件回调 | 11 个（3 × `builder-inited` + 6 × `html-page-context` + 2 × `build-finished`） | PST-F-010~012 |
| 页面区段 | 9 个 `sections/` 片段 | PST-F-036 |
| 可插拔组件 | 23 个 `components/` 模板 | PST-F-037 |
| 主题选项 | 约 50 个（31 通用/功能 + 17 模板放置 + 2 废弃别名） | PST-F-026 |
| 本地化 | 10 种语言目录 | PST-F-084 |
| 测试 | 构建快照 + Playwright/Axe 可访问性 + 交互测试 | PST-F-085~087 |

**构建时序（简化）**：

```text
builder-inited
  ├── add_shorten_xform      注册链接缩短 post-transform
  ├── setup_translators      按 builder 动态构造 translator
  └── update_config          迁移废弃键、校验 switcher、合成 icon_links
        ↓（Sphinx 读取 + 解析 + 写出 HTML）
html-page-context（每页 6 次回调）
  ├── canonical URL 修正（dirhtml）
  ├── 编辑链接 / 源码链接
  ├── 顶部导航与侧栏树生成（toctree.py）
  ├── 模板补后缀 + 空渲染剔除 + CSS 去重
  ├── 双 logo 路径计算
  └── 次级侧栏按页匹配
        ↓
build-finished
  ├── 重写 pygments.css（light/dark 双前缀）
  └── 复制本地 logo 到 _static
```

**能力主线**：

1. **三套目录，三套算法**：顶部导航只遍历 `root_doc` 的 toctree 顶层条目；侧栏从"当前顶层祖先"解析子树并做缓存；页内 TOC 直接改写 `context["toc"]`（PST-F-046~053）。
2. **双主题是同一份 HTML 的状态**：`data-theme` + CSS 变量 + 双前缀 Pygments，不生成第二份页面（PST-F-063~069）。
3. **布局即配置**：每个区段是有序模板名列表，空渲染自动移除（PST-F-039~040）。
4. **产品化外设**：版本切换器（含 404 回退）、版本警告横幅（14 天抑制）、公告条、即时搜索（300ms 防抖）、分析脚本注入（PST-F-020~021、F-071~074）。

**最短可用配置**（来自概念与示例文档的共识形态）：

```python
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "header_links_before_dropdown": 4,
    "show_nav_level": 2,
    "navigation_depth": 4,
    "search_as_you_type": True,
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}
```

**它不擅长**：线性阅读体验、边注排版、Notebook 交互启动；这些不在其设计目标内。

### 2.2 sphinx-book-theme：在父主题上做"阅读流改造"

**定位**：Executable Books 团队维护的书籍式主题，Jupyter Book 默认主题，面向教程、教材、研究报告、可复现实验。

**规模指标**：

| 指标 | 值 | 证据 |
|---|---|---|
| 继承声明 | `inherit = pydata_sphinx_theme` | SBT-F-044 |
| 模板覆盖 | 仅 3 个 block（navbar / main / body） | SBT-F-066~069 |
| 自有组件 | 7 个 `components/` + 1 个 `sections/` + 1 个 `macros/` | SBT-F-070~072 |
| 自有选项 | 29 个（含 1 个已废弃） | SBT 选项速查表 |
| 事件优先级 | `update_navbar_defaults` 400（早于父主题）；按钮钩子 501（晚于父主题） | SBT-F-023、F-029 |
| 翻译 | 22 个 locale JSON，catalog 名 `booktheme` | SBT-F-022、F-129 |
| 测试 | 构建快照（`pytest-regressions`），无独立 a11y 套件记录 | SBT-F-131~135 |

**页面模型**：

```text
┌──────────────────────────────────────────────────────────────┐
│ announcement（可选）                                          │
├──────────────┬───────────────────────────────┬───────────────┤
│ primary      │ article header（工具箱）        │ secondary     │
│ sidebar      ├───────────────────────────────┤ sidebar       │
│ 全书目录      │ 单列正文（Tufte 阅读流）        │ 页内 TOC      │
│              │  ── 边注 / margin 溢出到右留白 ──│               │
├──────────────┴───────────────────────────────┴───────────────┤
│ content footer（作者/版权/更新） → site footer                │
└──────────────────────────────────────────────────────────────┘
```

**三条独有能力链**：

1. **页眉按钮 = 数据 + 宏**：Python 侧生成按钮字典（下载组 / 全屏 / 源码 / 编辑 / issue / 仓库 / 6 类启动服务），Jinja 只按 `type` 映射到 `render_funcs`（SBT-F-073~074、F-086~110）。启动服务覆盖 Binder、JupyterHub、Colab、Deepnote、JupyterLite、Thebe。
2. **边注 = 文档树变换**：`HandleFootnoteTransform` 在 post-transform 阶段把脚注搬到引用点，生成 `SideNoteNode`；`{-}` 前缀转无编号 margin note；块级内容走 `{margin}` 指令（SBT-F-111~124）。
3. **Notebook 协作边界**：主题只负责 HTML 结构与按钮，执行由 `myst-nb`、`sphinx-thebe` 完成；`.ipynb` 下载依赖构建期复制（SBT-F-095~107）。

**最短可用配置**：

```python
html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/org/repo",
    "path_to_docs": "docs",
    "use_download_button": True,
    "use_fullscreen_button": True,
    "use_sidenotes": True,
    "show_navbar_depth": 2,
    "launch_buttons": {"binderhub_url": "https://mybinder.org", "colab_url": "https://colab.research.google.com"},
}
```

**它不擅长**：多产品门户、多读者角色、复杂版本矩阵（官方定位与 SBT-I-007 均指向此结论）；且已进入维护模式。

---

## 3. 十二维对比

### D1 生态位与阅读模型

| 维度 | PST | SBT |
|---|---|---|
| 首要读者 | 科学计算库的 API + 指南站点 | 教材/教程的连续读者 |
| 导航世界观 | 站点地图：多个并列顶层章节 | 书本：全书一条主线 |
| 首屏结构 | 顶部导航 + 左章节树 + 右页内 TOC | 左全书目录 + 单列正文 + 右边注/TOC |
| 页面操作入口 | 右侧栏（编辑/源码/页内 TOC） | 页眉工具箱（下载/源码/仓库/启动） |
| 面包屑 | 默认开启（`article_header_start = breadcrumbs`） | 默认关闭，改为侧栏开关按钮 |

**判读**：这不是审美差异，而是两种信息架构。PST 假设"读者从多个入口跳入"；SBT 假设"读者从第 1 章读到第 N 章"。SBT 把面包屑换成"切换侧栏"按钮，正是线性阅读不需要位置回溯的直接体现。

### D2 版本与维护

| 维度 | PST | SBT |
|---|---|---|
| 当前源码版 | `0.25.0dev0` | `1.5.0.dev` |
| 最近正式版 | 活跃迭代中 | `1.4.0`（2026-07-19） |
| 维护声明 | 无维护模式提示 | README 明确 **Maintenance Mode** |
| 新功能预期 | 持续 | 不保证 |
| 风险 | 默认值随版本变化 | 能力停滞、父主题差距扩大 |

**判读**：一个在加速，一个在冻结。二者组合使用意味着"子包冻结 + 父包演进"，差距只会变大，SBT 的精确版本锁是必要防御而非保守选择（SBT-I-007）。

### D3 依赖与兼容

| 项 | PST | SBT |
|---|---|---|
| Python | `>=3.11` | `>=3.11` |
| Sphinx | `>=8.2,<10` | `>=8.2` |
| 父主题 | `basic`（Sphinx 内置） | `pydata-sphinx-theme==0.23.0`（精确） |
| 构建后端 | `sphinx-theme-builder>=0.3.2` | `sphinx-theme-builder>=0.2.0a7` |
| Node | `24.22.2` | `20.9.0` |
| 前端依赖 | Bootstrap 5.2+、Popper、FontAwesome 7、compare-versions | 继承父主题，另加自有 SCSS/JS |
| 许可证 | BSD-3-Clause（同族） | BSD-3-Clause |

**判读**：两包的 Node 版本不一致（24 vs 20），在同一 monorepo 内并行开发时需要分别准备工具链。SBT 的精确锁意味着父主题的安全修复不会自动流入。

### D4 架构范式

| 维度 | PST | SBT |
|---|---|---|
| 与下游关系 | 继承 Sphinx `basic`，重写骨架 | 继承 PST，只覆盖差异 |
| 装配方式 | `setup()` 连接 11 个回调 | `setup()` 同时注册主题/指令/节点/变换/事件（13 类） |
| 复杂度载体 | 构建期 Python（导航、模板过滤、资源改写） | Python（按钮、变换）+ 薄模板 + JS 适配层 |
| 配置写入时机 | `update_config` 直接改 `builder.theme_options` | `setup()` 内直接调用 + `config-inited` 双保险 |
| 并行安全 | `parallel_read_safe / write_safe = True` | 同 |

**判读**：PST 的问题域是"如何在 Sphinx 生命周期内改写构建结果"；SBT 的问题域是"如何在父主题的契约上安全叠加"。后者的难点不在写代码，而在**知道父主题哪些行为不能被覆盖**。

### D5 布局与区段

| 维度 | PST | SBT |
|---|---|---|
| 区段数 | 9 | 继承 9 + 自有 `footer-content` |
| 组件数 | 23 | 7 |
| 区段配置 | 模板名列表 + 空渲染剔除 | 同机制，仅处理 `theme_footer_content_items` |
| 次级侧栏默认 | `page-toc, edit-this-page, sourcelink` | `page-toc.html` |
| 页脚 | `footer_start/center/end` 三段 | 内容页脚四项（作者/版权/更新/自定义）+ 站点页脚 |
| 覆盖粒度 | 可整段替换 | 只覆盖 3 个 block，其余靠组件替换 |

**判读**：SBT 的"薄"体现在组件数量（7 vs 23），但它通过"组件替换"而非"模板重写"获得定制力——这是继承设计的正确用法，也让升级面收敛到少数文件。

### D6 导航算法

| 维度 | PST | SBT |
|---|---|---|
| 顶部导航 | 遍历 `root_doc` 顶层条目 + 外链 | 默认不渲染（`navbar_*` 全空） |
| 主侧栏范围 | 当前顶层祖先的子树 | **全书树**（`startdepth=0`） |
| 展开控制 | `show_nav_level` / `navigation_depth` / `collapse_navigation` | `show_navbar_depth` / `max_navbar_depth` / `collapse_navbar` |
| 缓存 | 有（键含祖先/输出目录/层级），`dirhtml` 不缓存 | 复用父主题缓存路径 |
| 当前页标记 | 构建期写入，缓存命中时搬运 | 同 |
| 折叠控件 | `<details>/<summary>` | 同 |

**判读**：这是两包最容易踩坑的一维。SBT 的侧栏模板显式传入 `show_nav_level=theme_show_navbar_depth`（SBT-F-075），因此**在 SBT 下设置父主题的 `show_nav_level` 对主侧栏无效**。同理 `navigation_depth` 被 `max_navbar_depth` 取代。

### D7 配置系统

| 维度 | PST | SBT |
|---|---|---|
| 选项来源 | 单一 `theme.conf`（约 50 项） | 自有 29 项 + 继承父主题约 50 项 |
| 默认值风格 | 提供完整默认组合（navbar 四区有默认组件） | **清空** navbar 四区，导航搬进左栏 |
| 类型处理 | Python 侧转换 + 模板 `int` 过滤器 | 显式 `as_bool()` / `tobool` / `int` 过滤器 |
| 同名键语义 | 基准语义 | 部分键语义反转或失效（见下表） |
| 文档可发现性 | 一包查全 | 需两包交叉查 |

**同名不同义清单**（跨包迁移的高危区）：

| 配置 | PST 默认/语义 | SBT 默认/语义 | 后果 |
|---|---|---|---|
| `navbar_start` | `navbar-logo` | 空 | 照抄 PST 配置不会得到 logo 区 |
| `navbar_center` | `navbar-nav` | 空 | 顶部导航默认不存在 |
| `navbar_end` | `theme-switcher, navbar-icon-links` | 空 | 主题切换器需自行放回 |
| `navbar_persistent` | `search-button-field` | 空（运行时 `[]`） | 移动端常驻区为空 |
| `secondary_sidebar_items` | `page-toc, edit-this-page, sourcelink` | `page-toc.html` | 编辑/源码链接消失 |
| `show_nav_level` | 主侧栏展开层级 | 被 `show_navbar_depth` 取代 | 设了不生效 |
| `navigation_depth` | 侧栏最大层级 | 被 `max_navbar_depth` 取代 | 设了不生效 |
| `collapse_navigation` | 关闭折叠 | 被 `collapse_navbar` 取代 | 设了不生效 |

### D8 样式与资产管线

| 维度 | PST | SBT |
|---|---|---|
| 样式源 | SCSS（Bootstrap 定制）+ 主题 CSS 变量 | SCSS 分层（abstracts/base/components/content/extensions/sections） |
| 编译 | webpack + sass，产物不入库 | `sphinx-theme-builder` + webpack，产物不入库 |
| 缓存失效 | CSS 去重；Pygments 双前缀重写 | 资源追加 `?digest=sha1`（仅主题自身 CSS/JS） |
| 高亮 | `pygments_light_style` / `pygments_dark_style`（a11y 高对比默认） | 继承父主题，`pygments_style = tango` |
| 颜色定制 | `html[data-theme] { --pst-color-primary: light-dark(...) }` | 同（变量来自父主题） |
| 暗色模式 | `data-theme` + CSS 变量 + 首屏内联脚本 | 继承 |

**判读**：两者共享同一套变量与暗色机制，定制知识可迁移；但 SBT 的哈希缓存只覆盖自身资源（SBT-F-040~041），子主题必须自己声明样式表（SBT-I-006）。

### D9 差异化能力

| 能力 | PST | SBT | 备注 |
|---|---|---|---|
| 版本切换器 + 警告横幅 | ✅ 一等公民 | ✅ 继承（0.23.0 实现） | SBT 未覆盖该链路 |
| 即时搜索（300ms） | ✅ | ✅ 继承 | |
| 公告条（14 天抑制） | ✅ | ✅ 继承 | |
| 编辑/源码/issue 链接 | ✅ 右栏 | ✅ 页眉按钮（可配） | 入口位置不同 |
| 下载 `.md`/`.ipynb`/PDF | ❌ | ✅ | 书籍场景核心 |
| 在线启动（Binder/Colab/Thebe 等 6 类） | ❌ | ✅ | |
| 脚注转边注 / margin | ❌ | ✅ | post-transform 实现 |
| 全宽内容 | 部分（表格滚动） | ✅ `full-width` | |
| 面包屑 | ✅ 默认 | ❌ 默认关 | |
| Google/Plausible 分析注入 | ✅ | 继承 | |

### D10 可访问性与测试

| 维度 | PST | SBT |
|---|---|---|
| 语义补齐 | `aria-level`、`aria-current`、skip link、`<dialog>` | 继承 + 自有 checkbox/label 边注结构 |
| 键盘交互 | Ctrl/Cmd+K 搜索、Escape 关闭、方向键导航（可配） | 继承 |
| 自动化 a11y | Playwright + Axe 扫描 Kitchen Sink | 未见独立 a11y 套件 |
| 回归测试 | 构建快照 + 交互测试 + 链接缩短测试 | 构建快照（含按钮快照） |
| 已知局限 | 自动化仅覆盖 30–40% 问题 | 无声明 |

**判读**：SBT 的边注用 `<input type=checkbox>` + `<label>` 实现无 JS 展开，语义上是巧妙的；但"上标编号 + 隐藏 checkbox"对读屏器的实际体验需要人工验证，两包都没有这类实测记录。

### D11 定制与升级成本

| 维度 | PST | SBT |
|---|---|---|
| 定制入口 | 区段模板列表、`html_sidebars`、CSS 变量、translator/transform | 组件替换、子主题、`html_theme_options`、margin 类 |
| 典型改动成本 | 低（改配置）→ 中（换组件）→ 高（改 translator） | 低（改选项）→ 中（换组件）→ 高（覆盖 block） |
| 升级风险面 | 默认值与模板结构 | 父主题 block 名、上下文变量、快照、翻译目录、按钮 URL |
| 升级动作 | 对齐 release notes | 六步检查：依赖→配置→模板→样式→测试→产物（SBT-I-007） |
| 版本策略 | 跟随发布 | 生产锁 `1.4.0` + 锁父主题 `0.23.0` |

### D12 知识包质量

| 指标 | PST | SBT |
|---|---|---|
| Markdown 文件 | 29 | 24 |
| 总行数 | 3,699 | 4,474 |
| 总字符 | 107,746 | 127,526 |
| 平均行/篇 | 127.6 | 186.4 |
| 标题数 | 279 | 310 |
| 表格行 | 499 | 576 |
| 代码块 | 130 | 182 |
| 内部链接 | 110 | 91 |
| 断链 | 0 | 0 |
| frontmatter 覆盖 | 28/29（仅 `log.md` 缺） | 20/24（3 个 index + log 缺） |
| 事实 / 洞察 / 模式 | 88 / 6 / 3 | 185 / 7 / 0 |
| 对抗审查 | 9 条修正 + 4 条确认 + 风险清单 | 无 `review.md` |
| 结论 | 四阶段产物完整，可追溯 | 事实最密，但缺 E/V 产物 |

**判读**：SBT 每篇更长、表格更多、事实更密（185 条），说明采集粒度细到函数级；PST 胜在**产物结构完整**——有模式可复用、有审查可追溯。两种"厚"不是一回事。

---

## 4. 洞察

### I-01 继承税：代码越薄，契约越硬

- **陈述**：SBT 以 3 个 block、7 个组件、29 个自有选项获得 PST 的全部布局与产品化能力，但它必须精确锁定父主题 `0.23.0`，并把父主题的 block 名、上下文变量、DOM 类名当作不可违约的契约。
- **证据**：SBT-F-004、F-044、F-066~069、F-070~072；SBT-I-001、I-007。
- **反常识**：通常认为"继承 = 少写代码 = 低维护"；这里恰好相反——覆盖点越少，单点失效的影响面越大（父主题改一个 block 名，子主题整体失效），所以要用精确版本锁把不确定性挡在门外。
- **行动**：采用继承式主题时，把"父版本 + 覆盖点清单 + 快照测试"三件套写进仓库；升级按六步清单执行，不盲目重生成快照。

### I-02 复杂度守恒：选主题是选"维护哪一类复杂度"

- **陈述**：PST 的复杂度集中在构建期导航算法（祖先定位、缓存键、标记搬运）与双主题产物改写；SBT 把页面复杂度换成 URL 矩阵（3 provider × 6 启动平台）、文档树变换与父主题行为补丁。总量没有减少，只是换了位置。
- **证据**：PST-F-045~054、F-063~064；SBT-F-086~110、F-111~124、F-171~179。
- **反常识**：SBT 的 `index.js` 里有 `fixSidebarToggle` 用 capture phase 拦截父主题事件、`initTocHide` 用 `IntersectionObserver` 在边注进入视口时隐藏右栏——这些不是功能，是**为维持书籍阅读流而打的补丁**。补丁越多，说明两套布局模型摩擦越大。
- **行动**：评估主题时先问"我的团队更擅长维护 Python 构建逻辑，还是 CSS/JS 适配层"；不要假设"主题越轻，运维越轻"。

### I-03 两种世界观共用一套骨架

- **陈述**：两包共享 Bootstrap 5 网格、PST 的 section 模板与 `data-theme` 机制；差异靠"列宽 + 侧栏内容 + 观察器"实现，而不是两套 HTML 骨架。
- **证据**：SBT-F-066~069（只改 3 个 block）、F-171~174（观察器与 rootMargin）、F-178~179（≥992px 拦截）；PST-F-036~038。
- **反常识**：书籍主题并没有"另一套布局引擎"，它是在三栏网格上把中列变窄、把溢出内容推到右留白。因此 SBT 的布局问题经常表现为"父主题行为不合适"，而不是"本书模板写错"。
- **行动**：SBT 布局异常时，先在 PST 源码里定位该行为是否由父主题产生，再决定是改子主题组件还是加适配层；适配层要集中登记，避免散落在多个 JS 文件。

### I-04 同名配置不同义：跨包抄配置的头号陷阱

- **陈述**：`navbar_*` 在 SBT 中默认全空；`show_nav_level` / `navigation_depth` / `collapse_navigation` 在 SBT 主侧栏路径下被 `show_navbar_depth` / `max_navbar_depth` / `collapse_navbar` 取代。
- **证据**：PST-F-027~030、PST 选项速查；SBT-F-057~060、F-075。
- **反常识**：这些键并未报错、也不会告警——设了就是不生效。SBT 继承了父主题的选项定义，却在自己的侧栏模板里换了一套参数名，形成"合法但无效"的配置。
- **行动**：从 PST 迁到 SBT 时，按"同名不同义清单"逐项改写；在项目里维护一份 `html_theme_options` 归属表（父/子），升级时对照。

### I-05 验证声明 ≠ 验证证据

- **陈述**：SBT 全部文档标注 `verified: { by: "process:seven-concepts-v" }`，但包内没有 `review.md`、没有 `patterns.md`、没有进程登记；PST 则有完整的 9 条修正记录与 4 条确认项。
- **证据**：两包 `spec/` 目录对比；PST `spec/review.md`；SBT `log.md` 自述为"R/I 阶段工作稿"。
- **反常识**：事实条数更多（185 vs 88）容易让人给出更高可信度评价，但"可复核密度"取决于审查记录，而不是采集数量。没有 V 产物的 `verified` 字段只是元数据，不构成证据链。
- **行动**：评估知识包时先看 `spec/` 四件套是否齐全；缺 `review.md` 的包，其 `verified` 应降级为"待复核"，引用时优先回查源码。

### I-06 版本漂移会静默产生错误建议

- **陈述**：PST 知识包基线为 `0.25.0dev0`，SBT 锁 `0.23.0`；PST 文档中"v0.24.0 起 FontAwesome `<i>` 不再转 `<svg>`"、a11y 高对比高亮默认值等结论，对 SBT 用户不成立。
- **证据**：PST-F-068、F-031；SBT-F-004；两包同日生成、同一 `stale_after`。
- **反常识**：两个包互相链接、同组同源，读者会自然认为它们描述同一版本；实际是两个时间切片。交叉引用不会报错，只会给出"看起来对"的错误配置。
- **行动**：在 SBT 项目里查 PST 文档前，先确认该文档描述的行为是否存在于 0.23.0；给知识包加"父主题版本适用区间"字段，比统一 `stale_after` 更有用。

---

## 5. 模式萃取

### P-01 双层主题继承契约

**触发场景**：需要在成熟主题之上做垂直领域改造（书籍、教程、企业规范），又不想从零实现骨架。

**结构**：

```text
基础主题（骨架 + 通用能力）
    ▲ theme.conf: inherit
子主题（只覆盖差异 block + 组件替换 + 增量注册）
    ▲ entry point: sphinx.html_themes
最终站点
```

**步骤**：

1. 用 `theme.conf` 的 `inherit` 与模板 `extends` 建立继承，不复制父模板。
2. 只覆盖必要 block；覆盖清单写入仓库文档。
3. 新增能力走 `setup()` 注册（指令、节点、transform、事件），不另发扩展包。
4. 用事件优先级解决时序（早于父主题用 400，晚于用 501）。
5. 精确锁定父版本，并把快照测试作为契约验证。

**反模式**：整份复制父主题 `layout.html` 再改；用 `!important` 覆盖父样式；升级时 `--force-regen` 全部快照。

**迁移验证**：套到"企业设计系统 + 产品站点"场景，检查是否只需覆盖少量 block 与组件即可完成品牌化；若需重写骨架，则继承不成立。

### P-02 薄覆盖 + 双源配置索引

**触发场景**：子包只声明差异配置，父包配置仍可用，用户需要知道"哪个键属于谁、是否已失效"。

**结构**：

```text
自有选项表（含默认值/类型/模板变量）
继承选项表（标注父版本 + 是否被子包覆盖）
同名不同义清单（键 / 父语义 / 子语义 / 后果）
```

**步骤**：

1. 子包 `theme.conf` 只写差异项，并在文档中列全。
2. 单独维护"继承选项"表，标注适用父版本。
3. 对被子包替换的父选项，显式写"已失效/被 X 取代"。
4. 升级时对照三张表做配置审计。

**反模式**：文档只写"支持父主题全部选项"；默认值改动不写迁移说明；同名键静默失效。

**迁移验证**：套到任何"框架 + 插件"组合（如 Django + 第三方 app），检查用户能否在一页内判断配置归属。

### P-03 父主题适配层清单化

**触发场景**：子主题必须在运行时修正父主题行为（布局冲突、事件顺序、断点差异）。

**结构**：

```text
assets/scripts/
  ├── index.js          入口，只做初始化编排
  ├── adapters/         每个父主题行为差异一个文件
  └── ADAPTERS.md       清单：问题 / 拦截点 / 依赖的父主题假设 / 失效信号
```

**步骤**：

1. 每个补丁只解决一个父主题行为差异，独立文件。
2. 记录它依赖的父主题 DOM/类名/断点。
3. 在父主题升级检查清单中加入"逐条验证适配层"。
4. 父主题修复后删除对应补丁，而不是层层叠加。

**反模式**：补丁散落在主入口；用 capture phase 拦截却不写原因；补丁依赖具体像素值而无注释。

**迁移验证**：SBT 的 `fixSidebarToggle`（capture phase、992px 断点）与 `initTocHide`（观察器、-33% rootMargin）正是该模式的反面教材——它们有效，但缺少清单化治理。

---

## 6. 对抗审查（V 阶段）

### 6.1 对报告结论的质疑与处置

| # | 质疑 | 证据 | 处置 |
|---|---|---|---|
| V-01 | "SBT 缺少版本切换器"是否成立？ | 证伪：SBT-F-077 显示 `article-header-buttons.html` 直接 include `theme-switcher.html`；theme.conf 未覆盖该链路 | 已改为"继承 0.23.0 实现，文档未展开" |
| V-02 | "两包导航选项同名"是否成立？ | 证伪：SBT-F-075 传入 `show_nav_level=theme_show_navbar_depth` | 已改写为"同名键语义被替换"，并补充失效清单 |
| V-03 | "SBT 事实更少、质量更低"是否成立？ | 证伪：185 > 88；真实差距在 patterns/review 缺失 | 已区分"事实密度"与"产物完整度"两个指标 |
| V-04 | "SBT 有 1 处断链"是否成立？ | 证伪：该处为代码块内 Jinja `render_funcs[btype](**bopts)` 被链接正则误判；排除代码块后为 0 | 已撤销该结论，并在附录记录方法 |
| V-05 | SBT 的 `verified` 声明是否可追溯？ | 成立：无 `spec/review.md`、无 `references/processes/` 登记，`log.md` 自述 R/I 工作稿 | 记为 I-05，并建议降级为"待复核" |
| V-06 | PST 的 `0.25.0dev0` 结论能否用于 SBT？ | 不成立：SBT 锁 0.23.0；PST-F-068 明确 v0.24.0 起行为变化 | 记为 I-06，并写入选型风险 R1 |

### 6.2 确认无需修改

| # | 项 | 核查 |
|---|---|---|
| C-01 | PST 的 11 个回调计数 | 3+6+2，与 facts 一致 |
| C-02 | SBT 只覆盖 3 个 block | `docs_navbar` / `docs_main` / `docs_body`，与 facts 一致 |
| C-03 | 两包断链为 0 | 排除代码块后脚本复核通过 |
| C-04 | SBT 的精确版本锁是必要设计 | `layout.html` 依赖父 block 与上下文变量，锁版本可解释 |

### 6.3 剩余风险

| # | 风险 | 影响 | 缓解 |
|---|---|---|---|
| R1 | 父主题版本漂移（0.25 vs 0.23） | 交叉引用给出错误配置 | 查 PST 文档前确认 0.23.0 是否具备该行为 |
| R2 | SBT 维护模式 | 新功能停滞，与父主题差距扩大 | 生产锁 `1.4.0`；评估 fork/子主题成本 |
| R3 | 配置双源 | 用户误设失效键 | 维护"同名不同义清单" |
| R4 | 适配层脆弱 | 父主题改 DOM 即失效 | 适配层清单化 + 升级逐条验证 |
| R5 | 未做真实浏览器/读屏实测 | 边注与抽屉的 a11y 结论未经实测 | 上线前人工键盘 + 读屏抽查 |
| R6 | 知识包 `verified` 不可追溯（SBT） | 引用强度被高估 | 关键结论回查源码 |

### 6.4 质量门自检

| 门 | 要求 | 本次结果 |
|---|---|---|
| G1 | 事实无因果词 | 通过：§2、§3 的表格只陈述差异，因果解释集中在 §4 洞察 |
| G2 | 洞察四元组完整 | 通过：6 条均含陈述/证据/反常识/行动 |
| G3 | 模式可迁移 | 通过：3 个模式均给出非当前领域的迁移验证 |
| G4 | 行动项原子化 | 部分适用：本报告不含行动项清单，§7 给出可独立执行的迁移步骤 |
| V 门 | ≥5 条实质质疑，≥2 条采纳 | 通过：6 条质疑，4 条采纳并改写结论 |

---

## 7. 选型决策

### 7.1 决策树

```text
文档主体是什么？
├── API 参考 + 指南 + 多版本文档
│   └── 需要顶部导航/版本切换/即时搜索 → PST
├── 教程 / 教材 / 课程 / 实验报告（连续阅读）
│   ├── 使用 MyST / Notebook → SBT（Jupyter Book 默认）
│   └── 需要边注、margin、全宽图 → SBT
├── 多产品门户 / 多读者角色
│   └── 两者都不合适 → 门户型方案或自建
└── 只需 API 文档、追求极简
    └── alabaster / Furo 更轻
```

### 7.2 场景矩阵

| 场景 | 首选 | 理由 | 注意 |
|---|---|---|---|
| NumPy 风格科学计算站点 | PST | 版本切换、搜索、品牌化开箱即用 | 选项多，先读速查表 |
| 课程讲义 / 教材 | SBT | 单列阅读 + 边注 + 下载 | 锁 `1.4.0` 与父主题 |
| Jupyter Book 项目 | SBT | 默认主题，Notebook 链路完整 | 确认 JB 版本对应主题版本 |
| 企业规范手册（线性） | SBT | 书籍目录 + 页眉工具箱 | 主题维护模式，长期需评估 |
| 多产品文档门户 | 两者均非最优 | 导航模型不匹配 | 考虑自建或门户方案 |
| 已有 PST 站点加"书籍感" | 不要直接换 | 导航模型与入口位置全变 | 先做单章试点 |

### 7.3 迁移路径

**PST → SBT**：

1. 安装 `sphinx-book-theme==1.4.0`，把 `html_theme` 改为 `sphinx_book_theme`。
2. 按"同名不同义清单"改写 `show_nav_level` → `show_navbar_depth`、`navigation_depth` → `max_navbar_depth`、`collapse_navigation` → `collapse_navbar`。
3. 把 `navbar_*` 自定义项迁移到 `sidebars` 或 `html_sidebars`（SBT 默认清空 navbar）。
4. 右栏的编辑/源码链接改为页眉按钮（`use_edit_page_button` / `use_source_button`）。
5. 需要边注时开 `use_sidenotes`，并检查脚注是否为行内内容。
6. 配置 `repository_url` / `path_to_docs`，否则下载与源码按钮不生成。
7. 跑构建快照，逐页确认面包屑消失、侧栏变全书树是预期行为。

**SBT → PST**：

1. 移除 `use_sidenotes`；把 `{margin}` 块改回脚注或提示框。
2. 页眉按钮能力（下载/启动）在 PST 无对应物，需扩展或放弃。
3. 侧栏从全书树变为"当前顶层章节子树"，重新设计顶层 toctree。
4. 恢复右栏 `edit-this-page` / `sourcelink`。
5. 重新评估阅读流：单列窄栏会变成三栏布局，需重做排版验收。

---

## 8. 学习路径建议

### 8.1 使用者（各 30–60 分钟）

| 顺序 | PST | SBT |
|---|---|---|
| 1 | 简介 → 快速开始 → 基础站点示例 | 定位与生态 → 安装与最小站点 → 书籍站点示例 |
| 2 | 配置项速查（按需查） | 选项速查（按需查） |
| 3 | 导航与 toctree | 页面分区与导航 |

### 8.2 定制者（各 2–3 小时）

| 顺序 | PST | SBT |
|---|---|---|
| 1 | 架构总览（事件管线） | 主题骨架与构建链 |
| 2 | 布局与模板区段 | 页面分区 + 页眉按钮机制 |
| 3 | 品牌、样式与暗色模式 | 边注、margin 与全宽内容 |
| 4 | 搜索、版本切换与公告 | Notebook 与在线交互 |
| 5 | 内部实现与扩展点 | 定制、子主题与主题开发 |

### 8.3 维护者（各 1 天）

1. 先读 PST 的 `spec/patterns.md`（3 个可迁移模式），建立"构建期计算 + 运行期交互"的心智模型。
2. 再读 SBT 的 `spec/insights.md`，重点看 I-002（双初始化约束）与 I-007（升级即项目）。
3. 对照两包 `references/source-map.md` 走一遍源码目录。
4. 用一页纸写下"父主题契约清单"：block 名、上下文变量、DOM 类、断点。

**交叉学习顺序**：先 PST 后 SBT。理由是 SBT 的多数"异常"只有理解了 PST 的导航缓存、模板过滤与双主题机制后才能解释；反过来先学 SBT 会把父主题行为误认为子主题缺陷。

---

## 9. 附录

### A. 审计数据

| 指标 | PST | SBT |
|---|---|---|
| 文件数 | 29 | 24 |
| 总行数 | 3,699 | 4,474 |
| 总字符 | 107,746 | 127,526 |
| 平均行/篇 | 127.6 | 186.4 |
| 标题 | 279 | 310 |
| 表格行 | 499 | 576 |
| 代码块 | 130 | 182 |
| 内部链接（排除代码块） | 110 | 91 |
| 断链 | 0 | 0 |
| frontmatter | 28/29 | 20/24 |
| spec 产物 | facts / insights / patterns / review | facts / insights |

审计脚本：`.cowork-temp/bundle-audit.js`（一次性工具，未纳入交付）。

### B. 事实抽样对照

| 主题 | PST 事实 | SBT 事实 | 差异含义 |
|---|---|---|---|
| 继承基线 | `inherit = basic`（PST-F-025） | `inherit = pydata_sphinx_theme`（SBT-F-044） | 两层级联 |
| 组件规模 | 23 个（PST-F-037） | 7 个（SBT-F-070） | 薄覆盖 |
| 侧栏范围 | 祖先子树（PST-F-048） | `startdepth=0` 全书树（SBT-F-075） | 导航世界观 |
| 右栏默认 | TOC + 编辑 + 源码（PST-F-028） | 仅 TOC（SBT-F-049） | 操作入口迁移 |
| 主题切换 | `data-theme` + 变量（PST-F-063~069） | 继承 + checkbox 边注结构（SBT-F-120） | 机制复用 |
| 测试 | 快照 + Axe/Playwright | 快照为主 | a11y 保障差异 |

### C. 术语

| 术语 | 含义 |
|---|---|
| 区段（section） | 页面上的一个可配置区域，由模板名列表组成 |
| 组件（component） | 放入区段的单个模板，如 `page-toc`、`navbar-logo` |
| 薄覆盖 | 子主题只覆盖差异 block，不复制父模板 |
| 继承税 | 因依赖父主题契约而产生的升级与排查成本 |
| 适配层 | 在运行时修正父主题行为的 JS/CSS 补丁集合 |

### D. 复核方法

1. 打开任一包的 `spec/facts.md`，按 `F-xxx` 找到源码路径。
2. 打开 `spec/review.md`（PST 有）核对质疑与修正；SBT 需直接回查源码。
3. 按 `references/source-map.md` 进入仓库目录验证。
4. 对本报告的结构性数字，可用附录 A 的脚本重跑复现。

---

## 附：本次交付的边界

- 未修改两个知识包的任何文件；本报告为独立产物。
- 未执行真实浏览器构建与读屏实测；相关结论均来自源码与包内文档。
- 版本判断以包内 `pyproject.toml` / `__init__.py` 记录为准，未联网核对上游最新提交。
- 报告中所有定量指标可由附录 A 的脚本复现；定性判断均标注了可回查的证据编号。
