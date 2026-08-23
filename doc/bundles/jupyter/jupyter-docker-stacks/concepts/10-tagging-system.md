---
type: Concept
title: "Tagging 元数据系统"
description: "tagging/ Python工具架构：Tagger/Manifest插件体系、自动标签生成、软件清单、多平台标签合并"
tags: [tagging, manifest, tagger, plumbum, metadata, automation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-tagging, resource: "/references/tagging-source.md", title: "Tagging工具源码索引" }
---

# Tagging 元数据系统

tagging/ 目录是 Jupyter Docker Stacks 的**镜像标签与软件清单自动化系统**。构建完成后，它从运行中的容器内自动探测版本信息，生成多维度Docker标签和JSON格式软件清单。

## 为什么需要Tagging系统？

Docker镜像通常只有`latest`标签或简单的版本号标签。Jupyter Docker Stacks需要更丰富的标签来满足用户需求：
- **日期标签**：`2026-07-28`，方便用户固定到特定构建版本
- **版本标签**：`python-3.13.14`、`lab-4.3.x`，方便按软件版本选择
- **平台标签**：`aarch64-...`前缀，区分多架构镜像
- **SHA标签**：`sha-abc1234`，精确对应Git commit

这些标签不能在Dockerfile中硬编码，因为版本会随依赖更新而变化。Tagging系统在**构建后**从容器内部探测真实版本，确保标签准确性。

## 架构概览

```
tagging/
├── apps/           # CLI应用入口
├── hierarchy/      # 镜像层级与Tagger/Manifest映射（核心配置）
├── taggers/        # 标签生成器（每个生成一组标签）
├── manifests/      # 软件清单生成器（每个生成一份JSON）
└── utils/          # Docker/Git/平台工具函数
```

## CLI应用（apps/）

四个CLI命令，对应Makefile中的`hook/%`目标：

| 命令 | 入口 | 功能 |
|------|------|------|
| write_tags_file | tagging.apps.write_tags_file | 在容器内运行，探测版本并写入标签文件 |
| write_manifest | tagging.apps.write_manifest | 在容器内运行，生成软件清单JSON |
| apply_tags | tagging.apps.apply_tags | 在主机运行，对Docker镜像应用标签（docker tag） |
| merge_tags | tagging.apps.merge_tags | 合并多平台镜像的标签 |

### 调用流程

Makefile中的`hook/%`目标串联了这三步：

```makefile
hook/%:
    python3 -m tagging.apps.write_tags_file ...    # 步骤1：在容器内生成标签列表
    python3 -m tagging.apps.write_manifest ...     # 步骤2：在容器内生成清单
    python3 -m tagging.apps.apply_tags ...         # 步骤3：在主机应用标签
```

1. write_tags_file在运行的容器中执行，将标签列表写入`/tmp/jupyter/tags/{platform}-{image}.txt`
2. write_manifest在运行的容器中执行，将软件清单写入`/tmp/jupyter/manifests/`
3. apply_tags在主机读取标签文件，执行`docker tag`命令为镜像添加所有标签

## 核心配置：hierarchy/images_hierarchy.py

这是Tagging系统的**核心配置文件**，定义了每个镜像的：

```python
@dataclass
class ImageDescription:
    parent_image: str | None           # 父镜像名（用于标签继承）
    taggers: list[TaggerInterface]     # 该镜像的标签生成器列表
    manifests: list[ManifestInterface] # 该镜像的清单生成器列表
```

每个镜像的配置：

| 镜像 | Tagger | Manifest |
|------|--------|----------|
| docker-stacks-foundation | commit_sha, date, ubuntu_version, python_major_minor, python, mamba, conda | conda_environment, apt_packages |
| base-notebook | jupyter_notebook, jupyter_lab, jupyter_hub | （继承父层） |
| minimal-notebook | （无额外） | （无额外） |
| scipy-notebook | （无额外） | （无额外） |
| r-notebook | r | r_packages |
| julia-notebook | julia | julia_packages |
| tensorflow-notebook | tensorflow | （无额外） |
| pytorch-notebook | pytorch | （无额外） |
| datascience-notebook | r, julia | r_packages, julia_packages |
| pyspark-notebook | spark, java | spark_info |
| all-spark-notebook | r | r_packages |

标签和清单具有**继承性**：子镜像自动包含父镜像的所有Tagger和Manifest。例如datascience-notebook的标签包含foundation→base→scipy的所有标签加上r和julia标签。

