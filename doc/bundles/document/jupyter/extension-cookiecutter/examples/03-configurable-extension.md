---
type: Example
title: 添加可配置参数
description: 演示如何为扩展添加 traitlets 可配置参数，包括不同类型的配置项、配置验证、在 Handler 中使用配置，以及测试配置覆盖。
tags: [example, configuration, traitlets, configurable, settings]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-py
    resource: /references/extension-app-source.md
    title: ExtensionApp 类源码解析
---

## 概述

模板中的 `ping_response` 展示了最基本的可配置参数。本示例演示如何添加多种类型的可配置参数、添加参数验证、在多个 Handler 中共享配置，以及如何测试不同的配置值。

## 步骤 1：定义多种类型的配置项

修改 `my_extension/extension.py`，添加多种 traitlets 配置：

```python
from traitlets import Unicode, Integer, Bool, List, Dict, Float, validate
from jupyter_server.extension.application import ExtensionApp
from .handlers import PingHandler, ConfigDemoHandler


class Extension(ExtensionApp):

    name = "my_extension"
    handlers = [
        ("my-extension/ping", PingHandler),
        ("my-extension/config", ConfigDemoHandler),
    ]

    # --- 字符串配置 ---
    ping_response = Unicode(
        default_value="pong",
        help="Response text for the ping endpoint."
    ).tag(config=True)

    api_prefix = Unicode(
        default_value="my-extension",
        help="URL prefix for extension API endpoints."
    ).tag(config=True)

    # --- 整数配置 ---
    max_items = Integer(
        default_value=100,
        help="Maximum number of items to return in list endpoints."
    ).tag(config=True)

    # --- 布尔配置 ---
    enable_cache = Bool(
        default_value=True,
        help="Whether to enable response caching."
    ).tag(config=True)

    debug_mode = Bool(
        default_value=False,
        help="Enable debug mode with verbose error messages."
    ).tag(config=True)

    # --- 浮点数配置 ---
    timeout = Float(
        default_value=30.0,
        help="Request timeout in seconds."
    ).tag(config=True)

    # --- 列表配置 ---
    allowed_origins = List(
        trait=Unicode(),
        default_value=["http://localhost:3000"],
        help="Allowed CORS origins."
    ).tag(config=True)

    # --- 字典配置 ---
    feature_flags = Dict(
        trait=Bool(),
        default_value={"beta_features": False, "experimental_api": False},
        help="Feature flags for enabling/disabling features."
    ).tag(config=True)

    # --- 参数验证 ---
    @validate("max_items")
    def _validate_max_items(self, proposal):
        """验证 max_items 在合理范围内"""
        value = proposal["value"]
        if value < 1:
            raise ValueError("max_items must be at least 1")
        if value > 1000:
            raise ValueError("max_items cannot exceed 1000")
        return value

    @validate("timeout")
    def _validate_timeout(self, proposal):
        """验证 timeout 为正数"""
        value = proposal["value"]
        if value <= 0:
            raise ValueError("timeout must be positive")
        return value

    def initialize_settings(self):
        """将所有配置注入 settings，供 Handler 访问"""
        self.settings.update({
            "ping_response": self.ping_response,
            "max_items": self.max_items,
            "enable_cache": self.enable_cache,
            "debug_mode": self.debug_mode,
            "timeout": self.timeout,
            "allowed_origins": self.allowed_origins,
            "feature_flags": self.feature_flags,
        })
```

## 步骤 2：创建使用配置的 Handler

创建 `ConfigDemoHandler` 演示如何在 Handler 中访问各种配置：

```python
import json
import tornado
from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.base.handlers import APIHandler


class ConfigDemoHandler(ExtensionHandlerMixin, APIHandler):
    """Demonstrate accessing configuration values in a Handler."""

    @property
    def max_items(self):
        return self.settings["max_items"]

    @property
    def enable_cache(self):
        return self.settings["enable_cache"]

    @property
    def debug_mode(self):
        return self.settings["debug_mode"]

    @property
    def feature_flags(self):
        return self.settings["feature_flags"]

    @tornado.web.authenticated
    def get(self):
        """GET /config - 返回当前配置值"""
        config_info = {
            "max_items": self.max_items,
            "enable_cache": self.enable_cache,
            "debug_mode": self.debug_mode,
            "feature_flags": self.feature_flags,
        }
        self.finish(json.dumps(config_info))
```

## 步骤 3：更新 handlers 模块导出

确保 `my_extension/handlers.py` 中包含所有 Handler，或在 `__init__.py` 中导出。如果 ConfigDemoHandler 定义在单独文件中，需要在 extension.py 中正确导入。

## 步骤 4：配置方式

用户可以通过以下几种方式配置扩展参数：

### 方式 1：配置文件（推荐）

