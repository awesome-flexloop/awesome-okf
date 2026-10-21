---
type: Reference
title: "VibeKnow CLI 编号事实清单（F-001~F-104）"
description: "以 v0.9.2 @ 93a26eca 固定信源逐条采集的 104 条编号事实，每条标注仓库内相对路径与行号，数量陈述附统计口径"
tags: [vibeknow, cli, 事实清单, 可溯源, source-code]
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

# VibeKnow CLI 编号事实清单（F-001~F-104）

本文是 VibeKnow CLI 教程全束的事实底座。信源为仓库 tag `v0.9.2`、commit `93a26eca3383d480148c5cfd8da7995ee3352187`、remote `git@github.com:vibeknow/cli.git`，提交时间 2026-09-09 14:56:00 +0800（`chore(release): 0.9.2`），工作树干净。

**路径约定**：所有路径为仓库内相对路径，不使用 `file:///` 与本机绝对路径。
**数量纪律**：凡「X 个 / Y 处 / N 类」类陈述均由独立脚本产出，原始匹配数与去重名数分列，统计口径随条目附注。

## 一、信源与形态

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-001 | 信源固定在 tag `v0.9.2`、commit `93a26eca3383d480148c5cfd8da7995ee3352187`，remote `git@github.com:vibeknow/cli.git` | `git describe --tags`；`git rev-parse HEAD` | 仓库共 18 个 tag（v0.1.0…v0.9.2） |
| F-002 | 仓库自述为基于 Cobra 的 Go CLI，附带 npm 分发包装 | `AGENTS.md:1` | — |
| F-003 | 模块路径 `github.com/vibeknow/cli`，Go 工具链声明 `go 1.25.0` | `go.mod:1`、`go.mod:3` | — |
| F-004 | 直接依赖 10 个条目，含 `spf13/cobra v1.10.2`、`spf13/pflag v1.0.9`、`gopkg.in/yaml.v3 v3.0.1` 等 | `go.mod:7-25` | 按 `require` 块逐行计 |
| F-005 | 顶层目录：`cmd/`、`internal/`、`client/`、`skills/`、`tests/`、`npm/`、`scripts/`、`.github/`，另有 `main.go`、`go.mod`、`package.json`、`AGENTS.md`、`build.sh` | 仓库目录树 | — |
| F-006 | `build.sh` 交叉编译 5 个平台，二进制名 `vibeknow`（Windows 为 `vibeknow.exe`） | `build.sh:1-40` | — |

## 二、命令树与旗标

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-007 | 顶层注册命令目标 19 个：13 个分组命令 + 6 个非分组命令 | `cmd/root.go:88-102` 及 `cmd/doctor.go`、`cmd/completion.go`、`cmd/update.go`、`cmd/version.go` 的 `init()` | 脚本原始输出 20 项，其中 `apicmd` 与 `Cmd` 为正则把 `apicmd.Cmd` 切开的伪影 |
| F-008 | 分组子命令共 41 个 | `count_command_tree.py` | 以 `AddCommand` 调用点为准 |
| F-009 | `vk video` 下挂 13 个子命令 | `cmd/video/*.go` | `cmd/video/` 下 15 个 `.go` 文件中 `helpers.go` 与 `video.go` 不含独立子命令 |
| F-010 | 根命令挂 3 个持久旗标：`--profile`、`--output`、`--verbose` | `cmd/root.go` | — |
| F-011 | `cmd/` 旗标注册调用 104 处；（文件, 旗标名）去重 103 对；旗标名全局去重 72 个 | `count_facts2.py` | 括号配对抓取完整实参后取首个字符串字面量 |
| F-012 | `vk create` 拥有 23 个自有旗标 | `cmd/create.go:832-856`（22）+ `cmd/create_preset.go`（1） | 按旗标名去重 |
| F-013 | `cmd/video/` 旗标（文件, 旗标名）去重对 44 个 | `count_facts2.py` | — |
| F-014 | 未知旗标触发 `clerr.Validation`（退出码 2），并按 Levenshtein 距离给出最接近旗标名 | `cmd/exitcode.go:28-35`、`54-56` | — |
| F-015 | `usagePrefixes` 收录 9 条 cobra 命令行解析失败前缀 | `cmd/exitcode.go:104-127` | 脚本计数 9 |
| F-016 | `vk api call` 支持 `--service`、`--method`、`--path`、`--body` 4 个旗标 | `cmd/api/call.go` | — |
| F-017 | `vk profile add` 支持 8 个旗标 | `cmd/profile/add.go` | — |

