---
type: Concept
title: "构建流水线：from → run → commit"
description: "buildah 核心构建三步流程的源码实现、BuilderOptions/CommitOptions/RunOptions 配置详解、ONBUILD 指令处理。"
tags: [buildah, builder-options, commit-options, run-options, onbuild, build-flow]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T12:15:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08 T12:15:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: buildah-main
    resource: /references/source.md
    title: buildah 源码与文档信源登记
---

# 构建流水线：from → run → commit

Buildah 的核心构建流程由三个关键步骤组成：**from**（创建 working container）、**run**（执行构建命令）和 **commit**（提交为镜像）。每一步都有对应的 Go 源码结构体和核心调用链，理解这些结构体是掌握 Buildah 编程模型的基础。

## 第一步：from —— 创建 working container

入口：`cmd/buildah/from.go` → `fromCmd()` → `buildah.NewBuilder()`

```
fromCmd()
  ↓
getStore()  — 获取 containers/storage 实例
  ↓
buildah.NewBuilder(ctx, store, options)
  ├── FromImage:  "docker.io/library/alpine:latest" 或 "scratch"
  ├── Container:  "my-working-container"           （working container 名称）
  ├── PullPolicy: always | missing | never | newer
  ├── Format:     oci | docker                     （输出格式）
  ├── NamespaceOptions             （UTS/IPC/NET/PID/USER namespace）
  ├── IDMappingOptions             （UID/GID 映射）
  └── Isolation:  chroot | nsexec | proot          （隔离模式）
  ↓
onBuild(builder)  — 处理 ONBUILD 触发指令
  ↓
builder.Save()  — 持久化 working container 状态
```

### BuilderOptions 关键字段

```go
type BuilderOptions struct {
    FromImage     string           // 基础镜像（"scratch" = 空镜像）
    Container     string           // working container 名称
    PullPolicy    types.PullPolicy // always/missing/never/newer
    Format        string           // oci 或 docker
    NamespaceOptions []NamespaceOption  // 命名空间选项
    IDMappingOptions []IDMappingOption  // 用户映射
    Isolation     types.Isolation    // chroot/nsenter/proot
}
```

### ONBUILD 指令处理

`from` 命令在创建容器后会检查基础镜像是否包含 `ONBUILD` 触发指令，并自动执行：

```go
// onBuild() 支持的所有子指令
onBuild(builder) → switch onBuildCommand {
    case "CMD", "ENV", "ENTRYPOINT", "EXPOSE", "HOSTNAME",
         "LABEL", "RUN", "SHELL", "STOPSIGNAL", "USER",
         "VOLUME", "WORKINGDIR", "ADD", "COPY",
         "ANNOTATION", "MAINTAINER", "ONBUILD":
        // 执行对应的 ONBUILD 指令
}
```

## 第二步：run —— 在 working container 内执行命令

入口：`cmd/buildah/run.go` → `runCmd()` → `builder.Run()`

```
runCmd()
  ↓
openBuilder(store, containerName)  — 打开已有的 working container
  ↓
volumes.GetVolumes(...)  — 解析 --volume/--mount/--device 标志
  ↓
builder.Run(args, options)  — 执行命令（内部 fork/exec）
  ↓
builder.Save()  — 保存文件系统变更
```

### RunOptions 关键字段

```go
type RunOptions struct {
    Hostname            string              // 容器 hostname
    User                string              // 运行用户（user:group）
    WorkingDir          string              // 工作目录
    Env                 []string            // 环境变量
    AddCapabilities     []string            // 添加的 Linux capabilities
    DropCapabilities    []string            // 丢弃的 Linux capabilities
    Mounts              []spec.Mount        // 绑定挂载
    Volumes             []types.BundleVolume // 命名卷挂载
    DeviceSpecs         []spec.LinuxDevice  // 设备映射
    Isolation           types.Isolation     // chroot/nsenter/proot
    NamespaceOptions    []NamespaceOption   // 命名空间
    ConfigureNetwork    string              // network 模式
    Terminal            bool                // 是否分配 TTY
    ValidExitCodes      []int               // 有效退出码（0 默认）
    Umask               string              // umask 值
}
```

### 隔离模式选择

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `chroot` | 最简单，直接 chroot 到容器根文件系统 | 无网络需求、本地构建 |
| `nsenter` | 进入新建命名空间后 chroot | 需要网络/PID 隔离 |
| `proot` | 用户态模拟命名空间 | rootless 构建 |

## 第三步：commit —— 提交为镜像

入口：`cmd/buildah/commit.go` → `commitCmd()` → `builder.CommitResults()`

```
commitCmd()
  ↓
openBuilder(store, containerName)  — 打开 working container
  ↓
parse target image name  — 解析目标镜像引用（alltransports.ParseImageName）
  ↓
builder.CommitResults(ctx, dest, options)  — 核心提交操作
  ↓
输出 image ID 到 stdout 或 iidfile
  ↓
可选 builder.Delete()  — 提交后删除 working container
```

### CommitOptions 关键字段

```go
type CommitOptions struct {
    PreferredManifestType     string           // oci/v2s1/v2s2
    Squash                    bool             // 单 layer（合并所有层）
    Compression               string           // gzip/uncompressed
    CompressionLevel          *int             // gzip 压缩级别
    SignBy                    string           // GPG fingerprint 签名
    EncryptionKeys            []string         // 加密密钥
    EncryptLayers             []int            // 需加密的层
    SBOMScanOptions           SBOMScanOptions  // SBOM 扫描配置
    UnsetEnvs                 []string         // 清除的环境变量
    OverrideChanges           []string         // 覆盖 Containerfile RUN 指令
    OverrideConfig            *types.ImageData  // 覆盖镜像配置（CMD/ENV/USER等）
    Manifest                  string           // 关联的 manifest list digest
    Timestamp                 *int64           // 固定构建时间戳
    ForceContentDigest        bool             // 强制使用内容 digest
    Iidfile                   string           // 输出 image ID 的文件
    Quiet                     bool             // 静默模式
}
```

### commit 与 Dockerfile 的关系

```bash
# 方式 A：直接使用 Containerfile（等价于 docker build）
buildah build -f Containerfile -t myimage:latest .

# 方式 B：手工逐步构建（等价于 docker commit）
buildah from alpine:latest          # 创建 working container
buildah run mycontainer apk add curl  # 执行命令
buildah config --cmd "/app/start.sh" mycontainer  # 设置 CMD
buildah commit mycontainer myimage:latest  # 提交镜像
```

## 镜像列表与推送

```bash
# 列出本地镜像（images.go）
buildah images
# 输出：REPOSITORY  TAG  IMAGE ID  CREATED  SIZE  R/O  HISTORY

# 推送镜像（push.go）
buildah push myimage:latest docker://registry.example.com/myimage:latest

# push 支持 manifest list（多架构）
buildah push myimage:latest oci:/tmp/myimage-oci
```

## 相关概念
- [/concepts/00-introduction.md](00-introduction.md) — working container 生命周期总览
- [/examples/00-dockerfile-build.md](../examples/00-dockerfile-build.md) — 完整构建示例
