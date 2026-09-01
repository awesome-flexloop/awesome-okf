---
type: spec
title: "trae-skills 源码事实清单"
---

# trae-skills 源码事实清单

## 项目信息

- F-001: 项目位于 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-skills\`，是 TRAE IDE 的社区维护 Agent Skills 集合，采用 MIT 许可证。
- F-002: 项目根目录包含 `README.md`、`README.zh-CN.md`、`CONTRIBUTING.md`、`LICENSE`、`.gitignore`。
- F-003: 项目包含 `assets/image/Skills.gif` 作为 Skills Banner 图片。
- F-004: Skills 安装路径分两种：项目级为 `.trae/skills/<skill-name>/SKILL.md`，全局级为 `~/.trae/skills/<skill-name>/SKILL.md`。
- F-005: README.md 的 Skills 目录表格列出了 9 个技能：daily-trend-writer、git-commit-generator、cn-punctuation-checker、wechat-mini-program-development、kz-article-deep-analysis、video-to-keyframes、web-design-teroop、trae-claw-install、cloudbase。

## 目录结构

- F-006: 技能文件统一存放在 `skills/` 目录下，每个技能为一个独立子目录。
- F-007: `skills/_template/SKILL.md` 是技能模板文件。
- F-008: 技能目录可选子目录包括 `examples/`（input.md/output.md 示例）、`templates/`（可复用模板）、`resources/`（参考文件、脚本、资源）。
- F-009: 实际技能子目录共 12 个（含 _template）：`_template`、`cloudbase`、`cn-punctuation-checker`、`daily-hot-news`、`daily-trend-writer`、`git-commit-generator`、`kz-article-deep-analysis`、`trae-claw-install`、`video-to-keyframes`、`web-design-teroop`、`wechat-mini-program-development`、`zopia_ai_skills`。

## SKILL.md 格式规范

- F-010: 每个技能必须包含 `SKILL.md` 文件作为核心指令文件。
- F-011: SKILL.md 以 YAML frontmatter 开头，必填字段为 `name`（小写连字符命名）和 `description`（描述功能与使用场景）。
- F-012: 模板定义的 SKILL.md 章节结构为：`# Skill Name` → `## Description` → `## Usage Scenario` → `## Instructions` → `## Examples (Optional)`。
- F-013: frontmatter 中的 `name` 字段规则：小写字母、连字符代替空格、命名保持稳定。
- F-014: frontmatter 中的 `description` 字段要求明确说明做什么以及何时使用，这是 agent 决定是否加载该 skill 的依据。
- F-015: 部分技能扩展了 frontmatter 字段，如 kz-article-deep-analysis 额外包含 `version: 1.0.3` 和 `metadata.author: K叔`。

## 各技能核心内容

### cloudbase

- F-016: cloudbase 技能文件为 `skills/cloudbase/SKILL.md`，name 为 `cloudbase`。
- F-017: description 为：在 Trae 中构建/部署/调试腾讯云开发（TCB）应用时使用，涵盖 Web、微信小程序、云函数、CloudRun、认证、NoSQL/PostgreSQL、存储、内置 AI；优先使用 CloudBase MCP 工具。
- F-018: 指令步骤为 7 步：确认场景 → 确保 CloudBase MCP 可用 → 显式绑定环境（调用 envQuery 解析 EnvId）→ 优先使用 MCP 工具做管理工作 → 加载匹配的已发布 CloudBase skill → 按顺序实现（资源准备→前后端代码→本地验证→部署）→ 收尾（运行 cloudbase-code-review、报告 EnvId 和 URL）。
- F-019: CloudBase MCP 配置 JSON 为 `{"mcpServers":{"cloudbase-mcp":{"command":"npx","args":["-y","@cloudbase/cloudbase-mcp@latest"],"env":{}}}}`。
- F-020: 约束条款：不得编造 CloudBase API 路径或 MCP 工具参数；不得在前端代码中暴露 API key/service_role 凭证；同一路径 2-3 次失败后停止并重路由。

