---
okf_version: "0.2"
type: reference
title: "事实清单"
description: "oil-ui 事实登记 F-001~F-041，含来源、类型与核验状态（F-001~F-030 博文初始，F-031~F-041 官方一手增量）"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
  - id: github-repo
    resource: https://github.com/oil-oil/oil-ui
  - id: skillmd
    resource: https://github.com/oil-oil/oil-ui/blob/main/SKILL.md
  - id: gallery
    resource: https://ui.oiloil.org
  - id: pro
    resource: https://ui.oiloil.org/pro
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
extended:
  by: seven-concepts-cmd
  at: "2026-10-13T00:00:00+08:00"
status: stable
stale_after: 2027-03-31
---

# 事实清单

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-001 | oil-ui 是给 AI 编程 Agent 装的 Skill，非独立工具 | page_fact | blog | 博文开头定位 | ✅ |
| F-002 | 作者此前做过 beautify-github-readme 与 oiloil-ui-ux-guide | author_claim | blog | 作者介绍 | ✅ |
| F-003 | oil-ui 给 AI 一套可执行的八步设计方法论 | author_claim | blog | 方法描述 | ✅ |
| F-004 | 输出为多个可对比的设计方向，非单一答案 | author_claim | blog | 使用流程 | ✅ |
| F-005 | 痛点一：AI 缺乏设计判断标准 | author_claim | blog | 痛点归纳 | ✅ |
| F-006 | 痛点二：默认"Inter + Tailwind 默认色板 + 8px 圆角 + 淡阴影"的懒方案 | author_claim | blog | 痛点归纳 | ✅ |
| F-007 | 痛点三：不会拉开多个方向 | author_claim | blog | 痛点归纳 | ✅ |
| F-008 | 五种调性刻度：能量/完成度/密度/分量/严肃度 | page_fact | blog | 方法第 2 步 | ✅ |
| F-009 | 支持老项目改造："先分清再体检" | author_claim | blog | 老项目段落 | ✅ |
| F-010 | 开源时间 2026-09-30、MIT 许可 | page_fact | blog | 项目信息 | ✅ |
| F-011 | 仓库油 oil-oil/oil-ui、作者 Zhihuang Lin | page_fact | blog | 项目信息 | ✅ |
| F-012 | 博文称画廊"目前展示 52 个作品" | page_fact | blog | 画廊描述 | ⚠️（核验增至 65） |
| F-013 | 停留作品与模型标签按生成模型分组 | page_fact | blog | 画廊描述 | ✅ |
| F-014 | 列模型名"GPT 6.1 Sol / GPT 6 Luna / Claude Opus 5.5 / Claude Sonnet 5.5" | page_fact | blog | 模型标签举例 | ⚠️（标签非背书） |
| F-015 | 主张 oil-ui 不绑定单一模型，跨模型适用 | author_claim | blog | 能力说明 | ✅ |
| F-016 | 支持树 Claude Code / Cursor / Codex 等 Agent | author_claim | blog | 兼容说明 | ✅ |
| F-017 | 老项目改造提倡只推进一处 | author_claim | blog | 改造成法 | ✅ |
| F-018 | 自带风格对比页（ProfileComparer） | page_fact | blog | 方法第 7 步 | ✅ |
| F-019 | 安装命令 `npx skills add oil-oil/oil-ui`，需 Node.js 18+ | page_fact | blog | 安装段落 | ✅ |
| F-020 | 版本检查：10 分钟/超时 2 秒跳过/不上传/无 Python 只提醒一次 | page_fact | blog | 版本检查段落 | ✅ |
| F-021 | 官方仓库存在，作者既有项目可查 | page_fact | github-repo | https://github.com/oil-oil | ✅ |
| F-022 | 仓库 v0.14.0 / 203 Stars / 21 commits / Python 53.3% + HTML 45.6% | page_fact | github-repo | 仓库统计（2026-10-10 时点） | ✅ |
| F-023 | 开源版与 Pro 功能分界（免费含八步/对比页/层级/截图/基础体检；Pro 加交互/布局/打磨/特效/三立场） | page_fact | pro | README 对照表 | ✅ |
| F-024 | Pro 定价 69 元买断、永久更新 | page_fact | pro | Pro 售卖页 | ✅ |
| F-025 | 安装命令与画廊首页命令逐字一致 | page_fact | gallery | ui.oiloil.org 首页 | ✅ |
| F-026 | 画廊当前"全部 65"作品（2026-10-10 核验时点） | page_fact | gallery | 画廊实时 | ⚠️（覆盖 F-012 时效） |
| F-027 | 画廊存在 6 种模型分组标签 | page_fact | gallery | 画廊标签 | ✅ |
| F-028 | "老项目"行与 Pro 能力分界在官方对照表可查 | page_fact | pro | README 对照表 | ✅ |
| F-029 | 相邻工具 draw-ui、oil-motion存在 | page_fact | github-repo | 官方推荐 | ✅ |
| F-030 | 八步法与五刻度以 README 为唯一权威口径 | page_fact | github-repo | README §方法 | ✅ |
| F-031 | SKILL.md 定义五步工作流：探索并收敛方向 → 建立视觉与交互结构 → 制作并取得实际证据 → 独立评审与修正 → 验证与交付 | page_fact | skillmd | SKILL.md §1-5 | ✅ |
| F-032 | 范围分流：按"小改动/新界面/单组件打磨/存量项目/截图还原/UI评审"决定是否需要完整走步骤1-5 | page_fact | skillmd | SKILL.md §选择范围 | ✅ |
| F-033 | 原则"只在缺失信息会改变核心方向时才提问"，不把设计探索变成强制问卷或逐步审批 | page_fact | skillmd | SKILL.md §选择范围 | ✅ |
| F-034 | 自动更新：使用触发版本检查，最多每10分钟联网一次，有新版本即尝试自动更新（需 Python 3 + Node 18+） | page_fact | github-repo | README §安装 | ✅ |
| F-035 | 环境变量 `OIL_NO_AUTO_UPDATE=1` 只提醒不自动更新；`OIL_NO_UPDATE_CHECK=1` 完全关闭检查 | page_fact | github-repo | README §安装 | ✅ |
| F-036 | 恢复提示命令：`npx github:oil-oil/oil-cli update oil-ui --path "<安装路径>"`；离线时不提示新版本 | page_fact | github-repo | README §安装 | ✅ |
| F-037 | SKILL.md 核心为宿主中立的文本流程，不依赖其他 Skill 或指定模型；对比页生成器需 Python 3.10+ 标准库 | page_fact | skillmd | SKILL.md metadata | ✅ |
| F-038 | references 参考文件体系：design-direction / visual-language / media / imagery / motion / style-explorer / layout-and-viewport / visual-review | page_fact | skillmd | SKILL.md §各步引用 | ✅ |
| F-039 | 独立评审机制：方向探索阶段对比页先交用户、评审为推荐流程；每阶段一轮；Pro 以 9 分为目标最多评审三轮 | page_fact | github-repo | README 对照表 | ✅ |
| F-040 | 评审以"这一体裁里顶尖设计团队会怎么做"为参照、按 10 分制给出差距；评审者不看作史/代码/旧评分 | page_fact | skillmd | SKILL.md §4 独立评审 | ✅ |
| F-041 | 能力边界：无看图能力时明确"未验证实际视觉"、不生成虚假视觉评分；不管理密钥、不安装工具、不发布网站 | page_fact | skillmd | SKILL.md §能力边界 | ✅ |

> **状态说明**：`✅` 官方核验一致；`⚠️` 时效快照或口径差异（详见 [verification.md](verification.md)）；无 `❌` 硬错误。F-031~F-041 为 2026-10-13 官方一手增量（SKILL.md / README.md 直接核验）。

## 核验状态汇总

- 博文 F-001~F-020，官方核验补充 F-021~F-030，官方一手增量 F-031~F-041。
- **9✅ / 2⚠️ / 0❌**（11 项博文 P0/P1 关键声明）。
- 两条勘误：作品数 52→65（F-012→F-026 时效）、模型名是画廊标签非能力背书（F-014→F-027 口径）。
- F-031~F-041 全部为官方一手文件（SKILL.md / README.md）直接摘取，无时效类待复核项。

---
**核验结论**：[verification.md](verification.md)。