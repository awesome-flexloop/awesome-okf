---
okf_version: "0.2"
type: bundle
title: 秒悟 Meoo 产品功能全景指南
description: 秒悟（Meoo）官方产品功能的中文教程束——平台总览与四类人群、Agent/Swarms/Plan/Design 四模式、构建器 13 模型、网页应用四阶段主线、微信小程序七步与三方权责、可视化修改、云服务与 AI 服务（9 传参值/两端点）、素材中心、文件存储、根目录 SEO/GEO、技能与技能市场、连接器；14 篇概念页，全部事实回溯 docs.meoo.com 十四源 150 条编号事实
tags: [meoo, miaowu, product-guide, no-code, web-apps, wechat-miniprogram, cloud-services, ai-service, asset-center, skills, connectors]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: home
    resource: https://docs.meoo.com/
    title: 欢迎来到秒悟Meoo！
  - id: agent-modes
    resource: https://docs.meoo.com/features/agent-modes
    title: 不同Agent模式差异
  - id: models
    resource: https://docs.meoo.com/features/models
    title: 支持模型介绍
  - id: web-apps
    resource: https://docs.meoo.com/features/web-apps
    title: 功能介绍-网页应用搭建
  - id: wechat-miniprogram
    resource: https://docs.meoo.com/features/wechat-miniprogram
    title: 【New】小程序搭建&部署
  - id: visual-editing
    resource: https://docs.meoo.com/features/visual-editing
    title: 可视化修改
  - id: cloud-services
    resource: https://docs.meoo.com/features/cloud-services
    title: 云服务介绍
  - id: ai
    resource: https://docs.meoo.com/features/ai
    title: AI 服务
  - id: asset-center
    resource: https://docs.meoo.com/features/asset-center
    title: 秒悟素材中心
  - id: file-storage
    resource: https://docs.meoo.com/features/file-storage
    title: 文件上传/下载/存储
  - id: project-config
    resource: https://docs.meoo.com/features/project-config
    title: 根目录文件配置
  - id: skills
    resource: https://docs.meoo.com/features/skills
    title: 技能创建和使用
  - id: skill-marketplace
    resource: https://docs.meoo.com/features/skill-marketplace
    title: 技能市场
  - id: connectors
    resource: https://docs.meoo.com/features/connectors
    title: 连接器
---

# 秒悟 Meoo 产品功能全景指南

> **类型**：产品功能教程（仅 `concepts/` 与 `references/`，无 `examples/`——产品操作为对话/界面驱动，无可复现命令流）
> **源站分区**：首页营销页 ＋ 功能特性（应用构建能力 / 高级功能 / 扩展能力）共 14 个官方页面
> **数据时点**：2026-10-18；模型代次、套餐权益、MCP 支持等时效项以 `docs.meoo.com` 最新页面为准（`stale_after` 2027-01-18）

## 本文概要

本束回答一个问题：**不会写代码的人，用秒悟到底能做出什么、每一步的规则和边界在哪里。** 官方把答案分散在 14 个页面里，本束按使用旅程重组为三条线：

1. **怎么构建**（01–05）——四种 Agent 模式怎么选、13 个构建器模型什么区别、网页应用从一句话到发布的完整主线、微信小程序的七步与三方权责、生成后怎么可视化精修；
2. **平台服务**（06–10）——云服务（不开就是展示页）、运行时 AI 服务（9 个 API 传参值）、素材中心、文件三条通道与 CDN、根目录验证文件与 SEO/GEO 规则；
3. **扩展生态**（11–13）——把提示词沉淀为 Skill、在技能市场分发、用连接器接入外部 API。

贯穿全束的主线是**「对话即控制台」**：建库、加 AI、配登录、放根目录文件、创建存储桶——这些传统控制台动作在秒悟都收敛为一句对话指令，平台在背后完成资源申请、密钥注入与代码生成。

## 读者地图：按身份选路径

