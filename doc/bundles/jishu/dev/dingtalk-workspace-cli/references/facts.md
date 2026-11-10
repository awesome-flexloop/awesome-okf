---
okf_version: "0.2"
type: Reference
title: "dingtalk-workspace-cli 源码事实登记（F-001 ~ F-081）"
description: "对 dws 仓库 HEAD c631e4fb（v1.0.68-beta.1）的一手只读核验，逐条登记 81 项可追溯事实，供本束全部概念与示例文档引用"
source_repo: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
source_commit: "c631e4fb"
source_version: "1.0.68-beta.1"
measured_at: "2026-11-09"
---

# 源码事实登记

> **信源等级**：L1（被解读对象自身的源码与仓库内文档），非二手转述。
> **性质标注**：`[事实]` 仓库可直接核验的客观声明；`[文档口径]` 仓库文档的自我描述，未经运行时复现；`[清点]` 本次现场目录/文件清点所得。
> **核验方式**：只读 `git log`、`go.mod`、`CHANGELOG.md`、`README.md`、`docs/*.md` 与目录树；**未执行** `dws` 二进制，故所有运行时行为均属文档口径。
> 核验结论与对抗审查见 [verification.md](verification.md)。

## A. 仓库与发布（F-001 ~ F-008）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-001 | Go 模块路径为 `github.com/DingTalk-Real-AI/dingtalk-workspace-cli` | `go.mod` 首行 | P0 | [事实] |
| F-002 | `go.mod` 声明 `go 1.26.7` | `go.mod` | P0 | [事实] |
| F-003 | 当前分支 `main`，HEAD `c631e4fb`，提交日期 2026-11-06，提交信息 `chore: update beta formula for v1.0.68-beta.1` | `git log -1` | P0 | [事实] |
| F-004 | 最新发布版本 `1.0.68-beta.1`（2026-11-06） | `CHANGELOG.md` 首条 | P0 | [事实] |
| F-005 | 许可证 Apache-2.0，版权方 Alibaba Group（2026） | `LICENSE` | P0 | [事实] |
| F-006 | `internal/` 下 59 个一级包 | 目录清点 | P1 | [清点] |
| F-007 | `test/` 下 11 个分类目录（含 unit、contract、integration、mock_mcp、smoke、skill_* 系列） | 目录清点 | P1 | [清点] |
| F-008 | `docs/` 下 69 篇 Markdown（含架构、命令域模型、参考手册、RFC 与迁移方案） | 目录清点 | P1 | [清点] |

## B. 定位与总体架构（F-009 ~ F-016）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-009 | 定位为「一个用于钉钉工作区的命令行工具」，同时面向人类与 AI Agent | `README.md` 开篇 | P0 | [文档口径] |
| F-010 | 对外提供静态、带版本的命令面，覆盖钉钉 MCP 能力，并同时暴露两套表面：面向人的 Cobra CLI 与面向机器的 Schema | `README.md`、`docs/architecture.md` | P0 | [文档口径] |
| F-011 | 每个产品各自暴露 MCP 端点，客户端以 Streamable HTTP 聚合 | `docs/architecture.md` | P0 | [文档口径] |
| F-012 | 运行期**不做** `tools/list` 动态发现；全部命令定义在构建期静态展开 | `docs/command-framework-architecture.md` | P0 | [文档口径] |
| F-013 | 对外覆盖 20 个服务域：contact、chat、calendar、todo、oa、attendance、ding、report、aitable、doc、whiteboard、drive、minutes、mail、sheet、wiki、devdoc、aisearch、live、api | `README.md` Key Services 表 | P0 | [文档口径] |
| F-014 | `docs/command-index.md`（pre 环境快照）记录 13 个产品、180 条命令 | `docs/command-index.md` 首段 | P0 | [文档口径] |
| F-015 | 命令命名形态为 `dws <product> <resource> <verb>`，部分命令提供别名与快捷命令 | `README.md`、`docs/reference.md` | P0 | [文档口径] |
| F-016 | 不存在独立顶层 `bot` 产品，机器人能力并入 `dws chat bot` | `README.md` 迁移说明 | P0 | [文档口径] |

