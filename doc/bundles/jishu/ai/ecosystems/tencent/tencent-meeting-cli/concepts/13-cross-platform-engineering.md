---
type: Concept
title: "传输、输出与跨平台工程：HTTP 层、枚举转换、日志崩溃与版本沿革"
description: "源码视角的横切机制：thttp 客户端与双代理、诊断请求头、客户端错误码分段与退避重试；16 个枚举文件与 JSON 字节树转换；输出信封中间件族；自研滚动日志与 panic 崩溃上报；CHANGELOG 18 版演进与源码/文档不一致清单。"
tags: [tencent-meeting, tmeet, source-code, http, retry, error-codes, enum, logging, crash-report, changelog]
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

# 传输、输出与跨平台工程

> 本文收口前三篇源码概念未覆盖的横切机制：HTTP 传输与错误处理、枚举与字段转换、输出管道、日志与崩溃上报，以及版本沿革中源码与文档的几处不一致。

## HTTP 层：两个代理与一组诊断头

`internal/core/thttp` 的 DefaultHttpClient：整体 Timeout 3s、MaxIdleConns 200（F-156）。业务请求实际分两条代理路径：

| 代理 | 形态 | 重试/鉴权行为 |
|------|------|---------------|
| cgi-proxy | 泛型 `ProxyRsp{code,message,nonce,data}` | 网络失败时用 DefaultNoProxyHttpClient（绕过代理配置）新建 Request 重试 1 次（F-157） |
| rest-proxy | 开放平台 REST | 每请求先 RefreshToken；最多 retry 3 次；TokenExpired/NotRetry 不重试；服务端码 200190303 判为 token 过期（F-158） |

每个 REST 请求携带的请求头既是诊断链路也是风控指纹（F-159）：

| 头 | 内容 |
|----|------|
| Tmeet-Unique-ID | `<openId>*<machineId>` |
| Tmeet-Device-Info | `os;agent;model`（agent/model 取值 TMEET_AGENT/TMEET_MODEL 环境变量优先于 agent.json，F-193） |
| Tmeet-Open-Source | 固定 `CLI` |
| Tmeet-Cli-Ver | 二进制版本（cmd.Version） |
| Tmeet-Trace | `cmdPath;traceID`；链路 trace 优先取响应头 X-TC-Trace |
| Tmeet-Cli-Name | 38 个 ApiCmd 之一（见 [10](10-command-assembly.md)） |

鉴权头（X-TC-Nonce 等）由 OAuth2Authenticator 附加（F-162）。

### 错误码分段与退避

- 客户端错误码按号段分类（F-160）：1000-1007、2000-2008、3000-3002、4000-4002（事件域，对应用户面 F-098）、9000=Panic；判定用 exception 包的包级函数 `exception.Is(err, target)`（当两边都是 `*TmeetError` 时只比较 Code；TmeetError 类型本身没有 Is 方法，不能靠标准 errors.Is 取巧）。
- 通用重试策略（F-161）：最多执行 4 次（MaxAttempts=3）、100ms 起步、2.0 倍率、3s 封顶、±25% jitter（jitter 即随机抖动，防多客户端同步重试打爆服务端）。用户侧观感是网络抖动被自动消化，但 token 类错误立即失败不反复打接口。

## 枚举体系：16 个文件、23 个实例类型

`internal/utils/enumerate` 实测 16 个非测试枚举文件（F-185），值得单独认识的几类：

- **CorpLockMask**：uint32 位掩码——0x1 文字水印 / 0x2 音频水印 / 0x4 自动录制 / 0x8 自动 ASR。它是 meeting create/update 响应 hints 的来源：企业强制项压过用户入参（用户面 F-044）。
- **InstanceType：实测 23 个成员**（F-186），精确取值集合 {0-10、12、20、21、22、30、32、33、81、82、83、84、86}——包含 Vision Pro（12）、Rooms/Controller 触控设备（20/21/22/30/32/33，注意 23-29、31 缺号）、HarmonyOS 设备（81-84、86，85 缺号）；此外 11 也缺号。解析参会人设备类型时不要假设编号连续。
- 业务枚举（F-187）：MeetingType(0/1/2/4/5/6)、MeetingRecurringType(0-4)、MeetingUserRole(0-7)、RecordState(1/2/3)、RecordType(0/2/3/4/5)、WaitingRoomOperateType（1/2/3，双向映射）等，均与命令参考中的枚举入参一一对应。

## converter：响应 JSON 的字节树变换