创建或编辑 `jupyter_server_config.py`（通常在 `~/.jupyter/` 或当前目录）：

```python
c.Extension.ping_response = "hello from config"
c.Extension.max_items = 50
c.Extension.enable_cache = False
c.Extension.debug_mode = True
c.Extension.timeout = 60.0
c.Extension.allowed_origins = ["http://localhost:3000", "https://myapp.example.com"]
c.Extension.feature_flags = {"beta_features": True, "experimental_api": False}
```

注意配置类名：`c.Extension.xxx` 中的 `Extension` 是 ExtensionApp 子类的类名。如果你将类名改为 `MyExtension`，则使用 `c.MyExtension.xxx`。

### 方式 2：命令行参数

```bash
jupyter server --Extension.max_items=50 --Extension.debug_mode=True
```

### 方式 3：JSON 配置文件

在 `jupyter-config/jupyter_server_config.d/` 目录下可以配置，但 JSON 不支持复杂验证逻辑。

## 步骤 5：测试配置覆盖

在测试中通过 `jp_server_config` fixture 覆盖配置：

```python
import json
import pytest


async def test_default_config(jp_fetch):
    """测试默认配置值"""
    response = await jp_fetch("my-extension/config")
    assert response.code == 200
    config = json.loads(response.body)
    assert config["max_items"] == 100
    assert config["enable_cache"] is True
    assert config["debug_mode"] is False
    assert config["feature_flags"]["beta_features"] is False


async def test_custom_ping_response(jp_fetch):
    """测试默认 ping_response"""
    response = await jp_fetch("my-extension/ping")
    payload = json.loads(response.body)
    assert payload["ping_response"] == "pong"


@pytest.fixture
def jp_server_config(jp_server_config):
    """覆盖配置：启用 debug 模式和 beta features"""
    return {
        "ServerApp": {"jpserver_extensions": {"my_extension": True}},
        "Extension": {
            "ping_response": "custom ping",
            "max_items": 25,
            "debug_mode": True,
            "feature_flags": {"beta_features": True, "experimental_api": True},
        }
    }


async def test_custom_config(jp_fetch):
    """测试自定义配置值（使用上面的 fixture）"""
    response = await jp_fetch("my-extension/config")
    config = json.loads(response.body)
    assert config["max_items"] == 25
    assert config["debug_mode"] is True
    assert config["feature_flags"]["beta_features"] is True
    assert config["feature_flags"]["experimental_api"] is True

    # 验证 ping 端点也使用自定义值
    ping_resp = await jp_fetch("my-extension/ping")
    ping_payload = json.loads(ping_resp.body)
    assert ping_payload["ping_response"] == "custom ping"
```

注意：自定义配置的 fixture 会替换默认的 `jp_server_config`，必须包含 `ServerApp.jpserver_extensions` 来启用扩展。

## 步骤 6：测试配置验证

mypy 和 traitlets 验证器确保配置值有效。测试无效配置时 Jupyter Server 会报错：

```bash
# 无效值（max_items < 1）会导致启动失败
jupyter server --Extension.max_items=0
# 错误：ValueError: max_items must be at least 1
```

## traitlets 类型速查

| traitlets 类型 | Python 类型 | 示例默认值 |
|---------------|------------|-----------|
| `Unicode()` | str | `"default text"` |
| `Integer()` | int | `100` |
| `Float()` | float | `30.0` |
| `Bool()` | bool | `True`/`False` |
| `List(trait=Unicode())` | list[str] | `["a", "b"]` |
| `Dict(trait=Bool())` | dict[str, bool] | `{"key": True}` |
| `Set(trait=Unicode())` | set[str] | `{"a", "b"}` |
| `Tuple(Unicode(), Integer())` | tuple[str, int] | `("a", 1)` |
| `Enum(["a", "b", "c"])` | str (受限值) | `"a"` |
| `Path()` | pathlib.Path | `Path("/tmp")` |
| `Callable()` | callable | `some_function` |
| `Instance(MyClass)` | MyClass | |

## 最佳实践

1. **始终提供 help 文本**：`help="描述此配置的作用"`，用户可以通过 `--help-all` 看到
2. **设置合理默认值**：确保默认值能让扩展开箱即用
3. **使用 @validate 验证参数**：对有范围约束的参数添加验证器
4. **通过 settings 传递给 Handler**：不要在 Handler 中直接访问 traitlets，统一通过 settings
5. **使用 @property 包装 settings 访问**：提高可读性和可测试性
6. **编写配置测试**：为重要配置编写自定义 fixture 的测试用例

## 相关概念

- [ExtensionApp 开发](../concepts/04-extension-app.md)
- [API Handler 开发](../concepts/05-api-handlers.md)
- [测试策略](../concepts/07-testing.md)
- [基础 Ping 扩展示例](01-basic-ping-extension.md)
