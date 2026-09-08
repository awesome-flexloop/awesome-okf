---
type: Concept
title: "copy 命令与 sharedCopyOptions 标志组"
description: "skopeo copy 核心命令的 Go 源码实现、共享标志组 design、multi-arch 处理策略、加密/解密层机制。"
tags: [skopeo, copy-command, shared-copy-options, multi-arch, encryption-layer, signature]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T11:15:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08T11:15:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: skopeo-copy
    resource: /references/source.md
    title: skopeo 源码与文档信源登记
---

# copy 命令与 sharedCopyOptions 标志组

`skopeo copy` 是整个工具集最核心、功能最丰富的命令，实现了从源镜像引用到目标镜像引用的完整复制流水线。其 Go 源码位于 `cmd/skopeo/copy.go`，入口为 `copyCmd()` 函数，核心调用为 `copy.Image(ctx, policyContext, destRef, srcRef, copyOpts)`。

## 核心调用链

```
parseImageName(srcRef)
    ↓
parseImageName(destRef)
    ↓
getPolicyContext()           ← 加载签名策略（default or custom policy.json）
    ↓
image.NewSource(ctx, srcRef, sysCtx)  ← 创建源镜像读取器
    ↓
image.NewDestination(ctx, destRef, sysCtx)  ← 创建目标镜像写入器
    ↓
copy.Image(ctx, policyContext, destRef, srcRef, copyOpts)  ← 执行复制
```

## copyOptions 结构体详解

`copyOptions` 是 copy 命令的所有可配置项的聚合体，分为以下逻辑组：

### 1. 传输选项（srcImage/destImage）

```go
type copyOptions struct {
    srcImage, destImage *imageOptions   // 来源/目标的独立传输配置
    deprecatedTLSVerify *deprecatedTLSVerifyOption
    retryOpts           *retry.Options  // 重试次数与间隔
    copy                *sharedCopyOptions  // ⭐ 共享标志组（见下文）
}
```

`imageOptions` 控制单次传输行为（如 manifest 类型选择、compression 等），独立于 `sharedCopyOptions`。

### 2. 复制行为标志

```go
type copyOptions struct {
    // ...

    additionalTags []string         // 额外 tag：复制时附带打上这些标签
    quiet          bool             // 静默模式（不输出进度）
    all            bool             // 复制 multi-arch 全部架构 manifest list
    multiArch      string           // 多架构处理策略
                                    //   "all"        复制全部架构
                                    //   "most-permissive" 最少依赖策略
                                    //   "specific"   仅复制指定架构
    signBy         string           // GPG fingerprint：用指定密钥签名
    digestFile     string           // 将目标 digest 写入指定文件
    encryptionKey  []string         // 层加密密钥（加密复制时使用）
    encryptLayer   []int            // 需加密的层索引
    decryptionKey  []string         // 层解密密钥（解密复制时使用）
    imageParallelCopies uint       // 并行拷贝层数（默认 3）
    stripRemovedPlatforms bool     // 移除 manifest list 中已删除的 platform
}
```

### 3. sharedCopyOptions 共享标志组（核心）

这是 skopeo 设计中最精巧的部分：**一组在多个命令间共享的传输标志**，由 `commonFlag.SharedFlags()` 构建：

```go
type sharedCopyOptions struct {
    // 安全相关
    tlsVerify  commonFlag.OptionalBool  // 可选 bool：true/false/enable/disable/skip
    compress   commonFlag.OptionalBool
    decompress commonFlag.OptionalBool

    // 认证相关
    srcAuth, destAuth string           // 来源/目标独立认证（覆盖 authfile）
    username, password string          // 命令行内联认证
    identityToken     string            // OAuth2 token
    authfile          string            // ~/.config/containers/auth.json

    // 证书相关
    certDir string                // mTLS 证书目录
    removeSignatures bool         // 复制时不携带原签名
    signaturePolicy string        // 自定义签名策略文件
}
```

### 4. deprecatedTLSVerify 过渡标志

```go
type deprecatedTLSVerifyOption struct {
    Value bool
    Set   bool  // 是否用户显式指定
}
```

早期版本使用 `--tls-verify=false`，新版推荐 `--dest-tls-verify=false`（源/目标分离），该结构处理兼容。

## multi-arch 多架构处理策略

```bash
# 复制全部架构（含 manifest list）
skopeo copy --all docker://nginx:latest dir:/tmp/nginx-all

# 仅复制当前平台（默认行为，不指定 --all）
skopeo copy docker://nginx:latest dir:/tmp/nginx-single

# 最宽松策略：只复制当前能运行的架构
skopeo copy --multi-arch=most-permissive docker://nginx:latest dir:/tmp/nginx-most

# 指定平台
skopeo copy --multi-arch=specific --platform linux/amd64 docker://nginx:latest dir:/tmp/nginx-amd64
```

## 签名与加密控制

```bash
# 复制时保留原签名
skopeo copy docker://registry.local/nginx:latest docker://registry.remote/nginx:latest

# 复制时去除原签名（不携带）
skopeo copy --remove-signatures docker://registry.local/nginx:latest docker://registry.remote/nginx:latest

# 用 GPG 密钥重新签名
skopeo copy --sign-by 0xA1B2C3D4 docker://registry.local/nginx:latest docker://registry.remote/nginx:latest

# 加密层复制（源镜像有加密层时）
skopeo copy \
  --decryption-key file:///path/to/key.pem \
  --encryption-key file:///new/key.pem \
  docker://registry.enc/nginx:latest docker://registry.dec/nginx:latest
```

## 相关概念
- [/concepts/00-introduction.md](00-introduction.md) — skopeo 整体架构与传输协议总览
- [/concepts/02-sync-architecture.md](concepts/02-sync-architecture.md) — sync 批量同步与 copy 的关系（sync 内部复用 copy.Image）
