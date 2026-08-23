---
okf_version: "0.2"
type: example
title: 创建自定义 Workspace
description: 定义和注册自定义 Workspace，配置专属系统提示词、工具集、技能包和路由规则，实现子 Agent 委派与专业领域任务处理
tags: [zleap-agent, example, workspace, agent, sub-agent, routing, tools, skills]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/workspace-pipeline.md
  - /concepts/agent-core-loop.md
  - /concepts/skill-package-system.md
sources:
  - id: zleap-agent-self
    resource: /references/zleap-agent-sources.md
    title: Zleap-Agent 源码参考
---

# 创建自定义 Workspace

## 场景说明

本示例演示如何在 Zleap Agent 中创建自定义 Workspace（工作空间）。Workspace 是 Zleap Agent 的核心概念，每个 Workspace 相当于一个具有专属系统提示词（persona）、工具集和技能包的子 Agent。Zleap 通过路由机制自动将用户请求分发到最合适的 Workspace 处理，也支持 Workspace 之间的委派（handoff）。

**前置条件**：
- 已完成 Zleap Agent 安装配置（参见 [安装配置 Zleap Agent](setup-zleap-agent.md)）
- 已构建所有包（`pnpm build`）
- TypeScript 开发环境（Node.js ≥ 22）
- 了解 Zleap Agent 的 Workspace 管线概念

## 完整代码示例

### 示例 1：通过代码注册自定义 Workspace

```typescript
// examples/custom-workspace.ts
// 演示：创建并注册一个代码审查专用 Workspace

import { WorkSpaceRegistry, type WorkSpaceDefinition, type WorkContext, type Artifact } from '@zleap/core';

// ── 步骤 1：定义 Workspace Handler ──
// Workspace Handler 是一个异步函数，接收 WorkContext 和 AbortSignal，
// 返回 Artifact（包含标题、摘要和可选数据）。

async function codeReviewHandler(context: WorkContext, signal: AbortSignal): Promise<Omit<Artifact, 'id' | 'workspaceId' | 'createdAt'>> {
  const { goal, availableTools, callTool, emit, skills, priorArtifacts } = context;

  // 发送进度通知（UI 会实时显示）
  emit({ kind: 'text', text: '🔍 正在分析代码审查请求...\n' });

  // 步骤 1：如果有 priorArtifacts，先了解已有上下文
  if (priorArtifacts.length > 0) {
    emit({ kind: 'text', text: `📎 接收到 ${priorArtifacts.length} 个前置产物，正在加载上下文...\n` });
  }

  // 步骤 2：使用可用工具执行任务
  // 检查是否有文件读取工具
  const readFileTool = availableTools.find(t => t.id === 'read_file');
  if (readFileTool) {
    emit({ kind: 'tool', name: 'read_file', phase: 'start', detail: '读取目标代码文件' });

    try {
      // 从 goal 中提取文件路径（实际应用中应使用更可靠的解析方式）
      const filePathMatch = goal.match(/[\w./-]+\.(ts|js|py|go|rs|java)/);
      if (filePathMatch) {
        const fileContent = await callTool('read_file', { path: filePathMatch[0] });

        emit({ kind: 'tool', name: 'read_file', phase: 'end', detail: `已读取 ${filePathMatch[0]}` });
        emit({ kind: 'text', text: `\n📝 文件内容已加载，开始审查...\n\n` });

        // 步骤 3：这里 LLM 会基于 system prompt + 文件内容 + 工具结果进行分析
        // Handler 本身通常不直接做 LLM 调用——LLM 调用由 TurnLoop 驱动
        // Handler 主要负责编排工具调用和组织工作流

        return {
          title: '代码审查报告',
          summary: `已完成对 ${filePathMatch[0]} 的代码审查，发现若干改进建议。`,
          data: {
            filePath: filePathMatch[0],
            reviewItems: [
              { severity: 'warning', line: 42, issue: '缺少错误处理', suggestion: '添加 try/catch' },
              { severity: 'info', line: 78, issue: '变量命名不清晰', suggestion: '使用更具描述性的名称' },
            ]
          }
        };
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      emit({ kind: 'tool', name: 'read_file', phase: 'end', detail: `读取失败: ${message}`, isError: true });
      return {
        title: '代码审查失败',
        summary: `无法读取目标文件: ${message}`,
        data: { error: message }
      };
    }
  }

  // 默认返回
  return {
    title: '代码审查',
    summary: '请提供需要审查的代码文件路径。',
  };
}

// ── 步骤 2：创建 Workspace 定义 ──
const codeReviewWorkspace: WorkSpaceDefinition = {
  id: 'code-review',
  label: '代码审查助手',
  description: '专门用于代码审查的 Workspace，能够读取代码文件、分析代码质量、发现潜在问题并提供改进建议。',
  handler: codeReviewHandler,
};

// ── 步骤 3：注册到 WorkSpaceRegistry ──
const registry = new WorkSpaceRegistry();
registry.register(codeReviewWorkspace);

// ── 步骤 4：查询已注册的 Workspace ──
console.log('已注册的 Workspace:');
for (const space of registry.list()) {
  console.log(`  - ${space.id}: ${space.label} (${space.description})`);
}

// 通过 ID 获取 Workspace
const retrieved = registry.get('code-review');
console.log(`\n查找 code-review: ${retrieved?.label ?? '未找到'}`);
```

