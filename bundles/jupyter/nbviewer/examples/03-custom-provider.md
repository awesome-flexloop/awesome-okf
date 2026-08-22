---
type: Example
title: 自定义Provider开发
description: 从零开发自定义nbviewer Provider的完整示例，包括轻量URL重写Provider和完整Handler Provider两种模式
tags:
  - jupyter
  - nbviewer
  - provider
  - extension
  - example
  - development
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/
---

# 自定义Provider开发

本文档通过两个实际示例演示如何开发自定义Provider。

## 示例一：轻量URL重写Provider

**场景**：你的公司内部有一个Notebook分享服务`notebook.company.com`，分享链接格式为`https://notebook.company.com/nb/abc123`，需要转换为直链`https://notebook.company.com/download/abc123.ipynb`。

这种场景只需一个`__init__.py`文件，无需自定义Handler。

### 步骤1：创建Provider包

```bash
mkdir -p my_nbviewer_providers/company
touch my_nbviewer_providers/__init__.py
touch my_nbviewer_providers/company/__init__.py
```

### 步骤2：实现uri_rewrites()

```python
# my_nbviewer_providers/company/__init__.py

def uri_rewrites(rewrites=[]):
    """将公司Notebook分享URL转换为直链下载URL"""
    return rewrites + [
        # 匹配 https://notebook.company.com/nb/{id}
        # 转换为 /urls/notebook.company.com/download/{id}.ipynb
        (
            r"^https?://notebook\.company\.com/nb/([a-zA-Z0-9_-]+)/?$",
            "/urls/notebook.company.com/download/{0}.ipynb"
        ),
    ]
```

### 步骤3：安装到Python路径

```bash
pip install -e .
```

或在setup.py中配置包：
```python
# setup.py
from setuptools import setup, find_packages
setup(
    name="my-nbviewer-providers",
    packages=find_packages(),
)
```

### 步骤4：配置nbviewer加载Provider

```bash
python -m nbviewer \
  --provider-rewrites="['nbviewer.providers.gist', 'nbviewer.providers.github', 'nbviewer.providers.dropbox', 'nbviewer.providers.huggingface', 'my_nbviewer_providers.company', 'nbviewer.providers.url']"
```

注意：将自定义Provider放在`nbviewer.providers.url`之前，确保在兜底规则之前匹配。

### 测试

在首页输入框输入：`https://notebook.company.com/nb/abc123`

应该被重定向到：`/urls/notebook.company.com/download/abc123.ipynb`，由URLHandler下载并渲染。

## 示例二：完整Handler Provider

**场景**：你需要从一个需要API认证的Notebook服务获取Notebook。该服务有自己的API，需要传入API Key，且目录浏览需要特殊处理。

### 步骤1：创建包结构

```bash
mkdir -p my_nbviewer_providers/myservice
touch my_nbviewer_providers/myservice/__init__.py
touch my_nbviewer_providers/myservice/handlers.py
touch my_nbviewer_providers/myservice/client.py
```

### 步骤2：实现API客户端

```python
# my_nbviewer_providers/myservice/client.py
import os
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from urllib.parse import urlencode

class MyServiceClient:
    """MyService API客户端"""
    
    def __init__(self, log, api_key=None):
        self.log = log
        self.api_key = api_key or os.environ.get("MYSERVICE_API_KEY", "")
        self.base_url = os.environ.get(
            "MYSERVICE_API_URL", 
            "https://api.myservice.com/v1"
        )
        self.client = AsyncHTTPClient()
    
    async def fetch_notebook(self, notebook_id):
        """获取Notebook内容"""
        url = f"{self.base_url}/notebooks/{notebook_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request = HTTPRequest(url, headers=headers)
        response = await self.client.fetch(request)
        return response.body.decode("utf-8")
    
    async def list_notebooks(self, folder_id=None):
        """列出目录中的Notebook"""
        url = f"{self.base_url}/notebooks"
        if folder_id:
            url += f"?folder={folder_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request = HTTPRequest(url, headers=headers)
        response = await self.client.fetch(request)
        import json
        return json.loads(response.body)
```

### 步骤3：实现Handler

