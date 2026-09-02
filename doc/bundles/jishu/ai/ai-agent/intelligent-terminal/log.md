# 更新日志

## 2026-09-02

**Migration**: 从 SpecWeave docs/knowledge/learning/ 迁入 awesome-okf-xs（08 分类）

* 章节文档 frontmatter 重写为 OKF v0.2（type/title/description/tags/sources/generated/status/stale_after）
* 隐私清洗：个人文件系统路径替换为占位符；中文内嵌引号转全角
* 舍弃：源侧 README.md/index.md（导航）、log.md、seven-concepts-report.md、retrospective*/verification-report*（隐私元数据）

**Migration**: 合并 learning 08/intelligent-terminal-wiki（13 章：总览/架构/WTA master/helper TUI/C++ 集成/协议/wtcli/agent hooks/autofix/构建系统/日志调试/配置/设计模式），与既有 concepts 互补。

**Merge**: 从 SpecWeave learning 合并独有内容（03 分类迁移）

新增 6 篇概念（wta-master 主进程、wta-helper TUI、C++ 集成、构建系统、日志与调试、设计模式），源自 learning 08-systems-infrastructure/intelligent-terminal-wiki；其余章节与既有概念重叠（02 架构→dual-process-architecture、06 协议→acp-json-rpc-protocol、07 wtcli→wtcli-command-tool、08 hooks→hooks-auto-upgrade、09 autofix→osc133-autofix、12 配置→settings-configuration），未重复迁入。

