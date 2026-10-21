---
type: Concept
title: "video set：改 work 只需读-改-写，但会让已渲染 MP4 失效"
description: "vk video set 的 work 级旗标集合、字幕样式 10 旗标的读-改-写语义、preset 优先于单旗标的应用顺序、strokeWidth=0 与未设置的区分、export_invalidated 提示链"
tags: [vibeknow, cli, 字幕, 样式, work, export]
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

# video set：改 work 只需读-改-写，但会让已渲染 MP4 失效

> **事实编号**：F-073~F-080（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


`vk video set` 改的是「已经生成的视频」——换 BGM、开关字幕、调整字幕样式、改标题。这类修改不需要流水线重跑，因此**免费且立即生效**。但它有一个必须知道的后果：涉及 work 的改动会让已渲染的 MP4 失效。

## 旗标集合

| 类别 | 旗标 |
|---|---|
| work 级 | `bgm`、`bgm-volume`、`subtitle` |
| 字幕样式 | `subtitle-preset`、`subtitle-size`、`subtitle-color`、`subtitle-font`、`subtitle-font-weight`、`subtitle-bg-color`、`subtitle-bottom`、`subtitle-stroke-color`、`subtitle-stroke-width`、`subtitle-animation` |
| 例外 | `title`（不触及任何输出） |

**`--title` 不在 work 旗标集合里。** 它按 task 寻址，改的是名字，不改渲染结果，因此不使 MP4 失效。改名还排在所有 work 修改之前单独执行。

## 字幕样式是「读-改-写」

源码里有一行注释写得很直白：

```go
// Style is read-modify-write, never write-only.
style := figlens.ParseSubtitleStyle(work.SubtitleStyle)
```

后端**整体保存**字幕样式。所以如果只把字号写回去，字体、颜色、描边会一起被清掉——这是后端的数据形状决定的，不是 CLI 的选择。CLI 的做法是：先解析出既有样式对象，再逐字段覆盖本次真正给出的那几项。

十个样式字段：字体族、字号、字重、颜色、背景色、底部百分比、描边色、描边宽度、动画。

## preset 先落，单旗标后落

应用顺序固定：

```
preset.Patch.Apply(style)   →  再逐个单旗标覆盖
```

源码注释解释了为什么是这个顺序：「这个外观，但更大一点」是人们会说的话；「更大一点，但外观随便」不是。

也正因如此，官方文档与 Skill 都建议**优先用 `--subtitle-preset`**：可读性是组合而不是独立设置的若干项——描边款会同时清掉背景板，背景板款会同时关掉描边。单独设一半，命令照样退出 0，视频只是看起来不对，而没有任何机制会报告这件事。

preset 本身只触碰构成该外观的字段；字号、垂直位置等在 preset 之外单独设置。

## 「0」与「未设置」是两件事

`strokeWidth` 的取值范围是 0..12。**0 表示无描边**，而「未设置」表示交给渲染器默认。

样式合并用指针字段保留这个区别：命令行显式给了 `--subtitle-stroke-width 0`，写回去的就是 0；没给这个旗标，字段保持 nil，不会把既有的描边宽度清掉。

这个区别在展示时也要守住。`describeSubtitleStyle` 省略零值字段而不是打印 0，源码注释给的理由是：线上载荷本来就省略它们，渲染器把「缺失」读作自己的默认；打印 "strokeWidth = 0" 会声称一个并没有被存储的设置。

## 校验在网络之前

所有不需要联网的检查都在联网之前完成。源码注释写明理由：一个坏的数字不该花用户的钱，也不该因为在第一次写出去之后才被发现，而留下半套设置已经生效的状态。

需要联网解析的两个旗标也在任何写入之前解析：`--subtitle-preset` 与 `--subtitle-font`。两者都接受**显示索引**或**真实值**，解析失败时在本地拒绝并附上有效值列表，而不是让后端回一句「not allowed」而让人无从知道该填什么。

`on|off` 两值旗标（`--bgm`、`--subtitle`）用旗标名报错，指向要改的东西而不是线上的值。

## 「不可用」与「传错了」要分开

`classifySettingError` 把后端的两类 HTTP 400 分开：

| 后端回应 | 退出码 | 含义 |
|---|---|---|
| `not supported` / `not capable` / `unsupported` | 5 | 请求本身没问题，但这件事做不到——换任何输入都没用 |
| 其它 400 | 2 | 输入错了，改了再试 |

前者应当告诉用户而不是继续试值。

## export_invalidated：把后果说在前面

只要动了 work，渲染出的 MP4 就必须作废——改动被烘焙进了文件。预览和分享链接仍然可用，但下载在下次 `vk video export` 之前拿到的是旧文件。

CLI 因此在 JSON 载荷里带 `export_invalidated` 布尔量；为真时还附带 `next_actions`，第一条就是重新导出的命令。源码注释的理由：一个关了音乐的用户后来找不到文件，会没有任何办法把这两件事联系起来；不知道这件事的 Agent 也就无法提醒用户。

## 实践建议

1. **先 preset 后微调**：`--subtitle-preset` 打底，再单独改一项。
2. **改样式后记得重新导出**，并留意 `export_invalidated`。
3. **只改标题不会作废导出**，改 BGM 或字幕会。
4. **看到退出码 5 就是这件事做不到**，换参数没用。

## 相关概念

- [/concepts/03-output-and-events.md](/concepts/03-output-and-events.md) —— `applied` 与 `next_actions` 载荷
- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码 2 与 5 的分界
- [/concepts/04-run-ledger-and-async.md](/concepts/04-run-ledger-and-async.md) —— task_id 与 session_id 的寻址
- [/references/flag-inventory.md](/references/flag-inventory.md) —— 旗标全清单
