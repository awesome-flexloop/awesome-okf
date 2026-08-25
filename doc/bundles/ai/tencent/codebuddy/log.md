---
type: Changelog
scope: codebuddy
name: log
version: "0.1.0"
---

# Changelog

## 0.1.0 — 2026-08-23

### 新增

- 初始 OKF v0.2 知识包生成
- **spec/facts.md**：79 条编号事实（F-001 ~ F-079），覆盖 CodeBuddy IDE、IDE 文档、CLI、NPC、WorkBuddy、Security 六个官方信源
- **spec/insights.md**：5 条核心架构洞察，每条包含陈述/证据/反常识/行动：
  1. 三态一体——IDE、插件、CLI 共享同一套 AI 核心能力
  2. 产设研全链路闭环——从自然语言到部署的垂直整合
  3. NPC 云端 AI 员工——从本地辅助到自主交付的范式跃迁
  4. 对抗性安全审查——多 Agent 证伪与 PoC 动态验证重构 SAST
  5. 分层记忆与 Sub-agent 架构——CLI 的企业级可定制性
- **6 个信源登记文档**：
  - ide.md（IDE 官网，F-001 ~ F-008）
  - docs-intro.md（IDE 文档介绍，F-009 ~ F-025）
  - cli.md（CLI 官网，F-026 ~ F-038）
  - npc.md（NPC 官网，F-039 ~ F-051）
  - workbuddy.md（WorkBuddy 官网，F-052 ~ F-060）
  - security.md（Security 官网，F-061 ~ F-079）
- **6 个概念文档**：
  - 00-product-matrix.md（产品矩阵总览）
  - 01-ide.md（CodeBuddy IDE 产设研一体）
  - 02-cli.md（CLI 终端工具与分层记忆）
  - 03-npc.md（NPC 云端 AI 员工）
  - 04-workbuddy.md（WorkBuddy 在线助手）
  - 05-security.md（Security 安全审计六步闭环）
- **2 个示例文档**：
  - quick-start-cli.md（CLI 安装、初始化、诊断与核心功能）
  - ide-workflow.md（IDE 从需求到部署的产设研全流程）
- **索引文件**：concepts/index.md、examples/index.md、references/index.md
- **根 index.md**：知识包介绍、产品矩阵篇/核心能力篇/实战示例/信源登记簿分区导航、学习路径、信任与生命周期说明

### 数据来源

- CodeBuddy IDE 产品官网（https://www.codebuddy.cn/ide/）
- CodeBuddy IDE 官方文档介绍（https://www.codebuddy.cn/docs/ide/Introduction）
- CodeBuddy CLI 产品官网（https://www.codebuddy.cn/cli/）
- CodeBuddy NPC 产品官网（https://www.codebuddy.cn/npc/）
- WorkBuddy 在线应用（https://www.workbuddy.cn/app）
- CodeBuddy Security 产品官网（https://www.codebuddy.cn/security/）

### 生成方式

- R 阶段：从六个官方网页提取 79 条编号事实，每条标注信源与对应事实 ID
- I 阶段：基于事实综合分析，形成 5 条核心架构洞察（陈述/证据/反常识/行动）
- E 阶段：按 OKF v0.2 规范创建目录结构，编写 6 信源、6 概念、2 示例及完整导航索引
- V 阶段：由 `process:seven-concepts-v` 过程核验，所有事实均可溯源至官方页面，无虚构内容
