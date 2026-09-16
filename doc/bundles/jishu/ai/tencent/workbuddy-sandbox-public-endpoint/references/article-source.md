---
okf_version: "0.2"
type: Reference
title: "WorkBuddy 沙箱公网端点博文事实登记"
description: "微信公众号文章 F-001~F-052 双份事实登记，区分博文口径、官方核验、实时响应头与横向对标证据。"
tags: [workbuddy, cloudstudio, sandbox, public-endpoint, fact-registry, 博文转化]
generated: { by: "blog-article-to-okf-wiki:R/E", at: "2026-09-16T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T22:40:00+08:00" }
status: stable
stale_after: 2026-11-30
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/bMRwxrGDltjsoo-HneHi2Q
  - id: tencent-product-overview
    url: https://cloud.tencent.com/document/product/1831/134329
  - id: wma-product-intro
    url: https://cloud.tencent.com/document/product/1831/134407
  - id: codebuddy-remote-control
    url: https://cloud.tencent.com/document/product/1831/137049
  - id: codebuddy-ide-release
    url: https://cloud.tencent.com/document/product/1831/134323
  - id: live-agentos-bj10
    url: https://8bd2366a16a4492ba26179a292680f40.bj10.agentos-app.net
  - id: live-agentos-sh7
    url: https://adef3be1fd79db112.sh7.agentos-app.net
  - id: live-agentos-bj3
    url: https://37ee2229152f4698848762ad5528a193.bj3.agentos-app.net
  - id: netease-repost
    url: https://m.163.com/dy/article/L6S4D18R05314EKW.html
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
  - id: doubao-work-third-party-test
    url: https://ai.lzw.me/best-blogs/article/5c76486940
---

# WorkBuddy 沙箱公网端点博文事实登记

> 主信源：微信公众号「AI工具实测派」《你敢相信吗？WorkBuddy 白送你一台「免费服务器」，90%的人却只会拿来写代码》，作者 wrokbuddy，2026-08-28 19:53。
> F-001~F-027 为博文事实；F-028~F-039 为 2026-09-16 官方资料、公开案例与实时请求补充事实；F-040~F-052 为 TraeCode、TraeWork 与豆包工作横向对标补充事实。

## A. 元信息

| F编号 | 类型 | 事实 | 核验状态 |
|------|------|------|----------|
| F-001 | O | 博文标题为《你敢相信吗？WorkBuddy 白送你一台「免费服务器」，90%的人却只会拿来写代码》 | ➖ |
| F-002 | O | 公众号为「AI工具实测派」，作者署名为「wrokbuddy」，发布时间为 2026-08-28 19:53，标记原创，发布地四川 | ➖ |
| F-003 | O | URL 为 https://mp.weixin.qq.com/s/bMRwxrGDltjsoo-HneHi2Q，浏览器访问无验证码、登录或付费墙 | ✅ |

## B. 博文所述机制

| F编号 | 类型 | 事实 | 核验状态 |
|------|------|------|----------|
| F-004 | V | 博文称多数人使用 WorkBuddy 主要是写代码、跑脚本、出报告，完成后关闭 | ➖ |
| F-005 | O | 博文称 WorkBuddy 沙箱是带公网出口的小服务器，本地服务启动后自动获得 HTTPS 公网域名，无需自行处理 nginx 和证书 | ✅/⚠️ |
| F-006 | O | 博文以沙箱内监听 `:3000` 作为示例端口 | ➖ |
| F-007 | O | 博文称平台分配 `<沙箱ID>.sh1.agentos-app.net` 形式的 HTTPS 子域名 | ⚠️ |
| F-008 | O | 博文称腾讯云 CLB 在负载均衡层执行 TLS 终止，证书由平台管理 | ⚠️ |
| F-009 | O | 博文称沙箱内 `sandbox-proxy` 将公网流量反向代理到本地端口 | ⚠️ |
| F-010 | O | 博文称本地服务可通过 `https://<沙箱ID>.sh1.agentos-app.net` 直接访问，反向代理、证书和 nginx 由平台处理 | ✅/⚠️ |
| F-011 | O | 博文给出 4 步：启动本地服务、在沙箱信息或任务面板找到公网域名、浏览器打开 HTTPS 域名、替换为真实后端 | ⚠️ |

## C. 场景与生命周期