### 示例 2：配置 Workspace 规格（通过 Seed/Avatar Profile）

在 Zleap 中，Workspace 的完整配置（包括 persona、工具白名单、路由卡片等）通常通过数据库中的 Avatar Profile 或默认 Seed 来定义。以下展示如何构建 Workspace 规格：

```typescript
// examples/workspace-spec.ts
// 演示：构建 WorkspaceSpec（运行时 Workspace 配置）

import {
  type WorkspaceSpec,
  defaultMainWorkspaceSpec,
  buildDefaultSeedWorkspaceDetails,
  workspaceView,
} from '@zleap/agent/workspaces';

// ── 方式 A：使用默认 Main Workspace ──
const mainSpec = defaultMainWorkspaceSpec();
console.log('=== 默认 Main Workspace ===');
console.log(`ID: ${mainSpec.id}`);
console.log(`Label: ${mainSpec.label}`);
console.log(`Kind: ${mainSpec.kind}`);
console.log(`工具数量: ${mainSpec.toolIds.length}`);
console.log(`路由提示 (when): ${mainSpec.when.slice(0, 100)}...`);
console.log(`Persona (前100字符): ${mainSpec.persona.slice(0, 100)}...`);

// ── 方式 B：从默认 Seed 构建所有内置 Workspace ──
const allDefaults = buildDefaultSeedWorkspaceDetails();
console.log('\n=== 默认 Seed 中的所有 Workspace ===');
for (const ws of allDefaults) {
  console.log(`  - [${ws.kind}] ${ws.id}: ${ws.label}`);
  console.log(`    when: ${ws.when.slice(0, 80)}...`);
  console.log(`    工具数: ${ws.toolIds.length}, 技能数: ${ws.skillIds?.length ?? 0}`);
}

// ── 方式 C：创建自定义 WorkspaceSpec ──
const dataAnalysisSpec: WorkspaceSpec = {
  id: 'data-analysis',
  label: '数据分析专家',
  kind: 'work',  // 'work' = 子空间（由 main 空间委派进入）
  icon: '📊',
  description: '擅长数据分析、统计计算和可视化的专业 Workspace',
  when: '当用户需要分析数据、计算统计指标、生成数据报告或进行数据可视化时使用。适用于CSV/JSON数据解析、趋势分析、汇总统计等任务。',
  notFor: '不适用于代码编写、网页搜索、文件系统操作以外的任务',
  persona: `你是一位资深数据分析师，擅长：
1. 数据清洗和预处理
2. 描述性统计分析
3. 趋势识别和异常检测
4. 数据可视化建议
5. 生成结构化分析报告

工作原则：
- 始终先了解数据结构再进行分析
- 对统计结果给出清晰的解释
- 注意数据偏差和样本量限制
- 使用 Markdown 表格呈现关键数据
- 分析完成后给出可操作的建议`,
  toolIds: [
    'read_file',       // 读取数据文件
    'write_file',      // 写出分析报告
    'run_command',     // 运行数据分析脚本
    'search_files',    // 查找数据文件
  ],
  status: 'ready',
  ui: {
    label: '数据分析',
    icon: '📊',
    accent: '#3b82f6',  // 蓝色主题
  },
};

// 生成 WorkspaceView（UI 展示用的轻量视图）
const dataAnalysisView = workspaceView(dataAnalysisSpec);
console.log('\n=== 自定义 Workspace 视图 ===');
console.log(JSON.stringify(dataAnalysisView, null, 2));
```

