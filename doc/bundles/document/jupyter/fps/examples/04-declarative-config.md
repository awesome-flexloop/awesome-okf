---
type: Example
title: 声明式JSON配置
description: 使用JSON配置文件声明式组装FPS应用，零粘合代码组合多个模块，通过entry-points和CLI参数覆盖配置。
tags: [example, config, json, entry-points, declarative]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-guide
    resource: /references/config-source.md
    title: docs/guide.md A declarative application
  - id: fps-config-py
    resource: /references/config-source.md
    title: src/fps/_config.py
---

## 概述

本示例演示如何通过JSON配置文件完全声明式地组装FPS应用，不需要编写任何粘合代码。模块类型通过Python路径或entry-points名称引用。

## 路由模块代码

创建 `router.py`（只包含业务模块，不需要Main入口）：

```python
from fastapi import FastAPI
from fps import Module
from pydantic import BaseModel

class Config(BaseModel):
    key: str = "count"
    value: int = 3

class Router(Module):
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.config = Config(**kwargs)

    async def prepare(self):
        app = await self.get(FastAPI)

        @app.get("/")
        def read_root():
            return {self.config.key: self.config.value}
```

## JSON配置文件

创建 `config.json`：

```json
{
  "main": {
    "type": "fps_module",
    "modules": {
      "fastapi": {
        "type": "fps.web.fastapi:FastAPIModule"
      },
      "server": {
        "type": "fps.web.server:ServerModule",
        "config": {
          "port": 8000
        }
      },
      "router": {
        "type": "router:Router",
        "config": {
          "value": 7
        }
      }
    }
  }
}
```

## 运行

```bash
fps --config config.json
```

访问 `http://127.0.0.1:8000` 返回 `{"count": 7}`（value被配置覆盖为7）。

## 配置解析

### 根模块使用fps_module

```json
"main": {
  "type": "fps_module",
  "modules": { ... }
}
```

`"fps_module"` 是内置entry-point，指向 `fps:Module` 基类。它作为纯容器，不提供任何功能，只负责组合子模块。这意味着不需要编写Main类——FPS Module基类本身就能作为容器。

### 模块类型引用方式

| type值 | 引用方式 | 示例 |
|--------|---------|------|
| Python路径 | `module.path:ClassName` | `"fps.web.fastapi:FastAPIModule"` |
| Entry-point名 | 在`fps.modules`组注册的名称 | `"fps_module"` |
| 本地模块 | `文件名:类名`（当前目录） | `"router:Router"` |

### 嵌套模块配置

```json
"server": {
  "type": "fps.web.server:ServerModule",
  "config": {
    "port": 8000
  }
}
```

`config` 字典中的键值对作为kwargs传给模块的 `__init__`。

### CLI与配置文件叠加

可以同时使用 `--config` 和 `--set`，CLI参数覆盖配置文件：

```bash
fps --config config.json --set server.port=9000 --set router.value=10
```

这会将端口改为9000，router的value改为10。

### 选择子模块作为根

如果配置中有多个顶层模块，可以指定运行其中一个：

```json
{
  "app1": { "type": "...", "modules": {} },
  "app2": { "type": "...", "modules": {} }
}
```

```bash
fps --config config.json app2  # 只运行app2
```

## 查看配置

使用 `--show-config` 查看实际生效的配置（含默认值）：

```bash
fps --config config.json --show-config
```

使用 `--help-all` 查看所有配置参数的说明：

```bash
fps --config config.json --help-all
```

## 多环境配置

可以为不同环境创建不同的配置文件：

`config.dev.json`：
```json
{
  "main": {
    "type": "fps_module",
    "modules": {
      "fastapi": { "type": "fps.web.fastapi:FastAPIModule", "config": {"debug": true} },
      "server": { "type": "fps.web.server:ServerModule", "config": {"port": 8000} },
      "router": { "type": "router:Router" }
    }
  }
}
```

`config.prod.json`：
```json
{
  "main": {
    "type": "fps_module",
    "modules": {
      "fastapi": { "type": "fps.web.fastapi:FastAPIModule", "config": {"debug": false} },
      "server": { "type": "fps.web.server:ServerModule", "config": {"port": 80, "host": "0.0.0.0"} },
      "router": { "type": "router:Router" }
    }
  }
}
```

## 关键要点

- JSON配置文件可以完全描述一个应用的模块组装，不需要编写Main/入口类
- `"fps_module"` entry-point可用作无代码容器模块
- 模块type支持三种引用格式：Python路径、entry-point名称、本地文件名
- CLI的 `--set` 参数可以覆盖配置文件中的任意嵌套参数
- `--config` 和 `--set` 可以叠加使用
- `--show-config` 和 `--help-all` 帮助调试配置

## 相关概念

- [配置系统](../concepts/05-configuration-system.md)
- [插件架构](../concepts/08-plugin-architecture.md)
- [可插拔Web服务器](03-web-server.md)
