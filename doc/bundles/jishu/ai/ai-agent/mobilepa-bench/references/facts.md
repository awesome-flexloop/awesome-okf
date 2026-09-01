---
type: Reference
title: "MobilePA-Bench 与 Qwen-UI-Agent 网站事实台账"
description: "mobilepa-bench 束唯一事实依据：MobilePA-Bench 事实 F-001~F-032（沿用 R 阶段原编号）+ Qwen-UI-Agent 网站仓事实 WEB-A-01~WEB-A-24（改编号并标注 facts-websites.md 原编号）。"
tags: [MobilePA-Bench, Qwen-UI-Agent, 事实台账, 信源, 基准评测]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
---

# 事实台账（Facts）

> **台账说明**：本文件由两份 R 阶段事实清单适配合并而成，是本束全部 concepts 文档的唯一事实依据。concepts 中出现的任何数字、URL、API/字段名引用都必须能在本文件找到对应编号。
>
> - **A 部分**：MobilePA-Bench（F-001 ~ F-032），沿用 `facts-mobilepa-bench.md` 原编号。信源根：`external/libs/tools/Tongyi-MAI/MobilePA-Bench`。
> - **B 部分**：Qwen-UI-Agent 网站仓（WEB-A-01 ~ WEB-A-24），为避免与 A 部分 F 编号冲突改用 WEB-A 前缀，每条标注 `facts-websites.md` A 部分原编号。信源根：`external/libs/tools/Tongyi-MAI/Qwen-UI-Agent`。

---

## A 部分：MobilePA-Bench（F-001 ~ F-032）

### F-001 仓库为基准的项目页/Paper 资产，非实现代码仓
- 位置: README.md（L39）；仓库根目录文件清单
- 内容: README「News」原文记载："2026-08-25: The project repository was opened with an interactive project page, leaderboard, and a private-evaluation link"。仓库根目录经全量核查仅含 `README.md`、`LICENSE`、`.gitignore`、`github-pages/`（纯静态站点）与 `.github/`（CI 脚本与 workflow），不存在任何基准任务数据、评测 harness、模型或智能体实现代码目录；基准本体以 arXiv 论文（arXiv:2608.23035）形式发布。

### F-002 基准一句话定义
- 位置: README.md（L21）
- 内容: 原文定义："MobilePA-Bench is an interactive, stateful, and tool-centric benchmark for evaluating the tool-calling and planning capabilities of mobile planner agents. It moves beyond static function matching by executing agent actions in a mutable mobile environment and checking both the action trace and the resulting state."

### F-003 Highlights 五条要点
- 位置: README.md（L29-35）
- 内容: 逐条字面要点：①Executable and stateful（应用数据、权限与设备状态随每次动作演化）；②Broad mobile coverage（1,705 任务、212 工具、13 域、89 子类）；③Four capability dimensions（Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration）；④Evidence-based evaluation（固定策略验证工具选择、落地参数、执行顺序、最终环境状态与智能体行为）；⑤Realistic failure modes（工具依赖、权限边界、冲突请求、运行时错误、不完整用户上下文）。

### F-004 规模数字（README 与页面一致）
- 位置: README.md（L32）；github-pages/index.html（L237-238）
- 内容: 1,705 个评估任务、212 个 realistic tools、13 个 functional domains、89 个子类别（level-2 subcategories）。README 与站点 Benchmark Statistics 副标题数字一致。

### F-005 四能力维度定义表
- 位置: README.md（L52-59）
- 内容: 表格四行字面定义——Tool Use: "Grounded tool selection, argument construction, ordered execution, recovery, and safe refusal"；Memory: "Retrieval and application of user profiles, preferences, routines, history, and situational context"；Skills: "Selection and execution of reusable composite procedures instead of rebuilding every workflow from scratch"；Sub-agent: "Task decomposition, contextual handoff, and coordination with GUI, search, image, and other specialized agents"。每行附站点锚点链接（#tool-use-examples / #memory-examples / #skill-examples / #sub-agent-examples）。

