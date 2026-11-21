---
okf_version: "0.2"
type: bundle
title: "skylinevpn-cli：封闭二进制的公开发行工程"
description: "以 skylinevpn-cli 发行仓库（HEAD 415d0bb，v3.0.1）为一手信源，解析公开仓库如何承载封闭二进制产品的安装、校验、暂存、门禁与发布；含产品命令面、双寻址发行拓扑、递归泄漏扫描与信任边界"
tags: [SkylineVPN, CLI, VPN, 发行工程, 供应链安全, GitHub Release, 安装器, 泄漏防护]
generated: { by: "seven-concepts-cmd", at: "2026-11-21T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T12:00:00+08:00" }
status: stable
stale_after: 2027-05-31
delegates_to:
  - concepts/index.md
  - examples/index.md
  - references/index.md
sources:
  - id: repo
    resource: "https://github.com/skyline-projext/skylinevpn-cli"
    title: "skylinevpn-cli 发行仓库（HEAD 415d0bb，v3.0.1）"
  - id: facts
    resource: /references/facts.md
    title: "仓库事实登记 F-001 ~ F-072"
  - id: verification
    resource: /references/verification.md
    title: "核验报告、口径冲突与对抗审查"
---

# skylinevpn-cli：封闭二进制的公开发行工程

> **性质声明**：本包由 **seven-concepts-cmd 技能（R→I→E→C）** 对仓库 `HEAD 415d0bb`（`v3.0.1`）只读研读生成，属**一手仓库研读**，非官方文档转述，亦非实测报告。
>
> **三条硬边界**：① **未执行 `skyline` 二进制**，产品行为均来自 README 与 CHANGELOG；② **未运行任何安装器**，安装期行为来自 README 与 `build_release.py` 的改写规则；③ **未访问 GitHub Release 与服务端**，资产清单与上传者核验是流程要求而非本次实测。
>
> 引用任何数字前请先读 [事实登记](references/facts.md) 与 [核验报告](references/verification.md)。

`skylinevpn-cli` 是一个 VPN 客户端的**公开发行仓**：仓库里没有产品源码，只有六种语言的用户文档、版本记录、专有许可，以及 `tools/` 下四个发布脚本与一份发行手册（F-007）。

因此本束学的是两件事，而不是「VPN 怎么实现」：

1. **产品面**：`skyline` 命令怎么用、支持哪些平台、安装/更新/卸载怎么走。
2. **交付面**：三个上游 CI 束如何被校验、改写、扫描、清单化，再通过多重门禁发布成 GitHub Release。

## 先读结论

| 问题 | 结论 | 依据 |
|------|------|------|
| 这个仓库能学到什么 | 一份可审计的**发行工程**样本：命中数断言、自洽重写、递归解包泄漏扫描、身份锁与发布门 | F-046、F-056、F-058、F-065 ~ F-072 |
| 它不能证明什么 | 产品安全性、协议实现、服务端行为；也**不抗发布方失陷**（无签名） | F-007、D-1 |
| 最容易误读的点 | 「校验和通过 = 安全」；「安装器内嵌哈希与 `SHA256SUMS.txt` 二选一」 | C-1、[06](concepts/06-trust-model-and-boundaries.md) |
| 发布流程的硬门在哪 | `publish-release.sh`：token 属主、身份全历史、校验和、HEAD==origin/main、人工确认 | F-071、F-072 |

## 阅读路线

| 你的身份 | 路线 |
|---------|------|
| 使用者 | [01 产品面](concepts/01-product-surface.md) → [演练 00 安装校验卸载](examples/00-install-verify-uninstall.md) → [演练 01 日常与排障](examples/01-daily-usage-and-troubleshooting.md) |
| 维护者 | [02 发行拓扑](concepts/02-distribution-topology.md) → [04 暂存管线](concepts/04-release-staging-pipeline.md) → [05 身份与泄漏门](concepts/05-identity-and-leak-gates.md) → [演练 02 发布 Runbook](examples/02-maintainer-release-runbook.md) |
| 评估者 | [06 信任模型与边界](concepts/06-trust-model-and-boundaries.md) → [核验报告](references/verification.md) → [事实登记](references/facts.md) |

## 适用与不适用

**适用**：想了解一个闭源 CLI 产品如何做公开发行；想借鉴发布门禁设计；需要按官方文档安装与排障。

**不适用**：需要 VPN 协议/加密实现细节；需要审计二进制安全性；需要可直接复用的通用发布框架（脚本与上游安装器变量强耦合，应抽取模式而非照搬）。

## 知识包结构

```text
skylinevpn-cli/
├── index.md      本页：元数据、性质声明、阅读路线
├── import.md     导入说明：独立 bundle / MyST 站点 / Agent 上下文三条路径
├── log.md        生成日志与质量门自评
├── concepts/     7 篇：定位、产品面、发行拓扑、安装校验链、暂存管线、身份门、信任模型
├── examples/     3 篇：安装校验卸载、日常排障、维护者 Runbook
└── references/   facts（F-001~F-072）、verification（C/D 清单）、索引
```

```{toctree}
:maxdepth: 1
:caption: 本知识包

concepts/index
examples/index
references/index
import
```
