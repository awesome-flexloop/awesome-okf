---
type: Changelog
scope: tencentdb-agent-memory
name: log
version: "0.1.0"
---

# Changelog

## 0.1.0 — 2026-10-04

### 新增

- 首次建束：TencentDB Agent Memory 源码学习 OKF 知识包
- **信源截面**：`TencentCloud/TencentDB-Agent-Memory`，commit `8b86874a2daea49e3ff0fb53d699203146c5c77d`（feat/server_team，v2.0.2-beta.3-7-g8b86874，2026-10-04 采集），本地位于本仓 external 稳定信源区
- **spec/facts.md**：F-001 ~ F-300 共 300 条编号事实，分 14 个主题段；含 7 处「⚠️ 口径」并列登记（组织名、三套版本号、Knowledge/Panel 端口、客户端 7 vs 8、数据目录、Standalone 镜像名）
- **spec/insights.md**：6 条四元组洞察——①协议不变替代插件生态；②沉淀/压缩双管线；③fail-open 降级美学；④自定义 Prompt 与固定协议分离；⑤三元组强隔离与数据面/元数据面拆分；⑥知识资产工具化与异步构建状态机
- **concepts/**：13 篇（00~12）
- **examples/**：4 篇（一键部署 / Claude Code 接入 / 自定义 Prompt / Wiki·CodeGraph 摄取）
- **references/**：5 份（源码地图 / README+CHANGELOG / v3 API 三卷 / 部署安装 / SDK+CI）

### V 阶段记录（2026-10-04 完成）

- **门禁结果（py314 / awesome-okf-xs）**：`invoke gates.toctrees` 通过（全部 index.md 引用有效、内容文档可达，含本束 29 文件）；`invoke gates.bundles` 通过（9 域 / 61 组 / 586 束五面一致）；`invoke gates.utf8` 通过（10906 文件）。
- **计数断言（机械清点）**：束内 29 个 .md（根 2 + spec 2 + concepts 14[13 篇+index] + examples 5[4 篇+index] + references 6[5 份+index]）；facts.md 定义 F-001~F-300 共 300 条、无缺号；全束引用无越界编号（无 F-301+）；束内相对链接 0 断链；无 file:/// 与 .temp 引用；concepts/examples 无 mermaid 代码块；分区 index 无 frontmatter 与范本束 tencent-meeting-cli 约定一致。
- **Grep 级 API 抽验（回源 commit 8b86874）**：① V3_ALLOWED_SUBPATHS 实集 18 成员（v2-router.ts:153-172 逐条计数），同文件 :520 注释自述「14 条」系过期注释，已在 references/03 显式标注防误用；② RRF_K=60（search-utils.ts:18 等 4 处）；③ L1_BATCH_SIZE=5、MAX_L1_CHUNK_RETRIES=3（offload/index.ts:401-402）；④ registerOffload/compressByScoreCascade/EMERGENCY_MIN_MESSAGES_TO_KEEP（offload/index.ts:42-47）；⑤ 注入标记 `<tdai_recalled_l1_memories>`（tdai-l1-recall-injector.ts:94）、`<tdai_memory_tools>`（tdai-tools-injector.ts:70）；⑥ TS SDK MemoryClient（v3/client.ts:147）与构造字段 endpoint/apiKey/serviceId/teamId/agentId/userId（client.ts:8-19 + v3/types.ts:22-32）；⑦ wikilink 正则（engines/wiki/manager.ts:89）、wiki_fts/graph_edge（index-db.ts:76/97）；⑧ META_START（scene-format.ts:18）；⑨ DISK_FLAT 优先 + HNSW 回退 M:16/efConstruction:200（tcvdb/memory-store.ts:312-323）；⑩ MemoryProxy 包名 context-proxy@0.1.0、hono ^4.7.10。
- **V 中修复**：F-206 信源锚点由 engines/wiki/index.ts 修正为 manager.ts:89（含 graphology 读时构建补充）；references/index 笔误「2002-beta.1」改「2.0.2-beta.1」；references/03 补过期源码注释警示。
- **索引更新**：tencent 分组（11 束/75 概念/20 示例/46 信源/1063 事实）、ecosystems 类（86 束）、ai 域（216 束）、jishu 域（437 束）、根总索引（586 束；其中 +1 属并行会话 cubesandbox，其 containers 计数按门禁地面真值同步为 15）。

### 已知局限

- 学习截面为 feat/server_team 分支提交而非正式 release tag（最近 tag 后差 7 个提交）
- 全部事实基于静态阅读，未在真实 Docker/Agent 环境运行验证；示例文件均已声明
- CHANGELOG 克隆 URL 的组织名（Tencent）与实际 remote（TencentCloud）不一致，并列登记未裁决
- MongoDB 后端、ClickHouse 可观测、OAuth2 对接为试验/可选特性，文档细节未逐行深挖代码
