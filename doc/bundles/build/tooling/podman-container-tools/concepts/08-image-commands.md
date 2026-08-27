---
type: Concept
title: 镜像操作命令
description: images/子目录27个命令分类详解：镜像获取推送、查询信息、构建标记、删除清理、信任管理与跨主机传输，及Buildah依赖关系
tags: [podman, concept, commands, image, buildah, build, pull, push, registry, trust]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## 镜像与 Buildah 的关系

Podman 专注于容器运行时管理，镜像构建功能底层依赖 **Buildah**（`containers/buildah`）库。理解这一分工是理解 Podman 镜像命令的基础。

### 工具链分工

| 工具 | 专注领域 | 核心能力 |
|------|----------|----------|
| **Buildah** | 镜像构建 | `buildah bud`(build), `buildah from`, `buildah copy`, `buildah run` 等细粒度构建命令 |
| **Podman** | 容器运行 | `podman run`, `podman ps` 等容器生命周期管理；`podman build` 底层调用 Buildah |
| **Skopeo** | 镜像搬运 | `skopeo copy`, `skopeo inspect` 等跨仓库镜像操作 |

### Podman build 的底层实现

`podman build` 和 `podman buildx` 命令底层调用 Buildah 库执行实际的镜像构建：
- 解析 Containerfile/Dockerfile
- 执行构建指令（FROM/RUN/COPY/CMD 等）
- 管理构建缓存
- 利用 OverlayFS 的写时复制特性分层构建
- 最终产物存储在 containers/storage 中，Podman 可直接运行

Buildah 专注于构建 OCI 镜像，Podman 专注于维护和运行 OCI 镜像及容器，两者互补，共享 containers/storage 和 containers/image 底层库，镜像可无缝互通。

## 镜像命令概览

`cmd/podman/images/` 目录包含 27 个镜像操作命令，覆盖镜像从获取、构建、查询到删除、推送、签名的完整生命周期。所有镜像命令在 `podman image` 父命令下，常用命令有顶层别名（如 `podman images` = `podman image ls`）。

## 获取与传输命令

### 拉取镜像：pull

| 命令 | 说明 |
|------|------|
| `pull` | 从镜像仓库拉取镜像到本地 |

```bash
podman pull docker.io/library/nginx:latest
podman pull alpine
podman pull --arch=arm64 nginx
podman pull --tls-verify=false myregistry.local/app:latest
```

常用标志：
- `--arch`：指定架构（amd64/arm64/ppc64le等）
- `--tls-verify`：是否验证 TLS 证书（私有仓库用）
- `--creds`：仓库认证凭据（USER:PASSWORD）
- `--quiet, -q`：静默输出，只显示拉取的镜像 ID

不指定仓库前缀时，默认从 `docker.io/library/` 拉取（Docker Hub 官方镜像）。

### 推送镜像：push

| 命令 | 说明 |
|------|------|
| `push` | 将本地镜像推送到镜像仓库 |

```bash
podman push myimage:latest docker.io/myuser/myimage:v1
podman push --tls-verify=false myimage myregistry.local/app:latest
podman push myimage:latest dir:/tmp/image-export
```

支持多种传输目标：容器仓库（docker://）、本地目录（dir://）、OCI 归档（oci-archive://）、Docker 归档（docker-archive://）。

### 加载镜像：load

| 命令 | 说明 |
|------|------|
| `load` | 从 tar 归档加载镜像到本地存储 |

```bash
podman load -i image.tar
podman load < image.tar.gz
gzip -dc image.tar.gz | podman load
```

`load` 用于加载 `podman save` 导出的镜像归档（包含镜像历史和元数据），与 `import` 不同。

### 导入镜像：import

| 命令 | 说明 |
|------|------|
| `import` | 从容器文件系统 tar 包导入为镜像 |

```bash
podman import container-rootfs.tar myimage:latest
podman import --change "CMD /bin/sh" rootfs.tar myimage:v1
cat rootfs.tar | podman import - myimage:latest
```

`import` 创建的镜像只有一个层，不包含原镜像的历史和元数据。`--change` 可设置 Dockerfile 风格的配置指令（CMD/ENTRYPOINT/ENV 等）。

### 保存镜像：save

| 命令 | 说明 |
|------|------|
| `save` | 将镜像保存为 tar 归档（可在另一台机器 load） |

