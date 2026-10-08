---
type: Concept
title: "命令装配与中间件：手写 cobra 壳与远程驱动的输出契约"
description: "源码视角的命令运行机制：base.go + opts + middleWare.Chain 洋葱装配；38 个 ApiCmd 常量的真实用途；compact 远程字段表全链路；分页兼容、枚举校验、隐藏命令与 hint 结构化装配。"
tags: [tencent-meeting, tmeet, source-code, cobra, middleware, compact, pagination, api-cmd]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: source-code
    resource: /references/source-code.md
    title: tencentmeeting-cli 源码主体（tag v1.0.18 @ e631b35）
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单与 CHANGELOG（v1.0.18）
---

# 命令装配与中间件

> 用户面的 44 个子命令在 [02 - 命令体系与全局约定](02-command-map.md) 已讲清「怎么用」；本文回答源码侧的「怎么装起来」，并澄清一个容易误判的架构问题：tmeet **不是** schema-driven 命令框架。

## 一个叶子命令的标准形态

每个域在 `cmd/<domain>/base.go` 导出 `NewBaseCmd` 挂子命令；叶子命令遵循统一三段式（F-128）：

1. 定义 `XxxOptions` 结构持有参数与依赖；
2. 手工声明 cobra flag（StringVar / IntVar / StringSliceVar / StringArrayVar）；
3. 用洋葱模型包裹业务函数：

```go
middleWare.Chain(opts.Run,
    WithApiCmd(StaticApiCmd(ApiCmdMeetingGetById)),
    // …其他输出/转换中间件
)
```

业务 `Run` 在最内层，外层中间件依次处理鉴权前置、apiCmd 标注、字段转换、compact 裁剪、信封输出。

## 38 个 ApiCmd 常量：它们到底驱动什么

`internal/cmdutil/api_schema.go:17-100` 定义了**实测 38 个** ApiCmd* 字符串常量（F-129）：

| 域 | 数量 | 常量示例 |
|----|------|----------|
| meeting | 12 | meeting_create / meeting_get_by_id / meeting_get_by_code … |
| record | 9 | record_list / record_smart_minutes / record_permission_apply_commit … |
| report | 4 | report_participants / report_job_result … |
| contact | 3 | contact_search / contact_lookup_by_phone/email |
| control | 3 | control_call / control_kick / control_waiting_room |
| minutes | 3 | minute_search / minute_get / minute_get_transient |
| tshoot | 2 | tshoot_log_upload / tshoot_feedback |
| app | 2 | app_info_set / app_info_get |

⚠️ **关键事实（源码证伪）**：这些常量**既不生成 cobra 命令，也不生成任何 flag**（F-130）。它们只有两个消费点：

1. 作为请求头 `Tmeet-Cli-Name` 的值，让服务端知道是哪条业务命令（同时进入 Tmeet-Trace 诊断链路）；
2. 作为 `--compact` 拉取精简字段表时的 `cmd` 参数。

命令是否存在、接受哪些 flag、调用哪个 REST 路径，全部是编译期手工固化的——路径硬编码在各自 Run 里，flag 全靠手工声明（F-130、F-131）。这与洞察六的判断一致：**变化最慢的命令契约发版固化，变化最快的输出字段表才远程化**。

### 一个叶子命令对多个 ApiCmd：FlagSwitch

`meeting get` 同时支持 `--meeting-id` 与 `--meeting-code`，背后是两个 API 形态。代码用 FlagSwitch/FlagSwitchWithDefault 按 flag 出现情况在 `ApiCmdMeetingGetById` 与 `ApiCmdMeetingGetByCode` 间切换（F-132）——实现侧印证了用户面「meeting-id 优先」的规则。

## `--compact` 的完整链路

用户文档只说「精简输出、拉取失败透明放行」（F-077），源码链路为（F-133）：

```
命令运行
  └─ GET https://work.medialab.qq.com/v1/api/compact-schema
       ?operator_id=<openId>&operator_id_type=2&cmd=<apiCmd>&source=CLI
       ├─ 命中 filecache（cache/schema，TTL 由服务端下发）→ 直接用
       └─ 未命中 → per-apiCmd 互斥锁 + double-check 防击穿 → 拉取并缓存
  └─ 输出层 KeepFields(data, depth=10, compactFields) 深度裁剪
  └─ 任一步失败：透明放行，输出完整 data
```

