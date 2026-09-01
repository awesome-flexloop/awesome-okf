---
type: spec
title: "trae-mcp 源码事实清单"
---

# trae-mcp 源码事实清单

## 项目信息

- F-001: 项目位于 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-mcp\`，是 TRAE IDE 的社区维护 MCP（Model Context Protocol）服务器集合，采用 MIT 许可证。
- F-002: 项目根目录包含 `README.md`、`README.zh-CN.md`、`CONTRIBUTING.md`、`CONTRIBUTING.zh-CN.md`、`LICENSE`、`.gitignore`。
- F-003: 项目包含 `assets/images/MCP.gif` 作为 MCP Banner 图片。
- F-004: README.md 说明项目主要托管 MCP Servers（Tools），Skills（SOPs）在 TRAE Agent Skills 仓库。
- F-005: README.md 引用链接 `./README-skills.md` 指向 Skills 仓库（该文件在仓库中不存在）。

## MCP 概念

- F-006: MCP 全称为 Model Context Protocol，是 Anthropic 推出的开放标准协议，用于标准化 AI 模型与外部系统的连接方式。
- F-007: README.md 将 MCP 比喻为 AI 模型的"感官"和"四肢"，赋予 AI 三种能力：①操作工具（执行命令行、发送消息、管理代码仓库）②读取数据（访问本地文件、查询数据库、阅读文档）③连接服务（与 Slack、GitHub、Google Drive 等外部平台交互）。
- F-008: 在 TRAE 中，配置的 MCP 服务器作为 agent 可调用的 Tools，agent 可根据任务需求自动选择并执行这些工具。

## MCP 配置格式

- F-009: TRAE 中添加 MCP 服务器的路径为：Settings → MCP → Add → Manually Add。
- F-010: MCP 配置为 JSON 格式，顶层为 `mcpServers` 对象，key 为 MCP 名称，value 包含 `command`（启动命令）、`args`（命令参数数组）、`env`（环境变量对象）。
- F-011: 本地构建的 MCP 配置示例：`{"mcpServers":{"your-mcp-name":{"command":"node","args":["/absolute/path/to/build/index.js"],"env":{"API_KEY":"your-api-key"}}}}`。
- F-012: 使用方式：保存配置后返回 TRAE 聊天界面，使用 Builder with MCP 或自定义 agent 即可在对话中调用新添加的 MCP。

## 目录结构

- F-013: MCP 文件存放在 `mcp/` 目录下，每个 MCP 为一个独立子目录。
- F-014: 当前 mcp/ 目录包含 3 个子目录：`_template/`（模板）、`cloudbase/`、`git-commit-generator/`。
- F-015: `.github/ISSUE_TEMPLATE/` 下包含两个 Issue 模板：`bug_report.md`、`skill_request.md`。

## MCP 模板（_template）

- F-016: `mcp/_template/SKILL.md` 为 MCP 技能模板，frontmatter 包含 `name` 和 `description` 字段。
- F-017: 模板的 SKILL.md 章节结构为：`# Skill Name` → `## Description` → `## Usage Scenario` → `## Instructions`（编号步骤）→ `## Examples (Optional)`，与 trae-skills 的 _template 结构完全一致。

## CloudBase MCP

- F-018: `mcp/cloudbase/` 目录仅包含 `README.md` 一个文件，无实际 MCP 服务器代码。
- F-019: CloudBase MCP 为腾讯云开发 MCP 服务器，npm 包名为 `@cloudbase/cloudbase-mcp`。
- F-020: CloudBase MCP 能力范围覆盖：AI 模型、认证（auth）、NoSQL/PostgreSQL 数据库、云函数、存储（storage）、CloudRun、微信小程序工具。
- F-021: CloudBase MCP 状态为 Ready（npm 包形式，通过 Trae 手动 MCP 配置使用）。
- F-022: CloudBase MCP 配置：`{"mcpServers":{"cloudbase-mcp":{"command":"npx","args":["-y","@cloudbase/cloudbase-mcp@latest"],"env":{}}}}`。
- F-023: 首次使用时，服务器会打开浏览器登录/环境选择流程。
- F-024: 文档链接：IDE 设置文档 https://docs.cloudbase.net/ai/cloudbase-ai-toolkit/ai-agent-plugins，源码 https://github.com/TencentCloudBase/CloudBase-AI-Toolkit，Open Plugin 仓库 https://github.com/TencentCloudBase/cloudbase-plugin。
- F-025: README.md 中 MCP Server List 表格标注 CloudBase 状态为 ✅ Ready，其余标注"To be added"和 🚧 状态。

