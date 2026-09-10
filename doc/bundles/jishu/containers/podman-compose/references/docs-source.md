---
type: Reference
title: podman-compose 官方文档与补全脚本信源登记
description: docs/ 目录（7 份版本 Changelog、Extensions、Mappings）与 completion/bash 补全脚本的版本固定与内容索引
tags: [podman, compose, documentation, changelog, extensions, completion, reference]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: docs-source
    resource: /references/docs-source.md
    title: podman-compose docs/ 与 completion/ 信源登记（v1.6.0 / commit e3df104）
---

# podman-compose 官方文档与补全脚本信源登记

本文件登记 podman-compose 仓库 `docs/` 与 `completion/` 目录的内容，作为本束「x-podman 扩展」与「版本演进」两篇概念文档的信源。

## 版本固定

| 项目 | 值 |
|------|-----|
| 仓库快照 | git `v1.6.0-97-ge3df104`，commit `e3df10472e194ab6d547b5ad25542c5c79e1a5fb`（2026-08-11） |
| 最新正式 release | 1.6.0（2026-06-03，见 Changelog-1.6.0.md） |
| 文档目录 | `docs/`（9 个文件：7 份 Changelog + Extensions + Mappings）、`completion/bash/`（1 个文件） |

## docs/ 文件清单

| 文件 | 内容 | 覆盖概念 |
|------|------|---------|
| `Extensions.md` | Podman 对 docker-compose 格式的官方扩展说明：容器/密钥/网络级 x-podman 字段、每网络 MAC 与接口名、podman 特有网络模式与挂载类型、Docker Compose 兼容开关、自定义 Pod 管理 | [x-podman 扩展字段全解](../concepts/08-x-podman-extensions.md) |
| `Mappings.md` | 0.1.x 时代的 6 种网络映射模式（1podfw/1pod/identity/hostnet/cntnet/publishall） | [版本演进与能力矩阵](../concepts/09-version-evolution.md) |
| `Changelog-1.1.0.md` | 2024-04-17：uidmap/gidmap、--parallel、stats、include、build 命令、profile、多网络、IPAM 等 | [版本演进与能力矩阵](../concepts/09-version-evolution.md) |
| `Changelog-1.2.0.md` | 2024-06-26：x-podman 字典→x-podman.* 字段迁移、--rootfs、images 命令、GPU、additional_contexts、stdin、environment secrets | 同上 |
| `Changelog-1.3.0.md` | 2025-01-07：depends_on condition、x-podman.no_hosts、两个默认网络兼容开关、网络级 mac_address、Python 3.13 兼容 | 同上 |
| `Changelog-1.4.0.md` | 2025-05-10：!reset/!override 标签、x-podman.disable-dns/dns/interface_name/pod_args、--abort-on-container-failure、down --rmi、SIGINT 优雅关闭 | 同上 |
| `Changelog-1.4.1.md` | 2025-06-05：bind mount 相对宿主路径修复（单修复版本） | 同上 |
| `Changelog-1.5.0.md` | 2025-07-07：docker_compose_compat 元开关、name_separator_compat、PODMAN_COMPOSE_* 环境变量、x-podman.routes、systemd unregister、自定义 pod 名 | 同上 |
| `Changelog-1.6.0.md` | 2026-06-03：--wait/--wait-timeout、glob/image 挂载、COMPOSE_PROFILES、嵌套插值、teardown 前拉镜像、service: build contexts、服务级配置变更检测 | 同上 |

## completion/ 文件清单

| 文件 | 内容 |
|------|------|
| `completion/bash/podman-compose` | Bash 可编程补全脚本（411 行）：`complete -F _podmanCompose podman-compose` 注册；根命令补全 14 个（help/version/pull/push/build/up/down/ps/run/exec/start/stop/restart/logs）；为 up/down/exec/build/logs/ps/pull/push/restart/stop/start/run 12 个子命令维护静态选项列表；路径类选项走 `compgen -f`；服务名与容器内命令补全为 stub（不解析 compose 文件） |

## 关键事实注记

- **补全脚本与代码存在漂移**：脚本的 `root_commands` 列 14 个命令（含 help），而源码（同一快照）已注册 24 个子命令，`ls`、`cp`、`wait`、`pause`、`unpause`、`kill`、`stats`、`images`、`config`、`systemd`、`port` 共 11 个未进入补全；全局选项列表也未含 `--in-pod`、`--pod-args`、`--profile`、`--env-file`、`--parallel`、`--verbose` 等。补全选项是手工维护的静态快照，不从 argparse 自动生成。
- **newsfragments/ 目录**（仓库根，非 docs/）承载 1.6.0 之后、未发布的变更片段（如 `add_cp_command.feature`、`add_ls_command.feature`、`ipc.feature`、`passwd_extension.feature` 等 30 个片段），对应源码中已实现但 Changelog 尚未汇总的能力。
- Extensions.md 声明的扩展与源码 `XPodmanSettingKey` 枚举（6 个全局键）及翻译层字段（`x-podman.uidmaps/gidmaps/rootfs/no_hosts/passwd/relabel/dns/routes/disable_dns/mac_address/interface_name`）相互印证。

## 相关信源

- [源码信源登记](source-code-map.md)：podman_compose.py 版本固定、结构地图与符号索引
- [官方 README](readme-source.md)：项目介绍与安装方法