### cn-punctuation-checker

- F-021: cn-punctuation-checker 技能文件为 `skills/cn-punctuation-checker/SKILL.md`，name 为 `"cn-punctuation-checker"`（带引号）。
- F-022: 功能为检测中文文本中错误使用的英文标点，支持精确位置报告（行号、列号、上下文片段）、Markdown 格式报告、批量修复、项目级扫描（自动排除代码文件）。
- F-023: 支持的英文→中文标点映射共 12 组：,→， .→。 ?→？ !→！ :→： ;→； "→"/" '→'/ ' ( )→（） [ ]→【】 -→— ...→……。
- F-024: 默认检查文件类型包括：.md、.txt、.html/.htm、.xml、.json（仅检查字符串值）、.yml/.yaml、.properties、.vue/.jsx/.tsx/.js/.ts。
- F-025: 默认排除目录包括：node_modules、.git、dist、target、build、out、.idea、.vscode、__pycache__、.next、.nuxt。
- F-026: 默认排除文件类型（代码文件）包括：.css/.scss/.less/.sass、.py、.java、.go、.cpp/.c/.h/.hpp、.cs、.php、.rb、.swift、.kt、.rs、.sql。
- F-027: 智能检测规则：仅检查含中文字符的行、排除 URL 和文件路径中的标点、排除代码字符串、排除 Markdown 代码块和 HTML 注释。
- F-028: 该 SKILL.md 未遵循标准的 Description/Usage Scenario/Instructions 章节结构，而是采用 Features/Supported Punctuation Marks/Usage/Execution Flow/Smart Detection Rules 结构。

### daily-hot-news

- F-029: daily-hot-news 技能文件为 `skills/daily-hot-news/SKILL.md`，name 为 `daily-hot-news`。
- F-030: 触发关键词为"今日热搜""新闻热榜""今天有什么热点""全网热搜""热门新闻""今日新闻""热榜"；不适用于历史新闻或特定领域深度分析。
- F-031: 默认聚合 6 个平台：微博热搜、百度热搜、知乎热榜、头条热榜、哔哩哔哩热门、抖音热搜；默认每个平台 Top 10。
- F-032: 指令分 3 步：确认用户需求（平台/数量）→ 执行 `resources/scripts/fetch_news.py` 获取数据 → 格式化输出（含 emoji、表格、时间戳、免责声明）。
- F-033: 输出格式为 Markdown，标题为"# 🔥 今日全网热榜 | {日期} {时间}"，每个平台一个二级标题+表格（排名/热搜话题/热度），排名前 3 名使用 🥇🥈🥉 emoji。

### daily-trend-writer

- F-034: daily-trend-writer 技能文件为 `skills/daily-trend-writer/SKILL.md`，name 为 `daily-trend-writer`。
- F-035: 功能描述为全自动化公众号内容生产流水线，每日发现"小而美"选题，输出"咪蒙风格"与"技术干货"两篇高质量公众号文章。
- F-036: 工作流分为 6 个 Phase：Phase 0 时间同步 → Phase 1 热点发现与榜单生成 → Phase 2 选题与深挖 → Phase 3 内容打磨（调用 subskills/doc-coauthoring）→ Phase 4 多风格文章写作（咪蒙风格 + 微信公众号技术干货）→ Phase 5 归档与交付。
- F-037: Phase 0 要求执行 `date "+%Y-%m-%d %H:%M:%S %Z"` 获取系统时间，格式化为 YYYY-MM-DD（搜索）和 YYYYMMDDHHMMSS（归档目录）。
- F-038: Phase 1 输出 4 类分类热点榜：实用工具榜、社区热点榜、教程经验榜、行业动态榜。
- F-039: Phase 4 任务 A 调用 `subskills/mimeng-writing` Skill 撰写爆款文（5个标题候选、短句、情绪词、故事化叙事）。
- F-040: Phase 4 任务 B 调用 `subskills/wechat-article-writer` Skill 撰写技术干货文（结构：背景→核心功能→原理/教程→总结）。
- F-041: Phase 5 归档路径格式为 `./YYYYMMDDHHMMSS/mimeng_{topic_slug}.md`、`./YYYYMMDDHHMMSS/tech_{topic_slug}.md`、可选 `brief_{topic_slug}.md`。
- F-042: 技能目录包含 `examples/input.md`、`examples/output.md`、`resources/trend-sources.md`、`subskills/doc-coauthoring.md`、`subskills/mimeng-writing.md`、`subskills/wechat-article-writer.md`、`templates/topic-brief.md`、`templates/trend-board.md`。

