---
type: reference
title: ScholarClaw 架构洞察
tags: [scholarclaw, academic-search, skill, insights]
sources:
  - id: scholarclaw-vendor
    resource: vendor/netease-youdao/ScholarClaw/
    title: ScholarClaw 源码（vendor 子模块，基线 commit 97bdb5e）
---

# ScholarClaw 架构洞察

> I 阶段分析。基于 R 阶段 64 条事实（F-sc-001~F-sc-064）。
> 分析日期：2026-09-09

---

## 洞察一：TypeScript 客户端 + Shell 脚本双调用面——同一后端 API 的两套"薄壳"

**陈述**：ScholarClaw 本身不实现任何搜索逻辑，它是远端 SaaS（`https://scholarclaw.youdao.com`）的纯客户端封装，且为同一组后端 API 提供了两套平行调用面。第一套是 TypeScript 客户端 `ScholarClawClient`（`server/index.ts`）：约 20 个方法覆盖全部 HTTP 路由（健康检查、通用搜索、学术搜索、引用、OpenAlex、博客、基准测试、推荐共 9 组），除 `submitBlog` 外全部走统一 `request()` 通道，JSON 编码。第二套是 shell 脚本层（`scripts/` 下 16 个 `.sh` = 1 个公共库 `common.sh` + 15 个功能脚本，根目录另有 `package.sh`/`install.sh`），用 curl 直调同一组路由；`package.json` 再以 14 个 npm scripts 别名和 `lobsterai` 元数据块（14 个 `supportedCommands`）把 shell 层桥接进宿主工具的命令生态。三套"入口"（TS 方法 / shell 脚本 / npm 命令）最终汇聚到同一个远端服务。

**证据**：
- F-sc-008：导出 `ScholarClawClient` 类与默认实例，类内方法经统一 `request()` 发出 HTTP 调用（`submitBlog` 除外）
- F-sc-009~F-sc-019：TS 侧 9 组共 20 个方法的路由清单（`/health`、`/search`、`/scholar/search`、`/citations`、`/openalex/*`、`/api/blog/*`、`/api/benchmark/*`、`/api/recommend/*`）
- F-sc-029：shell 侧 16 个 `.sh` 文件（`common.sh` + 15 个功能脚本）
- F-sc-058：14 个 npm scripts 别名对应各 shell 脚本功能
- F-sc-059：`lobsterai` 元数据块（skillType=`api`、14 个 supportedCommands、defaultServerUrl）
- F-sc-015 vs F-sc-035：同一 `/api/blog/submit` 接口，TS 侧用 `URLSearchParams` 表单编码，shell 侧用 curl `-F` multipart 表单——两套调用面连编码方式都不一致

**反常识**：常见预期是"TS 客户端是给程序用的，shell 脚本是人调试用"——但本项目 shell 层并非调试副产品，而是**主交付物**：`install.sh` 把 shell 脚本安装为 `sc-*` 系统别名、`SKILL.md` 教 LLM 调用的也是 shell 命令、`package.json` 的 `main` 直接指向 `.ts` 源文件而 dependencies 为空（F-sc-057）——TS 侧甚至不被构建运行（`tsconfig.json` 声明了 `outDir: ./dist` 但无构建脚本配合）。换句话说，这是一份"以 Markdown 契约 + shell 脚本为主体、TS 类型为辅助参考"的 skill 包，而非传统意义的 SDK。另一个反常识是两套调用面在细节处各自为政：URL 编码在 `search.sh` 是自实现函数、在 `openalex_*.sh` 改用 `jq -sRr @uri`（F-sc-031 vs F-sc-034），博客提交的表单编码两法并存（F-sc-015、F-sc-035），没有任何一处强制统一。

**行动**：
- 集成时先选边：LLM/智能体场景走 SKILL.md 契约调 shell 命令；需要类型安全的程序化调用可参考 TS 客户端的路由与类型定义，但需自行承担"该层未经构建验证"的风险。
- 直接对接后端 API 时，以 TS 客户端（`server/index.ts` + `server/types.ts`）为路由与参数契约的权威参照，以 shell 脚本验证实际可用的最小参数集。
- 提交含特殊字符的查询时注意两套编码实现差异；绕过封装直接 curl 时，参照 `openalex_*.sh` 的 `jq -sRr @uri` 方案最稳妥。
- 判断某个功能"是否存在"时，shell 脚本集是更全的清单（`blog.sh` 同步封装、`health.sh` 简易模式均不在 supportedCommands 中，见 F-sc-064）。

