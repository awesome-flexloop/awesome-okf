---
type: Reference
title: "测试框架源码索引"
description: "cookiecutter-docker-stacks 测试框架源码信源登记（TrackedContainer、pytest fixtures）"
tags: [testing, pytest, docker, trackcontainer, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-conftest, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/tests/conftest.py", title: "tests/conftest.py" }
  - { id: src-test-notebook, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/tests/test_notebook.py", title: "tests/test_notebook.py" }
  - { id: src-tracked, resource: "external/libs/jupyter/cookiecutter-docker-stacks/{{cookiecutter.stack_name}}/tests/utils/tracked_container.py", title: "tests/utils/tracked_container.py" }
  - { id: src-pytest-ini, resource: "external/libs/jupyter/cookiecutter-docker-stacks/pytest.ini", title: "pytest.ini" }
  - { id: src-mypy-ini, resource: "external/libs/jupyter/cookiecutter-docker-stacks/mypy.ini", title: "mypy.ini" }
  - { id: src-flake8, resource: "external/libs/jupyter/cookiecutter-docker-stacks/.flake8", title: ".flake8" }
---

# 测试框架源码索引

本文档登记 cookiecutter-docker-stacks 测试框架的源码路径、类/方法签名与关键行为。

## TrackedContainer 类

**文件**：[tests/utils/tracked_container.py](external/libs/jupyter/cookiecutter-docker-stacks/%7B%7Bcookiecutter.stack_name%7D%7D/tests/utils/tracked_container.py)

### 类签名

```python
class TrackedContainer:
    def __init__(self, docker_client: docker.DockerClient, image_name: str): ...
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| container | Container \| None | Docker容器实例，初始为None |
| docker_client | docker.DockerClient | Docker客户端实例 |
| image_name | str | 要启动的镜像名称 |

### 方法

| 方法 | 签名 | 说明 |
|------|------|------|
| run_detached | `(self, **kwargs: Any) -> None` | 后台运行容器，默认detach=True、tty=True |
| get_logs | `(self) -> str` | 获取容器日志（decode后字符串） |
| get_health | `(self) -> str` | reload容器后返回health状态 |
| exec_cmd | `(self, cmd: str, **kwargs: Any) -> str` | 在容器内执行命令，失败抛AssertionError |
| run_and_wait | `(self, timeout: int, no_warnings=True, no_errors=True, no_failure=True, **kwargs) -> str` | 运行容器并等待退出，检查退出码和日志警告/错误 |
| remove | `(self) -> None` | 强制删除容器并重置container为None |

### 静态方法

| 方法 | 签名 | 说明 |
|------|------|------|
| get_errors | `(logs: str) -> list[str]` | 返回以"ERROR"开头的日志行 |
| get_warnings | `(logs: str) -> list[str]` | 返回以"WARNING"开头的日志行 |
| _lines_starting_with | `(logs: str, pattern: str) -> list[str]` | 内部方法：提取以指定模式开头的行 |

### run_detached 默认参数

```python
default_kwargs = {"detach": True, "tty": True}
```

### run_and_wait 断言逻辑

1. 调用 `run_detached(**kwargs)` 启动容器
2. `container.wait(timeout=timeout)` 等待退出
3. 获取日志后检查：退出码为0（rc_success）、日志无ERROR/WARNING（可通过参数关闭）
4. 调用 `self.remove()` 清理容器
5. 通过 `assert` 语句分别断言三个条件

## pytest Fixtures

**文件**：[tests/conftest.py](external/libs/jupyter/cookiecutter-docker-stacks/%7B%7Bcookiecutter.stack_name%7D%7D/tests/conftest.py)

| Fixture | Scope | 返回类型 | 说明 |
|---------|-------|---------|------|
| http_client | session | requests.Session | 带重试机制的HTTP会话（total=5, backoff_factor=1） |
| docker_client | session | docker.DockerClient | 从环境变量创建的Docker客户端 |
| image_name | session | str | 从环境变量TEST_IMAGE读取镜像名 |
| container | function | TrackedContainer | 创建TrackedContainer实例，yield后自动remove |
| free_host_port | function | int | 通过绑定端口0查找空闲主机端口 |

### http_client 重试配置

```python
retries = Retry(total=5, backoff_factor=1)
# 同时挂载到 http:// 和 https://
```

### free_host_port 实现

```python
with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
    s.bind(("", 0))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    yield s.getsockname()[1]
```

## 默认测试用例

**文件**：[tests/test_notebook.py](external/libs/jupyter/cookiecutter-docker-stacks/%7B%7Bcookiecutter.stack_name%7D%7D/tests/test_notebook.py)

### test_secured_server

```python
def test_secured_server(
    container: TrackedContainer,
    http_client: requests.Session,
    free_host_port: int
) -> None:
```

**行为**：
1. 容器后台运行，映射8888端口到free_host_port
2. HTTP GET请求 `http://localhost:{free_host_port}`
3. 断言响应状态码200（raise_for_status）
4. 断言响应HTML中包含 "login_submit"（Jupyter登录页面）

## 测试配置文件

### pytest.ini

```ini
[pytest]
addopts = -ra --color=yes
log_cli = 1
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)
log_cli_date_format=%Y-%m-%d %H:%M:%S
markers = info: marks tests as info
```

### mypy.ini

- python_version = 3.12
- strict = True
- follow_imports = error
- disallow_untyped_decorators = False
- 忽略 `docker.*` 包的类型检查

### .flake8

- max-line-length = 88
- select = C, E, F, W, B, B950
- extend-ignore = E203, E501, W503
