---
type: Concept
title: AGENTS.md 开发契约
description: AGENTS.md 是 AI-native 项目中的 AI 开发契约文件，定义 AI Agent 应遵循的规则、工具映射和行为约束。superpowers-trae-init 通过 .trae/rules/superpowers.md 实现了这一契约，包含 4 条铁律、工具适配映射和触发器字典。
tags: [trae-templates, agents-md, ai-contract, superpowers, iron-rules, tool-mapping]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 什么是 AI 开发契约

传统项目有各种配置文件给工具链看：`package.json` 给 npm、`tsconfig.json` 给 TypeScript 编译器、`.eslintrc` 给 ESLint。而 **AI-native 项目还需要一种给 AI Agent 看的"配置文件"**——这就是 AGENTS.md 开发契约。

AGENTS.md 定义了 AI Agent 在项目中应遵循的行为规则、工具使用方式和质量门禁。它与 `.trae/rules/` 下的规则文件互补：
- **AGENTS.md**：放置在项目根目录，作为项目级 AI 行为规范的主入口
- **`.trae/rules/`**：放置模块化的规则片段，可被 AGENTS.md 引用

superpowers-trae-init 模板中的 `.trae/rules/superpowers.md` 就是 AI 开发契约的参考实现。

## 两种配置：机器配置 vs Agent 配置

| 维度 | 机器配置（传统配置文件） | Agent 配置（AGENTS.md/.trae/rules/） |
|------|------------------------|--------------------------------------|
| **目标读者** | 编译器、工具链、运行时 | AI Agent |
| **文件格式** | JSON/YAML/TOML（结构化） | Markdown（自然语言+结构化标签） |
| **约束方式** | 语法/类型/规则强制 | 指令/铁律/工作流约束 |
| **内容** | 依赖管理、编译选项、路径配置 | 工作流阶段、质量门禁、工具映射、技能路由 |
| **示例** | package.json、tsconfig.json | superpowers.md、AGENTS.md |

传统项目模板的 README.md 是给人类看的文档，而 AGENTS.md / `.trae/rules/` 是给 AI 看的指令——两者互补。

## 4 条铁律（Iron Rules）

superpowers.md 定义了 4 条不可违反的铁律，作为 AI 编码的质量门禁：

### 铁律 1：NO FIX WITHOUT ROOT CAUSE（禁止不查根因直接修复）

> 禁止在没有找到根因的情况下直接修复 Bug。必须执行 `systematic-debugging` 技能进行系统化调试，通过假设→插桩→复现→分析→修复→验证的科学流程定位根因。

**意义**：防止 AI "凭感觉"修复 Bug（如加 try-catch 吞异常、修改条件判断绕过问题），要求必须理解问题本质。

### 铁律 2：NO PRODUCTION CODE WITHOUT RED TEST（禁止测试失败前写生产代码）

> 禁止在没有失败测试的情况下编写生产代码。必须遵循 TDD 流程：先写失败测试（Red）→ 写代码使测试通过（Green）→ 重构（Refactor）。

**意义**：强制测试驱动开发，确保每一行生产代码都有对应的测试覆盖。这是 TDD 的核心循环在 AI 编码场景下的强制性转译。

### 铁律 3：NO BLIND MOCKING（禁止 Mock 行为，必须测试真实行为）

> 禁止在测试中盲目使用 Mock 对象。应优先测试真实行为和集成点，仅在外部依赖不可控时才使用 Mock，并明确 Mock 的契约。

**意义**：防止 AI 滥用 Mock 导致测试通过但实际功能不可用。Mock 应验证交互契约，而非伪造返回值让测试绿掉。

### 铁律 4：NO GUESSING THE OUTPUT（禁止未实际运行就宣布完成）

> 禁止在没有实际运行验证的情况下宣布任务完成。必须运行测试、启动服务、或执行验证命令来确认输出符合预期。

**意义**：这是防止 AI 幻觉（hallucination）的关键约束。AI 不能"觉得"代码是对的，必须通过实际运行来证明。

## 工具适配映射（Tool Adaptation Mapping）

AI Agent 有一套通用工具概念，但不同 IDE 的具体工具实现不同。superpowers.md 定义了从通用概念到 TRAE 特定工具的强制映射：

| 通用概念 | TRAE 工具 | 映射要求 |
|----------|-----------|----------|
| CLI 输出跟踪 / 任务列表 | **TodoWrite** | 必须使用 TodoWrite 跟踪任务进度，而非在终端输出 TODO 注释 |
| 子代理派发（spawn_agent） | **Task** 工具 | 使用 Task 派发子任务，必须两阶段审查：①Spec 对齐度审查 ②代码质量审查 |
| 本地知识库 / 持久记忆 | **manage_core_memory** | 使用 Core Memory 存储项目知识，而非创建本地 README 或笔记文件 |

### Task 两阶段审查

派发子代理时必须执行两阶段审查：
1. **Spec 对齐度审查**：子任务结果是否与需求规格一致
2. **代码质量审查**：代码是否符合规范、有无安全问题、是否经过测试

这防止了子代理"自由发挥"导致结果偏离目标。

## 触发器字典（Trigger Dictionary）

触发器字典将开发场景分为三类，每类对应一组应自动加载的技能。这与 trae-skills 中 SKILL.md 的 `description` 触发机制类似，但作用于项目级而非技能级。

### 第一组：架构与计划（Architecture & Planning）