---

## 洞察二：SKILL.md 是 LLM 技能契约——时序与容错参数写在 Markdown 里而非代码里

**陈述**：`SKILL.md`（frontmatter：`name: scholarclaw`、`version: 1.4.1`、`official: false`）在本项目中承担的不是 README 式说明，而是**面向 LLM 的运行时契约**：①触发条件——学术场景（论文检索、文献调研、学术问答）下应使用本 skill 替代 web-search；②性能预期——分场景响应时间期望表，约束 LLM 的等待与降级决策；③SSE 事件契约——流式响应中仅提取 `final_response` 与 `response_chunk` 两类事件，忽略 `session_start`、`tool_call_*`；④博客异步三步法——「提交→轮询任务状态→获取结果」，轮询间隔 10–15 秒、最多 40 次（即最坏约 10 分钟）；⑤重试策略——HTTP 503/504 按 2s、4s、8s 指数退避、最多 3 次，HTTP 400/404 不重试。这五条共同构成一个"无 SDK 的 API 使用协议"：任何遵循该文档的 LLM 客户端都能正确驱动远端服务。

**证据**：
- F-sc-043~F-sc-045：SKILL.md 元数据（1.4.1、official: false）、触发条件、响应时间期望表
- F-sc-046：SSE 流仅提取 `final_response`/`response_chunk`，忽略 `session_start`、`tool_call_*`
- F-sc-047：博客三步法，轮询 10–15s × 最多 40 次
- F-sc-048：503/504 按 2/4/8s 退避最多 3 次；400/404 不重试
- F-sc-050：配置优先级声明（环境变量 > OpenClaw 配置 > 配置文件 > 默认值）
- F-sc-037 vs F-sc-047：`blog.sh` 实现的轮询节奏为 `POLL_INTERVAL=5` 秒、总超时 600 秒——与 SKILL.md 的 10–15s×40 轮约定不同

**反常识**：一般认知里"重试退避、轮询节奏"是代码实现细节，文档只写能力清单。ScholarClaw 反其道而行——**这些时序参数只存在于 Markdown 契约中，代码实现（`blog.sh`）用的是另一套值（5s 间隔、600s 超时）**。这不是疏漏，而是揭示了该项目的真实架构：SKILL.md 面向"下一代调用方"（LLM），shell 脚本面向"上一代调用方"（人类/CI），两代调用方允许各自演进，契约层才是 skill 的长期稳定面。另一个反常识是 SSE 过滤策略的"少即是多"：不显式处理 `session_start`/`tool_call_*` 不是功能缺失，而是刻意约定——LLM 只需消费两类事件即可完成 SOTA 对话，其余事件留给需要过程可视化的场景（`benchmark_chat.sh -s` 的 SSE 模式则原样透传，见 F-sc-038）。

**行动**：
- 自研 LLM 客户端时，以 SKILL.md 的时序参数为准（10–15s×40 轮、2/4/8s 退避），不要照抄 `blog.sh` 的 5s 常量；两者冲突时契约层优先。
- 把重试语义实现为可配置策略对象（retryable=[503,504]、backoff=[2,4,8]、max=3、non_retryable=[400,404]），而非散落的状态码 if-else，便于与服务端演进解耦。
- SSE 消费端只解析 `final_response`/`response_chunk` 两类事件名，其余事件记录后丢弃；不要因出现未知事件而中断解析。
- 触发条件声明（学术场景替代 web-search）意味着该 skill 预期被宿主 Agent 的 skill 路由机制加载——评估其效果时应放在 Agent 的 skill 选择链路中，而非孤立测试单条命令。

---

## 洞察三：curl + jq 的零依赖极简主义——复杂度全部外推给远端 SaaS

