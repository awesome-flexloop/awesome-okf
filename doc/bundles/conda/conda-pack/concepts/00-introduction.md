---
okf_version: "0.2"
type: "concept"
title: "conda-pack 简介"
description: conda-pack 是什么——一个将 conda 环境打包为可重定位归档的命令行工具，核心能力、适用场景和与其他工具的对比。
tags: [conda-pack, introduction, packaging]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
  - id: cli
    resource: /references/cli-source.md
    title: cli.py 与辅助模块源码
---

# conda-pack 简介

## 什么是 conda-pack

conda-pack 是一个**将已有的 conda 环境打包为可重定位归档文件的命令行工具和 Python 库** [F-001]。它以 BSD-3-Clause 许可证开源发布，项目托管于 GitHub（https://github.com/conda/conda-pack），由 Jim Crist 等人维护 [F-001][F-010]。

conda-pack 解决的核心问题是：**如何将一个 conda 环境从一台机器完整地复制到另一台机器，而无需在目标机器上重新安装包或求解依赖？** conda 环境中包含大量硬编码的绝对路径（shebang、脚本、配置文件、二进制文件等），直接复制目录无法在新位置正常工作。conda-pack 通过前缀占位符机制和部署时修复脚本解决了这个问题。

## 核心能力

### 环境打包

conda-pack 可以将指定的 conda 环境（通过名称、路径或当前激活环境）打包成多种归档格式：

- **tar 系列**：`.tar`、`.tar.gz`/`.tgz`、`.tar.bz2`/`.tbz2`、`.tar.xz`/`.txz`、`.tar.zst`/`.tzst`
- **zip**：`.zip`（支持 ZIP64 大文件扩展）
- **squashfs**：`.squashfs`（只读压缩文件系统，需外部 `mksquashfs` 工具）
- **Cloudera Parcel**：`.parcel`（适配 CDH/Hadoop 集群部署）
- **no-archive**：不打包，直接复制到目标目录 [F-018]

### 前缀重定位

conda-pack 的核心技术是**前缀替换机制**：

1. 打包时，将文件中的原始路径替换为占位符 `/opt/anaconda1anaconda2anaconda3`（长度固定为22字符）[F-005]
2. 归档中附带自动生成的 `conda-unpack` 脚本
3. 在目标机器解压后，运行 `conda-unpack` 将占位符替换为实际路径 [F-038]

文本文件使用简单字符串替换，二进制文件使用 null 填充替换保证偏移不变，Windows 上特殊处理 distlib 入口点 exe 的 shebang [F-051][F-052]。

### 跨平台支持

conda-pack 原生支持 Linux、macOS（含 arm64）和 Windows 三大平台 [F-006][F-053]：

| 平台 | BIN_DIR | 二进制替换策略 | 特殊处理 |
|------|---------|---------------|---------|
| Linux | `bin/` | null 填充二进制替换 | — |
| macOS | `bin/` | null 填充二进制替换 | 修改文件后自动 `codesign` 重签名 |
| Windows | `Scripts/` | distlib pyzzer shebang 替换 | 扩展长度路径（`\\?\` 前缀）处理 |

### 文件过滤

支持通过 glob 模式排除（`--exclude`）和重新包含（`--include`）文件，可多次使用形成过滤器链 [F-015][F-016][F-042]。Python API 提供 `CondaEnv.exclude(pattern)` 和 `CondaEnv.include(pattern)` 方法。

## 适用场景

- **离线部署**：在有网络的机器上打包环境，复制到无网络的目标机器部署
- **一致环境分发**：在团队或集群中分发完全一致的 Python 环境
- **Docker/容器镜像优化**：预打包环境避免容器内重复安装
- **HPC/集群部署**：通过 Cloudera Parcel 格式集成到 Hadoop 生态
- **CI/CD 流水线**：将测试验证过的环境归档作为构建产物

## conda-pack vs 其他方案

| 特性 | conda-pack | conda-pack + conda-unpack | `conda env export` + `conda env create` | 直接复制目录 |
|------|-----------|--------------------------|----------------------------------------|-------------|
| **是否需要网络** | 打包时需要 | 部署时不需要 | 创建时需要 | 不需要 |
| **是否需要目标机器安装 conda** | 不需要 | 不需要 | 需要 | 不需要 |
| **环境一致性** | ✅ 字节级一致 | ✅ 字节级一致 | ⚠️ 可能解析到不同版本 | ❌ 绝对路径断裂 |
| **部署速度** | 快（解压即可） | 快（解压+运行脚本） | 慢（重新求解+下载安装） | 不可用 |
| **是否处理二进制路径** | ✅ | ✅ | N/A（全新安装） | ❌ |
| **可重定位** | ⚠️ 需指定 dest-prefix | ✅ 任意路径 | ✅ | ❌ |
| **包缓存复用** | ❌ 归档是独立的 | ❌ | ✅ 利用包缓存 | ❌ |

**关键区别**：
- `conda env export` 导出的是环境规格（YAML），目标机器需要重新求解和下载所有包，版本可能漂移
- conda-pack 打包的是环境的完整副本，包含所有二进制文件，解压后通过 `conda-unpack` 修复路径即可使用
- 如果需要在同一台机器上复制环境，优先使用 `conda create --clone`，比打包更快且利用硬链接

## 项目信息

| 属性 | 值 |
|------|-----|
| 许可证 | BSD-3-Clause [F-010] |
| Python 版本要求 | ≥ 3.9 [F-059] |
| 唯一运行时依赖 | setuptools [F-059] |
| CLI 入口点 | `conda-pack = conda_pack.cli:main` [F-041] |
| 构建系统 | setuptools + setuptools_scm [F-059] |
| 核心代码行数 | ~2500 行（7个 Python 文件） |

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
