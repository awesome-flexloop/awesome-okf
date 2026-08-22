---
type: Reference
title: Papyri TypeScript 摄取器与查看器源码信源
description: Papyri TypeScript ingest/ 摄取引擎和 viewer/ Astro Web 渲染器源码索引
tags: [papyri, typescript, ingest, viewer, astro]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-repo
    resource: https://github.com/carreau/papyri
    title: Papyri GitHub Repository
---

## TypeScript 端源码索引

### Ingest 摄取引擎（ingest/）

源码路径：`external/libs/jupyter/papyri/ingest/src/`

| 文件 | 职责 |
|------|------|
| `index.ts` | 公共 API 导出 |
| `ingest.ts` | Ingester 类——将 Bundle 写入 blob store + graph DB |
| `encoder.ts` | CBOR 编解码、IR 节点 TypeScript 类型定义 |
| `visitor.ts` | 前向引用收集器（遍历 IR 节点） |
| `bundle.ts` | Bundle Node 验证（assertBundle） |
| `keys.ts` | Key 元组 (module/version/kind/path) + keyStr 序列化 |
| `graph-db.ts` | GraphDb 接口 + SqliteGraphDb 实现 |
| `blob-store.ts` | BlobStore 接口 + FsBlobStore 实现（文件系统 blob 存储） |
| `raw-store.ts` | RawStore 接口 + FsRawStore 实现（原始 .papyri.gz 归档） |
| `inventory.ts` | Intersphinx objects.inv 解析器（链接到非 papyri 项目） |
| `fs-safe.ts` | 文件系统安全路径处理 |
| `url-safety.ts` | URL 安全校验（阻止 javascript:/data: 等 XSS 向量） |

**数据库迁移**：`ingest/migrations/` 目录包含 SQL schema 迁移文件（0001_init.sql ~ 0005_bundle_content_hash.sql）。

### Viewer Web 渲染器（viewer/）

源码路径：`external/libs/jupyter/papyri/viewer/src/`

**技术栈**：Astro + React islands + TypeScript，`@astrojs/node` 适配器，server output 模式。

#### 核心库（lib/）

| 文件 | 职责 |
|------|------|
| `ir-reader.ts` | Blob → 类型化 IR 解码器（IR 变更的"减震器"） |
| `ir-types.ts` | 与 IR 节点形状镜像的 TypeScript 类型 |
| `ir-schema.ts` | 自动生成的 IR 字段/类型 schema（驱动 IR-stats 面板） |
| `backends.ts` | getBackends() —— 按适配器构建 BlobStore + GraphDb |
| `graph.ts` | 图查询（getBackrefs/getForwardRefs 等） |
| `bundle-walk.ts` | Bundle 遍历共享工具（walkBundle/walkAllBundles） |
| `nav.ts` | 导航/TOC 辅助 |
| `qualname-page.ts` | 限定名页面视图模型 |
| `qualname.ts` | 限定名解析/规范化 |
| `doc-page.ts` | 叙述文档页面视图模型 |
| `image-index.ts` | 图片索引构建 |
| `xref.ts` | 交叉引用解析 |
| `render-node.ts` | IR 节点 → HTML 字符串辅助 |
| `highlight.ts` | Shiki 语法高亮 |
| `math.ts` | KaTeX 数学公式渲染 |
| `search.ts` | 单 Bundle 搜索索引 |
| `paths.ts` | 路径发现、环境变量覆盖 |
| `links.ts` | 链接辅助 |
| `slugs.ts` | URL slug 工具 |
| `auth.ts` | 认证辅助（passkey/password/session） |
| `api-utils.ts` | API 响应辅助 |
| `version-utils.ts` | PEP 440 版本比较 |
| `theme.ts` | 主题检测 |
| `visibility.ts` | 可见性切换状态 |
| `signature.ts` | 签名渲染辅助 |

#### 页面路由（pages/）

| 路由 | 文件 | 说明 |
|------|------|------|
| `/` | `index.astro` | Bundle 列表（首页） |
| `/login` | `login.astro` | 登录页面 |
| `/settings` | `settings.astro` | 用户设置 |
| `/project/[pkg]/[ver]/` | `project/[pkg]/[ver]/index.astro` | Bundle 概览 |
| `/project/[pkg]/[ver]/[...slug]` | `project/[pkg]/[ver]/[...slug].astro` | 限定名文档页面 |
| `/project/[pkg]/[ver]/docs/[...doc]` | `project/[pkg]/[ver]/docs/[...doc].astro` | 叙述文档页面 |
| `/project/[pkg]/[ver]/examples/[...ex]` | `project/[pkg]/[ver]/examples/[...ex].astro` | 示例页面 |
| `/project/[pkg]/[ver]/nodes/` | `project/[pkg]/[ver]/nodes/` | IR 节点浏览器 |
| `/project/[pkg]/[ver]/text-search/` | `project/[pkg]/[ver]/text-search/` | 全文搜索 |
| `/api/bundle` | `api/bundle.ts` | PUT 上传端点（触发 ingest） |
| `/api/bundles.json` | `api/bundles.json.ts` | Bundle 列表 JSON |
| `/api/reingest` | `api/reingest.ts` | POST 重新摄取原始归档 |
| `/api/inventory` | `api/inventory.ts` | Intersphinx 清单管理 |
| `/api/search.json` | `api/search.json.ts` | 跨 Bundle 搜索 |
| `/admin/*` | `admin/` | 管理面板（认证保护） |
| `/api/auth/*` | `api/auth/` | 认证端点（login/logout/passkey） |

### 存储架构

- **Blob Store**：文件系统，每个文档以 CBOR blob 存储，key 为 (package, version, category, identifier)
- **Graph DB**：SQLite（`~/.papyri/ingest/papyri.db`），跟踪文档存在性和前向/后向引用边
- **Raw Store**：原始 `.papyri.gz` 归档存储在 `_raw/<pkg>/<ver>.papyri.gz`，是唯一权威 IR
- 图数据库和 blob store 均可通过 `POST /api/reingest` 从 raw store 重建

### 认证系统

- 全局上传令牌（CI/本地开发）
- 用户级项目范围令牌（`papyri_pat_` 前缀，在 `/settings` 生成）
- Passkey（WebAuthn）认证支持
- 基于 session 的 Web 认证 + 中间件
