---
okf_version: "0.2"
type: bundle
title: "jupyter_server_fileid"
description: "Jupyter Server 文件 ID 服务扩展：为文件分配稳定的 UUID 标识，解决文件重命名/移动后引用失效的问题。本知识包从源码出发，系统讲解 jupyter_server_fileid v0.9.3 的架构、API 和实战用法。"
---

# jupyter_server_fileid

> Jupyter Server 文件 ID 服务扩展：为文件分配稳定的 UUID，跨路径变更追踪文件身份。

`jupyter_server_fileid` 是 Jupyter Server 的官方扩展，为工作目录中的文件分配稳定的 UUID 标识符。即使文件被重命名、移动或复制，其 ID 保持不变，从而让前端扩展和第三方工具能够可靠地引用文件而不依赖易变的路径。

## 快速导航

### 📘 核心概念（9 篇）

**入门**
- [简介](concepts/00-introduction.md) — jupyter_server_fileid 解决的问题、核心能力、项目信息与架构概览
- [5分钟快速上手](concepts/01-getting-started.md) — 安装扩展、配置管理器、使用 REST API 查询文件 ID

**核心**
- [架构总览](concepts/02-architecture-overview.md) — 四层架构（Extension→Handler→Manager→SQLite）、事件驱动数据流与设计哲学
- [抽象基类与核心 API](concepts/03-file-id-manager.md) — BaseFileIdManager 接口契约、traitlets 配置、路径归一化与 CRUD 抽象方法
- [双管理器对比：Arbitrary vs Local](concepts/04-arbitrary-vs-local.md) — ArbitraryFileIdManager（纯路径映射）与 LocalFileIdManager（inode 跟踪）的设计差异与适用场景
- [事件驱动同步与带外检测](concepts/05-event-sync-mechanism.md) — jupyter_events 事件监听、contents service 事件格式、inode 跟踪与带外移动检测算法
- [REST API 端点](concepts/06-http-api.md) — 两个 HTTP 端点的请求参数、响应格式、错误处理与前端使用方式

**进阶**
- [扩展配置与自定义管理器](concepts/07-extension-configuration.md) — 配置 FileIdExtension 选项、创建自定义 File ID 管理器
- [CLI 工具与数据库管理](concepts/08-cli-and-database.md) — CLI drop 命令、SQLite Schema、pytest 测试插件

### 💻 示例代码（3 个）

- [编程接口基础使用](examples/01-basic-usage.md) — 直接使用 Python API 进行索引、查询、移动、复制、删除和带外检测
- [REST API 使用示例](examples/02-rest-api-usage.md) — curl、Python requests、前端 fetch 调用 HTTP API
- [自定义 File ID 管理器](examples/03-custom-manager.md) — 继承 BaseFileIdManager 实现 S3 对象存储的自定义管理器
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（5 个文件）

- [manager.py](references/manager-source.md) — File ID 管理器核心实现（BaseFileIdManager、ArbitraryFileIdManager、LocalFileIdManager）
- [handler.py](references/handler-source.md) — REST API 端点处理器
- [extension.py](references/extension-source.md) — FileIdExtension 扩展入口
- [cli.py](references/cli-source.md) — CLI 命令工具
- [pytest_plugin.py](references/pytest-plugin-source.md) — pytest 测试 fixtures
- [源码信源索引](references/index.md) — 信源文档总目录

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **v0.9.3** |
| Python 版本要求 | ≥ 3.9 |
| 构建系统 | Hatchling ≥ 1.0 |
| 必需依赖 | jupyter_server ≥ 2.10,<3, jupyter_events ≥ 0.9.0 |
| 可选依赖 | click（CLI 工具） |
| 测试依赖 | pytest, pytest-cov, pytest-jupyter, jupyter_server[test] |
| 许可证 | BSD-3-Clause |
| CLI 命令 | `jupyter-fileid drop` |
| REST API 端点 | `GET /api/fileid/id`, `GET /api/fileid/path` |
| 内置管理器 | ArbitraryFileIdManager（默认）、LocalFileIdManager |
| 源码路径 | `external/libs/jupyter/jupyter_server_fileid/` |

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [抽象基类与核心 API](concepts/03-file-id-manager.md) → [双管理器对比](concepts/04-arbitrary-vs-local.md) → [事件驱动同步](concepts/05-event-sync-mechanism.md) → [REST API 端点](concepts/06-http-api.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
