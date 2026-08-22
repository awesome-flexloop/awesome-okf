# trae-skills 核心洞察与知识地图

## 核心洞察（四元组）

### 洞察 1：SKILL.md 是"提示词包"而非代码包

| 维度 | 内容 |
|------|------|
| **陈述** | SKILL.md 的本质是 YAML frontmatter 元数据 + Markdown 指令体构成的**提示词包（Prompt Package）**，而非传统意义上的代码包或插件。它的核心交付物是自然语言指令，通过 frontmatter 的 `name`/`description` 元数据让 Agent 决定何时加载，通过 Markdown 正文中的步骤化指令指导 Agent 行为。脚本（Python/JS）仅作为可选辅助资源存在。 |
| **证据** | F-004（安装路径为 `.trae/skills/<name>/SKILL.md`，单一 Markdown 文件为入口）、F-010（每个技能必须包含 SKILL.md 作为核心指令文件）、F-011（YAML frontmatter 必填 name 和 description）、F-012（标准章节为 Description/Usage Scenario/Instructions/Examples，全部是自然语言结构）、F-014（description 是 agent 决定是否加载 skill 的依据） |
| **反常识** | 直觉上"技能"应该像 VS Code 插件或 npm 包一样包含可执行代码作为核心，但 trae-skills 中代码是附属品——纯 prompt 型技能（如 git-commit-generator、cn-punctuation-checker）无需任何脚本即可工作，脚本仅在需要外部数据获取或复杂计算时才出现。技能的"能力边界"由 Markdown 指令定义，而非由代码 API 定义。 |
| **行动** | 设计新技能时，应优先用 Markdown 指令体描述完整工作流，仅在纯 prompt 无法完成（需调用外部 API、执行系统命令、处理二进制数据）时才引入脚本资源。frontmatter 的 description 字段必须精确描述"做什么"和"何时使用"，这是技能被正确触发的唯一依据。 |

### 洞察 2：社区技能存在三类模板模式

| 维度 | 内容 |
|------|------|
| **陈述** | 12 个社区技能可归纳为三种结构模式：**①纯 Prompt 型**（仅 SKILL.md + 可选 examples/templates/resources 中的文本文件，无脚本）、**②脚本辅助型**（SKILL.md + resources/scripts/ 下的 Python/JS 脚本执行具体操作）、**③Workflow 编排型**（SKILL.md 定义多阶段 Phase 工作流，调用 subskills 和多个脚本/模板协同完成复杂任务）。三种模式的复杂度递增，但核心始终是 SKILL.md 的指令编排。 |
| **证据** | F-008（技能目录可选子目录包括 examples/templates/resources）、纯 Prompt 型证据：F-043~F-047（git-commit-generator：仅 diff 分析 + 模板生成，无执行脚本）、F-074~F-079（wechat-mini-program-development：8步指令指导 Agent 创建项目结构和代码文件）；脚本辅助型证据：F-029~F-033（daily-hot-news：调用 fetch_news.py 获取数据）、F-091~F-098（fetch_news.py 和 generate_report.py 两个 Python 脚本）；Workflow 型证据：F-034~F-042（daily-trend-writer：6 个 Phase，调用 subskills/doc-coauthoring、subskills/mimeng-writing、subskills/wechat-article-writer 三个子技能）、F-062~F-068（video-to-keyframes：4 个 Python 脚本流水线编排） |
| **反常识** | 三种模式并非"高级/低级"之分——最简单的纯 Prompt 型技能（如 git-commit-generator）可能使用频率最高，而最复杂的 Workflow 型技能（如 daily-trend-writer）反而因为依赖子技能链路过长而脆弱。脚本辅助型技能的脚本通常极简（如 fetch_news.py 仅用标准库），核心价值仍在 SKILL.md 的触发条件和输出格式定义中。 |
| **行动** | 新技能设计应从纯 Prompt 型起步，验证触发逻辑和指令有效性后再按需引入脚本。Workflow 型技能需在 SKILL.md 中明确每个 Phase 的输入/输出契约，并通过 subskills/ 目录实现指令复用，避免单文件过长。每个技能目录应严格遵循 _template 的规范结构，扩展字段（如 version、metadata.author）可按需添加但不破坏核心结构。 |

### 洞察 3：社区积分通过 GitHub Actions + Ledger 实现自动化激励

