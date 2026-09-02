---
type: Concept
title: TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）
description: 针对 external/TuyaOpen 工作区的可执行学习路线：先跑通 LINUX target 构建闭环，再进入硬件烧录与 AI 智能体硬件能力区。
tags: [tuyaopen, learning-path, iot, embedded, sdk, cli, tos]
generated: { by: "process:learning-bundles-migration", at: "2026-09-02T00:00:00Z" }
status: draft
stale_after: 2027-09-02
sources:
  - id: learning-source
    resource: SpecWeave docs/knowledge/learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md
---
# TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）

## 1. 入门目标

- 在不接触硬件的情况下，先完成一次可复现的构建闭环（dist 产物可定位）。
- 明确 TuyaOpen 的“统一入口”在哪里，以及每一步的验收点是什么。

## 2. 三阶段路线

### 阶段 A：主机闭环（LINUX target）

- 环境初始化：`export.*`（会创建/复用 `.venv`、执行 `uv sync`、并运行 `tos.py prepare`），AGENTS.md
- 环境校验：`tos.py check`，AGENTS.md
- 构建示例：进入 `examples/<category>/<project>` 后执行 `tos.py build`，AGENTS.md
- 验收点：`<project>/dist/` 产物可定位，AGENTS.md

### 阶段 B：设备闭环（烧录与串口监控）

- 目标：`build → flash → monitor`
- 子命令集合：`flash/monitor` 等在 `tos.py` 的注册表中可见，`tos.py`
- 重要约束：避免交互式配置命令，采用修改 `app_default.config` 固化配置，AGENTS.md

### 阶段 C：AI 能力区（价值区）

- 目标：把端侧能力与云侧多模态 AI 能力打通（语音/视觉/传感器/远程控制/OTA）
- 入口：TuyaOpen 概述与系统组成，[README_zh.md](../../../../../../external/libs/Zleap-Agent/README_ZH.md#L44-L71)

## 3. 关联复盘材料

- TuyaOpen 目录全链路复盘（复盘+洞察+萃取+学习+导出）
