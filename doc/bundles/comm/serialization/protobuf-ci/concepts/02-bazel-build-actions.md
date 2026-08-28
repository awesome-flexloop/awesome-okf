---
type: Concept
title: "bazel 与 bazel-docker 构建动作及远程缓存"
description: "protobuf-ci 两条 Bazel 执行路径：宿主机 bazel 与容器 bazel-docker 的步骤对比、BAZEL_FLAGS 拼装、bazelisk 缓存、GCS 远程缓存与 repository cache save/restore 配对。"
tags: [protobuf-ci, github-actions, bazel]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-ci-actions
    resource: /references/protobuf-ci-actions.md
    title: "protobuf-ci 仓库 CI 动作信源"
---

Bazel 构建在 protobuf-ci 中有两条顶层执行路径：bazel（在宿主机 runner 上直接运行 Bazel）与 bazel-docker（在 docker 容器内运行 Bazel）。两者的 action.yml 里 name 字段同为 'Docker Bazel Run'、description 同为 'Run a Bazel-based docker image for Protobuf CI testing'（源码原文如此）。二者都经由 internal/bazel-setup 完成 BAZEL_FLAGS 基线与远程缓存装配，末尾都以 repository cache 保存收束；核心差异在于容器路径需要 /workspace/ 前缀的凭据与缓存挂载。字段级细节见 [/references/protobuf-ci-actions.md](/references/protobuf-ci-actions.md)。

## bazel：宿主机执行路径

inputs：

| input | 必填 | 默认 | 说明 |
|---|---|---|---|
| credentials | 是 | — | GCP 凭据 |
| bazel-cache | 是 | — | 描述称 "This will trigger the generation of a BAZEL_CACHE environment variable inside the container" |
| version | 否 | '6.4.0' | Bazel 版本 |
| bazel | 否 | — | "The Bazel command to run" |
| bash | 否 | — | 描述注明 "$BAZEL_FLAGS and $BAZEL_STARTUP_FLAGS will be available" |
| exclude-targets | 否 | — | "Bazel target patterns to exclude. Each pattern must be prefixed with a minus sign." |
| bazel-flags | 否 | — | 追加到 BAZEL_FLAGS 的标志 |

步骤序列：Symlink → uses internal/gcloud-auth（id: auth）→ uses internal/setup-runner → uses internal/bazel-setup（id: bazel，传入 credentials-file 与 bazel-cache）。

执行分支：inputs.bash 存在时直接 `run: ${{ inputs.bash }}`；否则执行 `bazelisk ${{ steps.bazel.outputs.bazel-startup-flags }} ${{ inputs.bazel }} $BAZEL_FLAGS ... -- {exclude-targets}`。末尾非 PR 事件调用 internal/repository-cache-save。

## bazel-docker：容器执行路径

inputs 与 bazel 基本一致，差异是多出必填的 image（"The docker image to use"），且 bash 描述只承诺 "$BAZEL_FLAGS will be available"（无 startup flags）。两条路径的环节对比：

| 环节 | bazel（宿主） | bazel-docker（容器） |
|---|---|---|
| 镜像哈希 | 无 | "Calculate Image Hash" 步骤：`echo ${{ inputs.image }} \| md5sum \| cut -f1 -d' '` |
| bazel-cache 键 | 原样传入 bazel-setup | 追加 `-${{ steps.image-hash.outputs.value }}` |
| 凭据路径 | credentials-file 原样 | credentials-file 前缀 `/workspace/` |
| repository_cache | `--repository_cache=$(pwd)/${{ env.REPOSITORY_CACHE_PATH }}` | `--repository_cache='/workspace/${{ env.REPOSITORY_CACHE_PATH }}'` |
| bash 模式执行 | 宿主 `run: ${{ inputs.bash }}` | uses internal/docker-run，run-flags: `--entrypoint "/bin/bash"`，command: `-l -c "${{ inputs.bash }}"` |
| bazel 模式执行 | 宿主 bazelisk 命令 | uses internal/docker-run，command: `${{ inputs.bazel }} ${{ env.BAZEL_FLAGS }} ...` |

两条路径都有 Validate inputs 步骤：bash 与 bazel 同时给出（或同时缺省）时 `exit 1`。

