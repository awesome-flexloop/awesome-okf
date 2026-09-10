---
type: Reference
title: podman-compose 官方 examples/ 示例信源登记
description: 仓库 examples/ 目录 12 个官方示例应用的清单、文件构成与演示特性索引
tags: [podman, compose, examples, reference, patterns]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples-source
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记（v1.6.0 / commit e3df104）
---

# podman-compose 官方 examples/ 示例信源登记

本文件登记仓库 `examples/` 目录的 12 个官方示例应用，作为示例图鉴文档的事实依据。

## 版本固定

| 项目 | 值 |
|------|-----|
| 仓库快照 | git `v1.6.0-97-ge3df104`，commit `e3df10472e194ab6d547b5ad25542c5c79e1a5fb`（2026-08-11） |
| 示例目录 | `examples/`（12 个应用目录） |

## 示例清单（12 个）

| 目录 | 服务规模 | 核心演示特性 | 关键文件 |
|------|---------|-------------|---------|
| `echo/` | 1 | 最小单服务、`${HOST_PORT:-8080}` 端口插值、curl 验证回显 | docker-compose.yaml、README.md |
| `hello-app/` | 1 | 约 2MB 小镜像单服务、默认 8080 端口 | docker-compose.yaml、README.md |
| `azure-vote/` | 2 | 前端 + Redis 后端、dict 语法 env、`container_name`、`.env` 设置 HOST_PORT | docker-compose.yaml、README.md |
| `busybox/` | 2 | `links` 服务别名（redis:myredis）、dict 语法 labels、短格式 env 变量透传（值为 null）、注释形式的选项目录 | docker-compose.yaml |
| `wordpress/` | 2 | 命名卷持久化（db_data）、列表语法 env、隐式依赖（WORDPRESS_DB_HOST=db）、短端口语法 | docker-compose.yaml |
| `hello-python/` | 2 | build + image 双轨、`read_only` 根文件系统、命名卷、Dockerfile 构建 Python Web、跨服务 REDIS_HOST | docker-compose.yaml、Dockerfile、app/web.py、requirements.txt、README.md |
| `hello-app-redis/` | 7 | 6 节点 Bitnami Redis 集群（5 数据节点 + 1 creator）、列表式 depends_on、每节点独立命名卷、REDIS_NODES 集群成员变量 | docker-compose.yaml、README.md |
| `nodeproj/` | 4 | `extends` 服务继承（init 基服务 → task/web）、`env_file`（local.env）、tmpfs 多挂载、build context 路径插值（`./containers/${NODE_IMG:-node16-runtime}`）、`user: ${UID:-1000}`、bind mount 源码、`run --rm --no-deps init` 一次性初始化工作流 | docker-compose.yml、example.env、example.local.env、containers/node16-runtime/Dockerfile、index.js、README.md |
| `nvidia-smi/` | 1 | `deploy.resources.reservations.devices` GPU 预留（driver nvidia、count、capabilities [gpu]） | docker-compose.yaml |
| `docker-inline/` | 1 | `build.dockerfile_inline` 内联 Dockerfile 构建（无需 Dockerfile 文件） | docker-compose.yml |
| `awx3/` | 5 | AWX 3.0.1 大型应用：postgres/rabbitmq/memcached + awx_web/awx_task、多服务 links、hostname/user、大量 dict env | docker-compose.yml |
| `awx17/` | 模板生成 | Ansible role 模板化生成 compose（`.j2` 模板）、宿主机路径 sed 改写、`run --rm --service-ports task awx-manage migrate` 一次性迁移命令工作流 | README.md、roles/local_docker/（tasks/templates/defaults） |

## 关键事实注记

- **compose 文件命名混用**：示例中 `docker-compose.yaml`、`docker-compose.yml`、`docker-compose.yaml` 三种命名并存，印证源码 `COMPOSE_DEFAULT_LS` 的 14 候选名设计。
- **插值惯例统一**：4 个示例（echo/hello-app/hello-app-redis/azure-vote）使用完全相同的 `"${HOST_PORT:-8080}:8080"` 端口参数化写法；azure-vote 与 nodeproj 的 README 展示了 `.env` 分层（项目 .env 与服务 env_file）。
- **短格式 env 透传**：busybox 中 `ENV_IS_SET`（列表语法，无等号）与 `ENV_IS_SET2:`（dict 语法，值为 null）两种写法都表示"从宿主环境继承该变量"，与源码 `rec_subs`/`container_to_args` 的归一化逻辑对应。
- **extends 继承示例**：nodeproj 是全仓库唯一使用 `extends: {service: init}` 的示例，task 与 web 两个服务继承 init 的 build/volume/env_file 配置后只覆写 command。
- **links 与 depends_on 并存**：awx3/nodeproj 中 links 既提供网络别名又被源码计入 `_deps`（归一化时 links 生成 service_started 依赖）。
- **read_only + tmpfs 组合**：hello-python 与 nodeproj 对需要写临时文件的只读根文件系统服务用 tmpfs 挂载 /tmp、/run、/var/run。
- 示例不自带 healthcheck/profiles/networks 自定义网络等配置，相关特性以 `tests/integration/` 中的测试用例为主要覆盖。

## 相关信源

- [源码信源登记](source-code-map.md)：示例中字段到 podman argv 的翻译实现
- [官方文档信源登记](docs-source.md)：版本能力时间线
- [官方 README](readme-source.md)：项目概述
