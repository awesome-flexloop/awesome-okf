# 更新日志

## 2026-08-23

- 初始化 LangChain 官方文档站参考型 OKF v0.2 bundle。
- R（事实采集）：探索 `src/`、`pipeline/`、`scripts/` 目录结构，提取 100 条事实写入 `spec/facts.md`，覆盖文档站配置、MDX 组织、frontmatter 规范、构建管道、Makefile 目标、辅助脚本、CI/CD、文档风格规范。
- I（洞察提炼）：写入 2 条架构洞察到 `spec/insights.md`——单源 MDX → 双语构建的"一次编写，双版生成"模式；导航中心化（docs.json）与文件系统去中心化的张力与平衡。
- E（参考索引）：创建 `references/site-structure.md`，结构化索引 src/ 下主要 MDX 文件（langsmith/、oss/langchain/、oss/langgraph/、oss/deepagents/、oss/python/integrations/、oss/javascript/integrations/ 等）、snippets/、code-samples/、pipeline/、scripts/。
- 创建 `index.md`（含 `okf_version: "0.2"`）和本日志文件。
- 交叉链接统一使用 `/langchain-ai/docs/` 开头的 bundle 相对路径。
