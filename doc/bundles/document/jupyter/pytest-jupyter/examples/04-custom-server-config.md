---
okf_version: "0.2"
type: example
title: "自定义Server配置"
description: "通过覆盖fixtures来自定义Jupyter Server配置：默认内核、根目录、base URL、认证token、扩展启用等。"
tags: [custom-config, jp-server-config, jp-base-url, jp-root-dir, jp-argv, fixture-override, extension-testing]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-server-source
    resource: "/references/jupyter-server-source.md"
    title: "Server插件源码信源"
  - id: readme
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/README.md"
    title: "README.md"
---

# 自定义Server配置

本文档演示如何通过覆盖pytest-jupyter的默认fixtures来自定义Jupyter Server测试配置。pytest-jupyter的每个配置fixture都设计为可被覆盖，测试只需在conftest.py或测试文件中重新定义同名fixture即可替换默认行为。

## 前置条件

```bash
pip install "pytest-jupyter[server]"
```

## 示例1：修改默认内核

默认情况下Server插件使用Python3内核（NATIVE_KERNEL_NAME）。要让测试默认使用echo内核（加速测试），覆盖`jp_server_config` fixture：

```python
# conftest.py
import pytest
from traitlets.config import Config

pytest_plugins = ["pytest_jupyter.jupyter_server"]

@pytest.fixture
def jp_server_config():
    """配置使用echo内核作为默认内核"""
    c = Config()
    c.MultiKernelManager.default_kernel_name = "echo"
    c.ServerApp.jpserver_extensions = {
        "jupyter_server_terminals": True
    }
    return c
```

或者在单个测试文件中覆盖：

```python
import pytest
from traitlets.config import Config

@pytest.fixture
def jp_server_config():
    c = Config()
    c.MultiKernelManager.default_kernel_name = "echo"
    return c

async def test_uses_echo_kernel(jp_fetch):
    # 创建kernel时不传name，将使用默认的echo内核
    response = await jp_fetch(
        "api", "kernels",
        method="POST",
        body="{}"
    )
    import json
    kernel = json.loads(response.body)
    assert kernel["name"] == "echo"
```

README中也提到了这个配置：
```json
{
    "MultiKernelManager": {
        "default_kernel_name": "<desired_kernel_name>"
    }
}
```

## 示例2：自定义Base URL

默认`jp_base_url`返回`"/a%40b/"`（测试URL编码场景）。测试需要特定base URL时覆盖它：

```python
@pytest.fixture
def jp_base_url():
    """使用根路径作为base URL"""
    return "/"

async def test_root_base_url(jp_fetch, jp_base_url):
    assert jp_base_url == "/"
    response = await jp_fetch("api", "spec.yaml")
    assert response.code == 200

@pytest.fixture
def jp_base_url():
    """自定义前缀"""
    return "/my-app/"

async def test_custom_prefix(jp_fetch, jp_base_url):
    response = await jp_fetch("api", "status")
    assert response.code == 200
```

## 示例3：自定义根目录

```python
import pytest
from pathlib import Path

@pytest.fixture
def jp_root_dir(tmp_path):
    """使用自定义的根目录（包含测试数据文件）"""
    # 创建带测试数据的目录
    nb_dir = tmp_path / "notebooks"
    nb_dir.mkdir()
    (nb_dir / "test.ipynb").write_text('{"nbformat": 4, "cells": []}')
    return nb_dir

async def test_root_dir_contents(jp_fetch, jp_root_dir):
    # 列出根目录内容
    response = await jp_fetch("api", "contents", method="GET")
    assert response.code == 200
    import json
    contents = json.loads(response.body)
    # test.ipynb应该在根目录中
    names = [item["name"] for item in contents.get("content", [])]
    assert "test.ipynb" in names
```

或者使用`jp_configurable_serverapp`直接设置root_dir=None（使用cwd）或其他路径：

```python
async def test_null_root_dir(jp_configurable_serverapp, tmp_path):
    """测试root_dir=None时使用默认cwd行为"""
    app = jp_configurable_serverapp(root_dir=None)
    # root_dir为None时不设置，ServerApp使用默认行为
    assert app is not None
```

## 示例4：自定义命令行参数

```python
@pytest.fixture
def jp_argv():
    """传递自定义命令行参数"""
    return [
        "--ServerApp.disable_check_xsrf=True",
        "--ServerApp.allow_origin='*'",
    ]

async def test_custom_argv(jp_serverapp):
    # jp_serverapp使用自定义argv初始化
    assert jp_serverapp is not None
```

