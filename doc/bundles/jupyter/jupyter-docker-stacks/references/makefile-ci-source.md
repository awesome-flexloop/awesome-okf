---
type: Reference
title: "Makefile与CI/CD源码索引"
description: "Jupyter Docker Stacks 构建系统（Makefile、GitHub Actions）源码信源登记"
tags: [makefile, build, ci-cd, github-actions, docker]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-makefile, resource: "external/libs/jupyter/docker-stacks/Makefile", title: "Makefile（构建入口）" }
  - { id: src-workflow-build, resource: "external/libs/jupyter/docker-stacks/.github/workflows/docker.yml", title: "docker.yml（主构建工作流）" }
  - { id: src-workflow-build-test, resource: "external/libs/jupyter/docker-stacks/.github/workflows/docker-build-test-upload.yml", title: "docker-build-test-upload.yml（构建测试上传）" }
  - { id: src-workflow-tag-push, resource: "external/libs/jupyter/docker-stacks/.github/workflows/docker-tag-push.yml", title: "docker-tag-push.yml（标签推送）" }
  - { id: src-wiki-update, resource: "external/libs/jupyter/docker-stacks/.github/workflows/docker-wiki-update.yml", title: "docker-wiki-update.yml（Wiki更新）" }
  - { id: src-wiki, resource: "external/libs/jupyter/docker-stacks/wiki/", title: "wiki/（Wiki自动更新工具）" }
  - { id: src-docs, resource: "external/libs/jupyter/docker-stacks/docs/", title: "docs/（Sphinx官方文档）" }
---

# Makefile与CI/CD源码索引

## Makefile 目标

| 目标 | 说明 |
|------|------|
| `help` | 自动文档化帮助（解析##注释） |
| `build/%` | 构建单个镜像（如 `make build/base-notebook`） |
| `build-all` | 按依赖顺序构建所有镜像 |
| `test/%` | 测试单个镜像 |
| `test-all` | 测试所有镜像 |
| `hook/%` | 运行构建后Hook（生成标签和清单） |
| `hook-all` | 运行所有镜像的Hook |
| `pull/%` | 拉取镜像 |
| `pull-all` | 拉取所有镜像 |
| `push/%` | 推送镜像所有标签 |
| `push-all` | 推送所有镜像 |
| `run-shell/%` | 以jovyan用户交互式运行bash |
| `run-sudo-shell/%` | 以root用户交互式运行bash |
| `check-outdated/%` | 检查过时的conda/mamba包 |
| `cont-stop-all` | 停止所有容器 |
| `cont-rm-all` | 删除所有容器 |
| `cont-clean-all` | 停止+删除所有容器 |
| `img-list` | 列出本地jupyter镜像 |
| `img-rm` | 删除dangling和jupyter镜像 |
| `docs` | Sphinx构建HTML文档 |
| `linkcheck-docs` | Sphinx链接检查 |

## 关键Makefile变量

| 变量 | 默认值 | 说明 |
|------|-------|------|
| REGISTRY | quay.io | 镜像仓库 |
| OWNER | jupyter | 仓库命名空间 |
| ROOT_IMAGE | default_root_image | Foundation层根镜像 |
| PYTHON_VERSION | 3.13 | Python版本 |
| DOCKER_BUILD_ARGS | (空) | 额外docker build参数 |
| CONTAINER_CLI | auto(docker/container) | 容器引擎 |
| DOCKER_BUILDKIT | 1 | 启用BuildKit |

## 构建顺序（ALL_IMAGES）

```
docker-stacks-foundation → base-notebook → minimal-notebook → scipy-notebook
  ├→ r-notebook
  ├→ julia-notebook
  ├→ tensorflow-notebook
  ├→ pytorch-notebook
  ├→ datascience-notebook
  └→ pyspark-notebook → all-spark-notebook
```

## GitHub Actions 工作流

| 工作流文件 | 功能 |
|-----------|------|
| docker.yml | PR/push时构建测试 |
| docker-build-test-upload.yml | 主构建测试上传流水线 |
| docker-tag-push.yml | 标签创建与推送 |
| docker-tag-push-merge.yml | 合并后标签推送 |
| docker-tag-merge.yml | 标签合并 |
| docker-wiki-update.yml | 自动更新GitHub Wiki |
| registry-overviews.yml | Registry概览更新 |
| registry-move.yml | Registry迁移 |
| image-delete.yml | 镜像删除 |
| contributed-recipes.yml | 社区贡献配方测试 |
| pre-commit.yml | pre-commit检查 |
| codeql.yml | CodeQL安全分析 |
| scorecard.yml | OpenSSF评分卡 |
| sphinx.yml | Sphinx文档构建 |

## Wiki 自动更新工具

wiki/ 目录包含Python工具，自动从镜像manifest生成GitHub Wiki页面：
- `config.py`：Wiki更新配置
- `update_wiki.py`：Wiki更新主程序
- `manifest_time.py`：Manifest时间戳处理
