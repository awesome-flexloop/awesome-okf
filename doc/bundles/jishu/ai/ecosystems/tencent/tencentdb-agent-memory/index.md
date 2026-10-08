---
type: bundle
okf_version: "0.2"
scope: tencentdb-agent-memory
name: tencentdb-agent-memory
version: "0.1.0"
source: code
description: "腾讯 TencentDB Agent Memory 源码知识包：MemoryCore/MemoryKnowledge/MemoryPanel/MemoryProxy 四件架构，L0-L3 四层记忆沉淀与 offload 上下文压缩双管线，Skill/Wiki/CodeGraph 四类资产，v3 三元组强隔离，双协议代理零插件接入（commit 8b86874 截面，300 条编号事实）。"
---

# TencentDB Agent Memory 知识库

TencentDB Agent Memory 是腾讯开源的 Agent 记忆系统（MIT，仓库 [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)，Node.js ≥ 22.16），README 标语为「让 Agent 沉淀经验，让人专注创造」，围绕三个技术问题展开：**什么值得留下、谁可以使用、下一次怎样少拿但拿对**（F-019）。它由四个组件构成：MemoryCore（记忆核心 :8420）、MemoryKnowledge（Wiki/CodeGraph 知识引擎）、MemoryPanel/Hub（团队操作台）、MemoryProxy（OpenAI/Anthropic 双协议 LLM 代理 :8096）（F-022）。

理解本系统有四把钥匙：① **双管线**——L0→L3 跨会话记忆沉淀与 offload 会话内上下文压缩是两套同名不同义的机制，仅在 Skill 产物处汇合；② **降级优先**——JSONL 主存不可降级、向量/LLM/BM25 能力全部可缺席，记下来优先于记得好；③ **协议不变**——Agent 改 base URL 即获得团队记忆，无需插件/Hook/MCP，适配成本收敛在 proxy 的 8 个协议适配器内；④ **隔离即存储格式**——v3 强制 team/agent/user 三元组，隔离字段直接进入 FTS5 与 vec0 虚表。

本知识包基于固定源码截面（commit `8b86874`，feat/server_team 分支，v2.0.2-beta.3 后第 7 个提交，2026-10-04 采集）经 R→I→E→V→C 流程生成，共 300 条编号事实、6 条四元组洞察、13 篇概念、4 篇示例、5 份信源登记。

## 概念篇

| 文档 | 说明 |
|------|------|
| [产品定位与四件架构](concepts/00-overview.md) | 技术三问、四件全景与端口、三套版本口径、Standalone/Service 形态 |
| [四层记忆与四类资产](concepts/01-four-layer-memory.md) | L0 Conversation→L1 Atom→L2 Scenario→L3 Persona；Skill/Wiki/CodeGraph；可见性四值与角色 |
| [L0/L1 记忆管线](concepts/02-l0-l1-pipeline.md) | 抽取/去重四决策/JSONL+向量双写/fail-open 降级/hooks/后台服务 |
| [L2 场景、L3 Persona 与自定义 Prompt](concepts/03-l2-scene-l3-persona.md) | scene_blocks 与 heat、5 类 Persona 触发、Prompt 四级解析与固定输出协议 |
| [存储后端与混合检索](concepts/04-storage-retrieval.md) | sqlite/TCVDB/Mongo 决策、RRF_K=60、BM25、配额、元数据/数据面分库 |
| [Skill 记忆资产](concepts/05-skill-memory.md) | 三物理表、不可变多版本快照、head 索引、17 个 v3 端点、乐观锁权限 |
| [网关、API 与多租户隔离](concepts/06-gateway-isolation.md) | 响应信封、422 三元组、18 数据面子路径、Bearer 鉴权、per-instance |
| [offload 上下文压缩管线](concepts/07-offload-context.md) | 双管线辨析、L1.5 任务边界、L2 MMD 节点、L3 三级压缩、L4 create-skill |
| [MemoryKnowledge 知识引擎](concepts/08-memory-knowledge.md) | 5 表状态机、12 个 MCP 只读工具、Wiki 链接图谱、llm-binding、auto-sync |
| [MemoryProxy 双协议代理](concepts/09-memory-proxy.md) | /v1/chat/completions 与 /v1/messages、8 适配器、8 注入器、mem 指令 |
| [MemoryPanel 与访问控制](concepts/10-panel-acl.md) | Hub 面板、16 个 RPC action、Loadout、OAuth2、四值可见性管理 |
| [部署拓扑](concepts/11-deploy-topology.md) | 三容器拓扑、start-all 顺序、端口卷默认值、两组 LLM、健康检查 |
| [官方 SDK 与工程配套](concepts/12-sdk-engineering.md) | TS/Python SDK v3 强制三元组、CI、测试与运维脚本 |

