---
type: SourceReference
title: "skopeo 源码与文档信源登记"
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T10:00:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: skopeo-readme
    url: "https://github.com/containers/skopeo/blob/main/README.md"
    type: upstream
  - id: skopeo-copy
    path: "external/dao/action/podman-container-tools/skopeo/cmd/skopeo/copy.go"
    type: source-code
  - id: skopeo-delete
    path: "external/dao/action/podman-container-tools/skopeo/cmd/skopeo/delete.go"
    type: source-code
  - id: skopeo-sync
    path: "external/dao/action/podman-container-tools/skopeo/cmd/skopeo/sync.go"
    type: source-code
  - id: skopeo-inspect
    path: "external/dao/action/podman-container-tools/skopeo/cmd/skopeo/inspect.go"
    type: source-code
  - id: skopeo-login
    path: "external/dao/action/podman-container-tools/skopeo/cmd/skopeo/login.go"
    type: source-code
  - id: skopeo-main
    path: "external/dao/action/podman-container-tools/skopeo/cmd/skopeo/main.go"
    type: source-code
---

# skopeo 源码与文档信源登记

## 信源定位

| 名称 | 路径/URL | 类型 | 说明 |
|------|---------|------|------|
| README.md | [GitHub](https://github.com/containers/skopeo/blob/main/README.md) | upstream | 官方项目说明，含功能概述、传输协议与命令表格 |
| cmd/skopeo/copy.go | `external/dao/action/podman-container-tools/skopeo/cmd/skopeo/copy.go` | source-code | 核心 copy 命令：共享标志组、multiArch 处理、加密/解密层 |
| cmd/skopeo/delete.go | `external/dao/action/podman-container-tools/skopeo/cmd/skopeo/delete.go` | source-code | delete 命令：单参数校验、alltransports.ParseImageName、ref.DeleteImage |
| cmd/skopeo/sync.go | `external/dao/action/podman-container-tools/skopeo/cmd/skopeo/sync.go` | source-code | sync 命令：docker/dir/yaml 三种源传输、regexp/semver 过滤、dry-run 支持 |
| cmd/skopeo/inspect.go | `external/dao/action/podman-container-tools/skopeo/cmd/skopeo/inspect.go` | source-code | inspect 命令：JSON 输出、Go 模板格式化、raw/config 选项、manifest digest 算法可选 |
| cmd/skopeo/login.go | `external/dao/action/podman-container-tools/skopeo/cmd/skopeo/login.go` | source-code | login 命令：使用 go.podman.io/common/pkg/auth，tls-verify flag |
| cmd/skopeo/main.go | `external/dao/action/podman-container-tools/skopeo/cmd/skopeo/main.go` | source-code | 程序入口，注册所有子命令，全局选项（debug/logLevel/tlsVerify） |

## 核心代码事实（Grep 级可验证）

### 命令分组与子命令列表（来自 README + cmd 文件）

| 命令 | Go 文件 | 核心功能 |
|------|--------|---------|
| copy | copy.go | 镜像复制，支持 6 种传输协议，多架构，加密/解密层 |
| delete | delete.go | 删除仓库中指定镜像 |
| inspect | inspect.go | 检查镜像元数据，支持 JSON/模板/ raw 输出 |
| list-tags | list_tags.go | 列出仓库中所有标签 |
| login | login.go | 认证登录容器注册表 |
| logout | logout.go | 登出容器注册表 |
| sync | sync.go | 批量同步镜像，支持 docker/dir/yaml 源，regexp/semver 过滤 |
| generate-sigstore-key | generate_sigstore_key.go | 生成 Sigstore 密钥 |
| manifest-digest | manifest.go | 计算 manifest digest |
| standalone-sign | signing.go | 独立签名镜像（notary） |
| standalone-verify | signing.go | 独立验证签名 |

### 传输协议（6 种，来自 README + alltransports 导入）

| 协议 | 说明 | 典型用途 |
|------|------|---------|
| `containers-storage:` | Podman/Buildah 本地存储 | 访问本地已拉取的镜像 |
| `dir:` | 目录格式（OCI 或 Docker） | 离线镜像传输、备份 |
| `docker:` | Docker Hub / 私有 Registry | 标准镜像仓库交互 |
| `docker-archive:` | Docker save 归档文件 | 离线镜像导入导出 |
| `docker-daemon:` | 本地 Docker daemon | 与 Docker 引擎交互 |
| `oci:` | OCI Image Layout | OCI 格式镜像仓库 |

### skopeo copy 核心结构（copy.go）

```go
// copyOptions 结构体关键字段
type copyOptions struct {
    // 传输选项
    srcImage, destImage     *imageOptions
    deprecatedTLSVerify     *deprecatedTLSVerifyOption
    retryOpts               *retry.Options
    copy                    *sharedCopyOptions  // 共享标志组（TLS/认证/压缩等）

    // 复制行为
    additionalTags          []string
    quiet                   bool
    all                     bool                   // 复制 multi-arch 全部架构
    multiArch               string                 // ImageListSelection: all/most-permissive/specific
    signBy                  string                 // GPG fingerprint 签名
    digestFile              string
    encryptionKey           []string
    encryptLayer            []int
    decryptionKey           []string
    imageParallelCopies     uint                   // 并行拷贝数
    stripRemovedPlatforms   bool
}
```

核心调用链：
```
parseImageName(srcRef) → parseImageName(destRef)
→ getPolicyContext() → image.NewSource(ctx, srcRef, sysCtx)
→ image.NewDestination(ctx, destRef, sysCtx)
→ copy.Image(ctx, policyContext, destRef, srcRef, copyOpts)
```

### sync 命令关键结构（sync.go）

```go
// syncOptions 支持三种源传输
type syncOptions struct {
    source   string  // "docker" | "dir" | "yaml"
    destination string // "docker" | "dir"
    scoped   bool    // 是否用源路径作为命名空间前缀
    all      bool
    dryRun   bool
    keepGoing bool
    appendSuffix string
}

// sourceConfig 从 YAML 文件读取
type sourceConfig map[string]registrySyncConfig  // registry → config
type registrySyncConfig struct {
    Images           map[string][]string  // 精确引用列表
    ImagesByTagRegex map[string]string    // 正则过滤
    ImagesBySemver   map[string]string    // semver 约束过滤
    Credentials      types.DockerAuthConfig
    TLSVerify        tlsVerifyConfig
    CertDir          string
}
```

### inspect 命令输出结构（inspect.go）

```go
// 输出数据结构
type Output struct {
    Name          string
    Tag           string
    RepoTags      []string
    Created       *time.Time
    DockerVersion string
    Labels        map[string]string
    Architecture  string
    Os            string
    Layers        []string
    LayersData    []map[string]string
    Env           []string
    Digest        digest.Digest
}
```

## 项目背景

skopeo 是 [Podman Container Tools](https://github.com/containers/podman-container-tools)（CNCF Sandbox 项目）的三大核心工具之一，与 Buildah、Podman 并列。项目地址：`external/dao/action/podman-container-tools/skopeo/`。

构建依赖：`go.podman.io/image/v5`（镜像传输核心库）、`go.podman.io/common`（认证/重试等公共工具）、`spf13/cobra`（CLI 框架）。
