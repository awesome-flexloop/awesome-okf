---
type: concept
scope: omlmd
name: registry
version: "0.1.6"
source: https://github.com/containers/omlmd/blob/main/omlmd/provider.py
description: OMLMDRegistry 扩展 oras-py 的实现机制
---

# OMLMDRegistry 扩展 oras-py

`OMLMDRegistry` 继承自 `oras.provider.Registry`，是 omlmd 对 oras-py 库的扩展，添加了按媒体类型过滤下载层和获取配置层的能力。

## oras-py 简介

oras-py 是 OCI Registry As Storage（ORAS）项目的 Python 实现，提供了将任意内容推送到 OCI 兼容注册表的能力。OMLMD 基于 oras-py 构建，专注于 ML 模型场景的扩展。

oras-py 的核心类：
- `oras.provider.Registry`：基础注册表客户端，提供 push、pull、get_manifest、download_blob 等方法
- `oras.decorator.ensure_container`：装饰器，自动解析容器引用

## OMLMDRegistry 类定义

```python
from oras import provider
from oras.decorator import ensure_container
from oras.defaults import annotation_title as ANNOTATION_TITLE
from oras.utils import sanitize_path

class OMLMDRegistry(provider.Registry):
```

OMLMDRegistry 直接继承 `provider.Registry`，复用其所有基础能力（认证、manifest 获取、blob 上传下载等），仅重写和添加两个方法。

## @ensure_container 装饰器

两个核心方法都使用了 `@ensure_container` 装饰器：

```python
@ensure_container
def download_layers(self, package, download_dir, media_types):
    ...

@ensure_container
def get_config(self, package) -> str:
    ...
```

该装饰器的作用是自动解析和规范化容器引用字符串，将 `package` 参数转换为内部的容器对象，确保后续操作可以正确访问注册表。

## download_layers() 方法

按媒体类型过滤下载层，是 `pull()` 操作的核心实现。

### 方法签名

```python
@ensure_container
def download_layers(self, package, download_dir, media_types):
```

**参数说明**：
- `package`：OCI 镜像引用（被 `@ensure_container` 自动解析）
- `download_dir`：本地下载目录
- `media_types`：媒体类型过滤列表，为 `None` 或空列表时下载所有层

### 实现逻辑

```python
def download_layers(self, package, download_dir, media_types):
    manifest = self.get_manifest(package)

    paths = []

    for layer in manifest.get("layers", []):
        if (
            media_types is None
            or len(media_types) == 0
            or layer["mediaType"] in media_types
        ):
            artifact = layer["annotations"][ANNOTATION_TITLE]
            outfile = sanitize_path(
                download_dir, os.path.join(download_dir, artifact)
            )
            path = self.download_blob(package, layer["digest"], outfile)
            paths.append(path)

    return paths
```

### 工作流程

```
1. 获取 OCI Manifest
2. 遍历 manifest.layers 数组
3. 对每个 layer 检查 mediaType：
   ├─ media_types 为 None/空 → 下载
   ├─ layer.mediaType 在 media_types 中 → 下载
   └─ 否则 → 跳过
4. 从 layer.annotations 获取原始文件名（使用 ANNOTATION_TITLE 即 "org.opencontainers.image.title"）
5. 使用 sanitize_path() 确保路径安全（防止路径遍历攻击）
6. 调用 download_blob() 下载 blob 到本地
7. 返回下载成功的文件路径列表
```

### 媒体类型过滤的使用场景

| media_types 值 | 行为 | 用途 |
|---|---|---|
| `None` 或 `[]` | 下载所有层 | 完整拉取模型和元数据 |
| `["application/x-mlmodel"]` | 仅下载模型层 | 推理时只需要模型文件 |
| `["application/x-config"]` | 仅下载元数据层 | 浏览模型信息无需下载权重 |

### 路径安全

使用 `oras.utils.sanitize_path()` 处理输出路径，防止恶意构造的注解文件名导致路径遍历攻击（如 `../../etc/passwd`）。

## get_config() 方法

获取 Artifact 的配置层内容，用于元数据查询和爬取。

