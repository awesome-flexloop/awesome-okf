---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- docker
- cookiecutter
- template
sources:
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/README.md
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/cookiecutter.json
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/configs/minimal.yaml
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/mypy.ini
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/pytest.ini
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/requirements-test.txt
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/.hadolint.yaml
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/.markdownlint.yaml
- ../../../../../external/libs/jupyter/cookiecutter-docker-stacks/.pre-commit-config.yaml
type: Facts
title: cookiecutter-docker-stacks 源码事实清单
---

# cookiecutter-docker-stacks Facts

## 项目元数据

- F-001: README.md:1 — 项目名称为 "Jupyter Docker Stacks cookiecutter"
- F-002: README.md:7-8 — 项目目的是帮助社区创建和分享新的 Jupyter Docker 镜像，用于定义、构建和分享 Jupyter 环境
- F-003: README.md:10-11 — 文档指向 Jupyter Docker Stacks 官方文档的 Community Stacks 页面

## Cookiecutter 配置

- F-004: cookiecutter.json:2 — stack_name 默认值为 "my-jupyter-stack"
- F-005: cookiecutter.json:3 — stack_org 默认值为 "my-project"
- F-006: cookiecutter.json:4-19 — stack_base_image 提供 14 个基础镜像选项：docker-stacks-foundation、base-notebook、minimal-notebook、scipy-notebook、r-notebook、julia-notebook、tensorflow-notebook、tensorflow-notebook:cuda-latest、pytorch-notebook、pytorch-notebook:cuda11-latest、pytorch-notebook:cuda12-latest、datascience-notebook、pyspark-notebook、all-spark-notebook
- F-007: cookiecutter.json:20 — stack_description 默认值为 "\{{cookiecutter.stack_name}} is a community maintained Jupyter Docker Stack image"，使用 stack_name 变量插值

## 模板目录结构

- F-008: \{{cookiecutter.stack_name}}/ 是 cookiecutter 生成的项目根目录，目录名由 stack_name 变量决定
- F-009: \{{cookiecutter.stack_name}}/image/Dockerfile:1 — Dockerfile FROM 指令使用 \{{cookiecutter.stack_base_image}} 作为基础镜像
- F-010: \{{cookiecutter.stack_name}}/image/Dockerfile:3-9 — Dockerfile 包含注释指导用户：以 ${NB_USER} 身份安装包、使用 USER root 切换、最后必须 USER ${NB_UID} 恢复非特权用户
- F-011: \{{cookiecutter.stack_name}}/README.md:1 — README 标题使用 \{{cookiecutter.stack_name}} 变量
- F-012: \{{cookiecutter.stack_name}}/README.md:3 — README 描述使用 \{{cookiecutter.stack_description}} 变量

## CI/CD 工作流

