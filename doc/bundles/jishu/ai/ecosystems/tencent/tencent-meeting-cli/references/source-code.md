---
type: Reference
title: "tencentmeeting-cli 源码主体信源（tag v1.0.18 @ e631b35）"
description: "tencentmeeting-cli Go 源码主体的固定版本快照登记：仓库坐标、模块/目录地图、关键文件锚点、机械复核统计与跨信源口径差异，是概念 09~13（源码内部机制）的唯一事实来源。"
tags: [tencent-meeting, tmeet, reference, source-code, go, cobra, internals, v1.0.18]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: source-code
    resource: https://github.com/TencentCloud/tencentmeeting-cli/tree/v1.0.18
    title: tencentmeeting-cli 源码主体（tag v1.0.18，commit e631b355da2b001d24b82f453b65d96f39c59865，2026-09-11）
---

# tencentmeeting-cli 源码主体信源（v1.0.18）

## 信源元信息

| 项目 | 内容 |
|------|------|
| 仓库 | https://github.com/TencentCloud/tencentmeeting-cli |
| 固定 tag | `v1.0.18`（2026-09-11 发布，对应 npm 包 v1.0.18） |
| commit | `e631b355da2b001d24b82f453b65d96f39c59865` |
| 许可证 | MIT |
| 语言/构建 | Go（module `tmeet`，go 1.22.0）；5 目标 CGO_ENABLED=0 静态交叉编译 + Node 包装器分发 |
| 本地学习副本 | 固定 tag 快照（非 main 浮动分支），所有事实锚点以 `文件:行号` 登记 |
| 采集日期 | 2026-10-04 |
| 对应事实 | F-113 ~ F-199（见 [spec/facts.md](../spec/facts.md) 第十二节） |
| 固定理由 | 文档引用集合（command.md/SKILL.md v1.0.18）∩ 版本变更集合 = ∅；tag 不可变，满足信源稳定性门 G0 |

## 模块地图（cmd / internal 边界）

| 路径 | 职责 | 关键锚点 |
|------|------|----------|
| `main.go` | 唯一入口，一行 `os.Exit(cmd.Execute())` | F-114 |
| `cmd/root.go` | 根命令、全局 flag、启动顺序、annotation preCheck、`var Version="dev"` | F-115、F-125~F-127 |
| `cmd/<域>/` | 10 个命令域（auth/meeting/contact/record/report/control/minutes/tshoot/app/event）的 cobra 装配与 opts | F-128、F-131、F-132、F-136 |
| `internal/core/` | Tmeet 容器、endpoints 四主机、thttp、keychain、filelock、filecheck | F-116、F-117、F-148~F-162 |
| `internal/auth/` | OAuth 设备码三 endpoint、轮询/刷新、token 结构 | F-138~F-141 |
| `internal/config/` | UserConfig/AppMeta/AgentConfig、原子写、ResourceReleaseHook | F-142~F-145 |
| `internal/cmdutil/` | 38 个 ApiCmd 常量、compact schema 拉取与裁剪、分页兼容、EnumValue、hints | F-129~F-135、F-137 |
| `internal/event/` | bus/source/hub/transport/spawner/busdiscover、wsspb、注册表、dedup、IPC | F-163~F-184 |
| `internal/output/` | 信封输出、bare JSON、WithConvert/WithHints 等中间件 | F-190 |
| `internal/utils/enumerate/` | 16 个枚举文件（23 成员 InstanceType 等） | F-185~F-187 |
| `scripts/tmeet.js`、`scripts/cleanup.js` | npm 包装器与 postinstall 钩子 | F-121、F-122 |
| `skills/tmeet-skill/` | SKILL.md（401 行）、references/ 10 篇、scripts/agent_init.py（122 行） | F-124、F-197、F-198 |
| `build.sh`、`Makefile` | 5 目标交叉构建、先测试后编译、ldflags 注入 | F-115、F-119、F-120 |

## 机械复核统计（G4 计数断言原始记录）

以下数字均于 2026-10-04 以 Glob/Grep/PowerShell 对固定 tag 快照独立计数，非人工估计：

