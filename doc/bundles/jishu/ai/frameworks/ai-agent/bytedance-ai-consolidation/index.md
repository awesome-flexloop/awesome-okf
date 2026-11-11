---
okf_version: "0.2"
type: bundle
title: "字节 AI 大洗牌：扣子与 TRAE 收口，豆包成为超级入口"
description: "运营派 AI Lab 行业评论的知识化重组（非操作教程）——扣子企业版两阶段下线、TraeWork/TraeCode 合并为 TRAE、TRAE CN 账号并入豆包飞书、豆包工作承接工作场景，附五条洞察与三个可迁移判读模式；49 条事实、13 项 P0 核验（8✅/4⚠️/1❌）、5 项勘误"
tags: [字节跳动, 扣子, Coze, TRAE, 豆包工作, 豆包, 超级入口, Agent, 账号体系, 组织整合, 行业分析]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-11T11:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-11T12:10:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: article
    resource: https://mp.weixin.qq.com/s/ibCX76N6j82B10AEn2SN9g
    title: 运营派 AI Lab《字节AI大洗牌，扣子和TRAE陨落》（作者欧阳俊杰）
  - id: coze-official
    resource: https://docs.coze.cn/enterprise-plan-discontinuation-notice
    title: 扣子企业版下线公告（2026-10-29）
  - id: trae-merge-report
    resource: https://feng.ifeng.com/c/8x51bt8r6yN
    title: 硅星人《TRAE 合并 Code 与 Work》2026-10-09
  - id: sina-finance
    resource: https://finance.sina.com.cn/wm/2026-08-24/doc-inipkzxw2928801.shtml
    title: 新浪财经《独家｜字节AI生产力整合：TRAE、扣子并入豆包》2026-08-24
  - id: sohu-account
    resource: https://www.sohu.com/a/1098229335_122066678
    title: 搜狐《字节TRAE账号将于11月18日升级为豆包飞书账号》2026-11-06
---

# 字节 AI 大洗牌：扣子与 TRAE 收口，豆包成为超级入口

> **性质声明**：本知识包基于微信公众号「运营派 AI Lab」2026 年 11 月发布的行业评论转化，**非官方文档、非产品实测、非操作教程**。原文标题使用"陨落"，属媒体修辞；本包按可核事实改写为"收口"，差异见 [references/verification.md](references/verification.md) 勘误 E-1。
> **信源边界**：原文无任何量化数据、无公告链接（F-038、F-039）；本包不以估算补位，凡规模判断均标"定性"。产品仍处变动期，`stale_after: 2027-01-31`。

## 一句话结论

一个月内三件事——扣子企业版退场、TraeWork 与 TraeCode 合并、TRAE 个人账号并入豆包飞书——共同指向同一个动作：**能力向豆包上收，对外入口减少，用统一账号把工作上下文与结果交付串起来**（F-021~F-028）。

## 三件事速览

| 事件 | 关键日期 | 实际动作 | 常被误读为 |
|---|---|---|---|
| 扣子企业版下线 | 2026-10-29 公告；11-30 停新售；2026-12-31 / 2027-12-31 分批下线 | 企业套餐两阶段退场，个人版继续运营并调价 | "扣子停了" |
| TraeWork + TraeCode 合并 | 2026-10-09 发布 | 一个客户端，Agent + IDE 双模式 | "TRAE 没了" |
| TRAE 账号升级 | 2026-11-06 公告；11-18 生效 | 个人账号并入豆包飞书，企业客户除外 | "只是换个登录方式" |

## 主题关联（豆包工作主题簇）

本包与同组四束构成主题簇。建议顺序：产品实测 → 战略分析 → 组织生产力 → 事件整合（本包）：

