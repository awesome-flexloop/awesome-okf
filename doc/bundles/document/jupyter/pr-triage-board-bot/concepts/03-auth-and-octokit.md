---
okf_version: "0.2"
type: "concept"
title: "GitHub App认证与Octokit配置"
description: "GitHub App认证流程、Octokit插件组合（分页+限流）、私钥管理、限流重试策略与日志配置"
tags: [authentication, github-app, octokit, auth-app, rate-limiting, throttling, private-key]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: main-source
    resource: /references/main-source.md
    title: "入口与CLI源码"
  - id: utils-source
    resource: /references/utils-source.md
    title: "工具函数源码"
  - id: action-yml
    resource: "../../../../../external/libs/jupyter/pr-triage-board-bot/action.yml"
    title: "action.yml"
---

# GitHub App认证与Octokit配置

## 为什么使用GitHub App而非Personal Access Token？

机器人需要读写GitHub Project看板、查询组织成员、读取仓库协作者等权限。使用GitHub App认证相比Personal Access Token（PAT）有以下优势：

1. **细粒度权限**：精确控制App能访问哪些资源（Metadata只读、Members只读、Projects读写）
2. **可安装到组织**：一次安装即可访问组织内所有授权仓库，不需要每个仓库配置token
3. **短期token**：App认证获取的是短期安装token（1小时过期），泄露风险更低
4. **可审计**：App作为独立身份出现在审计日志中，与个人账户分离

## 认证三元组

GitHub App认证需要三个参数：

| 参数 | 说明 | 获取方式 |
|------|------|---------|
| `appId` | GitHub App的数字ID | App设置页面的"App ID"字段 |
| `installationId` | App安装到组织后的安装ID | 安装设置URL末尾的数字 |
| `privateKey` | RSA私钥（PEM格式） | App设置页面生成下载的.pem文件 |

## makeOctokit：创建认证客户端

```typescript
import { Octokit } from "@octokit/core";
import { createAppAuth } from "@octokit/auth-app";
import { paginateGraphQL } from "@octokit/plugin-paginate-graphql";
import { throttling } from "@octokit/plugin-throttling";

function makeOctokit(appId: number, installationId: number, keyPath: string) {
    const PaginatedOctokitConstructor = Octokit.plugin(paginateGraphQL, throttling);
    return new PaginatedOctokitConstructor({
        authStrategy: createAppAuth,
        auth: {
            appId: appId,
            installationId: installationId,
            privateKey: fs.readFileSync(keyPath).toString()
        },
        throttle: { /* 限流回调 */ },
        log: { debug: console.debug, info: console.info, warn: console.warn, error: console.error }
    });
}
```

### Octokit.plugin() 插件组合

`Octokit.plugin()` 将多个插件混入Octokit构造函数，返回新的构造函数。项目使用两个插件：

1. **paginateGraphQL**（`@octokit/plugin-paginate-graphql`）：
   - 添加 `octokit.graphql.paginate()` 方法
   - 自动处理GraphQL分页（通过cursor/pageInfo）
   - 使用方式：`octokit.graphql.paginate(query, variables)` 返回所有页面合并后的结果

2. **throttling**（`@octokit/plugin-throttling`）：
   - 自动处理GitHub API速率限制
   - 根据 `Retry-After` 头等待后重试
   - 需要配置 `onRateLimit` 和 `onSecondaryRateLimit` 回调

### PaginatedOctokit类型

```typescript
export type PaginatedOctokit = Octokit & paginateGraphQLInterface;
```

此类型别名在 `utils.ts` 中定义，作为全项目统一的Octokit类型，确保所有代码都使用了分页插件。

## 私钥管理

私钥文件在运行时通过 `fs.readFileSync(keyPath).toString()` 同步读取：

**本地运行**：通过 `--gh-app-pem-file` 参数指定.pem文件路径。

**GitHub Action运行**：action.yml中的处理流程：

```yaml
# 步骤1：将secret中的私钥写入临时文件
- name: Setup GitHub App Private Key
  run: echo "${{ inputs.gh-app-private-key }}" > private-key.pem
  shell: bash
  working-directory: ${{ github.action_path }}

# 步骤2：运行机器人（使用私钥文件）
- name: Run PR Triage Bot
  run: node dist/src/main.js --gh-app-pem-file private-key.pem ...

# 步骤3：清理私钥文件（always()确保即使失败也执行）
- name: Cleanup private key
  run: rm -f private-key.pem
  shell: bash
  if: ${{ always() }}
```

> ⚠️ **安全要点**：私钥通过GitHub Secrets传递，运行时写入临时文件，使用后立即删除。清理步骤使用 `if: always()` 确保即使机器人运行失败也会删除私钥文件。

## 限流策略

GitHub API有速率限制（REST: 5000次/小时，GraphQL: 5000点/小时）。项目配置了自动重试：

```typescript
throttle: {
    onRateLimit: (retryAfter, options, octokit, retryCount) => {
        octokit.log.warn(`Request quota exhausted for request ${options.method} ${options.url}`);
        if (retryCount < 2) {
            octokit.log.info(`Retrying after ${retryAfter} seconds.`);
            return true;  // 返回true表示允许重试
        }
    },
    onSecondaryRateLimit: (retryAfter, options, octokit, retryCount) => {
        octokit.log.warn(`SecondaryRateLimit detected for request ${options.method} ${options.url}`);
        if (retryCount < 2) {
            octokit.log.info(`Retrying after ${retryAfter} seconds.`);
            return true;
        }
    }
}
```

关键点：
- **主限流**（Rate Limit）：配额耗尽时最多重试2次
- **次级限流**（Secondary Rate Limit）：GitHub检测到滥用模式时的限制，同样重试2次
- 返回 `true` 表示插件自动等待 `retryAfter` 秒后重试
- 返回 `undefined`/不返回 表示不重试，直接抛出错误
- `retryCount` 从0开始，所以 `retryCount < 2` 表示最多重试2次（总共3次尝试）

## 日志配置

```typescript
log: {
    debug: console.debug,
    info: console.info,
    warn: console.warn,
    error: console.error
}
```

Octokit的四个日志级别直接绑定到console对应方法。限流插件使用 `warn` 和 `info` 输出限流事件。项目代码使用 `console.log` 输出进度信息。

## 认证流程示意

```
CLI参数 / Action Inputs
    │
    ├── appId
    ├── installationId
    └── privateKey (从文件读取)
         │
         ▼
  createAppAuth 认证策略
         │
         │ 内部流程：
         │ 1. 使用私钥签名JWT（App身份）
         │ 2. 用JWT换取Installation Access Token
         │ 3. Token自动附加到所有API请求
         │ 4. Token过期自动刷新
         ▼
  认证后的Octokit实例
         │
         ▼
  GraphQL API 调用
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [Project管理类](04-project-class.md)
- [CLI与GitHub Action集成](08-cli-and-action.md)
