---
type: concept
title: concepts 索引
description: miaowu-product-guide bundle 概念文档导航——平台总览、构建期模式/模型/网页/小程序/可视化、平台服务（云服务/AI/素材/文件/根目录）、扩展生态（技能/市场/连接器）共 14 篇
tags: [meoo, miaowu, product-guide, platform]
---

# concepts/ 索引

本目录存放秒悟 Meoo 产品功能全景的教程化概念页，共 14 篇，按「总览 → 怎么构建（01–05）→ 平台服务（06–10）→ 扩展生态（11–13）」三条线组织。

## 文档列表

| 文档 | 说明 |
|------|------|
| [00-platform-overview.md](00-platform-overview.md) | 平台总览：云端 AI 开发工具定位、四项自动交付、五亮点（区分营销与事实）、四类人群、六类应用 |
| [01-agent-modes.md](01-agent-modes.md) | Agent / Swarms / Plan / Design 四模式选型表与组合用法 |
| [02-model-selection.md](02-model-selection.md) | 构建器 13 模型选型图谱（4 厂商参数均标厂商自述）；与运行时 9 传参值双清单辨析 |
| [03-web-app-build.md](03-web-app-build.md) | 网页应用四阶段主线：五要素提示词与三组正反例、一键建库话术、自动单测、回滚对比、两档域名 |
| [04-wechat-miniprogram.md](04-wechat-miniprogram.md) | 小程序七步流程、H5/真机双预览、备案审核、三方权责 10 行表、五项配置、7 项清单、6 FAQ |
| [05-visual-editing.md](05-visual-editing.md) | 可视化修改：「可视化+代码」双模、圈选标注、圈选后对话改码 |
| [06-cloud-services.md](06-cloud-services.md) | 云服务：不开就是展示页、四特性、数据库 CSV、50MB 文件、GoTrue 认证、Secrets |
| [07-ai-service.md](07-ai-service.md) | AI 服务：9 传参值/两端点/两档计费/自动四步/Cloud→AI，含三段官方 fetch 参考代码 |
| [08-asset-center.md](08-asset-center.md) | 素材中心：素材制作 Tab、Agent/直连双模、积分预估、图视音频生成、筛选收藏夹回收站 |
| [09-file-storage.md](09-file-storage.md) | 文件上传/下载/存储：10 格式、5MB/10 个、沙箱易失、代码下载套餐、存储桶 CDN 四步法 |
| [10-root-file-seo-geo.md](10-root-file-seo-geo.md) | 根目录文件：验证文件默认开放 vs SEO/GEO 双条件、独立域名判定、4 FAQ |
| [11-skills-authoring.md](11-skills-authoring.md) | 技能创建：Skill vs Prompt、四原则、天气示例、模型推荐、三步构建、五步迭代 |
| [12-skill-marketplace.md](12-skill-marketplace.md) | 技能市场：语义搜索、8 类型 vs 7 标签、详情页权限矩阵、zip 上传 |
| [13-connectors.md](13-connectors.md) | 连接器：外部 API、积分计费、连接两层模型、两场景、监控解绑、注册自有连接器（MCP dated） |

## 阅读建议

- **第一次了解秒悟**：从 [00](00-platform-overview.md) 开始，再按身份选线；
- **要动手做一个网页应用**：00 → 01 → 02 → 03，需要后台能力加读 06/07；
- **要发布微信小程序**：03 → 04（配合 06 的登录认证、09 的 CDN）；
- **要给应用加 AI/素材能力**：07 → 08 → 09；
- **要做平台扩展**：11 → 12 → 13；
- 所有事实断言的逐字出处在 [references/source-ledger.md](../references/source-ledger.md)（F-001–F-150，14 源），口径冲突、时效风险与噪声处理在 [references/verification.md](../references/verification.md)。
- 命令行与开放平台（CLI 安装、BYOC 部署、团队 token 集成）不在本束，见姊妹束 [miaowu-cli-open-guide](../../miaowu-cli-open-guide/index.md)。

```{toctree}
:hidden:
:maxdepth: 2

00-platform-overview
01-agent-modes
02-model-selection
03-web-app-build
04-wechat-miniprogram
05-visual-editing
06-cloud-services
07-ai-service
08-asset-center
09-file-storage
10-root-file-seo-geo
11-skills-authoring
12-skill-marketplace
13-connectors
```