## git-commit-generator MCP

- F-026: `mcp/git-commit-generator/` 目录结构与 trae-skills 中同名 skill 完全相同，包含：`SKILL.md`、`examples/input.md`、`examples/output.md`、`templates/commit-message.txt`、`resources/conventional-commits-types.md`。
- F-027: 该目录下无实际 MCP 服务器实现代码（无 index.js/build/目录等），内容与 skills 仓库的 git-commit-generator 完全一致，本质上是一个 Skill 而非 MCP Server。
- F-028: SKILL.md frontmatter：name 为 `git-commit-generator`，description 为"基于代码变更（diffs）生成符合 Conventional Commits 规范的清晰、标准化 git commit 信息"。
- F-029: SKILL.md 指令步骤：①分析变更（读取 git diff、确定 scope、参考 conventional-commits-types.md 确定 type）②构造提交信息（遵循 commit-message.txt 模板：`<type>(<scope>): <subject>`，祈使语气，无句号，50字符以内；正文说明 what/why，使用 bullet points）③输出格式（代码块，多逻辑变更建议拆分多个 commit）。
- F-030: `templates/commit-message.txt` 定义的提交信息模板结构为：`<type>(<scope>): <subject>` + 空行 + `<body>` + 空行 + `<footer>`。
- F-031: `resources/conventional-commits-types.md` 定义 11 种 Conventional Commits 类型：feat（新功能）、fix（Bug修复）、docs（文档）、style（格式/不影响代码含义）、refactor（重构）、perf（性能改进）、test（测试）、build（构建系统/依赖）、ci（CI配置）、chore（杂项/不修改src或test）、revert（回退）。
- F-032: `examples/input.md` 示例输入为 README.md 中一行文字的简单修改 diff。
- F-033: `examples/output.md` 示例输出为 `docs: update quickstart instructions in README\n\nRefine the cloning step for better clarity.`。
- F-034: SKILL.md 包含两个示例：①简单文档更新（docs 类型）②多文件功能新增（feat(auth) 类型，带 bullet points 正文）。

## Issue 模板

- F-035: `.github/ISSUE_TEMPLATE/bug_report.md` 为 Bug 报告模板，标题格式 `[BUG] <Skill Name>: <Short Description>`，标签 `bug`，表单字段：Skill Name、Describe the bug、To Reproduce、Expected behavior、Screenshots/Logs。
- F-036: `.github/ISSUE_TEMPLATE/skill_request.md` 为 MCP 请求模板（注意 about 字段写"Suggest a new MCP server for TRAE"，但 name 为"MCP Request"，与 skills 仓库的 skill_request 模板类似），标题格式 `[MCP] <MCP Name>`，标签 `enhancement`，表单字段：MCP Name、Description、Status、Documentation、Usage Scenario、Proposed Instructions (Optional)、Example Inputs/Outputs。

## 学习资源

- F-037: README.md 列出 3 个 MCP 学习资源：MCP 官方文档 https://modelcontextprotocol.io/、Anthropic MCP 公告 https://www.anthropic.com/news/model-context-protocol、MCP 中文快速入门指南 https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide。
- F-038: README.md 底部包含 Star History 图表链接（star-history.com SVG）。
- F-039: README.md 链接指向 TRAE 官网 https://www.trae.ai/ 和 TRAE MCP 文档 https://docs.trae.ai/ide/model-context-protocol。
