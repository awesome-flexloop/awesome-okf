---
type: Reference
title: "HTTP Handler源码"
description: "API端点路由、Handler动态Mixin替换机制、三类Mixin的组合方式、Swagger文档服务"
tags: [handler, http-api, websocket, tornado, mixin, swagger]
sources:
  - id: base-handlers
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/base/handlers.py"
    title: "base/handlers.py"
  - id: kernel-handlers
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/kernels/handlers.py"
    title: "services/kernels/handlers.py"
  - id: kernelspec-handlers
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/kernelspecs/handlers.py"
    title: "services/kernelspecs/handlers.py"
  - id: session-handlers
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/handlers.py"
    title: "services/sessions/handlers.py"
  - id: api-handlers
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/api/handlers.py"
    title: "services/api/handlers.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
---

# HTTP Handler源码

本信源登记EG所有HTTP Handler的路由注册与动态Mixin替换机制。

## 动态Mixin替换机制 [F-137,F-142]

EG不重写Jupyter Server的Kernel/Session Handler，而是通过遍历 `jupyter_server_handlers.default_handlers`，动态为每个Handler混入三个Mixin。

以kernel handlers为例 [F-137]：

```python
default_handlers: list[tuple] = []
for path, cls in jupyter_server_handlers.default_handlers:
    if cls.__name__ in globals():
        # 如果EG中定义了同名Handler类，直接使用
        default_handlers.append((path, globals()[cls.__name__]))
    else:
        # 否则动态创建混入三个Mixin的子类
        bases = (TokenAuthorizationMixin, CORSMixin, JSONErrorsMixin, cls)
        default_handlers.append((path, type(cls.__name__, bases, {})))
```

Session handlers采用相同机制 [F-142]。这种设计确保：
1. 与Jupyter Server完全兼容（API路径不变）
2. 所有Handler自动获得Token认证、CORS处理、JSON错误响应
3. EG自定义的Handler类（如MainKernelHandler/ZMQChannelsHandler）优先使用

## API端点路由表

### 基础端点 [F-131,F-132,F-133]

| 路径 | Handler | 方法 | 说明 |
|------|---------|------|------|
| `/api` | APIVersionHandler | GET | 返回版本信息 `{"version": jupyter_version, "gateway_version": eg_version}` |
| `/(.*)` | NotFoundHandler | * | 404兜底 |

### Kernel端点 [F-134,F-135,F-136]

| 路径 | Handler | 方法 | 说明 |
|------|---------|------|------|
| `/api/kernels` | MainKernelHandler | GET | 列出内核（受list_kernels控制） |
| `/api/kernels` | MainKernelHandler | POST | 创建新内核 |
| `/api/kernels/{kernel_id}` | KernelHandler | GET | 查询内核状态 |
| `/api/kernels/{kernel_id}` | KernelHandler | DELETE | 关闭内核 |
| `/api/kernels/{kernel_id}/channels` | ZMQChannelsHandler | WebSocket | ZMQ通道WebSocket代理 |

`MainKernelHandler` 的POST流程：
1. 解析请求体获取kernelspec name和env
2. 调用 `kernel_manager.start_kernel()`
3. 返回kernel模型（含id、name、WebSocket连接URL）

`ZMQChannelsHandler` 负责WebSocket连接代理：
1. 客户端WebSocket连接 → 验证kernel_id
2. 建立到内核5个ZMQ通道（shell/iopub/stdin/hb/control）的连接
3. 双向转发消息（WebSocket ↔ ZMQ）
4. 若配置了SSH隧道，通过隧道连接ZMQ端口

### KernelSpec端点 [F-138,F-139,F-140,F-141]

| 路径 | Handler | 方法 | 说明 |
|------|---------|------|------|
| `/api/kernelspecs` | MainKernelSpecHandler | GET | 列出所有kernelspec |
| `/api/kernelspecs/{name}` | KernelSpecHandler | GET | 获取单个kernelspec |
| `/api/kernelspecs/{name}/resources/(.+)` | KernelSpecResourceHandler | GET | 获取kernelspec资源文件 |

### API文档端点 [F-143,F-144,F-145,F-146]

| 路径 | Handler | 说明 |
|------|---------|------|
| `/api/swagger.json` | SpecJsonHandler | Swagger JSON规范 |
| `/api/swagger.yaml` | APIYamlHandler | Swagger YAML规范 |
| `/api/swagger` | (redirect) | 重定向到swagger.json |

`BaseSpecHandler` 继承 `CORSMixin` 和 `tornado.web.StaticFileHandler`，提供Swagger spec静态文件服务。

## EG自定义Handler类

### MainKernelHandler [F-134]

继承TokenAuthorizationMixin, CORSMixin, JSONErrorsMixin和Jupyter Server的MainKernelHandler。覆写post/get方法添加EG特有逻辑：
- POST时从env中提取KERNEL_USERNAME
- GET时检查list_kernels配置，非管理员只能看到自己的内核

### ZMQChannelsHandler [F-136]

继承三个Mixin和Jupyter Server的ZMQChannelsHandler。添加：
- EG_COMM通道支持（中断通知launcher）
- SSH隧道连接逻辑
- 内核用户名验证

### KernelHandler [F-135]

添加DELETE时清理session，REST方法用于中断内核。
