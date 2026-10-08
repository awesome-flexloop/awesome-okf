---
type: Example
title: 定义自定义工具
description: 学习如何使用 defineTool 在 DeepSeek Harness 中定义类型安全的自定义工具，包括参数 Schema、输出投影、并发安全和 UI 呈现。
tags:
  - defineTool
  - tool
  - schema
  - validation
  - output-projection
related:
  - create-cordis-plugin
  - connect-mcp-server
  - build-agent-loop
sources:
  - packages/core/tools/src/schema.ts
  - packages/core/tools/src/index.ts
  - packages/fs/tool-fs/src/index.ts
  - packages/fs/tool-fs/src/read.ts
---

# 定义自定义工具

## 场景说明

DeepSeek Harness 的工具系统是模型与外部世界交互的核心桥梁。每个工具通过 `defineTool()` 函数声明，提供编译时类型推断、运行时参数校验、输出 Schema 强制执行，以及可选的 UI 呈现钩子。本示例演示如何定义一个功能完整的「计算器」工具，覆盖：

- 使用 `defineTool` 定义工具的完整流程
- 参数 Schema 声明（`parameters`）与类型推断（`InferArgs`）
- 输出 Schema 声明（`output.schema`）与渲染投影（`output.render`）
- 执行函数（`execute`）与取消信号处理（`exec.signal`）
- 超时设置（`timeoutMs`）与并发安全分类（`isConcurrencySafe`）
- 工具注册到 Cordis 上下文（`ctx.tools.register()`）
- UI 呈现钩子（`presentCall` / `presentResult`）

## 完整代码示例

创建文件 `plugins/calc-tool/index.ts`：

