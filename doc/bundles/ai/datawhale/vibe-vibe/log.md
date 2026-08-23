# 变更日志

本文件记录 Vibe Vibe OKF 知识束的版本演进。

## v0.1.0 — 2026-08-23

### 新增

- 初始知识束生成，遵循精简 R→I→E→V 流程。
- **R 阶段**：阅读 README.md、docs/index.md、docs/Basic/index.md、docs/zh/index.md、docs/en/index.md、docs/public/llms.txt、docs/deployment/index.md、docs/.vitepress/config.mts、package.json、Dockerfile、docker-compose.yml，LS docs/ 目录，采集 18 组编号事实（F-001 ~ F-018）。
- **I 阶段**：提炼 3 个架构洞察：
  1. 基础篇 v2 用"单一连续案例"替代"知识点章节"——教学设计从教程转向陪伴式项目
  2. 双语架构的简洁性源于 VitePress 稳定版——与 10 语言项目的工程复杂度形成对比
  3. llms.txt 是"AI 助教路由表"而非"仓库结构文档"——把教程本身变成 AI 可导航的学习系统
- **E 阶段**：创建 OKF v0.2 文档集
  - 根索引 `index.md`
  - 3 个概念：Vibe 开发理念、Basic 入门教学设计、多语言文档架构
  - 1 个示例：Docker 私有化部署
  - 1 个信源登记：source-repo.md
  - 变更日志 `log.md`
- **V 阶段**：校验文档结构、frontmatter 完整性、交叉链接一致性。

### 信源

- 官方仓库：https://github.com/datawhalechina/vibe-vibe
- 采集日期：2026-08-23
- 基于工作区副本（Alpha v0.0.4）
