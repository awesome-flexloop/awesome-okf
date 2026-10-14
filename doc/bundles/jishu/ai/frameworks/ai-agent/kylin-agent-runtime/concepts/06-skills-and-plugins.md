---
type: Concept
title: 技能与插件：三层技能树、curator 策展与 17 钩插件体系
description: 两类扩展机制：三层技能树与 curator 自动策展、PluginManager 三来源装载、17 个生命周期钩子与四类能力注册。
tags: [kylin-agent-runtime, skills, plugins, curator, provider-registry]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 技能与插件：三层技能树、curator 策展与 17 钩插件体系

技能（skill，带 SKILL.md 元数据的可装载知识/流程包）与插件（plugin，以钩子介入运行时生命周期的 Python 模块）是 Kylin Agent Runtime 的两类一等扩展机制。技能回答"模型在特定任务上该知道什么、按什么步骤做"，插件回答"运行时事件发生时代码如何介入"。本文覆盖技能的三层目录与运行时四件套、curator（技能策展器，自动评审与状态流转的治理进程）、PluginManager 的装载与 17 个生命周期钩子、内置插件目录与四类能力 Provider 注册，并标注 openKylin 下游增量（F-087/F-088/F-094~F-101，Q-004/Q-005）。

## 三层技能目录

技能文件分布在三个层级，运行时由 `get_all_skills_dirs`（agent/skill_utils.py:273）汇总（F-088/F-098/F-099）：

1. **内置技能树 `skills/`**：随发行版分发。快照内顶层目录条目 25 个（含隐藏的 `.curator_backups`），递归有 77 个 `SKILL.md`（Q-005，本批以 Glob 机械复核为 77 个文件）。树根有 4 个状态文件：`.bundled_manifest`（发行清单）、`.curator_state`（策展状态）、`.usage.json` 与 `.usage.json.lock`（使用计数及其锁）（F-098）。分类目录涵盖 creative/p5js、dogfood、email/himalaya、github（6 个技能）、kylin-cua、mcp/native-mcp、media/songsee、research/arxiv、yuanbao、ukui-direct-control、autonomous-ai-agents、productivity、software-development 等（F-098）。
2. **可选技能库 `optional-skills/`**：顶层 17 个分类目录——autonomous-ai-agents、blockchain、communication、creative、devops、dogfood、email、finance、health、mcp、migration、mlops、productivity、research、security、software-development、web-development，根目录带 `DESCRIPTION.md` 说明（F-099，17 个分类经本批 `Get-ChildItem` 机械复核，Q-005）。
3. **外部目录**：`get_all_skills_dirs` 除上述两处外还汇总用户配置的外部技能目录，使企业/个人技能库不必放入仓库即可被发现（F-088）。

内置与可选的分工是发行策略：`skills/` 中的技能开箱即用且状态受 curator 管理，`optional-skills/` 是更大的按需取用池，外部目录则留给部署侧自定义（F-098/F-099）。

## 技能运行时四件套

技能从"磁盘上的目录"变成"模型可调用的能力"，由 `agent/` 下四个模块协作完成（F-088）：

| 模块 | 关键函数 | 职责 |
|---|---|---|
| skill_bundles.py | `scan_bundles`（:168）、`get_skill_bundles`（:195）、`build_bundle_invocation_message`（:253） | 扫描技能包（多文件打包形态）并构造调用消息 |
| skill_commands.py | `scan_skill_commands`（:263）、`build_skill_invocation_message`（:428） | 扫描技能附带的命令并构造调用消息 |
| skill_preprocessing.py | `preprocess_skill_content`（:123） | 技能内容预处理：模板变量替换 + inline shell（内联 shell）片段执行 |
| skill_utils.py | `parse_frontmatter`（:52）、`skill_matches_platform`（:92）、`get_all_skills_dirs`（:273）、`discover_all_skill_config_vars`（:366） | SKILL.md frontmatter（前言元数据块）解析、平台条件匹配、目录汇总、配置变量发现与命名空间处理 |

`parse_frontmatter` 把 SKILL.md 顶部的元数据块与正文分离，`skill_matches_platform` 按元数据中的平台条件过滤——不匹配当前平台的技能不进入候选集；`discover_all_skill_config_vars` 让技能声明的变量能被统一收集与命名空间化（F-088）。技能对模型暴露为 `skills_list`/`skill_view`/`skill_manage` 等工具（F-050，注册点见 skills_tool 的 2 个 register 与 skill_manager 的 1 个 register，F-060），因此技能系统本身也复用 [04-tool-system](/concepts/04-tool-system.md) 的注册表，不另设调用通道。

## curator：LLM 评审与自动状态流转

`skills/` 不是静态目录，而是受 curator（策展器）治理的活集合，治理代码在 `agent/curator.py` 与 `agent/curator_backup.py`（F-087）：

