---
okf_version: "0.2"
type: Reference
title: "WorkBuddy 沙箱公网端点 P0 核验报告"
description: "核验博文关于 WorkBuddy/CloudStudio 沙箱公网 HTTPS、域名后缀、网关链路和生命周期的声明：7✅/5⚠️/0❌。"
tags: [workbuddy, cloudstudio, sandbox, verification, p0-check, https, public-endpoint]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-09-16T22:05:00+08:00" }
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
---

# P0 核验报告：WorkBuddy 沙箱公网端点

> 核验时间：2026-09-16。方法：腾讯云官方文档交叉验证、公开第三方案例回溯、HTTPS 页面抓取、HTTP 响应头检查。

## 1. 总览

| 结论 | 数量 | 说明 |
|------|------|------|
| ✅ 通过 | 7 | 产品身份、Runtime、端口转发、实时 HTTPS 域名、边缘网关等核心能力可验证 |
| ⚠️ 口径差异/未完全证实 | 5 | 域名后缀、CLB、sandbox-proxy、生命周期、生产场景存在边界或漂移 |
| ❌ 硬错误 | 0 | 未发现足以否定“平台可提供公网 HTTPS 端点”的核心证据 |

**总体判定**：博文的高层结论成立——WorkBuddy/CloudStudio 相关环境确实可承载公网 HTTPS 页面（F-031、F-034、F-035）。但博文对具体域名后缀和内部网络组件的描述不能直接写成官方定论：实时观测到的边缘网关是 `CloudStudio Gateway`，`CLB → sandbox-proxy` 未见公开官方文档支持（F-037、F-038）。Bundle 因此保持 `stable`，但全文保留显著口径提示。

## 2. P0/P1 逐项核验

| # | 博文声明 | 证据 | 结论 |
|---|----------|------|------|
| 1 | WorkBuddy 是腾讯相关 AI 产品 | 腾讯云 WorkBuddy Enterprise 产品概述明确 CodeBuddy、WorkBuddy、WMA 三款产品定位（F-028） | ✅ |
| 2 | 沙箱/Runtime 是 Linux 运行环境 | WMA 产品介绍称 Runtime 含完整 Linux 文件系统和终端（F-029） | ✅ |
| 3 | 云端 Agent 可长期运行 | WMA 官方称云端沙箱支持 7×24、自动休眠与毫秒级恢复（F-030） | ✅ |
| 4 | 平台具备端口转发能力 | WMA 官方将端口转发列为 Agent Runtime 一体化能力（F-031） | ✅ |
| 5 | `*.agentos-app.net` 可承载公网页面 | 三个第三方案例域名 2026-09-16 HTTPS GET 均返回 200（F-034） | ✅ |
| 6 | HTTPS 与网关由平台侧提供 | 三个 200 响应均经 HTTPS 访问，响应头含 `Server: CloudStudio Gateway`（F-035） | ✅ |
| 7 | CloudStudio 已部署环境在产品内可管理 | CodeBuddy IDE 4.12.0 更新记录列出 CloudStudio 已部署环境查看/删除（F-033） | ✅ |
| 8 | 固定域名后缀为 `<id>.sh1.agentos-app.net` | 实时案例存在 `bj10`、`sh7`、`bj3` 等不同前缀（部分疑似地域标识）；2026-09-15 转载稿改用 `app.workbuddy.host`（F-007、F-036） | ⚠️ |
| 9 | 腾讯云 CLB 做 TLS 终止 | 公开官方文档未检索到该具体链路；响应头未显示 CLB 字段（F-008、F-037、F-038） | ⚠️ |
| 10 | 沙箱内 `sandbox-proxy` 反代本地端口 | 公开官方文档未检索到该组件说明；响应头未显示该组件（F-009、F-037、F-038） | ⚠️ |
| 11 | “会话在、服务在”可概括全部 WorkBuddy 形态 | WMA 具备 7×24、休眠恢复、持久化等企业托管能力；博文描述更像临时预览环境（F-014、F-030、F-039） | ⚠️ |
| 12 | 六类场景都可直接替代传统服务器 | 临时 Demo/静态页有实时案例；Webhook/支付回调等入站场景还受端口、限流、暴露策略和 SLA 限制（F-012、F-021） | ⚠️ |

## 3. 勘误四张清单

### 3.1 日期/版本表

| 项目 | 博文口径 | 核验结果 | 处理 |
|------|----------|----------|------|
| 发布日期 | 2026-08-28 19:53 | 浏览器页面元信息一致（F-002） | ✅ |
| 平台版本 | 未提供 | 无法将域名行为绑定到特定 WorkBuddy/CloudStudio 版本 | ⚠️ 正文标注版本缺失 |
| 官方相邻产品版本 | 未提 | CodeBuddy IDE 4.12.0 于 2026-09-08 增加 CloudStudio 部署环境管理（F-033） | 补充为生态证据 |

