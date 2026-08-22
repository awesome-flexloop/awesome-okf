---
title: 生成日志
id: bundle-log
version: 1.0.0
okf-spec: v0.2
bundle: nbviewer
---

# nbviewer.org-deploy Wiki 生成日志

## 生成信息

| 项目 | 值 |
|------|-----|
| OKF 规范版本 | v0.2 |
| 源码仓库 | jupyter/nbviewer.org-deploy (main分支) |
| 源码路径 | `external/libs/jupyter/nbviewer.org-deploy` |
| 生成路径 | `projects/awesome-okf-xs/bundles/jupyter/nbviewer` |
| Helm版本 | v3.12.0 |
| kubectl版本 | v1.29.15 |
| Python (CI) | 3.13 |
| 生成日期 | 2026-08-22 |

## 文档结构

```
nbviewer/
├── index.md                    # Bundle主入口
├── log.md                      # 本文件（生成日志）
├── concepts/                   # 概念文档（9篇）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-architecture-overview.md
│   ├── 03-deployment-config.md
│   ├── 04-cicd-and-automation.md
│   ├── 05-version-update.md
│   ├── 06-helm-deploy-process.md
│   ├── 07-fastly-cdn.md
│   ├── 08-testing-and-secrets.md
│   └── 08-uri-rewrite.md       # nbviewer主应用文档（非deploy，已保留）
├── examples/                   # 实操示例（3篇）
│   ├── index.md
│   ├── invoke-tasks.md
│   ├── local-debug.md
│   └── manual-upgrade.md
└── references/                 # 源码信源（6篇+索引）
    ├── index.md
    ├── project-meta-source.md
    ├── config-source.md
    ├── cicd-source.md
    ├── tasks-source.md
    ├── statuspage-source.md
    └── tests-source.md
```

## 文件统计

| 目录 | 文件数 |
|------|--------|
| concepts/ | 10（含index + 08-uri-rewrite.md） |
| examples/ | 4（含index） |
| references/ | 7（含index） |
| 根目录 | 2 |
| **合计** | **23** |

## R 阶段（事实采集）覆盖的源码

### 核心脚本（2个）

| 文件 | 行数 | 用途 |
|------|------|------|
| `deploy.sh` | 31 | Helm部署执行脚本（CI/本地双模式） |
| `tasks.py` | 151 | pyinvoke任务（Fastly CDN管理） |

### 配置文件（5个）

| 文件 | 用途 |
|------|------|
| `config/nbviewer.yaml` | Helm公开values（副本数、镜像、参数、statuspage配置） |
| `config/cdn.yaml` | CDN配置（**空文件**，不被deploy.sh使用） |
| `secrets/config/nbviewer.yaml` | Helm密钥values（git-crypt加密） |
| `secrets/config/cdn.yaml` | CDN密钥配置（git-crypt加密，不被deploy.sh使用） |
| `secrets/ovh-kubeconfig.yaml` | OVH K8s kubeconfig（git-crypt加密） |

### CI/CD（2个工作流 + 2个脚本）

| 文件 | 用途 |
|------|------|
| `.github/workflows/cd.yml` | 主部署流水线（checkout→install→unlock→deploy→test） |
| `.github/workflows/watch-dependencies.yaml` | 自动版本检查+PR创建 |
| `scripts/update-nbviewer.py` | 版本检测和更新（cd.yml + config/nbviewer.yaml） |
| `scripts/get-prs.py` | PR列表提取（用于PR描述生成） |

### Statuspage（2个文件）

| 文件 | 用途 |
|------|------|
| `statuspage/statuspage.py` | GitHub API速率监控脚本（2分钟循环上报） |
| `statuspage/Dockerfile` | python:3.7-alpine独立镜像 |

### 测试（1个文件）

| 文件 | 用途 |
|------|------|
| `tests/test_nbviewer.py` | 冒烟测试（BeautifulSoup解析首页 + 参数化链接检查） |

### 项目元文件（7个）

