---
okf_version: "0.2"
type: concept
title: Dash简介
description: Plotly出品的Python Web应用框架，基于React+Flask/FastAPI/Quart的响应式编程模型，无需编写JavaScript即可构建数据可视化Web应用，MIT许可证，版本4.4.1
tags: [Dash, Plotly, Web框架, React, Flask, 响应式编程, 数据可视化]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - id: dash-version
    resource: external/libs/python/dash/dash/version.py
    title: Dash版本号定义
  - id: dash-init
    resource: external/libs/python/dash/dash/__init__.py
    title: Dash包公开API
  - id: dash-class
    resource: external/libs/python/dash/dash/dash.py
    title: Dash主类定义
---

# Dash简介

Dash 是由 [Plotly](https://plotly.com) 公司开发的开源 Python Web 应用框架，专门用于构建交互式数据可视化 Web 应用，**无需编写 JavaScript**。Dash 的核心理念是"响应式编程"（Reactive Programming），开发者只需声明 UI 布局和 Python 回调函数，框架自动处理前后端通信、状态管理和 UI 更新。

## 基本信息

| 属性 | 值 |
|------|-----|
| **版本** | 4.4.1（定义在 version.py） |
| **许可证** | MIT |
| **开发公司** | Plotly Technologies Inc. |
| **前端技术** | React + dash-renderer（自定义渲染器） |
| **后端支持** | Flask（默认）、FastAPI、Quart |
| **图表引擎** | Plotly.js |

## 核心设计理念

### 响应式（Reactive）编程模型

Dash 采用类似 Excel 电子表格的响应式编程范式：

1. **声明式 UI**：通过 Python 类（`html.Div`、`dcc.Graph` 等）声明组件树
2. **输入-输出绑定**：使用 `@app.callback` 装饰器声明"当输入变化时，输出如何更新"
3. **自动更新**：前端 dash-renderer 监听组件属性变化，自动向后端发起请求，更新输出组件

这意味着开发者不需要手动编写 AJAX 请求、DOM 操作或事件监听代码。

### 纯 Python 全栈

传统 Web 开发需要同时掌握前端（HTML/CSS/JS）和后端（Python/Flask/Django），Dash 将两端抽象为：

- **Python 后端**：定义布局、编写回调逻辑、处理数据
- **React 前端**：由 dash-renderer 自动管理，Python 组件类自动序列化为 React 组件

组件包 `dash-core-components`（dcc）、`dash-html-components`（html）、`dash-table` 提供了丰富的预置组件，通过 Python 类即可使用。

### 多后端架构

Dash 4.x 引入了多后端支持（backends/ 目录），不再强依赖 Flask：

- **Flask**：默认后端，WSGI 同步，成熟稳定
- **FastAPI**：ASGI 异步，高性能，支持自动 API 文档
- **Quart**：ASGI 异步，Flask 的异步版本，API 兼容

后端通过抽象基类 `BaseDashServer`（base_server.py）统一接口，包括 `RequestAdapter` 和 `ResponseAdapter` 来归一化不同框架的请求/响应对象。

## 公开 API 概览

__init__.py 导出的核心 API：

```python
from dash import (
    # 核心类
    Dash,                    # 应用主类
    page_container,          # 多页面容器组件
    no_update,               # 阻止输出更新的信号
    # 依赖声明
    Input, Output, State,    # 回调依赖
    ClientsideFunction,      # 客户端回调
    MATCH, ALL, ALLSMALLER,  # 模式匹配通配符
    # 回调相关
    callback,                # 模块级回调装饰器（v2.0+）
    clientside_callback,     # 客户端回调注册
    callback_context, ctx,   # 回调上下文（获取触发信息等）
    set_props,               # 直接设置组件属性
    # 应用管理
    get_app,                 # 获取当前app实例（避免循环导入）
    # 路径工具
    get_asset_url, get_relative_path, strip_relative_path,
    # 背景回调
    CeleryManager, DiskcacheManager,
    # 多页面
    register_page, page_registry,
    # 其他
    Patch,                   # 增量更新
    NoUpdate,                # 不更新标记类
    jupyter_dash,            # Jupyter集成
    hooks,                   # 钩子系统
    dcc, html, dash_table,   # 组件包
)
```

## 适用场景

- **数据仪表盘**：实时监控、BI 报表、KPI 面板
- **数据分析工具**：交互式探索、参数调优、模型可视化
- **科学计算**：Jupyter 之外的独立 Web 界面
- **内部工具**：快速原型、数据录入、管理后台
- **机器学习演示**：模型 Demo、交互式推理界面

## 版本 4.x 的关键特性

1. **多后端支持**：Flask/FastAPI/Quart 可切换
2. **MCP 集成**：内置 Model Context Protocol 服务器支持（`dash/mcp/`）
3. **WebSocket 回调**：支持长连接实时更新
4. **API 端点**：回调可暴露为独立 HTTP API 端点
5. **压缩传输**：支持 gzip 压缩回调 payload
6. **异步回调**：支持 `async def` 回调函数

## 相关概念

- [应用架构](01-app-architecture.md)
- [回调系统](02-callback-system.md)
- [组件系统](03-component-system.md)
- [第一个Dash应用](../examples/first-dash-app.md)