### F-006 News 时间线
- 位置: README.md（L37-40）
- 内容: 2026-08-24 论文上 arXiv（arxiv.org/abs/2608.23035）；2026-08-25 项目仓库开放（项目页 + leaderboard + private-evaluation 链接）。

### F-007 Overview 建模与评测方式描述
- 位置: README.md（L42-46）
- 内容: 原文：移动规划智能体被建模为通过 structured tools、reusable skills、persistent memory 和 specialized sub-agents 进行操作的决策器；环境执行每个动作、更新状态并返回观察或运行时错误。评测器为每个任务分配固定验证策略（fixed verification policy），成功可要求 "an exact tool call, a target state transition, a prescribed action order, or a valid collaboration pattern"。

### F-008 Private Evaluation 提交要求
- 位置: README.md（L62-64）
- 内容: 面向 hosted mobile planner agents 的保密评测通道：提交 HTTPS、OpenAI-compatible、支持 tool-calling 的 endpoint，将在 Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration 四维评测。入口为 secure submission portal（116.62.42.171/login?next=/submit）。

### F-009 Private Evaluation 四条特性
- 位置: README.md（L66-69）
- 内容: 字面四条——①Confidential by design（提交直达专用评测服务器，API 凭据不经 GitHub Pages）；②Hidden-test integrity（基准查询、ground truth、judge 凭据与被测模型隔离）；③Reviewed results（每次运行在发布前经人工检查）；④Expected turnaround（通常 3 个工作日内返回报告，每账户每 7 天允许 1 次请求）。

### F-010 评测服务 URL 由 site_config.js 统一注入
- 位置: github-pages/static/js/site_config.js（L4-10）
- 内容: `evaluationServiceUrl = "https://116.62.42.171"`，挂载到 `window.MobilePABenchConfig`；脚本遍历所有带 `data-evaluation-path` 属性的链接，把 href 改写为服务地址 + path。index.html 中 Evaluation login 按钮即带 `data-evaluation-path="/login"`（L29-30）、私有评测按钮带 `/login?next=/submit`（L71-72）。

### F-011 leaderboard 数据文件头部注释声明版本与权重公式
- 位置: github-pages/static/js/leaderboard_data.js（L1-3）
- 内容: 原文注释："// MobilePA-Bench v1.5 leaderboard data (from paper_v5 Table 1, tab:main_results)"、"// Overall = 0.5*Tool + 0.2*Memory + 0.2*Skills + 0.1*SubAgent"、"// info: org used only for optional grouping/badges"。

### F-012 leaderboard 收录 13 个模型及分数
- 位置: github-pages/static/js/leaderboard_data.js（L4-18）
- 内容: `LEADERBOARD_DATA` 数组 13 条，每条字段 model/org/overall/basic/subagent/memory/skills/costPer1k。前三名：Claude-Opus-5（Anthropic，overall 75.52，basic 83.85）、Claude-Fable-5（Anthropic，75.31）、Kimi-K3（Moonshot，73.01）；其后为 Qwen-3.8-Max（Alibaba，72.51）、Gemini-3.6-Flash（Google，71.21）、Gemini-3.1-Pro（71.18）、GLM-5.2（Zhipu，67.71）、Claude-Opus-4.8（65.52）、Qwen-3.7-Max（64.71）、Seed-2.1-Pro（ByteDance，63.65）、GPT-5.6-Sol（OpenAI，62.68）、GPT-5.5（61.44）、Kimi-2.6（55.63）。列名 basic 对应 Tool Use 维度。

### F-013 页面 Overall 权重表述
- 位置: github-pages/index.html（L107-109）
- 内容: Leaderboard 章节副标题原文："Overall = 50% Tool Use + 20% Memory + 20% Skills + 10% Sub-agent."；"Best value per column is highlighted"。

### F-014 Cost/1K 口径说明
- 位置: github-pages/index.html（L112-115）
- 内容: 原文："All capability values are percentages (%). Overall is reported only for models with complete coverage of all four dimensions."；"Cost/1K Tasks is estimated from visible output tokens only; input, cached, and hidden reasoning tokens are excluded."

