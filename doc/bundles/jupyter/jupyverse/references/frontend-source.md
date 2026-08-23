---
type: Reference
title: "Frontend 配置信源"
description: "前端配置模块，定义 FrontendConfig 数据类，提供 base_url 和 collaborative 两个核心配置项。"
tags: [frontend, configuration, base-url, collaboration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: frontend_init
    resource: /external/libs/jupyter/jupyverse/api/frontend/src/jupyverse_frontend/__init__.py
    title: jupyverse_frontend/__init__.py
  - id: frontend_main
    resource: /external/libs/jupyter/jupyverse/plugins/frontend/src/fps_frontend/main.py
    title: fps_frontend/main.py
---

# Frontend 配置信源

## FrontendConfig

```python
class FrontendConfig(Config):
    base_url: str = "/"
    collaborative: bool = False
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| base_url | str | "/" | 应用的基础 URL 路径，用于反向代理部署 |
| collaborative | bool | False | 是否启用协作模式 |

## FrontendModule

```python
class FrontendModule(Module):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.config = FrontendConfig(**kwargs)

    async def prepare(self) -> None:
        self.put(self.config, FrontendConfig)
```

Frontend 插件非常简单，在 prepare 阶段将 FrontendConfig 注册到依赖注入容器，供其他模块（如 Kernels、Lab、Auth）获取。
