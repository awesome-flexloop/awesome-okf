---
type: Concept
title: Kylin Agent Runtime 总览：面向 openKylin 的自进化智能体运行时
description: openKylin 基于 Hermes 改进的自进化智能体运行时，涵盖三条学习回路、九种运行形态、多版本号现状、Hermes 血缘对照与 AISubsystem SIG 归属。
tags: [kylin-agent-runtime, overview, openkylin, hermes, self-evolution]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
  - id: community-sig
    resource: /references/community-sig.md
    title: openKylin AISubsystem SIG 信源
---

# Kylin Agent Runtime 总览：面向 openKylin 的自进化智能体运行时

Kylin Agent Runtime 是 openKylin 社区在 Hermes Agent 之上改进的智能体运行时，中文 README 首句自述为"基于 Hermes 改进的自进化智能体运行时"，仓库托管于 openKylin Gitee 组织，要求 Python 3.11，以可编辑模式安装（F-010、F-001）。它保留了 Hermes 的对话内核、工具体系与多模型传输层，同时在分发品牌、国产消息平台、桌面协同与供应链合规上叠加 openKylin 增量（I-3）。

本篇给出项目定位、自进化三条回路、版本号现状、九种运行形态、Hermes 血缘对照与社区归属。固定事实基线为 commit `ee0c1709199b37ebccdc69b545f266e52e5ed6c9`（master，2026-10-13），`git describe` = `V0.9.4-52-gee0c170`。

## 项目定位

`pyproject.toml` 声明 name = "kylin-agent-runtime"、version = "1.0.1"、requires-python = ">=3.11"、license = MIT、authors = [{name = "Nous Research"}]（F-001）。上游血缘在仓内仍然显眼：开发指南 AGENTS.md 标题为 "Hermes Agent - Development Guide"，功能清单文档标题为 "Hermes Agent 功能清单"（F-013、F-017）。

"自进化"在代码中不是单一记忆机制，而是三条治理强度不同的学习回路（I-4）：技能策展回路让技能库随使用自动流转状态，用户画像回路在置信度门槛和加密存储下学习用户，会话记忆回路以 SQLite 全文检索沉淀全部会话。三者各自有独立存储、独立策略，详见 [记忆与上下文](/concepts/07-memory-and-context.md)。

## 自进化闭环的三条回路

| 回路 | 核心机制 | 治理约束 | 证据 |
|---|---|---|---|
| 技能策展 | curator 以 LLM 评审技能，`run_curator_review` / `maybe_run_curator` 按 idle、stale、archive 规则自动状态流转，配套 `snapshot_skills` 快照备份与 `rollback` 回滚 | 自动流转受 `should_run_now` 规则约束，可暂停，回滚有备份链 | F-087 |
| 用户画像 | 110 个字段定义（FIELDS 81 个 + LEGACY_FIELDS 29 个），`RuntimeUserProfile.observe` 抽取画像条目 | 推断写入要求 confidence ≥ 0.70；boundary（身份边界）生命周期字段只接受 explicit 显式声明；落盘走 Fernet 加密的 EncryptedFileProfileStore；对外身份用 HMAC-SHA256 生成 `v1_` 前缀假名 ID | F-089、F-090、F-091、Q-010 |
| 会话记忆 | SessionDB 持久化会话与消息，InsightsEngine 在其上聚合会话、工具、技能使用统计 | 9 张普通表 + 2 张 Telegram 迁移表 + 2 张 FTS5（全文检索虚表），其中 trigram 分词器支撑中日韩文字子串检索 | F-086、F-129~F-132、Q-006 |

三条回路中，画像回路的治理最强：字段分 static/dynamic/boundary 三类生命周期，密钥经环境变量 KYLIN_PROFILE_KEY 注入，抽取器读 KYLIN_PROFILE_LLM_* 配置，onboarding（入门引导）固定询问称呼、年龄、职业三问（F-090、F-091）。

## 多版本号并存的现状

快照内五个版本号各按独立节奏发布，并不一致（Q-007）：

| 版本号 | 位置 | 值 | 含义 |
|---|---|---|---|
| 打包版本 | pyproject.toml | 1.0.1 | wheel 分发包版本（F-001） |
| 上游 tag 血缘 | git describe | V0.9.4-52 | 最近上游 tag V0.9.4 之后 52 个提交（Q-007） |
| CLI 包版本 | kylin_agent_runtime_cli/__init__.py | 0.9.4（发布日期 2026.7.24） | 新 CLI 自身版本（F-014） |
| ACP 注册版本 | acp_registry/agent.json | 0.9.3 | uvx 分发包 `kylin-agent-runtime[acp]==0.9.3`（F-015） |
| 桌面控制技能 | skills/kylin-cua/version | 0.9.8 | kylin-cua 技能独立版本（F-016） |

