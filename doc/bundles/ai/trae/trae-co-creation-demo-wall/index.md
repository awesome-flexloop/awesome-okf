---
type: Index
title: trae-co-creation-demo-wall
description: trae-co-creation-demo-wall 是基于 Next.js 15 全栈框架构建的 AI 共创作品展示平台，支持作品提交、审核、展示、点赞排行等完整功能。本bundle基于源码深度分析，覆盖核心架构、数据模型、认证体系、国际化、部署运维。
tags: [demo-wall, nextjs, fullstack, prisma, nextauth, i18n, docker]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## trae-co-creation-demo-wall Bundle

本bundle提供 trae-co-creation-demo-wall（AI 共创作品展示墙）的源码级学习文档，基于七概念方法论从源码提炼核心知识，覆盖从入门使用到生产部署的完整学习路径。

## 快速导航

### 入门

| 文档 | 内容 |
|------|------|
| [项目简介](/concepts/00-introduction.md) | 定位、技术栈总览、核心特性、能力边界 |
| [快速开始](/concepts/01-getting-started.md) | 环境要求、安装步骤、环境变量、数据库初始化、开发启动 |

### 核心架构

| 文档 | 内容 |
|------|------|
| [架构总览](/concepts/02-architecture-overview.md) | Next.js全栈架构、垂直分表模型、三层数据流、治理闭环 |
| [数据模型设计](/concepts/03-data-model.md) | Prisma Schema详解、Work五表垂直分表、SysDict字典系统、RBAC角色 |
| [认证系统](/concepts/04-auth-system.md) | NextAuth v5配置、Credentials+JWT、授权守卫、用户封禁双重检查 |
| [国际化路由](/concepts/05-i18n-routing.md) | next-intl配置、[language]动态段、三层中间件链、翻译文件 |

### 扩展机制

| 文档 | 内容 |
|------|------|
| [API 路由设计](/concepts/06-api-routes.md) | RESTful路由组织、Prisma CRUD、Zod校验、文件上传代理 |
| [CRUD 数据层](/concepts/07-crud-layer.md) | 通用CRUD函数、zustand缓存、react-query Hooks、表单校验 |
| [富文本编辑器](/concepts/08-rich-text-editor.md) | Tiptap配置、sanitize-html白名单XSS防护 |
| [COS 对象存储](/concepts/09-cos-storage.md) | 腾讯云COS SDK、服务端代理上传、类型/大小限制 |
| [审核与治理](/concepts/10-audit-governance.md) | 双状态审核机、三类审计日志、封禁闭环、管理后台 |
| [字典系统](/concepts/11-dictionary-system.md) | SysDict/SysDictItem动态分类、labelI18n多语言、字典复用 |
| [前端组件体系](/concepts/12-frontend-components.md) | shadcn/ui、Radix UI、CRUD通用组件、业务组件、粒子动效 |
| [作品提交流程](/concepts/13-form-submission.md) | 四步向导、StepIndicator、react-hook-form+zod校验 |
| [点赞与统计](/concepts/14-like-system.md) | WorkLike唯一约束、计数优化、toggle-like API、排行榜 |

### 运维

| 文档 | 内容 |
|------|------|
| [Docker 部署](/concepts/15-docker-deployment.md) | 三阶段Dockerfile、五服务compose编排、entrypoint初始化、Nginx |
| [测试体系](/concepts/16-testing.md) | Docker依赖测试、运行时测试、seed序列测试、部署配置测试 |

### 示例

| 文档 | 内容 |
|------|------|
| [开发环境搭建](/examples/setup-dev-environment.md) | 从clone到dev启动的完整流程 |
| [用户注册认证](/examples/user-registration-auth.md) | 注册API、NextAuth登录、Session获取、权限检查 |
| [作品提交](/examples/submit-work.md) | 四步表单填写、图片上传、富文本编辑、标签选择 |
| [管理员审核](/examples/admin-review.md) | 后台登录、审核通过/拒绝、荣誉授予、用户管理 |
| [字典管理](/examples/dictionary-management.md) | 查询字典、添加字典项、国家/城市/分类配置 |
| [COS 文件上传](/examples/cos-file-upload.md) | 服务端代理上传、文件删除、类型限制 |
| [Docker 部署](/examples/docker-deploy.md) | docker-compose配置、生产环境变量、Nginx配置 |
| [自定义 CRUD API](/examples/custom-crud-api.md) | 新增API路由的完整模式（schema+权限+校验+日志） |

