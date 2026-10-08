# 核验报告

> 核验日期：2026-09-16
> 核验方式：GitHub REST API + 官方仓库 README + docs.openviking.ai 官方文档（部署/配置/MCP/集成）逐句比对 + 阿里云百炼官方文档模型核验
> 核验人：OKF Wiki Bot（blog-article-to-okf-wiki 七阶段工作流）

## 总结

| 项 | 结果 |
|----|------|
| 事实总数 | 48（博文 32：含 2 条作者观点；核验补充 16） |
| P0 关键声明 | 10 项 |
| ✅ 通过 | **10**（其中 3 项附口径细化，非错误） |
| ⚠️ 口径差异 | 2（/health 响应字段；VikingBot 工具名） |
| ❌ 失败 | **0** |

**结论**：博文的核心声明（开源主体、35K+ star、viking:// 文件系统、三层加载、Docker 部署链路、百炼模型配置、跨会话记忆、多 Agent 接入）全部与官方材料一致，未发现虚构或营销夸大；博文本身不含成效数字。2 项 ⚠️ 均为**术语/响应字段层面的口径差异**，不影响任何操作步骤的正确性，正文已按官方口径呈现并标注博文说法。bundle 状态 `verified`，无需 flagged。

## P0 逐项核验

### 1. 项目身份与"字节开源" — ✅

- 仓库 https://github.com/volcengine/OpenViking 真实存在且 Public，owner 为 volcengine 组织（火山引擎，字节跳动旗下云品牌），与"字节开源"表述一致（F-002/F-004）
- 官方一句话描述："Self-evolving Context Database for AI Agents. Unify Agent Memory, Knowledge RAG and Skills."（F-033）
- 主语言 Python；仓库创建于 2026-01-05；许可证 AGPL-3.0（F-033/F-043）

### 2. "35K+ star" — ✅

- GitHub API 2026-09-09/10 快照 stargazers_count = **36,276**（博文发布当天；forks 2,772），"35K+"为保守下限表述，成立（F-003/F-033）
- star 数随时间变化，正文引用时带"2026-09 快照"时点限定

### 3. viking:// 虚拟文件系统与三类上下文 — ✅

- README 原文：上下文组织为 viking:// 下的虚拟文件系统，可用 ls/tree/read/write 操作；resources（文档/代码/网页）、memories（用户偏好与经验）、skills（任务做法）各有 viking:// URI（F-004/F-005/F-038）
- 博文 user 树路径 user/macro/peers/macro/memories/profile.md 与官方布局 user/{user_id}/{memories,resources,skills,peers} 一致（F-028/F-038）

### 4. L0/L1/L2 三层加载 — ✅

- 官方：L0 Abstract = `.abstract.md` 一句话摘要；L1 Overview = `.overview.md` 结构与要点；L2 Details = 完整原文按需读取；语义处理过的目录携带 L0/L1 摘要（F-006/F-037）
- 博文终端检索所见 .abstract.md/.overview.md/profile.md 文件名与层级标注与官方一致（F-027）

### 5. 目录递归检索 / 可回溯 — ✅

- README：向量搜索先定位候选目录再下探内容；find 直查、search 可结合会话上下文规划检索（F-008）
- 学术底座：目录感知查询论文（arXiv:2606.16903，ICDE 收录）的 TrieHI 机制已集成，用于向量排序前解析目录范围；检索轨迹可复用（F-007/F-045）

### 6. Docker 部署链路（镜像/端口/挂载/同启组件） — ✅

- 官方部署文档：镜像 `ghcr.io/volcengine/openviking:latest`；容器内 HTTP 绑 0.0.0.0:1933，Web Studio 同源 /studio，默认同时启动 vikingbot 网关（F-018/F-019/F-021/F-035）
- 全部持久态（ov.conf、ovcli.conf、workspace）位于容器内 `/app/.openviking`，单挂载即可——博文 `-v /mydata/openviking:/app/.openviking` 与官方 `-v ~/.openviking:/app/.openviking` 同构（F-035）
- 安全要求：容器绑 0.0.0.0 时**必须设 root_api_key，否则服务拒绝启动**——博文配置含该字段，部署可成功（F-013/F-022/F-035）
- 博文命令较官方少 `--restart unless-stopped`，仅为重启策略差异，不影响正确性

