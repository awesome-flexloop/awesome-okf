---
type: Concept
title: "VibeKnow CLI 整体形态：19 个顶层命令与四服务后端"
description: "VibeKnow CLI 的定位、命令树全貌、四个后端服务的职责划分、配置目录解析与构建产物，附首次使用前的准备清单"
tags: [vibeknow, cli, go, 命令树, 架构导览]
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
  - id: map
    resource: /references/source-code-map.md
    title: "VibeKnow CLI 源码结构地图"
---

# VibeKnow CLI 整体形态

> **事实编号**：F-001~F-006、F-086~F-094（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


VibeKnow CLI 是一个基于 Cobra 的 Go 命令行工具，附带 npm 分发包装。它把「文档 / URL / 本地文件 → 短视频」这件事拆成两个阶段：第一阶段生成预览（分享页 + 封面图），第二阶段导出 MP4（计费）。中间的每一次状态转移都由退出码承载。

本文是全束的入口，先建立整体地形，再进入各专题。

## 命令树全貌

顶层注册 19 个命令目标：13 个分组命令 + 6 个非分组命令。分组子命令共 41 个。

```
vk
├── create              # 主命令：文档/URL/文件 → 视频
├── init                # 初始化
├── update              # 自更新
├── version             # 版本
├── doctor              # 自检
├── completion          # shell 补全
├── api                 # 通用端点调用（1 个子命令：call）
├── auth                # 认证（4：login / status / logout / whoami）
├── avatar              # 头像（1：list）
├── config              # 配置（3：get / set / list）
├── credits             # 积分（1：balance）
├── doc                 # 文档（3：upload / get / images）
├── jobs                # 运行账本（3：list / get / prune）
├── kb                  # 知识库（3：delete / list / prune）
├── profile             # 配置档案（5：add / list / use / remove / show）
├── subtitle            # 字幕（2：fonts / presets）
├── theme               # 主题（1：list）
├── video               # 作品（13：status / wait / download / list / url /
│                       #        export / export-status / script / edit /
│                       #        set / pause / resume / avatar-retry）
└── voice               # 音色（1：list）
```

`vk video` 是分量最重的一组，13 个子命令覆盖了从「跑起来」到「改一改」到「导出来」的完整链路。

## 两阶段工作流

| 阶段 | 命令 | 计费 | 产物 |
|---|---|---|---|
| 生成预览 | `vk create` | 会计费（跑一次渲染） | 分享页 + 封面图 |
| 导出成片 | `vk video export` | 会计费（1 credit） | MP4 |

`vk create --export` 把两个阶段串成一次调用，但 `--async` 与 `--export` 互斥——异步在运行确认后即脱离，到不了导出那一步。两者组合返回退出码 2。

## 四个后端服务

CLI 通过 `client/` 下的四个客户端访问后端，共 39 个去重端点：

| 服务 | 端点数 | 职责 |
|---|---|---|
| `figlens` | 26 | 视频生成主链路：任务初始化、流式生成、作品与场景、字幕、头像、导出、流水线控制 |
| `vectoria` | 6 | 知识库与文档：知识库 CRUD、文件 / URL 上传、文档查询与图片提取 |
| `account` | 5 | 认证：设备码登录、令牌刷新、登出、用户资料 |
| `vibeknow` | 2 | 积分余额、音色列表 |

`vk api call --service <name> --method <m> --path <p> --body <b>` 提供不经过专用子命令直接打端点的通道。

## 四个视频类型与两个引擎

| 维度 | 取值 |
|---|---|
| 视频类型（`--mode`） | `replica`（复刻）、`image`（讲稿生图，线上 `image2`）、`handdraw`（手绘，线上 `hand-draw`）、`script`（弃用别名，等价 `--script-lock`） |
| 引擎（`--engine`） | `pipeline`（线上枚举 0，端点 `/v1/agent3forVideo/stream`）、`agent`（线上枚举 1，端点 `/v1/agent2forVideo/stream`） |

两个维度并非自由组合：agent 引擎不派发 `replica` / `image2` / `hand-draw` 三种图，组合会被本地校验拦下（退出码 2），不会走到上传与计费。

## 配置与凭证

配置目录解析顺序：

1. `VIBEKNOW_CONFIG_HOME`（测试与隔离场景用它）
2. Windows：`%AppData%/vibeknow`
3. `$XDG_CONFIG_HOME/vibeknow`
4. `~/.config/vibeknow`

目录不会被自动创建。目录下的关键文件：

| 路径 | 内容 |
|---|---|
| `<config-dir>/profiles.yaml` | 配置档案（端点、默认项目、信任标记） |
| `<config-dir>/action.key` | 付费动作令牌的铸造密钥（32 字节随机值，权限 0o600） |
| `<config-dir>/jobs.jsonl` | 本地运行账本（append-only JSONL） |
| `<config-dir>/presets/` | preset 文件目录 |

`vk profile add` 可配置 8 个旗标，其中 4 个 `--endpoint-*` 分别指向四个服务，`--trust` 与 `--is-production` 标记档案用途。

## 构建产物

`build.sh` 交叉编译 5 个平台：darwin/amd64、darwin/arm64、linux/amd64、linux/arm64、windows/amd64。二进制名 `vibeknow`（Windows 为 `vibeknow.exe`），版本号通过 `-ldflags -X github.com/vibeknow/cli/cmd.version` 注入。

仓库同时提供 npm 分发包装，`skills/` 目录下随包附带 3 个面向 AI Agent 的 Skill。

## 首次使用前的准备清单

1. **安装**：从 release 取二进制，或走 npm 包装；`vibeknow version` 确认版本。
2. **登录**：`vk auth login`（支持 `--headless`、`--device-code`、`--no-wait`、`--with-token` 四个旗标）；`vk auth status` 确认，`vk auth whoami` 看当前身份。
3. **看余额**：`vk credits balance`。余额不足时相关命令退出码 5。
4. **选工作区**：`vk profile add` 建档案，`vk profile use` 切换，`vk profile list` 列出。
5. **自检**：`vk doctor` 检查本机环境。
6. **试跑**：`vk create --text "……" --mode image`，先看预览再决定是否导出。

## 相关概念

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码契约（下一步必读）
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 付费动作的授权门
- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— create 的参数域
- [/references/source-code-map.md](/references/source-code-map.md) —— 源码结构地图
