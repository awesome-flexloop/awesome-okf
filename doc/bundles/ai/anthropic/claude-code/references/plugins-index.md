---
type: reference
title: "官方插件索引"
tags: [claude-code, plugins, official-plugins, index]
---

# 官方插件索引

本文档列出 Claude Code 的 13 个官方插件，按功能类别分组。

## 插件分类总览

| 类别 | 插件数量 | 包含插件 |
|------|---------|---------|
| 开发工作流类 | 4 | code-review, commit-commands, feature-dev, pr-review-toolkit |
| 安全与质量类 | 3 | security-guidance, ralph-wiggum, hookify |
| 学习与风格类 | 2 | learning-output-style, explanatory-output-style |
| 开发工具类 | 4 | plugin-dev, agent-sdk-dev, frontend-design, claude-opus-4-5-migration |

---

## 一、开发工作流类

### 1. code-review（自动化 PR 代码审查）

| 属性 | 内容 |
|------|------|
| **描述** | 自动化 Pull Request 代码审查 |
| **提供的 Commands** | `/code-review` |
| **提供的 Agents** | 5 个并行 Sonnet agents（多维度审查） |
| **一句话功能** | 启动 5 个并行代理从不同维度自动审查代码变更 |

### 2. commit-commands（Git 工作流自动化）

| 属性 | 内容 |
|------|------|
| **描述** | Git 工作流自动化命令集 |
| **提供的 Commands** | `/commit`, `/commit-push-pr`, `/clean_gone` |
| **一句话功能** | 自动生成规范提交信息，一键完成 commit → push → PR 全流程 |

### 3. feature-dev（7 阶段功能开发工作流）

| 属性 | 内容 |
|------|------|
| **描述** | 结构化的 7 阶段功能开发工作流 |
| **提供的 Commands** | `/feature-dev` |
| **提供的 Agents** | code-explorer, architect, reviewer |
| **一句话功能** | 引导从需求分析到代码审查的完整功能开发流程 |

### 4. pr-review-toolkit（PR 审查工具集）

| 属性 | 内容 |
|------|------|
| **描述** | 专业的 PR 审查工具集 |
| **提供的 Commands** | `/pr-review-toolkit:review-pr` |
| **提供的 Agents** | 6 个专项审查 agents |
| **一句话功能** | 6 个专项代理从安全、性能、风格等维度深度审查 PR |

---

## 二、安全与质量类

### 5. security-guidance（安全提醒钩子）

| 属性 | 内容 |
|------|------|
| **描述** | 实时安全提醒与监控钩子 |
| **提供的 Hooks** | PreToolUse hook |
| **监控模式** | 9 种常见安全风险模式 |
| **一句话功能** | 在工具调用前自动检测 9 类安全风险并提醒 |

### 6. ralph-wiggum（自引用 AI 迭代循环）

| 属性 | 内容 |
|------|------|
| **描述** | 自引用 AI 迭代改进循环 |
| **提供的 Commands** | `/ralph-loop`, `/cancel-ralph` |
| **提供的 Hooks** | Stop hook |
| **一句话功能** | 让 Claude 自我审查和迭代改进输出结果的递归循环 |

### 7. hookify（创建自定义 Hooks）

| 属性 | 内容 |
|------|------|
| **描述** | 辅助创建自定义 hooks 防止不当行为 |
| **提供的 Commands** | `/hookify` 系列命令 |
| **提供的 Agents** | conversation-analyzer agent |
| **提供的 Skills** | writing-rules skill |
| **一句话功能** | 分析对话并帮助用户编写自定义规则和 hooks |

---

## 三、学习与风格类

### 8. learning-output-style（交互式学习模式）

| 属性 | 内容 |
|------|------|
| **描述** | 鼓励用户动手实践的交互式学习输出风格 |
| **提供的 Hooks** | SessionStart hook |
| **一句话功能** | 会话开始时注入教学指令，鼓励用户自己写代码而非直接看答案 |

### 9. explanatory-output-style（教育性解释输出风格）

| 属性 | 内容 |
|------|------|
| **描述** | 详细解释实现选择的教育性输出风格 |
| **提供的 Hooks** | SessionStart hook |
| **一句话功能** | 让 Claude 在输出代码时详细解释为什么这样实现 |

---

## 四、开发工具类

### 10. plugin-dev（插件开发工具包）

| 属性 | 内容 |
|------|------|
| **描述** | Claude Code 插件开发工具包 |
| **提供的 Commands** | `/plugin-dev:create-plugin` |
| **提供的 Skills** | 7 个 expert skills（插件开发各阶段） |
| **提供的 Agents** | 3 个专用 agents |
| **一句话功能** | 一站式辅助开发 Claude Code 插件的完整工具链 |

### 11. agent-sdk-dev（Claude Agent SDK 开发工具包）

| 属性 | 内容 |
|------|------|
| **描述** | Claude Agent SDK 开发工具 |
| **提供的 Commands** | `/new-sdk-app` |
| **提供的 Agents** | agent-sdk-verifier-py, agent-sdk-verifier-ts |
| **一句话功能** | 快速创建和验证基于 Claude Agent SDK 的应用（Python/TypeScript） |

### 12. frontend-design（生产级前端界面设计）

| 属性 | 内容 |
|------|------|
| **描述** | 生产级前端界面设计能力 |
| **提供的 Skills** | frontend-design skill |
| **一句话功能** | 提供专业的前端设计最佳实践和组件设计指导 |

### 13. claude-opus-4-5-migration（模型迁移指南）

| 属性 | 内容 |
|------|------|
| **描述** | Sonnet 4.x/Opus 4.1 到 Opus 4.5 的迁移辅助 |
| **提供的 Skills** | claude-opus-4-5-migration skill |
| **一句话功能** | 指导从旧版 Claude 模型迁移到 Opus 4.5 的变更和适配 |

---

## 插件完整对照表

| 序号 | 插件名称 | Commands | Agents | Skills | Hooks |
|:---:|---------|:--------:|:------:|:------:|:-----:|
| 1 | agent-sdk-dev | ✅ `/new-sdk-app` | ✅ 2 个验证 agents | - | - |
| 2 | claude-opus-4-5-migration | - | - | ✅ 迁移 skill | - |
| 3 | code-review | ✅ `/code-review` | ✅ 5 个并行 Sonnet agents | - | - |
| 4 | commit-commands | ✅ 3 个 Git 命令 | - | - | - |
| 5 | explanatory-output-style | - | - | - | ✅ SessionStart |
| 6 | feature-dev | ✅ `/feature-dev` | ✅ 3 个 agents | - | - |
| 7 | frontend-design | - | - | ✅ 设计 skill | - |
| 8 | hookify | ✅ `/hookify` 系列 | ✅ conversation-analyzer | ✅ writing-rules | - |
| 9 | learning-output-style | - | - | - | ✅ SessionStart |
| 10 | plugin-dev | ✅ `/plugin-dev:create-plugin` | ✅ 3 个 agents | ✅ 7 个 expert skills | - |
| 11 | pr-review-toolkit | ✅ `/pr-review-toolkit:review-pr` | ✅ 6 个专项 agents | - | - |
| 12 | ralph-wiggum | ✅ 2 个命令 | - | - | ✅ Stop |
| 13 | security-guidance | - | - | - | ✅ PreToolUse |

---

## 相关资源

- [插件体系概念](../concepts/01-plugin-system.md) — 了解 Commands/Agents/Skills/Hooks 扩展机制
- [基本使用示例：安装插件](../examples/basic-usage.md#安装插件示例) — 如何安装和使用插件
