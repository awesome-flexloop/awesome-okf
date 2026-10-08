# Concepts

本目录包含 TencentDB Agent Memory 的 13 个概念文档，按「入门 → 记忆管线 → 平台能力 → 部署与工程」组织。所有断言回引 [spec/facts.md](../spec/facts.md) 的 F 编号（F-001 ~ F-300）。

## 入门与总体架构

- [00 - 产品定位与四件架构](00-overview.md) — 标语与技术三问、Core/Knowledge/Panel/Proxy 四件、三套版本口径、Standalone/Service 两形态
- [01 - 四层记忆与四类资产](01-four-layer-memory.md) — L0→L1→L2→L3、Chat Memory/Skill/Wiki/CodeGraph、可见性四值与角色

## 核心管线

- [02 - L0/L1 记忆管线](02-l0-l1-pipeline.md) — 抽取默认值、去重四决策、JSONL+向量双写、fail-open 降级、hooks 与后台服务
- [03 - L2 场景、L3 Persona 与自定义 Prompt](03-l2-scene-l3-persona.md) — scene_blocks/META/heat、5 类 Persona 触发、memory-prompt 四级解析与固定输出协议
- [04 - 存储后端与混合检索](04-storage-retrieval.md) — sqlite/TCVDB/Mongo 决策、vec0/FTS5 隔离列、RRF/BM25、配额与元数据/数据面分库
- [05 - Skill 记忆资产](05-skill-memory.md) — 三物理表、不可变多版本快照、head 索引、17 个 v3 端点、提取与乐观锁
- [06 - 网关、API 契约与多租户隔离](06-gateway-isolation.md) — 响应信封、422 三元组、18 数据面子路径、Bearer 鉴权、per-instance
- [07 - offload 上下文压缩管线](07-offload-context.md) — 沉淀/压缩双管线辨析、L1.5 任务边界、L2 MMD、L3 三级压缩、L4 create-skill

## 平台能力

- [08 - MemoryKnowledge 知识引擎](08-memory-knowledge.md) — 5 表状态机、12 个 MCP 只读工具、Wiki 图谱索引、llm-binding、auto-sync
- [09 - MemoryProxy 双协议代理](09-memory-proxy.md) — OpenAI/Anthropic 双协议、8 适配器、8 注入器、mem 指令、频控与计费
- [10 - MemoryPanel 与访问控制](10-panel-acl.md) — Hub 面板、16 个 RPC action、Loadout、四值可见性、OAuth2

## 部署与工程

- [11 - 部署拓扑](11-deploy-topology.md) — 三容器拓扑、start-all 顺序、端口卷默认值、两组 LLM、健康检查
- [12 - 官方 SDK 与工程配套](12-sdk-engineering.md) — TS/Python SDK v3 强制三元组、CI、测试与运维脚本生态

## 阅读建议

1. **新用户**：00 → 01 → [十分钟上手](../examples/01-quickstart.md) → [Claude Code 接入](../examples/02-claude-code-proxy.md)
2. **理解记忆机制**：02 → 03 → 04（先读 07 开头的「双管线辨析」避免把压缩与沉淀混为一谈）
3. **多租户/平台开发者**：05 → 06 → 10
4. **部署运维**：11 → 08 → 09
5. **SDK 集成者**：12 → [自定义 Prompt 示例](../examples/03-custom-memory-prompt.md)
6. **代码/知识资产场景**：08 → [Wiki/CodeGraph 摄取示例](../examples/04-wiki-codegraph-ingest.md)

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-four-layer-memory
02-l0-l1-pipeline
03-l2-scene-l3-persona
04-storage-retrieval
05-skill-memory
06-gateway-isolation
07-offload-context
08-memory-knowledge
09-memory-proxy
10-panel-acl
11-deploy-topology
12-sdk-engineering
```