| 文件 | 用途 |
|------|------|
| `README.md` | 项目说明和运维指南 |
| `pyproject.toml` | pytest配置 + Ruff lint规则 |
| `requirements.in` | 直接依赖（5个包） |
| `requirements.txt` | 锁定依赖（pip-compile生成） |
| `.gitattributes` | git-crypt加密规则（5个模式） |
| `.pre-commit-config.yaml` | pre-commit hooks（ruff + prettier + 通用hooks） |
| `.github/dependabot.yml` | 月度依赖更新（pip + github-actions） |

### 加密文件（4个）

| 文件 | 加密方式 | 被谁使用 |
|------|---------|---------|
| `creds` | git-crypt | tasks.py（exec()读取FASTLY_KEY等） |
| `env_file` | git-crypt | Helm注入nbviewer容器 |
| `env_statuspage` | git-crypt | Helm注入statuspage sidecar |
| `secrets/**` | git-crypt | deploy.sh（kubeconfig + Helm密钥） |

## I 阶段（架构洞察）关键发现

1. **deploy.sh极简设计**：仅31行bash，通过CI环境变量区分CI/本地模式，不生成中间values文件
2. **config/cdn.yaml是空文件**：CDN管理完全通过Fastly API（tasks.py），不通过Helm values
3. **Fastly后端IP硬编码**：all_instances()中写死135.125.83.237:80，代码标注TODO需从K8s自动发现
4. **copy-backend模式**：新后端复制第一个现有后端的8个配置字段，保证一致性
5. **upgrade任务未实现**：invoke upgrade抛NotImplementedError，部署通过deploy.sh而非invoke
6. **冒烟测试针对生产环境**：测试直接请求https://nbviewer.org，不是测试环境
7. **statuspage是sidecar**：不是独立Deployment，而是nbviewer Pod中的sidecar容器
8. **双位置版本号**：NBVIEWER_VERSION（cd.yml）和image tag（config/nbviewer.yaml）必须同步

## 事实纠偏记录

本次生成纠正了以下常见文档错误：

| 错误描述 | 正确事实 |
|---------|---------|
| deploy.sh生成helm-values.deploy.yaml | 不生成，直接用两个-f参数 |
| deploy.sh使用GITHUB_REF_NAME | 不使用Git引用 |
| deploy.sh最后同步CDN | 不同步，需手动invoke fastly |
| tasks.py有lock-cdn/unlock-cdn/sync-cdn-backends任务 | 只有fastly/trigger-build/doitall/upgrade |
| tasks.py有SERVICE_ID等硬编码常量 | 凭据从creds文件读取，只有IP硬编码 |
| tests/有conftest.py/test_app.py/test_statuspage.py | 只有test_nbviewer.py |
| 测试有指数退避重试助手 | 无重试机制 |
| statuspage是Helm Chart的一部分 | statuspage/是独立目录，有自己的Dockerfile |
| config/cdn.yaml包含CDN配置 | 文件为空，不被deploy.sh使用 |
| deploy.sh有-f标志指定额外values | 只有config/nbviewer.yaml和secrets/config/nbviewer.yaml |

## 已知限制

1. **secrets/目录下加密文件的明文内容**无法验证（未解密），仅根据非加密文件的引用推断其用途
2. **Helm Chart内部模板**（nbviewer仓库中的helm-chart）未深入分析，本文档仅关注deploy仓库侧的配置和流程
3. **Cloudflare DNS配置**无法从代码中获取，仅记录README中的说明
4. **New Relic配置**（newrelic.ini在.gitattributes中）文件在仓库中不存在，可能已废弃
5. **machine/**目录在.gitattributes中加密但仓库中不存在
6. **08-uri-rewrite.md**是nbviewer主应用的文档（非deploy），保留在原位置未做修改

## 后续更新建议

- 每次nbviewer版本升级时更新index.md中的当前版本信息
- 如果Fastly后端IP变更，更新concepts/02-architecture-overview.md和07-fastly-cdn.md中的IP地址
- 如果Helm/kubectl版本在cd.yml中更新，更新文档中的版本引用
- 如果all_instances()改为从Kubernetes自动发现IP，更新07-fastly-cdn.md
- 如果invoke upgrade被实现，更新06-helm-deploy-process.md和examples/invoke-tasks.md
