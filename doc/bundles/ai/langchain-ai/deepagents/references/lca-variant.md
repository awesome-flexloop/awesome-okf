---
type: reference
scope: deepagents
name: lca-variant
version: "0.7.8"
source: https://github.com/langchain-ai/lca-deepagents
description: lca-deepagents 变体说明——LangChain Academy 课程材料仓库与 deepagents SDK 的关系
---

# lca-deepagents 变体说明

## 仓库定位

[lca-deepagents](https://github.com/langchain-ai/lca-deepagents) 是 [LangChain Academy](https://academy.langchain.com/) 课程 **"Foundation: Introduction to Deep Agents"** 的官方课程材料仓库。它不是 deepagents SDK 的分支或替代实现，而是**基于 deepagents SDK 的教学示例和练习集合**。

- **PyPI 项目名**：`lca-deepagents-python`
- **版本**：`0.1.0`
- **固定 SDK 版本**：`deepagents==0.7.0`
- **Python 要求**：`>=3.11,<3.15`

## 与主仓库的关系

| 维度 | deepagents（主仓库） | lca-deepagents（变体） |
|---|---|---|
| 性质 | 生产级 SDK 和工具集 | 教学课程材料 |
| 版本 | 0.7.8（持续迭代） | 固定 0.7.0（课程快照） |
| 内容 | SDK 源码、ACP、CLI、dcode | 课程模块、练习、示例项目 |
| 依赖 | langchain、langgraph 等 | deepagents SDK + 教学工具 |

lca-deepagents 通过 `pyproject.toml` 将 `deepagents==0.7.0` 作为普通依赖安装，直接使用 SDK 的公开 API（`create_deep_agent`、`SubAgent`、`FilesystemBackend` 等），不修改 SDK 源码。

## 仓库结构

```
lca-deepagents/
├── python/                    # Python 课程实现
│   ├── m1/                    # 模块1：基础代理（模型、工具、MCP、HITL）
│   ├── m2/                    # 模块2：后端与沙箱（文件系统、解释器）
│   ├── m3/                    # 模块3：技能、内存、摘要
│   ├── m4/                    # 模块4：子代理委派
│   ├── m5/                    # 模块5：综合项目（Sales Assistant）
│   ├── pyproject.toml
│   ├── env_utils.py
│   └── models.py
├── typescript/                # TypeScript 实现（即将推出）
├── agent-chat-ui/             # agent-chat-ui 的 fork（为 m5.5 增强）
├── thinkific/                 # Thinkific 课程平台的源材料
│   └── src/m0-m5/             # 课程章节（SVG/HTML 图表）
└── README.md
```

## 课程模块映射

| 模块 | 主题 | 对应 deepagents 概念 |
|---|---|---|
| m1 | 运行 Deep Agent、模型、系统提示、工具、MCP、消息/线程/检查点、HITL | `create_deep_agent`、模型配置、工具、MCP |
| m2 | Deep Agent 环境、文件系统后端、沙箱与本地 Shell、解释器 | `BackendProtocol`、`FilesystemBackend`、`LocalShellBackend` |
| m3 | 摘要与上下文卸载、技能、内存 | `SummarizationMiddleware`、`SkillsMiddleware`、`MemoryMiddleware` |
| m4 | 委派、构建子代理团队、动态子代理 | `SubAgentMiddleware`、`SubAgent`、`CompiledSubAgent`、`AsyncSubAgent` |
| m5 | 综合项目、本地部署、Sales Assistant、异步子代理、沙箱异步代理 | 全部概念的综合应用 |

## 附加依赖

相比主 SDK，lca-deepagents 额外依赖（`python/pyproject.toml` 第13-33行）：

- `langgraph-cli[inmem]>=0.4.0`：本地开发服务器
- `deepagents-code`：终端编码代理
- `langchain-quickjs`：QuickJS 代码解释器中间件
- `langchain-mcp-adapters`：MCP 客户端适配器
- `tavily-python`：Tavily 网络搜索
- `matplotlib>=3.11.0`：图表生成
- `questionary>=2.0.0`：交互式命令行提示
- `markdown`、`nh3`：Markdown 处理和 HTML 清理
- `langchain-ollama>=1.1.0`：Ollama 本地模型支持
- `langchain-community>=0.4.2`：社区集成

## 教学示例：Chinook Sales Assistant

`python/m5/sales_assistant/` 是课程的综合项目，展示了 deepagents 的多个高级特性组合使用：

### 架构特点

1. **文件系统后端**：`FilesystemBackend(root_dir=str(HERE), virtual_mode=True)` 将项目目录作为虚拟文件系统
2. **MCP 集成**：通过 `MultiServerMCPClient` 连接模拟邮件服务器
3. **四个专业子代理**：
   - `chinook-analyst`：数据库专家，唯一接触 SQL 的代理，新客户写入需人工审批
   - `inbox-manager`：邮件专家，唯一接触邮件工具的代理，保存草稿需人工审批
   - `quote-reviewer`：报价单审核者，验证算术和一致性
   - `genre-researcher`：音乐流派研究员，用于新闻稿并行扇出（需 Tavily）
4. **技能系统**：`skills=["/skills"]` 加载可复用工作流
5. **内存系统**：`memory=["/AGENTS.md"]` 加载操作手册
6. **代码解释器**：`CodeInterpreterMiddleware()` 提供精确算术
7. **人工审批门控**：通过 `interrupt_on` 和 `FilesystemPermission` 实现

### 关键安全模式

子代理文件的文档（`subagents.py` 第17-21行）明确说明了一个重要的架构约束：

> 将受审批控制的工具（`mail_create_draft`、`add_customer`）仅放在有门控的专业子代理上，而不放在主代理上。因为通用子代理继承主代理工具——如果主代理有 `add_customer`，通过 `task` 委派即可绕过审批。

这是对 deepagents 子代理继承模型的深度理解和正确使用。

## thinkific 源材料

`thinkific/src/` 目录包含课程平台的源材料，m0-m5 各模块有详细的 Markdown 章节和 SVG/HTML 图表。这些材料是理解 deepagents 设计理念的优秀教学资源，图表涵盖：

- 代理循环（agent loop）
- 后端选择（localshell vs sandbox）
- 上下文卸载（offloading）
- 技能结构（skill anatomy）
- 子代理扇出（agents fanout、context isolation、sync/async）
- 沙箱流程图

## agent-chat-ui fork

`agent-chat-ui/` 是 [langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) 的 fork，为课程第5.5课 "The Sales Assistant (Advanced)" 增加了功能，包括：

- Agent inbox 组件（中断的工具调用审批界面）
- 沙箱文件面板
- 内容块预览和多模态预览
- 工具调用表格展示

## 相关文档

- [使用示例](/ai/langchain-ai/deepagents/examples/lca-variant) — lca-deepagents 的具体代码示例
- [规划与子代理](/ai/langchain-ai/deepagents/concepts/planning-subagents) — 子代理架构概念
- [总览](/ai/langchain-ai/deepagents/concepts/overview) — Deep Agents 整体介绍