## Tagger 标签生成器

所有Tagger实现`TaggerInterface`接口，接收一个Docker Runner对象，返回标签字符串列表。

### 日期标签（date_tagger）

生成格式：`YYYY-MM-DD`

```python
def date_tagger(runner) -> list[str]:
    return [datetime.now(timezone.utc).strftime("%Y-%m-%d")]
```

### SHA标签（commit_sha_tagger）

生成格式：`sha-<7位短SHA>`

从Git历史获取当前构建的commit SHA。

### Ubuntu版本标签（ubuntu_version_tagger）

生成格式：`ubuntu-24.04`

在容器内通过`/etc/os-release`获取Ubuntu版本。

### Python版本标签

两个Tagger：
- `python_major_minor_tagger`：`python-3.13`
- `python_tagger`：`python-3.13.14`

在容器内通过`python --version`获取精确版本。

### Mamba/Conda版本标签

- `mamba_tagger`：`mamba-2.8.1`
- `conda_tagger`：`conda-24.x.x`

在容器内通过`mamba --version`和`conda --version`获取。

### Jupyter组件版本标签

- `jupyter_notebook_tagger`：`notebook-7.2.2`
- `jupyter_lab_tagger`：`lab-4.3.x`
- `jupyter_hub_tagger`：`hub-5.x.x`

在容器内通过`pip show notebook/jupyterlab/jupyterhub`获取版本。

### 其他软件版本标签

| Tagger | 格式 | 获取方式 |
|--------|------|---------|
| r_tagger | `r-4.4.x` | `R --version` |
| julia_tagger | `julia-1.11.x` | `julia --version` |
| tensorflow_tagger | `tensorflow-2.20.x` | `pip show tensorflow` |
| pytorch_tagger | `pytorch-2.x.x` | `pip show torch` |
| spark_tagger | `spark-3.5.x` | 从Spark JAR文件名解析 |
| java_tagger | `java-21` | `java -version` |

## Manifest 软件清单

Manifest生成JSON格式的软件清单，记录镜像中安装的所有软件包版本信息。这些信息用于：
- GitHub Wiki自动更新
- 安全漏洞扫描
- 版本溯源

### Conda环境清单（conda_environment_manifest）

导出完整的conda环境包列表：名称、版本、build字符串、channel。

### APT包清单（apt_packages_manifest）

通过`dpkg-query`导出所有APT安装包：名称、版本。

### R包清单（r_packages_manifest）

通过R的`installed.packages()`导出R包列表。

### Julia包清单（julia_packages_manifest）

通过Julia的`Pkg.status()`导出Julia包列表。

### Spark信息清单（spark_info_manifest）

导出Spark版本、Scala版本、Hadoop版本、Java版本等信息。

## 工具函数（utils/）

| 模块 | 功能 |
|------|------|
| docker_runner.py | 封装Docker容器启动/执行/停止，提供命令执行接口 |
| get_platform.py | 检测当前平台（x86_64/aarch64） |
| get_prefix.py | 根据平台和variant生成文件名前缀 |
| get_manifest_digest.py | 获取Registry中镜像的manifest digest |
| git_helper.py | Git辅助函数（获取SHA、branch等） |
| quoted_output.py | 命令输出引用解析 |

## plumbum库的使用

tagging系统使用`plumbum`库替代subprocess来执行Docker命令：

```python
import plumbum
docker = plumbum.local["docker"]
docker["tag", config.full_image(), tag].run_fg()
```

plumbum提供了类型安全的命令组合接口，比raw subprocess更易读且不易出错。

## Config对象

Config类封装CLI参数，提供便捷方法：

```python
@dataclass
class Config:
    registry: str
    owner: str
    image: str
    variant: str
    platform: str
    tags_dir: Path
    manifests_dir: Path | None
    # ...

    def full_image(self) -> str:
        return f"{self.registry}/{self.owner}/{self.image}"
```

## 多平台标签合并（merge_tags）

Docker Buildx构建多平台镜像后，需要将各平台的标签合并到同一个manifest list。merge_tags负责：
1. 读取各平台的标签文件
2. 合并标签列表（去重）
3. 创建manifest list并推送

## 相关概念

- [构建与CI/CD](12-build-ci-cd.md)
- [测试框架](11-testing-framework.md)
