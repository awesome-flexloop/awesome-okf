# TRAE Learning 源码事实清单

## 项目基本信息

- F-001: 项目 npm 包名为 `trae-learning-projects`，版本 `1.0.0`，描述为"学习园区"，license 为 ISC，type 为 `module`。来源：package.json
- F-002: 项目仓库地址为 `https://github.com/trae-community/trae-learning-projects`，Issues 地址指向同一仓库。来源：package.json
- F-003: 项目开发依赖为 `vitepress: ^1.6.4` 和 `vue: ^3.5.27`，无运行时依赖。来源：package.json
- F-004: npm scripts 定义了三条命令：`docs:dev`（vitepress dev）、`docs:build`（vitepress build）、`docs:preview`（vitepress preview）。来源：package.json
- F-005: 项目根目录包含 LICENSE、README.md、README.zh-CN.md、CONTRIBUTING.md、CONTRIBUTING.zh-CN.md、.gitignore 文件。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-learning\`

## VitePress 站点配置

- F-006: VitePress 配置设置 `base: '/trae-learning/'`，站点标题为 "TRAE Learning"，描述为 "Vibecoding 进阶指南"。来源：config.js
- F-007: 站点强制暗色模式（`appearance: 'force-dark'`），启用 cleanUrls，设置 `ignoreDeadLinks: true`。来源：config.js
- F-008: 站点 logo 使用 GitHub 头像 URL：`https://avatars.githubusercontent.com/u/257951088`。来源：config.js
- F-009: 顶部导航栏包含两个入口："指南"（链接 `/guide/what-is-vibecoding`）和"社区教程"（链接 `/tutorials/`）。来源：config.js
- F-010: 社交链接为 GitHub 图标，指向 `https://github.com/trae-community/trae-learning-projects`。来源：config.js
- F-011: `/guide/` 侧边栏分组"核心理念"包含 4 个条目：什么是 Vibecoding、心流与效率、Prompt 工程指南、最佳实践。来源：config.js
- F-012: `/tutorials/` 侧边栏分组"实战教程"包含 6 个条目：入门项目、REST API、React 组件、自动化测试、系统设计、性能优化。来源：config.js

## 主题与自定义组件

- F-013: 自定义主题继承自 VitePress DefaultTheme，导入 `custom.css`、`VibeHero.vue` 和 `HomeFeatures.vue`，并注册为全局 Vue 组件。来源：index.js
- F-014: 主题 CSS 定义品牌主色为 `#0FDC78`（绿色），搭配黑色背景和白色文字，使用 Inter 和 JetBrains Mono 字体。来源：custom.css
- F-015: 主题 CSS 强制所有 VitePress 布局容器（VPContent、VPHome、VPDoc、VPPage、Layout）背景为 `#000000`。来源：custom.css
- F-016: 主题 CSS 隐藏了外观切换按钮（`.VPNavBarAppearance`、`.VPSwitchAppearance` 设置为 `display: none`）。来源：custom.css
- F-017: 主题 CSS 定义了三种动画关键帧：`pulse-glow`、`float`、`fade-in-up`，以及三个发光工具类 `glow-sm`、`glow-md`、`glow-lg`。来源：custom.css
- F-018: 主题 CSS 在 `@media (max-width: 768px)` 断点处调整了 feature 卡片 padding/border-radius 和 manifesto 区域边距。来源：custom.css

## VibeHero 首页组件

