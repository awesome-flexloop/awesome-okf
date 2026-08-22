---
type: Reference
title: Entry Points 参考
description: Jupyter AI entry points 分组、注册方式和版本约束参考
tags: [entry-points, extension, developer, persona, model-provider]
sources:
  - id: entry-points-api
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/index.md
    title: entry_points_api/index.md
  - id: providing-entry-points
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/providing_entry_points.md
    title: providing_entry_points.md
  - id: versioning
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/versioning.md
    title: versioning.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Entry Points 参考

Jupyter AI 通过 Python entry points 机制实现插件化扩展。任何安装在同一 Python 环境中的包都可以通过注册 entry points 来添加自定义 Persona 或其他扩展对象。

## Entry Point 分组

| 分组名 | 期望对象类型 | 状态 | 说明 |
|---|---|---|---|
| `jupyter_ai.personas` | BasePersona 子类 | 稳定 | 添加自定义 AI Persona |
| `jupyter_server_mcp.tools` | MCP 工具函数路径 | 稳定 | 注册默认 MCP 工具（元包自身使用） |

> 未来版本可能添加更多分组（如 model_providers、embeddings_providers）。

## 注册格式

在 `pyproject.toml` 中使用 hatchling/setuptools 标准格式：

```toml
[project.entry-points."<entry-point-group>"]
<unique-name> = "<module-path>:<class-name>"
```

### 规则

- `<entry-point-group>` 必须加引号（因为包含下划线和点号）
- `<unique-name>` 在同一分组内必须唯一
- `<module-path>` 是 Python 模块导入路径（点号分隔）
- `<class-name>` 是模块中的类名或函数名

### 示例：注册 Persona

```toml
[project.entry-points."jupyter_ai.personas"]
claude_code = "jupyter_ai_claude_code.persona:ClaudeCodePersona"
my_persona = "my_package.my_module:MyPersona"
```

## 版本约束最佳实践

扩展开发者应直接对使用的子包添加版本范围约束，不要依赖 jupyter-ai 的版本范围：

```toml
dependencies = [
  "jupyter_ai_persona_manager>=0.1.2,<0.2.0",
  "jupyter_ai_tools>=0.6.1,<0.7.0",
]
```

原因：jupyter-ai 的版本范围是为保证自身可用而设，不保证你导入的特定 API 在范围内不变。

## 生效条件

1. 包必须安装在 Jupyter AI 所在的同一 Python 环境
2. 安装或卸载 entry points 后必须**重启 JupyterLab**（entry points 仅在服务启动时读取）
3. 使用 `pip install -e .`（editable 模式）开发时，代码修改后也需要重启服务

## 开发环境

官方推荐使用 [jupyter-ai-devrepo](https://github.com/jupyter-ai-contrib/jupyter-ai-devrepo) 进行开发：

```bash
git clone --recurse-submodules https://github.com/jupyter-ai-contrib/jupyter-ai-devrepo.git
cd jupyter-ai-devrepo
# 需要 uv 和 just
just pull-all      # 拉取所有子模块最新代码
just install-all   # 以 editable 模式安装所有包
just start         # 启动 JupyterLab
```

### Devrepo 常用命令

| 命令 | 说明 |
|---|---|
| `just start` | 启动 JupyterLab |
| `just sync` | 同步 Python 环境与 uv.lock |
| `just pull-all` | 切换所有子模块到 main 并拉取最新代码 |
| `just build-all` | 构建所有子模块前端资源 |
| `just install-all` | editable 安装所有包（含 build-all 和 enable-extensions） |
| `just reinstall-all` | 重新安装一切（修复损坏的 venv） |
| `just pytest` | 在子模块目录内运行单元测试 |

## 设计原则

扩展开发应遵循 Jupyter AI 的核心设计原则：

1. **厂商中立（vendor-agnostic）**：不歧视特定 Agent 或模型提供商
2. **仅响应显式提示（only responds to explicit prompt）**：不自动监听文件或发送提示
3. **提示透明（transparent）**：系统提示和提示模板开源可见
4. **可追溯（traceable）**：生成内容标注来源
5. **以人为中心（human-centered）**：UI 符合通用聊天应用习惯

## 相关概念

- [Entry Points API](/concepts/09-entry-points-api.md)
- [AI Persona 系统](/concepts/05-ai-personas.md)
- [自定义 Persona 示例](/examples/custom-persona.md)
- [Persona API 参考](/references/persona-api.md)