## 三、退出码与失败类型

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-018 | `internal/clerr` 定义 6 个退出码常量：0/1/2/3/4/5 | `internal/clerr/clerr.go:25-30` | 源码注释译述 |
| F-019 | `internal/clerr` 定义 5 个失败类型字符串：`validation`、`auth`、`network`、`api`、`internal` | `internal/clerr/clerr.go:15-19` | 脚本计数 5 |
| F-020 | 退出码 8 常量名 `ExitBlocked`（`internal/cmdutil/gate.go:28`）；6 与 7 无命名常量，以 `WithCode(n)` 内联 | `internal/cmdutil/gate.go:28` 等 | 使用点分布：6 共 9 处，7 共 1 处 |
| F-021 | 退出码 4 亦覆盖 `rate_limited`、`internal_error`、`concurrent_work_limit`、`work_edit_busy` | `AGENTS.md:73-75` | 后端码名按字面量保留 |
| F-022 | 退出码 5 亦覆盖 `insufficient_credits` | `AGENTS.md:76-78` | — |
| F-023 | 阻塞至终态的命令以终态状态作为退出码；单次读取型命令退出 0 并在载荷中报告状态 | `AGENTS.md:160-167` | — |

## 四、付费授权门（exit 8）

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-024 | `cmdutil.Gate` 四级解析：授权声明 → 令牌校验 → TTY 交互 → 写出决策并以退出码 8 结束 | `internal/cmdutil/gate.go:56-75` | — |
| F-025 | 两个授权边界类型：`export_confirmation`（`session_id`/`credits`/`operation`）与 `scene_edit_confirmation`（`session_id`/`scene_index`/`script_only`/`from`/`to`） | `internal/cmdutil/gate.go:30-42`；`AGENTS.md:139-142` | 两处一致 |
| F-026 | `action_id` 为 `act_` 前缀 + HMAC-SHA256 十六进制摘要前 24 位 | `internal/pending/pending.go:51`、`102-112` | 前缀常量 `TokenPrefix = "act_"` |
| F-027 | 规范化载荷按键名排序后以 `k=<json值>;` 拼接 | `internal/pending/pending.go:133-151` | JSON 序列化失败时跳过该键 |
| F-028 | 铸造密钥位于 `<config-dir>/action.key`，为 32 字节 `crypto/rand` 随机值，目录 0o700、文件 0o600 | `internal/pending/pending.go:153-159` 及 `secret()` | 校验用 `subtle.ConstantTimeCompare` |
| F-029 | 阻塞输出落在 stdout：json 为 `pending_actions[]`，ndjson 为 `type="action.required"`，text 为 `status=blocked` + `action_id=` + `resume=` | `internal/cmdutil/gate.go` 的 `block()` | 载荷含 `options[].effect`（`resume`/`none`）与完整 `resume_command` |
| F-030 | `vk video export` 恢复命令形态为 `vk video export <task_id> --session-id <sid> --confirm <token>` | `cmd/video/export.go:64-73` | — |
| F-031 | `vk video edit` 恢复命令形态为 `vk video edit <task_id> --session-id <sid> --scene <n> --script <quoted> [--script-only] --confirm <token>` | `cmd/video/edit.go:316-323` | 脚本文本经 `shellQuote` 转义 |
| F-032 | 令牌为「证据边界」而非安全边界 | `AGENTS.md:123-127` | 源码注释同义 |