- **评审入口**：`run_curator_review(on_summary, synchronous, dry_run)`（curator.py:1369）以 LLM 评审技能；`maybe_run_curator(idle_for_seconds)`（:1763）判断空闲时长后决定是否触发，避免占用活跃会话（F-087）；
- **自动状态流转**：`should_run_now`（:199）判定时机，`apply_automatic_transitions`（:256）按 idle/stale/archive 规则自动推进技能状态；状态由 `load_state`（:82）/`save_state`（:97）持久化于 `.curator_state`，`set_paused`（:118）支持人工暂停策展（F-087/F-098）；
- **备份与回滚**：`snapshot_skills(reason="manual")`（curator_backup.py:209）在评审/流转前快照整个技能树，`list_backups`（:333）列出备份，`rollback(backup_id)`（:527）回滚——自动变更因此可撤销（F-087）。

使用计数与策展状态在文件层分离：`.usage.json` 记录技能使用情况（带 `.usage.json.lock` 锁文件支持并发写），`.curator_state` 记录策展状态机数据，二者都是 `skills/` 树根的普通状态文件而非数据库——这与策展器"直接治理文件树"的模型一致，备份时整树快照即可同时保住状态（F-098/F-087）。

curator 是洞察 I-4 所述三条自进化回路中治理强度最高的一条：评审由 LLM 执行，但状态流转规则化、变更前必快照、可暂停可回滚，自动化不脱离治理（I-4）。策展所需的模型调用走辅助 LLM 面 `call_llm`，见 [05-model-providers](/concepts/05-model-providers.md)。

## 技能与插件的边界

两类扩展常被混淆，代码中的分界很清晰：技能是"给模型读的"——SKILL.md 是 Markdown 知识与流程，经预处理后进入提示词或由 skills 工具按需查看，不执行任意 Python 逻辑（模板变量与 inline shell 是受控预处理，F-088）；插件是"给运行时跑的"——Python 模块通过 17 个钩子在进程内执行，可以改写输出、拦截工具调用、注册 Provider（F-094/F-095）。一个插件可以附带技能（如 google_meet 目录内同时有 plugin 资产与 SKILL.md），但技能本身不能反向注册钩子。此外，shell 钩子（`agent/shell_hooks.py` 的 `register_from_config`）虽然执行的是外部 shell 命令，其合法事件名同样取自 `VALID_HOOKS`，并以 shell-hooks-allowlist.json 授权——即"同一事件名集合，Python 插件与 shell 命令两条执行路径"（F-044/F-095）。

## PluginManager：三种装载来源

插件管理器 `PluginManager` 位于 `kylin_agent_runtime_cli/plugins.py:770`，核心方法为 `discover_and_load`（:790），单插件装载走 `_load_plugin`（:1167），并按来源分派给 `_load_directory_module`（:1236，目录模块）与 `_load_entrypoint_module`（:1274，entry-points 模块）（F-094）。三种来源并存：

1. **仓内捆绑插件目录**：`get_bundled_plugins_dir`（:55）默认指向仓内 `plugins/`，但会尊重环境变量 `HERMES_BUNDLED_PLUGINS` 的覆盖（Nix 包装/打包场景使用，:62）；
2. **目录插件**：以模块目录形式放入插件路径的 Python 模块；
3. **pip 插件**：通过 Python entry-points 组 `hermes_agent.plugins`（常量 `ENTRY_POINTS_GROUP`，:170）发布安装的第三方包（F-094）。

模块级还提供 `discover_plugins`（:1395）与 `invoke_hook`（:1404）两个薄封装，供运行时各处一次性发现与按钩子名广播调用（F-094）。entry-points 组名保留 `hermes_agent.plugins` 而非改为 kylin，是"分发品牌层改名、代码符号层不改"的下游策略（I-3）。

## 17 个生命周期钩子

插件能介入哪些时点，由白名单集合 `VALID_HOOKS`（plugins.py:128）封闭定义，共 17 个（F-095，逐一复核与 Q-004 一致）：

| 分组 | 钩子（17 个） |
|---|---|
| 工具调用（2） | pre_tool_call、post_tool_call |
| 输出变换（3） | transform_terminal_output、transform_tool_result、transform_llm_output |
| LLM/API（4） | pre_llm_call、post_llm_call、pre_api_request、post_api_request |
| 会话（5） | on_session_start、on_session_end、on_session_finalize、on_session_reset、subagent_stop |
| 网关与审批（3） | pre_gateway_dispatch、pre_approval_request、post_approval_response |

其中三个 transform 钩子用于改写终端输出、工具结果与最终 LLM 输出；`pre_gateway_dispatch` 在消息平台事件鉴权/配对之前触发，可返回 skip/rewrite/allow 指令影响投递；两个审批钩子为观察者角色（返回值被忽略，插件不能借此预批危险操作，否决应在 pre_tool_call 完成）（F-095，钩子注释语义）。钩子集合封闭意味着插件无法自造事件名——扩展能力被约束在既定生命周期内。

