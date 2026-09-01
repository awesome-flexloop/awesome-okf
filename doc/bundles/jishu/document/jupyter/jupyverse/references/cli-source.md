---
type: Reference
title: "CLI 入口信源"
description: "jupyverse 命令行入口实现，基于 rich-click 委托 FPS CLI，支持插件自动发现与禁用。"
tags: [cli, command-line, entry-point, click]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: cli
    resource: /external/libs/jupyter/jupyverse/api/api/src/jupyverse_api/cli.py
    title: jupyverse_api/cli.py
---

# CLI 入口信源

## CLI 选项

`jupyverse` 命令通过 `rich_click` 定义，支持以下选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--debug` | flag | False | 启用调试模式 |
| `--show-config` | flag | False | 显示实际配置 |
| `--help-all` | flag | False | 显示配置描述 |
| `--backend` | str | "asyncio" | 事件循环（asyncio 或 trio） |
| `--open-browser` | flag | False | 自动打开浏览器 |
| `--host` | str | "127.0.0.1" | 监听地址 |
| `--port` | int | 8000 | 监听端口 |
| `--websocket-permessage-deflate` | flag | False | WebSocket permessage-deflate 压缩 |
| `--query-param` | multiple | - | 查询参数（key=value） |
| `--allow-origin` | multiple | - | 允许的 CORS 源 |
| `--set` | multiple | - | 设置配置项 |
| `--disable` | multiple | - | 禁用指定插件 |
| `--timeout` | float | None | 启动超时 |
| `--stop-timeout` | float | 1 | 停止超时 |

## 插件发现机制

`get_pluggin_config()` 函数通过 Python entry points 发现插件：

```python
jupyverse_modules = [
    ep.name for ep in entry_points(group="jupyverse.modules") if ep.name not in disable
]
```

生成的配置结构：

```python
{
    "jupyverse": {
        "type": "jupyverse_api.main:JupyverseModule",
        "modules": {module: {"type": module} for module in jupyverse_modules},
    }
}
```

该配置通过 `fps_main.callback()` 委托给 FPS 框架处理。
