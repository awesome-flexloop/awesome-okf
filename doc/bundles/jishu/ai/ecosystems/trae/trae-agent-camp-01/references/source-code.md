---
type: Reference
title: "小满/PhonePal 源码核验事实登记（S-001~S-051）"
description: "对本地 xiaoman 仓库（main 580fdf7 与远端 camp/xiaoman）逐文件核验的 51 条事实：包名与版本、目录装配、记忆与技能格式、Agent 循环与常量、Sentinel 规则、提醒实现、模型客户端、轨迹与 CLI 输出"
tags: [trae, agent, source-code, verification, memory, sentinel, reminder, cli]
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

# 源码核验事实登记

> **信源说明**：本文件登记对本地仓库 `external/dev/libs/others/xiaoman` 的只读核验结果。`main` 分支为 PhonePal 主线（commit 580fdf7，2026-11-01）；`origin/camp/xiaoman` 为课程版「小满」分支，通过 `git show` 只读读取，未切换工作树。两份代码同源，包名、CLI 名与少量功能不同，事实中逐条标注。
>
> **与课程事实的关系**：课程文档（F 编号）说明「课程怎么讲」；本文件（S 编号）说明「代码怎么写」。二者冲突时，以 S 编号为准并在正文标注差异。

## 一、仓库、版本与设备边界

| 编号 | 事实 | 分支 |
|------|------|------|
| S-001 | 仓库远程为 `git@github.com:aduoge/xiaoman.git`；本地 main HEAD 为 580fdf7（2026-11-01，提交信息「文档中文化并整理 core-agent 代码结构」）。 | main |
| S-002 | 远端存在四个分支引用：`main`、`camp/xiaoman`、`camp/xiaoman-web`、`ios/wda-hands`；未发现课程文档所称的 `camp/02-skill-builder`。 | 远端 |
| S-003 | main 分支 applicationId 与 namespace 均为 `dev.phonepal.app`；camp/xiaoman 分支均为 `dev.xiaoman.app`。 | 两分支 |
| S-004 | 两个分支的 versionCode 均为 1、versionName 均为 `0.1.0`；minSdk 30（Android 11），compileSdk 与 targetSdk 均为 35。 | 两分支 |
| S-005 | 构建需要 JDK 17 与 Android SDK 35；许可证为 MIT。 | 两分支 |
| S-006 | README 写明不支持 iOS：iOS 不允许一个 App 读取或操作其他 App。 | main |
| S-007 | 课程分支含 `docs/classroom.md` 学生手册，写明手机需要 Android 11 及以上、iPhone 不支持、TRAE 负责读代码改代码跑命令。 | camp/xiaoman |

## 二、目录装配与数据位置

| 编号 | 事实 | 分支 |
|------|------|------|
| S-008 | `<external files>` 在课程分支为 `/sdcard/Android/data/dev.xiaoman.app/files`；其下有 `memory/`、`skills/`、`traces/` 三个目录。 | camp/xiaoman |
| S-009 | 内置技能从 APK assets 解压到应用内部目录 `<filesDir>/bundled-skills/`，用户技能目录为 `<external files>/skills/`。 | camp/xiaoman |
| S-010 | 技能仓库按「内置技能在前、用户技能在后」的顺序加载，后者按技能名覆盖前者；用户技能损坏时，同名内置技能保持生效。 | 两分支 |
| S-011 | 记忆每篇笔记对应一个 Markdown 文件：permalink `a/b` 落到 `<memory>/a/b.md`；写入采用临时文件 + 原子重命名，编码 UTF-8；隐藏文件与目录被忽略。 | 两分支 |
| S-012 | 删除笔记会删除对应文件并清理空目录；读取可接受 permalink 或标题；检索索引按文件 mtime 与大小同步。 | 两分支 |

## 三、记忆格式

| 编号 | 事实 | 分支 |
|------|------|------|
| S-013 | 记忆采用 Basic Memory 风格的 Markdown：frontmatter 含 `title`、`type`、`permalink`、`tags`；正文 `## Observations` 下每行 `- [category] content #tag (context)`；`## Relations` 下每行 `- relation [[Target]] (context)`。 | 两分支 |
| S-014 | 代码自行实现该格式，未内嵌 Basic Memory（AGPL-3.0）代码；正文中的 `[[wiki 链接]]` 会转成 `links_to` 关系。 | 两分支 |
| S-015 | 记忆写入工具在已有同名笔记时追加观察与关系，并按 `(category, content)` 与 `(type, target)` 去重；`memory_forget` 才真正删除文件。 | 两分支 |

## 四、Agent 与操作循环

