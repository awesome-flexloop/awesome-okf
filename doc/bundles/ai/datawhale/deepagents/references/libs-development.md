---
title: libs/DEVELOPMENT.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/DEVELOPMENT.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/DEVELOPMENT.md
---

# libs/DEVELOPMENT.md 引用

Monorepo 设置、命令参考和开发流程文档。

## 核心内容

- **前置条件**：`uv`（包管理，禁止 pip/poetry/conda）和 `make`（任务运行器）
- **仓库布局**：`libs/` 下独立版本化包，无根 pyproject.toml，每个包有自己的 pyproject.toml/Makefile/README.md/uv.lock
- **快速开始**：在包目录内 `uv sync --all-groups`，`make test`，`make lint`
- **四条 monorepo 规则**：显式 `uv sync`、不在包外创建虚拟环境、不混合环境、各包设置自己的 Python 版本范围
- **常用命令**：`make test`、`make integration_test`、`make lint`、`make format`、`make type`、`make coverage`
- **跨包命令**：从 `libs/` 运行 `make lint`、`make format`、`make lock`、`make lock-check`、`make lock-bump DEP=<pkg>`
- **测试**：测试文件镜像源码布局，无网络测试在 unit_tests，网络测试在 integration_tests；警告即错误
- **基准测试**：deepagents、code、partners/quickjs 三个包有 bench 目标，结果上传 CodSpeed
- **pre-commit**：格式化、lint、锁文件检查、Conventional Commit 验证，分支名 pre-push 钩子
- **贡献约定**：Conventional Commits 带 scope，外部 PR 需链接已批准 issue

## 相关概念

- [Monorepo 架构](/ai/datawhale/deepagents/concepts/monorepo-architecture)