## 内置插件目录与可替换后端

仓内 `plugins/` 有 17 个内置插件目录（F-096，本批机械复核）：agent-eval-recorder、browser、context_engine、disk-cleanup、example-dashboard、google_meet、hermes-achievements、image_gen、kanban、memory、model-providers、observability、platforms、spotify、teams_pipeline、video_gen、web；而 `plugins/__init__.py` 全文只有 1 行注释，真正的发现由 PluginManager 完成而非包导入（F-096）。这 17 个目录按职责可粗分为五组：

- **可替换后端族**：memory（8 个记忆实现的父目录）、web（8 个搜索实现的父目录）、image_gen、video_gen、browser；
- **平台与内容**：platforms、spotify、google_meet、kanban；
- **可观测与评测**：observability、agent-eval-recorder；
- **工程支撑**：context_engine、model-providers、disk-cleanup、teams_pipeline；
- **示例/成就**：example-dashboard、hermes-achievements。

其中两个后端族以"多实现可替换"方式组织（F-097，数量经本批复核）：

- **记忆后端 8 个**（`plugins/memory/`）：byterover、hindsight、holographic、honcho、mem0、openviking、retaindb、supermemory；
- **Web 搜索后端 8 个**（`plugins/web/`）：brave_free、ddgs、exa、firecrawl、parallel、searxng、tavily、xai，每个后端目录含 `plugin.yaml`、`provider.py`、`__init__.py` 三件套（F-097）。

记忆后端插件如何接入内核的 `MemoryProvider` 抽象与 `MemoryManager` 编排，见 [07-memory-and-context](/concepts/07-memory-and-context.md)。

## 四类能力 Provider 与 registry

浏览器、搜索、图像生成、视频生成四类外部能力走同一套"抽象基类 + registry + 配置选择"模式（F-100）：

| 能力 | ABC（agent/ 下） | 抽象方法/能力位 | 激活配置 |
|---|---|---|---|
| 浏览器 | `BrowserProvider`（browser_provider.py:49） | create_session、close_session、emergency_cleanup | config 的 cloud_provider |
| Web 搜索 | `WebSearchProvider`（web_search_provider.py:63） | search、extract、crawl + supports_* 能力位 | search_backend |
| 图像生成 | `ImageGenProvider`（image_gen_provider.py:51） | generate（默认 landscape 横向） | image_gen.provider |
| 视频生成 | `VideoGenProvider`（video_gen_provider.py:75） | generate + capabilities（modalities、max_duration=10 等） | video_gen.provider |

各 registry 同构提供 `register_provider`/`list_providers`/`get_provider` 与 `get_active_*_provider`：浏览器侧为 `get_active_browser_provider`（browser_registry.py:189），搜索侧细分为 `get_active_search_provider`/`get_active_extract_provider`/`get_active_crawl_provider`（web_search_registry.py:224-244），图像与视频侧为 `get_active_provider`（image_gen_registry.py:75、video_gen_registry.py:76）（F-100/F-101）。浏览器实现资产另有 camofox 模式（browser_camofox.py）、CDP 端点解析（browser_cdp_tool.py）与监督器（browser_supervisor.py）作为内置侧支撑（F-101）。这与模型供应商层的传输注册、工具体系的自注册同构，是全仓"ABC + registry + config 选择"扩展范式的又一实例。

## openKylin 下游增量

符号层保留 Hermes 血缘的同时，技能/插件面有两处明确的麒麟增量（I-3）：

- **kylin-cua 技能**：`skills/kylin-cua/` 提供桌面 CUA 配套技能，`skills/kylin-cua/version` 单行为 `0.9.8`（F-016，本批复核内容一致），与 [04-tool-system](/concepts/04-tool-system.md) 中 computer_use 工具的 `CuaDriverBackend` 配套；
- **ukui-direct-control 技能**：`skills/ukui-direct-control/SKILL.md` 面向 UKUI（openKylin 桌面环境）的直接控制（F-098）；
- 插件 entry-points 组名沿用 `hermes_agent.plugins`、环境变量沿用 `HERMES_BUNDLED_PLUGINS`，以降低与上游持续合并的成本（F-094/I-3）。

品牌分发与代码符号的分层策略总览见 [00-overview](/concepts/00-overview.md)。

## 相关概念

- [04-tool-system](/concepts/04-tool-system.md)：技能以 skills_list/skill_view/skill_manage 工具形态挂入同一注册表
- [05-model-providers](/concepts/05-model-providers.md)：curator 评审经 call_llm/PluginLlm 调用模型
- [07-memory-and-context](/concepts/07-memory-and-context.md)：8 个记忆后端如何接入 MemoryProvider 体系
- [00-overview](/concepts/00-overview.md)：openKylin 与 Hermes 的血缘、差异与 SIG 归属
- [hermes-agent 上游束](../../hermes-agent/index.md)：技能/插件机制的上游形态