```typescript
/**
 * 计算器工具插件：注册一个支持四则运算的模型可见工具。
 * @module my-dsh-calc-tool
 */

import type { Context } from '@deepseek-ai/cordis'
import type { ContentBlock } from '@deepseek-ai/dsh-llm'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { InferArgs, InferValue } from '@deepseek-ai/dsh-tools'
import z from '@deepseek-ai/schemastery'

export const name = 'calc-tool'
export const inject = ['tools']

export interface Config {
  /** 单次计算超时时间（毫秒）。 */
  timeoutMs?: number
  /** 是否允许并行计算。 */
  allowParallel?: boolean
}

export const Config: z<Config> = z.object({
  timeoutMs: z.number().default(5000),
  allowParallel: z.boolean().default(true),
})

/** 支持的运算符。 */
type Operator = 'add' | 'subtract' | 'multiply' | 'divide'

/** 计算结果的规范输出结构。 */
interface CalcResult {
  expression: string
  result: number
  unit?: string
}

// ---- 工具定义 ----

/** 计算器工具：执行基本四则运算。 */
const calculator = defineTool({
  // 工具名称：必须全局唯一，模型通过此名称调用
  name: 'calculator',

  // 给模型阅读的描述：清晰说明工具功能、参数含义和使用场景
  description: [
    'Perform basic arithmetic calculations (add, subtract, multiply, divide).',
    'Use this tool for any mathematical computation instead of calculating in your head.',
    'Returns the expression evaluated and its numeric result.',
  ].join(' '),

  // 协作超时预算（毫秒）：超过此时间框架可取消执行
  timeoutMs: 5000,

  // ---- 参数 Schema ----
  // 这是一个隐式开放对象根（implicit open object root），
  // 每个属性声明类型、描述、是否必需（required: true），
  // TypeScript 类型会自动推断。
  parameters: {
    a: {
      type: 'number',
      description: 'Left operand (first number).',
      required: true,
    },
    b: {
      type: 'number',
      description: 'Right operand (second number).',
      required: true,
    },
    operator: {
      type: 'string',
      enum: ['add', 'subtract', 'multiply', 'divide'],
      description: 'The arithmetic operator to apply.',
      required: true,
    },
    unit: {
      type: 'string',
      description: 'Optional unit label to append to the result (e.g. "USD", "meters").',
    },
  },

  // ---- 并发安全分类 ----
  // 返回 true 表示该工具在给定参数下可以安全并行执行，
  // 不会修改共享状态或产生竞态条件。
  isConcurrencySafe(_args) {
    // 计算器是纯函数，总是并发安全
    return true
  },

  // ---- 输出 Schema ----
  // output.schema 声明规范输出值的 JSON Schema，
  // execute 返回值会被校验，违反 schema 会抛出 ToolOutputError。
  output: {
    schema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        expression: {
          type: 'string',
          description: 'Human-readable expression that was evaluated.',
        },
        result: {
          type: 'number',
          description: 'Numeric result of the calculation.',
        },
        unit: {
          type: 'string',
          description: 'Unit label, if provided.',
        },
      },
    },

    // render 将规范值投影为模型可见的 ContentBlock[]，
    // 这是模型实际看到的工具返回内容。
    render(
      args: InferArgs<{
        a: { type: 'number'; required: true }
        b: { type: 'number'; required: true }
        operator: { type: 'string'; enum: readonly Operator[]; required: true }
        unit: { type: 'string' }
      }>,
      value: CalcResult,
    ): ContentBlock[] {
      const text = value.unit
        ? `${value.expression} = ${value.result} ${value.unit}`
        : `${value.expression} = ${value.result}`
      return [{ type: 'text', text }]
    },

    // 可选：presentationMeta 为 UI 呈现提供结构化元数据
    presentationMeta(_args, value): Record<string, unknown> {
      return { kind: 'calculation', ...value }
    },
  },

  // ---- 执行函数 ----
  // args 是经过类型推断和运行时校验的参数对象，
  // exec 提供执行上下文（取消信号、Agent 引用、上下文延迟等）。
  async execute(
    args,
    exec,
  ): Promise<CalcResult> {
    const { a, b, operator } = args

    // 检查取消信号：长时间运行的操作应定期检查 exec.signal.aborted
    // 计算器很快，这里仅演示模式
    exec.signal.throwIfAborted()

    let result: number
    const opSymbol: Record<Operator, string> = {
      add: '+',
      subtract: '-',
      multiply: '×',
      divide: '÷',
    }

    switch (operator) {
      case 'add':
        result = a + b
        break
      case 'subtract':
        result = a - b
        break
      case 'multiply':
        result = a * b
        break
      case 'divide':
        if (b === 0) {
          // 抛出 Error 会被框架捕获并转换为工具失败结果
          throw new Error('Division by zero is not allowed')
        }
        result = a / b
        // 浮点数精度修正
        result = Math.round(result * 1e10) / 1e10
        break
      default:
        // 永远不应到达：参数 Schema 的 enum 已校验
        throw new Error(`Unknown operator: ${operator}`)
    }

    const expression = `${a} ${opSymbol[operator]} ${b}`

    return {
      expression,
      result,
      ...args.unit ? { unit: args.unit } : {},
    }
  },

  // ---- 可选：挂起状态呈现 ----
  // 返回 UI 渲染意图，用于在工具执行期间显示自定义卡片
  presentCall(args) {
    const opSymbol: Record<string, string> = {
      add: '+', subtract: '-', multiply: '×', divide: '÷',
    }
    return {
      kind: 'terminal',
      title: `calculator: ${args.a} ${opSymbol[args.operator]} ${args.b}`,
    }
  },

  // ---- 可选：完成状态呈现 ----
  presentResult(_args, result) {
    if (result.isError) return undefined
    return {
      kind: 'terminal',
      output: result.content.map(c => c.type === 'text' ? c.text : '').join('\n'),
    }
  },
})

// ---- 更复杂的工具示例：带延迟上下文的天气查询 ----

const weatherTool = defineTool({
  name: 'query_weather',
  description: 'Query current weather for a given city. Returns temperature and conditions.',
  timeoutMs: 10000,

  parameters: {
    city: {
      type: 'string',
      description: 'City name to query weather for (e.g. "Beijing", "New York").',
      required: true,
    },
    unit: {
      type: 'string',
      enum: ['celsius', 'fahrenheit'],
      description: 'Temperature unit.',
    },
  },

  isConcurrencySafe(args) {
    // 同一城市的并发查询是安全的
    return true
  },

  output: {
    schema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        city: { type: 'string' },
        temperature: { type: 'number' },
        conditions: { type: 'string' },
        humidity: { type: 'integer' },
      },
    },
    render(_args, value): ContentBlock[] {
      return [{
        type: 'text',
        text: [
          `Weather in ${value.city}:`,
          `  Temperature: ${value.temperature}°${_args.unit === 'fahrenheit' ? 'F' : 'C'}`,
          `  Conditions: ${value.conditions}`,
          `  Humidity: ${value.humidity}%`,
        ].join('\n'),
      }]
    },
  },

  async execute(args, exec): Promise<{
    city: string
    temperature: number
    conditions: string
    humidity: number
  }> {
    // 演示：实际场景中此处会调用 HTTP API
    // exec.signal 应传递给 fetch 的 AbortSignal
    exec.signal.throwIfAborted()

    // 模拟网络延迟
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(resolve, 100)
      exec.signal.addEventListener('abort', () => {
        clearTimeout(timer)
        reject(exec.signal.reason)
      })
    })

    // 模拟数据
    const conditions = ['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy']
    const baseTemp = args.unit === 'fahrenheit' ? 72 : 22
    return {
      city: args.city,
      temperature: baseTemp + Math.round((Math.random() - 0.5) * 20),
      conditions: conditions[Math.floor(Math.random() * conditions.length)],
      humidity: 40 + Math.floor(Math.random() * 40),
    }
  },
})

// ---- 插件 apply ----

export function apply(ctx: Context, config: Config): void {
  ctx.effect(() => {
    // 注册工具到工具注册表
    // 返回的 dispose 函数在插件卸载时自动注销工具
    const disposeCalc = ctx.tools.register(calculator)
    const disposeWeather = ctx.tools.register(weatherTool)
    ctx.logger.info('calc-tool: calculator and query_weather registered')
    return () => {
      disposeCalc()
      disposeWeather()
      ctx.logger.info('calc-tool: tools unregistered')
    }
  }, 'calc-tool.register')
}
```