### git-commit-generator

- F-043: git-commit-generator 技能文件为 `skills/git-commit-generator/SKILL.md`，name 为 `git-commit-generator`。
- F-044: 功能为基于代码变更（git diff）生成符合 Conventional Commits 规范的标准化提交信息。
- F-045: 触发场景：用户要求"写 commit message"/"生成 commit"、用户问"我改了什么"、agent 需要为刚完成的变更提议 commit message。
- F-046: 指令分 3 步：分析变更（读取 diff、确定 scope、参考 `resources/conventional-commits-types.md` 确定 type）→ 构造提交信息（遵循 `templates/commit-message.txt` 结构：`<type>(<scope>): <subject>`，祈使语气，无句号，50字符以内；正文用 bullet points 说明 what/why）→ 输出（代码块格式，多逻辑变更建议拆分）。
- F-047: 技能目录包含 `examples/input.md`、`examples/output.md`、`resources/conventional-commits-types.md`、`templates/commit-message.txt`。

### kz-article-deep-analysis

- F-048: kz-article-deep-analysis 技能文件为 `skills/kz-article-deep-analysis/SKILL.md`，name 为 `kz-article-deep-analysis`，版本 v1.0.3，作者 K叔。
- F-049: 功能为深度解读非学术类文章（博客、随笔、评论），抽取核心议题与核心主张，输出结构化分析报告，不适用于学术论文或书籍。
- F-050: 核心任务为解构文章（核心议题、核心主张、论证逻辑）和认知增量评估（观点与读者既有认知的差异与张力）。
- F-051: 工作流分为 4 个步骤（@步骤）：获取与预处理（WebFetch/直接文本、提取标题作者）→ 深度解构（下探核心议题、提炼核心主张、梳理论证骨架≤3论据、绘制ASCII推理拓扑图）→ 认知增量（定位增量点、绘制ASCII Art认知卡片）→ 生成报告（按 `assets/template.md` 结构）。
- F-052: 步骤使用 `@动作:`、`@类型:`、`@优先级:`、`@验证点:`、`@验证方式:` 等注释标签进行结构化标记。
- F-053: 技能目录包含 `assets/template.md`、`references/methodology.md`、`scripts/verify.py`。
- F-054: 版本历史记录：v1.0.3（增加使用示例）、v1.0.2（术语专业化）、v1.0.1（添加作者元数据）、v1.0.0（初始版本）。

### trae-claw-install

- F-055: trae-claw-install 技能文件为 `skills/trae-claw-install/SKILL.md`，name 为 `trae-claw-install`。
- F-056: 功能为从仓库驱动的 OpenClaw 部署工作流，包含平台路由、setup/start/check、验收检查和统一故障排除。
- F-057: 前置条件：当前工作目录为仓库根目录、终端可用、仓库包含平台脚本和故障排除文档。
- F-058: 指令 5 步：检测平台并路由脚本（Windows→WSL2 使用 `scripts/windows/wsl/*.sh`，macOS→`scripts/macos/*.sh`，Linux→`scripts/linux/*.sh`）→ 验证基线（node >=22、npm 可用、openclaw 缺失则继续 setup）→ 执行标准流程（setup→start→check）→ 运行最低验收（openclaw doctor/status/dashboard）→ 失败时故障排除工作流。
- F-059: 输出契约：成功时报告平台/执行步骤/验收结果/服务可访问性；失败时报告首个错误/已执行诊断/下一步可操作修复。
- F-060: 约束条款：复用仓库脚本和文档，不创建并行流程；不写入真实密钥；Windows 优先在 WSL2 Linux 文件系统内执行。
- F-061: 技能目录包含 `examples/input.md`、`examples/output.md`。

