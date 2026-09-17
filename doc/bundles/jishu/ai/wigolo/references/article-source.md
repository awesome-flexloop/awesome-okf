---
okf_version: "0.2"
type: Reference
title: "wigolo 博文事实清单（信源登记）"
description: "微信公众号博文《零API Key、零费用》的 F 编号事实双份登记与官方核验状态（F-001~F-055）"
tags: [wigolo, article-source, fact-registry, blog-article]
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-09-16T20:45:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: github-repo
    url: https://github.com/KnockOutEZ/wigolo
  - id: github-api
    url: https://api.github.com/repos/KnockOutEZ/wigolo
---

# 博文事实清单（article-source）

> 本文件是 F 编号事实的双份登记之一（另一份在 spec `facts.md`，两集合正则比对一致：F-001~F-055 连续无跳号）。
> 类型：O=客观事实，V=作者观点/体验，S=厂商自述。核验：✅ 官方一致 ｜ ⚠️ 口径/时效差异（详见 [verification.md](verification.md)）｜ ➖ 无需外部核验。
> 博文：公众号「GHub开源甄选」作者小涛，2026-09-15 07:01 发布，3246 字。F-001~F-033 出自博文，F-034~F-055 为 2026-09-16 官方核验补充。

## A. 博文元信息（F-001 ~ F-003）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 博文标题《零API Key、零费用！这个GitHub开源神器让AI Agent彻底告别"搜索付费焦虑"》 | ➖ |
| F-002 | O | 公众号「GHub开源甄选」/作者「小涛」/2026-09-15 07:01/原创/广东/3246 字 | ➖ |
| F-003 | O | 推介项目 wigolo，仓库 https://github.com/KnockOutEZ/wigolo | ✅ F-034 |

## B. 项目身份与热度（F-004 ~ F-006）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-004 | O | 定位：AI Agent 的「本地搜索引擎」「本地优先 Web 情报层」，经 MCP 协议调用 | ✅ F-036 |
| F-005 | O | 「四月份开源」「三千多颗 Star」「GitHub Trending 挂了好几天」 | 月份✅ F-034；Star⚠️ F-035；Trending⚠️ F-053 |
| F-006 | O | 作者 KnockOutEZ，许可证 AGPL-3.0，完全开源 | ✅ F-034/F-037 |

## C. 能力与设计（F-007 ~ F-014）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-007 | O | 经 MCP 提供搜索/抓取/爬站/结构化提取/本地缓存/相似查找/深度研究/自动采集/变更监控，共十个工具 | ✅ F-041 |
| F-008 | O | 18 个公共搜索引擎直接适配器；抓取、提取、重排序、嵌入均本地运行 | ✅ F-042 |
| F-009 | O | 仅 research、agent 需写长文总结，建议配免费 Gemini Key；不配则返回原始证据 | ✅ 补正 F-040 |
| F-010 | O | 数据全存 `~/.wigolo/`（查询记录/缓存网页/向量索引）；不主动配 LLM 则无数据外传 | ✅ F-037/F-046 |
| F-011 | S | 转述作者对比测试：Claude 内置搜索/wigolo/Tavily/Exa 四工具同题，均找到答案；wigolo 唯一有逐字摘录+字节级定位+可解释评分，弱结果标 junk | ⚠️ F-044 官方自述演示 |
| F-012 | O | 反爬拦截时标 `blocked_by_challenge`；缓存过期显式告知，不拿旧数据糊弄 | ✅ F-043 |
| F-013 | V | 作者将上述行为归纳为「诚实输出」 | ➖ |
| F-014 | V | 开篇以 Tavily/Exa 付费与重复计费痛点引入（"比咖啡钱还贵"为修辞） | ➖ |