## 实战示例

| 示例 | 说明 |
|------|------|
| [十分钟一键部署](examples/01-quickstart.md) | 配两组 LLM → start-all.sh 三件套 → .admin-key → purge 重置 |
| [Claude Code 经 Proxy 接入](examples/02-claude-code-proxy.md) | ANTHROPIC_BASE_URL/TOKEN、首轮 sessionInit、mem 会话指令 |
| [自定义记忆 Prompt](examples/03-custom-memory-prompt.md) | memory-prompt create/set/log、SHA-256 审计、500/10000 限额与协议红线 |
| [Wiki/CodeGraph 摄取与查询](examples/04-wiki-codegraph-ingest.md) | create→轮询 ready、12 个 MCP 只读工具、llm-binding、auto-sync |

## 核心洞察（四元组）

1. **以「协议不变」替代插件生态**——双协议侧车承载记忆业务，N×M 插件矩阵改写为 N 适配器 × 1 内核；
2. **沉淀管线与压缩管线刻意分离**——L0→L3 产出跨会话资产，offload L1.5/L2/L3/L4 服务当前会话预算，仅 Skill 汇合；
3. **降级优先（fail-open）**——主存不可降级、派生索引皆可重建，记下来优先于记得好，监控须消费「不健康」标记；
4. **自定义 Prompt 与固定输出协议分离**——策略文本可编辑（≤500 条/≤10000 字），JSON/MD/Persona 协议冻结，正文不留痕只存 SHA-256；
5. **多租户隔离写进存储格式**——三元组强制 + FTS5/vec0 隔离列 + scope 行级函数 + 元数据/数据面分库；
6. **组织资产工具化而非整库注入**——Wiki/CodeGraph/Skill 经 12 个只读 MCP 工具随用随取，配合异步状态机与 Loadout 最小授权。

详见 [spec/insights.md](spec/insights.md)。

## 信源登记簿

| 信源 | 文件 | 内容 |
|------|------|------|
| 源码地图 | [01-source-code-map.md](references/01-source-code-map.md) | commit/tag、四组件目录地图、10 项计数机械复核 |
| README/CHANGELOG | [02-readme-changelog.md](references/02-readme-changelog.md) | 产品表述、5 版本时间线、ROADMAP、7 组口径差异 |
| v3 API 三卷 | [03-api-references.md](references/03-api-references.md) | Core 108 端点、Knowledge 37 端点、Proxy 6 接口、OpenAPI |
| 部署安装 | [04-deploy-install.md](references/04-deploy-install.md) | 8 客户端、start-all 脚本、env/端口/卷、两形态 |
| SDK/CI | [05-sdk-ci.md](references/05-sdk-ci.md) | TS/Python SDK 结构、CI、测试与运维脚本 |

完整编号事实见 [spec/facts.md](spec/facts.md)（F-001 ~ F-300）。

## 学习路径建议

