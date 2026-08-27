---
type: Reference
title: Trae Templates 源码信源
description: trae-templates 项目中 23 个模板（5 大分类）的完整索引，包括每个模板的技术栈、文件结构、启动命令和关键特性。
tags: [trae-templates, reference, source, templates-index]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: facts
    title: trae-templates 源码事实清单
  - id: insights
    title: trae-templates 核心洞察与知识地图
---

## 项目概况

trae-templates 是 TRAE IDE 的社区维护项目模板集合，采用 MIT 许可证。项目位于社区仓库 `trae-community/trae-templates/`，包含 23 个极简启动模板，按 5 大分类组织。

- 使用方式：浏览目录 → 复制模板文件夹到目标位置或复制特定配置文件到已有项目 → 按模板内 README.md 自定义
- 贡献要求：模板必须包含详细的 README.md 说明使用方法
- 设计原则：最小可用（Minimal Viable），仅包含必需文件，拒绝多余脚手架

## 五维分面分类总览

| 分类 | 目录名 | 模板数量 | 包含模板 |
|------|--------|----------|----------|
| Web 前端 | web-frontend | 8 | web-basic、react-starter、vue-starter、nextjs-starter、nuxtjs-starter、svelte-starter、angular-starter、tailwind-starter |
| 后端服务 | backend-service | 5 | fastapi-service、nodejs-express、go-gin-service、java-springboot、rust-actix |
| 移动与桌面 | mobile-desktop | 3 | react-native、flutter-starter、electron-starter |
| 数据与 AI | data-ai | 3 | python-script、jupyter-notebook、pytorch-starter |
| 工具与 DevOps | tools-devops | 4 | docker-compose、editor-config、gitignore、superpowers-trae-init |

## Web Frontend 模板（8个）

### web-basic

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/web-basic/` |
| 技术栈 | 纯 HTML/CSS/JS，零构建工具 |
| 文件结构 | `index.html`、`style.css`、`script.js`、`README.md`、`README.zh-CN.md` |
| 特性 | HTML5 语义化结构、基础 CSS reset、空 JS 文件已链接、零配置 |
| 启动方式 | 直接在浏览器打开 index.html |

### react-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/react-starter/` |
| 技术栈 | React 18、Vite、CSS Modules、Node.js 16+ |
| 文件结构 | `index.html`、`package.json`、`vite.config.js`、`src/App.jsx`、`src/main.jsx`、`src/index.css`、`README.md`、`README.zh-CN.md` |
| npm scripts | `npm run dev`（localhost:5173）、`npm run build`、`npm run preview` |

### vue-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/vue-starter/` |
| 技术栈 | Vue 3（Composition API）、Vite、CSS、Node.js 16+ |
| 文件结构 | `index.html`、`package.json`、`vite.config.js`、`src/App.vue`、`src/main.js`、`src/style.css`、`README.md`、`README.zh-CN.md` |
| npm scripts | `npm run dev`（localhost:5173）、`npm run build`、`npm run preview` |

### nextjs-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/nextjs-starter/` |
| 技术栈 | React 18、Next.js 14（App Router）、TypeScript、Module Resolution: Bundler |
| 文件结构 | `package.json`、`tsconfig.json`、`next.config.mjs`、`.gitignore`、`app/layout.tsx`、`app/page.tsx`、`README.md`、`README.zh-CN.md` |
| 启动方式 | `npm install && npm run dev`（localhost:3000） |

### nuxtjs-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/nuxtjs-starter/` |
| 技术栈 | Vue 3、Nuxt 3、TypeScript |
| 文件结构 | `package.json`、`tsconfig.json`、`nuxt.config.ts`、`app.vue`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| npm scripts | `npm run dev`（localhost:3000）、`npm run build` |

### svelte-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/svelte-starter/` |
| 技术栈 | Svelte、Vite |
| 文件结构 | `index.html`、`package.json`、`vite.config.js`、`src/App.svelte`、`src/main.js`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| npm scripts | `npm run dev`、`npm run build` |
| 注意 | README 首行存在复制遗留（写"React working in Vite"），实际为 Svelte 模板 |

### angular-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/angular-starter/` |
| 技术栈 | Angular、TypeScript |
| 文件结构 | `package.json`、`tsconfig.json`、`.gitignore`、`src/main.ts`、`src/app/app.component.ts`、`src/app/app.config.ts`、`src/app/app.routes.ts`、`README.md`、`README.zh-CN.md` |
| npm scripts | `npm start`（localhost:4200，自动重载）、`npm run build`（输出到 dist/）、`npm test`（Karma 单元测试） |

### tailwind-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/web-frontend/tailwind-starter/` |
| 技术栈 | HTML、Tailwind CSS |
| 文件结构 | `package.json`、`tailwind.config.js`、`.gitignore`、`src/index.html`、`src/input.css`、`README.md`、`README.zh-CN.md` |
| npm scripts | `npm run build`（watch 模式编译 CSS 到 dist/output.css） |
| 启动方式 | `npm install → npm run build → 浏览器打开 src/index.html` |

