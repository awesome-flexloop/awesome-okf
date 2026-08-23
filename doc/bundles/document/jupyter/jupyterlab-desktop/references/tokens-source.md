---
type: Reference
title: 核心接口与类型定义源码信源
description: src/main/tokens.ts 核心接口与类型定义源码登记，包含 ICLIArguments、IPythonEnvironment、IEnvironmentType、IDisposable、IRect 等核心类型
tags: [types, interfaces, tokens, environment, cli, disposable]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tokens-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/tokens.ts
    title: tokens.ts source on GitHub
---

# 核心接口与类型定义源码信源

## 源码路径

`src/main/tokens.ts`

## 文件职责

定义应用中跨模块使用的核心 TypeScript 接口、枚举和类型，作为模块间的"契约"。

## IVersionContainer 接口

```typescript
interface IVersionContainer {
  [name: string]: string;
}
```

版本号字典，键为包名，值为版本字符串。

## IEnvironmentType 枚举

```typescript
enum IEnvironmentType {
  Path = 'path',              // 通用路径类型
  CondaRoot = 'conda-root',   // Conda base 环境
  CondaEnv = 'conda-env',     // Conda 子环境
  WindowsReg = 'windows-reg', // Windows 注册表发现
  VirtualEnv = 'venv'         // Python venv 虚拟环境
}
```

### EnvironmentTypeName 映射

```typescript
const EnvironmentTypeName: { [key in IEnvironmentType]: string } = {
  [IEnvironmentType.Path]: 'system',
  [IEnvironmentType.CondaRoot]: 'conda',
  [IEnvironmentType.CondaEnv]: 'conda',
  [IEnvironmentType.WindowsReg]: 'win',
  [IEnvironmentType.VirtualEnv]: 'venv'
};
```

将环境类型映射为用户可读的显示名称。

## IPythonEnvironment 接口

Python 环境的完整描述：

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | `string` | Python 可执行文件路径 |
| `name` | `string` | 显示名称（不保证唯一） |
| `type` | `IEnvironmentType` | 环境类型 |
| `versions` | `IVersionContainer` | 各依赖包版本号（jupyterlab 等） |
| `defaultKernel` | `string` | 默认 kernel 名称 |

## PythonEnvResolveErrorType 枚举

```typescript
enum PythonEnvResolveErrorType {
  PathNotFound = 'path-not-found',
  InvalidPythonBinary = 'invalid-python-binary',
  ResolveError = 'resolve-error',
  RequirementsNotSatisfied = 'requirements-not-satisfied'
}
```

## IPythonEnvResolveError 接口

```typescript
interface IPythonEnvResolveError {
  type: PythonEnvResolveErrorType;
  message?: string;
}
```

## IPythonEnvValidateResult 接口

```typescript
interface IPythonEnvValidateResult {
  valid: boolean;
  error?: IPythonEnvResolveError;
}
```

## IDisposable 接口

```typescript
interface IDisposable {
  dispose(): Promise<void>;
}
```

实现此接口的类（JupyterApplication、SessionWindowManager、JupyterServerFactory、Registry 等）需提供异步清理方法。

## ICLIArguments 接口

CLI 解析后的参数结构（继承自 yargs.Arguments）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `cwd?` | `string` | 当前工作目录 |
| `_` | `(string \| number)[]` | 位置参数数组 |
| `$0` | `string` | 脚本名称 |
| `[x: string]` | `unknown` | 其他任意选项（索引签名） |
| `pythonPath` | `string \| unknown` | `--python-path` 选项 |
| `workingDir` | `string \| unknown` | `--working-dir` 选项 |
| `persistSessionData` | `boolean \| unknown` | `--persist-session-data` 选项 |

## IRect 接口

窗口矩形：

```typescript
interface IRect {
  x: number;      // 左上角 X 坐标
  y: number;      // 左上角 Y 坐标
  width: number;  // 窗口宽度
  height: number; // 窗口高度
}
```

## 相关概念

- [架构概览](/concepts/01-architecture-overview.md)
- [Python 环境管理](/concepts/05-python-env-management.md)
- [CLI 命令系统](/concepts/07-cli-system.md)