## C. 命令契约模型（F-017 ~ F-025）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-017 | 每个叶命令由 `corecmd.Spec` 描述（身份、Cobra 元数据、参数、约束、安全语义、契约、执行体） | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-018 | 存在三类执行体：静态管线生成命令、raw 分发器、手写 Go 命令 | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-019 | 参数回退链为「CLI flag → InputSchema 属性 → Cobra flag → 别名 → 默认值」 | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-020 | 约束支持 one_of、require_one_of、互斥、联动等组合 | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-021 | 安全语义字段包含 effect、risk、confirmation、idempotency，确认提示由安全元数据推导 | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-022 | 契约分三层声明（`ContractDecl` / `ProductDecl` / `ContractFinal`），Catalog 是发布输出而非输入 | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-023 | 框架设五条不变量：叶必有 Spec、flag 一律 kebab-case、flag 为唯一输入面、安全元数据必填、Schema 必须派生 | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-024 | 除选择器类位置参数外，命令不接受自由位置参数，输入统一走 flag | `docs/command-domain-model.md` | P0 | [文档口径] |
| F-025 | CLI 帮助与 Schema 由同一注册表派生，不维护两份真相 | `docs/command-framework-architecture.md` | P0 | [文档口径] |

## D. 静态端点管线（F-026 ~ F-032）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-026 | 端点数据的唯一来源是 `internal/syncdata` | `docs/architecture.md` | P0 | [文档口径] |
| F-027 | 管线为：KeyList → MCP 叶 ToolSpec → 叶 Spec → CommandRegistry → Cobra 命令树 | `docs/command-framework-architecture.md` | P0 | [文档口径] |
| F-028 | 一个 MCP 工具会展开为多条命令，展开比约 10 倍 | `docs/command-framework-architecture.md` | P1 | [文档口径] |
| F-029 | 生成物有校验：proto → 生成器 → 提交 Go 代码 → `git diff --exit-code` 守护 | `docs/command-framework-architecture.md` | P0 | [文档口径] |
| F-030 | `dws schema` 不访问 MCP 端点、不调用 `tools/list`、不读业务数据 | `docs/reference.md` | P0 | [文档口径] |
| F-031 | Schema 支持分级浏览：总览 → 产品 → 分组 → 叶命令；`--compact` 输出白名单字段，`--all` 输出全量 | `docs/reference.md` | P0 | [文档口径] |
| F-032 | 叶命令的 Schema 字段包含规范路径、参数、约束、effect、risk、confirmation、idempotency 及适用/回避场景 | `docs/reference.md` | P0 | [文档口径] |

## E. 身份与凭据（F-033 ~ F-040）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-033 | `dws auth login` 走浏览器 OAuth 授权；`--device` 提供无头设备码流程 | `README.md` | P0 | [文档口径] |
| F-034 | 可用自有应用登录：`--client-id` / `--client-secret` | `README.md` | P0 | [文档口径] |
| F-035 | `dws auth status --readonly --format json` 适合并发轮询登录态 | `README.md` | P0 | [文档口径] |
| F-036 | 支持多账号：`dws profile list`、`dws profile switch <corpId:userId>`，`-` 表示回切上一账号 | `README.md` | P0 | [文档口径] |
| F-037 | `dws auth export` / `import` 支持 tar.gz 或 base64，用于跨机迁移；Windows 不支持导出与导入 | `README.md` | P0 | [文档口径] |
| F-038 | 令牌以 PBKDF2 派生密钥 + AES-256-GCM 加密，密钥绑定设备；优先 OS 钥匙串（macOS Keychain / Windows DPAPI） | `README.md` | P0 | [文档口径] |
| F-039 | `dws auth migrate-keychain --to file-dek` 迁移钥匙串存储，且可重复执行 | `README.md` | P0 | [文档口径] |
| F-040 | 关键环境变量：`DWS_CONFIG_DIR`、`DWS_CLIENT_ID`、`DWS_CLIENT_SECRET`、`DWS_TRUSTED_DOMAINS`、`DWS_ALLOW_HTTP_ENDPOINTS`、`DWS_DISABLE_KEYCHAIN` | `docs/reference.md` | P0 | [文档口径] |

