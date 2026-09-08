---
type: Concept
title: "sync 批量同步命令与 YAML 配置驱动"
description: "skopeo sync 命令的三种源传输（docker/dir/yaml）、regexp/semver 过滤机制、dry-run 预演与镜像批量迁移。"
tags: [skopeo, sync-command, yaml-config, regexp-filter, semver-filter, batch-migration]
generated: { by: "reference_agent/trae-cn", at: 2026-09-08T11:45:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-08T11:45:00+08:00 }
status: stable
stale_after: 2027-09-08
sources:
  - id: skopeo-sync
    resource: /references/source.md
    title: skopeo 源码与文档信源登记
---

# sync 批量同步命令与 YAML 配置驱动

`skopeo sync` 是面向批量镜像同步的命令，支持从 Docker 仓库、本地目录或 YAML 配置文件批量拉取并推送到目标位置。核心设计哲学是**配置驱动 + 过滤可声明**，适合 CI/CD 流水线中的镜像归档与镜像仓库复制场景。

## 基本语法

```bash
skopeo sync [flags] <source> <destination>
```

`<source>` 和 `<destination>` 均为 image reference，但 source 支持额外的传输协议类型（`yaml:`）。

## 三种源传输模式

### 模式 1：docker — 从远程仓库同步

```bash
# 从 Docker Hub 同步所有镜像到私有仓库
skopeo sync --src docker docker://registry.example.com/all \
            --dest docker docker://mirror.registry.com/all

# 带认证
skopeo sync --src docker --creds user:pass \
            docker://docker.io/library \
            docker://mirror.registry.com/library
```

### 模式 2：dir — 从本地目录同步

```bash
# 将本地 dir:/tmp/images 下的所有 OCI/Docker 镜像同步到远程
skopeo sync --src dir dir:/tmp/images \
            --dest docker docker://registry.example.com/imported
```

### 模式 3：yaml — 从配置文件同步（最灵活）

YAML 配置文件是 `sync` 最强大的功能，支持正则匹配、semver 约束、独立凭证等细粒度控制。

```yaml
# sync-config.yaml
docker://registry.example.com/myapp:
  images:
    app-server: ["v1.0.0", "v1.1.0", "latest"]      # 精确指定
    worker: ["^v2\."]                                  # 正则匹配（v2.x.x）
  images-by-tag-regex:
    ".*": "^stable-$"                                  # 标签正则过滤
  images-by-semver:
    legacy-app: ">=1.0.0 <2.0.0"                       # semver 约束
  credentials:
    username: deploy
    password-file: ~/.secrets/reg-pass
  tls-verify: true
  cert-dir: /etc/container-certs

docker://docker.io/library:
  images-by-semver:
    nginx: "^1.27"
    redis: "^7"
```

```bash
# 执行同步
skopeo sync --src yaml sync-config.yaml \
            --dest docker docker://mirror.registry.com/imported \
            --scoped   # 用源路径作为命名空间前缀
```

## 核心过滤机制

### 正则过滤（ImagesByTagRegex）

```go
// sync.go 中的过滤集合
type tagRegexFilterCollection map[string]string  // image → regex
```

正则表达式以 `^` 开头表示前缀匹配，如 `"^v2\."` 匹配所有 `v2.x.x` 标签。

### Semver 约束过滤（ImagesBySemver）

使用 [Masterminds/semver/v3](https://github.com/Masterminds/semver) 库，支持语义化版本约束：

```yaml
images-by-semver:
  myapp: ">=1.0.0 <2.0.0"     # 区间约束
  redis: "^7"                 # 主版本 7 的所有次版本
  nginx: "~1.27"              # 1.27.x 系列的 patch 更新
```

## 关键标志

```bash
# 预览模式（dry-run）：只显示将要同步的镜像列表，不执行实际复制
skopeo sync --dry-run --src yaml sync-config.yaml --dest docker docker://mirror.local/app

# 保持源命名空间（scoped）：目标路径自动加上源 registry 前缀
skopeo sync --scoped ...

# 附加后缀（append-suffix）：在所有镜像名后加后缀
skopeo sync --append-suffix -backup ...

# 持续运行（keep-going）：一个镜像失败不中断整个同步
skopeo sync --keep-going ...

# 全量复制（all）：包含 manifest list 全部架构
skopeo sync --all ...
```

## 目标传输协议限制

目标只支持 `docker:` 和 `dir:` 两种传输：

| 目标传输 | 说明 | 典型用途 |
|---------|------|---------|
| `docker:` | 推送到远程注册表 | 镜像仓库复制 |
| `dir:` | 写入本地目录 | 镜像归档备份 |

## 同步流程（源码视角）

```
parseImageName(srcRef)
    ↓
根据源传输类型分发：
├── "docker" → listTags(srcRef) → 遍历标签 → copy.Image()
├── "dir"    → os.ReadDir(dirPath) → 解析 manifest → copy.Image()
└── "yaml"   → 读取 YAML → 解析 sourceConfig → 对每个 registry 分发
                                         ↓
                              应用 tagRegexFilterCollection
                              应用 semverFilterCollection
                                         ↓
                              遍历匹配镜像 → copy.Image()
    ↓
所有 copy.Image() 调用共享同一份 copyOptions（来自 CLI 标志）
```

## 相关概念
- [/concepts/00-introduction.md](00-introduction.md) — skopeo 传输协议与架构总览
- [/concepts/01-copy-architecture.md](01-copy-architecture.md) — copy 命令是 sync 的内部执行单元