### 示例 3：Workspace 之间的委派（Handoff）

```typescript
// examples/workspace-handoff.ts
// 演示：Workspace 之间的任务委派机制

import type { WorkspaceHandoffRequest, WorkspaceResult } from '@zleap/core';

// Workspace 可以在返回结果中通过 handoffs 字段请求委派到其他 Workspace
// 这是 Zleap 实现多 Agent 协作的核心机制

async function researchHandler(context: WorkContext, signal: AbortSignal): Promise<Omit<Artifact, 'id' | 'workspaceId' | 'createdAt'>> {
  const { goal, callTool, emit } = context;

  emit({ kind: 'text', text: '🔍 正在进行信息检索...\n' });

  // 使用搜索工具收集信息
  const searchResult = await callTool('web_search', { query: goal });

  emit({ kind: 'text', text: '📋 信息收集完成，准备委派给写作 Workspace...\n' });

  // 返回结果时附带 handoff 请求，将任务委派给写作 Workspace
  const result: WorkspaceResult = {
    status: 'completed',
    summary: '已完成信息检索，收集到相关资料。',
    artifacts: [
      {
        kind: 'search_results',
        ref: 'search-output-1',
        description: '搜索到的相关网页和摘要',
        source: 'generated',
      }
    ],
    observations: [
      '搜索到 5 个高相关度结果',
      '主要信息来源为官方文档和技术博客',
    ],
    errors: [],
    suggestedNextSteps: [
      '基于收集的资料撰写完整报告',
      '添加图表和数据可视化',
    ],
    // 关键：请求委派到 writing Workspace
    handoffs: [
      {
        space: 'writing',
        task: '基于以下研究资料，撰写一份结构清晰的技术报告。',
        context: '已完成资料收集，包含官方文档和社区实践案例。',
        reason: '研究完成，需要专业写作能力将资料组织成报告。',
      } satisfies WorkspaceHandoffRequest,
    ],
  };

  return {
    title: '研究阶段完成',
    summary: result.summary,
    data: result,
  };
}

// WorkspaceResult 的 status 字段控制流程走向：
// - 'completed'：正常完成，可以交付结果或继续 handoff
// - 'failed'：失败，返回错误信息
// - 'blocked'：被阻塞（如等待外部资源）
// - 'needs_user_input'：需要用户补充信息
// - 'needs_approval'：需要用户审批（如危险操作）

const researchWorkspace: WorkSpaceDefinition = {
  id: 'research',
  label: '资料研究员',
  description: '负责信息检索和资料收集，完成后委派给写作 Workspace',
  handler: researchHandler,
};
```

### 示例 4：定义带技能包（Skill）的 Workspace

```typescript
// examples/workspace-with-skills.ts
// 演示：绑定技能包到 Workspace

import type { SkillDefinition } from '@zleap/core';

// SkillDefinition 定义了可复用的技能包
const codeReviewSkill: SkillDefinition = {
  id: 'skill-code-review-checklist',
  version: 1,
  label: '代码审查清单',
  description: '系统化的代码审查流程，覆盖安全性、性能、可维护性等维度',
  instructions: `## 代码审查流程

1. **安全性审查**：检查 SQL 注入、XSS、硬编码密钥等
2. **性能审查**：检查 N+1 查询、内存泄漏、不必要的计算
3. **可维护性审查**：检查命名、函数长度、复杂度、注释
4. **错误处理**：检查是否有适当的 try/catch 和边界条件
5. **测试覆盖**：检查是否有对应的单元测试