## Backend Service 模板（5个）

### fastapi-service

| 属性 | 值 |
|------|-----|
| 路径 | `templates/backend-service/fastapi-service/` |
| 技术栈 | FastAPI、Uvicorn、Python 3.8+ |
| 文件结构 | `requirements.txt`、`app/main.py`、`README.md`、`README.zh-CN.md` |
| 启动命令 | `uvicorn app.main:app --reload`（localhost:8000） |
| 特性 | 自动交互式 API 文档（Swagger UI /docs、ReDoc /redoc）、Python 类型提示 |

### nodejs-express

| 属性 | 值 |
|------|-----|
| 路径 | `templates/backend-service/nodejs-express/` |
| 技术栈 | Node.js、Express、JavaScript |
| 文件结构 | `package.json`、`index.js`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动命令 | `npm install && npm start`（localhost:3000） |
| 端点 | `GET /` 返回 "Hello World!" |

### go-gin-service

| 属性 | 值 |
|------|-----|
| 路径 | `templates/backend-service/go-gin-service/` |
| 技术栈 | Go、Gin Web 框架 |
| 文件结构 | `go.mod`、`main.go`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动命令 | `go mod tidy && go run main.go`（localhost:8080） |
| 端点 | `GET /ping` 返回 `{"message": "pong"}` |

### java-springboot

| 属性 | 值 |
|------|-----|
| 路径 | `templates/backend-service/java-springboot/` |
| 技术栈 | Java 17+、Spring Boot、Maven |
| 文件结构 | `pom.xml`、`.gitignore`、`src/main/java/com/example/demo/DemoApplication.java`、`README.md`、`README.zh-CN.md` |
| 启动命令 | `mvn spring-boot:run`（localhost:8080） |

### rust-actix

| 属性 | 值 |
|------|-----|
| 路径 | `templates/backend-service/rust-actix/` |
| 技术栈 | Rust、Actix-web（需 rustup 安装 Rust） |
| 文件结构 | `Cargo.toml`、`src/main.rs`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动命令 | `cargo run`（127.0.0.1:8080） |
| 端点 | `GET /` 返回 "Hello World from Rust Actix!" |

## Mobile & Desktop 模板（3个）

### react-native

| 属性 | 值 |
|------|-----|
| 路径 | `templates/mobile-desktop/react-native/` |
| 技术栈 | React Native、Expo、JavaScript |
| 文件结构 | `package.json`、`App.js`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动方式 | `npm install → npm start → 用 Expo Go 扫描二维码（Android/iOS）或按 w 在浏览器打开` |

### flutter-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/mobile-desktop/flutter-starter/` |
| 技术栈 | Flutter、Dart |
| 文件结构 | `pubspec.yaml`、`lib/main.dart`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 说明 | README 为 Flutter 默认生成内容，包含官方文档和 Codelab 链接 |

### electron-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/mobile-desktop/electron-starter/` |
| 技术栈 | Electron、Node.js、HTML/JavaScript |
| 文件结构 | `package.json`、`main.js`、`index.html`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动方式 | `npm install → npm start` |

## Data & AI 模板（3个）

### python-script

| 属性 | 值 |
|------|-----|
| 路径 | `templates/data-ai/python-script/` |
| 技术栈 | Python 3.8+、venv、logging |
| 文件结构 | `main.py`、`requirements.txt`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 特性 | 预配置虚拟环境、内置日志（控制台+文件）、依赖管理、Python 专用 .gitignore |
| 启动方式 | `python -m venv venv → 激活 → pip install -r requirements.txt → python main.py` |

### jupyter-notebook

| 属性 | 值 |
|------|-----|
| 路径 | `templates/data-ai/jupyter-notebook/` |
| 技术栈 | Python、Jupyter |
| 文件结构 | `notebook.ipynb`、`requirements.txt`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动方式 | `pip install -r requirements.txt → jupyter notebook → 打开 notebook.ipynb` |

### pytorch-starter

| 属性 | 值 |
|------|-----|
| 路径 | `templates/data-ai/pytorch-starter/` |
| 技术栈 | Python、PyTorch |
| 文件结构 | `train.py`、`requirements.txt`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 启动方式 | `pip install -r requirements.txt → python train.py` |
| 特性 | 自动检测 CUDA 可用性，将模型/数据移至 GPU |

## Tools & DevOps 模板（4个）

### docker-compose

| 属性 | 值 |
|------|-----|
| 路径 | `templates/tools-devops/docker-compose/` |
| 文件结构 | `docker-compose.yml`、`.gitignore`、`README.md`、`README.zh-CN.md` |
| 服务定义 | web（Nginx，端口 80）、db（PostgreSQL 数据库） |
| 命令 | `docker-compose up -d`（启动）、`docker-compose down`（停止） |

### editor-config