| F编号 | 类型 | 事实 | 核验状态 |
|------|------|------|----------|
| F-012 | O | 博文列出临时演示、Webhook 接收端、小程序/公众号后端联调、frp/ngrok 替代、静态页托管、Agent 接口六类场景 | ⚠️ |
| F-013 | V | 博文将传统路径概括为购买轻量云、配置 nginx、申请证书，并称沙箱路径几分钟可完成 | ➖ |
| F-014 | V | 博文认为“会话在、服务在”适合阅后即焚演示，沙箱回收后链接失效可视为安全特性 | ⚠️ |
| F-015 | O | 博文建议用 `while sleep 60; do date; done` 周期性心跳避免会话空转 | ➖ |
| F-016 | O | 博文建议用 `nohup node server.js > app.log 2>&1 &` 后接 `disown` 让服务脱离终端后台运行 | ➖ |
| F-017 | O | 博文建议让 WorkBuddy 自行挂心跳并检查域名连通性 | ➖ |
| F-018 | O | 博文提示需要 7×24 时应使用正经云服务器或容器，保活只是拖时间，不是保险 | ✅ |
| F-019 | O | 博文提示沙箱活着服务才活着，不应把该能力当生产环境 | ✅ |
| F-020 | O | 博文提示不要在沙箱中放置机密和长期数据 | ✅ |
| F-021 | O | 博文提示端口与限流以平台实际规则为准 | ✅ |
| F-022 | O | 博文称平台只分配域名，不能自定义品牌域名 | ⚠️ |

## D. 提示词与素材

| F编号 | 类型 | 事实 | 核验状态 |
|------|------|------|----------|
| F-023 | O | 博文给出的提示词要求在沙箱 `:3000` 启动服务，并写入 `sh1.agentos-app.net`、腾讯云 CLB TLS 终止、sandbox-proxy 反代、无需 nginx/证书等表述，最后要求返回域名并验证 | ⚠️ |
| F-024 | O | 博文结尾引导后台回复「AI工具」获取网盘指令卡，并邀请评论分享服务 | ➖ |
| F-025 | O | 全文有架构示意、场景对比、指令卡 3 张 PNG 配图，正文无 HTML 超链接 | ➖ |
| F-026 | V | “90%的人”和“白送免费服务器”为标题修辞，不作为统计事实 | ➖ |
| F-027 | O | 博文表格将传统方案分别写为云服务器/Vercel、公网固定服务器、HTTPS 域名、frp/ngrok、对象存储+CDN、额外基础设施 | ➖ |

## E. 官方与实时核验补充

| F编号 | 类型 | 事实 | 核验状态 |
|------|------|------|----------|
| F-028 | O | 腾讯云官方将 CodeBuddy、WorkBuddy、WorkBuddy Managed Agents 定义为 WorkBuddy Enterprise 的三款产品，分别面向智能编码、AI 办公协同和智能体托管/规模化运行 | ✅ |
| F-029 | O | WMA Runtime 是 Session 背后的云端沙箱，包含完整 Linux 文件系统和终端、Agent Manifest 以及一个或多个 Session | ✅ |
| F-030 | O | WMA Agent 在云端沙箱运行，可 7×24 小时不间断服务和运行，并支持自动休眠与毫秒级恢复 | ✅ |
| F-031 | O | WMA Agent Runtime 将端口转发与数据持久化、跨节点恢复、秒级 CoW Fork、预热池并列为一体化能力 | ✅ |
| F-032 | O | CodeBuddy Code Remote Control 的公网模式使用 Cloudflare Tunnel，临时域名为 `*.trycloudflare.com`，需安装 cloudflared，功能处于 Beta；这不是本文的 `agentos-app.net` 链路 | ✅ |
| F-033 | O | CodeBuddy IDE 4.12.0 新增 CloudStudio 已部署环境查看与删除，部署记录可自助清理 | ✅ |
| F-034 | E | 2026-09-16 三个公开第三方案例域名 `bj10`、`sh7`、`bj3.agentos-app.net` 经 HTTPS 请求均返回 HTTP 200，页面分别为个人技术站、学习闯关台、保质期计算器 | ✅ |
| F-035 | E | 上述三个响应头均含 `Server: CloudStudio Gateway` 与 `X-Trace-Id` | ✅ |
| F-036 | O | 2026-09-15 网易号转载稿使用 `<沙箱ID>.app.workbuddy.host`；示例域名 HEAD 返回 501，但响应头同样含 CloudStudio Gateway、X-Request-Id、X-Trace-Id | ⚠️ |
| F-037 | O | 截至 2026-09-16，公开检索未找到腾讯官方文档直接说明 `sh1.agentos-app.net`、`sandbox-proxy` 或“CLB→sandbox-proxy”这条具体内部链路 | ⚠️ |
| F-038 | E | 实时响应头可观测边缘网关为 CloudStudio Gateway，未观察到可直接证明 CLB 或 sandbox-proxy 的字段 | ⚠️ |
| F-039 | O | 临时预览沙箱、CloudStudio 已部署环境、CodeBuddy Remote Control、WMA 托管 Runtime 是不同产品形态，生命周期和适用场景不能互相套用 | ✅ |