### F-015 页面章节结构（6 个锚点 section + 1 个评测入口横幅）
- 位置: github-pages/index.html（L18-33、57、84、104、120、199、231、289）
- 内容: 粘性导航链接依次为 #intro（Introduction）、#leaderboard（Leaderboard）、#demo（Demo）、#cases（Task Examples）、#benchmark（Benchmark）、#citation（Citation）与外部 Evaluation login；另有不带锚点的 evaluation-entry section（"Confidential evaluation for hosted models"）。hero 区作者署名 "MAI Team, Alibaba Token Hub, Alibaba Group"（L44）。

### F-016 Task Examples 四个维度锚点
- 位置: github-pages/index.html（L206-223）
- 内容: 四个 case tab 按钮分别携带 `data-anchor` 属性：basic→tool-use-examples、memory→memory-examples、skills→skill-examples、subagent→sub-agent-examples，各标 "3" 个案例计数。

### F-017 Benchmark Statistics 六项统计
- 位置: github-pages/index.html（L236-246）
- 内容: 六个 pill：1,705 Evaluation Tasks；212 Realistic Tools；13 Functional Domains；89 Subcategories；N=15 Candidate Recall；T=15 Max Steps。

### F-018 四维度任务分布
- 位置: github-pages/index.html（L248-256）
- 内容: Tasks per capability dimension：Tool Use 1,040；Memory Usage 376；Skill Usage 200；Sub-agent Collaboration 89（四项合计 1,705）。

### F-019 13 个工具域及工具数
- 位置: github-pages/index.html（L265-282）
- 内容: 域-工具数表：Audio & Entertainment 25；Apps & Storage 23；Display & Sound 22；System Settings 22；Time Management 16；AI Assistant 16；Calls & Communication 15；Network & Connectivity 14；Travel & Lifestyle 13；Devices & Cross-device 13；Input & Interaction 12；Utilities & Productivity 11；Security & Privacy 10。

### F-020 案例数据按四维度组织，每维 3 案例
- 位置: github-pages/static/js/case_studies_data.js（L1-2 及全文）
- 内容: 文件头注释 "// Representative task traces across the four MobilePA-Bench capability dimensions."；`window.TASK_EXAMPLES_DATA.dimensions` 含 basic（title "Tool Use"）、memory（"Memory Usage"）、skills（"Skill Usage"）、subagent（"Sub-agent Collaboration"）四键，每键 cases 数组 3 条，每条含 id/title/query/checker/subtype/interactions/finalResponse 字段。

### F-021 验证策略 checker 类型字面量
- 位置: github-pages/static/js/case_studies_data.js（全文 Grep "checker"）
- 内容: 出现的 checker 字面量：Strict tool + arguments；Behavior judge；Final DB state；DB state + retrieval；Behavior judge + retrieval；Skill routing + execution。Tool Use 维度 3 案例分别对应三种 checker；Memory 维度案例用 DB state + retrieval / Behavior judge + retrieval；Skills 维度 3 案例均为 Skill routing + execution；Sub-agent 维度 3 案例均为 Behavior judge。

### F-022 案例 subtype 与代表案例
- 位置: github-pages/static/js/case_studies_data.js（L9-51、26-35、55-100）
- 内容: Tool Use 案例含 BTU-204（"Payment sequence under real state changes"，subtype Ordered execution，interactions 依次调用 control_flashlight/open_app/manage_nfc）、BTU-622（"Conflicting network goals"，subtype Conflict intent，模型判定关流量与 4K 流播冲突后反问用户）、BTU-863（subtype Compound state change，dark mode + repeat one + 30 分钟倒计时三连调用）。Memory 案例含 MEM-0043（subtype Memory update，把睡前单词 App 从 Anki 改为 Quizlet）、MEM-0054（Multi-memory composition）、MEM-MT0421（Multi-turn memory，Bluetooth 发送会议纪要到 MacBook Pro）。

