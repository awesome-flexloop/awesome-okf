---
type: spec
title: "trae-templates 核心洞察与知识地图"
---

# trae-templates 核心洞察与知识地图

## 核心洞察（四元组）

### 洞察 1：技术栈分面分类法——五维交叉的模板组织体系

| 维度 | 内容 |
|------|------|
| **陈述** | trae-templates 采用**五维分面分类法**（Faceted Classification）组织 23 个模板，而非传统的树状层级分类。五个分面为：web-frontend（Web前端，8个）、backend-service（后端服务，5个）、mobile-desktop（移动与桌面，3个）、data-ai（数据与AI，3个）、tools-devops（工具与DevOps，4个）。每个分面下按框架/技术栈进一步细分，同一技术领域（如"全栈开发"）的模板分散在不同分面中，用户按"目标平台+技术栈"双维度定位模板。 |
| **证据** | F-006~F-007（templates/ 目录下分5大类共23个模板，明确列出5个分类名称和数量）、Web前端分面证据：F-011~F-044（8个模板覆盖纯HTML/CSS/JS、React、Vue、Next.js、Nuxt、Svelte、Angular、Tailwind 全主流前端生态）、后端分面证据：F-045~F-069（5个模板覆盖 FastAPI、Node.js/Express、Go/Gin、Java/Spring Boot、Rust/Actix 五种主流后端语言/框架）、移动桌面证据：F-070~F-081（React Native/Expo、Flutter、Electron 三个跨平台方案）、Data/AI证据：F-082~F-095（Python脚本、Jupyter Notebook、PyTorch 训练脚本）、Tools/DevOps证据：F-096~F-117（Docker Compose、.editorconfig、.gitignore、superpowers-trae-init） |
| **反常识** | 与常见的"按语言分类"或"按框架分类"不同，五维分面的第一维度是**应用形态**（Web前端/后端服务/移动桌面/数据AI/工具DevOps），而非技术语言。这意味着同一个框架（如 React）同时出现在 web-frontend（react-starter）和 mobile-desktop（react-native）两个分面，但分面语义已经区分了使用场景。tools-devops 分类下的 superpowers-trae-init 不是传统意义上的"项目模板"，而是 IDE 工作流配置模板——它被纳入模板库是因为"复制即用"的使用方式与项目模板一致（F-004、F-107~F-111）。 |
| **行动** | 使用模板时应先确定应用形态分面（前端/后端/移动/AI/工具），再在该分面下选择技术栈。新增模板时需判断其所属分面，若跨分面（如全栈模板）应考虑拆分为前后端两个模板而非创建新分类。superpowers-trae-init 作为"非项目模板"的存在提示我们：模板库的收录标准是"复制即用"而非"必须是可运行项目"。 |

### 洞察 2：superpowers-trae-init 的 `.trae/` 配置驱动模式——4条铁律+工具映射+触发器字典

