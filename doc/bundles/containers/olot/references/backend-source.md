---
type: Reference
title: olot 后端抽象层源码信源
description: olot 项目后端实现，包含 skopeo、oras cp 和 oras-py 三种后端
tags: [backend, skopeo, oras, source-code]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T15:44:35+08:00"
verified:
  by: "process:source-verification"
  at: "2026-08-26T15:44:35+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: skopeo
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/backend/skopeo.py"
    title: "olot/backend/skopeo.py - skopeo CLI 后端"
  - id: oras-py
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/backend/oras_py.py"
    title: "olot/backend/oras_py.py - oras-py Python 后端"
  - id: oras-cp
    resource: "file:///d:/spaces/SpecWeave/external/dao/action/Containers/olot/olot/backend/oras_cp.py"
    title: "olot/backend/oras_cp.py - oras cp CLI 后端"
---

# olot 后端抽象层源码信源

## 后端类型

olot 支持三种后端实现，用于镜像的拉取（pull）和推送（push）：

| 后端 | 类型 | 依赖 | 特点 |
|------|------|------|------|
| skopeo | CLI 工具 | 外部 skopeo 命令 | 成熟稳定，多架构支持好 |
| oras cp | CLI 工具 | 外部 oras 命令 | OCI 原生工具 |
| oras-py | Python 库 | `pip install olot[oras-py]` | 纯 Python，无需外部工具 |

## skopeo 后端函数

位置：`olot/backend/skopeo.py`

| 函数 | 签名 | 说明 |
|------|------|------|
| `is_skopeo()` | `() -> bool` | 检查系统中是否可用 skopeo |
| `skopeo_pull()` | `(base_image: str, dest: str \| os.PathLike, params: typing.Sequence[str]=()) -> None` | 从 registry 拉取镜像到 OCI layout |
| `skopeo_push()` | `(src: str \| os.PathLike, oci_ref: str, params: typing.Sequence[str]=()) -> None` | 从 OCI layout 推送镜像到 registry |
| `skopeo_inspect()` | `(skopeo_ref: str, params: typing.Sequence[str]=()) -> str` | 检查镜像元数据 |

## oras-py 后端函数

位置：`olot/backend/oras_py.py`

| 函数 | 签名 | 说明 |
|------|------|------|
| `is_oras_py()` | `() -> bool` | 检查 oras Python 库是否已安装 |
| `oras_py_pull()` | `(base_image: str, dest: str \| os.PathLike, *, insecure: bool = False, tls_verify: bool = True) -> None` | 纯 Python 拉取镜像 |
| `oras_py_push()` | `(src: str \| os.PathLike, oci_ref: str, *, insecure: bool = False, tls_verify: bool = True) -> None` | 纯 Python 推送镜像 |

## oras cp 后端函数

位置：`olot/backend/oras_cp.py`

提供基于 oras CLI 命令的拉取和推送功能，与 skopeo 后端功能对应。

## 后端选择策略

- 有 skopeo CLI 时优先使用 skopeo
- 需要无外部工具依赖的纯 Python 环境使用 oras-py
- 使用 oras 工具链时使用 oras cp

## 安装可选依赖

```bash
# 安装 oras-py 后端支持
pip install olot[oras-py]

# 安装 modelcar 基础镜像支持
pip install olot[modelcar-base-image]
```