### video-to-keyframes

- F-062: video-to-keyframes 技能文件为 `skills/video-to-keyframes/SKILL.md`，name 为 `"video-to-keyframes"`（带引号）。
- F-063: 功能为视频抽帧→转场/分段检测→候选关键帧选择→生成复筛 HTML 画廊页，产物落盘到当天文件夹。
- F-064: 触发场景：用户提供视频并说抽帧/拆帧/关键帧/候选关键帧/镜头拆分/转场点/分段/分镜初筛。
- F-065: 依赖 Python 3.10+、numpy、opencv-python。
- F-066: 输出目录结构：`<当天文件夹>\_frames_<视频名>_<间隔>\` 下包含 f_*.jpg 候选帧池、frames.csv/json/top_keep.json/meta.json、`\_keyframe_candidates\` 子目录（cuts.json、segments.json、segments_gallery.html、gallery.html、candidates.csv/json、selected.txt、prompt_pack.html），以及 `<视频名>_拆分.txt` 汇总文件。
- F-067: 一键运行命令：`python .\skills\video-to-keyframes\resources\scripts\run_video_workflow.py "<视频路径>" --day-folder "<当天文件夹>" --every-seconds 0.5 --max-frames 600`。
- F-068: 复筛要点：先看 segments_gallery.html 确认分段合理性，再看 gallery.html 挑 6-12 张帧，将 cand_id 写入 selected.txt。

### web-design-teroop

- F-069: web-design-teroop 技能文件为 `skills/web-design-teroop/SKILL.md`，name 为 `web-design-teroop`。
- F-070: 角色定位为首席设计架构师，创建、持久化和维护正式的设计规范文档（.design-spec.md），作为项目视觉标识的单一可信源。
- F-071: 指令 5 步：预检（查找根目录 .design-spec.md 或 Core Memory 中已有设计）→ 发现阶段（搜索 4 种流行网页设计风格，让用户选择视觉风格和整体氛围）→ 生成并持久化设计规范（5个维度：设计风格、色彩方案、字体排版、图标策略、Logo概念；写入 ./.design-spec.md 并更新 Core Memory）→ 布局与设计调整（必须调用 AskUserQuestion 确认调整方向，同步更新文件和内存）→ 技术合成（转换为 tailwind.config.js 配置，提供 React 组件实现）。
- F-072: 设计规范文档 5 个维度模板章节为：1. Design Style、2. Color Palette、3. Typography、4. Iconography、5. Logo。
- F-073: 维护规则：所有后续 UI 开发任务必须先读 .design-spec.md；任何设计变更必须同时反映在本地文件和 Core Memory。

### wechat-mini-program-development

- F-074: wechat-mini-program-development 技能文件为 `skills/wechat-mini-program-development/SKILL.md`，name 为 `"wechat-mini-program-development"`（带引号）。
- F-075: 功能为微信小程序开发技能，提供标准项目结构、统一请求封装、API 端点管理、配置文件约定。
- F-076: 触发场景：用户要求创建微信小程序项目、需要小程序开发帮助、需要 HTTP 请求封装、需要 API 管理。
- F-077: 指令 8 步：项目结构搭建 → 创建 utils/config.js（baseUrl/timeout/appId，CommonJS 语法）→ 创建 utils/api.js（集中端点管理，user/goods/order 模块）→ 创建 utils/request.js（统一请求/响应拦截器）→ 创建 utils/util.js（工具函数：formatTime/showLoading/hideLoading/showToast/showSuccess/showConfirm）→ 设置全局登录检查（app.js 中 onLaunch 调用 checkLoginStatus）→ 配置 tabBar（app.json 中配置 pages/window/tabBar/style/sitemapLocation）→ 使用示例。
- F-078: request.js 拦截器特性：自动拼接完整 URL、自动添加 Content-Type: application/json、自动注入 token、支持自定义 header/timeout/loading；响应端 HTTP 200-299 为成功、业务 code===0 为成功、自动返回 data 字段、401 自动跳转登录页清 token、5xx 和网络错误统一处理。
- F-079: 标准项目结构为：app.js/app.json/app.wxss/sitemap.json/pages/（每页 index.js/json/wxml/wxss）/components/utils/assets/.trae/。

### zopia_ai_skills

- F-080: zopia_ai_skills 技能文件为 `skills/zopia_ai_skills/SKILL.md`，name 为 `zopia-api`。
- F-081: 功能为通过 Zopia API 驱动 AI 视频制作：创建项目、配置风格、与 Agent 对话生成剧本/角色/分镜/视频、查询项目状态和积分。
- F-082: 认证流程：引导用户访问 https://zopia.ai/settings/api-tokens 生成 token，格式为 `zopia-xxxxxxxxxxxx`，有效期 30 天，每次请求 header 携带 `Authorization: Bearer <TOKEN>`。
- F-083: 推荐工作流：Create Project → Save Settings（locale/style/aspect_ratio/generation_method）→ Multi-turn Agent Chat → View Results。
- F-084: Agent Chat 自动调用 4 个工具：screenplay_writer、character_designer、storyboard_artist、video_producer。
- F-085: 多轮对话机制：首次调用不传 session_id，响应返回 session_id；后续调用传入 session_id 继续同一会话；不传则开始新对话。
- F-086: 核心 API 端点：POST /api/base/create（创建项目，返回 baseId）、POST /api/base/settings（保存设置，locale/aspect_ratio/style 必填）、POST /api/v1/agent/chat（Agent 对话）、GET /api/base/settings、GET /api/base/list、GET /api/base/{id}、GET /api/billing/getBalance。
- F-087: 并发限制：同一 session_id 同一时间只能一个请求，返回 409 表示另一个仍在运行。
- F-088: 错误码：400 参数错误、401 未认证/token过期、402 积分不足、403 无权限、404 资源不存在、409 会话运行中。
- F-089: 视频生成最佳实践：生成前与用户确认镜头数量，每批 3-5 个镜头生成，不要一次全部生成。
- F-090: 技能目录额外包含 `API_REFERENCE.md`、`EXAMPLES.md`、`README.md`、`README_CN.md`、`SETTINGS_REFERENCE.md`。

## 脚本文件细节

### daily-hot-news 脚本

- F-091: `skills/daily-hot-news/resources/scripts/fetch_news.py` 为热榜数据抓取脚本，仅使用 Python 标准库（无需 pip install）。
- F-092: fetch_news.py 配置了 4 层数据源优先级：①韩小韩 API（api.vvhan.com，首选）②60s API（60s.viki.moe，备选）③小众独行 API（xzdx.top，备选）④自建 DailyHotApi（环境变量 DAILY_HOT_API_BASE）。
- F-093: PLATFORM_CONFIG 字典定义 6 个平台（weibo/baidu/zhihu/toutiao/bilibili/douyin），每个平台配置 vvhan_type、sixty_s_path、xzdx_type、dailyhot_path、name、emoji。
- F-094: fetch_news.py 命令行参数：`--platforms`（逗号分隔平台列表，默认全部）、`--top`（每平台条目数，默认10）、`--format`（json/markdown，默认json）、`--output`（输出文件路径，默认stdout）。
- F-095: fetch_news.py 的 `format_hot_value` 函数格式化热度值：≥1亿显示"X.X亿"，≥1万显示"X.X万"。
- F-096: `skills/daily-hot-news/resources/scripts/generate_report.py` 为报告生成脚本，将 fetch_news.py 输出的 JSON 转为 markdown/text/html 三种格式。
- F-097: generate_report.py 命令行参数：`--data`（JSON 数据文件路径，- 表示 stdin，必填）、`--format`（markdown/text/html，默认markdown）、`--output`（输出文件路径）。
- F-098: generate_report.py 的 HTML 报告使用渐变背景（#667eea→#764ba2）、圆角卡片、排名圆形色块（金/银/铜色）。

### kz-article-deep-analysis 脚本

- F-099: `skills/kz-article-deep-analysis/scripts/verify.py` 为技能结构验证脚本。
- F-100: verify.py 检查项：SKILL.md 是否存在 → SKILL.md 是否包含 YAML frontmatter → frontmatter 是否包含 name/description/version → 是否包含 `## @工作流:` 章节 → 是否包含 `## 版本历史` 章节 → references/methodology.md 是否存在 → assets/template.md 是否存在。
- F-101: verify.py 命令行参数：`--skill`（技能文件夹路径，必填），返回 0 表示通过、1 表示失败。

