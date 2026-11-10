---
type: Reference
title: "MetaWeblog 接口与博客园约定"
description: "cnblogs-publish 使用的 MetaWeblog XML-RPC 端点、9 个方法签名、Post/FileData 结构，以及 blogid、[Markdown]、首页推荐、无后缀 URL 与审核语义。"
tags: ["cnblogs", "metaweblog", "xml-rpc", "api", "reference"]
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

# MetaWeblog 接口与博客园约定

本文件汇总 skill 自带的 `references/metaweblog-api.md`，并标注代码实际使用范围。接口属于博客园自述的 MetaWeblog 兼容层，协议为 XML-RPC 1.0，服务端类名 `BlogServer.Service.XmlRpc`。

## 端点与鉴权

| 项 | 值 |
|---|---|
| 端点 | `https://rpc.cnblogs.com/metaweblog/<博客名>` |
| 用户名 | 博客园**登录用户名**，不是昵称 |
| 密码字段 | 访问令牌（Access Token）；密码登录已取消 |
| 令牌获取 | 博客后台 → 设置 → 开放 API / 服务访问 |
| 传输限制 | 代码只允许 HTTPS；HTTP 仅放行 127.0.0.1 / localhost / ::1 |

`blogid` 固定传 `cnblogs`（不是博客名），博客名已在端点路径里；脚本默认 `blogid=cnblogs`，可用 `--blogid` 覆盖。

## 方法清单

仓库参考文献列出 9 个方法；代码实际调用其中 8 个（`wp.newCategory` 未使用）。

| 方法 | 参数（按顺序） | 返回 | 代码是否调用 |
|---|---|---|---|
| `blogger.getUsersBlogs` | blogid, username, token | BlogInfo 数组 | 是（setup/check） |
| `blogger.deletePost` | blogid, postid, username, token, publish(bool) | bool | 是（delete） |
| `metaWeblog.newPost` | blogid, username, token, Post, publish(bool) | postid 字符串 | 是（publish） |
| `metaWeblog.editPost` | postid, username, token, Post, publish(bool) | bool/any | 是（update） |
| `metaWeblog.getPost` | postid, username, token | Post | 是（get/update/delete/URL 回读） |
| `metaWeblog.getRecentPosts` | blogid, username, token, numberOfPosts | Post 数组 | 是（list） |
| `metaWeblog.getCategories` | blogid, username, token | CategoryInfo 数组 | 是（categories/分类校验） |
| `metaWeblog.newMediaObject` | blogid, username, token, FileData | `{url}` | 是（upload/图片替换） |
| `wp.newCategory` | blog_id, username, token, WpCategory | int | 否 |

## Post 结构

必填：`title`、`description`。脚本实际写入的字段：

| 字段 | 来源 |
|---|---|
| `title` | `--title` / frontmatter `title` / 正文首个 H1 |
| `description` | 正文；markdown 原样，html 经内置转换 |
| `categories` | `--categories` / frontmatter `categories`，markdown 模式自动补 `[Markdown]` |
| `mt_keywords` | `--tags` / frontmatter `tags` 或 `keywords`，逗号连接 |
| `wp_slug` | `--slug` / frontmatter `slug` |
| `mt_excerpt` | `--summary` / frontmatter `summary` 或 `excerpt` |

`dateCreated` 默认不传，由服务端取当前时间；`mt_convert_breaks`、`mt_text_more`、`link`、`permalink` 未使用。

## FileData 结构

```text
{ name: "a.png", type: "image/png", bits: <文件内容 base64 字符串> }
```

返回 `{ url: "https://img..../a.png" }`；脚本随后把正文中的本地图片引用替换为该 URL。

## 博客园四个关键约定

1. `blogid` 固定 `cnblogs`，博客名在端点路径中。
2. `[Markdown]` 是 Markdown 渲染开关，必须出现在 `categories` 中；它通常不出现在普通分类列表里。
3. `[发布至博客园首页]` 是首页推荐分类（分类 id 为 0），需显式加入才进入推荐流程，同样需要审核。
4. 规范文章地址无 `.html` 后缀：`https://www.cnblogs.com/<博客名>/p/<postid>`；带 `.html` 会 301 跳转。

## 审核与可见性语义

- 审核只针对**公开发布**；非公开（草稿/私有）不进入审核，可立即存储。
- `newPost` / `editPost` 成功只表示**已写入**；公开文章可能仍在人工审核，首页不可见或公开 URL 404 都不等于失败。
- MetaWeblog 的 Post 结构没有审核状态字段；不要轮询公开页面判断成败。
- 官方 OpenAPI 提供 `POST /openapi/v1/posts/reviewStatus:check`（0 待审核 / 1 通过 / 2 不通过），但需要 PAT，与本 skill 的 MetaWeblog 令牌不是同一套，当前未接入。

## 与官方 OpenAPI 的边界

| 通道 | 认证 | 能力 | 本 skill |
|---|---|---|---|
| MetaWeblog | 用户名 + 开放 API 访问令牌 | 发布/更新/读取/删除/分类/图床 | 使用 |
| OpenAPI | 账号中心 PAT（Bearer + Authorization-Type: pat） | `IsAigc`、`reviewStatus` 等 | 未接入 |

两套令牌不可混用；若需要官方 AI 标识或审核状态，应单独实现 OpenAPI 适配器。

## 相关文档

- [发布流水线](/concepts/04-publishing-pipeline.md)
- [可见性与审核](/concepts/05-visibility-and-review.md)
- [源码登记](/references/source-code.md)
