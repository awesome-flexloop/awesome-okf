---
type: reference
title: 信源台账与事实清单
description: 秒悟 CLI 部署与开放平台集成指南束的 F-001–F-074 编号事实清单（个人 CLI 使用 29 条 / 开放平台总览 12 条 / CLI 开放集成 17 条 / 阿里云 BYOC 16 条）、S1–S4 信源登记表、放弃核验清单、转写噪声登记与单源声明
tags: [meoo, miaowu, cli, open-api, byoc, 信源登记, 事实清单, 核验]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: S1
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南（功能特性 › 应用构建能力）
  - id: S2
    resource: https://docs.meoo.com/open
    title: Meoo 开放平台（Meoo开放能力）
  - id: S3
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入（Meoo开放能力 › 接入流程）
  - id: S4
    resource: https://docs.meoo.com/features/cli-aliyun
    title: MEOO CLI 进阶：部署到你自己的阿里云账号（功能特性 › 应用构建能力）
---

# 信源台账与事实清单

本文件登记本束全部编号事实（**F-001–F-074，共 74 条，编号连续无跳号**）与 S1–S4 信源台账。事实内容除明确标注外均为源页逐字口径，未添加推断；命令、环境变量、端点、版本号零改写。

事实按四个源页分四段：个人 CLI 使用（F-001–F-029，S1）、开放平台总览（F-030–F-041，S2）、CLI 开放集成（F-042–F-058，S3）、阿里云 BYOC（F-059–F-074，S4）。四源均为 2026-10-18 匿名抓取、HTTP 200、无重定向。

## S1：个人 CLI 使用事实（F-001–F-029）

