---
type: Concept
title: "可见性与审核：发布成功不等于已公开"
description: "解释 cnblogs-publish 的默认非公开策略、公开发布的审核语义、首页推荐分类、AI 声明边界，以及为什么不能用首页或 404 判断失败。"
tags: ["cnblogs", "visibility", "review", "draft", "publication"]
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

# 可见性与审核：发布成功不等于已公开

这是该 skill 最容易被误判的语义：`newPost` 返回 `postid` 只代表**文章已写入博客园**；对公开发布而言，不代表已经对公众可见。

## 5.1 两种可见性

| 模式 | 触发 | 是否审核 | 公网可见 |
|---|---|---|---|
| 非公开（草稿/私有） | 默认；`--draft` / `--private`；frontmatter `draft: true` | 否 | 否，可立即安全保存 |
| 公开 | 显式 `--publish` / `--public` | 可能人工审核 | 审核通过后才可见 |

默认值是 `publish=false`。只有显式公开参数才把 `publish` 设为 true。

## 5.2 审核期间会发生什么

- 博客首页可能没有这篇文章。
- 公开 URL 可能返回 404，或仅作者可见。
- 审核结果由博客园后台决定；MetaWeblog 不提供审核状态查询。

因此：

1. 不要用浏览器或 `curl` 抓首页/文章页来"验证发布是否成功"。
2. 不要因为首页没有或公开页 404 就重复 `publish`——会产生重复文章。
3. 确认写入只用 `get <postid> --json`。
4. 公开发布时告诉用户"已提交，等待审核"；非公开时告诉用户"已保存，不会公开、无需审核"。

## 5.3 输出字段如何表达状态

| 字段 | 非公开 | 公开 |
|---|---|---|
| `draft` | true | false |
| `visibility` | `non_public` | `public` |
| `review_possible` | false | true |
| `visibility_note` | 提示已安全保存、无需审核 | 提示可能人工审核、勿重复发布 |

这些字段随发布/更新结果一起返回，Agent 应把它们转述给用户，而不是自行推断。

## 5.4 首页推荐

在分类中加入 `[发布至博客园首页]` 才会进入首页推荐流程：

```bash
python3 scripts/cnblogs.py publish post.md --publish \
  --categories "[发布至博客园首页]" --json
```

首页推荐同样需要审核；它不是"绕过审核"的开关。

## 5.5 更新已公开文章的风险

`update` 默认非公开。若文章原本公开，而更新时没有加 `--publish`，脚本会以 `publish=false` 调用 `editPost`，文章会转为非公开。这是默认安全策略的直接后果，不是 bug。更新公开文章时应显式：

```bash
python3 scripts/cnblogs.py update <postid> post.md --publish --json
```

## 5.6 AI 声明的边界

默认插入的"AI 生成声明"只是正文顶部的一段可见文字：

- 不设置博客园平台的官方 AI 标识；
- MetaWeblog 的 Post 没有 `IsAigc` 字段；
- 官方 OpenAPI 的 `IsAigc` 需要另一套 PAT，当前未接入；
- 正文已含"AI 生成声明"时不重复插入；
- 可用 `--no-ai-generated` 或 frontmatter `ai_generated: false` 关闭。

## 5.7 决策速查

| 目标 | 命令 |
|---|---|
| 先存下来，不公开 | `publish post.md --json`（默认） |
| 明确草稿/私有 | `publish post.md --draft --json` 或 `--private` |
| 公开发布 | `publish post.md --publish --json` |
| 公开并推荐首页 | `publish post.md --publish --categories "[发布至博客园首页]" --json` |
| 更新并保持公开 | `update <id> post.md --publish --json` |
| 确认写入 | `get <id> --json` |

## 相关概念

- [发布流水线](/concepts/04-publishing-pipeline.md)
- [CLI 参考](/concepts/06-cli-reference.md)
- [MetaWeblog 接口与博客园约定](/references/api-and-conventions.md)
