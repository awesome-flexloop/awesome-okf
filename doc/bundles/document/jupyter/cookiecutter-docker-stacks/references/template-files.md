---
type: Reference
title: "模板文件源码索引"
description: "cookiecutter-docker-stacks 模板生成的项目文件源码信源登记"
tags: [cookiecutter, template, dockerfile, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-cookiecutter-json, resource: "external/libs/jupyter/cookiecutter-docker-stacks/cookiecutter.json", title: "cookiecutter.json" }
  - { id: src-dockerfile, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/image/Dockerfile", title: "image/Dockerfile" }
  - { id: src-readme, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/README.md", title: "README.md" }
  - { id: src-docker-yml, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/.github/workflows/docker.yml", title: ".github/workflows/docker.yml" }
  - { id: src-req-dev, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/requirements-dev.txt", title: "requirements-dev.txt" }
  - { id: src-gitignore, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/.gitignore", title: ".gitignore" }
  - { id: src-gitattributes, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/.gitattributes", title: ".gitattributes" }
  - { id: src-devcontainer-df, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/.devcontainer/Dockerfile", title: ".devcontainer/Dockerfile" }
  - { id: src-devcontainer-json, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/.devcontainer/devcontainer.json", title: ".devcontainer/devcontainer.json" }
---

# 模板文件源码索引

本文档登记 cookiecutter-docker-stacks 模板生成的项目文件源码路径与关键内容概要。

## 模板根目录文件

| 文件 | 源码路径 | 核心内容 |
|------|---------|---------|
| cookiecutter.json | cookiecutter.json | 定义4个模板变量：stack_name、stack_org、stack_base_image（14个选项）、stack_description |
| README.md | \{{cookiecutter.stack_name}}/README.md | 项目README模板，仅包含项目名和描述 |
| requirements-dev.txt | \{{cookiecutter.stack_name}}/requirements-dev.txt | 开发依赖：docker、pytest、requests |
| .gitignore | \{{cookiecutter.stack_name}}/.gitignore | 标准Python .gitignore + Mac/VSCode/PyCharm忽略规则 |
| .gitattributes | \{{cookiecutter.stack_name}}/.gitattributes | 统一LF行尾：`* text=auto eol=lf` |

## 镜像构建目录

| 文件 | 源码路径 | 核心内容 |
|------|---------|---------|
| image/Dockerfile | \{{cookiecutter.stack_name}}/image/Dockerfile | FROM基础镜像 + 注释指导用户添加RUN语句 |

## CI/CD 目录

| 文件 | 源码路径 | 核心内容 |
|------|---------|---------|
| .github/workflows/docker.yml | \{{cookiecutter.stack_name}}/.github/workflows/docker.yml | 完整CI/CD流水线：构建→测试→推送Docker Hub |

## 测试目录

| 文件 | 源码路径 | 核心内容 |
|------|---------|---------|
| tests/conftest.py | \{{cookiecutter.stack_name}}/tests/conftest.py | pytest fixtures：http_client、docker_client、image_name、container、free_host_port |
| tests/test_notebook.py | \{{cookiecutter.stack_name}}/tests/test_notebook.py | 默认测试：验证Jupyter Server登录页面 |
| tests/utils/tracked_container.py | \{{cookiecutter.stack_name}}/tests/utils/tracked_container.py | TrackedContainer类：Docker容器生命周期管理 |

## Dev Container 目录

| 文件 | 源码路径 | 核心内容 |
|------|---------|---------|
| .devcontainer/Dockerfile | \{{cookiecutter.stack_name}}/.devcontainer/Dockerfile | 基于devcontainers/python:3.13，安装测试依赖 |
| .devcontainer/devcontainer.json | \{{cookiecutter.stack_name}}/.devcontainer/devcontainer.json | VS Code开发容器配置：docker-in-docker + 推荐扩展 |

## 模板变量

| 变量 | 默认值 | 类型 | 说明 |
|------|--------|------|------|
| stack_name | "my-jupyter-stack" | 字符串 | 生成项目的目录名和镜像名 |
| stack_org | "my-project" | 字符串 | Docker组织/用户名 |
| stack_base_image | 列表选项 | 选择列表 | 基础镜像，14个官方镜像可选 |
| stack_description | 自动生成 | 字符串 | 项目描述，默认基于stack_name生成 |
