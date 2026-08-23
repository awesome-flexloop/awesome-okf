---
type: Reference
title: 内置 AI 工具参考
description: jupyterlite-ai 内置的 discover_commands、execute_command、browser_fetch、discover_skills、load_skill 工具定义
tags: [jupyterlite-ai, tools, reference]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
---

# 内置 AI 工具参考

jupyterlite-ai 在 ToolRegistry 中注册了 4-5 个内置工具，使 AI 代理能够与 JupyterLab 环境交互。

## discover_commands 工具

**注册名称**：`discover_commands`

**用途**：发现所有可用的 JupyterLab 命令及其元数据、参数和描述。

**创建函数**：`createDiscoverCommandsTool(commands: CommandRegistry): ITool`

**输入 Schema**：

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `query` | string \| null | 否 | 可选搜索查询，支持多词查询（空格分隔），每个词必须包含在命令 id/label/caption/description 中 |

**输出**：
```typescript
{
  success: boolean;
  commandCount: number;
  commands: Array<{
    id: string;
    label?: string;
    caption?: string;
    description?: string;
    args?: any;
  }>;
}
```

**搜索算法**：
- 大小写不敏感匹配
- 多词查询按空格拆分，每个词必须出现在至少一个可搜索字段中
- 字段权重：label(4) > caption(3) > id(2) > description(1)
- 完整短语匹配额外加权 4 倍

## execute_command 工具

**注册名称**：`execute_command`

**用途**：执行特定的 JupyterLab 命令，支持可选参数。

**创建函数**：`createExecuteCommandTool(commands: CommandRegistry): ITool`

**审批策略**：通过 `createExecuteCommandApprovalPolicy(settingsModel)` 配置，`commandsRequiringApproval` 列表中的命令需要用户审批。

**输入 Schema**：

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `commandId` | string | 是 | 要执行的命令 ID |
| `args` | Record<string, unknown> | 否 | 传递给命令的参数对象（必须是对象，不能是字符串） |

**输出**：
```typescript
// 成功时
{
  success: true;
  commandId: string;
  result: any;  // Widget 返回 {id, title}，其他对象尝试 JSON 序列化
}

// 失败时
{
  success: false;
  error: string;  // 命令不存在时的错误信息
}
```

**特殊处理**：
- 如果命令返回 Lumino Widget 实例，序列化为 `{ id, title }` 避免复杂对象
- 其他对象尝试 `JSON.parse(JSON.stringify(result))` 序列化
- 序列化失败返回 `'[Complex object - cannot serialize]'`
- 无返回值返回 `'Command executed successfully'`

## browser_fetch 工具

**注册名称**：`browser_fetch`

**用途**：直接从浏览器使用 HTTP GET 获取 URL 内容。受浏览器 CORS/CSP/混合内容策略限制。

**创建函数**：`createBrowserFetchTool(): ITool`

**输入 Schema**：

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `url` | string | 是 | 要获取的 HTTP(S) URL |
| `maxContentChars` | number | 否 | 返回的最大字符数（默认 20000，最大 100000） |
| `timeoutMs` | number | 否 | 超时毫秒数（默认 20000，最大 120000） |

**输出**：
```typescript
// 成功时
{
  success: true;
  url: string;           // 最终 URL（跟随重定向后）
  requestedUrl: string;  // 请求的原始 URL
  status: number;        // HTTP 状态码
  statusText: string;
  contentType: string;
  contentLength: string | null;
  isTruncated: boolean;
  returnedChars: number;
  totalChars: number;
  totalCharsExact: boolean;
  content: string;
  limitations: string;   // CORS 等限制说明
}

// 失败时
{
  success: false;
  errorType: 'invalid_url' | 'unsupported_protocol' | 'timeout' | 'http_error' | 'network_or_cors';
  error: string;
  url: string;
  likelyCauses?: string[];  // 网络/CORS 错误时的可能原因
}
```

**安全限制**：
- 仅支持 `http:` 和 `https:` 协议
- 使用 `credentials: 'omit'` 不发送 Cookie
- 流式读取响应体，达到字符上限后取消读取
- Accept 头限制为文本类型

## discover_skills 工具

**注册名称**：`discover_skills`

**用途**：发现可用的 Agent 技能及其名称和描述。

**创建函数**：`createDiscoverSkillsTool(skillRegistry: ISkillRegistry): ITool`

**输入 Schema**：

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `query` | string \| null | 否 | 可选搜索查询过滤技能 |

**输出**：
```typescript
{
  success: true;
  skillCount: number;
  skills: Array<{
    name: string;
    description: string;
  }>;
}
```

## load_skill 工具

**注册名称**：`load_skill`

**用途**：加载技能定义或技能捆绑的特定资源文件。

**创建函数**：`createLoadSkillTool(skillRegistry: ISkillRegistry): ITool`

**输入 Schema**：

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | 是 | 要加载的技能名称 |
| `resource` | string \| null | 否 | 要加载的资源路径（如 `references/REFERENCE.md`） |

**输出**：
```typescript
// 加载技能定义时
{
  success: true;
  name: string;
  description: string;
  instructions: string;
  resources?: string[];
}

// 加载资源文件时
{
  success: true;
  name: string;
  resource: string;
  content: string;
}

// 失败时
{
  success: false;
  error: string;
  // 资源错误时附加 name, resource 字段
}
```
