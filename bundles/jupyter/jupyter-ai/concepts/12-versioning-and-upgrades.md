---
type: Concept
title: 版本与升级
description: Jupyter AI 的版本管理策略、版本上限机制、升级注意事项、子包版本兼容规则
tags: [versioning, upgrade, semver, ceiling-pin, compatibility, release]
sources:
  - id: versioning
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/versioning.md
    title: versioning.md
  - id: pyproject
    resource: external/libs/jupyter/jupyter-ai/pyproject.toml
    title: pyproject.toml
  - id: init-py
    resource: external/libs/jupyter/jupyter-ai/jupyter_ai/__init__.py
    title: jupyter_ai/__init__.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 版本与升级

Jupyter AI 采用语义化版本（SemVer）结合版本上限（ceiling pin）的策略管理版本，确保稳定体验的同时允许快速迭代。

## 当前版本

- **元包版本**：3.1.3
- **Python 要求**：>=3.9
- **许可证**：BSD-3-Clause

版本号在 `jupyter_ai/__init__.py` 中定义：

```python
__version__ = "3.1.3"
```

## 版本策略

### 版本上限（Ceiling Pin）

元包对每个子包依赖都设置了**版本上限**，格式为 `>=floor,<next-breaking>`：

```toml
"jupyter_ai_tools>=0.6.1,<0.7.0"
"jupyter_ai_acp_client>=0.2.1,<0.3.0"
"jupyter_server_mcp>=0.2.1,<0.4.0"
```

这确保子包的破坏性更新不会意外破坏用户的 jupyter-ai 安装。在 0.x 阶段，minor 版本号变更可能包含 breaking changes，因此 ceiling pin 锁定到当前 minor 版本。

### Patch 版本（3.1.2 → 3.1.3）

- **变更范围**：仅提升 floor（最低版本要求）
- **兼容性**：保证 API 完全兼容，只包含 bug 修复
- **子包约束**：要求子包版本 >= 修复版本，< 下一个 breaking 版本

### Minor 版本（3.1.x → 3.2.0）

- **变更范围**：提升 ceiling（上限），引入新功能
- **兼容性**：可能包含 API 破坏性变更
- **子包约束**：允许使用子包的新 minor 版本

## 升级建议

### 频繁升级

Jupyter AI 处于活跃开发阶段，建议**频繁升级**以获取最新功能和修复。

### 使用环境管理器

优先使用环境管理器（conda/mamba/micromamba/uv/pixi）升级，而不是直接 pip：

```bash
# micromamba（推荐）
micromamba update -c conda-forge jupyter-ai

# uv
uv pip install -U jupyter-ai

# conda
conda update -c conda-forge jupyter-ai

# pip
pip install --upgrade jupyter-ai
```

### 升级后的注意事项

- `.chat` 文件不保证前向兼容，旧版本聊天文件可能在新版本中无法正常工作
- 升级前如需保留重要对话，让 AI 读取旧聊天并生成摘要
- 检查扩展是否需要更新（`pip list | grep jupyter-ai`）
- 重启 JupyterLab 使更改生效

## 扩展开发者版本约束

如果你在开发基于 Jupyter AI 的扩展（自定义 Persona、工具包等），**应该直接对你使用的子包添加版本范围**，不要依赖元包的版本约束。

```toml
# ✅ 正确：直接依赖使用的子包
dependencies = [
  "jupyter_ai_persona_manager>=0.1.2,<0.2.0",
  "jupyter_ai_tools>=0.6.1,<0.7.0",
]

# ❌ 错误：只依赖元包
dependencies = [
  "jupyter_ai>=3.1.0,<4.0.0",
]
```

原因：元包的版本范围是为保证元包自身可用而设，不保证你导入的特定 API 在整个范围内保持不变。子包遵循独立 SemVer，直接约束子包版本更精确。

## 子包版本关系

元包通过 `submodules/manifest.json` 跟踪每个子包的来源仓库，构建和发布时自动将子包版本固定到兼容范围。以下是当前版本（3.1.3）的核心子包版本范围：

| 子包 | 版本范围 |
|---|---|
| jupyterlab_chat | >=0.23.2,<0.24.0 |
| jupyter_server_documents | >=0.3.3,<0.4.0 |
| jupyter_ai_router | >=0.0.7,<0.1.0 |
| jupyter_ai_persona_manager | >=0.1.2,<0.2.0 |
| jupyter_ai_chat_commands | >=0.0.4,<0.1.0 |
| jupyter_ai_acp_client | >=0.2.1,<0.3.0 |
| jupyter_server_mcp | >=0.2.1,<0.4.0 |
| jupyter_ai_tools | >=0.6.1,<0.7.0 |
| jupyterlab_notebook_awareness | >=0.2.0,<0.3.0 |
| jupyterlab_commands_toolkit | >=0.1.6,<0.2.0 |

## 故障排查

### 升级后 Agent 不工作
1. 确认 Agent CLI 已安装且为最新版本
2. 确认 ACP 适配器已安装（如果需要）
3. 重新登录 Agent（如 `claude login`）
4. 重启 JupyterLab

### 版本冲突
如果遇到依赖冲突，建议创建干净的虚拟环境重新安装：

```bash
conda create -n jupyter-ai -c conda-forge jupyter-ai
conda activate jupyter-ai
```

## 相关概念

- [元包架构](/concepts/03-metapackage-architecture.md)
- [安装与配置](/concepts/01-installation-and-setup.md)
- [Entry Points API](/concepts/09-entry-points-api.md)
- [元包源码参考](/references/metapackage-source.md)
