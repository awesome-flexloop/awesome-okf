---
type: concept
title: "Docker 构建支持"
description: "constructor 的 Docker 构建功能：生成 Dockerfile、使用 buildx 构建镜像、导出 tar 包，以及容器化部署 conda 环境。"
tags: [Docker, 容器, Dockerfile, buildx, 镜像, OCI]
status: stable
stale_after: 2027-12-31
level: intermediate
prerequisites: ["04-installer-types", "09-platform-installers"]
reading_time: 8
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-docker
    resource: "constructor/docker_build.py"
---

# Docker 构建支持

constructor 除了生成原生安装程序（.sh/.exe/.pkg）外，还支持生成 **Dockerfile** 和可选的 **Docker 镜像 tar 包**，用于容器化部署 conda 环境。

## 启用 Docker 构建

Docker 构建需要满足两个条件：
1. `installer_type` 包含 `docker`（或 `all`）
2. 提供 `docker_base_image`（基础镜像）

### 最小配置

```yaml
name: mypython
version: "1.0"
installer_type: docker
docker_base_image: debian:bookworm-slim
channels:
  - conda-forge
specs:
  - python 3.14.*
  - pip
```

### 平台映射

Docker 构建仅支持 Linux 平台，constructor 自动映射 conda 平台到 Docker 平台：

| conda 平台 | Docker 平台 |
|-----------|------------|
| `linux-64` | `linux/amd64` |
| `linux-aarch64` | `linux/arm64` |
| `linux-ppc64le` | `linux/ppc64le` |
| `linux-s390x` | `linux/s390x` |
| `linux-armv7l` | `linux/arm/v7` |

## 构建流程

`docker_build.create(info, verbose)` 执行以下步骤：

1. **先构建 SH 安装程序**：Docker 构建依赖 .sh 安装程序作为输入层
2. **创建 Docker 构建目录**（临时目录）
3. **复制 .sh 安装程序到构建目录**
4. **生成 Dockerfile**（`generate_dockerfile()`）
5. **如指定 `docker_image_format: "tar"`**：调用 `build_image()` 使用 docker buildx 构建镜像并导出为 tar
6. **输出 Dockerfile 和可选镜像 tar 包**

### generate_dockerfile

从 Jinja2 模板 `constructor/dockerfile_template.tmpl` 渲染 Dockerfile：

```dockerfile
# 模板变量包括：
# - base_image: debian:bookworm-slim
# - default_prefix: /opt/mypython
# - installer_filename: mypython-1.0-Linux-x86_64.sh
# - name/version
# - labels (OCI标签)
# - initialize_conda
# - init_run_block (conda init命令)
```

Dockerfile 的核心逻辑：
1. `FROM <base_image>`
2. 复制 `.sh` 安装程序到镜像中
3. 以批处理模式运行安装程序：`bash <installer>.sh -b -p <prefix>`
4. 可选 `conda init --all` 初始化 shell
5. 清理安装程序和包缓存
6. 设置 PATH 和入口点

### build_image（导出镜像）

```python
def build_image(info, docker_dir):
    # 使用 docker buildx 构建
    # docker buildx build --platform linux/amd64 -t <name>:<version> --output type=docker,dest=<output.tar> .
```

构建完成后导出为 tar 包，文件名格式：`<name>-<version>-<platform>-<arch>-docker.tar`

## Docker 配置字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `docker_base_image` | string | **必填** | Docker 基础镜像（如 `debian:bookworm-slim`、`ubuntu:24.04`） |
| `docker_tag` | string | `<name>:<version>` | 镜像标签 |
| `docker_labels` | dict | `{}` | 额外 OCI 标签 |
| `docker_image_format` | `"tar"` | `None` | 导出镜像格式（目前仅支持 tar） |

### 自动设置的 OCI 标签

constructor 自动设置以下 OCI 标准标签：
- `org.opencontainers.image.title`: name
- `org.opencontainers.image.version`: version

用户可通过 `docker_labels` 添加自定义标签。

## 安装路径

Docker 容器中的默认安装路径为 `/opt/<name>`（小写），可通过 `default_prefix` 覆盖：

```yaml
default_prefix: /opt/conda
```

在 Docker 构建时，也可通过 build arg 覆盖：

```bash
docker build --build-arg PREFIX=/custom/path .
```

## conda 初始化

`initialize_conda` 选项在 Docker 中的行为：
- `classic`/`True`：在 Dockerfile 中运行 `conda init --all`，将 conda 初始化写入 bashrc
- `condabin`：仅添加 condabin 到 PATH（不需要 conda init）
- `False`：不初始化（适合纯 Python 运行时）

如环境包含 mamba，会自动添加 `mamba shell init`。

## 使用示例

### 生成 Dockerfile（不构建镜像）

```yaml
name: mypython
version: "1.0"
installer_type: docker
docker_base_image: debian:bookworm-slim
channels:
  - conda-forge
specs:
  - python=3.14
```

构建后输出：
- `mypython-1.0-Linux-x86_64.sh`（SH 安装程序）
- `Dockerfile`（可直接用于 docker build）

用户可自行构建：
```bash
docker build -t mypython:1.0 .
docker run -it --rm mypython:1.0 python --version
```

### 构建并导出镜像 tar

```yaml
name: mypython
version: "1.0"
installer_type: docker
docker_base_image: debian:bookworm-slim
docker_image_format: tar
docker_tag: mypython:1.0
docker_labels:
  org.opencontainers.image.description: "My Python environment"
  maintainer: "me@example.com"
channels:
  - conda-forge
specs:
  - python=3.14
  - numpy
  - pandas
```

构建后额外输出：
- `mypython-1.0-Linux-x86_64-docker.tar`（Docker 镜像 tar 包）

加载和运行：
```bash
docker load -i mypython-1.0-Linux-x86_64-docker.tar
docker run -it --rm mypython:1.0 python -c "import numpy; print(numpy.__version__)"
```

### 同时生成 SH 和 Docker

```yaml
installer_type: all    # Linux上生成 .sh + Dockerfile
```

## 注意事项

1. **Docker 构建需要 Docker/Buildx**：构建机器必须安装 Docker 且 `docker buildx` 可用（通过 `utils.has_docker_buildx()` 检测）。
2. **基础镜像兼容性**：确保基础镜像的 libc 版本（glibc）与包兼容。Debian/Ubuntu 等 glibc 发行版最安全；Alpine（musl）不兼容 conda 包。
3. **SH 安装程序是构建输入**：即使只需要 Docker 输出，constructor 也会先生成 .sh 安装程序作为 Docker 构建上下文的一部分。
4. **docker_base_image 必须包含 bash**：SH 安装程序需要 bash 执行；`scratch` 或 distroless 镜像不可用。
5. **环境变量和入口点**：Dockerfile 默认将 `PREFIX/bin` 添加到 PATH，但不设置 ENTRYPOINT/CMD，用户需自行添加。

## 下一步

- 04-安装程序类型：了解所有安装程序类型的对比
- 示例：Docker 镜像构建：查看完整 Docker 配置示例