| 维度 | 内容 |
|------|------|
| **陈述** | 社区贡献激励采用**完全自动化**的积分系统，由 GitHub Actions 工作流驱动，通过 JSON Ledger（台账）实现幂等记账，无需人工干预。积分事件覆盖三类贡献行为（手动加分、PR 合并、Issue 关闭），通过 eventKey 幂等键防止重复计分，积分结果写入 community-points-data 分支并自动生成 Markdown 排行榜。 |
| **证据** | F-116~F-118（community-points.json 初始结构含 scores 和 ledger，community-leaderboard.md 自动生成）、F-119（.github/scripts/update-community-points.js 为积分更新脚本）、F-120（三类积分事件：workflow_dispatch 手动加分、PR merged +1分、Issue closed +1分；PR 引用 close/fix/resolve 关联 Issue 额外+1分）、F-122（eventKey 幂等键格式：manual:/pr:/issue:/issue:resolved-by-pr:）、F-123~F-127（GitHub Actions 工作流触发条件、权限、并发控制、checkout→切换分支→运行脚本→提交推送的完整流程）、F-128（正则提取 PR 中 close/fix/resolve 引用的 Issue 编号） |
| **反常识** | 积分系统的核心不是"算分"而是"防重复"——ledger 的 eventKey 设计确保同一 PR 合并不会被多次计分（即使 Actions 重跑），PR 解决的 Issue 积分归 PR 作者而非关闭者（通过 GraphQL 查询关联关系），bot 用户自动忽略。这是一个典型的"事件溯源+幂等消费"架构，积分存储在独立分支而非 main 分支，避免积分更新污染代码历史。 |
| **行动** | 积分机制可复用为其他开源社区的贡献激励模板。关键点包括：①用独立分支存储积分数据避免污染主分支；②eventKey 设计覆盖所有事件类型确保幂等；③PR-Issue 关联通过 close/fix/resolve 关键字自动检测而非手动标记；④bot 用户和忽略名单通过环境变量可配置。 |

### 洞察 4：技能触发条件的精确描述决定加载时机

| 维度 | 内容 |
|------|------|
| **陈述** | SKILL.md frontmatter 中 `description` 字段和正文中的触发场景描述是 Agent **决定何时加载该技能**的唯一依据。好的触发条件描述包含三个要素：①**正面触发词**（用户说什么关键词时触发）、②**反面排除条件**（什么场景不适用）、③**能力边界声明**（能做什么/不能做什么）。触发条件的模糊或缺失会导致技能漏触发或误触发。 |
| **证据** | F-014（description 要求明确说明做什么以及何时使用，是 agent 决定是否加载的依据）、正面触发词证据：F-030（daily-hot-news 明确列出触发关键词："今日热搜""新闻热榜"等7个）、F-045（git-commit-generator 列出3种触发场景）、F-064（video-to-keyframes 列出8个触发关键词）、F-076（wechat-mini-program-development 列出4种触发场景）；反面排除证据：F-030（daily-hot-news 明确"不适用于历史新闻或特定领域深度分析"）、F-049（kz-article-deep-analysis 明确"不适用于学术论文或书籍"）；能力边界证据：F-020（cloudbase 约束条款：不得编造 API 路径、不得暴露凭证、失败2-3次后停止）、F-060（trae-claw-install 约束条款：复用仓库脚本、不写入密钥） |
| **反常识** | 多数开发者编写技能时倾向于详细描述"怎么做"（Instructions 步骤），却忽视"何时做"（触发条件）。但实际上对 Agent 而言，触发条件的精确性比步骤详细度更重要——步骤写得粗略 Agent 还能自行推理，触发条件模糊则 Agent 根本不会加载该技能，写得再好也无用。cn-punctuation-checker（F-028）甚至没有遵循标准章节结构，但凭借精确的功能描述仍能正常工作。 |
| **行动** | 编写 SKILL.md 时，description 字段必须包含"功能+触发场景"双重信息，正文应在 Description 或 Usage Scenario 章节明确列出触发关键词和排除条件。约束条款（什么不能做）与能力声明（什么能做）同等重要，能有效防止 Agent 越界操作。参考 daily-hot-news（F-030）的触发条件写法：正面关键词穷举 + 反面场景排除。 |

---

## 知识地图

### 学习路径

**入门（理解 SKILL.md 本质）**：
1. 阅读 `skills/_template/SKILL.md`，理解 YAML frontmatter + Markdown 指令体的基本结构（对应洞察 1）
2. 对比阅读纯 Prompt 型技能 `skills/git-commit-generator/SKILL.md`，理解最简技能的形态
3. 安装一个技能到 `.trae/skills/` 目录，观察 TRAE 如何通过 description 字段匹配触发