### 方法签名

```python
@ensure_container
def get_config(self, package) -> str:
```

**返回值**：配置层的文件内容（JSON 字符串）

### 实现逻辑

```python
@ensure_container
def get_config(self, package) -> str:
    manifest = self.get_manifest(package)

    manifest_config = manifest.get("config", {})

    for layer in manifest.get("layers", []):
        if layer["digest"] == manifest_config["digest"]:
            temp_dir = tempfile.mkdtemp()
            try:
                with tempfile.NamedTemporaryFile(
                    dir=temp_dir, delete=False
                ) as temp_file:
                    self.download_blob(package, layer["digest"], temp_file.name)
                with open(temp_file.name, "r") as temp_file_read:
                    file_content = temp_file_read.read()
                    return file_content
            finally:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir, topdown=False):
                        for file in files:
                            os.remove(os.path.join(root, file))
                        for dir in dirs:
                            os.rmdir(os.path.join(root, dir))
                    os.rmdir(temp_dir)
    raise RuntimeError("Unable to locate config layer")
```

### 工作流程

```
1. 获取 OCI Manifest
2. 从 manifest.config 获取配置层的 digest
3. 在 manifest.layers 中查找匹配该 digest 的层
   （注意：config 引用也会出现在 layers 数组中）
4. 创建临时目录
5. 在临时目录中创建临时文件
6. 下载 blob 到临时文件
7. 读取临时文件内容
8. finally 块：递归删除临时目录及其所有内容
9. 如果未找到配置层，抛出 RuntimeError
```

### 临时文件管理

使用 `tempfile.mkdtemp()` 创建独立临时目录，配合 `try-finally` 确保：
- 无论成功失败，临时文件都会被清理
- 使用 `topdown=False` 遍历删除，先删文件再删目录
- 不依赖操作系统的临时文件自动清理机制

### 为什么使用临时文件？

`download_blob()` 方法设计为写入文件而非返回内存内容，原因：
1. 模型文件可能非常大（GB 级），无法全部加载到内存
2. 统一的 API 设计，大文件小文件处理方式一致
3. 元数据配置层通常很小（KB 级），临时文件开销可以忽略

## 继承的 oras-py 能力

OMLMDRegistry 从 `provider.Registry` 继承了以下核心能力（在 push 流程中使用）：

| 方法 | 用途 |
|---|---|
| `get_manifest()` | 获取 OCI Manifest JSON |
| `download_blob()` | 下载指定 digest 的 blob |
| `push()` | 上传文件集合（Helper.push() 内部调用） |
| `upload_blob()` | 上传单个 blob |

## OCI Manifest 结构理解

download_layers 和 get_config 的实现都基于对 OCI Manifest 结构的理解。一个典型的 OMLMD Manifest 结构如下：

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/x-config",
    "digest": "sha256:abc123...",
    "size": 1234
  },
  "layers": [
    {
      "mediaType": "application/x-mlmodel",
      "digest": "sha256:def456...",
      "size": 1000000,
      "annotations": {
        "org.opencontainers.image.title": "model.joblib"
      }
    },
    {
      "mediaType": "application/x-config",
      "digest": "sha256:abc123...",
      "size": 1234,
      "annotations": {
        "org.opencontainers.image.title": "model_metadata.omlmd.json"
      }
    },
    {
      "mediaType": "application/x-config",
      "digest": "sha256:ghi789...",
      "size": 1300,
      "annotations": {
        "org.opencontainers.image.title": "model_metadata.omlmd.yaml"
      }
    }
  ],
  "annotations": {
    "name": "My Model",
    "author": "John Doe",
    "customProperties+json": "{\"accuracy\":0.95}"
  }
}
```

关键点：
- `config` 字段指向主元数据层（JSON 格式）
- `layers` 数组包含所有层，**也包括 config 指向的层**
- 每个 layer 有 `mediaType`、`digest`、`size`、`annotations`
- 文件名通过 `org.opencontainers.image.title` 注解存储
- Manifest 顶层也可以有 annotations 存储元数据摘要
