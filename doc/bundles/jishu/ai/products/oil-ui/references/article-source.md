---
okf_version: "0.2"
type: reference
title: "事实清单"
description: "oil-ui 博文事实登记 F-001~F-030，含来源、类型与核验状态"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
  - id: github-repo
    resource: https://github.com/oil-oil/oil-ui
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
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

> **状态说明**：`✅` 官方核验一致；`⚠️` 时效快照或口径差异（详见 [verification.md](verification.md)）；无 `❌` 硬错误。

## 核验状态汇总

- 博文 F-001~F-020，官方核验补充 F-021~F-030。
- **9✅ / 2⚠️ / 0❌**（11 项 P0/P1 关键声明）。
- 两条勘误：作品数 52→65（F-012→F-026 时效）、模型名是画廊标签非能力背书（F-014→F-027 口径）。

---
**核验结论**：[verification.md](verification.md)。