---
type: Reference
title: "dh CLI 源码事实登记"
description: "dh（DoltHub CLI）源码事实编号总表 F-001~F-060，覆盖构建信息、命令树、工厂注入、认证凭据、HTTP/API 客户端、异步操作与上传，逐条溯源至本地源码"
tags: [dh, dolthub, cli, go, source-code]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-repo
    resource: https://github.com/dolthub/cli
    title: "dolthub/cli — GitHub 仓库"
  - id: dh-cli-local
    resource: "本地源码 external/dao/action/DoltHub/cli @ 2ef50ab"
    title: "dh CLI 本地源码（commit 2ef50ab）"
---

# dh CLI 源码事实登记

> 本文件登记本 bundle 全部事实编号，逐条溯源至本地源码 `external/dao/action/DoltHub/cli`。
> **信源**：① 官方源码（dolthub/cli，本地克隆）。
> **分析基线**：commit `2ef50ab87632b40c08782f43573e2b3c43ebfbd9`（2026-09-08），`git describe` 输出 `v0.0.1-2-g2ef50ab`。
> **信源距离**：① 官方源码（第一手），所有事实均可在源码中 Grep 验证。

---

## 事实编号总表（F-001 ~ F-060）

> 共 60 条事实，按"元信息 → 入口命令树 → 工厂注入 → 配置 → 认证凭据 → HTTP/API → 仓库解析 → 异步操作 → 上传 → 输出与命令"十组组织。

### 一、元信息与构建

| F 编号 | 事实简述 |
|--------|---------|
| F-001 | dh 是 DoltHub 官方命令行接口，仓库 `github.com/dolthub/cli`，二进制名 `dh`（Windows 为 `dh.exe`） |
| F-002 | CLI 支持 Linux/macOS/Windows；从源码构建需 Go 1.26 或更新（go.mod 声明 `go 1.26.0`） |
| F-003 | 分析基线版本 v0.0.1，commit `2ef50ab87632b40c08782f43573e2b3c43ebfbd9`（2026-09-08），`git describe` 为 `v0.0.1-2-g2ef50ab` |
| F-004 | Docker 镜像 `dolthub/cli`，提供版本 tag 与 `latest` |
| F-005 | Go module `github.com/dolthub/cli`；直接依赖 cobra v1.10.2、pflag v1.0.9、go-keyring v0.2.8、go-gh/v2 v2.13.0 |
| F-006 | 仓库含 150 个 `.go` 文件（含测试）；`internal/dolthub` 包 19 个文件（9 源文件 + 10 测试文件） |

### 二、入口与命令树

| F 编号 | 事实简述 |
|--------|---------|
| F-007 | 入口 `cmd/dh/main.go` 定义 `var version = "dev"`，`main()` 调 `os.Exit(app.Main(os.Args[1:], os.Stdin, os.Stdout, os.Stderr, version))` |
| F-008 | `app.Main` 调 `app.Run(args, iostreams.New(stdin, stdout, stderr), version)` |
| F-009 | `app.Run` 依次执行 `factory.New(version, streams)` → `root.NewCmdRoot(f)` → `cmd.SetArgs(args)` → `execute` |
| F-010 | 退出码常量：exitSuccess=0、exitFailure=1、exitUsage=2、exitAuth=4 |
| F-011 | 根命令 `dh` 挂 14 个命令组：api、auth、branch、browse、completion、config、db、operation、pr、release、sql、tag、table、version |
| F-012 | 错误类型：FlagError、SilentError、NoResultsError、CancelError、AuthError、ExternalCommandError（各含 Unwrap 与 fallback 文案） |
| F-013 | 错误渲染：NoResultsError→exit 0；SilentError→exit 1；FlagError/CancelError→exit 2；AuthError→exit 4 并提示 `dh auth login`；ExternalCommandError→透传子进程退出码 |
| F-014 | `execute` 将 `unknown command` 前缀错误转换为 FlagError |

### 三、工厂与依赖注入

