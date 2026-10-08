---
type: reference
title: LobsterAI 信源登记（I 阶段，基线 2026.9.4）
description: LobsterAI 知识束的上游信源、固定基线、许可证与关键信源文件清单，供事实回溯与基线复验使用。
tags: [lobsterai, electron, ai-agent, sources, provenance]
sources:
  - id: lobsterai-vendor
    resource: vendor/netease-youdao/LobsterAI
    title: LobsterAI 源码（固定基线 2026.9.4 @ 7592cd0）
---

# LobsterAI 信源登记

> 本文档登记 LobsterAI 知识束的全部信源信息。R 阶段事实清单（facts.md）与 I 阶段洞察（insights.md）均以此基线为准；复验或升级基线时须重新执行下述计数方法。

## 上游与固定基线

| 项目 | 值 |
|---|---|
| 上游仓库 | git@github.com:netease-youdao/LobsterAI.git |
| 固定基线 tag | 2026.9.4 |
| 基线 commit（完整 hash） | 7592cd034a7cb458a8650df0325b4980dd1bc162 |
| 基线校验命令 | `git -C vendor/netease-youdao/LobsterAI rev-parse HEAD` |
| 许可证 | MIT License（Copyright (c) 2026 NetEase Youdao，见仓库根 LICENSE） |
| package.json name/version | lobsterai / 2026.9.4 |
| 关键依赖版本 | electron 40.2.1、better-sqlite3 ^12.8.0、@modelcontextprotocol/sdk ^1.27.1、zod ^4.3.6、nim-web-sdk-ng 10.9.77-alpha.4；README 声明 openclaw v2026.6.1、dsh 0.1.1-rc.1 |

## 关键信源文件清单

> 按子系统分组；「覆盖事实」为 facts.md 中的引用编号区间。

### 项目级

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| package.json | F-la-001~F-la-006 | 名称/版本、Node engines、技术栈依赖、脚本、openclaw.plugins 10 插件清单 |
| README.md | F-la-003, F-la-007, F-la-009 | 技术栈声明、技能数量声明（过期）、依赖版本声明 |
| AGENTS.md | F-la-008 | 架构分工声明（Cowork 产品层 / OpenClaw 唯一运行时）与 IPC/日志/i18n 规范 |
| LICENSE | —（许可证条款） | MIT 许可证全文 |
| vitest.config.ts | F-la-070, F-la-071 | 测试 include 双模式（src/ 与 tests/）、node 环境、20 秒超时、路径别名 |

### 主进程（src/main/）

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| src/main/main.ts | F-la-010~F-la-014 | 主窗口创建（约 13470 行段）、webPreferences 安全基线、webview 偏好重写、加载策略 |
| src/main/sqliteStore.ts | F-la-015~F-la-018 | SqliteStore 工厂、PRAGMA 迁移、13 张表建表语句 |
| src/main/coworkStore.ts | F-la-019~F-la-022 | CoworkStore 会话/消息/配置记忆/其他四组方法签名 |
| src/main/agentManager.ts | F-la-023 | AgentManager 委托方法与预设 Agent 方法 |
| src/main/trayManager.ts | F-la-024 | 托盘创建/菜单/提醒接口 |
| src/main/im/nimGateway.ts | F-la-025 | NIM 网关类方法族（EventEmitter） |
| src/main/im/nimQChatClient.ts | F-la-026 | QChat 客户端接口与方法 |
| src/main/im/qqMediaDownload.ts | F-la-027 | QQ 媒体下载限额（25MB）与 7 天清理策略 |
| src/main/im/imGatewayManager.ts | F-la-028 | 九平台网关管理器与各平台连通性测试方法 |
| src/main/mcp/mcpStore.ts | F-la-029 | MCP 服务器 CRUD 与 launch resolution 读写 |
| src/main/mcp/mcpLaunchResolution.ts | F-la-030 | 启动解析常量、来源指纹与 npx 判定工具函数 |
| src/main/mcp/mcpRuntime.ts | F-la-031 | MCP 运行时（AskUser 服务器、桥接处理器、缓存刷新） |
| src/main/libs/mcpBridgeServer.ts | F-la-032 | 桥接服务器与三类工具请求/响应类型 |
| src/main/skills/skillManager.ts | F-la-033 | SkillManager 13 方法（同步/检测/下载/升级/监听） |
| src/main/skills/index.ts | F-la-034 | OpenClaw 同步报告重导出 |
| src/main/skins/（20 个 .ts，8 个测试） | F-la-035, F-la-074 | 皮肤运行时：控制器/协议/呈现/存储/工具桥/媒体桥/包生命周期 |
| src/main/ipcHandlers/kits/handlers.ts | F-la-036 | kits IPC 处理器、SKILLs 目录与 SKILL.md 文件名常量 |
| src/main/preload.ts | F-la-037~F-la-040 | IPC 通道全清单（命名空间分组、9 个流事件、IM 平台参数化通道、OAuth 流程） |

### 渲染进程（src/renderer/）

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| src/renderer/App.tsx | F-la-041 | 顶层视图路由（Cowork/Kits/Library/ScheduledTasks/Settings/SkillsAndConnectors） |
| src/renderer/store/slices/（21 个 .ts：13 个 slice + 8 个测试） | F-la-042 | Redux slice 全集（Glob 计数） |

### 共享层（src/shared/cowork/）

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| src/shared/cowork/btw.ts | F-la-043~F-la-046 | 打断提问协议：四态枚举、六组限长常量、双命令别名（/btw、/side） |
| src/shared/cowork/goal.ts | F-la-047, F-la-048 | 目标协议：六态枚举、token 预算字段与格式化 |
| src/shared/cowork/rail.ts | F-la-049 | 轨道索引协议：索引项结构、预览截断与 Markdown 剥离 |
| src/shared/cowork/steer.ts | F-la-050~F-la-052 | 纠偏协议：三态枚举、7 种拒绝原因、多模态负载 |
| src/shared/cowork/constants.ts | F-la-053~F-la-056 | 权限会话 ID、分页常量、CoworkIpcChannel 常量对象、ForkMode |

### 定时任务（src/scheduledTask/）

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| src/scheduledTask/design.md | F-la-057, F-la-058 | 三层架构与四大理念（OpenClaw 驱动/策略模式/来源推断/15 秒轮询） |
| src/scheduledTask/types.ts | F-la-059, F-la-060 | Schedule 与 Payload 判别联合、任务/运行接口 |
| src/scheduledTask/constants.ts | F-la-061~F-la-063 | DeliveryMode/SessionTarget/WakeMode/TaskStatus 枚举、17 个 IPC 通道 |
| src/scheduledTask/cronJobService.ts | F-la-064 | CronJobService 轮询方法与四组网关映射函数 |

### 技能包（SKILLs/）

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| SKILLs/*/SKILL.md（29 个） | F-la-065, F-la-067 | 技能单文件约定（name/description/official/version） |
| SKILLs/skills.config.json | F-la-066, F-la-068, F-la-069 | 注册表 version/defaults 29 条、order 全清单、显式禁用项 |

### 测试（tests/）

| 文件 | 覆盖事实 | 说明 |
|---|---|---|
| tests/（38 个文件，2 个子目录） | F-la-072, F-la-073 | Vitest 与 node:test 混用；sqlite-backup/ 与 openclaw-extensions/ 子目录 |
