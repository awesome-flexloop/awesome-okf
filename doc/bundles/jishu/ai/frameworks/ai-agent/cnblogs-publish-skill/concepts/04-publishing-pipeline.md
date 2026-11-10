---
type: Concept
title: "发布流水线：从 Markdown 到 postid"
description: "cnblogs-publish 的一次发布如何解析 frontmatter、决定标题/分类/标签、处理 AI 声明与本地图片，并调用 MetaWeblog 返回可解析的 JSON。"
tags: ["cnblogs", "publish", "frontmatter", "markdown", "pipeline"]
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

# 发布流水线：从 Markdown 到 postid

一次 `publish` 在调用 RPC 之前，会先在本地完成全部可预期变换。理解这个顺序，才能解释"为什么标题被删了""为什么分类多了一个 `[Markdown]`""为什么图片上传失败但文章仍然发布"。

## 4.1 输入与编码

- 读取路径：`Path(file).expanduser()`；文件必须存在。
- 编码：`utf-8-sig`（自动去掉 BOM）。
- frontmatter：仅当第一行是 `---` 时解析，遇到下一个 `---` 或 `...` 结束。

frontmatter 解析器是行式的，支持：

```yaml
title: 文章标题
tags: [.NET, AI]
categories:
  - 随笔
  - 后端
draft: true
publish: false
format: markdown
upload_images: true
ai_generated: false
```

标量支持引号、行内列表、块列表、`true/yes/on`、`false/no/off`、`null/~`；键名统一转小写；**不支持嵌套 YAML**。

## 4.2 格式决策

```text
--format（默认 auto）
  → auto：frontmatter format → 配置 format → markdown
  → markdown：正文原样提交，自动追加 [Markdown]
  → html：正文经内置 md2html 转换，移除 [Markdown]
```

`--format html` 若检测到 `$$` 或管道表格，会追加 warning："内置简易转换器，数学公式/复杂表格可能需要人工检查"。

## 4.3 标题决策

| 优先级 | 来源 | 行为 |
|---|---|---|
| 1 | `--title` | 使用该值 |
| 2 | frontmatter `title` | 使用该值 |
| 3 | 正文首个非空行是 `# 标题` | 用 H1 文本作标题 |
| — | 以上都没有 | 报错，要求 frontmatter 或 `--title` |

默认会把用作标题的 H1 从正文移除；`--keep-h1` 保留正文 H1。更新时若新文件没有标题，会用服务端当前标题兜底。

## 4.4 分类与标签

- 切分：中英文逗号都接受（`re.split(r"[,，]")`）。
- 优先级：命令行 > frontmatter（`categories`；`tags` 或 `keywords`）> 空。
- markdown 模式：自动补 `[Markdown]`（大小写不敏感去重）。
- html 模式：移除 `[Markdown]`。
- 分类校验：若 `validate_categories=true`，先取服务端分类列表；不存在的分类只产生 warning，不阻塞发布。

## 4.5 AI 生成声明

默认在正文顶部插入：

```markdown
> **AI 生成声明**：本文内容由 AI 生成或经 AI 辅助完成，请注意甄别。
```

- 关闭：`--no-ai-generated` 或 frontmatter `ai_generated: false`。
- 若正文任意位置已含"AI 生成声明"，不重复插入。
- 这是**正文可见声明**，不是博客园平台的官方 AI 标识；MetaWeblog 的 Post 没有 `IsAigc` 字段。

## 4.6 本地图片

默认开启（`--no-upload-images` 关闭，frontmatter `upload_images` 可覆盖）。

| 语法 | 处理 |
|---|---|
| Markdown 图片语法（`![alt]` + 路径；路径可用尖括号包裹） | 解析路径，上传后替换为返回 URL |
| `<img src="path">` | 同上（HTML 模式） |
| `data:`、`#anchor`、带 scheme 的 URL | 不动 |
| 相对路径 | 相对文章所在目录解析 |
| 文件不存在 | 追加 warning，保留原引用 |
| 上传异常 | 追加 warning，保留原引用；不阻塞发布 |

同一路径在一次发布中只上传一次（按 `resolve()` 缓存）。上传调用 `metaWeblog.newMediaObject`，FileData 为 `{name,type,bits}`。

## 4.7 草稿决策

| 优先级 | 来源 | 结果 |
|---|---|---|
| 1 | `--draft` / `--private` | 非公开 |
| 1 | `--publish` / `--public` | 公开 |
| 2 | frontmatter `draft` | 按其布尔值 |
| 3 | frontmatter `publish: false` | 非公开 |
| 4 | 默认 | 非公开 |

`--draft` 与 `--publish` 互斥（argparse mutually exclusive group）。

## 4.8 提交与 URL

```text
newPost(blogid, username, token, post, publish=not draft)
  → postid
  → getPost(postid) 读取 link/permalink/url
  → 失败则拼 https://www.cnblogs.com/{blog}/p/{postid}
```

`postid` 会去掉可能的引号。`getPost` 失败只追加 warning（"链接为按博客名推测"），不影响发布结果。

## 4.9 输出契约

成功时 stdout 是单个 JSON（`--json`）或人类可读文本；两者来自同一 payload。

| 字段 | 含义 |
|---|---|
| `ok` | 成功为 true |
| `action` | `publish` / `update` / `get` / … |
| `postid` | 文章 ID（字符串） |
| `title` | 最终标题 |
| `url` | 公开文章地址（无 `.html`） |
| `draft` | 是否非公开 |
| `format` | `markdown` / `html` |
| `categories` / `tags` | 最终分类/标签 |
| `warnings` | 非致命问题列表 |
| `visibility` | `non_public` / `public` |
| `review_possible` | 是否可能进入人工审核 |
| `visibility_note` | 面向用户的可见性说明 |
| `ai_generated` | 是否启用 AI 声明 |
| `ai_declaration_added` | 本次是否实际插入 |

失败时输出 `{"ok": false, "error": "...", "code": N}`，错误文本已脱敏。

## 4.10 更新路径的差异

`update` 先 `getPost` 读取当前文章，再用新文件覆盖；缺失的 `title`/`categories`/`tags`/`slug`/`summary` 会从服务端回填。它同样默认非公开——**更新一篇已公开文章时若不加 `--publish`，会把它转为非公开**。这是使用 update 时最容易忽略的行为。

## 相关概念

- [可见性与审核](/concepts/05-visibility-and-review.md)
- [CLI 参考](/concepts/06-cli-reference.md)
- [MetaWeblog 接口与博客园约定](/references/api-and-conventions.md)