converter 包直接在 JSON 字节树上做字段改名/重组（点路径与同名双模式、maxDepth 限深），避免先反序列化成具体结构再序列化（F-188）。常用转换器：

- **TimestampConverter**：以 1e11 为阈值自动判别秒/毫秒时间戳并转 ISO 8601——这是用户面「时间戳字段自动转换」（F-038）的实现；
- **Base64DecodeConverter**：⚠️ 源码实际只处理 **3 种**编码标识，而 CHANGELOG v1.0.18 称支持 4 种（F-189）。以源码为准。

## 输出管道：信封与中间件族

- `formatOutput` 组装统一信封 `{trace_id, message, data, hints}`；事件族走 EventPrint 输出 bare JSON NDJSON（F-190，对应 F-036/F-037）。
- 业务输出中间件（F-190）：

| 中间件 | 作用 |
|--------|------|
| WithConvert | 挂接 converter 字段变换 |
| WithContactSearchLogic | users 恰好 1 条时只保留 open_id（减少成员信息外显） |
| WithMetaFieldFilter | 按 filter_field 裁剪元字段 |
| WithTotalCountLogic | total_count=0 时移除该字段（避免无意义噪声字段进模型上下文） |
| WithHints | 注入 corp_lock_mask 提示（见 [10](10-command-assembly.md)） |

整套中间件的设计取向与洞察三一致：一切为「机器消费时更少噪声、更省 token」服务。

## 自研日志与崩溃上报

**日志**（F-191）：未用第三方库，自研异步日志：

- 文件 `tmeet-YYYY-MM-DD.log`，单文件 10MB 滚动、保留 7 天；bus 用 InitNamed 写 `logs/bus-*.log`；
- 写入经容量 4096 的异步 channel（业务路径不阻塞在磁盘 IO 上）；
- trace_id 为 32 字符 hex：8 字符秒级时间戳 + 4 字符 PID + 20 字符随机。

**崩溃**（F-192）：panic 被根 defer recover 后 POST `/v1/cli/crash`（1s 超时；body 含 operator_id、operator_id_type:2、crash_stack、error_code），栈截断 8192 字符，PanicExitCode=2；运行不产生 coredump 文件——对凭证安全是必要设计（内存映像不落盘，见 [11](11-credential-security-internals.md)）。

## 版本沿革：18 个版本与三处「以源码为准」

CHANGELOG 实测 **18 个**版本条目：v1.0.1（2026-04-07）→ v1.0.18（2026-09-11），**没有 v1.0.0**（F-195）。README/Makefile 里的 v1.0.0 只是构建示例值。五个半月 18 个版本、v1.0.17→v1.0.18 仅隔 2 天，迭代密度很高。

第三轮源码学习确认的「文档/直觉 vs 源码」差异清单（详见 [references/source-code.md](../references/source-code.md)）：

| 议题 | 文档/直觉 | 源码事实 |
|------|-----------|----------|
| 命令定义 | 像 schema 驱动 | 38 ApiCmd 不生成命令/flag，仅用于请求头与 compact（F-130） |
| BuildTime | Makefile 有注入 | Go 侧无此符号，-X 被静默忽略（F-115） |
| postinstall | 像清理跨平台二进制 | 实际执行 auth logout（F-122） |
| 系统 Keychain | 文档统一措辞 | 仅 macOS；Linux 0600 文件、Windows DPAPI（F-149） |
| recording.failed | 头注释提及 | 未注册，实际 8 个事件 key（F-174） |
| Base64 编码数 | CHANGELOG 称 4 种 | 源码 3 种（F-189） |
| 首个版本 | 文案有 v1.0.0 | CHANGELOG 自 v1.0.1 始（F-195） |

工程纪律：CONTRIBUTING 要求 gofmt + go test + 中文注释 + 新功能附测试；SECURITY 承诺仅维护 latest、私域上报、7 工作日响应/30 天修复（F-194）。引用行为时以 v1.0.18 固定 tag 为界，新版本发布后应重新核对上述差异表。

## 相关概念

- [09 - 源码工程总览](09-codebase-architecture.md)｜[10 - 命令装配与中间件](10-command-assembly.md)｜[11 - 凭证安全内部机制](11-credential-security-internals.md)｜[12 - 事件总线内核](12-event-bus-internals.md)
- 用户面横切约定：[02 - 命令体系与全局约定](02-command-map.md)｜[08 - 应用配置与运维反馈](08-app-tshoot.md)

## 延伸阅读

- 信源登记与机械复核统计：[references/source-code.md](../references/source-code.md)
- 核心洞察：[洞察六 · 薄 CLI](../spec/insights.md)
