---
type: Concept
title: Agent 目录结构与模板规范
description: trae-agents 的目录命名约定、README.md 必备 8 章节结构、_template 模板规范、内置工具勾选清单与配置建议
tags: [agents, template, readme-structure, directory-convention, tool-checklist, trae-agents]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/agents-source.md
    title: "Trae Agents 源码信源"
---

# Agent 目录结构与模板规范

## 目录命名约定

在 `agents/` 目录下创建 Agent 时，遵循以下约定：

1. **目录名**：使用 kebab-case（小写字母+连字符），如 `code-review-expert`、`test-helper`
2. **目录结构**：每个 Agent 一个独立目录，目录内包含一个 `README.md` 文件
3. **禁止特殊字符**：目录名不使用空格、大写字母、下划线或其他特殊字符

正确示例：
- `agents/git-commit-generator/`
- `agents/documentation-assistant/`
- `agents/code-review-expert/`

错误示例：
- `agents/GitCommitGenerator/`（驼峰命名）
- `agents/git_commit_generator/`（下划线）
- `agents/git commit/`（含空格）

## README.md 必备章节

每个 Agent 的 README.md 必须包含以下 8 个章节，以确保信息完整性和一致性：

### 1. 基本信息（YAML frontmatter）

文件开头使用 YAML frontmatter 定义元数据：

```yaml
---
name: Agent 名称
description: 一句话描述 Agent 的功能
---
```

### 2. 提示词（Prompt）

完整的系统提示词内容，包括：
- 角色定义（Agent 是谁、擅长什么）
- 行为规则（应该做什么、不应该做什么）
- 输出格式（返回结果的结构和规范）
- 约束条件（边界和限制）

### 3. 工具配置

分两部分说明：
- **MCP 服务**：需要哪些 MCP 服务器（如不需要则标注"不需要特殊的 MCP 服务"）
- **内置工具勾选清单**：使用复选框标注启用的工具

内置工具勾选清单格式：
```markdown
- [x] 文件编辑
- [x] 终端命令
- [ ] 网络搜索
- [ ] 浏览器自动化
- [ ] 其他智能体调用
```

### 4. 可协作智能体

列出该 Agent 可以调用的其他 Agent 名称及协作场景。如无可标注"无特殊协作需求"。

### 5. 使用示例

至少提供 **2 个**使用示例，每个示例包含：
- 输入（用户给 Agent 的指令）
- 输出（Agent 的预期响应或行为）

示例是用户理解 Agent 能力的最直观方式。

### 6. 配置建议

提供两方面的建议：
- **模型选择**：推荐使用的模型（如 GPT-4/Claude/Gemini Pro）
- **高级设置**：温度参数、上下文长度建议等

模板默认推荐：GPT-4/Claude 模型，温度 0.7。

### 7. 相关资源

列出与该 Agent 相关的文档、教程、参考链接等。

### 8. 贡献者与许可证

标注贡献者信息和许可证（默认 MIT）。

## _template 目录的作用

`agents/_template/` 目录是新项目的标准起点，其作用包括：

1. **标准化起点**：贡献者复制模板目录，填写内容即可，无需从零设计结构
2. **质量基线**：模板中的每个章节提示都标明了应填写的内容类型，确保最低信息完备度
3. **一致性保障**：所有 Agent 遵循相同章节结构，用户浏览任何 Agent 都能快速定位信息
4. **活文档**：模板本身随项目演进而更新，反映最新的最佳实践

## 工具最小化原则

配置 Agent 工具时应遵循**最小权限原则**：只勾选 Agent 完成任务所必需的工具，避免过度授权。

例如，git-commit-generator 只需要"终端命令"来执行 `git diff`，因此仅勾选这一项，不启用文件编辑、网络搜索等无关工具。这不仅减少了安全风险，也让 Agent 的行为更加聚焦和可预测。

## 贡献前自检清单

提交新 Agent 前，对照以下清单自检：

- [ ] 目录名使用 kebab-case 命名
- [ ] YAML frontmatter 包含 name 和 description
- [ ] 8 个必备章节全部填写
- [ ] 提示词完整可用，非占位文本
- [ ] 工具配置按实际需要勾选（最小化原则）
- [ ] 至少 2 个使用示例
- [ ] 配置建议包含模型和温度推荐
- [ ] 已更新根目录 README 的 Agent List 表格

## 相关链接

- [TRAE Agents 仓库定位与"文档即配置"模式](/concepts/00-introduction.md)
- [Git Commit Generator 参考实现分析](/concepts/02-git-commit-agent.md)
- [创建自定义 Agent 示例](/examples/create-agent.md)
- [TRAE Agents 仓库资源索引](/references/agents-source.md)