## D. 安装与命令（F-015 ~ F-026）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-015 | O | 前置要求 Node.js 20+（博文提 LTS 已到 22） | ✅ F-038 |
| F-016 | O | `npx wigolo init --agents=claude-code`，自动下载浏览器引擎与本地模型，约 1.5GB | ✅ F-038 |
| F-017 | O | 一键接入 Claude Code/Cursor/Codex/Gemini CLI/VS Code/Windsurf/Zed 等 | ✅ F-039（官方 9 目标，少列 OpenCode/Antigravity） |
| F-018 | O | `npx wigolo doctor` 全绿即就绪；Claude Code 中可直接提问触发带引用搜索 | ✅ F-038/F-054 |
| F-019 | O | `npx wigolo search "local-first AI agent" --limit=3`；返回摘录/来源引擎/评分/失败引擎；缓存命中更快 | ⚠️ F-051 参数名口径 |
| F-020 | O | `wigolo serve` 启动 REST API，默认 127.0.0.1:3333 | ✅ F-049 |
| F-021 | O | curl 调 `POST /v1/search`，body `{"query":...,"max_results":5}`；十工具支持 REST，有 OpenAPI 3.1；VPS/内网配 token | ✅ F-049 |
| F-022 | O | Docker 两命令：`docker run -i --rm -v wigolo-data:/data ghcr.io/knockoutez/wigolo`；HTTP 模式加 `-p 3333:3333 -e WIGOLO_API_TOKEN=... serve --host 0.0.0.0` | ✅ F-046/F-048 |
| F-023 | O | slim 镜像懒加载模型；`:full` 标签预装浏览器引擎启动更快 | slim✅ F-046；:full⚠️ F-047 |
| F-024 | O | `WIGOLO_LLM_PROVIDER=gemini` + `GEMINI_API_KEY`，aistudio.google.com/apikey 免费申请 | ✅ F-050 |
| F-025 | O | 也可配 Anthropic/OpenAI/Groq 或本地 Ollama | ✅ F-050 |
| F-026 | O | 配 LLM 后 research 自动分解问题、并行子查询、抓取来源、合成带引用报告 | ✅ F-041 |

## E. 技巧与评价（F-027 ~ F-033）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-027 | V | 技巧1：传数组 `["a","b","c"]` 并行搜索，多引擎扇出 | ✅ F-042 |
| F-028 | V | 技巧2：重要问题 `search_depth: deep`，默认标准深度，deep 召回率更高 | ✅ F-051 |
| F-029 | V | 技巧3：`include_domains` 锁定官方文档（如 `["nextjs.org"]`）防 SEO 垃圾 | ✅ F-051 |
| F-030 | V | 技巧4：缓存即知识库，离线毫秒级；`wigolo cache` 语义检索=私有搜索引擎 | ✅ F-043/F-054 |
| F-031 | V | 评价：wigolo 务实，解决「免费、私有、高效访问网页」痛点，是「成本最低的接入方式，字面意义零成本」 | ➖（口径见 F-040/F-045） |
| F-032 | O | Public Beta、更新频繁、作者在 X 活跃、可 GitHub issue 反馈 | ✅ F-037/F-053 |
| F-033 | O | 博文笔误记录：「eighteen个搜索引擎」中英混杂、「guthub地址」拼写错误 | ➖ 正文不沿用 |

