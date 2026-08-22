---
type: Reference
title: "部署配置文件源码"
description: "config/nbviewer.yaml（Helm values公开配置）、config/cdn.yaml（空占位文件）、secrets/目录（git-crypt加密密钥）的完整结构解析"
tags: [nbviewer, deploy, helm, config, yaml, git-crypt, secrets]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config-nbviewer
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/config/nbviewer.yaml"
    title: "config/nbviewer.yaml"
  - id: config-cdn
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/config/cdn.yaml"
    title: "config/cdn.yaml"
  - id: secrets-dir
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/secrets/"
    title: "secrets/ 目录"
  - id: deploy-sh
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/deploy.sh"
    title: "deploy.sh"
---

# 部署配置文件源码

本信源登记 nbviewer.org-deploy 项目中配置文件的结构与字段含义。

## 1. config/nbviewer.yaml（公开Helm Values）

文件路径：`config/nbviewer.yaml`

此文件包含 Helm 部署的公开配置值，被 `deploy.sh` 通过 `-f config/nbviewer.yaml` 参数传递给 `helm upgrade` 命令。

```yaml
replicas: 3

image: jupyter/nbviewer:a53d108

memcached:
  config:
    memoryLimit: 1600
  resources:
    requests:
      cpu: 100m
      memory: 2Gi
    limits:
      cpu: 500m
      memory: 2Gi

nbviewer:
  extraArgs:
    - "--cache-expiry-min=3600"
    - "--cache-expiry-max=14400"
    - "--content-security-policy=connect-src *"
    - "--jupyter-js-widgets-version=2.1"
    - "--jupyter-widgets-html-manager-version=0.15"
    - >-
      --NBViewer.extra_head_html=
      <script defer data-domain="nbviewer.org" src="https://plausible.io/js/script.file-downloads.outbound-links.js"></script>
      <script>window.plausible = window.plausible || function() { (window.plausible.q = window.plausible.q || []).push(arguments) }</script>

statuspage:
  enabled: true
  pageId: fzcq6v7wcg65
  metricId: rfcg9djxtg6n
```

### 字段说明

| 字段 | 类型 | 值 | 说明 |
|------|------|---|------|
| `replicas` | integer | `3` | nbviewer Pod 副本数 |
| `image` | string | `jupyter/nbviewer:a53d108` | Docker 镜像标签（短commit hash） |
| `memcached.config.memoryLimit` | integer | `1600` | Memcached 内存限制（MB） |
| `memcached.resources.requests.cpu` | string | `100m` | Memcached CPU 请求 |
| `memcached.resources.requests.memory` | string | `2Gi` | Memcached 内存请求 |
| `memcached.resources.limits.cpu` | string | `500m` | Memcached CPU 上限 |
| `memcached.resources.limits.memory` | string | `2Gi` | Memcached 内存上限 |
| `nbviewer.extraArgs` | string[] | 6个参数 | 传递给 nbviewer 的命令行参数 |
| `statuspage.enabled` | boolean | `true` | 是否启用 statuspage sidecar |
| `statuspage.pageId` | string | `fzcq6v7wcg65` | Statuspage.io 页面 ID |
| `statuspage.metricId` | string | `rfcg9djxtg6n` | Statuspage.io 指标 ID |

### nbviewer 命令行参数详解

| 参数 | 值 | 用途 |
|------|---|------|
| `--cache-expiry-min` | `3600` | 缓存最小过期时间（秒，1小时） |
| `--cache-expiry-max` | `14400` | 缓存最大过期时间（秒，4小时） |
| `--content-security-policy` | `connect-src *` | CSP策略，允许所有连接源（解决issue #797） |
| `--jupyter-js-widgets-version` | `2.1` | ipywidgets JS版本（解决issue #818） |
| `--jupyter-widgets-html-manager-version` | `0.15` | widgets HTML manager版本（解决issue #818） |
| `--NBViewer.extra_head_html` | Plausible脚本 | 注入Plausible analytics到HTML头部 |

## 2. config/cdn.yaml（空占位文件）

文件路径：`config/cdn.yaml`