## F. TraeCode / TraeWork / 豆包工作对标补充

| F编号 | 类型 | 事实 | 核验状态 |
|------|------|------|----------|
| F-040 | O | TraeCode 官方 SOLO 模式文档称，SOLO 让 AI 自主完成需求理解、代码生成、测试、结果预览和部署的完整开发过程 | ✅ |
| F-041 | O | TraeCode 国际版通过第三方服务 Vercel 在线部署 Web 应用；部署后可通过链接分享，更新后可部署新版本 | ✅ |
| F-042 | O | TraeCode 部署入口包括 AI 聊天面板的 Deploy 按钮、Browser 工具右上角 Deploy 按钮，或自然语言触发部署任务 | ✅ |
| F-043 | O | 火山引擎 IGA Pages 文档明确“TRAE 中国版当前未提供一键部署能力”，组合方案为 TRAE CN 负责生成迭代、IGA Pages 负责部署分发与运行时 | ✅ |
| F-044 | O | IGA Pages 是火山引擎一站式 AI 应用部署与全球加速平台，提供零配置部署、全球边缘网络和 Serverless 函数能力，接管节点、证书、缓存等基础设施细节 | ✅ |
| F-045 | O | IGA Pages 支持 Skill/CLI 部署、GitHub 仓库集成自动部署、自定义域名和 SSL 证书；不适合常驻后台服务、定时任务、数据库常连接和深度定制 Nginx/容器镜像 | ✅ |
| F-046 | O | TraeWork 是 AI-native workspace，提供 Web、桌面、移动三端和 Work、Code、Design 三模式；Web 适合临时需求/快速验证，桌面支持本地与云任务，移动端可派发监控云任务 | ✅ |
| F-047 | O | TraeWork Cloud agent 在云端稳定隔离环境执行代码分析、运行和调试，提供统一运行时与依赖管理 | ✅ |
| F-048 | O | BytePlus Pages + Trae Work 指南称，Trae Work 生成网页后可通过 `byted-bp-cdn-pagesdeploy` Skill 上传 Pages 并返回分享链接 | ✅ |
| F-049 | O | BytePlus Pages 支持静态 HTML/CSS/JavaScript、SPA、文档站、博客和 Git 持续部署前端项目，通过 BytePlus 全球边缘节点分发 | ✅ |
| F-050 | O | Trae Work 经 Pages 部署后的临时预览地址约每 3 小时重置；长期对外分享应在 Pages 控制台绑定稳定自定义域名，并可查看部署记录和回滚历史版本 | ✅ |
| F-051 | O | 豆包工作任务模式官方须知确认有本地电脑和云电脑两种环境；云电脑为独立隔离环境，默认不访问本地文件，本地关机后任务仍可后台运行，产物保存在云端；技能、连接器、工作伙伴扩展能力 | ✅ |
| F-052 | O | AI Best 转载 Draco正在VibeCoding 的第三方实测文（2026-08-27）称豆包工作云电脑为 2 核 4G Debian 沙盒、提供公网 IP，并演示 EdgeOne 部署；该说法未在豆包官方任务功能须知中直接核验 | ⚠️ |

## 事实统计

| 分组 | 编号范围 | 数量 |
|------|----------|------|
| 博文元信息 | F-001~F-003 | 3 |
| 博文机制 | F-004~F-011 | 8 |
| 场景与生命周期 | F-012~F-022 | 11 |
| 提示词与素材 | F-023~F-027 | 5 |
| 官方/实时补充 | F-028~F-039 | 12 |
| 横向对标补充 | F-040~F-052 | 13 |
| **合计** | F-001~F-052 | **52** |
