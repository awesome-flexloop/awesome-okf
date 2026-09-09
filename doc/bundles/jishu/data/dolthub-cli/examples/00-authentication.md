---
type: Example
title: "认证操作示例"
description: "dh auth login/status/logout 与 DH_TOKEN 的实操命令与输出，覆盖浏览器登录、token 认证与登出"
tags: [dh, dolthub, cli, auth, example]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# 认证操作示例

> 本示例覆盖 `dh` 的登录、状态查看、登出与 `DH_TOKEN` 认证。命令形态与源码 README 及命令定义一致。

## 浏览器登录

```sh
./bin/dh auth login
./bin/dh auth status
```

默认 host 为 `www.dolthub.com`（F-017），登录走 OAuth PKCE 浏览器流程（F-028）。若 `DH_HOST` 或配置选了其他 host，可用 `--hostname` 指定生产环境：

```sh
./bin/dh auth login --hostname www.dolthub.com
```

登录成功后输出形如：

```
Logged in to www.dolthub.com as <username>
```

## token 认证（DH_TOKEN）

设置 `DH_TOKEN` 后，命令自动使用该 token（F-024），无需浏览器登录：

```sh
export DH_TOKEN="..."
dh sql --db OWNER/DATABASE --ref main "select 1"
```

> 注意：`DH_TOKEN` 存在时无法执行 `dh auth login`（F-060），需先 `unset DH_TOKEN`。

## 登出

```sh
./bin/dh auth logout
```

登出会从凭据存储删除对应 host/user 的凭据（`FallbackStore.Delete` 同时清理 keyring 与 file 两处，F-026）。

## 覆盖 OAuth client ID

开发或自定义 host 需要自己的 client ID（F-029）：

```sh
DH_OAUTH_CLIENT_ID="your-client-id" dh auth login --hostname your-host.example.com
```

## 相关概念

* [认证与凭据管理](/concepts/02-authentication.md)
* [SQL 查询示例](/examples/01-sql-queries.md)
