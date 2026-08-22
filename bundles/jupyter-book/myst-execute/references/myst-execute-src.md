---
type: reference
title: "myst-execute 执行核心源码"
description: "myst-execute 包的执行管线源码入口，包含 computeExecutableNodes、applyComputedOutputsToNodes、kernelExecutionTransform 等核心函数"
tags: [myst-execute, execution, kernel, cache, unified-plugin]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "mystmd/packages/myst-execute/src/execute.ts"
    facts: [F-011, F-012, F-013, F-014, F-015]
  - path: "mystmd/packages/myst-execute/src/kernel.ts"
    facts: [F-016, F-017, F-018, F-019, F-020, F-021]
  - path: "mystmd/packages/myst-execute/src/transform.ts"
    facts: [F-032, F-033, F-034, F-035]
  - path: "mystmd/packages/myst-execute/src/manager.ts"
    facts: [F-036, F-037, F-038, F-039, F-040]
  - path: "mystmd/packages/myst-execute/src/cache.ts"
    facts: [F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031]
  - path: "mystmd/packages/myst-execute/src/types.ts"
    facts: [F-022, F-023]
  - path: "mystmd/packages/myst-execute/src/utils.ts"
    facts: [F-041, F-042, F-043, F-044]
  - path: "mystmd/packages/myst-execute/src/index.ts"
    facts: [F-010]
  - path: "mystmd/packages/myst-execute/package.json"
    facts: [F-001, F-002, F-003, F-004]
---

# myst-execute 执行核心源码

## 源码位置

**仓库根**：`external/libs/ai/jupyter-book/mystmd/`
**包目录**：`packages/myst-execute/src/`

## 核心文件清单

| 文件 | 职责 | 关键导出 |
|------|------|---------|
| `execute.ts` | 执行管线核心 | `computeExecutableNodes()`, `applyComputedOutputsToNodes()`, `getExecutableNodes()` |
| `kernel.ts` | Jupyter 内核通信 | `createKernelConnection()`, `executeCodeCell()`, `evaluateInlineExpression()` |
| `transform.ts` | unified 插件 | `kernelExecutionTransform`, `kernelExecutionPlugin`, `buildCacheKey()` |
| `cache.ts` | 多级缓存实现 | `ICache<T>`, `LocalDiskCache<T>`, `LegacyExecutionCache`, `NotebookExecutionCache`, `TieredExecutionCache` |
| `manager.ts` | Jupyter Server 生命周期 | `findExistingJupyterServer()`, `launchJupyterServer()`, `JupyterServerSettings` |
| `types.ts` | 类型定义 | `ExecutableNode`, `CodeResult`, `ExpressionResult`, `DocumentExecutionResult` |
| `utils.ts` | 节点判断工具 | `isCodeBlock()`, `codeBlockRaisesException()`, `codeBlockSkipsExecution()`, `isInlineExpression()` |
| `index.ts` | 包入口 | 汇总导出所有公共 API |

## 依赖关系

```
index.ts
  ├─ transform.ts (kernelExecutionTransform)
  │   ├─ kernel.ts (createKernelConnection, executeCodeCell, evaluateInlineExpression)
  │   ├─ cache.ts (IDocumentExecutionCache)
  │   ├─ execute.ts (getExecutableNodes, computeExecutableNodes, applyComputedOutputsToNodes)
  │   └─ manager.ts (findExistingJupyterServer, launchJupyterServer)
  ├─ cache.ts (导出所有缓存类)
  └─ manager.ts (JupyterServerSettings, findExistingJupyterServer, launchJupyterServer)
```

## 版本信息

- 包版本：0.4.0
- 许可证：MIT
- 构建系统：TypeScript → ESM (dist/index.js)
- 测试框架：vitest

## 关键运行时依赖

- `@jupyterlab/services ^7.6.0`：Jupyter 内核/Session 管理
- `@jupyterlab/nbformat ^3.5.2`：Notebook 格式类型
- `myst-common ^1.10.0`：MDAST 工具函数、NotebookCell 常量
- `myst-spec ^0.0.5`：MyST AST 类型定义（Code/CodeBlock/InlineExpression/Outputs）
- `unified ^10.1.2`：插件系统
- `unist-util-select ^4.0.3`：AST 节点选择
- `vfile ^5.3.7`：虚拟文件
