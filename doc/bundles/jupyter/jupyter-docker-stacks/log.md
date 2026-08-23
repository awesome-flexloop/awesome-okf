---
title: 生成日志
id: bundle-log
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
---

# Jupyter Docker Stacks Wiki 生成日志

## 生成信息

| 项目 | 值 |
|------|-----|
| OKF 规范版本 | v0.2 |
| 源码版本 | jupyter/docker-stacks main 分支 |
| 源码路径 | `external/libs/jupyter/docker-stacks` |
| 生成路径 | `projects/awesome-okf-xs/bundles/jupyter-docker-stacks` |
| 基础镜像版本 | Ubuntu 24.04 |
| 默认 Python 版本 | 3.12 |
| 镜像标签参考 | `2026-07-28` |
| 生成日期 | 2026-08-21 |

## 文档结构

```
jupyter-docker-stacks/
├── index.md                    # 主入口文档（镜像速查表、环境变量、导航）
├── log.md                      # 本文件（生成日志）
├── concepts/                   # 概念文档（14 篇）
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-image-hierarchy.md
│   ├── 03-foundation-layer.md
│   ├── 04-base-notebook.md
│   ├── 05-minimal-scipy.md
│   ├── 06-specialized-stacks.md
│   ├── 07-startup-lifecycle.md
│   ├── 08-hooks-and-customization.md
│   ├── 09-user-permissions.md
│   ├── 10-tagging-system.md
│   ├── 11-testing-framework.md
│   ├── 12-build-ci-cd.md
│   └── 13-best-practices.md
├── examples/                   # 示例文档（5 篇 + 索引）
│   ├── index.md
│   ├── 01-basic-run.md
│   ├── 02-custom-image.md
│   ├── 03-gpu-cuda.md
│   ├── 04-ci-integration.md
│   └── 05-recipes.md
└── references/                 # 信源索引（6 篇）
    ├── index.md
    ├── dockerfiles.md
    ├── startup-scripts.md
    ├── tagging-source.md
    ├── tests-source.md
    └── makefile-ci-source.md
```

## 文件统计

| 目录 | 文件数 | 预计行数 |
|------|--------|----------|
| concepts/ | 14 | ~1700 |
| examples/ | 6 | ~1200 |
| references/ | 6 | ~600 |
| 根目录 | 2 | ~250 |
| **合计** | **28** | **~3750** |

## R 阶段（事实采集）覆盖的源码

### Dockerfile（12 个镜像）

| 镜像 | 源码路径 |
|------|----------|
| docker-stacks-foundation | `images/docker-stacks-foundation/Dockerfile` |
| base-notebook | `images/base-notebook/Dockerfile` |
| minimal-notebook | `images/minimal-notebook/Dockerfile` |
| r-notebook | `images/r-notebook/Dockerfile` |
| julia-notebook | `images/julia-notebook/Dockerfile` |
| scipy-notebook | `images/scipy-notebook/Dockerfile` |
| tensorflow-notebook | `images/tensorflow-notebook/Dockerfile` |
| pytorch-notebook | `images/pytorch-notebook/Dockerfile` |
| datascience-notebook | `images/datascience-notebook/Dockerfile` |
| pyspark-notebook | `images/pyspark-notebook/Dockerfile` |
| all-spark-notebook | `images/all-spark-notebook/Dockerfile` |

### 启动脚本

| 脚本 | 路径 | 用途 |
|------|------|------|
| start.sh | `images/docker-stacks-foundation/start.sh` | 主入口脚本（用户管理、hooks、降权） |
| run-hooks.sh | `images/docker-stacks-foundation/run-hooks.sh` | Hook 执行器 |
| fix-permissions | `images/docker-stacks-foundation/fix-permissions` | 权限修复脚本 |
| 10activate-conda-env.sh | `images/docker-stacks-foundation/10activate-conda-env.sh` | Conda 环境激活 |
| _docker_stacks_log.sh | `images/docker-stacks-foundation/_docker_stacks_log.sh` | 日志格式化 |
| start-notebook.py | `images/base-notebook/start-notebook.py` | Jupyter 启动入口 |
| start-notebook.sh | `images/base-notebook/start-notebook.sh` | Shell 兼容层 |
| start-singleuser.py | `images/base-notebook/start-singleuser.py` | JupyterHub 单用户入口 |
| start-singleuser.sh | `images/base-notebook/start-singleuser.sh` | Shell 兼容层 |
| jupyter_server_config.py | `images/base-notebook/jupyter_server_config.py` | Jupyter Server 配置 |
| docker_healthcheck.py | `images/base-notebook/docker_healthcheck.py` | 健康检查 |