| 你是谁 | 阅读顺序 | 关键产物 |
|---|---|---|
| 第一次接触秒悟，想建立全貌 | [00](concepts/00-platform-overview.md) → [03](concepts/03-web-app-build.md) | 产品心智 + 四阶段主线 |
| 业务人员/创业者，要快速做网页/H5 | 00 → [01](concepts/01-agent-modes.md) → 03 → [05](concepts/05-visual-editing.md) | 可发布的网址链接 |
| 商家/运营，要发微信小程序 | 03 → [04](concepts/04-wechat-miniprogram.md)，配读 [06](concepts/06-cloud-services.md) §4.3 | 微信内可搜索的小程序 |
| 要给应用加 AI 对话/识图/生图 | [07](concepts/07-ai-service.md) → [09](concepts/09-file-storage.md)，选模型前读 [02](concepts/02-model-selection.md) | 带运行时 AI 能力的应用 |
| 内容/营销，要批量产素材 | [08](concepts/08-asset-center.md) | 图/视频/音频素材资产库 |
| 团队要沉淀规范与扩展能力 | [11](concepts/11-skills-authoring.md) → [12](concepts/12-skill-marketplace.md) → [13](concepts/13-connectors.md) | 私有 Skill + 外部 API 连接 |
| 运维/部署要用命令行与自有云 | 转姊妹束 [miaowu-cli-open-guide](../miaowu-cli-open-guide/index.md) | CLI/BYOC/团队 token 集成 |

## 三个必须先知道的口径

1. **模型有两张清单，不能混用**：构建器选「谁来写代码」有 13 个型号（[02](concepts/02-model-selection.md)，Qwen3.8/V4/GLM-5.3 代次）；运行时 API 的 `model` 字段只有 9 个传参值（[07](concepts/07-ai-service.md)，`qwen3.6-plus`/`deepseek-v3.2` 等）。唯一直接同名的是 `kimi-k2.5`。核验结论为 conflicting 双源并存，见 [verification.md](references/verification.md) 核验项四。
2. **5MB 与 50MB 各属一条通道**：对话框附件单文件 5MB/最多 10 个（[09](concepts/09-file-storage.md) F-108）；云服务文件管理单文件 50MB（[06](concepts/06-cloud-services.md) F-070）；>5MB 文件只在沙箱临时存储、实例销毁即清除，持久化进应用走存储桶 + CDN 四步法。
3. **平台主权边界要认清**：营销语（「分钟级」「全球可访问」）是厂商自述不是承诺；微信小程序的账号/备案/审核主权在微信（[04](concepts/04-wechat-miniprogram.md)）；SEO/GEO 文件在平台默认域名上不开放、必须独立自定义域名（[10](concepts/10-root-file-seo-geo.md)）；连接器 MCP 支持是后续规划、当前仅外部 API（[13](concepts/13-connectors.md) F-143）。

## 文档结构

### concepts/ — 概念教程（14 篇）

