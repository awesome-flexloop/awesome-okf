---
type: Concept
title: TypeScript 摄取与渲染器
description: Papyri viewer 的 TypeScript 摄取器（ingest）和 Astro 渲染端——处理 CBOR bundle、GraphStore 持久化、HTML 渲染
tags: [papyri, typescript, viewer, ingest, astro, cbor]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: viewer-src
    resource: /references/viewer-source.md
    title: Papyri TypeScript 摄取器与查看器源码信源
---

## Viewer 架构

Viewer 是 Papyri 的 TypeScript/Astro 端，负责：

1. **摄取（Ingest）**：接收 `.papyri` CBOR 制品，解码并存入 GraphStore
2. **API 服务**：提供 HTTP API 供前端查询文档、搜索、获取后向引用
3. **HTML 渲染**：使用 Astro 服务端渲染文档页面
4. **认证管理**：上传认证、管理员面板

### 技术栈

- **框架**：Astro（服务端渲染 + 静态页面）
- **数据库**：better-sqlite3（同步 SQLite 绑定，高性能）
- **CBOR**：cbor-x（高速 CBOR 编解码，支持 tag）
- **构建**：pnpm monorepo（workspaces）

### 目录结构

```
papyri/ts/
├── ingest/        # TypeScript 摄取器
│   ├── index.ts   # ingest 入口、relink pass
│   ├── visitor.ts # IR visitor 后处理
│   ├── graph.ts   # 图数据库操作（对应 Python graph_store.py）
│   ├── blob.ts    # BlobStore 实现
│   └── nodes.ts   # IR 节点 TS 类型定义与 CBOR 编解码
├── viewer/        # Astro 网站
│   ├── src/
│   │   ├── pages/       # Astro 页面路由
│   │   ├── components/  # UI 组件
│   │   ├── layouts/     # 页面布局
│   │   └── lib/         # 工具函数
│   └── astro.config.mjs
└── package.json
```

## 摄取流程（TypeScript ingest）

`ingest/index.ts` 中的摄取流程：

1. **接收 PUT 请求**：API route `/api/bundle` 接收 `.papyri` 文件（CBOR + gzip）
2. **解压**：gzip 解压得到 CBOR 字节
3. **CBOR 解码**：使用 cbor-x 解码为 Bundle 对象（包含 CBOR tag 映射）
4. **Blob 存储**：每个子文档的 IR CBOR blob 存到 BlobStore（SHA256 寻址）
5. **插入 nodes**：写入 SQLite `nodes` 表
6. **Relink pass**：遍历所有 IR，解析 kind="to-resolve" 的 CrossRef
7. **建立 backrefs**：填充 `backrefs` 表
8. **全文索引**：提取文本到 `search` FTS5 表
9. **版本管理**：更新 `versions` 表，设置默认版本

### Relink Pass

Relink pass 是跨包引用解析的关键步骤：

1. 遍历所有已摄取包的所有 IR 节点
2. 查找所有 `RefInfo(kind="to-resolve")` 的 CrossRef
3. 在 GraphStore 中查找匹配的目标（按 module + path 匹配）
4. 找到目标 → 更新 RefInfo 字段，blob 重写
5. 找不到 → kind 改为 "missing"
6. 同时在 backrefs 表建立反向链接

新 bundle 摄取后会触发全量 relink（对已存在的 to-resolve 引用重新尝试解析）。

### CBOR 标签注册

TypeScript 端同样维护 CBOR tag → 节点类型的映射，对应 Python 端的 `REV_TAG_MAP`。每个 Node 类实现：

- `toCBOR()` / `fromCBOR()`：序列化/反序列化
- 静态 `cborTag` 属性：分配的 CBOR tag 号

## 渲染流程

### 页面路由

Viewer 使用 Astro 的文件系统路由：

| 路由 | 页面 |
|------|------|
| `/` | 首页/包列表 |
| `/<package>/` | 包概览页（最新版本） |
| `/<package>/<version>/api/<path>` | API 文档页 |
| `/<package>/<version>/docs/<path>` | 叙述文档页 |
| `/<package>/<version>/examples/<path>` | 示例页 |
| `/search?q=<query>` | 搜索结果页 |
| `/api/bundle` | Bundle 上传 API（PUT） |
| `/api/search` | 搜索 API |
| `/admin` | 管理面板 |

### IR 渲染组件

`viewer/src/components/` 中的组件递归渲染 IR 节点：

- `<Node node={irNode} />`：通用节点渲染分发器
- `<Section section={...} />`：章节渲染
- `<Paragraph node={...} />`：段落
- `<CodeBlock node={...} />`：代码块（含语法高亮和执行结果）
- `<CrossRef link={...} />`：交叉引用链接
- `<Admonition node={...} />`：提示框
- `<TableNode node={...} />`：表格
- `<ParametersSection node={...} />`：参数列表
- `<SignatureNode node={...} />`：函数签名

### Debug 节点视觉区分

标记为 `@debug` 的节点类型（如 `InlineRole`、`InlineBlock`、`SubstitutionRef`、`Comment`、`Targets`、`UnprocessedDirective`、`InlineTarget`）在渲染时有特殊的视觉标记（如边框、颜色），帮助开发者识别尚未完全处理的 IR 节点。

## 认证与安全

Viewer 包含基础的认证系统：

- **上传认证**：`PAPYRI_UPLOAD_TOKEN` 或 admin 用户认证
- **管理员账户**：通过 `PAPYRI_USERNAME`/`PAPYRI_PASSWORD` 环境变量种子化首个管理员
- **认证数据库**：`~/.papyri/auth.db`（SQLite）
- **Bundle 上传限制**：默认 50MB

## 开发模式

```bash
cd ts
pnpm install
pnpm dev  # 启动 Astro 开发服务器（默认 http://localhost:4321）
```

开发模式下（`PAPYRI_DEV_SEED=1`）：
- 自动种子化 admin/password 账户
- 启用热重载
- 详细错误信息

## 相关概念

- [架构总览](02-architecture-overview.md)
- [GraphStore 与交叉链接](09-graphstore-and-crosslinks.md)
- [pack 与 upload](08-pack-and-upload.md)
- [限定名与交叉引用](06-qualified-names.md)
