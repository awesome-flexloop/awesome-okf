# 示例代码索引

本目录包含 pytest-jupyter 的实用测试示例代码，按使用场景分类。

## 示例列表

### 基础示例

| 示例 | 所需插件extra | 核心fixtures | 内容 |
|------|-------------|-------------|------|
| [Core插件基础测试](01-basic-core-test.md) | 无（默认安装） | jp_environ, jp_*_dir, echo_kernel_spec | 环境隔离验证、async测试函数、临时目录使用 |

### 内核测试

| 示例 | 所需插件extra | 核心fixtures | 内容 |
|------|-------------|-------------|------|
| [内核测试](02-kernel-testing.md) | `[client]` | jp_start_kernel, jp_zmq_context | echo内核、Python内核、多内核、ZMQ、直接实例化测试 |

### Server测试

| 示例 | 所需插件extra | 核心fixtures | 内容 |
|------|-------------|-------------|------|
| [Server API测试](03-server-api-test.md) | `[server]` | jp_fetch, jp_ws_fetch, jp_serverapp | REST API、kernel生命周期、WebSocket、认证授权 |
| [自定义Server配置](04-custom-server-config.md) | `[server]` | jp_server_config, jp_base_url, jp_configurable_serverapp | 覆盖默认fixture、配置扩展、多配置对比 |

## 快速开始

如果你是第一次使用 pytest-jupyter，按以下顺序阅读：

1. **[Core插件基础测试](01-basic-core-test.md)** — 了解基本fixture使用和async测试
2. 根据需要升级到client或server层：
   - 测试内核/消息协议 → **[内核测试](02-kernel-testing.md)**
   - 测试REST API/WebSocket → **[Server API测试](03-server-api-test.md)**
3. 需要自定义配置时阅读 **[自定义Server配置](04-custom-server-config.md)**

## 插件安装命令

```bash
# 仅core（基础fixtures）
pip install pytest-jupyter

# core + client（内核测试）
pip install "pytest-jupyter[client]"

# core + client + server（完整Server测试，推荐）
pip install "pytest-jupyter[server]"
```

## conftest.py 配置参考

```python
# 最小配置（core only）
pytest_plugins = ["pytest_jupyter"]

# client层
pytest_plugins = ["pytest_jupyter.jupyter_client"]

# server层（推荐，包含所有fixtures）
pytest_plugins = ["pytest_jupyter.jupyter_server"]

# 加载多个插件
pytest_plugins = [
    "pytest_jupyter",
    "pytest_jupyter.jupyter_server",
]
```

```{toctree}
:hidden:

01-basic-core-test
02-kernel-testing
03-server-api-test
04-custom-server-config
```
