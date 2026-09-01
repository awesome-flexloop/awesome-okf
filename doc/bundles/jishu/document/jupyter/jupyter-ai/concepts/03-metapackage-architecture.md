---
type: Concept
title: 元包架构
description: Jupyter AI v3 的元包（metapackage）架构、12个 jupyter-ai-contrib 子包 + jupyterlab_chat 的职责划分、版本管理与文档聚合机制
tags: [architecture, metapackage, subpackages, composition, versioning, monorepo]
sources:
  - id: agents-md
    resource: external/libs/jupyter/jupyter-ai/AGENTS.md
    title: AGENTS.md
  - id: pyproject
    resource: external/libs/jupyter/jupyter-ai/pyproject.toml
    title: pyproject.toml
  - id: contributors
    resource: external/libs/jupyter/jupyter-ai/docs/source/contributors/index.md
    title: contributors/index.md
  - id: versioning
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/versioning.md
    title: versioning.md
  - id: manifest
    resource: external/libs/jupyter/jupyter-ai/submodules/manifest.json
    title: submodules/manifest.json
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 元包架构

Jupyter AI v3 最根本的架构决策是**从单体仓库（monorepo）转变为元包（metapackage）**。理解这一架构是理解整个 Jupyter AI 生态系统的基础。

## 什么是元包

元包（metapackage）是一种特殊的 Python 包，它本身不包含（或极少包含）功能代码，而是通过依赖声明将一组独立的子包组合成一个可用的发行版。

**v3 之前**：Jupyter AI 是一个单体仓库，所有功能代码都在同一个代码库中。

**v3 之后**：`jupyter-ai` 元包本身几乎为空——主包 `jupyter_ai/` 目录下只有一个 `__init__.py` 文件（含版本号和默认 MCP 工具列表），所有功能都分散在 `jupyter-ai-contrib` 组织下的独立子包中。[^agents-md]

```
jupyter-ai/（元包，几乎为空）
├── jupyter_ai/__init__.py    # 仅含 __version__ 和 DEFAULT_JUPYTER_SERVER_MCP_TOOLS
├── pyproject.toml            # 声明对子包的依赖（10核心+3可选）
├── docs/                     # 用户文档
├── submodules/               # 文档聚合的 git submodule
│   └── manifest.json         # 子包注册表
└── scripts/                  # 文档构建和发布脚本
```

## 子包全景

元包通过 `pyproject.toml` 声明了 10 个核心依赖子包（含 jupyterlab_chat）和 3 个可选子包：

### 核心依赖（必装）

| 子包 | 版本范围 | 职责 |
|---|---|---|
| `jupyterlab_chat` | >=0.23.2,<0.24.0 | 聊天 UI 基础组件（React + Python 后端，基于 Yjs CRDT） |
| `jupyter_server_documents` | >=0.3.3,<0.4.0 | 服务端文档处理（YDoc 协作、输出处理、内核管理） |
| `jupyter_ai_router` | >=0.0.7,<0.1.0 | 消息路由层，将消息分发到正确的 Persona |
| `jupyter_ai_persona_manager` | >=0.1.2,<0.2.0 | Persona 注册中心和 BasePersona 基类 |
| `jupyter_ai_chat_commands` | >=0.0.4,<0.1.0 | 默认聊天斜杠命令集 |
| `jupyter_ai_acp_client` | >=0.2.1,<0.3.0 | Agent Client Protocol 客户端实现 |
| `jupyter_server_mcp` | >=0.2.1,<0.4.0 | Jupyter Server 的 MCP 接口/扩展 |
| `jupyter_ai_tools` | >=0.6.1,<0.7.0 | Notebook 和 JupyterLab 的 Agent 工具集 |
| `jupyterlab_notebook_awareness` | >=0.2.0,<0.3.0 | Notebook 和活动单元格的 Awareness 追踪 |
| `jupyterlab_commands_toolkit` | >=0.1.6,<0.2.0 | JupyterLab 命令工具包 |

### 可选依赖（通过 extras 安装）

| extra | 子包 | 职责 |
|---|---|---|
| `magics` | `jupyter_ai_litellm`, `jupyter_ai_magic_commands` | LiteLLM 模型抽象 + IPython Magic 命令 |
| `jupyternaut` | `jupyter_ai_litellm`, `jupyter_ai_jupyternaut` | LiteLLM 模型抽象 + 默认 Jupyternaut Persona |

### 实验性子包

还有更多实验性子包在 `jupyter-ai-contrib` 组织下活跃开发，包括 jupyter-ai-personas、jupyter-ai-demos、jupyter-floating-chat、jupyter-server-ai-tools、jupyterlab-magic-wand、jupyterlab-document-collaborators 等。[^contributors]

## 子包注册表

`submodules/manifest.json` 维护了 PyPI 包名到 GitHub 仓库的映射：

```json
{
  "jupyter_server_documents": "jupyter-ai-contrib/jupyter-server-documents",
  "jupyter_ai_router": "jupyter-ai-contrib/jupyter-ai-router",
  "jupyter_ai_persona_manager": "jupyter-ai-contrib/jupyter-ai-persona-manager",
  "jupyter_ai_chat_commands": "jupyter-ai-contrib/jupyter-ai-chat-commands",
  "jupyter_ai_acp_client": "jupyter-ai-contrib/jupyter-ai-acp-client",
  "jupyter_server_mcp": "jupyter-ai-contrib/jupyter-server-mcp",
  "jupyter_ai_tools": "jupyter-ai-contrib/jupyter-ai-tools",
  "jupyterlab_notebook_awareness": "jupyter-ai-contrib/jupyterlab-notebook-awareness",
  "jupyterlab_commands_toolkit": "jupyter-ai-contrib/jupyterlab-commands-toolkit",
  "jupyter_ai_litellm": "jupyter-ai-contrib/jupyter-ai-litellm",
  "jupyter_ai_magic_commands": "jupyter-ai-contrib/jupyter-ai-magic-commands",
  "jupyter_ai_jupyternaut": "jupyter-ai-contrib/jupyter-ai-jupyternaut"
}
```