**重要事实**：此文件存在但内容为空。`deploy.sh` 中**不引用**此文件——Helm 命令只使用 `-f config/nbviewer.yaml -f secrets/config/nbviewer.yaml`，不包含 `-f config/cdn.yaml` 或 `-f secrets/config/cdn.yaml`。

CDN（Fastly）配置完全通过 `tasks.py` 中的 `invoke fastly` 命令管理，不通过 Helm values。

## 3. secrets/ 目录（git-crypt加密）

目录路径：`secrets/`

```
secrets/
├── config/
│   ├── cdn.yaml          # CDN密钥配置（加密）
│   └── nbviewer.yaml     # Helm密钥配置（加密）
└── ovh-kubeconfig.yaml   # OVH Kubernetes kubeconfig（加密）
```

所有 `secrets/` 目录下的文件通过 [.gitattributes](#gitattributes加密模式) 的 `git-crypt` 过滤器自动加密。这些文件在仓库中存储为加密二进制，解密后才是明文 YAML。

### deploy.sh 中的使用

```bash
# kubeconfig路径
export KUBECONFIG=$PWD/secrets/ovh-kubeconfig.yaml

# Helm密钥配置
helm upgrade nbviewer $nbviewer_chart -f config/nbviewer.yaml -f secrets/config/nbviewer.yaml
```

### CDN密钥配置

`secrets/config/cdn.yaml` 存在但**不被 deploy.sh 使用**。它可能包含 Fastly 相关配置，但实际 Fastly 操作通过 `tasks.py` 直接使用 Fastly API（凭据存储在 `creds` 文件中）。

## 4. 其他配置文件

### creds 文件

根目录下的 `creds` 文件（无扩展名），同样通过 git-crypt 加密。`tasks.py` 通过 `exec()` 读取此文件获取凭据：

```python
creds = {}
with open("creds") as f:
    exec(f.read(), creds)
```

该文件定义了以下变量（从tasks.py的使用推断）：
- `DOCKER_TRIGGER_TOKEN`：Docker Hub自动构建触发token
- `FASTLY_KEY`：Fastly API密钥
- `FASTLY_SERVICE_ID`：Fastly服务ID

### env_file 和 env_statuspage

- `env_file`：nbviewer 容器环境变量文件（git-crypt加密）
- `env_statuspage`：statuspage sidecar环境变量文件（git-crypt加密），包含 `STATUSPAGE_API_KEY`、`STATUSPAGE_PAGE_ID`、`STATUSPAGE_METRIC_ID`、`GITHUB_OAUTH_KEY`、`GITHUB_OAUTH_SECRET`

## .gitattributes 加密模式

```
secrets/** filter=git-crypt diff=git-crypt
creds filter=git-crypt diff=git-crypt
newrelic.ini filter=git-crypt diff=git-crypt
env_* filter=git-crypt diff=git-crypt
machine/** filter=git-crypt diff=git-crypt
```

| 模式 | 覆盖范围 |
|------|---------|
| `secrets/**` | secrets目录下所有文件 |
| `creds` | 根目录creds文件 |
| `newrelic.ini` | New Relic配置（仓库中可能不存在） |
| `env_*` | 所有env_开头的文件（env_file、env_statuspage） |
| `machine/**` | machine目录下所有文件 |

## 配置加载链路

```
deploy.sh 执行时:
  1. export KUBECONFIG=secrets/ovh-kubeconfig.yaml  (kubeconfig)
  2. helm dep up ../nbviewer/helm-chart/nbviewer     (更新chart依赖)
  3. helm upgrade nbviewer <chart> \
       -f config/nbviewer.yaml \                    (公开配置)
       -f secrets/config/nbviewer.yaml \            (加密密钥配置)
       --cleanup-on-fail
  4. kubectl rollout status -w deployment/nbviewer  (等待部署完成)

注意: config/cdn.yaml 和 secrets/config/cdn.yaml 不在此链路中
```

## 相关信源

- [deploy.sh部署脚本源码](cicd-source.md#deploysh)
- [tasks.py Invoke任务源码](tasks-source.md)
- [CI/CD工作流源码](cicd-source.md)
