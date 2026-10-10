---
okf_version: "0.2"
type: reference
title: "核验报告"
description: "oil-ui 博文 P0 核验结论、勘误说明与信源距离评估"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
  - id: github-repo
    resource: https://github.com/oil-oil/oil-ui
  - id: gallery
    resource: https://ui.oiloil.org
  - id: pro
    resource: https://ui.oiloil.org/pro
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
status: stable
stale_after: 2027-03-31
---

# 核验报告

## 核验说明

- **时机**：2026-10-10，对 2026-10-06 发布的「开源星探」博文进行官方核验。
- **方法**：博文 11 项 P0/P1 关键声明，逐一对照 GitHub 官方仓库、官方画廊、Pro 售卖页。
- **结论**：**9✅ / 2⚠️ / 0❌**——无硬错误；两处为时效快照与口径差异，不影响核心结论。

## P0 逐项结论

| # | 博文声明 | 官方证据 | 结论 |
|---|---------|---------|------|
| P0-1 | 仓库 `oil-oil/oil-ui` 存在（MIT、2026-09 开源） | GitHub 仓库实时页（21 commits / v0.14.0 / MIT） | ✅ |
| P0-2 | 作者此前做过 oiloil-ui-ux-guide（CRAP 等） | skill-repo.io / GitHub raw SKILL.md | ✅ 项目存在 |
| P0-3 | 八步设计法 | README §方法 1-8 逐字一致 | ✅ |
| P0-4 | 五种调性刻度 | README 第 2 步一致 | ✅ |
| P0-5 | 安装命令 `npx skills add oil-oil/oil-ui` | README §安装 + 画廊首页命令 | ✅ |
| P0-6 | 风格对比页交互 | README §自带的风格对比页一致 | ✅ |
| P0-7 | 版本检查机制（10 分钟/超时跳过/不传内容/无 Python 只提醒一次） | README §版本检查一致 | ✅ |
| P0-8 | Oil UI Pro 存在（69 元买断） | Pro 售卖页 + README 对照表 | ✅ |
| P0-9 | 老项目改造能力 | README §开源版和完整版对照表"老项目"行 | ✅ |
| P0-10 | 画廊"52 个作品" | 画廊实时"全部 65" | ⚠️ 时效快照（F-012 → F-026） |
| P0-11 | 模型名"GPT 6.1 Sol / GPT 6 Luna / Claude Opus 5.5 / Claude Sonnet 5.5" | 画廊 6 种模型标签真实存在 | ⚠️ 口径（标签非背书，F-014 → F-027） |

## 勘误说明

### ⚠️ 勘误 1：作品数 52 → 65（时效快照）

博文称画廊"目前展示了 52 个作品"（F-012，快照时点 2026-10-06）。官方画廊当前显示"全部 65"（F-026，核验时点 2026-10-10）。**处理**：正文与 index.md 均采用官方现行 65 并标注时点；动态数字一律以可访问官方页面为准。

### ⚠️ 勘误 2：模型名是画廊标签，非能力背书

博文把 "GPT 6.1 Sol / GPT 6 Luna / Claude Opus 5.5 / Claude Sonnet 5.5" 作为"不同模型生成的"论据（F-014），用于支撑"oil-ui 不绑定单一模型"（F-015）。核验确认这些是**画廊真实存在的分组标签**（F-027），但**不能据此推断模型能力或评测排名**。**处理**：在本包中仅作"标签存在性"采信，不上升为对模型的评价；方法论主张（跨模型适用）本身与官方定位一致。

### 无 ❌ 硬错误、无重大遗漏

未发现如域名错误、命令错误、虚构功能、张冠李戴等硬错误。博文与官方口径高度一致，可见作者对项目理解较深。

## 信源距离评估

| 层级 | 信源 | 用途 |
|------|------|------|
| L0（一手·最高） | GitHub 官方仓库 `oil-oil/oil-ui` | 八步法、五刻度、安装、版本检查、免费/Pro 对照表的唯一权威口径 |
| L0（一手） | 官方画廊 `ui.oiloil.org` | 作品数与模型标签 |
| L0（一手） | Pro 售卖页 `ui.oiloil.org/pro` | Pro 定价与能力 |
| L2（二手·新闻） | 公众号「开源星探」博文 | 触发与转述（叙事、痛点归纳） |

- 方法论与操作陈述已**全部升级到官方一手口径**（F-030 强调 README 为唯一权威）。
- 叙事性表达（"极大提升""绝了"等标题党、痛点归纳）保留为作者观点，不作事实采证。

## 数据时效建议

- **动态数字**（Star 203、Fork 6、作品 65）为 2026-10-10 快照，引用时须带时点。
- **功能分界**（免费/Pro）以 README 对照表为准，Pro 为闭源付费产品，购买前以官方当期条款为准。
- `stale_after: 2027-03-31`——八步法等方法论骨架跨周期有效，数字与版本号到期前复核。

---
**对应事实登记**：[article-source.md](article-source.md)。