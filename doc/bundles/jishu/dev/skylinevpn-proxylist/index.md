---
okf_version: "0.2"
type: bundle
title: "skylinevpn-proxylist：单文件规则数据仓的编译与发布"
description: "以 skylinevpn-proxylist 仓库（HEAD 9c6567c，2026-11-16）为一手信源，解析一份 26,698 条代理规则的单一数据文件如何由上游 gfwlist 每周编译、归约、提交并发布为带固定下载地址的 GitHub Release"
tags: [SkylineVPN, proxylist, gfwlist, AutoProxy, 规则表, 数据仓, GitHub Actions, 发布通道, 归约算法]
generated: { by: "seven-concepts-cmd", at: "2026-11-21T17:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T17:00:00+08:00" }
status: stable
stale_after: 2027-05-31
delegates_to:
  - concepts/index.md
  - examples/index.md
  - references/index.md
sources:
  - id: repo
    resource: "https://github.com/skyline-projext/skylinevpn-proxylist"
    title: "skylinevpn-proxylist 规则数据仓（HEAD 9c6567c，2026-11-16）"
  - id: facts
    resource: /references/facts.md
    title: "仓库事实登记 F-001 ~ F-068"
  - id: verification
    resource: /references/verification.md
    title: "核验报告、口径歧义与对抗审查"
---

# skylinevpn-proxylist：单文件规则数据仓的编译与发布

> **性质声明**：本包由 **seven-concepts-cmd 技能（R→I→E→C）** 对仓库 `HEAD 9c6567c`（2026-11-16）只读研读生成，属**一手仓库研读**，非产品文档转述，亦非实测报告。
>
> **三条硬边界**：① **未联网执行 `scripts/build.sh`**，构建行为来自脚本源码与注释；② **未访问 GitHub Release 页面**，发布行为来自 `release.yml` 与 git 元数据；③ **未接入任何客户端**，规则的匹配语义来自 `merge.py` 的归约代码反推，不代表任何消费端实现。
>
> 引用任何数字前请先读 [事实登记](references/facts.md) 与 [核验报告](references/verification.md)。

这个仓库只有 7 个受版本控制的文件：一份 389 KB 的规则清单、两个脚本、一个工作流、一份 README、一份专有许可、一份 `.gitignore`。没有源码、没有测试、没有依赖。

它做的事情可以一句话概括：**每周把上游 GFW 列表编译成本仓的三节规则表，提交，然后发布一个以日期命名的 GitHub Release。**

因此本束学的不是「VPN 怎么实现」，也不是「怎么翻墙」，而是三件工程问题：

1. **数据格式**：一份规则表如何用三种表达力（后缀 / 精确 / 正则）覆盖全部条目（[01](concepts/01-rule-file-format.md)）。
2. **编译归约**：上游 AutoProxy 语法如何被降维成三节，冗余条目如何被父后缀吸收（[02](concepts/02-upstream-digestion-pipeline.md)、[03](concepts/03-reduction-algorithm.md)）。
3. **发布通道**：一个数据文件如何获得稳定下载地址、如何在无变化时不产生空提交（[04](concepts/04-release-channel-and-fixed-url.md)）。

## 先读结论

| 问题 | 结论 | 依据 |
|------|------|------|
| 这是什么仓 | **单文件数据产品仓**：产物是 `proxy.list`，代码只是编译器 | F-007、F-013 |
| 规则表有多大 | 26,698 条：后缀 26,447 / 精确 84 / 正则 167，纯 ASCII | F-015、F-017 |
| 怎么更新 | 周一 00:00 UTC 定时拉上游 gfwlist → base64 解码 → 合并 → 有变化才提交 → 发版 | F-025 ~ F-031、F-045 ~ F-058 |
| 归约做了什么 | 父后缀吸收子域、精确项被后缀覆盖则删、全集排序 | F-040、F-041 |
| 最容易被误读的点 | 「每周一个版本」不等于「每周内容都变」：`v20261109` 指向 11-02 的提交 | F-006、C-2 |
| 最大的工程风险 | 全程**弱断言**：上游异常可产出近空表并照样发布；无签名、无校验和 | D-2、D-1 |

## 阅读路线

| 你的身份 | 路线 |
|---------|------|
| 使用者 / 接入方 | [01 规则格式](concepts/01-rule-file-format.md) → [演练 01 接入与更新策略](examples/01-consumer-integration.md) |
| 想复用这套流水线的人 | [02 上游消化](concepts/02-upstream-digestion-pipeline.md) → [03 归约算法](concepts/03-reduction-algorithm.md) → [04 发布通道](concepts/04-release-channel-and-fixed-url.md) → [演练 00 本地复现](examples/00-local-rebuild-and-idempotency.md) |
| 维护者 | [演练 02 维护者 Runbook](examples/02-maintainer-runbook.md) → [05 风险与边界](concepts/05-boundaries-and-risk-model.md) → [核验报告](references/verification.md) |
| 评估者 / 审计者 | [05 风险与边界](concepts/05-boundaries-and-risk-model.md) → [核验报告](references/verification.md) → [事实登记](references/facts.md) |

## 适用与不适用

**适用**：想了解「数据即产品」的最小可行仓库形态；想借鉴定时编译 + 固定下载地址的发布模式；需要弄清楚 `proxy.list` 三节到底怎么解释。

**不适用**：需要 VPN 协议或隧道实现；需要判断某站点是否真的可达；需要一份合规可用的访问控制清单（本仓只为自有产品供数，且无任何适用性担保）。

## 与同组知识包的关系

- 与 [skylinevpn-cli](../skylinevpn-cli/index.md) 同属 SkylineVPN 组织：前者交付**二进制与安装器**，本包交付**规则数据**；两者都用「tag + 固定地址」做分发，但本包的发布门显著更弱（无身份锁、无泄漏扫描、无校验和）。
- 与 [github](../github/index.md) 的 Actions 主题互补：那里讲工作流语法，这里讲一个真实工作流如何被当作定时发布机使用。

## 知识包结构

```text
skylinevpn-proxylist/
├── index.md      本页：元数据、性质声明、阅读路线
├── import.md     导入说明：独立 bundle / MyST 站点 / Agent 上下文三条路径
├── log.md        生成日志与质量门自评
├── concepts/     6 篇：定位、格式、消化、归约、发布、边界
├── examples/     3 篇：本地复现、消费方接入、维护者 Runbook
└── references/   facts（F-001~F-068）、verification（C/D 清单）、索引
```

```{toctree}
:maxdepth: 1
:caption: 本知识包

concepts/index
examples/index
references/index
import
```
