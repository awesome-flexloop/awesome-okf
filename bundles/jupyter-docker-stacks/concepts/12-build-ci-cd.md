---
type: Concept
title: "构建与 CI/CD"
description: "Makefile构建系统、GitHub Actions工作流、Docker BuildKit、多架构构建、Wiki自动更新"
tags: [build, ci-cd, github-actions, makefile, buildkit, multi-arch, wiki]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-makefile, resource: "/references/makefile-ci-source.md", title: "Makefile与CI/CD源码索引" }
---

# 构建与 CI/CD

Jupyter Docker Stacks 使用 Makefile 作为本地构建入口，结合 GitHub Actions 实现自动化构建、测试、标签生成和镜像推送。

## Makefile 构建系统

Makefile 是开发者本地构建和测试的主要入口。

### 关键变量

| 变量 | 默认值 | 说明 |
|------|-------|------|
| REGISTRY | quay.io | 目标镜像仓库 |
| OWNER | jupyter | 仓库命名空间 |
| ROOT_IMAGE | default_root_image | Foundation层基础镜像（可替换） |
| PYTHON_VERSION | 3.13 | Python版本 |
| DOCKER_BUILD_ARGS | (空) | 额外docker build参数 |
| CONTAINER_CLI | auto | 容器引擎（docker或Apple container） |

### 容器引擎自动检测

```makefile
CONTAINER_CLI?=$(if $(shell command -v docker),docker,container)
```

自动检测Docker或Apple Container Framework（macOS），并根据引擎设置不同的命令参数：

| 设置 | Docker | Apple Container |
|------|--------|----------------|
| CONTAINER_NS | docker container | container |
| IMAGE_LS_FLAGS | (空) | --verbose |
| IMAGE_PRUNE_FLAGS | --force | (空) |
| IMAGE_REFS | docker image ls --format | container image ls \| awk |

### BuildKit 强制启用

```makefile
export DOCKER_BUILDKIT:=1
```

所有构建使用BuildKit，支持多阶段构建的bind mount（如Micromamba注入）、并行层构建等。

### 构建目标

```bash
# 构建单个镜像
make build/base-notebook

# 构建所有镜像（按依赖顺序）
make build-all

# 构建时覆盖参数
make build/docker-stacks-foundation PYTHON_VERSION=3.12 ROOT_IMAGE=ubuntu:22.04
```

构建命令等价于：
```bash
docker build --tag quay.io/jupyter/<image-name> ./images/<image-name> \
    --build-arg REGISTRY=quay.io \
    --build-arg OWNER=jupyter \
    --build-arg ROOT_IMAGE=default_root_image \
    --build-arg PYTHON_VERSION=3.13
```

### Hook目标（标签+清单生成）

```bash
make hook/base-notebook
```

在构建完成后运行tagging工具，生成标签文件和软件清单，然后应用标签到镜像。

### 测试目标

```bash
make test/base-notebook
make test-all
```

调用`tests.run_tests`，使用pytest-xdist并行执行测试。

### 其他常用目标

| 目标 | 功能 |
|------|------|
| `make pull/all` | 拉取所有镜像 |
| `make push/all` | 推送所有镜像的所有标签 |
| `make run-shell/%` | 以jovyan用户进入容器bash |
| `make run-sudo-shell/%` | 以root用户进入容器bash |
| `make cont-clean-all` | 停止并删除所有容器 |
| `make img-rm` | 删除dangling和jupyter镜像 |
| `make docs` | Sphinx构建HTML文档 |
| `make linkcheck-docs` | Sphinx链接检查 |
| `make check-outdated/%` | 检查过时包 |

## GitHub Actions 工作流

项目使用多个GitHub Actions工作流实现CI/CD自动化。

### 主构建工作流：docker-build-test-upload.yml

这是核心CI/CD流水线，在push到main分支和PR时触发：

1. **构建阶段**：使用Docker Buildx构建所有镜像
   - 支持linux/amd64和linux/arm64双架构
   - 使用cache-from/cache-to加速构建
2. **测试阶段**：对每个镜像运行pytest测试
3. **Hook阶段**：运行tagging工具生成标签和清单
4. **上传阶段**：推送镜像到Quay.io（仅main分支）

