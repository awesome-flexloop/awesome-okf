---
type: Concept
title: 读取器与执行器扩展
description: Notebook读取器和执行器的工作原理、内置实现以及如何通过entry points开发自定义扩展
tags: [jupyter, cache, reader, executor, plugin, entry-points, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:46:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# 读取器与执行器扩展

jupyter-cache 设计为可扩展架构，通过 setuptools entry points 支持自定义读取器和执行器。

## 读取器（Readers）

### 读取器的作用

读取器负责将 URI（通常是文件路径）转换为内存中的 Notebook 对象（nbformat）。不同读取器支持不同的Notebook来源。

### 内置读取器：filesystem

默认读取器从本地文件系统读取 `.ipynb` 文件：

```python
# read_data 配置
read_data = {"name": "filesystem"}
```

工作流程：
1. 将URI视为本地文件路径
2. 使用 `nbformat.read()` 读取 `.ipynb` JSON
3. 返回nbformat.NotebookNode对象

### 读取器接口

读取器是一个可调用对象，签名为：

```python
def my_reader(uri: str, read_data: dict) -> nbformat.NotebookNode:
    """
    从URI读取Notebook。

    :param uri: Notebook标识符（路径、URL、ID等）
    :param read_data: 读取配置字典，必须包含'name'字段
    :return: NotebookNode对象（nbformat v4+）
    :raises NbReadError: 读取失败时
    """
```

### 开发自定义读取器

示例：从S3读取Notebook

```python
# my_s3_reader.py
import nbformat
from jupyter_cache.readers import NbReadError

def read_from_s3(uri, read_data):
    """从S3读取Notebook。

    read_data 需包含:
        name: "s3"
        bucket: S3桶名
        aws_access_key_id: (可选) AWS凭证
        aws_secret_access_key: (可选) AWS凭证
    """
    try:
        import boto3
    except ImportError:
        raise NbReadError("boto3 is required for S3 reader")

    bucket = read_data.get("bucket")
    if not bucket:
        raise NbReadError("bucket is required for S3 reader")

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=uri)
    content = response["Body"].read()
    return nbformat.reads(content, as_version=4)
```

注册entry point（`pyproject.toml`）：

```toml
[project.entry-points."jupyter_cache.readers"]
s3 = "my_s3_reader:read_from_s3"
```

安装后使用：

```python
cache.add_notebook_file(
    "notebooks/analysis.ipynb",
    read_data={"name": "s3", "bucket": "my-notebooks"}
)
```

## 执行器（Executors）

### 执行器的作用

执行器负责运行 Notebook 代码单元格并捕获输出。不同执行器适用于不同的执行环境。

### 内置执行器：BasicExecutor

`jupyter_cache.executors.basic.BasicExecutor` 使用 jupyter_client 在本地启动 Kernel 执行：

特点：
- 使用本地Jupyter Kernel
- 支持超时控制
- 捕获stdout/stderr/display_data/error
- 识别输出中的文件产物
- 逐单元格顺序执行

### 执行器接口

执行器继承自 `Executor` 基类：

```python
from jupyter_cache.executors.base import Executor
from jupyter_cache.cache.main import NbArtifacts

class MyExecutor(Executor):
    name = "my-executor"

    def execute(self, nb, uri, exec_data=None):
        """执行Notebook。

        :param nb: NotebookNode对象
        :param uri: Notebook标识符
        :param exec_data: 执行配置字典
        :return: (执行后的NotebookNode, NbArtifacts)
        """
        # ... 执行逻辑 ...
        return executed_nb, NbArtifacts([], "/tmp")
```

### 开发自定义执行器

示例：在Docker容器中执行Notebook

```python
# docker_executor.py
import nbformat
import docker
from jupyter_cache.executors.base import Executor
from jupyter_cache.cache.main import NbArtifacts
import tempfile, os

class DockerExecutor(Executor):
    name = "docker"

    def execute(self, nb, uri, exec_data=None):
        exec_data = exec_data or {}
        image = exec_data.get("image", "jupyter/scipy-notebook:latest")
        timeout = exec_data.get("timeout", 600)

        # 将Notebook写入临时文件
        with tempfile.TemporaryDirectory() as tmpdir:
            nb_path = os.path.join(tmpdir, "notebook.ipynb")
            nbformat.write(nb, nb_path)

            # 使用Docker执行
            client = docker.from_env()
            container = client.containers.run(
                image,
                command=f"jupyter nbconvert --to notebook --execute --inplace notebook.ipynb",
                volumes={tmpdir: {"bind": "/home/jovyan/work", "mode": "rw"}},
                working_dir="/home/jovyan/work",
                detach=True,
            )
            container.wait(timeout=timeout)

            # 读取执行结果
            executed_nb = nbformat.read(nb_path, as_version=4)

            # 收集产物
            artifacts = NbArtifacts([], tmpdir)

            return executed_nb, artifacts
```

注册entry point：

```toml
[project.entry-points."jupyter_cache.executors"]
docker = "docker_executor:DockerExecutor"
```

使用：

```python
cache.execute_all_notebooks(
    executor="docker",
    exec_data={"image": "jupyter/scipy-notebook:latest", "timeout": 600}
)
```

## get_reader 工厂函数

`readers.py` 中的 `get_reader()` 函数根据 name 查找已注册的读取器：

```python
from jupyter_cache.readers import get_reader, DEFAULT_READ_DATA

# 默认读取器配置
print(DEFAULT_READ_DATA)  # {"name": "filesystem"}

# 获取指定名称的读取器
reader_func = get_reader("s3")
```

查找顺序：
1. 在内置读取器中查找
2. 通过 entry points 在已安装包中查找
3. 未找到则抛出异常

## Entry Points 发现机制

jupyter-cache 使用 `importlib.metadata.entry_points()`（或 `pkg_resources`）发现已安装包中注册的插件：

- 插件包安装后自动可用，无需手动配置
- 多个包可以注册同名扩展点的不同实现
- 通过name区分不同实现

## 选择合适的读取器和执行器

| 场景 | 推荐读取器 | 推荐执行器 |
|------|-----------|-----------|
| 本地开发 | filesystem | basic |
| CI/CD流水线 | filesystem | basic 或 docker |
| 云端Notebook | s3/gcs | 远程kernel执行器 |
| 多语言Notebook | filesystem | 对应语言kernel执行器 |

## 相关概念

- [Notebook执行与插件](/concepts/04-notebook-execution.md)
- [缓存API详解](/concepts/03-cache-api.md)
- [配置项参考](/concepts/07-configuration.md)
- [Python API示例](/examples/python-api.md)
