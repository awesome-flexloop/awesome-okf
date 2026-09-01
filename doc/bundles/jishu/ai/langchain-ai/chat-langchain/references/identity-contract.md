---
type: reference
scope: chat-langchain
name: identity-contract
version: "0.1.0"
source: https://github.com/langchain-ai/chat-langchain
description: Chat LangChain identity.py 身份合约参考——多区域 Supabase、guest provider、validated_token ingress、actor scoping
---

# Identity 合约参考

本文档描述 `identity.py` 中 `define_identity(...)` 的完整配置。该文件由 MDA 编译器自动发现，`agent.py` 不导入它。

## define_identity 调用

```python
identity = define_identity(
    ingress={"http": {"mode": "validated_token", "providers": _providers()}},
    tenancy="single",
    scoping={"threads": "actor", "memory": "none", "credentials": "agent"},
)
```

| 参数 | 值 | 说明 |
|---|---|---|
| `ingress.http.mode` | `"validated_token"` | 浏览器自带 access token 直接调用部署，MDA 验证 |
| `ingress.http.providers` | `_providers()` | Supabase 多区域 provider + guest provider |
| `tenancy` | `"single"` | 单租户部署 |
| `scoping.threads` | `"actor"` | 线程按 actor（用户 email 或 guest id）隔离 |
| `scoping.memory` | `"none"` | 无跨线程记忆 |
| `scoping.credentials` | `"agent"` | 凭证由 agent 持有 |

## Provider 配置（_providers 函数）

### 区域映射

```python
_REGION_ENV: dict[str, tuple[str, str]] = {
    "us":   ("SUPABASE_URL",       "SUPABASE_ANON_KEY"),
    "eu":   ("SUPABASE_EU_URL",    "SUPABASE_EU_ANON_KEY"),
    "apac": ("SUPABASE_APAC_URL",  "SUPABASE_APAC_ANON_KEY"),
    "aws":  ("SUPABASE_AWS_URL",   "SUPABASE_AWS_ANON_KEY"),
}
```

前端通过 `x-supabase-region` header 传递区域标签。仅配置了对应 URL 环境变量的区域才会注册 provider。

### Supabase Provider

对每个已配置区域：

```python
provider = providers.supabase(url=base.rstrip("/"), introspect=True)
provider["id"] = f"supabase-{region}"
provider["introspect"]["headers"] = {"apikey": "${" + key_env + "}"}
```

关键配置：

- **`introspect=True`**：使用 `/auth/v1/user` 端点内省验证 token，而非 JWKS 验证。这是因为 US/EU 区域的 JWKS 为空（legacy HS256 token），无法通过公钥验证。
- **`discovery_url`**：由 `providers.supabase` 自动解析真实的 `*.supabase.co` issuer，用于多 provider 路由（自定义 auth domain 场景下必需）。
- **introspect headers**：apikey 通过 `${ENV_VAR}` 语法从环境变量注入，不在代码中硬编码。

### Guest Provider

```python
providers.guest(ttl="24h", actor_prefix="guest:")
```

匿名访客 provider：

- MDA 自行签发和验证签名 guest token（HS256，密钥来自 `MDA_GUEST_SIGNING_KEY` 环境变量）。
- 替代了旧版前端的 guest token 签发路由，前端改为调用部署的 `POST /identity/guest` 端点。
- Guest token 有效期 24 小时，actor id 以 `guest:` 为前缀。

## 与旧版 auth.py 的对应关系

| 旧 `src/api/auth.py` | 新 `identity.py` / 中间件 |
|---|---|
| Supabase JWT 验证逻辑 | `providers.supabase(introspect=True)` |
| Guest token 签发端点 | `providers.guest(ttl="24h")` + `POST /identity/guest` |
| `@auth.on.threads` owner 标记 | `scoping={"threads": "actor"}` |
| `validate_inputs` 输入截断 | `IngressGuardsMiddleware`（agent 中间件层） |
| Trace metadata 注入 | `define_deep_agent(metadata=...)` |

## 环境变量

| 变量 | 用途 |
|---|---|
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` | US 区域 Supabase 项目 |
| `SUPABASE_EU_URL` / `SUPABASE_EU_ANON_KEY` | EU 区域 |
| `SUPABASE_APAC_URL` / `SUPABASE_APAC_ANON_KEY` | APAC 区域 |
| `SUPABASE_AWS_URL` / `SUPABASE_AWS_ANON_KEY` | AWS 区域 |
| `MDA_GUEST_SIGNING_KEY` | Guest token HS256 签名密钥 |

## 相关文档

- Agent 入口参考
- 架构总览
- 事实清单
