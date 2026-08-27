# Claude for Financial Services Bundle 更新日志

## 2026-08-27

### 新增

- 🎉 初始化 financial-services bundle 首个版本
- ✅ 覆盖 Anthropic 官方金融服务库完整中文文档
- 🤖 10个End-to-End Agents全覆盖（四大功能域）：
  - 覆盖与顾问：Pitch Agent、Meeting Prep Agent
  - 研究与建模：Market Researcher、Earnings Reviewer、Model Builder
  - 基金管理与财务运营：Valuation Reviewer、GL Reconciler、Month-End Closer、Statement Auditor
  - 运营与开户：KYC Screener
- 📦 7个官方Vertical Plugins + 2个合作方插件：
  - financial-analysis（核心：13个skills/commands + 12个MCP连接器）
  - investment-banking、equity-research、private-equity
  - wealth-management、fund-admin、operations
  - lseg（合作方）、sp-global（合作方）
- 🔌 12个MCP金融数据连接器完整索引：Daloopa、Morningstar、S&P Global、FactSet、Moody's、MT Newswires、Aiera、LSEG、PitchBook、Chronograph、Egnyte、Box
- 📚 概念文档（4 篇）：
  - [Claude for Financial Services概览](concepts/00-overview.md) — 产品定位、双模式架构（Cowork+Managed Agents API）、四大功能域、免责声明、适用场景
  - [10个金融Agents详解](concepts/01-agents.md) — Agent概念、每个Agent功能/输入输出/包含skills/部署方式
  - [垂直行业Skills与Commands](concepts/02-vertical-skills.md) — Vertical插件概念、7个官方vertical详解、Skills同步机制
  - [数据连接器与部署](concepts/03-connectors-deployment.md) — 12个MCP连接器、三种部署方式、MSFT 365工具、自定义扩展方法
- 📖 参考文档（1 篇）：
  - [Agents与Skills完整索引](references/agents-skills-index.md) — 10 Agents表 + 7 Verticals的Skills/Commands对照表 + 12 MCP连接器表 + 斜杠命令速查
- 🏗️ 导航结构：
  - 根 [index.md](index.md)（含 okf_version: 0.2）
  - concepts/index.md
  - references/index.md
  - 本 log.md
- 🔗 交叉链接：与 official-skills（Skills机制）、claude-code（插件安装）、python-sdk（Managed Agents API）子bundle正确链接
