---
type: Example
title: "高级测试编写"
description: "使用TrackedContainer编写自定义pytest测试、容器执行命令、HTTP端点验证、日志检查等高级测试模式"
tags: [example, testing, pytest, trackcontainer, custom-tests]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-tests, resource: "/references/tests-source.md", title: "测试框架源码索引" }
---

# 高级测试编写

本示例展示如何使用 cookiecutter-docker-stacks 的测试框架编写更丰富的自定义测试，包括包验证、环境检查、HTTP端点测试、日志检查等模式。

## 测试基础回顾

模板提供了三个核心fixture：

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `container` | function | TrackedContainer实例，测试后自动清理 |
| `http_client` | session | 带重试的requests.Session |
| `free_host_port` | function | 自动分配的空闲端口号 |

## 测试模式1：包导入验证

验证自定义安装的包都可以正常导入：

```python
# tests/test_packages.py
import pytest
from tests.utils.tracked_container import TrackedContainer

PACKAGES = [
    ("polars", "pl"),
    ("duckdb", None),
    ("seaborn", "sns"),
    ("xgboost", "xgb"),
    ("sklearn", None),
    ("pandas", "pd"),
]

@pytest.mark.parametrize("package,alias", PACKAGES)
def test_package_import(container: TrackedContainer, package: str, alias: str | None):
    """参数化测试：验证每个包都能成功导入"""
    container.run_detached()
    import_line = f"import {package}" + (f" as {alias}" if alias else "")
    output = container.exec_cmd(f"python -c '{import_line}; print(\"OK\")'")
    assert "OK" in output, f"Failed to import {package}"
```

## 测试模式2：环境变量验证

```python
# tests/test_environment.py
from tests.utils.tracked_container import TrackedContainer

def test_nb_user(container: TrackedContainer):
    """验证默认用户为jovyan"""
    container.run_detached()
    user = container.exec_cmd("echo $NB_USER").strip()
    assert user == "jovyan"

def test_working_directory(container: TrackedContainer):
    """验证工作目录为/home/jovyan"""
    container.run_detached()
    pwd = container.exec_cmd("pwd").strip()
    assert pwd == "/home/jovyan"

def test_python_version(container: TrackedContainer):
    """验证Python版本"""
    container.run_detached()
    version = container.exec_cmd("python --version 2>&1").strip()
    assert "Python 3" in version

def test_conda_available(container: TrackedContainer):
    """验证mamba/conda可用"""
    container.run_detached()
    # 基础镜像使用micromamba
    output = container.exec_cmd("which micromamba || which mamba || which conda")
    assert output.strip() != ""
```

## 测试模式3：Jupyter Server HTTP端点验证

```python
# tests/test_server.py
import requests
from tests.utils.tracked_container import TrackedContainer

def test_server_api_endpoint(
    container: TrackedContainer,
    http_client: requests.Session,
    free_host_port: int
):
    """验证Jupyter Server API端点可访问"""
    container.run_detached(
        ports={"8888/tcp": free_host_port},
        environment={"JUPYTER_TOKEN": "test-token-123"}
    )

    # 访问API端点（带token）
    resp = http_client.get(
        f"http://localhost:{free_host_port}/api",
        headers={"Authorization": "token test-token-123"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data

def test_lab_endpoint(
    container: TrackedContainer,
    http_client: requests.Session,
    free_host_port: int
):
    """验证JupyterLab页面可访问"""
    container.run_detached(ports={"8888/tcp": free_host_port})
    resp = http_client.get(f"http://localhost:{free_host_port}/lab")
    resp.raise_for_status()
    assert "JupyterLab" in resp.text or "login_submit" in resp.text

def test_static_assets(
    container: TrackedContainer,
    http_client: requests.Session,
    free_host_port: int
):
    """验证静态资源可访问"""
    container.run_detached(ports={"8888/tcp": free_host_port})
    resp = http_client.get(f"http://localhost:{free_host_port}/static/favicon.ico")
    # 可能返回200或302（重定向到登录页）
    assert resp.status_code in (200, 302)
```

## 测试模式4：启动日志检查

```python
# tests/test_startup.py
import time
from tests.utils.tracked_container import TrackedContainer

def test_startup_no_errors(container: TrackedContainer):
    """验证容器启动日志中无ERROR"""
    container.run_detached()
    time.sleep(8)  # 等待Jupyter完全启动
    logs = container.get_logs()
    errors = TrackedContainer.get_errors(logs)
    # 过滤掉已知的非关键error
    real_errors = [e for e in errors if "permission denied" not in e.lower()]
    assert len(real_errors) == 0, f"Startup errors: {real_errors}"

def test_jupyter_url_in_logs(container: TrackedContainer):
    """验证日志中包含Jupyter访问URL"""
    container.run_detached()
    time.sleep(8)
    logs = container.get_logs()
    assert "http://127.0.0.1:8888" in logs or "token=" in logs

def test_jupyter_started(container: TrackedContainer):
    """验证Jupyter Server已启动"""
    container.run_detached()
    time.sleep(8)
    logs = container.get_logs()
    assert "Jupyter Server" in logs or "jupyterlab" in logs.lower()
```

