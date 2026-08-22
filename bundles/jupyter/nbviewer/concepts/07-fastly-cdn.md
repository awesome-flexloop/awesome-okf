---
type: Concept
title: "Fastly CDN管理"
description: "tasks.py中FastlyService类的API、fastly任务同步逻辑、all_instances()硬编码IP、copy-backend模式、无lock/unlock任务"
tags: [nbviewer, deploy, fastly, cdn, backend, load-balancer, invoke]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tasks
    resource: "/references/tasks-source.md"
    title: "Invoke任务信源"
---

# Fastly CDN管理

nbviewer.org 使用 Fastly 作为CDN和负载均衡层。CDN后端管理通过 `tasks.py` 中的 `invoke fastly` 任务手动操作，不是自动化部署流程的一部分。

## Fastly在架构中的位置

```
用户 → Cloudflare DNS → Fastly CDN → OVH Kubernetes (135.125.83.237:80)
```

Fastly承担以下角色：
1. **CDN缓存**：缓存静态资源和渲染的Notebook页面
2. **负载均衡**：将请求分发到后端nbviewer实例
3. **TLS终结**：处理HTTPS连接
4. **健康检查**：主动检查后端健康状态

## 唯一可用的CDN任务：fastly

`tasks.py` 中只有一个CDN相关的invoke任务：

```bash
invoke fastly    # 同步Fastly后端配置
```

**不存在的任务**（文档中常见错误）：
- ❌ `invoke lock-cdn` — 不存在
- ❌ `invoke unlock-cdn` — 不存在
- ❌ `invoke sync-cdn-backends` — 不存在（功能由 `fastly` 任务实现）

## FastlyService类

`FastlyService` 类封装了Fastly API的操作。

### 初始化流程

```python
f = FastlyService(api_key=creds["FASTLY_KEY"], service_id=creds["FASTLY_SERVICE_ID"])
```

1. 创建 `requests.Session`，设置 `Fastly-Key` 请求头
2. 获取所有版本列表 `self.versions()`
3. 取最新版本号
4. 如果最新版本已经是 `active` 状态，先克隆一个新版本（在新版本上编辑，不直接修改活跃版本）
5. 设置 `self.version` 为可编辑的版本号

### 版本管理机制

Fastly使用版本化配置管理：

```
当前活跃版本 (active=true)
    │
    ├─ 克隆 → 新版本 (draft, 可编辑)
    │             │
    │             ├─ 添加/删除后端
    │             │
    │             └─ activate → 新活跃版本 + 再克隆一个draft
    │
    └─ 保留（回滚用）
```

每次操作流程：
1. 确保在draft版本上编辑
2. 执行后端增删操作
3. 调用 `deploy()` 激活版本
4. 自动克隆新版本供下次编辑

### API方法

| 方法 | HTTP | 路径 | 说明 |
|------|------|------|------|
| `backends()` | GET | `/backend` | 获取所有后端 |
| `add_backend(name, hostname, port, copy_backend)` | POST | `/backend` | 添加新后端 |
| `remove_backend(name)` | DELETE | `/backend/{name}` | 删除后端 |
| `deploy()` | PUT | `/activate` + `/clone` | 激活版本并克隆新版本 |

### add_backend的copy-backend模式

这是一个重要的设计模式：

```python
def add_backend(self, name, hostname, port, copy_backend=None):
    if copy_backend is None:
        copy_backend = self.backends()[0]
    data = {
        key: copy_backend[key]
        for key in [
            "healthcheck", "max_conn", "weight", "error_threshold",
            "connect_timeout", "between_bytes_timeout", "first_byte_timeout",
            "auto_loadbalance",
        ]
    }
    data.update({"address": hostname, "name": name, "port": port})
    self.api_request("/backend", method="POST", data=data)
```

新后端不是从零创建配置，而是**复制现有后端的8个关键配置字段**，只覆盖地址、名称和端口。

复制的配置字段：

| 字段 | 说明 |
|------|------|
| `healthcheck` | 健康检查配置名称 |
| `max_conn` | 最大连接数 |
| `weight` | 负载均衡权重 |
| `error_threshold` | 错误阈值（超过则标记为不健康） |
| `connect_timeout` | 连接超时 |
| `between_bytes_timeout` | 字节间超时 |
| `first_byte_timeout` | 首字节超时 |
| `auto_loadbalance` | 是否自动负载均衡 |