```bash
podman save -o myimage.tar myimage:latest
podman save --format oci-archive -o myimage-oci.tar myimage:latest
podman save myimage:latest | gzip > myimage.tar.gz
```

常用标志：
- `-o, --output`：输出文件路径
- `--format`：归档格式（docker-archive/oci-archive/oci-dir，默认 docker-archive）
- `--compress`：压缩镜像层

`save` 导出的是完整镜像（含所有层历史和元数据），可通过 `load` 在另一台机器导入。

### 跨主机传输：scp

| 命令 | 说明 |
|------|------|
| `scp` | 通过 SSH 在主机间安全传输镜像 |

```bash
podman scp myimage:latest user@remotehost::
podman scp myimage:latest user@remotehost:/remote-image:tag
```

`scp` 利用 SSH 连接将镜像直接传输到远程主机的 Podman 存储，无需经过中间 registry。传输过程自动在本地 save、远程 load。

## 查询命令

### 镜像列表：list / images

| 命令 | 说明 |
|------|------|
| `list` | 列出本地存储的镜像 |
| `image` | `list` 的别名（`podman image ls`） |

```bash
podman images
podman image ls
podman images -a
podman images --format "{{.ID}} {{.Repository}}:{{.Tag}} {{.Size}}"
podman images -q
podman images --filter dangling=true
```

常用标志：
- `-a, --all`：显示所有镜像（包括中间层）
- `-q, --quiet`：只显示镜像 ID
- `--format`：自定义输出格式
- `--filter, -f`：按条件过滤（dangling、before、since、reference、label 等）
- `--no-trunc`：不截断输出

`podman images` 显示镜像 ID、仓库名、标签、大小和创建时间。

### 详情查看：inspect / exists

| 命令 | 说明 |
|------|------|
| `inspect` | 查看镜像的详细配置和层信息（JSON 格式） |
| `exists` | 检查镜像是否存在（脚本友好） |

```bash
podman inspect nginx:latest
podman inspect --format "{{.Architecture}} {{.Os}}" nginx
podman image exists nginx:latest && echo "Image exists"
```

`inspect` 返回镜像的完整元数据：层列表、环境变量、入口点、暴露端口、架构、创建时间、作者等。

### 历史记录：history

| 命令 | 说明 |
|------|------|
| `history` | 显示镜像的构建历史（每一层的命令和大小） |

```bash
podman history nginx:latest
podman history --no-trunc nginx
podman history --format "{{.ID}} {{.CreatedBy}} {{.Size}}" nginx
```

按层显示镜像构建过程中的每一条指令，便于理解镜像构成和排查大镜像问题。`--no-trunc` 显示完整命令。

### 层树状视图：tree

| 命令 | 说明 |
|------|------|
| `tree` | 以树状结构显示镜像的层级关系 |

```bash
podman image tree nginx:latest
podman image tree --whatrequires nginx:latest
```

直观展示镜像的层叠加关系，`--whatrequires` 显示依赖该镜像的子镜像/容器。

### 搜索镜像：search

| 命令 | 说明 |
|------|------|
| `search` | 在镜像仓库中搜索镜像 |

```bash
podman search nginx
podman search --limit 5 python
podman search --filter is-official=true ubuntu
podman search registry.example.com/myapp
```

在容器镜像仓库中搜索镜像，默认搜索 Docker Hub。显示镜像名称、描述、星级、是否官方、是否自动构建等信息。

## 构建命令

### 构建镜像：build

| 命令 | 说明 |
|------|------|
| `build` | 使用 Containerfile/Dockerfile 构建镜像（底层调用 Buildah） |

```bash
podman build -t myimage:v1 .
podman build -f Containerfile.prod -t myapp:prod .
podman build --build-arg VERSION=1.0 -t myapp .
podman build --no-cache -t myapp:latest .
podman build --platform linux/arm64,linux/amd64 -t myapp:multiarch .
```

常用标志：
- `-t, --tag`：指定镜像名称和标签
- `-f, --file`：指定 Containerfile/Dockerfile 路径
- `--build-arg`：设置构建时变量
- `--no-cache`：不使用构建缓存
- `--pull-always`：总是拉取最新基础镜像
- `--target`：多阶段构建中指定目标阶段
- `--platform`：指定目标平台（多架构构建）
- `-v, --volume`：挂载构建时卷
- `--squash`：将所有层压缩为一个层

`podman build` 在当前目录查找 `Containerfile` 或 `Dockerfile`，按指令顺序构建镜像。

