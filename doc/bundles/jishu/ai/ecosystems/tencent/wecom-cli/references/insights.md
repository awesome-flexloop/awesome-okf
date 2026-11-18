---
type: reference
title: wecom-cli 架构洞察（I 阶段）
description: 基于 F-001–F-172 条源码事实提炼的 wecom-cli 核心机制洞察与 concepts/ 知识地图
tags: [wecom, wecom-cli, rust, cli, architecture, insights]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: I（架构洞察）
baseline: 1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde（npm @wecom/cli 1.3.4）
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# wecom-cli 架构洞察（I 阶段）

> 本文基于 [facts.md](facts.md) 登记的 F-001–F-172 条源码事实，按「陈述 / 证据 / 反常识 / 行动」四段式提炼 6 条机制洞察。文中不引入 facts.md 之外的新事实；编号一经引用即为唯一证据源。

## I-01：命令树是服务端 schema 的投影，本地只保留装配骨架

**陈述**：wecom-cli 的可用命令集合不是编译期写死的 clap 定义，而是运行时按服务端下发的 service 列表与各 resource/method 的 schema 动态装配到 clap 命令树上；本地代码只提供装配算法、缓存与兜底子命令。

**证据**：F-034（根命令以 `Command::new` 构造并设 `arg_required_else_help`）、F-037（仅目标服务传入 `target_schema`，其余服务以 `None` 构建骨架树）、F-044（两阶段装配：先异步收集 service_list 与 schema，再在同步闭包内用纯函数建树）、F-068（registry 缓存 TTL 为 60 秒）、F-069（缓存过期即向远端重取）。

**反常识**：通常 CLI 的命令集合与二进制版本强绑定，只有升级 CLI 才会获得新命令；这里命令面的新鲜度由缓存 TTL（60 秒）而非发布节奏决定——二进制不变，"能力面"仍可变。

**行动**：排查"命令不存在"时先分清是本地骨架问题还是服务端 schema/缓存问题，按 F-052 的 `schema list` 与缓存状态/清理命令取证；构造回归用例时以"骨架树 + 动态填充"为模型，必须同时覆盖目标服务注入 schema 与其余服务传 `None` 两条路径。

## I-02：双域沙箱把"写能力"分域，deny 是独立于 allow 的恒真否决层

**陈述**：路径安全由两个独立文件系统域承担——私有域 roots 仅 `[config_dir]`，工作域 roots 为 `[cwd, 固定临时目录]` 且叠加对 config_dir 的 deny；deny 规则独立于 allow，即便 roots 为 `None`（不受目录限制）仍然生效。

**证据**：F-116（规则在构造期注入，roots 与 deny 无环境变量/命令行扩展口）、F-118（工作域 roots 为 cwd，并按 `pinned_temp_dir()` 追加固定临时目录）、F-120（内建 deny glob 共 34 条，分四组）、F-124（多段凭据库含 `**/.config/wecom`）、F-128（deny 恒优先；默认 deny 为空，须显式注入才生效）。

**反常识**：直觉上"沙箱"等于把操作限制在某个目录内；这里即使解除目录限制（roots 为 `None`），凭据形状的文件仍会被拒绝。安全模型是两条正交轴——"写只能落在哪"（能力最小化）与"秘密长什么样不可读写"（模式否决），不是单一半径大小。

**行动**：新增写入类功能时必须显式选择域（私有域 vs 工作域），不要试图用环境变量扩根；安全测试把"无 roots 时 deny 仍命中"列为必测不变量，并覆盖 F-169 登记的符号链接逃逸等 12 例 `sandbox_paths` 场景。

## I-03：加密落盘 + 环境变量优先，构成"有本地状态但可无状态运行"的边界

**陈述**：默认路径把凭据加密为 `credentials.enc`（AES-256-GCM），但解析时只要 `WECOM_CLI_ACCESS_TOKEN` 非空就直接返回 Env 授权、完全绕过文件；同时 853004 会触发静默刷新并重放原请求。

**证据**：F-077（凭据路径为 `default_home_dir()/credentials.enc`）、F-080（加密算法为 `Aes256Gcm`）、F-091（解析优先级中 Env 分支先于文件）、F-092（`TOKEN_EXPIRED_ERRCODE = 853004`）、F-093（命中后调用刷新并重放原请求）。

**反常识**：加密落盘常被当成"安全的唯一真相源"；此设计的真相源优先级是 env > 文件，且 token 过期由传输后端透明修复。因此同一二进制在 CI（纯 env）与本机（加密文件）行为一致，但排障时可观察的证据面完全不同。

