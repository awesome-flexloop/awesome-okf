---
okf_version: "0.2"
type: example
title: "Core插件基础测试"
description: "使用Core插件的fixtures进行环境隔离测试、临时目录验证、async测试函数编写。"
tags: [core, basic-testing, jp-environ, tmp-path, async, environment-isolation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: test-core
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/tests/test_jupyter_core.py"
    title: "tests/test_jupyter_core.py"
  - id: jupyter-core-source
    resource: "/references/jupyter-core-source.md"
    title: "Core插件源码信源"
---

# Core插件基础测试

本文档演示如何使用pytest-jupyter的Core插件（`pytest_jupyter.jupyter_core`）编写不涉及网络和内核的基础测试。

## 前置条件

```bash
pip install pytest-jupyter
```

```python
# conftest.py
pytest_plugins = ["pytest_jupyter"]  # 等同于pytest_jupyter.jupyter_core
```

## 示例1：验证环境隔离

最基本的测试——验证`jp_environ` fixture正确隔离了Jupyter环境。

```python
import os
from jupyter_core import paths

def test_jupyter_data_dir_is_isolated(jp_environ):
    """测试Jupyter数据目录被隔离到临时路径"""
    data_dir = paths.jupyter_data_dir()
    # 数据目录应该存在
    assert os.path.exists(data_dir)
    # 数据目录应该在临时路径下（不是用户真实的~/.local/share/jupyter）
    assert "tmp" in data_dir or "Temp" in data_dir or "temp" in data_dir

def test_jupyter_config_dir_is_isolated(jp_environ):
    """测试Jupyter配置目录被隔离"""
    config_dir = paths.jupyter_config_dir()
    assert os.path.exists(config_dir)

def test_jupyter_runtime_dir_is_isolated(jp_environ):
    """测试Jupyter运行时目录被隔离"""
    runtime_dir = paths.jupyter_runtime_dir()
    assert os.path.exists(runtime_dir)
```

## 示例2：异步测试函数

Core插件原生支持`async def test_*`风格的异步测试，无需安装pytest-asyncio。

```python
import asyncio

async def test_async_function_support():
    """测试异步测试函数能正常运行"""
    await asyncio.sleep(0.01)
    assert True

async def test_jp_asyncio_loop_is_available(jp_asyncio_loop):
    """测试可以直接使用jp_asyncio_loop fixture"""
    assert jp_asyncio_loop is not None
    # 在fixture提供的循环上运行协程
    result = jp_asyncio_loop.run_until_complete(asyncio.sleep(0.01, result=42))
    assert result == 42
```

## 示例3：使用临时目录fixtures

虽然`jp_environ`聚合了所有目录fixtures，但你也可以单独使用各个目录fixtures。

```python
def test_tmp_directories(jp_home_dir, jp_data_dir, jp_config_dir, jp_runtime_dir):
    """测试各临时目录fixture正确创建目录"""
    from pathlib import Path

    assert isinstance(jp_home_dir, Path)
    assert isinstance(jp_data_dir, Path)
    assert jp_home_dir.exists()
    assert jp_data_dir.exists()
    assert jp_config_dir.exists()
    assert jp_runtime_dir.exists()

    # 所有目录都在tmp_path下
    # （因为它们都基于pytest内置的tmp_path fixture创建）
    assert "home" in str(jp_home_dir)
    assert "data" in str(jp_data_dir)
    assert "config" in str(jp_config_dir)
    assert "runtime" in str(jp_runtime_dir)

def test_kernel_dir_exists(jp_kernel_dir):
    """测试内核spec目录存在"""
    assert jp_kernel_dir.exists()
    assert "kernels" in str(jp_kernel_dir)
```

## 示例4：Echo内核spec安装

`echo_kernel_spec` fixture在临时环境中安装echo内核的kernelspec。

```python
import json
from pathlib import Path

def test_echo_kernel_spec_installed(echo_kernel_spec, jp_kernel_dir):
    """测试echo内核spec被正确安装"""
    # echo_kernel_spec返回内核spec目录路径
    kernel_json = Path(echo_kernel_spec) / "kernel.json"
    assert kernel_json.exists()

    # 读取kernel.json
    spec = json.loads(kernel_json.read_text())
    assert spec["display_name"] == "echo"
    assert spec["language"] == "echo"
    assert "pytest_jupyter.echo_kernel" in spec["argv"][2]
    assert "{connection_file}" in spec["argv"][-1]
```

## 示例5：编写使用Jupyter路径工具的测试

如果你在开发一个使用jupyter_core路径API的工具，可以使用`jp_environ`确保测试不影响用户环境。

```python
import json
from jupyter_core import paths

def test_write_config_to_isolated_dir(jp_environ):
    """测试向隔离的配置目录写入配置文件"""
    config_dir = paths.jupyter_config_dir()
    config_file = Path(config_dir) / "my_config.json"

    # 写入测试配置
    config_file.write_text(json.dumps({"test_key": "test_value"}))

    # 读取验证
    loaded = json.loads(config_file.read_text())
    assert loaded["test_key"] == "test_value"

    # 文件确实在隔离目录中，不影响用户真实配置
    assert str(config_file).startswith(str(Path(config_dir)))
```

## 运行测试

```bash
# 运行core插件相关测试
pytest tests/ -v -p pytest_jupyter

# 查看core插件提供的所有fixtures
pytest --fixtures -p pytest_jupyter
```

## 相关概念

- [Core插件详解](../concepts/03-core-plugin.md) — Core插件fixtures完整API
- [架构总览](../concepts/02-architecture-overview.md) — 异步测试支持机制
- [内核测试示例](02-kernel-testing.md) — 升级到Client插件测试内核
