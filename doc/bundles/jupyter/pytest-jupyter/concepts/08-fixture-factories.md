---
okf_version: "0.2"
type: concept
title: "Fixture工厂模式"
description: "理解 pytest-jupyter 中工厂fixtures的设计模式：jp_configurable_serverapp、jp_fetch、jp_ws_fetch、jp_start_kernel、jp_create_notebook等返回可调用对象的fixtures。"
tags: [factory-pattern, fixture-factory, pytest-fixtures, configurable-fixtures, inner-function, closure, dependency-injection]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-server-source
    resource: "/references/jupyter-server-source.md"
    title: "Server插件源码信源"
  - id: jupyter-client-source
    resource: "/references/jupyter-client-source.md"
    title: "Client插件源码信源"
---

# Fixture工厂模式

pytest-jupyter 大量采用**fixture工厂模式**——fixture不直接返回资源对象，而是返回一个内部函数（工厂），测试代码调用这个函数来创建资源。这种模式提供了更大的灵活性，是理解pytest-jupyter设计的关键。

## 什么是Fixture工厂模式？

### 普通Fixture（直接返回资源）

```python
@pytest.fixture
def jp_serverapp(...):
    app = ServerApp.instance(...)
    app.initialize(...)
    app.start_app()
    return app  # 直接返回app实例
```

**局限：**
- 每个测试只能有一个ServerApp实例
- 参数在fixture定义时固定，测试中难以灵活配置
- 无法在一个测试中创建多个实例

### 工厂Fixture（返回可调用对象）

```python
@pytest.fixture
def jp_configurable_serverapp(...):
    # fixture做准备工作...

    def _configurable_serverapp(config=..., port=..., **kwargs):
        # 每次调用创建一个新实例
        app = ServerApp.instance(...)
        return app

    return _configurable_serverapp  # 返回工厂函数
```

**优势：**
- 测试可以灵活创建零个、一个或多个实例
- 每次调用可以传入不同参数
- fixture负责准备环境和清理资源，工厂函数负责创建
- 通过闭包捕获fixture上下文中的资源（事件循环、临时路径等）

## pytest-jupyter中的工厂Fixtures

| 工厂Fixture | 返回的函数签名 | 用途 |
|------------|--------------|------|
| `jp_configurable_serverapp` | `(config, base_url, argv, http_port, root_dir, **kwargs) → ServerApp` | 创建可配置的ServerApp实例 |
| `jp_fetch` | `(*parts, headers, params, method, body, **kwargs) → HTTPResponse` | 发送HTTP请求 |
| `jp_ws_fetch` | `(*parts, headers, params, **kwargs) → WebSocketClientConnection` | 建立WebSocket连接 |
| `jp_start_kernel` | `(kernel_name=NATIVE_KERNEL_NAME, **kwargs) → (km, kc)` | 启动Jupyter内核 |
| `jp_create_notebook` | `(nbpath) → NBNode` | 创建notebook文件 |
| `send_request` | `(url, **fetch_kwargs) → int` | 发送请求并返回状态码 |

## 工厂模式的核心机制

### 机制1：闭包捕获Fixture上下文

工厂函数是在fixture内部定义的内部函数，通过Python闭包（closure）捕获fixture作用域中的变量：

```python
@pytest.fixture
def jp_start_kernel(jp_environ, jp_asyncio_loop):
    kms = []  # 被闭包捕获的资源追踪列表
    kcs = []

    async def inner(kernel_name=NATIVE_KERNEL_NAME, **kwargs):
        km, kc = await start_new_async_kernel(kernel_name=kernel_name, **kwargs)
        kms.append(km)  # 修改外层列表
        kcs.append(kc)
        return km, kc

    yield inner

    # 清理：遍历闭包中累积的资源
    for kc in kcs:
        kc.stop_channels()
    for km in kms:
        jp_asyncio_loop.run_until_complete(km.shutdown_kernel(now=True))
```

**关键点：**
- `kms`和`kcs`列表在fixture作用域中定义
- `inner`函数通过闭包访问和修改这些列表
- 每次调用`inner`都会追加资源到列表
- yield之后的清理代码可以访问所有创建的资源

[F-032]

### 机制2：默认参数值从Fixture依赖注入

