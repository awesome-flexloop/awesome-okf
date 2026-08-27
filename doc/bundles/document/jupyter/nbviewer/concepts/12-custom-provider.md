---
type: Concept
title: 自定义Provider扩展
description: 开发自定义Provider的完整步骤、Provider契约、Handler继承模式和URI重写规则注册
tags:
  - jupyter
  - nbviewer
  - provider
  - extension
  - plugin
  - development
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/__init__.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/base.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/url/handlers.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/dropbox/handlers.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/huggingface/handlers.py
---

# 自定义Provider扩展

本文档详细说明如何开发和注册自定义 Provider。Provider 是 nbviewer 的核心扩展点，通过实现特定的模块接口，可以添加新的 Notebook 数据源支持。

## Provider 契约

每个 Provider 是一个 Python 模块（包），必须实现以下两个函数中的至少一个：

### 必须实现的函数

#### 1. default_handlers(handlers, **handler_names)

返回 Tornado URLSpec 列表，定义该 Provider 处理的路由。

```python
def default_handlers(handlers=[], **handler_names):
    """返回该Provider的URL路由列表
    
    Parameters
    ----------
    handlers : list
        已有的URLSpec列表，新路由应该追加到末尾
    **handler_names : dict
        包含可替换的Handler类位置，key格式为{provider_type}_handler
    
    Returns
    -------
    list
        追加后的URLSpec列表，每个元素是 (pattern, handler_class, init_kwargs) 元组
    """
```

#### 2. uri_rewrites(rewrites=[])

返回 URI 重写规则列表，定义如何将用户输入的 URL 转换为内部路由路径。

```python
def uri_rewrites(rewrites=[]):
    """返回该Provider的URI重写规则
    
    Parameters
    ----------
    rewrites : list
        已有的(regex, template)规则列表
    
    Returns
    -------
    list
        追加后的(regex, template)规则列表
    """
```

> **注意**：
> - 如果 Provider 只提供 URL 重写（将外部URL转换为已有Provider的路由），只需实现 `uri_rewrites()`，不需要 `default_handlers()`（如 Dropbox、HuggingFace Provider）
> - 如果 Provider 需要新的路由和Handler，两个函数都需要实现（如 GitHub、Gist、URL Provider）
> - Local Provider 只实现 `default_handlers()`（本地文件不需要URI重写）

## 两种 Provider 模式

### 模式一：轻量重写 Provider（无自定义Handler）

Dropbox 和 HuggingFace 是这种模式的典型例子：

```python
# nbviewer/providers/dropbox/handlers.py  (实际上不需要handlers.py)
# nbviewer/providers/dropbox/__init__.py
def uri_rewrites(rewrites=[]):
    return rewrites + [
        (r"^http(s?)://www.dropbox.com/(sh?)/(.+?)(\?dl=.)*$",
         "/url{0}/dl.dropbox.com/{1}/{2}")
    ]
```

**特点**：
- 不定义新的 Handler 类
- 只通过 `uri_rewrites()` 将外部 URL 转换为已有的 `/url/...` 路由
- 由 URL Provider 的 URLHandler 处理实际的文件获取
- 代码极简，适合将各种 URL 分享服务桥接到 nbviewer

适用场景：
- 文件可通过简单的URL转换获得直链（www → dl 域名替换等）
- 不需要自定义认证或API调用
- 数据源本质上是普通HTTP文件下载

### 模式二：完整 Handler Provider

GitHub 和 Gist 是这种模式的典型例子：

**特点**：
- 定义继承自 RenderingHandler 的自定义 Handler 类
- 实现 `get_notebook_data()` 和 `deliver_notebook()` 方法
- 通常有配套的 API 客户端（如 AsyncGitHubClient）
- 可以处理认证、分页、API限流等复杂逻辑
- 需要实现 `default_handlers()` 和 `uri_rewrites()`

适用场景：
- 需要调用特定API获取Notebook（而非直接HTTP下载）
- 需要认证（OAuth、API Token）
- 需要特殊的文件获取逻辑（如目录浏览、分支选择）
- 需要特殊的错误处理

## 开发步骤

### 步骤1：创建 Provider 包结构

```
myprovider/
├── __init__.py      # 必需：default_handlers() 和/或 uri_rewrites()
└── handlers.py      # 可选：自定义Handler类
```

### 步骤2：实现 uri_rewrites（轻量Provider）