- F-019: VibeHero 组件使用 Canvas 2D 绘制一个旋转的 3D 地球仪（程序化生成纹理，60 纬度 × 100 经度网格），位于页面右侧（cx = w*0.66, cy = h*0.46）。来源：VibeHero.vue
- F-020: VibeHero 地球纹理使用 140×70 Float32Array 存储，通过多层正弦/余弦函数叠加（6 层不同频率）模拟大陆轮廓，应用 `Math.pow(val, 0.75)` 校正。来源：VibeHero.vue
- F-021: VibeHero 在地球外围漂浮 18 个代码符号（包括 `{}`、`</>`、`AI`、`fn()`、`#`、`vibe`、`=>`、`$`、`%`、`code`、`let`、`[]`、`git`、`<div>`、`npm`、`class`、`&&`、`0xFF`），使用 JetBrains Mono 字体渲染。来源：VibeHero.vue
- F-022: VibeHero 包含 40 个闪烁粒子（sparkles），随机分布在球面，根据相位和速度产生闪烁效果，仅在 flicker > 0.6 时渲染。来源：VibeHero.vue
- F-023: VibeHero 绘制了 12 条经线和 7 条纬线（1-7 纬度）作为网格线，颜色为 `rgba(15, 220, 120, 0.04)`。来源：VibeHero.vue
- F-024: VibeHero 地球倾角常量 `TILT = 0.38` 弧度，旋转速度为每帧 `angle += 0.002`。来源：VibeHero.vue
- F-025: VibeHero 模板包含一个 "AI-Powered Development" 徽章（带闪烁绿点）、大标题 "TRAE LEARNING"（LEARNING 使用渐变色）、副标题 "The Art of Vibecoding / 探索 AI 辅助开发的无限可能"。来源：VibeHero.vue
- F-026: VibeHero 包含两个按钮："开始学习"（绿色主按钮，链接到 guide/what-is-vibecoding）和"浏览教程"（幽灵按钮，链接到 tutorials/）。来源：VibeHero.vue
- F-027: VibeHero 组件在 onUnmounted 中取消 requestAnimationFrame 并移除 resize 事件监听。来源：VibeHero.vue

## HomeFeatures 组件

- F-028: HomeFeatures 组件展示 4 个功能特性，采用左右交替布局（偶数项 direction: rtl），每项左侧文字描述 + 右侧玻璃拟态代码卡片。来源：HomeFeatures.vue
- F-029: HomeFeatures 的 4 个特性分别为："心流编码"（typescript 代码示例）、"极速反馈"（prompt 代码示例）、"专家共建"（yaml 代码示例）、"技术审美"（javascript 代码示例）。来源：HomeFeatures.vue
- F-030: HomeFeatures 实现了自定义语法高亮函数 `hl(code, lang)`，支持 prompt/yaml/js/ts 四种语言，使用正则匹配关键字、字符串、注释、函数调用、数字等。来源：HomeFeatures.vue
- F-031: HomeFeatures 代码卡片使用 macOS 风格窗口装饰（红黄绿三个圆点），右上角显示语言标签。来源：HomeFeatures.vue
- F-032: HomeFeatures 左侧有一个跟随鼠标/滚动的绿色光条（light-bar），包含 bloom/glow/core/line 四层渐变效果，通过 CSS 变量 `--light-y` 控制垂直位置。来源：HomeFeatures.vue
- F-033: HomeFeatures 在特性列表下方展示一个 Manifesto 区块，引用文字为"在 AI 时代，编程的门槛正在消失，而审美的价值正在凸显……"，署名"— TRAE Community"。来源：HomeFeatures.vue
- F-034: HomeFeatures 在 `@media (max-width: 900px)` 隐藏光条，在 `@media (max-width: 768px)` 将特性改为单列布局。来源：HomeFeatures.vue

## 首页与目录结构