```python
@pytest.fixture
def jp_configurable_serverapp(jp_server_config, jp_base_url, jp_argv, ...):
    def _configurable_serverapp(
        config=jp_server_config,    # 默认值来自fixture
        base_url=jp_base_url,        # 默认值来自fixture
        argv=jp_argv,
        http_port=jp_http_port,
        tmp_path=tmp_path,
        root_dir=jp_root_dir,
        **kwargs,
    ):
        c = Config(config)
        # ...创建app
        return app
    return _configurable_serverapp
```

工厂函数的参数默认值指向fixture依赖的fixtures。这意味着：
1. 不传入参数时使用fixture的默认配置
2. 传入参数时覆盖对应默认值
3. `**kwargs`透传给`ServerApp.instance()`提供额外配置

[F-080]

### 机制3：资源追踪与批量清理

由于工厂模式允许创建多个资源实例，fixture必须在yield之后追踪并清理所有实例：

```python
# jp_start_kernel的清理模式
kms = []
kcs = []

async def inner(...):
    km, kc = ...
    kms.append(km)  # 追踪
    kcs.append(kc)
    return km, kc

yield inner

# 批量清理所有创建的资源
for kc in kcs:
    kc.stop_channels()
for km in kms:
    jp_asyncio_loop.run_until_complete(km.shutdown_kernel(now=True))
```

相比之下，普通fixture只需要清理一个资源实例。

## 各工厂Fixture详解

### jp_configurable_serverapp：最典型的工厂

这是最完整的工厂fixture实现，展示了所有核心模式：

```python
@pytest.fixture
def jp_configurable_serverapp(jp_nbconvert_templates, jp_environ, jp_server_config,
                               jp_argv, jp_http_port, jp_base_url, tmp_path,
                               jp_root_dir, jp_logging_stream, jp_asyncio_loop):
    ServerApp.clear_instance()

    # 预处理：注入默认扩展配置
    serverapp_config = jp_server_config.setdefault("ServerApp", {})
    exts = serverapp_config.setdefault("jpserver_extensions", {})
    if "jupyter_server_terminals" not in exts and is_v2:
        exts["jupyter_server_terminals"] = True

    def _configurable_serverapp(config=..., base_url=..., ..., **kwargs):
        # 每次调用：创建全新ServerApp实例
        c = Config(config)
        c.NotebookNotary.db_file = ":memory:"
        default_token = hexlify(os.urandom(4)).decode("ascii")
        # ...设置token、root_dir等
        app = ServerApp.instance(log_level="DEBUG", port=http_port, ...)
        app.init_signal = lambda: None
        app.initialize(argv=argv, new_httpserver=False)
        # ...重定向日志
        app.start_app()
        return app

    return _configurable_serverapp
```

**fixture预处理（yield之前，每次测试执行一次）：**
- 清除ServerApp单例
- 注入默认扩展配置

**工厂函数（每次调用执行）：**
- 复制config对象（避免多次调用共享同一个Config对象）
- 设置内存数据库
- 生成随机token
- 创建并初始化新的ServerApp实例

**注意**：`jp_server_cleanup`（autouse fixture）负责清理ServerApp资源，因此jp_configurable_serverapp本身没有显式的yield后清理代码。

[F-080]

### jp_fetch/jp_ws_fetch：请求工厂

HTTP和WebSocket请求工厂展示了另一种模式——参数收集与组合：

```python
@pytest.fixture
def jp_fetch(jp_serverapp, http_server_client, jp_auth_header, jp_base_url):
    def client_fetch(*parts, headers=None, params=None, **kwargs):
        # 1. URL拼接与编码
        path_url = url_escape(url_path_join(*parts), plus=False)
        base_path_url = url_path_join(jp_base_url, path_url)
        params_url = urllib.parse.urlencode(params or {})
        url = base_path_url + "?" + params_url

        # 2. 认证头合并（不覆盖用户设置）
        headers = headers or {}
        for key, value in jp_auth_header.items():
            headers.setdefault(key, value)

        # 3. 默认超时
        request_timeout = kwargs.pop("request_timeout", 20)

        # 4. 发送请求
        return http_server_client.fetch(
            url, headers=headers, request_timeout=request_timeout, **kwargs
        )
    return client_fetch
```