```python
# myprovider/__init__.py
def uri_rewrites(rewrites=[]):
    return rewrites + [
        # 规则顺序：更具体的规则在前
        (r"^https://myservice\.com/user/([^/]+)/notebook/(.+)$",
         "/urls/myservice.com/api/notebooks/{0}/{1}"),
        (r"^https://myservice\.com/shared/(.+)$",
         "/urls/myservice.com/shared/{0}"),
    ]
```

### 步骤3：实现自定义 Handler（完整Provider）

Handler 必须继承自 `RenderingHandler`，并实现模板方法：

```python
# myprovider/handlers.py
from ...providers.base import RenderingHandler, cached
from tornado import web

class MyServiceHandler(RenderingHandler):
    """处理 myservice.com 的Notebook获取"""
    
    async def get_notebook_data(self, user, notebook_id):
        """从MyService API获取Notebook数据
        
        此方法负责：
        1. 调用API获取Notebook JSON
        2. 设置breadcrumbs（面包屑）
        3. 设置provider_url/excutor_url等元信息
        4. 返回原始JSON字符串，或处理目录/重定向等非Notebook响应
        """
        # 调用API获取Notebook
        api_url = f"https://api.myservice.com/v1/users/{user}/notebooks/{notebook_id}"
        response = await self.client.fetch(api_url)
        
        # 解析响应获取Notebook JSON
        nbdata = response.body.decode('utf-8')
        
        # 设置模板变量（通过namespace传递给finish_notebook）
        self breadcrumbs = [
            {"url": self.base_url, "name": "home"},
            {"url": f"/myservice/{user}", "name": user},
            {"url": self.request.uri, "name": notebook_id},
        ]
        
        # 返回JSON数据（将被deliver_notebook进一步处理）
        return nbdata, {
            "breadcrumbs": breadcrumbs,
            "provider_url": f"https://myservice.com/{user}/notebooks/{notebook_id}",
            "title": f"{notebook_id} - {user}",
        }
    
    async def deliver_notebook(self, nbdata, namespace):
        """调用finish_notebook完成渲染"""
        json_notebook = nbdata
        download_url = namespace.get("provider_url")
        await self.finish_notebook(
            json_notebook,
            download_url=download_url,
            msg=f"notebook from myservice: {namespace['title']}",
            public=True,
            **namespace,
        )
    
    @cached
    async def get(self, user, notebook_id):
        """路由入口，@cached装饰器提供缓存和限流"""
        nbdata, namespace = await self.get_notebook_data(user, notebook_id)
        await self.deliver_notebook(nbdata, namespace)


def default_handlers(handlers=[], **handler_names):
    # 支持Handler类替换
    my_handler = _load_handler_from_location(
        handler_names.get("myservice_handler",
                         "__main__.myprovider.handlers.MyServiceHandler")
    )
    
    return handlers + [
        (r"/myservice/([^/]+)/([^/]+)", my_handler, {}),
    ]


def _load_handler_from_location(handler_location):
    module_name, handler_name = tuple(handler_location.rsplit(".", 1))
    import importlib
    module = importlib.import_module(module_name)
    return getattr(module, handler_name)
```

### 步骤4：注册 default_handlers

```python
# myprovider/__init__.py
from .handlers import default_handlers

def uri_rewrites(rewrites=[]):
    return rewrites + [
        (r"^https://myservice\.com/([^/]+)/notebook/([^/]+)$",
         "/myservice/{0}/{1}"),
    ]
```

### 步骤5：配置 Provider 加载

#### 方式一：命令行参数

```bash
python -m nbviewer \
  --providers="['nbviewer.providers.url', 'nbviewer.providers.github', 'nbviewer.providers.gist', 'myprovider']" \
  --provider-rewrites="['nbviewer.providers.gist', 'nbviewer.providers.github', 'nbviewer.providers.dropbox', 'nbviewer.providers.huggingface', 'myprovider', 'nbviewer.providers.url']"
```

注意：
- `--providers` 列表控制哪些 Provider 的 `default_handlers()` 被注册
- `--provider-rewrites` 列表控制哪些 Provider 的 `uri_rewrites()` 被注册
- 两个列表的**顺序很重要**：先注册的路由/重写规则优先匹配

#### 方式二：配置文件

创建 `nbviewer_config.py`：

```python
c.NBViewer.providers = [
    "nbviewer.providers.url",
    "nbviewer.providers.github", 
    "nbviewer.providers.gist",
    "myprovider",
]

c.NBViewer.provider_rewrites = [
    "nbviewer.providers.gist",
    "nbviewer.providers.github",
    "myprovider",
    "nbviewer.providers.dropbox",
    "nbviewer.providers.huggingface",
    "nbviewer.providers.url",
]
```

