---
type: Reference
title: "Hypit 关键声明 P0 核验报告"
description: "对安装、定位、示例成本、并发与时效性声明进行官方源核验。"
tags: ["Hypit", "P0核验", "勘误", "视频工作流"]
generated: { by: "reference_agent", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/N5jRPXG_fSs668l5mSUdvQ?from=industrynews&color_scheme=light#rd
  - id: repo
    resource: https://github.com/hypit-ai/hypit
  - id: readme
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/README.md
  - id: skill
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/skills/hypit/SKILL.md
---

# 核验结论

## 信源距离

文章属于第三方开源项目介绍；关键技术声明以 Hypit 官方仓库、README 和官方 Skill 为裁决源。没有发现需要把 bundle 标成 `flagged` 的核心硬错误。

## P0 清单

| 声明 | 结果 | 处理 |
|---|---|---|
| Hypit 官方仓库与 Agent 视频工作流定位（F-003~F-005） | ✅ | README 逐项一致 |
| 安装命令（F-009） | ✅ | README 逐字一致 |
| 词级锚定而非固定秒数（F-005） | ✅ | README 明确写出 words instead of seconds |
| 生成模型可选、代码可渲染（F-007） | ✅ | README 明确说明无需生成模型 |
| 20 秒 GOAT DEBATE、三种 clone（F-013~F-015） | ✅ | README 示例说明一致 |
| `$1.15` 成本与 64 Chromium 并发（F-016~F-017） | ✅ | 仅作为该官方示例运行口径 |
| Node/pnpm/TypeScript/许可证（F-011~F-012） | ✅ | README 徽章口径；依赖可能随版本变化 |

## 勘误与边界

1. F-023 的 1.1 万 Star 是博文页面时点单源，不写成当前仓库规模。
2. F-016 不是“Hypit 每条视频 $1.15”，而是官方 GOAT DEBATE 示例的总成本。
3. Seedance、GPT Image、WhisperX 等为第三方服务或工具；其价格、配额和可用性不由 Hypit 保证。
4. 许可证以仓库当前 LICENSE 为准；README 徽章中的 “with conditions” 提示读者继续查看许可证正文。
5. 使用参考视频和人物、Logo、产品素材时，需自行确认版权、肖像权和平台规则。
