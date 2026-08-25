---
okf_version: "0.2"
type: group
title: "LangChain 官方文档站"
description: "LangChain 官方文档站（docs.langchain.com）的结构索引——基于 Mintlify 的多语言 MDX 文档站，覆盖 LangSmith、LangChain、LangGraph、Deep Agents 四大产品线"
---

# LangChain 官方文档站

本知识包是对 LangChain 官方文档站仓库（`langchain-ai/docs`）的**参考型索引**，记录文档站的目录结构、MDX 组织方式、构建管道和质量保障体系。文档站托管于 Mintlify，线上地址为 [docs.langchain.com](https://docs.langchain.com)，采用单源 MDX + 构建时双语（Python/JavaScript）拆分的架构。

## 文档站结构概览

文档站分为 4 个产品域，所有手写内容位于 `src/` 目录：

| 产品域 | 源目录 | MDX 数量（约） | 导航结构 |
|--------|--------|---------------|---------|
| Home | `src/index.mdx` | 1 | 单页自定义布局 |
| LangSmith | `src/langsmith/` | 474 | 7 个标签页（扁平文件组织） |
| LangSmith Fleet | `src/langsmith/fleet/` | 25 | 5 个分组（无子标签页） |
| Open Source | `src/oss/` | 600+ | 2 语言 × 7 标签页（按产品+语言双维度组织） |

开源部分进一步细分为三大框架：

- **Deep Agents**（`src/oss/deepagents/`，36 顶层 MDX + code/frontend 子目录）
- **LangChain**（`src/oss/langchain/`，32 MDX）
- **LangGraph**（`src/oss/langgraph/`，34 MDX + errors/frontend 子目录）

集成文档按语言和组件类型双层组织：`src/oss/python/integrations/`（21 个组件子目录）和 `src/oss/javascript/integrations/`（17 个组件子目录），每个组件目录下按提供商命名 MDX 文件。

## 构建管道

文档站使用自建 Python 管道（`pipeline/`）在 Mintlify 之上做预处理：

1. **语言拆分**：`DocumentationBuilder` 解析 `:::python` / `:::js` 围栏，生成 `/python/` 和 `/javascript/` 两套站点
2. **片段重写**：将 `/snippets/...` import 重写为语言特定路径
3. **API 链接映射**：`@[ClassName]` 语法通过 `link_map.py` 解析到 `reference.langchain.com`
4. **UTM 注入**：为外部链接添加追踪参数

CLI 入口为 `docs` 命令（`docs dev` / `docs build` / `docs mv` / `docs migrate`），通过 `uv` 安装。Makefile 封装了完整的开发、构建、lint、测试工作流。

## 知识包内容

| 文档 | 类型 | 说明 |
|------|------|------|
| [references/site-structure.md](/ai/langchain-ai/docs/references/site-structure.md) | 参考索引 | src/ 目录下主要 MDX 文件、子目录、pipeline/ 和 scripts/ 的完整结构化索引 |
| [spec/facts.md](/ai/langchain-ai/docs/spec/facts.md) | 事实采集 | 100 条从仓库源码提取的事实（目录结构、frontmatter 规范、构建管道、CI 等） |
| [spec/insights.md](/ai/langchain-ai/docs/spec/insights.md) | 架构洞察 | 2 条深度洞察：单源双语构建模式、导航中心化与文件去中心化的张力 |
| [log.md](/ai/langchain-ai/docs/log.md) | 更新日志 | 本知识包的变更历史 |

## 关键数字

- **474** 个 LangSmith 产品文档 MDX
- **600+** 个开源框架文档 MDX
- **1047** 个可复用 MDX 片段
- **404** 个可执行代码示例文件
- **21** 个 Python 集成组件类别
- **100** 条已验证事实

## 源码位置

`d:/spaces/SpecWeave/external/libs/ai/langchain-ai/docs/`

> 本知识包为参考型 bundle，不包含 concepts/ 深度概念文档和 examples/ 示例文档。所有事实均通过直接读取仓库源码（docs.json、AGENTS.md、pyproject.toml、pipeline/ 代码、Makefile 等）提取验证。

```{toctree}
:hidden:

references/site-structure
spec/facts
spec/insights
log
```