| F 编号 | 事实简述 |
|--------|---------|
| F-015 | `Factory` 结构体聚合 11 个能力：AppVersion、IO、Config、Credentials、RefreshToken、Authenticator、Prompter、ResolveRepository、LookupEnv、APIClientForHost、Browser |
| F-016 | `factory.New` 用 `sync.Once` 惰性加载配置，构造 FallbackStore 凭据、System prompter、BrowserAuthenticator、APIClientForHost、ResolveRepository |

### 四、配置

| F 编号 | 事实简述 |
|--------|---------|
| F-017 | `config.DefaultHost = "www.dolthub.com"` |
| F-018 | Config 接口方法：Host、ConfiguredHost、SetHost、ActiveUser、SetActiveUser、UnsetActiveUser、DefaultRepository、ConfiguredRepository、SetDefaultRepository、Write |
| F-019 | 配置文件路径 `os.UserConfigDir() + "/dh/config.json"`，JSON 格式，schemaVersion=1 |
| F-020 | `config.File.Write` 原子写：临时文件 `.config-*` + chmod 0600 + Sync + Rename；目录 0700 |
| F-021 | Config 实现：File（JSON）、Memory（测试）；Environment 装饰器用 DH_HOST、DH_REPO 环境变量覆盖 |

### 五、认证与凭据

| F 编号 | 事实简述 |
|--------|---------|
| F-022 | 凭据 Store 接口 Get/Set/Delete；Source 枚举 keyring/file |
| F-023 | KeyringStore 用 go-keyring，service 名 "dh"，account 形如 `host:user` |
| F-024 | EnvironmentStore 使 DH_TOKEN 优先读取（不持久化、不删除） |
| F-025 | FileStore 存 `os.UserConfigDir() + "/dh/credentials.json"`；非 Windows 要求目录 0700、文件 0600，否则报 "unsafe permissions" |
| F-026 | FallbackStore 读优先 file、写优先 keyring，keyring 不可用回退 file（登录后打印未加密警告） |
| F-027 | OAuthToken 字段 AccessToken/RefreshToken/TokenType/ExpiresAt，序列化前缀 `dh.oauth.v1:` |
| F-028 | OAuth 授权码 + PKCE：scope `api_read_write`、`code_challenge_method S256`；token 端点 `/api/oauth/access_token`、授权端点 `/oauth/authorize` |
| F-029 | 生产 OAuth client ID 由 `productionOAuthClientID` 内置，`DH_OAUTH_CLIENT_ID` 可覆盖；非生产 host 必须显式配置 |
| F-030 | BrowserAuthenticator：回调默认 `http://localhost:53682/callback`、超时 5 分钟、loopback HTTP server、校验 state、交换 code、CurrentUsername 校验身份 |
| F-031 | TokenSource 加载凭据，过期（默认 skew 1 分钟）时 Refresh 轮换，先持久化再返回新 token |

### 六、HTTP 传输与 API 客户端

| F 编号 | 事实简述 |
|--------|---------|
| F-032 | `httptransport.New` 给每个请求加 `User-Agent: dh/<version>` |
| F-033 | `httptransport.NewAuthenticated` 仅对精确匹配的信任 hostname 附加 `Authorization: Bearer <token>` |
| F-034 | `dolthub.Client` 为 DoltHub REST API v2 客户端，baseURL 以 `/api/v2/` 结尾 |
| F-035 | `Client.Raw` 校验 endpoint 相对 /api/v2/：拒绝绝对 URL、拒绝 `..`/`.` 段、拒绝 fragment |
| F-036 | 响应体限制：成功 16 MiB（maxSuccessResponse）、错误 1 MiB（maxErrorResponse） |
| F-037 | API 响应结构 `{data, meta}`，meta 含 `next_page_token`；错误统一解码为 APIError |
| F-038 | APIError 字段 Status/Method/Path/RequestID/Type/Title/Detail/Code；`safeServerText` 过滤控制字符、正则 `(?i)bearer\s+[^\s]+` 替换为 `Bearer [REDACTED]`；ExchangeError 不保留服务器自由文本 |

### 七、仓库解析

