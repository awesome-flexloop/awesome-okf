---
type: Concept
title: "模块内部：技能、循环、闸门与自建技能的实现"
description: "从源码看技能的生命周期、操作循环的参数、Sentinel 的判定、MCP 工具路由、提醒与轨迹，以及 0.2.0 分支的 SKILL_SAVE 如何做到「没有确认就写不进手机」"
tags: [trae, agent, source-code, skills, sentinel, mcp, internals]
generated: 2026-11-18
status: draft
sources:
  - id: source-code
    resource: "/references/source-code.md"
    title: "源码核验事实登记（选读）"
---

# 模块内部：技能、循环、闸门与自建技能的实现

这一篇回答「为什么按四问写的技能能被稳定执行」，以及「手机上一句话写技能」在代码里到底做了什么。读完后，你排障时能直接指到模块，而不是反复改提示词。

## 技能的一生

```text
技能文件夹
  → SkillParser 解析 frontmatter（七字段）
  → 校验（name/description/apps/channel/deeplinks）
  → FlowParser 校验 flow.yaml（仅当 SKILL.md 有效）
  → DirectorySkillRepository 合并多个根目录
  → 聊天模型只看到 name + description 的技能索引
  → 选中后把正文注入操作提示词
```

四个关键事实（S-033、S-034、S-036、S-010）：

- **合法键只有七个**：`name`、`description`、`apps`、`channel`、`confirm_before`、`memory`、`deeplinks`；写错键会被 lint 判为问题。
- **`description` 是检索面**：聊天模型靠它挑技能，所以要写「做什么、用哪个 App」，不要写口号。
- **`flow.yaml` 后校验**：`SKILL.md` 不合法时，流程文件根本不会被解析。
- **覆盖顺序固定**：内置技能先加载，用户技能后加载并按同名覆盖；用户技能损坏时，同名内置技能仍然生效。

## 操作循环的参数

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `maxSteps` | 30 | 一次手机任务最多多少步 |
| `stuckRepeats` | 3 | 连续几次屏幕不变算卡住 |
| `historyWindow` | 8 | 回放给操作模型的最近步数 |
| `maxNodes` | 120 | 每步最多发送多少节点 |
| 解析失败上限 | 3 | 连续解析失败即结束任务 |

循环顺序是：观察屏幕 → 组装提示词（目标、技能说明、技能引用记忆、howto 命中、历史、节点、截图）→ 请求操作模型（JSON 模式）→ 宽松解析 → Sentinel 授权 → 执行 → 卡死检测（S-017、S-019、S-022）。

**排障含义**：如果任务总在第 30 步失败，那不是模型笨，而是任务太长；如果连续三次屏幕不变，先怀疑页面没加载完或点击没命中，而不是继续改提示词。

## Sentinel：规则在模型之外

| 判定 | 触发条件 |
|------|----------|
| 拒绝 | 受保护屏幕上的设备操作；向密码框输入；技能声明 `apps` 时越界包 |
| 询问 | 目标文字命中 17 个内置确认词或技能 `confirm_before`；deeplink 不在技能模板 |
| 允许 | 其他动作 |

授权分「仅一次」与「本次任务」；后者按任务与确认词记忆，任务结束清除。每次决策写入 `audit.jsonl`（S-024~S-027）。

**排障含义**：技能里写「不要付款」只是规则；真正拦住付款的是 Sentinel 的确认词。技能写歪了，闸门仍然有效。

## MCP：不操作手机的另一条路

聊天模型同时看到内置工具与 MCP 工具，MCP 工具名格式为 `服务器名__工具名`（如 `amap__maps_weather`）。能用 MCP 完成的事优先走工具，剩下只有 App 能做的才交给 `phone_task`（S-054）。

每个服务器有 `confirm` 策略：

| 策略 | 行为 |
|------|------|
| `writes`（默认） | 除标注只读的工具外，每次调用前询问 |
| `all` | 全部询问 |
| `none` | 不询问，只适合查询类服务 |

**排障含义**：叫车、下单类服务保持 `writes`；如果 Agent 说「没有终端无法确认」，不是它坏了，而是安全策略在生效。

## 自建技能 0.2.0：确认写在能力层

`camp/02-skill-builder` 增加了 `SKILL_SAVE` 工具（S-058）：

1. 模型生成完整 `SKILL.md`。
2. 工具先按 App 相同规则校验；不合法直接返回错误。
3. 合法则把草稿展示给用户，等待明确的「确认」。
4. 用户确认后才写入用户技能目录，并重新加载。
5. 重新加载后检查该技能是否真的可用；不可用则返回错误。

这条链路对应第 5 篇的「双闸门」：技能里可以写「保存前先确认」，但即使技能写歪，没有确认输入，`SKILL_SAVE` 也不会落盘。

## 三个运行形态，同一套核心

| 形态 | 设备层 | 记忆位置 | 能做什么 |
|------|--------|----------|----------|
| 安卓 App | `hands` 无障碍 | 手机 App 目录 Markdown | 聊天、MCP、操作 App |
| 网页版 | 无（不操作手机） | 浏览器 `localStorage` | 聊天、MCP、日历提醒 |
| iOS | `ios-hands` + WDA | Mac 本机 | 聊天、MCP、操作 iPhone |

三者共用 `core-agent`、`core-memory`、`core-skills`、`core-sentinel`；差异只在 `Device` 实现与存储位置（S-055、S-056）。

## 读源码的顺序建议

1. `core-api` 的 `Skills.kt`、`Device.kt`、`Sentinel.kt`：先看数据结构。
2. `core-skills/SkillParser.kt`：看校验规则。
3. `core-agent/OperatorLoop.kt`：看一步任务怎么跑。
4. `core-sentinel/PolicySentinel.kt`：看什么会被拦。
5. `app/AppGraph.kt`：看这些模块怎么被组装起来。

对应事实编号见 [源码核验事实登记](../references/source-code.md)（S-001~S-059）。