## F. 官方核验补充（F-034 ~ F-055，2026-09-16）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-034 | O | GitHub API：仓库真实，id 1208642537，创建 2026-04-12T15:04:11Z，main 分支，TypeScript，owner=User（id 70368615） | ✅ |
| F-035 | O | 时点快照 2026-09-16T01:46Z：Star **5268**、forks 419、open issues 59、subscribers 21；最近 push 2026-09-15 | ✅ 动态数字 |
| F-036 | O | 官方描述："The go-to web for your AI coding agent — local-first search, fetch, crawl & research over MCP. No API keys, no cloud, $0/query. Public beta."；主页 knockoutez.github.io/wigolo；npm 包名 wigolo | ✅ |
| F-037 | O | README 徽章：AGPL-3.0、public beta、Node ≥20、MCP server、npm 已发布、CI 正常 | ✅ |
| F-038 | O | Quickstart：`npx wigolo init` / `init --agents=a,b`；Node ≥20、约 1.5GB、macOS/Linux/Windows；逐组件报告；`--no-warmup` 延迟下载 | ✅ |
| F-039 | O | `--agents` 9 目标：claude-code/cursor/codex/gemini-cli/opencode/vscode/windsurf/zed/antigravity；其他 MCP 客户端注册 `npx -y wigolo` | ✅ |
| F-040 | O | 免 key 为 6 工具：search/fetch/crawl/extract/cache/find-similar；research、agent、`search format=answer` 需 LLM，无 key 返回 raw brief+evidence | ✅ 博文「两个」补正 |
| F-041 | O | 十工具：search/fetch（反爬自动升级无头浏览器）/crawl（BFS/DFS/sitemap/map）/extract（表格/JSON-LD/schema）/cache/find_similar（三路融合）/research/agent（自主采集循环）/diff/watch（变更检测+webhook） | ✅ |
| F-042 | O | search=18 直接适配器+rank fusion+ML 重排序+可解释评分；数组并行、域名限定、时间范围、精确短语、图片结果 | ✅ |
| F-043 | O | 证据结构：excerpt+citation_id+`source_span{start,end}` 字节偏移+`evidence_score{final,semantic,lexical,engine_consensus}`+freshness_signal；弱结果标 junk；失败引擎/陈旧缓存/降级/截断显式标注 | ✅ |
| F-044 | S | README Benchmark（厂商自述）：单个 Claude Fable 5 会话内 WebSearch/wigolo/Tavily/Exa 同题，四者同答案同顶级源；wigolo 唯一字节锚定摘录+评分分解+引擎遥测，2 条弱结果标 junk；口径 July 2026；非独立评测 | ⚠️ 已标性质 |
| F-045 | O | 官方对比表（2026-07）：wigolo 无 key、$0/query；Firecrawl/Exa/Tavily 需 key 计费；字节锚定/评分分解/持久本地记忆/数据留本机四项仅 wigolo ✅ | ✅ |
| F-046 | O | 镜像 `ghcr.io/knockoutez/wigolo` 为 slim，引擎与模型首次使用下载至 `/data` 卷；stdio 命令与博文逐字一致；卷持久化缓存/模型/引擎/加密密钥 | ✅ |
| F-047 | O | `full` 官方文档确认是 Dockerfile 构建目标（`docker build --target full -t wigolo:full .`）；未确认 ghcr 发布 `:full` 预构建标签 | ⚠️ |
| F-048 | O | 非回环绑定 fail-closed：无 `WIGOLO_API_TOKEN`（或未 `--allow-unauthenticated`）拒绝启动；官方提供 compose.serve.yml | ✅ |
| F-049 | O | REST：默认 127.0.0.1:3333；`POST /v1/{tool}` 覆盖 10 工具；`GET /openapi.json`=OpenAPI 3.1；同端口 `/mcp`、`/sse`；serve 参数 `[--port][--host][--allow-unauthenticated]` | ✅ |
| F-050 | O | LLM：`WIGOLO_LLM_PROVIDER=gemini`+`GEMINI_API_KEY`（AI Studio 免费层）；支持 anthropic/openai/groq/ollama/OpenAI 兼容端点；密钥另可统一走 `WIGOLO_LLM_API_KEY`，不读 flag | ✅ |
| F-051 | O | CLI 参数口径：headless search 用 `--max-results`/`--include-domains`/`--search-depth` 等；`wigolo shell` 内别名为 `--limit`/`--domains` | ⚠️ 博文 --limit 口径差异 |
| F-052 | O | 两套 SDK：TypeScript `npm i wigolo-sdk`（零依赖，local 模式自动复用/拉起 daemon）；Python `pip install wigolo`（仅标准库，同步+异步） | ✅ |
| F-053 | O | 作者 KnockOutEZ；X @yourtowhid；邮箱 ktowhid201@gmail.com；Discord 社区；Trendshift #79424（与 GitHub Trending 不同产品，博文 Trending 说法无法直接证实） | ⚠️ |
| F-054 | O | 其他命令：`doctor --fix`、`verify` 真实网络冒烟、`config --uninstall`（留 ~/.wigolo，彻底删需 rm -rf）、`shell` NDJSON REPL；watch 仅 daemon/MCP 会话存活时运行 | ✅ |
| F-055 | O | 赞助商 TestMu AI（原 LambdaTest）；声明保持免费接受赞助；Homebrew/单文件二进制/install.sh 有源码但制品未发布 | ✅ |

## 双份一致性核对

- 本文件 F 编号集合 = spec `facts.md` 集合 = {F-001 … F-055}，连续无跳号
- V 阶段补充事实：无（所有核验事实在 R 阶段一次性登记，双份回转完成）