**行动**：排障先判定授权来源——`auth show --status` 只区分 authorized/unauthorized、不区分来源（F-100），需结合环境变量是否设置与凭据文件是否存在交叉判断；把"env 覆盖文件""刷新失败保留原错误"作为契约测试项。配置目录可经 `WECOM_CLI_CONFIG_DIR` 改道，空值视为未设置（F-095）。

## I-04：韧性策略被收编进 transport，而非散落在各 service

**陈述**：轮询间隔与长任务超时、连续网络错误上限、断点续传段长与终止条件、请求超时缺省值，全部由 `wecom-transport` 的常量与类型承载；service 层只负责组装 payload 与分流输出。

**证据**：F-101（三个默认常量，含 `MAX_CONSECUTIVE_NETWORK_ERRORS = 3`）、F-103（轮询模式枚举 `PollMode`）、F-105（超时起点记录与逐轮比较）、F-110（续传段数上限 4096、单段上限 64 MiB）、F-113（timeout 默认 `None`，仅显式设置才写入）。

**反常识**："默认不设 HTTP 超时"看似鲁棒性缺陷，但与轮询自身的 task_timeout、以及连续网络错误上限组合后，超时语义被收敛为"每个长任务自带超时"，避免 HTTP 层与业务层双重计时互相干扰。

**行动**：新增长任务接口时优先复用 transport 的轮询/续传机制，不要在 service 内重复写 sleep/retry；压测覆盖"短读不终止""416 终止""已知 total 提前终止"三类边界。

## I-05：Skills 层的 14 vs 15 是文档漂移的显影剂，`requires.bins` 才是可执行性契约

**陈述**：同一基线上，AGENTS.md 记 14 个 Skill，docs/skills.md 记 15 行，磁盘实际为 15 个目录；14 个 SKILL.md 声明 `metadata.requires.bins: ["wecom-cli"]`，唯一例外 `wecomcli-shared` 只承担前置检查并声明版本下限 1.2.1。

**证据**：F-137（磁盘 15 个技能目录）、F-139（14 个 SKILL.md 含 bins 声明）、F-140（shared 技能声明版本下限 1.2.1）、F-151（AGENTS.md 的 14 口径）、F-152（docs/skills.md 的 15 行口径）。

**反常识**：文档数字不一致并不影响技能可用性——真正决定"能不能跑"的是 SKILL.md frontmatter 的 bins 依赖声明与 shared 的版本检查，技能计数只是导航层元数据。

**行动**：校验 Skills 以"目录数 + bins 声明覆盖率（14/15）+ shared 前置检查"三项为准，不采信 AGENTS.md 的 14；更新文档时按 F-154 的指向关系同时修改 AGENTS.md 与 docs/skills.md 两处。

## I-06：文档-代码漂移成对出现，单一主入口原则管不住被内联复述的计数

**陈述**：基线中存在两组并置口径差异：Skill 计数 14 vs 15；crate 计数 3 vs 5（docs/development.md 写三个 crate，Cargo.toml members 为五个）。而 docs/README.md 自述"同一主题只保留一个主入口"。

**证据**：F-151 / F-152（Skill 计数的两组口径）、F-164（development.md 的 3 crate 表述）、F-165（Cargo.toml 的 5 个成员）、F-157（docs/README.md 的单一主入口原则）。

**反常识**：漂移不是随机笔误，而是"叙述型文档（AGENTS.md、development.md）与清单型文档（Cargo.toml、skills 目录）由不同维护动作驱动"的结构性结果；单一主入口原则约束了导航，却没约束被内联复述的计数。

**行动**：任何"数量"表述建立单一来源（members 数组、skills 目录），其余位置改为链接引用；审计脚本把"结构表 vs 清单"的差异列为告警项，而不是只查链接可达性。

## concepts/ 知识地图

以下 8 篇概念文档已在 E 阶段落盘，本节记录其主题、覆盖要点与学习路径；编号范围为事实引用区间，写作时不得越出 facts.md 已登记事实。

### 00-overview（定位与安装）

- **一句话概要**：从 npm 包形态到五平台子包再到具体二进制的分发链路，以及 wecom-cli 的仓库定位与适用边界。
- **覆盖要点**：
  - 包元数据与 bin 入口（F-009 ~ F-011、F-015 ~ F-017）
  - 五平台子包与 fixed 版本策略（F-019 ~ F-021）
  - 安装命令、Node 版本与许可证（F-162、F-163）
  - 仓库形态与受控文件规模（F-001、F-003）
- **前置文档**：无。
- **学习目标**：能完整复述"`npx` / 全局安装 → 平台子包 → 可执行文件 → 子命令"的链路，并说明其边界。

### 01-command-model（命令模型）

