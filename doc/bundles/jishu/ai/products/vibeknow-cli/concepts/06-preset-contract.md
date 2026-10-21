---
type: Concept
title: "preset 契约：只描述长相与声音，输入与授权永远留在命令行"
description: "vk create --preset 的白名单 14 键与拒绝 9 键、pflag Changed 旗标实现「命令行优先」、schema_version=1 与 KnownFields(true) 的严格解析、preset 搜索目录与无 vk preset list 的现状"
tags: [vibeknow, cli, preset, 参数默认值, 安全边界]
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

# preset 契约：只描述长相与声音，输入与授权永远留在命令行

> **事实编号**：F-067~F-072（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


`--preset` 允许把「每次都一样的那些参数」写进一个文件，避免在命令行重复敲一长串。它同时也是一条安全边界：**preset 能设什么、不能设什么，是被显式枚举出来的，不是靠"没在白名单里就报错"兜底。**

## 允许设置的 14 个键

| 键 | 类别 |
|---|---|
| `mode` | 视频类型 |
| `script-lock` | 脚本锁定 |
| `aspect` | 画幅 |
| `bgm` | 背景音乐 |
| `engine` | 渲染引擎 |
| `pages` | 页数 |
| `images` | 插图索引 |
| `theme` | 主题样式 |
| `language` | 语言 |
| `voice` | 音色 |
| `prompt` | 提示词 |
| `avatar` | 数字人 |
| `avatar-position` | 数字人位置 |
| `avatar-size` | 数字人尺寸 |

这 14 个的共同点：**描述一条视频长什么样、听起来如何，且在不同运行之间是相同的。**

## 拒绝设置的 9 个键

拒绝不是沉默跳过，而是逐条给出理由，错误信息里会写清楚「应该怎么做」：

| 键 | 拒绝理由（源码原文的意译） |
|---|---|
| `export` | 授权一次计费动作，请写在命令行 |
| `yes` | 授予计费动作的同意，请写在命令行 |
| `confirm` | 承载一次性动作令牌，请写在命令行 |
| `from` | 标识某一次运行的输入，不是一份可复用的风格 |
| `text` | 标识某一次运行的输入，不是一份可复用的风格 |
| `kb-id` | 标识某一次运行的输入，不是一份可复用的风格 |
| `async` | 描述这次调用而非风格，请写在命令行 |
| `preview-dir` | 是不随文件走的本地路径，请写在命令行 |
| `output` | 描述这次调用而非风格，请写在命令行 |

被拒绝的键分两类：**授权类**（`export` / `yes` / `confirm`）与 **单次调用类**（`from` / `text` / `kb-id` / `async` / `preview-dir` / `output`）。前者若能写进文件，一份躺在磁盘上的 preset 就等于一次预授的计费许可；后者若能写进文件，preset 就不再是「默认值」而是「命令」。

## 命令行永远赢

展开 preset 时，CLI 检查 pflag 的 `Changed` 标志：**用户在命令行显式给过的旗标，preset 不覆盖。**

```go
if fs.Changed(name) {
    continue // command line wins
}
```

源码注释写明：命令行是调用方的直接指令，文件不允许与它矛盾。于是 preset 的语义严格是**默认值**而非**覆盖值**。

展开顺序按键名排序，源码注释给的理由是「让一个无效文件总是先报同一个键」——map 的遍历顺序会让错误信息随运行而变。

## 文件格式

```yaml
schema_version: "1"
name: my-style
description: "..."
create:
  mode: image
  aspect: vertical
  language: zh-CN
```

| 约束 | 行为 |
|---|---|
| `schema_version` | 只接受 `"1"`；声明为其它值直接拒读，不按猜测解析 |
| 缺省 `schema_version` | 视作 `"1"` |
| 顶层键拼错 | `dec.KnownFields(true)` 拒读——一个拼错的顶层键会让 preset 静默什么都不做 |
| `create:` 块为空 | 拒读：一个什么都没设的 preset 是笔误，不是默认值 |
| 键名拼写 | 下划线与连字符等价（`avatar_position` = `avatar-position`） |
| 值类型 | 必须是标量，交给 pflag 解析并做范围检查，报错信息与命令行一致 |

`schema_version` 的存在让 preset 文件有明确的演进契约：未来格式变化时，旧文件会被明确拒绝，而不是被按新格式误读。

## 搜索目录与名字解析

| 项目 | 规则 |
|---|---|
| 目录 | `<config-dir>/presets` |
| 裸名 | 依次尝试 `.yaml` 与 `.yml` |
| 含分隔符或 YAML 后缀 | 直接当路径读 |
| 找不到 | 错误信息附上目录里可用的名称列表 |
| 列举 | **没有 `vk preset list` 子命令** |

「找不到时附可用名称列表」是把拼写错误变成一步修复的操作；源码注释承认这也是该特性**唯一**的列举方式——`vk preset list` 不存在。

`<config-dir>` 的解析顺序是 `VIBEKNOW_CONFIG_HOME` > Windows `%AppData%/vibeknow` > `$XDG_CONFIG_HOME/vibeknow` > `~/.config/vibeknow`，且目录不会被自动创建。

## 失败即退出码 2，且早于上传

preset 加载或展开的任何失败都以**退出码 2** 结束。源码注释的说法是：preset 对调用方来说就是命令行的一部分，所以坏掉的 preset 是一次无效调用——而且**代价为零**，因为展开发生在第一次上传之前。

错误信息里还会附上 preset 目录路径作为提示。

## 每次运行都报告展开结果

preset 参与之后，「这次运行实际用了哪些参数」就不能只看命令行了。CLI 因此在每次带 preset 的运行里都说明展开情况：

- 事件通道开启时，发 `preset.applied` 事件，带 `preset` 名、`path` 与实际生效的 `keys` 列表
- 事件通道关闭时，向 stderr 打印一行说明；一个键都没生效时打印的是「没有应用任何键」那一档

这与 [01-exit-code-contract.md](/concepts/01-exit-code-contract.md) 里「JSON 只是载荷补充」是同一条主张的延伸：**能显式说明的事情，不要让使用者去猜。**

## 实践建议

1. **preset 只放外观类参数**：mode、aspect、bgm、theme、language、voice。
2. **授权类参数永远在命令行**：`--export`、`--yes`、`--confirm` 一个都不进文件。
3. **preset 展开失败先看退出码 2 与提示里的目录路径**，文件在 `<config-dir>/presets`。
4. **同一参数以命令行为准**，preset 只是默认值。

## 相关概念

- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— preset 填充的参数取值域
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 为什么授权类键必须留在命令行
- [/concepts/03-output-and-events.md](/concepts/03-output-and-events.md) —— `preset.applied` 事件的通道
- [/references/flag-inventory.md](/references/flag-inventory.md) —— 旗标全清单
