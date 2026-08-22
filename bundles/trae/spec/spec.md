---
spec_version: "1.0"
created: "2026-08-23"
status: draft
---

# TRAE Community 生态 OKF Wiki 生成规格

## 问题陈述

TRAE Community（[github.com/trae-community](https://github.com/trae-community)）是 TRAE AI IDE 的官方社区组织，包含 12 个子项目，涵盖社区治理、Agent 配置、MCP 服务器、技能库、项目模板、演示作品展示、共创平台、学习资源、活动运营等多个方面。当前这些项目缺乏系统化的中文源码级教程，需要通过 source-code-to-okf-wiki 工作流生成 OKF v0.2 规范的知识束。

## 用户与目标

- **用户**：希望了解 TRAE Community 生态架构、学习各子项目源码结构与设计模式的中文开发者
- **目标**：为 trae-community 下全部 12 个子项目生成结构化 OKF 知识束，覆盖概念文档、实战示例、信源参考三层结构
- **非目标**：
  - 不修改 trae-community 源码
  - 不生成英文文档
  - 不覆盖 TRAE IDE 本体（仅社区生态项目）
  - 不深度分析每个 starter template 的业务代码（模板项目聚焦结构与脚手架设计）

## 功能需求

### FR-1：分类索引
- 创建 `bundles/trae/index.md` 作为 TRAE 生态分组索引
- 按子项目性质分组：核心系统、学习与演示、社区资源、模板脚手架
- 更新 `bundles/index.md` 总索引，增加 trae 分组

### FR-2：子项目知识束
为 12 个子项目分别创建 OKF bundle，按项目复杂度分三个深度等级：

**深度 L2（完整 R→I→E→V→C，代码项目）**：
- `trae-co-creation-demo-wall`：Next.js 全栈应用，含路由层/API/组件层/工具层/Prisma 数据层
- `trae-co-creation-demo-wall-intl`：国际化版本（与中文版共享架构，聚焦差异点）

**深度 L1（R→I→E→V，配置/脚本项目）**：
- `trae-skills`：技能库，含 SKILL.md 规范、9个社区技能、Python/JS 脚本
- `trae-templates`：项目模板库，5大类18个 starter 模板
- `trae-learning`：VitePress 学习站，含 guide/ 和 tutorials/ 内容体系
- `trae-friends-events`：活动数据管理，含 CSV 数据模型 + Python 更新脚本
- `trae-mcp`：MCP 服务器集合，含 cloudbase MCP 配置与使用

**深度 L0（轻量文档，资源/展示类项目）**：
- `awesome-trae`：Awesome 列表，资源分类体系
- `trae-agents`：Agent 配置库，Agent 定义规范与 git-commit-generator 实例
- `trae-demos`：演示作品展示，Issue 提交流程与评审标准
- `trae-co-creation-projects`：共创项目展示，分类体系与提交流程
- `trae-discussions`：社区讨论入口，讨论分类与参与指南

### FR-3：文档结构
每个 bundle 遵循 OKF v0.2 规范：
```
<bundle-name>/
├── index.md          # 根索引（含 okf_version frontmatter）
├── log.md            # 变更日志
├── concepts/         # 概念文档
│   ├── index.md
│   └── NN-xxx.md
├── examples/         # 示例文档（L1/L2 项目）
│   ├── index.md
│   └── ...
└── references/       # 信源登记（L1/L2 项目）
    ├── index.md
    └── <source>.md
```

L0 项目简化为：index.md + log.md + concepts/（无需 examples/ 和 references/）

### FR-4：信源先行
- L1/L2 项目的 references/ 信源文件必须在 concepts/ 之前生成
- 所有代码引用必须指向源码中的具体文件路径
- API/函数/类名必须经 Grep 验证存在

### FR-5：分批生成
- 每批生成 ≤ 7 个文档文件
- index.md 必须最后生成
- 每批完成后自检 frontmatter 完整性

## 非功能需求

### NFR-1：文档质量
- 所有概念文档含完整 YAML frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）
- 代码块标注语言类型
- 交叉链接使用 `/` 开头的 bundle-relative 路径
- 中文撰写，英文技术术语首次出现括号注释

### NFR-2：验证要求
- L2 项目：所有类名/函数名/API 路径经 Grep 源码验证
- L1 项目：关键脚本函数、SKILL.md 字段、模板结构经源码验证
- L0 项目：README 内容交叉引用验证
- 所有内部链接 0 断链
- frontmatter 字段 100% 完整

### NFR-3：方法论遵循
- 严格遵循 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）
- 遵循 seven-concepts-cmd 知识沉淀场景链路（R→I→E）
- 质量门 G1-G4 全部通过

## 约束条件

- **源码路径**：`d:\spaces\SpecWeave\external\libs\ai\trae-community\`
- **输出路径**：`d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\trae\`
- **文档规范**：OKF v0.2
- **语言**：中文
- **文件名**：kebab-case 英文
- **不修改**：源码目录、已有 bundle 内容（仅更新 bundles/index.md）

## 假设

- trae-community 各子项目已克隆到本地，源码可读
- awesome-okf-xs 子项目已初始化
- 不需要安装额外依赖（文档生成为纯文本工作）

## 验收标准

### AC-1（rule）：分类索引完整
- `bundles/trae/index.md` 存在且含 okf_version frontmatter
- `bundles/index.md` 已更新，包含 trae 分组条目
- 分组索引正确列出所有 12 个子项目 bundle

### AC-2（rule）：所有子项目 bundle 创建
- 12 个子项目目录均存在于 `bundles/trae/` 下
- 每个 bundle 含 index.md 和 log.md
- L1/L2 项目含 concepts/、examples/、references/ 三个子目录及各自 index.md
- L0 项目至少含 concepts/ 目录及 index.md

### AC-3（rule）：frontmatter 合规
- 所有 .md 文件（除子目录 index.md）含完整 YAML frontmatter
- 必填字段：type/title/description/tags/generated/verified/status/stale_after/sources（references 可不做 sources 自引用）
- 根 index.md 含 okf_version: "0.2"
- 子目录 index.md 不含 frontmatter

### AC-4（rule）：API 真实性
- L2 项目文档中引用的所有类名/函数名/API 路径经 Grep 验证存在于源码
- L1 项目关键结构（SKILL.md frontmatter 字段、模板目录结构、脚本函数名）经验证
- 无虚构 API、无过时方法、无编造的参数签名

### AC-5（rule）：链接完整性
- 所有内部交叉链接（/concepts/、/examples/、/references/ 路径）可解析
- 无 `../` 相对路径，全部使用 `/` 开头 bundle-relative 路径
- sources 字段指向的 references/ 文件存在

### AC-6（rubric）：文档质量（0-3 分，≥2 分通过）
- 3 分：概念文档逻辑清晰、代码示例准确可运行、学习路径合理、洞察深入
- 2 分：文档结构完整、API 描述准确、内容覆盖核心知识点
- 1 分：文档存在但有遗漏或浅层描述
- 0 分：文档缺失或大量虚构内容

### AC-7（rubric）：方法论遵循（0-2 分，≥1 分通过）
- 2 分：R→I→E→V→C 五阶段完整执行，facts.md/insights.md 存在且通过质量门
- 1 分：核心阶段执行，有事实采集和验证环节
- 0 分：跳过关键阶段直接生成
