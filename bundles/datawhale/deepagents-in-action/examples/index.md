# 示例索引

本课程的代码示例通过 [AgentSeek](https://github.com/ob-labs/agentseek) 模板系统交付，每个章节对应一个可直接运行的项目模板。

## 模板与章节映射

| 模板 | 适用章节 | 创建命令 |
|------|----------|----------|
| deepagents/default | 第1、2章 | `agentseek create deepagents/default --checkout main --no-input` |
| deepagents/content-builder | 第3、7、8、11章 | `agentseek create deepagents/content-builder --checkout main --no-input` |
| deepagents/research | 第4、5、6章 | `agentseek create deepagents/research --checkout main --no-input` |
| deepagents/mcp | 第9、12章 | `agentseek create deepagents/mcp --checkout main --no-input` |
| deepagents/sandbox | 第10章 | `agentseek create deepagents/sandbox --checkout main --no-input` |
| deepagents/streaming | 第14章 | `agentseek create deepagents/streaming --checkout main --no-input` |
| langchain/rubric | 第13章 | `agentseek create langchain/rubric --checkout main --no-input` |

## 统一生命周期

所有模板遵循同一套生命周期入口：

```bash
# 升级 AgentSeek 并查看可用模板
uv tool install --upgrade agentseek
agentseek create --list-templates --checkout main

# 创建项目后
cd <生成的项目目录>
agentseek info
agentseek task --list
agentseek doctor
agentseek dev
```

## 增量扩展说明

部分章节需要在模板基础上按正文补充能力：

- **第6章**（异步子Agent）：从 research 模板开始，将 researcher 拆成独立 graph 并接入 AsyncSubAgent
- **第8章**（长期记忆）：从 content-builder 模板开始，加入 CompositeBackend、StoreBackend 和 namespace
- **第9章**（HITL）：从 mcp 模板开始，为有副作用的工具配置 interrupt_on
- **第11章**（文件权限）：从 content-builder 模板开始，加入 FilesystemPermission 划分访问边界

## 模型配置

示例默认通过硅基流动接入模型，使用 `MODEL_NAME` 环境变量管理模型名：

- 入门：`Qwen/Qwen2.5-7B-Instruct`（免费）
- 快速试跑：`deepseek-ai/DeepSeek-V4-Flash`
- 复杂场景：`zai-org/GLM-5.2`（1M上下文）

> 复杂任务（规划、总结、多子Agent编排）建议使用能力更强的模型，小模型可能无法稳定跑通。

## 推荐辅助技能

```bash
# LangChain 开发指南——工程陷阱与验证修复
npx skills add ob-labs/agentseek --skill langchain-dev-guide

# LangSmith Trace 调试——追踪与性能分析
npx skills add ob-labs/agentseek --skill langsmith-trace
```
