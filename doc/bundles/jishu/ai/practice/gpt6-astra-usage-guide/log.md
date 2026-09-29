---
okf_version: "0.2"
type: log
title: 变更日志（gpt6-astra-usage-guide）
description: bundle 生成、核验与审查记录
tags: []
---

# 变更日志

## 2026-09-16 v1.0.0 初始生成

- **工作流**：blog-article-to-okf-wiki 七阶段（R→I→E→V），由 seven-concepts-cmd 元编排（场景 4：知识沉淀）
- **信源**：微信公众号 cxuanAI《Skill 又要被干掉了？OpenAI 祭出了 Astra 的使用焚诀》（2026-09-07），browser_use 提取全文 6555 字（WebFetch 被微信反爬拦截，符合既定规律）
- **骨架判定**：操作可复现性两问皆否（无端到端流程、作者未实测）→ 无 examples/，定性技术综述/官方指南解读
- **归属**：`jishu/ai/` 直挂束（不新建 openai 分组；先例 mattpocock-skills、free-llm-api-roundup 等博文转化直挂束）
- **事实**：F-001～F-043 共 43 条，spec facts.md 与 references/article-source.md 双份登记
- **核验**：10 个 P0 集群（✅8/⚠️2/❌0），权威信源 4 个 OpenAI 官方页面 + 2 个二手源；2 项 ⚠️（F-006 发布时间口语措辞、F-042 引流标题命题不成立）已在正文落实
- **补充事实**：博文遗漏的 8 项官方事实入束（规格定价、async 机制、steering 边界、监控覆盖面/403/webhook、priority 限制、迁移参数清单、Bedrock GA）
- **文件**：10 个（index/log + concepts×5（含 index）+ references×3（含 index））
- **机械门禁**：8 项手动等效门禁全通过；子模块 gate 脚本实测结果见 review.md 与下节

### 门禁运行说明（已实测，非占位）

直接运行子模块 `scripts/` 下门禁脚本（不经过 invoke 包装）：

- `check-utf8.py`：✅ 通过（全库 10321 文件）。
- `check-toctrees.py` / `check-bundles-index.py`：本 bundle 作用域干净（9 toctree 条目全存在、45 相对链接全可达、ai/ 直属 58 目录=58 toctree 条目、双份 F 集合 43=43 连续）；但全库红灯，17 处 toctree 问题与计数 +1 漂移全部来自并行会话在途束（`ai-agent/ai-agent-book`、`free-llm-api-hands-on`、`llama-cpp-local-inference`，缺 log.md/index.md），与本 bundle 无关，未代为修改。
- 本 bundle 计数按最后一致基线 +1：544/411/192 → 545/412/193，避免与并行会话收尾双重计数。
- 手动等效 8 项机械门禁全部通过，详见 spec 的 review.md。

### 已知历史计数漂移（非本次引入，未改）

- `jishu/index.md` 导语"111 个一级束"与 ai 行"45 束"为历史手工计数，与 `bundles/index.md` 三角对账口径长期不一致；本次遵循最小变更，仅更新 `bundles/index.md` 的权威计数与 `jishu/ai/index.md` 导航，不顺手修历史漂移。
