---
type: Example
title: "示例：公开发布与首页推荐"
description: "显式公开发布、加入 [发布至博客园首页] 分类、理解审核等待与正确确认方式；含分类覆盖的副作用。"
tags: ["cnblogs", "example", "publish", "public", "review", "homepage"]
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

# 示例：公开发布与首页推荐

公开发布是显式动作，且可能进入人工审核。本示例演示两种常见组合，以及如何避免"看到 404 就重复发布"。

## 1. 公开发布

```bash
python3 scripts/cnblogs.py publish posts/debug-notes.md --publish --json
```

与默认路径的差异：

| 字段 | 非公开 | 公开 |
|---|---|---|
| `draft` | true | false |
| `visibility` | `non_public` | `public` |
| `review_possible` | false | true |
| `visibility_note` | 已保存、无需审核 | 已提交、可能人工审核 |

`newPost` 成功只表示写入；审核通过前首页可能没有、公开 URL 可能 404。

## 2. 公开发布并推荐首页

```bash
python3 scripts/cnblogs.py publish posts/debug-notes.md --publish \
  --categories "[发布至博客园首页]" --json
```

注意：命令行 `--categories` 会**覆盖** frontmatter 的 `categories`，而不是追加。最终分类只有 `[发布至博客园首页]` 和自动补的 `[Markdown]`。如果还想保留原分类，需要显式写全：

```bash
--categories "[发布至博客园首页],[随笔],[后端]"
```

首页推荐分类的 id 为 0；加入后文章进入首页推荐流程，同样需要审核。

## 3. 预期输出（节选）

```json
{
  "ok": true,
  "action": "publish",
  "postid": "123457",
  "url": "https://www.cnblogs.com/<博客名>/p/123457",
  "draft": false,
  "visibility": "public",
  "review_possible": true,
  "visibility_note": "博客园可能对公开博文进行人工审核；审核通过前文章可能不会出现在首页或公网……",
  "categories": ["[发布至博客园首页]", "[Markdown]"]
}
```

## 4. 审核期间的正确动作

1. 把 `postid`、`url`、`visibility_note` 转述给用户，说明"已提交，等待审核"。
2. 需要确认时只调用 `get <postid> --json`，检查 API 侧记录。
3. 不要抓首页、不要测公开 URL、不要重复 `publish`。
4. 审核结果由博客园后台决定；MetaWeblog 不提供审核状态查询。

## 5. 从草稿升级为公开

如果先发了草稿，后来想公开，用 `update` 并显式 `--publish`：

```bash
python3 scripts/cnblogs.py update 123456 posts/debug-notes.md --publish --json
```

不要重新 `publish`——那会创建第二篇文章。

## 6. 失败与误判对照

| 现象 | 是否失败 | 处理 |
|---|---|---|
| 返回 `postid`，首页没有 | 否 | 等待审核 |
| 公开 URL 404 | 否 | 等待审核；用 `get` 确认 |
| `code: 3` | 是 | 服务端拒绝，检查鉴权/分类 |
| 分类 warning | 否 | 分类不存在，先创建或改名 |
| `getPost` 失败但有 `postid` | 否 | URL 为推测值，文章已写入 |

## 相关概念

- [可见性与审核](/concepts/05-visibility-and-review.md)
- [示例：发布非公开草稿](/examples/01-publish-draft.md)
- [MetaWeblog 接口与博客园约定](/references/api-and-conventions.md)