| 断言 | 实测值 | 复核方式 |
|------|--------|----------|
| `.go` 文件总数（排除 vendor） | 252（测试 64 + 非测试 188） | Get-ChildItem -Recurse |
| ApiCmd* 常量数 | 38（meeting 12/record 9/report 4/contact 3/control 3/tshoot 2/minutes 3/app 2） | Grep api_schema.go:17-100 |
| 注册 EventKey 数 | 8（schemas.go 中 8 次 RegisterKey） | Grep `RegisterKey(KeyDef` |
| InstanceType 枚举成员 | 23（0-10/12/20-22/30/32/33/81-84/86） | Grep instanceid.go |
| enumerate 非测试文件 | 16 | Get-ChildItem |
| CHANGELOG 版本条目 | 18（v1.0.1~v1.0.18，无 v1.0.0） | Select-String `^##` |
| SKILL.md 行数 / 二级章节 | 401 行 / 9 个 `##` | Get-Count / Select-String |
| docs/command.md（中/英） | 各 1594 行 | 行数统计 |
| Skill references 分命令文档 | 10 篇 | Get-ChildItem |
| EnumValue 实际使用点 | 2 处（control waiting-room、app set） | Grep |
| MarkDeprecated 调用点 | 7 处（report 3/meeting 2/record 2） | Grep |
| WSS 心跳默认间隔 | 25s（`defaultHeartbeatInterval`） | Grep wssource.go:102 |
| bus 每连接发送队列 | 100（`sendChCap`） | Grep bus/conn.go:39 |
| 事件去重环容量 | 512（`DefaultDedupCapacity`） | Grep dedup.go:31 |
| windows 命名管道缓冲 | 65536（`pipeBufferSize`） | Grep transport_windows.go:30 |

## 源码对文档信源的印证、深化与纠正

**印证（实现与文档一致）**：设备码 5s 轮询/300s 超时（F-021/F-023）、信封结构（F-036）、event bare JSON（F-037）、ISO 时间转换（F-038）、page-token 分页（F-039）、ready/exit 契约（F-081）、不读 stdin（F-084）、jq 静默丢弃（F-085）、logout 两阶段 hook（F-032）。

**深化（文档只说 What，源码补 How）**：

- 官方文档「系统 Keychain」（F-025、F-107）仅在 macOS 字面上成立——Linux 主密钥是 0600 的 `master.key` 文件，Windows 主密钥走注册表 + DPAPI；**加密原语三平台统一**（AES-256-GCM、AAD 绑定 open_id），但**业务数据存储载体分叉**：macOS/Linux 写 `<open_id>.enc` 文件，Windows 把 AES-GCM 密文 base64 后写注册表值（不经 DPAPI、无 `.enc` 文件）（F-149~F-151）。
- `--compact` 的字段表来自服务端 `/v1/api/compact-schema` 而非本地 schema 文件，缓存 TTL 服务端下发、失败透明放行（F-133）。
- per-host bus 是带 alive-lock 选举、owner 哈希隔离、引用计数订阅与 drop-oldest 背压的完整单机 IPC 微内核（F-163~F-183）。

**纠正（源码与文档/直觉不符，以源码为准）**：

| 议题 | 文档/直觉口径 | 源码事实 | 事实 |
|------|---------------|----------|------|
| 命令定义来源 | 易被猜为 schema 驱动生成 | 38 个 ApiCmd 常量只做请求头与 compact 裁剪；cobra 命令/flag 全手工、REST 路径硬编码 | F-129、F-130 |
| BuildTime 注入 | Makefile 看似注入构建时间 | Go 中无 BuildTime 符号，-X 被链接器静默忽略 | F-115 |
| postinstall 行为 | 易被猜为清理跨平台二进制 | 实际执行 `tmeet auth logout` 清登录态，失败也 exit 0 | F-122 |
| recording.failed | schemas.go 头注释提及 | 未注册；event list 实际仅 8 个 key | F-174 |
| 结束事件拼写 | 束内 v0.1.0 示例 04 写作 `meeting.ended` | 官方名为 `meeting.end`（schemas.go:44-45 + command.md:1472），已更正旧示例 4 处 | F-173/F-174 |
| Base64 转换编码数 | CHANGELOG v1.0.18 称 4 种 | 源码实际 3 种 | F-189 |
| 首个版本 | 部分旧文案称「v1.0.0 时期」 | CHANGELOG 自 v1.0.1 始，共 18 个版本，无 v1.0.0 | F-195 |
| Windows 业务数据位置 | 包泛化注释/config.go 历史措辞暗示 `.enc` 文件 | 注册表 `HKCU\Software\TmeetCli\keychain` 下同名值（AES-GCM base64），平台注释 + Get/Set 实现为权威 | F-149/F-150 |
| 引用计数退订 | 易被猜为「最后一个消费者离开即退订」 | 1→0 刻意不发 UNSUBSCRIBE，由服务端 TTL 自动取消；重连后 Snapshot Replay | F-175 |
| payload 数组长度 | 易被泛化为「8 个 key 恒为单元素数组」 | 长度 1 契约仅 meeting.started/meeting.end，数组为未来批量推送预留 | F-173 |

## 与其他 9 信源的关系

- 本信源是**实现侧权威**：凡文档与源码冲突，机制解释以本信源为准，用户面文案仍归各文档信源，冲突并列登记不删改；
- 命令参数级行为仍以 [command-reference.md](command-reference.md)（docs/command.md v1.0.18，1594 行）为用户面权威，源码回答「为什么是这样」；
- Agent 行为红线以 [skill-manifest.md](skill-manifest.md) 为权威，源码回答「CLI 自身强制了什么、什么只靠 Skill 约束」。