### video-to-keyframes 脚本

- F-102: `skills/video-to-keyframes/resources/scripts/` 目录下共 4 个 Python 脚本：extract_frames_and_describe.py、generate_daily_folder.py、run_video_workflow.py、select_keyframes.py，以及 requirements.txt。
- F-103: generate_daily_folder.py 功能简单：在 base_dir 下创建以当前日期命名的文件夹（默认格式 %Y-%m-%d），命令行参数为 base_dir（默认.）和 --format。
- F-104: extract_frames_and_describe.py 为抽帧脚本，依赖 cv2（opencv-python）和 numpy。
- F-105: extract_frames_and_describe.py 使用 FrameInfo dataclass 记录每帧信息：index、timestamp_s、file、width、height、sharpness（拉普拉斯方差）、brightness、contrast、saturation、motion（与前帧差均值）、suggested_keep、description（中文描述如"曝光正常，对比适中，清晰度正常，色彩适中，画面稳定"）。
- F-106: extract_frames_and_describe.py 命令行参数：video（必填）、--out、--every-seconds（默认0.5）、--max-frames（默认600）、--start（默认0.0）、--end、--jpeg-quality（默认92）、--min-sharpness（默认80.0）、--brightness-min（默认60.0）、--brightness-max（默认200.0）。
- F-107: extract_frames_and_describe.py 输出文件：meta.json（视频元信息）、frames.json（全部帧信息数组）、frames.csv（CSV 格式）、top_keep.json（按清晰度排序前30帧）、f_XXXXX_tHH-MM-SS-sss.jpg 帧图片。
- F-108: select_keyframes.py 为关键帧选择脚本，使用 dHash（差值哈希，64位）和汉明距离进行帧间相似度计算和转场检测。
- F-109: select_keyframes.py 定义 3 个 dataclass：Cand（候选帧：group_id/cand_id/timestamp_s/src_file/out_file/score/sharpness/brightness/contrast/saturation/motion/description）、Cut（转场点：index_left/index_right/t_left/t_right/cut_t/dhash_dist）、Segment（分段：seg_id/start_t/end_t/rep_t/rep_file/rep_score/frame_count）。
- F-110: select_keyframes.py 的评分函数 `_score` 加权公式：清晰度0.45 + 亮度适中度0.25 + 对比度0.15 + 饱和度0.05 + 低运动0.10。
- F-111: select_keyframes.py 转场检测算法：相邻帧 dHash 汉明距离 ≥ cut_thr 且前后 stable_window 窗口内最大距离 ≤ stable_thr 时判定为转场；过短分段（< min_seg_len）会被合并。
- F-112: select_keyframes.py 输出文件：cuts.json（转场点列表）、segments.json（分段列表）、candidates.json/csv（候选帧）、gallery.html（候选帧画廊页）、segments_gallery.html（分段代表帧画廊）、prompt_pack.html（复筛+提示词协作页，含暗色模式、文件上传、一键复制）、selected.txt（空文件，供人工填写）。
- F-113: select_keyframes.py 命令行参数：frames_json（必填）、--out、--hamming（去重阈值，默认10）、--max-cands（默认30）、--cut-thr（默认22）、--stable-thr（默认10）、--stable-window（默认3）、--min-gap（默认1.0s）、--min-seg-len（默认1.5s）。
- F-114: run_video_workflow.py 为一键编排脚本，依次调用 extract_frames_and_describe.py 和 select_keyframes.py，最后生成 `<视频名>_拆分.txt` 汇总文件。
- F-115: run_video_workflow.py 命令行参数：video（必填）、--day-folder、--every-seconds（默认0.5）、--max-frames（默认600）、--jpeg-quality（默认92）、--hamming（默认10）、--max-cands（默认30）、--cut-thr（默认30）、--stable-thr（默认31）、--stable-window（默认1）、--min-gap（默认1.0）、--min-seg-len（默认2.0）。

