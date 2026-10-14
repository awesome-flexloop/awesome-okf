---
type: Concept
title: 工具系统：自注册注册表、工具集组合与终端环境
description: 工具如何被发现、注册、组合与执行：自注册 ToolRegistry、31 个工具集、computer_use 两层结构与 8 个终端环境后端。
tags: [kylin-agent-runtime, 工具系统, tool-registry, 终端环境, computer-use]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 工具系统：自注册注册表、工具集组合与终端环境

Kylin Agent Runtime 的工具（tool，模型可调用的函数能力）采用"丢文件即注册"的开放模型：`tools/` 目录下每个自包含模块在导入时向进程级单例 `ToolRegistry` 注册自己的 schema 与处理函数，对话环再按工具集（toolset，工具的命名分组）组合出当次对模型可见的工具面。本文沿"注册表 → 发现链 → 工具集组合 → 工具群分布 → 执行环境 → 审批与护栏"六层说明这套机制（F-046~F-060）。

## ToolRegistry 单例与 ToolEntry 元数据

注册表本体是一个进程级单例：模块级语句 `registry = ToolRegistry()` 位于 `tools/registry.py:544`，所有工具模块都向同一个实例注册（F-046）。`ToolRegistry.register(...)` 的参数即一项工具的完整元数据，关键字段包括 `name`、`toolset`、`schema`（JSON Schema 描述）、`handler`（实际执行函数）、`check_fn`（可用性探测，如依赖是否安装）、`requires_env`、`is_async`、`description`、`emoji`、`max_result_size_chars`、`dynamic_schema_overrides`（运行时按配置动态改写 schema 的零参回调）以及 `override`（F-046）。

每条工具在注册表内对应一个 `ToolEntry`，它用 `__slots__` 固化上述 11 个字段，避免成百上千次工具调用场景下的字典开销（F-048）。模块还提供两个结果封装辅助函数：`tool_error`（registry.py:563）与 `tool_result`（registry.py:577），供 handler 返回统一形态的结果字符串（F-048）。

注册参数中有两类"门控"字段：`check_fn` 用于探测外部前置状态（例如 Docker 守护进程是否可达、Playwright 二进制是否就位、某个凭证文件是否存在），`requires_env` 声明工具依赖的环境变量；二者共同决定一项已注册工具能否进入 `get_tool_definitions` 的输出——注册成功不等于对模型可见（F-046/F-049）。`dynamic_schema_overrides` 则用于在导出定义时按运行时配置浅合并（shallow merge）改写 schema 字段，使模型看到的工具描述与当前生效配置保持一致（F-046）。

## 发现链：glob → AST 静态判定 → importlib 自注册

新增一个内置工具不需要维护任何中央清单。发现函数 `discover_builtin_tools(tools_dir=None)`（registry.py:57）分三步扫描 `tools/` 根目录的 `*.py` 文件（F-047）：

1. **glob 枚举**：按文件名排序扫描，排除 `__init__.py`、`registry.py`、`mcp_tool.py` 三个非工具模块；
2. **AST 静态预判**：`_module_registers_tools` 解析模块 AST，只检查模块体（module body）顶层语句中是否存在形如 `registry.register(...)` 的表达式调用（由 `_is_registry_register_call` 判定：属性名为 `register`、接收者名为 `registry`）。这一步只读源码不执行代码，函数内部的注册调用不会被误判（F-047）；
3. **importlib 导入自注册**：通过预判的模块用 `importlib.import_module` 导入，模块顶层的 `registry.register(...)` 语句在导入副作用中完成注册；导入失败只记 warning，不阻断其余工具发现（F-047）。

`model_tools.py` 在模块级触发整条发现链：第 32 行 `from tools.registry import discover_builtin_tools, registry`，第 180 行直接调用 `discover_builtin_tools()`——任何 import 了 `model_tools` 的进程都会完成一次全量工具自注册（F-049）。

```mermaid
sequenceDiagram
    participant MT as model_tools 模块
    participant D as discover_builtin_tools
    participant AST as AST 预判器
    participant FM as tools/file_tools.py
    participant R as registry 单例
    participant Loop as 对话环

    MT->>D: 模块级调用（model_tools.py:180）
    D->>D: glob tools/*.py，排除 3 个非工具文件
    D->>AST: _module_registers_tools(候选文件)
    AST-->>D: 顶层存在 registry.register( 调用
    D->>FM: importlib.import_module("tools.file_tools")
    FM->>R: registry.register(name="read_file", toolset="file", ...)
    R-->>FM: 写入 ToolEntry
    Loop->>MT: get_tool_definitions(启用的工具集)
    MT->>R: 汇总 ToolEntry.schema
    R-->>Loop: 当次对模型可见的工具定义
```

