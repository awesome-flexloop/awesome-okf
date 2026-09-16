---
okf_version: "0.2"
type: bundle
title: "WorkBuddy 沙箱公网端点：临时 HTTPS 服务的能力与边界"
description: "核验 WorkBuddy/CloudStudio 沙箱公网 HTTPS 能力，并横向对比 TraeCode/Vercel、TRAE CN/IGA Pages、TraeWork/BytePlus Pages 与豆包工作云电脑。"
tags: [workbuddy, cloudstudio, traecode, traework, doubao-work, vercel, iga-pages, byteplus-pages, sandbox, https, public-endpoint, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-09-16T22:25:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T22:25:00+08:00"
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
---

# WorkBuddy 沙箱公网端点：临时 HTTPS 服务的能力与边界

> **类型**：技术综述/操作提示，非完整可复现 examples 教程。
> **核验结论**：原 WorkBuddy P0/P1 共 12 项，**7✅ / 5⚠️ / 0❌**；对标扩展新增 13 条事实（F-040~F-052），其中 TraeCode/TraeWork/Pages 路径以官方文档为准，豆包工作公网 IP 说法仍为第三方实测。
> **最重要边界**：公网 HTTPS 能力已获官方端口转发能力与实时页面证据支持；博文的固定域名后缀、CLB TLS 终止和 `sandbox-proxy` 内部链路未获官方公开文档证实。

## 本文回答什么

微信博文将 WorkBuddy 沙箱描述为一台“免费服务器”：本地启动服务后，平台自动给出公网 HTTPS 域名，nginx 与证书由平台处理（F-005~F-010）。本知识包对这一说法做三层拆分：

1. **能力是否存在**：存在。腾讯云 WMA 官方资料确认 Runtime 具备端口转发能力（F-031）；多个 `*.agentos-app.net` 历史页面在 2026-09-16 仍可经 HTTPS 访问（F-034）。
2. **网关是什么**：实时响应头显示 `Server: CloudStudio Gateway`（F-035）。
3. **博文内部链路是否完全可信**：保留边界。`sh1.agentos-app.net` 后缀、腾讯云 CLB TLS 终止和沙箱内 `sandbox-proxy` 均未找到直接官方公开文档；2026-09-15 转载稿还出现了 `app.workbuddy.host` 后缀（F-007~F-009、F-036~F-038）。

## 阅读路径

| 顺序 | 文档 | 读者收获 |
|------|------|----------|
| 1 | [公网端点机制：从沙箱端口到 HTTPS 域名](concepts/00-public-endpoint-mechanism.md) | 看懂可验证链路、CloudStudio Gateway 证据和产品形态差异 |
| 2 | [临时服务的适用场景与边界](concepts/01-temporary-service-use-cases.md) | 判断 Demo、静态页、Webhook、Agent API 等场景是否适用 |
| 3 | [会话保活、生产边界与提示词改写](concepts/02-lifecycle-and-operations.md) | 理解心跳/nohup 的局限，获得安全版 Agent 提示词 |
| 4 | [横向对标 WorkBuddy、TraeCode、TraeWork 与豆包工作](concepts/03-platform-comparison.md) | 区分沙箱端口、Vercel、IGA Pages、BytePlus Pages 与云电脑模式 |
| 参考 | [博文事实登记](references/article-source.md) | 查看 F-001~F-052 双份事实登记 |
| 参考 | [P0 核验报告](references/verification.md) | 查看 7✅/5⚠️/0❌、实时响应头和勘误四清单 |

## 核心事实速查

| 项目 | 结论 |
|------|------|
| 高层能力 | WorkBuddy/CloudStudio 相关环境可承载公网 HTTPS 页面（F-031、F-034） |
| 实时网关 | `Server: CloudStudio Gateway`（F-035） |
| 历史域名族 | 实测 `bj10`、`sh7`、`bj3.agentos-app.net` 均有公开页面（F-034） |
| 域名漂移 | 2026-09-15 转载稿使用 `app.workbuddy.host`（F-036） |
| 未证实细节 | `sh1` 固定后缀、CLB TLS 终止、沙箱内 `sandbox-proxy`（F-037、F-038） |
| 最适场景 | 临时 Demo、公开静态页、短时联调（F-012、F-034） |
| 谨慎场景 | GitHub/支付 Webhook、长期 Agent API、含写入或敏感数据的接口（F-012、F-019~F-021） |
| 生产替代 | WMA 托管 Runtime、云服务器、容器、Vercel、IGA/BytePlus Pages 等正式托管路径（F-018、F-030、F-031、F-041、F-045、F-050） |
| TraeCode 路径 | 国际版 SOLO 经 Vercel 部署；TRAE CN 当前需另接 IGA Pages（F-041~F-045） |
| TraeWork 路径 | 经 BytePlus Pages Skill 发布网页；临时预览约 3 小时重置，长期需自定义域名（F-048~F-050） |
| 豆包工作边界 | 官方确认云电脑隔离和后台运行；公网 IP/EdgeOne 部署为第三方实测（F-051、F-052） |

## 已知边界与使用提示

- **不要硬编码域名后缀**：`sh1.agentos-app.net` 只是博文口径，实际环境可能显示其他环境前缀或 `app.workbuddy.host`，以沙箱/任务面板为准（F-007、F-036）。
- **不要把响应头推断成完整架构**：已观测到 CloudStudio Gateway，但它不能单独证明 CLB 与 sandbox-proxy 的内部职责（F-035、F-038）。
- **不要把临时端点当生产服务器**：博文自己也提示沙箱活着服务才活着、不要放机密和长期数据、7×24 应使用云服务器或容器（F-018~F-020）。
- **Webhook 需要额外验证**：HTTPS 只是必要条件之一，签名校验、重试、限流、稳定性和审计均需单独保障。
- **提示词应让 Agent 读取实际平台信息**：安全版见 [concepts/02](concepts/02-lifecycle-and-operations.md)。

## 主题关联

- [CodeBuddy 产品矩阵](../codebuddy/index.md)：本束是其中 WorkBuddy/CodeBuddy/CloudStudio 相邻能力的专题补充。
- [P0 核验报告](references/verification.md)：记录实时域名、响应头、官方文档和博文口径之间的差异。
- [博文事实登记](references/article-source.md)：所有数字、域名、产品名和命令的事实来源。

## 目录结构

```text
workbuddy-sandbox-public-endpoint/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-public-endpoint-mechanism.md
│   ├── 01-temporary-service-use-cases.md
│   ├── 02-lifecycle-and-operations.md
│   └── 03-platform-comparison.md
└── references/
    ├── index.md
    ├── article-source.md
    └── verification.md
```

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