## 测试模式5：使用run_and_wait验证一次性命令

```python
# tests/test_commands.py
from tests.utils.tracked_container import TrackedContainer

def test_pip_list(container: TrackedContainer):
    """验证pip list可以执行且无错误"""
    logs = container.run_and_wait(
        timeout=30,
        command="pip list",
        remove=False  # 不自动删除容器（因为run_and_wait内部会remove）
    )
    # run_and_wait已经自动remove了，所以这里不用再清理
    assert "Package" in logs  # pip list输出包含"Package"表头

def test_python_hello_world(container: TrackedContainer):
    """验证Python可以运行简单脚本"""
    logs = container.run_and_wait(
        timeout=10,
        command='python -c "print(\"Hello from Jupyter container!\")"'
    )
    assert "Hello from Jupyter container!" in logs
```

## 测试模式6：卷挂载测试

```python
# tests/test_volumes.py
import os
import tempfile
from tests.utils.tracked_container import TrackedContainer

def test_workspace_mount(container: TrackedContainer):
    """验证工作目录挂载后可读写"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 在主机临时目录创建测试文件
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("hello from host")

        container.run_detached(
            volumes={tmpdir: {"bind": "/home/jovyan/work/test", "mode": "rw"}}
        )
        # 在容器内读取文件
        output = container.exec_cmd("cat /home/jovyan/work/test/test.txt")
        assert "hello from host" in output
```

## 测试模式7：自定义配置验证

```python
# tests/test_custom_config.py
import requests
from tests.utils.tracked_container import TrackedContainer

def test_custom_jupyter_config(
    container: TrackedContainer,
    http_client: requests.Session,
    free_host_port: int,
    tmp_path
):
    """验证自定义Jupyter配置生效"""
    # 创建自定义配置
    config_file = tmp_path / "jupyter_server_config.py"
    config_file.write_text("""
c = get_config()
c.ServerApp.max_buffer_size = 536870912  # 512MB
c.ServerApp.disable_check_xsrf = False
""")

    container.run_detached(
        ports={"8888/tcp": free_host_port},
        volumes={
            str(config_file): {
                "bind": "/etc/jupyter/jupyter_server_config.py",
                "mode": "ro"
            }
        },
        environment={"JUPYTER_TOKEN": "test"}
    )

    import time
    time.sleep(5)

    # 验证服务器正常启动（配置正确加载）
    resp = http_client.get(
        f"http://localhost:{free_host_port}/api",
        headers={"Authorization": "token test"}
    )
    assert resp.status_code == 200
```

## pytest 标记（Markers）

使用pytest标记分类测试：

```python
# tests/conftest.py（追加自定义markers）
# 在pytest.ini中添加markers配置
```

编辑 `pytest.ini`：

```ini
[pytest]
addopts = -ra --color=yes
log_cli = 1
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)
log_cli_date_format=%Y-%m-%d %H:%M:%S
markers =
    info: marks tests as info (deselect with '-m "not info"')
    gpu: marks tests that require GPU
    slow: marks tests that are slow to run
```

使用标记运行测试：

```bash
# 只运行快速测试（排除GPU和慢测试）
TEST_IMAGE=my-image pytest tests/ -v -m "not gpu and not slow"

# 只运行GPU测试
TEST_IMAGE=my-image pytest tests/ -v -m gpu

# 只运行包导入测试
TEST_IMAGE=my-image pytest tests/ -v -k "test_package"
```

## 测试最佳实践

| 实践 | 说明 |
|------|------|
| 每个测试独立创建容器 | 使用function级container fixture保证隔离 |
| 添加适当的等待时间 | Jupyter启动需要5-10秒，使用`time.sleep()`或重试 |
| 使用参数化测试 | `@pytest.mark.parametrize` 批量验证多个包 |
| 验证非关键错误 | 过滤已知的无害ERROR，避免测试误报 |
| 使用标记分类测试 | `@pytest.mark.gpu`/`@pytest.mark.slow` 按需运行 |
| 测试后自动清理 | TrackedContainer在fixture teardown时自动remove |
| 测试UID/GID | 验证容器以jovyan（UID 1000）而非root运行 |
| 验证包版本 | `import xxx; print(xxx.__version__)` 确认版本正确 |

## 相关示例

- [创建自定义数据科学镜像](01-basic-custom-image.md)
- [GPU/CUDA深度学习镜像](02-gpu-image.md)

## 相关概念

- [测试框架详解](/concepts/05-testing-framework.md)
- [Dockerfile模板与编写指南](/concepts/04-dockerfile-template.md)
- [最佳实践](/concepts/09-best-practices.md)
