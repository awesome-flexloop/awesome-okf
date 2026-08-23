---
type: Concept
title: 权限系统
description: deepcode-cli 实现基于作用域的权限模型，定义 10 种权限作用域覆盖文件读写、Git 操作、网络和 MCP，支持 allow/deny/ask 三种策略与合并优先级。
tags: [deepcode-cli, 权限, security, permission-scope, settings]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: deepcode-cli 源码信源
---

# 权限系统

## 权限作用域

deepcode-cli 在 `packages/core/src/settings.ts:26-36` 中定义了 10 种权限作用域：

```typescript
export type PermissionScope =
  | "read-in-cwd"
  | "read-out-cwd"
  | "write-in-cwd"
  | "write-out-cwd"
  | "delete-in-cwd"
  | "delete-out-cwd"
  | "query-git-log"
  | "mutate-git-log"
  | "network"
  | "mcp";
```

### 作用域分类

| 类别 | 作用域 | 说明 |
|------|--------|------|
| 文件读取 | `read-in-cwd` / `read-out-cwd` | 读取工作目录内/外的文件 |
| 文件写入 | `write-in-cwd` / `write-out-cwd` | 写入工作目录内/外的文件 |
| 文件删除 | `delete-in-cwd` / `delete-out-cwd` | 删除工作目录内/外的文件 |
| Git 只读 | `query-git-log` | 查询 Git 历史记录 |
| Git 变更 | `mutate-git-log` | 修改 Git 历史或状态 |
| 网络 | `network` | 发起网络请求 |
| MCP | `mcp` | 调用 MCP 工具 |

权限系统按"工作目录内外"二分，而非简单的读/写分类。每个文件操作作用域都区分 `in-cwd` 和 `out-cwd`。

## 权限配置结构

权限配置位于 `settings.json` 的 `permissions` 字段（`packages/core/src/settings.ts:40-45`）：

```typescript
export type PermissionSettings = {
  allow?: PermissionScope[];
  deny?: PermissionScope[];
  ask?: PermissionScope[];
  defaultMode?: PermissionDefaultMode;
};
```

`defaultMode` 取值为 `"allowAll"` 或 `"askAll"`（`settings.ts:38`）。

### 配置示例

```json
{
  "permissions": {
    "allow": ["read-in-cwd", "query-git-log"],
    "deny": ["delete-out-cwd"],
    "ask": ["write-out-cwd", "network", "mcp"],
    "defaultMode": "allowAll"
  }
}
```

## 默认行为

在未配置任何权限时，`normalizePermissions` 函数（`settings.ts:262-269`）返回：

```typescript
{
  allow: [],
  deny: [],
  ask: [],
  defaultMode: "allowAll",
}
```

这意味着默认模式下，所有权限作用域均被放行，agent 可以读取和写入工作目录内外的文件。

## 设置合并优先级

`mergePermissions` 函数（`settings.ts:271-287`）合并用户级和项目级权限配置：

1. `allow` 列表：用户级与项目级取并集
2. `deny` 列表：用户级与项目级取并集
3. `ask` 列表：用户级与项目级取并集
4. `defaultMode`：项目设置优先，其次用户设置，最后回退到 `"allowAll"`

合并逻辑源码：

```typescript
function mergePermissions(
  userSettings: DeepcodingSettings | null | undefined,
  projectSettings: DeepcodingSettings | null | undefined
): Required<PermissionSettings> {
  const userPermissions = normalizePermissions(userSettings?.permissions);
  const projectPermissions = normalizePermissions(projectSettings?.permissions);
  return {
    allow: mergePermissionLists(userPermissions.allow, projectPermissions.allow),
    deny: mergePermissionLists(userPermissions.deny, projectPermissions.deny),
    ask: mergePermissionLists(userPermissions.ask, projectPermissions.ask),
    defaultMode: projectSettings?.permissions
      ? projectPermissions.defaultMode
      : userSettings?.permissions
        ? userPermissions.defaultMode
        : "allowAll",
  };
}
```

无效的作用域名称会被 `normalizePermissionList`（`settings.ts:229-244`）静默过滤，仅接受 `VALID_PERMISSION_SCOPES` 集合中的值。

## Plan Mode 强制询问

在 Plan Mode 下，以下 5 个高危作用域被强制加入询问列表（`packages/core/src/session.ts:78-84`）：

```typescript
const PLAN_MODE_FORCE_ASK_SCOPES = [
  "write-in-cwd",
  "write-out-cwd",
  "delete-in-cwd",
  "delete-out-cwd",
  "mutate-git-log",
] as const satisfies readonly PermissionScope[];
```

即使这些作用域在 `allow` 列表中，Plan Mode 仍会要求用户确认。

## 非交互模式限制

`--exec` 模式下无法进行权限确认。当会话进入 `ask_permission` 状态时，`runExecMode` 会输出错误并以退出码 1 终止（`packages/cli/src/exec-runner.ts:125-128`）：

```
Execution requires permission confirmation, which is unavailable in --exec mode.
```

错误信息会列出所需权限及原因，并提示：将所需作用域从 `permissions.ask` 移至 `permissions.allow` 可在非交互模式下放行。

## 权限作用域描述

`exec-runner.ts:188-213` 中定义了每个作用域的人类可读描述：

| 作用域 | 描述 |
|--------|------|
| `read-in-cwd` | read files inside the workspace |
| `read-out-cwd` | read files outside the workspace |
| `write-in-cwd` | write files inside the workspace |
| `write-out-cwd` | write files outside the workspace |
| `delete-in-cwd` | delete files inside the workspace |
| `delete-out-cwd` | delete files outside the workspace |
| `query-git-log` | query Git history |
| `mutate-git-log` | change Git history |
| `network` | network access |
| `mcp` | MCP tool access |
| `unknown` | unclassified side effects |

## 设置文件位置

| 级别 | 路径 |
|------|------|
| 用户级 | `~/.deepcode/settings.json` |
| 项目级 | `<projectRoot>/.deepcode/settings.json` |

项目级设置与用户级设置通过 `resolveSettingsSources` 函数合并，项目级优先。

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [三包 monorepo 架构](/concepts/01-architecture.md)
- [MCP 集成](/concepts/03-mcp-integration.md)
- [CLI 命令与会话管理](/concepts/04-cli-commands.md)
