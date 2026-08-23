# Facts - deepagents-in-action

> R阶段事实采集，零推测，每条事实指向源码位置。

## F-001 项目基本信息

- 项目名称：《Deep Agents 实战》
- 副标题：基于 LangChain / LangGraph 生态，系统构建生产级 AI Agent
- 出品方：沧海九粟（LangChain 官方认证大使，B站万粉UP主，《LangChain 实战》《LangGraph 实战》作者）
- 开源社区：Datawhale
- 课程网站：https://datawhalechina.github.io/deepagents-in-action/
- 视频合集：B站 https://space.bilibili.com/28357052/lists/7757577?type=season
- 图文合集：小红书
- 来源：README.md:3-18

## F-002 版本要求

- Deep Agents 版本要求：≥ 0.5
- 部分功能有更高最低版本要求：
  - `FilesystemPermission` 基础权限：deepagents>=0.5.2
  - `FilesystemBackend` 的 `virtual_mode` 参数：deepagents>=0.5.0
  - `interrupt` 权限模式：deepagents>=0.6.8
  - `RubricMiddleware`（Beta）：deepagents>=0.6.5
  - 第13章以 deepagents==0.7.1 验证版本化行为
  - 第14章 Event Streaming v3：deepagents>=0.6
- 官方文档：https://docs.langchain.com/oss/python/deepagents/overview
- 来源：README.md:27-30

## F-003 模型选择策略

- 默认通过硅基流动（SiliconFlow）接入模型
- 建议用 `MODEL_NAME` 环境变量管理模型名，不写死在代码里
- 入门/简单任务：
  - 免费版 `Qwen/Qwen2.5-7B-Instruct` 可跑通示例
  - `deepseek-ai/DeepSeek-V4-Flash` 适合快速试跑
- 复杂场景（任务规划、上下文总结、多子Agent编排）：
  - 小模型往往无法稳定跑通
  - 推荐 `zai-org/GLM-5.2`，面向长程Agent任务，支持1M上下文
- 来源：README.md:32-38

## F-004 课程大纲——准备篇

基于 AgentSeek 工程化套件搭建开发环境：

- pre01：AgentSeek 生命周期工作流——创建 DeepAgents 模板，检查环境并启动前后端
- pre02：`npx skills` 安装开发技能——为AI编码助手加载LangChain工程经验
  - langchain-dev-guide：LangChain开发指南——工程陷阱与验证修复
  - langsmith-trace：LangSmith Trace调试——追踪与性能分析
- AgentSeek 统一生命周期入口：
  - `agentseek create <template>` 创建项目
  - `agentseek info` 查看信息
  - `agentseek task --list` 列出任务
  - `agentseek doctor` 环境检查
  - `agentseek dev` 启动开发
- `--checkout main` 获取最新模板，冻结作业环境可换成完整提交SHA
- 来源：README.md:43-87

## F-005 课程大纲——认知篇（第1-2章）

| 章节 | 标题 | 模板 | 核心实验 |
|------|------|------|----------|
| 第1章 | 从 Agent Framework 到 Agent Harness — Deep Agents 的诞生逻辑 | deepagents/default | 从最小 create_deep_agent 项目识别 Runtime、Framework 与 Harness 的边界 |
| 第2章 | 快速上手 — 5分钟构建你的第一个 Deep Agent | deepagents/default | 修改系统提示词和自定义工具，跑通第一个可工作的 Deep Agent |

- 来源：README.md:89-107

## F-006 课程大纲——核心篇（第3-6章）

| 章节 | 标题 | 模板 | 核心实验 |
|------|------|------|----------|
| 第3章 | 虚拟文件系统 — Deep Agents 的 Context Engineering 核心 | deepagents/content-builder | 利用 FilesystemBackend 观察内容、中间结果和 Skills 如何落盘 |
| 第4章 | 任务规划与分解 — 让 Agent 学会拆解复杂任务 | deepagents/research | 通过 Todo 面板观察 write_todos 的计划生成与状态变化 |
| 第5章 | 子 Agent 与上下文隔离 — 让 Agent 学会委派 | deepagents/research | 观察主Agent将搜索委派给research-agent，比较两侧上下文 |
| 第6章 | 异步子 Agent — 让主 Agent 同时驱动多个子任务 | deepagents/research | 将researcher拆成独立graph并接入AsyncSubAgent |

- 来源：README.md:109-145

## F-007 课程大纲——进阶篇（第7-12章）

| 章节 | 标题 | 模板 | 核心实验 |
|------|------|------|----------|
| 第7章 | Skills — 可复用的 Agent 能力包 | deepagents/content-builder | 使用内置blog-post与social-media Skills观察匹配和渐进式加载 |
| 第8章 | 长期记忆 — 让 Agent 拥有跨对话的记忆 | deepagents/content-builder | 加入 CompositeBackend、StoreBackend 和运行时 namespace |
| 第9章 | Human-in-the-Loop — 构建安全的人机协作流程 | deepagents/mcp | 为有副作用的工具配置 interrupt_on |
| 第10章 | 沙箱执行 — 让 Agent 安全地运行代码 | deepagents/sandbox | 选择Daytona或LangSmith Sandbox，观察隔离执行、文件读写与清理 |
| 第11章 | 文件系统权限 — 用声明式规则控制 Agent 的读写边界 | deepagents/content-builder | 加入 FilesystemPermission 并划分访问边界 |
| 第12章 | MCP — 用标准协议扩展 Deep Agents 工具生态 | deepagents/mcp | 验证stdio/HTTP Server、工具发现、稳定前缀与名称冲突 |

