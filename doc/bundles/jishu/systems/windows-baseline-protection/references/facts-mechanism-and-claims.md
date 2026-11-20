---
type: Reference
title: "原文事实登记卷二：检查项、应用侧策略与作者主张（F-025~F-048）"
description: "逐条事实登记下半卷——F-025~F-048，覆盖首版检查项与 7/8 口径差异、可验证安全状态的三种读出形式、应用侧策略归属、早期伙伴名单，以及源文中须降级为观点的陈述。"
tags: ["windows-baseline-protection", "事实登记", "F编号", "基线保护", "证据分层"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: S1
    url: "https://mp.weixin.qq.com/s/sIb3u-ZMf-l2sRrz2iB8Vg"
  - id: volume-one
    resource: "/references/article-source.md"
  - id: verification
    resource: "/references/verification.md"
---

# 原文事实登记卷二（F-025~F-048）

> 口径类型与信源 ID 沿用[卷一](article-source.md)。本卷 F-025~F-048 与卷一 F-001~F-024 合为连续区间 **F-001~F-048**。
> 标 `author_claim` 的条目是作者判断或推测，**不得当作平台口径或既定事实引用**。

---

## E. 首版检查项与状态性质（F-025~F-032）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-025 | 源文称把 TPM、安全启动、内存完整性、只加载已签名驱动等「一共 8 项安全检查」打包，给出一个通过/不通过结果 | page_fact | S1 | 第 8 段 |
| F-026 | 微软 IT Pro Blog 列首版 8 项：安全处理器、安全启动、VBS、内存完整性、仅已签名驱动、Windows 认证驱动、内核调试保护、易受攻击驱动保护 | official_fact | M2 | criteria 节 |
| F-027 | 官方说明列表中每一项都是 Windows 现有能力；新增的是把它们作为**一个可证明结果**一起评估 | official_fact | M2 | criteria 节 |
| F-028 | 设备仅当满足全部要求时报告 `true`，否则 `false`；结果由平台计算、以硬件为根，用户、IT 管理员与应用均可读取 | official_fact | M2 | 简化防护节 |
| F-029 | 微软支持页按 **7 类**呈现，把「仅已签名驱动」与「Windows 认证驱动」合并为「测试签名保护」；媒体按 **8 项**拆分。差别来自分类口径，不是任一方写错 | official_fact | M7/T4 | 支持页 / 转引 |
| F-030 | 状态在启动时由安全处理器测量；每项自启动起强制执行，关闭任一项都需要重启，故用户与应用只需查询一次 | official_fact | M2 | How it works 节 |
| F-031 | 状态可版本化、标准随威胁演进提高，官方原文「This is the floor, not the ceiling」；通过当前版本的设备可能不通过后续版本 | official_fact | M2 | criteria 节 |
| F-032 | 术语冲突：本功能与 2024 年前后经 Security Compliance Toolkit 分发的 Windows Security Baseline 配置策略包**同名不同物** | official_fact | T4 | 术语辨析 |

## F. 三种读出形式与策略归属（F-033~F-039）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-033 | 源文强调结果「不是给系统自己用的，是开放给软件开发商读取的」 | page_fact | S1 | 第 9 段 |
| F-034 | 官方列三种结果形式：简单状态查询（是/否）、详细报告（缺哪些要求）、硬件支持的证明令牌（由安全依赖方验证） | official_fact | M2 | How it works 节 |
| F-035 | 源文列应用可选动作：弹出警告、限制联网和登录、砍掉部分功能、记录设备状态并上报、直接拒绝启动 | page_fact | S1 | 第 11 段引用块 |
| F-036 | 官方与多家媒体列 `allow` / `warn` / `limit features` / `block` 四档，并强调平台不裁决、策略由开发者决定 | official_fact | M2/T2 | 官方 + 报道 |
| F-037 | 微软 Windows 产品经理 Brandon Bray 表述「The platform reports the state; you own the policy」 | official_fact | T4 | 引述 |
| F-038 | 源文转述「平台只是报告状态，策略由开发者决定」，类比安卓权限控制，并评价为「依旧好一手甩锅」 | author_claim | S1 | 第 15 段 |
| F-039 | 源文称银行与反作弊场景可用硬件生成的证明令牌把结果放到服务端验证和记录，对本地绕过制造更多限制 | page_fact | S1 | 第 17 段 |

## G. 早期伙伴、用户侧与影响（F-040~F-045）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-040 | 源文称已加入测试的有 Adobe、暴雪、1Password 与「一些在线考试平台」 | page_fact | S1 | 第 13 段 |
| F-041 | 多源完整名单为 Adobe、Battle.net (Blizzard)、1Password、Raycast、Schoolyear（在线考试软件）；源文未点名 Raycast 与 Schoolyear | official_fact | M2/T2/T4 | 交叉比对 |
| F-042 | 源文称「Adobe 你懂的，用来打击盗版，检测不通过就拒绝启动」；多家报道明确**没有任何早期伙伴公开承诺拦截未通过设备**，Adobe 口径为补充反恶意与反盗版工作、Battle.net 口径为不增加玩家摩擦前提下提升安全 | author_claim | S1 | 第 13 段 |
| F-043 | 个人/未托管设备在「设置 > 安全 > 基线保护」查看；受管理设备由 Microsoft 365 管理中心 baseline security mode 管理 | official_fact | M2/M3 | 官方 |
| F-044 | 源文称关过内存完整性的玩家、为 Linux 双系统关过安全启动的用户「都在不通过的名单里」，「以后想要打开正版软件，就要先去 BIOS 里重启还原」 | author_claim | S1 | 第 16 段 |
| F-045 | 《战地风云 6》的 Javelin 反作弊已要求开启安全启动，属「应用自行要求设备安全状态」的既有先例 | page_fact | T2/T5 | 报道 |

## H. 作者观点与推测（F-046~F-048）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-046 | 源文列举 Defender 黑历史：把自家 Office 标记成病毒、删恶意文件连带删用户文件、把 Win11 核心根证书当木马、免费杀软评测倒数第二 | author_claim | S1 | 第 19 段 |
| F-047 | 源文称「以前是保护电脑不被别人动…现在也开始保护厂商的软件不被人动了」，并称「手机系统在查开发者的身份，电脑在查设备的身份」 | author_claim | S1 | 第 21 段 |
| F-048 | 源文推测 AI 未来「完全有能力写出在你电脑里寄生且很难被察觉到的程序」，并自述「说起来有点科幻，这也是以后的事情了」 | author_claim | S1 | 第 22 段 |

---

**卷二计数**（脚本机械统计）：`page_fact` 6 条 / `official_fact` 12 条 / `author_claim` 6 条，共 **24 条**，F-025~F-048 连续无跳号。
**全包合计**（脚本机械统计）：`page_fact` 20 / `official_fact` 21 / `author_claim` 7 = **48 条（F-001~F-048）**，无跳号、无重号。

> 补充信源 ID：**M7** = 微软 Baseline protection 支持页（经 T4 转引）。
