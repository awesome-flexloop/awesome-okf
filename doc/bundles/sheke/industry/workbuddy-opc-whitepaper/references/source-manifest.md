---
type: Reference
title: "《WorkBuddy OPC 白皮书》信源采集与逐页覆盖台账"
description: "登记 W0（SPA 壳页）/P0（HTML 制品）/P1（正文数据源）三条获取路径与 X1（PDF 母本）未取得项，并逐页列出白皮书 32 页及各章小结、目录、封面、数据说明的章/节、知识归属与覆盖状态。"
tags: [WorkBuddy, OPC, 白皮书, 采集台账, 覆盖登记, OKF]
generated: { by: "seven-concepts-cmd", at: "2026-10-15" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15" }
status: flagged
stale_after: "2026-12-31"
sources:
  - { id: W0, resource: "https://www.workbuddy.link/p/FVCdAodl3HBHMMPypCogBi", title: "白皮书分享页（SPA 壳页）" }
  - { id: P0, resource: "https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/opc-whitepaper-mobile.html", title: "白皮书 HTML 制品（正文提取基准）" }
  - { id: P1, resource: "https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/janus.data.json", title: "白皮书正文数据源（节点交叉参照）" }
---

# 信源采集与逐页覆盖台账

> 双份登记：本台账记录**页级**覆盖；声明级覆盖见[原文事实清单](article-source.md)（F-001~F-357）。
> 采集缓存（壳页 HTML、制品 HTML、`janus.data.json`、提取脚本与提取后的 Markdown）留在任务临时目录，**不入库、不入 bundle**。

## 一、两条获取路径（SPA 壳页 vs 静态制品）

分享页 `www.workbuddy.link/p/<id>` 为**客户端渲染（SPA）**：纯 HTTP 抓取仅得 4 526 B 壳页（`window.__PUBLISH_BOOTSTRAP__` 指向静态制品基址，并携带 `publishVersion: 4`），**不含正文**；正文须经页面静态制品（P0 HTML / P1 JSON）提取。故本束采「壳页解析 → 制品提取」两段式路径，下表显著区分：

| 路径 | 信源代号 | 特征 |
| --- | --- | --- |
| SPA 壳页路径 | W0 | 仅得引导数据（制品基址 + `publishVersion`），**无正文**；用于确认制品快照版本 |
| 静态制品路径 | P0 / P1 | 正文以静态 HTML（P0）与正文 JSON（P1）落盘，**P0 为正文提取基准**，P1 仅作节点级交叉参照 |

## 二、采集台账（W0 / P0 / P1 / X1）

| 代号 | URL | 访问日期 | 获取方式 | 取得体量 | publishVersion | 知识归属 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W0 | <https://www.workbuddy.link/p/FVCdAodl3HBHMMPypCogBi> | 2026-10-15 | 纯 HTTP 抓取（SPA 客户端渲染，仅得壳页） | 4 526 B（壳页） | 4 | concepts/00（元信息：白皮书来源与制品口径） | 已访问；仅解析出制品基址与 `publishVersion: 4`，无正文 |
| P0 | <https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/opc-whitepaper-mobile.html> | 2026-10-15 | 静态制品 HTTP 获取 + 正文提取（`div.page` 分页 A4 版式，32 页） | 262 925 B（HTML）→ 提取 Markdown 32 页 / 25 508 字符 | 4 | 全部 F 条目的正文基准（concepts/01–06） | **已获取并解析——本束正文提取基准**；32 页正文全覆盖 |
| P1 | <https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/janus.data.json> | 2026-10-15 | HTTP 获取 JSON（3 385 节点，与 HTML 的 `data-page-node-id` 一一对应） | 717 277 B | 4 | references/（节点级交叉参照；不作为事实来源） | 已获取；仅作与 P0 的对照，未据其新增任何事实 |
| X1 | （未取得——本分享页未随附下载入口） | 2026-10-15（核验「未取得」状态） | 未取得 | — | — | references/source-manifest.md（未取得项显式登记） | **未取得**；不据版式推断内容 |

### 公开性判定与 `robots` 登记

- URL 无 `code`/`token`/邀请码等访问控制参数、无登录要求（页面内 `share/userinfo` 返回 `not login`，而正文制品仍可取）；页面具社交平台分享卡片 meta（`og:title` = WorkBuddy OPC 白皮书）；出品方为腾讯云 WorkBuddy 团队、正文含公开合作邀约 → 判定为**公开内容（Public）**，走标准工作流，产出物入 `doc/bundles/`。
- 页面 `robots` 为 **`noindex, nofollow`**（不索引）：不构成访问控制，**不影响**公开性判定，此处如实登记。
- P0 / P1 制品与 W0 同源、同公开性判定；X1 公开性判定不适用。

## 三、逐页 / 逐章覆盖状态表（页1–页32）

| 页 | 章 / 节 | 归属文档 | 覆盖状态 |
| --- | --- | --- | --- |
| 页1 | 封面（标题 / 副题 / 出品方 / 日期 / 版权 / 官网域名） | concepts/00 | 已覆盖（元信息） |
| 页2 | 目录（CONTENTS · 六章 32 节 · 各章起始页码） | concepts/00 | 已覆盖（元信息） |
| 页3 | 第一章导语 · §1.1 规模数据 · 脚注 1–2 | concepts/01 | 已覆盖 |
| 页4 | §1.2 超级个体 · §1.3 效率革命（Anthropic） · 脚注 3–4 | concepts/01 | 已覆盖 |
| 页5 | §1.3 效率革命（HDSR / HACR / smartcity.team） · §1.4 创业生命周期被重置 · 脚注 5–7 | concepts/01 | 已覆盖 |
| 页6 | §1.5 极致实验：Polsia · §1.6 陷阱一 / 陷阱二 · 脚注 8–9 | concepts/01 | 已覆盖 |
| 页7 | §1.6 陷阱三 · **第一章本章小结** | concepts/01 | 已覆盖 |
| 页8 | 第二章导语 · §2.1 硅基员工 · §2.2 「80% AI + 20% 品味」 · §2.3 三层能力模型（起） · 脚注 1–2 | concepts/02 | 已覆盖 |
| 页9 | §2.3 三层能力模型（表） · §2.4 六大商业模式 · 脚注 3 | concepts/02 | 已覆盖 |
| 页10 | §2.5 六条已验证 C 端赛道 · §2.6 万能套利公式 · 脚注 4 | concepts/02 | 已覆盖 |
| 页11 | §2.7 能力洗牌 · **第二章本章小结** · 脚注 5 | concepts/02 | 已覆盖 |
| 页12 | 第三章导语 · §3.1 北京朝阳（7 维度 10 措施） · 脚注 1 | concepts/03 | 已覆盖 |
| 页13 | §3.2 深圳行动计划（十维度表） · §3.3 全国覆盖（导语） · 脚注 2–3 | concepts/03 | 已覆盖 |
| 页14 | §3.3 全国覆盖（省市亮点表 + 行业数据佐证） · §3.4 政策落地配套缺口 · 脚注 4 | concepts/03 | 已覆盖 |
| 页15 | §3.4 末 · §3.5 园区与本地化生态 · **§3.5 数据说明** · 脚注 1–3 | concepts/03 | 已覆盖 |
| 页16 | **第三章本章小结** | concepts/03 | 已覆盖 |
| 页17 | 第四章导语 · §4.1 超级个体为何需要团队（四重结构需要表 + 数据佐证） · §4.2 组织竞争力公式（起） · 脚注 1–3 | concepts/04 | 已覆盖 |
| 页18 | §4.2 组织竞争力公式（释） · §4.3 三种超级团队形态（表 + AI Native 案例） · §4.4 三层产品架构 · 脚注 4 | concepts/04 | 已覆盖 |
| 页19 | §4.4.1 起步期专家矩阵 · §4.4.2 扩张期助理 · §4.4.3 联合期 Teams（起） | concepts/04 | 已覆盖 |
| 页20 | §4.4.3 Teams（机制表 + 上下文飞轮） · §4.5 混合架构 · **第四章本章小结** · 脚注 5 | concepts/04 | 已覆盖 |
| 页21 | 第五章导语 · §5.1 全流程解决方案（立项与验证表） | concepts/05 | 已覆盖 |
| 页22 | §5.1 产品开发与设计表 · 内容创作与分发表 | concepts/05 | 已覆盖 |
| 页23 | §5.1 销售变现与增长表 · 数据分析与决策表 | concepts/05 | 已覆盖 |
| 页24 | §5.1 财税法务合规表 · 个人 IP 与品牌表 | concepts/05 | 已覆盖 |
| 页25 | §5.2 案例一 韦优 · 案例二 蔡琛律师 | concepts/05 | 已覆盖 |
| 页26 | §5.2 案例三 智觉（李殿鹏） · **第五章本章小结** · **§5.2 案例数据说明** | concepts/05 | 已覆盖 |
| 页27 | 第六章导语 · §6.1 四个建设维度 · §6.2 各维度核心需求（政策与空间起） · 脚注 1 | concepts/06 | 已覆盖 |
| 页28 | §6.2 工具与算力 / 人才与标准 / 连接与传播 · §6.3 WorkBuddy 定位（表） · 脚注 2 | concepts/06 | 已覆盖 |
| 页29 | §6.4 OPC 从业者认证体系（表） · §6.5 合作形式（导语） · §6.5.1 政府 / 产业园区（起） | concepts/06 | 已覆盖 |
| 页30 | §6.5.1 合作模式表 · §6.5.2 媒体 / 智库（含合作模式表） · §6.5.3 KOL / 自媒体（起） | concepts/06 | 已覆盖 |
| 页31 | §6.5.3 合作层级表 · §6.5.4 行业专家 / 生态伙伴（含合作模式表） | concepts/06 | 已覆盖 |
| 页32 | 结语（生态共建呼吁与 WorkBuddy 定位复述） | concepts/06 | 已覆盖 |

## 四、集合比对结论（AC-1）

| 项 | 值 |
| --- | --- |
| 白皮书页码集合（页1–页32） | 32 |
| 已登记归属的页数 | 32 |
| 双向差集（脱漏 / 多登） | 0（`页码集合 − 已归属集合` = 0，`已归属集合 − 页码集合` = 0） |
| 六章覆盖 | 第一章（页3–7）/ 第二章（页8–11）/ 第三章（页12–16）/ 第四章（页17–20）/ 第五章（页21–26）/ 第六章（页27–32）全部有归属 |
| 非正文页（封面 / 目录 / 各章小结 / 数据说明 / 结语）归属 | 封面、目录 → concepts/00；各章小结 → concepts/01–05；§3.5 数据说明 → concepts/03；§5.2 案例数据说明 → concepts/05；结语 → concepts/06 |
| X1（PDF 母本）登记 | **未取得**，显式登记于本表台账，未静默跳过 |

> 白皮书无「第六章本章小结」（第六、七章以「结语」收束）；该收束页（页32）归属 concepts/06。全部 32 页均有归属文档与覆盖状态，正文页数（22）与非正文页数（封面 1 + 目录 1 + 各章小结 5 + 数据说明 2 + 结语 1 = 10）合计 32，与页面集合一致。