## 五、exit 6 的三态投递判定

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-033 | 退出码 6 详情载荷含 `delivery` 与 `resend_safe`；`delivery` 取 `submitted` / `not_submitted` / `indeterminate` | `internal/cmdutil/unknown.go` | — |
| F-034 | `resend_safe` 仅在 `delivery == not_submitted` 时为 true | 同上 `ResendSafe()` | 判定式 `u.Delivery == DeliveryNotSubmitted` |
| F-035 | 三态判据：已有 work 行 / 后端 not_found / 探针失败 | `AGENTS.md:88-92` | — |
| F-036 | 退出码 6 覆盖预算耗尽、流无终止事件、任务暂停三种情形 | `AGENTS.md:59-63` | — |

## 六、输出格式与事件通道

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-037 | 输出格式 3 种：`text`、`json`、`ndjson`；非法取值返回失败而非静默回落 | `internal/output/format.go:11-15`、`52-62` | — |
| F-038 | 格式优先级：显式 `--output` > `VIBEKNOW_OUTPUT` > 默认 `text`；`flagSet` 区分「传了空串」与「未传」 | `internal/output/format.go:42-50` | — |
| F-039 | 源码注释明确不做「检测管道自动切 JSON」 | `internal/output/format.go:22-25` | 对齐 gh / kubectl / docker |
| F-040 | 结构化进度事件走 stderr，每行以 `vk_event=` 前缀开头 | `internal/events/events.go:1-17`、`29` | — |
| F-041 | 事件默认仅在 `--output json` 时开启；`VIBEKNOW_EVENTS` 取 `1`/`on`/`true`/`stderr` 开、`0`/`off`/`false`/`none` 关；ndjson 模式事件留在 stdout | `internal/events/events.go:60-79` | — |
| F-042 | 事件为建议性质：`Emit` 丢弃写入失败，不向调用方返回失败 | `internal/events/events.go:37-58`、`86-96` | — |

## 七、预览产物、运行账本与异步语义

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-043 | 预览资产类型 `cover_image`（KindCover）与 `video_playback`（KindVideo）；事件类型 `resource_ready` 与 `resource_preview_warning` | `internal/preview/preview.go:38-47` | — |
| F-044 | 预览交付按内容 sha256 哈希去重，写入采用临时文件 + rename | `internal/preview/preview.go:96`、`157`、`215` | — |
| F-045 | 源资源 URL 不进入事件载荷 | `internal/preview/preview.go` | 源码注释记录签名 URL 等同发布凭据 |
| F-046 | 账本路径 `<config-dir>/jobs.jsonl`；状态 6 个：`submitted`、`running`、`succeeded`、`failed`、`unknown`、`paused` | `internal/jobs/jobs.go:39-44`、`77-82` | — |
| F-047 | 账本写入为单次 `O_APPEND` 追加；行数超 `compactThreshold = 2000` 时改写文件 | `internal/jobs/jobs.go:72`、`111`、`125` | — |
| F-048 | 账本写入为尽力而为：失败在 stderr 告警，不使运行失败；条目缺失表示「此处未记录」 | `AGENTS.md:181-184` | — |
| F-049 | 目标解析三级顺序：显式 `--session-id` → 本地账本 → 后端最近 work；仅给 task_id 时不做远程解析 | `cmd/video/helpers.go:56-120` | — |
| F-050 | `--async` 不跳过启动流水线；`asyncDetachTimeout = 60 * time.Second` 为等待首个流事件的上限，触顶不致命但会报告 | `cmd/create.go:61-65` | — |
| F-051 | `--async` 与 `--export` 互斥，组合返回退出码 2 | `cmd/create.go:122-124` | — |
| F-052 | 同步导出轮询在取消或超时时以退出码 6 结束；导出失败以 `WithCode(7)` 结束 | `cmd/video/export.go:123`、`128`、`150` | — |
| F-053 | 后端导出对同一 (user, session) 幂等，返回同一 task_id | `cmd/video/export.go` | — |

