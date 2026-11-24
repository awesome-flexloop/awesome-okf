---
type: Report
title: "里程碑复盘：mystx 主题 P0–P4 与发布前收尾"
description: "对 2026-11-24 15:15–17:41 的 mystx 主题建设（基座切换 → P4 → 收尾修正 → 文档原子化 → MyST 接入 → 视口与可达性实测）做 R/I/V/E/A 全链路复盘"
tags: [retrospective, milestone, seven-concepts, sphinx-theme, a11y, report]
generated: { by: "main-agent/lobsterai", at: "2026-11-24T17:47:08+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T17:55:00+08:00" }
status: stable
stale_after: 2027-05-24
sources:
  - id: repo-mystx
    resource: projects/xuanspace/libs/mystx
    title: mystx 主题仓库（36 次提交，15:15–17:41）
    commit: f54db57
  - id: repo-xuanspace
    resource: projects/xuanspace
    title: xuanspace 子模块（mystx 指针）
    commit: 2c73514
  - id: repo-specweave
    resource: .
    title: SpecWeave 外层仓（xuanspace 指针）
    commit: 7dc8cb93c
  - id: design
    resource: projects/xuanspace/libs/mystx/doc/dev/design/
    title: 设计文档（9 个原子页）
  - id: method
    resource: .agents/commands/seven-concepts.md
    title: 七概念方法论编排指令集
scope: 单里程碑（主题从零到可发布：P0–P4 + 收尾 + 文档 + 兼容性）
---

# 里程碑复盘：mystx 主题 P0–P4 与发布前收尾

> **一句话结论**：能力层几乎一次成型——真正的返工全部落在「页面级布局判定」和「不溢出但不可用」这两类看不见的语义上，而不是配色、字号或组件实现。

## 目录

- 复盘摘要
- 时间线与事实清单（R）
- 洞察（I）
- 对抗审查（V）
- 模式萃取（E）
- 原子行动项（A）
- 质量门自检
- 附录：指标与口径

---

## 0. 复盘摘要

| 项 | 结果 |
|---|---|
| 任务 | 基于 pydata-sphinx-theme 造书籍化主题 mystx，借鉴 sphinx-book-theme 的阅读能力 |
| 起止 | 15:15（基座切换首次提交）→ 17:41（可达性修复提交） |
| 提交 | 36 次（feat 6 / fix 4 / docs 18 / test 4 / chore 2 / build 1 / refactor 1） |
| 交付 | 主题包（Python 665 行 / 8 文件，模板 52 行 / 4 文件，CSS 329 行 / 3 文件）+ 文档 23 篇 1,498 行 |
| 验证 | `sphinx -W` 0 warning；`pytest` 46 passed（44 个测试函数）；sdist 离线重建成功；视口矩阵 7 页 × 10 宽度无横向溢出 |
| 事后修正 | 6 处：布局/交互 3、可达性 1、仓库卫生 2 |
| 结论 | 能力一次成型；缺陷集中在布局判定与可达性语义，两者都只能靠「看产物、用键盘」发现 |

**三条教训**：

1. 树里改得对不等于页面上看得对——构建零 warning 与页面排版正确是两件事。
2. 「没有横向溢出」是最容易骗过自己的验收项，它和「能不能用」无关。
3. 文档拆分与依赖接入的收益不在写的那一刻，而在下一个人（或下一次会话）能不能只读一页就够。

---

## 1. 时间线与事实清单（R）

### 1.1 阶段时间线（本地时间）