## 示例5：使用jp_configurable_serverapp创建多配置实例

需要对比不同配置行为时，在测试内部多次调用工厂函数：

```python
async def test_multiple_configs(jp_configurable_serverapp, tmp_path):
    """测试不同配置的ServerApp"""
    from traitlets.config import Config

    # 配置A：启用terminals扩展
    config_a = Config()
    config_a.ServerApp.jpserver_extensions = {"jupyter_server_terminals": True}
    app_a = jp_configurable_serverapp(config=config_a, root_dir=tmp_path)

    # 注意：ServerApp是单例模式，同一时间只能有一个实例运行
    # jp_server_cleanup会在测试结束后清理
    assert app_a is not None
```

> **注意**：Jupyter Server的ServerApp使用单例模式（`ServerApp.instance()`），同一时间只能运行一个ServerApp实例。如果需要测试多个配置，需要确保前一个实例被正确清理。

## 示例6：测试Jupyter扩展

测试自己开发的Jupyter Server扩展时，需要启用扩展：

```python
import pytest
from traitlets.config import Config

@pytest.fixture
def jp_server_config():
    """配置启用被测扩展"""
    c = Config()
    c.ServerApp.jpserver_extensions = {
        "my_extension": True,  # 启用你的扩展
        "jupyter_server_terminals": True,
    }
    return c

@pytest.fixture
def jp_extension_environ(jp_env_config_path, monkeypatch):
    """配置扩展的环境路径"""
    from jupyter_server.extension import serverextension
    monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(jp_env_config_path)])
    # 这里可以做更多扩展配置...

async def test_my_extension_endpoint(jp_fetch):
    """测试扩展提供的API端点"""
    response = await jp_fetch("my_extension", "endpoint", method="GET")
    assert response.code == 200
```

## 示例7：自定义Token和认证

```python
import pytest

@pytest.fixture
def jp_server_config():
    c = Config()
    # v2 使用 IdentityProvider.token
    c.IdentityProvider.token = "my-test-token"
    # v1 使用 ServerApp.token
    c.ServerApp.token = "my-test-token"
    return c

async def test_custom_token(jp_serverapp):
    """测试自定义token"""
    # token应该是我们设置的值
    token = (jp_serverapp.identity_provider.token
             if hasattr(jp_serverapp, 'identity_provider')
             else jp_serverapp.token)
    assert token == "my-test-token"
```

## 示例8：禁用自动清理日志输出

```python
@pytest.fixture
def jp_logging_stream():
    """自定义日志流（例如不自动print）"""
    import io
    return io.StringIO()
```

## 配置覆盖优先级

理解fixture覆盖的优先级很重要：

1. **conftest.py中的fixture**：对所有测试生效
2. **测试文件中的fixture**：仅对该文件中的测试生效
3. **测试函数参数中直接使用jp_configurable_serverapp()**：优先级最高，单次调用配置

```python
# 优先级3：调用工厂函数时传参覆盖
async def test_inline_override(jp_configurable_serverapp):
    from traitlets.config import Config
    c = Config()
    c.ServerApp.port_retries = 0
    app = jp_configurable_serverapp(
        config=c,
        base_url="/custom/",
        root_dir=None,
    )
    # 此app使用inline配置，忽略fixture默认值
```

## 可覆盖Fixtures速查表

| Fixture | 默认值 | 覆盖用途 |
|---------|-------|---------|
| `jp_server_config` | terminals扩展启用 | 配置ServerApp选项、扩展、内核管理器 |
| `jp_base_url` | `"/a%40b/"` | 修改base URL前缀 |
| `jp_root_dir` | `{tmp_path}/root_dir` | 设置Notebook根目录 |
| `jp_template_dir` | `{tmp_path}/templates` | 设置模板目录 |
| `jp_argv` | `[]` | 传递命令行参数 |
| `jp_environ` | 完整隔离 | 自定义环境变量和路径 |
| `jp_http_port` | 自动分配 | 指定固定端口（不推荐，会冲突） |

## 相关概念

- [Server插件详解](/concepts/05-server-plugin.md) — 各fixture的完整说明
- [Fixture工厂模式](/concepts/08-fixture-factories.md) — jp_configurable_serverapp工厂模式
- [Server API测试](03-server-api-test.md) — 基础API测试示例
