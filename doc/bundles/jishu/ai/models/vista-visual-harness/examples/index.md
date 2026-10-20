---
type: category
title: "实战示例"
description: "VISTA 知识包的三篇可执行示例——环境准备与授权配置、ARC-AGI-3 单局与批量、其余三个基准的运行方式。"
tags: [vista, examples, setup, run]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
  - id: article-source
    resource: /references/article-source.md
---

# 实战示例

本目录共 **3 篇**可执行示例，全部命令逐条对应仓库固定 commit `c97c354f` 的 README 与 `scripts/` [F-086]。

| # | 文档 | 内容 | 适用对象 |
|---|------|------|---------|
| 00 | [环境准备与授权配置](00-setup-and-auth.md) | 前置检查表、取源码（固定 commit）、虚拟环境与固定版本安装、`.env` 凭证、Docker 镜像、Agent CLI 安装、完成检查表 | 第一次接触 VISTA 的读者 |
| 01 | [ARC-AGI-3 单局与批量](01-arc3-single-and-batch.md) | 单局命令与参数表、25 局批量、竞争模式（账号池/调度/限流）、运行产物解读、失败排查表 | 复现论文主结果 |
| 02 | [其余三个基准](02-other-benchmarks.md) | GameWorld / AI GameStore / BabyVision 的环境准备、单次与批量运行、各自协议常量与评分口径 | 复现跨基准结果 |

## 关于 examples/ 的设立

本束第一轮交付时**不设** `examples/`，理由是操作可复现性两问的第一问为"否"——当时唯一的信源是**博文**，博文未给出任何读者可照做的流程。

本轮补充源码后该前提改变：仓库 README 提供完整的可复现路径（固定版本、前置命令、参数语义、故障模式）[F-075][F-086]，因此设立 `examples/` [F-130]。

> **两条口径同时成立**：本束**仍是一篇论文解读与源码导读**，不是"从零部署教程"——示例覆盖的是**跑通与复现实验**，不是把 VISTA 部署为生产服务。

## 执行顺序建议

```
00 环境准备与授权配置
   └─ 01 ARC-AGI-3 单局与批量   ← 论文主结果在此
        └─ 02 其余三个基准        ← 跨基准验证在此
```

```{toctree}
:hidden:
:maxdepth: 2

00-setup-and-auth
01-arc3-single-and-batch
02-other-benchmarks
```
