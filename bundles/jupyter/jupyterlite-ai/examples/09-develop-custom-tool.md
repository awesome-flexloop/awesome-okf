---
type: Example
title: "开发自定义 AI 工具"
description: "通过 JupyterLab 扩展为 AI 添加自定义工具，扩展 Agent 的能力"
tags: [jupyterlite-ai, developer, custom-tool, extension, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: tokens
    resource: /references/tokens-api.md
    title: Token 与核心接口 API 参考
  - id: tools
    resource: /references/built-in-tools.md
    title: 内置 AI 工具参考
---

# 开发自定义 AI 工具

通过 JupyterLab 扩展插件机制，你可以为 JupyterLite AI 添加自定义工具，让 AI 能够执行特定领域的操作。

## 前置条件

- JupyterLab 4.x 开发环境
- TypeScript 知识
- 熟悉 Lumino 插件系统
- 已安装 `@jupyterlite/ai` 包

## 工具开发步骤

### 1. 创建 JupyterLab 扩展

```bash
# 使用 cookiecutter 创建扩展
pip install cookiecutter
cookiecutter https://github.com/jupyterlab/extension-cookiecutter-ts

# 安装依赖
jlpm install
```

### 2. 依赖声明

在 `package.json` 中添加对 AI 包的依赖：

```json
{
  "dependencies": {
    "@jupyterlite/ai": "^0.19.0",
    "@jupyternaut/agent": "^0.19.0"
  },
  "peerDependencies": {
    "@jupyterlab/application": "^4.0.0"
  }
}
```

### 3. 定义工具

使用 Vercel AI SDK 的工具定义格式：

```typescript
// src/tools/my-custom-tool.ts
import { tool } from 'ai';
import { z } from 'zod';
import type { IJupyterLab } from '@jupyterlab/application';

export function createMyCustomTool(app: IJupyterLab) {
  return tool({
    description: '描述这个工具的功能，AI 根据此描述决定何时调用',
    parameters: z.object({
      param1: z.string().describe('参数1的说明'),
      param2: z.number().optional().describe('可选参数2的说明'),
    }),
    execute: async ({ param1, param2 }) => {
      // 工具的执行逻辑
      // 可以访问 JupyterLab app 对象
      // 执行操作并返回结果字符串
      const result = await doSomething(app, param1, param2);
      return `操作结果：${result}`;
    },
  });
}
```

### 4. 注册工具到 IToolRegistry

在插件的 `activate` 函数中注册工具：

```typescript
// src/index.ts
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';
import { IToolRegistry } from '@jupyternaut/agent';
import { createMyCustomTool } from './tools/my-custom-tool';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@my-org/my-custom-tool',
  autoStart: true,
  requires: [IToolRegistry],
  activate: (app: JupyterFrontEnd, toolRegistry: IToolRegistry) => {
    // 创建工具实例
    const myTool = createMyCustomTool(app);

    // 注册到工具注册表
    toolRegistry.addTool('my_custom_tool', myTool, {
      isDestructive: false,  // 设为 true 则执行前需用户审批
      requiresApproval: false,
    });

    console.log('My custom AI tool registered!');
  },
};

export default plugin;
```

## 工具定义参考

### IToolRegistry 接口

```typescript
interface IToolRegistry {
  addTool(id: string, tool: Tool, options?: ToolOptions): void;
  removeTool(id: string): void;
  getTools(): Record<string, Tool>;
  getTool(id: string): Tool | undefined;
  toolsChanged: ISignal<this, IToolRegistry.IToolChangedArgs>;
}

interface ToolOptions {
  isDestructive?: boolean;    // 是否是破坏性操作
  requiresApproval?: boolean; // 是否需要用户审批
  category?: string;          // 工具分类
  icon?: string;              // 图标类名
}
```

### 工具参数设计原则

1. **使用 Zod schema 定义参数**，提供清晰的类型和描述
2. **参数描述要详细**，AI 根据描述决定传什么值
3. **参数数量适度**，避免过多参数增加 AI 选择难度
4. **返回字符串结果**，工具执行结果应为 AI 可理解的文本

## 完整示例：数据查询工具

```typescript
// src/tools/query-data.ts
import { tool } from 'ai';
import { z } from 'zod';

export function createDataQueryTool() {
  return tool({
    description: `查询已加载的 pandas DataFrame 的信息。
使用此工具可以：
- 查看 DataFrame 的列名和数据类型
- 获取描述性统计信息
- 筛选和查询数据
参数 df_name 是 DataFrame 的变量名，query 是要执行的 pandas 查询语句。`,
    parameters: z.object({
      df_name: z.string().describe('DataFrame 变量名，如 "df"、"sales_data"'),
      operation: z.enum(['info', 'describe', 'head', 'query'])
        .describe('要执行的操作：info(基本信息)/describe(统计)/head(前N行)/query(自定义查询)'),
      n: z.number().optional().describe('head 操作返回的行数，默认 5'),
      query_str: z.string().optional().describe('query 操作的 pandas query 字符串'),
    }),
    execute: async ({ df_name, operation, n = 5, query_str }) => {
      // 注意：在 JupyterLite 中需要通过内核执行
      // 在 JupyterLab 中可以通过 kernel 连接执行
      const code = generateQueryCode(df_name, operation, n, query_str);
      const result = await executeInKernel(code);
      return result;
    },
  });
}

function generateQueryCode(dfName: string, op: string, n: number, q?: string): string {
  switch (op) {
    case 'info':
      return `${dfName}.info()`;
    case 'describe':
      return `${dfName}.describe().to_string()`;
    case 'head':
      return `${dfName}.head(${n}).to_string()`;
    case 'query':
      return `${dfName}.query("${q}").to_string()`;
    default:
      return '';
  }
}
```

## 最佳实践

1. **工具描述要清晰**：这是 AI 理解工具用途的唯一途径
2. **单一职责**：每个工具只做一件事，做好一件事
3. **返回有用结果**：结果应包含足够的信息供 AI 继续推理
4. **正确设置审批标志**：修改数据/文件的工具必须设置 `isDestructive: true`
5. **处理错误**：工具执行出错时返回友好的错误信息，而非抛出异常
6. **避免副作用**：工具执行不应有意外的副作用
