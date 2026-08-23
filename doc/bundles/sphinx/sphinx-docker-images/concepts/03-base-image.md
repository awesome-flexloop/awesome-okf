---
type: concept
title: "Base 镜像详解"
description: "逐层解析 sphinxdoc/sphinx 基础镜像的 Dockerfile 构建过程、依赖选择与体积优化策略"
tags: [docker, dockerfile, base-image, optimization]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: base, resource: "/references/dockerfile-base.md", title: "Base 镜像 Dockerfile 源码" }
---

# Base 镜像详解

`sphinxdoc/sphinx` 是三个镜像中最基础也是最常用的镜像，面向日常文档构建场景。本章逐层解析其 Dockerfile 设计。

## 完整 Dockerfile 回顾

```dockerfile
FROM python:slim

LABEL org.opencontainers.image.authors="Sphinx Team <https://www.sphinx-doc.org/>"
LABEL org.opencontainers.image.documentation="https://sphinx-doc.org/"
LABEL org.opencontainers.image.source="https://github.com/sphinx-doc/sphinx-docker-images"
LABEL org.opencontainers.image.version="8.2.3"
LABEL org.opencontainers.image.licenses="BSD-2-Clause"
LABEL org.opencontainers.image.description="Base container image for Sphinx"

WORKDIR /docs
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      graphviz \
      imagemagick \
      make \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip \
 && python3 -m pip install --no-cache-dir Sphinx==8.2.3 Pillow

CMD ["sphinx-build", "-M", "html", ".", "_build"]
```

## 逐层解析

### Layer 1：基础镜像选择

```dockerfile
FROM python:slim
```

选择 `python:slim` 而非其他基础镜像的原因：

- **python:slim** 是 Python 官方维护的 Debian 精简版镜像，预装 Python 3 和 pip
- 相比 `python:alpine`，slim 使用 glibc（Alpine 使用 musl），兼容性更好，Python C 扩展无需额外编译
- 相比完整 `python` 镜像，slim 去除了开发工具和文档，体积小很多（~50MB vs ~900MB）
- Debian 系的 apt 包管理器生态丰富，安装 graphviz/imagemagick 等工具方便

### Layer 2：OCI 标签元数据

```dockerfile
LABEL org.opencontainers.image.authors="..."
LABEL org.opencontainers.image.version="8.2.3"
```

使用 [OCI 标准标签](https://github.com/opencontainers/image-spec/blob/main/annotations.md) 标注镜像元数据：

| 标签 | 说明 |
|------|------|
| `org.opencontainers.image.authors` | 作者信息（Sphinx Team） |
| `org.opencontainers.image.documentation` | 文档 URL |
| `org.opencontainers.image.source` | 源码仓库 URL |
| `org.opencontainers.image.version` | 版本号（与 Sphinx 版本一致） |
| `org.opencontainers.image.licenses` | 许可证（BSD-2-Clause） |
| `org.opencontainers.image.description` | 镜像描述 |

这些标签通过 `docker inspect` 可查，也被 Docker Hub/GHCR 等镜像仓库展示。

### Layer 3：工作目录

```dockerfile
WORKDIR /docs
```

设置工作目录为 `/docs`。用户使用时需要将本地文档目录挂载到这个路径：

```bash
-v /path/to/your/docs:/docs
```

### Layer 4：系统依赖安装

```dockerfile
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
      graphviz \
      imagemagick \
      make \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
```

这是 Dockerfile 中最关键的一层，包含多个体积优化技巧：

**为什么只安装这三个包？**

| 包 | 用途 |
|----|------|
| `graphviz` | Sphinx 的 graphviz 扩展用于绘制图表（如继承图、调用图） |
| `imagemagick` | 图片处理，Sphinx 的图片转换和优化需要 |
| `make` | 执行 Makefile 构建（sphinx-quickstart 生成的 Makefile） |

**体积优化四步法**：

1. `--no-install-recommends`：只安装必需的包，不安装推荐包（显著减少体积）
2. `apt-get autoremove`：删除自动安装但不再需要的依赖
3. `apt-get clean`：清理 apt 缓存目录
4. `rm -rf /var/lib/apt/lists/*`：删除包列表文件（slim 镜像默认没这个，但手动清理更保险）

> **重要**：这四个步骤必须在同一个 `RUN` 指令中完成。如果分成多个 RUN，每个 RUN 会创建一个新层，前面层的文件即使被删除仍会占用镜像体积。

### Layer 5：Python 依赖安装

```dockerfile
RUN python3 -m pip install --no-cache-dir --upgrade pip \
 && python3 -m pip install --no-cache-dir Sphinx==8.2.3 Pillow
```

**关键点**：

- `--no-cache-dir`：禁用 pip 缓存，避免缓存文件进入镜像层
- **版本锁定**：`Sphinx==8.2.3` 精确锁定版本，确保构建可复现
- **Pillow 不锁版本**：Pillow 是图片处理库，使用最新版以获取安全更新
- 先升级 pip 再安装包，避免旧版 pip 的兼容性问题

### Layer 6：默认命令

```dockerfile
CMD ["sphinx-build", "-M", "html", ".", "_build"]
```

- 使用 **exec 形式**（JSON 数组）而非 shell 形式，确保信号正确传递
- 默认执行 HTML 构建
- 用户可以覆盖此命令，如 `sphinx-build -M epub . _build` 或 `sphinx-quickstart`

## 镜像体积估算

| 层 | 大约体积增量 | 说明 |
|----|------------|------|
| python:slim 基础 | ~50MB | Debian + Python 3 |
| apt 安装 + 清理 | ~80MB | graphviz + imagemagick + make 及其依赖 |
| pip 安装 | ~70MB | Sphinx + 依赖 + Pillow |
| **总计** | **~200MB** | 压缩后约 80-100MB |

## 最佳实践总结

从 base Dockerfile 中可以学到的 Docker 镜像最佳实践：

1. **选择合适的基础镜像**：python:slim 平衡了体积和兼容性
2. **使用 --no-install-recommends**：减少不必要的系统包
3. **同层清理**：apt 安装和清理在同一个 RUN 中完成
4. **--no-cache-dir**：pip 安装不保留缓存
5. **锁定关键依赖版本**：Sphinx==8.2.3 确保可复现构建
6. **使用 OCI 标签**：标准元数据便于镜像发现和管理
7. **合理设置 WORKDIR**：与用户挂载点一致
8. **CMD 使用 exec 形式**：正确的信号处理

## 相关概念

- [三镜像架构解析](/concepts/02-image-architecture.md)：三个镜像的分工与设计
- [LaTeX/PDF 镜像详解](/concepts/04-latexpdf-image.md)：TeXLive 包的选择策略
- [自定义镜像扩展](/concepts/07-customization.md)：基于 base 镜像创建自定义镜像
