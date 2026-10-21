---
type: Concept
title: "预览产物：把本地产物交给调用方，把签名 URL 留在原地"
description: "--preview-dir 的落盘契约、cover_image/video_playback 两类资产、resource_ready 事件字段、按内容 sha256 去重、临时文件+rename 的原子写入、文件名 slug 消毒与源 URL 不入事件"
tags: [vibeknow, cli, preview, 产物落盘, 去重, 安全]
generated:
  by: trae-seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: "2027-04-21"
sources:
  - id: vksrc
    resource: https://github.com/vibeknow/cli
    title: "VibeKnow CLI 源码仓库 v0.9.2 @ 93a26eca"
  - id: flags
    resource: /references/flag-inventory.md
    title: "VibeKnow CLI 旗标清单"
---

# 预览产物：把本地产物交给调用方，把签名 URL 留在原地

> **事实编号**：F-043~F-045（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


`vk create` 早期只回一个 `share_url`——一个托管的 HTML 页面。人能打开它，**在终端里驱动 CLI 的 Agent 打开不了**。于是一个视频工具唯一值得看的产出，恰好是 Agent 唯一没法转交的产出。

`--preview-dir` 就是为这件事加的：把视觉产物写进调用方指定的目录，用一个事件宣告「这个路径上的文件已经完整了」。

## 契约

```
resource_ready 事件 = 一个绝对路径 + 一份已经写完的文件
```

| 字段 | 含义 |
|---|---|
| `type` | `resource_ready` |
| `asset_kind` | `cover_image` 或 `video_playback` |
| `session_id` | 产物所属的运行 |
| `local_path` | 绝对路径 |
| `bytes` | 文件大小（能取到时） |

另一类事件是 `resource_preview_warning`，带 `code`（`download_failed` / `resolve_failed`）与 `message`。`code` 是稳定令牌，消费方可以据此分支而不必解析消息文本。

## 刻意不包含的东西

**源资源的 URL 不进事件载荷。** 源码注释写明：那些 URL 是签名的、会过期的，一个把它们记进日志的 Agent 相当于发布了一份凭据。本地路径是调用方唯一需要的地址。

## 资产两类

| `asset_kind` | 是什么 |
|---|---|
| `cover_image` | 后端为预览渲染的静帧 |
| `video_playback` | 导出的 MP4 |

## 按内容去重，不按地址

去重依据是**内容的 sha256**，不是 URL，也不是时间戳。

源码注释给出原因：后端对未变化的资产也会签发全新的 URL——按地址判断会让同一张图在每次调用时被重新投递一遍。

被去重掉的产物**不重新宣告**。源码注释继续解释：一个本该可以安全重跑的命令，如果每次轮询都让 Agent 把同一张静帧给用户看两遍，那就没有意义了。

## 原子写入

下载先落到同目录的临时文件（`.preview-*.part`），比对新文件与目标文件的哈希：

- 相同 → 保留目标文件，丢弃临时文件，标记为「未变化」
- 不同 → **rename 最后执行**

`rename` 放在最后是有意的：在它成功之前，目标位置上始终是上一份完整的文件，所以读取该目录的调用方永远不会看到半截文件。

## 失败不使运行失败

`Deliver` **从不返回错误**。下载失败的预览是一个缺失的便利，而不是一次失败的运行——视频毕竟渲染好了。失败以 warning 事件上报，运行继续。

源码注释把这与产物的定位对齐：预览是复核的辅助，**永远不是结果的证据**。

同样地，`New` 传空目录时返回 `(nil, nil)`，之后所有方法都是空操作——没给 `--preview-dir` 的调用方不需要任何分支。

## 文件名消毒

文件名模板是 `<slug(session_id)>-<asset_kind><ext>`。

`slug` 把后端提供的 id 规整为单一路径分量里安全的字符：只保留字母、数字、`-`、`_`，其余替换为 `_`；结果为空时用 `run` 兜底；超过 64 字符则截断。

源码注释说得很直接：session_id 不是用户输入，但它也不是本进程的输入，而文件名模板里的 `../` 这种东西只需要成立一次。

扩展名从 URL 推断，先剥掉查询串与片段——签名 URL 带着它们，而 `.jpg?X-Amz-Signature=…` 不是扩展名。推断不出时按类型回落：`video_playback` → `.mp4`，`cover_image` → `.jpg`。

## 目录是调用方自己的

`--preview-dir` 允许绝对路径，目录以 `0o700` 创建。这与 `--dest` 不同——后者指名单个文件，且被限制在工作目录内的相对路径；前者指名的是调用方自己选的暂存目录，Agent 的临时目录是正常答案。

不被信任的不是这个目录，而是构成文件名的后端 id，所以消毒的是后者。

## 实践建议

1. **给 Agent 一个专用暂存目录**，`--preview-dir` 会把产物落在那里。
2. **只认 `resource_ready` 事件里的路径**，别去猜文件名。
3. **`resource_preview_warning` 出现不代表渲染失败**，视频可能已经好了。
4. **不要把分享链接当产物地址**，签名会过期。

## 相关概念

- [/concepts/03-output-and-events.md](/concepts/03-output-and-events.md) —— 事件通道与 `vk_event=` 前缀
- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— preview 通道在校验序列中的位置
- [/concepts/10-ai-skill-contract.md](/concepts/10-ai-skill-contract.md) —— Skill 对这些事件的消费纪律
- [/references/flag-inventory.md](/references/flag-inventory.md) —— 旗标全清单
