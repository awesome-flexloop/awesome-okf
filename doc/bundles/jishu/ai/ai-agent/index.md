---
okf_version: "0.2"
type: group
title: "🤖 AI Agent 框架"
description: "AI Agent 运行时框架与架构模式——从工具调用循环到多代理编排、记忆系统、插件架构的源码级中文教程"
total_bundles: 37
---

# 🤖 AI Agent 框架

本组存放 AI Agent 运行时框架与架构模式的源码中文教程，覆盖 Python/TypeScript/C++/Rust/Go 五种语言生态中 21 个开源项目的核心架构设计。从 Agent 基础概念到生产级框架实现，从插件架构到多Agent编排，从通信协议到 Coding Agent 源码解读，构建完整的 AI Agent 知识体系。

## 推荐学习路径

```
🧱 ai-agent-fundamentals  Agent跨项目基础（6大架构模式对比）—— 必读起点
  ↓
🔌 cordis                 插件元框架（DI容器+Fiber生命周期+事件总线）—— 架构底座
  ↓
┌────────────────────────────────────────────────────────────┐
│  选一个Tier 1主力框架深入学习（根据语言/场景偏好）：          │
│  🐍 hermes-agent      多Provider/平台Python框架            │
│  🐍 veadk-python      火山引擎SDK（豆包+A2A/A2UI）         │
│  📘 zleap-agent       Workspace-first（TS+Rust Tauri）    │
│  📘 deepseek-harness  Cordis插件架构（50+包TS monorepo）  │
│  💻 intelligent-terminal Windows Terminal（C++/Rust+ACP） │
└────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────┐
│  Tier 2-3 专项深入（按需选读）：                              │
│  🧠 second-me          个人AI分身（三层记忆HMM+LoRA）       │
│  👥 agency-agents      270+ Persona角色库+NEXUS编排       │
│  🖥️ agency-agents-app  Tauri+Svelte5桌面工作台            │
│  📋 anthropics-skills  Anthropic Skills规范最佳实践        │
│  📚 book-to-skill      书籍→技能编译器                     │
│  🧩 i-have-adhd        ADHD认知辅助技能（10条规则）        │
└────────────────────────────────────────────────────────────┘
```

---

## 知识包导航

### 🧱 跨项目基础

| 知识包 | 文档数 | 一句话简介 |
|--------|--------|-----------|
| [ai-agent-fundamentals](ai-agent-fundamentals/index.md) | 6+3+1=10 | Agent跨项目架构模式——6大核心模式对比（核心循环/Provider/插件/多Agent/记忆/MCP-ACP），4框架代码级对比，框架选型指南 |

### ⚙️ Tier 1：大型框架/运行时

| 知识包 | 语言 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [hermes-agent](hermes-agent/index.md) | Python | 10+4+1=15 | 渐进式披露多Agent框架——Think-Act-Observe循环、ToolRegistry(100+工具)、34+模型Provider、8种记忆插件、MCP/ACP双协议、Gateway多平台网关(22+消息平台)、Cron调度 |
| [veadk-python](veadk-python/index.md) | Python | 10+4+1=15 | 火山引擎Agent SDK——Agent/Runner双层架构、豆包/方舟原生集成、A2A/A2UI协议、RAG知识库(8种向量后端)、双层记忆、Sequential/Parallel/Loop/Supervisor组合模式、Tunnel内网桥接 |
| [zleap-agent](zleap-agent/index.md) | TS/Rust | 10+4+1=15 | Workspace-first Agent——Run→Work→WorkStep三级Fiber状态机、PostgreSQL+pgvector双线记忆(A/B线+RRF融合)、飞书/微信/Feishu CLI网关、子Agent委派、pg-boss定时任务 |
| [deepseek-harness](deepseek-harness/index.md) | TypeScript | 10+4+1=15 | DeepSeek Agent框架——Cordis插件架构(50+包)、Phase状态机+Inbox双队列、defineTool类型安全工具、Event-Sourcing会话、MCP/ACP双协议、Skill分层系统 |
| [intelligent-terminal](intelligent-terminal/index.md) | C++/Rust | 10+4+1=15 | Windows Terminal原生Agent——双进程架构(Helper+Master)、COM协议服务器、命名管道传输、ACP JSON-RPC 2.0、OSC 133自动修复、Agent Pane XAML UI、wtcli命令工具 |

### 🔌 Tier 2：中型框架/库

