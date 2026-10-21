---
type: Reference
title: "VibeKnow CLI 后端端点全表"
description: "client/ 四个服务客户端的 39 个去重后端端点路径、HTTP 方法与用途，以及端点提取的统计口径"
tags: [vibeknow, cli, 后端端点, api, client]
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
---

# VibeKnow CLI 后端端点全表

本文登记 VibeKnow CLI 调用的后端端点。信源为 tag `v0.9.2` @ `93a26eca`。

## 统计口径

- 只取 `client/` 目录下**非测试文件**中 HTTP 调用实参里的 `/v` 开头路径字面量。
- `fmt.Sprintf` 格式串归一化：`%s` / `%d` 统一替换为 `{param}`。
- 跨文件按归一化后的路径去重。

去重后合计 **39 个**端点，分布于 4 个服务客户端。

## 服务划分

| 服务 | 端点数 | 职责 |
|---|---|---|
| `figlens` | 26 | 视频生成主链路：任务初始化、流式生成、作品与场景、字幕、头像、导出、流水线控制 |
| `vectoria` | 6 | 知识库与文档：知识库 CRUD、文件/URL 上传、文档查询与图片提取 |
| `account` | 5 | 认证与用户：设备码登录、令牌刷新、登出、用户资料 |
| `vibeknow` | 2 | 账户辅助：积分余额、音色列表 |

## `client/account`（5）

| 路径 | 用途 |
|---|---|
| `/v1/auth/device/code` | 申请设备码 |
| `/v1/auth/device/token` | 轮询设备码换取令牌 |
| `/v1/auth/token/refresh` | 刷新访问令牌 |
| `/v1/auth/logout` | 登出 |
| `/v1/user/profile` | 读取用户资料 |

## `client/vibeknow`（2）

| 路径 | 用途 |
|---|---|
| `/v1/credits/balance` | 查询积分余额 |
| `/v1/pipeline-voices` | 查询可用音色列表 |

## `client/vectoria`（6）

| 路径 | 用途 |
|---|---|
| `/v1/knowledgebases` | 列出知识库 |
| `/v1/knowledgebases?offset={param}&limit={param}` | 分页列出知识库 |
| `/v1/knowledgebases/{param}` | 单个知识库 |
| `/v1/knowledgebases/{param}/documents/file` | 上传本地文件为文档 |
| `/v1/knowledgebases/{param}/documents/url` | 上传 URL 内容为文档 |
| `/v1/knowledgebases/{param}/documents/{param}` | 单个文档 |

## `client/figlens`（26）

### 视频生成主链路

| 路径 | 用途 |
|---|---|
| `/v1/tasks/init` | 初始化任务（创建 work 行） |
| `/v1/agent3forVideo/stream` | pipeline 引擎（线上枚举 0）的流式生成 |
| `/v1/agent2forVideo/stream` | agent 引擎（线上枚举 1）的流式生成 |
| `/v1/task/extractDocImages` | 从文档提取图片（供 `--images` 使用） |

### 作品与场景

| 路径 | 用途 |
|---|---|
| `/v1/works/page?page={param}&size={param}` | 作品分页列表 |
| `/v1/works/detailBySession?session_id={param}` | 按 session 读取作品详情 |
| `/v1/works/scenes?work_id={param}` | 读取作品的场景列表 |
| `/v1/works/videoUrl?id={param}` | 读取作品视频地址 |
| `/v1/works/updateTitle` | 更新作品标题（`vk video set --title`） |
| `/v1/scene/edit` | 改写场景（`vk video edit`） |

### 字幕

| 路径 | 用途 |
|---|---|
| `/v1/works/subtitleSwitch` | 字幕开关 |
| `/v1/works/subtitleStyle` | 字幕样式（整体读写） |
| `/v1/works/subtitleFonts` | 可用字体族列表 |
| `/v1/works/subtitlePresets` | 字幕预设列表 |

### 音乐

| 路径 | 用途 |
|---|---|
| `/v1/works/bgmSwitch` | 背景音乐开关 |
| `/v1/works/bgmVolume` | 背景音乐音量 |

### 头像与主题

| 路径 | 用途 |
|---|---|
| `/v1/avatar/catalog` | 头像目录 |
| `/v1/avatar/scenes/retry` | 头像场景重试（`vk video avatar-retry`） |
| `/v1/assets?type=avatar` | 头像资源列表 |
| `/v1/themes?type=` | 主题列表 |

### 导出

| 路径 | 用途 |
|---|---|
| `/v1/agent2forVideo/exportRemoteV2` | 发起远程导出 |
| `/v1/agent2forVideo/exportResultV2` | 查询导出结果 |
| `/v1/agent2forVideo/signedUrl` | 获取签名下载地址 |
| `/v1/agent2forVideo/fastQueryOptimize` | 快速查询优化 |

### 流水线控制

| 路径 | 用途 |
|---|---|
| `/v1/pipeline/pause` | 暂停运行（`vk video pause`） |
| `/v1/pipeline/resume` | 恢复运行（`vk video resume`） |

## 引擎与视频类型的端点对应

| 引擎 | 线上枚举 | 流式端点 |
|---|---|---|
| `pipeline` | `EnginePipeline = 0` | `/v1/agent3forVideo/stream` |
| `agent` | `EngineAgent = 1` | `/v1/agent2forVideo/stream` |

| 视频类型 | 线上取值 |
|---|---|
| 复刻 | `replica` |
| 讲稿生图 | `image2` |
| 手绘 | `hand-draw` |

## 端点之外的直接调用

`vk api call` 提供通用端点调用能力，旗标为 `--service`、`--method`、`--path`、`--body`（4 个），服务名取自 `account` / `figlens` / `vectoria` / `vibeknow` 四项之一（`internal/endpoints/defaults.go`）。

## 相关概念

- [/concepts/00-cli-overview.md](/concepts/00-cli-overview.md) —— 整体形态与四服务划分
- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— 参数域与端点的对应