| 编号 | 事实 | 分支 |
|------|------|------|
| S-016 | 聊天模型可用工具为 `memory_search`、`memory_read`、`memory_write`、`memory_forget`、`list_skills`、`reminder_set`、`phone_task`。 | camp/xiaoman |
| S-017 | AgentConfig 默认值：`maxSteps=30`、`stuckRepeats=3`、`historyWindow=8`、`maxNodes=120`、`learnFromSuccess=true`。 | 两分支 |
| S-018 | 设置页可调 `maxSteps` 范围为 1..200；两个模型各自有 Base URL、模型名、API Key 与温度（0..2）；聊天与操作两个模型都配置完成才算整体 configured。 | 两分支 |
| S-019 | 操作循环每步：观察屏幕 → 以 JSON 模式请求操作模型 → 宽松解析回复（最多 3 次解析失败）→ Sentinel 授权 → 执行 → 卡死检测；连续 3 次屏幕不变先警告模型，再次卡住则失败。 | 两分支 |
| S-020 | 操作动作类型为 `tap`、`long_press`、`swipe`、`type`、`back`、`home`、`launch`、`deeplink`、`wait`、`ask_user`、`finish`；坐标归一化到 0..1000。 | 两分支 |
| S-021 | 课程分支 Agent 常量：`MAX_TOOL_ROUNDS=8`、`HISTORY_LIMIT=20`、`MEMORY_HITS=5`、`MAX_HOWTO_NOTES=3`；成功路径写入 `howto/<技能名或包名>`，类型与标签均为 `howto`。 | camp/xiaoman |
| S-022 | 操作提示词按顺序拼装：目标（或子目标）、技能说明、技能引用的记忆、命中的 howto 笔记、最近 `historyWindow` 步历史、上一步反馈、节点列表（≤`maxNodes`）与截图。 | 两分支 |
| S-023 | 聊天历史保存在内存中，课程分支上限为 20 条 user/assistant 消息；一轮对话最多 8 个工具轮次。 | camp/xiaoman |

## 五、安全闸门

| 编号 | 事实 | 分支 |
|------|------|------|
| S-024 | 拒绝规则：受保护（FLAG_SECURE）屏幕上的设备操作除 `back`、`home`、`wait` 外一律拒绝；向密码框输入拒绝；技能声明 `apps` 时操作清单之外的包拒绝（启动器与 App 自身除外）。 | 两分支 |
| S-025 | 询问规则：`tap`、`long_press`、`type` 的目标文字或节点文字命中确认词时询问；`deeplink` 与技能模板的 scheme 和 host 都不匹配时询问。 | 两分支 |
| S-026 | 内置确认词共 17 个：支付、付款、确认支付、立即支付、转账、发送、删除、下单、提交订单、确认呼叫、呼叫、购买、pay、send、delete、purchase、order；技能的 `confirm_before` 只能追加，不能删除内置词。 | 两分支 |
| S-027 | 授权范围分「仅一次（ONCE）」与「本次任务（TASK）」；TASK 授权按任务与确认词记忆，任务结束时清除；每次决策写入审计记录。 | 两分支 |
| S-028 | 课程分支实测记录：vivo V2141A / Android 14 上任务 `app-20261102-225742-pc64` 执行 10 个手机动作、经过 2 次「允许一次」，停在确认订单页；页面为 A5 笔记本 2.40 元包邮，未提交订单或支付。 | camp/xiaoman |
| S-029 | 前端确认卡片优先展示「暂不允许」与「允许一次」，「同类操作都允许」收在更多选项；批准后仍需回到目标 App 重新核对页面。 | camp/xiaoman |

## 六、提醒

| 编号 | 事实 | 分支 |
|------|------|------|
| S-030 | 提醒由聊天工具 `reminder_set` 设置，时间参数为 ISO-8601 本地时间（如 `2026-11-03T08:00`），按设备时区解析。 | camp/xiaoman |
| S-031 | 提醒调度使用 `AlarmManager.setAndAllowWhileIdle`：Doze 下也会触发，但属非精确定时，不需要精确闹钟权限；手机重启会清空闹钟，代码注释写明尚无持久化。 | camp/xiaoman |
| S-032 | 提醒到点由 `ReminderReceiver` 弹出通知；通知需要 POST_NOTIFICATIONS 权限；应用声明了 INTERNET、POST_NOTIFICATIONS、FOREGROUND_SERVICE、FOREGROUND_SERVICE_SPECIAL_USE 四项权限。 | camp/xiaoman |

## 七、技能