## 八、create 参数域与正交组合

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-054 | `--mode` 接受 4 档：`replica`、`image`（线上 `image2`）、`handdraw`（线上 `hand-draw`）、弃用别名 `script`；空值表示不指定 | `cmd/create.go:1191-1208` | 弃用别名命中时向 stderr 输出告警 |
| F-055 | `--engine` 接受 2 档：`pipeline`（`EnginePipeline = 0`）与 `agent`（`EngineAgent = 1`） | `cmd/create.go:1310`；`client/figlens/engine.go` | 端点分别为 `/v1/agent3forVideo/stream` 与 `/v1/agent2forVideo/stream` |
| F-056 | agent 引擎与 `replica` / `image2` / `hand-draw` 的任意组合返回校验失败 | `cmd/create.go:1327`、`141-143` | 校验位于上传与计费之前 |
| F-057 | agent 引擎禁用 `--theme` 与 `--language`；agent 引擎禁用 `--avatar`；`hand-draw` 禁用 `--avatar`；`replica` 禁用 `--images`；agent 引擎禁用 `--images` | `cmd/create.go:155-197` | 各条均为 `clerr.Validation` |
| F-058 | `--pages` 取值范围 0..20，且仅在 `image2` 下可用 | `cmd/create.go:144-151` | 上界对应后端 `Image2MaxPageCount` |
| F-059 | `--aspect` 归一为 `horizontal` / `vertical`；`16:9` 与 `9:16` 为别名 | `cmd/create.go:1241-1251` | — |
| F-060 | `--language` 允许 7 个取值：`zh-CN`、`en-US`、`es-ES`、`fr-FR`、`pt-BR`、`ja-JP`、`ko-KR` | `cmd/create.go:1258` | — |
| F-061 | `--images` 接受逗号分隔的 1 基索引；重复与空白被容忍，非正整数或非数字返回校验失败；空输入透传为 nil | `cmd/create.go:1214-1237` | 与 `vk doc images` 打印编号一致 |
| F-062 | `--from` 四分支：文本或 `-` → 上传文本；`doc_id` → 直接使用且必须配 `--kb-id`；`http(s)` URL → 上传 URL；其余按本地文件 | `cmd/create.go:220-243` | — |
| F-063 | `--text` 与 `--from` 同时出现或同时缺失均返回校验失败 | `cmd/create.go:107-116` | — |
| F-064 | `doc_id` 识别正则接受 `doc_` 前缀加 8 位以上字母数字，或 8-4-4-4-12 小写十六进制 UUID | `cmd/create.go:73-82` | — |
| F-065 | 校验顺序：preset 展开 → text/from 互斥 → async+export 互斥 → mode → aspect → engine → engine+mode 组合 → pages → theme/language → avatar → images | `cmd/create.go:103-198` | preset 展开位于 `RunE` 起始处 |
| F-066 | `--voice` 在任何上传动作之前解析 | `cmd/create.go:200-215` | — |

## 九、preset 契约

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-067 | preset 允许的 `create` 旗标 14 个 | `internal/preset/preset.go:80-95` | 脚本计数 14 |
| F-068 | preset 拒绝的键 9 个，每个附带拒绝理由 | `internal/preset/preset.go:100-110` | 脚本计数 9 |
| F-069 | preset 展开跳过用户已显式设置的旗标（`pflag` 的 `Changed` 标志） | `internal/preset/preset.go` 的 `Apply(fs *pflag.FlagSet, f *File)` | — |
| F-070 | preset 的 `schema_version` 不等于 `1` 时被拒绝读取；顶层拼错的键由 `dec.KnownFields(true)` 拒绝 | `internal/preset/preset.go:64`、`203-207` | — |
| F-071 | preset 搜索目录 `<config-dir>/presets`；裸名称按 `.yaml`/`.yml` 查找；不存在时提示信息附可用名称；无 `vk preset list` 子命令 | `internal/preset/preset.go:112-119`、`132-162` | — |
| F-072 | preset 展开失败一律以退出码 2 结束，发生在上传之前 | `cmd/create_preset.go` | — |

