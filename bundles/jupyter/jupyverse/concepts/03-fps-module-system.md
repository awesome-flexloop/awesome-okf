---
type: Concept
title: "FPS 模块系统与依赖注入"
description: "FPS（FastAPI Plugin System）是 Jupyverse 的底层框架，提供 Module 生命周期管理、声明式依赖注入和基于 entry points 的插件发现机制。"
tags: [fps, module, lifecycle, dependency-injection, entry-points, plugin-discovery]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-module-source.md
    title: JupyverseModule 主模块信源
  - id: cli
    resource: /references/cli-source.md
    title: CLI 入口信源
  - id: fps_kernels
    resource: /references/fps-kernels-source.md
    title: fps-kernels 实现信源
---

# FPS 模块系统与依赖注入

FPS（FastAPI Plugin System）是 Jupyverse 的底层插件框架，提供模块生命周期管理和依赖注入容器。理解 FPS 是理解 Jupyverse 架构的关键。

## Module 生命周期

每个 FPS 插件都是一个 `fps.Module` 的子类，遵循三阶段生命周期：

```
prepare() → start() → [运行中] → stop()
```

### prepare() 阶段

`prepare()` 是模块初始化阶段，负责：
- 获取依赖的其他服务（通过 `self.get(Type)`）
- 创建自身的服务实例
- 将服务注册到容器（通过 `self.put(instance, Type)`）
- 注册配置对象
- 启动后台任务（通过 `create_task_group`）

```python
class ContentsModule(Module):
    async def prepare(self) -> None:
        app = await self.get(App)           # 获取 App 依赖
        auth = await self.get(Auth)         # 获取 Auth 依赖
        contents = _Contents(app, auth)     # 创建服务实例
        self.put(contents, Contents)        # 注册为 Contents 类型
```

### start() 阶段

`start()` 在所有模块的 `prepare()` 完成后调用，负责启动需要所有依赖就绪才能启动的服务：

```python
class JupyverseModule(FastAPIModule):
    async def start(self) -> None:
        async with create_task_group() as tg:
            tg.start_soon(super().start)    # 启动 FastAPI 服务器
            if self.jupyverse_config.start_server:
                await self.modules["server"].started.wait()
            # 服务器启动后的逻辑...
```

### stop() 阶段

`stop()` 在应用关闭时调用，负责清理资源：

```python
async def stop(self) -> None:
    self.lifespan.shutdown_request.set()    # 通知所有等待关闭的任务
```

### done() 与 teardown_callback

- `self.done()`：标记 prepare 阶段完成（在 `create_task_group` 内使用）
- `self.put(instance, Type, teardown_callback=callback)`：注册清理回调，容器关闭时调用

## 依赖注入机制

FPS 使用**类型-based** 的依赖注入容器：

### self.put() — 注册服务

```python
self.put(instance, Type)
```

将 `instance` 注册为 `Type` 类型的服务。后续所有调用 `self.get(Type)` 的模块将获得这个实例。

### self.get() — 获取依赖

```python
dependency = await self.get(Type)
```

异步获取已注册的 `Type` 类型服务。如果服务尚未注册（依赖的模块还没 prepare），会等待直到可用。

### self.add_module() — 添加子模块

```python
self.add_module("fps.web.server:ServerModule", "server", host=..., port=...)
```

动态添加子模块，指定模块的 Python 路径、名称和配置参数。

## 插件发现机制

Jupyverse 通过 Python entry points 自动发现插件。

### Entry Point 注册

每个插件在 `pyproject.toml` 中声明 `jupyverse.modules` entry point：

```toml
[project.entry-points."jupyverse.modules"]
contents = "fps_contents.main:ContentsModule"
kernels = "fps_kernels.main:KernelsModule"
auth = "fps_auth.main:AuthModule"
```

### CLI 插件收集

CLI 启动时，`get_pluggin_config()` 函数收集所有 entry points：

```python
def get_pluggin_config(disable: tuple[str, ...]) -> dict:
    jupyverse_modules = [
        ep.name for ep in entry_points(group="jupyverse.modules")
        if ep.name not in disable
    ]
    config = {
        "jupyverse": {
            "type": "jupyverse_api.main:JupyverseModule",
            "modules": {module: {"type": module} for module in jupyverse_modules},
        }
    }
    return config
```

生成的配置告诉 FPS：
1. 根模块类型是 `jupyverse_api.main:JupyverseModule`
2. 要加载的子模块列表（排除 `--disable` 指定的插件）

### --disable 参数

由于认证插件互斥（同一时间只能用一种认证方式），通过 `--disable` 排除不需要的插件：

```bash
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth
```

## 模块配置传递

模块通过 `**kwargs` 接收配置参数。配置来源有三种：

### 1. CLI --set 参数

```bash
jupyverse --set "frontend.collaborative=true" --set "kernels.default_kernel=python3"
```

### 2. 代码中 add_module 传参

```python
self.add_module("fps.web.server:ServerModule", "server",
                host="0.0.0.0", port=8888)
```

### 3. entry point 配置中的 type 字段

CLI 生成的 `modules` 配置中，每个模块可以通过 `{"type": module_name, "key": value}` 传递配置。

## 异步任务组

FPS 模块广泛使用 anyio 的 `create_task_group` 管理后台任务：

```python
async def prepare(self) -> None:
    # ... 创建服务实例 ...
    async with create_task_group() as tg:
        tg.start_soon(self.kernels.start)  # 启动后台任务
        self.done()                          # 标记 prepare 完成
```

这种模式确保后台任务在模块生命周期内运行，模块关闭时任务组自动取消所有子任务。

## 典型模块实现模式

以下是所有功能插件遵循的标准模式：

```python
from fps import Module

class MyFeatureModule(Module):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.config = MyFeatureConfig(**kwargs)  # 接收配置

    async def prepare(self) -> None:
        self.put(self.config, MyFeatureConfig)   # 注册配置

        # 获取依赖
        app = await self.get(App)
        auth = await self.get(Auth)

        # 创建实现实例
        service = _MyFeature(app, auth, self.config)

        # 注册服务，附带清理回调
        self.put(service, MyFeature, teardown_callback=service.stop)
```

## 相关概念

- [架构总览](02-architecture-overview.md) — 整体架构和双层分离
- [App 与 Router 基础设施](04-app-and-router.md) — FastAPI 包装和路由注册
- [插件开发指南](12-plugin-development.md) — 开发自定义 FPS 插件
