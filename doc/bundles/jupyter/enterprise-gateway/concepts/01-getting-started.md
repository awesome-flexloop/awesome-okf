---
okf_version: "0.2"
type: "concept"
title: "5分钟快速上手"
description: "安装Enterprise Gateway、本地启动服务、通过API创建内核并执行代码的最小示例"
tags: [getting-started, install, cli, quickstart, local]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: app-entry
    resource: "/references/app-entry-source.md"
    title: "主应用入口源码"
  - id: config-mixin
    resource: "/references/config-mixin-source.md"
    title: "配置Mixin源码"
---

# 5分钟快速上手

## 安装

使用pip安装Enterprise Gateway：

```bash
pip install enterprise-gateway
```

这将安装 `enterprise_gateway` Python包和 `jupyter-enterprise-gateway` CLI命令 [F-004]。

安装前确保已安装Jupyter相关依赖（jupyter_client、jupyter_core、jupyter_server、tornado、pyzmq、ipykernel等）。

## 启动服务

最简单的本地启动方式：

```bash
jupyter enterprisegateway --ip=0.0.0.0 --port=8888
```

启动成功后会看到日志输出 [F-030]：
```
[I ...] Jupyter Enterprise Gateway 3.4.0.dev0 is available at http://0.0.0.0:8888
```

关键参数说明（参见 [配置体系详解](03-app-and-config.md)）：

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `--ip` | 127.0.0.1 | 监听IP地址 [F-032] |
| `--port` | 8888 | 监听端口 [F-032] |
| `--port_retries` | 50 | 端口被占用时的重试次数 [F-032] |
| `--debug` | False | 开启debug日志 |

如果希望外部可访问，使用 `--ip=0.0.0.0`。

## 验证服务状态

启动后可以通过API验证服务是否正常：

```bash
# 查看版本信息
curl http://localhost:8888/api
```

返回：
```json
{
  "version": "<jupyter_server_version>",
  "gateway_version": "3.4.0.dev0"
}
```

这个端点由 [APIVersionHandler](/references/handlers-source.md) 处理 [F-131]。

## 查看可用内核

```bash
curl http://localhost:8888/api/kernelspecs
```

返回所有已注册的kernelspec列表，每个kernelspec包含：
- `name`：内核名称
- `display_name`：显示名
- `language`：编程语言
- `spec`：启动命令、环境变量、metadata（含process_proxy配置）

## 创建并使用内核

```bash
# 创建一个Python内核
curl -X POST http://localhost:8888/api/kernels \
  -H "Content-Type: application/json" \
  -d '{"name": "python3"}'
```

返回内核信息（示例）：
```json
{
  "id": "a1b2c3d4-...",
  "name": "python3",
  "last_activity": "...",
  "connections": 0,
  "execution_state": "starting"
}
```

创建内核的完整流程参见 [内核启动流程详解](09-kernel-launch-flow.md)。

创建成功后，可以通过WebSocket连接到 `/api/kernels/{kernel_id}/channels` 发送代码执行请求并接收结果。这需要Jupyter的Wire Protocol，实际使用中通常由Notebook前端（JupyterLab/Notebook）自动处理。

## 使用环境变量配置

EG的所有配置项都支持环境变量（`EG_*` 前缀）[F-047]。例如：

```bash
# 设置最大内核数
export EG_MAX_KERNELS=10

# 设置每用户最大内核数
export EG_MAX_KERNELS_PER_USER=3

# 禁止列出其他用户的内核
export EG_LIST_KERNELS=False

# 启动
jupyter enterprisegateway --ip=0.0.0.0
```

## 使用Token认证

```bash
# 启动时设置Token
export EG_AUTH_TOKEN=my-secret-token
jupyter enterprisegateway --ip=0.0.0.0

# 请求时携带Token
curl -H "Authorization: token my-secret-token" http://localhost:8888/api
# 或通过URL参数
curl http://localhost:8888/api?token=my-secret-token
```

Token认证由 [TokenAuthorizationMixin](/references/config-mixin-source.md) 处理 [F-054,F-055]。

## 下一步

- 了解EG的整体架构 → [架构总览](02-architecture-overview.md)
- 配置项完整参考 → [应用入口与配置体系](03-app-and-config.md)
- 远程内核部署 → [部署模式与Kernel Launcher](10-deployment-modes.md)
- 本地实战示例 → [本地启动EG并执行代码](/examples/01-start-eg-locally.md)