**陈述**：整个项目运行时依赖仅两项：`curl`（必需）与 `jq`（可选），`package.json` 的 dependencies 为空，devDependencies 只有 `@types/node` 与 `typescript`（F-sc-051、F-sc-057）。公共库 `common.sh` 统一了全部 shell 脚本的调用模式：curl `-s -w "\n%{http_code}"`（输出体与状态码一并捕获）、`handle_http_error` 错误处理、检测到 `jq` 时以 `jq .` 美化输出；配置取值优先级为环境变量 > 配置文件 > 默认值（`get_api_key`/`get_server_url`）。安装由 `install.sh` 完成：落盘到 `~/.scholarclaw`、生成 `scholarclaw.env`、写入 `sc-*` 命令别名并分发快速启动脚本；分发则由 `package.sh` 构建 `dist/` 并产出 tar.gz/zip 及 sha256 校验文件。搜索、重排、引用扩展、博客生成、基准评测等全部计算都发生在远端 `scholarclaw.youdao.com`，本地无任何缓存与状态。

**证据**：
- F-sc-030：`common.sh` 的 `init_config`、取值优先级、curl 统一模式、`handle_http_error`、jq 美化
- F-sc-051：Dependencies 声明 curl 必需、jq 可选
- F-sc-057：dependencies 为空，engines 要求 node>=16
- F-sc-042：`install.sh` 安装至 `~/.scholarclaw`、生成 `scholarclaw.env` 与 `sc-*` 别名
- F-sc-041：`package.sh` 构建 dist/ 与归档 + sha256 校验
- F-sc-032、F-sc-040：scholar.sh curl `--max-time 60`、health.sh `--max-time 10`——超时约束也全部写在脚本常量中

**反常识**：名为"AI 学术搜索"的项目，本地仓库里**没有任何模型、索引、检索逻辑甚至 npm 运行时依赖**——它薄到可以在任何装了 curl 的裸环境运行。这与"AI 应用 = 重依赖 + GPU"的直觉相反，其架构前提是把全部智能放在服务端 SaaS，客户端只负责协议适配。这带来一个易被忽视的成本转移：可用性、速率限制、数据出境完全绑定有道服务端（apiKey 经 `~/.scholarclaw/config.json` 或环境变量注入，F-sc-002、F-sc-003），离线/内网环境无法通过本地部署兜底。同时 jq"可选"意味着**输出格式不稳定**——有 jq 时是美化 JSON，无 jq 时是原始紧凑 JSON，下游做脚本化解析时不能假设格式。

**行动**：
- 内网/离线部署评估：本项目无法满足，需自建兼容后端或改用本地检索方案；选型时把"服务端可用性 SLA"纳入风险清单。
- 编写自动化流水线消费脚本输出时，显式检查 `jq` 是否存在并统一用 `jq -c` 归一化，不要直接 diff 原始输出。
- 故障排查顺序：先用 `sc-health`（10s 超时，`-v` 追加详细检查）区分网络/服务端问题，再查 apiKey 配置（401/403/429 判定见 F-sc-020）。
- 长耗时操作（scholar 搜索 60s、博客轮询最长 600s）在 CI 中需显式放宽步骤超时，脚本内常量即是预期的上限参考。

---

## 洞察四：源码间不一致是"快速演进 + 防御性兼容"的信号——以运行时行为为准，不以类型枚举为准

**陈述**：基线 commit 中存在三处源码间不一致：①引擎清单——README 引擎表含 `openalex` 不含 `cache`，而 `config.ts` 的 `SEARCH_ENGINES` 含 `CACHE` 不含 `openalex`（OpenAlex 实际由独立 `/openalex/*` 路由承载）；②博客状态枚举——`types.ts`/`config.ts` 声明 `pending/running/completed/failed` 四值，而 `blog.sh` 的状态匹配分支与 SKILL.md 状态示例中出现 `processing`、`queued`、`success`；③命令清单——`package.json` 的 14 个 `supportedCommands` 不含 `blog.sh` 同步封装，但 `install.sh` 生成的 `sc-blog` 别名却指向它。三处差异的共同模式是：**类型层（文档/枚举/元数据）滞后或超前于实现层，而实现层做了超集兼容**。

**证据**：
- F-sc-062：README 引擎表 vs `config.ts` SEARCH_ENGINES 清单不一致
- F-sc-063：状态枚举（4 值）vs `blog.sh`/`SKILL.md` 实际取值（含 `processing`/`queued`/`success`）
- F-sc-064：supportedCommands 不含 `blog.sh` vs `sc-blog` 别名指向 `blog.sh`
- F-sc-037：`blog.sh` 状态分支为 `completed|success`、`failed|error`、`pending|running|processing|queued` 三组并集匹配
- F-sc-007：`BLOG_STATUSES`/`BENCHMARK_STATUSES` 均只有四值