在 `cordis.yml` 中加载：

```yaml
- id: calc-tool
  name: './plugins/calc-tool'
  config:
    timeoutMs: 5000
    allowParallel: true
```

## 逐步解释

### 1. defineTool 的核心结构

```
defineTool({
  name: string           // 工具唯一名称
  description: string    // 给模型的功能描述
  parameters: { ... }    // 参数 Schema（隐式开放对象）
  output: {              // 输出契约
    schema: { ... }      // 输出 JSON Schema
    render(args, value)  // 输出→ContentBlock[] 投影
  }
  async execute(args, exec) { ... }  // 执行逻辑
  // 可选字段：
  timeoutMs?: number
  isConcurrencySafe?(args): boolean
  presentCall?(args): ToolCallView
  presentResult?(args, result): ToolResultView
  finalizeContent?(exec, result): ContentBlock[]
})
```

`defineTool` 在编译时通过泛型参数推断 `args` 和返回值的 TypeScript 类型，在运行时编译 Schema 为 JSON Schema 并在 `execute` 前自动校验参数。

### 2. 参数 Schema 类型系统

参数 Schema 是一个**隐式开放对象根**（implicit open object root），每个属性可以是：

| 类型 | 说明 | 额外约束 |
|------|------|----------|
| `type: 'string'` | 字符串 | `enum`, `const` |
| `type: 'number'` / `'integer'` | 数值/整数 | `enum`, `const` |
| `type: 'boolean'` | 布尔值 | `enum`, `const` |
| `type: 'null'` | null 值 | — |
| `type: 'array'` | 数组 | `items`（元素 Schema） |
| `type: 'object'` | 对象 | `properties`, `additionalProperties`（必须显式声明） |
| `type: 'json'` | 任意 JSON 值 | — |
| `oneOf: [...]` | 联合类型 | 至少两个分支 |

属性通过 `required: true` 标记为必需，未标记的属性是可选的（`?`）。

### 3. 输出 Schema 与 render 投影

`output.schema` 声明工具返回的**规范值**（canonical value）的结构，框架在 `execute` 返回后校验此值。`output.render` 将规范值转换为模型实际看到的 `ContentBlock[]`（通常是文本块）。

