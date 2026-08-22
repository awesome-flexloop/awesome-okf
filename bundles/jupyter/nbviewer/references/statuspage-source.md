---
type: Reference
title: "Statuspage Sidecar源码"
description: "statuspage/目录：独立Docker镜像和Python脚本，作为Kubernetes sidecar监控GitHub API速率限制并上报Statuspage.io"
tags: [nbviewer, deploy, statuspage, sidecar, monitoring, github-api, docker]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: statuspage-py
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/statuspage/statuspage.py"
    title: "statuspage/statuspage.py"
  - id: statuspage-dockerfile
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/statuspage/Dockerfile"
    title: "statuspage/Dockerfile"
  - id: config-nbviewer
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/config/nbviewer.yaml"
    title: "config/nbviewer.yaml (statuspage配置节)"
---

# Statuspage Sidecar源码

本信源登记 `statuspage/` 目录的文件结构和代码逻辑。

## 目录结构

```
statuspage/
├── Dockerfile       # 独立Docker镜像构建文件
└── statuspage.py    # Python监控脚本
```

**重要事实**：
- `statuspage/` 是项目根目录下的独立子目录，**不是** Helm Chart 的一部分
- 它有自己的 Dockerfile，构建独立的容器镜像
- 在 Kubernetes 中作为 sidecar 容器与 nbviewer 主容器一起部署
- 通过 `config/nbviewer.yaml` 中的 `statuspage.enabled: true` 启用

## Dockerfile

```dockerfile
FROM python:3.7-alpine
RUN pip install requests
ADD statuspage.py statuspage.py
CMD ["python", "statuspage.py"]
```

| 指令 | 说明 |
|------|------|
| `FROM python:3.7-alpine` | 基于Python 3.7 Alpine镜像（轻量级） |
| `RUN pip install requests` | 仅安装requests依赖 |
| `ADD statuspage.py statuspage.py` | 将脚本复制到容器中 |
| `CMD ["python", "statuspage.py"]` | 容器启动命令 |

## statuspage.py 完整逻辑

### 环境变量配置

```python
api_key = os.environ["STATUSPAGE_API_KEY"]
page_id = os.environ["STATUSPAGE_PAGE_ID"]
metric_id = os.environ["STATUSPAGE_METRIC_ID"]
api_base = "api.statuspage.io"

github_id = os.environ["GITHUB_OAUTH_KEY"]
github_secret = os.environ["GITHUB_OAUTH_SECRET"]
```

所有配置通过环境变量注入，无硬编码凭据。环境变量通过 `env_statuspage` 文件（git-crypt加密）定义。

| 环境变量 | 用途 |
|---------|------|
| `STATUSPAGE_API_KEY` | Statuspage.io OAuth API密钥 |
| `STATUSPAGE_PAGE_ID` | Statuspage.io页面ID |
| `STATUSPAGE_METRIC_ID` | Statuspage.io指标ID |
| `GITHUB_OAUTH_KEY` | GitHub OAuth App ID（用于API认证） |
| `GITHUB_OAUTH_SECRET` | GitHub OAuth App Secret |

### get_rate_limit() 函数

```python
def get_rate_limit():
    """Retrieve the current GitHub rate limit for our auth tokens"""
    r = requests.get(
        "https://api.github.com/rate_limit", auth=(github_id, github_secret)
    )
    r.raise_for_status()
    resp = r.json()
    return resp["resources"]["core"]
```

- 向 GitHub API `/rate_limit` 端点发送GET请求
- 使用 Basic Auth（GitHub OAuth App的ID和Secret）
- 返回核心API的速率限制信息（包含 `limit`、`remaining`、`reset` 等字段）

### post_data() 函数

```python
def post_data(limit, remaining, **ignore):
    """Send the percent-remaining GitHub rate limit to statuspage"""
    percent = 100 * remaining / limit
    now = int(datetime.utcnow().timestamp())
    url = f"https://api.statuspage.io/v1/pages/{page_id}/metrics/{metric_id}/data.json"

    r = requests.post(
        url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "OAuth " + api_key,
        },
        data={
            "data[timestamp]": now,
            "data[value]": percent,
        },
    )
    r.raise_for_status()
```

- 计算剩余配额百分比：`100 * remaining / limit`
- 使用Unix时间戳（UTC）
- 向Statuspage.io的metrics data API POST数据点
- 认证方式：`Authorization: OAuth <api_key>`

### get_and_post() 函数

```python
def get_and_post():
    data = get_rate_limit()
    print(json.dumps(data))
    post_data(limit=data["limit"], remaining=data["remaining"])
```

组合操作：获取速率限制 → 打印JSON日志 → 上报数据。

### 主循环

```python
while True:
    try:
        get_and_post()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    # post every two minutes
    time.sleep(120)
```

- **无限循环**，每120秒（2分钟）执行一次
- 异常捕获：错误打印到stderr，不中断循环
- 优雅降级：网络故障时只记录错误，下次循环重试

## Helm配置中的Statuspage

在 `config/nbviewer.yaml` 中：

```yaml
statuspage:
  enabled: true
  pageId: fzcq6v7wcg65
  metricId: rfcg9djxtg6n
```

| 字段 | 值 | 说明 |
|------|---|------|
| `enabled` | `true` | 启用statuspage sidecar部署 |
| `pageId` | `fzcq6v7wcg65` | Statuspage.io页面ID（公开信息） |
| `metricId` | `rfcg9djxtg6n` | Statuspage.io指标ID（公开信息） |

API密钥和GitHub凭据通过 `secrets/config/nbviewer.yaml`（git-crypt加密）注入为环境变量。

## 部署架构

```
┌─────────────────────────────────────────┐
│         Kubernetes Pod: nbviewer        │
│                                         │
│  ┌─────────────────┐  ┌──────────────┐  │
│  │ nbviewer 主容器  │  │ statuspage   │  │
│  │ (Tornado Web)   │  │ sidecar      │  │
│  │ :80/            │  │ (监控脚本)    │  │
│  └────────┬────────┘  └──────┬───────┘  │
│           │                  │          │
│     外部流量            每2分钟:         │
│                         │  GET GitHub   │
│                         │  /rate_limit  │
│                         │               │
│                         │  POST Statuspage│
│                         │  /metrics/data │
└─────────────────────────┼──────────────┘
                          │
                    ┌─────┴─────┐
                    │  外部API   │
                    │ GitHub +   │
                    │ Statuspage │
                    └───────────┘
```

## 相关信源

- [部署配置文件源码](config-source.md#statuspage-配置节)
- [测试与密钥管理](/concepts/08-testing-and-secrets.md)