| 时段 | 动作 | 代表提交 |
|---|---|---|
| 15:15 | 切到 `pydata-sphinx-theme` 基座，建文档站，navbar 中和（P0） | `3a47316` `ec2be9e` |
| 15:19–15:20 | 数据驱动页眉工具箱（P2） | `1461d20` |
| 15:28 | 侧栏展开非当前章节的子树，修正为只标当前链 | `9185d18` |
| 15:49–15:50 | 脚注转边注 + `{margin}` 指令（P3） | `010117e` |
| 16:01 | 内容页脚 + Notebook 样式（P4） | `27be1d5` |
| 16:26 | 按钮/页脚下沉到 Python，模板压到 52 行 | `6fea8cb` |
| 16:26 | sdist 排除 `tests/chaos`，裸跑 pytest 只收主题测试 | `cde861f` |
| 16:30 | 窄屏边注展开由块级改行内，标点不再被挤走 | `383c490` |
| 16:38 | 分区首页加 `mystx-no-toc`，正文左对齐 | `78b61fd` |
| 16:44 | 侧栏默认只展开顶层（`book_nav_depth` 3 → 1） | `e8d6cbe` |
| 16:55–16:58 | 设计文档迁入文档站，目录 `development` → `dev` | `9377948` `c8b92fa` |
| 17:10 | 设计文档原子化为 9 页 | `235cdc2` |
| 17:25 | 站点接入 `myst-parser>=5.2`，加 4 项 Markdown 测试 | `1f9138d` |
| 17:36–17:41 | 视口矩阵实测，修边注键盘不可达 | `f54db57` |

### 1.2 事实清单

F-01 主题以单继承方式挂在 `pydata-sphinx-theme` 0.24.x 上，未引入 sphinx-book-theme 依赖。
F-02 `theme.toml` 清空 `navbar_start/center/end/persistent` 与 `article_header_start`。
F-03 侧栏模板为 `book-nav.html`，`sidebars = ["book-nav.html"]`。
F-04 自有选项 6 个：`book_nav_scope`、`book_nav_depth`、`book_header_buttons`、`book_use_sidenotes`、`book_content_width`、`book_footer_items`。
F-05 页眉按钮的 URL 规则集中在 `book/buttons.py`，模板只负责渲染。
F-06 页脚条目由 `book/footer.py` 的 `build_footer()` 生成，模板 7 行。
F-07 边注由 `FootnoteToSidenote`（post-transform，priority 1，仅 html）完成脚注改写。
F-08 `{margin}` 指令继承 `Sidebar`，产出 `aside.margin`。
F-09 模板总行数 52，分布在 4 个文件（layout 23 / book-header-buttons 13 / book-nav 9 / book-footer 7）。
F-10 Python 代码 665 行，8 个文件，预算 900 行。
F-11 测试文件 7 个，44 个测试函数，实跑 46 项用例。
F-12 文档 23 篇（含设计文档 9 个原子页），1,498 行。
F-13 设计文档正文拆为 index/axioms/assumptions/solution/delivery/records/corrections/patterns/risks。
F-14 站点 `extensions` 为 `["mystx", "myst_parser"]`，开启 `colon_fence` / `deflist` / `tasklist`。
F-15 `pyproject.toml` 的 `doc` 与 `dev` 额外依赖含 `myst-parser>=5.2`，`project.dependencies` 不含。
F-16 `sphinx -W -q` 构建退出码 0，warning 数 0。
F-17 视口矩阵覆盖 7 个页面 × 10 个宽度（360–1920），共 70 格。
F-18 70 格中 `scrollWidth - clientWidth` 全部为 0。
F-19 正文宽度在 1024–1280 px 视口下为 704 px；含边注页在 1440 px 及以上为 736 px（46rem），1280 px 时为 645 px（右侧页内目录仍占位）。
F-20 `mystx-has-margin` 在 1400 px 及以上隐藏右侧页内目录栏。
F-21 边注开关在窄屏（<1400 px）为 `input[type=checkbox]` + `label` 结构，无 JavaScript。
F-22 修复前该复选框样式为 `display: none`，`inp.focus()` 返回失败，Tab 顺序中不存在。
F-23 修复后复选框为 1 px `clip-path` 隐藏，`input` 排在 `label` 之前。
F-24 修复后实测 Tab 可停在编号上，Space 使边注 `display` 由 `none` 变为 `inline`。
F-25 `:focus-visible` 在 CDP 注入按键下不生效，焦点框存在性只能由 CSS 规则断言保证。
F-26 仓库存在 `v0.1.1`–`v0.3.8` 共 13 个旧 tag，`setuptools-scm` 推导版本为 `0.3.9.dev*`。
F-27 `v0.0.1` tag 截至复盘时未创建。
F-28 三个仓库的工作树在复盘时均为 clean（mystx `f54db57` / xuanspace `2c73514` / SpecWeave `7dc8cb93c`）。