这种分离有两个好处：
- **结构化数据可程序化消费**：UI 可通过 `presentationMeta` 获取结构化数据
- **模型看到优化后的文本**：`render` 可将结构化数据格式化为自然语言

### 4. execute 函数与 exec 上下文

`execute(args, exec)` 接收两个参数：
- `args`：经过 Schema 校验和类型推断的参数对象
- `exec`：`ToolRunContext`，包含：
  - `exec.signal: AbortSignal`：取消信号，长时间运行操作必须监听
  - `exec.agent: Agent`：发起调用的 Agent 引用
  - `exec.deferContext(message)`：延迟附加上下文消息到下一轮模型请求
  - `exec.concludeTurn()`：标记当前轮次在工具结果后结束

### 5. 超时与并发安全

- `timeoutMs`：声明协作超时。框架的 `dsh-tool-call-timeout-policy` 插件会在超时时通过 `AbortSignal` 通知取消。工具必须在 `execute` 中检查 `exec.signal` 才能响应超时。
- `isConcurrencySafe(args)`：纯函数分类器。返回 `true` 表示该工具调用可以与其他并发安全调用并行执行；返回 `false`（或省略）则形成排他屏障（exclusive barrier）。

### 6. 工具注册

```typescript
const dispose = ctx.tools.register(toolDefinition)
```

- 注册到全局工具层，所有 Agent 默认可见
- 返回 disposer，调用后注销工具
- 在 `ctx.effect()` 内注册时，disposer 在插件卸载时自动执行
- 在 Agent 作用域内（`agent.ctx.tools.register()`）注册则仅对该 Agent 可见

## 输出结果

模型加载工具后，发送 "Calculate 123.45 × 67.89" 时：

```
[模型] Call tool: calculator
       args: { a: 123.45, b: 67.89, operator: "multiply" }

[工具执行]
  → calculator: 123.45 × 67.89
  → 123.45 × 67.89 = 8381.0205
```

模型看到的工具返回内容为 `123.45 × 67.89 = 8381.0205`（由 `output.render` 生成的文本块）。

如果除数为零：

```
[模型] Call tool: calculator
       args: { a: 10, b: 0, operator: "divide" }
[工具错误] Division by zero is not allowed
```

## 注意事项

1. **description 写给模型看**：`description` 应清晰描述工具功能、参数含义和何时使用。模型完全依赖此字段决定是否调用工具。描述模糊是工具调用失败的常见原因。

2. **参数必须声明 additionalProperties**：对象类型的参数 Schema 必须显式声明 `additionalProperties: true` 或 `false`，否则编译时会报错。这防止意外创建封闭对象。

3. **execute 中的错误处理**：`execute` 中抛出的 `Error` 会被框架自动捕获为工具失败结果（`isError: true`），错误消息会呈现给模型。不需要 try/catch 包裹常规错误。但应抛出有意义的错误消息，模型会看到并可能自我修正。

4. **signal 转发**：如果工具调用外部 API（HTTP、子进程等），必须将 `exec.signal` 转发为请求的 `AbortSignal`，否则超时和取消无法生效。

5. **render 必须是纯函数**：`output.render` 不应有副作用，因为它可能在重放（replay）时被多次调用。它只应依赖 `args` 和 `value`。

6. **presentCall/presentResult 容错**：UI 呈现钩子在日志重放时可能收到旧版本 schema 的参数，框架会自动软校验——校验失败时返回 `undefined`（使用通用呈现），不会抛出异常。因此这两个方法中的参数类型可能不完全可信。

7. **工具名保留**：`run_code` 是 Code Mode 的保留传输工具名，不可注册或覆盖。其他名称建议使用 snake_case（如 `query_weather`）以保持与模型习惯一致。

8. **避免在 execute 中直接修改 ctx**：`execute` 接收的 `exec` 提供了受限的上下文访问。如需与其他服务交互，通过闭包捕获 `ctx` 引用是可接受的，但应注意作用域——在 Agent 作用域注册的工具闭包会持有 Agent 上下文。
