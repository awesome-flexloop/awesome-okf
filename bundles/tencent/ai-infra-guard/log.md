---
type: Changelog
title: AI-Infra-Guard 知识束变更日志
---

# 变更日志

## 2026-08-23 — 初始版本

基于 AI-Infra-Guard 源码（commit main 分支，2026-08 快照）生成 OKF v0.2 知识束。

### 新增

- **spec/facts.md**：68 条编号事实，覆盖 CLI、WebSocket Server、Runner、指纹 DSL、漏洞结构、Agent 客户端、5 种任务类型、internal/mcp、Python 子系统、数据规模
- **spec/insights.md**：5 个核心洞察 + 知识地图 + 事实覆盖矩阵
- **references/**：5 个信源文件（go-server、scan-engine、vuln-struct、python-subsystems、data-rules）
- **concepts/**：7 个概念文档
  - 00 分布式 Server-Agent 架构总览
  - 01 四种任务类型
  - 02 指纹规则 DSL
  - 03 CVE 漏洞匹配
  - 04 WebSocket 通信协议
  - 05 Go/Python 桥接机制
  - 06 MCP 安全扫描
- **examples/**：3 个示例文档（CLI 扫描、自定义指纹、Docker 部署）
- **index.md / log.md**：根索引和变更日志

### 统计

- 事实数量：68 条（F-001 ~ F-068）
- 概念文档：7 篇
- 示例文档：3 篇
- 信源文件：5 篇
- 数据文件：142 指纹 / 2014 漏洞 / 15 MCP 规则 / 17 评测集

### 生成方法

使用 source-code-to-okf-wiki R→I→E→V 工作流：
- R 阶段：逐文件阅读 Go 源码，提取零推测事实
- I 阶段：提炼架构洞察，设计知识地图
- E 阶段：信源先行，分批生成 references → concepts → examples → indexes
- V 阶段：Grep 验证 API 真实性
