---
type: Reference
title: "Tagging 工具源码索引"
description: "Jupyter Docker Stacks 镜像标签与清单自动化系统（tagging/）源码信源登记"
tags: [tagging, manifest, automation, python, plumbum]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:source-grep", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-hierarchy, resource: "external/libs/jupyter/docker-stacks/tagging/hierarchy/images_hierarchy.py", title: "images_hierarchy.py（镜像层级定义）" }
  - { id: src-apply, resource: "external/libs/jupyter/docker-stacks/tagging/apps/apply_tags.py", title: "apply_tags.py（标签应用CLI）" }
  - { id: src-write-tags, resource: "external/libs/jupyter/docker-stacks/tagging/apps/write_tags_file.py", title: "write_tags_file.py（标签文件生成）" }
  - { id: src-write-manifest, resource: "external/libs/jupyter/docker-stacks/tagging/apps/write_manifest.py", title: "write_manifest.py（清单写入）" }
  - { id: src-merge-tags, resource: "external/libs/jupyter/docker-stacks/tagging/apps/merge_tags.py", title: "merge_tags.py（标签合并）" }
  - { id: src-config, resource: "external/libs/jupyter/docker-stacks/tagging/apps/config.py", title: "config.py（CLI配置对象）" }
  - { id: src-common-cli, resource: "external/libs/jupyter/docker-stacks/tagging/apps/common_cli_arguments.py", title: "common_cli_arguments.py（通用CLI参数）" }
  - { id: src-calc-ref, resource: "external/libs/jupyter/docker-stacks/tagging/apps/calculate_image_ref.py", title: "calculate_image_ref.py（镜像引用计算）" }
  - { id: src-taggers, resource: "external/libs/jupyter/docker-stacks/tagging/taggers/", title: "taggers/（标签生成器）" }
  - { id: src-manifests, resource: "external/libs/jupyter/docker-stacks/tagging/manifests/", title: "manifests/（清单生成器）" }
  - { id: src-utils, resource: "external/libs/jupyter/docker-stacks/tagging/utils/", title: "utils/（工具函数）" }
---

# Tagging 工具源码索引

tagging/ 目录是 Jupyter Docker Stacks 的镜像标签与清单自动化系统，使用 Python + plumbum 库实现。构建后自动从运行中的容器探测版本信息，生成多维度标签和软件清单。

## 模块架构

```
tagging/
├── apps/                    # CLI 应用入口
│   ├── apply_tags.py        # 应用标签到镜像（docker tag）
│   ├── write_tags_file.py   # 生成标签列表文件
│   ├── write_manifest.py    # 生成软件清单JSON
│   ├── merge_tags.py        # 合并多平台标签
│   ├── calculate_image_ref.py # 计算完整镜像引用
│   ├── config.py            # Config 数据类
│   └── common_cli_arguments.py # CLI参数解析器
├── hierarchy/
│   ├── images_hierarchy.py  # 镜像层级与Tagger/Manifest映射（核心定义）
│   ├── get_manifests.py     # 获取镜像的Manifest列表
│   └── get_taggers.py       # 获取镜像的Tagger列表
├── taggers/                 # 标签生成器（每个生成一组标签）
│   ├── tagger_interface.py  # Tagger接口定义
│   ├── date.py              # 日期标签（如2026-07-28）
│   ├── sha.py               # Git SHA标签
│   ├── ubuntu_version.py    # Ubuntu版本标签
│   └── versions.py          # 软件版本标签（Python/Mamba/Conda/Jupyter/R/Julia等）
├── manifests/               # 软件清单生成器
│   ├── manifest_interface.py # Manifest接口定义
│   ├── apt_packages.py      # APT包清单
│   ├── conda_environment.py # Conda环境清单
│   ├── r_packages.py        # R包清单
│   ├── julia_packages.py    # Julia包清单
│   ├── spark_info.py        # Spark信息清单
│   └── build_info.py        # 构建信息清单
└── utils/                   # 工具函数
    ├── docker_runner.py     # Docker命令执行封装
    ├── get_manifest_digest.py # 获取Manifest摘要
    ├── get_platform.py      # 平台检测
    ├── get_prefix.py        # 文件前缀生成
    ├── git_helper.py        # Git辅助函数
    └── quoted_output.py     # 命令输出引用解析
```

## 核心数据类

**ImageDescription**（hierarchy/images_hierarchy.py）：
- `parent_image: str | None`：父镜像名
- `taggers: list[TaggerInterface]`：该镜像的标签生成器列表
- `manifests: list[ManifestInterface]`：该镜像的清单生成器列表

**Config**（apps/config.py）：封装CLI参数，提供 `full_image()` 方法返回完整镜像引用。

## Tagger 清单

| Tagger | 输出标签示例 | 适用镜像 |
|--------|------------|---------|
| commit_sha_tagger | `sha-abc1234` | foundation |
| date_tagger | `2026-07-28` | foundation |
| ubuntu_version_tagger | `ubuntu-24.04` | foundation |
| python_major_minor_tagger | `python-3.13` | foundation |
| python_tagger | `python-3.13.14` | foundation |
| mamba_tagger | `mamba-2.8.1` | foundation |
| conda_tagger | `conda-24.x` | foundation |
| jupyter_notebook_tagger | `notebook-7.2.2` | base |
| jupyter_lab_tagger | `lab-4.3.x` | base |
| jupyter_hub_tagger | `hub-5.x` | base |
| r_tagger | `r-4.4.x` | r/datascience/all-spark |
| julia_tagger | `julia-1.11.x` | julia/datascience |
| tensorflow_tagger | `tensorflow-2.20.x` | tensorflow |
| pytorch_tagger | `pytorch-2.x` | pytorch |
| spark_tagger | `spark-3.5.x` | pyspark/all-spark |
| java_tagger | `java-21` | pyspark |

## Manifest 清单

| Manifest | 输出内容 | 适用镜像 |
|----------|---------|---------|
| conda_environment_manifest | Conda环境包列表（JSON） | foundation |
| apt_packages_manifest | APT安装包列表 | foundation |
| r_packages_manifest | R包列表 | r/datascience/all-spark |
| julia_packages_manifest | Julia包列表 | julia/datascience |
| spark_info_manifest | Spark版本信息 | pyspark/all-spark |
| build_info_manifest | 构建元信息 | 全局 |
