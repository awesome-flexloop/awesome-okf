---
okf_version: "0.2"
type: bundle
title: "Win11 智能应用控制与基线保护：设备信任状态如何开放给应用"
description: "微信公众号科技评论转化教程——以微软 7 个官方一手源为机制骨架，讲清智能应用控制（SAC）与 Windows 基线保护的区别、首版 8 项检查与 7 类口径、可版本化状态的三种读出形式、应用侧四档策略归属；48 条编号事实 F-001~F-048、16 项 P0 核验、6 组口径分账、6 项缺口，含唯一实质勘误「把开发者可选策略写成厂商既定策略」。route: chaptered-summary，非逐字转录。"
tags: ["windows-baseline-protection", "Windows 11", "智能应用控制", "基线保护", "设备证明", "信任模型", "博文转化", "教程"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: article
    url: "https://mp.weixin.qq.com/s/sIb3u-ZMf-l2sRrz2iB8Vg"
    title: "Win11新功能上线，以后你要用「和谐版」软件难了（果核剥壳，2026-11-20）"
  - id: facts-one
    resource: "/references/article-source.md"
    title: "原文事实登记卷一（F-001~F-024）"
  - id: facts-two
    resource: "/references/facts-mechanism-and-claims.md"
    title: "原文事实登记卷二（F-025~F-048）"
  - id: verification
    resource: "/references/verification.md"
    title: "P0 核验报告"
  - id: sources
    resource: "/references/sources-and-glossary.md"
    title: "信源清单与术语表"
---

# Win11 智能应用控制与基线保护

> **⚠️ flagged / 预览期功能。** 本包由一篇**第三方科技评论**切入，机制骨架全部改锚到**微软官方一手文档**（7 个源）。源文含 **1 处实质勘误**：「Adobe 检测不通过就拒绝启动」——多家独立报道明确**没有任何早期伙伴公开承诺拦截未通过设备**（[C11 / E4](references/verification.md)）。另有 5 组口径差异并列登记、6 项已知缺口。引用前请先读 [P0 核验报告](references/verification.md)。
> 本包走 `route: chaptered-summary`（深度摘要 + 原创改写），**不逐字转录**源文。

## 一句话结论

变的不是防护清单（8 项全是既有能力），而是**谁能读结果**：Windows 把设备安全状态合成一个可版本化的 `true`/`false`，开放给应用；**平台提供四档动作但不裁决，策略由每个应用自己定**。

## 主题关联

| 关联知识包 | 关系 |
|---|---|
| [WSL 子系统中文教程](../wsl/index.md) | 同属 Windows 系统层；WSL 涉及虚拟化与安全启动的启用前提，可与基线检查项对照 |
| [WSL 自定义发行版构建](../wsl-custom-distro/index.md) | 自定义 rootfs 与 UEFI/安全启动配置，属本包「固件级修复路径」的上游场景 |
| [PowerShell 5 困境防御](../powershell-hell/index.md) | 同为「系统层约束导致操作失败」的防御型教程，可对照失败模式写法 |
| [kylin-wayland-compositor 源码精读](../kylin-wayland-compositor/index.md) | 同组系统层精读，含安全门户章节，可对照「平台把能力开放给谁」的接口视角 |
| [RTX Spark Windows 本地 AI PC 概念教程](../../iot/rtx-spark/index.md) | 同为 Windows 平台概念教程 + 厂商口径核验，可对照「厂商自宣与独立核验分栏」写法 |

## 阅读路径

| 想了解 | 读 |
|---|---|
| 这两个功能到底是不是一回事、什么时候发布的 | [00 · 两个机制与一条时间线](concepts/00-two-mechanisms-and-timeline.md) |
| 为什么绿色软件会被拦、能不能单独放行 | [01 · 智能应用控制](concepts/01-smart-app-control.md) |
| 8 项是哪 8 项、为什么别处写 7 类 | [02 · 首版检查项与 7/8 口径](concepts/02-baseline-criteria.md) |
| 状态怎么测、什么叫可版本化、证明令牌是什么 | [03 · 可验证安全状态](concepts/03-verifiable-security-state.md) |
| 谁决定拦不拦、Adobe 那句话错在哪 | [04 · 应用侧策略归属](concepts/04-app-side-policy.md) |
| 作者关于「信任边界」的判断能不能引用 | [05 · 信任边界的位移](concepts/05-trust-boundary-shift.md) |
| 动手查自己这台电脑 | [01 · 设备自查与修复路径](examples/01-check-your-device.md) |
| 判断某款软件会不会拦我 | [02 · 五问核对表](examples/02-read-an-app-policy.md) |
| 每条事实的信源、核验、勘误与缺口 | [事实登记卷一](references/article-source.md) / [卷二](references/facts-mechanism-and-claims.md) / [核验报告](references/verification.md) |
| 方法论洞察、模式与对抗审查 | [洞察与模式](references/insights-and-pattern.md) / [V 门记录](references/adversarial-review.md) |

## 核心结论速查

| 结论 | 依据 | 核验 |
|---|---|---|
| 首版 8 项全是 Windows 现有能力，新增的是「一起评估为一个可证明结果」 | F-027、F-028 | ✅ M2 官方 |
| 官方宣布与构建标注均为 **2026-11-17**，源文 11/18 是媒体转述时点 | F-017~F-019、F-022 | ⚠️ 并列（E1） |
| **8 项 / 7 类并列**：支持页把两条驱动规则合并为测试签名保护 | F-026、F-029 | ⚠️ 口径差异，不裁决（E2） |
| 状态启动时测量、关闭任一项需重启，一次查询即可 | F-030 | ✅ M2 官方 |
| 状态可版本化，通过首版 ≠ 通过后续版本 | F-031 | ✅ M2 官方 |
| 三种读出：简单状态 / 详细报告 / 硬件证明令牌 | F-034 | ✅ M2 官方 |
| 平台提供 allow/warn/limit/block 四档但**不裁决**，策略归应用 | F-036、F-037 | ✅ M2 官方 + Bray 引述 |
| 早期伙伴 5 家（Adobe、Battle.net、1Password、Raycast、Schoolyear） | F-040、F-041 | ⚠️ 源文不完整（E5） |
| 「Adobe 检测不通过就拒绝启动」 | F-042 | ❌ **实质勘误**：无伙伴公开承诺拦截（E4） |
| 计划 2027 正式可用 | F-020、F-021 | ✅ M2 官方 |
| Defender 黑历史、AI 恶意软件推演 | F-046、F-048 | ⭕ **不采信**（C15、C16） |

## 已知边界

- **证据结构**：1 个评论源（S1）+ 7 个微软官方源（M1~M7）+ 5 组媒体交叉（T1~T5）。48 条事实分 `page_fact` 20 / `official_fact` 21 / `author_claim` 7 三类（脚本机械统计，F-001~F-048 连续无跳号）。
- **唯一实质勘误 E4**：能力 ≠ 策略。所有页面统一写「平台提供四档、伙伴未承诺任何一档」。
- **并列分账**：E1 时点、E2 数量、E5 名单、E6 术语——均并列登记，**不合并、不抹平、不裁决**。
- **已知缺口 G1~G6**：默认拦截策略无公开证据 / 版本化规则未发布 / 伙伴档位未公开 / GA 版本渠道未定 / 源文三处无出处 / 本地应用采用情况无公开信息。
- **性质**：概念教程 + 可执行自查，**不是**兼容性结论、性能建议、趋势预测或法律意见；不输出「某软件能否打开」的保证或概率。
- **时效**：Insider 预览期，`status: flagged`；机制细则可能调整。

## 时效与复核触发

| 项 | 值 |
|---|---|
| 登记时点 | 2026-11-20 |
| `status` | **flagged** |
| `stale_after` | **2027-03-31** |
| 复核触发 | ① 2027 正式可用发布；② 官方发布基线版本增项与版本化规则；③ 任一早期伙伴公布实际策略档位；④ 首版检查项调整；⑤ 例行复核 |

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
examples/index
references/index
log
```
