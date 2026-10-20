---
okf_version: "0.2"
type: log
title: 变更日志（deepseek-v41-flash-1017）
description: bundle 生成、核验与审查记录
tags: []
---

# 变更日志

## 2026-10-20 v1.0.0 初始生成

- **工作流**：blog-article-to-okf-wiki 七阶段（R→I→E→V），由 seven-concepts-cmd 元编排（场景 4：知识沉淀，depth=standard）
- **信源**：微信公众号「赛博禅心」《DeepSeek V4.1 Flash 新版发布：api 自带搜索能力》（2026-10-17 16:32），WebFetch 提取全文约 1900 字（含两张官方图表转录）
- **骨架判定**：操作可复现性两问皆否（无端到端流程、作者未实测）→ 无 examples/，定性为发布解读型技术综述
- **归属**：`jishu/ai/practice/` 博文核验转化束（先例：gpt6-astra-usage-guide、token-economy-explosion、verbi 等同批次转化束）；未并入 `ecosystems/deepseek*` 既有束，避免与 [deepseek-search-fetch](../../ecosystems/deepseek-search-fetch/index.md)、[deepseek-pricing](../../ecosystems/deepseek-pricing/index.md)、[deepseek-harness](../../ecosystems/deepseek-harness/index.md) 重复
- **事实**：F-001～F-068 共 68 条，10 组分区（信源/开源/纵向基准/横向基准/成本/定价/平台/许愿式编程/搜索 API/观点层）
- **核验**：6 个 P0 集群（✅5/⚠️1/❌0）+ 1 条第三方 USD 定价不采信（F-047）；权威信源：DeepSeek 官方公告、API 文档定价页、HuggingFace 模型卡（快照）、多家媒体报道
- **补充事实**：博文遗漏的 8 类官方事实入束（峰谷定价全表、旧模型名迁移脚注、并发/思考模式/FIM 规格、扣费规则、上下文与最大输出、旧模型名静默迁移风险等）
- **V 阶段**：四视角对抗审查提出 13 条具体意见，采纳并修正 7 条（详见 [verification.md](references/verification.md) §三）
- **文件**：11 个（index/log + concepts×6（含 index）+ references×3（含 index））

### 门禁与计数

- `check-utf8.py`：✅ 通过
- `check-toctrees.py` / `check-bundles-index.py`：本 bundle 作用域干净（toctree 条目齐全、相对链接可达、F 编号 68 条连续无跳号）；全库结果另见下节
- 计数按最后一致基线 +1：`bundles/index.md` 654→655、`jishu/ai/index.md` 253→254、practice 21→22

### 已知历史计数漂移（非本次引入，未改）

- `jishu/index.md` 导语中的「111 个一级束」与 ai 行「45 束」为历史手工计数，与 `bundles/index.md` 长期不一致；本次遵循最小变更原则，只更新权威计数与 `jishu/ai/index.md`、`practice/index.md` 导航，不顺手修历史漂移。