**反常识**：直觉上"代码与文档不一致 = 质量缺陷"，但此处的不一致呈现方向性规律：实现层（`blog.sh`）的匹配集合是类型层（`BLOG_STATUSES`）的**超集**，说明服务端实际返回的状态值超出客户端类型声明，实现者选择以运行时行为为准、枚举仅作参考。这是快速迭代中 SaaS 服务端先行、客户端分层跟进的典型痕迹——README 面向用户宣传最新能力（openalex），`config.ts` 常量残留旧引擎（CACHE），`blog.sh` 分支兼容服务端实际返回。若按"枚举即全部合法值"的静态思维编程，会在 `processing`/`queued` 状态上误判任务失败。

**行动**：
- 状态轮询判断使用分组/前缀匹配（完成组、失败组、进行中组），禁止对状态字段做精确等值比较；新增服务端状态时只需扩展分组，不影响主流程。
- 引擎参数做入参白名单校验时，以服务端报错为准回退，不要硬编码 `SEARCH_ENGINES` 作为唯一合法集。
- 升级 ScholarClaw 版本时，重点 diff 三处易漂移面：`config.ts` 常量表、SKILL.md 时序参数、`package.json` 的 lobsterai 元数据。
- 撰写下游文档引用引擎/状态清单时，交叉核对 README 与 `config.ts` 两处并标注差异，以事实清单存疑节（F-sc-062~F-sc-064）为准。

---

## 知识地图

### 概念文档规划

ScholarClaw 体量小（服务端 3 个 TS 文件 + 16 个 shell 脚本 + 1 份 SKILL.md），规划 5 篇概念文档，由入门到高级：

| 编号 | 文件名 | 标题 | 一句话概要 | 前置依赖 | 引用事实编号区间 |
|------|--------|------|-----------|---------|-----------------|
| 00 | 00-overview.md | ScholarClaw 项目概览与定位 | 零依赖学术搜索 skill 包的定位、双层调用面总览、配置体系与安装方式 | 无 | F-sc-001~F-sc-007, F-sc-041~F-sc-042, F-sc-043~F-sc-045, F-sc-050~F-sc-051, F-sc-057~F-sc-061 |
| 01 | 01-server-client.md | TypeScript 客户端与 HTTP 路由 | `ScholarClawClient` 的 20 个方法、9 组路由、统一 request 通道与类型体系 | 00 | F-sc-008~F-sc-028 |
| 02 | 02-shell-toolchain.md | Shell 脚本工具链与命令体系 | `common.sh` 公共库、15 个功能脚本、install/package 与 npm 别名桥接 | 00 | F-sc-029~F-sc-040, F-sc-058~F-sc-059 |
| 03 | 03-skill-contract.md | SKILL.md 技能契约与调用时序 | LLM 面向的五重契约：触发条件、SSE 事件、博客三步法、重试退避、配置优先级 | 00, 02 | F-sc-046~F-sc-051, F-sc-052~F-sc-056 |
| 04 | 04-evolution-inconsistency.md | 源码不一致与防御性兼容模式 | 引擎表、状态枚举、命令清单三处不一致的登记与"以运行时为准"的解读 | 01, 02, 03 | F-sc-005, F-sc-007, F-sc-037, F-sc-062~F-sc-064 |

### 学习路径

1. **入门（理解是什么）**：00
   - 建立全局视图：这是远端 SaaS 的薄客户端 skill 包，零本地依赖，配置落盘 `~/.scholarclaw`。
2. **核心（理解怎么工作）**：01 → 02
   - 先掌握 TS 客户端的路由与类型契约（API 面的权威参照），再落到 shell 脚本层的实际调用模式与安装体系。
3. **进阶（理解怎么用、怎么防坑）**：03 → 04
   - 理解 SKILL.md 的 LLM 时序契约（轮询/退避/SSE 过滤），最后以三处源码不一致为案例，建立"枚举参考、运行时为准"的防御性集成思维。
