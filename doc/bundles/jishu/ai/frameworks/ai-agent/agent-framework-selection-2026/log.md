---
type: Log
title: 生成日志
description: 2026 AI Agent 框架选型 bundle 的七阶段执行记录、质量门判定、勘误与计数变更
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T15:10:00+08:00" }
status: stable
stale_after: 2027-01-31
---

# 生成日志

## 2026-11-10 — 初始转化

### 输入

- 主信源：https://dev.to/mr_manushukla/2026-ai-agent-frameworks-compared-langgraph-vs-crewai-vs-microsoft-agent-framework-vs-pydantic-ai-4f8k
- 原文：https://ecorpit.com/ai-agent-framework-production-langgraph-crewai-microsoft-pydantic-2026/（Last updated 2026-07-19）
- 工作流：`blog-article-to-okf-wiki` v1.0.0 → `seven-concepts` 编排（R→I→E→V→C）

### 阶段记录

1. **S0 预检**：公开 URL、无访问控制 → 标准工作流；产出落 `projects/awesome-okf-xs/doc/bundles/`。
2. **R 事实采集**：F-001~F-081 登记；信源距离判定为“第三方服务商综述（含自述）”。
3. **R 核验**：13 项 P0；GitHub Releases / PyPI / 官方公告 / 官方文档交叉核验。
4. **I 骨架判定**：操作可复现性两问均为“否” → 不设 `examples/`；归属 `ai-agent`。
5. **E 生成**：先 references → concepts → index；所有具体声明挂 F 编号。
6. **V 审查**：四视角 + 双份 F 编号比对 + 链接/计数/UTF-8 门禁。
7. **C 提交**：子模块 → 主仓库 spec → 子模块指针（不 push）。

### 质量门

| 门 | 判定 | 说明 |
|----|------|------|
| G1 事实无因果词 | 通过 | facts 表只陈述“是什么”，观点标 📝 |
| G2 洞察四元组 | 通过 | insights.md 四条均含陈述/证据/反常识/行动 |
| G3 模式可迁移 | 通过 | “按主导约束选型”“双框架分层”可迁移到非 Agent 选型 |
| G4 行动项原子化 | 通过 | tasks.md 五项均有 Owner/截止/验证方式 |
| V 门 | 通过 | 实质意见 13 条，采纳 10 条，拒绝 2 条，1 条转为待复核事项 |

### 勘误与降级

| 项 | 原文 | 核验结果 | 处置 |
|----|------|---------|------|
| LlamaIndex Workflows 1.0 日期 | 2026-06-22 | PyPI 1.0.0 = 2025-06-25；2026-10 最新 2.26.1 | F-072；正文改正确值；verification 单列 |
| MAF A2A 原生 | native at 1.0 | 公告写 A2A 1.0 support coming soon | F-074；降级为 ⚠️ |
| 五框架都支持 MCP | every one speaks MCP | 未逐框架取证，深度不一 | F-058；降级为 ⚠️ |
| Replit 生产用户 | 与另外五家并列 | 官方客户页未列 | F-075；标“单源” |
| token 价格区间 | $1~$5 / 1M | 无单一官方价 | F-061/F-080；保留区间并提示不可精算 |

### 计数变更

| 层级 | 变更前 | 变更后 |
|------|--------|--------|
| ai-agent 组 | 62 | 63 |
| frameworks 类 | 96 | 97 |
| ai 域 | 293 | 294 |
| jishu 域 | 531 | 532 |
| 全库 | 725 | 727（工作树当前值，含并行新增束） |

### 已知边界

- 未做五框架的本地安装/压测；所有能力判断来自官方文档与发布说明。
- 价格、用户名单、“不到一周上线”保留原始口径并标注不可精算/单源。
- MAF 在 2026-10 已新增 Go 预览；`stale_after` 前需复查版本与连接器变化。
- 结构检查依赖手动等效验证：当前环境未运行 `invoke gates.*`，已执行链接/计数/UTF-8 手动清单。

### 下次复核

- 2027-01-31 前复查：五框架最新稳定版、MAF Go/A2A 状态、LlamaIndex Workflows 2.x 定位、MCP 支持深度。
