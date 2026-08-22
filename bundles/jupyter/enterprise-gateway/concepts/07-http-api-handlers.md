---
okf_version: "0.2"
type: "concept"
title: "HTTP API体系"
description: "HTTP端点路由、Handler动态Mixin替换机制、Token认证/CORS/JSON错误处理、Swagger API文档、WebSocket代理"
tags: [http-api, handler, tornado, websocket, cors, auth, mixin, swagger]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: handlers
    resource: "/references/handlers-source.md"
    title: "HTTP Handler源码"
  - id: config-mixin
    resource: "/references/config-mixin-source.md"
    title: "配置Mixin源码"
---

# HTTP API体系

Enterprise Gateway基于Tornado提供RESTful HTTP API，完全兼容Jupyter Server的API规范。EG通过**动态Mixin替换**机制，在不重写Jupyter Server Handler的前提下，为所有API端点统一添加认证、CORS和错误处理。

## 动态Mixin替换机制 [F-137,F-142]

这是EG Handler体系的核心设计模式。EG不继承Jupyter Server的Handler类然后覆写，而是在启动时遍历Jupyter Server的handler列表，动态创建混入三个Mixin的新类。

```python
default_handlers = []
for path, cls in jupyter_server_handlers.default_handlers:
    if cls.__name__ in globals():
        # EG中有自定义实现的Handler，直接使用
        default_handlers.append((path, globals()[cls.__name__]))
    else:
        # 动态创建混入三个Mixin的子类
        bases = (TokenAuthorizationMixin, CORSMixin, JSONErrorsMixin, cls)
        new_cls = type(cls.__name__, bases, {})
        default_handlers.append((path, new_cls))
```

这种设计的优势：
1. **零修改兼容**：Jupyter Server的Handler代码完全不需要修改
2. **统一横切关注点**：所有Handler自动获得认证/CORS/错误处理
3. **可选择性覆写**：需要特殊处理的Handler（如MainKernelHandler）在globals()中定义，优先使用
4. **版本兼容**：Jupyter Server升级Handler逻辑时，EG自动继承新行为

### MRO顺序

```python
class MainKernelHandler(TokenAuthorizationMixin, CORSMixin, JSONErrorsMixin, JupyterMainKernelHandler):
```

方法解析顺序：TokenAuthorizationMixin → CORSMixin → JSONErrorsMixin → Jupyter原生Handler。这意味着：
- prepare()最先执行Token认证（最先拦截未授权请求）
- set_default_headers()由CORSMixin设置CORS头
- write_error()由JSONErrorsMixin返回JSON格式错误
- 如果EG自定义Handler覆写了这些方法，可以通过super()调用Mixin逻辑

## 三类Handler Mixin

### TokenAuthorizationMixin [F-054,F-055]

在 `prepare()` 方法中执行Token认证：
1. 检查 `self.settings.get('eg_auth_token')` 是否设置
2. 未设置 → 直接放行（无认证模式）
3. 已设置 → 从以下位置获取客户端token：
   - URL参数：`?token=<value>`
   - Authorization头：`Authorization: token <value>`
4. 比较token值，不匹配 → `send_error(401)`

注意header_prefix是 `"token "`（不是"Bearer "），这与Jupyter Notebook的认证方式一致。

### CORSMixin [F-051,F-052,F-053]

- `set_default_headers()`：从settings中读取EG_CORS配置，设置6个CORS响应头
- `options()`：直接 `self.finish()` 处理CORS预检请求
- 调用 `clear_header("Content-Security-Policy")` 禁用CSP（Notebook前端需要加载各种资源）

SETTINGS_TO_HEADERS映射：
| settings key | HTTP header |
|-------------|-------------|
| eg_allow_credentials | Access-Control-Allow-Credentials |
| eg_allow_headers | Access-Control-Allow-Headers |
| eg_allow_methods | Access-Control-Allow-Methods |
| eg_allow_origin | Access-Control-Allow-Origin |
| eg_expose_headers | Access-Control-Expose-Headers |
| eg_max_age | Access-Control-Max-Age |

### JSONErrorsMixin [F-056]

`write_error(status_code, **kwargs)` 返回统一的JSON错误格式：
```json
{
  "reason": "Not Found",
  "message": "Kernel does not exist"
}
```
非HTTPError异常（如代码bug）会附加traceback字段便于调试。

## API端点一览

