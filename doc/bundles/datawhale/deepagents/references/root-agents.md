---
title: 根 AGENTS.md
type: reference
bundle: /datawhale/deepagents
source_path: AGENTS.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/AGENTS.md
---

# 根 AGENTS.md 引用

Deep Agents monorepo 的全局开发指南，包含仓库级规则。

## 核心内容

- **开发工作流**：在修改的包内工作，使用 `uv` 和 `make`；不随意添加依赖
- **PR 约定**：Conventional Commits 格式（type(scope):），分支命名 `<github-username>/<scope>/<short-description>`
- **公共接口**：保持导出函数签名稳定，新参数使用 keyword-only 带默认值
- **代码规范**：类型注解、Google 风格 docstring、函数不超过约 20 行、禁止 `eval()`/`exec()`/`pickle` 处理用户输入
- **测试规范**：单元测试无网络，集成测试允许网络；`asyncio_mode = "auto"`；警告即错误
- **仓库路由**：明确定位各包路径——SDK 在 `libs/deepagents`，编码 Agent 在 `libs/code`，部署 CLI 在 `libs/cli`，ACP 在 `libs/acp`，Talon 在 `libs/talon`，Evals 在 `libs/evals`，Partner 包在 `libs/partners/<partner>`
- **CI 与发布**：使用 release-please，GitHub Actions 固定到完整 commit SHA
- **OpenWiki**：生成的 `openwiki/` 证据索引，由定时 GitHub Actions 工作流刷新，不应手动编辑

## 相关概念

- [Monorepo 架构](/datawhale/deepagents/concepts/monorepo-architecture)