来源：[Meoo CLI 使用指南](https://docs.meoo.com/features/cli)，面向终端个人用户的安装、登录、部署指南（正文 4 节 + 11 条 FAQ）。

| 事实编号 | 事实内容 | 来源 |
|---------|---------|------|
| F-001 | meoo cli 是秒悟（Meoo）官方推出的命令行工具，让 Claude Code、Codex、Qoder、Qoderwork 等本地 agent 在写完前端代码后直接接管「数据库、用户登录、文件存储、百炼模型服务、部署上线」的所有云端工作 | S1 |
| F-002 | 支持工具为「具备 Coding 能力的本地 agent」，源页列举：Claude Code、Codex、Cursor、Qoder、Qoderwork、Cline 等主流 agent | S1 |
| F-003 | 适用场景四条：①从 0-1 搭建项目，需要接入数据库、部署到线上并生成分享链接；②本地已有的静态页面同步云端协作；③本地已有全栈项目，希望保留服务端架构并部署到线上；④本地已有的 SSR、API 服务、后台系统希望一键发布 | S1 |
| F-004 | 适用人群三类：有全栈交付需求的泛开发者；vibe coding 爱好者（想把作品做成链接分享的创作者）；设计师、产品经理、运营（快速产出落地页、H5 长图、活动页并与团队协同打磨） | S1 |
| F-005 | 安装前置条件：已安装 Node.js 20 或更新版本（源页链接 `https://nodejs.org/en/download/`） | S1 |
| F-006 | macOS 用户推荐通过 nvm 或 Homebrew 安装 Node.js；Windows 用户还需安装 Git for Windows 和 zip 工具 | S1 |
| F-007 | 自动安装（推荐）话术（在本地 agent 对话框发送，逐字）：`读取 meoo.com/skill-setup.md 并按照说明安装秒悟技能` | S1 |
| F-008 | 手动安装命令（逐字）：`npm install -g @aliyun-meoo/cli` | S1 |
| F-009 | 验证安装命令（逐字）：`meoo --version`；显示版本号即安装成功 | S1 |
| F-010 | 登录授权流程：安装完成后 CLI 自动打开浏览器跳转到 meoo.com 授权页面；首次授权需登录秒悟账号，之后只需在网页确认设备名称并点击「授权登录」；授权成功后 CLI 自动获取凭证并保存 | S1 |
| F-011 | 未触发自动登录时的手动登录命令（逐字）：`meoo login`，执行后跳转浏览器登录授权界面 | S1 |
| F-012 | 用本地 agent 创建项目的示例话术（以 codex 桌面端为例，逐字）：`帮我用meoo做一个好看的个人主页，数据接入云服务数据库，然后一键发布到线上` | S1 |
| F-013 | 该流程中 agent 自动写个人主页、调用 meoo cli 在云端创建数据库、补齐缺失后端代码、部署到线上并生成可分享链接 | S1 |
| F-014 | 本地预览话术「起个本地预览看看效果」；浏览器自动打开 `localhost:3015`，可本地完整测试注册账号、提交表单、查看数据库 | S1 |
| F-015 | 上线话术「部署上线」；AI 自动执行 `meoo deploy`，构建打包并发布到 CDN，终端输出可直接分享的访问链接 | S1 |
| F-016 | 如需扩充数据库容量、调用大模型服务（AI 问答、文生图、识图等）、自定义域名、自定义网页发布范围（全网可见/指定人员可见/仅自己可见），建议把代码同步到 meoo 云端，话术（逐字）：`帮我把代码同步到meoo云端`；同步后可在 meoo 官网看到应用并在秒悟里二次修改 | S1 |
| F-017 | FAQ 给出的项目有服务端进程时的补充话术（逐字）：`这个项目需要服务端进程，请使用全栈应用部署。` | S1 |
| F-018 | 静态应用本地预览通常是 `localhost:3015`；全栈应用按项目自己的方式启动；本地预览和部署上线是两件独立的事，可先反复本地修改再部署 | S1 |
| F-019 | 本地代码与 meoo 网页后台同时编辑存在冲突风险；本地开发期间不建议直接在网页后台发布覆盖；确需网页侧协作修改时，先把代码同步到 Meoo 云端再操作网页 | S1 |
| F-020 | 云服务开通存在延迟：命令返回成功只代表开通申请已发出，数据库实例还需时间就绪；源页口径「等 2-3 分钟后让 AI 重试即可」 | S1 |
| F-021 | 静态部署与全栈应用部署对比（源页 Q6 表格五行）：适合项目（React/Vue/Taro SPA、个人主页、活动页、纯前端工具 ↔ Next.js SSR、Nuxt SSR、Express、FastAPI、Django、Spring Boot、Go HTTP 服务）；是否有服务端进程（没有 ↔ 有）；发布方式（构建前端产物发布到 CDN ↔ 上传源码云端构建并运行服务）；后端逻辑（使用 Meoo Cloud / Edge Functions ↔ 可以保留项目自带服务端）；典型命令（见 F-022） | S1 |
| F-022 | 典型命令（逐字）：静态部署 `meoo deploy`；全栈应用部署首次 `meoo deploy --runtime image`，后续可直接 `meoo deploy` | S1 |
| F-023 | 纯静态页面（个人主页、活动页等不需要注册登录、不存数据的项目）不需开通云服务，可直接发布，不会消耗云服务额度 | S1 |
| F-024 | 全栈应用云端构建环境（源页 Q9 逐字）：OS 为 Linux，构建/运行目录是 `/code`；Java OpenJDK 21；Node.js 24.15.0；npm 11.13.0；pnpm 10.33.3；Yarn 1.22.22；Python 3.13；Go 1.26.0；常用工具 `git`、`curl`、`wget`、`unzip`、`rsync`、`build-essential`、`pkg-config` | S1 |
| F-025 | 全栈运行约束（逐字）：应用必须监听 `0.0.0.0:${PORT:-9000}`；`scripts/setup.sh` 在远端构建时执行；`scripts/start.sh` 在容器启动时执行；本地文件存储不持久，容器会冷启动/重建，持久化要走云数据库或外部服务 | S1 |
| F-026 | 全栈部署不需要用户自己写 Dockerfile 或安装 Docker；告诉 Agent 项目需要服务端进程后，Agent 补齐部署配置并调用 Meoo CLI 在云端构建运行 | S1 |
| F-027 | 余额不足处理：前往 `https://docs.meoo.com/pricing`（订阅与积分说明）查看套餐额度，或到 `https://meoo.com` 删除不用的项目/实例释放资源；源页明示「目前限时免费体验，Free 用户可以部署 1 个全栈项目，Pro 用户 4 个，MAX 用户 8 个」⚠️ dated | S1 |
| F-028 | 既有项目可迁移：纯前端走静态部署，带服务端进程走全栈应用部署；迁移前建议先备份代码，再让 Agent 检查项目类型、列出改造点并执行部署 | S1 |
| F-029 | 本页面包屑为「功能特性 › 应用构建能力」，底部分页指向上一页 Web Apps（`/features/web-apps`）与下一页 `/features/cli-aliyun`，可佐证 CLI 两页与阿里云页为同一栏目连续页面 | S1 |

## S2：开放平台总览事实（F-030–F-041）

来源：[Meoo 开放平台](https://docs.meoo.com/open)，开放能力区首页。

| 事实编号 | 事实内容 | 来源 |
|---------|---------|------|
| F-030 | Meoo Open API 提供项目创建、AI 应用生成、云能力和发布能力；接入方法是先确定「以谁的身份调用」，再选择需要的功能流程，只有需要核对字段时才进入 API 目录 | S2 |
| F-031 | 生产环境地址 `https://meoo.com`；当前版本 `v1` | S2 |
| F-032 | 三种身份接入方式（源页表格）：①团队系统集成——适合企业系统集成、单大账号或多租户 SaaS，平台是否识别最终用户「可选；Owner 模式不隔离，虚拟账号模式按 `member_id` 隔离」，推荐账号「系统集成唯一推荐方式：团队版」；②用户 API Key——适合个人测试、临时调试、个人 CLI，平台不识别最终用户、始终代表 API Key 创建者，仅推荐个人和非生产场景；③OAuth 授权——适合第三方产品代 Meoo 用户操作，平台识别最终用户（由用户登录并授权），由实际授权用户账号版本决定 | S2 |
| F-033 | 三种模式最终都使用 Bearer Token 调用业务 API；团队 AK/SK 仅用于成员管理和为团队 Owner 或虚拟成员签发短期 Token，不能直接调用项目、Agent 或 Release；系统集成不再推荐直接使用用户 API Key | S2 |
| F-034 | 三种功能接入流程：①全链路接入（目标：让 Meoo 生成应用并发布上线；结果：生成结果、预览地址和正式网站链接）；②仅部署接入（已自行构建只使用托管发布；静态 zip 发布后的网站链接）；③仅生成接入（只使用 AI 生成不发布；生成过程、会话记录和临时预览地址） | S2 |
| F-035 | API 参考四类入口：API 目录（按资源查看接口、Scope 和字段）；源码导出 API（将项目当前源码导出为 ZIP 并获取短期下载链接）；通用协议（错误、分页、幂等、请求追踪和 SSE）；稳定性与安全（凭证保管、重试、限流和上线检查） | S2 |
| F-036 | 接入前须知（逐字口径）：当前开放平台的集成权益限制较小，仅建议用于开发和预发联调；正式生产上线需等待「集成版」权益套餐上线，并按届时公布的额度与服务保障完成开通 ⚠️ dated | S2 |
| F-037 | 团队 AK/SK 暂未开放用户侧自助创建入口，未来随「集成版」套餐提供；现阶段联调需联系秒悟团队人工创建测试凭证并提供团队账号；Secret 仅在创建时交付一次 ⚠️ dated | S2 |
| F-038 | 长期凭证只能保存在接入方可信服务端，不能写入浏览器、移动端、代码仓库或构建产物 | S2 |
| F-039 | 用户 API Key 可由用户在 Meoo 前端自行创建，但不作为系统集成凭证；团队 AK/SK 当前由秒悟管理员在内部后台创建，不提供公开创建接口 | S2 |
| F-040 | OAuth 应用不能自行注册；需联系 Meoo 配置回调地址、允许账号版本和 Scope，并获取 `client_id` 与 Client Secret ⚠️ dated/条件性 | S2 |
| F-041 | 测试和生产环境的账号、凭证、项目不能混用 | S2 |

## S3：CLI 开放集成事实（F-042–F-058）

来源：[CLI 开放集成接入](https://docs.meoo.com/open/guides/cli)，面向接入方团队的 6 节接入流程。与 S1 非重复页（面包屑、title、正文、分页均不同，详见 [verification.md](verification.md) 核验项十二）。

| 事实编号 | 事实内容 | 来源 |
|---------|---------|------|
| F-042 | 使用 Meoo 提供的 Skill + CLI，可以让 Agent 直接调用秒悟的项目开发、云服务、源码同步和发布能力；接入流程（源页逐字加粗）：**安装 Meoo Skill + CLI → 用团队 AK/SK 签发临时 token → 注入 MEOO_TOKEN → Agent 执行任务**；接入方只需签发临时 token 并注入 `MEOO_TOKEN`，Agent 即可按 Skill 指引使用 | S3 |
| F-043 | 两种 Agent 接入方式对比（源页表格五行）：使用 Meoo Skill + CLI 时 Meoo 提供配套 Skill、CLI、项目模板和操作命令；接入方安装配套 Skill 和 CLI、签发临时 token 并通过 MEOO_TOKEN 注入；Agent 读取 Skill 按指引选 CLI 命令执行；Agent 使用 CLI 项目模板组织代码；适合快速让已有 Agent 复用官方工具。基于 OpenAPI 自行封装时 Meoo 提供云服务 OpenAPI 和项目导入 API；接入方自行封装工具、定义参数与结果处理、生成项目结构并组织调用；适合自行设计 Agent 工具与开发流程 | S3 |
| F-044 | 准备接入资源：开放团队与 AK/SK——在开放版管理后台创建团队 API 凭证，由接入方服务端保存 AK/SK 并完成请求签名；成员身份——联调时可用团队 Owner，面向业务用户时建立业务用户与虚拟成员 `member_id` 的映射 | S3 |
| F-045 | 凭证权限（逐字）：团队 AK/SK 配置 `team.member.token.issue`；查询成员时配置 `team.member.read`；可委托权限包含 `cli.compat` | S3 |
| F-046 | 集成运行环境：Node.js 18 或以上，安装支持 MEOO_TOKEN 的 CLI 接入版本；Agent 具备终端执行能力及 Skill 加载能力 | S3 |
| F-047 | 服务地址：生产环境为 `https://meoo.com`；联调时使用对应环境地址及该环境签发的凭证 | S3 |
| F-048 | 成员 token 签发接口（请求报文逐字）：`POST /open/v1/team/members/{member_id}/tokens`，`Content-Type: application/json`，请求体 `{"scopes": ["cli.compat"], "expires_in": 900}`；按团队 AK/SK 的 HMAC 签名协议调用；从响应中取得 `access_token` 和 `expires_in` | S3 |
| F-049 | `member_id` 选择本次任务对应的团队成员；`expires_in` 为有效期秒数，按任务时长设置并满足团队凭证允许的有效期范围；CLI 以该成员身份执行操作，项目访问范围由成员所属团队、角色和资源权限共同确定；接入方记录到期时间 | S3 |
| F-050 | CLI/Skill 安装命令（逐字，安装包路径需替换为实际路径）：`npm install -g "/path/to/meoo-cli.tgz"`、`meoo --version`、`meoo skill install` | S3 |
| F-051 | `meoo skill install` 会检测 Claude Code、Cursor、Trae、CodeBuddy、Qoder 的已有配置目录；自有 Agent 可用（逐字）`meoo skill install --target /path/to/agent/skills/meoo-cli` 安装到实际加载目录 | S3 |
| F-052 | `--target` 目标目录为 meoo-cli Skill 文件夹本身，包含 `SKILL.md` 和 `references/`；需将该目录配置到 Agent 的 Skill 加载路径；升级 CLI 后再次执行安装命令以同步配套指引 | S3 |
| F-053 | token 注入（逐字）：`export MEOO_TOKEN="<access_token>"`；`export MEOO_API_URL="https://meoo.com"`；由接入方服务端、Secret 管理或任务调度器将变量注入 Agent 命令执行进程，CLI 子进程继承这些变量 | S3 |
| F-054 | 身份与项目核验命令（逐字）：`meoo --json whoami`、`meoo --json projects list`；Agent 可用 `--json` 获取结构化结果 | S3 |
| F-055 | 项目操作命令序列（在本地应用目录使用实际项目 urlId，逐字）：`meoo projects use "<项目 urlId>"`、`meoo cloud status`、`meoo sandbox push`、`meoo deploy`，依次为选择项目、查看云服务状态、同步本地源码、构建发布 | S3 |
| F-056 | CI 直发命令（逐字）：`meoo --json deploy --project "<项目 urlId>" --skip-build --skip-push --force`；使用已有构建产物直接发布到目标项目，执行前需完成构建并核对项目；`--force` 用于自动化任务中的确认步骤 | S3 |
| F-057 | token 生命周期四阶段（源页表格）：任务启动（按业务用户确定 member_id，签发或复用有效 token 并注入）；token 临近到期（用团队 AK/SK 为同一成员重新签发，运行中的 Agent 通过执行器更新后续子进程环境）；身份或权限错误（检查目标环境、token 到期时间、`cli.compat` 权限、成员状态及目标项目权限后重新调用）；任务完成（回收任务环境中的 token，保留任务结果及脱敏操作记录） | S3 |
| F-058 | 多业务用户并发运行时，按任务分别传入各自成员的 token；AK/SK 由接入方服务端或密钥管理系统保存，成员 token 通过任务环境传递，Skill 用于描述操作流程 | S3 |

## S4：阿里云 BYOC 事实（F-059–F-074）

来源：[MEOO CLI 进阶：部署到你自己的阿里云账号](https://docs.meoo.com/features/cli-aliyun)。

| 事实编号 | 事实内容 | 来源 |
|---------|---------|------|
| F-059 | `meoo aliyun deploy` 是进阶部署路径：不把作品托管在 Meoo 平台，而是直接在用户自己的阿里云账号下创建真实云资源（ECS、EIP、可选 RDS、可选 SLB 等）；资源归用户管理，账单由用户阿里云账号承担，与 Meoo 平台托管资源分开 | S4 |
| F-060 | Meoo CLI 内置多套云资源编排模板，自动生成并提交 ROS 资源栈，编排 ECS、EIP、RDS、SLB、OSS 等资源；用户不需要自己写云资源 YAML、手动配置部署脚本 | S4 |
| F-061 | 适用场景四条：想要完全自控的云服务器而非平台托管；想用自己账号下的 RDS、负载均衡；有合规或成本要求云资源必须落在自己账号；已有阿里云账号想直接部署 meoo 项目。适用人群：有云资源使用经验的开发者、已有阿里云账号和 AccessKey 的用户、需自控服务器自付账单的团队或个人 | S4 |
| F-062 | 安装最新版 CLI 的 agent 话术（逐字）：`读取 meoo.com/skill-setup.md，并按照说明安装秒悟技能和最新版 meoo cli` | S4 |
| F-063 | 本机需先安装 aliyun CLI：agent 话术「帮我安装 aliyun CLI」，也可按阿里云官方文档手动安装 `https://help.aliyun.com/zh/cli/install-cli` | S4 |
| F-064 | 配置命令（逐字）`aliyun configure`，按提示依次填写：AccessKey ID、AccessKey Secret（抓取稿中该词被截断为「AccessKey Secr」，见转写噪声登记）、Region（例如 `cn-hangzhou`）、Output format（可使用默认值） | S4 |
| F-065 | AccessKey 入口（逐字链接）：查看 AccessKey `https://ram.console.aliyun.com/profile/access-keys`；创建 AccessKey `https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair`；源页建议在 RAM 中创建专用 AccessKey，不建议长期使用主账号 AccessKey | S4 |
| F-066 | AccessKey 最小权限：ECS（创建和管理云服务器）、ROS（创建和管理资源栈）、OSS（临时存放部署产物和 ROS 模板）、STS（身份校验）为必需；RDS 可选（只有项目需要 MySQL 数据库时才用）；SLB 可选（只有选择高可用拓扑时才用）；权限问题去 RAM 控制台 `https://ram.console.aliyun.com/` 配置 | S4 |
| F-067 | 配置完成后让 agent 检查环境，话术（逐字）`帮我检查一下阿里云部署环境`；检查项为 aliyun CLI、账号身份、Region、OSS/ROS/ECS 等能力是否可用 | S4 |
| F-068 | 部署前费用预估话术（逐字）：`先帮我估一下部署到我自己的阿里云账号大概要花多少钱，别真创建资源`；询价不会创建正式 ECS、RDS、SLB 资源，只会临时使用 OSS 上传模板进行询价；输出包含地域、拓扑、ECS 规格、小时单价和月度预估 | S4 |
| F-069 | 部署指令必须明确「我自己的阿里云账号」，示例话术（逐字）：`帮我把这个项目部署到我自己的阿里云账号上，费用我自己出`；部署成功后可看到部署到阿里云账号下的访问链接 | S4 |
| F-070 | 上线后运维操作（源页表格）：更新——`meoo aliyun update` 重新打包上传更新线上版本（单机直接替换，高可用拓扑滚动更新避免同时中断）；状态——`meoo aliyun status --refresh` 显示拓扑、地域、公网 IP、ECS 实例、SLB、RDS、当前版本和 ROS 栈状态；清理——`meoo aliyun delete` 删除 ROS 栈并级联释放 ECS、EIP、RDS、SLB 等资源，删除前需手动输入 `DELETE` 确认；清理后仍应去阿里云控制台亲自核对 ECS、EIP、SLB、RDS、OSS 是否有残留计费资源；健康检查失败先运行 status 或访问公网地址确认（首次启动可能只是装环境慢）；回滚——`meoo aliyun rollback` 使用本地状态文件里记录的上一版产物回滚，若从未执行过 update 可能没有可回滚版本 | S4 |
| F-071 | `meoo deploy` 与 `meoo aliyun deploy` 对比（源页表格）：资源位置（Meoo 托管的基础设施 CDN/函数计算 ↔ 用户自己的阿里云账号 ECS/RDS/SLB）；计费（Meoo ↔ 用户自己的阿里云账号）；登录（需要 `meoo login` ↔ 不需要但要先配好 `aliyun` CLI）；适合谁（绝大多数人的日常发布、分享作品 ↔ 想自控服务器、自付账单的人） | S4 |
| F-072 | 密码不能直接通过命令参数传递（命令行参数可能进入 shell 历史或进程列表）；Meoo 支持交互式输入、环境变量，或自动生成强密码并保存到本地权限收紧的文件里 | S4 |
| F-073 | 自动开通目前只支持 RDS MySQL；PostgreSQL、Redis、MongoDB 需要用户自己在阿里云配置，再把连接信息接入项目 ⚠️ dated | S4 |
| F-074 | 健康检查失败不一定是部署失败：首次启动可能要安装环境和依赖，便宜机型会更慢；先等几分钟访问公网地址或运行 `meoo aliyun status --refresh`，不要立刻删除资源 | S4 |

## 信源登记表（S1–S4）

| 编号 | 类型 | 标题 | URL | 访问日期 | 可达性 |
|------|------|------|-----|---------|--------|
| S1 | 主源 | Meoo CLI 使用指南 | https://docs.meoo.com/features/cli | 2026-10-18 | 匿名可访问，HTTP 200，无重定向，HTML title「Meoo CLI 使用指南 - Meoo」 |
| S2 | 主源 | Meoo 开放平台 | https://docs.meoo.com/open | 2026-10-18 | 匿名可访问，HTTP 200，无重定向，面包屑「Meoo开放能力」 |
| S3 | 主源 | CLI 开放集成接入 | https://docs.meoo.com/open/guides/cli | 2026-10-18 | 匿名可访问，HTTP 200，无重定向，HTML title「CLI 开放集成接入 - Meoo」 |
| S4 | 主源 | MEOO CLI 进阶：部署到你自己的阿里云账号 | https://docs.meoo.com/features/cli-aliyun | 2026-10-18 | 匿名可访问，HTTP 200，无重定向，HTML title 含「部署到你自己的阿里云账号」 |

四源均为秒悟官方文档站 `docs.meoo.com` 公开页面，无 `share?code=`/`token=`/邀请码等访问控制参数。采集方式为 WebFetch（HTML 转 Markdown），转换局限见下「转写噪声登记」。

## 放弃核验清单

以下事项**源页未明示或超出本束 4 个源页范围，本束不予推断**，登记为缺口：

| 缺口事项 | 源页状态 | 处理 |
|---------|---------|------|
| 团队 AK/SK 的具体 HMAC 签名算法细节（串接顺序、签名头名称） | S3 仅称「按团队 AK/SK 的 HMAC 签名协议」，细节在未抓取的「团队系统集成」页（`/open/team-integration`） | 未抓取，不予推断；仅登记延伸阅读 |
| token 接口响应体完整字段与错误码 | S3 仅说明取 `access_token` 和 `expires_in`；通用错误协议在未抓取的 `/open/protocol` | 未抓取，不予推断 |
| 「集成版」权益套餐的额度、价格与上线时间 | S2 仅称「未来随集成版套餐提供」「按届时公布的额度」 | dated，不予推断 |
| 团队版账号的开通路径与费用 | S2/S3 仅出现「团队版」「开放版管理后台」字样，无开通入口说明 | 未抓取，不予推断 |
| 云服务 OpenAPI 与项目导入 API 的接口清单 | S3 仅提及存在该两类 API 及「API Reference」「项目导入、构建与发布」文档 | 未抓取，不予推断 |
| ROS 资源栈的模板内容、默认 ECS 规格区间与具体单价数字 | S4 称询价输出含 ECS 规格/小时单价/月度预估，但未列固定价目 | 源页未给固定值，不予推断 |
| 全链路/仅部署/仅生成三条接入流程的分步细节 | S2 仅给流程入口链接（`/open/guides/full-integration` 等） | 未抓取，不予推断 |
| OAuth 授权的完整授权端点与 Scope 清单 | S2 仅说明不能自行注册、需联系 Meoo 配置 | 未抓取，不予推断 |
| `localhost:3015` 端口是否可配置、被占用时行为 | S1 仅给静态应用默认端口 | 源页未明示，不予推断 |
| 各 CLI 命令的全部参数与退出码 | 源页为教程页，仅出现本台账登记的命令形态 | 以源页为限，不补全 CLI 参考手册 |

## 转写噪声登记（禁入教程正文）

采集为 WebFetch HTML→Markdown 机械转换，以下残片**不是源站内容、禁止出现在本束概念页/示例正文中**，仅在此登记留痕：

| 噪声 | 出处 | 判定 |
|------|------|------|
| `_4d3c6c660f48.png)`、`-3_4d3c6c660f48.png)`、`_4d3c6c660f48.jpeg)` | S4 第 1/2/3/4 节 | 截图丢失 Markdown 图片前缀后的残留，原始图片 URL/alt 不可恢复，不得据其还原图片语义 |
| punycode 乱码域名 `https://meoo.xn--com;-et6fu2kn3dvbv89bue05lda726i28i6z2abw2cea298dh7g7z1apgxbp1dqxaqv./` | S3 第 2 节「服务地址」表格 href | 转换器对「https://meoo.com；联调时……」链接的异常编码，非真实地址；真实生产地址以正文 `https://meoo.com` 为准（F-031、F-047） |
| 占位 href `http://team.member.read/`、`http://skill.md/` | S3 第 2 节权限点名、第 4 节文件名 | 原文是权限点名称 `team.member.read`（F-045）与 Skill 内文件 `SKILL.md`（F-052），非真实外链 |
| 「AccessKey Secr」截断 | S4 第 3 节 | 应为「AccessKey Secret」（交互配置项通用名称），抓取文本被截断；教程正文按「AccessKey Secret」表述并在核验报告注明 |
| 视频时间轴文本 `0:00 / 0:50` | S1 第 3 节 | 页面内嵌视频播放器转换残留，视频源 URL 未出现在转换结果中，不转写视频内容 |

## 单源声明

| 主题 | 涉及事实 | 来源状态 |
|------|---------|---------|
| 个人用户 CLI 安装/登录/预览/部署/FAQ（含全栈云端构建矩阵、1/4/8 套餐口径） | F-001–F-029 | 全部为 S1 单源（官方文档页），无第三方核验 |
| 开放平台身份模式、功能流程与接入红线 | F-030–F-041 | 全部为 S2 单源（官方文档页） |
| 团队 AK/SK 签 token、Skill 安装、MEOO_TOKEN 注入、CI 命令 | F-042–F-058 | 全部为 S3 单源（官方文档页） |
| 阿里云 BYOC 部署与运维 | F-059–F-074 | 全部为 S4 单源（官方文档页） |
| 跨源交叉项：生产环境地址 `https://meoo.com` | F-031、F-047、F-053 | S2/S3 双源一致 |
| 跨源交叉项：Node.js 版本要求 | F-005（20+）、F-046（18+）、F-024（云端镜像 24.15.0） | 三源三处语境不同，并列不调和，详见 [verification.md](verification.md) 核验项二 |
| 跨源交叉项：技能安装话术 `meoo.com/skill-setup.md` | F-007、F-062 | S1/S4 双源（措辞略有差异，各自逐字保留） |

本束 74 条事实均来自秒悟官方文档站自身页面，无独立第三方信源；凡源页带时效条件（限时免费、暂未开放、目前只支持）均已在事实表以 ⚠️ dated 标注。