| 维度 | 内容 |
|------|------|
| **陈述** | superpowers-trae-init 不是传统项目脚手架，而是一个 **AI 开发工作流配置包**，通过 `.trae/` 目录下的规则文件和技能目录实现 TRAE IDE 的行为定制。其核心架构分三层：**①4条铁律**（NO FIX WITHOUT ROOT CAUSE / NO PRODUCTION CODE WITHOUT RED TEST / NO BLIND MOCKING / NO GUESSING THE OUTPUT）作为不可违反的约束；**②工具适配映射**（将 Agent 的通用工具如 TodoWrite/Task/manage_core_memory 映射到 TRAE 特定实现）；**③触发器字典**（将开发场景分类到架构计划/开发审查/排错闭环三组，每组对应一组应加载的技能）。 |
| **证据** | F-107~F-111（模板通过复制 `.trae/` 目录到项目根来生效，需手动添加核心记忆后新开会话加载）、F-112（核心记忆内容含4条约束：brainstorming→using-git-worktrees→writing-plans→test-driven-development→code-review→finish-branch 闭环）、F-113（4条铁律的详细定义，每条铁律都指向必须执行的技能，如 systematic-debugging）、F-114（Trae 工具适配强制映射：TodoWrite 替代 CLI 跟踪、Task 替代 spawn_agent、manage_core_memory 替代本地知识库；Task 派发必须两阶段审查）、F-115（触发器字典三类分组：架构与计划4个技能、开发与审查4个技能、排错与闭环4个技能）、F-116（`.trae/skills/` 下包含25+个技能子目录，构成完整的技能生态） |
| **反常识** | 传统项目模板提供的是"代码起点"，superpowers-trae-init 提供的是"AI 行为约束起点"——它不生成任何业务代码，而是通过规则和技能集改变 TRAE Agent 的开发行为模式。4条铁律本质上是 TDD（测试驱动开发）和系统化调试方法论在 AI 编码场景下的强制性转译。更反直觉的是，remembering-conversations 技能包含完整的 TypeScript 实现（13个 .ts 文件、SQLite/向量嵌入、会话索引与搜索），说明 `.trae/skills/` 下的"技能"可以包含真正的可执行代码实现，而非仅 Markdown 指令。 |
| **行动** | superpowers-trae-init 是 TRAE 项目"AI 开发契约"的参考实现。新团队采用时应：①复制 `.trae/` 目录到项目根；②在核心记忆中添加4条约束；③根据项目特点调整触发器字典中的技能列表。4条铁律可作为 AI 编码的质量门禁，其中"NO GUESSING THE OUTPUT"（禁止未运行就宣布完成）是防止 AI 幻觉的关键约束。工具适配映射提示：在自定义技能中应优先使用 TRAE 原生工具（TodoWrite/Task 等）而非模拟 CLI 工作流。 |

### 洞察 3：模板的"最小可用"设计原则——仅包含必需文件，拒绝多余脚手架

| 维度 | 内容 |
|------|------|
| **陈述** | 所有 23 个模板严格遵循**"最小可用"（Minimal Viable）设计原则**：每个模板仅包含该技术栈启动并运行所必需的最少文件，不包含多余的配置文件、依赖锁定文件、示例代码或文档脚手架。文件数量极度精简——最少的 web-basic 仅 5 个文件（含 README），nodejs-express 仅 5 个文件，go-gin-service 仅 5 个文件。每个模板提供一个可直接运行的主入口文件，README 说明启动方式。 |
| **证据** | F-009（所有模板均为极简启动模板，文件数量精简，不包含多余依赖锁定文件）、F-010（每个模板提供一个主入口文件，直接可运行或可编译）、F-012（web-basic 仅5文件：index.html/style.css/script.js + 双README）、F-016（react-starter 仅8文件，无 lockfile、无 eslint 配置、无测试框架）、F-024（nextjs-starter 仅8文件，无 app/globals.css、无 components/ 目录示例）、F-052（nodejs-express 仅5文件，单文件 index.js 服务器）、F-057（go-gin-service 仅5文件，单文件 main.go）、F-066（rust-actix 仅5文件，单文件 main.rs）、F-083（python-script 仅5文件，单文件 main.py）、F-101（editor-config 仅3文件，单文件 .editorconfig）、F-105（gitignore 仅4文件，两个 .gitignore 模板文件） |
| **反常识** | 这与官方 CLI 生成的模板形成鲜明对比——`create-react-app` 生成数十个配置文件和依赖，`vue-cli` 生成完整的项目结构含 router/store 示例，`express-generator` 生成完整 MVC 目录结构。trae-templates 的"最小可用"刻意反其道而行：**不替开发者做技术决策**。例如 react-starter 不包含路由库、状态管理、测试框架或 CSS 方案的选择（F-015~F-018，仅 React+Vite+CSS Modules）；python-script 仅提供 venv+logging 的最小约定（F-082~F-086），不指定 argparse/click/typer 等 CLI 框架。唯一例外是 svelte-starter 的 README 存在复制遗留错误（F-034，首行写"This template provides a minimal setup to get React working in Vite"），侧面印证了模板是手工极简制作而非 CLI 生成。 |
| **行动** | 使用模板时应将其视为"起点"而非"完整项目框架"，按需添加路由、状态管理、测试等依赖。贡献新模板时应遵循最小可用原则：①删除所有非必需配置文件；②单文件入口可运行；③不替用户选择辅助库；④README 双语说明启动命令。这种极简设计的好处是：不会因模板自带的过时依赖导致安全问题，不会因预设的目录结构限制开发者自由度，AI Agent 基于模板生成代码时也不会被多余脚手架干扰。 |