**设计要点：**
- `*parts`收集URL路径段，自动拼接和编码
- `headers.setdefault`确保认证头存在但不覆盖用户自定义值
- `kwargs.pop("request_timeout", 20)`提取并设置默认超时，其余透传
- 闭包捕获`jp_auth_header`、`jp_base_url`、`http_server_client`

[F-085]

jp_ws_fetch额外展示了**参数过滤**模式：
```python
allowed = list(inspect.signature(tornado.websocket.websocket_connect).parameters)
for name in list(kwargs):
    if name not in allowed:
        del kwargs[name]
```
通过`inspect.signature`获取目标函数可接受的参数名，过滤掉不兼容的kwargs，增强跨版本兼容性。

[F-086]

### jp_create_notebook：最简单的工厂

```python
@pytest.fixture
def jp_create_notebook(jp_root_dir):
    def inner(nbpath):
        nbpath = jp_root_dir.joinpath(nbpath)
        if nbpath.suffix != ".ipynb":
            raise Exception("File extension for notebook must be .ipynb")
        parent = nbpath.parent
        parent.mkdir(parents=True, exist_ok=True)
        nb = nbformat.v4.new_notebook()
        nbtext = nbformat.writes(nb, version=4)
        nbpath.write_text(nbtext)
        return nb
    return inner
```

这个简单工厂：
1. 验证文件扩展名
2. 创建父目录
3. 创建空notebook并写入文件
4. 返回notebook对象

没有需要清理的资源（文件在tmp_path中，测试结束后自动删除）。

[F-088]

## 普通Fixture vs 工厂Fixture的选择

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 每个测试只需要一个实例，参数固定 | 普通Fixture | 简单直接 |
| 需要在测试中灵活配置参数 | 工厂Fixture | 可在调用时传参 |
| 需要在一个测试中创建多个实例 | 工厂Fixture | 可多次调用 |
| 需要条件性创建资源 | 工厂Fixture | 可以不调用，不创建资源 |
| 资源创建成本高且大多数测试不需要 | 工厂Fixture | 避免不必要的创建 |
| 资源创建有依赖关系需要分步 | 工厂Fixture | 可以按顺序创建 |

## 编写自定义工厂Fixture的模板

基于pytest-jupyter的模式，编写自定义工厂Fixture时遵循以下模板：

```python
@pytest.fixture
def my_resource_factory(some_dependency, tmp_path, jp_asyncio_loop):
    # 1. 初始化：准备环境、创建资源追踪列表
    created_resources = []

    # 2. 定义工厂函数（闭包）
    def _create_resource(config=None, **kwargs):
        """创建资源的内部函数"""
        # 参数默认值处理
        config = config or default_config
        # 创建资源
        resource = create_some_resource(config, **kwargs)
        # 追踪资源
        created_resources.append(resource)
        return resource

    # 3. yield工厂函数给测试使用
    yield _create_resource

    # 4. 清理：释放所有追踪的资源
    for resource in created_resources:
        resource.cleanup()
```

## 工厂模式的注意事项

1. **Config对象隔离**：如果工厂函数接收Config对象参数，应该复制（`Config(config)`）而非直接使用传入的对象，防止多次调用共享同一Config导致配置污染
2. **资源追踪列表必须初始化**：在fixture作用域中（而非工厂函数内）创建追踪列表
3. **闭包变量修改**：Python 3中内层函数可以修改外层列表（append等），但不能重新赋值外层变量（需用nonlocal）
4. **默认参数使用None**：对于可变类型默认参数（如`headers=None, params=None`），使用None作为哨兵值，在函数体内初始化为空dict/list
5. **不要在工厂fixture的yield前创建实际资源**：fixture的setUp阶段只做准备工作，实际资源创建推迟到工厂函数被调用时

---

**下一步阅读：**
- [Server插件详解](/concepts/05-server-plugin.md) — 看jp_configurable_serverapp和jp_fetch/jp_ws_fetch如何在实际中使用
- [示例：Server API测试](/examples/03-server-api-test.md) — 工厂fixtures的实战代码
- [示例：自定义Server配置](/examples/04-custom-server-config.md) — 如何通过fixture覆盖来自定义ServerApp