| F 编号 | 事实简述 |
|--------|---------|
| F-039 | `repository.Repository` 字段 Host/Owner/Name；Parse 支持 OWNER/REPO、HOST/OWNER/REPO、DoltHub URL |
| F-040 | Resolver 解析优先级：显式 --db → DH_REPO → 已配置默认仓库 → `dolt remote -v` 候选 → 交互选择 |
| F-041 | `ReadDoltRemotes` 执行 `dolt remote -v`，识别 `doltremoteapi.dolthub.com`（归一化为 www.dolthub.com）与 `www.dolthub.com` |
| F-042 | 无候选时报错提示使用 `--db`、`DH_REPO` 或 `dh config set repo` |

### 八、异步操作

| F 编号 | 事实简述 |
|--------|---------|
| F-043 | OperationType 枚举 import/merge/sql_write/fork/dolt_ci；OperationStatus 枚举 queued/running/succeeded/failed |
| F-044 | `operationwaiter.Waiter` 默认 interval 1s、max 10s，指数退避（interval 倍增）+ 0.8~1.2 随机抖动，Observe 回调观察 |
| F-045 | `pagination.Collect` 泛型游标分页，token 视为不透明，检测重复 token 防死循环 |
| F-046 | 异步操作（SQL write、fork、merge、table import）返回 OperationRef，由 waiter 轮询至终态 |

### 九、上传

| F 编号 | 事实简述 |
|--------|---------|
| F-047 | `upload.PartSize` 5 MiB、`MaxFileSize` 1 GiB；4 worker 并发、最多 20 MiB part 缓冲 |
| F-048 | `upload.File` 逐 part 计算 md5，最终 MD5 = md5(拼接各 part base64 digest) |
| F-049 | 上传 URL 10 分钟过期，失败需重启（不刷新、不续传）；400/403 提示 URL 可能过期 |

### 十、输出与命令

| F 编号 | 事实简述 |
|--------|---------|
| F-050 | `tableprinter.Table` 终端输出用 tabwriter 对齐 + 大写表头，非终端输出 tab 分隔 |
| F-051 | `AddJSONFlags` 提供 `--json`/`--jq`/`--template`，复用 go-gh 的 jq 与 template 能力 |
| F-052 | `AddDatabaseFlag` 加 `--db/-R` 主 flag 与隐藏 `--repo` 兼容别名 |
| F-053 | `sql` 读查询要求 `--ref`；写查询要求 `--write` + `--branch`，`--no-wait` 跳过等待 |
| F-054 | `sql` 读 JSON 字段 columns/message/rows/status/warnings；写 JSON 字段 cancelable/created_at/error/href/id/result/status/type |
| F-055 | `sql` 写查询调 `RunSQLWrite` 返回 OperationRef，默认进度条 + 等待完成 |
| F-056 | `table import` 支持 CSV/PSV/XLSX/JSON（JSON 需 --update/--replace），--overwrite/--update/--replace 互斥 |
| F-057 | `table import` 流程：CreateImportUpload → upload.File → CreateImport → waiter 等待；主键 `--primary-key` 逗号分隔或重复 |
| F-058 | `browse` 构造 URL `repositories/{owner}/{name}`，可加 `data/{branch}` 或 `pulls/{number}` |
| F-059 | `browser.System.Browse` 跨平台：darwin `open`、windows `rundll32 url.dll,FileProtocolHandler`、linux `xdg-open` |
| F-060 | `login` 在 DH_TOKEN 存在时拒绝登录；登录成功 SetActiveUser + Write，失败 rollback 凭据 |

---

## 信源登记

| 信源 | 类型 | 距离 | 引用内容 |
|------|------|------|---------|
| [dolthub/cli](https://github.com/dolthub/cli) | 官方源码仓库 | ① | 全部概念/示例文档 |
| 本地克隆 `external/dao/action/DoltHub/cli` | 官方源码（本地） | ① | F-001~F-060 逐条溯源 |

## 事实分布说明

- 全部 60 条事实均可在本地源码中 Grep 验证，无训练数据统计惯性导致的虚构。
- 命令示例（examples/）来自 README.md 与命令 `Long`/`Example` 字段，均与源码一致。
- 版本号、commit hash、文件计数为本次分析时点快照，随上游演进可能漂移，`stale_after` 设为 2026-12-31。
