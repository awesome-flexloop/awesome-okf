---
type: Reference
title: "README.md 与 docs/README.md 文档工程"
description: "Podman 源码根 README.md 项目定位与 docs/README.md Sphinx 文档目录结构：man page 源目录、requirements.txt 依赖、CODE_STRUCTURE.md 代码库分层、MANPAGE_SYNTAX.md 手册页语法。"
tags: [podman, readme, docs, sphinx, manpage, code-structure, reference]
generated: { by: "reference_agent/trae-cn", at: 2026-09-07T10:10:00+08:00 }
verified: { by: "process:grep-v", at: 2026-09-07T10:10:00+08:00 }
status: stable
stale_after: 2027-09-07
---

# README.md 与 docs/README.md 文档工程

本信源登记簿整理 Podman 源码仓库根 `README.md` 与 `docs/README.md` 两份文档所陈述的事实，覆盖项目定位、快速安装、文档工程目录结构、Sphinx 依赖与构建流程。

## 事实 1：项目定位与主要特性（根 README.md）

| 事实编号 | 内容 | 原始依据 |
|---------|------|---------|
| F1-1 | Podman 全称 POD MANager，是一个**无守护进程的开源容器引擎**，用于在 Linux 系统上开发、管理和运行 OCI 容器与 Pod | Podman 仓库根 README.md 首段 |
| F1-2 | Podman 提供 Docker 兼容的 CLI，且原生支持 Pod 资源模型（Kubernetes 同源） | README.md 特性列表 |
| F1-3 | Podman 支持 rootful 和 rootless 两种模式，官方推荐优先 rootless 以减小攻击面 | README.md 安全章节 |
| F1-4 | 配套工具链：Buildah（镜像构建，`podman build` 内部调用它）、Skopeo（镜像传输，`podman pull/push/save/load` 底层依赖）、crun/runc（OCI runtime） | README.md ecosystem 段落 |

## 事实 2：docs/README.md —— Sphinx 文档工程目录结构

| 目录/文件 | 作用 |
|-----------|------|
| `docs/source/markdown/` | **man page Markdown 源**，所有 `podman-*.1.md.in` 都在这里，是命令手册的单一可信源 |
| `docs/source/markdown/links/` | man page 别名（`podman container ps -> podman-ps` 等 `.so` 软链等效文件） |
| `docs/source/markdown/options/` | 共用选项文档（每个 flag 一个 .md 文件，被多个命令的 man page include） |
| `docs/source/_static/` | Sphinx 静态资源：custom.css 自定义样式、api.html（Swagger UI 嵌入） |
| `docs/build/` | `make docs` / `make html` 的产物目录（不入库） |
| `docs/build/man/` | 最终生成的 man page（nroff 格式） |
| `docs/build/remote/{linux,darwin,windows}/` | 按平台生成的远端 man page 或 HTML 渲染 |
| `docs/requirements.txt` | Sphinx + myst_parser + sphinx-markdown-tables + python3-recommonmark 依赖清单（docs/README.md 列出） |
| `docs/remote-docs.sh` | 跨平台 man page 生成脚本 |
| `docs/links-to-html.lua` + `docs/use-pagetitle.lua` | Pandoc filters：man page 别名转 HTML a 标签、设置 document title |

## 事实 3：本地文档构建流程

| 步骤 | 命令 | 前置依赖 |
|------|------|---------|
| ① 安装依赖（Fedora 示例） | `sudo dnf install python3-sphinx python3-recommonmark ; pip install sphinx-markdown-tables myst_parser` | EPEL / 系统 Python 3 |
| ② 生成 man page（nroff） | `cd docs && make docs` | Go toolchain（因为 .md.in 需经 podman 二进制自己 include 展开选项） |
| ③ 生成 HTML | `cd docs && make html` | Sphinx + myst_parser |
| ④ 本地预览 | `python -m http.server 8000 --directory build/html` | Python 3 |
| ⑤ 在线官方站点 | `https://docs.podman.io/`（Read the Docs 自动构建） | — |

## 事实 4：docs/CODE_STRUCTURE.md —— Go 代码库顶层目录清单

| 顶层目录 | 核心职责 |
|---------|---------|
| `cmd/podman/` | CLI 命令 + flags 定义（Cobra）；每个子目录一个命令域 |
| `cmd/quadlet/` | Quadlet CLI 自身二进制（被 systemd 调用） |
| `libpod/` | Linux/FreeBSD 核心：Container/Pod/Volume 实体 + 状态机 + SQLite/BoltDB 磁盘库 |
| `pkg/api/` | REST API 服务端（gorilla/mux），被 `podman system service` 启动 |
| `pkg/bindings/` | 稳定 Go HTTP 客户端；ABI 承诺稳定（远程/第三方调用用它） |
| `pkg/domain/entities/` | ContainerEngine / ImageEngine 接口 + Options 结构体 |
| `pkg/domain/infra/abi/` | 接口的本地实现：直接调用 ic.Libpod.* |
| `pkg/domain/infra/tunnel/` | 接口的远程实现：转发给 pkg/bindings HTTP |
| `pkg/specgen/` | SpecGenerator：CLI/API 参数 → 统一规格描述（容器/Pod） |
| `pkg/libartifact/` | `podman artifact` 新命令核心 |
| `pkg/machine/` | `podman machine`（跨平台 VM）的核心逻辑 |
| `test/e2e/` + `test/system/` | Ginkgo 集成测试 + BATS 系统测试 |
| `vendor/` | `go mod vendor` 产物，**禁止手改**——任何修改必须先提上游 PR → go.mod bump → 再 vendor |

## 事实 5：docs/MANPAGE_SYNTAX.md —— 手册页语法约束

Podman man page 不是手写最终版，而是"`.md.in` 模板 + options/*.md 片段 include"：
- 头几行的 `% podman-run 1` 行决定 man 节号与名称
- `## OPTIONS` 下面用 `#### --option` + 描述 + 示例
- 跨命令共用的 flag 写在 `docs/source/markdown/options/xxx.md`，在 `.md.in` 里用 Markdown include 语法（或 pandoc 宏）引用
- man page build 时由 `docs/remote-docs.sh` 走 pandoc + Lua filters 产出最终 nroff/HTML

## 事实 6：REST API / Swagger 文档生成

| 事实 | 说明 |
|------|------|
| F6-1 | 最新 API 文档在线：`https://docs.podman.io/en/latest/_static/api.html`（RTD 构建时注入） |
| F6-2 | Swagger YAML：`https://docs.podman.io/en/latest/_static/swagger.yaml` 可下载 |
| F6-3 | 版本定位：把 URL 中 `latest` 换成 `v6.0.0` 即可取指定版 yaml；v5.8.4 以前的老版本 yaml 存在 GCS bucket `libpod-master-releases` |

## 相关文档
- [/concepts/00-introduction.md](../concepts/00-introduction.md) — 基于 CODE_STRUCTURE.md 的架构解读
- [/references/cli-domain-source.md](cli-domain-source.md) — CLI + pkg/domain 双实现源码信源
- [/references/libpod-source.md](libpod-source.md) — libpod + containers/* 协同源码信源
