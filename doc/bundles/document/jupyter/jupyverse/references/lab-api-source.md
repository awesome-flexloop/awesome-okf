---
type: Reference
title: "Lab API 信源"
description: "JupyterLab 前端服务抽象层，定义 Lab ABC、PageConfig 和静态资源管理，提供前端页面、设置、扩展和翻译端点。"
tags: [lab, jupyterlab, frontend, page-config, static-files, settings]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: lab_init
    resource: /external/libs/jupyter/jupyverse/api/lab/src/jupyverse_lab/__init__.py
    title: jupyverse_lab/__init__.py
  - id: lab_py
    resource: /external/libs/jupyter/jupyverse/api/lab/src/jupyverse_lab/lab.py
    title: jupyverse_lab/lab.py
  - id: page_config
    resource: /external/libs/jupyter/jupyverse/api/lab/src/jupyverse_lab/page_config.py
    title: jupyverse_lab/page_config.py
---

# Lab API 信源

## PageConfig

PageConfig 使用钩子（hook）模式管理 JupyterLab 页面配置：

```python
class PageConfig:
    def __init__(self):
        self._config: dict[str, Any] = {}
        self._hooks: list[Callable[[dict[str, Any]], Awaitable[None]]] = []

    def register(self, hook):
        self._hooks.append(hook)

    def set(self, **kwargs):
        self._config = kwargs

    async def get(self) -> dict[str, Any]:
        for hook in self._hooks:
            await hook(self._config)
        return self._config
```

各插件通过 `register()` 注册钩子函数，在页面配置被请求时注入自己的配置项。

## Lab 抽象基类

Lab 继承 Router 和 ABC，负责 JupyterLab 前端服务。

### 初始化行为

1. 设置 `prefix_dir = Path(sys.prefix)`
2. 向 PageConfig 注册 `get_page_config` 钩子
3. 设置 `extensions_dir = prefix_dir/share/jupyter/labextensions`
4. 扫描联邦扩展（federated extensions）
5. 根据 dev_mode 决定 JupyterLab 静态文件目录
6. 为每个联邦扩展挂载 `/lab/extensions/{name}/static` 静态文件
7. 挂载 `/lab/api/themes` 主题静态文件

### REST API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | JupyterLab 根页面（可带 redirect 参数） |
| GET | `/favicon.ico` | 网站图标 |
| GET | `/static/notebook/components/MathJax/{rest_of_path}` | MathJax 资源 |
| GET | `/lab/api/listings/.../listings.json` | 扩展列表 |
| GET | `/lab/api/extensions` | 已安装扩展信息 |
| GET | `/lab/api/translations/` | 翻译列表 |
| GET | `/lab/api/translations/{language}` | 指定语言翻译 |
| GET | `/lab/api/settings/{name0}:{name1}` | 获取设置（扁平路径） |
| GET | `/lab/api/settings/{name0}/{name1}:{name2}` | 获取设置（嵌套路径） |
| PUT | `/lab/api/settings/@jupyterlab/{name0}:{name1}` | 更新设置 |
| GET | `/lab/api/settings` | 获取所有设置 |
| POST | `/api/shutdown` | 关闭服务器 |

### PageConfigModule

```python
class PageConfigModule(Module):
    async def prepare(self):
        self.put(PageConfig())
```

创建 PageConfig 实例并注册到依赖注入容器。
