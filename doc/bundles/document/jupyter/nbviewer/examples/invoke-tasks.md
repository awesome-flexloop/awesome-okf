---
type: Example
title: "使用Invoke任务管理CDN"
description: "如何使用invoke fastly同步Fastly CDN后端、invoke trigger-build触发Docker构建、invoke doitall完整流程的使用指南"
tags: [nbviewer, deploy, invoke, fastly, cdn, tasks, pyinvoke]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tasks
    resource: "/references/tasks-source.md"
    title: "Invoke任务信源"
---

# 使用Invoke任务管理CDN

本文档演示如何使用 `invoke`（pyinvoke）命令行工具管理Fastly CDN后端和触发构建。

## 前提条件

1. 已安装Python依赖：`pip install -r requirements.txt`
2. 已通过git-crypt解锁 `creds` 文件
3. 网络能访问Fastly API和Docker Hub

## 可用任务一览

| 命令 | 功能 | 状态 |
|------|------|------|
| `invoke fastly` | 同步Fastly CDN后端配置 | ✅ 可用 |
| `invoke trigger-build` | 触发Docker Hub自动构建 | ✅ 可用 |
| `invoke doitall` | 完整流程（git pull + upgrade + fastly） | ⚠️ upgrade未实现 |
| `invoke upgrade` | Helm升级部署 | ❌ NotImplementedError |

**重要**：`invoke upgrade` 抛出 `NotImplementedError("Not implemented yet for helm")`，Helm部署通过 `deploy.sh` 脚本执行，不是通过invoke任务。

## 示例1：查看Fastly后端状态并同步

```bash
# 进入项目目录
cd nbviewer.org-deploy

# 确保creds文件已解密
git-crypt unlock

# 运行fastly任务
invoke fastly
```

### 输出示例

**当后端配置一致时（无变更）**：
```
Checking fastly backends
Fastly OK
```

**当后端需要更新时**：
```
Checking fastly backends
Deleting backend old-ovh
Adding backend ovh 135.125.83.237:80
Activating fastly configuration 42
```

### fastly任务做了什么

1. 读取 `creds` 文件中的 `FASTLY_KEY` 和 `FASTLY_SERVICE_ID`
2. 创建FastlyService实例，自动克隆可编辑版本
3. 获取当前Fastly后端列表
4. 获取 `all_instances()` 中的期望后端列表（硬编码在tasks.py中）
5. 删除不在期望列表中的后端
6. 添加缺失的后端（使用copy-backend模式复制第一个后端的配置）
7. 如果有变更，激活新版本并克隆下一个编辑版本

## 示例2：更新后端IP地址

当OVH Kubernetes集群的Service IP变更时：

```bash
# 步骤1：获取当前Service IP
export KUBECONFIG=secrets/ovh-kubeconfig.yaml
kubectl get svc -n nbviewer
# 输出示例:
# NAME       TYPE           CLUSTER-IP     EXTERNAL-IP       PORT(S)
# nbviewer   LoadBalancer   10.3.229.149   135.125.83.237    80:32393/TCP

# 步骤2：编辑tasks.py中的all_instances()函数
# 修改IP地址为新的EXTERNAL-IP
```

需要修改的代码（tasks.py中的all_instances函数）：

```python
def all_instances():
    all_nbviewers = {}
    # TODO: get service from kubernetes
    all_nbviewers[("NEW_IP_ADDRESS", 80)] = "ovh"  # 更新IP
    return all_nbviewers
```

```bash
# 步骤3：运行fastly同步
invoke fastly

# 步骤4：同时更新Cloudflare DNS
# 访问 https://dash.cloudflare.com/dns 手动更新cdn.jupyter.org的A记录
```

## 示例3：触发Docker Hub构建

```bash
invoke trigger-build
```

此命令向Docker Hub发送POST请求，触发自动构建：

```
https://hub.docker.com/api/build/v1/source/579ab043-912f-425b-8b3f-765ee6143b53/trigger/{DOCKER_TRIGGER_TOKEN}/call/
```

触发后等待几分钟，Docker Hub会构建新镜像。新镜像tag由Docker Hub自动生成。

## 示例4：查看invoke可用任务列表

```bash
invoke --list
```

## 不存在的任务（常见错误）

以下命令**不存在**，不要使用：

| 错误命令 | 说明 |
|---------|------|
| `invoke lock-cdn` | 不存在此任务，CDN不需要锁定 |
| `invoke unlock-cdn` | 不存在此任务 |
| `invoke sync-cdn-backends` | 不存在，功能由 `invoke fastly` 实现 |

Fastly的版本管理是内置的——每次修改都在新版本上编辑，激活后自动克隆新版本，无需手动锁定/解锁。

## 排错

| 错误 | 原因 | 解决 |
|------|------|------|
| `FileNotFoundError: 'creds'` | creds文件未解密 | 运行 `git-crypt unlock` |
| `KeyError: 'FASTLY_KEY'` | creds文件中缺少FASTLY_KEY | 检查creds文件内容 |
| `requests.exceptions.HTTPError 401` | Fastly API密钥无效 | 检查FASTLY_KEY是否正确 |
| `requests.exceptions.ConnectionError` | 网络无法访问Fastly API | 检查网络连接 |
| `NotImplementedError` | upgrade任务未实现 | 使用 `bash deploy.sh` 进行Helm部署 |

## 相关文档

- [Fastly CDN管理](../concepts/07-fastly-cdn.md)
- [Invoke任务信源](../references/tasks-source.md)
- [本地部署调试](local-debug.md)
