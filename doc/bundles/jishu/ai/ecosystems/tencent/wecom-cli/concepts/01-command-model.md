---
type: concept
title: 命令模型：两阶段装配与 schema 驱动解析
description: 解析 wecom-cli 的命令形态、argv 归一、schema 下发后的两阶段 clap 装配、参数三通道与退出码。
tags: [wecom, wecom-cli, command-model]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# 命令模型：两阶段装配与 schema 驱动解析

wecom-cli 的解析器不是一次性写死的 clap 树。它先壳后肉：首阶段只装配"够用来找到服务"的骨架，等服务端 schema 到手后，再为**目标服务**补齐完整的参数与子命令。理解这条主线和四条命令形态，就能解释绝大多数"为什么这个参数不在 help 里""为什么首次调用慢半拍"的问题。

## 一、四种命令形态

文档把命令面归为四类（见 F-046），它们的解析路径并不相同：

| 形态 | 示例结构 | 解析方式 | 鉴权 |
|---|---|---|---|
| 方法调用 | `wecom-cli <service> [resource...] <method> [flags]` | 依据在线 schema 生成完整 clap 子树 | 需要 |
| 元命令 | `wecom-cli <service> --doc` / `--schema` | 骨架层即可识别，按需拉取文档 | 在子命令路径解析前处理 |
| 内建辅助 | `wecom-cli <service> +<helper>` | 由产品层注册的辅助命令，不进 schema | 由 helper 自行决定 |
| 全局命令 | `wecom-cli auth` / `cache` / `schema` | 二进制内建自定义命令 | 视子命令而定 |

`--doc` 与 `--schema` 在服务级就被优先处理：`handle_service_cmd` 先打印本地或远程文档，或把 schema 以 pretty JSON 输出，然后才进入子命令路径解析（见 F-053）。因此它们根本不会走到方法参数装配，这也是"未登录也能看能力边界"的实现基础。`auth`、`cache`、`schema` 三个全局命令则是内建能力（见 F-052），其中 `cache` 与 `schema` 在服务子命令之后追加（见 F-039），`auth` 在未启用 `skip-auth-check` 特性时注册（见 F-057）。

## 二、首阶段：只装配骨架

首阶段装配的输入只有 argv 和本地配置，产出是一棵"可路由"的最小命令树：

1. 根命令注册为 `wecom`（见 F-034）；
2. 若首个位置参数不在已占用名称集合内，就把它当作自定义命令注入，以便承接后续动态 schema（见 F-035、F-036）；
3. 为每个服务挂上骨架节点（服务骨架/内建骨架，见 F-037），并把别名映射一并登记（见 F-038）；
4. 单独拦截 `--version`，按 `XXX.YYY.ZZZ` 三段式输出后直接退出（见 F-042），避免为一个版本号触发发现请求。

随后解析器做"首参归一"（见 F-041）：跳过全局参数，锁定第一个位置参数作为路由键。这个键既可能是服务名，也可能是别名，但此时它还没有子命令，任何方法级参数都无处安放——这就是需要第二阶段的直接原因。

## 三、第二阶段：按需下发 schema

只有在确认为方法调用、且不属于"跳过发现"的情形时，才会进入发现流程（见 F-043）。发现请求只针对**当前目标服务**拉取 schema，再据此把该服务的资源层级、方法名、参数与说明装配成完整 clap 子树（见 F-044）。这样做有两个收益：根 `--help` 不必为 13 个服务各拉一次 schema；未知服务的报错也更早、更便宜。

装配失败会返回本地错误码 `10021`（见 F-045），通常意味着 schema 结构不可消费或装配逻辑拒绝。方法定位采用"显式 method → 资源叶子 → 最后一个位置参数"的优先级（见 F-056），因此 `doc search` 与 `doc <resource> search` 可以落在同一方法上。

## 四、参数的三个通道

参数进入命令有三条通道，优先级与容错各不相同：

| 通道 | 写法 | 适用场景 | 关键约束 |
|---|---|---|---|
| 命名参数 | `--keyword 周报 --limit 10` | 常规调用，schema 已声明 | 必须写在位置参数之前，否则被 clap 当作位置值（见 F-051） |
| 原始 JSON | `--json '{"keywords":["周报"]}'` | 嵌套结构、批量字段 | 会被容错修复器预处理（见 F-135） |
| 键值赋值 | `--set keywords=["周报"] --set limit=10` | 逐项覆盖、增量修改 | 可重复，按顺序应用并覆盖 `--json` 的同名深层值（见 F-050） |

`--json` 的容错修复不是"猜测语义"，而是修补常见手写破损：单引号定界、未加引号的键、被截断的花括号等，仅对对象与数组生效（见 F-135）。这解释了为什么某些"看起来不合法"的 JSON 仍能成功——但不要依赖它来传递有歧义的值。

## 五、内建辅助与提示

`+<helper>` 是保留给产品层的辅助命令语法：辅助命令有自己的运行结果类型，并按"内建/自定义"分类决定是否参与鉴权（见 F-053、F-054、F-055）。需要说明的是，本仓库的二进制**没有注册任何产品辅助命令**（在 `crates/wecom-cli/src` 中检索不到 `.helper(` 调用），因此当前版本 `+<helper>` 只是可扩展位，不是可用功能。

当调用在本地就失败时，错误里可能附带 `SKILL_HINT` 提示（见 F-058）。与 `--json` 解析相关的失败还会给出修复建议，这与 F-135 的修复器是同一套设计的两个面：一个尽量修，一个在修不了时告诉 Agent 下一步怎么做。

## 六、输出与退出码

方法调用成功后，结果统一走 stdout；进度、日志与诊断走 stderr，便于管道消费。分页结果以 NDJSON 形式输出（见 F-074），`--output` 则把结果落到文件并在输出中返回文件元信息（见 F-075）。退出码只有三档（见 F-172）：

| 退出码 | 含义 | 典型触发 |
|---|---|---|
| `0` | 成功 | 方法返回成功，或分页正常结束 |
| `1` | 业务错误 | 服务端拒绝、授权失败、参数语义不合法 |
| `2` | 本地错误 | schema 装配失败（如 10021）、文件沙箱拒绝、参数解析失败 |

业务错误会以 `{"success": false, "error": {"code": ..., "message": ...}}` 的形式打印到 stdout，便于上层区分"命令跑完了但业务失败"与"命令根本没跑起来"。

## 七、延伸阅读

- 服务与业务范围：[/concepts/00-overview.md](/concepts/00-overview.md)
- 解析器所在的 crate 与调用链：[/concepts/02-crate-architecture.md](/concepts/02-crate-architecture.md)
- 鉴权失败与 853004 的处理：[/concepts/03-auth-session.md](/concepts/03-auth-session.md)
- 分页、轮询与传输细节：[/concepts/04-transport-resilience.md](/concepts/04-transport-resilience.md)
- 文件参数为何会被拒绝：[/concepts/05-sandbox-security.md](/concepts/05-sandbox-security.md)