## 版本管理策略

### 版本上限（Ceiling Pin）

元包对每个子包依赖都设置了**版本上限**（ceiling pin），格式为 `>=floor,<next-breaking>`：[^versioning]

```toml
"jupyter_ai_tools>=0.6.1,<0.7.0"
```

这确保子包的破坏性更新（minor 版本在 0.x 阶段可能包含 breaking changes）不会意外破坏用户的 jupyter-ai 安装。

### 版本规则

| 发布类型 | 版本变更 | 依赖策略 |
|---|---|---|
| Patch 版本（3.1.2 → 3.1.3） | 仅提升 floor | 要求子包的 API 兼容补丁版本 |
| Minor 版本（3.1.x → 3.2.0） | 提升 ceiling | 引入新功能，可能包含 API 破坏性变更 |

### 扩展开发者的版本约束

基于 Jupyter AI 构建扩展的开发者应该**直接对使用的子包添加版本范围**，不要依赖元包的版本约束：

```toml
dependencies = [
  "jupyter_ai_tools>=0.6.1,<0.7.0",
]
```

元包的版本范围是为保证元包自身可用而设，不保证你导入的特定 API 在范围内保持不变。

## 文档聚合机制

v3 的另一个架构特点是**文档分布式存储，统一聚合展示**：

- **用户文档**：仅存放在主仓库 `docs/source/users/`
- **贡献者/开发者文档**：存放在各子包**自己的仓库**中
- **聚合方式**：通过 git submodule（sparse-checkout 仅 docs/ 目录）+ Sphinx 扩展自动聚合

### 子包文档约定

每个子包可以在自己的仓库中添加：
```
docs/source/contributors/index.md   → 显示在主站的 Contributors 下
docs/source/developers/index.md     → 显示在主站的 Developers 下
```

子包 `index.md` 的 H1 标题成为子页面名称（惯例使用仓库名，如 `# jupyter-ai-tools`）。

### 版本冻结

- **main 分支（latest 文档）**：子模块跟踪各自的 `main` 分支，每日自动更新
- **发布标签（stable 文档）**：子模块冻结到匹配 pyproject.toml 版本范围的已发版标签

### Sphinx 扩展聚合

`docs/source/_ext/subpackage_docs.py` 是一个 Sphinx 扩展，在 `builder-inited` 阶段将各子模块的 `docs/source/{contributors,developers}/` 子树复制到 git-ignored 的暂存目录，并注入到聚合 toctree 中。缺失的文档静默跳过，保持构建绿色。

## 架构分层

从功能角度，元包的 13 个依赖子包（含 jupyterlab_chat）可以分为 5 层：

```
┌──────────────────────────────────────────────────────┐
│                   扩展层（Extensions）                │
│  jupyter_ai_jupyternaut, jupyter_ai_magic_commands,  │
│  自定义 Persona（第三方）, 自定义 MCP 服务器          │
├──────────────────────────────────────────────────────┤
│                  协议适配层（Protocol）               │
│  jupyter_ai_acp_client（ACP）, jupyter_server_mcp    │
│  （MCP Server）, jupyter_ai_litellm（LLM Provider） │
├──────────────────────────────────────────────────────┤
│                   核心服务层（Core）                  │
│  jupyter_ai_router（路由）, jupyter_ai_persona_manager│
│  （Persona 管理）, jupyter_ai_chat_commands（命令）  │
├──────────────────────────────────────────────────────┤
│                  工具层（Tools）                      │
│  jupyter_ai_tools, jupyterlab_commands_toolkit,      │
│  jupyterlab_notebook_awareness                       │
├──────────────────────────────────────────────────────┤
│                  基础层（Foundation）                 │
│  jupyterlab_chat（聊天 UI/CRDT）,                     │
│  jupyter_server_documents（文档/内核/YDoc）           │
└──────────────────────────────────────────────────────┘
```

## 为什么选择元包架构

元包架构相比单体仓库有以下优势：

1. **独立发版**：各子包可以按自己的节奏迭代发版，不需要等待主仓库发布周期
2. **职责清晰**：每个子包有明确的单一职责，降低理解和维护复杂度
3. **可组合性**：开发者可以只依赖需要的子包（如只依赖 jupyter_ai_tools 而不安装聊天 UI）
4. **容错隔离**：一个子包的问题不会阻塞其他子包的开发和发布
5. **生态开放**：第三方可以独立开发 Persona 或工具包，通过 entry points 集成

## 相关概念

- [Jupyter AI 简介](00-introduction.md)
- [ACP 与 MCP 双协议](04-protocols-acp-mcp.md)
- [AI Persona 系统](05-ai-personas.md)
- [Entry Points API](09-entry-points-api.md)
- [版本与升级](12-versioning-and-upgrades.md)
- [元包源码参考](../references/metapackage-source.md)

[^agents-md]: 文档贡献指南
[^contributors]: contributors/index.md
[^versioning]: versioning.md