**核心（掌握三类模式与触发设计）**：
1. 纯 Prompt 型：精读 `skills/cn-punctuation-checker/SKILL.md`（非标准结构但功能完整的案例）和 `skills/wechat-mini-program-development/SKILL.md`（多步骤代码生成型）
2. 脚本辅助型：精读 `skills/daily-hot-news/SKILL.md` + `resources/scripts/fetch_news.py`，理解脚本与指令的协作方式
3. Workflow 编排型：精读 `skills/daily-trend-writer/SKILL.md`，理解 Phase 分解、subskills 调用、归档路径约定（对应洞察 2）
4. 触发条件设计：对比 F-030/F-045/F-049/F-064 中的正反触发条件写法（对应洞察 4）

**扩展（社区机制与复杂技能）**：
1. 社区积分机制：阅读 `.github/workflows/community-points.yml` + `.github/scripts/update-community-points.js`（对应洞察 3）
2. 复杂脚本技能：精读 `skills/video-to-keyframes/` 的 4 脚本流水线（dHash 转场检测、评分加权公式）
3. 验证工具：阅读 `skills/kz-article-deep-analysis/scripts/verify.py`，理解技能质量自检方法
4. API 集成技能：阅读 `skills/zopia_ai_skills/SKILL.md`，理解外部 API 认证、会话管理、错误码处理模式

### 概念-事实映射表

| 概念 | 关联事实 | 概念文档名（建议） |
|------|----------|-------------------|
| SKILL.md 文件格式 | F-004, F-010~F-015 | skill-md-format.md |
| 技能目录结构约定 | F-006~F-009 | skill-directory-structure.md |
| 技能触发条件设计 | F-014, F-030, F-045, F-049, F-060, F-064, F-076 | skill-trigger-design.md |
| 纯 Prompt 型技能模式 | F-043~F-047, F-074~F-079 | pure-prompt-skill-pattern.md |
| 脚本辅助型技能模式 | F-029~F-033, F-091~F-098 | script-assisted-skill-pattern.md |
| Workflow 编排型技能模式 | F-034~F-042, F-062~F-068, F-102~F-115 | workflow-skill-pattern.md |
| 社区积分自动化机制 | F-116~F-129 | community-points-mechanism.md |
| Subskills 子技能复用 | F-039~F-040, F-042 | subskills-reuse.md |
| 技能版本管理 | F-015, F-054, F-099~F-101 | skill-versioning-and-verification.md |
| 外部 API 集成模式 | F-080~F-090 | external-api-integration.md |

### 示例规划

| 示例文档名（建议） | 覆盖技能/场景 | 核心内容 |
|-------------------|-------------|---------|
| example-git-commit-generator.md | git-commit-generator | 输入 diff → 输出 Conventional Commits 格式信息的完整流程 |
| example-daily-hot-news.md | daily-hot-news | 配置平台/数量 → 运行 fetch_news.py → 格式化 Markdown 热榜输出 |
| example-video-keyframes.md | video-to-keyframes | 一键运行命令 → segments_gallery.html 确认分段 → gallery.html 复筛关键帧 |
| example-cloudbase-workflow.md | cloudbase | 绑定环境 → MCP 工具管理资源 → 实现前后端 → 部署与收尾 |
| example-wechat-miniprogram.md | wechat-mini-program-development | 8步搭建标准小程序项目：config.js → api.js → request.js → util.js → app.js |
| example-community-points-contribution.md | 社区积分 | 提交 PR → 自动触发积分 → 排行榜更新的完整链路 |

### 引用规划

| 信源文档名（建议） | 源文件路径 | 核心内容 |
|-------------------|-----------|---------|
| ref-skill-template.md | `skills/_template/SKILL.md` | 技能模板标准结构 |
| ref-fetch-news-script.md | `skills/daily-hot-news/resources/scripts/fetch_news.py` | 热榜数据抓取脚本（4层数据源降级策略） |
| ref-video-workflow-scripts.md | `skills/video-to-keyframes/resources/scripts/` | 视频抽帧与关键帧选择脚本集（dHash、评分公式、转场检测算法） |
| ref-community-points-action.md | `.github/workflows/community-points.yml` + `.github/scripts/update-community-points.js` | 社区积分 GitHub Actions 工作流与记账脚本 |
| ref-conventional-commits-types.md | `skills/git-commit-generator/resources/conventional-commits-types.md` | Conventional Commits 类型定义 |
| ref-zopia-api-reference.md | `skills/zopia_ai_skills/API_REFERENCE.md` | Zopia AI 视频制作 API 端点参考 |
