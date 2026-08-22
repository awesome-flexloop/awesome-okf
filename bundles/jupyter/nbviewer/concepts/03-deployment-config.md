---
type: Concept
title: "部署配置详解"
description: "config/nbviewer.yaml Helm values完整解析、空cdn.yaml说明、secrets加密配置、statuspage配置"
tags: [nbviewer, deploy, helm, config, values, yaml, secrets, git-crypt]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config
    resource: "/references/config-source.md"
    title: "配置文件信源"
---

# 部署配置详解

本文档详细解析 nbviewer.org-deploy 的所有配置文件，包括公开Helm values、加密密钥配置和空文件说明。

## 配置文件分类

| 文件 | 加密 | 用途 | deploy.sh使用 |
|------|------|------|:---:|
| `config/nbviewer.yaml` | ❌ | 公开Helm values | ✅ |
| `config/cdn.yaml` | ❌ | 空占位文件 | ❌ |
| `secrets/config/nbviewer.yaml` | ✅ | 密钥Helm values | ✅ |
| `secrets/config/cdn.yaml` | ✅ | CDN密钥配置 | ❌ |
| `secrets/ovh-kubeconfig.yaml` | ✅ | Kubernetes集群凭证 | ✅ |
| `creds` | ✅ | Fastly/Docker Hub凭据 | ❌（tasks.py使用） |
| `env_file` | ✅ | nbviewer容器环境变量 | Helm管理 |
| `env_statuspage` | ✅ | statuspage环境变量 | Helm管理 |

## config/nbviewer.yaml（公开配置）

这是主要的Helm values配置文件，定义了部署的副本数、镜像、资源限制和应用参数。

### 副本数与镜像

```yaml
replicas: 3
image: jupyter/nbviewer:a53d108
```

| 参数 | 值 | 说明 |
|------|---|------|
| `replicas` | 3 | 同时运行3个nbviewer Pod |
| `image` | `jupyter/nbviewer:a53d108` | Docker镜像，标签为nbviewer repo的短commit hash |

**镜像版本更新**：镜像标签由 `scripts/update-nbviewer.py` 自动更新，检查Docker Hub最新tag。

### Memcached配置

```yaml
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
```

| 参数 | 值 | 说明 |
|------|---|------|
| `memoryLimit` | 1600 | Memcached最大内存（MB），约1.6GB |
| CPU request | 100m | 0.1核，保证最低调度资源 |
| CPU limit | 500m | 0.5核，防止CPU争抢 |
| Memory request/limit | 2Gi | 内存请求和上限都是2GB |

Memcached作为nbviewer的渲染结果缓存层，减少对上游GitHub/Gist的重复请求。

### nbviewer应用参数

```yaml
nbviewer:
  extraArgs:
    - "--cache-expiry-min=3600"
    - "--cache-expiry-max=14400"
    - "--content-security-policy=connect-src *"
    - "--jupyter-js-widgets-version=2.1"
    - "--jupyter-widgets-html-manager-version=0.15"
    - >-
      --NBViewer.extra_head_html=
      <script ...>...</script>
```

#### 缓存配置

| 参数 | 值 | 说明 |
|------|---|------|
| `--cache-expiry-min=3600` | 3600秒（1小时） | 缓存条目的最小TTL |
| `--cache-expiry-max=14400` | 14400秒（4小时） | 缓存条目的最大TTL |

渲染的Notebook HTML在Memcached中缓存1-4小时，具体过期时间取决于内容类型和访问频率。

#### CSP策略

```
--content-security-policy=connect-src *
```