### 标签推送工作流

- **docker-tag-push.yml**：创建日期标签时推送
- **docker-tag-merge.yml**：合并PR后的标签处理
- **docker-tag-push-merge.yml**：合并后的标签推送

标签系统支持：
- 日期标签（每周构建）
- 多平台manifest list
- 从SHA派生的不可变标签

### Wiki更新：docker-wiki-update.yml

自动从镜像manifest生成GitHub Wiki页面，包含：
- 每个镜像安装的包列表
- 版本信息表格
- 构建历史

wiki/目录包含实现这个功能的Python工具。

### 其他工作流

| 工作流 | 功能 |
|--------|------|
| docker.yml | PR时的快速构建测试（不推送） |
| contributed-recipes.yml | 社区贡献配方（docs/using/recipe_code/）测试 |
| pre-commit.yml | pre-commit钩子检查（lint、格式） |
| codeql.yml | CodeQL安全分析 |
| scorecard.yml | OpenSSF评分卡安全审计 |
| sphinx.yml | Sphinx文档构建（ReadTheDocs替代） |
| registry-overviews.yml | Registry概览页面更新 |
| registry-move.yml | Registry迁移工具 |
| image-delete.yml | 旧镜像清理 |

## 多架构构建

从2022-09-21起，除tensorflow-notebook外的所有镜像都是多平台镜像（linux/amd64 + linux/arm64）。tensorflow-notebook从2023-06-01起也支持多平台。

### 多架构构建策略

1. 使用`docker buildx build --platform linux/amd64,linux/arm64`
2. 每个架构单独构建，生成平台标签（`x86_64-...`、`aarch64-...`）
3. 通过`docker buildx imagetools create`合并为manifest list
4. merge_tags工具合并多平台标签

### 自托管Runner历史

- 2022-07-05至2023-10-31：aarch64构建使用@mathbunnyru赞助的self-hosted runner
- 2023-10-31至2025-02-11：使用2i2c非营利组织赞助的aarch64 runner
- 2025-02-11起：使用GitHub-hosted aarch64 runner

## Docker BuildKit 特性使用

项目充分利用BuildKit特性来优化构建：

### Multi-stage Build

```dockerfile
FROM mambaorg/micromamba:2.8.1@sha256:... AS micromamba
FROM $ROOT_IMAGE
RUN --mount=type=bind,from=micromamba,source=/bin/micromamba,target=/usr/local/bin/micromamba \
    micromamba install ...
```

Micromamba通过bind mount从多阶段构建注入，安装后不保留在最终镜像中。

### Cache Mounts

虽然当前Dockerfile中没有显式使用`--mount=type=cache`，但BuildKit的层缓存机制自动优化构建速度。

### Secrets Mounts

GitHub Actions中使用`--mount=type=secret`传递Registry凭据。

## 文档构建

文档使用Sphinx + MyST parser构建（docs/目录）：

- 用户指南：镜像选择、运行方法、常用配置、故障排除
- 贡献者指南：开发设置、问题处理、功能贡献、测试、Lint、社区配方
- 维护者指南：新镜像/包策略、标签管理、维护任务

Makefile目标：
```bash
make docs              # 构建HTML
make linkcheck-docs    # 检查断链
```

## Wiki自动更新

wiki/目录的工具自动生成GitHub Wiki内容：
- `update_wiki.py`：主程序，从镜像manifest数据生成Wiki页面
- `config.py`：Wiki更新配置
- `manifest_time.py`：Manifest时间戳处理

每次构建后，CI自动运行这些工具更新Wiki，确保文档与镜像内容同步。

## 本地开发工作流

1. **环境准备**：Docker、Python 3、pre-commit
2. **构建镜像**：`make build/base-notebook`
3. **运行测试**：`make test/base-notebook`
4. **调试**：`make run-shell/base-notebook`（jovyan用户）或`make run-sudo-shell/base-notebook`（root）
5. **文档**：`make docs`
6. **提交前**：pre-commit自动运行lint和格式检查

## 相关概念

- [Tagging元数据系统](10-tagging-system.md)
- [测试框架](11-testing-framework.md)
- [最佳实践](13-best-practices.md)
- [基础启动示例](../examples/01-basic-run.md)