| 编号 | 事实 | 分支 |
|------|------|------|
| S-033 | 技能 frontmatter 的合法键恰为七个：`name`、`description`、`apps`、`channel`、`confirm_before`、`memory`、`deeplinks`；出现未知键即报错。 | 两分支 |
| S-034 | `name` 必填且匹配 `[a-z0-9-]+`，应与文件夹同名；`description` 必填、非空、单行；`apps` 每项须为包名；`deeplinks` 每项须为 `scheme://...`。 | 两分支 |
| S-035 | `channel` 取值为 `api`、`cli`、`deeplink`、`gui`（默认）、`deeplink-then-gui`、`mixed`；源码中没有 `chat` 取值。 | 两分支 |
| S-036 | `flow.yaml` 仅在 `SKILL.md` 本身有效后才校验；步骤类型为 `launch`、`deeplink`、`ai`、`confirm`、`tap`、`type`、`wait`、`assert`；每步恰好一个 `类型: 值`；`wait` 取 0..600000 毫秒。 | 两分支 |
| S-037 | 课程分支内置示例技能含 `set-alarm`；其 `channel: gui`，操作系统时钟包（`com.android.deskclock`、`com.google.android.deskclock`、`com.android.BBKClock`），规则为只新增闹钟、不编辑或删除已有闹钟。 | camp/xiaoman |
| S-038 | 课程二文档提到的 `today-plan`、`health-alarms`、`taobao-compare`、`daily-quiz`、`ai-news-brief` 五个技能，在公开的 camp/xiaoman 分支技能目录中均未出现。 | 远端 |

## 八、模型客户端

| 编号 | 事实 | 分支 |
|------|------|------|
| S-039 | 设置页 Base URL 默认值为 `https://ark.cn-beijing.volces.com/api/v3`；客户端请求地址为 baseUrl 去掉尾部斜杠后拼 `/chat/completions`。 | 两分支 |
| S-040 | 客户端对 408、409、429、5xx 与传输错误最多重试 2 次，退避从 500ms 起或采用服务端 `Retry-After`；provider 错误码为 `SetLimitExceeded` 时不重试。 | 两分支 |
| S-041 | 若端点返回 400 且响应体包含 `response_format`，客户端会去掉 JSON 模式重试一次，并在本次客户端生命周期内关闭 JSON 模式。 | 两分支 |
| S-042 | 错误信息不包含 API Key；轨迹写入时对长度不少于 4 的密钥做 `***` 掩码。 | 两分支 |

## 九、轨迹、日志与开发者 CLI

| 编号 | 事实 | 分支 |
|------|------|------|
| S-043 | 轨迹目录为 `<external files>/traces/<run_id>/`，内含 `trace.jsonl`（每事件一行）、`audit.jsonl`（每次 Sentinel 决策一行）与 `step-<n>.png`（逐步截图）。 | 两分支 |
| S-044 | 日志格式为 `<run_id> <EventKind> <json>`；main 分支 logcat 标签为 `PhonePal`，课程分支为 `Xiaoman`。 | 两分支 |
| S-045 | 运行 ID：App 生成 `app-YYYYMMDD-HHMMSS-xxxx`，CLI 生成 `cli-YYYYMMDD-HHMMSS-xxxx`；调试广播可预置 run id，使 CLI 指定的 id 与轨迹目录一致。 | 两分支 |
| S-046 | 开发者 CLI：main 分支入口 `cli/phonepal.py`，课程分支入口 `cli/xiaoman.py`；命令为 `lint`、`push`、`run`、`stop`、`logs`、`traces pull`、`traces show`；全局 `--adb` 与 `--serial/-s` 可写在子命令前后。 | 两分支 |
| S-047 | `lint` 按 App 相同规则校验，问题输出 `path:line: message`，有问题的退出码为 1；摘要行输出到 stderr，格式为 `N skill(s) checked, N ok, N problem(s)`。 | 两分支 |
| S-048 | `push` 先 lint，未通过则拒绝推送；通过后删除并重建远端 `skills/<name>/`，逐个 `adb push` 文件，再广播 `RELOAD_SKILLS`；成功时输出 `pushed <本地目录> -> <远端目录> (<文件列表>)` 与 `skills reloaded; ...`。 | 两分支 |
| S-049 | `traces show` 在本地找不到该 run id 时会先 `adb pull`；`logs` 持续读取 logcat，可按 `--run-id` 过滤；`run --follow` 直到 `PhoneTaskFinished`/`Failed`，成功退出码 0。 | 两分支 |
| S-050 | 课程分支手册给出的成功判据为：lint 显示 `0 problem(s)` 与 push 后 `skills reloaded`，再在手机上原样复测。 | camp/xiaoman |
| S-051 | 课程分支 `test :app:assembleDebug` 通过，记录 226 次 JUnit 测试执行、0 失败 0 错误（含 debug/release，并非 226 个独立场景）。 | camp/xiaoman |

## 编码说明

- S-001~S-051 为源码与仓库文档的只读核验结果，采集于 2026-11-17。
- 标注「两分支」的事实表示 main 与 camp/xiaoman 一致；「camp/xiaoman」表示仅课程版具备。
- 课程文档与源码冲突的项（包名、CLI 入口、channel 取值、02 分支与五个技能的存在性）在正文中逐条标注，不静默覆盖课程口径。
