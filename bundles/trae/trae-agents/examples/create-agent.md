---
type: Example
title: 创建自定义 Agent 示例
description: 从复制 _template 模板到完成配置并提交 PR 的完整自定义 Agent 创建流程
tags: [example, agents, create-agent, workflow, trae-agents, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/agents-source.md
    title: "Trae Agents 源码信源"
---

# 创建自定义 Agent 示例

本示例演示如何从零创建一个 TRAE 自定义 Agent 并提交到 trae-agents 仓库。

## 场景假设

假设你想创建一个 **Code Review Expert**（代码审查专家）Agent，它能根据代码变更自动进行代码审查，发现潜在问题并给出改进建议。

## 步骤一：准备工作

1. Fork `trae-community/trae-agents` 仓库到你的 GitHub 账号
2. Clone 你 fork 的仓库到本地
3. 创建新分支：`git checkout -b add-code-review-expert`
4. 阅读 `CONTRIBUTING.md` 了解贡献规范

## 步骤二：创建 Agent 目录

复制模板目录，重命名为你的 Agent 名称：

```bash
cp -r agents/_template agents/code-review-expert
```

目录名使用 kebab-case：`code-review-expert`。

## 步骤三：填写 YAML frontmatter

编辑 `agents/code-review-expert/README.md`，修改顶部的 YAML 部分：

```yaml
---
name: Code Review Expert
description: 根据代码变更自动进行代码审查，识别 Bug、安全漏洞、性能问题和代码风格问题，给出改进建议
---
```

## 步骤四：编写提示词（Prompt）

这是 Agent 最核心的部分。一个好的 Prompt 包含：

**角色定义**：
```
你是一位资深代码审查专家，拥有 10 年以上的软件开发经验。
你精通多种编程语言和框架，擅长发现代码中的潜在问题。
```

**审查维度**：
```
从以下维度审查代码：
1. 🐛 Bug 检测：逻辑错误、空指针、资源泄漏、边界条件
2. 🔒 安全漏洞：SQL 注入、XSS、认证绕过、敏感信息泄露
3. ⚡ 性能问题：N+1 查询、内存泄漏、不必要的循环、阻塞操作
4. 📐 代码风格：命名规范、函数长度、代码重复、注释质量
5. 🏗️ 架构设计：耦合度、单一职责、依赖倒置、可测试性
```

**输出格式**：
```
按以下格式输出审查结果：
## 总体评价
（1-2 句话概括代码质量）

## 问题列表
按严重程度排序（🔴 Critical > 🟡 Warning > 🔵 Suggestion）：
- [级别] 位置（文件:行号）：问题描述 → 建议方案

## 正面反馈
（至少提一个做得好的地方）
```

**行为约束**：
```
- 只审查提供的代码，不猜测未展示的部分
- 建议要具体可操作，不说"建议优化"这种空话
- 优先标注真正的问题，不过度挑剔风格偏好
- 如果代码质量良好，直接说明，不强行找问题
```

## 步骤五：配置工具

根据 Code Review Expert 的需求，勾选合适的工具：

```markdown
- [x] 文件编辑（读取代码文件进行审查）
- [x] 终端命令（执行 git diff、运行测试等）
- [ ] 网络搜索（本地代码审查不需要联网）
- [ ] 浏览器自动化（不需要）
- [ ] 其他智能体调用（独立完成审查）
```

MCP 服务：不需要特殊的 MCP 服务。

## 步骤六：列出协作智能体

```markdown
本 Agent 可独立工作，无强制协作需求。可选协作场景：
- 与 Git Commit Generator 配合：审查通过后自动生成 commit message
```

## 步骤七：编写使用示例

至少提供 2 个示例：

**示例 1：审查函数代码**
```
输入：
请审查以下 Python 函数：
def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

输出：
## 总体评价
代码存在严重的安全漏洞和资源管理问题，需要立即修复。

## 问题列表
- 🔴 第3行：SQL 注入漏洞，使用 f-string 直接拼接用户输入 → 使用参数化查询：conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
- 🔴 第2-4行：数据库连接未关闭，存在资源泄漏 → 使用 with 语句或 try/finally 确保连接关闭
- 🟡 第4行：返回值未做 None 检查，可能导致后续调用出错 → 添加 None 检查并给出明确提示

## 正面反馈
函数命名清晰，单一职责明确。
```

**示例 2：审查 PR diff**
（类似格式，提供一段 diff 输入和审查结果输出）

## 步骤八：添加配置建议

```markdown
## 配置建议

### 推荐模型
- GPT-4 / Claude 3.5 Sonnet（代码理解能力强）

### 高级设置
- 温度：0.2-0.4（代码审查需要准确性，低温度减少幻觉）
- 上下文长度：建议 16K 以上（大型 PR 的 diff 可能很长）
```

## 步骤九：填写相关资源和贡献者

```markdown
## 相关资源
- [Conventional Comments](https://conventionalcomments.org/) - 标准化审查评论格式
- [Google Code Review Guide](https://google.github.io/eng-practices/review/) - Google 代码审查指南

## 贡献者
- @your-github-username

## 许可证
MIT
```

## 步骤十：更新 Agent List 表格

在根目录 `README.md` 的 Agent List 表格中添加一行：

```markdown
| [Code Review Expert](agents/code-review-expert/README.md) | 根据代码变更自动进行代码审查 | ✅ Stable |
```

同时更新 `README.zh-CN.md` 中的对应表格。

## 步骤十一：提交 PR

提交 PR 时使用清晰的标题和描述：

```markdown
## New Agent: Code Review Expert

**Agent Name**: Code Review Expert
**Description**: 根据代码变更自动进行代码审查，识别 Bug、安全漏洞、性能问题和代码风格问题

### Checklist
- [x] Read CONTRIBUTING.md
- [x] Directory uses kebab-case naming
- [x] YAML frontmatter filled (name + description)
- [x] All 8 sections completed
- [x] Prompt is complete and tested
- [x] Tools configured following minimal permission principle
- [x] At least 2 usage examples provided
- [x] Configuration recommendations included (model + temperature)
- [x] Updated Agent List in both README.md and README.zh-CN.md
```

## 提交后流程

1. **24 小时内**：收到维护者确认
2. **审核中**：可能收到修改建议（如 Prompt 优化、补充示例等）
3. **调整后**：按建议修改并 push 到同一分支
4. **通过后**：PR 被合并，Agent 正式收录

## 设计建议

参考 git-commit-generator 的成功要素，创建 Agent 时注意：

1. **单一职责**：一个 Agent 做好一件事，不要做"万能助手"
2. **最小工具**：只勾选必要工具，避免过度授权
3. **具体示例**：至少 2 个覆盖主要场景的示例
4. **温度匹配**：准确性任务用低温（0.2-0.4），创造性任务用高温（0.7-0.9）
5. **格式约束**：明确规定输出格式，让结果可预测

## 相关链接

- [TRAE Agents 仓库定位与"文档即配置"模式](/concepts/00-introduction.md)
- [Agent 目录结构与模板规范](/concepts/01-agent-structure.md)
- [Git Commit Generator 参考实现分析](/concepts/02-git-commit-agent.md)
- [TRAE Agents 仓库资源索引](/references/agents-source.md)