### 洞察 4：AGENTS.md 作为 AI 开发契约文件——模板与 TRAE IDE 的协作模式

| 维度 | 内容 |
|------|------|
| **陈述** | trae-templates 生态隐含了一个关键协作模式：**AGENTS.md 是 AI 开发的契约文件**，它定义了 AI Agent 在项目中应遵循的规则、工具映射和行为约束。superpowers-trae-init 通过 `.trae/rules/superpowers.md` 实现了这一契约，而普通项目模板（如 web-frontend、backend-service 下的模板）虽然未直接包含 AGENTS.md，但模板的 README.md 和 `.trae/` 目录结构暗示了 AI 协作的接入点——AGENTS.md 应作为项目级 AI 行为规范放置在项目根目录或 `.trae/rules/` 下，与代码文件同等重要。 |
| **证据** | F-108（superpowers-trae-init 的核心文件是 `.trae/rules/superpowers.md` 而非传统的配置文件）、F-110~F-111（快速开始流程：复制 .trae 目录 → 在 TRAE 中打开项目 → 手动添加核心记忆 → 新开会话加载规则和技能集）、F-113（superpowers.md 定义4条铁律，Agent 加载后必须遵守）、F-114（工具适配映射强制改变 Agent 的工具使用方式）、F-115（触发器字典控制技能的自动加载时机）、F-112（核心记忆作为持久化的项目级约束，关键词 superpowers|workflow|tdd|debugging|skills 触发记忆召回）；反向证据：F-079（wechat-mini-program-development 技能中标准项目结构包含 `.trae/` 目录，说明 `.trae/` 已成为 TRAE 项目的标准目录约定）、F-008（每个模板包含双语 README.md，是给人类看的文档；而 `.trae/` 下的规则文件是给 AI 看的指令——两者互补） |
| **反常识** | 传统项目模板的"配置文件"（如 .eslintrc、tsconfig.json、package.json）是给**编译器和工具链**看的，而 AGENTS.md / `.trae/rules/` 是给 **AI Agent** 看的"配置文件"。这意味着 AI-native 项目需要两种配置：机器配置（工具链）和 Agent 配置（行为规则）。superpowers-trae-init 的 25+ 个技能和铁律体系表明，Agent 配置的复杂度不亚于工具链配置——它需要定义工作流阶段、质量门禁、工具映射、技能路由等。这种"AI 契约文件"是软件开发中的新事物，传统项目模板库中没有对应概念。 |
| **行动** | 创建新模板时，除了代码文件和 README.md，还应考虑是否需要提供 `.trae/rules/` 下的 AI 行为规则文件。对于简单模板（如 web-basic），README 中的使用说明足够 AI 理解；对于复杂工作流（如 TDD 全流程），应提供类似 superpowers.md 的规则文件。AGENTS.md 放置在项目根目录是最直接的方式，`.trae/rules/` 适合放置模块化的规则片段。模板用户在复制模板后应审查并定制 AI 规则，确保 Agent 行为符合项目团队的开发规范。 |

---

## 知识地图

### 学习路径

**入门（理解模板分类与使用）**：
1. 浏览 templates/ 目录，建立五维分面分类的全局认知（对应洞察 1）
2. 以 web-basic 为起点，理解"最小可用"模板的文件构成（对应洞察 3）
3. 选择自己技术栈对应的模板（如 react-starter / fastapi-service），复制并运行，体验"复制即用"的使用方式

**核心（理解 superpowers 工作流与 AI 协作模式）**：
1. 精读 superpowers-trae-init 模板，理解 `.trae/` 目录的结构和作用（对应洞察 2、4）
2. 阅读 `.trae/rules/superpowers.md`，掌握4条铁律、工具适配映射和触发器字典
3. 浏览 `.trae/skills/` 下 25+ 个技能目录，理解技能生态如何支撑铁律执行
4. 实践：将 superpowers-trae-init 的 `.trae/` 目录复制到一个已有项目，体验 AI 开发契约的效果

