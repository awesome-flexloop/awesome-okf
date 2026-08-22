---
type: Concept
title: TRAE Agents 仓库定位与"文档即配置"模式
description: trae-agents 作为 TRAE 自定义智能体配置集合的仓库定位、agents/ 目录约定以及"文档即配置"的设计理念
tags: [agents, trae, documentation-as-configuration, directory-convention, trae-agents]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/agents-source.md
    title: "Trae Agents 源码信源"
---

# TRAE Agents 仓库定位与"文档即配置"模式

## 仓库定位

trae-agents 是 TRAE 社区维护的**自定义智能体配置集合仓库**，采用 MIT 许可证。它的核心功能是收集、展示和分享社区创建的 TRAE Agent 配置，让用户可以浏览现成的 Agent 设置，直接导入 TRAE IDE 使用。

仓库明确区分了两类扩展：

- **Agents**（本仓库）：智能体配置——定义 Agent 的名称、提示词、工具权限和协作关系
- **MCP Servers**（trae-mcp 仓库）：工具服务器——提供 Agent 可调用的程序化工具能力

这种分离让用户按需查找：想要智能体行为配置来 trae-agents，想要外部工具连接去 trae-mcp。

## Agent 配置四要素

每个 TRAE Agent 的配置包含 4 个核心要素：

1. **📋 名称（Name）**：Agent 的标识名称，用于在 TRAE 中识别和选择
2. **💬 提示词（Prompt）**：系统提示词，定义 Agent 的角色、行为规则和输出格式
3. **🛠️ 工具（Tools）**：Agent 可调用的工具集合，包括 MCP 服务和内置工具（文件编辑、终端命令、网络搜索、浏览器自动化、其他智能体调用）
4. **🤝 协作（Collaboration）**：Agent 可以调用的其他智能体，形成 Agent 间协作网络

## 目录约定：agents/\<agent-name\>/README.md

项目采用简洁的目录约定存储 Agent 配置：

```
agents/
├── _template/           # 标准化模板目录
│   └── README.md        # 模板文件（新 Agent 的起点）
└── git-commit-generator/  # 具体 Agent 目录
    └── README.md        # 该 Agent 的完整配置文档
```

每个 Agent 是一个**独立目录**，目录名使用 kebab-case 命名（如 `git-commit-generator`），目录内只需要一个 `README.md` 文件即可完整描述 Agent 配置。

## "文档即配置"模式

trae-agents 最核心的设计选择是采用**纯 Markdown + YAML frontmatter** 的"文档即配置"（Documentation as Configuration）模式，而非 JSON/YAML 等结构化配置格式。

### 设计取舍

| 维度 | 结构化配置（JSON/YAML） | 文档即配置（Markdown + YAML） |
|------|------------------------|------------------------------|
| 机器可解析性 | ✅ 高，可直接被程序读取 | ❌ 较低，需要解析 Markdown |
| 人类可读性 | ❌ 差，嵌套层级深、符号多 | ✅ 极佳，自然语言+格式标记 |
| Git 友好性 | ❌ diff 噪音大，格式敏感 | ✅ diff 清晰，行级变更明确 |
| PR 审查难度 | ❌ 难以快速判断配置质量 | ✅ 像审查文档一样直观 |
| 贡献门槛 | ❌ 需了解配置 schema | ✅ 会写 Markdown 就能贡献 |

选择 Markdown 而非结构化格式，牺牲了一定的机器可解析性，但换来了极佳的人类可读性和社区友好性——这对于一个**社区驱动的配置分享仓库**是正确的权衡。

### YAML frontmatter + Markdown 正文混合格式

每个 Agent 的 README.md 采用混合格式：
- **YAML frontmatter**（顶部 `---` 之间）：存放结构化元数据（name、description）
- **Markdown 正文**：存放自由形式的内容（提示词、使用示例、配置建议等）

这种混合格式既保留了必要的元数据结构化能力，又让内容表达保持灵活。

## 4 步使用流程

README 中描述了用户使用 Agent 的标准流程：

1. **Browse Agents**：浏览 Agent List 表格，找到需要的 Agent
2. **View Configuration Details**：点击进入对应目录查看 README.md 中的完整配置
3. **Create in TRAE**：打开 TRAE IDE → 进入智能体管理 → 按文档填写名称/提示词/工具配置 → 保存测试
4. **Adjust and Optimize**：根据使用效果调整提示词和参数

## 相关链接

- [Agent 目录结构与模板规范](/concepts/01-agent-structure.md)
- [Git Commit Generator 参考实现分析](/concepts/02-git-commit-agent.md)
- [创建自定义 Agent 示例](/examples/create-agent.md)
- [TRAE Agents 仓库资源索引](/references/agents-source.md)
