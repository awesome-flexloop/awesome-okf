---
type: Concept
title: 版本演进与能力矩阵
description: 基于 7 份官方 Changelog 梳理 podman-compose 从 0.1.x 到 1.6.0 的演进主线、版本能力门槛、未发布变更与 bash 补全脚本资产
tags: [podman, compose, changelog, versioning, compatibility, bash-completion, evolution]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: docs
    resource: /references/docs-source.md
    title: podman-compose docs/ 与 completion/ 信源登记（Changelog 1.1-1.6 / Mappings）
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# 版本演进与能力矩阵

本文基于官方 7 份 Changelog（1.1.0–1.6.0 六个小版本，含 1.4.1 补丁）与 Mappings 历史文档，梳理 podman-compose 的演进主线、版本门槛与周边资产，回答"某个能力从哪个版本开始可用、升级时要注意什么"。

## 0.1.x → 1.x：架构断点

0.1.x 分支运行在 podman 3.1.0 之前，rootless 能力受限，靠 6 种**网络映射模式**（全局 `-t` 选项）补偿，记录于 Mappings.md：

| 模式 | 机制 |
|------|------|
| `1podfw` | 全部容器放入一个 pod，容器间经 localhost 通信，端口映射在 pod 上做 |
| `1pod` | 全部容器放入一个 pod，端口映射在各容器上做（文档标注 does not work） |
| `identity` | 不做映射 |
| `hostnet` | host 网络，容器间经宿主网关与发布端口通信 |
| `cntnet` | 创建一个容器并经 `--network container:name` 复用其网络栈 |
| `publishall` | `-P` 发布全部端口，经网关通信 |

1.x 分支（podman ≥ 3.4）原生 rootless 网络成熟后，这些 hack 全部移除：**`-t` 选项被删除**，网络模式改用标准字段 `network_mode: host` 等表达。这是升级 0.1.x 用户最核心的 breaking change。

## 1.x 版本时间线（能力引入矩阵）

| 版本 | 日期 | 标志性能力 |
|------|------|-----------|
| 1.1.0 | 2024-04-17 | `include` 顶层组合、`build` 命令、`profile`、`--parallel`、多网络与每网络 IP/MAC、IPAM driver、uidmap/gidmap、`stats`、`config --no-normalize`、build 文件密钥 |
| 1.2.0 | 2024-06-26 | **`x-podman` 字典迁移为 `x-podman.*` 扁平字段**、`--rootfs`、`images` 命令、GPU 支持、`additional_contexts`、stdin 传入 compose、environment secrets、compose 内声明 in_pod |
| 1.3.0 | 2025-01-07 | `depends_on` 条件生效、两个默认网络兼容开关、`x-podman.no_hosts`、网络级 `mac_address`/网络别名、`device_cgroup_rules`、down 删除网络、Containerfile 等替代 Dockerfile 名、**声明兼容 Python 3.13** |
| 1.4.0 | 2025-05-10 | **`!reset`/`!override` 合并标签**、`x-podman.disable-dns`/`dns`/`interface_name`/`pod_args`、`--abort-on-container-failure`、`down --rmi`、pids_limit、SIGINT 优雅关闭、systemd socket activation 的 fd 透传 |
| 1.4.1 | 2025-06-05 | 单修复：bind mount 相对宿主路径解析 |
| 1.5.0 | 2025-07-07 | **`docker_compose_compat` 元开关**、`name_separator_compat`、`PODMAN_COMPOSE_*` 环境变量通道、`x-podman.routes`、systemd unregister、自定义 pod 名、secret relabel（z/Z）、`io.podman.compose.service` 标签 |
| 1.6.0 | 2026-06-03 | `--wait`/`--wait-timeout`、`glob` 与 `image` 挂载类型、`COMPOSE_PROFILES` 环境变量、嵌套变量插值、**拆除旧容器前先拉镜像**、`service:` 构建上下文、服务级配置变更检测（config-hash）、`start_interval` |

## 三条演进主线

1. **方言退场、标准收敛**：0.1.x 的 `-t` 网络映射 → 原生网络模型；1.2.0 的 `x-podman` 嵌套字典 → 扁平标准风格字段；1.5.0 的 `docker_compose_compat` 开关明确预告分隔符/网络名兼容项未来默认翻转并移除。项目方向是让默认行为逐步对齐 docker-compose，x-podman 只保留标准无法表达的 Podman 独有能力。
2. **可靠性与幂等加固**（集中在 1.4–1.6）：依赖条件真正生效（1.3/1.4）、SIGINT 优雅清理（1.4）、`!reset/!override` 让 override 文件可控合并（1.4）、config-hash 服务级变更检测与镜像变化重建（1.6）、teardown 前预拉镜像减少停机（1.6）、多字节长日志行冻结修复（1.3/1.6 两次）。
3. **生态双语兼容**：资源标签同时打 `io.podman.compose.*` 与 `com.docker.compose.*` 两套前缀（1.5 补齐 service 标签），使 docker 生态工具也能识别 podman-compose 管理的资源。