| 知识包 | 语言 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [cordis](cordis/index.md) | TypeScript | 7+3+1=11 | 可组合插件元框架——Context DI容器、Proxy代理构造、Fiber六状态生命周期、5种事件派发模式、Reflect元数据、Timer调度，hermes/zleap/deepseek-harness共同的架构底座 |
| [second-me](second-me/index.md) | Python/TS | 7+3+1=11 | 个人AI数字分身——L0→L1→L2三层记忆HMM、LoRA微调(r=64/alpha=16)+DPO对齐、GGUF量化+llama.cpp本地推理、14步训练流水线、Flask API、Space多Agent策略 |

### 🎯 Tier 3：专项工具/应用/技能

| 知识包 | 类型 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [agency-agents](agency-agents/index.md) | 角色库 | 4+1+1=6 | 270+专业Agent Persona库——17部门分类体系、Markdown模板规范、NEXUS 7阶段编排框架(Full/Sprint/Micro三模式)、16种工具集成适配、convert.sh多格式转换 |
| [agency-agents-app](agency-agents-app/index.md) | 桌面应用 | 3+1+1=5 | Agency Agents桌面工作台——Tauri 2(Rust)+Svelte 5(Runes)、三源Catalog模型、五状态安装协调、35个Tauri命令、⌘K命令面板、Preset Teams策展 |
| [anthropics-skills](anthropics-skills/index.md) | 技能规范 | 4+1+1=6 | Anthropic官方Skills参考——SKILL.md格式标准(6字段)、三级渐进式加载、.skill分发包、eval双slave评估基准、A/B盲比、17个内置Skill分类 |
| [agent-skills-spec](agent-skills-spec/index.md) | 技能规范 | 8+2+2+1=13 | Agent Skills开放标准——SKILL.md权威格式规范(name五规则/description≤1024/compatibility≤500)、渐进式披露三阶段token预算、eval驱动迭代(evals/grading双臂对照)、description触发率优化(3次/0.5阈值/60-40切分)、46客户端三层加载契约、skills-ref参考实现(parser四类ParseError/validator校验序列/to_prompt XML/CLI三子命令) |
| [book-to-skill](book-to-skill/index.md) | 知识工具 | 4+1+1=6 | 书籍→Agent Skill编译器——确定性文本提取、7种文档格式解析器、13语言章节检测、四层产出流水线、多层安全防护 |
| [i-have-adhd](i-have-adhd/index.md) | 辅助技能 | 3+1+1=5 | ADHD认知辅助技能——10条ADHD友好输出规则、Session Hooks偏好持久化、10+IDE/Agent平台集成、Always-On跨应用模式 |
| cli-anything | CLI框架 | 8+3+6=17 | Agent原生CLI接口框架——ReplSkin双语终端外壳、SKILL.md自动生成(AST+Jinja2)、PreviewBundle v1三层持久化协议、CLI-Hub包管理器(注册表+pip安装器)、Matrix技能矩阵、Cursor/Claude/Codex多平台插件适配、四层测试与真实软件原则 |

### 💻 Tier 4：Coding Agent 源码解读

| 知识包 | 语言 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [codewhale](codewhale/index.md) | Rust | 8+2+1=11 | CodeWhale Coding Agent——21 crate Cargo workspace、Fleet多Agent控制平面、Workflow双轨引擎(TOML+JS)、MCP安全三重防护、Skill四层所有权架构、ExecPolicy沙箱(Seatbelt/bwrap) |
| [deepseek-reasonix](deepseek-reasonix/index.md) | Go/TS | 8+2+1=11 | DeepSeek Reasonix——ACP v1协议(JSON-RPC/Factory/inbox)、Agent运行循环(arbiter/governor/compaction)、Bot网关(QQ/飞书适配器)、Checkpoint恢复(fork/branch)、Fleet DAG调度、Wails桌面应用 |
| [openai-codex](openai-codex/index.md) | TS/Rust/Py | 7+2+1=10 | OpenAI Codex CLI——三语言架构(Node.js CLI+Rust TUI+Python SDK)、Bazel构建、三层沙箱防御(平台沙箱/execpolicy/SafetyCheck)、AGENTS.md目录树发现、Skills显式/隐式调用 |
| [nanobot](nanobot/index.md) | Python/TS | 6+1+1=8 | Nanobot Agent——Python Agent核心(AgentLoop/Runner)、MessageBus消息总线+WebSocket协议、SDK类型系统(StreamEvent/RunResult)、CLI/TUI(Bun+OpenTUI)/WebUI(React+Vite)三端架构 |
| [deepcode-cli](deepcode-cli/index.md) | TypeScript | 5+1+1=7 | DeepCode CLI——三包monorepo(cli/core/vscode-ide-companion)、10种权限作用域(read-in-cwd/network/git等)、MCP客户端(mcp__server__tool命名空间)、12个斜杠命令 |
| [opencode](opencode/index.md) | TypeScript | 5+1+1=7 | OpenCode Terminal Coding Agent——Bun+Turbo+SST技术栈、SessionV2会话模型(Context Epoch)、V2配置规范、infra模块(app/console/lake/stage/stats/secret)、Cloudflare+AWS混合云部署 |
| [pi-cli](pi-cli/index.md) | TypeScript | 5+1+1=7 | Pi AI CLI——9包monorepo(ai/tui/agent/client/server/evals等)、AI包(models/oauth/cli/compat/images)、TUI差分渲染引擎、5个内置prompt(cl/is/pr/sa/wr)、锁步版本控制 |

