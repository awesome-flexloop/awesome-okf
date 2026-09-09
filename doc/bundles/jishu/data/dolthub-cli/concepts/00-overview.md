---
type: Concept
title: "dh CLI 概述与安装"
description: "dh（DoltHub CLI）的产品定位、安装方式、构建方式与 14 个命令组全貌，对应 F-001~F-006、F-011"
tags: [dh, dolthub, cli, install, overview]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# dh CLI 概述与安装

> 本文档介绍 `dh` 命令行工具的产品定位、安装、构建与命令组全貌。对应 [F-001~F-006、F-011](/references/source.md)。

`dh` 是 [DoltHub](https://www.dolthub.com) 的官方命令行接口（F-001），用于在命令行中操作 DoltHub 云平台上的数据库——包括认证、SQL 查询、表导入、分支/标签/Release 管理、Pull Request 协作等。它把"GitHub for Data"的体验从 Web 端延伸到了终端。

## 定位

DoltHub 是 Dolt 数据库的云托管平台（"GitHub for Data"），`dh` 就是它的"gh"（GitHub CLI）。与操作本地 Dolt 仓库的 `dolt` 命令不同，`dh` 面向的是云端 DoltHub 的 REST API v2（F-034）。

| 维度 | 说明 |
|------|------|
| 仓库 | `github.com/dolthub/cli`（F-001） |
| 二进制 | `dh`（Windows `dh.exe`）（F-001） |
| 平台 | Linux / macOS / Windows（F-002） |
| 语言 | Go，源码构建需 Go 1.26+（F-002） |
| 分析版本 | v0.0.1（commit `2ef50ab`，2026-09-08）（F-003） |

## 安装

从 [GitHub Releases](https://github.com/dolthub/cli/releases) 下载对应平台归档，用 `checksums.txt` 校验后解压出 `dh` 放入 `PATH` 目录（F-001）。

Docker 镜像为 `dolthub/cli`，提供版本 tag 与 `latest`（F-004）：

```sh
docker run --rm dolthub/cli:latest version
```

Docker 认证与挂载文件用法见 `docker/README.md`。

## 从源码构建

```sh
make build
./bin/dh version
```

测试与格式化分别用 `make test` 与 `make fmt`（F-002）。

## 命令组全貌

根命令 `dh` 下挂 14 个命令组（F-011）：

| 命令组 | 用途 |
|--------|------|
| `auth` | 登录 / 登出 / 状态（OAuth PKCE + token） |
| `sql` | 对分支/标签/提交执行 SQL 读写查询 |
| `table` | 本地文件导入 DoltHub 表 |
| `db` | 数据库创建 / fork / 查看 |
| `branch` | 分支创建 |
| `pr` | Pull Request 创建 / 合并 / 评论 / 列表等 |
| `release` | Release 创建 / 列表 / 查看 |
| `tag` | 标签创建 |
| `operation` | 异步操作列表 / 进度 / 查看 / 监听 |
| `config` | 配置读取 / 写入 / 列表 |
| `browse` | 在浏览器打开仓库 |
| `api` | 底层 API 调用 |
| `completion` | shell 补全 |
| `version` | 版本信息 |

## 相关概念

* [dh CLI 架构与分层](/concepts/01-architecture.md)
* [认证与凭据管理](/concepts/02-authentication.md)
