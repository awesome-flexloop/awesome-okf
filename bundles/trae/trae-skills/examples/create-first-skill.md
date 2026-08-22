---
type: Example
title: 创建第一个 Skill
description: 基于 _template 模板创建一个纯 Prompt 型 Skill 的完整步骤示例，从目录创建、SKILL.md 编写到本地测试和验证。
tags: [trae-skills, example, first-skill, _template, tutorial]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 示例目标

创建一个名为 `readme-checker` 的纯 Prompt 型技能，功能是检查项目 README.md 的完整性和规范性。这是一个入门级技能，不需要任何脚本。

## 步骤 1：创建目录结构

```bash
mkdir -p skills/readme-checker
```

## 步骤 2：创建 SKILL.md

在 `skills/readme-checker/` 目录下创建 `SKILL.md` 文件：

```markdown
---
name: readme-checker
description: 检查项目 README.md 文件的完整性和规范性，在用户要求"检查 README"、"review README"、"README 质量"或需要评估项目文档完整性时使用。检查 README 是否包含项目描述、安装说明、使用方法、配置说明、贡献指南、许可证等必要章节。
---

# README Checker

## Description

你是一个项目文档质量检查专家。你的任务是检查项目根目录下的 README.md 文件，评估其完整性和规范性，提供结构化的检查报告和改进建议。

## Usage Scenario

**触发场景：**
- 用户要求"检查 README"、"review README"、"README 质量"
- 用户要求评估项目文档完整性
- 用户需要改进 README 的建议

**不适用场景：**
- 不检查 README 以外的文档文件
- 不修改 README 内容（仅提供建议）
- 不检查非 Markdown 格式的文档

## Instructions

1. **定位文件**：在项目根目录查找 README.md（含 README.zh-CN.md 等双语文件）
2. **章节检查**：逐项检查以下必要章节是否存在：
   - 项目标题和简介（一句话描述项目做什么）
   - 安装说明（Installation / Getting Started）
   - 使用方法（Usage / Quick Start）
   - 配置说明（Configuration，如需要）
   - 贡献指南（Contributing，开源项目必需）
   - 许可证（License）
3. **质量评估**：对每个已有章节评估内容质量：
   - 描述是否清晰准确
   - 命令/代码示例是否可直接运行
   - 是否存在过时信息标记
4. **生成报告**：输出结构化检查报告，格式如下：
   - 总览：已有章节数/应有章节数，评分（0-100）
   - 缺失章节列表
   - 已有章节质量评价
   - 改进建议（按优先级排列）
5. **双语检查**：如果存在 README.zh-CN.md，检查中英文版本内容是否同步

## Examples

输入：项目根目录有 README.md
输出：
# README 检查报告
## 总览
- 已有章节：4/6
- 评分：65/100
## 缺失章节
- ⚠️ 贡献指南（Contributing）
- ⚠️ 许可证（License）
## 改进建议
1. [高] 添加 LICENSE 文件并在 README 中声明许可证
2. [中] 安装说明中缺少依赖版本要求
...
```

## 步骤 3：本地安装测试

将技能目录复制到项目级或全局级技能路径：

```bash
# 项目级安装
cp -r skills/readme-checker .trae/skills/

# 或全局级安装
cp -r skills/readme-checker ~/.trae/skills/
```

## 步骤 4：验证触发

在 TRAE 中新开会话，测试以下场景：

**正面测试**（应触发）：
- "帮我检查一下 README"
- "review 一下项目的 README 质量"
- "README 有没有缺什么"

**反面测试**（不应触发）：
- "帮我写一段代码"
- "检查一下 Python 语法错误"

## 步骤 5：端到端测试

1. 在一个有 README.md 的项目目录中打开 TRAE
2. 说"检查 README"
3. 验证 Agent 是否：
   - 正确读取 README.md
   - 按章节检查清单逐项评估
   - 输出结构化报告
   - 给出改进建议

## 步骤 6：迭代优化

根据测试结果调整 SKILL.md：
- 如果触发不准确 → 调整 description 和 Usage Scenario
- 如果输出格式不对 → 在 Examples 中给出更详细的示例
- 如果检查项遗漏 → 在 Instructions 中补充

## 常见问题

**Q: 技能没有被触发？**
A: 检查 description 是否包含明确的触发关键词。description 是 Agent 判断是否加载的唯一依据。

**Q: Agent 没有按步骤执行？**
A: 步骤编号要清晰，每步使用明确的动作动词。可在 Instructions 中强调"必须按以下步骤执行"。

**Q: 输出格式不统一？**
A: 在 Examples 或 Instructions 中给出明确的输出模板和格式要求。

## 相关概念

- [SKILL.md 格式规范](/concepts/01-skill-format.md)
- [纯 Prompt 型技能](/concepts/03-prompt-only-skills.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)
- [触发条件设计示例](/examples/trigger-condition-design.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)
- [带 Python 脚本的 Skill 示例](/examples/skill-with-python-script.md)