### 7. ov.conf 四段配置与百炼模型 — ✅

- server/storage/embedding/vlm 四段与官方配置指南一致；字段 host/port/root_api_key/public_base_url、workspace、agfs/vectordb backend 均存在（F-013/F-014/F-017）
- text-embedding-v4：官方 dashscope provider 支持列表在册，dimension 1024、中文优化；博文走 `provider: "openai"` + `dashscope.aliyuncs.com/compatible-mode/v1`，属官方文档并列给出的"OpenAI 兼容端点"合法接法；原生接法可用 `provider: "dashscope"`（F-015/F-042）
- qwen3-vl-plus：阿里云百炼在售 Qwen3 视觉模型（文/图/视频输入、256K 上下文，现版本等同快照 qwen3-vl-plus-2025-12-19），OpenAI 兼容 Vision 接口可调，承担 VLM 有效（F-016/F-046）

### 8. 跨会话记忆机制（会话沉淀 + 自动召回） — ✅（工具名 ⚠️ 见下）

- 官方机制：提交会话（commit）归档对话并启动后台抽取，记忆策略对候选记忆执行 create/merge/skip；Hooks 集成在会话开始/提问时自动召回注入、会话停止时捕获提交（F-009/F-038/F-041）
- 记忆明文以 Markdown 文件落盘（profile.md 等），可在 Studio 上下文树直接预览，与博文"看得见摸得着"一致（F-028）
- 新会话回答职业问题的信息来自检索而非会话历史，机制成立（F-026）

### 9. 多 Agent 接入矩阵与"三步接入" — ✅（口径细化）

- 官方集成表覆盖博文所列全部对象：Claude Code、Codex、OpenClaw、TRAE、Cursor 在册（F-029/F-040）
- **口径细化 1**：博文把 TRAE、Cursor 归为"通用 MCP 方式"，官方实际为两者提供了专用 **Hooks + MCP** 集成（自动召回/捕获），通用 MCP 也支持但非唯一方式——正文按官方口径呈现
- **口径细化 2**：博文称"SDK（Python、LangChain 等）"，官方 SDK 语言为 **Python / Go / TypeScript**（另有 HTTP API），LangChain 属于 Tools + store 框架集成而非 SDK 语言——正文按官方口径呈现
- 三步接入（起 Server → 跑安装脚本 → 重启）与官方快速开始一致；补充官方前置：macOS/Linux + Node.js 18+（F-030/F-041）

### 10. VikingBot 与 Web Studio 形态 — ✅

- 官方 Docker 镜像内置 VikingBot 且默认随服务与控制台同启；`pip install "openviking[bot]"`、`openviking-server --with-bot`、`ov chat` 为非容器形态（F-031/F-034/F-035）
- Studio 为自带 Web 控制台（/studio 同源），亦有免安装在线版 openviking.ai/studio；仪表盘/上下文树/会话区与博文描述同构（F-021/F-024/F-034）

## ⚠️ 口径差异（2 项，均非硬错误）

### ⚠️-1 /health 响应字段

- 博文：/health 返回 `status: ok`、`healthy: true`，并带出服务版本与 auth_mode（F-020）
- 官方现行文档（2026-09-11 更新）：`GET /health` 无鉴权，示例仅 `{"status":"ok"}`（liveness）；组件级健康在 `GET /ready`（检查 AGFS/VectorDB/APIKeyManager/Embedding/Ollama）（F-036）
- 处理：正文以官方两探针口径为准，博文说法标注为"作者实测所见（或含版本扩展字段）"；/health 用于存活验证的操作结论不受影响

### ⚠️-2 VikingBot 调用的工具名