**扩展（模板设计与贡献）**：
1. 对比同一分面下不同技术栈模板的文件结构差异（如 react-starter vs vue-starter vs svelte-starter）
2. 分析 remembering-conversations 技能的 TypeScript 实现，理解 `.trae/skills/` 下可包含代码级实现
3. 研究 tools-devops 分面下的配置模板（editor-config/gitignore/docker-compose），理解非项目模板的价值
4. 学习社区贡献规范，按最小可用原则设计新模板

### 概念-事实映射表

| 概念 | 关联事实 | 概念文档名（建议） |
|------|----------|-------------------|
| 五维分面分类体系 | F-006~F-007 | template-faceted-classification.md |
| 最小可用设计原则 | F-009~F-010, F-012, F-052, F-083 | minimal-viable-template-principle.md |
| Web 前端模板模式 | F-011~F-044 | web-frontend-templates.md |
| 后端服务模板模式 | F-045~F-069 | backend-service-templates.md |
| 移动桌面模板模式 | F-070~F-081 | mobile-desktop-templates.md |
| 数据 AI 模板模式 | F-082~F-095 | data-ai-templates.md |
| 工具 DevOps 模板模式 | F-096~F-117 | tools-devops-templates.md |
| Superpowers 铁律体系 | F-112~F-113 | superpowers-iron-rules.md |
| Trae 工具适配映射 | F-114 | trae-tool-adaptation-mapping.md |
| 触发器字典与技能路由 | F-115~F-116 | trigger-dictionary-skill-routing.md |
| .trae/ 配置驱动模式 | F-107~F-111, F-117 | trae-config-driven-pattern.md |
| AGENTS.md AI 开发契约 | F-108, F-110~F-115 | agents-md-ai-contract.md |
| 双语 README 规范 | F-008, F-005 | bilingual-readme-convention.md |

### 示例规划

| 示例文档名（建议） | 覆盖模板/场景 | 核心内容 |
|-------------------|-------------|---------|
| example-react-starter-setup.md | react-starter | Vite + React 18 从零到运行的完整流程（npm install → npm run dev） |
| example-fastapi-service-setup.md | fastapi-service | FastAPI 服务启动、Swagger UI 访问、自动文档查看 |
| example-superpowers-init.md | superpowers-trae-init | 复制 .trae/ → 添加核心记忆 → 新会话加载 → 4条铁律验证 |
| example-docker-compose-up.md | docker-compose | docker-compose up -d 启动 Nginx + PostgreSQL，验证服务可用性 |
| example-template-selection-guide.md | 全分面 | 根据项目需求（Web/后端/移动/AI/工具）选择合适模板的决策树 |
| example-custom-template-creation.md | 贡献指南 | 按最小可用原则创建一个新模板的步骤和检查清单 |

### 引用规划

| 信源文档名（建议） | 源文件路径 | 核心内容 |
|-------------------|-----------|---------|
| ref-superpowers-rules.md | `templates/tools-devops/superpowers-trae-init/.trae/rules/superpowers.md` | Superpowers 4条铁律、工具映射、触发器字典全文 |
| ref-template-file-structures.md | 各模板目录 | 各模板的完整文件清单和技术栈版本信息 |
| ref-superpowers-skills-catalog.md | `templates/tools-devops/superpowers-trae-init/.trae/skills/` | 25+ 技能目录的清单和分类索引 |
| ref-remembering-conversations.md | `templates/tools-devops/superpowers-trae-init/.trae/skills/remembering-conversations/` | 对话记忆技能的 TypeScript 实现（嵌入/索引/搜索） |
| ref-editor-config-rules.md | `templates/tools-devops/editor-config/.editorconfig` | 标准编辑器配置规则（charset/indent/EOF 等） |
| ref-gitignore-templates.md | `templates/tools-devops/gitignore/` | Node.js 和 Python 的 .gitignore 模板 |
| ref-docker-compose-config.md | `templates/tools-devops/docker-compose/docker-compose.yml` | Nginx + PostgreSQL 的 Docker Compose 服务配置 |
