---
type: Reference
title: "小满源码核验事实登记（选录 S-001~S-059，编号与 01 包一致）"
description: "与 01 课包共用同一套源码事实编号，按 02 课主题选录 43 条：包名与路径、技能七字段与 channel 枚举、校验规则与 lint 输出、push 行为、轨迹与 logs、Agent 常量、Sentinel、提醒、02 分支与五个技能的存在性，以及 MCP/网页版/iOS 新模块"
tags: [trae, agent, source-code, skills, cli, lint, channel, verification]
generated: 2026-11-17
verified: process:seven-concepts-v
status: draft
sources:
  - id: repo-main
    resource: "本地仓库 external/dev/libs/others/xiaoman（main 分支，commit 580fdf7，2026-11-01）"
    title: "xaioman main：PhonePal 0.1.0"
  - id: repo-camp
    resource: "同一仓库远端分支 origin/camp/xiaoman（课程版：小满 dev.xiaoman.app）"
    title: "xaioman camp/xiaoman：小满课程版"
  - id: repo-remote
    url: https://github.com/aduoge/xiaoman
    title: "aduoge/xiaoman"
---

# 源码核验事实登记（02 课选录）

> **编号约定**：本文件与 01 课包的 `references/source-code.md` 共用同一套 S 编号，按 02 课主题**选录**，因此编号不连续。需要在两包之间对照时，同一 S 编号指向同一条事实。
>
> **信源**：本地仓库 `external/dev/libs/others/xiaoman`；`main` 为 PhonePal 主线（580fdf7，2026-11-01），`origin/camp/xiaoman` 为课程版小满分支，均只读读取，未切换工作树。

## 一、仓库与版本

| 编号 | 事实 | 分支 |
|------|------|------|
| S-001 | 2026-11-18 复读时本地 main HEAD 为 08cd059（2026-11-07）；远端分支包括 `main`、`camp/xiaoman`、`camp/xiaoman-web`、`camp/02-skill-builder`、`ios/wda-hands`，02 课分支**已公开**。 | 远端 |
| S-002 | 远端分支引用包括 `main`、`camp/xiaoman`、`camp/xiaoman-web`、`camp/02-skill-builder`、`ios/wda-hands`。 | 远端 |
| S-003 | main 与 camp/xiaoman 的 applicationId 与 namespace 均为 `dev.xiaoman.app`；早期 main 的 `dev.phonepal.app` 已随改名合并。 | 两分支 |
| S-004 | main 为 versionCode 1 / versionName `0.1.0`；`camp/02-skill-builder` 为 versionCode 2 / versionName `0.2.0`；minSdk 30，targetSdk 35。 | 两分支 |
| S-005 | 构建需要 JDK 17 与 Android SDK 35；许可证为 MIT。 | 两分支 |
| S-007 | 课程分支含 `docs/classroom.md` 学生手册；2026-11-07 版把第二节场景换成呼声榜 TOP5，仍写明 Android 11 及以上、iPhone 不支持、TRAE 负责读代码改代码跑命令。 | camp/xiaoman |

## 二、路径与技能加载

| 编号 | 事实 | 分支 |
|------|------|------|
| S-008 | `<external files>` 在课程分支为 `/sdcard/Android/data/dev.xiaoman.app/files`；其下有 `memory/`、`skills/`、`traces/` 三个目录。 | camp/xiaoman |
| S-009 | 内置技能从 APK assets 解压到应用内部目录 `<filesDir>/bundled-skills/`；用户技能目录为 `<external files>/skills/`。 | camp/xiaoman |
| S-010 | 技能仓库按「内置在前、用户在后」加载，用户技能按名称覆盖内置；用户技能损坏时同名内置技能保持生效。 | 两分支 |

## 三、技能格式与校验

| 编号 | 事实 | 分支 |
|------|------|------|
| S-033 | 技能 frontmatter 的合法键恰为七个：`name`、`description`、`apps`、`channel`、`confirm_before`、`memory`、`deeplinks`；出现未知键即报错。 | 两分支 |
| S-034 | `name` 必填且匹配 `[a-z0-9-]+`，应与文件夹同名（不一致会报告但仍按 name 加载）；`description` 必填、非空、单行；`apps` 每项须为包名；`deeplinks` 每项须为 `scheme://...`。 | 两分支 |
| S-035 | `channel` 取值为 `api`、`cli`、`deeplink`、`gui`（默认）、`deeplink-then-gui`、`mixed`、`chat`；`chat` 已进入 `SkillChannel` 枚举与 `docs/skills.md` 的「聊天工作流」一节。 | 两分支 |
| S-036 | `flow.yaml` 仅在 `SKILL.md` 有效后才校验；步骤类型为 `launch`、`deeplink`、`ai`、`confirm`、`tap`、`type`、`wait`、`assert`；每步恰好一个 `类型: 值`；`wait` 取 0..600000 毫秒。 | 两分支 |
| S-037 | 课程分支内置示例含 `set-alarm`，`channel: gui`，操作系统时钟包，只新增闹钟、不改已有闹钟。 | camp/xiaoman |
| S-038 | `today-plan`、`health-alarms`、`taobao-compare`、`daily-quiz`、`ai-news-brief` 五个技能**已进入公开仓库** `skills/examples/`；示例技能合计 11 个。 | main |
| S-052 | 本仓库与 camp/xiaoman 分支中没有 `superagent-lead` 目录或引用；课程称其为独立仓库。 | 两分支 |

