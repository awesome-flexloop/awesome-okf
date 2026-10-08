# Anthropic 生态 Wiki 更新日志

## 2026-09-02 — 新增 system-prompts 子束

**新增 [system-prompts](system-prompts/index.md) 子束（13文档）**：Anthropic 官方系统提示词发布史中文 Wiki。

- 信源：platform.claude.com 官方发布页 en 版 `.md` 端点，2026-09-02 全量快照（18 个模型子页、30 个日期条目，2024-07-12 → 2026-09-01，约 465KB raw markdown）
- concepts 7 篇：公开机制与政策边界、18×30 全景矩阵、四时代逐条目解析（3.x / 4.0-4.1 / 4.5 / 固定快照）、设计思想演进分析
- references 2 篇：信源索引（18 官方子页 + 采集方法）、条目事实登记表（61 条 F 编号索引）
- 方法论：seven-concepts 知识沉淀链路（R→I→E→V）；关键引文逐字摘录、61 条 F 编号登记、6/6 抽查核验通过；版本对比以逐行 diff 实测为准（官方加粗标注执行不严）
- 质量门：gates.utf8 / gates.toctrees / gates.bundles / sphinx build 全绿

## 2026-08-27 — 初始版本

**初始版本发布**，覆盖Anthropic官方开源生态6大核心项目，共69个文档文件。

### 新增内容

#### python-sdk 子Bundle（24文档·深度源码分析）
- **参考文档（6）**：SDK客户端架构、Messages API、Tools Beta、多云适配、类型与错误处理、源码结构
- **概念文档（10）**：
  - 入门篇：SDK安装与快速开始、客户端初始化与认证、消息基础
  - 核心篇：流式传输SSE、Tool Use工具调用、视觉与文件处理、多云适配器(Bedrock/Vertex)
  - 高级篇：Beta版Agents/Memory API、分页与列表资源、中间件扩展机制
- **示例文档（6）**：基础对话、流式输出、函数调用、多轮对话Agent、图片理解、自定义中间件
- **质量验证**：V阶段Grep级API验证，修复4处虚构API、1处断链、12处待生成标记，零虚构零断链

#### claude-code 子Bundle（9文档）
- 概念：Claude Code CLI概览、插件体系（commands/agents/skills/hooks/MCP servers）
- 示例：自定义Slash Command开发
- 参考：13个官方插件索引
- 目录索引：commands/、agents/、hooks/目录导航

#### cookbooks 子Bundle（10文档）
- 概念：Cookbook概览、能力域分类体系（Capabilities/Tool Use/Multimodal/Advanced/Agent SDK/Third-party）
- 5个能力域分组详解
- 参考：30+食谱完整索引
- 目录导航：tools/、video-tutorials/、third-party/、third-party-api/索引

#### prompt-engineering 子Bundle（8文档）
- 概念：
  - 入门篇：结构化提示、清晰表达、角色设定
  - 中级篇：数据与指令分离、XML格式化输出、思维链CoT、示例驱动(Few-shot)
  - 高级篇：防幻觉策略与复杂提示设计
- 附录：链式提示/工具使用/RAG模式索引
- 完整覆盖原交互式教程9章内容

#### official-skills 子Bundle（9文档）
- 概念：Skills生态概览、SKILL.md格式规范、Skill Creator元技能详解、Claude API Skill详解
- 参考：19个官方Skills分类总索引（API开发4 + 文档处理5 + 设计创意7 + 沟通写作3）
- 重点覆盖：claude-api多语言SDK参考、skill-creator评估方法论

#### financial-services 子Bundle（9文档）
- 概念：金融服务概览（双模式部署Cowork+Managed Agents API）、10个金融Agents详解、7个垂直行业Skills与Commands、数据连接器与部署方式
- 参考：10 Agents表 + 7 Verticals Skills/Commands对照表 + 12 MCP连接器完整索引
- 覆盖四大功能域：覆盖与顾问、研究与建模、基金管理与财务运营、运营与开户

#### 组织级文档（2文档）
- **index.md**（含okf_version: 0.2）：生态全景图、6子Bundle导航表、4条学习路径、9大关键特性、文档统计
- **log.md**：本文件

### 方法论
- 使用 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）
- python-sdk执行完整R（90事实）→I（5洞察+知识地图）→E（分批生成）→V（Grep级API验证）流程
- 其余5个子项目采用结构化整理+索引模式
- 遵循OKF v0.2 frontmatter规范

### 质量保证
- 所有API名称、类名、方法路径经Grep源码验证
- 交叉链接路径一致性检查
- 每个concept包含「相关概念」章节
- 共69个文档文件，覆盖Anthropic官方6个开源子目录全部内容
