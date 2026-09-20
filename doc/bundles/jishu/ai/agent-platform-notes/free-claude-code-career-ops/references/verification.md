---
type: Reference
title: "P0 声明核验与勘误"
description: "对文章中的数字、许可证、核心能力和免费承诺进行官方源对照，明确可证实项与边界。"
tags: [核验, P0, 勘误, 开源项目, 时效]
generated: { by: "process:seven-concepts-r", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-31
sources:
  - { id: blog, resource: "https://mp.weixin.qq.com/s/yEmCTdlwaKyj_h9eQRBsJg" }
  - { id: fcc, resource: "https://github.com/Alishahryar1/free-claude-code" }
  - { id: career, resource: "https://github.com/santifer/career-ops" }
---

# P0 声明核验与勘误

> **状态：flagged。** 核心“每月 13 亿 token、全程免费”的组合承诺依赖多个 provider 的免费层，不是稳定的产品保证；免费额度和限制会变化。[F-005][F-013][F-028]

## 核验表

| 声明 | 结论 | 处理 |
|---|---|---|
| free-claude-code 每月 13 亿以上免费 token、50 个 provider | ✅ 官方 README 有同口径表述 | 正文标为项目自述和时效性额度，不写成永久保证。[F-005] |
| RTK 最多减少 90% 终端输出 token | ⚠️ 官方 README 有表述，但未见独立同条件实验 | 标为工具自述，不能外推为总成本或总工作效率。[F-009] |
| career-ops 评估 740+ 职位、获得 Head of Applied AI offer | ⚠️ 作者 README/案例自述 | 标为作者案例，不作普遍成功率证据。[F-023] |
| career-ops MIT | ✅ GitHub README/仓库信息可核对 | 保留。[F-024] |
| 两个项目均为 MIT | ⚠️ 文章合并表述；本轮只直接核对 career-ops | free-claude-code 的许可证应以仓库当前 LICENSE 为准，不把文章合并口径当作已核验事实。[F-025] |
| free-claude-code 属于 Anthropic 或提供 Claude 模型 | ❌ 与官方 README 的独立项目声明冲突 | 正文明确区分“Claude Code 工具链/接口”与“后端模型”。[F-012] |
| 组合后全程不花一分钱 | ❌ 不能作为稳定承诺 | 改写为“可能降低订阅门槛”，并保留 API、provider 限制、模型质量和网络成本边界。[F-028] |
| 两个项目的星标数量 | ⚠️ 文章图片是时间快照 | 不在概念正文重复具体星数，仅保留为原文事实。[F-003][F-004] |

## 四类勘误清单

- **日期/版本**：文章没有固定版本号；本 bundle 的 `stale_after` 为 2026-11-30，复核前应重新读取两个仓库。
- **成效数字**：13 亿 token、90% 节省和 740+ 职位均不是独立实验或普遍保证。
- **口径对照**：免费额度是各 provider 免费层的合计口径，不等于单一 provider 向每个用户发放 13 亿 token。
- **引文逐字**：文章“一个省钱、一个赚钱”“一把梯子”属于作者观点，不作为项目官方定位。[F-026][F-027]

## 核验范围

本轮完成文章正文、两个项目公开 README 和仓库元信息的静态对照；未安装项目、未调用 API、未验证实时额度或职位抓取结果。
