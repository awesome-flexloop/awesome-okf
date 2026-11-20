---
type: Concept
title: "04 · 应用侧策略归属：四档动作与本包唯一实质勘误"
description: "平台提供 allow/warn/limit/block 四档但不裁决、策略由每个应用自行决定；完整早期伙伴名单，以及把「可选能力」写成「厂商既定策略」的实质勘误。"
tags: ["windows-baseline-protection", "概念", "策略归属", "勘误", "证据分层"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: facts-two
    resource: "/references/facts-mechanism-and-claims.md"
  - id: verification
    resource: "/references/verification.md"
---

# 04 · 应用侧策略归属

源文最抓人的一句是「这个结果不是给系统自己用的，是开放给软件开发商读取的」（F-033）。方向对；但接下来发生了本包**唯一一处实质勘误**。

## 四档动作，平台不裁决

拿到 `false` 之后，微软列出四档（F-036）：

| 档位 | 应用可以做什么 |
|---|---|
| `allow` | 照常运行 |
| `warn` | 弹出安全警告 |
| `limit features` | 限制部分功能（源文举例：限制联网和登录、砍掉部分功能、记录设备状态并上报，F-035） |
| `block` | 拒绝启动 |

**关键在于谁选这一档**：微软明确平台只报告状态，策略由开发者决定（F-036）；Windows 产品经理 Brandon Bray 的表述是 `The platform reports the state; you own the policy`（F-037）。源文转述这一点是准确的，只是附了「依旧好一手甩锅」的评价——那是作者观点（F-038），不是机制事实。

换句话说，微软没有新增一条「Windows 会拦软件」的规则，而是**把裁决权下放**了。这也是[洞察 2](../references/insights-and-pattern.md)：标题式叙事说「微软收紧」，机制事实是微软退出逐设备裁决。

## 早期伙伴：谁在测试，以及他们承诺了什么

| 源文（F-040） | 多源完整名单（F-041） |
|---|---|
| Adobe、暴雪、1Password、「一些在线考试平台」 | **Adobe、Battle.net (Blizzard)、1Password、Raycast、Schoolyear**（在线考试软件） |

源文漏了 Raycast，把 Schoolyear 泛化成「一些在线考试平台」（核验报告 E5）。另据 T2，微软还与 Epic Games、CrowdStrike、Dropbox 等探讨集成，属**另一份探讨名单**，本包不与测试名单混记。

各家公开口径：

- **Adobe**：标准化验证可**补充**其现有的反恶意与反盗版工作；
- **Battle.net**：在不给玩家增加不必要摩擦的前提下提升平台安全；
- **Schoolyear**：考试前确认学生设备符合要求，是场景最明确的一例。

## ❌ 本包唯一实质勘误（E4）

**源文写法**（F-042）：「Adobe 你懂的，用来打击盗版，**检测不通过就拒绝启动**」。

**核验结论**：多家独立报道明确 **Adobe 与 Battle.net 均未宣布会拦截未通过的设备，也没有任何早期伙伴公开承诺采用 `block` 档**。把「开发者可选的 `block` 档」写成「Adobe 已采用的策略」，是把**能力**当成了**策略**。

本包所有页面统一按「平台提供四档、伙伴未承诺任何一档」呈现，并在[核验报告 C11](../references/verification.md) 单列。这不是数字小误，它会直接改变读者对「我的软件明天还能不能打开」的判断。

> **纪律**：参与测试 ≠ 已选档位 ≠ 已承诺拦截。截至 2026-11-20，各伙伴实际档位未公开（缺口 G3）；预览期是否存在默认拦截策略亦无公开证据（缺口 G1）。

## 已有先例，但仍是应用各自决定

《战地风云 6》的 Javelin 反作弊已要求开启安全启动（F-045）——说明「应用自行要求设备安全状态」并非新事。基线保护做的是把这类自建检查**标准化**，而不是把拦截变成系统默认。

要判断某款具体软件会不会拦你，不要从「Windows 版本」或「厂商在名单里」推断，按[五问核对表](../examples/02-read-an-app-policy.md)逐项查公开策略。

> 下一步：[05 · 信任边界的位移](05-trust-boundary-shift.md)。