---

## 2. 洞察（I）

### I-01 模板行数不是可维护性指标，数据与视图的边界才是

- **陈述**：模板从 74 行压到 52 行本身不产生收益；收益来自「同一规则只存在于一处」，所以之后新增页脚与接入 MyST 都没碰模板。
- **证据**：`6fea8cb` 把按钮 href/download/javascript 与页脚条目下沉到 `buttons.py` / `footer.py`；此后 P4 之后的两次能力变更（站点切 MyST、边注可达性修复）改动集中在 `py` 与 `css`，4 个模板文件行数未变（52 行）。
- **反常识**：多数人把「模板更短」当重构目标，实际该盯的是「同一个判断出现了几次」。行数减少只是副产品，判断收敛才是本体。
- **行动**：新增能力先问「规则归谁」，只有纯结构差异（多一层 wrapper、换标签）才写进模板；带条件的展示一律进 Python。

### I-02 书籍主题的缺陷几乎都发生在布局判定，而不是样式

- **陈述**：本里程碑 3 处布局/交互缺陷（分区首页空白、窄屏标点被挤走、侧栏越权展开）没有一处是配色、字号、间距问题，全部是「谁来决定这页长什么样」判错了。
- **证据**：空白源于 `display_toc` 为假时基座仍用 `justify-content: center`；标点源于展开态写成 `display: block`；侧栏源于 `show_nav_level` 被设成 3。三处修复都只改判定与一到两条 CSS，没有调任何视觉参数。
- **反常识**：看到「不好看」的第一反应是调 CSS 数值，但这类问题的正确入口是「页面级状态有没有被表达出来」。数值调得再准，判定错了照样错。
- **行动**：页面级差异一律由构建期计算成 `body` 类名（`mystx-has-margin` / `mystx-no-toc`），CSS 只消费类名，不在样式层做条件判断。

### I-03 「无脚本交互」把可达性债藏到了鼠标背后

- **陈述**：`label + checkbox` 的边注开关用鼠标测永远通过，70 格视口矩阵也全绿，但键盘用户一次 Tab 都到不了开关——布局不溢出与可用性无关。
- **证据**：修复前 `input.margin-toggle { display: none }`，`focus()` 失败、元素不在 Tab 序、也不在无障碍树里；修复后同一元素在无障碍树中显示为 checkbox（名为「1」「2」「⊕」），Tab 可达、Space 可展开。
- **反常识**：把「响应式」等同于「多宽度截图正常」是这类主题最常见的验收幻觉；真正的门槛是输入方式，而不是视口宽度。
- **行动**：验收清单增加一项固定检查——每个交互控件必须「Tab 能到达、焦点可见、键盘能等价触发」，不足三条即视为未完成。

---

## 3. 对抗审查（V）

| 攻击 | 回应 | 结论 |
|---|---|---|
| I-01 只是把逻辑从 Jinja 挪进 Python，总量没少 | 模板里仍保留 `{% set prefixes = {...} %}` 这类常量映射，但没有任何条件分支；带分支的部分（按钮 URL、页脚条目、边注变换）都在 py 且有单测 | 洞察保留，边界收紧为：模板允许常量映射，不允许条件分支 |
| I-02 用 body 类名会让 CSS 与 Python 隐式耦合，类名变成魔法字符串 | 类名集中在 `options.py` 常量，`test_layout.py` 覆盖 4 种组合；泄漏面只有 2 个类名 | 洞察保留，代价已量化 |
| I-03 验收加键盘项会拖慢每次发版 | 单次检查约 30 秒；本轮正是这条检查抓到了真缺陷，且该缺陷用户侧不可绕过 | 洞察保留，动作升级为硬门 |
| 原结论「PST 的 `sidebars` 配置是布局问题根源」 | 实测空白来自 `justify-content`，与 `sidebars` 无关；已从文档删除该说法 | **删除**，属于错误归因 |

---

## 4. 模式萃取（E）

### P-01 结构判定上移（Structure-Decides-Upstream）

