---
type: spec
title: handy-n8n 事实清单
bundle: /datawhale/handy-n8n
sources: https://github.com/datawhalechina/handy-n8n
---

# handy-n8n 事实清单

## 项目元信息

F-001: handy-n8n 是 Datawhale 开源的 n8n 系统学习教程，定位为"理论 + 实操"，从入门到精通 n8n 工作流自动化。项目负责人为王晓亮（@tomowang）。

F-002: 项目源码位于 `external/libs/ai/datawhalechina/handy-n8n`，采用 docsify 架构（`_sidebar.md` + `index.html`），在线阅读地址为 https://datawhalechina.github.io/handy-n8n/。n8n 官方站点为 https://n8n.io/，GitHub 仓库为 https://github.com/n8n-io/n8n。

F-003: n8n（nodemation，node + automation，读作 n-eight-n）是一个开源的、基于节点的工作流自动化工具，具备模块化、可视化、可扩展性、数据流四大特点。

F-004: 项目采用 CC BY-NC-SA 4.0 开源协议。文档站点集成 docsify 及自定义插件（docsify-plugin-n8n.js、docsify-plugin-cjk.js），并嵌入 n8n-demo-component 用于工作流在线预览。

## 章节结构（与 _sidebar.md 一致）

F-005: **C01 - n8n 初识**（`c01/README.md`）——n8n 简介（定义、特点：模块化/可视化/可扩展性/数据流）、应用场景（数据同步、营销自动化、客户服务、内部流程、内容管理、开发运维）、节点分类（AI/Communication/Data & Storage/Development/HITL）、n8n 与 dify/coze 的多维度对比（功能特性、易用性、扩展性、部署方式、性能稳定性、社区支持、成本）。

F-006: **C02 - n8n 安装与配置**（`c02/README.md` 及 4 个子文档）——四种部署方式对比：
- 官方 SaaS（`saas.md`）：14 天免费试用，基础版 $20/月，开箱即用
- 本地 PC 部署（`local-pc-deploy.md`）：Docker 部署，创建 n8n_data 卷，端口 5678，时区 Asia/Shanghai，默认 SQLite 存储
- 云主机部署（`cloud-host-deploy.md`）：Docker Compose 部署 withPostgresAndWorker（n8n + postgres + redis + worker），Caddy 反向代理自动 SSL，队列模式可水平扩展
- HuggingFace Space 部署（`hf-space-deploy.md`）：使用 Supabase 外部数据库，Duplicate Space 模板，免费 CPU Basic（2vCPU/16GB/50GB），需配置 DB_POSTGRESDB_*、N8N_ENCRYPTION_KEY、WEBHOOK_URL 等环境变量

F-007: **C03 - n8n 基本概念**（`c03/README.md` 及 4 个子文档）——
- n8n 平台介绍（`n8n-workspace.md`）：注册账户、界面介绍、工作流导入（复制粘贴/URL 导入）、数据结构（对象数组，每项含 json 和 binary 字段，自动逐项处理）
- n8n 触发器节点（`n8n-trigger-nodes.md`）：Manual Trigger（手动）、Schedule Trigger（定时/Cron，时区配置）、Webhook Trigger（HTTP 回调，路径参数/查询参数，三种响应模式）、Chat Trigger（聊天触发器，Hosted Chat 模式）
- n8n 核心节点（`n8n-core-nodes.md`）：数据处理节点（Edit Fields 变量赋值、Split Out 数据拆分）、控制流节点（If 条件判断、Merge 数据合并四种模式、Loop 循环）、HTTP 请求节点
- n8n 中的代码（`n8n-code.md`）：Expressions 表达式（`{{ }}` JavaScript 模板，单语句限制，tournament 模板引擎）、Code 节点（JavaScript/Python 双语言，Run Once for All Items / Run Once for Each Item 两种模式，内置变量 $input/$json/$now，Python 通过 pyodide 执行，外部库需配置 NODE_FUNCTION_ALLOW_EXTERNAL）

