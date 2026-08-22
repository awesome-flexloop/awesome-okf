---
type: Example
title: 触发条件设计示例
description: 通过对比社区技能中 daily-hot-news、git-commit-generator、kz-article-deep-analysis、video-to-keyframes 的触发条件写法，展示正面触发词、反面排除条件和约束条款的设计模式。
tags: [trae-skills, example, trigger-condition, when-to-use, description]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 触发条件的重要性

SKILL.md frontmatter 中的 `description` 字段和正文中的触发场景描述是 Agent 决定何时加载技能的唯一依据。触发条件的精确性比步骤详细度更重要——步骤写得粗略 Agent 还能自行推理，触发条件模糊则 Agent 根本不会加载。

触发条件设计的三要素：
1. **正面触发词**：用户说什么时触发
2. **反面排除条件**：什么场景不适用
3. **能力边界/约束条款**：能做什么/不能做什么

## 示例 1：关键词穷举型（daily-hot-news）

daily-hot-news 采用正面关键词穷举 + 反面场景排除的模式：

### description 字段

> 聚合全网热门新闻热榜，支持微博热搜、百度热搜、知乎热榜、头条热榜、哔哩哔哩热门、抖音热搜等平台。在用户询问"今日热搜""新闻热榜""今天有什么热点""全网热搜"等热榜相关话题时触发。

### Usage Scenario 中的触发词

**正面触发关键词**（穷举 7 个）：
- "今日热搜"
- "新闻热榜"
- "今天有什么热点"
- "全网热搜"
- "热门新闻"
- "今日新闻"
- "热榜"

**反面排除条件**：
> 不适用于历史新闻查询或特定领域深度分析。

**设计分析**：
- 优点：关键词穷举充分，覆盖用户可能的多种表达方式
- 优点：反面排除明确，避免在深度分析场景误触发
- 适用场景：功能边界清晰、用户意图表达多样的技能

## 示例 2：场景描述型（git-commit-generator）

git-commit-generator 采用场景描述而非关键词穷举：

### description 字段

> 基于代码变更（git diff）生成符合 Conventional Commits 规范的标准化提交信息。

### Usage Scenario 中的触发场景（3 种）

1. **用户主动要求**：用户要求"写 commit message"/"生成 commit"
2. **用户状态查询**：用户问"我改了什么"
3. **Agent 主动提议**：Agent 刚完成代码变更，需要提议 commit message

**设计分析**：
- 优点：覆盖了"用户要求""用户询问""Agent 主动"三种触发时机
- 优点：场景描述比关键词更灵活，能匹配语义相近的表达
- 适用场景：触发场景是具体行为而非特定关键词的技能

## 示例 3：功能+排除型（kz-article-deep-analysis）

kz-article-deep-analysis 明确定义适用范围和不适用范围：

### description 字段

> 深度解读非学术类文章（博客、随笔、评论），抽取核心议题与核心主张，输出结构化分析报告。

### 关键触发描述

**适用**：非学术类文章（博客、随笔、评论）
**不适用**：学术论文、书籍

**设计分析**：
- 优点：通过文章类型定义边界，清晰明确
- 优点：排除容易混淆的场景（学术论文 vs 博客文章）
- 适用场景：功能有明确适用/不适用对象的技能

## 示例 4：动词短语型（video-to-keyframes）

video-to-keyframes 采用动词短语穷举（8 个）：

### 触发关键词

- "抽帧"
- "拆帧"
- "关键帧"
- "候选关键帧"
- "镜头拆分"
- "转场点"
- "分段"
- "分镜初筛"

**设计分析**：
- 优点：全部是视频处理领域的专业动词/名词短语，精确匹配
- 优点：覆盖从用户通俗说法（"抽帧""拆帧"）到专业术语（"转场点""分镜初筛"）
- 适用场景：领域专有词汇明确的技能

## 示例 5：多条件组合型（wechat-mini-program-development）

wechat-mini-program-development 列出 4 种触发场景：

1. 用户要求创建微信小程序项目
2. 需要小程序开发帮助
3. 需要 HTTP 请求封装
4. 需要 API 管理

**设计分析**：
- 优点：覆盖了从项目创建到具体功能开发的多种需求
- 优点：既包含宏观需求（"创建小程序"）也包含微观需求（"请求封装"）
- 适用场景：覆盖开发全流程的脚手架型技能

## 约束条款设计示例

好的触发条件还包含约束条款，防止 Agent 越界操作：

### cloudbase 约束条款

- 不得编造 CloudBase API 路径或 MCP 工具参数
- 不得在前端代码中暴露 API key/service_role 凭证
- 同一路径 2-3 次失败后停止并重路由

### trae-claw-install 约束条款

- 复用仓库脚本和文档，不创建并行流程
- 不写入真实密钥
- Windows 优先在 WSL2 Linux 文件系统内执行

**设计分析**：
- 约束条款告诉 Agent "什么绝对不能做"
- 安全相关约束（不暴露密钥）和质量相关约束（不编造参数）同等重要
- 失败处理约束（2-3 次后停止）防止无限循环

## 设计模板

综合以上示例，推荐的触发条件设计模板：

```markdown
## Usage Scenario

**触发场景（当用户说/需要以下内容时加载本技能）：**
- [关键词/短语1]
- [关键词/短语2]
- [场景描述1]
- [场景描述2]

**不适用场景（以下情况不要加载本技能）：**
- [排除场景1]
- [排除场景2]

**约束条款（必须遵守）：**
- [禁止事项1]
- [禁止事项2]
- [失败处理策略]
```

## 正反案例对比

### ❌ 差的触发条件

```yaml
description: Git 工具
```

问题：
- 没有说明做什么（提交信息生成？分支管理？冲突解决？）
- 没有说明何时使用
- Agent 无法判断是否应该加载

### ✅ 好的触发条件

```yaml
description: 基于代码变更（git diff）生成符合 Conventional Commits 规范的标准化提交信息。在用户要求"写 commit message"/"生成 commit"、询问"我改了什么"、或 Agent 完成变更需要提议提交信息时使用。
```

优点：
- 明确功能：基于 git diff 生成 Conventional Commits 格式的提交信息
- 穷举场景：用户要求、用户询问、Agent 主动三种时机
- Agent 能精确判断加载时机

## 验证触发条件的方法

1. **正面测试**：列出 5-10 种用户可能的表达方式，确保都能触发
2. **反面测试**：列出 5-10 种不应触发的场景，确保不会误触发
3. **边界测试**：测试模糊场景（如"git 操作"这种宽泛需求），判断是否合理
4. **迭代优化**：根据实际使用中的漏触发/误触发案例调整 description

## 相关概念

- [SKILL.md 格式规范](/concepts/01-skill-format.md)
- [纯 Prompt 型技能](/concepts/03-prompt-only-skills.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)
- [创建第一个 Skill](/examples/create-first-skill.md)