## 版本能力门槛

| 门槛 | 影响 | 降级行为 |
|------|------|---------|
| podman ≥ 3.4 | 使用 1.x 分支的前提 | 更旧版本需用 0.1.x |
| podman 4.6.0 | `healthy`/`unhealthy` 依赖条件、`--wait` 等待 | 更低版本仅告警跳过，不报错 |
| podman 5.6.0 | up 前 `podman pull --policy` 预拉取优化 | 更低版本跳过预拉取（功能不受影响） |
| Python ≥ 3.9 | 运行前提 | — |
| Python 3.13 | 1.3.0 起官方声明兼容 | — |

源码中对 Python 3.11+ API 也做了保护（如 `Task.cancelling()` 先判断 `sys.version_info`）。

## 1.6.0 之后的未发布变更

当前代码快照（`v1.6.0-97-ge3df104`）包含 97 个 release 后的提交，仓库以 `newsfragments/` 目录（towncrier 风格片段）承载，Changelog 尚未汇总。已在源码中落地的主要待发布能力包括：

- **新命令**：`cp`（容器与宿主间复制文件）、`ls`（列出运行中的 compose 项目）；
- **新功能**：`ipc` 配置、`x-podman.passwd` 扩展、up 的 `--no-hosts` 全局旗标与 `--no-attach`、多 `--env-file` 旗标、递归向上发现 compose 文件、`COMPOSE_FILE` 环境变量支持；
- **修复**：镜像变化触发重建（recreate_on_image_change）、`depends_on` 合并、command/entrypoint 插值、Windows 自定义 Dockerfile 名、`service_completed_successfully` 退出码校验、缺失环境变量的干净报错等。

> 实践提示：pip 安装 1.6.0 与直接用 main 分支快照在命令集上已有明显差异；本束文档基于源码快照描述 `cp`/`ls` 等命令时，均标注了其存在性以源码为准。

## 周边资产：bash 补全脚本

`completion/bash/podman-compose`（411 行）是手写的 Bash 可编程补全脚本，通过 `complete -F _podmanCompose podman-compose` 注册：

- **根命令补全**：静态维护 14 个命令（help/version/pull/push/build/up/down/ps/run/exec/start/stop/restart/logs）；
- **子命令选项**：为 12 个子命令各维护一份静态选项字符串（如 up 的 `--detach --force-recreate --scale ...`）；
- **参数类型感知**：路径类选项（`-f/--file`、`--podman-path`）走 `compgen -f` 补全文件；取通用值的选项（`-p`、`--podman-*args` 等）不补全；
- **词位计算**：通过遍历 COMP_WORDS 扣减选项及其参数，推算当前处于子命令树的深度（`comp_cword_adj`），区分"补服务名"与"补容器内命令"；
- **明确的 stub**：服务名补全（`_completeServiceNames`）与容器内命令补全（`_completeCommand`）是空函数——注释说明在补全脚本里解析 compose 文件过于复杂。

**已知漂移**：补全脚本是手工同步的静态快照，不从 argparse 自动生成。与当前源码相比，根命令缺少 `cp`、`ls`、`wait`、`pause`、`unpause`、`kill`、`stats`、`images`、`config`、`systemd`、`port`；全局选项缺少 `--in-pod`、`--pod-args`、`--profile`、`--env-file`、`--parallel`、`--verbose` 等。升级 podman-compose 后不要假设 Tab 补全与实际命令集一致，以 `podman-compose --help` 为准。

## 相关概念

- [快速上手与 Compose Spec 兼容](00-introduction.md)：版本号与分支说明的用户视角
- [x-podman 扩展字段全解](08-x-podman-extensions.md)：各扩展字段与兼容开关的引入版本
- [依赖图与 up/down 生命周期](07-dependency-lifecycle.md)：版本门槛 4.6.0/5.6.0 的实现位置
- [配置加载管线](06-config-pipeline.md)：COMPOSE_PROFILES、递归文件发现等配置侧演进
- [官方文档信源登记](../references/docs-source.md)：Changelog 原文索引