## F. 输出与错误（F-041 ~ F-046）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-041 | 输出格式支持 `table`、`json`、`raw`，`schema` 另有 `pretty` | `docs/reference.md` | P0 | [文档口径] |
| F-042 | `-o` 落盘；`--jq`、`--fields` 做字段投影 | `docs/reference.md` | P0 | [文档口径] |
| F-043 | 退出码语义：0 成功、1 一般错误、2 参数错误、3 认证/授权错误、4 待交互授权、5 权限不足、6 限流/服务端错误 | `docs/reference.md` | P0 | [文档口径] |
| F-044 | JSON 错误结构含 category、reason、hint、actions | `docs/reference.md` | P0 | [文档口径] |
| F-045 | `@path` 与 `@-` 从文件/stdin 注入值，按严格前缀判定，不做猜解 | `docs/reference.md` | P1 | [文档口径] |
| F-046 | 智能输入纠错覆盖命名风格、粘连拆分、模糊匹配、值归一四类 | `README.md` | P1 | [文档口径] |

## G. 安全与审计（F-047 ~ F-052）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-047 | `--dry-run` 只预览请求而不执行 | `README.md`、`docs/reference.md` | P0 | [文档口径] |
| F-048 | 写操作默认要求确认，`--yes` 跳过；确认提示由安全元数据生成 | `README.md` | P0 | [文档口径] |
| F-049 | 审计日志为 JSONL 哈希链，落位于 `internal/audit` | `README.md`、`internal/audit` | P1 | [文档口径] |
| F-050 | 出站域名白名单默认 `*.dingtalk.com`，可由 `DWS_TRUSTED_DOMAINS` 扩展 | `docs/reference.md` | P0 | [文档口径] |
| F-051 | 强制 HTTPS；`DWS_ALLOW_HTTP_ENDPOINTS=1` 仅放行回环地址 | `docs/reference.md` | P0 | [文档口径] |
| F-052 | 输入防御覆盖路径穿越、CRLF 注入、Unicode 伪装等类别 | `README.md` 安全章节 | P1 | [文档口径] |

## H. Agent 集成（F-053 ~ F-060）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-053 | Skills 提供两种布局：`multi` 为 16 个产品级技能，`mono` 为单技能（含 products 与 37 个脚本） | 目录清点 `skills/` | P0 | [清点] |
| F-054 | 安装入口：`npx skills add DingTalk-Real-AI/dingtalk-workspace-cli`，或 `dws skill setup --mode --target` | `README.md` | P0 | [文档口径] |
| F-055 | 技能安装记录于 `skills-state.json`，安装前备份，mono/multi 互切时清理对方产物 | `README.md` | P1 | [文档口径] |
| F-056 | 事件目录共 33 个事件，命令为 `dws event list/schema/consume/status/stop` | `README.md` | P0 | [文档口径] |
| F-057 | 事件以 NDJSON 输出到 stdout，支持 `--flatten` 与跨进程共享本地总线（Unix Socket / Named Pipe） | `README.md` | P0 | [文档口径] |
| F-058 | `dws api` 提供 GET/POST 直连开放平台，自动识别双域，支持 `--data`、`--file`、`--page-all`（默认 10 页、上限 500） | `README.md` | P0 | [文档口径] |
| F-059 | Agent 标识通过 `DWS_AGENT_PRODUCT/HOST/VER/EXT` 环境变量注入，`--ai-tag` 默认开启 | `README.md` | P1 | [文档口径] |
| F-060 | raw API 通道被排除在 Agent 可见 Schema 之外，避免绕过命令契约 | `README.md` | P1 | [文档口径] |

## I. 运维与边界（F-061 ~ F-064）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-061 | `dws upgrade` 支持自升级与 `--rollback` 回滚；`DWS_NO_SKILLS` 可关闭技能联动 | `README.md` | P1 | [文档口径] |
| F-062 | `dws dev connect` 把消息机器人桥接到本地 AI CLI，支持 `--unified-app-id` 与会话命令 `/new`、`/clear` | `README.md` | P1 | [文档口径] |
| F-063 | 文档与 CLI 输出为双语（中/英），存在 i18n 包承载文案 | `README.md`、`internal/i18n` | P1 | [文档口径] |
| F-064 | `internal/` 含 tui、openharmony 等平台/交互能力包，说明 CLI 不止于脚本调用 | 目录清点 | P2 | [清点] |