### Tagging 系统

| 模块 | 路径 |
|------|------|
| images_hierarchy.py | `tagging/hierarchy/images_hierarchy.py` |
| get_taggers.py | `tagging/hierarchy/get_taggers.py` |
| get_manifests.py | `tagging/hierarchy/get_manifests.py` |
| tagger_interface.py | `tagging/taggers/tagger_interface.py` |
| manifest_interface.py | `tagging/manifests/manifest_interface.py` |
| apply_tags.py | `tagging/apps/apply_tags.py` |

### 测试框架

| 模块 | 路径 |
|------|------|
| conftest.py | `tests/conftest.py` |
| tracked_container.py | `tests/utils/tracked_container.py` |
| images_hierarchy.py | `tests/hierarchy/images_hierarchy.py` |
| shared_checks/ | `tests/shared_checks/` |
| by_image/*/test_*.py | `tests/by_image/` |

### 官方文档

| 文档 | 路径 |
|------|------|
| running.md | `docs/using/running.md` |
| common.md | `docs/using/common.md` |
| selecting.md | `docs/using/selecting.md` |
| custom-images.md | `docs/using/custom-images.md` |
| recipes.md | `docs/using/recipes.md` |
| troubleshooting.md | `docs/using/troubleshooting.md` |

### 构建系统

| 文件 | 路径 |
|------|------|
| Makefile | `Makefile` |
| docker-build-test-upload.yml | `.github/workflows/docker-build-test-upload.yml` |
| docker.yml | `.github/workflows/docker.yml` |

## I 阶段（架构洞察）关键决策

1. **文档组织遵循 OKF v0.2 规范**：concepts/examples/references 三层结构
2. **概念文档按镜像层级顺序组织**：从 Foundation 到专业栈，符合 Dockerfile FROM 继承链
3. **启动生命周期单独成章**：这是理解容器行为的核心
4. **用户权限模型单独成章**：jovyan/UID/GID/sudo 是最常见的问题来源
5. **Tagging 系统作为独立概念**：体现了项目对可复现性的工程投入
6. **示例文档从入门到高级递进**：基础→自定义→GPU→CI→配方
7. **信源先行原则**：先完成 references/ 登记，再生成 concepts/ 文档

## 已知限制

1. **CUDA 变体镜像的详细 Dockerfile** 未单独展开（pytorch cuda12/cuda13、tensorflow cuda 子目录）
2. **GitHub Actions 工作流** 仅覆盖主要工作流，未分析所有 workflow 文件
3. **wiki/ 目录**（自动 Wiki 更新工具）未包含在本教程范围内
4. **examples/ 目录**（docker-compose、make-deploy、openshift 等部署示例）未完全覆盖
5. **版本标签 `2026-07-28`** 为文档编写时的参考标签，实际使用时请查询 [Quay.io](https://quay.io/organization/jupyter) 获取最新标签
6. 社区维护的第三方镜像（Community Stacks）仅做索引，未深入分析

## 后续更新建议

- 每季度对照官方仓库更新文档中的版本标签
- 关注 [CHANGELOG.md](https://github.com/jupyter/docker-stacks/blob/main/CHANGELOG.md) 中的重大变更
- 新版本 Python/Ubuntu 升级时更新 concepts/03-foundation-layer.md
- 新增官方镜像时更新 concepts/02-image-hierarchy.md 和 concepts/06-specialized-stacks.md