### 参考信源

| 文档 | 内容 |
|------|------|
| [Demo Wall 源码信源](/references/demo-wall-source.md) | 源码核心文件路径索引（按模块分类） |

## 学习路径推荐

### 路径1：使用者（了解项目功能）

```
00-introduction → 01-getting-started → examples/setup-dev-environment
                         ↓
               浏览首页/注册登录/提交作品
                         ↓
               02-architecture-overview（建立全局认知）
```

### 路径2：开发者（理解架构并扩展功能）

```
00-introduction → 02-architecture-overview
                      ↓
        ┌─────────┬───┴───┬──────────┐
        ↓         ↓       ↓          ↓
     03-data   04-auth  05-i18n   06-api-routes
     -model    -system  -routing       ↓
        ↓         ↓       ↓     07-crud-layer
     11-dict    10-audit  12-components
        ↓         ↓
     13-submit  08-rich-text
        ↓         ↓
     14-like    09-cos
        ↓
  examples/custom-crud-api（动手扩展）
```

### 路径3：运维者（部署和维护）

```
00-introduction → 01-getting-started → 15-docker-deploy
                      ↓                    ↓
              examples/docker-deploy   16-testing
                      ↓
              10-audit-governance（日志/封禁/审核管理）
```

## 7 个核心洞察

1. **垂直分表的作品数据模型**：Work 五表分离（Base/Detail/Image/Team/Statistic），按读写频率和数据关系精准切分——列表只查 Base 避免加载大文本，高频计数独立于 Statistic 避免锁竞争，一对多图片自然分表。

2. **RBAC + 字典驱动的可配置分类**：root/admin/common 三角色硬编码保安全，SysDict/SysDictItem 字典表驱动分类配置——运营可动态增删分类/城市/荣誉/封禁名单/屏蔽域名，无需改代码发版；labelI18n 原生支持多语言标签。

3. **next-intl [language] 动态段国际化**：URL 前缀方案（/zh-CN/...），三层中间件链（auth→路由保护→i18n），双层 layout 支持 per-locale lang 属性，API 路由跳过 i18n 中间件。

4. **服务端/客户端三层数据访问分离**：Prisma（服务端直接查询+事务）→ zustand（命令式预填缓存实现秒开）→ react-query（声明式 staleTime=2min 自动同步），各司其职不越界。

5. **富文本 + COS 直传内容管线**：Tiptap 编辑器 → 服务端 sanitize-html 白名单净化（XSS 安全底线）→ COS 服务端代理上传（密钥不暴露）→ 事务五表原子写入 + 标签自动审核。

6. **Docker 三阶段构建 + 五服务编排**：base→builder→runner 极小镜像，app-init 独立迁移容器防并发冲突，docker-compose 编排 app/db/db-dev/redis/nginx，entrypoint.sh 支持初始化/启动双模式。

7. **双状态审核 + 三类审计日志治理闭环**：auditStatus（合规）+ displayStatus（可见）正交独立，WorkAuditLog 审核链 + SysAuthLog 认证日志 + SysOperationLog 操作日志全覆盖，封禁双重检查（authorize+jwt callback）形成完整闭环。

## 版本信息

- **项目版本**：0.0.0
- **Next.js 版本**：^15.3.3
- **React 版本**：^18.3.1
- **Prisma 版本**：5.10.2
- **NextAuth 版本**：^5.0.0-beta.30
- **支持语言**：zh-CN（默认）、en-US、ja-JP
- **文档生成日期**：2026-04-22
- **文档有效期至**：2026-10-22
- **许可证**：详见项目 LICENSE 文件

```{toctree}
:maxdepth: 7

concepts/00-introduction
concepts/01-getting-started
concepts/02-architecture-overview
concepts/03-data-model
concepts/04-auth-system
concepts/05-i18n-routing
concepts/06-api-routes
concepts/07-crud-layer
concepts/08-rich-text-editor
concepts/09-cos-storage
concepts/10-audit-governance
concepts/11-dictionary-system
concepts/12-frontend-components
concepts/13-form-submission
concepts/14-like-system
concepts/15-docker-deployment
concepts/16-testing
examples/admin-review
examples/cos-file-upload
examples/custom-crud-api
examples/dictionary-management
examples/docker-deploy
examples/setup-dev-environment
examples/submit-work
examples/user-registration-auth
references/demo-wall-source
spec/facts
spec/insights
```