## J. CI 门禁（F-065 ~ F-069）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-065 | PR 合入要求恰好九个外部必需检查：Lint、Test、Coverage、Policy、Edition、Interface Integrity、AI Behavior、CLI Smoke、Mock MCP | `docs/ci-pr-gates.md` | P0 | [文档口径] |
| F-066 | `AI Behavior` 由 `pull_request_target` 工作流执行，从不检出或运行 PR 代码，并在 Draft/Ready 状态切换时取消旧评估 | `docs/ci-pr-gates.md` | P0 | [文档口径] |
| F-067 | `Policy` 门禁包含 fail-closed 的 CHANGELOG 契约，缺失即失败而非告警 | `docs/ci-pr-gates.md` | P0 | [文档口径] |
| F-068 | `Coverage` 门禁要求变更代码 100% 覆盖，且整体覆盖率不得回归 | `docs/ci-pr-gates.md` | P0 | [文档口径] |
| F-069 | `Interface Integrity` 覆盖 CLI、Schema、Skill 与稳定版本兼容性 | `docs/ci-pr-gates.md` | P0 | [文档口径] |

## K. 安装、升级与技能布局（F-070 ~ F-081）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-070 | 安装渠道包括：`install.sh`（macOS/Linux）、`install.ps1`（Windows PowerShell）、npm 全局包、Homebrew tap、GitHub Releases 预编译二进制、源码构建；另有 OpenHarmony 构建脚本与 Gitee 镜像 | `README.md` Installation | P0 | [文档口径] |
| F-071 | Linux 二进制链接 glibc（基线 2.17）；musl 发行版（如 Alpine）不受支持，安装器检测到后停止而非装入无法启动的二进制 | `README.md` Installation 注 | P1 | [文档口径] |
| F-072 | 源码构建默认启用 CGO，包含 SafeChat 后端，因此需要可用的 C 编译器；`CGO_ENABLED=0` 只用于有意的桩构建 | `README.md` 源码构建注 | P0 | [文档口径] |
| F-073 | 技能布局默认 `multi`（按产品拆分）；`mono` 可经 `DWS_SKILL_MODE=mono` 或 `dws skill setup --mode mono` 启用；两种模式下 CLI 命令完全一致，差异只在 Agent 侧技能布局 | `README.md` 技能布局 | P0 | [文档口径] |
| F-074 | TTY 安装会提示 `1) multi  2) mono`（默认 1）；`DWS_NO_SKILLS=1` 在 npm、`install.sh`、`install.ps1` 中跳过完整技能路径 | `README.md` | P1 | [文档口径] |
| F-075 | `dws upgrade` 要求 v1.0.7 及以上；支持 `--check`、`--list`、`--beta`、`--version`、`--rollback`、`--force`、`--skip-skills`、`-y` | `README.md` Upgrade | P0 | [文档口径] |
| F-076 | 多组织选择器支持 `corpId:userId`、`corpId:userName`、`corpName:userId`、`corpName:userName` 四种形态；`--profile <corpId>` 使用该组织已显式记录的当前账号，若该组织有多个账号且无记录则失败而非猜选 | `README.md` 多组织章节 | P0 | [文档口径] |
| F-077 | Profile 以 `corpId:userId` 唯一标识；跨组织读取由 Agent 编排（列出 profile、按 corpId 分组、取唯一 `isOrgCurrent=true` 账号），无内置 `--all-orgs`；`auth logout --profile <corpId>` 删除该组织全部本地账号 | `README.md` 多组织章节 | P0 | [文档口径] |
| F-078 | 自有应用模式需在开放平台创建应用，并在安全设置中加入重定向 URL `http://127.0.0.1,https://login.dingtalk.com`；企业管理员须在 open-dev.dingtalk.com 的「CLI Access Management」启用 CLI 访问 | `README.md` Getting Started | P0 | [文档口径] |
| F-079 | Quick Start 给出 8 条命令示例（联系人检索、日程、文档检索、白板查询、AI 听记、云盘、待办创建、待办预演）；Agent 调用范式为 `--yes` 跳过确认、`--dry-run` 预演、`--jq` 精确投影 | `README.md` Quick Start / Agent Invocation Patterns | P1 | [文档口径] |
| F-080 | `dws schema "<path>" --compact` 是 Agent 的规范视图；`dws schema --all` 导出完整契约供工具链与兼容性基线；Help 与 Schema 冲突视为契约漂移，应只传 Cobra 接受的 flag 并采用更保守的安全语义 | `README.md` Command Help and Schema | P0 | [文档口径] |
| F-081 | `dws skill setup` 支持 `--mode mono\|multi`、`--target all\|claude\|cursor\|codex\|zcode\|opencode\|qoder`、`--source`、`--yes`；每次移除前先预览并备份到 `~/.dws/skill-backups/<timestamp>/`，无法备份的目录不删除 | `README.md` Agent Skills | P1 | [文档口径] |