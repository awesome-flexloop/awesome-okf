---
type: Reference
title: Kanzan 公开中文站点信源与覆盖台账
date: 2026-10-27
status: stable
stale_after: 2026-12-31
sources:
  - id: site
    resource: https://www.kanzan.top/zh
  - id: blog
    resource: https://www.kanzan.top/zh/blog
---

# 信源与覆盖台账

采集时点为 2026-10-27。正文以 Defuddle 提取为主，超时或失败时以 WebFetch 回退；导航集合以 HTTP 页面链接去重统计。以下记录的是公开中文页面覆盖，不代表整个域名、英文镜像或关联产品站的全量覆盖。

## 栏目入口

| 键 | 页面 | URL | 处理 |
|---|---|---|---|
| P01 | 首页 | <https://www.kanzan.top/zh> | 已读；三条服务线与栏目入口 |
| P02 | 关于 | <https://www.kanzan.top/zh/about> | 已读；主体信息仅官网自述 |
| P03 | 服务 | <https://www.kanzan.top/zh/services> | 已读；场景、系统、团队 |
| P04 | 联系 | <https://www.kanzan.top/zh/contact> | 已读；未提交表单或联系公司 |
| P05 | 法律 | <https://www.kanzan.top/zh/legal> | 已读；法律文本仍为占位 |
| P06 | 博客索引 | <https://www.kanzan.top/zh/blog> | 已读；机械去重得到 21 个文章 URL |
| P07 | 站点地图 | <https://www.kanzan.top/sitemap.xml> | 已读；不能替代博客导航 |

## 文章集合

以下 21 篇均已读取正文。表内日期来自博客页面的发布时间展示，不以 sitemap 的 `lastmod` 代替。各篇的认识论地位不同：官网谈自身服务是主体自述，作者谈产品是能力宣称，作者转述研究则需回到研究原文。

