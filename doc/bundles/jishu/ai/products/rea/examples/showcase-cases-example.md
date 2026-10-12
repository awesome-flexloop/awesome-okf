---
okf_version: "0.2"
type: Example
title: "REA：官方 showcase 三类端到端逆向重建案例"
description: "README_zh 官方 showcase 的三个完整案例——DX-Ball 声像计算重建、Notion Electron 剪贴板桥追踪、TH04 DOS 环形子弹恢复——用它们说明一条 REA 端到端逆向重建路径：调用追踪 → 指令检查 → 证据驱动重建 → 与原始实现比对（事实 F-132）"
tags: [rea, example, showcase, dx-ball, notion, th04, reconstruction, electron, dos, pc-98]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T16:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: readme-zh
    url: "file" # 本地 README 简体中文：external/dao/rea/README_zh.md
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# 示例：官方 showcase 三类端到端逆向重建案例

> ⚠️ **可复现性说明**：本节整理 README_zh（官方 showcase 栏目）所列的三个已完成案例——DX-Ball、Notion、TH04。**案例本身在上游完成并在官方展示**，重建仓库与数据来自 README 声明与对应仓库；本知识包未在本机重跑。命令形态与机制参考 facts.md（F-067~F-131），案例事实来自 F-132，禁止超出清单臆造。

## 目标

通过官方展示的三类案例，理解 REA 如何把「喜欢的功能 → 弄清原理 → 二进制层面重建」串成端到端流程，并看清每类目标（native 二进制 / Electron 应用 / DOS 16 位游戏）对应的调查路径。

## 输入与前置

- Node 满足支持范围（F-007），已 `npx rea-agents setup` 注册 MCP（F-010/011）。
- 按目标准备分析工具：native 需 Hopper/Ghidra/IDA（F-030~F-032），Electron/JS 无需原生引擎（静态 JS 检查，F-135），DOS 16 位用 Ghidra 专项支持（F-090+）。

## 案例一：DX-Ball —— 重建声像计算

**路径**：沿声音调用追踪 → 定位按位置计算声像的辅助函数 → 检查指令 → 将不完整伪代码转为 C。

- 沿声音相关调用链向下追踪到负责把位置映射为声像（pan）的辅助函数。
- 检查该函数的 x86 指令，将不完整的伪代码补齐为可读 C。
- **验收**：重建结果通过 **3,205 个**原始 x86 测试用例，并**复现编译后函数的全部 63 个字节**。
- 重建仓库：`github.com/N0zoM1z0/dx-ball`。

**可照做 CLI 初探**（native 域）：

```bash
rea analyze /path/to/dxball --json        # 目标概览（F-056）
rea trace /path/to/dxball sound-pan --json # 沿声音调用追踪（对应示踪工作流）
```

## 案例二：Notion —— 追踪 Electron 剪贴板桥

**路径**：渲染进程剪贴板 API → preload → IPC → 主进程 → 富格式剪贴板数据。

- 在渲染进程定位剪贴板 API 入口。
- 沿 Electron 的 preload 暴露的桥（contextBridge 等）与 IPC 通道，追踪到主进程处理逻辑。
- 检查富格式（rich）剪贴板数据的构造与返回。

**可照做 CLI 初探**（Electron/JS 域）：

```bash
rea analyze-javascript-application /path/to/notion.app.asar --json   # 模块/导入/Electron 边界（F-072）
rea list-electron-targets http://127.0.0.1:9223                       # 附着已启动 Electron（F-114）
rea inspect-electron-page --observation-ms 5000 --include-script-sources  # 按需观测脚本源（F-114）
```

## 案例三：TH04 —— 恢复 DOS 环形子弹计算

**路径**：检查原始 PC-98 游戏 16 位指令 → 恢复固定角度与瞄准角度计算 → 重建 C++ → 与当年编译器输出对比。

- 针对 PC-98 的 16 位指令逐条检查。
- 恢复环形子弹生成所需的固定角度 / 瞄准角度计算逻辑。
- 用重建的 C++ 与当年代理编译器输出比对，验证重建正确性。
- 重建仓库：`github.com/N0zoM1z0/th04`。

**可照做 CLI 初探**（16 位 DOS 专项，Ghidra 深度适配）：

```bash
rea analyze /path/to/th04.exe --provider ghidra --json   # 指定 Ghidra 提供方（F-030）
rea decompile /path/to/th04.exe --function ring_bullets    # 反编译目标函数（对应 F-016 映射）
```

## 共同模式：从调查到重建

三个案例共享的 REA 工作流（衔接重建工程概念，见 [10 · 工程与管理](../concepts/10-engineering-workflow.md)）：

1. **调查（Investigation）**：`analyze`/`trace` 定位目标功能与调用链，获取结构化证据。
2. **证据驱动重建**：把不完整伪代码 / 指令转为可编译源码，用返回值覆盖测试用例（DX-Ball 的 3,205 用例）或编译器输出比照（TH04）验证。
3. **义务台账收口**：若走完整重建，用 `build_reconstruction_obligation_ledger` 记录 artifacts/providers/scenarios 与 unknowns（F-130），产出 `closure_digest`。

## 边界与注意事项

- 三类案例均为**合法逆向工程研究**，须遵守目标授权与适用法律（README 免责声明口径）。
- 命令为 README/源码核对后的示意路径，未在本机实跑；实际以 `rea <command> --help` 与官方 showcase 为准。
- 运行时观测（浏览器/进程）会以**你的用户权限**运行目标（F-135），注意隔离与授权。