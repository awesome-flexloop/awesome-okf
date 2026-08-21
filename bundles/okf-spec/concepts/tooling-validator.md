---
type: Reference
title: OKF Validator
description: OKF 官方在线验证工具（okf.md/validator），上传目录或粘贴 Markdown 文件即可检查知识包合规性，报告错误、警告与提示。
tags: [okf, tooling, validator, linter]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T08:00:00Z }
status: draft
stale_after: 2027-06-30T00:00:00Z
sources:
  - id: okf-md-validator
    resource: https://okf.md/validator
    title: OKF Validator
  - id: okf-spec
    resource: /references/okf-spec.md
    title: OKF SPEC v0.2
---

# OKF Validator

OKF Validator 是官方提供的在线知识包验证工具，托管于 [okf.md/validator](https://okf.md/validator)。[^okf-md-validator]

## 功能

Validator 对 OKF 知识包执行自动化合规检查，覆盖 v0.2 规范的核心要求：

| 检查类别 | 检查项 |
|---|---|
| **错误（Errors）** | 严重违反 MUST 级要求的问题（如缺失 `type` 字段、frontmatter 解析失败、index.md 格式错误） |
| **警告（Warnings）** | 违反 SHOULD 级约定的问题（如缺少 `title`、`description`、链接指向不存在的文件） |
| **提示（Hints）** | 风格建议和最佳实践（如缺少 sources/verified 元数据） |

## 使用方式

Validator 支持两种输入方式：

1. **目录上传**：上传整个知识包目录（推荐），工具会遍历所有 `.md` 文件并检查内部链接。
2. **粘贴/上传单个文件**：将 Markdown 内容粘贴到编辑器或上传单个文件进行快速检查。

Validator 在浏览器中运行（客户端 JavaScript），知识包内容不会上传到服务器，适合检查包含敏感内部信息的知识包。

## 验证范围

基于 v0.2 规范（§11 Conformance），Validator 应检查的核心合规项包括：

1. **frontmatter 解析**：每个概念文件（非 index.md/log.md）必须有可解析的 YAML frontmatter。
2. **type 字段**：每个概念文件必须有非空的 `type` 字段。
3. **路径结构**：根目录 `index.md` 和 `log.md` 存在且格式正确。
4. **相对链接有效性**：`[label](/path/to/file.md)` 链接目标存在（断链为警告，因为断链在 OKF 中是允许的——代表"尚未编写的知识"）。
5. **字段格式**：`generated.at`、`verified.at`、`stale_after` 等时间字段格式为 ISO 8601 datetime + UTC offset。
6. **footnote 引用匹配**：`[^id]` 引用必须在文档中有对应的 `[^id]: ...` 定义。

## 与 validate.sh 的关系

Validator 是在线工具，适合快速检查和可视化结果。而 Agent Skill 中附带的 `validate.sh` 脚本适合在命令行、CI/CD 流水线中使用。两者执行相同的核心检查，但使用场景不同：

| 特性 | 在线 Validator | validate.sh |
|---|---|---|
| 使用方式 | 浏览器访问 okf.md/validator | 命令行/CI |
| 安装要求 | 零安装，打开即用 | 需要先安装 OKF Agent Skill |
| 输入方式 | 目录上传/粘贴文本 | 本地文件系统路径 |
| 输出格式 | 网页可视化（错误/警告/提示） | 终端输出 + 退出码 |
| CI 集成 | ❌ | ✅ |
| 隐私保护 | 客户端运行（不上传服务器） | 完全本地运行 |

## 验证后的常见修复

- **缺失 type**：在 frontmatter 中添加 `type: <descriptive-type-name>`。
- **frontmatter 解析失败**：检查 YAML 语法（缩进、冒号后空格、特殊字符引号）。
- **断链**：要么创建缺失文件，要么移除链接（断链在 OKF 中是合法的，但 Validator 会给出警告）。
- **footnote 未定义**：为每个 `[^id]` 引用添加 `[^id]: ...` 定义。

## 相关概念

- [合规性](./conformance.md) - v0.2 正式合规三要件
- [OKF Agent Skill](./tooling-agent-skill.md) - 包含 validate.sh 命令行工具
- [OKF Knowledge Catalog CLI](./tooling-knowledge-catalog.md) - 官方生态 CLI 工具
- [实践指南](./practical-guidance.md) - 快速验证三规则

[^okf-md-validator]: OKF Validator 官方页面，见 [okf.md/validator](https://okf.md/validator)。
[^okf-spec]: OKF SPEC v0.2 规范，见 [references/okf-spec.md](/references/okf-spec.md)。
