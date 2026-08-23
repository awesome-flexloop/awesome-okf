---
plan_version: "1.0"
created: "2026-08-23"
status: draft
---

# TRAE Community 生态 OKF Wiki 生成任务清单

## 任务依赖关系

```
Task 1 (目录结构) → Task 2-4 (R阶段: 三组分批事实采集) → Task 5-7 (I阶段: 三组洞察)
  → Task 8-19 (E阶段: 12项目分批文档生成) → Task 20 (V阶段: 独立验证)
  → Task 21 (索引生成与总索引更新) → Task 22 (C阶段: 修复闭环)
```

---

## Task 1: 创建 bundle 目录结构

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-2
- **Description**: 为 trae 分组和所有 12 个子项目创建目录结构

创建以下目录：
```
bundles/trae/
├── spec/
├── awesome-trae/
│   └── concepts/
├── trae-agents/
│   └── concepts/
├── trae-co-creation-demo-wall/
│   ├── concepts/
│   ├── examples/
│   └── references/
├── trae-co-creation-demo-wall-intl/
│   ├── concepts/
│   ├── examples/
│   └── references/
├── trae-co-creation-projects/
│   └── concepts/
├── trae-demos/
│   └── concepts/
├── trae-discussions/
│   └── concepts/
├── trae-friends-events/
│   ├── concepts/
│   ├── examples/
│   └── references/
├── trae-learning/
│   ├── concepts/
│   ├── examples/
│   └── references/
├── trae-mcp/
│   ├── concepts/
│   ├── examples/
│   └── references/
├── trae-skills/
│   ├── concepts/
│   ├── examples/
│   └── references/
└── trae-templates/
    ├── concepts/
    ├── examples/
    └── references/
```

- **Test Requirements**:
  - **TR-1 (rule)**: 所有目录存在
  - **TR-2 (rule)**: spec/ 目录已存在（已创建）

- **Completion Evidence**: 目录列表确认

---

## R 阶段：事实采集

### Task 2: R阶段 - L2 项目事实采集（trae-co-creation-demo-wall 系列）

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-4, AC-7
- **Depends On**: Task 1
- **Description**: 深度阅读 trae-co-creation-demo-wall 和 trae-co-creation-demo-wall-intl 源码，提取编号事实清单

阅读范围：
- trae-co-creation-demo-wall: package.json, tsconfig.json, next.config.ts, prisma/schema.prisma, prisma/seed.ts, src/app/ 全部路由和API, src/lib/ 全部工具模块, src/components/ UI组件, src/middleware.ts, docker-compose.yml, Dockerfile, entrypoint.sh
- trae-co-creation-demo-wall-intl: package.json, src/lib/ 与中文版的差异, prisma/schema.prisma, Dockerfile, 缺失模块(如[i18n]路由)

产出：`bundles/trae/trae-co-creation-demo-wall/spec/facts.md`（含 intl 差异事实）

事实覆盖：项目依赖版本、目录结构、数据模型(Prisma schema)、API路由、认证流程(NextAuth)、CRUD操作、COS对象存储、i18n国际化、Redis缓存、角色权限、Docker部署架构

- **Test Requirements**:
  - **TR-1 (rule)**: G1质量门通过——事实中无"用于"/"目的是"/"设计为"等推断词
  - **TR-2 (rule)**: 每个事实指向具体源码文件路径和行号
  - **TR-3 (rule)**: 核心模块全覆盖（app路由/API/lib/prisma/components/middleware/Docker）
  - **TR-4 (rule)**: intl 版本差异事实单独标注

### Task 3: R阶段 - L1 项目事实采集（trae-skills + trae-templates + trae-mcp）

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-4, AC-7
- **Depends On**: Task 1
- **Description**: 阅读 trae-skills、trae-templates、trae-mcp 源码，提取编号事实清单

阅读范围：
- trae-skills: README, skills/_template/SKILL.md, 所有9个技能的SKILL.md, daily-hot-news/resources/scripts/, kz-article-deep-analysis/scripts/, video-to-keyframes/resources/scripts/, community-points.json, .github/scripts/
- trae-templates: README, templates/ 下5大类18个模板的结构、关键文件（每个模板读README+主入口文件）
- trae-mcp: README, mcp/_template/SKILL.md, mcp/cloudbase/README.md, mcp/git-commit-generator/