| 属性 | 值 |
|------|-----|
| 路径 | `templates/tools-devops/editor-config/` |
| 文件结构 | `.editorconfig`、`README.md`、`README.zh-CN.md` |
| 配置规则 | root=true、charset=utf-8、indent_style=space、indent_size=2、end_of_line=lf、insert_final_newline=true、trim_trailing_whitespace=true；*.md 文件特殊规则；*.py 文件 indent_size=4 |
| 编辑器支持 | VS Code 需安装插件、JetBrains IDE/Visual Studio 原生支持、Sublime Text/Vim 需插件 |

### gitignore

| 属性 | 值 |
|------|-----|
| 路径 | `templates/tools-devops/gitignore/` |
| 文件结构 | `Node.gitignore`、`Python.gitignore`、`README.md`、`README.zh-CN.md` |
| 使用方式 | 选择对应技术栈的文件，复制到项目根目录并重命名为 .gitignore |

### superpowers-trae-init

| 属性 | 值 |
|------|-----|
| 路径 | `templates/tools-devops/superpowers-trae-init/` |
| 文件结构 | `README.md`、`README.zh-CN.md`（TEMPLATE_README.zh-CN.md）、`.trae/` 目录 |
| 来源 | 改编自 obra/superpowers（MIT 许可证），裁剪为 TRAE 导向设置 |
| 核心文件 | `.trae/rules/superpowers.md`（4条铁律+工具映射+触发器字典）、`.trae/skills/`（25+ 技能目录） |

**superpowers.md 4 条铁律**：
1. NO FIX WITHOUT ROOT CAUSE（禁止不查根因直接修复）
2. NO PRODUCTION CODE WITHOUT RED TEST（禁止测试失败前写生产代码）
3. NO BLIND MOCKING（禁止 Mock 行为，必须测试真实行为）
4. NO GUESSING THE OUTPUT（禁止未实际运行就宣布完成）

**工具适配强制映射**：
- TodoWrite 替代 CLI 输出跟踪
- Task 替代 spawn_agent 派发子代理（两阶段审查：Spec对齐度+代码质量）
- manage_core_memory 替代本地知识库

**触发器字典三类**：
- 架构与计划：brainstorming、writing-plans、when-stuck、simplification-cascades
- 开发与审查：subagent-driven-development、test-driven-development、testing-anti-patterns、requesting-code-review
- 排错与闭环：systematic-debugging、root-cause-tracing、condition-based-waiting、verification-before-completion

**`.trae/skills/` 中较完整的技能**：

| 技能目录 | 包含内容 |
|----------|----------|
| gardening-skills-wiki | analyze-search-gaps.sh、check-index-coverage.sh、check-links.sh、check-naming.sh、garden.sh 等 shell 脚本 |
| remembering-conversations | TypeScript 实现（13个 .ts 文件：db.ts/embeddings.ts/indexer.ts/search.ts/summarizer.ts 等），含 install-hook/index-conversations/search-conversations 三个入口脚本 |
| condition-based-waiting | example.ts 示例 |
| requesting-code-review | code-reviewer.md 参考文件 |
| root-cause-tracing | find-polluter.sh 脚本 |
| systematic-debugging | CREATION-LOG.md 和多个 test-pressure 文件 |
| testing-skills-with-subagents | examples/CLAUDE_MD_TESTING.md |
| using-superpowers | find-skills 和 skill-run 可执行脚本 |
| writing-skills | graphviz-conventions.dot 和 persuasion-principles.md |

## 模板共性特征

1. **双语 README**：每个模板目录均包含 README.md 和 README.zh-CN.md（superpowers-trae-init 中文文件名为 TEMPLATE_README.zh-CN.md）
2. **极简设计**：文件数量极度精简（最少 3 个文件，最多 8 个文件），不含多余配置和依赖锁定文件
3. **单入口可运行**：每个模板提供一个主入口文件，直接可运行或可编译
4. **零依赖锁定**：不提供 lock 文件，开发者自行选择包管理器版本

## 相关概念

- [Trae Templates 简介](../concepts/00-introduction.md)
- [五维分面分类体系](../concepts/01-template-classification.md)
- [Web 前端模板](../concepts/02-web-frontend-templates.md)
- [后端服务模板](../concepts/03-backend-templates.md)
- [移动端和桌面端模板](../concepts/04-mobile-desktop-templates.md)
- [数据与 AI 模板](../concepts/05-data-ai-templates.md)
- [工具与 DevOps 模板](../concepts/06-tools-devops-templates.md)
- [AGENTS.md 开发契约](../concepts/07-agents-contract.md)

## 相关示例

- [使用 Next.js 模板创建项目](../examples/use-nextjs-template.md)
- [使用 superpowers-trae-init 初始化环境](../examples/use-superpowers-init.md)
- [创建自定义模板](../examples/create-custom-template.md)
- [AGENTS.md 配置示例](../examples/agents-md-config.md)
