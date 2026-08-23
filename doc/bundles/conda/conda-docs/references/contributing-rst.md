---
okf_version: "0.2"
type: reference
title: "贡献指南 contributing.rst 关键内容"
sources:
  - docs/source/contributing.rst
---

# 贡献指南 contributing.rst 关键内容

`contributing.rst` 是 Conda 社区贡献入门指南。

## Issue 路由规则

| 问题类型 | 目标仓库 |
|---------|---------|
| 特定 conda 包问题 | ContinuumIO/anaconda-issues |
| anaconda.org 问题 | Anaconda-Platform/support |
| repo.anaconda.com 问题 | ContinuumIO/anaconda-issues |
| `conda build` 命令问题 | conda/conda-build |
| `conda env` 命令问题 | conda/conda |
| 其他 conda 命令问题 | conda/conda |

## Bash 开发环境

**Fork 并克隆：**

```bash
CONDA_PROJECT_ROOT="$HOME/conda"
GITHUB_USERNAME=<your-username>
git clone git@github.com:$GITHUB_USERNAME/conda "$CONDA_PROJECT_ROOT"
cd "$CONDA_PROJECT_ROOT"
git remote add upstream git@github.com:conda/conda
```

**创建隔离开发环境：**

```bash
. dev/start
```

在 `./devenv` 创建项目隔离 Miniconda 环境。验证：`conda info --all` 检查 `conda location:` 指向项目目录。

**运行测试：**

```bash
make unit
# 或
py.test -m "not integration and not installed" conda tests
# 聚焦单个测试
py.test tests/test_create.py -k create_install_update_remove_smoketest
```

## Windows cmd.exe 开发环境

```cmd
set "CONDA_PROJECT_ROOT=%HOMEPATH%\conda"
set GITHUB_USERNAME=<your-username>
git clone git@github.com:conda/conda "%CONDA_PROJECT_ROOT%"
cd "%CONDA_PROJECT_ROOT%"
git remote add %GITHUB_USERNAME% git@github.com:%GITHUB_USERNAME%/conda
.\dev\start
```

## CLA 签署

通过 EchoSign 电子签名系统签署 CLA（类似 Django 和 Python 的 CLA 机制），需人工审核批准。

## 文档规范

- "conda" 小写，句首/标题除外；命令用 `` `conda` `` 代码格式
- 新增页面必须更新对应 index.rst 的 toctree
- conda-docs 的 toctree 在 `docs/source/index.rst`

## 相关概念

- [贡献指南与开发环境](../concepts/05-contributing.md)
- [社区支持与资源渠道](../concepts/06-community-support.md)
- [本地构建 conda-docs](../examples/local-build.md)