| 触发器 | 对应技能 | 何时加载 |
|--------|----------|----------|
| brainstorming | 头脑风暴技能 | 需要设计方案、讨论架构、探索思路时 |
| writing-plans | 编写计划技能 | 需要制定实现计划、拆分子任务时 |
| when-stuck | 卡壳求助技能 | 遇到障碍不知道如何继续时 |
| simplification-cascades | 简化级联技能 | 代码过于复杂需要重构简化时 |

### 第二组：开发与审查（Development & Review）

| 触发器 | 对应技能 | 何时加载 |
|--------|----------|----------|
| subagent-driven-development | 子代理驱动开发 | 需要派发子任务并行开发时 |
| test-driven-development | TDD 技能 | 编写新功能时（先写测试） |
| testing-anti-patterns | 测试反模式技能 | 编写/审查测试时识别反模式 |
| requesting-code-review | 代码审查请求 | 完成开发后请求审查 |

### 第三组：排错与闭环（Debugging & Closure）

| 触发器 | 对应技能 | 何时加载 |
|--------|----------|----------|
| systematic-debugging | 系统化调试 | Bug 修复时（铁律1要求） |
| root-cause-tracing | 根因追踪 | 需要深入排查问题根因时 |
| condition-based-waiting | 条件等待 | 需要等待异步条件满足时 |
| verification-before-completion | 完成前验证 | 宣布完成前必须执行（铁律4要求） |

## Core Memory 集成

superpowers-trae-init 要求手动添加项目级核心记忆：

- **标题**：Superpowers 严格工作流约束
- **关键词**：`superpowers|workflow|tdd|debugging|skills`
- **内容**：4 条工作流约束（闭环流程、禁止猜测调试、真实执行技能、卡壳求助）

核心记忆的作用是：当 TRAE 新开会话时，通过关键词召回项目级约束，确保 4 条铁律在会话开始时就生效。

## `.trae/` 目录结构

superpowers-trae-init 引入的 `.trae/` 目录是 TRAE 项目的标准配置目录：

```
.trae/
├── rules/
│   └── superpowers.md      # 核心规则文件（4条铁律+映射+触发器）
└── skills/                 # 项目级技能目录
    ├── brainstorming/
    │   └── SKILL.md
    ├── writing-plans/
    │   └── SKILL.md
    ├── test-driven-development/
    │   └── SKILL.md
    ├── systematic-debugging/
    │   └── SKILL.md
    ├── remembering-conversations/
    │   ├── tool/           # TypeScript 工具实现
    │   ├── src/            # 13个 .ts 文件
    │   └── SKILL.md
    └── ...（25+ 个技能）
```

### 项目级 vs 全局级技能

- **项目级**（`.trae/skills/`）：仅当前项目可用，随项目版本控制
- **全局级**（`~/.trae/skills/`）：所有项目可用

superpowers-trae-init 的技能安装在项目级，因为它们定义的是项目特定的开发流程约束。

## remembering-conversations：代码级技能实现

`.trae/skills/` 下的技能不同于 trae-skills 社区技能——它们可以包含真正的可执行代码实现。remembering-conversations 是一个典型例子：

- **功能**：会话记忆索引与搜索
- **实现**：TypeScript 完整实现（13 个 .ts 文件）
- **核心能力**：
  - `install-hook`：安装会话结束钩子
  - `index-conversations`：索引历史对话（向量嵌入）
  - `search-conversations`：语义搜索历史对话
- **技术栈**：SQLite、向量嵌入、TypeScript

这说明 `.trae/skills/` 不仅是提示词包，还可以包含完整的工具实现。

## 如何定制 AI 开发契约

基于 superpowers-trae-init 的模式，为项目定制 AI 开发契约的步骤：

1. **复制 `.trae/` 目录**：从 superpowers-trae-init 复制 `.trae/` 到项目根
2. **添加核心记忆**：在 TRAE 中添加项目级核心记忆
3. **审查铁律**：根据团队规范调整 4 条铁律（如添加代码风格约束、安全规则等）
4. **调整触发器字典**：根据项目技术栈添加/删除技能路由
5. **添加项目特定规则**：在 `.trae/rules/` 下创建新的规则文件
6. **新开会话验证**：确保 TRAE 加载了规则并按约束执行

简单项目可以不使用完整 superpowers，仅在项目根目录放置 `AGENTS.md` 文件，定义最核心的约束即可。详见 [AGENTS.md 配置示例](../examples/agents-md-config.md)。

## 为什么 AGENTS.md 重要

1. **行为可预测**：明确的规则让 AI Agent 的行为更可预测，减少意外
2. **质量门禁**：铁律作为硬性约束，防止 AI 走捷径（不测试就提交、不查根因就修复）
3. **团队一致性**：所有团队成员使用同一套 AI 规则，代码质量和风格一致
4. **知识持久化**：通过 Core Memory 和 `.trae/rules/`，项目知识不因会话结束而丢失
5. **新成员快速上手**：新开发者（或新 AI 会话）可以立即了解项目规范

## 相关概念

- [工具与 DevOps 模板](06-tools-devops-templates.md)
- [五维分面分类体系](01-template-classification.md)
- [Trae Templates 简介](00-introduction.md)

## 相关内容

- [源码信源索引](../references/templates-source.md)
- [使用 superpowers-trae-init 初始化环境](../examples/use-superpowers-init.md)
- [AGENTS.md 配置示例](../examples/agents-md-config.md)
