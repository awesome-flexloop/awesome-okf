# 核验报告

> 核验日期：2026-09-02
> 核验方式：官方仓库 README / LICENSE / llms.txt / docs（getting-started、troubleshooting）逐句比对 + WebSearch 第三方旁证
> 核验人：OKF Wiki Bot

## 总结

| 项 | 结果 |
|----|------|
| 事实总数 | 52（博文 33 + 核验补充 19） |
| P0 关键声明 | 10 项 |
| ✅ 通过 | **10** |
| ⚠️ 口径标注 | 2（Firecrawl 免费额度单源；博文确切发布日期未检出） |
| ❌ 失败 | **0** |

**结论**：博文涉及的仓库、许可证、工具清单、安装命令、结果契约、对比测试全部与官方材料一致，未发现虚构或夸大。博文作者的"实在话"（磁盘占用、引擎偶发失效、beta 边界）与官方 FAQ 的诚实声明互相印证。2 项 ⚠️ 均为信源完整性提示，不影响任何操作步骤的正确性。

## P0 逐项核验

### 1. GitHub 仓库真实存在 — ✅

- 仓库 https://github.com/KnockOutEZ/wigolo **真实存在且 Public**，TypeScript 项目
- README 标语与博文一致："Local-first web intelligence for AI agents — no keys, no cloud, no metered bill"
- 文档站 https://knockoutez.github.io/wigolo/，llms.txt 提供机器可读项目摘要
- 第三方旁证：CSDN 热点榜第 163 期（2026-07-19）收录，仓库创建于 2026-04-12，Public Beta

### 2. 开源许可证 AGPL-3.0 — ✅

- LICENSE 文件为 GNU AGPL v3 全文，Copyright 2026 Towhid Khan；llms.txt 标注 "AGPL-3.0-only"
- 维护者 @yourtowhid（Towhid Khan）；博文"作者一个人维护"基本准确，补充：README 鸣谢赞助商 TestMu AI（formerly LambdaTest）
- 官方 FAQ 对 AGPL 有通俗解释：**当工具用零义务**；仅当修改 wigolo 本体并把修改版作为网络服务提供给他人时触发开源义务（F-051）

### 3. 十个工具清单 — ✅

- docs/tools.md 与 llms.txt 均列十工具：search / fetch / crawl / cache / extract / find_similar / research / agent / diff / watch
- keyless 边界精确化：**六工具 keyless**（search/fetch/crawl/extract/cache/find_similar）；research/agent/`search --format answer` 需 LLM，无 key 时返回结构化证据简报而非成文（F-037）——博文"不配也不影响使用，把原始材料和证据交出来"表述准确

### 4. 18 个搜索引擎 + 本地重排 — ✅

- README 引擎适配器表列出 18 个直连搜索引擎（bing、duckduckgo 等）
- 架构：多引擎并行 → rank fusion → 本地 ML reranker 重排（on-device reranking model，约随包下载）
- query 支持数组扇出：一次调用并行查多个问题

### 5. 安装命令与环境要求 — ✅

- `npx wigolo init` 无人值守安装（下载浏览器引擎 + 本地 embedding/reranking 模型 + 逐组件健康检查）
- Node 20/22/24 LTS；macOS / Linux / Windows 全支持；Windows 数据目录 `%USERPROFILE%\.wigolo`
- 磁盘构成（官方 FAQ）：模型约 250MB + 浏览器引擎约 0.5–1GB，与博文"至少 1.5G"一致
- `--agents=claude-code,cursor` 一键接线，官方 auto-wire 矩阵含 9 个客户端

### 6. "七千多个测试用例" — ✅

- 官方 FAQ 原文："Public beta at 0.2.0. The documented surface is held to a test suite of roughly **7,600** automated tests"
- 博文"七千多个测试用例"与官方数字一致；顺带补全版本号：**0.2.0 public beta**

### 7. 字节级证据与诚实输出 — ✅

