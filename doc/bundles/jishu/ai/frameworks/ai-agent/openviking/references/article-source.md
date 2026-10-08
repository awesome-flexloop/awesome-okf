# 信源与事实登记

## 博文信息

| 项 | 内容 |
|----|------|
| 标题 | 《字节又开源了一个顶级 Agent 项目！》 |
| 作者/公众号 | macrozheng（作者署名：梦想de星空），原创 |
| 发布时间 | 2026-09-09 14:10（发布地：江苏） |
| URL | https://mp.weixin.qq.com/s/OFS4DzgTEcEgzNHyvRVD0g |
| 内容类型 | 开源项目介绍 + 一手部署实测教程（Docker 部署、Web Studio 配置、VikingBot 跨会话记忆实测、外部 Agent 接入） |
| 开源项目 | https://github.com/volcengine/OpenViking（火山引擎/字节跳动） |

## 信源距离分级

| 信源 | 距离 | 用途 |
|------|------|------|
| GitHub 官方仓库 README / LICENSE、docs.openviking.ai 官方文档、GitHub REST API | ① 官方发布 | 功能、命令、配置、工具清单、许可证、集成矩阵、基准数字的裁决依据 |
| 阿里云百炼官方帮助中心（help.aliyun.com） | ① 官方发布 | 博文所用 text-embedding-v4 / qwen3-vl-plus 模型与 OpenAI 兼容端点核验 |
| 微信公众号「macrozheng」原文 | ③ 第三方综述（含作者一手部署实测） | 部署叙事、操作顺序、UI 路径、使用体验与观点的来源 |

> 博文无厂商约稿/赞助标识，无"提效倍数/节省工时"类成效数字；唯一规模数字（35K+ star）已对 GitHub API 核验。官方 README 自带的 LoCoMo/tau2 基准为**厂商自述**（F-044），引用时单独标注。

## 事实登记（F-001~F-048）

> F-001~F-032 为博文事实（F-031/F-032 为作者观点）；F-033~F-048 为官方源核验补充。
> 核验状态：✅ 官方一致 ｜ ⚠️ 口径差异/单源 ｜ 📌 作者观点（非客观事实）。

### A. 博文元信息与定位

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 标题《字节又开源了一个顶级 Agent 项目！》；公众号 macrozheng；作者"梦想de星空"；原创；2026-09-09 14:10 发布于江苏 | ✅ 页面元数据 |
| F-002 | 项目地址：https://github.com/volcengine/OpenViking | ✅ |
| F-003 | 博文称 GitHub 35K+ star，项目针对"Agent 记不住事"问题 | ✅ F-033 |
| F-004 | 定位：面向 AI Agent 的开源上下文数据库；记忆、资源、技能统一存放在 viking:// 协议虚拟文件系统里 | ✅ README |
| F-005 | 与黑盒向量库不同，Agent 用 ls、tree、find 等熟悉操作浏览自己的上下文 | ✅ README |
| F-006 | 内容写入时处理成 L0 摘要、L1 概览、L2 详情三层，按需加载省 token | ✅ F-037 |
| F-007 | 每次检索留下目录浏览轨迹，结果不对能回溯到具体路径 | ✅ F-045 |

### B. 三大特性

| 编号 | 事实 | 核验 |
|------|------|------|
| F-008 | 特性①目录递归检索：先定位得分最高的目录，再逐层下探，结果连同周边上下文一起返回 | ✅ README/FAQ |
| F-009 | 特性②会话沉淀记忆：会话结束后异步把用户偏好和 Agent 经验写成长期记忆，下次对话自动召回，跨会话不失忆 | ✅ F-038 |
| F-010 | 特性③多 Agent 共用：同一份记忆通过插件、MCP、SDK 接给 Claude Code、Codex、Cursor 等外部 Agent，跨项目共用 | ✅ F-040（口径细化） |

### C. 部署配置（博文实测）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-011 | 以一台 Linux 服务器（192.168.3.101）为例完整部署 | — 博文环境 |
| F-012 | 创建 ov.conf 并复制到 /mydata/openviking 目录 | ✅ F-035 |
| F-013 | server 块：host 0.0.0.0、port 1933、root_api_key "abc123456efg"、public_base_url "http://192.168.3.101:1933" | ✅ 字段存在 |
| F-014 | storage 块：workspace "./data"；agfs.backend "local"；vectordb.backend "local" | ✅ |
| F-015 | embedding.dense：api_base 百炼 OpenAI 兼容接口 https://dashscope.aliyuncs.com/compatible-mode/v1 ，provider "openai"，dimension 1024，model "text-embedding-v4" | ✅ F-042/F-046 |
| F-016 | vlm：同走百炼兼容接口，model "qwen3-vl-plus"；embedding 与 vlm 一个 API Key 够用 | ✅ F-046 |
| F-017 | 四块职责：server=监听/端口/管理密钥（public_base_url 用于上传文件时回客户端可达地址）；storage=记忆与向量数据落盘位置；embedding=文本转向量；vlm=生成摘要/理解内容/VikingBot 思考模型 | ✅ 配置文档 |
| F-018 | `docker pull ghcr.io/volcengine/openviking:latest` | ✅ F-035 |
| F-019 | `docker run --name openviking -p 1933:1933 -v /mydata/openviking:/app/.openviking -d ghcr.io/volcengine/openviking:latest` | ✅ F-035 |
| F-020 | curl /health 验证；博文称返回 status:ok、healthy:true，并带出服务版本和 auth_mode | ⚠️ F-036 |

