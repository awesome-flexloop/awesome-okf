---
okf_version: "0.2"
type: log
title: 变更日志（claude-agent-sdk-production）
description: bundle 生成、核验与审查记录
tags: []
---

# 变更日志

## 2026-11-10 v1.0.0 初始生成

- **工作流**：blog-article-to-okf-wiki 七阶段（R→I→E→V），由 seven-concepts-cmd 元编排（场景 4：知识沉淀）
- **信源**：Stackademic 博文《Building Production AI Agents with Anthropic's Claude Agent SDK》（页面标注 2026-09-26；正文事件时点 2025-09-29），web_fetch 抓取完整 HTML 转 Markdown（8,733 字符，无截断）
- **骨架判定**：操作可复现性两问——第一问“有安装/配置/代码”是；第二问“作者实测、有版本/输入输出/步骤顺序”否 → 无 `examples/`，定性为技术综述 + 快速上手解读
- **归属**：`jishu/ai/practice`（工程实践、方法论与行业洞察），与 `claude-model-selection`、`codex-agent-workflow-practices` 同型；不新建分组
- **事实**：F-001～F-087 共 87 条，spec `facts.md` 与 `references/article-source.md` 双份登记，集合一致、连续无跳号
- **核验**：11 个 P0 集群（✅8 / ⚠️3 / ❌0），权威信源为 Anthropic 官方新闻、官方工程文章、Agent SDK overview/quickstart/permissions/hooks、PyPI 与 npm；3 项 ⚠️ 为 E-1 日期异常、E-2 模型时效、E-4 Darktrace 单源；E-3 为 Python CLI 打包精度
- **补充事实**：官方文档补入权限六步评估、六种模式、`allowed_tools`/`disallowed_tools` 语义、审计盲区、认证限制、当前模型阵容与版本快照
- **文件**：12 个（index + log + concepts×6（含 index）+ references×3（含 index））

### 门禁运行说明（实测）

- `scripts/check-bundles-index.py`：✅ 通过——9 域 / 64 组 / 729 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。
- `scripts/check-toctrees.py`：✅ 通过——全库 index.md 引用有效，所有内容文档均可达。
- `scripts/check-utf8.py`：✅ 通过——bundle 11 个文件 + spec 2 个文件均为有效 UTF-8。
- `scripts/check-section-anchors.py`：⚠️ 全库历史存量红灯（6560 处既有断链，非本束引入）；本 bundle 不含跨文档锚点引用，作用域内链接由自检脚本覆盖。
- 手动等效检查：双份 F 编号 87=87；bundle 内相对链接全部可达；frontmatter 必填字段齐备；表格管道符一致。
- `scripts/check-asset-baseline.py`：⚠️ 未通过——工作区存在并行会话的在途束（`coding-harness-general-purpose-agents` 等）与未提交改动，归一化字节残差超容差；该失败与 bundle 内容无关，提交/清理工作区后复跑。

### 已知计数背景（非本束引入）

- 本轮期间并行会话新增 `coding-harness-general-purpose-agents` 等束，`jishu/ai/frameworks` 也有新增；共享索引已按目录树地面真值（729 束 / 64 组 / 9 域）同步，包含并行束的计数，但未提交其内容。
- 本 bundle 自身计数：practice 32 束 / 30 目录、ai 296 束、jishu 534 束、总索引 729 束。

### 边界

- 代码片段未在本库环境执行，正文显著标注“未实测”。
- Darktrace 研究未独立定位，标“仅博文单源”。
- 页面日期与正文事件时点冲突，按 2025-09-29 知识时点处理（E-1）。
- `stale_after` 设为 2027-01-31；模型与 SDK 版本迭代快，到期前复核。
