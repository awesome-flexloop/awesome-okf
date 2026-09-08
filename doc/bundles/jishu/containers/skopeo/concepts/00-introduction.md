---
type: Concept
title: "skopeo 概述与传输协议架构"
description: "skopeo 无守护进程的远程镜像仓库操作工具、6 种传输协议架构、Cobra CLI 框架与核心命令设计哲学。"
tags: [skopeo, transport-protocols, oci, docker-image, daemonless, cobra, containers-storage]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T11:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08T11:00:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: skopeo-readme
    resource: /references/source.md
    title: skopeo 源码与文档信源登记
---

# skopeo 概述与传输协议架构

skopeo 是 [Podman Container Tools](https://github.com/containers/skopeo)（CNCF Sandbox 项目）的三大核心工具之一，定位是**无守护进程（daemonless）的远程镜像仓库操作工具**。与 Podman 管理容器生命周期、Buildah 专注镜像构建不同，skopeo 聚焦于镜像元数据读取、远程仓库操作与镜像迁移——它不需要任何容器运行时，也不需要守护进程，仅凭 Go 标准库与 `containers/image` 传输层即可完成所有操作。

## 设计哲学：为什么需要 skopeo？

容器运行时（Podman/Docker）擅长运行容器，镜像存储驱动（Buildah/storage）擅长构建镜像，但当场景变为"跨注册表迁移"、"查看远程镜像元数据而不拉取"、"离线镜像归档与恢复"时，直接调用运行时显得笨重甚至不可行。skopeo 填补了这一空白：

| 场景 | 传统方式 | skopeo 方式 |
|------|---------|------------|
| 查看远程镜像标签列表 | `podman pull` 拉取全部层 | `skopeo list-tags` 只读清单 |
| 跨仓库迁移镜像 | 先 pull 再 push（网络往返 2x） | `skopeo copy` 流式直通复制 |
| 格式转换（Docker↔OCI） | 手动解压/重组 layers.json | `skopeo copy --dest-format` 自动转换 |
| 批量同步镜像 | 手写脚本逐条 copy | `skopeo sync` 配置化批量处理 |
| 删除远端镜像 | 无标准 CLI 命令 | `skopeo delete` 直接删除 |

## 6 种传输协议架构

skopeo 的核心抽象是 **Image Reference（镜像引用）**——一个字符串标识符，前缀决定传输协议，后缀决定具体目标。所有命令的第一个非标志参数都是 image reference。

### 协议前缀与用途

```
<transport>:<reference>

传输协议（6 种）：
┌─────────────────────┬──────────────────────────┬─────────────────────────┐
│ 协议前缀             │ 含义                     │ 典型用途                │
├─────────────────────┼──────────────────────────┼─────────────────────────┤
│ containers-storage: │ Podman/Buildah 本地存储   │ 访问本地已拉取的镜像     │
│ dir:                │ 目录格式（OCI 或 Docker） │ 离线镜像传输、备份       │
│ docker:             │ Docker Hub / 私有 Registry│ 标准镜像仓库交互         │
│ docker-archive:     │ Docker save 归档文件      │ 离线镜像导入导出         │
│ docker-daemon:      │ 本地 Docker daemon        │ 与 Docker 引擎交互       │
│ oci:                │ OCI Image Layout          │ OCI 格式镜像仓库         │
└─────────────────────┴──────────────────────────┴─────────────────────────┘
```

### 传输协议示例

```bash
# containers-storage：访问本地 Podman 存储（无需网络）
skopeo inspect containers-storage:localhost/nginx:latest

# docker：Docker Hub 官方镜像
skopeo inspect docker://nginx:latest

# dir：本地目录格式的镜像
skopeo copy dir:/tmp/my-image oci:/tmp/my-oci-image

# docker-archive：Docker save 产出的 tar 文件
skopeo copy docker-archive:/tmp/nginx.tar docker://registry.example.com/nginx:latest

# oci：OCI 布局目录
skopeo copy oci:/tmp/my-oci docker://registry.example.com/nginx:latest
```

### 隐含 docker:// 前缀

当 image reference 不含已知传输协议前缀时，skopeo 隐式加上 `docker://`：

```bash
# 以下两条命令等价
skopeo inspect nginx:latest
skopeo inspect docker://nginx:latest
```

## CLI 架构：Cobra 命令树

skopeo 使用 [spf13/cobra](https://github.com/spf13/cobra) CLI 框架，命令结构扁平且所有子命令共享全局标志组。

```
skopeo
├── --debug              调试模式输出
├── --log-level=<level>  日志级别 (debug/info/warn/error)
├── --tls-verify=<bool>  默认 true；禁用 HTTPS 证书校验（仅用于测试）
│
├── copy <src> <dest>    复制镜像（核心命令）
├── delete <image>       删除远端镜像
├── inspect <image>      检查镜像元数据
├── list-tags <registry> 列出仓库标签
├── login [registry]     认证登录
├── logout [registry]    认证登出
├── sync <src> <dest>    批量同步镜像
├── manifest-digest <image> 计算 manifest digest
├── standalone-sign <image>   独立签名（notary）
├── standalone-verify <image> 独立验证签名
└── generate-sigstore-key          生成 Sigstore 密钥
```

## 共享标志组：TLS/认证/压缩统一配置

skopeo 的大部分命令共享同一组传输标志（定义为 `sharedCopyOptions`），避免每个命令重复定义：

```
全局共享标志（所有传输命令通用）：
  --tls-verify=bool        验证 TLS 证书（默认 true）
  --creds=[user[:password]] 认证信息（username/password）
  --identity-token=<token>  Identity token（用于 OAuth2）
  --authfile=<path>        认证文件路径（默认 ~/.config/containers/auth.json）
  --cert-dir=<path>        证书目录（用于 mTLS）
  --dest-compress=bool     压缩目标层（默认 true）
  --dest-no- Opt=true      禁用目标端优化（如 compression）
  --retry-times=<n>        重试次数
  --retry-delay=<duration> 重试间隔
```

## 命令家族的职责边界

| 命令家族 | 职责 | 是否需要运行时 | 是否需要 daemon |
|---------|------|-------------|---------------|
| **copy** | 镜像复制 + 格式转换 + 多架构处理 | 否 | 否 |
| **delete** | 删除远端镜像 | 否 | 否 |
| **inspect** | 读取镜像元数据（JSON） | 否 | 否 |
| **list-tags** | 枚举仓库标签 | 否 | 否 |
| **sync** | 批量复制（支持 YAML 配置 + 过滤） | 否 | 否 |
| **login/logout** | 凭证管理 | 否 | 否 |
| **manifest-digest** | 计算 digest | 否 | 否 |
| **standalone-sign/verify** | 镜像签名/验证 | 否 | 否 |
| **generate-sigstore-key** | 密钥生成 | 否 | 否 |

## 相关概念
- [/concepts/01-copy-architecture.md](01-copy-architecture.md) — copy 命令详细流程与 sharedCopyOptions 标志组解析
- [/concepts/02-sync-architecture.md](concepts/02-sync-architecture.md) — sync 批量同步命令与 YAML 配置驱动机制
