---
type: Example
title: "实操三：把风格固定下来，把改动收窄"
description: "用 preset 复用外观参数、用 video set 免费改 BGM 与字幕、用 video edit 重写单镜头旁白（计费）、用 kb prune 与 jobs prune 安全清理的完整范式"
tags: [vibeknow, cli, preset, 字幕, 改稿, 清理, 维护]
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
  - id: preset
    resource: /concepts/06-preset-contract.md
    title: "preset 契约"
---

# 实操三：把风格固定下来，把改动收窄

> 本文命令与行为均来自 v0.9.2 源码（commit `93a26eca`）。**本文作者未实机执行**；涉及计费的步骤请以测试账号实测为准。

视频做出来之后要改，是常态。这份实操讲三件事：**把外观参数固化**（preset）、**把免费的小改动做完**（`video set`）、**把要花钱的改动限定到一个镜头**（`video edit`），最后是清理。

## 一、preset：把外观参数固化下来

### 找到候选值

```bash
vibeknow theme list --mode image     # 可用的视觉主题
vibeknow voice list --language zh-CN # 音色模板 + 自己的克隆音色
vibeknow subtitle presets             # 现成的字幕外观
vibeknow subtitle fonts               # 可用的字体族
```

### 写一个 preset

preset 放在 `<config-dir>/presets/` 下。`<config-dir>` 的解析顺序是：

```
VIBEKNOW_CONFIG_HOME  >  %AppData%/vibeknow (Windows)  >  $XDG_CONFIG_HOME/vibeknow  >  ~/.config/vibeknow
```

目录不会被自动创建，要自己建：

```yaml
# <config-dir>/presets/knowledge-short.yaml
schema_version: "1"
name: knowledge-short
description: "竖屏图文讲解"
create:
  mode: image
  aspect: vertical
  language: zh-CN
  bgm: off
  theme: <从 theme list 抄下来的真实值>
```

### 用它

```bash
vibeknow create --from ./doc.pdf --preset knowledge-short --output json
```

### 四条边界

| 边界 | 说明 |
|---|---|
| **命令行永远赢** | preset 只提供默认值；你显式给过的旗标不被覆盖 |
| **授权类参数进不去** | `export` / `yes` / `confirm` 会被拒，并告诉你「请写在命令行」 |
| **单次调用类参数进不去** | `from` / `text` / `kb-id` / `async` / `preview-dir` / `output` 会被拒 |
| **没有 `vk preset list`** | 名字写错时错误信息会附上可用名称列表 |

键名可以用下划线或连字符（`avatar_position` = `avatar-position`）。`schema_version` 只接受 `"1"`；顶层键拼错会被 `KnownFields(true)` 拒读——一个拼错的键会让 preset 静默什么都不做。

preset 展开失败一律是退出码 2，且发生在任何上传之前。

## 二、video set：免费的小改动

```bash
# 换 BGM
vibeknow video set 42 --bgm on
vibeknow video set 42 --bgm-volume 0.6

# 开关字幕
vibeknow video set 42 --subtitle on

# 改字幕外观：先 preset，再微调
vibeknow video set 42 --subtitle-preset 2 --subtitle-size 52

# 改名（唯一不影响导出的改动）
vibeknow video set 42 --title "季度复盘"
```

**优先用 `--subtitle-preset`。** 可读性是组合：描边款会清掉背景板，背景板款会关掉描边。只设一半，命令照样退出 0，视频只是看起来不对，而且没有任何机制会报告。

**改完样式一定要重新导出。** 任何 work 级改动（bgm / subtitle / 样式）都会让已渲染的 MP4 失效；JSON 载荷里的 `export_invalidated` 会告诉你这件事，`next_actions[0].command` 是重新导出的命令。改标题是例外，它不触及输出。

字幕样式是**读-改-写**：后端整体保存样式，所以 CLI 先读出既有样式再逐字段覆盖——只改字号不会清掉你的字体和描边。`--subtitle-stroke-width 0` 表示无描边，与「未设置」是两回事，CLI 用指针字段保住这个区别。

## 三、video edit：只改一个镜头（计费）

```bash
# 先看现在的旁白稿
vibeknow video script 42

# 改第 3 个镜头，只重生成配音（更便宜）
vibeknow video edit 42 --scene 3 --script "新的旁白文本" --script-only
```

| 旗标 | 含义 |
|---|---|
| `--scene` | 第几个镜头，编号来自 `vk video script`（从 1 开始） |
| `--script` | 新的旁白文本 |
| `--script-only` | 只重生成配音，不动布局与背景图（更便宜） |
| `--yes` / `--confirm` | 与导出同款的授权门 |

`video edit` **计费**，因此同样有授权门：非交互环境下会停下来，退出码 8，载荷里带 `resume_command`。同样不要自己编 `--confirm`。

**改稿之后预览与分享链接是最新的，但已渲染的 MP4 不是。** 后端把旧文件留在原地，所以 `video download` 仍然返回上一版旁白，直到下一次 `video export`。响应里会标为 `export_stale`。

没有撤销：没有端点能返回某个镜头的上一版本。令牌绑定到那段确切文本，所以每次改写都是一个独立的授权块。

## 四、清理

```bash
# 本地账本：只丢已结束的运行
vibeknow jobs prune --terminal

# 远端知识库：先看
vibeknow kb prune --pattern "tmp-*" --output json

# 确认后再删
vibeknow kb prune --pattern "tmp-*" --yes
```

| 事项 | `vk kb prune` | `vk jobs prune` |
|---|---|---|
| 影响面 | 远端知识库（不可逆） | 仅本地账本 |
| 默认行为 | dry-run | 直接执行 |
| 强制条件 | 至少 `--pattern` 或 `--older-than` | 至少 `--terminal` / `--older-than` / `--all` |
| 是否碰后端 | 是 | **从不** |
| 幂等 | 404 记为成功 | — |

`vk jobs prune` 修剪的是**指针**，不会取消运行、不会删除 work、不会退还额度。

## 日常维护清单

1. **外观写进 preset，输入与授权留在命令行**。
2. **改完字幕或 BGM 就重新导出**，别忘了 `export_invalidated`。
3. **改稿前先 `vk video script`** 看编号，改一个镜头别整篇重来。
4. **清账本用 `--terminal`**，别用 `--all`。
5. **清知识库先 dry-run**，看 JSON 里的 `items` 再加 `--yes`。

## 延伸

- [/concepts/06-preset-contract.md](/concepts/06-preset-contract.md) —— preset 的白名单与拒绝清单
- [/concepts/07-subtitle-style-and-work-edit.md](/concepts/07-subtitle-style-and-work-edit.md) —— 读-改-写语义
- [/concepts/09-cleanup-safety-contract.md](/concepts/09-cleanup-safety-contract.md) —— 清理命令的安全契约
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— edit 与 export 的授权门