F-008: **C04 - n8n 高阶用法**（`c04/README.md` 及 2 个子文档）——
- n8n 子工作流与错误处理（`n8n-sub-workflows-and-error-handling.md`）：Execute Workflow 节点调用子工作流，Execute Sub-Workflow Trigger 接收调用，参数传递；Error Trigger 节点触发独立错误处理工作流，工作流设置中绑定 Error Workflow，SMTP 邮件通知配置（以网易邮箱为例）
- n8n AI 相关概念（`n8n-ai-concepts.md`）：集群节点 Cluster nodes（根节点 root + 子节点 sub-nodes，Chain 与 Agent 两种根类型）、Memory 记忆（Simple Memory/MongoDB/Redis/Postgres Chat Memory，loadMemoryVariables/saveContext 两次交互）、RAG（向量存储 Vector Store、Embedding Model、文档加载、内容上传与检索两阶段、Simple Vector Store）、Tools 工具（AI Agent 关联多个工具扩展能力）、MCP（Model Context Protocol，MCP Client 作为 Agent 工具 + MCP Server Trigger 暴露服务，Streamable HTTP 通讯，以 GitHub API 为例）

F-009: **C05 - n8n 社区节点与节点开发**（`c05/README.md`）——社区节点安装（Settings → Community nodes → Install，npm 包名，n8n-community-node-package 关键字）；自定义节点开发全流程（以高德地图天气服务为例）：申请 API Key、使用 n8n-nodes-starter 模板创建项目、declarative-style 声明式模式 vs programmatic-style 程序模式、构建节点类 AMap（displayName/name/icon/group/version/requestDefaults/properties/routing）、构建鉴权类 AMapApi（ICredentialType，authenticate 配置 qs/auth/header/body）、AMap.node.json 节点描述、本地测试（npm run build → npm link → ~/.n8n/custom 目录 npm link → n8n start）。

F-010: **C06 - n8n 案例分享**（`c06/README.md`）——两个实战案例：
- GitHub Trending 每日推送：定时任务获取 GitHub Trending 数据，邮件发送给指定用户，可推广至 RSS 等信息源
- GitHub Issue 通知：监听 GitHub Issue 事件，新 Issue 创建时通过飞书机器人发送通知

## 工作流资产

F-011: c03 工作流（`workflows/c03/`）——n8n_code_node.json（Code 节点 JS/Python 示例）、n8n_node_demo.json（核心节点综合演示）、node_chat_trigger.json、node_manual_trigger.json、node_schedule_trigger.json、node_webhook_trigger.json、test.json（平台介绍示例）。

F-012: c04 工作流（`workflows/c04/`）——n8n_chat_with_memory.json（带记忆聊天）、n8n_mcp.json（MCP GitHub 工具）、n8n_rag.json（RAG 知识库）、n8n_root_nodes.json（集群根节点展示）、n8n_sub_workflow.json（计算器子工作流）、n8n_tools.json（Agent 工具调用）。

F-013: c06 工作流（`workflows/c06/`）——github-trending.json（每日推送）、github-issue-notify.json（Issue 飞书通知）。

## 技术要点

F-014: n8n 数据在节点间以对象数组传递，每项包含 `json`（文本数据）和 `binary`（二进制数据，Base64 编码）字段。n8n 自动对数组逐项处理，大部分场景无需显式循环。

F-015: n8n 队列模式（Queue Mode）使用 Redis 作为消息队列，主实例 + worker 实例架构，可水平扩展 worker 提高并发处理能力。Simple Memory 在队列模式下不可靠（请求可能分发到不同 worker），应使用 Redis/MongoDB/Postgres 等外部记忆体。

F-016: n8n 自定义节点支持两种开发风格：声明式（declarative-style，JSON 描述，适合 REST API，官方推荐）和程序式（programmatic-style，代码逻辑，适合复杂 API）。节点类实现 INodeType 接口，鉴权类实现 ICredentialType 接口。

F-017: n8n AI 集群节点中，Chain 是简单的 LLM 串联方式（不支持记忆），Agent 是具备决策能力的 Chain（可访问工具、根据上下文执行任务）。内置 Chain 包括 Basic LLM Chain、Retrieval Q&A Chain、Summarization Chain、Sentiment Analysis、Text Classifier。

F-018: MCP（Model Context Protocol）是标准化 LLM 上下文提供的开放协议，n8n 通过 MCP Client Tool（作为 Agent 工具）和 MCP Server Trigger（将 n8n 节点暴露为 MCP 服务）实现双向 MCP 支持，通讯方式为 Streamable HTTP。

## 学习路径

F-019: 入门路径：C01 认识 n8n（与 dify/coze 对比定位）→ C02 选择部署方式（SaaS/本地/云主机/HF Space）→ C03 掌握基本概念（平台界面、触发器、核心节点、代码节点）。

F-020: 进阶路径：C04 高阶用法（子工作流模块化、错误处理容错、AI 集群节点/RAG/MCP）→ C05 扩展开发（社区节点安装、自定义节点 TypeScript 开发）→ C06 实战案例（定时推送、Webhook 通知）。