- **一句话概要**：一次调用如何经过 argv 预判、两阶段命令树装配、clap 解析与 handler 分派，最终落到统一错误与退出码。
- **覆盖要点**：
  - 入口与 argv 预判（F-033、F-041、F-043）
  - 两阶段建树与 schema 注入（F-037 ~ F-045）
  - 四类命令形态与全局 flag（F-046 ~ F-052）
  - helper/method 分派与 SKILL_HINT（F-054 ~ F-058）
  - 错误语义与退出码（F-045、F-059、F-172）
- **前置文档**：00-overview。
- **学习目标**：能对任意一次调用判断它落在装配、解析还是分派阶段，并解释对应错误码来源。

### 02-crate-architecture（五 crate 架构）

- **一句话概要**：workspace 五成员（CLI、核心库、FS、transport、显示）的职责边界、依赖方向与对外导出面。
- **覆盖要点**：
  - workspace 成员与 features（F-001 ~ F-008）
  - 核心库导出面（F-060 ~ F-062）
  - 默认 FS 实现的归属关系（F-129、F-130）
  - 文档 3 vs 实际 5 的口径差（F-164、F-165）
- **前置文档**：01-command-model。
- **学习目标**：能给定任一模块，指出其归属 crate、可依赖方向与对外可见符号。

### 03-auth-session（认证与会话）

- **一句话概要**：env / 加密文件 / 扫码三条授权来源的优先级、加密存储实现与 853004 静默刷新回路。
- **覆盖要点**：
  - 凭据路径与加密存储（F-076 ~ F-080）
  - 扫码与首次授权引导（F-081 ~ F-090）
  - 授权解析优先级（F-091）
  - 刷新与重放（F-092、F-093）
  - auth 子命令语义（F-096 ~ F-100）
  - 配置目录改道（F-095）
- **前置文档**：00-overview、01-command-model。
- **学习目标**：能画出三条授权来源的优先级判定图，并说明静默刷新失败时的可观察结果。

### 04-transport-resilience（传输与韧性）

- **一句话概要**：HTTP 调用、响应封套、长任务轮询、断点续传与超时策略在 transport 层的收编方式。
- **覆盖要点**：
  - 默认常量与用途（F-101）
  - ApiResponse 与信封协议（F-106 ~ F-109）
  - 长任务轮询类型与适配（F-102 ~ F-105、F-115）
  - 断点续传与终止信号（F-110 ~ F-112）
  - 超时缺省语义（F-112、F-113）
  - discovery 载荷与分页输出（F-072、F-074、F-075）
- **前置文档**：03-auth-session。
- **学习目标**：能说明一个长任务从提交、轮询、续传到分页输出的完整时序及各级超时归属。

### 05-sandbox-security（沙箱与安全）

- **一句话概要**：双域沙箱的构造规则、内建 deny 清单、平台差异，以及 trace/遥测的安全边界。
- **覆盖要点**：
  - 双域 roots 与构造期注入（F-116 ~ F-119）
  - 34 条内建 deny glob 与平台专属规则（F-120 ~ F-124）
  - deny 恒优先与默认空集（F-128）
  - 固定临时目录（F-131）
  - trace 与遥测（F-132 ~ F-136）
  - 安全 e2e 场景（F-169）
- **前置文档**：02-crate-architecture、03-auth-session。
- **学习目标**：能判断任一读写路径属于哪个域、是否命中 deny，并说明该路径在三个平台上的差异。

### 06-skills-layer（Skills 层）

- **一句话概要**：15 个技能目录的职责分工、SKILL.md 契约（bins 声明与版本下限）与导航表维护关系。
- **覆盖要点**：
  - 技能目录与体量（F-137、F-138、F-141 ~ F-149）
  - bins 声明与 shared 前置（F-139、F-140）
  - 导航表与 14 vs 15 口径（F-151、F-152）
  - SKILL_HINT 与版本检查（F-058、F-140）
- **前置文档**：01-command-model、05-sandbox-security。
- **学习目标**：能按 SKILL.md 契约判断某技能是否可执行，并定位其配套参考材料。

### 07-dev-release（开发与发布）

- **一句话概要**：从本地脚本、代码门禁、changeset 到五包同版发布的完整工程链路，以及文档与 e2e 规范。
- **覆盖要点**：
  - 开发脚本与工具链版本（F-012 ~ F-014）
  - 构建 profile、rustfmt、commitlint、lefthook、eslint、prettier（F-023 ~ F-031）
  - changeset fixed 发布（F-018 ~ F-021）
  - 文档规范与单一主入口（F-155 ~ F-161）
  - 文档口径差异（F-164 ~ F-166）
  - e2e 结构与用例计数（F-167 ~ F-170）
- **前置文档**：02-crate-architecture。
- **学习目标**：能独立完成"改代码 → 通过门禁 → 写变更集 → 五包同版发布"的全过程。