---
type: Concept
title: CRUD 数据层
description: Demo Wall 的三层数据访问架构：通用 CRUD 函数、zustand 客户端缓存、react-query 服务端状态同步、乐观更新与预填缓存。
tags: [demo-wall, crud, zustand, react-query, data-layer]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 三层数据访问架构

数据访问层明确分为三层（F-098, F-107, F-109, F-119）：

1. **服务端数据层**（Prisma Client）：Server Component 和 Route Handler 直接查询数据库
2. **客户端命令式缓存**（zustand）：useWorksStore 提供 Map 缓存，命令式操作
3. **客户端声明式同步**（react-query）：useWorks Hook 封装 useQuery，自动管理缓存

## Prisma 单例（F-098）

`src/lib/prisma.ts` 导出 prisma 单例实例：

- 使用 `globalThis` 缓存避免开发环境热重载创建多个数据库连接
- 开发环境日志级别：`['query', 'error', 'warn']`
- 生产环境日志级别：`['error']`

## CRUD 常量工具（F-100）

`src/lib/crud.ts` 导出：

- `CRUD_QUERY_PARAMS`：通用查询参数常量（page、pageSize、query、filter）
- `DICT_FILTERS`：字典筛选选项（all/system/custom）
- `TAG_FILTERS`：标签筛选选项（all/auto/manual）
- `normalizeFilter()`：规范化筛选参数

## zustand Store（F-107）

`src/lib/works-store.ts` 导出 `useWorksStore`：

**状态**：
- `listCache: Map<string, ListCacheEntry>`：作品列表缓存，key 为序列化查询参数字符串
- `detailCache: Map<string, Work>`：作品详情缓存

**ListCacheEntry 结构**：items、total、totalPages

**方法**：
- `setListCache(key, entry)`：设置列表缓存
- `setDetailCache(id, work)`：设置详情缓存（列表点击时预填，实现"秒开"）
- `getDetailCache(id)`：获取详情缓存

zustand 的命令式缓存与 react-query 的声明式缓存互补：react-query 随组件挂载/卸载自动管理，而 zustand 支持在列表页点击作品卡片时调用 setDetailCache 预填详情数据，避免跳转后的 loading 闪烁。

## React Query Hook（F-109）

`src/lib/use-works.ts` 导出 `useWorks(params)` Hook：

- 使用 `useQuery`，queryKey 为 `['works', params]`
- 请求 `GET /api/works?{params}`
- `staleTime: 2 分钟`：2分钟内切换筛选条件不会重复请求，后台刷新保证最终一致性

**WorksParams 接口**：page、pageSize、search、sort、lang、city、country、category、tags、date、honor

## 反馈 Hook（F-108）

`src/lib/use-feedback.ts` 导出 `useFeedback(timeout=2500)` Hook：

- 返回 `{ feedback, showFeedback }`
- `showFeedback(type, message)` 设置反馈状态并在 timeout 毫秒后自动清除
- 用于 CRUD 操作后的成功/错误提示

## 表单校验层（F-105）

`src/lib/work-form.ts` 导出：

- `WorkFormValues` 接口
- `buildWorkFormSchema(t, options)` 函数：接收翻译函数 t 和选项对象，返回 zod 校验 schema

主要校验规则：
- name：2-50 字符
- intro：10-100 字符
- country/city/category/devStatus：必填
- tags：1-5 个
- coverUrl：必填
- story：纯文本 20-2000 字符（HTML 经 stripHtmlTags 后计算）
- highlights：1-5 个，每个 1-30 字符
- scenarios：至少 1 个，每个 1-100 字符
- screenshots：1-5 个
- demoUrl/repoUrl：合法 URL 或空字符串
- team：至少 1 人，每人 1-20 字符
- teamIntro：1-500 字符（requireTeamIntro 选项控制）
- contactPhone：最多 20 字符
- contactEmail：合法邮箱或空字符串

## Provider 嵌套顺序（F-118）

QueryProvider（React Query ClientProvider）必须包裹在 SessionProvider 内、SiteLayout 外，确保所有子组件可使用 useQuery。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [API 路由设计](06-api-routes.md)
- [富文本编辑器](08-rich-text-editor.md)
- [作品提交流程](13-form-submission.md)
- [前端组件体系](12-frontend-components.md)