### D. Web Studio 配置（博文实测）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-021 | Studio 地址 /studio；首页仪表盘展示上下文数据量、Token 用量、检索次数；左侧导航分工作区、活动、设置、资源四区 | ✅ /studio 同源 |
| F-022 | 「连接设置」填 root_api_key（Root 或管理员 API 密钥）后控制台权限正常；提示缺用户 API 密钥；管理密钥只管管理操作，工作台/数据接口需用户密钥 | ✅ F-035 |
| F-023 | 「用户管理」新增用户（用户名 macro、角色 user），生成用户 API 密钥并回填连接设置，数据访问打通 | ✅ 多租户机制 |
| F-024 | 工作台三栏：左上下文树（user 个性化记忆、resources 外部资源）、中 viking:// 目录浏览、右会话区（终端/Agent 双模式）；工具调用与左侧目录联动定位 | ✅ README Studio |

### E. VikingBot 跨会话记忆实测

| 编号 | 事实 | 核验 |
|------|------|------|
| F-025 | "记住我的职业：Java开发工程师"→ Agent 调 openviking_memory_commit 写记忆，回复 Memory URI | ⚠️ 工具名 F-039 |
| F-026 | 新会话问"我的职业是什么"→ 先调 openviking_search 再答"Java 开发工程师"；信息不在会话历史，来自召回 | ⚠️ 工具名 F-039；机制 ✅ |
| F-027 | 终端 `/search 职业` 列出命中资源/记忆/技能，带 .abstract.md、.overview.md、profile.md 文件名与 L0/L1/L2 层级、score | ✅ 文件名 F-037；/search 为博文实测单源 |
| F-028 | 上下文树展开到 user/macro/peers/macro/memories/profile.md，预览明文"职业：Java开发工程师"；记忆明文落盘 | ✅ F-038 |

### F. 外部 Agent 支持与作者结论

| 编号 | 事实 | 核验 |
|------|------|------|
| F-029 | 官方接入页列 Claude Code、Codex、OpenClaw 等，通用 MCP（TRAE、Cursor 等），SDK（Python、LangChain 等） | ✅ F-040（口径细化） |
| F-030 | 接入三步：启动自部署 Server → 跑安装脚本接 Claude Code → 重启可用 | ✅ F-041 |
| F-031 | 📌 作者观点：OpenViking 把上下文当工程对象对待；一条 docker run 带起服务/控制台/VikingBot；召回与存储控制台一目了然 | 观点 |
| F-032 | 📌 作者建议：受够 Agent 换会话失忆、想给 Coding Agent 补可观察可管理长期记忆，值得花半小时部署 | 观点 |

### G. 核验补充事实