### 扩展构建：buildx / buildx_inspect

| 命令 | 说明 |
|------|------|
| `buildx` | 扩展构建命令（多架构、构建器实例管理） |
| `buildx_inspect` | 查看 buildx 构建器实例信息 |

```bash
podman buildx build --platform linux/amd64,linux/arm64 -t myapp:multiarch .
podman buildx ls
podman buildx inspect
```

`buildx` 提供更高级的构建能力，特别是多架构镜像构建和构建缓存管理。

### 挂载：mount / unmount

| 命令 | 说明 |
|------|------|
| `mount` | 挂载镜像根文件系统到宿主机 |
| `unmount` | 卸载已挂载的镜像 |

```bash
podman image mount nginx:latest
podman image unmount nginx:latest
podman image unmount -a
```

挂载后可在宿主机上浏览镜像内容，用于调试或提取文件。与容器 mount 类似但针对只读镜像层。

## 标记与删除命令

### 添加标签：tag

| 命令 | 说明 |
|------|------|
| `tag` | 为本地镜像添加新标签 |

```bash
podman tag myimage:latest myimage:v1
podman tag myimage:latest docker.io/myuser/myimage:latest
podman tag nginx:alpine mynginx:stable
```

`tag` 不为镜像创建新副本，只是在同一镜像上添加额外的名称引用。一个镜像可以有多个标签。

### 删除标签：untag

| 命令 | 说明 |
|------|------|
| `untag` | 删除镜像的标签（不删除镜像本身） |

```bash
podman untag myimage:oldtag
podman untag myimage:latest docker.io/myuser/myimage:latest
```

移除镜像的指定标签。如果镜像只剩一个标签，`untag` 会提示使用 `rmi` 删除镜像。

### 删除镜像：rm / rmi

| 命令 | 说明 |
|------|------|
| `rm` | 删除本地镜像（`rmi` 的别名） |

```bash
podman rmi myimage:latest
podman rmi a1b2c3d4
podman rmi -a
podman rmi -f myimage:latest
```

常用标志：
- `-a, --all`：删除所有镜像
- `-f, --force`：强制删除（即使有容器使用该镜像）
- `--prune`：删除未打标签的父镜像

如果镜像被容器引用（即使容器已停止），默认无法删除，需 `-f` 强制删除。

### 清理镜像：prune

| 命令 | 说明 |
|------|------|
| `prune` | 清理未使用的镜像（dangling 镜像） |

```bash
podman image prune
podman image prune -a
podman image prune -f
podman image prune --filter until=24h
```

默认只清理 dangling 镜像（无标签的虚悬镜像）。`-a` 清理所有未被任何容器使用的镜像。`-f` 跳过确认。

### 差异：diff

| 命令 | 说明 |
|------|------|
| `diff` | 查看镜像文件系统相对于其父镜像的变更 |

```bash
podman image diff myimage:latest
podman image diff --format json myimage:latest
```

显示镜像层添加/删除/修改的文件列表。

## 信任与签名命令

镜像信任机制用于验证镜像来源和完整性，防止供应链攻击。

### 信任管理：trust

| 命令 | 说明 |
|------|------|
| `trust` | 管理镜像信任策略 |

```bash
podman image trust show
podman image trust set --type accept docker.io/myofficial/*
podman image trust set --type reject registry.untrusted.com
```

信任策略控制是否接受来自特定仓库的镜像、是否要求签名验证等。

### 信任设置：trust_set

| 命令 | 说明 |
|------|------|
| `trust_set` | 设置镜像信任策略（trust set 的底层命令） |

### 信任查看：trust_show

| 命令 | 说明 |
|------|------|
| `trust_show` | 显示当前镜像信任策略（trust show 的底层命令） |

### 镜像签名：sign

| 命令 | 说明 |
|------|------|
| `sign` | 为镜像添加 GPG 签名 |

```bash
podman image sign --sign-by mykey@example.com myimage:latest
```

使用 GPG 私钥为镜像签名，下游用户可配置策略验证签名，确保镜像未被篡改且来自可信来源。

## 相关概念

- [CLI命令结构](06-cli-structure.md) — Cobra框架、命令注册表与双引擎模式
- [容器操作命令](07-container-commands.md) — 36个容器命令分类详解
- [架构概览](02-architecture-overview.md) — Buildah/Podman/Skopeo 工具链分工
- [Runtime运行时](03-runtime.md) — libimage.Runtime 镜像运行时初始化
