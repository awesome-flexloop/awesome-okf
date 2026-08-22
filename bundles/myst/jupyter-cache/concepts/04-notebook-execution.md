---
type: Concept
title: Notebook执行与插件体系
description: jupyter-cache的执行器插件体系、BasicExecutor实现、自定义执行器和读取器的扩展方式
tags: [jupyter, cache, executor, plugin, kernel, execution, entry-points]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:42:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# Notebook执行与插件体系

## 执行器抽象

jupyter-cache 的执行器（Executor）是可插拔的Notebook执行引擎，负责将代码单元格实际运行并填充输出。

### Executor 基类

`executors/base.py` 定义抽象基类，规定执行器接口：

```python
class Executor:
    """Notebook执行器抽象基类"""

    def execute(self, nb, uri, exec_data):
        """执行Notebook，返回执行后的Notebook和产物列表"""
        raise NotImplementedError
```

执行器接收：
- `nb`：Notebook节点（nbformat对象）
- `uri`：Notebook标识符
- `exec_data`：执行配置（超时、kernel等）

返回执行后的Notebook和NbArtifacts产物集合。

## BasicExecutor（默认执行器）

`executors/basic.py` 提供默认执行器，基于 `jupyter_client` 在本地Kernel中执行：

### 执行流程

1. **启动Kernel**：根据Notebook metadata中的kernel信息启动Jupyter Kernel
2. **逐Cell执行**：按顺序执行每个code单元格
3. **捕获输出**：收集stdout/stderr/display_data/error
4. **处理产物**：识别输出中的文件引用作为artifacts
5. **关闭Kernel**：执行完成后关闭Kernel连接

### 执行配置

通过 `exec_data` 可配置：
- `timeout`：单个单元格执行超时（秒）
- `kernel_name`：指定Kernel名称
- `allow_errors`：是否允许错误继续执行

```python
cache.execute_all_notebooks(
    exec_data={"timeout": 120, "allow_errors": False}
)
```

## 读取器体系

读取器（Reader）负责从不同来源加载Notebook内容。

### 默认读取器：filesystem

默认读取器从本地文件系统读取 `.ipynb` 文件，`read_data` 配置：

```python
{"name": "filesystem"}
```

### 读取器接口

```python
def read_notebook(uri, read_data):
    """根据URI和read_data配置读取Notebook，返回nbformat对象"""
    ...
```

读取器可从以下来源加载Notebook：
- 本地文件系统（默认）
- 远程URL
- 数据库
- 内存对象

## Entry Points 插件扩展

jupyter-cache 通过 setuptools entry points 支持第三方插件扩展。

### 三个扩展点

| Entry Point 组 | 用途 | 接口类 |
|----------------|------|--------|
| `jupyter_cache.executors` | Notebook执行引擎 | `Executor` |
| `jupyter_cache.readers` | Notebook读取来源 | Reader函数 |
| `jupyter_cache.converters` | Notebook格式转换 | Converter |

### 开发自定义执行器

1. 创建Python包，实现Executor子类：

```python
from jupyter_cache.executors.base import Executor
from jupyter_cache.cache.main import NbArtifacts

class DockerExecutor(Executor):
    name = "docker"

    def execute(self, nb, uri, exec_data):
        # 在Docker容器中执行Notebook
        image = exec_data.get("image", "jupyter/scipy-notebook")
        # ... Docker执行逻辑 ...
        return executed_nb, NbArtifacts([], "/tmp")
```

2. 在 `setup.py` 或 `pyproject.toml` 中注册：

```toml
[project.entry-points."jupyter_cache.executors"]
docker = "my_package:DockerExecutor"
```

3. 安装后即可使用：

```python
cache.execute_all_notebooks(
    executor="docker",
    exec_data={"image": "my-custom-image"}
)
```

### 开发自定义读取器

```python
def read_from_s3(uri, read_data):
    """从S3读取Notebook"""
    import boto3
    s3 = boto3.client("s3")
    bucket = read_data["bucket"]
    key = uri
    response = s3.get_object(Bucket=bucket, Key=key)
    import nbformat
    return nbformat.reads(response["Body"].read(), as_version=4)
```

```toml
[project.entry-points."jupyter_cache.readers"]
s3 = "my_package:read_from_s3"
```

## 执行错误处理

执行失败时：
1. traceback存储在 `NbProjectRecord.traceback` 字段
2. 该Notebook不会被添加到缓存
3. CLI显示❌状态标识
4. 修复后可通过 `jcache notebook execute-all` 重试（需先清除traceback）

```python
# 清除错误状态
cache.remove_tracebacks(pks=[1])
# 重新执行
cache.execute_all_notebooks()
```

## 相关概念

- [缓存架构设计](/concepts/02-architecture.md)
- [缓存API详解](/concepts/03-cache-api.md)
- [配置项参考](/concepts/07-configuration.md)
- [Python API示例](/examples/python-api.md)
