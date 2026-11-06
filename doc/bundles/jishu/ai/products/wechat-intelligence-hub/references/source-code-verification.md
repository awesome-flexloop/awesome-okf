---
type: Reference
title: "WeChat Intelligence Hub 源码级核验报告与首轮对账"
description: "基于固定 commit fb6a42c 的源码核验：G0 信源稳定性、首轮 8 项 ⚠️ 的逐项对抗性对账、漂移分类与定向修复清单、计数断言双口径复核"
tags: [wechat-intelligence-hub, source-code, verification, adversarial, drift, fact-check]
generated: { by: "source-code-to-okf-wiki:R/V", at: "2026-11-06T16:52:00+08:00" }
verified:
  by: process:seven-concepts-v
  at: "2026-11-06T16:52:00+08:00"
status: stable
stale_after: 2027-03-06
sources:
  - id: source-repo
    resource: https://github.com/Rion-Wu-tech/wechat-intelligence-hub
    title: "WeChat Intelligence Hub 源码仓库"
  - id: local-readme
    resource: https://github.com/Rion-Wu-tech/wechat-intelligence-hub/blob/fb6a42c34160d2ffa66ed5f114f8d8cdabe7f5f9/README.md
    title: "固定 commit 下的 README.md"
  - id: first-round-verification
    resource: verification.md
    title: "首轮 P0 权威核验报告（本报告的对账对象）"
---

# 源码级核验报告与首轮对账

> 本报告是首轮 [verification.md](verification.md) 的**源码级续核**。首轮基于微信博文 + GitHub REST API + 官方 README（`main` 分支网页快照），**未 clone 仓库、未读源码**；本轮基于固定 commit 的**本地源码**做对抗性对账。
> **方法论**：五步链路「源头复基线 → 对抗性对账 → 漂移分类 → 定向修复 → 落盘核对」，**只修改确认漂移的文档，绝不因重新生成而破坏已准确的内容**（见 `source-code-to-okf-adversarial-update` 模式文档）。

## 0. G0 信源稳定性预检

| 检查项 | 结果 |
|--------|------|
| 信源类型 | 本地只读源码副本（`external/dao/wechat/wechat-intelligence-hub`），含 `.git`，可追溯 remote |
| remote URL | `git@github.com:Rion-Wu-tech/wechat-intelligence-hub.git`（F-058） |
| 固定点 | **commit `fb6a42c34160d2ffa66ed5f114f8d8cdabe7f5f9`**（F-059） |
| 工作区状态 | `git status` 为空，与 commit 完全一致（F-064） |
| 禁止项复核 | 固定对象为**不可变 commit hash**，非 `main`/`master` 分支引用 ✅ |
| `check-source-path-stability.py` | ✅ rc=0：`scanned_files=12`、`blocking_count=0`、`env_bound_count=0`、`anchor_out_of_bounds_count=0` |

### ⚠️ G0 关键发现：HEAD 领先唯一 tag 13 个提交

| 项 | 值 |
|----|-----|
| 唯一 tag | `v0.9.2-preview.2` → commit `6b73940a2286b20e51badbba7e0d4be633d24f61`（2026-09-04 22:55:07 +0800） |
| HEAD | `fb6a42c…`（2026-10-17 03:53:01 +0800） |
| 差距 | **13 个提交**，64 个文件变更，+5569 / −202 行 |
| 新增关键文件 | `docs/USAGE.md`（317 行）、`SECURITY.md`、`rion_wechat_access.py`（954 行）、`report_security.py`（96 行）、`providers/wxkey/` |

**处置**：README 声明的「当前首发版本 `v0.9.2-preview.2`」是**发布口径的版本号**，而工作副本 HEAD 是该发布之后 13 个提交的**开发态**。二者不是同一快照。

- 本束所有源码级事实一律以 **commit `fb6a42c`** 为准，并在正文显式标注；
- 首轮「当前版本 `v0.9.2-preview.2`」（F-045）**不判错误**，但需补注「该 tag 落后本束源码基线 13 个提交」；
- 首轮核验的 README 是 `main` 分支网页快照，与本地 README 存在时间差——这正是首轮 5 项 UI ⚠️ 判为「官方未逐字核验」的**部分原因**（网页视图不完整），而非官方文档真的缺失。

## 1. 对抗性对账：首轮 8 项 ⚠️ 逐项复核

