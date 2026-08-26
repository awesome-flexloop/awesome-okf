---
type: Reference
title: "README.md 项目概览与快速入门"
description: "podman-py 项目 README 中的安装说明、依赖列表、基础使用示例与官方资源链接。"
tags: [podman-py, readme, installation, quickstart, dependencies]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:45:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme
    resource: https://github.com/containers/podman-py/blob/main/README.md
    title: podman-py README.md
---

# README.md 项目概览

## 项目基本信息

- **PyPI 包名**：`podman`
- **项目名称**：podman-py
- **描述**：Bindings for Podman RESTful API（Podman RESTful API 的 Python 绑定库）
- **官方文档**：https://podman-py.readthedocs.io/en/latest/
- **源码仓库**：https://github.com/containers/podman-py

## 安装

```bash
pip install podman
```

## 运行时依赖

- `requests>=2.24`
- `tomli>=1.2.3`（Python < 3.11 时需要）
- `urllib3`

## 可选依赖分组

| 分组 | 依赖 | 用途 |
|------|------|------|
| `progress_bar` | `rich>=12.5.1` | 镜像拉取进度条显示 |
| `docs` | `sphinx` | 文档构建 |
| `test` | `coverage`, `fixtures`, `pytest`, `requests-mock`, `tox` | 测试套件 |

## 基础使用示例

```python
import json
from podman import PodmanClient

uri = "unix:///run/user/1000/podman/podman.sock"

with PodmanClient(base_url=uri) as client:
    version = client.version()
    print("Release: ", version["Version"])
    print("Compatible API: ", version["ApiVersion"])
    print("Podman API: ", version["Components"][0]["Details"]["APIVersion"], "\n")

    for image in client.images.list():
        print(image, image.id, "\n")

    for container in client.containers.list():
        container.reload()
        print(container, container.id, "\n")
        print(container, container.status, "\n")
        print(sorted(container.attrs.keys()))

    print(json.dumps(client.df(), indent=4))
```