然后运行：`python -m nbviewer --config-file=nbviewer_config.py`

### 步骤6（可选）：注册可替换 Handler 类

如果允许用户通过 traitlets 配置替换自定义 Handler，需要在 NBViewer 类中添加对应 trait。但这需要修改 nbviewer 源码。更简单的方式是使用 `handler_settings`：

```python
# 在配置文件中
c.NBViewer.handler_settings = {
    # 自定义设置会被注入到所有Handler的initialize()
}
```

## RenderingHandler 模板方法详解

自定义 Handler 需要理解 RenderingHandler 的模板方法模式：

### 可覆盖的方法/属性

| 方法/属性 | 作用 | 默认行为 |
|-----------|------|----------|
| `get_notebook_data(*args)` | 获取Notebook原始数据 | 抽象，子类必须实现 |
| `deliver_notebook(data, *args)` | 调用finish_notebook渲染 | 抽象，子类必须实现 |
| `get(*args, **kwargs)` | 路由处理方法，必须被@cached装饰 | 调用get_notebook_data→deliver_notebook |
| `breadcrumbs(path)` | 生成面包屑导航 | 返回home+路径各段 |
| `_cache_key_attr` | 缓存键使用的请求属性 | `"path"` |
| `provider_url` | 原始Notebook来源URL | 供模板使用 |
| `executor_url` | Binder执行URL | 供"在Binder中打开"按钮使用 |

### @cached装饰器的要求

所有处理Notebook渲染的get方法必须使用`@cached`装饰器：

```python
from ..base import cached

@cached
async def get(self, *args):
    ...
```

`@cached`装饰器提供：
- 页面缓存（读写缓存）
- 并发去重（pending Future）
- 速率限制检查（缓存未命中时）
- 错误处理（catch_client_error集成）

### finish_notebook 参数

`finish_notebook()` 接受的关键参数：

```python
await self.finish_notebook(
    json_notebook,        # Notebook JSON字符串（必需）
    download_url=None,    # 原始文件下载URL（"在Binder中打开"需要）
    msg="",               # 日志消息
    public=True,          # 是否公开访问（影响frontpage缓存）
    breadcrumbs=None,     # 面包屑列表 [{"url":..., "name":...}, ...]
    title=None,           # 页面标题
    provider_url=None,    # Provider页面URL（供"查看原页面"链接）
    executor_url=None,    # Binder URL
    provider_label=None,  # Provider显示名
    provider_icon=None,   # Provider图标
)
```

## 轻量Provider示例（Dropbox模式）

最简单的Provider只需要一个`__init__.py`：

```python
# my_rewrite_provider/__init__.py
def uri_rewrites(rewrites=[]):
    return rewrites + [
        # 将 example.com/share/xxx 转换为直链
        (r"^https?://example\.com/share/([a-zA-Z0-9]+)$",
         "/urls/example.com/download/{0}"),
    ]
```

不需要`default_handlers()`，因为转换后的路径`/urls/...`由URLHandler处理。

## 完整Provider示例（GitHub模式）

参见GitHub Provider源码：
- `providers/github/client.py`：AsyncGitHubClient API客户端
- `providers/github/handlers.py`：GitHubBlobHandler、GitHubTreeHandler、GitHubUserHandler
- `providers/github/__init__.py`：default_handlers()和uri_rewrites()

## 注意事项

1. **规则顺序**：URI重写规则是顺序匹配的，更具体的规则必须排在更通用的规则之前
2. **线程安全**：Handler实例是每个请求创建的，但客户端对象（如AsyncGitHubClient）是全局共享的
3. **缓存键**：如果Notebook内容受查询参数影响（如`?download`），需要将`_cache_key_attr`设为`"uri"`
4. **错误处理**：API错误应抛出适当的HTTPError（404/403/429/503），由catch_client_error统一处理
5. **breadcrumbs**：始终设置面包屑，提供良好的用户导航体验
6. **不要阻塞事件循环**：所有I/O操作必须是异步的，CPU密集操作放到线程池

## 相关文档

- [Provider插件系统](05-provider-plugin-system.md)：Provider加载机制详解
- [Handler继承体系](04-handler-hierarchy.md)：RenderingHandler基类详解
- [URI重写机制](08-uri-rewrite.md)：重写规则管道
- [Provider源码分析](../references/providers-source.md)：内置Provider完整源码分析