## internal/bazel-setup 与 BAZEL_FLAGS 拼装

internal/bazel-setup（name 'Setup Bazel'）设置 `BAZEL=bazelisk`、基线 `BAZEL_FLAGS=--keep_going --test_output=errors --test_timeout=600`，并输出 bazel-flags 与 bazel-startup-flags 两个 outputs。bazel action 在基线之上追加两步环境变量拼装：

```yaml
BAZEL_FLAGS=$BAZEL_FLAGS --repository_cache=$(pwd)/${{ env.REPOSITORY_CACHE_PATH }}
BAZEL_FLAGS=$BAZEL_FLAGS ${{ inputs.bazel-flags }}
```

随后设置 `USE_BAZEL_VERSION=${{ inputs.version }}` 并执行 `bazelisk version`。

## bazelisk 版本缓存

bazelisk（Bazel 版本管理器）自身缓存路径按 OS 决定：Linux `~/.cache/bazelisk`、macOS `~/Library/Caches/bazelisk`、Windows `$LOCALAPPDATA\bazelisk`。该缓存由 actions/cache 管理：非 PR 事件 uses `actions/cache@9255dc7a253b0ccc959486e2bca901246202afeb`（注释 # v5.0.1 (Node 24)），key 为 `bazel-${{ runner.os }}-${{ inputs.version }}`；PR 事件改用 `actions/cache/restore`（同 SHA）——PR 只读不写。macOS 平台另有 `BAZEL_OSX_EXECUTE_TIMEOUT=600`（注释引用 bazelbuild/bazel#17437）。

## GCS 远程缓存与 pull_request_target 禁写

当 bazel-cache 给出且非本地 act 运行时，bazel-setup 为 Bazel 追加远程缓存参数：

```yaml
--google_credentials=${{ inputs.credentials-file }}
--remote_cache=https://storage.googleapis.com/protobuf-bazel-cache/protobuf/gha/${{ inputs.bazel-cache }}
```

非 pull_request_target 事件再追加 `--remote_upload_local_results`，注释原句 "External runs should never write to our caches."。即：共享 GCS 远程缓存对外部 fork PR 只读、禁写，防止不可信构建污染缓存——这与 docker-run 的 release 镜像拦截（见 [04 篇](/concepts/04-docker-checkout-bash-actions.md)）同属一套 fork PR 安全策略。

## repository cache save/restore 配对

internal/repository-cache-restore（name 'Restore Repository Cache'）设置三个变量并调用 actions/cache/restore：

```yaml
REPOSITORY_CACHE_BASE=repository-cache-${{ github.base_ref || github.ref_name }}-${{ runner.os }}
REPOSITORY_CACHE_NAME=$REPOSITORY_CACHE_BASE-{bazel-cache}-{github.sha}
REPOSITORY_CACHE_PATH=.repository-cache
```

restore 以 REPOSITORY_CACHE_NAME 为 key、REPOSITORY_CACHE_BASE 为 restore-keys，路径为 workspace 下的 .repository-cache。注释说明每个缓存 "can get up to ~500 MB and Github prunes the cache after 10 GB"——单个可达约 500 MB，GitHub 在 10 GB 配额后开始修剪。

internal/repository-cache-save 无 inputs，注释原句 "this action will only work if repository-cache-restore has already been called"（其 name 字段亦写作 'Restore Repository Cache'，源码原文如此）；仅当 `REPOSITORY_CACHE_HASH != hashFiles(...)`（仓库内容确有变化）时以 key `REPOSITORY_CACHE_BASE-${{ github.sha }}` 调用 actions/cache/save。bazel 与 bazel-docker 都在非 PR 事件末尾调用它，形成 restore→save 配对。

## 相关概念

- [/concepts/01-repo-positioning-and-structure.md](/concepts/01-repo-positioning-and-structure.md) — 仓库定位与结构：可复用 CI 动作集合
- [/concepts/03-ccache-sccache-actions.md](/concepts/03-ccache-sccache-actions.md) — ccache 与 sccache 编译缓存动作
- [/concepts/05-composer-cross-compile-actions.md](/concepts/05-composer-cross-compile-actions.md) — composer-setup 与 cross-compile-protoc 专项动作