设计要点：字段表是服务端运营项（可以不发版调整给模型看的字段），但失败必须降级为全量而非报错——compact 是优化不是契约。

## 登录前置：annotation 驱动的 preCheck

哪些命令免登录不靠硬编码命令名，而靠 cobra annotation（F-127、F-137）：

- `skipPreCheck=="true"`：整条命令跳过登录检查（auth 自身、event 查询类、隐藏命令）；
- `skipPreCheckFlag`：按 flag 名豁免（如 --help 场景）。

这解释了用户面规则（F-029）的实现方式：`event list/schema/status/stop` 与 auth 三命令正是带此 annotation 的命令集合。

## 新旧分页兼容层

`internal/cmdutil/pagination.go` 同时认识两套分页（F-134）：

- PageTypeOld=0（page/pos/size）与 PageTypeToken=1（page-token/page-size）；
- ChoosePageOrToken / ChoosePosOrToken 自动判断调用方传的是哪种，老脚本无需改造；
- page-size 上限按域不同：meeting/record 30、report 100；
- 旧参数经 MarkDeprecated 标记（实测 7 个调用点：report 3、meeting 2、record 2），与 F-039 的 deprecation 承诺对应。

## 枚举校验：EnumValue 只用在两处

自研 EnumValue 实现 pflag.Value，但全仓**仅 2 处**使用（F-131）：

- `control waiting-room --operate-type`（enter-meeting / back-to-waiting / expel）；
- `app set --layout-style`（sidebar / wide_sidebar / popout）。

其余枚举（会议类型、录制类型等几十种，见 [13](13-cross-platform-engineering.md)）在服务端或响应转换层处理，命令行不做封闭校验——仍是「最小手工约束」风格。

## Hint：一个零引用接口与它的结构化用法

`internal/cmdutil/hints` 包定义了接口 `HintProvider { Hints(string) []string }`，但**该包没有任何 import 者**——接口类型本身零引用（F-135）。实际机制是：

- `meeting create`/`meeting update` 的 Options 各自定义同签名方法 `Hints(responseData string) []string`（create.go:80、update.go:117）；
- 直接把方法值 `o.Hints` 传给 `output.WithHints(fn func(string) []string)`（options.go:80），靠结构化类型对接，不需要 import 接口；
- 提示内容由 `GenerateMeetingSettingsHints` 解析**响应中的 corp_lock_mask 位掩码**生成（企业级强制项优先于用户入参的实现侧来源，对应 F-044）。

## 两个隐藏命令

| 命令 | 作用 | 隐藏方式 |
|------|------|----------|
| `event _bus` | bus 守护进程的真实入口，由 spawner 再 exec 自身拉起 | Hidden + skipPreCheck；`--interval`(5s)/`--idle-timeout` 也 MarkHidden（F-136） |
| `tshoot commands` | DFS（Depth-First Search，深度优先搜索）遍历整棵命令树，列出全部叶子命令 | 面向 Agent 的机器可读自举帮助（F-136） |

`tshoot commands` 的存在值得注意：它让 Agent 不必硬编码命令清单即可发现当前二进制的全部叶子命令（命令面的「版本指纹」接口；对照事件侧封闭注册表，见 [12](12-event-bus-internals.md)）。

## 给二次开发者的结论

1. 不要试图 import ApiCmd 常量做反射式命令生成——它不含路径/参数信息，二开请直接读各 Run；
2. 新增命令的标准动作：opts 结构 + 手工 flag + Chain 包裹 + 一个 ApiCmd 常量（同时要服务端登记该 cmd 的 compact 表）；
3. 依赖 compact 行为时必须容忍全量降级，不要把精简字段当成稳定契约；
4. 排查「为什么这个命令要登录 / 不要登录」看 annotation，不要在 preCheck 里找命令名白名单。

## 相关概念

- [02 - 命令体系与全局约定](02-command-map.md)（用户面 44 命令与全局 flag）
- [09 - 源码工程总览](09-codebase-architecture.md)｜[11 - 凭证安全内部机制](11-credential-security-internals.md)｜[12 - 事件总线内核](12-event-bus-internals.md)｜[13 - 传输、输出与跨平台工程](13-cross-platform-engineering.md)

## 延伸阅读

- 信源登记：[references/source-code.md](../references/source-code.md)
- 核心洞察：[洞察六 · 「薄 CLI」架构](../spec/insights.md)
