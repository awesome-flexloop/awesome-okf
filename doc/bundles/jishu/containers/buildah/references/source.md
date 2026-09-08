---
type: SourceReference
title: "buildah 源码与文档信源登记"
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T10:00:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: buildah-readme
    url: "https://github.com/containers/buildah/blob/main/README.md"
    type: upstream
  - id: buildah-main
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/main.go"
    type: source-code
  - id: buildah-build
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/build.go"
    type: source-code
  - id: buildah-from
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/from.go"
    type: source-code
  - id: buildah-commit
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/commit.go"
    type: source-code
  - id: buildah-run
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/run.go"
    type: source-code
  - id: buildah-images
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/images.go"
    type: source-code
  - id: buildah-push
    path: "external/dao/action/podman-container-tools/buildah/cmd/buildah/push.go"
    type: source-code
  - id: github-profile
    path: "external/dao/action/podman-container-tools/.github/profile/README.md"
    type: upstream
---

# buildah 源码与文档信源登记

## 信源定位

| 名称 | 路径/URL | 类型 | 说明 |
|------|---------|------|------|
| README.md | [GitHub](https://github.com/containers/buildah/blob/main/README.md) | upstream | 官方项目说明，含 22 个命令分组表格与定位说明 |
| cmd/buildah/main.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/main.go` | source-code | CLI 入口，4 个命令分组常量，全局标志，30+ 子命令注册 |
| cmd/buildah/build.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/build.go` | source-code | build/bud 命令：Containerfile 构建入口 |
| cmd/buildah/from.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/from.go` | source-code | from 命令：创建 working container |
| cmd/buildah/commit.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/commit.go` | source-code | commit 命令：将 working container 写入镜像 |
| cmd/buildah/run.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/run.go` | source-code | run 命令：在 working container 内执行命令 |
| cmd/buildah/images.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/images.go` | source-code | images 命令：列出本地镜像 |
| cmd/buildah/push.go | `external/dao/action/podman-container-tools/buildah/cmd/buildah/push.go` | source-code | push 命令：推送镜像到注册表 |
| .github/profile/README.md | `external/dao/action/podman-container-tools/.github/profile/README.md` | upstream | CNCF Sandbox 项目整体介绍，含 Podman/Buildah/Skopeo/container-libs 关系 |

## 核心代码事实（Grep 级可验证）

### 22 个命令分 4 组（来自 main.go 常量定义）

| GroupID | 命令数量 | 命令列表 |
|---------|---------|---------|
| groupImages (images) | 8 | images、pull、push、tag、rmi、manifest、info、prune |
| groupContainers (containers) | 8 | containers、from、run、commit、config、build、mount、umount |
| groupRegistries (registries) | 3 | login、logout、source |
| groupSystem (system) | 3 | version、rpc、sftp |

### buildah from 核心流程（from.go）

```
fromCmd() → getStore() → buildah.NewBuilder(getContext(), store, options)
         → onBuild(builder)  // 处理 ONBUILD 指令
         → builder.Save()
```

`BuilderOptions` 关键字段：
- `FromImage`: 基础镜像名或 "scratch"
- `Container`: working container 名称
- `PullPolicy`: always/missing/never/newer
- `Format`: OCI 或 Docker 格式
- `NamespaceOptions`, `IDMappingOptions`, `Isolation`: 隔离与命名空间

### buildah commit 核心流程（commit.go）

```
commitCmd() → openBuilder(store, containerName)
           → parse target image name (alltransports.ParseImageName)
           → builder.CommitResults(ctx, dest, options)
           → 输出 image ID 到 stdout 或 iidfile
           → 可选 builder.Delete()
```

`CommitOptions` 关键字段：
- `PreferredManifestType`: oci/v2s1/v2s2
- `Squash`: 单 layer
- `Compression`: gzip/uncompressed
- `SignBy`: GPG fingerprint
- `EncryptionKeys`/`EncryptLayers`: 层加密
- `SBOMScanOptions`: SBOM 扫描
- `UnsetEnvs`/`OverrideChanges`/`OverrideConfig`: 配置覆盖
- `Manifest`: 关联 manifest list

### buildah build 核心流程（build.go）

```
buildCmd() → buildahcli.GenBuildOptions(c, inputArgs, iopts)
          → imagebuildah.BuildDockerfiles(getContext(), store, options, containerfiles...)
```

别名：`bud`、`build-using-dockerfile`

### buildah run 核心流程（run.go）

```
runCmd() → openBuilder(store, containerName)
        → volumes.GetVolumes(...)  // 挂载卷和设备
        → builder.Run(args, options)
        → builder.Save()  // 保存状态变更
```

`RunOptions` 关键字段：
- `Hostname`, `User`, `WorkingDir`, `Env`
- `AddCapabilities`/`DropCapabilities`
- `Mounts`/`Volumes`/`DeviceSpecs`
- `Isolation`: chroot/nsenter/proot
- `NamespaceOptions`, `ConfigureNetwork`
- `Terminal`, `ValidExitCodes`, `Umask`

### buildah images 输出结构（images.go）

```go
type jsonImage struct {
    ID        string
    Names     []string
    Digest    string
    CreatedAt string   // human-readable relative time
    Size      string   // human-readable (KB/MB/GB)
    ReadOnly  bool
    History   []string
}
```

表格列：REPOSITORY / TAG / IMAGE ID / CREATED / SIZE / R/O / HISTORY

## 定位说明

Buildah 定位为**专注于构建 OCI 镜像的低层 coreutils 接口**，不同于 Podman 的完整容器生命周期管理。核心概念区分：
- **Buildah container（working container）**：临时构建环境，用完即弃，不持久运行
- **Podman container（传统容器）**：长期运行的容器实例
- 两者存储隔离，互不可见
