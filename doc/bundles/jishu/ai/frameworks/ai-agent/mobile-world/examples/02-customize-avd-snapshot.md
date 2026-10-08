---
type: Example
title: "定制 AVD 快照：dev 容器内重制 init_state 并重建镜像"
description: "按 docs/configure_avd.md 的八步流程，在 dev 容器内修改模拟器状态、冻结日期、保存 init_state 快照、docker cp 回宿主并用 buildx 重建镜像的完整实操"
tags: [MobileWorld, AVD, 快照, dev模式, 确定性复现]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
  - id: mobile-world-sources
    resource: /references/source-registry.md
    title: MobileWorld 信源登记
---

# 定制 AVD 快照：dev 容器内重制 init_state 并重建镜像

MobileWorld 的任务初始化统一加载 `init_state` 模拟器快照（`snapshot_tag` 默认 `"init_state"`，F-060），并把日期冻结在 2025-10-16（F-060）。想让评测环境带上你自己的预装应用/账号/设置，就要重制这份快照并烧进新镜像。本篇按 docs/configure_avd.md 的八步流程（F-073）逐步实操。

## 为什么快照是确定性的基石

`initialize_task` 的第一步就是 `controller.load_snapshot(self.snapshot_tag)`，随后停 Mattermost/Mastodon 后端、清空 mall 配置与回调文件（F-061）。快照决定了每台容器评测起点的完全一致；而日期字面量由 BaseTask 的 `_compute_current_date()` 保证——只有 app_names 命中 `["Chrome", "Maps", "MCP-arXiv"]` 才同步当天日期，否则固定 `"2025-10-16"`（F-060）。所以定制快照时把日期定在 2025-10-16 与框架默认口径保持一致至关重要。

## 八步实操

（流程与命令出自 F-073）

### 第 1 步：启动 dev 容器

```bash
sudo mobile-world env run --image mobile_world:v1.1 --dev
```

`--dev` 模式只允许单容器，并自动启用 VNC（F-024、F-077）。

### 第 2 步：进入容器

```bash
mobile-world env exec mobile_world_env_0_dev
```

### 第 3 步：加载初始快照

```bash
adb emu avd snapshot load init_state
```

从官方 `init_state` 出发修改，保证基础状态一致。

### 第 4 步：VNC 页面手动配置

通过 VNC（`--vnc-start-port` 默认从 5800 起，F-024）在浏览器里手动操作模拟器：装应用、登账号、改设置——即你希望每个评测起点都具备的状态。

### 第 5 步：定冻结日期

```bash
adb shell su root date 101612002025.00
```

即 2025-10-16 12:00:00（MMDDhhmmYYYY.SS 格式，F-073）。与 `_compute_current_date()` 的默认字面量一致（F-060）。

### 第 6 步：保存快照并关闭模拟器

```bash
adb emu avd snapshot save init_state
adb emu kill
```

保存回 `init_state` 标签（`snapshot_tag` 默认值，F-060）。

### 第 7 步：拷回宿主

```bash
docker cp mobile_world_env_0_dev:/root/.android/avd/Pixel_8_API_34_x86_64.avd docker/
```

AVD 目录与 Dockerfile 的 `COPY docker/${AVD_NAME}.avd` 目标位置对应（`ENV AVD_NAME=Pixel_8_API_34_x86_64`，F-067）。

### 第 8 步：重建镜像

```bash
docker buildx build -t mobile_world:v1.2 -f docker/Dockerfile .
```

新镜像内的新快照即成为所有新起容器的评测起点（F-067、F-061）。

## 检查清单

- [ ] 日期已定为 2025-10-16 12:00:00（F-073），与默认冻结字面量一致（F-060）
- [ ] 快照保存到了 `init_state` 标签（F-073、F-060）
- [ ] AVD 已 `docker cp` 到 `docker/` 且文件名匹配 `Pixel_8_API_34_x86_64.avd`（F-067、F-073）
- [ ] 新镜像已通过 `docker buildx build` 重建并用于 `env run --image`（F-073）

## 相关概念

- [/concepts/07-docker-environment.md](/concepts/07-docker-environment.md)——镜像分层与 entrypoint 十步序列（快照在其中的位置）
- [/concepts/04-tasks-registry.md](/concepts/04-tasks-registry.md)——initialize_task 如何消费 init_state 快照与冻结时钟
- [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)——dev 模式与端口组