### 3.2 成效数字溯源表

| 博文表述 | 核验结果 | 处理 |
|----------|----------|------|
| 标题“90%的人” | 无统计样本、问卷或后台数据 | 标为作者修辞，不进入事实结论（F-026） |
| “几分钟搞定” | 无计时实验、应用复杂度与网络条件 | 标为作者场景化表述（F-013） |
| “免费服务器” | 未核验账号权益、配额、计费边界 | 正文改写为“临时公网端点能力”，不写成免费长期云服务器 |

### 3.3 口径对照表

| 口径 | 差异 | 正确呈现 |
|------|------|----------|
| `sh1.agentos-app.net` | 实测案例包括 `bj10`、`sh7`、`bj3.agentos-app.net`；转载稿出现 `app.workbuddy.host`（F-007、F-036） | 写为“历史/示例域名族包括 `<id>.<region>.agentos-app.net`，实际以面板分配为准” |
| CLB TLS 终止 | 可观测响应头是 CloudStudio Gateway，不等于 CLB 不存在，但无法公开证明（F-035、F-038） | 写为“博文称 CLB；可观测边缘网关为 CloudStudio Gateway，内部实现未证实” |
| 临时沙箱 vs WMA | WMA 官方支持 7×24、自动休眠/恢复与持久化；博文强调会话回收（F-014、F-030、F-039） | 分成临时预览环境和企业托管 Runtime，不互相套用 |
| CodeBuddy Remote Control | 官方公网链路为 Cloudflare Quick Tunnel + `*.trycloudflare.com`（F-032） | 明确它是相邻但不同的远程控制机制 |

### 3.4 引文/命令逐字核对

| 博文命令或引文 | 核验结果 | 处理 |
|----------------|----------|-------|
| `while sleep 60; do date; done` | 通用 POSIX shell 循环；未证明平台据此保活 | 保留为通用技巧，不承诺保活效果（F-015） |
| `nohup node server.js > app.log 2>&1 &` + `disown` | 通用 POSIX shell 后台化写法；未证明跨会话持久 | 标注为终端解绑，不是托管保障（F-016） |
| 提示词中的固定域名与内部组件 | 域名后缀漂移，内部组件未证实 | 改写提示词为“读取沙箱/任务面板实际域名，不要臆造 nginx/证书；若平台未自动暴露则停止并报告”（F-023） |

## 4. 实时请求证据

2026-09-16 08:02 UTC 左右执行 HTTP HEAD/GET：

| URL | 状态 | 关键响应头/内容 |
|-----|------|-----------------|
| `https://8bd2366a16a4492ba26179a292680f40.bj10.agentos-app.net` | 200 | `Server: CloudStudio Gateway`；页面为个人技术站 |
| `https://adef3be1fd79db112.sh7.agentos-app.net` | 200 | `Server: CloudStudio Gateway`；页面为学习闯关台 |
| `https://37ee2229152f4698848762ad5528a193.bj3.agentos-app.net` | 200 | `Server: CloudStudio Gateway`；页面为保质期计算器 |
| `https://demo-backend-93918.app.workbuddy.host` | 501 | `Server: CloudStudio Gateway`；根路径 HEAD 不支持，但网关可达 |

这些证据证明“公开 HTTPS 页面 + CloudStudio Gateway”事实，不证明每个沙箱本地端口都会无条件对外开放，也不证明任意 Webhook 流量都被平台允许。

> 证据快照说明：上述第三方沙箱 URL 可能在复核日前被回收；若原始页面失效，以本节留存的 2026-09-16 状态码与响应头记录作为当时证据快照，复核时应重新选取平台新分配域名验证网关。

## 5. 读者使用结论

1. **可放心采用的事实**：平台生态中存在公网 HTTPS 页面能力；历史域名族包括 `*.agentos-app.net`；边缘网关可观测标识为 CloudStudio Gateway（F-034、F-035）。
2. **必须现场确认的事实**：当前账号/环境分配的域名后缀、可暴露端口、保留时长、限流、自定义域名、入站 Webhook 支持情况（F-021、F-022、F-036）。
3. **不要照抄的内容**：硬编码 `sh1.agentos-app.net`、断言 CLB/sandbox-proxy 内部链路、把心跳/nohup 当作 7×24 SLA（F-008、F-009、F-015、F-016）。
4. **复核安排**：`stale_after=2026-11-30`，到期前重新核对官方文档、实际域名后缀、网关响应头和平台生命周期说明；如旧案例 URL 已回收，应使用新的平台分配域名重测。
