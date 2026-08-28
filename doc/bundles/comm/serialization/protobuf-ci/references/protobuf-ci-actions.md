---
type: Reference
title: "protobuf-ci CI 动作信源登记"
description: "登记 protobuf-ci 仓库 9 个顶层 action、7 个 internal action 及 protobuf 主仓 14 个 workflow 交叉验证信源，支撑 F-CI-001~056 事实。"
tags: [protobuf-ci, github-actions, composite-action, ci-cache]
generated: { by: "agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-ci-source
    resource: external/libs/protocolbuffers/protobuf-ci
    title: "protobuf-ci 仓库源码（main 分支）"
  - id: protobuf-source
    resource: external/libs/protocolbuffers/protobuf
    title: "protobuf 主仓库源码（v37.0-dev，workflow 交叉验证）"
---

本信源文件登记 protocolbuffers/protobuf-ci 仓库的信源路径，是 R 阶段事实清单 facts-protobuf-ci.md（F-CI-001~056，共 56 条事实）的信源登记表。protobuf-ci 束 concepts/ 中全部 5 篇概念文档的 frontmatter sources 字段均应指向本文件。

登记范围覆盖：仓库顶层文档（README/CONTRIBUTING/LICENSE）、9 个顶层 composite action（bash、bazel、bazel-docker、ccache、checkout、composer-setup、cross-compile-protoc、docker、sccache）、7 个 internal action（bazel-setup、ccache-setup-windows、docker-run、gcloud-auth、repository-cache-restore、repository-cache-save、setup-runner），以及 protobuf 主仓侧的 workflow 交叉验证信源（对应 F-CI-052~056）。

## 源码版本信息

| 项 | 值 |
|------|-----|
| 源码根路径 | external/libs/protocolbuffers/protobuf-ci（main 分支） |
| 引用方式 | 主仓 workflow 以 `protocolbuffers/protobuf-ci/<action>@v6` 固定 tag 引用（F-CI-052、F-CI-053） |
| 版本纪律 | protobuf-ci 任何变更须经 release 才能反映到其他仓库（F-CI-004、F-CI-056） |
| 交叉验证信源 | protobuf 主仓 v37.0-dev 的 .github/workflows/ 目录（24 个 yaml，其中 14 个引用 protobuf-ci） |

## 核心模块与文件清单

### 顶层文档

- `README.md` — 仓库说明文档
- `CONTRIBUTING.md` — 贡献指南
- `LICENSE` — 许可证（Apache-2.0）

### 9 个顶层 composite action

- `bash/action.yml` — bash 执行动作
- `bazel/action.yml` — 宿主机 bazel 构建动作
- `bazel-docker/action.yml` — 容器内 bazel 构建动作
- `ccache/action.yml` — ccache 编译缓存动作
- `checkout/action.yml` — 仓库检出动作
- `composer-setup/action.yml` — PHP composer 依赖动作
- `cross-compile-protoc/action.yml` — protoc 交叉编译动作
- `docker/action.yml` — docker 执行动作
- `sccache/action.yml` — sccache 编译缓存动作

### 7 个 internal action

- `internal/bazel-setup/action.yml` — bazel 环境装配
- `internal/ccache-setup-windows/action.yml` — Windows ccache 装配
- `internal/docker-run/action.yml` — docker 运行封装
- `internal/gcloud-auth/action.yml` — GCS 凭据认证
- `internal/repository-cache-restore/action.yml` — repository cache 恢复
- `internal/repository-cache-save/action.yml` — repository cache 保存
- `internal/setup-runner/action.yml` — runner 环境准备

### 主仓侧交叉验证信源（F-CI-052~056）

protobuf 主仓 .github/workflows/ 目录下 24 个 yaml 中引用 protobuf-ci 的 14 个文件：

- `.github/workflows/staleness_check.yml` — staleness 检查工作流
- `.github/workflows/test_bazel.yml` — Bazel 测试工作流
- `.github/workflows/test_cpp.yml` — C++ 测试工作流
- `.github/workflows/test_csharp.yml` — C# 测试工作流
- `.github/workflows/test_hpb.yml` — hpb 测试工作流
- `.github/workflows/test_java.yml` — Java 测试工作流
- `.github/workflows/test_objectivec.yml` — Objective-C 测试工作流
- `.github/workflows/test_php_ext.yml` — PHP 扩展测试工作流
- `.github/workflows/test_php.yml` — PHP 测试工作流
- `.github/workflows/test_python.yml` — Python 测试工作流
- `.github/workflows/test_ruby.yml` — Ruby 测试工作流
- `.github/workflows/test_rust.yml` — Rust 测试工作流
- `.github/workflows/test_upb.yml` — upb 测试工作流
- `.github/workflows/test_yaml.yml` — YAML 测试工作流

## 事实关联

| 事实区间 | 条数 | 事实清单文件 |
|---|---|---|
| F-CI-001 ~ F-CI-056 | 56 | facts-protobuf-ci.md |

事实清单文件为 R 阶段产出，位于 spec 目录 .trae/specs/protocolbuffers-okf-wiki/。本束 concepts/ 文档中所有 F-CI 编号事实均以本信源登记的源码路径为出处。

## 相关概念

- /concepts/01-repo-positioning-and-structure.md — 含 F-CI-001~007、052~056
- /concepts/02-bazel-build-actions.md — 含 F-CI-011~020、040、041、049、050
- /concepts/03-ccache-sccache-actions.md — 含 F-CI-021~025、036~039、042、043、047
- /concepts/04-docker-checkout-bash-actions.md — 含 F-CI-008~010、026、027、033~035、044~046、048、051
- /concepts/05-composer-cross-compile-actions.md — 含 F-CI-028~032