```python
# my_nbviewer_providers/myservice/handlers.py
import os
from tornado import web
from nbviewer.providers.base import RenderingHandler, cached
from .client import MyServiceClient
from nbviewer.utils import url_path_join

class MyServiceHandler(RenderingHandler):
    """处理myservice.com的Notebook"""
    
    _client = None
    
    @property
    def client(self):
        if self._client is None:
            self.__class__._client = MyServiceClient(
                log=self.log,
                api_key=self.settings.get("myservice_api_key", "")
            )
        return self.__class__._client
    
    async def get_notebook_data(self, notebook_id):
        """从MyService API获取Notebook"""
        try:
            nbdata = await self.client.fetch_notebook(notebook_id)
        except web.HTTPError as e:
            if e.code == 404:
                raise web.HTTPError(404, f"Notebook {notebook_id} not found")
            elif e.code == 403:
                raise web.HTTPError(403, "Access denied")
            raise
        
        # 设置面包屑
        breadcrumbs = [
            {"url": url_path_join(self.base_url, "/"), "name": "home"},
            {"url": self.request.uri, "name": notebook_id},
        ]
        
        return nbdata, {
            "breadcrumbs": breadcrumbs,
            "provider_url": f"https://myservice.com/nb/{notebook_id}",
            "title": f"Notebook {notebook_id}",
            "provider_label": "MyService",
            "provider_icon": "book",
        }
    
    async def deliver_notebook(self, nbdata, namespace):
        """调用finish_notebook渲染"""
        await self.finish_notebook(
            nbdata,
            download_url=namespace.get("provider_url"),
            msg=f"notebook from myservice: {namespace['title']}",
            public=True,
            **namespace,
        )
    
    @cached
    async def get(self, notebook_id):
        """路由入口"""
        nbdata, namespace = await self.get_notebook_data(notebook_id)
        await self.deliver_notebook(nbdata, namespace)


def default_handlers(handlers=[], **handler_names):
    """注册路由"""
    # 支持Handler类替换
    import importlib
    handler_location = handler_names.get(
        "myservice_handler",
        "my_nbviewer_providers.myservice.handlers.MyServiceHandler"
    )
    module_name, cls_name = handler_location.rsplit(".", 1)
    module = importlib.import_module(module_name)
    my_handler = getattr(module, cls_name)
    
    return handlers + [
        (r"/myservice/([a-zA-Z0-9_-]+)/?", my_handler, {}),
    ]


def uri_rewrites(rewrites=[]):
    """URI重写规则"""
    return rewrites + [
        (
            r"^https?://myservice\.com/nb/([a-zA-Z0-9_-]+)/?$",
            "/myservice/{0}"
        ),
    ]
```

### 步骤4：注册Provider

创建`__init__.py`（如果需要统一导出）：

```python
# my_nbviewer_providers/myservice/__init__.py
from .handlers import default_handlers, uri_rewrites
```

### 步骤5：配置nbviewer

```python
# nbviewer_config.py
import os
c = get_config()

c.NBViewer.port = 8080
c.NBViewer.processes = 2

# 注册Provider（含Handler和URI重写）
c.NBViewer.providers = [
    "nbviewer.providers.url",
    "nbviewer.providers.github",
    "nbviewer.providers.gist",
    "my_nbviewer_providers.myservice",
]

c.NBViewer.provider_rewrites = [
    "nbviewer.providers.gist",
    "nbviewer.providers.github",
    "my_nbviewer_providers.myservice",
    "nbviewer.providers.dropbox",
    "nbviewer.providers.huggingface",
    "nbviewer.providers.url",
]

# 自定义Handler设置（通过handler_settings注入）
c.NBViewer.handler_settings = {
    "myservice_api_key": os.environ.get("MYSERVICE_API_KEY", ""),
}
```

启动：
```bash
export MYSERVICE_API_KEY="your-api-key"
python -m nbviewer --config-file=nbviewer_config.py
```

### 测试

- 直接访问：http://localhost:8080/myservice/abc123
- URL转换：在首页输入`https://myservice.com/nb/abc123`
- 格式切换：http://localhost:8080/format/slides/myservice/abc123

## 调试技巧

1. **启用DEBUG日志**：`--debug`查看详细日志
2. **禁用缓存**：`--no-cache`避免缓存干扰调试
3. **刷新缓存**：URL后添加`?flush_cache=1`
4. **检查路由**：在init_handlers处断点查看注册的路由
5. **测试重写规则**：单独测试transform_ipynb_uri函数

## 相关文档

- [自定义Provider扩展](/concepts/12-custom-provider.md)：Provider契约和开发指南
- [Provider插件系统](/concepts/05-provider-plugin-system.md)：Provider加载机制
- [Handler继承体系](/concepts/04-handler-hierarchy.md)：RenderingHandler基类
- [URI重写机制](/concepts/08-uri-rewrite.md)：重写规则详解
