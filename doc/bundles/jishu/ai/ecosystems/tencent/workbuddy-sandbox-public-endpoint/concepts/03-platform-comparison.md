---
okf_version: "0.2"
type: Concept
title: "横向对标：WorkBuddy、TraeCode、TraeWork 与豆包工作"
description: "从执行环境、发布动作、托管底座、域名稳定性和适用负载比较四类 AI 工作/编程产品的公网化路径。"
tags: [workbuddy, traecode, traework, doubao-work, public-endpoint, deployment, benchmark]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki:E", at: "2026-09-16T23:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T23:30:00+08:00" }
status: stable
stale_after: 2026-11-30
sources:
  - id: facts
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: traecode-solo
    url: https://docs.trae.ai/ide/solo-mode?_lang=en
  - id: traecode-deployment
    url: https://docs.trae.ai/ide/vercel-deployment
  - id: traework
    url: https://docs.trae.ai/solo/what-is-trae-solo?_lang=en
  - id: byteplus-pages-traework
    url: https://docs.byteplus.com/th/docs/byteplus-cdn/pages-trae_zh-cn
  - id: trae-cn-iga-pages
    url: https://www.volcengine.com/docs/6559/2387290?lang=zh
  - id: doubao-work-notice
    url: https://www.doubao.com/legal/DoubaoAgentModeNotice
---

# 横向对标：WorkBuddy、TraeCode、TraeWork 与豆包工作

## 1. 先厘清四个产品角色

这四个名称都与 AI Agent、网页生成或云端执行有关，但它们承担的职责不同：

| 产品 | 主要角色 | 与公网化的关系 |
|------|----------|----------------|
| WorkBuddy / CloudStudio | AI 办公/开发环境与云端沙箱 | 已有公开页面经 CloudStudio Gateway 暴露；更接近沙箱端口或已部署环境的即时 HTTPS 入口（F-031、F-034、F-035） |
| TraeCode（国际版 SOLO） | AI 原生 IDE / Coding Agent | 内置部署服务经第三方 Vercel 发布 Web 应用，部署后可分享链接（F-040~F-042） |
| TRAE CN / TraeCode 中国版 | AI IDE 中国版 | 火山引擎文档明确“当前未提供一键部署能力”，推荐通过 IGA Pages Skill/CLI 部署（F-043~F-045） |
| TraeWork | AI-native workspace，Work/Code/Design 三模式、三端协同 | Cloud agent 负责云端执行；网页发布由 BytePlus Pages Skill 承担，临时预览约 3 小时重置（F-046~F-050） |
| 豆包工作 | 通用工作任务 Agent，含本地电脑/云电脑、技能、连接器、工作伙伴 | 官方确认云电脑可隔离后台执行；公网 IP/EdgeOne 部署目前主要来自第三方实测，不能直接等同官方通用公网托管承诺（F-051、F-052） |

> 结论：**“能在云端运行”和“自动获得稳定公网 HTTPS 地址”是两件事。**前者是执行环境能力，后者还需要端口、网关、托管、域名、证书和生命周期策略共同成立。

## 2. 公网化路径矩阵

| 维度 | WorkBuddy / CloudStudio | TraeCode 国际版 | TRAE CN + IGA Pages | TraeWork + BytePlus Pages | 豆包工作 |
|------|--------------------------|-----------------|---------------------|---------------------------|----------|
| 执行环境 | 云端沙箱 / Runtime；WMA 另有企业托管 Runtime（F-029~F-031） | SOLO Agent 在项目内生成、测试、预览和部署（F-040） | TRAE IDE 负责创意生成与代码迭代，IGA Pages 负责部署（F-043、F-044） | 桌面/Web/移动 + Cloud agent（F-046、F-047） | 本地电脑或云端独立隔离环境（F-051） |
| 发布动作 | 在沙箱/任务/部署环境中获得平台域名；具体 UI 路径需现场确认（F-007、F-011） | 点击聊天面板或 Browser 工具的 Deploy，或自然语言触发（F-042） | 安装 IGA Pages Skill 或使用 CLI，也可接 GitHub 自动部署（F-045） | 安装/调用 `byted-bp-cdn-pagesdeploy` Skill，并说“部署该页面并获取分享链接”（F-048） | 官方须知未给通用公网发布按钮；第三方实测提及云电脑公网 IP 和 EdgeOne（F-052） |
| 托管底座 | 可观测边缘网关为 CloudStudio Gateway；CLB/sandbox-proxy 未证实（F-035、F-037、F-038） | Vercel（F-041） | 火山引擎 IGA Pages，含全球边缘网络与 Serverless 函数（F-044） | BytePlus Pages，全球边缘节点分发静态站点/SPA/文档站等（F-049） | 云电脑是执行环境；若部署网页需另接 EdgeOne/其他托管平台（F-051、F-052） |
| 默认链接稳定性 | 域名后缀已观察到漂移；临时环境生命周期需以面板为准（F-007、F-036） | Vercel 部署链接与项目部署关联，具体保留策略受 Vercel 项目/账号约束 | 预览链接可全球访问；长期分享可绑定自定义域名（F-045） | 临时预览地址约 3 小时重置；长期分享需自定义域名（F-050） | 公网 IP/网站保留策略未获官方文档核验（F-052） |
| 自定义域名 | 博文称不支持，未获官方复核（F-022） | 编者推断：通常通过 Vercel 项目能力管理，具体以 Vercel 计划为准（非本文官方核验） | IGA Pages 控制台支持自定义域名与 SSL 配置（F-045） | Pages 控制台支持稳定自定义域名、部署记录和回滚（F-050） | 第三方路径取决于所用 EdgeOne/云资源配置（F-052） |
| 最适合 | 即时 Demo、公开静态页、短时联调（F-012、F-034） | 前端/全栈 Web 应用快速分享与版本再部署（F-041） | 原型、活动页、对话式应用、边缘函数，需要 GitOps 时更合适（F-044、F-045） | 非工程用户生成报告、小游戏、原型、手册等网页后快速分享（F-048~F-050） | 办公任务、云端长任务、浏览器/本地/云电脑操作；公网部署需按具体 Skill/云资源确认（F-051、F-052） |
| 不适合直接承担 | 生产 Webhook、长期 API、敏感数据、7×24 SLA（F-018~F-021） | 编者推断：超出 Vercel Serverless/Web 托管模型或受平台/账号限制的服务 | 常驻后台服务、定时任务、数据库常连接、深度定制 Nginx/容器镜像（F-045） | 约 3 小时预览链接不适合长期入口或生产回调（F-050） | 在官方未确认公网 SLA/域名前，不应默认其为公网应用托管平台（F-051、F-052） |

