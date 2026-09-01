---
type: reference
scope: omlmd
name: provider-source
version: "0.1.6"
source: https://github.com/containers/omlmd/blob/main/omlmd/provider.py
description: OMLMDRegistry 类源码参考
---

# OMLMDRegistry 源码参考

`OMLMDRegistry` 继承自 `oras.provider.Registry`，扩展了 oras-py 以支持 ML 模型层的过滤下载和配置层获取。

## 类定义

```python
from __future__ import annotations

import logging
import os
import tempfile

from oras import provider
from oras.decorator import ensure_container
from oras.defaults import annotation_title as ANNOTATION_TITLE
from oras.utils import sanitize_path

logger = logging.getLogger(__name__)


class OMLMDRegistry(provider.Registry):
```

## download_layers()

根据 media_types 过滤下载层：

```python
@ensure_container
def download_layers(self, package, download_dir, media_types):
    """
    Given a manifest of layers, retrieve a layer based on desired media type
    """
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

**参数说明**：
- `package`：OCI 镜像引用（如 `localhost:8080/matteo/ml-artifact:latest`）
- `download_dir`：下载目标目录
- `media_types`：媒体类型过滤列表，为 None 或空列表时下载所有层

**支持的媒体类型**：
- `application/x-mlmodel`：ML 模型文件
- `application/x-config`：元数据配置文件（JSON/YAML）

## get_config()

获取配置层内容，使用临时目录处理：

```python
@ensure_container
def get_config(self, package) -> str:
    """
    Given a manifest of layers, retrieve a layer based on desired media type
    """
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

**返回值**：配置层的 JSON 字符串内容

**工作流程**：
1. 获取 manifest
2. 找到 config 层对应的 digest
3. 在 layers 中匹配该 digest
4. 使用临时目录下载 blob
5. 读取文件内容并返回
6. 自动清理临时目录
