---
type: Concept
title: 支持表
description: KaTeX 官网 Support Table 页面的用途与阅读方式，按字母排序的 TeX 函数支持清单，Detexify 手写识别工具，以及从支持表条目溯源到源码宏定义和函数实现的方法。
tags: [katex, support-table, reference, detexify, tex-commands]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-support-table
    resource: /references/katex-website.md#web-support-table
    title: KaTeX 官网 Support Table 页面
  - id: web-supported
    resource: /references/katex-website.md#web-supported
    title: KaTeX 官网 Supported Functions 页面
  - id: facts
    resource: /spec/facts.md
    title: KaTeX 事实清单
---

## 概述

KaTeX 官网提供两个互补的函数参考页面：

- [Supported Functions](https://katex.org/docs/supported)：按**类型/逻辑分组**排序，适合浏览和系统学习
- [Support Table](https://katex.org/docs/support_table)：按**字母顺序**排序，适合已知命令名称快速查找

本文档说明 Support Table 页面的结构、阅读方式、与源码的溯源关系，以及 Detexify 手写识别工具的使用。按类型分类的函数清单见 [支持的函数](19-supported-functions.md)。

## 支持表结构

Support Table 页面是按字母排序的 TeX 函数列表，包含三列[^web-support-table]：

| 列名 | 内容 |
|------|------|
| Symbol/Function | 命令名称（如 `\frac`、`\alpha`、`\sum`）或符号 |
| Rendered | KaTeX 实际渲染效果预览 |
| Source or Comment | 命令来源说明、备注，或标记为"不支持" |

表格以 `\gdef\VERT{|}` 开头定义竖线符号[^facts]，条目覆盖从标点符号（`!`、`\%`、`\&`）到复杂命令的完整范围。

### 支持与不支持条目的阅读

Support Table 同时列出 KaTeX 支持和不支持的 TeX 函数。不支持的条目在 Source or Comment 列会明确标注，使用时会触发 ParseError 或在 `throwOnError: false` 时以红色错误文本渲染。

这与 Supported Functions 页面形成互补：Supported Functions 只列出支持的命令并按类别分组；Support Table 覆盖更全（含不支持项），便于确认某个命令是否可用。

## 两个页面的选择

| 场景 | 推荐页面 |
|------|---------|
| 系统学习某类命令（如"KaTeX 支持哪些重音命令"） | Supported Functions（按分类） |
| 已知命令名，确认是否支持 | Support Table（字母序） |
| 知道符号形状但不知道名称 | Detexify（手写识别） |
| 查找不支持的命令的替代方案 | Support Table（含不支持标注） |

## Detexify 手写识别

当你知道符号的形状但不知道 LaTeX 命令名称时，可使用 [Detexify](https://detexify.kirelabs.org/classify.html)[^web-support-table]：

1. 在网页的手写区域画出符号
2. 系统实时识别并列出最可能的 LaTeX 命令及其所属宏包
3. 根据识别结果在 Support Table 中确认 KaTeX 是否支持

Detexify 是第三方工具，覆盖标准 LaTeX 符号；识别出的命令需回到 KaTeX Support Table 验证是否被 KaTeX 支持。

## 源码溯源

从 Support Table 中的命令条目可以追溯到 KaTeX 源码中的实现位置。KaTeX 命令有三种实现方式[^src]：

### 1. 函数实现（src/functions/）

大部分命令通过 `defineFunction` 注册，实现位于 `src/functions/` 目录下的 43 个 .ts 文件中。例如：

- 分数族：`genfrac.ts`（处理 `\frac`、`\dfrac`、`\tfrac`、`\binom` 等）
- 算符族：`op.ts`（处理 `\sum`、`\int`、`\lim` 等大算符和函数名）
- 符号命令：各符号相关文件

每个函数定义包含 `handler`（解析逻辑）、`htmlBuilder`（HTML 渲染）和 `mathmlBuilder`（MathML 渲染），详见 [函数注册表](08-function-registry.md)。

### 2. 宏定义（src/macros.ts）

部分命令通过宏而非 `\DeclareMathSymbol` 定义[^facts]，位于 `src/macros.ts`。这些命令在展开时可能展开为多个 token，并受 `\expandafter` 和 `\noexpand` 影响。

宏定义的命令与函数实现的命令在行为上存在差异：宏在 MacroExpander（gullet）层展开，函数在 Parser（stomach）层执行。理解这一区别对调试宏相关问题很重要，详见 [宏展开器](04-macro-expander.md)。

### 3. 符号注册（src/symbols.ts）

单字符符号和通过 `\mathchar` 类命令访问的符号注册在 `src/symbols.ts` 中，按 math/text 模式和原子类型（bin/rel/open/close/punct/inner/ord）分组。

### 4. 环境实现（src/environments/）

`array`、`cd` 等环境通过 `defineEnvironment` 注册，实现位于 `src/environments/` 目录。

### 溯源方法

```
Support Table 条目
       │
       ├── 复杂命令（带参数、有特殊渲染逻辑）
       │       └── src/functions/*.ts（defineFunction 注册）
       │
       ├── 简单别名/组合命令
       │       └── src/macros.ts（宏定义）
       │
       ├── 单字符符号
       │       └── src/symbols.ts（符号注册表）
       │
       └── 环境类（\begin{...}）
               └── src/environments/*.ts（defineEnvironment 注册）
```

## 使用建议

1. **迁移现有 LaTeX 文档**：先在 Support Table 中逐一检查所用命令是否被 KaTeX 支持，对不支持的命令寻找替代方案
2. **编写新公式**：通过 Supported Functions 页面按分类浏览可用命令，或通过 Support Table 确认具体命令
3. **调试渲染问题**：遇到意外渲染结果时，从 Support Table 确认命令语义，再从源码溯源理解实现行为
4. **自定义扩展**：了解命令的实现方式（函数 vs 宏 vs 符号），确定自定义扩展应在哪一层介入（详见 [TeX 消化管隐喻](02-architecture-overview.md)）

## 相关概念

- [支持的函数](19-supported-functions.md) — 按 14 个分类整理的函数清单
- [函数注册表](08-function-registry.md) — defineFunction 机制与 FunctionSpec
- [宏系统](09-macro-system.md) — 宏定义与展开机制
- [架构总览](02-architecture-overview.md) — TeX 消化管三层模型
- [KaTeX 源码信源](../references/katex-source.md) — 源码文件完整索引

[^web-support-table]: 官网 Support Table 页面，https://katex.org/docs/support_table
[^web-supported]: 官网 Supported Functions 页面，https://katex.org/docs/supported
[^src]: KaTeX 源码信源，`src/functions/`（43 文件，F-012）、`src/macros.ts`（F-073）、`src/symbols.ts`、`src/environments/`（F-013）
[^facts]: KaTeX 事实清单，W-132（Support Table 以 `\gdef\VERT{|}` 开头）、W-140（部分符号通过宏定义）