| 知识包 | 视角与分工 |
|---|---|
| [doubao-work](../doubao-work/index.md) | APPSO 媒体一手实测：产品功能、多模态、额度模型、飞书集成 |
| [doubao-work-context-layer](../doubao-work-context-layer/index.md) | Context Layer 战略分析：飞书作为组织上下文层、Context 竞争论 |
| [doubao-work-org-productivity](../doubao-work-org-productivity/index.md) | 行业分析：组织 ROI、权限治理、落地落差数据 |
| [doubao-work-remotion-photo-video](../doubao-work-remotion-photo-video/index.md) | 工作流教程：素材、分镜、静帧、声音与项目交付 |
| **bytedance-ai-consolidation（本包）** | 事件整合：三条产品线的日期、范围、账号与组织归属，附判读工具 |

## 产品生态关联

- [扣子 Coze 生态](../../../ecosystems/coze/index.md)：Coze 平台、SDK 与可观测性；本包只覆盖其企业版退场，不重复平台用法。
- [TRAE 社区生态](../../../ecosystems/trae/index.md)：TRAE 平台、技能、模板与社区资源；本包只覆盖合并与账号，不重复 IDE 用法。
- [火山引擎 Agent](../../../ecosystems/volcengine-agent/index.md)：企业侧 Agent 能力与计费主体，与扣子旧版套餐退款路径相关。

## 知识结构

本知识包含 **5 篇概念文档**、**2 篇信源参考**与 1 篇日志，无 `examples/`（操作可复现性两问均为"否"）：

```
bytedance-ai-consolidation/
├── index.md
├── concepts/
│   ├── index.md
│   ├── 00-three-moves.md              三件事的时间线与官方口径
│   ├── 01-why-consolidate.md          五条洞察（含四元组）
│   ├── 02-doubao-work-hub.md          豆包工作作为整合汇点
│   ├── 03-super-entry.md              三层价值与入口竞争边界
│   └── 04-independent-playbook.md     三个可迁移判读模式
├── references/
│   ├── index.md
│   ├── article-source.md              F-001~F-049 事实登记
│   └── verification.md                13 项 P0 核验 + 5 项勘误
└── log.md
```

## 分层导航

### 概念文档

| 文档 | 核心内容 |
|---|---|
| [00-three-moves](concepts/00-three-moves.md) | 扣子两阶段下线、TRAE 双模式、账号升级、8 月组织整合；三件事件性质不同 |
| [01-why-consolidate](concepts/01-why-consolidate.md) | 能力上收/入口下减、账号不可逆、上下文护城河、薄壳危险区、三仪表 |
| [02-doubao-work-hub](concepts/02-doubao-work-hub.md) | 豆包工作承接工作场景；能力归属图；交付物 vs 回答；三个未答问题 |
| [03-super-entry](concepts/03-super-entry.md) | 入口/上下文/交付三层；首启率与停留链；框架的三个失效条件 |
| [04-independent-playbook](concepts/04-independent-playbook.md) | 三仪表、替换测试、定位表；各含反模式、检验与跨域迁移 |

### 信源参考

| 文档 | 内容 |
|---|---|
| [article-source](references/article-source.md) | F-001~F-049 完整登记（页面事实 31 / 作者判断 10 / 口径缺口 8） |
| [verification](references/verification.md) | 13 项 P0 核验（8✅/4⚠️/1❌）+ E-1~E-5 勘误 + 口径对照 |

## 信任与生命周期

- **P0 核验**：8 项通过、4 项存疑（媒体一致但官方原文未定位）、1 项证伪（标题"陨落"）。
- **事实总数**：49 条（F-001~F-049）。
- **勘误**：5 项，正文均已按正确口径表述。
- **内容敏感度**：公开（微信公众号公开文章）。
- **失效日期**：2027-01-31，覆盖 2026-12-31 与 2027-12-31 两个官方下线节点。

## 已知边界

1. **无量化数据**：原文没有份额、时长、收入、用户数；本包不补造，规模判断一律定性。
2. **官方原文缺口**：10-23 停服、11-06 公告、权益保留三项依赖媒体转述（V-08~V-10）。
3. **未实测**：本包不为豆包工作、TRAE 的功能做体验背书；实测见主题簇其他束。
4. **作者判断占比高**：F-027~F-036 共 10 条为观点，正文已逐条标注，不与事实混排。
5. **单案例萃取**：三个模式为 L1 成熟度，需第二个独立案例复验。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
