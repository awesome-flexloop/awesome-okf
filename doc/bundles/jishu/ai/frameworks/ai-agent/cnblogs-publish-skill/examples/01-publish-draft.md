---
type: Example
title: "示例：发布一篇非公开草稿"
description: "从带 frontmatter 的 Markdown 到默认非公开发布的完整命令、输出字段与验证步骤，含标题/分类/标签/AI 声明的实际效果。"
tags: ["cnblogs", "example", "publish", "draft", "frontmatter"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/api-and-conventions.md"
    type: "repository-docs"
    trust: high
---

# 示例：发布一篇非公开草稿

本示例演示最常见的安全路径：先把文章存成非公开，确认无误后再决定是否公开。执行前需完成[首次配置](/concepts/03-credentials-setup.md)。

## 1. 准备文章

创建 `posts/debug-notes.md`：

```markdown
---
title: 一次超时排查的完整记录
tags: [排障, 网络]
categories: [随笔, 后端]
summary: 从现象到根因的排查路径
---

# 一次超时排查的完整记录

## 现象

请求在 30 秒后超时。

## 排查

1. 复现并记录时间点。
2. 对比客户端与服务端超时配置。
```

## 2. 发布（默认非公开）

```bash
python3 scripts/cnblogs.py publish posts/debug-notes.md --json
```

等价于显式 `--draft` 或 `--private`。脚本会：

1. 读取 frontmatter，标题取 `title`，不会重复使用正文 H1（默认移除正文 H1）。
2. 分类变为 `[随笔, 后端, [Markdown]]`（自动追加渲染开关）。
3. 正文顶部插入 AI 生成声明（若尚未存在）。
4. 调用 `newPost(..., publish=false)`，再 `getPost` 获取链接。
5. 返回 JSON。

## 3. 预期输出

```json
{
  "ok": true,
  "action": "publish",
  "postid": "123456",
  "title": "一次超时排查的完整记录",
  "url": "https://www.cnblogs.com/<博客名>/p/123456",
  "draft": true,
  "format": "markdown",
  "categories": ["随笔", "后端", "[Markdown]"],
  "tags": ["排障", "网络"],
  "warnings": [],
  "visibility": "non_public",
  "review_possible": false,
  "visibility_note": "这是非公开发布（草稿/私有），不进入审核，可立即安全保存……",
  "ai_generated": true,
  "ai_declaration_added": true
}
```

`<博客名>` 是公开博客名；输出中没有用户名或令牌。

## 4. 验证写入

```bash
python3 scripts/cnblogs.py get 123456 --json
```

`get` 能读回标题/分类/正文即表示 API 侧已保存。非公开文章不需要等待审核，也不要去首页查找。

## 5. 常见偏差

| 现象 | 原因 | 处理 |
|---|---|---|
| 正文开头多了一段 AI 声明 | 默认开启 | 需要关闭时加 `--no-ai-generated` |
| 分类里多出 `[Markdown]` | markdown 模式自动追加 | 保留；这是渲染开关 |
| 标题重复 | 使用了 `--keep-h1` 且 frontmatter 也有 title | 去掉 `--keep-h1` 或删 frontmatter title |
| 图片仍是本地路径 | 文件不存在或上传失败 | 查看 `warnings`，修正路径 |
| 分类 warning | 分类未在博客后台创建 | 先建分类或改用已有分类 |

## 相关概念

- [发布流水线](/concepts/04-publishing-pipeline.md)
- [可见性与审核](/concepts/05-visibility-and-review.md)
- [示例：公开发布与首页推荐](/examples/02-publish-public-homepage.md)