### F-023 交互式 replay 演示的场景与 policy 字面量
- 位置: github-pages/static/js/replay_demo_data.js（L4-69）；github-pages/index.html（L120-196）
- 内容: `window.MobilePAReplayScenarios` 场景含 id "tool"（tab "Exact Tool Call"，policy "tool_acc"，policyLabel "Exact tool + arguments"，示例为 manage_alarm 创建 7:30 Morning run 闹钟，checks 列 Tool name/Argument fields/Grounded values）与 id "state"（tab "Stateful Completion"，policy "task_db_acc"，policyLabel "Final environment state"，示例为杭州周六行程计划，capabilities 标注 basic/memory/skills 三维）。Demo 区三栏分别为 Interaction（User & Agent）、Execution trace（Planner & Environment）、Fixed policy（Evidence Checker），底部注明 "Illustrative public examples; hidden evaluation tasks and ground truth remain private."（L194）。

### F-024 静态站依赖全部本地化，不依赖外部 CDN
- 位置: github-pages/index.html（L9-14）；github-pages/static/vendor/ 目录
- 内容: HTML 注释原文 "Local UI dependencies keep the static site independent of external CDNs."；vendor 目录含 bulma.min.css、fontawesome（css/all.min.css + webfonts）、tabulator.min.js/css、jquery.min.js；页面样式版本号带查询串（style.css?v=compact-intro-20260819、replay-demo.css?v=20260817-icons）。github-pages/ 根有 `.nojekyll` 文件。

### F-025 leaderboard 截图由 Playwright 脚本自动生成
- 位置: .github/scripts/capture-leaderboard.mjs（全文）
- 内容: 脚本用 `playwright` 的 `chromium.launch({ headless: true })` 打开 `http://127.0.0.1:4180/#leaderboard`（viewport 1440x1000，deviceScaleFactor 1），等待 `#leaderboard > .inner` 可见，隐藏 nav 元素后对该区块截图保存为 `github-pages/static/images/leaderboard.jpg`（jpeg quality 92，animations disabled）。该截图即 README 顶部展示图。

### F-026 GitHub Pages 部署 workflow
- 位置: .github/workflows/deploy-pages.yml（全文）
- 内容: workflow 名 "Deploy public benchmark site"，push 到 main 且 paths 命中 `github-pages/**` 或 workflow 本身时触发，另有 workflow_dispatch；permissions 为 contents: read / pages: write / id-token: write；concurrency group "pages"（cancel-in-progress）；部署步骤为 checkout@v4 → configure-pages@v5 → upload-pages-artifact@v3（path: github-pages）→ deploy-pages@v4。无构建步骤，直接上传静态目录。

### F-027 存在第二个 leaderboard 预览更新 workflow
- 位置: .github/workflows/update-leaderboard-preview.yml
- 内容: `.github/workflows/` 下除 deploy-pages.yml 外还存在 `update-leaderboard-preview.yml` 文件（R 阶段未展开细读其内容，仅登记存在性）。

### F-028 README 引用的论文 BibTeX
- 位置: README.md（L71-85）
- 内容: citation key `zhu2026mobilepabench`，标题 "MobilePA-Bench: Benchmarking Mobile Planner Agents on Complex Real-World Tasks"，作者 Zhu, Yi; Wu, Xiongwei; Wang, Qiyi; Qu, Tingyu; Liu, Jiajun; Cao, Sihan; Chen, Long; Sun, Weigao; Zhu, Feida; Zhong, Yiran; Hoi, Steven，journal 为 arXiv preprint arXiv:2608.23035，year 2026，primaryClass cs.AI。

### F-029 页面内 Citation 与 footer
- 位置: github-pages/index.html（L288-303）
- 内容: #citation 章节提供简化版 BibTeX（key `mobilepabench2026`，author "MAI Team, Alibaba Token Hub, Alibaba Group"）。footer 原文 "© 2026 MobilePA-Bench · MAI Team, Alibaba Token Hub, Alibaba Group. Page template inspired by Video-MME"（附 video-mme.github.io 链接）。

### F-030 许可证
- 位置: README.md（L91-93）；LICENSE
- 内容: "Unless otherwise noted, this repository is licensed under the Apache License 2.0"；根目录存在 LICENSE 文件，README 徽章亦标注 License Apache 2.0。

