---
type: Concept
title: "项目介绍"
description: "cookiecutter-docker-stacks 是什么、解决什么问题、核心特性与适用场景"
tags: [cookiecutter, jupyter, docker, introduction, overview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-readme, resource: "/references/template-files.md", title: "模板文件源码索引" }
  - { id: src-workflow, resource: "/references/workflow-source.md", title: "CI/CD工作流源码索引" }
---

# cookiecutter-docker-stacks 项目介绍

cookiecutter-docker-stacks 是 Jupyter 官方提供的一个 **Cookiecutter 项目模板**，用于帮助社区开发者快速创建、构建和分享自定义的 Jupyter Docker 镜像。[^src-readme]

它不是一个 Docker 镜像，而是一个**代码生成器模板**——运行 cookiecutter 命令后，会生成一个完整的、开箱即用的 Docker 镜像项目骨架，包含 Dockerfile、测试框架、CI/CD 流水线、Dev Container 配置等所有必要文件。

## 解决什么问题

从零创建一个符合 Jupyter Docker Stacks 规范的自定义镜像项目需要：

- 了解 Jupyter Docker Stacks 的基础镜像选择和继承关系
- 编写正确的 Dockerfile（非 root 用户、权限处理、用户切换）
- 设置测试框架验证镜像功能正常
- 配置 CI/CD 自动构建和推送镜像
- 配置开发环境（Dev Container）支持容器内开发

cookiecutter-docker-stacks 将这些最佳实践**固化为模板**，一条命令即可生成符合官方规范的项目结构。

## 生成项目包含什么

使用模板生成的项目目录结构如下：

```
<your-stack-name>/
├── image/
│   └── Dockerfile          # 镜像构建文件（基于选定的基础镜像）
├── tests/
│   ├── conftest.py         # pytest fixtures（Docker客户端、HTTP客户端等）
│   ├── test_notebook.py    # 默认测试：验证Jupyter Server启动
│   └── utils/
│       └── tracked_container.py  # 容器生命周期管理工具类
├── .devcontainer/
│   ├── Dockerfile          # Dev Container基础镜像
│   └── devcontainer.json   # VS Code开发容器配置
├── .github/
│   └── workflows/
│       └── docker.yml      # GitHub Actions CI/CD流水线
├── requirements-dev.txt    # 开发依赖（docker、pytest、requests）
├── README.md               # 项目说明
├── .gitignore              # Git忽略规则
└── .gitattributes          # Git属性配置
```

## 核心特性

- **14种基础镜像可选**：从最小化的 docker-stacks-foundation 到包含 PyTorch/TensorFlow/Spark 的全套数据科学镜像
- **完整测试框架**：pytest + Docker SDK，默认验证 Jupyter Server 登录页面
- **CI/CD 开箱即用**：GitHub Actions 工作流支持定时构建、PR测试、main分支自动推送Docker Hub
- **Dev Container 支持**：一键在容器内开发，预装 Docker-in-Docker 和推荐VS Code扩展
- **代码质量工具**：pre-commit 配置包含 black、isort、flake8、mypy、hadolint、yamllint、markdownlint
- **非root安全默认**：模板注释指导用户在切换root后必须切回非特权用户

## 模板变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| stack_name | 项目名/镜像名 | my-jupyter-stack |
| stack_org | Docker组织/用户名 | my-project |
| stack_base_image | 基础镜像（14选1） | quay.io/jupyter/docker-stacks-foundation |
| stack_description | 项目描述 | 自动生成 |

## 适用场景

| 场景 | 说明 |
|------|------|
| 团队定制 Jupyter 环境 | 在官方镜像基础上添加公司内部包、配置、扩展 |
| 教学/培训专用镜像 | 预安装课程所需的所有依赖和数据集 |
| 发布社区镜像 | 按官方规范创建并分享社区维护的 Jupyter 镜像 |
| 快速原型验证 | 快速搭建可复现的数据科学实验环境 |

## 与 jupyter-docker-stacks 的关系

```
jupyter/docker-stacks          ← 官方维护的镜像集（12个核心镜像）
        ↓ 基础镜像
cookiecutter-docker-stacks     ← 社区镜像模板（本项目）
        ↓ cookiecutter生成
your-custom-jupyter-stack      ← 你的自定义镜像项目
```

## 许可协议

cookiecutter-docker-stacks 使用 **BSD 3-Clause License**（Jupyter Development Team 版权）。

## 相关概念

- [快速上手](01-getting-started.md)
- [模板结构解析](02-template-structure.md)
- [模板变量详解](03-cookiecutter-variables.md)
- [Dockerfile模板与编写指南](04-dockerfile-template.md)

[^src-readme]: 项目 README 源码文档