### 🔬 Tongyi-MAI 生态源码精读

| 知识包 | 类型 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [mai-ui](mai-ui/index.md) | 源码精读 | 7+2+2+1=12 | MAI-UI GUI Agent 基础模型家族源码精读——2B/8B/32B/235B-A22B 四尺寸、vLLM 推理外壳（4 包依赖）、grounding/navigation 双 Agent、TrajStep 轨迹记忆与上下文工程、999/1000 双坐标口径、双通道评估管线，54 条事实可溯源（Qwen-UI-Agent 前代） |
| [mobile-world](mobile-world/index.md) | 评测框架精读 | 8+3+2+1=14 | MobileWorld 移动 GUI 智能体评测框架源码精读——DinD 单容器 Android 评测环境、agents/core/runtime/tasks 四层架构、BaseAgent 契约与九项注册表、任务快照+冻结时钟确定性复现、eval-server 大规模编排（40 容器/tmux）、MCP 工具注入、双 CLI 驱动，80 条事实全溯源（Qwen-UI-Agent 82.1% 成绩所在基准框架） |
| [mobilepa-bench](mobilepa-bench/index.md) | 基准精读 | 5+0+2+1=8 | MobilePA-Bench 移动规划智能体基准精读——页面即仓库（零评测代码）、1,705 任务/212 工具四维加权（Tool 50%）、六类 checker 固定验证策略、v1.5 榜单 13 模型与 Cost 口径、并入 Qwen-UI-Agent 网站技术栈简析（Next.js 16），网站型项目无 examples |

### 📰 产品资讯

