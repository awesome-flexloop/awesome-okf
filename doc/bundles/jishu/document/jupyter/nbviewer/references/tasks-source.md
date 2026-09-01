---
type: Reference
title: "Invoke任务源码（tasks.py）"
description: "tasks.py中FastlyService类和invoke任务的完整API解析：fastly CDN管理、trigger-build触发、doitall全流程、upgrade未实现"
tags: [nbviewer, deploy, invoke, tasks, fastly, cdn, pyinvoke]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tasks-py
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/tasks.py"
    title: "tasks.py"
---

# Invoke任务源码（tasks.py）

本信源登记 `tasks.py` 中定义的所有类、方法和 invoke 任务。

## 概述

`tasks.py` 使用 [pyinvoke](https://www.pyinvoke.org/) 框架定义命令行任务，主要用于管理 Fastly CDN 后端配置和触发 Docker 构建。

**凭据加载方式**：

```python
creds = {}
with open("creds") as f:
    exec(f.read(), creds)
```

通过 `exec()` 执行 `creds` 文件（git-crypt加密），将凭据变量加载到 `creds` 字典中。不使用硬编码常量（如 SERVICE_ID）。

## FastlyService 类

`FastlyService` 类（位于 tasks.py 第49-110行）封装了 Fastly CDN API 操作。

### 构造函数

```python
def __init__(self, api_key, service_id):
```

| 参数 | 来源 | 说明 |
|------|------|------|
| `api_key` | `creds["FASTLY_KEY"]` | Fastly API密钥 |
| `service_id` | `creds["FASTLY_SERVICE_ID"]` | Fastly服务ID |

构造逻辑：
1. 创建 `requests.Session`，设置 `Fastly-Key` 请求头
2. 获取最新版本号 `self.version`
3. 如果最新版本处于 `active` 状态，先克隆一个新版本进行编辑

### 方法列表

| 方法 | HTTP方法 | API路径 | 说明 |
|------|---------|---------|------|
| `api_request(path, include_version, method, **kwargs)` | 动态 | 动态构造 | 通用API请求方法 |
| `backends()` | GET | `/backend` | 获取所有后端列表 |
| `versions()` | GET | `/version`（不含版本号） | 获取所有版本列表 |
| `add_backend(name, hostname, port, copy_backend)` | POST | `/backend` | 添加后端 |
| `remove_backend(name)` | DELETE | `/backend/{name}` | 删除指定后端 |
| `deploy()` | PUT | `/activate` 然后 `/clone` | 激活当前版本并克隆新版本 |

### api_request 方法详解

```python
def api_request(self, path, include_version=True, method="GET", **kwargs):
    url = "{api}/service/{service_id}{v}{path}".format(
        api=FASTLY_API,
        service_id=self.service_id,
        v=f"/version/{self.version}" if include_version else "",
        path=path,
    )
    r = self.session.request(method, url, **kwargs)
    try:
        r.raise_for_status()
    except Exception:
        print(r.text)
        raise
    return r.json()
```

- `FASTLY_API = "https://api.fastly.com"`
- URL构造模式：`https://api.fastly.com/service/{service_id}/version/{version}{path}`
- 错误处理：打印响应文本后抛出异常

### add_backend 方法（copy_backend模式）

```python
def add_backend(self, name, hostname, port, copy_backend=None):
    if copy_backend is None:
        copy_backend = self.backends()[0]
    data = {
        key: copy_backend[key]
        for key in [
            "healthcheck",
            "max_conn",
            "weight",
            "error_threshold",
            "connect_timeout",
            "between_bytes_timeout",
            "first_byte_timeout",
            "auto_loadbalance",
        ]
    }
    data.update({"address": hostname, "name": name, "port": port})
    self.api_request("/backend", method="POST", data=data)
```

**关键设计：copy-backend模式**。新后端复制现有后端的配置（healthcheck、超时、权重等），只覆盖 `address`、`name`、`port` 三个字段。这确保所有后端使用相同的健康检查和负载均衡配置。

复制的配置字段：
- `healthcheck`：健康检查配置
- `max_conn`：最大连接数
- `weight`：负载均衡权重
- `error_threshold`：错误阈值
- `connect_timeout`：连接超时
- `between_bytes_timeout`：字节间超时
- `first_byte_timeout`：首字节超时
- `auto_loadbalance`：自动负载均衡

### deploy 方法

```python
def deploy(self):
    self.api_request("/activate", method="PUT")  # 激活当前版本
    self.api_request("/clone", method="PUT")      # 克隆新版本
    self.version = self.versions()[-1]["number"] # 更新版本号
```

部署流程：激活当前编辑版本 → 克隆新版本供后续编辑 → 更新内部版本号。

## all_instances() 函数

```python
def all_instances():
    """Return {(ip, port) : name} for all running nbviewer containers on all machines"""
    all_nbviewers = {}
    # add ovh by hand
    # TODO: get service from kubernetes
    all_nbviewers[("135.125.83.237", 80)] = "ovh"
    return all_nbviewers
```

**重要事实**：
- 返回字典 `{(ip, port): name}`，目前只有一个硬编码条目
- IP地址 `135.125.83.27:80`（OVH Cloud）是硬编码的
- 代码中标注了TODO：应从Kubernetes自动获取服务IP
- 没有Kubernetes服务发现功能
- README中提到：当IP变更时需手动更新此函数，然后运行 `invoke fastly`

## Invoke 任务列表

### 1. trigger_build

```python
@task
def trigger_build(ctx):
```

触发 Docker Hub 自动构建：
- 向 `https://hub.docker.com/api/build/v1/source/579ab043-912f-425b-8b3f-765ee6143b53/trigger/{DOCKER_TRIGGER_TOKEN}/call/` 发送POST请求
- 使用 `creds["DOCKER_TRIGGER_TOKEN"]`

### 2. doitall

```python
@task
def doitall(ctx):
```

完整升级流程（从本地笔记本执行）：
1. `git pull` — 确保仓库最新
2. `upgrade(ctx)` — 执行Helm升级（**注意：upgrade目前抛出NotImplementedError**）
3. `fastly(ctx)` — 更新Fastly CDN后端

**注意**：由于 `upgrade()` 未实现，`doitall` 实际上无法正常完成。

### 3. upgrade

```python
@task
def upgrade(ctx, yes=False):
    """Update helm deployment"""
    raise NotImplementedError("Not implemented yet for helm")
```

**重要事实**：此任务**未实现**，抛出 `NotImplementedError`。Helm部署通过 `deploy.sh` 脚本和 GitHub Actions CI 执行，不是通过 invoke 任务。

### 4. fastly（唯一可用的CDN管理任务）

```python
@task
def fastly(ctx):
    """Update the fastly CDN"""
```

Fastly CDN后端同步逻辑：
1. 创建 `FastlyService` 实例
2. 获取当前所有后端和期望的实例列表
3. **删除阶段**：遍历现有后端，如果 `(address, port)` 不在期望列表中，删除该后端
4. **添加阶段**：遍历期望实例，如果 `(ip, port)` 不在现有后端中，使用 `add_backend` 添加（复制第一个现有后端的配置）
5. 如果有变更，调用 `f.deploy()` 激活配置；否则输出 "Fastly OK"

**不存在的任务**：
- ❌ `lock-cdn`：不存在
- ❌ `unlock-cdn`：不存在
- ❌ `sync-cdn-backends`：不存在（功能由 `fastly` 任务实现）

## Fastly CDN 架构

```
当前Fastly后端 ←→ all_instances()期望状态
      │                │
      ├─ 不在期望中 → 删除后端
      └─ 缺失的后端 → 添加后端(copy-backend模式)
                           │
                    有变更? ──是→ f.deploy() (激活+克隆)
                           │
                           └─否→ 输出"Fastly OK"
```

## 相关信源

- [部署配置文件源码](config-source.md)
- [Helm部署流程](../concepts/06-helm-deploy-process.md)
- [Fastly CDN管理](../concepts/07-fastly-cdn.md)