注册表之外，`model_tools.py` 还提供工具面的三个消费侧函数：`get_tool_definitions`（:293，按启用工具集导出 schema 列表）、`coerce_tool_args`（:597，模型参数容错规整）、`handle_function_call`（:793，按名分发到 `ToolEntry.handler`），以及 `get_all_tool_names`（:963）、`get_toolset_for_tool`（:968）（F-049）。已下线工具名以 `REMOVED_TOOL_NAMES = frozenset({"session_search"})` 硬性过滤，即使模型返回该调用也不会执行（F-049）。

## 共享工具面与 31 个工具集

工具与工具集是多对一关系：每个 `ToolEntry` 携带一个 `toolset` 名，工具集再决定"某次会话给模型看哪些工具"。`toolsets.py` 定义两层结构（F-050/F-051）：

- `_HERMES_CORE_TOOLS`（toolsets.py:31）：CLI 与全部消息平台共享的核心工具名列表，覆盖 web_search/web_extract、terminal/process、read_file/write_file/patch/search_files、vision_analyze/image_generate、skills_list/skill_view/skill_manage、12 个 browser_* 名称、text_to_speech、todo、memory、clarify、execute_code/delegate_task、cronjob、send_message、4 个 ha_*（Home Assistant）、9 个 kanban_* 与 computer_use（F-050）；
- `TOOLSETS` 字典（toolsets.py:78）：定义 31 个顶层工具集键，支持工具集之间组合引用（多个平台工具集以 `_HERMES_CORE_TOOLS` 为基底再叠加平台专属工具）（F-051，键数以 `^    "[a-z_]+":\s*\{` 正则实测 31 行，Q-003）。31 个键按用途分组如下：

| 分组 | 工具集键 |
|---|---|
| 信息获取 | web、search、x_search、vision |
| 内容生成 | video、image_gen、video_gen、tts |
| 执行与环境 | terminal、computer_use、code_execution、file |
| 智能体协作 | moa（mixture-of-agents）、skills、delegation、clarify |
| 个人效能 | todo、memory、cronjob、homeassistant、kanban |
| 消息平台 | messaging、discord、discord_admin、yuanbao、feishu_doc、feishu_drive、spotify |
| 工程与安全 | browser、debugging、safe |

另有 `toolset_distributions.py` 提供 `DISTRIBUTIONS` 字典与 `get_distribution`/`list_distributions`/`sample_toolsets_from_distribution`/`validate_distribution` 等函数，用于按"工具分布"抽样启用不同工具面（评测/实验用途）（F-052）。

## 工具群分布

各工具模块的注册密度差异显著，大文件承载复杂工具族（F-053/F-054/F-060）：

| 工具族 | 注册数 | 证据位置 |
|---|---|---|
| 文件工具 read_file/write_file/patch/search_files | 4（一次注册） | file_tools.py:1170-1173（F-053） |
| 浏览器族 | browser_tool.py 内 10 个 register 调用 | browser_tool.py:3715-3789（F-053） |
| kanban 看板族 | 9 | kanban_tools.py:1218-1290（F-053） |
| terminal | 1（register 于 terminal_tool.py:2471） | F-054 |
| execute_code 代码执行 | 1（register 于 code_execution_tool.py:1902，含 checkpoint 钩子与 `_scrub_child_env`） | F-054 |
| delegate_task 子代理委派 | 1（delegate_tool.py:3933，审批回调位于 :74/:88/:101） | F-054 |
| cronjob / MCP | cronjob 1（:788）；mcp_tool.py 2 个 register（:3105、:3142） | F-054 |
| 其余散点 | memory 1、skills 2、skill_manager 1、todo 1、tts 1、vision 2、image_generation 1、video_generation 1、web_tools 2、x_search 1、mixture_of_agents 1、process_registry 1、send_message 1、homeassistant 4、feishu_doc 1/feishu_drive 4、yuanbao 5、discord 2 | F-060 |

