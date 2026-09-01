---
type: Concept
title: "ccache 与 sccache 编译缓存动作"
description: "ccache 环境变量全家桶与三级 restore-keys 回退链、Windows 专属安装路径（msvc-dev-cmd 与 300M 上限），以及 sccache 的 GCS 桶配置、RW 模式与 docker-run 参数透传。"
tags: [protobuf-ci, github-actions, ci-cache]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-ci-actions
    resource: /references/protobuf-ci-actions.md
    title: "protobuf-ci 仓库 CI 动作信源"
---

非 Bazel（CMake）构建路径的编译产物缓存由两个顶层 action 负责：ccache 与 sccache。ccache（C/C++ 编译器缓存）使用 GitHub Actions 内置 cache 存储；sccache（Mozilla 出品的共享编译缓存，Rust 实现）使用 GCS（Google Cloud Storage）桶存储。二者体现了"平台内缓存 vs 远程共享缓存"的分工——前者随 GitHub 缓存配额修剪，后者按 key prefix 跨 job 持久共享。字段级细节登记于 [/references/protobuf-ci-actions.md](/references/protobuf-ci-actions.md)。

## ccache 的环境变量全家桶

ccache action（name 'CCache Setup'）的 inputs：cache-prefix（required: true，"A unique prefix to prevent cache pollution"）、support-modules（"Whether or not we need to support modules. This can result in extra cache misses."）、vsversion（default '2019'，"The version of Visual Studio to use (Windows only)"）、ccache-version（default '4.8'，"A pinned version of ccache"）、windows-arch（default 'x64'）。

"Configure ccache environment variables" 步骤设置的完整变量集：

```yaml
CCACHE_BASEDIR=${{ github.workspace }}
CCACHE_DIR=${{ github.workspace }}/.ccache
CCACHE_COMPRESS=true
CCACHE_COMPRESSLEVEL=5
CCACHE_MAXSIZE=150M
CCACHE_SLOPPINESS=clang_index_store,include_file_ctime,include_file_mtime,file_macro,time_macros
CCACHE_DIRECT=true
```

support-modules 为真时追加 `CCACHE_SLOPPINESS=$CCACHE_SLOPPINESS,modules` 与 `CCACHE_DEPEND=true`——以额外 cache miss 为代价支持 C++ modules。

## 三级 restore-keys 回退链

缓存步骤 uses `actions/cache@9255dc7a253b0ccc959486e2bca901246202afeb`（注释 # v5.0.1），path 为 `.ccache/**` 并排除 `!.ccache/lock`、`!.ccache/tmp`。key 与 restore-keys 按注释列出的优先顺序构成三级回退链（1) 同提交 2) 当前分支 3) PR 基分支）：

| 优先级 | 键模式 | 语义 |
|---|---|---|
| 1（精确 key） | `ccache-{cache-prefix}-{github.ref_name}-{github.sha}` | 同一提交的缓存 |
| 2（restore-key） | `ccache-{cache-prefix}-{github.ref_name}` | 当前分支最近缓存 |
| 3（restore-key） | `ccache-{cache-prefix}-{github.base_ref}` | PR 基分支的缓存 |

## 平台安装与 Windows 专属路径

平台安装：Windows 委托 internal/ccache-setup-windows；macOS 直接 `brew install ccache`。随后以 compiler launcher（编译器启动器）方式把 ccache 注入 CMake：

```yaml
CCACHE_CMAKE_FLAGS=-Dprotobuf_ALLOW_CCACHE=ON -DCMAKE_C_COMPILER_LAUNCHER=$(which ccache ...) -DCMAKE_CXX_COMPILER_LAUNCHER=$(which ccache ...)
```

非 Linux runner 另执行 `ccache -z`（清零统计计数器，使命中率从本次运行重新计起）。

