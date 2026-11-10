---
type: Example
title: "示例：维护文章、图片与本地预览"
description: "用 list/get/update/delete/upload/render 完成日常维护，重点说明 update 默认转非公开、删除需 --yes、图片上传的部分失败语义。"
tags: ["cnblogs", "example", "update", "delete", "upload", "preview"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
---

# 示例：维护文章、图片与本地预览

发布之后，日常操作主要是查、改、删和图片管理。这些命令共享同一套凭据与配置，不需要重复 `setup`。

## 1. 列出最近文章

```bash
python3 scripts/cnblogs.py list --count 20 --json
```

`--count` 会被限制在 1–100，默认 10。返回 `items` 数组，每项含 `postid`、`title`、`url`、`dateCreated`、`categories`。

## 2. 读取单篇

```bash
python3 scripts/cnblogs.py get 123456 --json
```

返回标题、URL、时间、分类、标签和完整 `description`。人类可读模式下正文会附在分隔线之后。

## 3. 更新文章

```bash
# 只想改内容，保持非公开（默认）
python3 scripts/cnblogs.py update 123456 posts/debug-notes.md --json

# 文章已公开，更新后仍要保持公开
python3 scripts/cnblogs.py update 123456 posts/debug-notes.md --publish --json
```

更新流程：

1. `getPost` 读取当前文章。
2. 新文件缺失的 `title`/`categories`/`tags`/`slug`/`summary` 从服务端回填。
3. 重新执行标题、分类、AI 声明、图片替换等准备步骤。
4. `editPost`；返回 `false` 视为失败（退出码 3）。
5. 再 `getPost` 获取 URL。

**关键风险**：默认非公开同样适用于 `update`。不加 `--publish` 更新一篇公开文章，会把它转为非公开。

## 4. 删除文章

```bash
python3 scripts/cnblogs.py delete 123456 --yes --json
```

`--yes` 是硬性要求，否则直接报参数错误。脚本会先 `getPost` 取标题用于回显，再调用 `blogger.deletePost(..., publish=true)`。删除不可撤销，执行前应获得用户明确同意。

## 5. 上传图片

```bash
python3 scripts/cnblogs.py upload cover.png diagram.svg --json
```

- 支持多文件；每个文件独立上传。
- 部分失败时仍返回成功，失败项进 `warnings`；全部失败才报错。
- 返回 `items: [{file, url}]`，可把 URL 手工写进文章，或让 `publish` 自动替换本地引用。

## 6. 本地预览

```bash
# 输出到终端
python3 scripts/cnblogs.py render posts/debug-notes.md

# 写入文件
python3 scripts/cnblogs.py render posts/debug-notes.md --out preview.html

# 取 JSON 中的 html 字段
python3 scripts/cnblogs.py render posts/debug-notes.md --json
```

`render` 不联网、不读凭据，使用与 `--format html` 相同的内置转换器。它适合检查 HTML 兜底效果；默认 markdown 发布路径由博客园渲染，不需要先转 HTML。

## 7. 清理凭据

```bash
# 只删系统凭据
python3 scripts/cnblogs.py forget

# 凭据 + 配置文件
python3 scripts/cnblogs.py forget --all
```

换账号、怀疑泄露或准备卸载时使用。删除后需要重新 `setup` 才能发布。

## 8. 命令选择速查

| 目标 | 命令 |
|---|---|
| 找旧文 | `list --count N --json` |
| 读全文 | `get <id> --json` |
| 改内容且保持公开 | `update <id> file.md --publish --json` |
| 改内容且保持私有 | `update <id> file.md --json` |
| 删文 | `delete <id> --yes --json` |
| 上传图 | `upload a.png b.jpg --json` |
| 本地看 HTML | `render file.md --out preview.html` |

## 相关概念

- [CLI 参考](/concepts/06-cli-reference.md)
- [发布流水线](/concepts/04-publishing-pipeline.md)
- [可见性与审核](/concepts/05-visibility-and-review.md)