## 十、字幕样式与工作修改

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-073 | 字幕样式采用「读-改-写」方式写入 | `cmd/video/set.go:195-197` | 后端整体保存样式 |
| F-074 | 写入前以 `figlens.ParseSubtitleStyle(work.SubtitleStyle)` 解析既有样式再逐字段覆盖 | `cmd/video/set.go:197` | — |
| F-075 | 字幕样式旗标 10 个 | `cmd/video/set.go:43-47` | — |
| F-076 | `--subtitle-preset` 的应用顺序在其它字幕旗标之前 | `cmd/video/set.go:199-236` | preset 先落，单个旗标后落并覆盖 |
| F-077 | `strokeWidth` 取值 0 表示无描边，样式合并以指针字段保留「0」与「未设置」的区别 | `cmd/video/set.go:229`、`449` | — |
| F-078 | `--subtitle-stroke-width` 取值范围 0..12（`figlens.SubtitleStrokeWidthMax`） | `cmd/video/set.go:326-329` | — |
| F-079 | `vk video set` 触及 work 的旗标为 `bgm`、`bgm-volume`、`subtitle` 加 10 个字幕样式旗标；`--title` 不在其中 | `cmd/video/set.go:51`、`98-103` | — |
| F-080 | 任何 work 级修改都会使已渲染 MP4 失效；改名 `--title` 为例外 | `cmd/video/set.go:49-51`、`78-81` | — |

## 十一、批量清理安全契约

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-081 | `vk kb prune` 必须至少带 `--pattern` 或 `--older-than` 其一，否则退出码 2 | `cmd/kb/prune.go` 的 `validatePruneFilters` | — |
| F-082 | `vk kb prune` 默认走 dry-run，json 输出含 `dry_run: true`、`matched` 计数与 `items` 列表；加 `--yes` 才执行删除 | `cmd/kb/prune.go` | — |
| F-083 | `vk kb prune` 分页尺寸常量 `prunePageSize = 100` | `cmd/kb/prune.go` | — |
| F-084 | `vk jobs prune` 接受 `--terminal`、`--older-than`、`--all`；裸调用被拒绝 | `cmd/jobs/prune.go`；`AGENTS.md:176-179` | — |
| F-085 | `vk kb delete` 保留交互提示：销毁性但不计费 | `AGENTS.md:157-158` | — |

## 十二、后端端点与规模

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-086 | `client/` 下 4 个服务客户端：`account`、`figlens`、`vectoria`、`vibeknow` | `client/` 目录树；`internal/endpoints/defaults.go` | — |
| F-087 | 后端端点路径去重合计 39 个：`account` 5、`figlens` 26、`vectoria` 6、`vibeknow` 2 | `count_endpoints.py` | 仅取 `client/` 非测试文件中 HTTP 调用实参里的 `/v` 开头路径字面量，`fmt.Sprintf` 格式串归一化为 `{param}` |
| F-088 | `account` 端点 5 个 | `client/account/` | 见 [backend-endpoints.md](backend-endpoints.md) |
| F-089 | `vectoria` 端点 6 个 | `client/vectoria/` | 见 [backend-endpoints.md](backend-endpoints.md) |
| F-090 | `vibeknow` 端点 2 个 | `client/vibeknow/` | 见 [backend-endpoints.md](backend-endpoints.md) |
| F-091 | `figlens` 端点 26 个 | `client/figlens/` | 见 [backend-endpoints.md](backend-endpoints.md) |
| F-092 | i18n 词条 392 条，去重后 196 条 | `internal/i18n/strings.go` | 计数为源码词条数，中文与英文各占一份 |
| F-093 | `internal/` 各包非测试代码行数合计 6803 行；前三为 `httpclient` 861、`cmdutil` 812、`keychain` 558 | `count_endpoints.py` | 按 `len(splitlines())` 计，排除 `*_test.go` |
| F-094 | 配置目录解析顺序：`VIBEKNOW_CONFIG_HOME` > `%AppData%/vibeknow` > `$XDG_CONFIG_HOME/vibeknow` > `~/.config/vibeknow`；profiles 为 `<config-dir>/profiles.yaml` | `internal/config/path.go:12-30` | 目录不自动创建 |

