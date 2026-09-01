---
type: Concept
title: 后端抽象层（skopeo/oras）
description: 了解 olot 支持的三种后端实现，如何选择合适的后端，以及后端 API 的使用方式
tags: [backend, skopeo, oras, oras-py, pull, push]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /bundles/containers/olot/references/readme-source.md
    title: "olot 项目 README 信源"
  - id: backend-source
    resource: /bundles/containers/olot/references/backend-source.md
    title: "olot 后端抽象层源码信源"
---

# 后端抽象层（skopeo/oras）

olot 的核心功能（添加层）是纯 Python 实现，不依赖外部工具。但拉取（pull）和推送（push）镜像到/从远程 registry 需要后端支持。olot 提供了三种后端实现，适应不同的运行环境。

## 后端对比

| 后端 | 类型 | 依赖 | 优点 | 缺点 |
|------|------|------|------|------|
| **skopeo** | 外部 CLI | 需要系统安装 skopeo 命令 | 成熟稳定、多架构支持好、社区广泛使用 | 需要额外安装二进制工具 |
| **oras cp** | 外部 CLI | 需要系统安装 oras 命令 | OCI 原生、专为 OCI artifact 设计 | 功能相对较新，生态较小 |
| **oras-py** | Python 库 | `pip install olot[oras-py]` | 纯 Python、无外部依赖、易于嵌入 | 性能可能略低于 CLI 工具 |

## 安装对应依赖

### skopeo 后端

skopeo 是系统级工具，需要单独安装：

```bash
# Ubuntu/Debian
sudo apt-get install skopeo

# RHEL/CentOS
sudo dnf install skopeo

# macOS
brew install skopeo
```

不需要安装额外的 Python 包，olot 默认支持 skopeo。

### oras cp 后端

oras CLI 工具需要单独安装：

```bash
# 参考 oras 官方文档安装
# https://oras.land/docs/installation
```

### oras-py 后端（纯 Python）

安装可选的 Python 依赖：

```bash
pip install olot[oras-py]
# 或者使用 uv
uv add olot[oras-py]
```

这会安装 `oras >= 0.2.42` Python 包，不需要任何外部 CLI 工具。

## skopeo 后端 API

所有 skopeo 后端函数位于 `olot.backend.skopeo` 模块。

### is_skopeo()

检查系统中是否可用 skopeo 命令。

```python
from olot.backend.skopeo import is_skopeo

if is_skopeo():
    print("skopeo 可用")
else:
    print("请先安装 skopeo")
```

### skopeo_pull()

从远程 registry 拉取镜像到本地 OCI layout 目录。

**函数签名：**
```python
def skopeo_pull(
    base_image: str,
    dest: str | os.PathLike,
    params: typing.Sequence[str] = ()
) -> None
```

**参数：**
- `base_image`：远程镜像引用，如 `quay.io/mmortari/hello-world-wait:latest`
- `dest`：本地 OCI layout 目录路径
- `params`：额外传递给 skopeo 命令的参数列表

**示例：**
```python
from olot.backend.skopeo import skopeo_pull

skopeo_pull(
    "quay.io/mmortari/hello-world-wait:latest",
    "./download",
    params=["--multi-arch", "all"]
)
```

### skopeo_push()

将本地 OCI layout 目录中的镜像推送到远程 registry。

**函数签名：**
```python
def skopeo_push(
    src: str | os.PathLike,
    oci_ref: str,
    params: typing.Sequence[str] = ()
) -> None
```

**参数：**
- `src`：本地 OCI layout 目录路径
- `oci_ref`：远程镜像引用目标
- `params`：额外传递给 skopeo 命令的参数列表

**示例：**
```python
from olot.backend.skopeo import skopeo_push

skopeo_push(
    "./download",
    "quay.io/myuser/my-model:v1",
    params=["--multi-arch", "all"]
)
```

### skopeo_inspect()

检查远程或本地镜像的元数据，返回原始 JSON 字符串。

```python
from olot.backend.skopeo import skopeo_inspect
import json

result = skopeo_inspect("docker://quay.io/mmortari/hello-world-wait:latest")
metadata = json.loads(result)
print(metadata["Name"])
```

## oras-py 后端 API

所有 oras-py 后端函数位于 `olot.backend.oras_py` 模块。这是纯 Python 实现，不需要外部工具。

### is_oras_py()

检查 oras Python 库是否已安装。

```python
from olot.backend.oras_py import is_oras_py

if not is_oras_py():
    print("请运行: pip install olot[oras-py]")
```

### oras_py_pull()

使用纯 Python 从远程 registry 拉取镜像。

**函数签名：**
```python
def oras_py_pull(
    base_image: str,
    dest: str | os.PathLike,
    *,
    insecure: bool = False,
    tls_verify: bool = True
) -> None
```

**参数：**
- `base_image`：远程镜像引用
- `dest`：本地 OCI layout 目录
- `insecure`：是否允许不安全连接（HTTP）
- `tls_verify`：是否验证 TLS 证书

**示例：**
```python
from olot.backend.oras_py import oras_py_pull

oras_py_pull(
    "quay.io/mmortari/hello-world-wait:latest",
    "./download"
)
```

### oras_py_push()

使用纯 Python 推送镜像到远程 registry。

**函数签名：**
```python
def oras_py_push(
    src: str | os.PathLike,
    oci_ref: str,
    *,
    insecure: bool = False,
    tls_verify: bool = True
) -> None
```

**示例：**
```python
from olot.backend.oras_py import oras_py_push

oras_py_push(
    "./download",
    "quay.io/myuser/my-model:v1"
)
```

## oras cp 后端 API

`olot.backend.oras_cp` 模块提供与 skopeo 类似的 API，底层调用 `oras cp` 命令。

函数包括：
- `is_oras_cp()`：检查 oras 命令是否可用
- `oras_cp_pull()`：使用 oras cp 拉取镜像
- `oras_cp_push()`：使用 oras cp 推送镜像

> **注意**：使用 oras cp 拉取后，可能需要添加写权限：
> ```bash
> chmod +w ${IMAGE_DIR}/blobs/sha256/*
> ```

## 如何选择后端

| 场景 | 推荐后端 |
|------|---------|
| 已有 skopeo 环境，CI/CD 中使用 | skopeo |
| 需要纯 Python 环境，无系统依赖 | oras-py |
| 使用 oras 生态系统工具链 | oras cp |
| 需要 HTTP 不安全 registry | oras-py（设置 insecure=True）|
| 生产环境，稳定优先 | skopeo |

## 后端检测辅助函数

可以编写简单的检测逻辑自动选择可用的后端：

```python
from olot.backend.skopeo import is_skopeo
from olot.backend.oras_py import is_oras_py

def get_available_backend():
    if is_skopeo():
        from olot.backend.skopeo import skopeo_pull, skopeo_push
        return "skopeo", skopeo_pull, skopeo_push
    elif is_oras_py():
        from olot.backend.oras_py import oras_py_pull, oras_py_push
        return "oras-py", oras_py_pull, oras_py_push
    else:
        raise RuntimeError(
            "No backend available. "
            "Please install skopeo or run: pip install olot[oras-py]"
        )

backend_name, pull, push = get_available_backend()
print(f"Using backend: {backend_name}")
```

## 相关概念

- [Python API 编程](03-python-api.md)：完整的 Python API 使用流程
- [Python API 打包模型](../examples/02-python-api.md)：端到端 Python 示例
- [命令行基本使用](../examples/01-cli-usage.md)：CLI 使用 skopeo 工作流
