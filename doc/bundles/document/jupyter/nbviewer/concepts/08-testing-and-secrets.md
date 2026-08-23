---
type: Concept
title: "测试与密钥管理"
description: "冒烟测试机制（test_nbviewer.py + BeautifulSoup）、git-crypt加密模式、statuspage sidecar监控、密钥文件清单"
tags: [nbviewer, deploy, testing, pytest, git-crypt, secrets, statuspage, smoke-test]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tests
    resource: "/references/tests-source.md"
    title: "测试源码信源"
  - id: config
    resource: "/references/config-source.md"
    title: "配置文件信源"
  - id: statuspage
    resource: "/references/statuspage-source.md"
    title: "Statuspage信源"
---

# 测试与密钥管理

本文档介绍nbviewer.org-deploy的测试策略和密钥管理机制。

## 测试体系

### 测试定位：线上冒烟测试

nbviewer.org-deploy 的测试**不是**单元测试或集成测试，而是部署后的**冒烟测试**（smoke test），直接验证生产环境nbviewer.org的可用性。

### 测试文件结构

```
tests/
└── test_nbviewer.py    # 唯一的测试文件
```

**不存在的测试文件**：
- ❌ `tests/conftest.py` — 无pytest fixture配置
- ❌ `tests/test_app.py` — 无应用单元测试
- ❌ `tests/test_statuspage.py` — 无statuspage测试
- ❌ 重试助手或指数退避工具

### pytest配置

来自 `pyproject.toml`：

```toml
[tool.pytest.ini_options]
addopts = "-v"
testpaths = ["tests"]
```

- 详细输出模式（`-v`）
- 自动发现 `tests/` 目录下的测试

### 测试逻辑详解

测试文件在**模块导入时**就执行网络请求：

```python
NBVIEWER = "https://nbviewer.org"

# 模块级执行：导入时就请求首页
frontpage_request = requests.get(NBVIEWER)
frontpage = BeautifulSoup(frontpage_request.text, "html.parser")
frontpage_links = frontpage.find_all("a", class_="thumbnail")
frontpage_urls = [a["href"] for a in frontpage_links]
```

这意味着：
1. pytest收集测试时就请求nbviewer.org首页
2. 如果nbviewer.org不可达，测试在收集阶段就失败
3. 测试的URL列表是动态的——基于首页实际展示的示例notebook

#### test_main_page

```python
def test_main_page():
    frontpage_request.raise_for_status()
    assert frontpage_request.status_code == 200
    assert len(frontpage_urls) > 5
```

验证三个条件：
1. HTTP请求成功（`raise_for_status`）
2. 返回状态码200
3. 首页至少有5个以上示例notebook链接（`a.thumbnail`元素）

#### test_front_page（参数化）

```python
@pytest.mark.parametrize("path", frontpage_urls)
def test_front_page(path):
    url = f"{NBVIEWER}{path}"
    r = requests.get(url)
    assert r.status_code == 200
```

对首页每个缩略图链接逐一请求，验证返回200。

**测试特点**：
- 无重试机制（单次请求，失败即测试失败）
- 无超时设置（使用requests默认超时）
- 参数化数据在导入时确定，不会在每个测试中重新请求首页
- 测试覆盖范围取决于首页展示的示例notebook数量

### CI中的测试执行

在 `cd.yml` 中，测试在**部署成功后**执行：

```yaml
- name: deploy
  run: bash deploy.sh

- name: test
  run: pytest
```

测试是部署后的验证步骤——如果冒烟测试失败，说明部署虽然Helm层面成功了，但服务不可用。

### 本地运行测试

```bash
# 安装依赖
pip install pytest requests beautifulsoup4

# 运行所有测试
pytest tests/ -v

# 或直接运行（pytest自动发现tests/目录）
pytest
```

测试需要能访问 https://nbviewer.org。

### 测试依赖

| 包 | 用途 |
|---|------|
| pytest | 测试框架 |
| requests | HTTP客户端 |
| beautifulsoup4 | HTML解析（解析首页提取链接） |

## 密钥管理：git-crypt

所有敏感文件通过git-crypt加密存储在Git仓库中。

### 加密文件清单

根据 `.gitattributes` 配置：

| 模式 | 覆盖文件 | 内容 |
|------|---------|------|
| `secrets/**` | `secrets/` 下所有文件 | kubeconfig、Helm密钥配置、CDN密钥配置 |
| `creds` | 根目录 `creds` | Fastly API密钥、Docker trigger token |
| `newrelic.ini` | New Relic配置 | APM监控配置（文件可能不存在） |
| `env_*` | `env_file`、`env_statuspage` | 容器环境变量 |
| `machine/**` | `machine/` 目录 | 机器配置（目录可能不存在） |