## 十三、统一快照契约

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-095 | `internal/video/snapshot` 定义统一快照结构 `Snapshot` | `internal/video/snapshot/snapshot.go:20` | 字段含 TaskID、SessionID、WorkID、Engine、Title、DurationMs、CoverURL、Preview、Export、NextActions |
| F-096 | 快照状态常量 4 个：`idle`、`running`、`succeeded`、`failed` | `internal/video/snapshot/snapshot.go:53-56` | — |
| F-097 | 预览就绪判定为「work 状态为 Active 且分享令牌非空」 | `internal/video/snapshot/snapshot.go:97` | — |
| F-098 | 快照渲染分三种：`RenderText`（键值块 + stderr 提示行）、`Render`（按格式分派）、`RenderNDJSON`（载荷置 `type="snapshot"`） | `internal/video/snapshot/snapshot.go:146`、`176`、`190` | — |
| F-099 | `Target(taskID, sessionID)`：task_id 为 0 时输出 `--session-id <sid>` | `internal/video/snapshot/snapshot.go:243` | — |
| F-100 | `nextActions` 按导出状态分四支给出后续动作 | `internal/video/snapshot/snapshot.go:250-273` | idle / running / succeeded / failed |

## 十四、AI Skill 资产

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-101 | `skills/` 下 3 个 Skill：`vibeknow-core`、`vibeknow-create`、`vibeknow-doc`；连同 references 目录共 12 个文件 | `skills/` 目录树 | SKILL.md 行数 131 / 438 / 109 |
| F-102 | Skill frontmatter 含 `name`、`description`、`version`（0.9.2）、`emoji`、`homepage`、`allowed-tools`（`Bash(vibeknow:*)`）、`metadata.openclaw.requires.bins/install/primaryEnv/envVars` | `skills/vibeknow-create/SKILL.md:1-30` | — |
| F-103 | `vibeknow-create` 运行契约含三条硬约束：不重复执行 `vibeknow create`；不合并两个流（`2>&1` 破坏契约）；不自行编造 `--confirm` 值、不主动追加 `--yes` | `skills/vibeknow-create/SKILL.md`（Run Contract 段） | — |
| F-104 | `vibeknow-create` 工作流分 4 阶段：outline → tts → render → publish | `skills/vibeknow-create/SKILL.md` | — |

## 审计轨迹

| 轮次 | 事项 | 处理 |
|---|---|---|
| R1 | 旗标计数脚本 v1 只匹配「首参为字符串字面量」的注册形式，漏掉 `StringVar`/`BoolVar`/`IntVar` 等指针首参形式 | v2 改为括号配对抓取完整实参列表再取首个字符串字面量，分列「(文件,旗标名)去重对数」与「旗标名全局去重数」两个口径，得出 103 / 72（F-011） |
| R2 | 退出码常量在 `cmd/exitcode.go` 提取结果为 0 | 改扫全仓 `Exit*` 常量定义，定位到 `internal/clerr/clerr.go`（0-5）与 `internal/cmdutil/gate.go`（8）；6/7 为内联 `WithCode`（F-020） |
| R3 | 端点路径按「变量赋值形式」提取，四服务端均为 0 | 改为扫 HTTP 调用实参中的 `/v` 开头字面量，得 39 个去重端点（F-087） |
| R4 | 命令树以 `Use:` 字符串去重得 49，且顶层列表把 `apicmd.Cmd` 切成两项 | 改以 `AddCommand` 调用点为准，顶层修正为 19（F-007、F-008） |

## 相关概念

- [/concepts/00-cli-overview.md](/concepts/00-cli-overview.md) —— 事实清单的读者视角导览
- [/references/source-code-map.md](/references/source-code-map.md) —— 源码结构地图
- [/references/exit-code-contract.md](/references/exit-code-contract.md) —— 退出码契约全表
