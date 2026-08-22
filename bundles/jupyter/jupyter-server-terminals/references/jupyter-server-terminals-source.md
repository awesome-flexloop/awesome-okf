---
type: Reference
title: jupyter_server_terminals 源码信源登记
description: jupyter_server_terminals v0.5.4 源码路径、版本信息、核心模块清单与依赖关系
tags: [jupyter, terminals, source, reference, v0.5.4]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-st-github
    resource: https://github.com/jupyter-server/jupyter_server_terminals
    title: jupyter_server_terminals GitHub 仓库
    author: team:jupyter
---

# jupyter_server_terminals 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | jupyter_server_terminals |
| 版本 | **0.5.4** |
| 描述 | A Jupyter Server Extension Providing Terminals（为 Jupyter Server 提供终端功能的扩展） |
| 作者 | Jupyter Development Team (jupyter@googlegroups.com) |
| 许可证 | BSD-3-Clause |
| Python 要求 | ≥ 3.8 |
| Jupyter Server 要求 | ≥ 2.0.0 |
| 官方文档 | <https://jupyter-server-terminals.readthedocs.io> |
| 源码仓库 | <https://github.com/jupyter-server/jupyter_server_terminals> |

## 源码位置

jupyter_server_terminals 源码位于 SpecWeave 仓库的外部库目录：

```
external/libs/jupyter/jupyter_server_terminals/
```

该目录通过外部依赖引入，本地不做修改。

## 核心依赖

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| terminado | ≥ 0.8.3 | 终端 WebSocket/PTY 管理核心库 |
| pywinpty | ≥ 2.0.3 | Windows 平台 PTY 支持（仅 Windows 安装） |
| jupyter_server | ≥ 2.0.0 | Jupyter Server 基础框架（运行时依赖） |
| jupyter_core | * | 核心工具（ensure_async 等） |
| tornado | * | Web 框架（HTTP/WebSocket handler） |
| traitlets | * | 配置系统（Type/Integer/LoggingConfigurable） |

## 核心模块清单

源码包位于 `jupyter_server_terminals/` 目录：

| 模块 | 行数 | 说明 |
|------|------|------|
| `__init__.py` | 24 | 包入口，版本检查（要求 Jupyter Server ≥ 2.0），导出 TerminalsExtensionApp，定义 `_jupyter_server_extension_points()` |
| `_version.py` | 2 | 版本声明：`__version__ = "0.5.4"` |
| `app.py` | 128 | 扩展应用主类 TerminalsExtensionApp：生命周期管理（settings/handlers 初始化）、shell 配置、终端清理 |
| `base.py` | 17 | 基类与 Mixin：TerminalsMixin 提供 terminal_manager 属性访问 |
| `handlers.py` | 76 | WebSocket 处理器：TermSocket 类处理终端实时通信、认证授权、活动追踪 |
| `api_handlers.py` | 91 | REST API 处理器：TerminalRootHandler（列表/创建）、TerminalHandler（查询/删除） |
| `terminalmanager.py` | 172 | 终端管理器：TerminalManager 类继承 NamedTermManager，增加 REST 模型、culler 自动清理、Prometheus 指标 |
| `rest-api.yml` | 119 | OpenAPI 3.0.1 规范文档，定义 REST API 端点与 Terminal 模型 schema |

## 非代码文件

| 文件 | 说明 |
|------|------|
| `jupyter-config/jupyter_server_terminals.json` | 自动启用配置：`{"ServerApp": {"jpserver_extensions": {"jupyter_server_terminals": true}}}` |
| `pyproject.toml` | 项目配置：hatchling 构建、依赖声明、测试/文档/lint/typing 环境配置 |

## 公开 API 导出

`__init__.py` 导出的公开符号：

- **TerminalsExtensionApp**：扩展应用主类（从 `.app` 导入）
- **__version__**：版本字符串（从 `._version` 导入）
- **_jupyter_server_extension_points()**：Jupyter Server 扩展点发现函数（返回模块+app 映射列表）

## Jupyter Server 扩展点机制

`_jupyter_server_extension_points()` 返回的列表中包含一个字典：

```python
{
    "module": "jupyter_server_terminals.app",
    "app": TerminalsExtensionApp,
}
```

Jupyter Server 通过此入口发现并加载终端扩展。自动配置文件 `jupyter-config/jupyter_server_terminals.json` 确保扩展默认启用。

## REST API 端点（OpenAPI 规范）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/terminals` | 获取所有终端列表 |
| POST | `/api/terminals` | 创建新终端（支持 cwd 参数） |
| GET | `/api/terminals/{terminal_id}` | 获取指定终端信息 |
| DELETE | `/api/terminals/{terminal_id}` | 删除指定终端 |
| WebSocket | `/terminals/websocket/{name}` | 终端实时 I/O 通信 |

## Terminal 数据模型

REST API 返回的 Terminal JSON 对象：

```json
{
    "name": "1",
    "last_activity": "2026-08-22T06:00:00.000000Z"
}
```

- `name` (string, 必填)：终端名称/标识符
- `last_activity` (string, ISO 8601 UTC)：最后活动时间戳

[^jupyter-st-github]: jupyter_server_terminals 源码仓库：<https://github.com/jupyter-server/jupyter_server_terminals>