| 键 | 日期 | 主题与原文 | 支撑事实 |
|---|---|---|---|
| B01 | 2026-07-28 | [照片托管与 LifeFrame](https://www.kanzan.top/zh/blog/what-is-photo-hosting-why-lifeframe) | F-028、F-029 |
| B02 | 2026-07-14 | [工业稳定性悖论](https://www.kanzan.top/zh/blog/industrial-ai-stability-paradox) | F-023、F-024 |
| B03 | 2026-07-08 | [Next.js 生产部署流水线](https://www.kanzan.top/zh/blog/github-actions-nextjs-deploy-pipeline) | F-036～F-039 |
| B04 | 2026-05-27 | [AlphaProof Nexus](https://www.kanzan.top/zh/blog/alphaproof-nexus-ai-math-2026) | F-043～F-045 的转述背景 |
| B05 | 2026-05-25 | [单次 AI 任务成本](https://www.kanzan.top/zh/blog/deepseek-ai-task-cost-workflow-2026) | F-025～F-027 |
| B06 | 2026-05-22 | [淮安创业与城市记忆](https://www.kanzan.top/zh/blog/ai-huaian-opc-city-possibility) | F-035 |
| B07 | 2026-05-20 | [苏淮智汇湾入驻记录](https://www.kanzan.top/zh/blog/suhuai-zhihuiwan-kanzan-ai-lab-may-2026) | F-006 |
| B08 | 2026-05-19 | [Anthropic 访谈解读](https://www.kanzan.top/zh/blog/anthropic-81k-interviews-ai-analysis) | F-041、F-042 的转述背景 |
| B09 | 2026-05-19 | [本土 AI 创业判断与政策建议](https://www.kanzan.top/zh/blog/advice-for-ai-founders) | F-033、F-035 |
| B10 | 2026-05-18 | [公司简介](https://www.kanzan.top/zh/blog/kanzan-ai-company-profile) | F-006；主体介绍为背景，F-004、F-005 以 P02 为登记依据 |
| B11 | 2026-05-16 | [MCP 与 Skills 解析](https://www.kanzan.top/zh/blog/mcp-protocol-and-agent-skills-deep-dive-2026) | F-015～F-019 的转述背景 |
| B12 | 2026-05-13 | [前线部署工程师](https://www.kanzan.top/zh/blog/forward-deployed-engineer-ai-deployment) | F-034 |
| B13 | 2026-05-12 | [EventType 工作语言](https://www.kanzan.top/zh/blog/agent-eventtype-work-language) | F-021、F-022 |
| B14 | 2026-05-12 | [人类与 Agent 共用 Feed](https://www.kanzan.top/zh/blog/event-feed-ai-workspace) | F-020 |
| B15 | 2026-05-12 | [上传、分享与 AI 相册](https://www.kanzan.top/zh/blog/lifeframe-photo-upload-ai-album) | F-030、F-031 |
| B16 | 2026-05-10 | [LifeFrame 时间线与地理](https://www.kanzan.top/zh/blog/lifeframe-intro) | F-028、F-032 |
| B17 | 2026-05-10 | [Headless CMS 与 Agent](https://www.kanzan.top/zh/blog/from-wordpress-to-headless-cms-agent-era) | F-013、F-014 |
| B18 | 2026-05-08 | [AI 场景评估](https://www.kanzan.top/zh/blog/why-ai-projects-start-with-use-case-assessment) | F-008、F-009 |
| B19 | 2026-05-08 | [站点上线说明](https://www.kanzan.top/zh/blog/welcome) | F-007 |
| B20 | 2026-05-08 | [企业知识库治理](https://www.kanzan.top/zh/blog/enterprise-knowledge-base-ai-foundation) | F-010、F-011 |
| B21 | 2026-05-08 | [岗位工作流培训](https://www.kanzan.top/zh/blog/designing-ai-workflow-training) | F-012 |

## 权威补充来源

| 键 | 来源 | 已核验范围 | 限定 |
|---|---|---|---|
| A01 | [MCP 架构](https://modelcontextprotocol.io/docs/learn/architecture) | Host/Client/Server；Tools/Resources/Prompts；协议范围 | 动态文档，采集时点快照；不据此补写全部接口 |
| A02 | [Agent Skills 格式规范](https://agentskills.io/specification) | `SKILL.md`、YAML 元数据、可选目录、渐进披露 | 格式约定不等于任何宿主都支持 |
| A03 | [Anthropic 原始访谈研究](https://www.anthropic.com/features/81k-interviews) | 样本、分类方法、限制、发布日期 | 厂商自有用户研究；非人口代表性调查；未读取 PDF 附录 |
| A04 | [AlphaProof Nexus 论文 v2](https://arxiv.org/html/2605.22763v2) | 摘要、引言、架构、系统评估与成本章节 | 定点精读相关章节；未重跑证明或通读全部附录 |
| A05 | [GitHub 跳过工作流](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs) | `[skip ci]` 支持与必需检查限制 | 不证明博文流水线安全或已经运行 |
| A06 | [Prisma 原迁移入口](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production)及 HTTP 页面指向的[ORM 8 应用迁移](https://www.prisma.io/docs/orm/migrations/applying-a-migration) | HTTP 页面显示新体系，同日 WebFetch 返回旧内容；差异原文保存在核验记录 | 以版本和获取通道限定，不混用命令 |
| A07 | [MCP 安全最佳实践 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) | 本地进程授权、隔离、最小权限、令牌受众 | 固定版本的安全参考；不冒充当前全部规范 |

## 覆盖结果与缺口

| 集合 | 数量与状态 | 解释 |
|---|---|---|
| 中文栏目正文 | 6 页已读 | 首页、关于、服务、联系、法律、博客索引 |
| 博客索引文章 | 21/21 篇已读 | URL 去重与上表双向核对 |
| sitemap 独有中文文章 | 3 条读取返回 404 | `chart-render-test`、`kanzan-cms-online`、`use-payload-post-test` |
| 权威补充来源 | 7 条 | 通读短文；论文按相关章节精读 |
| 排除范围 | 无内容覆盖声明 | `/admin`、登录后功能、英文镜像、LifeFrame/OPC Feed/BullyStop 产品站全量内容 |

早期采集笔记曾写“22 篇”，恢复后以 HTTP 链接集合机械核准为 21 篇，已统一修正。三个 sitemap 独有 URL 无正文可读，不把它们计入成功覆盖或推测其内容。

未独立核验的事项包括工商登记、产品功能与价格、工业成效数字、创业文章的政策与法律判断、FDE 融资与人员数字。它们不用于本包的采购、合规或效果承诺。采集只使用公开页面，没有尝试后台访问、提交表单或绕过访问限制。

返回[知识包总览](../index.md)。