| 文档 | 主题 |
|------|------|
| [00-platform-overview.md](concepts/00-platform-overview.md) | 平台定位、四项自动交付、五亮点（营销/事实分层）、四人群、六类应用 |
| [01-agent-modes.md](concepts/01-agent-modes.md) | Agent/Swarms/Plan/Design 四模式选型表与组合用法 |
| [02-model-selection.md](concepts/02-model-selection.md) | 构建器 13 模型图谱（参数均标厂商自述）与双清单辨析 |
| [03-web-app-build.md](concepts/03-web-app-build.md) | 网页应用四阶段：五要素提示词、三组正反例、建库话术、自动单测、回滚发布 |
| [04-wechat-miniprogram.md](concepts/04-wechat-miniprogram.md) | 小程序七步、双预览、备案审核、权责 10 行表、五配置、7 项清单、6 FAQ |
| [05-visual-editing.md](concepts/05-visual-editing.md) | 「可视化+代码」双模、圈选标注、圈选对话改码 |
| [06-cloud-services.md](concepts/06-cloud-services.md) | 不开云服务=展示页、四特性、CSV、50MB、GoTrue、Secrets |
| [07-ai-service.md](concepts/07-ai-service.md) | 9 传参值、两端点、两档计费、自动四步、三段 fetch 参考代码 |
| [08-asset-center.md](concepts/08-asset-center.md) | 素材制作 Tab、Agent/直连双模、积分预估、图视音频、资产闭环管理 |
| [09-file-storage.md](concepts/09-file-storage.md) | 10 格式、5MB/10 个、沙箱易失、下载规则、CDN 四步法 |
| [10-root-file-seo-geo.md](concepts/10-root-file-seo-geo.md) | 验证文件 vs SEO/GEO 双轨规则、独立域名判定、4 FAQ |
| [11-skills-authoring.md](concepts/11-skills-authoring.md) | Skill vs Prompt、四原则、天气示例、模型推荐、五步迭代法 |
| [12-skill-marketplace.md](concepts/12-skill-marketplace.md) | 语义搜索、8 类型 vs 7 标签、权限矩阵、zip 上传 |
| [13-connectors.md](concepts/13-connectors.md) | 外部 API、积分计费、连接两层模型、两场景、监控解绑、注册自有连接器 |

### references/ — 信源登记与核验

| 文档 | 说明 |
|------|------|
| [source-ledger.md](references/source-ledger.md) | F-001–F-150 编号事实（150 条十四源分段）+ S1–S14 信源台账 + 放弃核验清单（14 项缺口）+ 转写噪声登记（9 类）+ 单源/跨源交叉声明 |
| [verification.md](references/verification.md) | 13 项 P0 核验：两端点/环境变量、9 传参值、13 模型参数、模型双源冲突、5MB/50MB 语境、计数枚举、微信权责、截图边界、代码还原、逐字引用、微信外链、噪声隔离、dated 时效组 |

## 与姊妹束的分工

- [miaowu-cli-open-guide](../miaowu-cli-open-guide/index.md)：秒悟**命令行与开放平台**面——CLI 安装登录、静态/全栈部署、自有阿里云 BYOC、团队 AK/SK 签 token 接入 Agent/CI。本束讲「在产品里能做什么、规则是什么」，姊妹束讲「不靠控制台怎么部署集成」，两束互补，事实编号体系独立（本束 F-001–F-150，姊妹束 F-001–F-074）。
- [miaowu-meoo-practice-cases](../miaowu-meoo-practice-cases/index.md)：同分组既有束——秒悟实训案例（网页侧 5 步搭建法与 7 个实操场景），适合读本束后做跟练。
- [miaowu-bounty-plaza](../miaowu-bounty-plaza/index.md)：同分组既有束——AI Builder 共创计划技能索引。

## 已知边界

- **厂商单源、文档级核验**：150 条事实均来自 `docs.meoo.com` 自身文字层，无运行验证、无第三方交叉；模型参数与基准排名全部为厂商自述。
- **营销页未量化**：主页「分钟级」「成本趋近于零」「全球可访问」等无价格页/SLA 背书；pricing 页在抓取清单外，套餐名称与权益（LITE/PRO/MAX、代码下载、自定义域名付费）均标时效风险。
- **截图与视频信息缺失**：14 源中大量入口位置、面板布局、手势由截图/GIF 承载，另有源页内嵌演示视频不可转写；本束只转写文字层明确路径，不脑补按钮外观。
- **深页未覆盖**：微信备案材料明细、审核时限与类目全表、隐私协议模板、各模型价格倍率、连接器凭证存储机制、技能包 zip 结构、素材生成参数全表等均在源页之外，登记于 [source-ledger.md](references/source-ledger.md)「放弃核验清单」，未做推断补全。
- **源页原文缺陷不校改**：「餐普规划」、「界面风格应简洁现代）」多余右括号、技能市场页句末漏字等原文问题保留并加注，不代为修正（逐项留痕于 [source-ledger.md](references/source-ledger.md) 转写噪声登记）。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