### F-031 Introduction 章节的定位论述
- 位置: github-pages/index.html（L84-101）
- 内容: 原文论述现有评测的缺口："static function-calling benchmarks rarely execute predicted calls against a persistent environment, while GUI-centric benchmarks underrepresent efficient structured APIs, personalized context, reusable procedures, and coordination with specialized agents"；MobilePA-Bench 以 interactive、stateful、tool-centric sandbox 补足，并重申 1,705 tasks / 212 tools / 13 domains 规模与四能力。

### F-032 Sub-agent 与 Skills 维度案例主题
- 位置: github-pages/static/js/case_studies_data.js（L155-193 附近）
- 内容: Sub-agent Collaboration 维度 summary 原文 "Delegation to specialized agents, recovery from tool boundaries, and transparent fallbacks."；三个案例标题分别为 "Recover into a GUI handoff"、"Keep an automation when media is unavailable"、"Delegate open-domain lookup without fabrication"（checker 均为 Behavior judge）。Skill Usage 维度 summary 为 "Loading reusable skills before executing a safe and complete business-tool plan."，三案例 checker 均为 Skill routing + execution。

---

## B 部分：Qwen-UI-Agent 网站仓（WEB-A-01 ~ WEB-A-24）

### WEB-A-01 仓库为网站源码，非实现代码仓（README 原文引证）
- 原编号: facts-websites.md A 部分 F-001
- 位置: README.md（L3-21）
- 内容: README 顶部 IMPORTANT 块原文："**Website source only — this is not the Qwen-UI-Agent implementation repository.** This repository contains only the source code and static assets for the Qwen-UI-Agent project website ... It does **not** contain the model, training code, or agent implementation."；中文段原文："**本仓库仅为网站源码，并非 Qwen-UI-Agent 的项目实现代码仓。** ... 不包含模型、训练代码或智能体实现代码"。

### WEB-A-02 官方实现代码仓指向 Tongyi-MAI/MAI-UI
- 原编号: facts-websites.md A 部分 F-002
- 位置: README.md（L11-12、20-21）
- 内容: README 明确写 "Looking for the Qwen-UI-Agent code? Visit the official project repository: **Tongyi-MAI/MAI-UI**"（英文/中文两处重复）。网站地址为 https://tongyi-mai.github.io/Qwen-UI-Agent/。

### WEB-A-03 站点定位与主流程
- 原编号: facts-websites.md A 部分 F-003
- 位置: README.md（L23-25、86-87）
- 内容: 原文："This repository powers the bilingual Qwen-UI-Agent technical report website. The site presents real-world capabilities, benchmark results, broader general and agentic capabilities, playable demos, and release materials."；主流程原文 "The primary flow is Capabilities → Performance (including Broader Capabilities) → Demos → Citation."

### WEB-A-04 package.json 包名与脚本
- 原编号: facts-websites.md A 部分 F-004
- 位置: package.json（全文）
- 内容: name `qwen-ui-agent-tech-report`，version 0.1.0，private，`"type": "module"`，engines `node >=22.13.0`。scripts：`dev`/`build`/`start` 均调用 `vinext`（带 `WRANGLER_LOG_PATH=.wrangler/wrangler.log`）；`build:pages` = `next build`；`test` = `npm run build && node --test tests/rendered-html.test.mjs`；`lint` = eslint；`db:generate` = `drizzle-kit generate`；另有 `validate:pages`（node scripts/validate-pages-prefix.mjs）与 `export:review`（node scripts/export-self-contained.mjs）。

### WEB-A-05 依赖清单（技术栈）
- 原编号: facts-websites.md A 部分 F-005
- 位置: package.json（L19-42）
- 内容: dependencies：next 16.2.6、react 19.2.6、react-dom 19.2.6、drizzle-orm 0.45.2。devDependencies：vite 8.0.13、vinext 0.0.50、wrangler 4.92.0、@cloudflare/vite-plugin 1.37.1、@vitejs/plugin-rsc 0.5.26、tailwindcss 4.2.1（及 @tailwindcss/postcss）、typescript 5.9.3、drizzle-kit 0.31.10、eslint 9.39.4、react-server-dom-webpack 19.2.6。