需要注意两个口径：核心工具面列出 12 个 `browser_*` 名称（F-050），而 browser_tool.py 文件内是 10 个 register 调用点（F-053）——前者是工具名清单口径，后者是单文件注册语句口径，二者不可混用。

## computer_use：shim 与 CUA 子包两层

`computer_use`（计算机使用，让模型操作图形界面）在物理上分成两层（F-055）：

- **shim 层** `tools/computer_use_tool.py`：模块 docstring 自述"Shim for tool discovery"，只负责以 `registry.register(name="computer_use", toolset="computer_use", handler=lambda...)` 把工具挂进发现链，handler 转发到子包（computer_use_tool.py:19-32）；
- **实现层** `tools/computer_use/` 子包：抽象基类 `ComputerUseBackend`（backend.py:71）与数据类 `UIElement`/`CaptureResult`/`ActionResult`（backend.py:16/34/58）；CUA（computer-use agent）驱动实现 `CuaDriverBackend(ComputerUseBackend)`（cua_backend.py:319）；执行入口 `handle_computer_use`（tool.py:208）与 schema 提供方 `get_computer_use_schema`（schema.py:189）（F-055）。

这种切分让重依赖的图形自动化栈不进入所有进程的导入路径——shim 永远可被发现，真实后端在 `check_fn` 与运行时按需加载（F-055）。openKylin 侧另有 `kylin-cua` 技能（skills/kylin-cua/version = 0.9.8，F-016）与桌面直接控制技能 `ukui-direct-control`（F-098）作为该工具的麒麟增量配套，技能与工具的装配关系见 [06-skills-and-plugins](/concepts/06-skills-and-plugins.md)。

## 终端环境：BaseEnvironment 与 8 个实现

`terminal` 工具的命令并不假定在本机执行。环境抽象基类 `BaseEnvironment(ABC)` 位于 `tools/environments/base.py:293`，配套 `ProcessHandle` Protocol（:192）描述进程句柄；环境选择由 `terminal_tool._create_environment`（terminal_tool.py:1174）按环境变量 `TERMINAL_ENV` 完成，未设置时回退 `local`（terminal_tool.py:700）（F-056）。

8 个具体环境后端实现（Q-009，经逐文件 Grep 复验类定义行）：

| 类 | 文件:行 | 说明 |
|---|---|---|
| `LocalEnvironment` | local.py:429 | 本机 shell |
| `DockerEnvironment` | docker.py:274 | 本地容器 |
| `SSHEnvironment` | ssh.py:36 | 远程 SSH 主机 |
| `ModalEnvironment` | modal.py:164 | Modal 云沙箱 |
| `ManagedModalEnvironment` | managed_modal.py:36 | 托管 Modal，继承共享基类 |
| `DaytonaEnvironment` | daytona.py:30 | Daytona 云开发环境 |
| `SingularityEnvironment` | singularity.py:156 | HPC 常见的 Singularity 容器 |
| `VercelSandboxEnvironment` | vercel_sandbox.py:235 | Vercel 沙箱 |

其中云沙箱侧有中间基类 `BaseModalExecutionEnvironment(BaseEnvironment)`（modal_utils.py:58）：`ManagedModalEnvironment`（managed_modal.py:36）继承它，而 `ModalEnvironment`（modal.py:164）与其余六个后端一样直接继承 `BaseEnvironment`。即 `BaseEnvironment` 的直接子类共 8 个（含该中间基类），可经 `TERMINAL_ENV` 选择的叶子后端为表中 8 个（Q-009）；跨环境文件同步由 `FileSyncManager`（file_sync.py:107）承担，使本地工作目录与远端沙箱之间的文件搬运对工具层透明（F-057）。openKylin 下游的可见增量是默认 pip 索引：`DEFAULT_PIP_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"`（base.py:31），在环境内安装 Python 包时默认走清华镜像（F-056）。终端后端属于 F-004 所称"首用时懒安装"的可选后端之一——Docker/Modal/SSH 等重依赖不进入核心安装集合，切换 `TERMINAL_ENV` 才需要相应依赖就位（F-004/F-057）。

## 审批、澄清、检查点与凭证注入

工具执行前后有一组横切机制（F-058/F-059）：