ACP（Agent Client Protocol，代理客户端协议）注册清单中 id = "kylin-agent"、name = "KylinAgent"，入口参数固定为 `["hermes-acp"]`（F-015）。

## 九种运行形态

功能清单列出同一内核的九种运行形态（F-017）：

| # | 形态 | 入口/载体 |
|---|---|---|
| 1 | 经典命令行 | `hermes` 兼容命令（F-005、F-017） |
| 2 | Ink TUI（Terminal User Interface，终端文本界面） | `--tui` 启动（F-011） |
| 3 | 消息网关 gateway | systemd 用户服务 `kylin-agent-runtime-gateway.service`（F-012） |
| 4 | OpenAI 兼容 API server | 网关平台适配器之一（F-017、F-108） |
| 5 | Web Dashboard | `dashboard` 子命令，默认端口 9119（F-011、F-138） |
| 6 | ACP 代理 | `hermes-acp` 命令，stdio 传输（F-005、F-118） |
| 7 | Cron 定时任务 | cron 包函数式调度，tick/run_job 投递（F-125、F-126） |
| 8 | Batch Runner 批处理 | 根模块 batch_runner.py（1278 行，F-149） |
| 9 | 库式 AIAgent API | 直接实例化 run_agent.AIAgent（F-021） |

console_scripts 注册 4 个入口：`kylin-agent-runtime` 与兼容别名 `hermes` 同指 kylin_agent_runtime_cli.main:main，`hermes-agent` 指 run_agent:main，`hermes-acp` 指 acp_adapter.entry:main（F-005）。

## Hermes 血缘与 openKylin 增量

下游改造呈现清晰的两层策略：面向用户的分发面全面麒麟化，代码符号面大面积保留上游命名。这不是改名不彻底，而是压低与上游持续合并成本的工程选择（I-3、E-003）。

**分发层（已麒麟化）**：

| 维度 | 现状 | 证据 |
|---|---|---|
| 包名/主命令 | kylin-agent-runtime | F-001、F-005 |
| 用户配置目录 | `~/.kylin-agent-runtime/`（config.yaml 放配置、.env 只放密钥、logs/ 三类日志） | F-018 |
| ACP 注册 | id kylin-agent、name KylinAgent | F-015 |
| 产品标签 | portal 标签返回 product=kylin-agent | I-3、E-003 |
| 中文自述 | "基于 Hermes 改进的自进化智能体运行时" | F-010 |

**代码符号层（保留 Hermes 血缘）**：

| 维度 | 现状 | 证据 |
|---|---|---|
| 作者元数据 | authors = Nous Research | F-001 |
| FastAPI 标题 | title="Hermes Agent" | F-138 |
| TUI 包名 | name="hermes-tui" | F-142 |
| 插件 entry-points 组 | "hermes_agent.plugins" | F-094 |
| 环境变量/目录变量 | HERMES_* 环境变量、hermes_home 大量留存 | F-018 |
| ACP 主类 | HermesACPAgent | F-118 |
| 兼容命令 | hermes / hermes-agent / hermes-acp 三个别名保留 | F-005 |
| 开发指南标题 | "Hermes Agent - Development Guide" | F-013 |

**可观察到的 openKylin 增量**：

- 国产消息平台组：钉钉、飞书、企业微信（含回调模式）、微信、QQ、元宝均有平台枚举成员与适配器实现，另有 api_server、webhook 等通用入口（F-108、F-112、F-113）。
- KylinAgent 桌面聊天审批协同：网关侧 kylin_chat_approval.ChatApprovals 处理聊天应用内审批（F-114）。
- 终端环境默认 pip 索引为清华镜像 `https://pypi.tuna.tsinghua.edu.cn/simple`（DEFAULT_PIP_INDEX_URL，F-056）。
- 提示词内建 CHINA_WEB_ACCESS_GUIDANCE（中文网络环境访问指引）片段（F-027）。
- 桌面协同技能：skills/kylin-cua（版本 0.9.8）与 ukui-direct-control（F-016、F-098）。
- 供应链收紧：核心依赖全部 `==` 精确钉版，注释记录 2026-05-12 Mini Shai-Hulud 蠕虫事件后收紧；`[all]` extra 反向收窄，可选后端首用时懒安装（F-003、F-004、I-5）。

## 社区归属：AISubsystem SIG

