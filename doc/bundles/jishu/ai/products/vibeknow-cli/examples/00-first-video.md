---
type: Example
title: "实操一：30 分钟内产出第一条视频"
description: "从认证到拿到 MP4 的完整链路——init/auth login、doc upload、create 同步渲染、preview-dir 取封面、video export 的授权门与 video download"
tags: [vibeknow, cli, 快速上手, 实操, 认证, 导出]
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
  - id: skill
    resource: /concepts/10-ai-skill-contract.md
    title: "AI Skill 运行契约"
---

# 实操一：30 分钟内产出第一条视频

> 本文命令与行为均来自 v0.9.2 源码（commit `93a26eca`）与仓库自带 Skill 文档。**本文作者未实机执行**；命令语义以源码为准，涉及计费与后端状态的步骤请以你自己的账号实测为准。

## 全流程概览

```
认证 → 准备素材 → 渲染（预览） → 导出 MP4（计费 + 确认） → 下载
```

**关键认知**：渲染本身免费并给出预览页与封面；**导出 MP4 才计费**，且这一步在非交互环境下会停下来等授权（退出码 8）。这条分界线决定了后面所有的脚本写法。

## 第 1 步：认证

```bash
# 交互式向导：建默认 profile 并登录
vibeknow init

# 或分开来
vibeknow auth login
vibeknow auth status        # 看凭证来源与当前 profile
vibeknow auth whoami        # 当前身份
```

四种登录方式互斥（`--with-token` / `--no-wait` / `--device-code` / `--headless`，同时给多个会被拒绝）：

| 场景 | 命令 |
|---|---|
| 人在终端 | `vibeknow auth login` |
| 有 PAT | `vibeknow auth login --with-token`（从 stdin 读） |
| **Agent 两段式** | `vibeknow auth login --no-wait` 打印设备码后退出 → 用户去浏览器确认 → `vibeknow auth login --device-code <code>` 续等 |
| 宿主自动化 | `vibeknow auth login --headless` 打印设备码 JSON 后自行轮询 |

`vibeknow init` 需要交互式终端；无 TTY 时它会直接提示改用 `auth login --with-token`。

## 第 2 步：准备素材

三条路，三选一：

```bash
# a) 本地文件 —— 自动上传（会建知识库）
vibeknow doc upload ./slides.pdf

# b) 已有知识库文档
vibeknow kb list
vibeknow doc get <doc_id>

# c) 直接给 create 一个 URL 或文本
vibeknow create --from "https://example.com/post"
vibeknow create --text "一段现成的文案"
```

`doc upload` 会创建知识库并轮询到文档解析完成。文档里的插图要用 `--images` 选时，先看编号：

```bash
vibeknow doc images <doc_id>     # 打印候选插图编号
```

编号是 **1 基**的，与 `create --images 1,3,5` 的写法一致。

## 第 3 步：渲染（预览，免费）

```bash
vibeknow create \
  --from ./slides.pdf \
  --mode image \
  --aspect vertical \
  --language zh-CN \
  --preview-dir ./out \
  --output json
```

**同步 vs 异步**：默认同步，阻塞到渲染完成。想立刻拿 id 就加 `--async`，返回 `task_id` 与 `session_id`。

**`--async` 与 `--export` 互斥**，同时给会被本地拒绝（退出码 2）。先渲染、后导出是唯一正确的顺序。

**`--preview-dir` 很重要**：它把封面静帧落盘，并用 `resource_ready` 事件宣告绝对路径。终端里你打不开 `share_url`，但你能把本地文件交给用户。

产物落在 `./out/`，文件名形如 `<session_id>-cover_image.jpg`。内容未变化时不会重复宣告，所以往同一目录重跑是安全的。

## 第 4 步：导出 MP4（计费 + 确认）

```bash
vibeknow video export 42 --session-id sess_xxx --output json
```

在交互终端里，CLI 会把计费条款摆出来问你「确认吗」。**在非交互环境（CI、Agent、管道）里它不替你决定**，而是：

| 情形 | 行为 |
|---|---|
| 带 `--yes` 或环境变量 `VIBEKNOW_ASSUME_YES=1` | 直接放行 |
| 带 `--confirm <action_id>` | 用这个一次性令牌放行 |
| 有 TTY | 交互询问 |
| 都没有 | 打印决策载荷并以**退出码 8** 退出 |

退出码 8 的载荷里有 `resume_command`，形如：

```bash
vk video export 42 --session-id sess_xxx --confirm act_xxxxxxxxxxxxxxxx
```

把这条命令转达出去，等用户批准后带上那个令牌重跑。

**不要自己编 `--confirm` 的值，也不要自作主张加 `--yes`。** CLI 停下来正是因为这个选择属于用户。

## 第 5 步：下载

```bash
vibeknow video download 42 --session-id sess_xxx --dest out.mp4 --overwrite
```

- `--dest` 指路径；`--output` 指的是**输出格式**（0.8 之前 `--output` 指的是文件路径，那个坑已经堵上）
- 不给 `--dest` 时默认写成 `<session_id>.mp4`
- 目标路径受 `SafeOutputPath` 限制，必须落在工作目录内的相对路径
- 已导出过才有文件；否则报校验失败并提示去 export

## 常见卡点

| 现象 | 原因 | 处理 |
|---|---|---|
| 退出码 8 | 非交互环境下遇到计费动作 | 走 `--confirm` 流程 |
| 退出码 2，报 `pages needs image` | `--pages` 只在 `--mode image` 下有效 | 去掉或改模式 |
| 退出码 2，报 `theme needs pipeline` | `--engine agent` 不支持 theme/language/avatar/images | 去掉或换 `--engine pipeline` |
| 退出码 6 | 投递状态无法确认 | 先 `vibeknow video status` 再决定是否重跑 |
| 找不到 MP4 | 改过 work（`video set`）导致导出失效 | 重新 `video export` |
| 渲染「卡住」 | 流水线本就有静默段 | 等终态事件，别重发 |

## 延伸

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 八个退出码的完整语义
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 授权门的四级解析
- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— 参数组合的合法范围
- [/examples/01-agent-safe-automation.md](/examples/01-agent-safe-automation.md) —— 把上面这套写成不会重复计费的脚本