| 编号 | 事实 | 信源 |
|------|------|------|
| F-033 | GitHub API 2026-09-09/10 快照：**36,276** stars、2,772 forks、105 watchers、703 open issues；仓库创建 **2026-01-05**；Python；AGPL-3.0；topics：agent-memory/agent-plugins/agentic-rag/context-database/dsh-plugin/self-evolving；官方描述 "Self-evolving Context Database for AI Agents. Unify Agent Memory, Knowledge RAG and Skills."；homepage openviking.ai | GitHub REST API |
| F-034 | 官方文档站 docs.openviking.ai；在线免安装 Studio openviking.ai/studio；基准版本 0.3.22；`pip install openviking --upgrade`（Python 3.10+，另需 embedding 与 VLM）；init/doctor 写 ~/.openviking/ov.conf；`pip install "openviking[bot]"` + `--with-bot` 起 VikingBot，`ov chat` 对话 | README/官方文档 |
| F-035 | Docker 文档：ghcr.io/volcengine/openviking:latest；容器内 1933 绑 0.0.0.0，Studio 同源 /studio，默认同启 vikingbot 网关；全部持久态在 /app/.openviking 单挂载；绑 0.0.0.0 **必须设 root_api_key 否则拒启动**；--without-bot / OPENVIKING_WITH_BOT=0 关 bot；OPENVIKING_CONF_CONTENT 传配置；旧入口 1934（Caddy 反代 1933，为既有部署保留）；另有 compose 与 Helm | docs/guides/03-deployment |
| F-036 | `GET /health` 无鉴权，文档示例仅 `{"status":"ok"}`（liveness）；`GET /ready` 检 AGFS/VectorDB/APIKeyManager/Embedding/Ollama（readiness）。博文 healthy/version/auth_mode 字段未见于现行文档（⚠️ 或为实测版本扩展返回；不影响存活验证结论） | 同上 |
| F-037 | L0=.abstract.md 一句话摘要；L1=.overview.md 核心信息与场景；L2=完整原文按需读取；语义处理过的目录携带 L0/L1 | README |
| F-038 | viking:// 布局：resources/（文档/仓库/网页）；user/{id}/ 下 memories/（含 preferences/）、resources/、skills/、peers/；会话 commit 归档+后台抽取，记忆策略对候选做 create/merge/skip；VikingBot 下 `ov compile` 组织 wiki/知识图谱/报告 | README |
| F-039 | MCP 端点 /mcp（1933 同进程同端口），X-Api-Key/Bearer 鉴权（localhost 免鉴权）；**15 工具**：find/search/read/list/tree/remember/write/edit/add_resource/list_watches/cancel_watch/grep/glob/forget/health；find=无会话上下文快检索，search mode="context" 组装注入上下文（替代旧 recall）。**博文 openviking_memory_commit/openviking_search 工具名不见于官方清单**（⚠️ 对应官方 remember/commit 机制与 search/find；疑为早期/界面化名称或作者转述） | MCP 指南/集成文档 |
| F-040 | 集成矩阵：Claude Code/Codex/Cursor/TRAE（含 TRAE CN/TraeCode CLI 2.0）Hooks+MCP；OpenClaw Context engine；Hermes built-in；OpenCode/DeerFlow/DSH Plugin+MCP；pi Native；Doubao Work Connector；LangChain Tools+store；SDK Python/Go/TypeScript + HTTP API。MCP 已验证平台：Claude Code/Trae/Cursor/ChatGPT&Codex/OpenCode/Manus/Claude Desktop(OAuth 2.1) | README/MCP 指南 |
| F-041 | 统一安装脚本 examples/memory-plugin-shared/install.sh --harness \<名称\>（claude-code/codex/cursor/trae/trae-cn/trae-cli 等，可逗号分隔）；trae-cli（TraeCode CLI 2.0）走 Codex 兼容插件格式；TOS 镜像 ovrelease.tos-cn-beijing.volces.com（--dist tos）；前置 macOS/Linux + Node 18+；装后重启客户端；Hooks：SessionStart/UserPromptSubmit/PreToolUse/Stop | TRAE/Cursor 集成文档 |
| F-042 | embedding provider 13 家：openai/azure/volcengine/vikingdb/jina/ollama/voyage/minimax/cohere/gemini/dashscope/litellm/local；dashscope 原生示例 text-embedding-v4/1024/text；博文 provider "openai" + /compatible-mode/v1 是官方并列给出的兼容接法；VLM 配置示例含 doubao-seed-2-0-lite-260428、gpt-5.4、kimi-code、GLM-4.6V/GLM-5V-Turbo（图像理解需视觉模型），openai-codex provider 可用 Codex OAuth | docs/guides/01-configuration |
| F-043 | 许可：主项目 AGPLv3，ov_cli/examples Apache-2.0；商业：火山托管 SaaS（个人/企业版，海外 BytePlus planned）、自管 BYOC（license key）；桌面 Helper 0.0.19 beta（macOS arm64/x64、Win x64）；多租户账号隔离 + 可选资源 ACL | README/LICENSE |
| F-044 | **厂商自述基准**（0.3.22，脚本 ./benchmark）：LoCoMo——OpenClaw 24.20%→82.08%、Hermes 33.38%→82.86%、Claude Code 57.21%→80.32%；输入 token -34.3%~91.0%；延迟 -58.45%~66.10%；tau2-bench——Retail 70.94%→77.81%（+6.87pp）、Airline 54.38%→66.25%（+11.87pp）；评测模型 Doubao 2.0 Pro + doubao-embedding-vision-251215 | README/benchmark blog |
| F-045 | 研究背景：VikingMem（arXiv:2605.29640，VLDB 2026）、目录感知检索/TrieHI（arXiv:2606.16903，ICDE）、VikingRAG（arXiv:2609.11390，submitted） | README Research |
| F-046 | 百炼核验：qwen3-vl-plus 在售（文/图/视频输入、256K 上下文、等同快照 qwen3-vl-plus-2025-12-19）；北京原价 ≤32k 输入 ¥1/输出 ¥10 每百万 token（2026-09 时点）；compatible-mode/v1 兼容端点；text-embedding-v4 为 1024 维中文优化模型 | help.aliyun.com |
| F-047 | ov CLI：status/add-resource（异步，task status 轮询）/ls/tree/find/grep；README 示例含 `ov tree viking://resources/volcengine -L 2`、`ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs/en`（导入后实际 URI 以 add-resource 返回为准）；ovcli.conf（url+api_key，OPENVIKING_CLI_CONFIG_FILE 可覆盖）；Python SDK SyncHTTPClient | README/deployment |
| F-048 | 其他部署：systemd（生产推荐，Environment 指向 /etc/openviking/ov.conf）、docker compose、Helm（examples/k8s-helm）、多实例配置（temp_upload shared、skip_process_lock、按实例 SQLite 路径）；自构镜像 `docker build --build-arg OPENVIKING_VERSION=0.3.12`（示例取值） | docs/guides/03-deployment |
