---
type: spec
title: "TRAE Agents 源码事实清单"
---

# TRAE Agents 源码事实清单

## 项目基本信息

- F-001: 项目为社区维护的 TRAE 自定义智能体配置集合，采用 MIT License。来源：README.md
- F-002: 项目横幅图片为 `./assets/image/Agents.gif`。来源：README.md
- F-003: 提供中英文双语切换：English 链接 ./README.md，中文链接 ./README.zh-CN.md。来源：README.md
- F-004: 项目明确区分智能体配置和 MCP Servers（工具），提示寻找 MCP 工具的用户查看 `../trae-mcp`。来源：README.md
- F-005: 根目录包含 README.md（英文）、README.zh-CN.md（中文）、CONTRIBUTING.md、CONTRIBUTING.zh-CN.md、LICENSE、.gitignore 文件，以及 agents/、assets/image/、.github/ISSUE_TEMPLATE/ 目录。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-agents\`
- F-006: README 底部包含 Star History 图表（使用 star-history.com API）和免责声明（仅供社区交流学习，生产环境需充分测试）。来源：README.md

## 智能体配置模型

- F-007: README 定义每个智能体包含 4 项配置：📋 名称（Name）、💬 提示词（Prompt）、🛠️ 工具（Tools，含 MCP 服务和内置工具）、🤝 协作（其他可调用智能体）。来源：README.md
- F-008: 项目列出 4 个智能体示例类型：Code Review Expert、Documentation Assistant、Debug Expert、Git Assistant。来源：README.md
- F-009: README 描述了 4 步使用流程：Browse Agents → View Configuration Details → Create in TRAE（打开 TRAE→进入智能体管理→填写配置→保存测试）→ Adjust and Optimize。来源：README.md
- F-010: 内置工具清单包含 5 项可勾选工具：文件编辑、终端命令、网络搜索、浏览器自动化、其他智能体调用。来源：README.md

## 智能体列表

- F-011: 当前智能体列表表格中仅有 1 个正式智能体：`git-commit-generator`（状态 ✅ Stable），另有一行"(To be added)"占位，表示仓库处于初始化阶段。来源：README.md
- F-012: agents/ 目录下有两个子目录：`_template/`（模板）和 `git-commit-generator/`（正式智能体）。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-agents\agents\`

## 智能体模板

- F-013: `agents/_template/README.md` 使用 YAML frontmatter（name、description）定义元数据，结构包含 8 个章节：基本信息、提示词（Prompt）、工具配置（MCP 服务 + 内置工具勾选清单）、可协作智能体、使用示例（至少2个）、配置建议（模型选择+高级设置）、相关资源、贡献者、许可证。来源：_template/README.md
- F-014: 模板中内置工具勾选清单为 5 项复选框（- [ ]）：文件编辑、终端命令、网络搜索、浏览器自动化、其他智能体调用。来源：_template/README.md
- F-015: 模板推荐模型为 GPT-4/Claude，温度设置 0.7。来源：_template/README.md

## Git Commit Generator 智能体

- F-016: git-commit-generator 智能体名称为 `Git Commit Generator`，功能为根据代码变更自动生成符合 Conventional Commits 规范的提交信息。来源：git-commit-generator/README.md
- F-017: Prompt 定义了 11 种 Conventional Commits 类型：feat、fix、docs、style、refactor、perf、test、build、ci、chore、revert。来源：git-commit-generator/README.md
- F-018: Prompt 规定提交信息格式为 `<type>(<scope>): <subject>`，要求：祈使语气、首字母小写、末尾不加句号、主题行 50 字符以内、正文每行 72 字符以内。来源：git-commit-generator/README.md
- F-019: Prompt 规定 5 条重要原则：准确性优先、简洁明了、遵循规范、建设性建议（多个不相关变更建议拆分）、上下文感知。来源：git-commit-generator/README.md
- F-020: Prompt 包含 4 个示例：文档更新（docs）、新功能开发（feat(auth)）、Bug 修复（fix(user-service)）、重构含 BREAKING CHANGE（refactor(api)）。来源：git-commit-generator/README.md
- F-021: 工具配置中仅勾选"终端命令"（用于执行 git diff），不勾选文件编辑/网络搜索/浏览器自动化/其他智能体调用；MCP 服务标注"不需要特殊的 MCP 服务"，可选配置 filesystem MCP。来源：git-commit-generator/README.md
- F-022: 推荐模型为 GPT-4/Claude 3.5/Gemini Pro，温度 0.3-0.5（偏重准确性），上下文长度 4K 足够。来源：git-commit-generator/README.md

## Issue 模板

- F-023: `.github/ISSUE_TEMPLATE/agent_request.md` 为 Agent Request 模板，标题前缀 `[Agent]`，标签 `enhancement`，字段包括：Agent Name、Description、Status、Documentation、Usage Scenario、Proposed Instructions（可选）、Example Inputs/Outputs、Additional Context。来源：agent_request.md
- F-024: `.github/ISSUE_TEMPLATE/bug_report.md` 为 Bug Report 模板，标题前缀 `[BUG]`，标签 `bug`，字段包括：Bug 描述、Agent Name、复现步骤、预期行为、实际行为、示例输入/输出、截图、环境信息（TRAE 版本/OS/Agent 版本）、附加上下文。来源：bug_report.md

## 贡献流程

- F-025: 贡献步骤为 6 步：阅读 CONTRIBUTING.md → Fork 仓库创建新分支 → 在 agents/ 下创建智能体目录 → 按模板提供完整配置 → 更新 Agent List 表格 → 提交 PR。来源：README.md
