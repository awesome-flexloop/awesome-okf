---
type: Reference
title: olot OCI 模块源码信源
description: olot 项目 OCI 相关模块源码，包含 OCI layout 操作、镜像清单、层注解等核心实现
tags: [oci, source-code, layers, manifest]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:source-verification"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: basics
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/basics.py"
    title: "olot/basics.py - 核心层操作逻辑"
  - id: constants
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/constants.py"
    title: "olot/constants.py - 层注解常量定义"
  - id: oci-common
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/oci/oci_common.py"
    title: "olot/oci/oci_common.py - OCI MediaType 定义"
---

# olot OCI 模块源码信源

## 核心函数签名

### oci_layers_on_top()

位置：`olot/basics.py:53-289`

```python
def oci_layers_on_top(
        ocilayout: str | os.PathLike,
        model_files: Sequence[os.PathLike],
        modelcard: os.PathLike | None = None,
        *,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        root_dir: str | os.PathLike | None = None,
        remove_originals: RemoveOriginals | None = None,
        add_modelpack: bool | None = None):
```

## 四元组层注解键

位置：`olot/constants.py:1-5`

| 常量名 | 值 | 说明 |
|--------|----|------|
| `ANNOTATION_LAYER_CONTENT_DIGEST` | `olot.layer.content.digest` | 原始文件摘要（非 tar/targz 摘要） |
| `ANNOTATION_LAYER_CONTENT_TYPE` | `olot.layer.content.type` | 内容类型：file 或 directory |
| `ANNOTATION_LAYER_CONTENT_INLAYERPATH` | `olot.layer.content.inlayerpath` | 容器文件系统中的展开路径 |
| `ANNOTATION_LAYER_CONTENT_NAME` | `olot.layer.content.name` | 原始文件名 |

## OCI MediaType 常量

位置：`olot/oci/oci_common.py`

| 常量名 | 值 |
|--------|----|
| `MediaTypes.manifest` | `application/vnd.oci.image.manifest.v1+json` |
| `MediaTypes.index` | `application/vnd.oci.image.index.v1+json` |
| `MediaTypes.layer` | `application/vnd.oci.image.layer.v1.tar` |
| `MediaTypes.layer_gzip` | `application/vnd.oci.image.layer.v1.tar+gzip` |
| `MediaTypes.empty` | `application/vnd.oci.empty.v1+json` |
| `MediaTypes.config` | `application/vnd.oci.image.config.v1+json` |

## 层处理流程

1. 验证 OCI layout 格式
2. 处理 Docker 格式清单转换（如需要）
3. 遍历所有 manifest 和 index
4. 对每个 model_file：创建 tar 层，计算摘要，写入 blobs
5. 对 modelcard：创建 targz 层，添加特殊注解
6. 更新每个 manifest 的 layers 列表
7. 更新 config 的 rootfs.diff_ids 和 history
8. 重新计算 config 和 manifest 的摘要
9. 更新 index.json 引用
10. （可选）添加 ModelPack manifest

## 默认模型路径

模型文件默认放置在容器内 `/models/` 目录下。使用 `root_dir` 参数时，相对路径会被保留，例如 `root_dir/onnx/model.onnx` 会存储为 `/models/onnx/model.onnx`。