## 社区积分机制

- F-116: 项目根目录包含 `community-points.json` 和 `community-leaderboard.md` 两个社区积分文件。
- F-117: community-points.json 初始结构为 `{"scores": {}, "ledger": {}}`，scores 存储用户积分，ledger 存储事件记录（防重复记账）。
- F-118: community-leaderboard.md 初始内容为表格表头和 "_No contributors yet_" 行，末尾有 `Updated at: 1970-01-01T00:00:00.000Z` 时间戳。
- F-119: `.github/scripts/update-community-points.js` 为 Node.js 积分更新脚本。
- F-120: 积分事件类型共 3 种：①workflow_dispatch（手动加分，支持 manual_user/manual_points/manual_reason/manual_event_key 参数）②pull_request closed + merged（PR合并，+1分；若PR描述中引用 close/fix/resolve #issueNumber，关联 issue 额外 +1分）③issues closed（Issue关闭，+1分；通过 GraphQL 查询是否由合并的 PR 解决，若是则将积分给 PR 作者而非关闭者）。
- F-121: 默认忽略用户集合包含 `github-actions[bot]`，所有以 `[bot]` 结尾的用户也会被忽略，额外可通过 POINTS_IGNORE_USERS 环境变量配置。
- F-122: ledger 中的 eventKey 格式：手动为 `manual:{eventSuffix}:{user}`、PR合并为 `pr:{prNumber}:merged`、PR解决Issue为 `issue:{issueNumber}:resolved-by-pr:{prNumber}`、Issue关闭为 `issue:{issueNumber}:closed`。
- F-123: `.github/workflows/community-points.yml` 为 GitHub Actions 工作流，名称"Community Points"。
- F-124: 工作流触发条件：workflow_dispatch（手动输入 manual_user/manual_points/manual_reason/manual_event_key）、pull_request closed、issues closed。
- F-125: 工作流权限：contents: write、pull-requests: read、issues: read。
- F-126: 工作流使用 concurrency group `community-points`（cancel-in-progress: false），在 ubuntu-latest 上运行。
- F-127: 工作流步骤：checkout（fetch-depth:0，在默认分支）→ 切换到 community-points-data 分支（不存在则创建）→ 运行 update-community-points.js 脚本（传入 GITHUB_EVENT_PATH/GITHUB_EVENT_NAME/GITHUB_ACTOR/GITHUB_REPOSITORY/GITHUB_RUN_ID/GITHUB_TOKEN，忽略 github-actions[bot],dependabot[bot]）→ 检查是否有变更 → 如有变更则以 github-actions[bot] 身份提交并推送到 community-points-data 分支。
- F-128: update-community-points.js 通过正则提取 PR 中 close/fix/resolve 关键字引用的 Issue 编号，支持本地引用（#123）、跨仓库引用（owner/repo#123）和 URL 引用（https://github.com/owner/repo/issues/123）三种格式。
- F-129: formatLeaderboard 函数生成排行榜 Markdown，按积分降序排列（同分按用户名排序），前三名无特殊标记。
