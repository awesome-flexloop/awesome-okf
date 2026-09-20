---
type: Reference
title: "核验报告与证据边界"
description: "对 OpenMontage 的机制、安装、流水线、规模数字和许可证进行官方核验"
tags: [OpenMontage, 核验, AGPL, 证据边界]
generated: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-12-31
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/Icq2rjqPi7gfVb-x7cCz8Q" }
  - { id: repo, resource: "https://github.com/calesthio/OpenMontage" }
  - { id: guide, resource: "https://raw.githubusercontent.com/calesthio/OpenMontage/main/AGENT_GUIDE.md" }
  - { id: license, resource: "https://raw.githubusercontent.com/calesthio/OpenMontage/main/LICENSE" }
---

# 核验报告与证据边界

> **状态：flagged。** 文章热度、节省时间和部分仓库规模数字是第三方时点描述，不能作为当前指标或效果承诺。官方仓库支持的是结构、安装路径和许可证事实。

## 日期与版本

| 项目 | 结论 |
| --- | --- |
| 微信文章日期 | 页面显示2026-07-31；仅表示文章发布时间 |
| GitHub 版本 | 当前主分支页面显示无正式 tag，教程引用读取日快照，不声明稳定版本 |
| Star/Fork | 随时间变化；文章数字保留为 F-011，不用于当前排名 |
| 许可证 | 官方 LICENSE 为 GNU AGPLv3 |

## 机制核验

- README 明确提供快速开始、流水线、工具/技能层和渲染路径，支持 F-004 至 F-013 的主要结构性描述。
- AGENT_GUIDE 明确要求具体请求遵循规则、读取技能、选择流水线并进行检查点处理；这支撑“Agent 作为导演”的解释，但不等于每次生成都成功。
- 官方材料没有为微信文章中的“省时50%”提供独立基准，因此该数字保持单源并标记为证据缺口。

## 许可证与成本边界

AGPLv3 讨论的是软件自由、修改和分发条件；Piper、本地渲染或开放素材可能减少 API 支出，但外部模型、云服务、素材使用条款和运维成本仍需单独核算。本文不提供法律意见。

## 复核要求

下一次复核应固定具体 commit，重新读取 README、AGENT_GUIDE、`pipeline_defs/` 和 `skills/` 的实际目录，核对流水线、工具和技能数量，并在有真实运行日志后再评估耗时、成本和成片质量。