输出格式：使用分级标记 🔴严重 / 🟡警告 / 🔵建议`,
  toolIds: ['read_file', 'search_files', 'run_command'],
  lifecycle: 'per_turn',
  invocationPolicy: 'explicit_only',
  trustStatus: 'trusted',
  sections: [
    { id: 'security', title: '安全性审查', level: 2 },
    { id: 'performance', title: '性能审查', level: 2 },
    { id: 'maintainability', title: '可维护性审查', level: 2 },
  ],
};

// Workspace 可以声明 autoMountSkills: true 自动挂载相关技能
// 或通过 skillIds 显式绑定
const advancedCodeReviewSpec: WorkspaceSpec = {
  id: 'advanced-code-review',
  label: '高级代码审查',
  kind: 'work',
  description: '带系统化审查清单的高级代码审查 Workspace',
  when: '当用户需要深度代码审查、安全审计或代码质量评估时使用',
  persona: '你是一位资深代码审查专家，严格按照审查清单进行系统性检查。',
  toolIds: ['read_file', 'search_files', 'run_command', 'web_search'],
  skillIds: ['skill-code-review-checklist'],
  autoMountSkills: true,
  status: 'ready',
};

console.log('技能绑定 Workspace:');
console.log(`  Workspace: ${advancedCodeReviewSpec.label}`);
console.log(`  绑定技能: ${advancedCodeReviewSpec.skillIds?.join(', ')}`);
console.log(`  自动挂载技能: ${advancedCodeReviewSpec.autoMountSkills}`);
```

## 逐步解释

### 1. WorkSpaceDefinition 核心结构

每个 Workspace 由 `WorkSpaceDefinition` 定义：

```typescript
type WorkSpaceDefinition = {
  id: string;           // 唯一标识符，用于路由和 handoff
  label: string;        // 显示名称
  description?: string; // 描述信息
  handler: WorkSpaceHandler; // 处理函数
};

// WorkSpaceHandler 签名
type WorkSpaceHandler = (
  context: WorkContext,  // 运行时上下文（目标、工具、记忆、发射器等）
  signal: AbortSignal    // 取消信号
) => Promise<Omit<Artifact, 'id' | 'workspaceId' | 'createdAt'>>;
```

`WorkContext` 提供了 Handler 执行所需的一切：
- `goal`：当前任务目标（用户请求或委派任务描述）
- `availableTools`：可用工具描述符列表
- `callTool()`：调用工具的函数
- `emit()`：发送实时进度（文本/工具状态/审批请求）
- `skills`：挂载的技能包
- `queryMemory()`：查询长期记忆
- `priorArtifacts`：前置产物（来自上一个 Workspace 或用户输入）
- `workspaceRoot`：文件系统根目录

### 2. WorkspaceSpec vs WorkSpaceDefinition

Zleap 中有两层 Workspace 定义：

- **`WorkSpaceDefinition`**（core 层）：最精简的定义，包含 id、label、handler，用于通过 `WorkSpaceRegistry` 注册程序化的 Workspace Handler。
- **`WorkspaceSpec`**（agent 层）：运行时完整规格，包含 persona（系统提示词）、when（路由卡片）、toolIds（工具白名单）、ui 配置等。这些规格通常存储在数据库中，由默认 Seed 初始化，通过 Web UI 管理。

两层之间的关系：`WorkspaceSpec` 描述了"这个空间是什么样的"（提示词、工具、路由规则），`WorkSpaceDefinition` 提供了"这个空间如何执行工作"（handler 逻辑）。简单场景下，Main Workspace 的 handler 直接驱动 LLM TurnLoop，不需要自定义 handler；复杂场景下可以编写自定义 handler 来编排多步工作流。

### 3. Main Workspace 与 Work 子空间

Workspace 有两种 kind：
- **`main`**：常驻主控空间（runtime id 为 `session`），负责接收用户请求、路由决策、汇总结果。一个 Agent 只有一个 main 空间。
- **`work`**：子工作空间，由 main 空间通过 handoff 委派进入，专注于特定类型任务（如代码审查、数据分析、文档写作）。

路由机制：当用户发送消息时，Kernel Router 会根据每个 Workspace 的 `when` 字段（路由卡片）判断应该进入哪个空间。main 空间是默认入口，它可以自行处理简单请求，或将复杂任务委派给 work 子空间。

### 4. Workspace 注册表

`WorkSpaceRegistry` 是 Workspace 的内存注册表：

```typescript
class WorkSpaceRegistry {
  register(definition: WorkSpaceDefinition): void;  // 注册
  get(id: string): WorkSpaceDefinition | undefined;   // 按 ID 查询
  list(): WorkSpaceDefinition[];                      // 列出所有
}
```

注册是幂等的吗？——不是。如果重复注册相同 id 会覆盖之前的定义（使用 `Map.set`）。

### 5. Handoff 委派机制

Workspace 之间通过 `handoffs` 数组实现任务委派：

```typescript
type WorkspaceHandoffRequest = {
  space: string;    // 目标 Workspace ID
  task: string;     // 委派的任务描述
  context?: string; // 上下文信息（前序工作的总结）
  reason?: string;  // 委派原因（用于日志和调试）
};
```

