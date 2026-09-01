---
okf_version: "0.2"
type: "concept"
title: "安全认证与高可用"
description: "Token认证、CORS跨域、SSL/TLS双向认证、用户模拟与授权、负载均衡、HA模式standalone/replication"
tags: [security, auth, cors, ssl, high-availability, load-balancing, impersonation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: config-mixin
    resource: "/references/config-mixin-source.md"
    title: "配置Mixin源码"
  - id: app-entry
    resource: "/references/app-entry-source.md"
    title: "主应用入口源码"
  - id: session-source
    resource: "/references/session-manager-source.md"
    title: "会话管理源码"
---

# 安全认证与高可用

## Token认证

### 启用Token认证

通过 `EG_AUTH_TOKEN` 环境变量或 `--EnterpriseGatewayApp.auth_token` 配置项设置Token值 [F-033]：

```bash
export EG_AUTH_TOKEN=my-secret-token
jupyter enterprisegateway
```

Token为空（默认）时不启用认证。

### Token传递方式 [F-055]

客户端可以通过两种方式传递Token：

1. **URL参数**：
   ```
   GET /api?token=my-secret-token
   ```

2. **Authorization头**：
   ```
   Authorization: token my-secret-token
   ```

> 注意：EG使用的Token前缀是 `"token "`，不是 `"Bearer "`。

Token认证由 [TokenAuthorizationMixin](../references/config-mixin-source.md) 在每个请求的 `prepare()` 方法中执行，在所有其他Handler逻辑之前拦截未认证请求。

## CORS跨域配置 [F-034]

当Notebook前端和EG运行在不同的域/端口时，需要配置CORS。

### 基本配置

```bash
# 允许的Origin（设为Notebook服务器地址，或*允许所有）
export EG_ALLOW_ORIGIN="https://notebook.example.com"

# 允许凭证（cookies、Authorization头等）
export EG_ALLOW_CREDENTIALS="true"

# 允许的请求头
export EG_ALLOW_HEADERS="Authorization,Content-Type"

# 允许的HTTP方法
export EG_ALLOW_METHODS="GET,POST,DELETE,OPTIONS"
```

CORS头由 [CORSMixin](../references/config-mixin-source.md) 在 `set_default_headers()` 中自动设置 [F-052]。

### CORS预检请求

OPTIONS请求由CORSMixin.options()直接返回200，不需要Handler处理 [F-053]。

## SSL/TLS配置 [F-035]

### 单向TLS（服务器证书）

```bash
export EG_CERTFILE=/path/to/server.crt
export EG_KEYFILE=/path/to/server.key
jupyter enterprisegateway
```

### 双向TLS（客户端证书验证） [F-022]

```bash
export EG_CERTFILE=/path/to/server.crt
export EG_KEYFILE=/path/to/server.key
export EG_CLIENT_CA=/path/to/client-ca.crt
jupyter enterprisegateway
```

配置client_ca后，SSL verify_mode设置为CERT_REQUIRED，客户端必须提供由CA签发的证书。

### SSL版本

默认使用PROTOCOL_TLSv1_2 [F-035]，可通过EG_SSL_VERSION配置。

### 主机名验证 [F-026]

配置 `EG_AUTHORIZED_ORIGIN` 后，EG会在SSL握手后验证客户端证书中的hostname是否匹配authorized_origin。不匹配则返回403 Forbidden。

## 用户授权 [F-041,F-066]

### 禁止用户列表

```bash
# 默认禁止root用户
export EG_UNAUTHORIZED_USERS="root,admin"
```

KERNEL_USERNAME在unauthorized_users中时，内核启动请求返回403。默认禁止root用户。

### 允许用户列表

```bash
# 只允许alice和bob启动内核
export EG_AUTHORIZED_USERS="alice,bob"
```

authorized_users非空时，只有列表中的用户可以启动内核。空集合（默认）表示允许所有用户（unauthorized_users中的除外）。

授权检查在两处执行：
1. `BaseProcessProxyABC._enforce_authorization()` — 进程启动前检查 [F-066]
2. `MainKernelHandler` — API层检查

### 用户模拟（Impersonation）[F-041]

```bash
export EG_IMPERSONATION_ENABLED=true
```

启用后，EG会以KERNEL_USERNAME指定的用户身份启动远程内核进程（在支持用户切换的平台上，如YARN、SSH）。这确保内核进程以请求用户的权限运行，实现资源隔离和审计。

## 内核资源限制 [F-036,F-111]

### 全局内核限额

```bash
export EG_MAX_KERNELS=100    # 最多同时运行100个内核
```

### 每用户限额

```bash
export EG_MAX_KERNELS_PER_USER=5  # 每个用户最多5个内核
```

限额检查包含pending中的启动请求，防止并发请求绕过限制。计数逻辑：
- 全局：`活跃内核数 + pending启动数 >= max_kernels` → 403
- 每用户：`用户活跃数 + 用户pending数 >= max_kernels_per_user` → 403

### 内核列表可见性

```bash
export EG_LIST_KERNELS=false  # 默认：用户只能看到自己的内核
```

设为true时允许任何用户通过GET /api/kernels查看所有内核。false时只返回当前用户的内核。

## 环境变量安全

### 敏感信息过滤 [F-124]

`_launch_kernel()` 中显式移除EG_AUTH_TOKEN和KG_AUTH_TOKEN环境变量，防止认证Token泄露到内核进程：

```python
env.pop("EG_AUTH_TOKEN", None)
env.pop("KG_AUTH_TOKEN", None)
```

### 环境变量白名单 [F-037]

- `EG_CLIENT_ENVS`：允许客户端从HTTP请求中传入的环境变量（黑名单安全模型改为白名单）
- `EG_INHERITED_ENVS`：EG进程继承并传递给内核的环境变量

默认情况下，只有白名单中的环境变量会被传递给内核进程。

## 负载均衡 [F-038,F-078]

### 远程主机配置

```bash
export EG_REMOTE_HOSTS="host1.example.com,host2.example.com,host3.example.com"
```

### 负载均衡算法 [F-049]

```bash
# 轮询（默认）
export EG_LOAD_BALANCING_ALGORITHM=round-robin

# 最少连接
export EG_LOAD_BALANCING_ALGORITHM=least-connection
```

- **round-robin**：依次选择主机，均匀分配
- **least-connection**：TrackKernelOnHost跟踪每台主机上的内核数，选择内核最少的主机

负载均衡由 `DistributedProcessProxy` 实现 [F-077,F-078]。内部类TrackKernelOnHost维护主机→内核数映射，启动内核时increment，关闭时decrement。

## 高可用（HA）模式 [F-044,F-027,F-028]

### 模式选择

```bash
# 模式1：standalone（单实例启动恢复）
export EG_AVAILABILITY_MODE=standalone

# 模式2：replication（多实例懒加载恢复）
export EG_AVAILABILITY_MODE=replication
```

### standalone模式

**适用场景**：单实例部署，EG重启后自动恢复内核。

**工作方式**：
1. EG启动时检查持久化session目录
2. 调用 `kernel_session_manager.start_sessions()` 批量恢复所有session
3. 对每个session：重建ProcessProxy→load_process_info→poll确认存活→重建ZMQ连接
4. 启动完成后所有内核已就绪，可以接收请求

**优点**：请求到达时内核已就绪，无恢复延迟
**缺点**：启动时间随内核数量线性增长；不支持多实例

### replication模式

**适用场景**：多EG实例部署（如K8s多副本），任何实例都可以处理任何内核请求。

**工作方式**：
1. EG启动时不主动恢复内核
2. 请求到达时，`check_kernel_id(kernel_id)` 检查内核是否在内存中
3. 不在内存中 → `_refresh_kernel(kernel_id)` 从持久化存储加载session
4. 调用 `start_kernel_from_session()` 懒加载恢复内核
5. 恢复成功后继续处理请求

**优点**：支持多实例水平扩展；启动快
**缺点**：首次访问已恢复内核时有恢复延迟

### HA与持久化联动 [F-027]

HA模式和持久化自动联动：
- 启用persistence但未设置availability_mode → 自动设为replication
- 设置availability_mode但未启用persistence → 自动启用persistence

无需手动配置两者。

### 自定义授权器类 [F-033]

```python
# jupyter_enterprisegateway_config.py
c.EnterpriseGatewayApp.authorizer_class = "mymodule.MyAuthorizer"
```

通过authorizer_class配置项可以替换默认的AllowAllAuthorizer，实现自定义授权逻辑（如对接企业IAM系统）。