### 加密文件详情

| 文件 | 格式 | 被谁使用 |
|------|------|---------|
| `secrets/ovh-kubeconfig.yaml` | YAML (kubeconfig) | deploy.sh / kubectl |
| `secrets/config/nbviewer.yaml` | YAML (Helm values) | deploy.sh / helm |
| `secrets/config/cdn.yaml` | YAML | 不被deploy.sh使用 |
| `creds` | Python变量赋值 | tasks.py (exec()读取) |
| `env_file` | KEY=VALUE | Helm/nbviewer容器 |
| `env_statuspage` | KEY=VALUE | Helm/statuspage sidecar |

### 解锁方式

**本地解锁**：
```bash
# 使用GPG密钥
git-crypt unlock

# 或使用对称密钥
git-crypt unlock /path/to/keyfile
```

**CI解锁**：
```yaml
- uses: sliteteam/github-action-git-crypt-unlock@...
  env:
    GIT_CRYPT_KEY: ${{ secrets.GIT_CRYPT_KEY }}
```

CI使用存储在GitHub Secrets中的对称密钥解锁。

### pre-commit排除

```yaml
exclude: "(.*/)?secrets/.*"
```

pre-commit hooks不处理secrets目录下的文件，避免格式化或修改加密文件。

## Statuspage Sidecar监控

statuspage作为Kubernetes sidecar容器，监控GitHub API速率限制并上报Statuspage.io。

### 部署方式

statuspage不是独立Deployment，而是作为nbviewer Pod中的sidecar容器：

```yaml
# config/nbviewer.yaml
statuspage:
  enabled: true
  pageId: fzcq6v7wcg65
  metricId: rfcg9djxtg6n
```

Helm Chart根据 `statuspage.enabled` 决定是否在nbviewer Pod中注入statuspage sidecar容器。

### 监控指标

| 指标 | 来源 | 上报频率 |
|------|------|---------|
| GitHub API核心速率剩余百分比 | `https://api.github.com/rate_limit` | 每2分钟 |

**为什么监控GitHub速率？** nbviewer在渲染GitHub/Gist上的Notebook时需要调用GitHub API，如果速率限制耗尽（0%剩余），nbviewer将无法正常服务GitHub上的Notebook。通过Statuspage.io展示此指标，运维团队可以及时发现API限流问题。

### 工作流程

```
无限循环:
  1. GET https://api.github.com/rate_limit (使用OAuth认证)
  2. 计算 percent = 100 * remaining / limit
  3. POST https://api.statuspage.io/v1/pages/{pageId}/metrics/{metricId}/data.json
  4. 异常捕获：打印到stderr，不中断循环
  5. sleep(120) — 等待2分钟
```

### 环境变量（加密存储）

| 变量 | 来源 | 说明 |
|------|------|------|
| `STATUSPAGE_API_KEY` | env_statuspage | Statuspage.io OAuth密钥 |
| `STATUSPAGE_PAGE_ID` | env_statuspage | Statuspage页面ID |
| `STATUSPAGE_METRIC_ID` | env_statuspage | Statuspage指标ID |
| `GITHUB_OAUTH_KEY` | env_statuspage | GitHub OAuth App ID |
| `GITHUB_OAUTH_SECRET` | env_statuspage | GitHub OAuth App Secret |

公开的 `pageId` 和 `metricId` 在 `config/nbviewer.yaml` 中明文配置，密钥通过环境变量注入。

### Docker镜像

statuspage使用独立的轻量级镜像：

```dockerfile
FROM python:3.7-alpine
RUN pip install requests
ADD statuspage.py statuspage.py
CMD ["python", "statuspage.py"]
```

- 基于Python 3.7 Alpine（极小体积）
- 只安装requests一个依赖
- 镜像独立构建和推送（非deployment自动构建）

## 安全注意事项

1. **永远不要提交解密后的secrets文件**：git-crypt自动处理加密/解密，不要手动强制添加解密文件
2. **creds文件格式**：是Python变量赋值语法（被exec()执行），不是YAML/JSON/INI格式
3. **GIT_CRYPT_KEY保护**：GitHub Actions中使用的GIT_CRYPT_KEY secret需要严格控制访问权限
4. **pre-commit排除secrets**：确保pre-commit不会意外处理加密文件
5. **.env.dev类文件**：项目未使用.env文件管理（使用env_file/env_statuspage命名方式），遵循现有模式

## 相关文档

- [Statuspage Sidecar源码](/references/statuspage-source.md)
- [测试源码解析](/references/tests-source.md)
- [部署配置详解](03-deployment-config.md)
