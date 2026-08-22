---
type: Concept
title: 富文本编辑器
description: Demo Wall 的 Tiptap 富文本编辑器配置，Link/Underline/Placeholder 扩展，sanitize-html XSS 防护白名单，编辑器组件集成。
tags: [demo-wall, tiptap, rich-text, sanitize, xss]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## Tiptap 编辑器配置

作品内容编辑使用 Tiptap 编辑器（@tiptap/react ^3.20.4），编辑器组件位于 `src/app/[language]/submit/editor/RichTextEditor.tsx`（F-007, F-019）。

### 启用的扩展（F-007）

- `@tiptap/starter-kit`：基础扩展集（粗体/斜体/标题/列表等）
- `@tiptap/extension-link`：超链接支持
- `@tiptap/extension-underline`：下划线
- `@tiptap/extension-placeholder`：占位符提示

## XSS 防护：sanitize-html（F-104）

富文本安全是重中之重。`src/lib/rich-text.ts` 配置了严格的白名单：

### RICH_TEXT_SANITIZE_OPTIONS 白名单

**允许的 HTML 标签**：
`p, br, strong, em, u, s, h2, h3, ul, ol, li, a, blockquote, code`

**允许的属性**：
- `a` 标签：`href`, `target`, `rel`

**允许的协议**（a 标签 href）：
`http`, `https`, `mailto`

**明确禁止**：
- 不允许 `script`, `iframe`, `img`, `video`, `style` 等危险标签
- 不允许 `javascript:` 协议（XSS 主要入口）
- 不允许 `onclick`/`onload` 等事件属性

### 导出函数

- `stripHtmlTags(html)`：正则去除所有 HTML 标签，返回纯文本（用于字数统计等场景）
- `sanitizeRichText(html)`：使用 sanitize-html 按白名单净化 HTML

### 服务端 sanitize 是安全底线

前端 sanitize 可以被绕过（直接发 HTTP 请求），因此**服务端 sanitize 是必须的**。作品提交（F-079）和更新（F-071）时都在服务端对 story 字段调用 `sanitizeRichText()` 净化。

## 编辑器集成

RichTextEditor 组件在 Step3Content（内容介绍步骤）中使用（F-019），用于编辑 story 字段。表单通过 react-hook-form 的 Controller 集成 Tiptap 编辑器。

## 内容展示安全

作品详情 API（GET /api/works/[id]）返回 story 字段时，再次对 HTML 进行 sanitize 处理（F-072），确保即使数据库中存在恶意内容（如绕过了之前的 sanitize），展示时也会被净化。

## 扩展富文本能力

若需新增富文本格式（如表格、图片内嵌），需要：
1. 安装对应的 Tiptap 扩展
2. 在 RichTextEditor 组件中注册扩展
3. **同步更新** `RICH_TEXT_SANITIZE_OPTIONS` 白名单，添加允许的标签和属性
4. 考虑前端实时预览和服务端 sanitize 的一致性

## 相关概念

- [作品提交流程](/concepts/13-form-submission.md)
- [CRUD 数据层](/concepts/07-crud-layer.md)
- [API 路由设计](/concepts/06-api-routes.md)