产出：各项目 `spec/facts.md`

- **Test Requirements**:
  - **TR-1 (rule)**: G1质量门通过——事实无推断性表述
  - **TR-2 (rule)**: SKILL.md 格式字段完整记录（name/description/frontmatter）
  - **TR-3 (rule)**: 模板分类和每类模板的技术栈覆盖
  - **TR-4 (rule)**: 脚本文件函数/入口点记录

### Task 4: R阶段 - L1+L0 项目事实采集（trae-learning + trae-friends-events + L0组）

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-4, AC-7
- **Depends On**: Task 1
- **Description**: 阅读 trae-learning、trae-friends-events 和 5个 L0 项目

阅读范围：
- trae-learning: .vitepress/config.js, .vitepress/theme/index.js, guide/*.md, tutorials/*.md, package.json, index.md
- trae-friends-events: data/events.csv, scripts/update_readme.py, README.md, OPERATION_GUIDE.md
- awesome-trae: README.md, README_zh.md（分类体系）
- trae-agents: README.md, agents/_template/README.md, agents/git-commit-generator/README.md
- trae-demos: README.md, demos/period-1/*.md, .github/ISSUE_TEMPLATE/*.yml
- trae-co-creation-projects: README.md, README_zh.md
- trae-discussions: README.md, README.zh-CN.md

产出：各项目 `spec/facts.md`

- **Test Requirements**:
  - **TR-1 (rule)**: G1质量门通过
  - **TR-2 (rule)**: VitePress 配置与文档结构记录
  - **TR-3 (rule)**: CSV 数据模型和 Python 脚本入口记录
  - **TR-4 (rule)**: L0 项目分类体系和内容结构记录

---

## I 阶段：架构洞察

### Task 5: I阶段 - L2 项目洞察与知识地图

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-6, AC-7
- **Depends On**: Task 2
- **Description**: 基于 facts.md，提炼 trae-co-creation-demo-wall 的核心洞察四元组，设计知识地图

洞察方向：
1. Next.js App Router 分层架构（app/[language] 前台 + app/api 后端）
2. Prisma + PostgreSQL 数据模型与角色权限体系
3. NextAuth 认证 + 中间件路由保护
4. 腾讯云 COS 对象存储集成
5. Docker 全栈部署架构（Next.js + PostgreSQL + Redis + Nginx）
6. 多语言国际化（next-intl 三种语言）

知识地图：入门(2篇) → 核心架构(4-5篇) → 数据层(2-3篇) → API层(2-3篇) → 部署运维(2篇) → intl差异(1篇)

产出：`bundles/trae/trae-co-creation-demo-wall/spec/insights.md`

- **Test Requirements**:
  - **TR-1 (rule)**: G2质量门——每个洞察含陈述/证据/反常识/行动四元组
  - **TR-2 (rule)**: 洞察引用具体 F-xxx 事实编号
  - **TR-3 (rule)**: 知识地图有明确学习路径和概念-事实映射

### Task 6: I阶段 - L1 项目洞察与知识地图

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-6, AC-7
- **Depends On**: Task 3
- **Description**: 为 trae-skills、trae-templates、trae-mcp、trae-learning、trae-friends-events 提炼洞察

各项目洞察方向：
- trae-skills: SKILL.md 规范格式、技能目录结构、脚本资源组织模式、社区积分机制
- trae-templates: 5大类模板分类体系、各技术栈最小可用模板结构、TRAE 集成模式
- trae-mcp: MCP 配置规范、cloudbase MCP 能力范围、MCP与Skill的区别
- trae-learning: VitePress 文档站架构、guide/tutorials 双轨内容体系、VibeCoding 概念框架
- trae-friends-events: CSV 数据驱动的 README 自动更新、TIMELINE 标记区域机制、活动类型分类

产出：各项目 `spec/insights.md`

- **Test Requirements**:
  - **TR-1 (rule)**: G2质量门——洞察四元组完整
  - **TR-2 (rule)**: 每个项目 2-4 个核心洞察
  - **TR-3 (rule)**: 知识地图含学习路径

### Task 7: I阶段 - L0 项目洞察与知识地图

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-6, AC-7
- **Depends On**: Task 4
- **Description**: 为 5 个 L0 项目提炼轻量洞察（每个项目 1-2 个洞察即可）

产出：各项目 `spec/insights.md`

- **Test Requirements**:
  - **TR-1 (rule)**: 每个 L0 项目至少 1 个洞察
  - **TR-2 (rule)**: 知识地图简化为概念文档清单

---

## E 阶段：文档生成（分批执行，每批≤7文件，references 先行）

### Task 8: E阶段 - trae-co-creation-demo-wall references/ 生成

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-5
- **Depends On**: Task 5
- **Description**: 生成 demo-wall 的信源登记文件

生成：
- references/prisma-schema.md - Prisma 数据模型信源
- references/api-routes.md - API 路由信源
- references/lib-modules.md - lib/ 工具模块信源
- references/auth-system.md - 认证系统信源
- references/docker-deploy.md - Docker 部署信源
- references/nextjs-config.md - Next.js 配置信源
- references/index.md - 信源索引

- **Test Requirements**:
  - **TR-1 (rule)**: references/ 先于 concepts/ 生成（信源先行）
  - **TR-2 (rule)**: 每个信源文件含 frontmatter 和源码路径引用
  - **TR-3 (rule)**: references/index.md 无 frontmatter

### Task 9: E阶段 - trae-co-creation-demo-wall concepts/ 第一批（入门+架构）

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-6
- **Depends On**: Task 8
- **Description**: 生成 demo-wall 概念文档前 5 篇

生成：
- concepts/00-introduction.md - 项目介绍与技术栈概览
- concepts/01-project-structure.md - 目录结构与分层架构
- concepts/02-app-router.md - Next.js App Router 路由体系
- concepts/03-api-routes.md - API 路由设计
- concepts/04-component-architecture.md - UI 组件架构

每批 ≤ 5 文件。

- **Test Requirements**:
  - **TR-1 (rule)**: 每篇含完整 frontmatter
  - **TR-2 (rule)**: sources 字段指向已存在的 references/ 文件
  - **TR-3 (rule)**: API/类名与 facts.md 一致

### Task 10: E阶段 - trae-co-creation-demo-wall concepts/ 第二批（数据+认证）

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-6
- **Depends On**: Task 9
- **Description**: 生成 demo-wall 概念文档中 5 篇

生成：
- concepts/05-prisma-schema.md - Prisma 数据模型设计
- concepts/06-auth-nextauth.md - NextAuth 认证系统
- concepts/07-middleware.md - 中间件与路由保护
- concepts/08-role-permission.md - 角色权限体系
- concepts/09-cos-storage.md - 腾讯云 COS 对象存储

- **Test Requirements**: 同 Task 9

### Task 11: E阶段 - trae-co-creation-demo-wall concepts/ 第三批（部署+examples）

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-6
- **Depends On**: Task 10
- **Description**: 生成 demo-wall 剩余概念文档和示例文档

生成 concepts/：
- concepts/10-i18n-next-intl.md - 国际化实现
- concepts/11-redis-cache.md - Redis 缓存集成
- concepts/12-docker-deployment.md - Docker 全栈部署
- concepts/13-seed-data.md - 种子数据与初始化
- concepts/index.md - 概念索引（无frontmatter）

生成 examples/：
- examples/local-dev-setup.md - 本地开发环境搭建
- examples/docker-deploy.md - Docker 部署示例
- examples/api-usage.md - API 调用示例
- examples/custom-extension.md - 自定义扩展指南
- examples/index.md - 示例索引（无frontmatter）

- **Test Requirements**:
  - **TR-1 (rule)**: concepts/index.md 和 examples/index.md 无 frontmatter
  - **TR-2 (rule)**: 代码示例可运行或与源码一致
  - **TR-3 (rule)**: index.md 列出所有目录内文档

### Task 12: E阶段 - trae-co-creation-demo-wall-intl 完整生成

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-3, AC-5, AC-6
- **Depends On**: Task 11
- **Description**: 生成 intl 版本的文档，聚焦与中文版的差异

生成 references/、concepts/（3-4篇，聚焦差异点：edge-config、精简lib、缺失功能）、examples/（1-2篇）

- **Test Requirements**:
  - **TR-1 (rule)**: 文档明确标注与中文版的差异
  - **TR-2 (rule)**: 不重复中文版已有内容，使用交叉引用
  - **TR-3 (rule)**: 所有 index.md 最后生成

### Task 13: E阶段 - trae-skills 文档生成

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-5, AC-6
- **Depends On**: Task 6
- **Description**: 生成 trae-skills 的 references/、concepts/、examples/

references/（先）: skill-format.md, script-resources.md, community-points.md
concepts/（分批，每批≤5）:
  - 00-introduction.md, 01-skill-md-spec.md, 02-skill-catalog.md
  - 03-script-patterns.md, 04-resource-organization.md
  - concepts/index.md
examples/:
  - create-skill.md, use-skill.md, community-points-system.md
  - examples/index.md

- **Test Requirements**:
  - **TR-1 (rule)**: references/ 先行
  - **TR-2 (rule)**: 技能目录覆盖所有9个社区技能
  - **TR-3 (rule)**: SKILL.md frontmatter 字段准确描述

### Task 14: E阶段 - trae-templates 文档生成

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-5, AC-6
- **Depends On**: Task 6
- **Description**: 生成 trae-templates 文档

references/: template-structure.md, category-mapping.md
concepts/:
  - 00-introduction.md, 01-template-catalog.md, 02-web-frontend-templates.md
  - 03-backend-templates.md, 04-mobile-desktop-templates.md
  - 05-data-ai-templates.md, 06-devops-templates.md
  - concepts/index.md
examples/: use-template.md, customize-template.md, examples/index.md

- **Test Requirements**:
  - **TR-1 (rule)**: 5大类模板全覆盖
  - **TR-2 (rule)**: 每个模板列出技术栈和关键文件

### Task 15: E阶段 - trae-mcp + trae-friends-events 文档生成

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-3, AC-5, AC-6
- **Depends On**: Task 6
- **Description**: 生成 trae-mcp 和 trae-friends-events 文档

trae-mcp:
- references/: mcp-protocol.md, cloudbase-mcp.md
- concepts/: 00-introduction.md, 01-mcp-concept.md, 02-cloudbase-mcp.md, concepts/index.md
- examples/: configure-mcp.md, use-mcp.md, examples/index.md

trae-friends-events:
- references/: csv-schema.md, update-script.md
- concepts/: 00-introduction.md, 01-event-data-model.md, 02-timeline-mechanism.md, concepts/index.md
- examples/: add-event.md, run-update-script.md, examples/index.md

- **Test Requirements**:
  - **TR-1 (rule)**: MCP 概念与 Skill 概念明确区分
  - **TR-2 (rule)**: CSV 字段和 Python 脚本入口准确

### Task 16: E阶段 - trae-learning 文档生成

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-3, AC-5, AC-6
- **Depends On**: Task 7
- **Description**: 生成 trae-learning 文档

references/: vitepress-config.md, content-structure.md
concepts/:
  - 00-introduction.md, 01-vitepress-architecture.md, 02-vibecoding-concept.md
  - 03-guide-content.md, 04-tutorial-content.md, concepts/index.md
examples/: local-preview.md, add-content.md, examples/index.md

- **Test Requirements**:
  - **TR-1 (rule)**: VitePress 配置和主题定制准确描述
  - **TR-2 (rule)**: guide/ 和 tutorials/ 内容体系完整覆盖

### Task 17: E阶段 - L0 项目文档生成（第一批：awesome-trae + trae-agents）

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-3, AC-6
- **Depends On**: Task 7
- **Description**: 生成 awesome-trae 和 trae-agents 的轻量文档

awesome-trae:
- concepts/: 00-introduction.md, 01-resource-categories.md, concepts/index.md

trae-agents:
- concepts/: 00-introduction.md, 01-agent-config.md, 02-git-commit-agent.md, concepts/index.md

L0 项目不生成 references/ 和 examples/（或只生成极简版）。

- **Test Requirements**:
  - **TR-1 (rule)**: 每篇含完整 frontmatter
  - **TR-2 (rule)**: 分类体系准确反映 README 结构

### Task 18: E阶段 - L0 项目文档生成（第二批：trae-demos + trae-co-creation-projects）

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-3, AC-6
- **Depends On**: Task 7
- **Description**: 生成 trae-demos 和 trae-co-creation-projects 文档

trae-demos:
- concepts/: 00-introduction.md, 01-submission-process.md, 02-demo-showcase.md, concepts/index.md

trae-co-creation-projects:
- concepts/: 00-introduction.md, 01-project-categories.md, 02-submission-guide.md, concepts/index.md

- **Test Requirements**: 同 Task 17

### Task 19: E阶段 - L0 项目文档生成（第三批：trae-discussions）

- **Priority**: low
- **Status**: pending
- **AC Coverage**: AC-3, AC-6
- **Depends On**: Task 7
- **Description**: 生成 trae-discussions 文档

trae-discussions:
- concepts/: 00-introduction.md, 01-discussion-guidelines.md, concepts/index.md

- **Test Requirements**: 同 Task 17

---

## V 阶段：独立验证

### Task 20: V阶段 - 全量验证与修复

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-3, AC-4, AC-5
- **Depends On**: Task 8-19
- **Description**: 对所有生成文档执行独立验证

验证项：
1. **结构检查**：目录结构完整，index.md 存在且格式正确
2. **Frontmatter 检查**：所有非index文件含完整必填字段
3. **链接检查**：所有内部交叉链接可解析，无 `../` 路径
4. **API Grep验证**（L2项目）：文档中所有类名/函数名/API路径在源码中验证存在
5. **结构验证**（L1项目）：SKILL.md字段、模板结构、脚本函数经验证
6. **内容验证**（L0项目）：分类体系和内容与README一致
7. **sources 验证**：所有 sources 指向的 references/ 文件存在
8. **批量修复**：发现的问题逐一修复

使用独立的 general_purpose_task 进行只读验证，不修改文件。

- **Test Requirements**:
  - **TR-1 (rule)**: G4质量门——0虚构API、0断链、frontmatter 100%完整
  - **TR-2 (rule)**: 交叉链接全部使用 `/` 开头路径
  - **TR-3 (rule)**: L2 项目关键 API 经 Grep 验证（输出验证日志）
  - **TR-4 (rubric)**: 文档质量评分 ≥2 分（AC-6 标准）

---

## 最终组装

### Task 21: 生成根索引与更新总索引

- **Priority**: high
- **Status**: pending
- **AC Coverage**: AC-1
- **Depends On**: Task 20
- **Description**: 生成各 bundle 的 index.md 和 log.md，创建 trae 分组索引，更新总索引

1. 为每个项目生成 index.md（含okf_version frontmatter，最后生成）
2. 为每个项目生成 log.md
3. 创建 `bundles/trae/index.md` 分组索引
4. 更新 `bundles/index.md` 增加 trae 分组
5. 更新 bundles/index.md 中的统计数字（total_bundles, groups 等）

- **Test Requirements**:
  - **TR-1 (rule)**: 每个 bundle 的 index.md 含 okf_version: "0.2" 和 type 字段
  - **TR-2 (rule)**: trae/index.md 列出所有 12 个子项目 bundle 链接
  - **TR-3 (rule)**: bundles/index.md 增加 trae 分组行和分组详情
  - **TR-4 (rule)**: 所有 index.md 最后写入（确保内容完整）

### Task 22: C阶段 - 最终闭环与模式沉淀

- **Priority**: medium
- **Status**: pending
- **AC Coverage**: AC-7
- **Depends On**: Task 21
- **Description**: 回顾全流程，补充反模式和迁移验证，记录经验

产出：验证最终报告，确认所有 AC 通过。如发现新可复用模式，记录到项目经验中。

- **Test Requirements**:
  - **TR-1 (rule)**: 所有 AC 有通过证据
  - **TR-2 (rubric)**: 方法论遵循评分 ≥1 分（AC-7 标准）
