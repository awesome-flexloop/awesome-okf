---
type: Concept
title: 快速上手：四条路径与建议顺序
description: Cua 快速上手——Cua Driver 安装（macOS/Linux/Windows）、Lume 本地虚拟机、Cua Bench 评测、云端 Fleets，以及作者建议的上手顺序（命令转述自官方 README，未经作者实测）
tags: [Cua, 快速上手, Cua Driver, Lume, Cua Bench, Fleets, 安装]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T10:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-finops-cua
    resource: https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg
    title: 《开源精选 | Cua》（FinOps实战，2026-09-26）
  - id: cua-driver-pypi
    resource: https://libraries.io/pypi/cua-driver
    title: Libraries.io：cua-driver PyPI 页（含官方 README 摘要）
---

# 快速上手：四条路径与建议顺序

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。
>
> **⚠️ 性质声明**：以下命令与步骤**全部转述自官方 README**（F-027~F-040），命令已经官方材料逐字核验（F-062）；但博文作者**未提供本人实测结果**，安装前建议对照官方文档站 cua.ai/docs 的「Your first result」教程执行（F-040）。

## 路径一：安装 Cua Driver（桌面自动化驱动）

**macOS / Linux 一行命令**（F-027）：

```bash
/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"
```

**Windows 用 PowerShell**（F-028）：

```powershell
irm https://cua.ai/driver/install.ps1 | iex
```

装好后跑官方教程的第一个任务（F-029）：连接你的 Agent（Claude Code、Codex、Cursor 都有官方集成指引），让它**打开计算器算 6 × 7**，并验证应用界面上确实显示 **42**。

> 别小看这个任务——它完整走通了「Agent 决策 → 驱动执行 → 结果验证」的闭环（F-029）。官方教程原文为："connect your agent, ask it to compute 6 × 7 in Calculator, and have it verify that the app displays 42"（F-061）。

## 路径二：用 Lume 开一台本地 macOS 虚拟机

**安装命令**（F-030）：

```bash
/bin/bash -c "$(curl -fsSL https://cua.ai/lume/install.sh)"
```

Lume 基于 Apple Virtualization.Framework，可以从 Apple 恢复镜像直接创建一台**原生 macOS Tahoe** 虚拟机，启动后通过 SSH 连接，全程无人值守（F-031）。需要 **Apple Silicon 芯片的 Mac**（F-031）。

## 路径三：用 Cua Bench 构建并评测任务

需要 **Python 3.12/3.13 和 uv**（F-032）：

```bash
uv tool install 'cua-bench[browser]'
uv tool run --from 'cua-bench[browser]' playwright install chromium
```

第一个评测任务**不需要虚拟机、Docker 或模型 API Key**（F-035）：创建一个小任务，运行它的参考解法，验证评估器给出 reward = 1.0，然后试着自己完成同一个任务。

## 路径四（进阶）：云端 Fleets

如果不想在本地折腾环境，可以直接用 **run.cua.ai** 的 Cua Fleets（F-036）：

1. 从池子里认领一台隔离的 Linux 云桌面；
2. 用 Sandbox SDK 跑命令、截屏；
3. 用完销毁。

本地沙箱和云端 Fleet 共享**同一套 Sandbox SDK**，代码可以无缝迁移（F-037）。

> ⚠️ **官方提醒（F-038）**：Fleet 池在认领结束后可能保留**付费容量**，教程里有完整的清理步骤，跟着做避免多花钱。

## 作者建议的上手顺序

如果你是第一次接触，建议按这个顺序走（F-039）：

```
1. Cua Bench 模拟任务（零依赖，不需要 VM 和 API Key）
   → 理解「任务—评估—轨迹」的概念
2. 安装 Cua Driver，让 Agent 操作一次计算器
   → 感受真实桌面自动化
3. 有 Apple Silicon Mac 的话，用 Lume 拉一台本地虚拟机
   → 做隔离实验
4. 最后再评估是否上云端 Fleets
```

循序渐进，既不会一上来就被环境劝退，也能逐步理解每个模块的定位。官方文档站 **cua.ai/docs** 对每个模块都有「Your first result」式的入门教程，跟着做即可（F-040）。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 五大核心模块：[01-five-core-modules.md](01-five-core-modules.md)
- 适用场景与局限：[05-scenarios-and-limitations.md](05-scenarios-and-limitations.md)