允许所有连接源（`connect-src *`）。这是为了解决 [issue #797](https://github.com/jupyter/nbviewer/issues/797) 中的跨域资源加载问题。

#### Widget版本锁定

| 参数 | 值 | 相关Issue |
|------|---|----------|
| `--jupyter-js-widgets-version=2.1` | 2.1 | [#818](https://github.com/jupyter/nbviewer/issues/818) |
| `--jupyter-widgets-html-manager-version=0.15` | 0.15 | [#818](https://github.com/jupyter/nbviewer/issues/818) |

锁定ipywidgets的JS版本和HTML manager版本，确保渲染兼容性。

#### Plausible Analytics

通过 `--NBViewer.extra_head_html` 注入Plausible统计脚本到每个页面的HTML头部：

```html
<script defer data-domain="nbviewer.org" src="https://plausible.io/js/script.file-downloads.outbound-links.js"></script>
<script>window.plausible = window.plausible || function() { (window.plausible.q = window.plausible.q || []).push(arguments) }</script>
```

- `data-domain="nbviewer.org"`：统计域名
- `file-downloads`：跟踪文件下载
- `outbound-links`：跟踪出站链接
- 第二行是Plausible的初始化兜底脚本

### Statuspage配置

```yaml
statuspage:
  enabled: true
  pageId: fzcq6v7wcg65
  metricId: rfcg9djxtg6n
```

| 参数 | 值 | 说明 |
|------|---|------|
| `enabled` | true | 启用statuspage sidecar容器部署 |
| `pageId` | fzcq6v7wcg65 | Statuspage.io页面ID（公开信息） |
| `metricId` | rfcg9djxtg6n | Statuspage.io指标ID（公开信息） |

API密钥和GitHub OAuth凭据通过 `secrets/config/nbviewer.yaml` 或 `env_statuspage` 以环境变量形式注入。

## config/cdn.yaml（空文件说明）

`config/cdn.yaml` 文件存在但内容为空。

**关键事实**：
- `deploy.sh` **不引用**此文件
- Helm命令只使用 `-f config/nbviewer.yaml -f secrets/config/nbviewer.yaml`
- CDN管理不通过Helm values配置，而是通过 `tasks.py` 直接调用Fastly API
- `secrets/config/cdn.yaml` 同样不被deploy.sh使用

这个空文件可能是历史遗留（早期版本可能通过Helm管理CDN配置），或者预留给未来使用。

## secrets/ 目录（加密配置）

所有 `secrets/` 下的文件通过 `.gitattributes` 配置的git-crypt过滤器自动加密。

### secrets/ovh-kubeconfig.yaml

OVHCloud Kubernetes集群的kubeconfig文件。`deploy.sh` 通过 `export KUBECONFIG=$PWD/secrets/ovh-kubeconfig.yaml` 使用。

在GitHub Actions CI中，通过 `sliteteam/github-action-git-crypt-unlock` action使用 `GIT_CRYPT_KEY` secret解密。

### secrets/config/nbviewer.yaml

Helm的密钥配置values，包含不应公开的配置（如密钥、凭据、私有配置等）。此文件与 `config/nbviewer.yaml` 一起传递给Helm：

```bash
helm upgrade nbviewer <chart> -f config/nbviewer.yaml -f secrets/config/nbviewer.yaml
```

Helm会合并两个values文件，后者的同名键覆盖前者。

## creds 文件

根目录下的 `creds` 文件（无扩展名），包含 `tasks.py` 所需的API凭据：

```python
# tasks.py中的读取方式
creds = {}
with open("creds") as f:
    exec(f.read(), creds)
```

必需的变量：

| 变量 | 用途 | 使用位置 |
|------|------|---------|
| `FASTLY_KEY` | Fastly API密钥 | `FastlyService(api_key=creds["FASTLY_KEY"], ...)` |
| `FASTLY_SERVICE_ID` | Fastly服务ID | `FastlyService(..., service_id=creds["FASTLY_SERVICE_ID"])` |
| `DOCKER_TRIGGER_TOKEN` | Docker Hub构建触发token | `trigger_build()` 任务 |

## env_file 和 env_statuspage

这两个文件通过git-crypt加密，包含容器的环境变量。它们通过Helm Chart配置注入到对应容器中，格式为标准的 `KEY=VALUE` 环境文件。

`env_statuspage` 中包含：
- `STATUSPAGE_API_KEY`
- `STATUSPAGE_PAGE_ID`
- `STATUSPAGE_METRIC_ID`
- `GITHUB_OAUTH_KEY`
- `GITHUB_OAUTH_SECRET`

## 配置更新方式

| 配置类型 | 更新方式 | 自动化 |
|---------|---------|--------|
| 镜像标签 | `scripts/update-nbviewer.py` | ✅ watch-dependencies自动开PR |
| Chart版本(NBVIEWER_VERSION) | `scripts/update-nbviewer.py` | ✅ watch-dependencies自动开PR |
| nbviewer参数 | 手动编辑config/nbviewer.yaml | ❌ 手动 |
| Memcached资源 | 手动编辑config/nbviewer.yaml | ❌ 手动 |
| 副本数 | 手动编辑config/nbviewer.yaml | ❌ 手动 |
| Fastly后端IP | 编辑tasks.py中all_instances() | ❌ 手动，然后invoke fastly |
| 密钥/凭据 | 通过git-crypt管理 | ❌ 手动编辑加密文件 |
| Python依赖 | 编辑requirements.in + pip-compile | ❌ dependabot月度检查 |

## 相关文档

- [架构总览](02-architecture-overview.md)
- [Helm部署流程](06-helm-deploy-process.md)
- [配置文件信源](/references/config-source.md)