项目仓库归属于 openKylin Gitee 组织，社区对应 openKylin AISubsystem SIG（Special Interest Group，特别兴趣小组，SIG 120），邮件列表为 aisubsystem@lists.openkylin.top。该 SIG 使命三条（信源 community-sig）：

1. 负责 AI 子系统相关软件包的规划、维护和升级；
2. 管理本地和云端大模型，屏蔽各个大模型和框架的差异，提供 AI 基础能力和特定场景相关的 SDK 接口；
3. 打造麒麟 OS Agent。

Kylin Agent Runtime 对应第 3 条"打造麒麟 OS Agent"的运行时形态；其 anthropic_messages、bedrock_converse、chat_completions、codex_responses 四类注册传输对应第 2 条"屏蔽大模型和框架差异"（Q-004、F-064）。SIG 仓库清单为 9 页 JavaScript 动态加载页面，静态抓取仅得首页，因此本束不断言 agent-runtime 登记于清单第几页。

## 技术基线与上手入口

构建后端为 setuptools（>=61.0），console_scripts 之外还声明 14 个顶层 py-modules 与 agent、tools、gateway、acp_adapter、plugins、providers 等 find 包（F-002、F-006、F-007）。测试走 pytest，配置 `-n auto --timeout=30`，另有 integration、real_concurrent_gate 标记（F-009）。分发包把 web_dist/tui_dist、gateway/assets、插件 dashboard 产物纳入 package-data（F-008）。

README 给出的安装与首发命令（F-010、F-011）：

```bash
git clone https://gitee.com/openkylin/agent-runtime.git
uv pip install -e ".[all]"
kylin-agent-runtime setup
kylin-agent-runtime          # 进入对话
kylin-agent-runtime --tui    # Ink TUI
kylin-agent-runtime -z "..." # 单次问答
kylin-agent-runtime dashboard
```

网关可安装为 systemd 用户服务，支持 start/stop/restart/status/enable/disable 与 journalctl 日志查看（F-012）。仓库另含 Dockerfile、docker-compose.yml 与 docker/entrypoint.sh 等容器资产，nix/ 下 11 个 Nix 表达式，以及 setup-kylin-agent-runtime.sh 与 scripts/install.{sh,ps1,cmd} 安装脚本（F-019、F-020）。

可选能力经 optional-dependencies 分组安装，extra 含 anthropic、mcp、acp（agent-client-protocol==0.9.0）、bedrock、web（fastapi==0.133.1 + uvicorn）、dingtalk、feishu、google、voice、computer-use 等；`[all]` 只收不可懒安装的包，模型、搜索、TTS、图像、记忆、消息平台等后端改为首用时懒安装（F-004、I-5）。

## 配置目录与横切能力

用户态数据集中在 `~/.kylin-agent-runtime/`：config.yaml 存放配置，.env 只放密钥，logs/ 下分 agent.log、errors.log、gateway.log 三类日志（F-018、F-147）。日志由 kylin_agent_runtime_logging.setup_logging 统一配置，用户目录经 kylin_agent_runtime_constants.get_hermes_home / display_hermes_home 解析，路径带 profile 感知（F-147）。代码内仍大量保留 hermes 命名，HERMES_* 环境变量与 hermes_home 是符号层血缘的一部分（F-018、I-3）。

国际化覆盖 16 个语言码（en、zh、zh-hant、ja、de、es、fr、tr、uk、af、ko、it、ga、pt、ru、hu），DEFAULT_LANGUAGE = "en"，locales/ 下 16 个 YAML 对应，经 get_language/t 取词（F-145）。进程引导侧 process_bootstrap 提供 _OpenAIProxy 代理与 _install_safe_stdio 安全标准 IO，user_directories 按 sys.platform 分平台返回路径（F-146）。

批处理与评测资产同仓发布：batch_runner.py（1278 行）承担批量任务，agent_eval_runner.py（470 行）跑智能体评测，mini_swe_runner.py（701 行）跑小型 SWE 任务，trajectory_compressor.py（1465 行）压缩轨迹；tests/ 含 1199 个 py 与 acp、agent、cli、cron、gateway、tools、run_agent 等测试包（F-149、Q-001）。

## 相关概念

- [架构与模块地图](/concepts/01-architecture-module-map.md) —— 三代同层结构与读码路径
- [Agent 核心对话环](/concepts/02-agent-core-loop.md) —— AIAgent 转发壳与迭代机制
- [CLI 与 TUI](/concepts/03-cli-and-tui.md) —— 双 CLI、48 个子命令与 Dashboard
- [hermes-agent](../../hermes-agent/index.md) —— 上游 Hermes Agent 知识束
- [AISubsystem SIG 信源](/references/community-sig.md) —— 社区归属与采集边界
