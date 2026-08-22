---
type: Reference
title: TRAE Agents 仓库资源索引
description: trae-agents 仓库源码位置、目录结构、Agent 配置模型、模板规范和贡献流程的信源登记簿
tags: [agents, trae, configuration, template, source-index, trae-agents]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/agents-source.md
    title: "Trae Agents 源码信源"
---

# TRAE Agents 仓库资源索引

本文档汇总 trae-agents 仓库的文件结构、Agent 配置模型和贡献机制。

## 仓库基本信息

| 项目 | 内容 |
|------|------|
| 仓库地址 | `trae-community/trae-agents`（GitHub） |
| 许可证 | MIT License |
| 定位 | 社区维护的 TRAE 自定义智能体配置集合 |
| 语言支持 | 中英双语（README.md / README.zh-CN.md） |
| 与 MCP 区分 | 明确区分 Agent 配置和 MCP Servers，MCP 工具指向 `../trae-mcp` |

## 仓库目录结构

```
trae-agents/
├── README.md                 # 英文 README
├── README.zh-CN.md           # 中文 README
├── CONTRIBUTING.md           # 英文贡献指南
├── CONTRIBUTING.zh-CN.md     # 中文贡献指南
├── LICENSE                   # MIT 许可证
├── .gitignore
├── agents/                   # Agent 配置目录
│   ├── _template/            # Agent 配置模板
│   │   └── README.md         # 模板文件（YAML frontmatter + 8 章节）
│   └── git-commit-generator/ # 唯一正式 Agent
│       └── README.md         # Git Commit Generator 配置
├── assets/image/
│   └── Agents.gif            # 横幅图片
└── .github/ISSUE_TEMPLATE/
    ├── agent_request.md      # 新 Agent 请求模板
    └── bug_report.md         # Bug 报告模板
```

## Agent 配置四要素

每个 TRAE Agent 包含 4 项核心配置：

| 要素 | 符号 | 说明 |
|------|------|------|
| 名称 | 📋 Name | Agent 的显示名称 |
| 提示词 | 💬 Prompt | 定义 Agent 行为的系统提示词 |
| 工具 | 🛠️ Tools | 可调用的工具（MCP 服务 + 内置工具） |
| 协作 | 🤝 Collaboration | 可调用的其他 Agent |

## 内置工具清单

Agent 可勾选的 5 项内置工具：

1. 文件编辑
2. 终端命令
3. 网络搜索
4. 浏览器自动化
5. 其他智能体调用

## 模板 8 章节结构

`agents/_template/README.md` 规定每个 Agent 文档必须包含：

1. 基本信息（YAML frontmatter: name, description）
2. 提示词（Prompt）
3. 工具配置（MCP 服务 + 内置工具勾选清单）
4. 可协作智能体
5. 使用示例（至少 2 个）
6. 配置建议（模型选择 + 高级设置）
7. 相关资源
8. 贡献者、许可证

模板推荐配置：模型 GPT-4/Claude，温度 0.7。

## Git Commit Generator 参考实现

| 配置项 | 值 |
|--------|-----|
| 名称 | Git Commit Generator |
| 功能 | 根据代码变更自动生成 Conventional Commits 提交信息 |
| Conventional Commits 类型 | feat/fix/docs/style/refactor/perf/test/build/ci/chore/revert（11种） |
| 格式 | `<type>(<scope>): <subject>`，祈使语气、首字母小写、无句号、主题≤50字符 |
| 勾选工具 | 仅"终端命令"（执行 git diff） |
| 推荐模型 | GPT-4/Claude 3.5/Gemini Pro，温度 0.3-0.5 |
| 上下文长度 | 4K 足够 |

## Issue 模板

| 模板 | 标题前缀 | 标签 | 关键字段 |
|------|---------|------|---------|
| Agent Request | `[Agent]` | enhancement | Agent Name/Description/Status/Documentation/Usage Scenario/Proposed Instructions/Example I/O |
| Bug Report | `[BUG]` | bug | Bug 描述/Agent Name/复现步骤/预期行为/实际行为/环境信息 |

## 6 步贡献流程

1. 阅读 CONTRIBUTING.md
2. Fork 仓库，创建新分支
3. 在 `agents/` 下创建智能体目录
4. 按 `_template/` 模板提供完整配置
5. 更新根目录 Agent List 表格
6. 提交 PR

## 当前状态

- 正式 Agent 数量：**1 个**（git-commit-generator，状态 Stable）
- 另有一行"(To be added)"占位，仓库处于初始化阶段
- 遵循"质量优先于数量"的冷启动策略：先打磨 1 个高质量参考实现，再引导社区贡献

## 相关链接

- [TRAE Agents 仓库定位与"文档即配置"模式](/concepts/00-introduction.md)
- [Agent 目录结构与模板规范](/concepts/01-agent-structure.md)
- [Git Commit Generator 参考实现分析](/concepts/02-git-commit-agent.md)
- [创建自定义 Agent 示例](/examples/create-agent.md)
