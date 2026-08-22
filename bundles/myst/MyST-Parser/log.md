---
type: Log
title: MyST-Parser Bundle 变更日志
okf_version: "0.2"
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
---

# 变更日志

## [1.0.0] - 2026-08-23

### 新增
- R 阶段：完成源码事实采集，生成 [spec/facts.md](spec/facts.md)，包含 117 条可验证事实
  - 项目元信息（版本、Python 依赖、核心依赖版本范围）
  - 扩展清单（18 个可选扩展及插件映射）
  - 配置系统（MdParserConfig 30+ 字段及默认值）
  - 核心模块路径映射（parsers/、renderers/、config/、sphinx_/、cli/）
  - setup_sphinx 注册清单（10 个 config value、2 个节点、4 个事件、3 个 transforms）
  - CLI 入口（7 个 myst-docutils-* 命令 + 1 个 myst-anchors）
- I 阶段：完成架构洞察，生成 [spec/insights.md](spec/insights.md)，包含 5 条核心洞察
  - 三层桥接架构（Markdown→Token→AST→输出）
  - 配置即数据类（MdParserConfig 驱动整个系统）
  - Mock 桥接机制（Sphinx 指令/角色零成本复用）
  - 双模式设计（Sphinx 扩展 vs Docutils 独立）
  - 警告分类体系（MystWarnings 23 种类型）
- E 阶段：生成完整文档集
  - references/：2 篇信源参考文档
    - myst-parser-source.md：源码路径映射
    - extensions-cheatsheet.md：扩展语法速查表
  - concepts/：16 篇概念文档，从入门到深入
    - 入门篇：简介、快速开始、语法概览
    - 架构篇：解析管线、配置系统、扩展系统、解析器与渲染器
    - 机制篇：指令与角色、交叉引用、Slug 与锚点、CLI 工具
    - Sphinx 集成篇：集成机制、Frontmatter、数学公式、警告系统、Docutils 独立
  - examples/：5 篇实战示例
    - 基础 Sphinx 配置、扩展配置实战、自定义指令与角色、交叉引用实战、CLI 独立使用
  - index.md：Bundle 根索引
  - 各级 index.md：concepts/、examples/、references/ 导航页
