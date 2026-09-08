---
type: Example
title: "镜像跨仓库迁移与格式转换"
description: "使用 skopeo copy 实现 Docker↔OCI 格式转换、跨注册表迁移、多架构复制与认证重定向的完整示例。"
tags: [skopeo, copy-command, format-conversion, multi-arch, registry-migration]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T11:30:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08T11:30:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: skopeo-copy
    resource: /references/source.md
    title: skopeo 源码与文档信源登记
---

# 镜像跨仓库迁移与格式转换

本示例演示使用 `skopeo copy` 完成生产环境中常见的三个场景：**格式转换**（Docker v2s2 → OCI）、**跨注册表迁移**（含认证重定向）、**多架构 manifest list 处理**。

## 前置条件

```bash
# 确认 skopeo 版本
skopeo --version
# skopeo version 1.15+

# 准备认证文件（两种方案任选其一）
# 方案 A：使用 authfile（推荐，凭证集中管理）
podman login registry.example.com --username deploy --password-file ~/.secrets/reg-password
podman login docker.io --username myuser --password-file ~/.secrets/docker-password

# 方案 B：每条命令内联认证
# skopeo copy --creds user:pass ...
```

## 场景 1：Docker 格式 → OCI 格式转换

```bash
# 从 Docker Hub 拉取 nginx（Docker v2s2 格式），转换为 OCI 格式存入本地目录
skopeo copy \
  --dest-format oci \
  docker://docker.io/library/nginx:1.27-alpine \
  dir:/tmp/nginx-oci

# 验证转换结果
skopeo inspect dir:/tmp/nginx-oci
# 输出 manifest 的 MediaType 应为 "application/vnd.oci.image.manifest.v1+json"

# 目录结构（OCI layout）
tree /tmp/nginx-oci
# oci-layout
# index.json
# blobs/sha256/...（各层 tar 包）
```

## 场景 2：跨注册表迁移（保留签名，去除原签名）

```bash
# 2a. 保留原签名的迁移（适用于可信源）
skopeo copy \
  --dest-tls-verify=true \
  --cert-dir /etc/container-certs \
  docker://registry.source.com/myapp:v1.2.3 \
  docker://registry.target.com/myapp:v1.2.3

# 2b. 迁移时去除原签名，由目标注册表重新签名（推荐，避免签名链污染）
skopeo copy \
  --remove-signatures \
  --sign-by 0xDEADBEEF \
  docker://registry.source.com/myapp:v1.2.3 \
  docker://registry.target.com/myapp:v1.2.3

# 2c. 迁移时附带额外标签
skopeo copy \
  --additional-tag registry.target.com/myapp:latest \
  --additional-tag registry.target.com/myapp:v1 \
  docker://registry.source.com/myapp:v1.2.3 \
  docker://registry.target.com/myapp:1.2.3
```

## 场景 3：多架构 manifest list 处理

```bash
# 3a. 复制全部架构（--all 标志，默认只复制当前平台）
skopeo copy \
  --all \
  docker://registry.example.com/nginx:latest \
  dir:/tmp/nginx-full-multiarch

# 3b. 仅复制指定平台（最精确控制）
skopeo copy \
  --multi-arch=specific \
  --platform linux/amd64,linux/arm64 \
  docker://registry.example.com/nginx:latest \
  docker://registry.mirror.com/nginx:latest

# 3c. 最宽松策略（复制当前能运行的架构）
skopeo copy \
  --multi-arch=most-permissive \
  docker://registry.example.com/nginx:latest \
  dir:/tmp/nginx-permissive

# 3d. 将多架构 OCI 目录推送到注册表
skopeo copy \
  --all \
  --dest-format oci \
  dir:/tmp/nginx-oci \
  docker://registry.mirror.com/nginx:latest
```

## 场景 4：从 Docker daemon 复制到 OCI 目录

```bash
# 4a. 从本地 Docker daemon 读取镜像
skopeo copy \
  docker-daemon:image-name:tag \
  oci:/tmp/from-docker-daemon

# 4b. 验证 OCI 目录内容
skopeo inspect oci:/tmp/from-docker-daemon

# 4c. 推送到远程注册表
skopeo copy \
  oci:/tmp/from-docker-daemon \
  docker://registry.example.com/myimage:latest
```

## 场景 5：保存 digest 到文件（供后续 CI/CD 使用）

```bash
# 复制时同时输出 manifest digest 到文件
skopeo copy \
  --digestfile /tmp/nginx.digest \
  docker://registry.example.com/nginx:latest \
  dir:/tmp/nginx-copied

# 读取 digest（用于精确引用）
cat /tmp/nginx.digest
# sha256:abcdef1234...

# 用 digest 精确引用（防篡改）
skopeo inspect docker://registry.example.com/nginx@sha256:abcdef1234...
```

## 常用标志速查表

| 标志 | 默认值 | 说明 |
|------|--------|------|
| `--all` | false | 复制 multi-arch 全部架构 |
| `--multi-arch` | most-permissive | 多架构策略：all/most-permissive/specific |
| `--remove-signatures` | false | 复制时去除原签名 |
| `--sign-by=<fingerprint>` | 无 | 复制后用指定 GPG key 签名 |
| `--digestfile=<path>` | 无 | 输出目标 digest 到文件 |
| `--dest-format=oci` | docker | 目标格式：oci/docker |
| `--dest-compress` | true | 压缩目标层 |
| `--dest-tls-verify` | true | 验证目标端 TLS |
| `--image-parallel-copies` | 3 | 并行拷贝层数 |
| `--strip-removed-platforms` | false | 移除 manifest list 中已删除的 platform |

## 常见错误排查

```bash
# 错误：tls-verify 失败
# 原因：目标注册表使用自签证书
# 解决：--dest-tls-verify=false（仅测试环境）或使用 --cert-dir 指定 CA

# 错误：namespace not found
# 原因：Docker Hub 新注册表规则要求命名空间
# 解决：使用完整路径 docker://docker.io/library/nginx:latest

# 错误：manifest unknown
# 原因：镜像 tag 不存在或已删除
# 解决：先用 skopeo list-tags 确认 tag 存在
```

## 相关概念
- [/concepts/00-introduction.md](../concepts/00-introduction.md) — skopeo 传输协议总览
- [/concepts/01-copy-architecture.md](../concepts/01-copy-architecture.md) — copy 命令源码结构与标志组详解