### WEB-A-06 双构建轨道：vinext（Cloudflare）与 next build（GitHub Pages）
- 原编号: facts-websites.md A 部分 F-006
- 位置: package.json（L9-14）；build/sites-vite-plugin.ts
- 内容: 同一源码存在两条构建路径：`vinext dev/build/start` + wrangler（Cloudflare 运行时）与 `next build`（`build:pages`，产出 GitHub Pages 静态站）。`build/sites-vite-plugin.ts` 定义名为 "sites" 的 Vite 插件（`apply: "build"`），在 `closeBundle` 时把 `.openai/hosting.json` 与 `drizzle/` 迁移目录复制到 `dist/.openai/`（注释原文 "Packages Sites metadata and migrations after Vite finishes compiling."）。

### WEB-A-07 next.config.ts 静态导出配置
- 原编号: facts-websites.md A 部分 F-007
- 位置: next.config.ts（全文）
- 内容: `output: "export"`（注释原文 "Keep the site fully static so the same source can be exported for GitHub Pages."）、`trailingSlash: true`、`basePath` 取自环境变量 `NEXT_PUBLIC_SITE_BASE_PATH`、`images: { unoptimized: true }`。

### WEB-A-08 sitePath.ts 的站点 URL 与 basePath 机制
- 原编号: facts-websites.md A 部分 F-008
- 位置: app/sitePath.ts（全文）
- 内容: `SITE_BASE_PATH` 读自 `NEXT_PUBLIC_SITE_BASE_PATH`（去尾斜杠，默认空串）；`PUBLIC_SITE_URL = "https://tongyi-mai.github.io/Qwen-UI-Agent/"` 硬编码；导出 `siteAsset()`（为以 `/` 开头的路径补 basePath 前缀）与 `absoluteSiteUrl()`（拼出绝对 URL）。

### WEB-A-09 layout.tsx 的站点 metadata
- 原编号: facts-websites.md A 部分 F-009
- 位置: app/layout.tsx（全文）
- 内容: metadata：title "Qwen-UI-Agent — Technical Report"；description "Qwen-UI-Agent is Alibaba's next-generation real-world-centric GUI agent for mobile, computer use, web browsers, and cross-platform workflows."；applicationName "Qwen-UI-Agent"；authors `[{ name: "MAI-UI Team" }]`；openGraph 图 og.png（1536x1024）；viewport themeColor "#ffffff"、colorScheme "light"；根节点 `<html lang="en">`（语言属性固定英文，双语由内容层处理）。

### WEB-A-10 首页仅渲染 ReportPage 组件
- 原编号: facts-websites.md A 部分 F-010
- 位置: app/page.tsx（全文 5 行）
- 内容: 默认导出 `Home()` 返回 `<ReportPage />`（来自 `./components/ReportPage`）。README 编辑指南对应原文 "Edit page structure in `app/components/ReportPage.tsx`"、"Edit the visual system and responsive layout in `app/globals.css`"。

### WEB-A-11 双语机制：Language / LocalizedText / localize
- 原编号: facts-websites.md A 部分 F-011
- 位置: app/siteContent.ts（L1-6、1723）
- 内容: `export type Language = "en" | "zh"`；`LocalizedText = { en: string; zh: string }`；文件末尾导出 `localize(text: LocalizedText, language: Language)` 函数。所有站点文案以 en/zh 双字段成对维护。

### WEB-A-12 SITE_COPY 导航与关键文案
- 原编号: facts-websites.md A 部分 F-012
- 位置: app/siteContent.ts（L8-109）
- 内容: en.nav 为 `["Capabilities", "Performance", "Demos", "Citation"]`（zh 对应「智能体能力/性能指标/演示/引用」）；subtitle en "Towards Next-Generation Real-World Centric Foundation GUI Agent" / zh 「阿里巴巴集团的新一代真实场景 GUI 智能体」；性能表列名 `baseColumn: "Qwen3.5-27B"`、`oursColumn: "Qwen-UI-Agent"`；`sourceNote` 原文 "Content and metrics are distilled from the current LaTeX draft. Values may change before release."（zh：「内容与指标来自当前 LaTeX 草稿，正式发布前仍可能调整」）；`groundingFootnote` 与 `generalProtocolNote` 均声明分数由作者在自有评测环境独立复现。