**为什么使用copy-backend模式？**
- 确保所有后端使用一致的健康检查和超时配置
- 避免手动配置8个字段时出错
- 如果第一个后端的配置更新了，新添加的后端自动继承新配置

## all_instances()：硬编码后端列表

```python
def all_instances():
    """Return {(ip, port) : name} for all running nbviewer containers on all machines"""
    all_nbviewers = {}
    # add ovh by hand
    # TODO: get service from kubernetes
    all_nbviewers[("135.125.83.237", 80)] = "ovh"
    return all_nbviewers
```

**关键事实**：
- 返回字典 `{(ip, port): name}`
- 目前只有**一个硬编码条目**：`("135.125.83.237", 80): "ovh"`
- 代码中标注了TODO：应从Kubernetes自动获取服务IP（`kubectl get svc`）
- 当OVH集群IP变更时，必须手动更新此函数

README中的说明：
> Fastly is scripted now, but we could do better. Load-balancer DNS/ip is hardcoded in tasks.py and must be updated if changed. See the output of `kubectl get svc` for the current ip address, and update with `invoke fastly`.

## fastly任务执行逻辑

```
invoke fastly
    │
    ├─ 创建FastlyService实例
    ├─ 获取当前Fastly后端列表 backends
    ├─ 获取期望实例列表 nbviewers = all_instances()
    │
    ├─ 阶段1：删除多余后端
    │   for backend in backends:
    │     host = (backend["address"], backend["port"])
    │     if host not in nbviewers:
    │       f.remove_backend(backend["name"])
    │       changed = True
    │     else:
    │       existing_backends.add(host)
    │
    ├─ 阶段2：添加缺失后端
    │   copy_backend = backends[0]  # 使用第一个后端作为模板
    │   for host, name in nbviewers.items():
    │     if host not in existing_backends:
    │       ip, port = host
    │       f.add_backend(name, ip, port, copy_backend)
    │       changed = True
    │
    └─ 阶段3：部署变更
        if changed:
          f.deploy()  # activate + clone
          print(f"Activating fastly configuration {f.version}")
        else:
          print("Fastly OK")
```

### 同步逻辑总结

1. **期望状态**：`all_instances()` 返回的 `{(ip, port): name}` 字典
2. **实际状态**：Fastly当前配置的后端列表
3. **调和（Reconciliation）**：
   - 实际存在但期望中没有 → 删除
   - 期望中有但实际不存在 → 添加（copy-backend模式）
   - 两者都有 → 保持不变
4. **部署**：有变更则激活新版本，无变更输出"Fastly OK"

## 凭据管理

Fastly凭据存储在 `creds` 文件（git-crypt加密）：

| 变量 | 说明 |
|------|------|
| `FASTLY_KEY` | Fastly API密钥 |
| `FASTLY_SERVICE_ID` | Fastly服务ID |

```python
creds = {}
with open("creds") as f:
    exec(f.read(), creds)

f = FastlyService(creds["FASTLY_KEY"], creds["FASTLY_SERVICE_ID"])
```

不使用硬编码常量。

## 何时需要运行invoke fastly

| 场景 | 是否需要fastly |
|------|:---:|
| 常规版本更新（镜像tag变更） | ❌ 不需要 |
| 后端IP地址变更（集群迁移等） | ✅ 需要 |
| 添加新的后端节点 | ✅ 需要 |
| 移除后端节点 | ✅ 需要 |
| 修改健康检查/超时配置 | ✅ 需要（需手动API调用，非脚本功能） |

## Cloudflare DNS注意事项

README中提到：

> cdn.jupyter.org is proxied through Cloudflare DNS. Changes to ip require manual update at https://dash.cloudflare.com/dns.

除了Fastly CDN，`cdn.jupyter.org` 还通过Cloudflare DNS代理。如果IP变更，需要同时更新：
1. Fastly后端（`invoke fastly`）
2. Cloudflare DNS记录（手动在Dashboard操作）

## 相关文档

- [Helm部署流程](06-helm-deploy-process.md)
- [Invoke任务使用示例](/examples/invoke-tasks.md)
- [部署配置详解](03-deployment-config.md#configcdnyaml空文件说明)
