---
type: Concept
title: 认证与 credential：JSON 协议与 5 个平台实现
description: cargo-credential 的 JSON 进程协议、Credential trait、CacheControl 缓存语义与 provider 配置解析链
tags: [rust, cargo, auth, credential, registry]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# 认证与 credential：JSON 协议与 5 个平台实现

cargo 与 registry 交互（发布、私有 registry 认证）需要凭据（token）。认证子系统采用**进程外 provider 架构**：cargo 主进程通过 JSON 协议与独立的 credential 进程（如 `cargo-credential-1password`）通信，凭据本身不进入 cargo 主进程的持久状态。

credential/README.md 的原文定义（F-cargo-124）：

> "cargo-credential is a generic library to assist writing a credential process. The other directories contain implementations that integrate with specific credential systems."

子系统分两端：

- **协议端**：`credential/cargo-credential`（辅助编写 credential 进程的通用库）+ `src/util/credential/`（cargo 主进程内置的 provider，含 token/paseto/process 适配）
- **实现端**：`credential/` 下 5 个平台 crate（1password、libsecret、macos-keychain、wincred，见[crate 家族](/concepts/01-crate-organization-cli-dispatch.md)）

## Credential trait：进程协议的入口（F-cargo-125）

`credential/cargo-credential/src/lib.rs` 定义的协议接口（:222-240）：

```rust
pub trait Credential {
    fn perform(&self, registry: &RegistryInfo<'_>, action: &Action<'_>,
               args: &[&str]) -> Result<CredentialResponse, Error>;
}
pub fn main(credential: impl Credential);
```

写一个自定义 credential 进程只需：实现 `Credential::perform`，然后把自己的实现传给 `cargo_credential::main`——参数解析、JSON 编解码、协议错误处理全部由库承担。

## JSON 协议：CredentialResponse 与 CacheControl（F-cargo-126/127/128）

响应类型（F-cargo-126）：

```rust
#[serde(tag = "kind", rename_all = "kebab-case", non_exhaustive)]
pub enum CredentialResponse {
    Get {
        token: Secret<String>,
        cache: CacheControl,
        operation_independent: bool,
    },
    Login,
    Logout,
    Unknown,
}
```

三种动作（Get/Login/Logout）对应 `cargo login`/`cargo logout` 与拉取凭据三类请求。`Secret<String>` 包装防止凭据意外泄露到日志。

缓存控制（F-cargo-127）：

```rust
pub enum CacheControl {
    Never,
    Expires { expiration: OffsetDateTime },
    Session,
    Unknown,
}
pub const PROTOCOL_VERSION_1: u32 = 1;  // "Credential process JSON protocol version."
```

`CacheControl` 语义链：`Never`（绝不缓存——每次操作都要重新获取）、`Expires`（带过期时间）、`Session`（本次 cargo 进程内缓存）。这正是 `GlobalContext::credential_cache` 的 `CredentialCacheValue`（含 `expiration: Option<OffsetDateTime>` 与 `operation_independent: bool`，F-cargo-044）的填充协议——provider 声明缓存策略，cargo 主进程执行缓存。

其他公开类型（F-cargo-128）：`CredentialHello`（握手）、`UnsupportedCredential`、`CredentialRequest`、`RegistryInfo`（registry 描述）、`Action`（动作请求）、`LoginOptions`、`Operation`。协议常量 `PROTOCOL_VERSION_1` 表明 JSON 协议有版本协商。

## provider 配置链：谁提供凭据（F-cargo-129）

`src/util/auth/mod.rs` 的 `credential_provider()` 定义 provider 选择链（F-cargo-129）：

- **默认**：`vec![vec!["cargo:token"]]`（token provider，读写 `$CARGO_HOME/credentials.toml`）
- **`-Z asymmetric_token` 时**：`vec![vec!["cargo:token"], vec!["cargo:paseto"]]`（追加 PASETO 非对称 token provider）
- **全局配置**：`registry.global-credential-providers`（读取后 `.rev()` **倒序**逐项 `resolve_credential_alias`——列表先声明者优先）
- **registry 专属**：`credential-provider` 覆盖全局配置

provider 名形如 `cargo:token`（内置）或 `cargo:token:libsecret`（进程外）。别名解析（`resolve_credential_alias`）经 `[credential-alias]` 配置段（F-cargo-042 的顶层键之一）展开——与命令别名（F-cargo-016/031）同一设计哲学。

## 内置 provider（F-cargo-130）

`src/util/credential/mod.rs` 文档自述："Built-in Cargo credential providers"（F-cargo-130），子模块：

- `token` — `cargo:token`，读写 credentials.toml 的默认 provider
- `paseto` — `cargo:paseto`，PASETO 非对称 token（对应 `-Z asymmetric_token`）
- `process` — 进程外 provider 的适配器（JSON 协议的 cargo 侧实现：启动子进程、编解码 CredentialRequest/CredentialResponse）
- `adaptor` — 适配器层

`process` 子模块是协议两端的总装点：它把本篇上文定义的 JSON 协议（CredentialResponse 与 CacheControl）与 5 个平台 crate 连接起来。

## 平台矩阵（交叉引用）

根 Cargo.toml 的平台特定依赖（F-cargo-006）决定哪个平台 crate 被编译进 cargo：Linux → `cargo-credential-libsecret`、macOS → `cargo-credential-macos-keychain`、Windows → `cargo-credential-wincred`。`cargo-credential-1password` 不绑定平台（独立进程协议实现）。

## 认证数据流

```
cargo 需要凭据（publish / 私有 registry）
    │ credential_provider()（F-cargo-129）
    ▼
provider 列表（cargo:token / cargo:paseto / cargo:token:libsecret / ...）
    │ resolve_credential_alias（[credential-alias] 段）
    ▼
GlobalContext::credential_cache 查询（CacheControl 决定命中与否）
    │ miss → util::credential::process 适配器
    ▼
子进程（cargo-credential-libsecret 等，JSON 协议 v1）
    │ CredentialResponse::Get { token, cache, operation_independent }
    ▼
Secret<String> 进入请求（crates-io / RegistrySource）
```

`save_credentials`（F-cargo-045）与 `GlobalContext.credential_values`（F-cargo-043）承担写入端。

## 相关概念

- [GlobalContext 配置系统](/concepts/03-global-context-config.md) — credential_cache 与 credential-alias 配置键
- [Sources 与 registry](/concepts/05-sources-registry.md) — 凭据的消费者
- [Crate 组织与 CLI 分发](/concepts/01-crate-organization-cli-dispatch.md) — 5 个 credential crate 的家族坐标
- [cargo 源码信源登记](/references/cargo-source-map.md) — credential/ 目录与 doc/book 的 credential-provider-protocol 文档坐标
