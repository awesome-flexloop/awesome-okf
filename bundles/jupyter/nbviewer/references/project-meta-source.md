---
type: Reference
title: "项目元信息源码"
description: "README.md、pyproject.toml、requirements.txt、.gitattributes、.pre-commit-config.yaml等项目元文件解析"
tags: [nbviewer, deploy, project-meta, readme, requirements, pre-commit, git-crypt]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/README.md"
    title: "README.md"
  - id: pyproject
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/pyproject.toml"
    title: "pyproject.toml"
  - id: requirements
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/requirements.txt"
    title: "requirements.txt"
  - id: requirements-in
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/requirements.in"
    title: "requirements.in"
  - id: gitattributes
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/.gitattributes"
    title: ".gitattributes"
  - id: pre-commit
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/.pre-commit-config.yaml"
    title: ".pre-commit-config.yaml"
  - id: gitignore
    resource: "../../../../../external/libs/jupyter/nbviewer.org-deploy/.gitignore"
    title: ".gitignore"
---

# 项目元信息源码

本信源登记 nbviewer.org-deploy 项目的元数据文件和基础配置。

## 项目概况（来自README）

| 属性 | 值 |
|------|---|
| 项目名 | nbviewer.org-deploy |
| 用途 | nbviewer.org 的部署仓库 |
| 部署方式 | Helm on OVHCloud (namespace: `nbviewer`) |
| Helm Chart来源 | 本地checkout的jupyter/nbviewer仓库中的helm-chart（不发布到chart仓库） |
| 自动化 | GitHub Actions（cd.yml + watch-dependencies.yaml） |
| 手动任务 | Fastly CDN管理通过pyinvoke脚本（tasks.py） |
| 许可证 | LICENSE文件（BSD风格，继承Jupyter项目） |

### README TODO项

README明确列出了两个待改进项：

1. **Fastly硬编码IP**：`tasks.py`中的 `all_instances()` 函数硬编码了负载均衡器IP，变更时需手动更新并运行 `invoke fastly`。代码中标注了TODO：应从Kubernetes自动获取服务IP。
2. **Cloudflare DNS手动管理**：`cdn.jupyter.org` 通过Cloudflare DNS代理，IP变更需在 https://dash.cloudflare.com/dns 手动更新。

### 版本更新步骤（README记录）

nbviewer版本存在于两个位置：
1. `.github/workflows/cd.yml` 中的 `NBVIEWER_VERSION`（chart版本，即nbviewer repo的commit hash）
2. `config/nbviewer.yaml` 中的 `image`（Docker镜像标签）

## pyproject.toml

```toml
[project]
name = "nbviewer.org-deploy"

[tool.pytest.ini_options]
addopts = "-v"
testpaths = ["tests"]

[tool.ruff.lint]
select = ["E9", "I", "UP", "F"]
```

| 节 | 配置 | 说明 |
|----|------|------|
| `[project]` | `name = "nbviewer.org-deploy"` | 项目名称（最小化配置，无版本号/依赖声明） |
| `[tool.pytest.ini_options]` | `addopts = "-v"`, `testpaths = ["tests"]` | pytest配置 |
| `[tool.ruff.lint]` | `select = ["E9", "I", "UP", "F"]` | Ruff linter规则选择 |

### Ruff规则说明

| 规则代码 | 名称 | 说明 |
|---------|------|------|
| E9 | pycodestyle Error | 语法错误检测 |
| I | isort | import排序 |
| UP | pyupgrade | 旧版本Python兼容代码升级建议 |
| F | PyFlakes | 未使用变量/导入等静态检查 |

## Python依赖

### requirements.in（直接依赖）

```
beautifulsoup4
pygithub
pytest
pyyaml
requests
```

| 包 | 用途 |
|---|------|
| `beautifulsoup4` | HTML解析（test_nbviewer.py解析首页） |
| `pygithub` | GitHub API客户端（get-prs.py获取PR列表） |
| `pytest` | 测试框架 |
| `pyyaml` | YAML解析（update-nbviewer.py读写配置文件） |
| `requests` | HTTP客户端（tasks.py Fastly API、statuspage.py、update-nbviewer.py） |

### requirements.txt（锁定依赖，pip-compile生成）

由 pip-compile with Python 3.12 生成，锁定版本如下：

| 包 | 版本 | 说明 |
|---|------|------|
| beautifulsoup4 | 4.13.5 | HTML解析 |
| certifi | 2025.8.3 | CA证书（requests依赖） |
| cffi | 2.0.0 | C FFI（cryptography依赖） |
| charset-normalizer | 3.4.3 | 字符编码检测（requests依赖） |
| cryptography | 46.0.1 | 加密库（pyjwt依赖） |
| idna | 3.10 | 国际化域名（requests依赖） |
| iniconfig | 2.1.0 | INI解析（pytest依赖） |
| packaging | 25.0 | 版本解析（pytest依赖） |
| pluggy | 1.6.0 | 插件系统（pytest依赖） |
| pycparser | 2.23 | C解析器（cffi依赖） |
| pygithub | 2.8.1 | GitHub API |
| pygments | 2.19.2 | 语法高亮（pytest依赖） |
| pyjwt[crypto] | 2.10.1 | JWT处理（pygithub依赖） |
| pynacl | 1.6.0 | NaCl加密（pygithub依赖） |
| pytest | 8.4.2 | 测试框架 |
| pyyaml | 6.0.2 | YAML处理 |
| requests | 2.32.5 | HTTP客户端 |
| soupsieve | 2.8 | CSS选择器（beautifulsoup4依赖） |
| typing-extensions | 4.15.0 | 类型扩展 |
| urllib3 | 2.5.0 | HTTP客户端底层 |