- 第6、8、9、11章需要在模板基础上按正文补充本章能力
- 来源：README.md:147-201

## F-008 课程大纲——前沿预览（第13-14章）

| 章节 | 标题 | 模板 | 核心实验 |
|------|------|------|----------|
| 第13章 | Grading Rubrics（评分量规）— 让 Agent 按验收标准自我迭代 | langchain/rubric | 运行Guided Demo，观察Evidence与Acceptance Gate |
| 第14章 | Streaming — 实时观察主 Agent、子 Agent 与工具调用 | deepagents/streaming | 运行Event Streaming v3应用，观察coordinator/subagent messages、工具生命周期、状态快照、最终输出和raw protocol |

- 第14章模板由 agentseek-templates PR #20 引入
- 后续课程内容将根据Deep Agents官方能力演进持续更新
- 来源：README.md:203-223

## F-009 AgentSeek 模板体系

课程使用的 AgentSeek 模板共7种：

| 模板 | 适用章节 | 用途 |
|------|----------|------|
| deepagents/default | 第1、2章 | 最小 Deep Agent 项目 |
| deepagents/content-builder | 第3、7、8、11章 | 内容构建类应用（文件系统、Skills、记忆、权限） |
| deepagents/research | 第4、5、6章 | 研究类应用（任务规划、子Agent、异步子Agent） |
| deepagents/mcp | 第9、12章 | MCP协议应用（HITL、MCP工具生态） |
| deepagents/sandbox | 第10章 | 沙箱代码执行 |
| deepagents/streaming | 第14章 | Event Streaming v3 流式应用 |
| langchain/rubric | 第13章 | 评分量规自我迭代 |

- 模板仓库：https://github.com/agentseek-ai/agentseek-templates
- 来源：README.md:93-220

## F-010 网站技术栈与项目结构

- 站点框架：Astro 6
- 样式：Tailwind CSS 4
- 语言：TypeScript
- Node.js 要求：≥ 22.12.0
- 项目结构：
  - `content/`：章节正文Markdown（每章一个文件，不含frontmatter）
  - `public/imgs/`：正文插图
  - `public/pdfs/`：章节PDF
  - `scripts/chapters.json`：章节元数据（标题、发布状态、视频链接等）
  - `scripts/prep-content.mjs`：内容预处理脚本（注入frontmatter）
  - `src/components/`：Astro组件
  - `src/layouts/`：页面布局
  - `src/pages/`：路由页面
- 来源：README.md:290-330

## F-011 内容流水线机制

- `content/` 目录中的Markdown文件是源文件，不含frontmatter
- `scripts/prep-content.mjs` 在 dev/build 前自动运行
- 从 `scripts/chapters.json` 读取元数据，生成带frontmatter的文件到 `src/content/chapters/`
- 正文图片统一写成 `../public/imgs/<文件名>`，预处理转换为 `/deepagents-in-action/imgs/<文件名>`
- 资产校验检查Markdown中引用的图片是否真实存在
- `content/` 下 .md 文件首行H1标题在生成时自动移除，页面标题统一取自 chapters.json
- 添加/修改章节内容只需编辑 content/ 目录
- 修改标题、发布状态、视频链接等元数据编辑 scripts/chapters.json
- 来源：README.md:332-343

## F-012 开源协议

- 课程文字内容：CC BY-NC-SA 4.0（知识共享署名-非商业性使用-相同方式共享4.0国际）
- 网站源代码：MIT
- 来源：README.md:355-358

## F-013 核心概念关键词

从章节标题中提炼的 Deep Agents 核心能力域：

- Agent Harness（Agent框架之上的运行时外壳）
- Context Engineering（上下文工程，以虚拟文件系统为核心）
- 虚拟文件系统（FilesystemBackend、virtual_mode）
- 任务规划（write_todos、Todo面板）
- 子Agent与上下文隔离（research-agent委派）
- 异步子Agent（AsyncSubAgent、独立graph）
- Skills（可复用Agent能力包、渐进式加载）
- 长期记忆（CompositeBackend、StoreBackend、namespace）
- Human-in-the-Loop（interrupt_on、人机协作）
- 沙箱执行（Daytona、LangSmith Sandbox、隔离执行）
- 文件系统权限（FilesystemPermission、声明式规则）
- MCP（Model Context Protocol、stdio/HTTP Server、工具发现）
- Grading Rubrics（评分量规、Evidence、Acceptance Gate、自我迭代）
- Event Streaming v3（coordinator/subagent messages、工具生命周期、状态快照）
- 来源：README.md:91-217