- README 结果示例确认字段：`citation_id`、`source_span`（字节偏移 start/end）、`evidence_score`（final/semantic/lexical/engine_consensus）、`freshness_signal`
- 弱结果打 `junk` 标签；失败引擎进 `engine_warnings`/`engine_telemetry` 而非静默隐藏；陈旧缓存显式标注
- fetch 遇反爬三级升级（plain HTTP → TLS-impersonation → 无头浏览器），过不去标 `blocked_by_challenge`，不把验证页当正文

### 8. 四工具横向对比（Benchmark） — ✅

- README Benchmark 段原文：单场 Claude（"Claude Fable 5"）会话同题对比内置 WebSearch / wigolo / Tavily / Exa
- 四者答案与头号信源一致；wigolo 唯一返回字节级定位证据 + 评分拆解 + 逐引擎遥测，并标出 2 条弱结果
- 官方对比矩阵由 Exa 完整渲染，口径标注 "Feature standing as of July 2026"
- 博文转述与原文一致，未发现夸大

### 9. REST / SDK / 框架集成 — ✅

- `wigolo serve` 默认 127.0.0.1:3333，`POST /v1/{tool}`，`GET /openapi.json`（OpenAPI 3.1），远程 MCP 走 /mcp + /sse
- 安全设计 fail-closed：绑定非 loopback 必须设 `WIGOLO_API_TOKEN`
- SDK：npm `wigolo-sdk`（零依赖，local 模式自动拉起 daemon）、PyPI `wigolo`（纯标准库，sync+async）
- 框架包：wigolo-langchain / wigolo-crewai / wigolo-llamaindex / wigolo-vercel-ai-sdk；Docker：ghcr.io/knockoutez/wigolo

### 10. 隐私模型 — ✅

- 全部数据留 `~/.wigolo/`（Windows `%USERPROFILE%\.wigolo`）
- 遥测默认关闭，opt-in（`WIGOLO_TELEMETRY=1`）才写 NDJSON；日志默认全走 stderr
- 代理凭据进 OS keychain 不落盘；LLM 为可选外接（含本地 Ollama），核心六工具无任何外发 key

## ⚠️ 口径标注（2 项）

1. **Firecrawl "一个月送一千页"**：博文转述的免费额度属厂商商业政策，随时间变动，本次未独立核验。引用时标注"博文口径，2026-07"。
2. **博文确切发布日期/标题**：微信页面元数据未成功抓取，检索亦未命中该公众号原文页；标题依内容概括，时点按文中 "July 2026" 口径与同题报道窗（2026-07-16~21）推断为 **2026-07 下旬**。

## 勘误四张清单

| 清单 | 结论 |
|------|------|
| ① 日期/版本 | 博文未给版本 → 补 **0.2.0 public beta**；博文日期未检出 → 标注约 2026-07 下旬 |
| ② 成效数字 | "七千多测试" ✅ ≈7,600；"18 引擎" ✅；"1.5G 磁盘" ✅（250MB 模型 + 0.5–1GB 浏览器）；"Firecrawl 一月一千页" ⚠️ 单源 |
| ③ 口径对照 | "作者一人维护" → 个人维护者 Towhid Khan + 赞助商 TestMu AI；"不要 key" → 核心六工具 keyless，成文报告需可选 LLM（可本地 Ollama） |
| ④ 引文核对 | 博文转述官方四工具对比与 README 原文一致，无歪曲；作者观点（省钱/爬取强项/数据不出机器）均与官方定位相容 |

## 时效性边界（stale_after: 2026-12-02）

以下内容变化快，3 个月后需复核：

- 版本号与测试规模（0.2.0 / ~7,600 tests）
- 十工具清单与引擎适配器数量（18）
- 一键接线客户端矩阵（9 个）与框架集成包
- Firecrawl/Tavily/Exa 等竞品的定价与额度政策
- linux-arm64 语义功能支持状态（官方标注 tracked for a future release）