### 版本与文档 [F-131,F-143~F-146]

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api` | 返回版本信息 `{"version": "...", "gateway_version": "..."}` |
| GET | `/api/swagger.json` | Swagger JSON规范 |
| GET | `/api/swagger.yaml` | Swagger YAML规范 |
| GET | `/api/swagger` | 重定向到swagger.json |

APIVersionHandler是EG自定义的Handler，直接继承三个Mixin和APIHandler [F-131]。

### 内核管理 [F-134~F-137]

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/kernels` | 列出内核（受list_kernels配置控制） |
| POST | `/api/kernels` | 创建新内核 |
| GET | `/api/kernels/{kernel_id}` | 查询内核状态 |
| DELETE | `/api/kernels/{kernel_id}` | 关闭并删除内核 |
| POST | `/api/kernels/{kernel_id}/interrupt` | 中断内核（SIGINT） |
| POST | `/api/kernels/{kernel_id}/restart` | 重启内核 |
| WS | `/api/kernels/{kernel_id}/channels` | WebSocket连接ZMQ通道 |

**GET /api/kernels** 的list_kernels控制 [F-134]：
- `list_kernels=False`（默认）：普通用户只能看到自己的内核
- `list_kernels=True`：允许列出所有用户的内核

**POST /api/kernels** 请求体：
```json
{
  "name": "python_kubernetes",
  "env": {
    "KERNEL_USERNAME": "alice",
    "MY_VAR": "my_value"
  },
  "path": "/notebooks/mynb.ipynb"
}
```

**WebSocket /channels** 端点 [F-136]：
- 这是Notebook前端与内核通信的核心通道
- ZMQChannelsHandler代理WebSocket与ZMQ之间的消息
- 支持EG_COMM通道向launcher发送中断通知
- 远程内核通过SSH隧道连接ZMQ端口
- ws_ping_interval配置WebSocket心跳间隔 [F-042]

### 内核规范 [F-138~F-141]

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/kernelspecs` | 列出所有kernelspec |
| GET | `/api/kernelspecs/{name}` | 获取指定kernelspec |
| GET | `/api/kernelspecs/{name}/resources/{path}` | 获取kernelspec资源（logo/kernel.js等） |

返回示例（GET /api/kernelspecs）：
```json
{
  "default": "python3",
  "kernelspecs": {
    "python_kubernetes": {
      "name": "python_kubernetes",
      "spec": {
        "argv": [...],
        "display_name": "Python on Kubernetes",
        "language": "python",
        "metadata": {
          "process_proxy": {
            "class_name": "...KubernetesProcessProxy",
            "config": {...}
          }
        }
      },
      "resources": {...}
    }
  }
}
```

### 会话管理 [F-142]

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions` | 列出所有会话 |
| POST | `/api/sessions` | 创建新会话（含创建内核） |
| GET | `/api/sessions/{session_id}` | 查询会话 |
| PATCH | `/api/sessions/{session_id}` | 更新会话（如重连时更新path） |
| DELETE | `/api/sessions/{session_id}` | 删除会话（关闭内核） |

Session handlers也采用动态Mixin替换机制 [F-142]。

## Handler注册顺序 [F-016]

`_create_request_handlers()` 中五类handler的拼接顺序很重要——Tornado按注册顺序匹配路由：

1. **api handlers**（/api/swagger.*）— Swagger文档
2. **kernel handlers**（/api/kernels.*）— 内核API
3. **kernelspec handlers**（/api/kernelspecs.*）— 内核规范API
4. **session handlers**（/api/sessions.*）— 会话API
5. **base handlers**（/api和/(.*)）— 版本查询和404兜底

`/(.*)` 路由在最后，作为404兜底（NotFoundHandler）[F-132]。每个handler的pattern自动加上base_url前缀。

## settings注入

init_webapp()创建Application时，在settings中注入的EG特有配置 [F-017]：

- 认证：`eg_auth_token`, `eg_authorized_users`, `eg_unauthorized_users`
- CORS：`eg_allow_credentials`, `eg_allow_headers`, `eg_allow_methods`, `eg_allow_origin`, `eg_expose_headers`, `eg_max_age`
- 内核限制：`eg_max_kernels`, `eg_list_kernels`
- 环境传递：`eg_inherited_envs`, `eg_client_envs`, `eg_kernel_headers`
- WebSocket：`ws_ping_interval`
- 特殊标志：`allow_remote_access=True`（Jupyter Server默认False，EG需要允许远程访问）