- **触发场景**：主题/模板类项目出现「只在某些页面错位」的问题（首页空白、无目录页偏移、含特殊块的页宽异常）。
- **步骤**：1）在构建期判断页面特征（有无目录、有无边注、有无侧栏）；2）写成一个 `body` 类名；3）CSS 只按类名分支，不在样式里猜结构；4）为每种组合写一条断言测试。
- **反模式**：用 `:has()` 或 DOM 结构选择器在 CSS 里反推页面类型；在模板里写 `{% if %}` 决定布局类。
- **迁移验证**：已在三个独立症状上复用（空白 / 标点 / 键盘），每次都是「先加类名或判定，再改样式」。

### P-02 无脚本交互的可达性三件套（Tab / Focus / Key）

- **触发场景**：用 `label + input[type=checkbox]` 或 `details/summary` 做零 JS 交互（折叠、展开、切换）。
- **步骤**：1）控件不得 `display: none`，改用 1 px `clip-path` 隐藏；2）控件在 DOM 中排在可见标签之前，使 `input:focus-visible + label` 可画焦点；3）为不支持 `:focus-visible` 的引擎补 `:focus` 兜底；4）实测 Tab 到达 + Space 触发。
- **反模式**：把「鼠标能点」当作交互完成；用 `display: none` 隐藏原生控件；把焦点样式只写在可见元素上却无法被聚焦。
- **迁移验证**：同一模式适用于任何 checkbox hack；本项目已用于边注，未来 `details` 折叠目录可直接套用「焦点必须在可见元素上」这一条。

---

## 5. 原子行动项（A）

| 编号 | 行动 | 状态 | 判定标准 |
|---|---|---|---|
| A-01 | 把「Tab 可达 / 焦点可见 / 键盘等价触发」写进验收 §6 清单 | 待执行 | 清单出现第 9 条，且下一次交互变更引用它 |
| A-02 | 读屏实测一次（NVDA 或 VoiceOver），记录边注与侧栏的朗读顺序 | 待执行 | 产出一段朗读记录 + 至少一条修正或明确「无需修正」 |
| A-03 | `v0.0.1` tag 的时机拍板 | 待人工 | tag 创建后版本号变为 `0.0.1`，一次 `python -m build` 通过 |
| A-04 | 视口矩阵脚本落到仓库（替代临时 iframe 页） | 待评估 | 脚本可重复运行并输出同样 70 格表；否则明确不做 |
| A-05 | design 文档 4.1–4.17 与原子页的映射表补进 `records.rst` | 待执行 | 读者能从编号直接跳到页面 |

---

## 6. 质量门自检

| 门 | 要求 | 结果 |
|---|---|---|
| G1 | 事实清单 ≥ 20 条且无因果词 | 28 条（F-01–F-28），逐条为客观陈述 |
| G2 | 每条洞察含陈述/证据/反常识/行动 | 3 条均四元组完整 |
| G3 | 模式可迁移（有触发场景与反模式） | 2 个模式，均给出迁移验证点 |
| G4 | 行动项原子（单一职责、可判定） | 5 项，各有判定标准；A-03 明确标为待人工 |
| G5 | 交付物自检（断链/结构/编码） | 本报告 Markdown 单文件，无跨文件链接；索引同步更新 |

---

## 7. 附录：指标与口径

| 指标 | 数值 | 口径 |
|---|---|---|
| 提交数 | 36 | `git log 3a47316^..HEAD`（主题重建起点之后） |
| Python | 665 行 / 8 文件 | `src/**/*.py`，不含 `__pycache__` |
| 模板 | 52 行 / 4 文件 | `theme/mystx/*.html` |
| CSS | 329 行 / 3 文件 | `theme/mystx/static/css/*.css` |
| 测试 | 44 函数 / 46 用例 | `tests/test_*.py`，`pytest -q` 实跑 46 passed |
| 文档 | 23 篇 / 1,498 行 | `doc/**/*.rst`、`doc/**/*.md`，排除 `_build` |
| 选项 | 6 个 `book_*` | `theme.toml` |
| 构建 | 0 warning | `sphinx -W -q -b html doc doc/_build/html` |
| 视口矩阵 | 70 格 / 0 溢出 | 7 页 × 10 宽度（360–1920） |
| 版本 | `0.3.9.dev*` | `setuptools-scm` 从旧 tag 推导；`v0.0.1` 未创建 |
