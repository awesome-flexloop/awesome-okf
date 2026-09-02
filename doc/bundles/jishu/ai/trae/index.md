---
type: category
title: "TRAE Community 生态"
okf_version: "0.2"
description: "TRAE Community 生态知识包——15个知识包、136篇内容文档（含82概念+36示例+18信源），覆盖平台应用、扩展系统、学习资源、社区治理、战略资讯五大板块"
total_bundles: 15
total_content_docs: 136
total_md_files: 184
verified: grep-verified
generated: true
status: stable
---

# TRAE Community 生态知识库

本知识包分组收录 [TRAE Community](https://github.com/trae-community) 开源社区生态各核心仓库的系统化中文源码教程。TRAE 是字节跳动推出的 AI 编程 IDE，trae-community 组织维护了围绕 TRAE 生态的展示平台、技能系统、模板库、MCP 服务器、学习文档和社区治理仓库。

所有知识包遵循 [OKF v0.2 规范](../../../meta/okf-spec/index.md)。源码教程类知识包通过源码深度阅读（R→I→E→V→C 五阶段链路）生成，API 引用均经源码事实验证；战略资讯类知识包（见下方"📰 战略资讯"板块）通过博文事实采集与多媒体核验（R→I→E→V 四阶段链路）生成，数据口径差异与作者观点均已显式标注。

## 📊 知识包概览

| 板块 | 知识包 | 级别 | 概念 | 示例 | 信源 | 内容文档 |
|------|--------|------|------|------|------|---------|
| 🖥️ 平台应用 | [trae-co-creation-demo-wall](trae-co-creation-demo-wall/index.md) | L2 | 17 | 8 | 1 | 26 |
| 🖥️ 平台应用 | [trae-co-creation-demo-wall-intl](trae-co-creation-demo-wall-intl/index.md) | L2 | 7 | 7 | 1 | 15 |
| 🔌 扩展系统 | [trae-skills](trae-skills/index.md) | L1 | 8 | 4 | 1 | 13 |
| 🔌 扩展系统 | [trae-templates](trae-templates/index.md) | L1 | 8 | 4 | 1 | 13 |
| 🔌 扩展系统 | [trae-mcp](trae-mcp/index.md) | L1 | 6 | 3 | 1 | 10 |
| 📚 学习资源 | [trae-learning](trae-learning/index.md) | L1 | 6 | 3 | 1 | 10 |
| 📚 学习资源 | [awesome-trae](awesome-trae/index.md) | L0 | 3 | 1 | 1 | 5 |
| 📚 学习资源 | [trae-demos](trae-demos/index.md) | L0 | 3 | 1 | 1 | 5 |
| 👥 社区治理 | [trae-agents](trae-agents/index.md) | L0 | 3 | 1 | 1 | 5 |
| 👥 社区治理 | [trae-co-creation-projects](trae-co-creation-projects/index.md) | L0 | 3 | 1 | 1 | 5 |
| 👥 社区治理 | [trae-discussions](trae-discussions/index.md) | L0 | 3 | 1 | 1 | 5 |
| 👥 社区治理 | [trae-friends-events](trae-friends-events/index.md) | L1 | 4 | 2 | 1 | 7 |
| 📰 战略资讯 | [bytedance-ai-consolidation](bytedance-ai-consolidation/index.md) | L0 | 3 | 0 | 2 | 5 |
| 📰 战略资讯 | [threeui](threeui/index.md) | L0 | 4 | 0 | 2 | 6 |
| 📰 战略资讯 | [tushare-ai-office](tushare-ai-office/index.md) | L0 | 4 | 0 | 2 | 6 |
| **合计** | **15 知识包** | | **82** | **36** | **18** | **136** |

> 注："内容文档"指 concepts/examples/references 目录下的实质性文档。含导航索引、spec 工作文件共 **184 个 .md 文件**。

## 🖥️ 平台应用层

| 知识包 | 一句话简介 |
|--------|-----------|
| [trae-co-creation-demo-wall](trae-co-creation-demo-wall/index.md) | AI 共创作品展示墙——Next.js 15 全栈应用，Prisma+PostgreSQL 数据层，NextAuth v5 认证，next-intl 三语国际化，腾讯云 COS 存储，Tiptap 富文本编辑，RBAC 权限+审核+审计日志治理闭环，Docker 五服务编排部署 |
| [trae-co-creation-demo-wall-intl](trae-co-creation-demo-wall-intl/index.md) | 展示墙国际版——面向海外部署的变体，Vercel Edge Config 边缘缓存，5 语言支持（增印尼语/越南语），CSV 数据导出，GDPR 合规审计留存（SetNull 策略），移除用户封禁系统，Vercel Serverless 优先部署 |

## 🔌 扩展系统层

| 知识包 | 一句话简介 |
|--------|-----------|
| [trae-skills](trae-skills/index.md) | 社区技能仓库——SKILL.md 提示词包规范（YAML frontmatter+Markdown 指令体），三类技能模式（纯 Prompt/脚本辅助/Workflow 编排），12 个社区技能实现，Python 脚本集成模式，社区积分自动化激励机制（GitHub Actions + Ledger 幂等去重） |
| [trae-templates](trae-templates/index.md) | 项目模板仓库——五维分面分类法（前端/后端/移动/AI/工具），23 个最小可用模板，superpowers-trae-init 的 .trae/ 配置驱动模式，AGENTS.md 作为 AI 开发契约文件（4条铁律+工具映射+触发器字典） |
| [trae-mcp](trae-mcp/index.md) | MCP 服务器集合——Model Context Protocol 三层模型（Transport/Protocol/Capability），MCP 与 Skill 本质区别（工具服务器 vs 提示词包），CloudBase MCP 云开发资源编排，MCP 开发入门指南 |

## 📚 学习资源层

| 知识包 | 一句话简介 |
|--------|-----------|
| [trae-learning](trae-learning/index.md) | 官方学习站——VitePress 文档站架构，自定义主题（Canvas 3D 地球仪+玻璃拟态），Vibecoding 理念（心流/意图/反馈），4 篇指南+6 篇实战教程三级递进，GitHub Pages 自动部署，双语 Issue 模板贡献闭环 |
| [awesome-trae](awesome-trae/index.md) | awesome-list 资源索引——8 大分类双层架构，跨仓库 hub 索引模式（导向姊妹仓库），中英双语维护，4 维权重评分审核机制（Relevance 30%+Quality 30%+Documentation 20%+Impact 20%） |
| [trae-demos](trae-demos/index.md) | 期数制 Demo 展示——period-N 目录组织，Markdown 驱动双语 Demo 卡片，多场景 Issue 模板投稿，TRAE Usage 40% 权重差异化审核 |

## 👥 社区治理层

| 知识包 | 一句话简介 |
|--------|-----------|
| [trae-agents](trae-agents/index.md) | Agent 配置仓库——"文档即配置"目录约定，README.md 8 章节规范，_template 模板，git-commit-generator 高质量参考实现冷启动 |
| [trae-co-creation-projects](trae-co-creation-projects/index.md) | 共创项目征集——Issue 表单驱动低门槛投稿，接受所有阶段项目，Collaboration 30% 权重差异化审核，中英双语提交 |
| [trae-discussions](trae-discussions/index.md) | 社区讨论论坛——GitHub Discussions 分类引导，5 大讨论分类，3 文件极简导航枢纽，社区礼仪与有效提问指南 |
| [trae-friends-events](trae-friends-events/index.md) | 活动数据管理——CSV+Python 零依赖轻量 CMS 模式，HTML 注释标记替换 README 时间轴，9 种活动类型颜色映射，OPERATION_GUIDE 运营指南+AI Prompt 辅助降低贡献门槛 |

## 📰 战略资讯层

| 知识包 | 一句话简介 |
|--------|-----------|
| [bytedance-ai-consolidation](bytedance-ai-consolidation/index.md) | 字节跳动 2026 年 8 月 AI 业务整合商业分析——TRAE/扣子/飞书并入豆包的组织时间线、算力成本驱动逻辑（含 850 亿年份错配更正与多口径标注）、腾讯/阿里/字节 AI 办公三方竞争格局；博文作者标注"个人观点"，数据经 36 氪/南华早报/第一财经等多媒体核验 |
| [threeui](threeui/index.md) | Meng To 开源的 Three.js/WebGL 视觉组件库——164 个 Community 效果、10 大分类（⚠️官网当前 9 个）、6 大组件类型、AI Coding 集成（Codex/Claude Code/Cursor）、MCP Server（Pro），WebGL UI 组件化趋势分析；P0 核验 4✅ 3⚠️ 0❌ |
| [tushare-ai-office](tushare-ai-office/index.md) | Tushare 宣布上架 WorkBuddy/千问办公/TraeWork 三大 AI 办公平台——⚠️ P0 核验发现核心声明存疑（3✅ 2⚠️ 1❌），Tushare MCP 仍需手动配置，三平台官方预置连接器未获证实，status: flagged |

## 学习路径推荐

### 路径1：TRA E用户（使用平台和扩展）

```
trae-skills/00-introduction → trae-templates/00-introduction → trae-mcp/00-introduction
                                    ↓
                           选择需要的 Skill/Template/MCP → examples/ 快速上手
                                    ↓
                           awesome-trae（发现更多资源）→ trae-demos（看示例）
```

### 路径2：平台开发者（二次开发/部署 Demo Wall）

```
trae-co-creation-demo-wall/00-introduction → 01-getting-started → 02-architecture-overview
                                    ↓
               ┌──────────┬──────────┼──────────┬──────────┐
               ↓          ↓          ↓          ↓          ↓
          03-data    04-auth    05-i18n    06-api     07-crud
               ↓          ↓          ↓          ↓          ↓
          09-cos    10-audit   13-form    15-docker   16-test
                                    ↓
                    examples/setup-dev-environment → examples/docker-deploy
                                    ↓
                    （海外部署）→ trae-co-creation-demo-wall-intl
```

### 路径3：生态贡献者（参与社区建设）

```
awesome-trae/00-introduction → trae-co-creation-projects/00-introduction
                                    ↓
               ┌──────────┬──────────┼──────────┐
               ↓          ↓          ↓          ↓
         trae-demos  trae-agents  trae-skills/07-write-skill
               ↓          ↓          ↓
         trae-discussions  trae-friends-events  trae-templates（贡献模板）
```

## 核心洞察（源码学习关键发现）

1. **Demo Wall 垂直分表**：WorkBase/Detail/Image/Team/Statistic 五表分离不是过度设计——读写频率差异、一对多图片、高频计数器独立是精准切分
2. **RBAC+字典双轨制**：角色硬编码安全优先，分类字典化运营可配——同一 SysDictItem 机制复用为封禁/屏蔽黑名单
3. **SKILL.md 本质是提示词包**：不是传统代码插件，而是 YAML frontmatter 元数据驱动的"提示词指令包"，when_to_use 精确描述决定加载时机
4. **MCP 与 Skill 互补**：MCP 是可调用的工具服务器（给 AI 手和眼），Skill 是提示词指令包（给 AI 方法论），二者定位不同但可协作
5. **CSV+Python 轻量 CMS**：非技术社区运营场景下，CSV 数据源+Python 脚本+Markdown 生成是零依赖、可审计、低门槛的最优解
6. **Vercel Edge Config 缓存字典**：边缘缓存最佳候选是高频读低频变更的字典数据，而非业务数据；手动同步比自动更可靠
7. **GDPR 审计留存**：外键 Cascade→SetNull 不是简单的策略调整，而是删除用户不销毁审计链的合规设计

## 仓库信息

- **组织**：[trae-community](https://github.com/trae-community)
- **许可证**：各仓库独立（Demo Wall 为 MIT）
- **文档生成日期**：2026-04-22
- **方法论**：七概念方法论（R→I→E→V→C）+ source-code-to-okf-wiki 工作流

```{toctree}
:hidden:
:maxdepth: 7

trae-co-creation-demo-wall/index
trae-co-creation-demo-wall-intl/index
trae-skills/index
trae-templates/index
trae-mcp/index
trae-learning/index
awesome-trae/index
trae-demos/index
trae-agents/index
trae-co-creation-projects/index
trae-discussions/index
trae-friends-events/index
bytedance-ai-consolidation/index
threeui/index
tushare-ai-office/index
spec/index
trae-v3-3-74-release-notes
log
```