> 命名说明：官方英文文档使用 **TraeWork**，BytePlus 中文指南中写作 **Trae Work**；本文除引用中文指南的 Skill/口令语境保留“Trae Work”外，统一写作 TraeWork。

## 3. 三条选择规则

### 规则 1：只想几分钟内“给别人看页面”

- **WorkBuddy/CloudStudio**：适合即时展示，但必须使用面板实际域名，不硬编码 `sh1.agentos-app.net`（F-007、F-036）。
- **TraeWork + BytePlus Pages**：面向不会写代码的用户，生成网页后用 Skill 发布最顺；但默认预览地址约 3 小时重置（F-048、F-050）。
- **TraeCode 国际版**：适合已经在 SOLO 中开发的 Web 应用，通过 Vercel Deploy 发布（F-041、F-042）。
- **TRAE CN**：需要显式接入 IGA Pages，不能误以为中国版 IDE 已内置同样的一键部署（F-043）。

### 规则 2：需要稳定链接、回滚和团队协作

优先选择正式 Pages/托管项目，而不是临时沙箱地址：

- TRAE CN + IGA Pages：适合需要 GitHub 自动部署、自定义域名、SSL 和边缘函数的团队（F-045）。
- TraeWork + BytePlus Pages：适合需要部署记录、回滚和稳定自定义域名的网页型成果（F-050）。
- TraeCode 国际版：稳定性、域名和函数能力应按 Vercel 项目计划确认。
- WorkBuddy：如要生产级运行，应转向 WMA、云服务器、容器或正式应用托管平台（F-018、F-030、F-031）。

### 规则 3：需要 Webhook、后端常驻或敏感数据

不要把“临时预览 HTTPS”当成完整后端平台：

1. Webhook 需要稳定 URL、重试策略、验签、日志和限流；WorkBuddy 临时端点与 TraeWork 3 小时预览地址都不满足默认要求（F-021、F-050）。
2. 常驻后台服务、定时任务、数据库常连接已被 IGA Pages 文档明确排除在推荐范围外（F-045）。
3. 豆包工作云电脑可以在本地关机后继续运行任务（F-051），但这只证明任务执行环境可持续，不证明其上服务天然具备公网负载均衡、证书和 SLA；第三方公网 IP/EdgeOne 实测需单独复核（F-052）。

## 4. 一句话选型

| 目标 | 首选路径 |
|------|----------|
| 临时打开一个沙箱页面给客户看 | WorkBuddy/CloudStudio 实际分配域名，或 TraeWork Pages 临时预览 |
| 非技术用户把报告/小游戏发成网页 | TraeWork + BytePlus Pages Skill |
| 开发者在 TraeCode 国际版发布 Web App | TraeCode SOLO Deploy → Vercel |
| 中国版 TRAE 需要自定义域名、GitOps、全球加速 | TRAE CN + IGA Pages |
| 办公任务在云端持续执行 | 豆包工作云电脑模式 |
| 生产 API、支付/GitHub Webhook、长期数据库 | WMA/云服务器/容器/正式 Pages 函数平台，按安全与 SLA 要求设计 |

## 5. 与本束前文的关系

- [公网端点机制](00-public-endpoint-mechanism.md)回答 WorkBuddy 自身的“可验证链路是什么”。
- [临时服务的适用场景与边界](01-temporary-service-use-cases.md)回答 WorkBuddy 能做什么、不能做什么。
- 本文回答“同样是 AI 工作/编程产品，TraeCode、TraeWork、豆包工作分别走哪条公网化路径”。
- [会话保活、生产边界与提示词改写](02-lifecycle-and-operations.md)给出临时服务上线前后的操作护栏。
