---
type: Concept
title: Tool 工具系统
description: Tool 注册表管理 AI 可调用的工具，内置 discover_commands、execute_command、browser_fetch 等工具，支持自定义扩展
tags: [jupyterlite-ai, tool, function-calling, tools]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
  - id: tools
    resource: /references/built-in-tools.md
    title: 内置 AI 工具参考
---

# Tool 工具系统

Tool 系统使 AI 代理能够通过 Function Calling 与 JupyterLab 环境交互。`IToolRegistry` 管理所有可用工具，内置 5 个工具，支持第三方扩展注册自定义工具。

## Tool 注册表

`ToolRegistry` 实现 `IToolRegistry` 接口：

```typescript
interface IToolRegistry {
  readonly tools: Record<string, ITool>;
  readonly namedTools: INamedTool[];
  readonly toolsChanged: ISignal<IToolRegistry, void>;
  add(name: string, tool: ITool): void;
  get(name: string | null): ITool | null;
  remove(name: string): boolean;
}
```

### 设计要点

- `tools` getter 返回浅拷贝，防止外部直接修改内部状态
- `add()` / `remove()` 操作后触发 `toolsChanged` 信号
- `get(null)` 返回 `null`，避免空值错误
- 工具类型 `ITool` 直接使用 Vercel AI SDK 的 `Tool` 类型

## 工具定义格式

工具使用 Vercel AI SDK 的 `tool()` 函数创建，配合 Zod 定义输入 Schema：

```typescript
import { tool } from 'ai';
import { z } from 'zod';

const myTool = tool({
  metadata: { title: 'My Tool' },  // UI 显示标题
  description: '工具功能描述',     // LLM 看到的描述
  inputSchema: z.object({
    param1: z.string().describe('参数1描述'),
    param2: z.number().optional().describe('可选参数2')
  }),
  execute: async (input) => {
    // 工具执行逻辑
    return { success: true, result: '...' };
  }
});
```

## 内置工具

| 工具名 | 创建函数 | 功能 |
|--------|---------|------|
| `discover_commands` | `createDiscoverCommandsTool(commands)` | 搜索/列出 JupyterLab 命令 |
| `execute_command` | `createExecuteCommandTool(commands)` | 执行 JupyterLab 命令 |
| `browser_fetch` | `createBrowserFetchTool()` | 浏览器 HTTP GET 获取 URL |
| `discover_skills` | `createDiscoverSkillsTool(skillRegistry)` | 列出可用 AI 技能 |
| `load_skill` | `createLoadSkillTool(skillRegistry)` | 加载技能定义或资源 |

### discover_commands

搜索 JupyterLab 命令系统中的所有可用命令：

- 支持多词模糊搜索（空格分隔，每个词都要匹配）
- 字段权重：label(4) > caption(3) > id(2) > description(1)
- 返回命令的 id、label、caption、description 和参数 schema
- AI 使用此工具先发现可用命令，再选择执行

### execute_command

执行指定的 JupyterLab 命令：

- 接收 `commandId` 和可选 `args` 参数
- 命令不存在时返回错误信息，提示使用 `discover_commands`
- 返回 Widget 结果时序列化为 `{id, title}` 避免复杂对象
- 其他对象尝试 JSON 序列化
- 支持用户审批机制（见下文）

### browser_fetch

从浏览器发起 HTTP GET 请求：

- 字符数限制：默认 20000，最大 100000
- 超时：默认 20 秒，最大 120 秒
- 流式读取响应，达到上限后取消
- 仅支持 http/https 协议
- 返回结构化结果（状态码、Content-Type、截断标记等）
- 受浏览器 CORS/CSP 策略限制

### discover_skills / load_skill

技能系统交互工具：

- `discover_skills`：列出所有可用技能，支持搜索
- `load_skill`：加载指定技能的指令或资源文件
- 资源路径有安全校验（禁止绝对路径和 `..` 遍历）

## 工具审批机制

敏感命令可以配置需要用户审批后才能执行：

```typescript
// 创建审批策略
const approvalPolicy = createExecuteCommandApprovalPolicy(settingsModel);

// 在 Vercel AI SDK 中使用
const result = await generateText({
  model,
  tools: selectedTools,
  toolApproval: approvalPolicy,  // 返回 'user-approval' 时暂停等待
  // ...
});
```

配置审批命令列表：

```typescript
// 在 AI 设置中
config.commandsRequiringApproval = [
  'notebook:delete-cell',
  'docmanager:delete-file'
  // ... 其他需要确认的命令
];
```

审批流程：

```
LLM 返回 tool_call (execute_command)
  → AgentManager 检查审批策略
    → 需要审批：发出 tool_approval_request 事件，暂停执行
      → UI 展示审批对话框
        → 用户 approveToolCall()：继续执行
        → 用户 rejectToolCall()：返回拒绝结果给 LLM
    → 不需要审批：直接执行
```

## 工具选择

用户可以在聊天工具栏中选择启用哪些工具。`AgentManager.setSelectedTools()` 更新工具集合并重新初始化 Agent：

```typescript
interface IAgentManager {
  setSelectedTools(toolNames: string[]): void;
  readonly selectedAgentTools: ToolMap;
}
```

当 `toolsEnabled` 配置为 `false` 时，所有工具被禁用，工具栏隐藏工具选择按钮。

## MCP 工具

MCP（Model Context Protocol）服务器提供的工具自动集成到工具系统：

1. `AgentManagerFactory` 通过 `IMcpManager` 监听服务器变更
2. 使用 `@ai-sdk/mcp` 的 `createMCPClient()` 连接每个 MCP 服务器
3. 调用 `client.tools()` 获取服务器暴露的工具
4. 调用 `agentManager.initializeAgent(mcpTools)` 将 MCP 工具注入
5. MCP 工具与内置工具合并，对 LLM 透明

## MIME Bundle 自动渲染

命令执行输出中的 MIME bundle 可以自动渲染到聊天中：

```typescript
// 配置哪些命令的输出自动渲染
config.commandsAutoRenderMimeBundles = ['notebook:run-cell'];
// 配置信任的 MIME 类型
config.trustedMimeTypesForAutoRender = [
  'text/plain', 'image/png', 'image/jpeg', 'application/json'
];
```

## 注册自定义工具

第三方扩展可以注册自定义工具：

```typescript
import { IToolRegistry } from '@jupyternaut/agent';
import { tool } from 'ai';
import { z } from 'zod';

const myCustomTool = tool({
  metadata: { title: 'Insert Cell' },
  description: '在当前 Notebook 中插入新单元格',
  inputSchema: z.object({
    cellType: z.enum(['code', 'markdown']).describe('单元格类型'),
    source: z.string().describe('单元格内容'),
    position: z.enum(['above', 'below']).optional().describe('插入位置')
  }),
  execute: async ({ cellType, source, position }) => {
    // 执行 Notebook 操作
    return { success: true, message: `Inserted ${cellType} cell` };
  }
});

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:register-tool',
  autoStart: true,
  requires: [IToolRegistry],
  activate: (app, toolRegistry) => {
    toolRegistry.add('insert_cell', myCustomTool);
  }
};
```

## 相关概念

- [Provider 模型管理](03-provider-system.md)
- [Agent 执行引擎](05-agent-engine.md)
- [Skill 技能系统](06-skill-system.md)
- [MCP 协议集成](08-mcp-integration.md)
- [内置工具参考](/references/built-in-tools.md)