- F-013: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:1 — GitHub Actions 工作流名称为 "Build, test, and publish Docker Image"
- F-014: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:5-7 — 环境变量 OWNER 和 IMAGE_NAME 分别从 github.repository_owner 和 github.event.repository.name 获取（{% raw %} 保护 cookiecutter 变量）
- F-015: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:12-14 — 每周一 07:00 UTC 定时触发（schedule cron）
- F-016: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:15-20 — PR 触发条件：docker.yml、image/**、tests/**、requirements-dev.txt 文件变更
- F-017: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:21-28 — Push 到 main 分支触发，路径过滤同 PR
- F-018: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:29 — 支持 workflow_dispatch 手动触发
- F-019: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:32-37 — 并发控制：按 workflow+ref 分组，取消同组中正在进行的任务
- F-020: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:40-41 — 单 job "build-test-publish-image"，运行在 ubuntu-24.04
- F-021: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:47 — Checkout 使用 actions/checkout@v7 (9c091bb)
- F-022: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:49-52 — 设置 Python 3.12
- F-023: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:54-57 — 安装 requirements-dev.txt 中的开发依赖
- F-024: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:59-63 — 提取 GITHUB_SHA 前12位作为镜像 tag
- F-025: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:65-77 — 使用 DOCKER_BUILDKIT=1 构建镜像，tag 为 owner/name 和 owner/name:sha12
- F-026: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:79-82 — 运行 pytest tests，TEST_IMAGE 环境变量使用 \{{cookiecutter.stack_org}}/\{{cookiecutter.stack_name}}
- F-027: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:84-91 — 仅在 main 分支或 schedule 触发时登录 Docker Hub（使用 docker/login-action@v4）
- F-028: \{{cookiecutter.stack_name}}/.github/workflows/docker.yml:93-96 — 推送所有 tag 到 Docker Hub

## 测试框架

- F-029: \{{cookiecutter.stack_name}}/tests/conftest.py:19-26 — http_client fixture：创建 requests.Session，配置 5 次重试和 backoff_factor=1
- F-030: \{{cookiecutter.stack_name}}/tests/conftest.py:29-34 — docker_client fixture：从环境创建 docker.DockerClient
- F-031: \{{cookiecutter.stack_name}}/tests/conftest.py:37-40 — image_name fixture：从 TEST_IMAGE 环境变量获取镜像名称
- F-032: \{{cookiecutter.stack_name}}/tests/conftest.py:43-57 — container fixture（function 级别）：创建 TrackedContainer，yield 后自动 remove
- F-033: \{{cookiecutter.stack_name}}/tests/conftest.py:60-66 — free_host_port fixture：绑定端口0获取空闲端口号
- F-034: \{{cookiecutter.stack_name}}/tests/test_notebook.py:7-14 — test_secured_server 测试：启动容器映射8888端口，HTTP GET 验证响应包含 "login_submit"（Jupyter Server 默认要求登录）
- F-035: \{{cookiecutter.stack_name}}/tests/utils/tracked_container.py — TrackedContainer 工具类封装 Docker 容器操作

## 开发容器

- F-036: \{{cookiecutter.stack_name}}/.devcontainer/Dockerfile:1 — Dev Container 基于 mcr.microsoft.com/devcontainers/python:3.13
- F-037: \{{cookiecutter.stack_name}}/.devcontainer/Dockerfile:3-5 — 安装 requirements-dev.txt 中的依赖
- F-038: \{{cookiecutter.stack_name}}/.devcontainer/devcontainer.json — Dev Container 配置文件

## 预设配置

- F-039: configs/ 目录包含 14 个 YAML 预设配置文件，对应 cookiecutter.json 中的每个基础镜像选项
- F-040: configs/minimal.yaml:1-2 — 预设配置使用 default_context 指定 stack_base_image，例如 minimal.yaml 设置为 "quay.io/jupyter/minimal-notebook"
- F-041: configs/ 包含 all-spark、base、datascience、foundation、julia、minimal、pyspark、pytorch、pytorch-cuda11、pytorch-cuda12、r、scipy、tensorflow、tensorflow-cuda 预设

## 代码质量配置

- F-042: .flake8 — flake8 代码风格配置
- F-043: .hadolint.yaml — hadolint Dockerfile lint 配置
- F-044: .markdownlint.yaml — markdown lint 配置
- F-045: .pre-commit-config.yaml — pre-commit hooks 配置
- F-046: mypy.ini — mypy 类型检查配置
- F-047: pytest.ini — pytest 配置
- F-048: requirements-test.txt — 测试依赖列表

## 其他模板文件

- F-049: \{{cookiecutter.stack_name}}/.gitattributes — Git 属性配置
- F-050: \{{cookiecutter.stack_name}}/.gitignore — Git ignore 规则
- F-051: \{{cookiecutter.stack_name}}/requirements-dev.txt — 开发依赖文件
- F-052: \{{cookiecutter.stack_name}}/.github/dependabot.yml — Dependabot 依赖更新配置