## 四、开发者 CLI

| 编号 | 事实 | 分支 |
|------|------|------|
| S-046 | CLI 入口：main 为 `cli/phonepal.py`，课程分支为 `cli/xiaoman.py`；命令为 `lint`、`push`、`run`、`stop`、`logs`、`traces pull`、`traces show`；全局 `--adb` 与 `--serial/-s` 可写在子命令前后。 | 两分支 |
| S-047 | `lint` 与 App 使用相同规则，问题输出 `path:line: message`，有问题的退出码为 1；摘要行输出到 stderr，格式为 `N skill(s) checked, N ok, N problem(s)`。 | 两分支 |
| S-048 | `push` 先 lint，未通过则拒绝推送；通过后删除并重建远端 `skills/<name>/`，逐个 `adb push` 文件，再广播 `RELOAD_SKILLS`；成功时输出 `pushed <本地目录> -> <远端目录> (<文件列表>)` 与 `skills reloaded; ...`。 | 两分支 |
| S-049 | `traces show` 在本地找不到该 run id 时先 `adb pull`；`logs` 持续读取 logcat，可按 `--run-id` 过滤；`run --follow` 直到 `PhoneTaskFinished`/`Failed`，成功退出码 0。 | 两分支 |
| S-050 | 课程分支手册给出的成功判据为：lint 显示 `0 problem(s)` 与 push 后 `skills reloaded`，再在手机上原样复测。 | camp/xiaoman |

## 五、Agent 与安全

| 编号 | 事实 | 分支 |
|------|------|------|
| S-016 | 聊天模型可用工具为 `memory_search`、`memory_read`、`memory_write`、`memory_forget`、`list_skills`、`reminder_set`、`phone_task`。 | camp/xiaoman |
| S-017 | AgentConfig 默认值：`maxSteps=30`、`stuckRepeats=3`、`historyWindow=8`、`maxNodes=120`、`learnFromSuccess=true`。 | 两分支 |
| S-018 | 设置页 `maxSteps` 可调 1..200；聊天与操作两个模型都配置完成才算整体 configured。 | 两分支 |
| S-019 | 操作循环：观察 → 操作模型（JSON 模式）→ 宽松解析（最多 3 次解析失败）→ Sentinel 授权 → 执行 → 卡死检测；连续 3 次屏幕不变先警告，再次卡住则失败。 | 两分支 |
| S-021 | 课程分支常量：`MAX_TOOL_ROUNDS=8`、`HISTORY_LIMIT=20`、`MEMORY_HITS=5`、`MAX_HOWTO_NOTES=3`；成功路径写入 `howto/<技能名或包名>`，类型与标签均为 `howto`。 | camp/xiaoman |
| S-022 | 操作提示词按顺序拼装：目标（或子目标）、技能说明、技能引用的记忆、命中的 howto 笔记、最近 `historyWindow` 步历史、上一步反馈、节点列表（≤`maxNodes`）与截图。 | 两分支 |
| S-024 | 拒绝：FLAG_SECURE 屏幕上的设备操作除 `back`、`home`、`wait` 外拒绝；密码框输入拒绝；技能声明 `apps` 时越界包拒绝（启动器与自身除外）。 | 两分支 |
| S-025 | 询问：`tap`、`long_press`、`type` 的目标或节点文字命中确认词；`deeplink` 与技能模板 scheme/host 不匹配。 | 两分支 |
| S-026 | 内置确认词 17 个：支付、付款、确认支付、立即支付、转账、发送、删除、下单、提交订单、确认呼叫、呼叫、购买、pay、send、delete、purchase、order；`confirm_before` 只能追加。 | 两分支 |
| S-027 | 授权范围 ONCE / TASK；TASK 按任务与确认词记忆，任务结束清除；每次决策写审计。 | 两分支 |

## 六、记忆与提醒

