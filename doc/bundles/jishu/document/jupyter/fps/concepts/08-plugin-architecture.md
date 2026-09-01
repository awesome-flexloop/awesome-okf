---
type: Concept
title: 插件架构
description: FPS基于Python entry-points的插件发现机制、插件间通过Context解耦的协作模式，以及Jupyverse如何利用FPS实现可组合Jupyter服务器。
tags: [plugin, entry-points, architecture, jupyverse, extensibility]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:54:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:54:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-config-py
    resource: /references/config-source.md
    title: src/fps/_config.py and src/fps/_importer.py
---

## 插件化设计理念

FPS的核心设计目标之一是支持**可插拔应用组装**。应用的各个功能模块可以由独立的Python包提供，通过entry-points注册后即可被FPS发现和加载，无需在应用代码中硬编码import。

这种设计的典型应用是 [Jupyverse](https://github.com/jupyter-server/jupyverse)——一个完全由FPS插件组合而成的Jupyter服务器实现：内核管理、文件服务、认证、Notebook API等都是独立的FPS插件包，可以按需安装和替换。

## Entry-points插件发现

### fps.modules入口点组

FPS使用Python标准的entry-points机制发现插件模块。插件包在 `pyproject.toml` 中注册 `fps.modules` 组：

```toml
[project.entry-points."fps.modules"]
fps_auth = "fps_auth.auth:AuthModule"
fps_contents = "fps_contents.contents:ContentsModule"
fps_kernels = "fps_kernels.kernels:KernelsModule"
```

安装这些包后，FPS可以通过entry-point名称直接加载模块：

```json
{
  "main": {
    "type": "fps_module",
    "modules": {
      "auth": {"type": "fps_auth"},
      "contents": {"type": "fps_contents"},
      "kernels": {"type": "fps_kernels"}
    }
  }
}
```

### import_from_string解析逻辑

`import_from_string()` 函数的三种解析路径：

1. **非字符串**：直接返回（用于代码中传入类对象）
2. **无冒号字符串**（如 `"fps_auth"`）：遍历 `fps.modules` entry-points组，按名称查找并加载
3. **含冒号字符串**（如 `"fps_auth.auth:AuthModule"`）：
   - 按 `:` 分割为模块路径和属性路径
   - `importlib.import_module("fps_auth.auth")` 导入Python模块
   - 按 `.` 分割属性路径逐级getattr获取类对象

### 内置入口点

FPS自身注册了一个内置entry-point：

```toml
[project.entry-points]
"fps.modules" = {fps_module = "fps:Module"}
```

`"fps_module"` 指向fps的`Module`基类，可以在JSON配置中用作容器模块，无需编写任何Python代码即可组装模块树。

## 插件间解耦

FPS插件之间不直接import，而是通过Context的类型驱动发布-订阅机制解耦：

### 服务契约即类型

插件A提供某个服务（如认证令牌验证），只需在start阶段发布实现了特定协议的对象：

```python
# fps_auth 插件
class AuthModule(Module):
    async def start(self):
        auth_service = AuthService()
        self.put(auth_service, AuthService)  # 按类型发布
```

插件B需要使用认证服务，通过类型获取：

```python
# fps_contents 插件
class ContentsModule(Module):
    async def start(self):
        auth = await self.get(AuthService)  # 按类型获取，无需import fps_auth
        # 使用auth...
```

这里的"契约"是Python类型本身（可以是类、Protocol、抽象基类）。只要发布方和消费方对类型达成一致（通常通过共享的类型定义包），它们不需要知道对方的存在。

### 向上冒泡实现跨分支共享

子模块发布的值自动冒泡到所有祖先Context，因此不同分支下的子模块可以通过共同祖先共享值：

```
Main (fps_module)
├── AuthModule (put AuthService → 冒泡到Main)
└── ContentsModule (get AuthService → 从Main获取)
```

这意味着AuthModule和ContentsModule是完全独立的包，它们只依赖于包含AuthService类型定义的共享包，不依赖于彼此。

## 配置驱动组装

完整的应用可以完全通过JSON配置文件组装，不需要编写"粘合代码"：

```json
{
  "jupyverse": {
    "type": "fps_module",
    "modules": {
      "fastapi": {"type": "fps.web.fastapi:FastAPIModule"},
      "server": {"type": "fps.web.server:ServerModule", "config": {"port": 8000}},
      "auth": {"type": "fps_auth", "config": {"mode": "token"}},
      "contents": {"type": "fps_contents"},
      "kernels": {"type": "fps_kernels", "config": {"default_kernel": "python3"}}
    }
  }
}
```

运行：
```bash
fps --config jupyverse.json
```

### CLI覆盖

即使是第三方插件的配置参数，也可以通过CLI的 `--set` 覆盖：

```bash
fps --config jupyverse.json --set server.port=8888 --set auth.mode=password
```

## 插件开发模式

### 创建FPS插件

插件开发的标准模式：

1. **定义服务类型**（Protocol/ABC）：
```python
from typing import Protocol

class AuthProvider(Protocol):
    async def authenticate(self, token: str) -> dict | None: ...
```

2. **实现Module子类**，在生命周期方法中发布/获取服务：
```python
from fps import Module

class MyAuthModule(Module):
    def __init__(self, name, mode: str = "token"):
        super().__init__(name)
        self.mode = mode

    async def start(self):
        provider = TokenAuth() if self.mode == "token" else PasswordAuth()
        self.put(provider, AuthProvider)
```

3. **注册entry-point**（pyproject.toml）：
```toml
[project.entry-points."fps.modules"]
my_auth = "my_auth:MyAuthModule"
```

4. **使用Pydantic管理配置**（推荐）：
```python
from pydantic import BaseModel

class AuthConfig(BaseModel):
    mode: str = "token"
    token_expiry: int = 3600

class MyAuthModule(Module):
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.config = AuthConfig(**kwargs)
```

### 配置参数自动文档

使用Pydantic后，`fps --config app.json --help-all` 能自动生成配置文档：
```
auth.mode:
    Default: token
    Type: str
    Description: Authentication mode (token or password)
auth.token_expiry:
    Default: 3600
    Type: int
    Description: Token expiry in seconds
```

## 与传统插件框架对比

| 特性 | FPS插件 | 传统插件（如Flask扩展） |
|------|---------|----------------------|
| 注册方式 | entry-points自动发现 | 显式 `app.register(ext)` |
| 依赖方向 | 通过类型解耦，互不import | 扩展import app，app知道扩展 |
| 启动协调 | prepare→start自动协调顺序 | 需手动管理初始化顺序 |
| 配置方式 | JSON声明+CLI覆盖+Pydantic校验 | 框架特定config对象 |
| 生命周期 | 三阶段自动管理 | 依赖框架信号/钩子 |
| 资源管理 | SharedValue借用机制 | 手动管理 |

## 相关概念

- [配置系统](05-configuration-system.md)
- [模块系统](02-module-system.md)
- [上下文与共享值](03-context-sharing.md)
- [可插拔Web服务器](07-web-modules.md)
