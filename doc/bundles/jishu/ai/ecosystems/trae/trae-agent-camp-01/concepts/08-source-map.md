---
type: Concept
title: "源码地图：小满的十一个模块与改动落点"
description: "按当前 main（08cd059）梳理 core-api、core-llm、core-memory、core-skills、core-sentinel、core-agent、core-mcp、hands、web-server、ios 与 app/cli 的职责，给出用 TRAE 读源码的路径与改动落点"
tags: [trae, agent, source-code, architecture, modules]
generated: 2026-11-18
status: stable
sources:
  - id: source-code
    resource: "/references/source-code.md"
    title: "源码核验事实登记"
---

# 源码地图：小满的十一个模块与改动落点

这一篇把「想改一处」翻译成「去哪个模块」。课程里的户型图比喻仍然成立，只是房子在 2026-11 之后扩建了：除了记忆、技能、手机操作，还多了 MCP 服务、网页版和 iOS 通道。

## 当前仓库状态

| 项 | 当前值 |
|----|--------|
| main HEAD | 08cd059（2026-11-07） |
| App 包名 | `dev.xiaoman.app` |
| 版本 | main 0.1.0；`camp/02-skill-builder` 0.2.0 |
| 远端分支 | `main`、`camp/xiaoman`、`camp/xiaoman-web`、`camp/02-skill-builder`、`ios/wda-hands` |
| 示例技能 | 11 个（含课程五个场景） |

## 模块表

| 模块 | 类型 | 职责 | 你会为了什么进去 |
|------|------|------|------------------|
| `core-api` | Kotlin/JVM | 所有接口与数据结构：`Action`、`AgentConfig`、`Note`、`Skill`、`Decision` | 想知道一个动作有哪些字段、技能能写哪些键 |
| `core-llm` | Kotlin/JVM | 兼容 OpenAI 的客户端：图片输入、工具调用、JSON 模式、重试 | 调超时、重试、JSON 模式，或换模型服务 |
| `core-memory` | Kotlin/JVM | Basic Memory Markdown + 中文检索索引 | 改记忆格式、检索、permalink 规则 |
| `core-skills` | Kotlin/JVM | `SKILL.md` / `flow.yaml` 的解析、校验与目录加载 | 加技能字段、改校验规则、调覆盖顺序 |
| `core-sentinel` | Kotlin/JVM | 允许 / 询问 / 拒绝、任务级授权、审计 | 改确认词、加拒绝规则、调授权范围 |
| `core-agent` | Kotlin/JVM | 聊天编排、操作循环、技能流程、经验沉淀 | 改 Agent 行为、提示词、工具、卡死检测 |
| `core-mcp` | Kotlin/JVM | MCP 客户端：把外部服务工具交给聊天模型 | 接新 MCP 服务、改确认策略与密钥脱敏 |
| `hands` | Android 库 | 无障碍读屏、点击、输入、悬浮停止按钮 | 改读屏与点击、调屏幕稳定等待 |
| `ios-hands` / `ios-runner` | Kotlin/JVM | WebDriverAgent 设备接口 / Mac 命令行 | 在 Mac 上试 iPhone，不装 App |
| `web-server` | Kotlin/JVM | 网页版服务端 + 移动端网页 | 改网页版聊天、MCP 目录、课堂令牌 |
| `app` | Android 应用 | 聊天、技能、记忆、设置、服务、授权确认、轨迹 | 改界面、加首页卡片、改设置项 |
| `cli` | Python 3 | lint / push / run / logs / traces | 校验技能、推手机、看轨迹 |

依赖方向：`app` 依赖全部 `core-*` 与 `hands`；`core-*` 之间只通过 `core-api` 通信。五个纯 JVM 模块不碰 Android API，可以在电脑上跑单元测试。

## 改动落点速查

| 你想改 | 先看 | 风险 |
|--------|------|------|
| 助手的说话方式、拆任务方式 | `core-agent/Prompts.kt`、`XiaomanAgent.kt` | 中 |
| 加一个内置工具 | `core-agent/AgentTools.kt` + `ChatTools.kt` | 中 |
| 加技能字段或校验规则 | `core-api/Skills.kt` + `core-skills/SkillParser.kt` + `cli/*/lint.py` | 高（两边必须同步） |
| 改确认词或拒绝规则 | `core-sentinel/ConfirmWords.kt`、`PolicySentinel.kt` | 高（安全相关） |
| 改记忆文件格式 | `core-memory/BasicMemoryFormat.kt` | 高（旧记忆兼容） |
| 改界面 | `app/ui/*` | 低到中 |
| 改网页版 | `web-server` + `docs/web.md` | 中 |
| 接新 MCP 服务 | `core-mcp` 的 `catalog.json` + `docs/mcp.md` | 低（配置） |

## 用 TRAE 读源码的最短路径

```text
请阅读 README.md 和 settings.gradle.kts，用不懂代码的人也能听懂的话告诉我：
1. 聊天、记忆、技能、手机操作、MCP 服务这五块分别在哪个模块；
2. 我在手机上说一句话之后，程序大概经过哪几步；
3. 如果我想改【具体习惯】，应该动哪个文件。
先只讲解，不要修改任何文件。
```

三问能答上来，再动手。第一次改动建议落在 `skills/examples/<技能>/SKILL.md` 或 `app/ui`，不要先动 `hands` 与 `core-sentinel`。

## 源码与课程的关系

课程讲的是「怎么用」，源码决定「为什么这样用」。两者冲突时，以当前源码为准，并在正文标注差异；本包把核验结果单独登记在 [源码核验事实](../references/source-code.md)（S-001~S-059），课程原文在 [课程事实登记](../references/course-source.md)（F-001~F-095）。
