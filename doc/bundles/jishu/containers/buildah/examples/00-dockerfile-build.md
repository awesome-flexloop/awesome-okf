---
type: Example
title: "从 Containerfile 构建并推送 OCI 镜像"
description: "使用 buildah build 命令从 Containerfile 构建多阶段镜像，包含签名、SBOM 扫描、manifest list 推送的完整流程。"
tags: [buildah, containerfile, multi-stage-build, oci, sigstore, sbom, manifest-list]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T12:30:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08T12:30:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: buildah-build
    resource: /references/source.md
    title: buildah 源码与文档信源登记
---

# 从 Containerfile 构建并推送 OCI 镜像

本示例演示使用 `buildah build` 完成一个典型的多阶段 Go 应用构建流程，包括 OCI 格式输出、镜像签名和 SBOM 扫描。

## 项目结构

```
myapp/
├── Containerfile       # 多阶段构建文件
├── cmd/server/main.go  # Go 源码
└── go.mod
```

## Containerfile（多阶段构建）

```dockerfile
# Stage 1: 编译
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-s -w' -o server ./cmd/server

# Stage 2: 运行时
FROM scratch
COPY --from=builder /app/server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
USER 65534
EXPOSE 8080
ENTRYPOINT ["/server"]
```

## Step 1：构建镜像（OCI 格式）

```bash
# 从 Containerfile 构建，输出 OCI 格式
buildah build \
  --format oci \
  --layers \
  -f Containerfile \
  -t registry.example.com/myapp:v1.0.0 \
  .

# 查看构建结果
buildah images
# REPOSITORY                            TAG      IMAGE ID      CREATED         SIZE
# registry.example.com/myapp            v1.0.0   abc123...     2 minutes ago   25MB
```

## Step 2：手动逐步构建（等价操作）

```bash
# 2a. 创建 working container
CONTAINER=$(buildah from golang:1.22-alpine)
echo "Working container: $CONTAINER"

# 2b. 复制源码
buildah copy $CONTAINER go.mod go.sum /app/
buildah copy $CONTAINER . /app/

# 2c. 执行编译命令
buildah run $CONTAINER -- sh -c 'cd /app && go mod download'
buildah run $CONTAINER -- sh -c 'cd /app && CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o server ./cmd/server'

# 2d. 配置运行时镜像（commit 时设置）
buildah config --cmd '["/server"]' $CONTAINER
buildah config --port 8080 $CONTAINER
buildah config --user 65534 $CONTAINER
buildah config --workingdir / $CONTAINER

# 2e. 提交为镜像
IMAGE_ID=$(buildah commit $CONTAINER registry.example.com/myapp:v1.0.0)
echo "Built image: $IMAGE_ID"

# 2f. 清理 working container
buildah rm $CONTAINER
```

## Step 3：镜像签名与 SBOM 扫描

```bash
# 3a. 用 GPG 密钥签名
buildah push \
  --sign-by 0xA1B2C3D4E5F6 \
  --format oci \
  registry.example.com/myapp:v1.0.0 \
  docker://registry.example.com/myapp:v1.0.0

# 3b. 生成并推送 SBOM（需要 buildah >= 1.33）
buildah push \
  --sbom /tmp/myapp.sbom.json \
  --format oci \
  registry.example.com/myapp:v1.0.0 \
  docker://registry.example.com/myapp:v1.0.0
```

## Step 4：多架构 manifest list 构建

```bash
# 为多个平台分别构建
for platform in linux/amd64 linux/arm64; do
  buildah build \
    --platform $platform \
    --format oci \
    --layers \
    -f Containerfile \
    -t registry.example.com/myapp:v1.0.0 \
    .
done

# 构建 manifest list（自动收集所有架构）
buildah manifest create registry.example.com/myapp:v1.0.0
for arch in amd64 arm64; do
  buildah manifest add \
    registry.example.com/myapp:v1.0.0 \
    docker://registry.example.com/myapp:v1.0.0-$arch
done

# 推送 manifest list
buildah manifest push registry.example.com/myapp:v1.0.0 \
  docker://registry.example.com/myapp:v1.0.0
```

## Step 5：验证构建结果

```bash
# 查看镜像详情
buildah inspect registry.example.com/myapp:v1.0.0

# 查看镜像层信息
buildah inspect --type image registry.example.com/myapp:v1.0.0 | jq '.LayerIds'

# 测试运行（仅验证，生产环境用 Podman）
buildah run --rm registry.example.com/myapp:v1.0.0 --help
```

## 常用标志速查

| 标志 | 说明 | 默认值 |
|------|------|--------|
| `--format oci` | 输出格式：oci/docker | docker |
| `--layers` | 使用缓存层（加速重建） | true |
| `--squash` | 合并所有层为单层 | false |
| `--platform` | 目标平台（amd64/arm64等） | 当前平台 |
| `--sign-by` | GPG fingerprint 签名 | 无 |
| `--sbom` | SBOM 输出文件路径 | 无 |
| `--logfile` | 构建日志文件 | 无 |
| `--pull` | 强制拉取最新基础镜像 | false |
| `--cap-add` | 添加 Linux capabilities | 无 |
| `--cap-drop` | 丢弃 Linux capabilities | 无 |

## 相关概念
- [/concepts/00-introduction.md](../concepts/00-introduction.md) — working container 概念
- [/concepts/01-build-flow.md](../concepts/01-build-flow.md) — from/run/commit 流水线源码详解