### WEB-A-13 APPLICATIONS 六卡片与视觉类型
- 原编号: facts-websites.md A 部分 F-013
- 位置: app/siteContent.ts（L111-149 起）；README.md（L53-57）
- 内容: `APPLICATIONS` 数组元素 `kind` 枚举为 "mobile" | "computer" | "gui-cli" | "browser" | "research" | "proactive" 六种；`visual` 类型联合为 `mobile-ui`（CSS 绘制手机场景）/ `video`（本地循环视频）/ `gui-cli` / `browser-capture`（三帧动画浏览器序列）/ `research-flow` / `proactive-flow` / `image`。README 原文："`APPLICATIONS` controls the six visual slides in the interactive 'what it can do' carousel."

### WEB-A-14 METHOD_STEPS 四阶段方法流水线
- 原编号: facts-websites.md A 部分 F-014
- 位置: app/siteContent.ts（L983-1025）
- 内容: 四步字面：01 Environment infrastructure（stat "≈10K concurrent"，覆盖手机、电脑、网页与 DeepSearch 沙箱 + 真实设备运行时）；02 Agent-driven data flywheel（stat "≈10K task-verifier pairs"，Agent 构造任务、环境、verifier、失败诊断与迭代计划）；03 SFT + ActionRL + Online RL（stat "100+ step trajectories"）；04 Proactive harness（stat "Mobile + Desktop + Search"，通知驱动主动服务、共享状态、跨平台规划、用户确认边界）。

### WEB-A-15 PERFORMANCE_BENCHMARKS 代表分数
- 原编号: facts-websites.md A 部分 F-015
- 位置: app/siteContent.ts（L544-588）
- 内容: MobileWorld 条目（metric "GUI-Only Success rate (%)"）：Qwen-UI-Agent 27B 82.1（access "ours"）、Seed 2.1 Pro 73.2、GPT-5.6 Sol 70.1、Claude Opus 4.8 67.5、Qwen 3.7 Plus 62.3、Gemini 3.1 Pro 58.1。MobileWorld-Real 条目（真实手机）：Qwen-UI-Agent 27B 92.2、Seed 2.1 Pro 88.7、Gemini 3.1 Pro 86.2，并带 `href: "/mobileworld-real/"` 链接。

### WEB-A-16 第二路由页 mobileworld-real
- 原编号: facts-websites.md A 部分 F-016
- 位置: app/mobileworld-real/page.tsx（全文）；app/components/MobileWorldRealPage.tsx
- 内容: 路由 `/mobileworld-real/` 渲染 `MobileWorldRealPage`；metadata 描述原文："MobileWorld-Real is a real-device benchmark with human-written mobile tasks across live Android apps, accounts, content, and networks."；openGraph 描述 "everyday mobile GUI work across 409 tasks and 104 live Android apps"。

### WEB-A-17 数据库 schema 故意留空
- 原编号: facts-websites.md A 部分 F-017
- 位置: db/schema.ts（全文 4 行）
- 内容: 原文注释："// Intentionally empty by default. // Add Drizzle tables here when the site actually needs a database. // See examples/d1/db/schema.ts for an opt-in example."，文件仅 `export {}`。即当前站点无任何数据表定义。

### WEB-A-18 drizzle.config.ts 配置
- 原编号: facts-websites.md A 部分 F-018
- 位置: drizzle.config.ts（全文）
- 内容: `defineConfig({ out: "./drizzle", schema: "./db/schema.ts", dialect: "sqlite" })`。

