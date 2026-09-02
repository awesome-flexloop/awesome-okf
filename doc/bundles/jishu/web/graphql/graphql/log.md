# 变更日志

## 2026-09-02

**Merge**: 从 SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/ 合并独有内容

- 新增 `concepts/12-client-engineering.md`：前端客户端工程（Apollo Client/Relay/urql 对比、HTTP 请求协议、GraphiQL、规范化/文档缓存、@client 与乐观更新），源自 learning 侧 05-client-basics.md
- 新增 `concepts/13-server-engineering.md`：服务端工程（Schema First vs Code First、Context、Resolver、N+1 与 DataLoader、错误处理、中间件、部署安全），源自 learning 侧 06-server-concepts.md
- 新增 `concepts/14-best-practices.md`：最佳实践与反模式（命名约定、游标分页、无版本演进、查询限制、持久化查询、Union 错误模式、五大反模式），源自 learning 侧 08-best-practices.md
- 重复确认：learning 侧 00/01/02/03 章（概览、核心概念、查询语法、类型系统）与既有 concepts/00-09 覆盖重叠，未重复迁入；11 章术语表与既有概念文档重叠，未迁入；07 章 Python 生态已由 concepts/10 覆盖
- 更新 `concepts/index.md`、`index.md` 导航与 toctree（12→15 概念）

**Merge**: 从 SpecWeave docs/knowledge/learning/04-docs-markup-tooling/mdx-graphql-guide/ 合并独有内容

- 新增 `references/mdx-graphql-guide/`（index + 4 章：00-overview/01-quickstart/02-query-components/03-best-practices）——可查询文档（MDX+GraphQL）主题系列，作为信源登记增量收录
- 更新 `references/index.md` 登记列表与 toctree

## 2026-08-23

- 初始版本创建
- 基于 GraphQL 规范（October 2021 Working Draft）+ AI WG MCP 源码 + 语义内省 RFC
- R 阶段：采集 669 条编号事实（F-001~F-669）
- I 阶段：提炼 5 个核心架构洞察
- E 阶段：生成 12 概念 + 4 示例 + 9 信源文档
- V 阶段：结构审查通过（0 断裂链接、25/25 frontmatter 合规）；事实溯源通过（20 MCP API + 24 内建类型 + 13 Python 库 + 26 RFC 要素全部验证）；修复 2 处 Fact ID 标注错误和 2 处格式问题
- C 阶段：轻量复盘完成