internal/ccache-setup-windows（name 亦为 'CCache Setup'）的安装链：uses `ilammy/msvc-dev-cmd@cec98b9d092141f74527d0afa6feb2af698cfe89`（注释 # v1.12.1）激活 MSVC 环境；设置 `CCACHE_EXE_PATH=$LOCALAPPDATA\ccache-{version}-windows-x86_64` 并写入 GITHUB_PATH；从 `https://github.com/ccache/ccache/releases/download/v{version}/ccache-{version}-windows-x86_64.zip` 下载二进制（安装器自身以 cache key `ccache-exe-${{ inputs.ccache-version }}` 缓存）。

Windows 特有变量：`CCACHE_COMPILER`（cl.exe 路径）、`CCACHE_COMPILERTYPE=msvc`、`CCACHE_COMPRESSLEVEL=10`（高于通用平台的 5）、`CCACHE_MAXSIZE=300M`（通用平台为 150M——注释原句 "Windows caches are about 2x larger than other platforms."）。

## sccache 的 GCS 桶配置

sccache action（name 'Setup sccache'）的 inputs：credentials（required: true，"The GCP credentials to use for caching"）、cache-prefix（required: true）、version（default 'v0.5.4'）。"Validate cache name" 步骤先做格式校验：cache-prefix 含 '+' 或空格时经 `actions/github-script@ed597411d8f924073f98dfc5c65a23a2325f34cd`（注释 # v8.0.0 (Node 24)）执行 `core.setFailed('Cache prefixes can't contain symbols or spaces.')`。

internal/gcloud-auth 之后设置的变量集：

```yaml
SCCACHE_GCS_KEY_PATH=${{ steps.auth.outputs.credentials-file }}
SCCACHE_GCS_BUCKET=protobuf-sccache
SCCACHE_GCS_KEY_PREFIX=${{ inputs.cache-prefix }}
SCCACHE_IDLE_TIMEOUT=0
SCCACHE_IGNORE_SERVER_IO_ERROR=1
```

"Enable sccache cache writing" 步骤再设置 `SCCACHE_GCS_RW_MODE=READ_WRITE`（注释引用 mozilla/sccache#1886，说明该 RW 模式依赖的上游能力）。

安装与预热：非 Linux 平台 uses `mozilla-actions/sccache-action@9e7fa8a12102821edf02ca5dbea1acd0f89a2696`（注释 # v0.0.10 (Node 24)，传 version 参数）；随后经 nick-fields/retry#v4.0.0（timeout_minutes: 5、retry_wait_seconds: 60、max_attempts: 5、continue_on_error: true）执行 `sccache --start-server`；并设置 `SCCACHE_CMAKE_FLAGS=-DCMAKE_C_COMPILER_LAUNCHER=sccache -DCMAKE_CXX_COMPILER_LAUNCHER=sccache`；非 Linux 执行 `sccache -z`。

## docker-run 的 sccache 参数透传

容器化构建同样能使用 sccache：internal/docker-run 的 "Forward sccache arguments" 步骤在 `SCCACHE_GCS_KEY_PATH != ''` 时生成透传参数：

```yaml
-e SCCACHE_GCS_RW_MODE=... -e SCCACHE_GCS_BUCKET=... -e SCCACHE_GCS_KEY_PREFIX=... -e SCCACHE_GCS_KEY_PATH=/workspace/$(basename ...)
```

最终执行 `docker run {args} {run-flags} -v${{ github.workspace }}:/workspace ${{ inputs.image }} ${{ inputs.command }}`——凭据文件取 basename 后挂进容器的 /workspace/，使容器内外的 sccache 共享同一 GCS 桶。

## 相关概念

- [/concepts/02-bazel-build-actions.md](/concepts/02-bazel-build-actions.md) — bazel 与 bazel-docker 构建动作及远程缓存
- [/concepts/04-docker-checkout-bash-actions.md](/concepts/04-docker-checkout-bash-actions.md) — docker、checkout、bash 基础动作与 internal 基建
- [/concepts/01-repo-positioning-and-structure.md](/concepts/01-repo-positioning-and-structure.md) — 仓库定位与结构：可复用 CI 动作集合