| 知识包 | 类型 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [qwen-creative-platform-news](qwen-creative-platform-news/index.md) | 资讯速报 | 1+2+1=4 | 阿里千问创作平台多Agent协同开测——5个Agent组成虚拟剧组(策划/编剧/视觉/分镜/成片)、Wan 3.0+Qwen-Image 3.0 Pro、书旗ManClaw漫剧Agent(Seedance 2.0)、导演视角解读 |
| [qwen-ui-agent](qwen-ui-agent/index.md) | 技术评测 | 3+1+2+1=7 | 阿里通义开源GUI智能体Qwen-UI-Agent技术评测——真机训练(100+设备/150+App/400+任务)、MobileWorld 82.1%超GPT-5.6/Claude Opus 4.8、CLI批量动作、3个内部流程实测(财务对账/运营日报/老CRM)、3项勘误(MAI-UI权重混淆/58%以偏概全/硬件要求有误) |
| [a2a-mcp-convergence](a2a-mcp-convergence/index.md) | 技术分析 | 4+2+1=7 | A2A与MCP协议合流分析——A2A转入AAIF与MCP共治、两协议正交分工(MCP连工具/A2A连Agent)、A2A技术架构(Agent Card/Task/Message+Part/三种交互模式)、AAIF三层Agent栈、归因授权追索三缺口、5项勘误(A2A时间线/1.1亿下载量/AWS GA日期硬性错误/四大工作流/引文意译) |
| [doubao-work](doubao-work/index.md) | 产品实测 | 4+2+1=7 | 字节豆包工作实测评测——独立桌面客户端+飞书深度打通、Seedance 2.5+Seedream 5.0多模态生成、文档/PPT/网页/AI协同编辑(80+设计风格/带数据库网页)、飞书组织架构/群聊总结/多维表格/会议纪要→任务流、"由豆包发送"标签、滚动额度模型、核心论点"模型决定AI有多聪明，组织上下文决定它能不能成为同事"、8项P0核验全通过零勘误 |
| [doubao-work-context-layer](doubao-work-context-layer/index.md) | 战略分析 | 4+2+1=7 | AI产品阿颖对豆包工作的Context Layer战略分析——飞书作为Agent组织上下文层、个人效率vs组织效率、Claude Tag(Slack)参照、Cat Wu上下文观(引语勘误)、Context竞争论、企业Agent四阶段演进、6项P0核验(4✅1⚠️1❌含10倍效率数据归因失实勘误) |
| [doubao-work-org-productivity](doubao-work-org-productivity/index.md) | 行业分析 | 4+2+1=7 | 36氪深度分析豆包工作组织生产力——Agent=Model+Harness能力商品化、Deloitte 34%/37%企业AI落地落差、飞书账号级集成、理解→执行→协作→沉淀组织闭环、BCG 42%员工周省8h但组织价值未转化、权限治理分界线、信通院双项认证(⚠️待佐证)、6项P0核验(5✅1⚠️0❌本系列最高通过率) |
| [claude-vision-skill](claude-vision-skill/index.md) | 工具教程 | 3+2+2+1=8 | claude-vision-skill给纯文本模型装眼睛——视觉转录架构(图片→qwen-vl-max→文字→DeepSeek推理)、Claude Code Skill自动触发机制、安装避坑(SKILL.md硬编码路径3处/dotenv静默失败)、本地/URL/剪贴板三场景+回退逻辑、⏰博文当天DeepSeek官方视觉模型上线、6项P0核验全✅ |
| [siemens-industrial-agent](siemens-industrial-agent/index.md) | 行业分析 | 4+2+1=7 | 量子位解析西门子工业Agent——工业Agent为何不能套壳(43%未部署/IT-OT断层)、Eigen工程智能体(ECAD集成/PLC标签/端到端执行/WAIC SAIL之星)、ICX编排层(下连PLM-ERP-MES-OT+Skill/Agent/Workflow)、Xcelerator三层生态与验证-沉淀-开发-分发飞轮、⚠️平台数字勘误(官方800款/500家非900/600)、报告系西门子联合发布、6项P0核验(3✅3⚠️) |
| [agora-gemini-transcribe](agora-gemini-transcribe/index.md) | 资讯速报 | 4+2+1=7 | 声网(Agora官方)官宣集成Google Gemini 3.5 Transcribe——双API(Live流式`gemini-3.5-transcribe-live`亚秒延迟/Interactions预录音+说话人归属)、WER流式4.0%/非流式2.6%(Artificial Analysis)、85+语言、Agents SDK三语言(Python/TS/Go)与链式ASR+LLM+TTS/MLLM端到端两架构、Smart Transcription计划支持CRM/信息采集场景、⚠️"全球首个Realtime API"措辞勘误(API为OpenAI产品/Agora为首发语音合作方)、厂商自宣稿无成效数字、6项P0核验(5✅1⚠️) |
| [llm-hallucination-governance](llm-hallucination-governance/index.md) | 法学论文 | 4+2+1=7 | 杨帆/吕士哲论大模型知识幻觉的软硬法协同治理——风险类型(谄媚+思维链/高密度编造/路径依赖)、治理多维困境(数据枯竭近半域名限爬虫·GPT-4约13万亿tokens超$100M·RAG难根除·宏观指引够不着)、软硬法协同(硬法三义务[显著标识/来源提示/动态审查]+责任界分+过错推定[个保法69条]+软法[自律/标准/红队/国际合作])、附带国际参照(日本治理创新2.0/加州SB1047→SB53)与三案(Mata v.Avianca/noyb诉OpenAI/杭州首例AI幻觉案)、⚠️5处勘误(杭州案年份/挪威案投诉年份/SB编号/GPT-4数据量/爬虫比例)、学术论文无examples/、8项P0核验(5✅3⚠️) |
| [matrix-zero-person-company](matrix-zero-person-company/index.md) | 产品资讯 | 3+2+1=6 | 智潮笔记解析Matrix(matrix.build)Agent公司操作系统——0人公司叙事(造的成本趋零竞争转向运营)、CEO Office+部门化分工+领队路由+Agential OKR、durable work memory与proof可验证交付(反幻觉完成)、商业基建开箱即用(Stripe/matrix.site域名/Agent钱包/VPTD经济指标)、九模型接入矩阵(Neo/Claude Code/Codex/ChatGPT/Gemini/GLM/DeepSeek/Kimi/Qwen)、⚠️成效数字全为厂商自述(GDPval 95.45%口径未验证/aivideopro.io案例无独立佐证)、macOS单平台单源、6项P0核验(2✅3⚠️1单源0❌无勘误) |
| [ai-app-survival](ai-app-survival/index.md) | 商业分析 | 6+0+2+1=9 | 晚点LatePost深度调研AI应用生存困境——三重挤压(模型吞噬/负毛利/上游入口)、Stripe 11.5月达100万ARR vs SaaS 15月、Bessemer AI均毛利25% vs SaaS 70%、Perplexity/Cursor负毛利会计口径、scaling to bankruptcy、Devv搜索窗口仅半年、a16z三年仅14家常驻、Epoch AI能力增速8到15指数点、Brookings模型厂下场归因、易观办公Agent三分之二流量集中大厂、下游卖结果与上游做模型(租客困境)、12项P0核验(9确认3存疑0证伪) |
| [wigolo](wigolo/index.md) | 工具教程 | 3+4+2+1=10 | wigolo本地优先Agent网页能力工具——MCP/REST/SDK三面提供search/fetch/crawl/extract/cache/find_similar/research/agent/diff/watch十工具、18搜索引擎并行+本地重排、字节级source_span证据与evidence_score置信度、fetch三级升级路由、数据全在~/.wigolo、六核心工具零API Key零按量费用、--agents一键接线9客户端、n8n/TS/Python SDK/框架包/Docker、⚠️AGPL-3.0与research/agent需LLM、10项P0核验全✅(2项口径标注:Firecrawl免费额度单源/博文日期未检出) |