- F-035: 首页 `index.md` 使用 `layout: home` frontmatter，仅包含 `<VibeHero />` 和 `<HomeFeatures />` 两个自定义组件，无其他 Markdown 内容。来源：index.md
- F-036: `guide/` 目录包含 4 个 Markdown 文件：what-is-vibecoding.md、flow-and-efficiency.md、prompt-engineering.md、best-practices.md。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-learning\guide\`
- F-037: `tutorials/` 目录包含 7 个 Markdown 文件：index.md、getting-started.md、rest-api.md、react-components.md、automated-testing.md、system-design.md、performance-optimization.md。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-learning\tutorials\`

## 指南内容（guide/）

- F-038: `what-is-vibecoding.md` 定义 Vibecoding 三个核心特征：心流驱动（Flow State）、意图传达（Intentionality）、即时反馈（Instant Loops）。来源：what-is-vibecoding.md
- F-039: `flow-and-efficiency.md` 列举三类打断心流的因素：语法和 API 查询、样板代码、不确定性焦虑，并给出四个习惯建议：拆小任务、Prompt 先于代码、不要盲接、及时提交。来源：flow-and-efficiency.md
- F-040: `prompt-engineering.md` 给出一个具体 Prompt 示例（Next.js + NextAuth 邮箱密码登录，含表单校验、加载状态、跳转逻辑），并列出四个技巧：给上下文不给废话、说清约束条件、分步处理复杂任务、不满意就直说。来源：prompt-engineering.md
- F-041: `best-practices.md` 提出五条最佳实践：看懂再提交、安全问题不能交给 AI 把关（SQL 注入/密钥/输入校验）、测试不能省、提交要小要频繁、对 AI 保持合理期望。来源：best-practices.md
- F-042: `best-practices.md` 列出了 AI 擅长的领域（样板代码、设计模式、解释代码、优化建议）和不那么可靠的领域（项目特有业务上下文、最新知识、跨文件复杂重构一致性）。来源：best-practices.md

## 教程内容（tutorials/）

- F-043: `tutorials/index.md` 将 6 个教程分为三级：入门项目（getting-started/rest-api，⭐-⭐⭐）、进阶项目（react-components/automated-testing，⭐⭐-⭐⭐⭐）、高级主题（system-design/performance-optimization，⭐⭐⭐⭐）。来源：index.md
- F-044: `getting-started.md` 教程项目为天气查询页面（纯 HTML+CSS+JS，调用 OpenWeatherMap API），分四步：描述需求、看懂代码、填入 API Key 运行、迭代改进。来源：getting-started.md
- F-045: `rest-api.md` 教程项目为 Node.js + Express 任务管理 API（CRUD：GET/POST/PUT/DELETE /tasks），分四步：生成项目骨架、逐个实现路由、加入请求校验、整理为 MVC 结构。来源：rest-api.md
- F-046: `react-components.md` 教程项目为 React + TypeScript TodoList 应用（create-react-app --template typescript），分三步：生成 TodoList 组件、拆分为 TodoInput/TodoItem/TodoList 三个子组件、加 localStorage 持久化，并提供完整代码参考。来源：react-components.md
- F-047: `automated-testing.md` 基于 REST API 教程项目，使用 Jest + supertest，分三步：AI 生成测试用例、运行并修复、覆盖更多场景，并指导配置 GitHub Actions CI。来源：automated-testing.md
- F-048: `system-design.md` 以短链服务（类 bit.ly）为例，分四步：从模糊需求开始（让 AI 提问）、估算规模（日活 100 万/短链保留 3 年）、设计数据模型（PostgreSQL/Base62 编码/索引）、讨论关键决策点并实现核心路径。来源：system-design.md
- F-049: `performance-optimization.md` 强调"先测量再优化"原则，涵盖前端（React 重渲染/长列表/打包体积）和后端（数据库慢查询/N+1 问题/缓存），给出测量→定位→优化→验证→提交的五步工作流。来源：performance-optimization.md

## CI/CD 部署配置

- F-050: GitHub Actions 部署工作流 `deploy.yml` 在 push 到 main 分支或手动触发（workflow_dispatch）时运行，包含 build 和 deploy 两个 job。来源：deploy.yml
- F-051: build job 在 ubuntu-latest 上运行，使用 Node.js 20，步骤为：checkout（fetch-depth: 0）、setup-node（npm 缓存）、configure-pages、npm ci、npm run docs:build、upload-pages-artifact（路径 .vitepress/dist）。来源：deploy.yml
- F-052: deploy job 需要 build job 完成，在 github-pages 环境中使用 actions/deploy-pages@v4 部署。来源：deploy.yml

## Issue 模板

- F-053: Issue 模板配置 `config.yml` 提供两个联系链接：中文"讨论区（学习交流/问题求助）"和英文"Discussion Forum (Learning Exchange/Q&A)"，均指向 `https://github.com/orgs/trae-community/discussions`。来源：config.yml
- F-054: `learning_path.yml` 模板标题前缀为"[路线] "，标签为 `["learning-path", "enhancement"]`，表单字段包括：主题（必填 input）、面向人群（必填 dropdown：零基础/转行入门/有经验开发者/其他）、学完效果（必填 textarea）、章节建议（可选 textarea）、参考资料（可选 textarea）。来源：learning_path.yml
- F-055: `resource_bug.yml` 模板标题前缀为"[资源问题] "，标签为 `["bug", "resource"]`，表单字段包括：出问题位置（必填 input）、问题描述（必填 textarea）、修改建议（可选 textarea）。来源：resource_bug.yml
- F-056: ISSUE_TEMPLATE 目录下共有 7 个 YAML 文件：config.yml、learning_path.yml、learning_path_en.yml、resource_bug.yml、resource_bug_en.yml、resource_request.yml、resource_request_en.yml。其中 resource_bug_en.yml 为空文件。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-learning\.github\ISSUE_TEMPLATE\`

## 资源目录

- F-057: 项目包含 `assets/image/` 目录，其中有 `Learning.gif` 资源文件。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-learning\assets\image\`
