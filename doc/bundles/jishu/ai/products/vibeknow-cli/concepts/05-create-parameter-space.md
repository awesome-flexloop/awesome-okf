---
type: Concept
title: "create 参数域：四档视频类型与两档引擎的正交组合"
description: "vk create 的 --mode 四档取值、--engine 两档枚举、引擎与类型的互斥矩阵、--pages/--aspect/--language/--images 的取值域、--from 四种来源分流与完整校验顺序"
tags: [vibeknow, cli, create, 参数校验, 视频类型, 引擎]
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

# create 参数域：四档视频类型与两档引擎的正交组合

> **事实编号**：F-054~F-066（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


`vk create` 的参数看起来很多，实际上只有两个轴在决定「这条命令能不能跑」：**视频类型（`--mode`）** 与 **渲染引擎（`--engine`）**。其余旗标都是在这两个轴确定后的可选项，且大部分有明确的取值域。

## 两个轴

### `--mode`：四档取值

| 命令行取值 | 线上取值 | 含义 |
|---|---|---|
| （空） | — | 不指定，由后端决定 |
| `replica` | `replica` | 复刻型视频 |
| `image` | `image2` | 图文型视频 |
| `handdraw` | `hand-draw` | 手绘型视频 |
| `script` | — | **弃用别名**，等价于 `--script-lock` |

弃用别名命中时，CLI 不会静默通过：向 stderr 打一行弃用告警，行为继续按 `--script-lock` 执行。

命令行名与线上名不同（`image`→`image2`、`handdraw`→`hand-draw`），是 CLI 与后端各自命名体系的差异，读后端响应时需要按线上值对照。

### `--engine`：两档枚举

| 命令行取值 | 线上枚举 | 后端路径 |
|---|---|---|
| `pipeline` | `EnginePipeline = 0` | `/v1/agent3forVideo/stream` |
| `agent` | `EngineAgent = 1` | `/v1/agent2forVideo/stream` |

## 组合矩阵：哪些搭配会被挡在本地

`validateEngineModeCombo` 与后续几处校验共同构成一张拒绝表：

| 组合 | 结果 |
|---|---|
| `agent` × {`replica`, `image`, `handdraw`} | 校验失败 |
| `agent` + `--theme` | 校验失败 |
| `agent` + `--language` | 校验失败 |
| `agent` + `--avatar` | 校验失败 |
| `agent` + `--images` | 校验失败 |
| `handdraw` + `--avatar` | 校验失败 |
| `replica` + `--images` | 校验失败 |
| 非 `image2` + `--pages` | 校验失败 |

**这些拒绝都在任何上传与计费动作之前完成。** 源码注释给出了理由：agent 引擎会**存下**这些配置却不生效，手绘图里根本没有数字人节点，replica 跑的是一张独立图——后端会照单全收然后渲染出一个没有用户要求的东西。CLI 在本地挡下，避免用户拿到一个静默少项的结果。

## 其余旗标的取值域

| 旗标 | 取值域 | 备注 |
|---|---|---|
| `--pages` | 0..20 | 上界 20 对应后端 `Image2MaxPageCount`；仅 `image2` 可用 |
| `--aspect` | `horizontal` / `vertical` | `16:9` 与 `9:16` 为别名 |
| `--language` | `zh-CN` `en-US` `es-ES` `fr-FR` `pt-BR` `ja-JP` `ko-KR` | 共 7 个 |
| `--images` | 逗号分隔的 **1 基**索引，如 `1,3,5` | 重复值与空白被容忍；非正整数或非数字报校验失败；空输入透传为 nil |

`--images` 的索引基数是 1，与 `vk doc images` 打印的文档编号一致。

## `--from` 的四种来源分流

| `--from` 取值 | 处理 |
|---|---|
| 文本 | 走文本上传 |
| `-` | 从 stdin 读文本后走文本上传 |
| `doc_id` | 直接使用该文档，**必须同时给 `--kb-id`** |
| `http(s)` URL | 走 URL 上传 |
| 其余 | 按本地文件处理 |

`doc_id` 的识别正则接受两种形态：`doc_` 前缀加 8 位以上字母数字，或标准 8-4-4-4-12 小写十六进制 UUID。

`--text` 与 `--from` 是「同一份输入的两种命名」：同时出现报校验失败，两者都不出现也报校验失败。源码注释记着原因——两者都放过就意味着悄悄挑一个丢掉另一个，而被丢掉的那份调用方永远不会知道。

## 校验顺序

```
preset 展开
  → text/from 互斥
  → async + export 互斥
  → mode
  → aspect
  → engine
  → engine + mode 组合
  → pages
  → theme / language
  → avatar
  → images
  → preview 通道创建
  → voice 解析
  → 输入解析与上传
```

**preset 展开排在最前**，因此 preset 里写错的组合会出现在同一条错误信息里，而不是被后续校验先截断。

末尾两项也各有理由：`--preview-dir` 创建不出来时拦截，因为渲染完再发现产物目录不存在就太晚了；`--voice` 在任何上传之前解析，因为无效音色引用不该让用户付出一个知识库和一份已解析文档的代价。

## `--async` 与 `--export` 互斥

两者同时出现直接报校验失败（退出码 2）。`--export` 在预览快照之后执行，而 `--async` 在运行确认后就脱离，两者合并会让 `--export` 被静默丢弃却仍然退出 0——调用方要 MP4，拿到的是预览，而且没有任何信号能区分。

详见 [/concepts/04-run-ledger-and-async.md](/concepts/04-run-ledger-and-async.md)。

## 实践建议

1. **先定轴再填参**：`--mode` 与 `--engine` 定下来之后，能用的旗标自然收窄。
2. **agent 引擎不要带 theme/language/avatar/images**，本地就会被拒，不用浪费一轮网络往返。
3. **`--images` 用 1 基索引**，与 `vk doc images` 的编号对齐。
4. **只用 `--text` 或只用 `--from`**，输入来源保持单一。

## 相关概念

- [/concepts/06-preset-contract.md](/concepts/06-preset-contract.md) —— preset 如何填充这些参数
- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 校验失败落在退出码 2
- [/concepts/00-cli-overview.md](/concepts/00-cli-overview.md) —— create 在命令树中的位置
- [/references/flag-inventory.md](/references/flag-inventory.md) —— 旗标全清单
