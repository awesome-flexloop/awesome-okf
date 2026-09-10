---
okf_version: "0.2"
type: Bundle
title: podman-compose
description: podman-compose 是 Compose Spec 的 Podman 后端实现，采用 daemon-less 架构和 rootless 优先设计，提供轻量安全的多容器编排能力
tags: [podman, containers, compose, orchestration, rootless, daemonless]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
  - id: docs
    resource: /references/docs-source.md
    title: podman-compose 官方 docs/ 文档与 bash 补全脚本信源
---

# podman-compose

podman-compose 是 [Compose 规范](https://compose-spec.io/) 的 [Podman](https://podman.io/) 后端实现，提供与 Docker Compose 兼容的多容器应用编排能力。

## 核心特性

- **daemon-less 架构**：直接调用 podman CLI，无需后台守护进程
- **rootless 优先**：无需 root 权限即可运行容器编排，安全第一
- **Compose Spec 兼容**：支持标准 `compose.yaml` 配置文件
- **单文件部署**：主体是单个 Python 脚本，可直接放入 PATH 执行
- **轻量高效**：构建上下文本地处理，无守护进程资源开销

## Bundle 结构

```
podman-compose/
├── index.md              # 本文件（Bundle 根索引）
├── log.md                # 变更日志
├── concepts/             # 概念文档
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-daemonless-arch.md
│   ├── 02-rootless.md
│   ├── 03-compose-patterns.md
│   ├── 04-source-architecture.md
│   ├── 05-cli-translation-layer.md
│   ├── 06-config-pipeline.md
│   ├── 07-dependency-lifecycle.md
│   ├── 08-x-podman-extensions.md
│   └── 09-version-evolution.md
├── examples/             # 实战示例
│   ├── index.md
│   ├── 01-wordpress.md
│   └── 02-multi-container.md
└── references/           # 信源登记
    ├── index.md
    ├── readme-source.md
    ├── source-code-map.md
    └── docs-source.md
```

## 快速导航

### 入门

| 文档 | 描述 |
|------|------|
| [快速上手与 Compose Spec 兼容](concepts/00-introduction.md) | 安装、环境要求、版本说明、命令参考 |

### 核心概念

| 文档 | 描述 |
|------|------|
| [daemon-less 架构](concepts/01-daemonless-arch.md) | 无守护进程架构设计与实现原理 |
| [rootless 模式下的网络与卷](concepts/02-rootless.md) | 无根模式的网络配置、卷管理、权限模型 |
| [Compose 文件常见模式](concepts/03-compose-patterns.md) | YAML 配置模式、最佳实践、完整示例 |

### 源码精读（基于 podman_compose.py v1.6.0）

| 文档 | 描述 |
|------|------|
| [单文件架构与 asyncio 执行模型](concepts/04-source-architecture.md) | 逻辑分层、装饰器命令注册、三种子进程调用、信号量并发模型 |
| [CLI 翻译层与标签状态](concepts/05-cli-translation-layer.md) | service dict → podman argv 翻译主函数、卷/网络/密钥映射、标签即数据库 |
| [配置加载管线](concepts/06-config-pipeline.md) | 文件发现、bash 风格插值引擎、归一化、!override/!reset 深合并、extends/include |
| [依赖图与 up/down 生命周期](concepts/07-dependency-lifecycle.md) | 12 种依赖条件、重建判定三条件、拉取策略、pod 创建与 down 清理顺序 |
| [x-podman 扩展字段全解](concepts/08-x-podman-extensions.md) | 容器/密钥/网络/Pod 扩展字段、podman 特有网络与挂载类型、Docker Compose 兼容开关 |
| [版本演进与能力矩阵](concepts/09-version-evolution.md) | 7 份 Changelog 梳理 0.1.x→1.6.0 能力时间线、podman/Python 版本门槛、未发布变更与 bash 补全脚本 |

### 实战示例

| 文档 | 描述 | 难度 |
|------|------|------|
| [WordPress 部署示例](examples/01-wordpress.md) | WordPress + MariaDB 双服务完整教程 | ⭐ 入门 |
| [多容器应用编排](examples/02-multi-container.md) | Web + Redis 集群高级编排，网络隔离与依赖管理 | ⭐⭐ 进阶 |

### 信源

| 文档 | 描述 |
|------|------|
| [官方 README](references/readme-source.md) | podman-compose 项目官方文档信源 |
| [源码信源登记](references/source-code-map.md) | podman_compose.py 版本固定、结构地图与核心符号索引 |
| [官方文档与补全脚本信源](references/docs-source.md) | 7 份版本 Changelog、Extensions 扩展说明、Mappings 历史与 bash 补全脚本 |

## 快速开始

1. 安装：
```bash
pip3 install podman-compose
```

2. 创建 `compose.yaml`：
```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
```

3. 启动：
```bash
podman-compose up -d
```

4. 访问：`http://localhost:8080`

## 环境要求

- podman >= 3.4（1.x 分支推荐）
- Python >= 3.9
- PyYAML
- python-dotenv
- podman dnsname 插件（CNI 网络需要，netavark 无需）

## 项目信息

- **协议**：GPL-2.0-only
- **作者**：Muayyad Alsadi
- **入口点**：`podman-compose = "podman_compose:main"`
- **构建后端**：setuptools
- **代码检查**：ruff (lint/format), mypy (类型检查)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
