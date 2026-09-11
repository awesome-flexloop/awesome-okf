---
type: Reference
title: "实现层源码地图：src/pkg、命令内部、构建脚本与 Shell 集成"
description: "Toolbx 实现层（podman/shell/skopeo/nvidia/term/utils 包、create/init-container/run 内部、go-build-wrapper、profile.d、data）逐文件信源登记，锚定 commit 81401f64。"
tags: [toolbx, toolbox, source-map, podman, skopeo, cdi, meson, go, reference]
generated: { by: "reference_agent/trae-cn", at: 2026-09-11T11:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-09-11T11:00:00+08:00 }
status: stable
stale_after: 2027-09-11
sources:
  - id: toolbox-repo-pinned
    resource: https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8
    title: containers/toolbox @81401f64（0.3-85-g81401f6，2026-08-05）
---

# 实现层源码地图

本信源登记 Toolbx **实现层**的全部一手代码位置，是第二轮概念文档（04-10）与示例文档（03-05）的事实来源。第一轮的 [cmd-source.md](cmd-source.md) 登记命令表层，本篇登记其子进程编排、容器内引导、跨发行版链接与工程体系的实现。

- **仓库**：<https://github.com/containers/toolbox>
- **核验快照**：commit `81401f64b3865129ea66f2a5e02a7eb40edd4fb8`（`git describe` = `0.3-85-g81401f6`，提交时间 2026-08-05；meson 项目版本 0.3）
- **本地对应**：`vendor/toolbox`（SpecWeave vendor 子模块只读引用）

## CLI 命令内部（src/cmd/，13 个非测试 Go 文件）

| 文件 | 信源 URL | 登记内容 |
|------|----------|---------|
| `create.go` | [blob/81401f64/src/cmd/create.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/create.go) | `podman create` argv 完整构造：14 个 namespace/安全参数、固定与条件 volume、socket D-Bus 发现、拉取确认两阶段交互 |
| `initContainer.go` | [blob/81401f64/src/cmd/initContainer.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/initContainer.go) | 隐藏入口命令：15 条 rbind、用户/Kerberos/PKCS#11/RPM 配置、CDI 应用、fsnotify+ticker 事件循环、初始化戳记 |
| `run.go` | [blob/81401f64/src/cmd/run.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/run.go) | exec argv（capsh 包装）、容器缺失三分支、CDI 生成与 p11-kit server 启动、戳记等待协议、cgroups 迁移、OSC 777 |
| `enter.go` | [blob/81401f64/src/cmd/enter.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/enter.go) | `$SHELL -l` 进入路径 |
| `root.go` | [blob/81401f64/src/cmd/root.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/root.go) | preRun 钩子、subid 校验、podman system migrate 版本戳记、全局选项 |
| `utils.go` | [blob/81401f64/src/cmd/utils.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/utils.go) | 名称解析错误映射、getCurrentUserShell、man 调用、eventfd/poll 可取消输入 |
| `rootDefault.go` / `rootMigrationPath.go` | [rootDefault.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/rootDefault.go) / [rootMigrationPath.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd/rootMigrationPath.go) | `migration_path_for_coreos_toolbox` 构建标签双实现 |
| `list.go` / `rm.go` / `rmi.go` / `completion.go` / `help.go` | [src/cmd/ 目录](https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/cmd) | 列表过滤、-a/-f 删除、7 个补全函数、帮助转发 |

## 内部包（src/pkg/，7 个子包）

| 包 | 信源 URL | 登记内容 |
|----|----------|---------|
| `pkg/podman` | [podman.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/podman/podman.go)、[container.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/podman/container.go)、[image.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/podman/image.go)、[errors.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/podman/errors.go) | 16 个 podman 子命令封装、Container/Image 接口与 V1/V2 JSON 双形态 Unmarshal、双标签识别 |
| `pkg/shell` | [shell.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/shell/shell.go) | exec.CommandContext 封装与退出码透传 |
| `pkg/skopeo` | [skopeo.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/skopeo/skopeo.go) | `skopeo inspect docker://` 与 LayersData 大小解析 |
| `pkg/nvidia` | [nvidia.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/nvidia/nvidia.go) | NVML/Tegra 探测矩阵与 CNCF CDI spec 生成 |
| `pkg/term` | [term.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/term/term.go) | termios GetState/SetState/raw 模式选项 |
| `pkg/utils` | [utils.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/utils/utils.go)、[fedora.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/utils/fedora.go)、[rhel.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/utils/rhel.go)、[ubuntu.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/utils/ubuntu.go)、[arch.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/utils/arch.go)、[utils_cgo.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/utils/utils_cgo.go) | 4 发行版 Distro 注册表、名称解析、43 个环境变量白名单、libsubid cgo 校验、flatpak-spawn 转发 |
| `pkg/version` | [version.go](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/pkg/version/version.go) | 构建期 -X 注入版本字符串 |

## 构建与集成资产

| 路径 | 信源 URL | 登记内容 |
|------|----------|---------|
| `src/go-build-wrapper` | [blob/81401f64/src/go-build-wrapper](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/go-build-wrapper) | 外链命令：`-I /run/host<ld>`、`-r /run/host<libc>`、`-z lazy`、版本注入、CoreOS 构建标签 |
| `meson.build` / `src/meson.build` / `meson_options.txt` | [根 meson.build](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/meson.build) / [src/meson.build](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/meson.build) | Meson 构建、7 架构动态链接器枚举、三 Shell 补全生成、go fmt/vet/test |
| `src/go.mod` | [blob/81401f64/src/go.mod](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/src/go.mod) | Go 1.22.0、18 个直接依赖及版本 |
| `profile.d/toolbox.sh` | [blob/81401f64/profile.d/toolbox.sh](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/profile.d/toolbox.sh) | ⬢ 提示符、双侧欢迎语、VTE/terminfo 处理 |
| `data/config/toolbox.conf`、`data/tmpfiles.d/toolbox.conf` | [config](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/data/config/toolbox.conf) / [tmpfiles.d](https://github.com/containers/toolbox/blob/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/data/tmpfiles.d/toolbox.conf) | TOML 配置示例；`/run/host -> ../` tmpfiles 符号链接 |
| `test/system/`（22 个 .bats + data/ 夹具） | [目录](https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/test/system) | BATS 系统测试、CDI JSON 夹具、bats-support/assert 子模块 |
| `playbooks/`（10 个）、`.github/workflows/`（3 个）、`.zuul.yaml` | [playbooks](https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/playbooks) | Ansible 环境编排与 GitHub/Zuul CI |
| `images/`（fedora/rhel/ubuntu/arch 四族 Containerfile） | [目录](https://github.com/containers/toolbox/tree/81401f64b3865129ea66f2a5e02a7eb40edd4fb8/images) | 官方镜像构建配方（含 f39 与 ubuntu 24.04） |

## 与第一轮信源的关系

- 第一轮 [readme-source.md](readme-source.md) 与 [cmd-source.md](cmd-source.md) 中的命令清单、包名等事实继续有效；本篇补充其**内部实现与 argv 级证据**。
- 命令数量口径：cobra 注册 9 个命令（含隐藏 `init-container` 与 `completion`）；面向用户 7 个（create/enter/run/list/rm/rmi/help，completion 为脚本用）。内部子包按子目录计为 7 个。
