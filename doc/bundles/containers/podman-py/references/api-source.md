---
type: Reference
title: "api/ HTTP 传输层实现"
description: "APIClient HTTP 客户端、APIResponse 错误映射、传输适配器（UDS/SSH/TCP）与工具函数。"
tags: [podman-py, APIClient, api, http, uds, ssh, adapter, requests]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: api-init
    resource: podman/api/__init__.py
    title: podman/api/__init__.py
  - id: api-client-py
    resource: podman/api/client.py
    title: podman/api/client.py
  - id: uds-py
    resource: podman/api/uds.py
    title: podman/api/uds.py
  - id: ssh-py
    resource: podman/api/ssh.py
    title: podman/api/ssh.py
---

# API 传输层实现

## 模块导出（podman/api/__init__.py）

| 导出 | 说明 |
|------|------|
| `APIClient` | HTTP 客户端主类 |
| `VERSION` | API 版本 |
| `COMPATIBLE_VERSION` | 兼容版本 |
| `DEFAULT_CHUNK_SIZE` | 默认块大小（2 × 1024 × 1024 = 2MB） |
| `create_tar` | 创建 tar 归档 |
| `decode_header` | 解码头部 |
| `encode_auth_header` | 编码认证头部 |
| `frames` | 帧处理 |
| `parse_repository` | 解析仓库地址 |
| `prepare_body` | 准备请求体 |
| `prepare_cidr` | 准备 CIDR |
| `prepare_containerfile` | 准备 Containerfile |
| `prepare_containerignore` | 准备 .containerignore |
| `prepare_filters` | 准备过滤器参数 |
| `prepare_timestamp` | 准备时间戳 |
| `stream_frames` | 流帧处理 |
| `stream_helper` | 流辅助函数 |

## 目录结构（podman/api/）

| 文件 | 说明 |
|------|------|
| `client.py` | APIClient 类与 APIResponse 类 |
| `ssh.py` | SSHAdapter（SSH 连接适配器） |
| `uds.py` | UDSAdapter（Unix Domain Socket 适配器） |
| `adapter_utils.py` | 适配器工具函数 |
| `api_versions.py` | API 版本常量 |
| `http_utils.py` | HTTP 工具函数 |
| `output_utils.py` | 输出处理工具 |
| `parse_utils.py` | 解析工具函数 |
| `path_utils.py` | 路径工具（含 `get_runtime_dir()`） |
| `tar_utils.py` | Tar 归档工具 |

## APIResponse 类

```python
class APIResponse:
    """代理 requests.Response，重写 raise_for_status() 实现 Podman API 错误映射"""
```

错误映射规则：
- HTTP 404 → 映射到 `NotFound` 异常
- 其他 HTTP 错误 → 映射到 `APIError` 异常

## APIClient 类

```python
class APIClient(requests.Session):
    """Podman REST API HTTP 客户端"""
```

继承自 `requests.Session`，复用 requests 的连接池、Cookie 管理等能力。

### 支持的 URL Scheme

```python
supported_schemes = ["unix", "http+unix", "ssh", "http+ssh", "tcp", "http"]
```

### 传输适配器选择

| Scheme | 适配器 | 说明 |
|--------|--------|------|
| `unix`, `http+unix` | `UDSAdapter` | Unix Domain Socket 本地连接 |
| `ssh`, `http+ssh` | `SSHAdapter` | SSH 隧道远程连接 |
| `tcp`, `http` | `requests.adapters.HTTPAdapter` | 普通 HTTP/TCP 连接 |

## 异常体系（podman/errors/exceptions.py）

| 异常类 | 说明 |
|--------|------|
| `PodmanError` | 基础异常类 |
| `APIError` | API 调用错误 |
| `NotFound` | 资源未找到（404） |
| `ImageNotFound` | 镜像未找到 |
