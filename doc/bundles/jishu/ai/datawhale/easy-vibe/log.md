# 变更日志

本文件记录 Easy-Vibe OKF 知识包的版本演进。

## v0.1.0 — 2026-08-23

### 新增

- 初始知识包生成，遵循精简 R→I→E→V 流程。
- **R 阶段**：阅读 README.md、AGENTS.md、CLAUDE.md、llms.txt、docs/index.md、docs/zh-cn/index.md、docs/welcome.md、docs/DEPLOYMENT.md、docs/zh-cn/guide/introduction.md、docs/.vitepress/config.mjs、docs/.vitepress/theme/index.js、docs/.vitepress/theme/components/WelcomeScreen.vue、scripts/build-locales.mjs、scripts/README.md、package.json、vercel.json、Dockerfile、.github/workflows/deploy.yml、.github/workflows/release-books.yml，采集 19 组编号事实（F-001 ~ F-019）。
- **I 阶段**：提炼 3 个架构洞察：
  1. Vibe Coding 教育范式——"先做产品，再学技术"的路径反转
  2. 10 语言站点的真正复杂度在构建系统，不在翻译
  3. 文档站同时为人类读者与 AI Agent 设计——"AI 可读性"成为一等目标
- **E 阶段**：创建 OKF v0.2 文档集
  - 根索引 `index.md`
  - 3 个概念：Vibe Coding 理念、多语言文档站架构、部署与工具链
  - 1 个示例：本地运行与构建示例
  - 2 个信源登记：source-repo.md、references/index.md
  - 变更日志 `log.md`
- **V 阶段**：校验文档结构、frontmatter 完整性、交叉链接一致性。

### 信源

- 官方仓库：https://github.com/datawhalechina/easy-vibe
- 采集日期：2026-08-23
- 基于 `main` 分支工作区副本