委派流程：
1. 当前 Workspace 完成自己的工作后，在 `WorkspaceResult.handoffs` 中添加委派请求
2. TurnLoop 接收到 handoff 请求后，创建新的 WorkStep，切换到目标 Workspace
3. 目标 Workspace 的 handler 接收到 `context` 和 `priorArtifacts`，继续执行
4. 如果目标 Workspace 也有 handoff，可以链式委派形成多步工作流

### 6. 工具与技能绑定

Workspace 通过 `toolIds` 控制可用工具集，通过 `skillIds` 绑定技能包：

- **toolIds**：工具白名单，只有列表中的工具才能在此 Workspace 中被调用。这是安全边界——例如，数据分析 Workspace 不应有执行系统命令的工具。
- **skillIds**：技能包列表，技能包提供可复用的指令集和流程模板。
- **autoMountSkills**：是否自动挂载匹配的技能（基于语义检索）。

### 7. 默认 Seed 与 Workspace 持久化

Zleap Agent 的内置 Workspace 不是硬编码在源码中的，而是通过 `createDefaultSuperAgentSeed()` 生成默认种子数据，首次启动时写入数据库。之后用户可以通过 Web UI 自定义 Workspace（修改 persona、工具集、路由规则等），这些修改存储在数据库中，运行时通过 `buildWorkspaceDetailsFromAvatarProfile()` 加载。

这意味着：
- 代码层面注册的 `WorkSpaceDefinition` 主要用于提供自定义 handler 逻辑
- Workspace 的提示词、工具白名单、路由规则等配置主要通过数据库/UI 管理
- 默认 Seed 保证了开箱即用的体验

## 输出结果

运行示例代码后：

**示例 1 输出**：
```
已注册的 Workspace:
  - code-review: 代码审查助手 (专门用于代码审查的 Workspace...)

查找 code-review: 代码审查助手
```

**示例 2 输出**：
```
=== 默认 Main Workspace ===
ID: session
Label: Zleap
Kind: main
工具数量: 12
路由提示 (when): 当用户的请求涉及通用对话、问题回答、任务规划、信息查询或其他专业领域无法直接处理时...
Persona (前100字符): You are Zleap, a highly capable AI assistant...

=== 默认 Seed 中的所有 Workspace ===
  - [main] session: Zleap
    when: 当用户的请求涉及通用对话...
    工具数: 12, 技能数: 0
  - [work] coding: 编程助手
    when: 当用户需要编写、调试、审查代码...
    工具数: 8, 技能数: 0
  ...
```

## 注意事项

1. **Handler 中的异步操作必须支持取消**：始终检查 `signal.aborted` 或将 `signal` 传递给底层 API（如 fetch 的 signal 选项），以支持优雅中断。

2. **emit() 是非阻塞的**：`emit()` 用于发送实时进度更新，不要在 emit 后假设 UI 已经处理了消息。它是"发后即忘"的。

3. **工具调用的错误处理**：`callTool()` 可能抛出异常，务必使用 try/catch 包裹，并通过 `emit({ kind: 'tool', phase: 'end', isError: true })` 通知 UI。

4. **Workspace ID 命名约定**：使用 kebab-case（如 `code-review`、`data-analysis`），避免特殊字符。Main 空间的 canonical id 是 `main`，runtime id 是 `session`。

5. **Handler 不应直接做 LLM 调用**：在 Zleap 的架构中，LLM 调用由 TurnLoop 在 Workspace 进入后自动驱动。自定义 Handler 主要用于编排工具调用和工作流。对于纯对话场景，只需配置 WorkspaceSpec 的 persona，不需要自定义 handler。

6. **Handoff 链式委派的深度控制**：避免过长的 handoff 链（建议不超过 3-4 跳），否则用户等待时间过长且错误恢复困难。每个 handoff 应携带足够的 context，避免信息丢失。

7. **toolIds 是安全边界**：严格限制每个 Workspace 的工具集。例如，涉及外部通信的 Workspace 不应有文件写入工具，数据分析 Workspace 不应有系统命令执行工具。

8. **when 字段的写法影响路由质量**：`when` 字段是给路由模型看的"分类广告"，应清晰描述适用场景和不适用场景（`notFor`），避免模糊表述。
