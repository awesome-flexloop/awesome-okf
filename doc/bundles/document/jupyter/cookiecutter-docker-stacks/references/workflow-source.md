---
type: Reference
title: "CI/CD 工作流源码索引"
description: "cookiecutter-docker-stacks 模板CI/CD工作流与预设配置源码信源登记"
tags: [cicd, github-actions, workflow, config, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-docker-yml, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/.github/workflows/docker.yml", title: "模板docker.yml" }
  - { id: src-tests-yml, resource: "external/libs/jupyter/cookiecutter-docker-stacks/.github/workflows/tests.yml", title: "cookiecutter自身tests.yml" }
  - { id: src-dependabot, resource: "external/libs/jupyter/cookiecutter-docker-stacks/.github/dependabot.yml", title: "dependabot.yml" }
  - { id: src-precommit, resource: "external/libs/jupyter/cookiecutter-docker-stacks/.pre-commit-config.yaml", title: ".pre-commit-config.yaml" }
---

# CI/CD 工作流源码索引

本文档登记 cookiecutter-docker-stacks 的 CI/CD 工作流文件与预设配置的源码路径与关键内容概要。

## 生成项目的 CI/CD 工作流（docker.yml）

### 触发条件

| 事件 | 条件 |
|------|------|
| schedule | 每周一 07:00 UTC（cron: "0 7 * * 1"） |
| pull_request | 路径匹配：.github/workflows/docker.yml、image/**、tests/**、requirements-dev.txt |
| push (main) | 同上路径匹配 |
| workflow_dispatch | 手动触发 |

### 执行步骤

| 步骤 | Action/命令 | 说明 |
|------|------------|------|
| Checkout Repo | actions/checkout@v7.0.0 | 检出代码 |
| Set Up Python | actions/setup-python@v6.3.0 | Python 3.12 |
| Install Dev Dependencies | pip install -r requirements-dev.txt | 安装docker/pytest/requests |
| Get commit sha | shell命令截取前12位 | 用于镜像tag |
| Build image | docker build (BuildKit) | 双tag: owner/name + owner/name:sha12 |
| Run tests | python3 -m pytest tests | TEST_IMAGE环境变量指定镜像 |
| Login to Docker Hub | docker/login-action@v4.4.0 | main分支或定时任务才执行 |
| Push Image | docker push --all-tags | main分支或定时任务才执行 |

### 关键配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| runs-on | ubuntu-24.04 | 构建运行器 |
| concurrency group | `${{ github.workflow }}-${{ github.ref }}` | 同分支并发取消 |
| DOCKER_BUILDKIT | 1 | 启用BuildKit |
| BUILDKIT_PROGRESS | plain | 完整构建日志 |
| permissions.contents | write | 允许写内容 |

## cookiecutter 自身测试工作流（tests.yml）

### 矩阵策略

对14个配置文件逐一测试：

```
foundation.yaml, base.yaml, minimal.yaml, scipy.yaml,
r.yaml, julia.yaml, tensorflow.yaml, tensorflow-cuda.yaml,
pytorch.yaml, pytorch-cuda11.yaml, pytorch-cuda12.yaml,
datascience.yaml, pyspark.yaml, all-spark.yaml
```

### 执行步骤

| 步骤 | 命令 | 说明 |
|------|------|------|
| Install cookiecutter | pip install -r requirements-test.txt | 安装cookiecutter |
| Create project | cookiecutter --no-input --config-file configs/${{matrix.config}} | 使用预设配置生成项目 |
| Build image | docker build image/ | 在/tmp/my-jupyter-stack下构建 |
| Install test deps | pip install -r requirements-dev.txt | 安装测试依赖 |
| Run tests | pytest tests/ | foundation.yaml跳过（无Jupyter Server） |

## 预设配置文件（configs/）

每个YAML配置只设置 `default_context.stack_base_image`：

| 配置文件 | 基础镜像 |
|---------|---------|
| foundation.yaml | quay.io/jupyter/docker-stacks-foundation |
| base.yaml | quay.io/jupyter/base-notebook |
| minimal.yaml | quay.io/jupyter/minimal-notebook |
| scipy.yaml | quay.io/jupyter/scipy-notebook |
| r.yaml | quay.io/jupyter/r-notebook |
| julia.yaml | quay.io/jupyter/julia-notebook |
| tensorflow.yaml | quay.io/jupyter/tensorflow-notebook |
| tensorflow-cuda.yaml | quay.io/jupyter/tensorflow-notebook:cuda-latest |
| pytorch.yaml | quay.io/jupyter/pytorch-notebook |
| pytorch-cuda11.yaml | quay.io/jupyter/pytorch-notebook:cuda11-latest |
| pytorch-cuda12.yaml | quay.io/jupyter/pytorch-notebook:cuda12-latest |
| datascience.yaml | quay.io/jupyter/datascience-notebook |
| pyspark.yaml | quay.io/jupyter/pyspark-notebook |
| all-spark.yaml | quay.io/jupyter/all-spark-notebook |

## pre-commit 配置钩子

| 钩子 | 版本 | 用途 |
|------|------|------|
| pyupgrade | v3.21.2 | Python语法升级（--py312-plus） |
| isort | 9.0.0a3 | import排序（black profile） |
| black | 26.5.1 | Python格式化（target py312） |
| mypy | v2.1.0 | 静态类型检查（manual阶段） |
| prettier | v3.9.4 | YAML/JSON/Markdown格式化 |
| pre-commit-hooks | v6.0.0 | 通用检查（大文件/EOF/空白） |
| hadolint | v2.14.0 | Dockerfile lint |
| yamllint | v1.38.0 | YAML lint |
| flake8 | 7.3.0 | Python lint |
| markdownlint-cli2 | v0.23.0 | Markdown lint |
