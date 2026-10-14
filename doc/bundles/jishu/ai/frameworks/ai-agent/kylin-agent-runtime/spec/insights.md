---
type: reference
title: Kylin Agent Runtime 架构洞察（I 阶段）
description: 基于 facts.md 的 5 条四元组架构洞察（陈述/证据/反常识/行动）与 10+2 文档知识地图，所有证据回指 F/Q 编号。
tags: [kylin-agent-runtime, insights, architecture]
generated: { by: "process:seven-concepts-i/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v/trae-cn", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# Kylin Agent Runtime 架构洞察（I 阶段）

> 每条洞察四元组：**陈述**（可验证判断）/ **证据**（F/Q 编号）/ **反常识**（与直觉预期的冲突点）/ **行动**（对应概念文档的写法决策）。

## 洞察 I-1：三代架构同层共存——遗产大脚本、agent 内核包、新 CLI/前端包

- **陈述**：代码库同时存在三个世代的结构：①14 个顶层 py-modules 巨型脚本（setuptools `py-modules` 平铺分发）；②`agent/` 内核包（120 个 py，承接模型适配、记忆、上下文、技能、供给注册等新逻辑）；③`kylin_agent_runtime_cli/`（94 个 py）+ `web/` + `ui-tui/` 新交互层。`AIAgent.__init__` 本身已退化为转发壳，真正初始化在 `agent.agent_init.init_agent`；两个 CLI（根 `cli.py` 的 HermesCLI 1.3 万行级 与 CLI 包 main.py 1.34 万行级）并存。
- **证据**：F-006（14 个 py-modules）、F-021/F-024（AIAgent 转发壳→init_agent）、F-133/F-134（HermesCLI 与 CLI 包双入口）、Q-001（分包规模）、Q-008（根脚本行数）。
- **反常识**：直觉上"包化重构后旧入口应当消失"；实际旧脚本全部保留且仍是分发主入口，新包通过被旧脚本 import 的方式挂载，形成"壳在旧层、肉在新层"。读者若从 `AIAgent.__init__` 函数体读起会读不到任何真实逻辑。
- **行动**：[01-architecture-module-map](/concepts/01-architecture-module-map.md) 按"遗产脚本层 / agent 内核层 / CLI 与前端层"三代着色画模块图，并明确"读 AIAgent 要跳到 init_agent"；[02-agent-core-loop](/concepts/02-agent-core-loop.md) 以转发壳为第一反差点。

## 洞察 I-2：两套相反的扩展哲学——工具"导入即注册"，内置平台"枚举硬连"

- **陈述**：工具体系是开放注册模型：`discover_builtin_tools()` 先以 AST 静态探测模块顶层是否含 `registry.register(`，再 importlib 导入完成自注册，ToolRegistry 单例承载全部工具。网关平台则是双轨：`Platform` 枚举固定 22 个内置成员，`GatewayRunner._create_adapter` 以 if/elif 链逐个硬连适配器（含 qqbot 子包）；名为 `platform_registry` 的注册表只服务插件平台，快照内观察不到内置平台的注册调用方。
- **证据**：F-046/F-047（AST 预判 + 自注册）、F-049（model_tools 模块级触发发现）、F-103/F-108/F-110（枚举 + if/elif + 注册表插件化）、F-112/F-113（20 文件适配器 + qqbot 子包）、Q-002（32 文件 vs 21 适配器 vs 22 枚举成员的口径差）。
- **反常识**：同一项目内"注册中心"名字最像开放扩展点的地方（platform_registry），内置实现反而绕开它；而没有花哨注册层的 tools/ 才是真正零样板自发现。新增一个内置平台要同时改枚举与工厂两处，与"加一个工具只需丢文件+register"形成鲜明对比。
- **行动**：[04-tool-system](/concepts/04-tool-system.md) 完整讲 AST→import→register 发现链；[08-gateway-and-cron](/concepts/08-gateway-and-cron.md) 专设"平台双轨制"小节，写清扩展内置平台与扩展插件平台的不同路径，并严格区分 32/21/22 三个数字口径。

## 洞察 I-3：openKylin 下游的真实增量在"品牌分发层 + 国产平台/桌面协同 + 供应链合规"，代码符号层保留 Hermes 血缘

- **陈述**：面向用户的分发面已全面麒麟化：包名 `kylin-agent-runtime`、主命令、`~/.kylin-agent-runtime/` 配置目录、portal 标签 `product=kylin-agent`、ACP 注册名 KylinAgent、中文 README 自述"基于 Hermes 改进"。代码符号面则大面积保留上游：author 仍为 Nous Research、FastAPI 标题 `Hermes Agent`、TUI 包名 `hermes-tui`、插件 entry-points 组 `hermes_agent.plugins`、环境变量 `HERMES_*`、ACP 主类 `HermesACPAgent`、console_scripts 保留 hermes/hermes-agent/hermes-acp 三个兼容别名。可观察到的 openKylin 增量包括：KylinAgent 桌面聊天审批协同（kylin_chat_approval，AGENTS.md 首条双仓同步纪律）、CHINA_WEB_ACCESS_GUIDANCE 提示、终端环境默认清华 pip 镜像、钉钉/飞书/企业微信/微信/QQ/元宝国产平台组、kylin-cua 桌面控制技能、ukui-direct-control 技能。
- **证据**：F-005/F-010/F-011（包名命令）、F-015（KylinAgent 注册）、F-018（配置目录与 HERMES 命名）、F-027（中文网络提示）、F-056（清华镜像）、F-095（entry-points 组名）、F-098（kylin-cua/ukui）、F-112/F-114（国产平台与桌面审批）、F-138/F-142（Hermes 命名残留）、F-013（AGENTS.md 标题）、Q-007（1.0.1/0.9.4/0.9.3/0.9.8 多版本号不同步）。
- **反常识**：fork 项目给人的预期是"全面改名切割"；实际策略是"分发品牌层改名、代码符号层不改名"，这是一种降低与上游持续合并成本的工程选择，而非改名不彻底的疏忽；版本号四处不同步（打包 1.0.1、CLI 0.9.4、ACP 0.9.3、kylin-cua 0.9.8）也说明各组件按独立节奏发布。
- **行动**：[00-overview](/concepts/00-overview.md) 设"与 Hermes 的血缘与差异"专节，用"分发层 vs 符号层"两张对照表陈述；[06-skills-and-plugins](/concepts/06-skills-and-plugins.md) 与 [08-gateway-and-cron](/concepts/08-gateway-and-cron.md) 标注麒麟增量；全束与既有 [hermes-agent](../../hermes-agent/index.md) 束交叉链接，不重复其上游内容。

## 洞察 I-4："自进化"由三条带不同治理强度的学习回路构成，而非单一记忆机制

- **陈述**：README 宣称的自进化闭环在代码里是三套独立机制：①技能策展——curator 以 LLM 评审技能、按 idle/stale/archive 规则自动状态流转，配套快照备份与回滚；②用户画像——110 个字段定义（81 当前 + 29 遗留），推断写入要求 confidence ≥ 0.70，boundary 生命周期字段只接受显式声明，存储用 Fernet 加密、用户身份用 HMAC-SHA256 假名化；③会话记忆——SessionDB 9 张业务表 + 2 张 FTS5 虚表（普通 FTS5 + trigram 分词器支撑中日韩子串检索），InsightsEngine 在其之上做工具/技能使用统计。
- **证据**：F-086（InsightsEngine）、F-087（curator + 备份）、F-089/F-090/F-091（画像字段、置信度门槛、加密与假名化）、F-129~F-132（表与 FTS5、检索方法）、Q-006/Q-010。
- **反常识**：营销语里一个"自进化"，工程上是三套存储、三套策略；最反直觉的是"学习用户"并非无约束写入——boundary 字段（身份边界类）必须用户显式提供、推断信息有置信度门槛、落盘即加密、对外身份不可逆假名化，治理设计先于功能。
- **行动**：[07-memory-and-context](/concepts/07-memory-and-context.md) 按"会话检索层 / 上下文压缩层 / 用户画像层 / 技能策展层"四层组织，把治理字段（0.70、boundary、Fernet、HMAC、trigram）作为记忆点而非脚注。

## 洞察 I-5：供应链安全是架构约束——精确钉版、懒安装收敛爆炸半径、脱敏与写保护纵深

- **陈述**：核心 dependencies 全部 `==` 精确钉版，注释明确记录 2026-05-12 Mini Shai-Hulud 蠕虫事件为收紧动因；`[all]` extra 的策略反向收窄——只收"每个会话都需要/进入 Agent 循环前必须就位/Packager 需打进 wheel"的包，所有可选后端（模型、搜索、TTS、图像、记忆、消息平台、终端沙箱）改为首用时懒安装。运行侧还有 36 条密钥正则日志脱敏、16 个写拒绝精确路径 + 9 个目录前缀、Shell 钩子 allowlist 三道纵深。
- **证据**：F-003（钉版与事件注释）、F-004（[all] 收窄策略与移出清单）、F-042（写黑名单）、F-043（脱敏）、F-044（hook allowlist）。
- **反常识**：名为"all"的安装集合在安全事件后刻意变小；"方便"让位于"一个被投毒的 PyPI 包不能自动到达每一个新装环境"。这不是依赖洁癖，而是事件驱动的爆炸半径治理。
- **行动**：[05-model-providers](/concepts/05-model-providers.md) 讲懒安装与凭证池/轮换时回扣这条约束；[02-agent-core-loop](/concepts/02-agent-core-loop.md) 安全护栏小节把脱敏/写保护/hook 授权串成一条纵防线。

## 知识地图（10 概念 + 2 示例 → 事实覆盖与链接关系）

| 文档 | 学习目标 | 主要事实覆盖 | 前置/关联 |
|---|---|---|---|
| concepts/00-overview | 定位、自进化闭环、版本与 Hermes 血缘、SIG 归属 | F-001~F-020、Q-007；SIG 信源 | 入口；→ hermes-agent 束 |
| concepts/01-architecture-module-map | 三代架构模块图、依赖链、技术栈 | F-006、F-021~F-024、F-102、F-129、Q-001、Q-008 | 00 |
| concepts/02-agent-core-loop | 转发壳→init_agent、对话环、工具迭代、护栏/重试/预算 | F-025~F-045 | 01 |
| concepts/03-cli-and-tui | 双 CLI、48 子命令、setup/dashboard、TUI 三件套 | F-133~F-144、Q-004 | 00、01 |
| concepts/04-tool-system | 自注册发现链、31 工具集、终端 8 后端、computer_use | F-046~F-060、Q-003、Q-009 | 02 |
| concepts/05-model-providers | 4 传输、provider 路由、凭证池、懒安装、元数据/定价 | F-061~F-080、F-003~F-004 | 02 |
| concepts/06-skills-and-plugins | 技能树/curator/插件 17 钩/四类供给注册 | F-087、F-088、F-094~F-101、Q-005 | 02、07 |
| concepts/07-memory-and-context | 压缩引擎、@引用、记忆 ABC、画像三层治理、SessionDB FTS | F-081~F-086、F-089~F-093、F-129~F-132、Q-006、Q-010 | 02 |
| concepts/08-gateway-and-cron | GatewayRunner、平台双轨、21 适配器、会话存储、cron 函数式调度 | F-102~F-117、F-125~F-128、Q-002 | 01、04 |
| concepts/09-acp-mcp-protocols | ACP stdio 服务器、MCP 10 工具、LSP 26 服务器 | F-118~F-124、Q-004 | 02、03 |
| examples/01-install-setup-first-run | uv 安装→setup→四种运行→测试 | F-010、F-011、F-0145；README.zh-CN | 00、03 |
| examples/02-gateway-and-cron-usage | systemd 网关服务 + cron 作业管理 | F-012、F-125、F-126、F-136 | 08 |

学习路径：00 → 01 → 02 为主干；03/04/05 为运行与能力展开；06/07 为自进化深水区；08/09 为对外连接（消息平台、编辑器协议）；两篇示例对应"首次上手"与"后台服务化"两个落点。
