---
type: Concept
title: "OpenCode Codemode 运行时与限制"
description: "分清解释执行、宿主工具、复用状态、schema校验与可选预算的接线"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, codemode, interpreter, tool]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode Codemode 运行时与限制

Codemode将代码解析后交给解释器，并连接宿主工具。它不是直接调用宿主`eval`；但“解释执行”本身也不证明整个进程已安全隔离。应把语法执行、宿主工具权限、数据校验和预算分别核对。本篇依据[F-123～F-130](../spec/facts-deepening-2.0.32.md)。

## 从Core工具目录进入解释器

`Tool.snapshot`将`codemode===false`的工具留在direct，其余进入CodeMode inventory。Core `CodeModeTool`以`WeakMap<Inventory, Runtime<Run>>`缓存运行时，逐调用提供`Run`；子工具调用仍经过`beforeExecute`和`executeTool`，不是绕开宿主链的另一个任意函数入口。（F-129、F-130）

```text
Core inventory → cached CodeMode runtime
→ execute(code) → Acorn parse → Interpreter.run
→ ToolRuntime decode/hook → Core executeTool
```

`CodeMode.execute`委托`make(options).execute(code)`；Acorn使用script parse并允许顶层await/return。复用的是prepared tools/catalog，而每次`executeProgram`在`Effect.suspend`中重新建立builtins、调用记录、logs、Pending和Interpreter。不要把缓存runtime误解为跨调用共享日志、执行栈或pending任务。（F-123、F-124）

## 呈现schema不等于执行校验

工具调用零参数归一为`{}`，多个参数被拒绝。`decodeInput`对Effect Schema执行解码，普通JSON Schema直接传入值；没有output schema时返回undefined。Core在选择工具结果时，typed output优先，否则采用text/null。（F-125、F-130）

对应codemode测试明确把JSON Schema称为render-only，并定义了mistyped input仍传入的断言。本轮只读取测试，未执行。不能因为模型看到了schema就推断传入值已经经运行时验证。

## 预算要查实际make参数

下面是源码类型节选，不是可直接运行的示例：

```ts
export type ExecutionLimits = {
  readonly timeoutMs?: number
  readonly maxToolCalls?: number
  readonly maxOutputBytes?: number
}
```

这些字段可选，没有默认值；显式值需通过安全整数和下限检查。工具调用计数发生在输入解码后、before hook前。更重要的是，Core的`CodeMode.make`只传tools/extensions/hooks，未传limits。存在预算类型与某调用方启用了预算，是不同事实。（F-126、F-130）

`maxOutputBytes`在结果产生后局部裁剪value/logs，warnings另有等额预算；toolCalls、error及截断提示不受一个统一响应字节上限约束。不能把结果裁剪称为整个过程内存硬上限，也不能推断所有响应字段合计一定不超预算。（F-128）

## 返回值与后台结束的时点

正常返回在plain-data copy-out后中断pending。timeout发生在copy-out前是失败；copy-out后后台工作尚未结束时可能保留成功值并带warning。因此“结果可返回”和“全部后台工作自然结束”并非同一确认点。（F-127）

审读时依次查executeProgram、ToolRuntime、tool-schema、Core make接线。完整语法/stdlib、web extension及进程级安全隔离不在本轮验证内。单次逻辑LLM调用仍称step，工具调用与codemode执行不要混称模型turn。

## 相关概念

- [模型与工具扩展](07-model-tool-extensibility.md)
- [插件契约与生命周期](12-plugin-contract-lifecycle.md)
- [新增事实与源码链接](../spec/facts-deepening-2.0.32.md)