| # | 首轮 ⚠️ 项 | 首轮依据 | 源码/官方文档证据 | 判定 |
|---|-----------|---------|------------------|------|
| #5 | 星标 1,976→2,764 时点差 | GitHub API 时点快照 | 源码**不含** star 时序数据；2026-11-06 API 复测仍为 **2,764**（forks 2,753、open_issues 10、`pushed_at` 2026-10-16 未变） | ⚠️ **维持**（时效差异，非造假） |
| #6 | 「5 天」增长窗口 | 仅博文单源 | 源码无 star 时序；`created_at` 2026-09-04 与发文 2026-09-24 仍相隔约 20 天 | ⚠️ **维持**（禁止表述为「创建后 5 天」） |
| #9 | 「不重签名」适用范围 | README 语义 | `SECURITY.md` **逐字**：「The separate experimental `rion-wechat-access` helper is **not** read-only: … may restart WeChat, debug its process and re-sign a shadow copy」，同时「The Reader and Intelligence Hub are read-only … do not send messages or automate replies」 | ✅ **坐实**（范围划分完全正确，且更精确） |
| #16 | 四个入口 UI 名称 | 仅博文图注 | `report_bundle_flagship.py` `PAGE_SPECS` 常量逐字给出 `综合行动` / `群聊日报` / `重点联系人` / `信号雷达`（title 为「商单信号雷达」）；同文件内嵌字符串另写「只保留综合行动、群聊日报、重点联系人和商单信号雷达四个入口」；`docs/USAGE.md` 亦逐字列出 | ✅ **坐实**（代码 + 文档双源） |
| #17 | 定向检索五维度 | 仅博文图注 | `docs/USAGE.md` 第 4 章逐字列出：某条信息 / 某个人 / 某个产品或事物 / 某个微信标签 / 某个项目或事件 | ✅ **坐实**（官方文档逐字） |
| #18 | 四种视图风格 / 明暗主题 | 仅博文图注 | **明暗主题**：实现级证据完整（`#theme-button` → `dataset.theme` → `localStorage['wechat-flagship-theme']` → `html[data-theme="dark"]` CSS 变量），✅ **坐实**。<br>**四种视图风格**：实为 `report-redesign-research-2026-08-28.md` 的「四套**待选**视觉风格」，原文结论「采用 A 作为主框架」；`style-previews/` 10 个文件无任何运行时代码引用 → **非运行时可切换主题** | ⚠️ **拆分为二**：明暗主题坐实；「四视图风格」**修正为设计期候选** |
| #19 | 移动端视图 | 仅博文图注 | `.mobile-routes` 导航元素、`mobile_nav_html` 按 route 生成、`@media` 断点下 sticky 横向滚动条、移动端截图 `flagship-today-mobile.png` | ✅ **坐实**（实现级） |
| #20 | 重点联系人 + 回复草稿 | 仅博文图注 | `PAGE_SPECS` 含 `contacts` 路由「重点联系人」；`intelligence_views.py` `_reply_draft` 为 6 类确定性模板；`USAGE.md`「系统只生成本地草稿，不会发送微信」；`SKILL.md`「回复内容只能作为本地草稿」 | ✅ **坐实**（代码 + 文档双源），并**补充**「模板非模型自由生成」 |

### 对账小结

- **8 项 ⚠️ 中 6 项被源码/官方文档坐实**（#9、#16、#17、#19、#20，及 #18 的明暗主题部分）；
- **1 项拆分为二**（#18：明暗主题 ✅ / 四视图风格 ⚠️ 修正为设计候选）；
- **2 项维持**（#5、#6：动态时点数字，源码无法提供 star 时序）。

**首轮结论的可信度评估**：首轮把 5 项 UI 声明判为「图注单源」是**审慎且正确的保守判定**——当时未 clone 源码，官方 README 网页视图确实未逐字给出全部名称。本轮未发现首轮存在**任何造假式断言**或**事实性错误**；仅 #18 的「四种视图风格」在语义上需要从「运行时能力」修正为「设计期候选方案」。

## 2. 漂移分类与定向修复清单

| 类别 | 定义 | 本轮条目 | 处置 |
|------|------|---------|------|
| **D1 文档漂移** | 首轮文档结论被源码证伪或需限定范围 | #18「四种视图风格」 | **定向修订** `concepts/02` 与根 `index.md` 的相关表述，保留其余已验证结论 |
| **D2 范围缺口** | 首轮结论正确但缺源码级限定 | #9（补 `SECURITY.md` 逐字边界）、版本口径（补 tag 落后 13 提交） | **追加限定**，不改写主结论 |
| **D3 计数口径** | 计数陈述需区分口径 | 工具数 29 vs 30；CLI 36 / 37 / 73；`SOURCE_RULES` 11 vs 8 | **补口径说明**，统一以脚本计数为准 |
| **D4 新增事实** | 源码独有的首轮未覆盖事实 | 只读的结构性保证、报告安全净化模型、回复草稿模板机制、风格预览为非运行时资产 | **新增概念文档**承载 |
| **D5 维持** | 无法用源码推进的动态数字 | #5 星标、#6 「5 天」 | **维持 ⚠️**，不因换信源而升级为 ✅ |

## 3. 计数断言双口径复核

> 规范要求：凡「X 个 / Y 份 / Z 处」类数量陈述，R 阶段须脚本计数，V 阶段须用**独立于 R 的手段**复核。