- **审批**：`tools/approval.py` 的 `_fire_approval_hook`（:36）在危险命令执行前触发审批钩子，CLI 交互与网关/ACP 审批共用同一点（F-058）；
- **澄清**：`clarify` 工具注册于 clarify_tool.py:131，handler `clarify_tool`（:23）与可用性检查 `check_clarify_requirements`（:78）；网关侧 `clarify_gateway.py` 以 `_ClarifyEntry`/`wait_for_response`（:48-103）把"向用户提问并等待回复"做成跨进程异步等待（F-058）；
- **检查点**：`checkpoint_manager` 对回滚目标做硬校验，`_validate_commit_hash`（:155）与 `_validate_file_path`（:171）拒绝非法 commit 哈希与越界路径（F-058）；
- **凭证与环境注入**：`register_credential_file`（credential_files.py:56）向工具环境登记凭证文件；`register_env_passthrough`（env_passthrough.py:70）透传环境变量，但 `_is_hermes_provider_credential`（:48）会拦截 Provider 自身凭证，避免密钥被工具随意读取；预算配置由 `BudgetConfig`（budget_config.py:23）承载（F-059）。

## MCP 外部工具的动态入口

发现链显式跳过 `mcp_tool.py`（glob 排除清单三项之一，F-047），因为 MCP（Model Context Protocol，模型上下文协议）工具不是静态自注册：该文件内有两个 `register` 调用（mcp_tool.py:3105、:3142），分别承载 MCP 服务连接后把外部工具动态挂入同一 `registry` 单例的入口（F-054）。这意味着外部 MCP 工具与内置工具在消费侧无差别——同样经过 `get_tool_definitions` 导出、`handle_function_call` 分发（F-049）；差别只在注册时机：内置工具在进程导入时注册，MCP 工具在服务连接/刷新时注册，注册表也因此需要支持运行期变更（F-046/F-054）。MCP 服务端如何把 Hermes 工具反向暴露给外部，见 [09-acp-mcp-protocols](/concepts/09-acp-mcp-protocols.md)。

## 工具护栏在核心环的位置

工具调用在对话环内由两个执行器承接：`execute_tool_calls_concurrent`（agent/tool_executor.py:355，并发）与 `execute_tool_calls_sequential`（:819，串行），中断时为每个 tool call 补写 "Tool execution cancelled"（F-031）。护栏层用两个 frozenset 给工具定性：`IDEMPOTENT_TOOL_NAMES`（16 项，read_file/search_files/web_search/browser_* 等只读工具）与 `MUTATING_TOOL_NAMES`（15 项，terminal/write_file/patch/delegate_task 等写操作工具）（F-032）；`ToolCallGuardrailController` 以 `before_call`/`after_call`/`reset_for_turn` 介入每次调用，阈值配置 `ToolCallGuardrailConfig` 对"同一错误连续出现 2 次警告/5 次阻断""同一工具失败 3 次警告/8 次终止""无进展 2 次警告/5 次阻断"等情形设限（F-033）。护栏与迭代预算、错误分类退避共同构成核心环的工具执行安全面，其在对话环中的完整位置见 [02-agent-core-loop](/concepts/02-agent-core-loop.md)。

## 设计对照：开放注册 vs 平台硬连

工具体系是本仓库"扩展哲学"的开放一侧：新增内置工具只需在 `tools/` 放置一个含顶层 `registry.register(...)` 的模块，发现链自动收录，无需改动任何枚举或工厂（F-047）。与之形成对照的是消息网关的内置平台——22 个平台在 `Platform` 枚举中固定、适配器由 `GatewayRunner._create_adapter` 的 if/elif 链逐个硬连（F-108/F-103）；名为 `platform_registry` 的注册表只服务插件平台。这种"工具零样板自发现、内置平台双点硬连"的同库反差是架构洞察 I-2 的核心，平台侧机制见 [08-gateway-and-cron](/concepts/08-gateway-and-cron.md)。

## 相关概念

- [02-agent-core-loop](/concepts/02-agent-core-loop.md)：工具调用在对话环中的迭代、并发执行与护栏拦截
- [05-model-providers](/concepts/05-model-providers.md)：工具 schema 如何经传输层转换为各厂商的工具协议
- [06-skills-and-plugins](/concepts/06-skills-and-plugins.md)：技能工具与插件如何挂载到同一注册表体系
- [09-acp-mcp-protocols](/concepts/09-acp-mcp-protocols.md)：MCP 外部工具的两个动态注册入口
- [hermes-agent 上游束](../../hermes-agent/index.md)：本机制的 Hermes 血缘说明