- 博文：写记忆调 `openviking_memory_commit`、检索调 `openviking_search`（F-025/F-026）
- 官方 2026-09 文档的 MCP 工具集为 15 个：find/search/read/list/tree/remember/write/edit/add_resource/list_watches/cancel_watch/grep/glob/forget/health，无上述两个名称；主动固化记忆对应 `remember`，会话后台沉淀对应 commit 机制，检索对应 `search`（带上下文）/`find`（直查）（F-039）
- 处理：判定为 VikingBot 早期/界面化名称或作者转述（博文为实测记录，工具调用名可能随版本变化）；正文保留博文实测叙述但显式标注与现行官方工具名的对应关系，读者接 MCP 时以官方 15 工具为准

## 勘误四张清单

| 清单 | 结论 |
|------|------|
| ① 日期/版本 | 博文未给软件版本 → 补 **0.3.22**（README 基准节，2026-09）；仓库创建日 **2026-01-05**（GitHub API）；博文发布 2026-09-09 与页面元数据一致；qwen3-vl-plus 当前等同 2025-12-19 快照（百炼公告） |
| ② 成效数字 | 博文无提效/工时/成本类成效数字，无污染项；star 35K+ ✅（36,276，2026-09-09 快照）；官方 LoCoMo/tau2 基准为**厂商自述**（F-044），正文显式标注且不并入博文结论 |
| ③ 口径对照 | "TRAE/Cursor = 通用 MCP" → 细化为专用 Hooks+MCP；"SDK（Python、LangChain）" → SDK 为 Python/Go/TS，LangChain 为框架集成；"35K+ star"带时点快照；百炼定价带"北京区原价/≤32k/2026-09"限定 |
| ④ 引文核对 | 博文未引用官方高管言论或报告结论，无引号转述风险；作者观点（F-031/F-032）显式分层，未固化为官方结论 |

## 信源清单

| ID | 信源 | 用途 |
|----|------|------|
| blog | https://mp.weixin.qq.com/s/OFS4DzgTEcEgzNHyvRVD0g | 博文原文（macrozheng，2026-09-09） |
| github-api | https://api.github.com/repos/volcengine/OpenViking | star/fork/创建日/许可/topics 快照 |
| github-readme | https://github.com/volcengine/OpenViking | 定位、架构、集成矩阵、基准、研究论文 |
| docs-deploy | https://docs.openviking.ai/en/guides/03-deployment | Docker、端口、挂载、探针、systemd/Helm |
| docs-config | https://docs.openviking.ai/en/guides/01-configuration | ov.conf、provider 列表、dashscope 示例 |
| docs-mcp | https://docs.openviking.ai/en/guides/06-mcp-integration | MCP 端点/鉴权/工具集 |
| docs-trae | https://docs.openviking.ai/en/agent-integrations/13-trae/llms.txt | 15 工具清单、Hooks 四事件、安装脚本 |
| docs-cursor | https://docs.openviking.ai/en/agent-integrations/12-cursor | Hooks + MCP 集成形态 |
| aliyun-vl | https://help.aliyun.com/zh/model-studio/qwen3-vl-plus | qwen3-vl-plus 模型事实与价格 |
| paper-vikingmem | https://arxiv.org/abs/2605.29640 | VikingMem（VLDB 2026） |
| paper-triehi | https://arxiv.org/abs/2606.16903 | 目录感知检索（ICDE） |
| paper-vikingrag | https://arxiv.org/abs/2609.11390 | VikingRAG（2026-09 投稿，结构化文档检索） |

## 时效性边界（stale_after: 2026-12-31）

以下内容变化快，到期前需复核：

- star/fork 等社区热度数字（引用必须带快照时点）
- 软件版本（核验时 0.3.22）与 MCP 15 工具清单（博文工具名差异或随版本演进而消解）
- 官方集成矩阵（新增 Agent 客户端/Harness）
- 百炼模型名称与价格（qwen3-vl-plus 快照版本、text-embedding-v4 档位定价）
- 商业形态（BytePlus 海外托管计划、自管版能力）与桌面端版本（核验时 Helper 0.0.19 beta）
