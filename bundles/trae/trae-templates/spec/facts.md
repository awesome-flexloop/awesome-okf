# trae-templates 源码事实清单

## 项目信息

- F-001: 项目位于 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-templates\`，是 TRAE IDE 的社区维护项目模板集合，采用 MIT 许可证。
- F-002: 项目根目录包含 `README.md`、`README.zh-CN.md`、`CONTRIBUTING.md`、`CONTRIBUTING.zh-CN.md`、`LICENSE`、`.gitignore`。
- F-003: 项目包含 `assets/image/Templates.gif` 作为 Templates Banner 图片。
- F-004: 使用方式：浏览目录 → 复制模板文件夹到目标位置或复制特定配置文件到已有项目 → 按模板内 README.md 自定义。
- F-005: 贡献要求：模板必须包含详细的 README.md 说明使用方法。

## 模板分类体系

- F-006: 模板统一存放在 `templates/` 目录下，分为 5 大类，共 23 个模板。
- F-007: 5 大分类为：web-frontend（Web前端，8个）、backend-service（后端服务，5个）、mobile-desktop（移动与桌面，3个）、data-ai（数据与AI，3个）、tools-devops（工具与DevOps，4个）。

## 目录结构特征

- F-008: 每个模板目录均包含 `README.md` 和 `README.zh-CN.md` 双语说明文件（superpowers-trae-init 仅含 README.md）。
- F-009: 所有模板均为极简启动模板，文件数量精简，不包含多余依赖锁定文件（部分有 .gitignore）。
- F-010: 每个模板提供一个主入口文件，直接可运行或可编译。

## Web Frontend 模板（8个）

### web-basic

- F-011: 路径 `templates/web-frontend/web-basic/`，纯 HTML/CSS/JS 静态页面模板，零构建工具。
- F-012: 文件结构：`index.html`、`style.css`、`script.js`、`README.md`、`README.zh-CN.md`，共5个文件（含README）。
- F-013: 特性：HTML5 语义化结构、基础 CSS reset 和样式、空 JS 文件已链接、零配置。
- F-014: 启动方式：直接在浏览器打开 index.html。

### react-starter

- F-015: 路径 `templates/web-frontend/react-starter/`，基于 Vite 的 React 18 启动模板。
- F-016: 文件结构：`index.html`、`package.json`、`vite.config.js`、`src/App.jsx`、`src/main.jsx`、`src/index.css`、`README.md`、`README.zh-CN.md`。
- F-017: 技术栈：React 18、Vite、CSS Modules，Node.js 16+。
- F-018: npm scripts：`npm run dev`（启动开发服务器，localhost:5173）、`npm run build`（生产构建）、`npm run preview`（预览生产构建）。

### vue-starter

- F-019: 路径 `templates/web-frontend/vue-starter/`，基于 Vite 的 Vue 3 启动模板，使用 Composition API。
- F-020: 文件结构：`index.html`、`package.json`、`vite.config.js`、`src/App.vue`、`src/main.js`、`src/style.css`、`README.md`、`README.zh-CN.md`。
- F-021: 技术栈：Vue 3、Vite、CSS，Node.js 16+。
- F-022: npm scripts 与 react-starter 相同（dev/build/preview），开发端口 localhost:5173。

### nextjs-starter

- F-023: 路径 `templates/web-frontend/nextjs-starter/`，Next.js 14 + TypeScript 模板（App Router）。
- F-024: 文件结构：`package.json`、`tsconfig.json`、`next.config.mjs`、`.gitignore`、`app/layout.tsx`、`app/page.tsx`、`README.md`、`README.zh-CN.md`。
- F-025: 技术栈：React 18、Next.js 14（App Router）、TypeScript、Module Resolution: Bundler。
- F-026: 启动方式：npm/yarn/pnpm install → npm run dev → localhost:3000。

### nuxtjs-starter

- F-027: 路径 `templates/web-frontend/nuxtjs-starter/`，Nuxt 3 极简模板。
- F-028: 文件结构：`package.json`、`tsconfig.json`、`nuxt.config.ts`、`app.vue`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-029: 技术栈：Vue 3、Nuxt 3、TypeScript。
- F-030: npm scripts：`npm run dev`（开发服务器，localhost:3000）、`npm run build`（生产构建）。

### svelte-starter

- F-031: 路径 `templates/web-frontend/svelte-starter/`，Svelte + Vite 模板。
- F-032: 文件结构：`index.html`、`package.json`、`vite.config.js`、`src/App.svelte`、`src/main.js`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-033: 技术栈：Svelte、Vite。
- F-034: 注意：README 描述首行写"This template provides a minimal setup to get React working in Vite"（疑似复制遗留，实际为 Svelte）。
- F-035: npm scripts：`npm run dev`（开发）、`npm run build`（生产构建）。

### angular-starter

- F-036: 路径 `templates/web-frontend/angular-starter/`，Angular CLI 生成的启动模板。
- F-037: 文件结构：`package.json`、`tsconfig.json`、`.gitignore`、`src/main.ts`、`src/app/app.component.ts`、`src/app/app.config.ts`、`src/app/app.routes.ts`、`README.md`、`README.zh-CN.md`。
- F-038: 技术栈：Angular、TypeScript。
- F-039: npm scripts：`npm start`（开发服务器，localhost:4200，自动重载）、`npm run build`（构建到 dist/）、`npm test`（Karma 单元测试）。

### tailwind-starter

- F-040: 路径 `templates/web-frontend/tailwind-starter/`，Tailwind CSS + HTML 启动模板。
- F-041: 文件结构：`package.json`、`tailwind.config.js`、`.gitignore`、`src/index.html`、`src/input.css`、`README.md`、`README.zh-CN.md`。
- F-042: 技术栈：HTML、Tailwind CSS。
- F-043: npm scripts：`npm run build`（watch 模式编译 CSS，输出到 dist/output.css）。
- F-044: 启动方式：npm install → npm run build → 在浏览器打开 src/index.html。

## Backend Service 模板（5个）

### fastapi-service

- F-045: 路径 `templates/backend-service/fastapi-service/`，基于 FastAPI 的高性能 API 服务模板。
- F-046: 文件结构：`requirements.txt`、`app/main.py`、`README.md`、`README.zh-CN.md`。
- F-047: 技术栈：FastAPI、Uvicorn、Python 3.8+。
- F-048: 启动命令：`uvicorn app.main:app --reload`（localhost:8000）。
- F-049: 自动文档：Swagger UI 在 /docs，ReDoc 在 /redoc。
- F-050: 特性：自动交互式 API 文档、Python 类型提示。

### nodejs-express

- F-051: 路径 `templates/backend-service/nodejs-express/`，Express.js 极简服务器模板。
- F-052: 文件结构：`package.json`、`index.js`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-053: 技术栈：Node.js、Express、JavaScript。
- F-054: 启动命令：`npm install && npm start`（localhost:3000）。
- F-055: 端点：`GET /` 返回 "Hello World!"。

### go-gin-service

- F-056: 路径 `templates/backend-service/go-gin-service/`，Go + Gin Web 框架 REST API 模板。
- F-057: 文件结构：`go.mod`、`main.go`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-058: 技术栈：Go、Gin。
- F-059: 启动命令：`go mod tidy && go run main.go`（localhost:8080）。
- F-060: 端点：`GET /ping` 返回 JSON `{"message": "pong"}`。

### java-springboot

- F-061: 路径 `templates/backend-service/java-springboot/`，Spring Boot 极简应用模板。
- F-062: 文件结构：`pom.xml`、`.gitignore`、`src/main/java/com/example/demo/DemoApplication.java`、`README.md`、`README.zh-CN.md`。
- F-063: 技术栈：Java 17+、Spring Boot、Maven。
- F-064: 启动命令：`mvn spring-boot:run`（localhost:8080）。

### rust-actix

- F-065: 路径 `templates/backend-service/rust-actix/`，Rust + Actix Web 服务模板。
- F-066: 文件结构：`Cargo.toml`、`src/main.rs`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-067: 技术栈：Rust、Actix-web，需要 rustup 安装 Rust。
- F-068: 启动命令：`cargo run`（127.0.0.1:8080）。
- F-069: 端点：`GET /` 返回 "Hello World from Rust Actix!"。

## Mobile & Desktop 模板（3个）

### react-native

- F-070: 路径 `templates/mobile-desktop/react-native/`，React Native（Expo）极简应用。
- F-071: 文件结构：`package.json`、`App.js`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-072: 技术栈：React Native、Expo、JavaScript。
- F-073: 启动方式：npm install → npm start → 用 Expo Go 扫描二维码（Android/iOS）或按 w 在浏览器打开。

### flutter-starter

- F-074: 路径 `templates/mobile-desktop/flutter-starter/`，Flutter 新项目模板。
- F-075: 文件结构：`pubspec.yaml`、`lib/main.dart`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-076: 技术栈：Flutter、Dart。
- F-077: README 为 Flutter 默认生成内容，包含官方文档和 Codelab 链接，无具体启动命令说明。

### electron-starter

- F-078: 路径 `templates/mobile-desktop/electron-starter/`，Electron 极简桌面应用。
- F-079: 文件结构：`package.json`、`main.js`、`index.html`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-080: 技术栈：Electron、Node.js、HTML/JavaScript。
- F-081: 启动方式：npm install → npm start。

## Data & AI 模板（3个）

### python-script

- F-082: 路径 `templates/data-ai/python-script/`，Python 脚本标准样板。
- F-083: 文件结构：`main.py`、`requirements.txt`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-084: 技术栈：Python 3.8+、venv、logging。
- F-085: 特性：预配置虚拟环境、内置日志（控制台+文件）、依赖管理、Python 专用 .gitignore。
- F-086: 启动方式：python -m venv venv → 激活 → pip install -r requirements.txt → python main.py。

### jupyter-notebook

- F-087: 路径 `templates/data-ai/jupyter-notebook/`，Jupyter Notebook 数据分析启动模板。
- F-088: 文件结构：`notebook.ipynb`、`requirements.txt`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-089: 技术栈：Python、Jupyter。
- F-090: 启动方式：pip install -r requirements.txt → jupyter notebook → 打开 notebook.ipynb。

### pytorch-starter

- F-091: 路径 `templates/data-ai/pytorch-starter/`，PyTorch 深度学习训练脚本模板。
- F-092: 文件结构：`train.py`、`requirements.txt`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-093: 技术栈：Python、PyTorch。
- F-094: 启动方式：pip install -r requirements.txt → python train.py。
- F-095: 特性：自动检测 CUDA 可用性，将模型/数据移至 GPU。

## Tools & DevOps 模板（4个）

### docker-compose

- F-096: 路径 `templates/tools-devops/docker-compose/`，Docker Compose 启动配置。
- F-097: 文件结构：`docker-compose.yml`、`.gitignore`、`README.md`、`README.zh-CN.md`。
- F-098: 服务定义：web（Nginx，端口80）、db（PostgreSQL 数据库）。
- F-099: 命令：`docker-compose up -d`（启动）、`docker-compose down`（停止）。

### editor-config

- F-100: 路径 `templates/tools-devops/editor-config/`，标准 .editorconfig 配置文件。
- F-101: 文件结构：`.editorconfig`、`README.md`、`README.zh-CN.md`。
- F-102: 配置规则：root=true、所有文件 charset=utf-8、indent_style=space、indent_size=2、end_of_line=lf、insert_final_newline=true、trim_trailing_whitespace=true；*.md 文件 insert_final_newline=false、trim_trailing_whitespace=false；*.py 文件 indent_size=4。
- F-103: README 包含编辑器支持表：VS Code 需安装插件、JetBrains IDE/Visual Studio 原生支持、Sublime Text/Vim 需插件。

### gitignore

- F-104: 路径 `templates/tools-devops/gitignore/`，.gitignore 模板集合。
- F-105: 文件结构：`Node.gitignore`、`Python.gitignore`、`README.md`、`README.zh-CN.md`。
- F-106: 使用方式：选择对应技术栈的文件，复制到项目根目录并重命名为 .gitignore。

### superpowers-trae-init

- F-107: 路径 `templates/tools-devops/superpowers-trae-init/`，为 TRAE 项目初始化 Superpowers 工作流的模板。
- F-108: 文件结构：`README.md`、`README.zh-CN.md`（注意：中文文件名为 TEMPLATE_README.zh-CN.md）、`.trae/` 目录。
- F-109: 来源：改编自 obra/superpowers（MIT 许可证），裁剪并重新打包为 TRAE 导向的设置。
- F-110: 包含内容：`.trae/rules/superpowers.md`（Superpowers 核心指令文件）、`.trae/skills/`（大量技能目录）。
- F-111: 快速开始方式：复制 .trae 目录到项目根 → 在 TRAE 中打开项目 → 手动添加项目级核心记忆 → 新开会话让 TRAE 加载规则和技能集。
- F-112: 需要手动添加的项目级核心记忆标题为"Superpowers 严格工作流约束"，关键词 superpowers|workflow|tdd|debugging|skills，内容包含 4 条约束：①严禁未经设计直接写代码，必须执行 brainstorming→using-git-worktrees→writing-plans→test-driven-development→code-review→finish-branch 闭环 ②Debug 时禁止猜测，必须调用 systematic-debugging ③技能必须通过 Skill 工具真实执行 ④遇到卡壳使用 when-stuck 等技能。
- F-113: `.trae/rules/superpowers.md` 定义 4 条"铁律"：NO FIX WITHOUT ROOT CAUSE（禁止不查根因直接修复，必须执行 systematic-debugging）、NO PRODUCTION CODE WITHOUT RED TEST（禁止测试失败前写生产代码）、NO BLIND MOCKING（禁止 Mock 行为，必须测试真实行为）、NO GUESSING THE OUTPUT（禁止未实际运行就宣布完成）。
- F-114: `.trae/rules/superpowers.md` 定义 Trae 工具适配强制映射：TodoWrite 替代 CLI 输出跟踪、Task 替代 spawn_agent 派发子代理（必须两阶段审查：Spec对齐度+代码质量）、manage_core_memory 替代本地知识库。
- F-115: `.trae/rules/superpowers.md` 包含触发器字典，分三类：架构与计划（brainstorming/writing-plans/when-stuck/simplification-cascades）、开发与审查（subagent-driven-development/test-driven-development/testing-anti-patterns/requesting-code-review）、排错与闭环（systematic-debugging/root-cause-tracing/condition-based-waiting/verification-before-completion）。
- F-116: `.trae/skills/` 下包含 25+ 个技能子目录，每个包含 SKILL.md，其中较完整的技能包括：
  - gardening-skills-wiki：包含 analyze-search-gaps.sh、check-index-coverage.sh、check-links.sh、check-naming.sh、garden.sh 等 shell 脚本
  - remembering-conversations：包含完整 TypeScript 工具实现（tool/ 目录下有 hooks/sessionEnd、prompts/search-agent.md、src/ 下 db.ts/embeddings.ts/indexer.ts/search.ts/summarizer.ts 等13个 .ts 文件、package.json/tsconfig.json、安装和测试脚本）
  - condition-based-waiting：包含 example.ts 示例文件
  - requesting-code-review：包含 code-reviewer.md 参考文件
  - root-cause-tracing：包含 find-polluter.sh 脚本
  - systematic-debugging：包含 CREATION-LOG.md 和多个 test-pressure 文件
  - testing-skills-with-subagents：包含 examples/CLAUDE_MD_TESTING.md
  - using-superpowers：包含 find-skills 和 skill-run 可执行脚本
  - writing-skills：包含 graphviz-conventions.dot 和 persuasion-principles.md
- F-117: remembering-conversations 技能包含 install-hook（安装钩子）、index-conversations（索引对话）、search-conversations（搜索对话）三个入口脚本。