### WEB-A-19 GitHub Pages 部署 workflow
- 原编号: facts-websites.md A 部分 F-019
- 位置: .github/workflows/deploy-pages.yml（全文）
- 内容: workflow 名 "Deploy GitHub Pages"，push main 或手动触发；Node 22 + `npm ci`；构建环境变量 `NEXT_PUBLIC_SITE_BASE_PATH: /Qwen-UI-Agent` 下执行 `npm run build:pages`，随后 `npm run validate:pages` 校验部署路径，上传 `./out` 至 deploy-pages@v4。

### WEB-A-20 测试与自检脚本
- 原编号: facts-websites.md A 部分 F-020
- 位置: tests/rendered-html.test.mjs；scripts/validate-pages-prefix.mjs；scripts/export-self-contained.mjs
- 内容: 三文件均存在；`npm test` 流程为先完整构建再用 Node 内置 test runner 对"构建产物 HTML"跑测试（package.json L15）；`validate:pages` 校验 Pages 前缀路径；`export:review` 产出自包含审阅导出。

### WEB-A-21 Demo explorer 五大域与指令来源语言标注
- 原编号: facts-websites.md A 部分 F-021
- 位置: README.md（L64-81）；app/siteContent.ts（L1115-1196，DEMO_CATEGORIES/DEMO_VIDEOS）
- 内容: README 原文：五个域为 "real-device mobile, computer use, cross-device GUI use, mobile use with Deep Research, and proactive service"；五个真机工作流与两个 Computer Use 完整工作流托管于 `public/demos/source/`（720p H.264）；Deep Research 域内嵌两个官方 Bilibili 演示；"Every `DEMO_VIDEOS` entry records its original instruction language in `instructionSourceLanguage`. The opposite-language interface automatically marks the instruction as `translated from Chinese` or `翻译自英文指令`."

### WEB-A-22 MODEL_ORGANIZATIONS 与本地化品牌 logo
- 原编号: facts-websites.md A 部分 F-022
- 位置: README.md（L58-59、97-101）；app/siteContent.ts（L361 起）
- 内容: README 原文："`MODEL_ORGANIZATIONS` maps each benchmark entry to its visible publisher label and local asset in `public/brand-logos/`"；"The compact benchmark logos are stored locally so the charts do not depend on third-party requests. Most SVGs come from Lobe Icons 1.94.0; Gemini and Anthropic use the supplied reference icons, and the Apodex avatar comes from its official Hugging Face organization."

### WEB-A-23 GENERAL_CAPABILITY_GROUPS 与 open-sourced 专才键
- 原编号: facts-websites.md A 部分 F-023
- 位置: README.md（L60-61）；app/siteContent.ts（L853-855）
- 内容: README 原文："`GENERAL_CAPABILITY_GROUPS` is rendered inside Performance as the 'Broader Capabilities' subsection; it is not a standalone page section."；`SpecialistKey` 类型字面量为 `"guiOwl" | "uiVenus" | "openCUA"` 三个专才模型键。

### WEB-A-24 站点当前状态声明
- 原编号: facts-websites.md A 部分 F-024
- 位置: README.md（L83-95）
- 内容: 原文："Replace the `Coming soon` resource cards with the final technical report, code, and checkpoint URLs at release time."；"External reference embeds remain explicitly labeled as temporary samples."；"Result figures that conflict across the current draft are intentionally omitted until the technical-report values are frozen."；导航/基准域/演示类目等所有可见文案须提供英文与完全本地化中文，"Model and benchmark proper names remain unchanged."

---

## 覆盖核对表

| 部分 | 事实编号 | 原始清单 | 适配说明 |
|---|---|---|---|
| A | F-001 ~ F-032 | facts-mobilepa-bench.md | 编号原样沿用，内容逐条保留（数字与引文未改动） |
| B | WEB-A-01 ~ WEB-A-24 | facts-websites.md A 部分 F-001 ~ F-024 | 改用 WEB-A 前缀编号避免与 A 部分冲突，每条标注原编号 |
| 未覆盖 | — | facts-websites.md B 部分 F-025 ~ F-040（MAI-UI-blog） | 属 mai-ui 束登记范围，本束不引用；其中两篇博客为 Notion 重定向 stub，正文一律不引用 |
