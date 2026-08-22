---
type: Log
title: MyST-NB Bundle 变更日志
okf_version: "0.2"
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
---

# 变更日志

## [1.0.0] - 2026-08-23

### 新增
- R 阶段：完成源码事实采集，生成 [spec/facts.md](spec/facts.md)，包含 170 条可验证事实
  - 项目元信息（版本、Python 要求、核心依赖、entry points、CLI 入口）
  - 核心目录结构（core/、ext/、sphinx_/、docutils_/ 等模块路径）
  - NbParserConfig 配置系统（30+ 字段及默认值、三层优先级、Section 枚举）
  - Notebook 读取层（NbReader、create_nb_reader、mystnb 文本格式解析）
  - 执行引擎层（4 种执行客户端、create_client 工厂、auto 模式逻辑）
  - 渲染层（NbElementRenderer、MIME 优先级、MIME 类型常量、MditRenderMixin）
  - Sphinx 集成（sphinx_setup 注册流程、Post-Transforms、CSS/JS 资源）
  - Docutils 独立模式（DocutilsApp、Parser、CLI 命令）
  - Glue 扩展（glue() 函数、指令/角色/Domain、crossref 替换）
  - Eval 扩展（EvalRoleAny、retrieve_eval_data、NotebookClientInline）
  - 警告系统（MystNBWarnings 6 种类型、create_warning）
  - CLI 工具（quickstart、md_to_nb、mystnb-docutils-*）
- I 阶段：完成架构洞察，生成 [spec/insights.md](spec/insights.md)，包含 5 条核心洞察
  - 四阶段 Notebook 处理管线（读→执→转→渲，新增执行层）
  - 双模式架构复用 MyST-Parser 基础设施（Mixin 模式 vs 基类继承）
  - 三层配置覆盖体系（全局→文件→Cell，Section 标签）
  - Glue/Eval 变量系统——文档与代码的数据桥梁
  - MIME 类型优先级与多输出渲染
- E 阶段：生成完整文档集
  - references/：2 篇信源参考文档
    - mystnb-source.md：源码路径映射与配置速查
    - notebook-cheatsheet.md：MyST Notebook 语法速查
  - concepts/：13 篇概念文档，从入门到深入
    - 入门篇：简介、快速开始、文件格式
    - 架构篇：处理管线、配置系统、执行模式、渲染与 MIME
    - 功能篇：Glue 粘贴、Eval 求值、代码隐藏
    - 集成篇：Sphinx 集成、Docutils 独立、自定义格式扩展
  - examples/：5 篇实战示例
    - 基础配置、执行模式配置、Glue & Eval、代码隐藏、CLI 独立使用
  - index.md：Bundle 根索引
  - 各级 index.md：concepts/、examples/、references/ 导航页