| 编号 | 事实 | 分支 |
|------|------|------|
| S-011 | 记忆每篇笔记一个 Markdown 文件：permalink `a/b` 落到 `<memory>/a/b.md`；写入为临时文件 + 原子重命名，UTF-8；忽略隐藏文件与目录。 | 两分支 |
| S-013 | 记忆采用 Basic Memory 风格：frontmatter 含 `title/type/permalink/tags`；`## Observations` 行 `- [category] content #tag (context)`；`## Relations` 行 `- relation [[Target]]`。 | 两分支 |
| S-015 | `memory_write` 在已有同名笔记时追加并按 `(category, content)` 去重；`memory_forget` 才真正删除文件。 | 两分支 |
| S-030 | 提醒由 `reminder_set` 设置，时间参数为 ISO-8601 本地时间（如 `2026-11-03T08:00`），按设备时区解析。 | camp/xiaoman |
| S-031 | 提醒使用 `AlarmManager.setAndAllowWhileIdle`：Doze 下可触发，但为非精确定时，不需要精确闹钟权限；重启清空闹钟（无持久化）。 | camp/xiaoman |
| S-032 | 提醒到点由 `ReminderReceiver` 弹出通知；需要 POST_NOTIFICATIONS；应用声明 INTERNET、POST_NOTIFICATIONS、FOREGROUND_SERVICE、FOREGROUND_SERVICE_SPECIAL_USE。 | camp/xiaoman |

## 七、模型客户端、轨迹与测试

| 编号 | 事实 | 分支 |
|------|------|------|
| S-039 | Base URL 默认值为 `https://ark.cn-beijing.volces.com/api/v3`；客户端请求地址为 baseUrl 去尾斜杠后拼 `/chat/completions`。 | 两分支 |
| S-040 | 对 408、409、429、5xx 与传输错误最多重试 2 次，退避 500ms 起或采用 `Retry-After`；provider 错误码 `SetLimitExceeded` 不重试。 | 两分支 |
| S-041 | 端点返回 400 且响应体包含 `response_format` 时，去掉 JSON 模式重试一次，并在本次客户端生命周期内关闭 JSON 模式。 | 两分支 |
| S-042 | 错误信息不含 API Key；轨迹写入对长度 ≥4 的密钥做 `***` 掩码。 | 两分支 |
| S-043 | 轨迹目录 `<external files>/traces/<run_id>/` 内含 `trace.jsonl`、`audit.jsonl` 与 `step-<n>.png`。 | 两分支 |
| S-044 | 日志格式 `<run_id> <EventKind> <json>`；main 的 logcat 标签为 `PhonePal`，课程分支为 `Xiaoman`。 | 两分支 |
| S-045 | 运行 ID：App 为 `app-YYYYMMDD-HHMMSS-xxxx`，CLI 为 `cli-YYYYMMDD-HHMMSS-xxxx`；调试广播可预置 run id。 | 两分支 |
| S-051 | 课程分支记录 `test :app:assembleDebug` 通过，226 次 JUnit 测试执行、0 失败 0 错误（含 debug/release，非 226 个独立场景）。 | camp/xiaoman |

## 八、2026-11-18 复读：新模块与 02 分支

| 编号 | 事实 | 分支 |
|------|------|------|
| S-053 | 新增模块 `core-mcp`、`mcp`、`web-server`、`ios-hands`、`ios-runner`、`deploy`；`settings.gradle.kts` 纳入 core-mcp、ios-hands、ios-runner、web-server。 | main |
| S-054 | MCP：聊天模型同时看到内置工具与 MCP 工具，工具名格式为 `服务器名__工具名`；每个服务器有 `confirm` 策略（writes/all/none）；需确认的调用在没有终端确认时一律拒绝；Key 只放环境变量并做掩码；内置目录在 `catalog.json`。 | main |
| S-055 | 网页版：iPhone 不装 App，用 Safari 添加到主屏幕；不操作手机屏幕，靠 MCP 服务办事；记忆存浏览器 `localStorage`（最新 200 条、约 180KB），服务器不落盘；会话空闲 2 小时清空；网页不能后台提醒，改为「添加到日历」。 | main |
| S-056 | iOS：`ios-hands` 的 `WdaDevice` 通过 WebDriverAgent 实现 `Device`；`ios-runner` 是 Mac 命令行，提供 `tools`、`call`、`ask`、`chat`。 | main |
| S-057 | 示例技能共 11 个，包含课程五个场景与 `set-alarm`、`meituan-takeout-order`、`train-ticket-order` 等。 | main |
| S-058 | `camp/02-skill-builder` 为 versionCode 2 / versionName `0.2.0`；分支含 `SKILL_SAVE` 工具（校验完整 SKILL.md、展示草稿并确认后新建或修改）与 `SkillAuthoringTest`。 | camp/02-skill-builder |
| S-059 | docs 目录含 `ARCHITECTURE.md`、`classroom.md`、`ios.md`、`mcp.md`、`skills.md`、`ui-interaction.md`、`web.md`；README 增加课堂实践、MCP、网页版、iOS 说明。 | main |

## 编码说明

- 采集时点：2026-11-17；2026-11-18 复读补充 S-053~S-059（main HEAD 08cd059）。
- 编号与 01 课包一致；同一编号在两包中指同一条事实。标注「两分支」表示 main 与 camp/xiaoman 一致。
- 与课程文档冲突的项（`chat` channel、02 分支、五个技能、superagent-lead）已在正文中更新；02 分支与五个技能已公开，`chat` 已进入源码枚举。