## .gitattributes（git-crypt加密配置）

```
secrets/** filter=git-crypt diff=git-crypt
creds filter=git-crypt diff=git-crypt
newrelic.ini filter=git-crypt diff=git-crypt
env_* filter=git-crypt diff=git-crypt
machine/** filter=git-crypt diff=git-crypt
```

| 模式 | 覆盖文件 | 状态 |
|------|---------|------|
| `secrets/**` | secrets/下所有文件（kubeconfig、密钥配置） | 加密 |
| `creds` | 根目录creds文件（Fastly/Docker凭据） | 加密 |
| `newrelic.ini` | New Relic配置 | 加密（文件可能不存在） |
| `env_*` | env_file、env_statuspage等环境变量文件 | 加密 |
| `machine/**` | machine/目录下所有文件 | 加密（目录可能不存在） |

## .pre-commit-config.yaml

```yaml
exclude: "(.*/)?secrets/.*"

ci:
  autoupdate_schedule: monthly

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.3
    hooks:
      - id: ruff
        types_or: [python]
        args: ["--fix", "--show-fixes"]
      - id: ruff-format
        types_or: [python]

  - repo: https://github.com/rbubley/mirrors-prettier
    rev: v3.6.2
    hooks:
      - id: prettier

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
      - id: check-executables-have-shebangs
```

| Hook | 工具 | 版本 | 说明 |
|------|------|------|------|
| ruff | ruff-pre-commit | v0.14.3 | Python lint（自动修复） |
| ruff-format | ruff-pre-commit | v0.14.3 | Python代码格式化 |
| prettier | mirrors-prettier | v3.6.2 | Markdown/YAML/JS格式化 |
| end-of-file-fixer | pre-commit-hooks | v6.0.0 | 文件末尾换行修复 |
| check-executables-have-shebangs | pre-commit-hooks | v6.0.0 | 可执行文件必须有shebang |

**注意**：`exclude: "(.*/)?secrets/.*"` 排除secrets目录下的文件，避免pre-commit处理加密文件。pre-commit.ci每月自动更新hooks版本。

## .gitignore

标准Python .gitignore，排除：
- `__pycache__/`、`*.py[cod]`（字节码）
- `*.so`（C扩展）
- 打包目录（build/、dist/、*.egg-info/等）
- 虚拟环境（env/）
- 测试缓存（.tox/、.coverage、.cache/等）
- `.ipynb_checkpoints`、`.DS_Store`

## 仓库文件结构

```
nbviewer.org-deploy/
├── .github/
│   ├── workflows/
│   │   ├── cd.yml                  # 部署流水线
│   │   └── watch-dependencies.yaml # 自动更新检查
│   └── dependabot.yml              # 依赖自动更新
├── config/
│   ├── cdn.yaml                    # CDN配置（空文件）
│   └── nbviewer.yaml               # Helm公开配置
├── scripts/
│   ├── get-prs.py                  # 获取PR列表（用于PR描述）
│   └── update-nbviewer.py          # 检查并更新nbviewer版本
├── secrets/
│   ├── config/
│   │   ├── cdn.yaml                # CDN密钥（加密）
│   │   └── nbviewer.yaml           # Helm密钥（加密）
│   └── ovh-kubeconfig.yaml         # OVH kubeconfig（加密）
├── statuspage/
│   ├── Dockerfile                  # Statuspage镜像构建
│   └── statuspage.py               # GitHub速率监控脚本
├── tests/
│   └── test_nbviewer.py            # 冒烟测试
├── .gitattributes                  # git-crypt加密规则
├── .gitignore                      # Git忽略规则
├── .pre-commit-config.yaml         # pre-commit hooks配置
├── LICENSE                         # 许可证
├── README.md                       # 项目说明
├── creds                           # Fastly/Docker凭据（加密）
├── deploy.sh                       # Helm部署脚本
├── env_file                        # nbviewer环境变量（加密）
├── env_statuspage                  # statuspage环境变量（加密）
├── pyproject.toml                  # Python项目配置
├── requirements.in                 # 直接依赖声明
├── requirements.txt                # 锁定依赖（pip-compile生成）
└── tasks.py                        # pyinvoke任务（Fastly CDN管理）
```

## 相关信源

- [部署配置文件源码](config-source.md)
- [Invoke任务源码](tasks-source.md)
- [CI/CD工作流源码](cicd-source.md)
- [测试源码解析](tests-source.md)
