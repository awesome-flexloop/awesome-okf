---
type: Concept
title: "CLI 参考：12 个命令与退出码"
description: "cnblogs-publish 全部子命令、公共与专用选项、JSON 输出契约和 0-5 退出码的速查表。"
tags: ["cnblogs", "cli", "reference", "commands", "exit-code"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
---

# CLI 参考：12 个命令与退出码

所有命令在 skill 根目录执行，入口为 `scripts/cnblogs.py`。`--help` 实测列出 12 个子命令。

## 6.1 命令总表

| 命令 | 位置参数 | 专用选项 | 作用 |
|---|---|---|---|
| `setup` | — | `--new-token`、`--reconfigure`、`--skip-check` | 在系统对话框录入并加密保存凭据 |
| `status` | — | — | 查看配置与凭据状态（不输出身份） |
| `check` | — | — | 调用 `getUsersBlogs` 验证鉴权 |
| `publish` | `file` | 见 6.3 | 新建文章（默认非公开） |
| `update` | `postid` `file` | 同 publish | 更新文章（默认非公开） |
| `get` | `postid` | — | 读取一篇文章 |
| `list` | — | `--count`（默认 10，范围 1–100） | 最近文章 |
| `delete` | `postid` | `--yes`（必须） | 删除文章 |
| `categories` | — | — | 列出分类 |
| `upload` | `files...` | — | 上传图片/文件到图床 |
| `render` | `file` | `--out` | 本地 Markdown→HTML 预览 |
| `forget` | — | `--all` | 删除系统凭据（可含配置文件） |

## 6.2 全局与公共选项

| 选项 | 作用域 | 说明 |
|---|---|---|
| `--config PATH` | 全局 | 配置文件路径，默认 skill 根目录 `config.json` |
| `--json` | 全部子命令 | 输出单个 JSON（供 Agent 解析） |
| `--blogid ID` | 全部子命令 | 覆盖配置的 `blogid`，默认 `cnblogs` |
| `--timeout SEC` | 全部子命令 | 覆盖网络超时，默认 30 秒 |

## 6.3 publish / update 选项

| 选项 | 说明 |
|---|---|
| `--title` | 标题（默认 frontmatter 或首个 H1） |
| `--tags` | 标签，逗号分隔 |
| `--categories` | 分类，逗号分隔 |
| `--slug` | `wp_slug` |
| `--summary` | 摘要 `mt_excerpt` |
| `--format {auto,markdown,html}` | 正文格式，默认 auto（优先 markdown） |
| `--keep-h1` | 保留正文首个 H1 |
| `--upload-images` / `--no-upload-images` | 上传本地图片并替换链接（默认开启） |
| `--ai-generated` / `--no-ai-generated` | 添加 AI 生成声明（默认开启） |
| `--draft` / `--private` | 非公开（默认） |
| `--publish` / `--public` | 公开发布（可能审核） |

`--draft` 与 `--publish` 互斥；更新命令的这两个选项同样互斥。

## 6.4 退出码

| 码 | 常量 | 含义 |
|---|---|---|
| 0 | `EXIT_OK` | 成功 |
| 1 | `EXIT_ERROR` | 未预期错误（`OSError` 或兜底异常） |
| 2 | `EXIT_USAGE` | 参数/配置/输入取消 |
| 3 | `EXIT_FAULT` | 博客园服务端拒绝（鉴权、分类、编辑失败等） |
| 4 | `EXIT_NETWORK` | 网络错误/超时 |
| 5 | `EXIT_SECRET_STORE` | 系统凭据库错误（沙箱、锁定、Linux 无 Secret Service） |

## 6.5 输出约定

- 成功：stdout 单个 JSON（`--json`）或人类可读文本；无 `--json` 时不打印 JSON。
- 失败：`--json` 时 stdout 为 `{"ok": false, "error": "...", "code": N}`；否则错误写到 stderr。
- 所有输出都已脱敏；不要期待在错误里看到原始令牌、用户名或端点。
- 发布/更新成功至少包含 `postid` 与 `url`；可见性字段见[可见性与审核](/concepts/05-visibility-and-review.md)。

## 6.6 典型调用

```bash
# 配置与自检
python3 scripts/cnblogs.py setup
python3 scripts/cnblogs.py status --json
python3 scripts/cnblogs.py check --json

# 发布（默认非公开）
python3 scripts/cnblogs.py publish post.md --json

# 公开发布并推荐首页
python3 scripts/cnblogs.py publish post.md --publish \
  --categories "[发布至博客园首页]" --json

# 维护
python3 scripts/cnblogs.py list --count 20 --json
python3 scripts/cnblogs.py get 123456 --json
python3 scripts/cnblogs.py update 123456 post.md --publish --json
python3 scripts/cnblogs.py delete 123456 --yes --json

# 图片与本地预览
python3 scripts/cnblogs.py upload cover.png --json
python3 scripts/cnblogs.py render post.md --out preview.html
```

Windows 上把 `python3` 换成 `python` 或 `py -3`。

## 相关概念

- [发布流水线](/concepts/04-publishing-pipeline.md)
- [示例：发布非公开草稿](/examples/01-publish-draft.md)
- [示例：维护文章与图片](/examples/03-manage-posts-and-images.md)