| 断言 | R 阶段手段 | V 阶段独立手段 | 结果 |
|------|-----------|----------------|------|
| `TOOL_SPECS` 工具数 = 30 | `ast` 解析 `AnnAssign` → `Dict` 键数 | `awk` 提取块 + `grep -cE '^\s{4}"[a-z0-9-]+": \{'` | ✅ 30 = 30 |
| 输入字段数 = 266 | `ast` 求各 `properties` 列表长度之和 | 正则 `"properties": \[([^\]]*)\]` 内引号串计数 | ✅ 266 = 266 |
| 不同属性名 = 87 | `ast` 收集去重 | — | ✅ 87 |
| Reader CLI 子命令 = 36 | `ast` 收集 `add_parser` 首参 | — | ✅ 36 |
| 情报产品 CLI 子命令 = 37 | `ast` 收集 `add_parser` 首参 | — | ✅ 37 |
| 旗舰 `PAGE_SPECS` = 4 | `ast` 元组长度 | 源码 `grep` 逐行核对 4 条 route | ✅ 4 = 4 |
| 旗舰 `SOURCE_RULES` = 11 | `ast` 元组长度 | `grep -c '(".*", "'` 块内计数 | ✅ 11 |
| HTML `SOURCE_RULES` = 8 | `ast` 元组长度 | 同上 | ✅ 8 |
| `style-previews/` 文件数 = 10 | 目录列举 | 跨仓库引用检索（0 处运行时引用） | ✅ 10 |
| `intelligence_views.py` 顶层函数 = 26 | `ast` 顶层函数计数 | — | ✅ 26 |
| `report_security.py` 函数 = 4 / 96 行 | `ast` + 行数 | — | ✅ 4 / 96 |
| `rion_wechat_access.py` = 954 行 / 24 函数 / 1 类 | `ast` | — | ✅ |
| 跟踪文件 = 126；`.py` 38（18 非测试 + 20 测试）；`.md` 43 | `git ls-tree -r HEAD` | — | ✅ HEAD 口径 |

**与首轮 README 口径的差异**：README（两处）称「29 项只读工具、266 个输入字段」。源码 `TOOL_SPECS` 实际为 **30** 项工具、**266** 个字段。

- **字段数一致**（266 = 266）；
- **工具数差 1 项**。最可能的口径解释：README 描述的是**与旧版 `wechat-cli 1.6.19` 对齐**的公开接口子集，源码在此基础上**新增了 1 个工具**（tag 之后 13 个提交内新增/改名，参见 `git diff v0.9.2-preview.2..HEAD`）。**本束不臆断具体是哪一项**，只登记「源码口径 30、README 口径 29，差 1 项，指向对外对齐子集 vs 源码全集的口径差」。

## 4. 源码级新增事实摘要（首轮未覆盖）

1. **只读是结构性保证**：30 个工具的 `read_only: True` 由列表推导式统一置位，无逐项开关；Reader 源码无任何写入型函数；数据库快照以 `mode=ro` 打开。首轮只能在文档层断言只读，本轮升级为代码层结论。
2. **报告安全是「失败关闭」模型**：Pandoc 禁原始 HTML + nh3 显式白名单 + 哈希 CSP + 禁外部图片与自动网络请求；`nh3` 缺失时 HTML 生成**报错而非降级**，不产出未净化页面。
3. **回复草稿是确定性模板而非模型自由生成**：6 类 intent（结算/反馈/报价/需求/进度/通用）× 关系远近双措辞。
4. **风格预览是非运行时资产**：`style-previews/` 10 个文件无运行时引用，四套风格 A~D 出自设计研究文档且结论为「采用 A 作为主框架」。
5. **四个顶层入口 ≠ 四种视图风格**：`PAGE_SPECS` 4 条是**四个顶层路由入口**；群聊页内另有 3 个视图（话题 / 重点群聊 / 群聊筛选）。这是首轮「四种视图风格」表述产生歧义的根因。

## 5. 本轮局限

- **未实机执行**：未运行 `install.sh` / `run_demo.sh` / `profile-init`，未在真实微信数据上验证；所有结论基于**静态源码阅读 + AST 解析**。
- **未取得 tag 对应快照**：本轮只分析 HEAD；tag `v0.9.2-preview.2` 的源码未单独展开，因此「工具数 29→30」的**具体差异项未定位**。
- **测试未执行**：20 个测试文件（5,582 行）仅统计规模，未运行 pytest，故「测试通过」类陈述不在本束范围。
- **star 时序缺口未补**：GitHub stargazers 时序接口本轮仍未取，#6「5 天」维持 ⚠️。
- **HTML 渲染产物未实看**：渲染结果通过源码与截图文件名推断，未在浏览器中实际打开渲染页面。

## 6. 复核安排

`stale_after: 2027-03-06` 前复核：tag 与 HEAD 的差距是否收敛、工具数 29/30 口径是否澄清、`USAGE.md` 与 README 的能力表述是否再变、`report_security.py` 白名单是否调整、AGPL 商业授权条款是否更新。
