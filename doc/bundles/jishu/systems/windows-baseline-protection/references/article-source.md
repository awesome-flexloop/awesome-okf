---
type: Reference
title: "原文事实登记卷一：元信息、智能应用控制与时间线（F-001~F-024）"
description: "微信公众号「果核剥壳」Win11 智能应用控制与基线保护一文的逐条事实登记上半卷——F-001~F-024，覆盖文章元信息、智能应用控制的源文陈述与微软官方口径、以及基线保护的发布时点。"
tags: ["windows-baseline-protection", "事实登记", "F编号", "智能应用控制", "Windows 11"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: S1
    url: "https://mp.weixin.qq.com/s/sIb3u-ZMf-l2sRrz2iB8Vg"
    title: "Win11新功能上线，以后你要用「和谐版」软件难了（果核剥壳，2026-11-20）"
  - id: verification
    resource: "/references/verification.md"
---

# 原文事实登记卷一（F-001~F-024）

> **本表不含执行者推断。** 每条为源文明示内容、微软官方一手口径，或独立媒体的可核对陈述。
> 口径类型：`page_fact`（源文/媒体明示、可逐字核对）/ `official_fact`（微软官方一手）/ `author_claim`（作者的价值、趋势、因果判断与推测）。
> 全包事实区间 **F-001~F-048**，下半卷见[机制与主张](facts-mechanism-and-claims.md)；核验结论见[P0 核验报告](verification.md)。

- **一手信源 S1**：微信公众号「果核剥壳」，署名「果核」，标注原创，2026-11-20 08:40，属地四川
- **采集时间**：2026-11-20；**采集通道**：WebFetch 直取页面正文
- **信源距离**：第三方科技评论（非厂商发布、非官方文档），文中机制描述多为转述
- **官方信源**：M1 Windows Experience Blog（Ignite 2026，11-17）· M2 Windows IT Pro Blog（A verifiable security state）· M3 Insider build 26340.10013 发行说明 · M4 Smart App Control FAQ · M5 Smart App Control overview · M6 适用于 Windows 的应用程序控制
- **媒体信源**：T1 IT之家（11-18）· T2 Wccftech（11-18）· T3 Windows Latest（经 T1/T2 转引）· T4 ghacks / neoteo / sffgeek / pureinfotech · T5 超能网（11-18）

---

## A. 文章元信息（F-001~F-003）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-001 | 文章标题《Win11新功能上线，以后你要用"和谐版"软件难了》；公众号「果核剥壳」，署名「果核」，标注原创，2026-11-20 08:40，属地四川 | page_fact | S1 | 标题/署名/日期行 |
| F-002 | 结构为三段：先述「智能应用控制」拦截现象，再转入 11 月 18 日预览的「基线保护」，结尾是平台信任关系与 AI 威胁的评论 | page_fact | S1 | 全文 |
| F-003 | 源 URL 无 `code`/`token`/邀请码参数，未登录即可读取正文，判为公开内容 | page_fact | S1 | URL / 采集记录 |

## B. 智能应用控制：源文陈述（F-004~F-011）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-004 | 源文画像：使用原版 Windows、未禁用 Windows 安全中心、仅装火绒共存的用户 | page_fact | S1 | 第 2 段 |
| F-005 | 源文称这类用户会遇到「软件打开后提示某个 DLL 文件被禁用，然后怎么也打不开」 | page_fact | S1 | 第 2 段 |
| F-006 | 源文点名新版 Quicker2 与部分网络工具受影响，并称「实际影响的软件数量更多」 | page_fact | S1 | 第 2 段 |
| F-007 | 源文称 V2EX 上有人提问该现象 | page_fact | S1 | 第 3 段 |
| F-008 | 源文称第一反应易是「中毒或者软件坏了」，实际是 Windows 安全中心在查签名 | page_fact | S1 | 第 3 段 |
| F-009 | 源文对比 SmartScreen：智能应用控制「连仍要运行的按钮都没有」，在运行加载阶段即被拦 | page_fact | S1 | 第 4 段 |
| F-010 | 源文称其结合数字签名与微软云端信誉库判断软件能否运行，没签名或信誉不够直接拦下 | page_fact | S1 | 第 5 段 |
| F-011 | 源文称「被拦得最多的就是个人开发者的小工具和绿色软件」，并推论「以后禁用 Windows 安全中心要成玩机必选项」 | author_claim | S1 | 第 5–6 段 |

## C. 智能应用控制：微软官方口径（F-012~F-016）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-012 | 判定顺序：云端智能安全服务先作信心预测；判为恶意/PUA 即阻止；无法预测时检查有效签名；未签名或签名无效视为不受信任并阻止 | official_fact | M4 | FAQ「How does it work」 |
| F-013 | 官方明确「There is currently no way to bypass Smart App Control protection for individual apps」，建议关闭 SAC 或联系开发者签名 | official_fact | M4 | FAQ「let this one specific app through」 |
| F-014 | SAC 有评估模式与强制模式；企业托管、开发者模式、S 模式、关闭可选诊断数据等情形会被自动关闭 | official_fact | M5/M4 | overview / FAQ |
| F-015 | 自 Windows 11 22H2 起提供；其预测服务在应用控制文档中称 Intelligent Security Graph (ISG) | official_fact | M6 | 应用控制文档 |
| F-016 | 近期更新允许无需全新安装即可在 Windows 安全中心启用/重新启用 SAC；SAC 与第三方杀软并行、不替代杀软 | official_fact | M4 | FAQ |

## D. 基线保护：发布时点与状态（F-017~F-024）

| F | claim | type | src | locator |
|---|---|---|---|---|
| F-017 | 源文称「11月18日，微软在 Windows 11 测试版里预览添加了一个叫基线保护的新功能」 | page_fact | S1 | 第 8 段 |
| F-018 | 微软 Windows Experience Blog 于 2026-11-17 在 Ignite 2026 宣布 baseline protection「now available in preview」 | official_fact | M1 | Ignite 2026 安全总览 |
| F-019 | Insider Experimental 构建 26340.10013 发行说明标注「2026 年 11 月 17 日更新」，基线保护与新「安全」页逐步推出 | official_fact | M3 | release notes |
| F-020 | 微软 IT Pro Blog 明确「general availability planned for 2027」 | official_fact | M2 | 开篇 |
| F-021 | 源文称「目前这些能力还在 Insider 测试阶段，计划 2027 年正式上线」 | page_fact | S1 | 第 14 段 |
| F-022 | IT之家 2026-11-18 援引 Windows Latest 同日博文，Wccftech、超能网等同期转述 | page_fact | T1/T2/T5 | 报道日期 |
| F-023 | 微软 IT Pro Blog 回溯：2026 年 2 月已阐述「默认更安全」方向——系统强制透明、以用户为中心的同意、易验证的安全基线 | official_fact | M2 | 开篇 |
| F-024 | 口径差异：11/18 是媒体转述时点，官方宣布日与构建说明更新日均为 11/17；源文未区分两者 | page_fact | S1/M1/M3 | 交叉比对 |

---

**卷一计数**（脚本机械统计）：`page_fact` 14 条 / `official_fact` 9 条 / `author_claim` 1 条，共 **24 条**，F-001~F-024 连续无跳号。