1. **首次接触**：[产品定位](concepts/00-overview.md) → [四层记忆](concepts/01-four-layer-memory.md) → [十分钟部署](examples/01-quickstart.md)
2. **Agent 使用者**：[MemoryProxy](concepts/09-memory-proxy.md) → [Claude Code 接入示例](examples/02-claude-code-proxy.md)
3. **理解记忆机制**：[L0/L1 管线](concepts/02-l0-l1-pipeline.md) → [L2/L3/Prompt](concepts/03-l2-scene-l3-persona.md) → [存储检索](concepts/04-storage-retrieval.md) → [offload 双管线](concepts/07-offload-context.md)
4. **多租户/平台开发**：[Skill 资产](concepts/05-skill-memory.md) → [网关隔离](concepts/06-gateway-isolation.md) → [Panel ACL](concepts/10-panel-acl.md)
5. **知识资产场景**：[MemoryKnowledge](concepts/08-memory-knowledge.md) → [摄取示例](examples/04-wiki-codegraph-ingest.md)
6. **SDK 集成者**：[SDK 与工程](concepts/12-sdk-engineering.md) → [自定义 Prompt 示例](examples/03-custom-memory-prompt.md)
7. **部署运维**：[部署拓扑](concepts/11-deploy-topology.md)

## 目录结构

```
tencentdb-agent-memory/
├── index.md                    # 本文件（知识包根索引）
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # R 阶段：300 条编号事实（F-001 ~ F-300）
│   └── insights.md             # I 阶段：6 条四元组洞察 + 知识地图
├── concepts/
│   ├── index.md
│   ├── 00-overview.md          # 00 ~ 12 共 13 篇
│   └── …
├── examples/
│   ├── index.md
│   ├── 01-quickstart.md        # 共 4 篇
│   └── …
└── references/
    ├── index.md
    ├── 01-source-code-map.md   # 共 5 份
    └── …
```

## 信任与生命周期说明

- **事实来源**：全部 300 条事实来自固定源码截面（remote `TencentCloud/TencentDB-Agent-Memory`，commit 8b86874a2daea49e3ff0fb53d699203146c5c77d，采集日 2026-10-04）及随仓文档（README_CN、CHANGELOG、INSTALL_CN、三卷 v3 API、deploy 脚本、SDK），代码事实带文件路径与行号锚点，未引入外部推测。
- **未运行验证声明**：本束由静态源码/文档学习生成，未在真实 Docker、LLM 或 Agent 客户端环境运行验证；4 篇示例均在开头显式声明，落地使用前请按示例实测。
- **截面性质**：学习截面位于 feat/server_team 分支（最近 tag v2.0.2-beta.3 之后第 7 个提交），非正式 release；行号锚点随分支前进可能漂移，复核以符号名为准。
- **口径差异处理**：7 组差异并列登记不做单边取舍——README 组织名 Tencent vs 实际 TencentCloud（F-018）；产品版本 v2.0.0 / npm 1.0.2-beta.1 / git tag v2.0.2-beta.3（F-021）；Knowledge 8421/8424（F-023）；Panel 8123/8125（F-024）；客户端 7 vs 8（F-027/F-028）；数据目录 memory-tencentdb/openclaw（F-054/F-055）；Standalone 镜像名 hermes-memory/memory-core（F-032/F-033）。
- **试验特性限定**：MongoDB 存储后端、ClickHouse 可观测、OAuth2 OA 对接均为可选/默认关闭（2.0.2-beta.1），引用不得省略该限定。
- **stale_after 解释**：统一设置为 2027-04-04（生成日后 6 个月）。依据：CHANGELOG 显示 2026-07~09 两月内发布 5 个版本、feat/server_team 分支活跃；到期应重新固定正式 release tag，复核 v3 API 端点数、proxy 适配器数与 env 默认值。
- **覆盖范围**：覆盖四件架构、L0-L3 沉淀管线、offload 压缩管线、Skill/Wiki/CodeGraph 资产模型、网关隔离、部署拓扑与官方 SDK；不含 LLM 提示词全文（系统不存正文）、TCVDB/COS/Redis 云服务本身、前端面板 UI 实现细节与 Benchmark 复现实验。
- **内容敏感度**：全部内容来自公开开源仓库，属公开内容（Public）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