---

## 跨项目概念对照

以下核心概念在多个框架中有不同实现，建议对照学习：

| 核心概念 | hermes-agent | zleap-agent | deepseek-harness | veadk-python | intelligent-terminal | cordis |
|---------|-------------|-------------|-----------------|-------------|---------------------|--------|
| Agent循环 | AIAgent Think-Act-Observe | Run→Work→WorkStep Fiber | Phase+Inbox双队列 | Agent+Runner双层 | Helper→Master双进程 | — |
| 插件系统 | Plugin注册表 | Service扩展 | Cordis Context/Service | 配置式组合 | COM+注册表 | Context+Fiber+Plugin |
| 工具注册 | ToolRegistry单例(100+) | MCP+内置工具 | defineTool+Cascade | Tool延迟注册 | wtcli+SendEvent | — |
| 记忆系统 | MemoryManager+8插件 | PG+pgvector双线 | Session/Scope/Compaction | Short+Long双层 | — | — |
| 多Agent | Gateway+LRU缓存 | Workspace Handoff | SubagentProvider | Sequential/Parallel/Loop | 多Agent CLI支持 | — |
| 通信协议 | MCP+ACP+22平台 | Gateway(飞书/微信) | MCP stdio/HTTP+ACP | A2A/A2UI/Tunnel | ACP JSON-RPC+命名管道 | — |
| 事件系统 | Cordis Events | Event Bus | Cordis Waterfall | 回调钩子 | COM事件队列 | 5种dispatch模式 |

---

> **信任声明**：本分组索引基于 22 个 AI Agent 开源项目源码逐模块分析生成，所有知识包均经 OKF 五阶段流程（R→I→E→V→C）验证。
> 
> **生成时间**：2026-08-29 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：37 个知识包，共 321 个内容文档（209 概念 + 58 示例 + 54 信源），零推测事实底稿随束存放

```{toctree}
:hidden:
:maxdepth: 7

ai-agent-fundamentals/index
hermes-agent/index
veadk-python/index
zleap-agent/index
deepseek-harness/index
intelligent-terminal/index
cordis/index
second-me/index
agency-agents/index
agency-agents-app/index
anthropics-skills/index
agent-skills-spec/index
book-to-skill/index
i-have-adhd/index
codewhale/index
deepseek-reasonix/index
openai-codex/index
nanobot/index
deepcode-cli/index
opencode/index
pi-cli/index
mai-ui/index
mobile-world/index
mobilepa-bench/index
qwen-creative-platform-news/index
qwen-ui-agent/index
a2a-mcp-convergence/index
doubao-work/index
doubao-work-context-layer/index
doubao-work-org-productivity/index
claude-vision-skill/index
siemens-industrial-agent/index
agora-gemini-transcribe/index
llm-hallucination-governance/index
matrix-zero-person-company/index
ai-app-survival/index
wigolo/index
```
