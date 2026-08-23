---
type: Reference
title: JupyterLab 插件架构参考
description: jupyterlite-ai 的 JupyterFrontEndPlugin 插件列表与依赖关系
tags: [jupyterlite-ai, plugins, jupyterlab, reference]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
---

# JupyterLab 插件架构参考

jupyterlite-ai 由 `@jupyternaut/persona` 和 `@jupyterlite/ai` 两个 JupyterLab 扩展组成，共注册约 20 个 JupyterFrontEndPlugin。

## @jupyternaut/persona 插件列表

Persona 层负责核心 AI 能力注册：Provider、Agent、Tool、Skill、Settings、Completion。

| 插件 ID | Provides | Requires | Optional | 描述 |
|---------|----------|----------|----------|------|
| `@jupyternaut/persona:provider-registry` | IProviderRegistry | - | - | Provider 注册表 |
| `@jupyternaut/persona:anthropic-provider` | - | IProviderRegistry | - | 注册 Anthropic Provider |
| `@jupyternaut/persona:google-provider` | - | IProviderRegistry | - | 注册 Google Provider |
| `@jupyternaut/persona:mistral-provider` | - | IProviderRegistry | - | 注册 Mistral Provider |
| `@jupyternaut/persona:openai-provider` | - | IProviderRegistry | - | 注册 OpenAI Provider |
| `@jupyternaut/persona:generic-provider` | - | IProviderRegistry | - | 注册 Generic Provider |
| `@jupyternaut/persona:settings-model` | IAISettingsModel | ISettingRegistry | - | AI 设置模型 |
| `@jupyternaut/persona:skill-registry` | ISkillRegistry | - | - | Skill 注册表 |
| `@jupyternaut/persona:tool-registry` | IToolRegistry | - | ISkillRegistry | Tool 注册表（注册内置工具） |
| `@jupyternaut/persona:skills` | - | IAISettingsModel, IDocumentManager, ISkillRegistry | ICommandPalette, ITranslator | 从文件系统加载 Skills |
| `@jupyternaut/persona:diff-manager` | IDiffManager | IAISettingsModel | - | Cell/File Diff 管理器 |
| `@jupyternaut/persona:registry` | IPersonaRegistry | IAISettingsModel | IProviderRegistry, IDocumentManager | Persona 注册表（无 Chat 依赖） |
| `@jupyternaut/persona:plugin` | - | IPersonaRegistry, IAgentManagerFactory, IAISettingsModel | IChatTracker, IProviderRegistry, IToolRegistry | 将 Persona 附加到 Chat Widget |
| `@jupyternaut/persona:mention` | - | IChatCommandRegistry | - | 注册 @提及聊天命令 |
| `@jupyternaut/persona:<secrets-namespace>` | IAgentManagerFactory | IAISettingsModel, IProviderRegistry | ISkillRegistry, ICompletionProviderManager, ISecretsManager, IMcpManager | Agent 工厂 + 代码补全（SecretsManager 签名） |
| `@jupyternaut/persona:settings-panel` | - | IAISettingsModel, IAgentManagerFactory, IProviderRegistry | ICommandPalette, ILayoutRestorer, ISecretsManager, IThemeManager, ITranslator, IFormRendererRegistry, IMcpManager | AI 设置面板 |
| `@jupyternaut/persona:completion-status` | - | IAISettingsModel | IStatusBar, ITranslator | 状态栏补全状态指示器 |

## @jupyterlite/ai 插件列表

Chat UI 层负责聊天界面、命令注册和工具栏。

| 插件 ID | Provides | Requires | Optional | 描述 |
|---------|----------|----------|----------|------|
| `@jupyterlite/ai:chat-command-registry` | IChatCommandRegistry | - | - | 聊天命令注册表 |
| `@jupyterlite/ai:clear-command` | - | IChatCommandRegistry | - | 注册 /clear 命令 |
| `@jupyterlite/ai:skills-command` | - | IChatCommandRegistry, ISkillRegistry | - | 注册 /skills 命令 |
| `@jupyterlite/ai:chat-toolbar-factory` | IChatToolbarFactory | ISettingRegistry, IToolbarWidgetRegistry, ITranslator | - | 共享工具栏工厂 |
| `@jupyterlite/ai:chat-model-handler` | IChatModelHandler | IAISettingsModel, IAgentManagerFactory, IDocumentManager, IRenderMimeRegistry, IPersonaRegistry, ISettingRegistry | IProviderRegistry, IToolRegistry | 聊天模型创建处理器 |
| `@jupyterlite/ai:activeCellManager` | - | IChatModelHandler, INotebookTracker | - | 活动单元格管理器（代码复制） |
| `@jupyterlite/ai:chat` | IChatTracker | IRenderMimeRegistry, IInputToolbarRegistryFactory, IChatModelHandler, IAISettingsModel, IChatCommandRegistry | ISettingRegistry, IThemeManager, ILayoutRestorer, ILabShell, ITranslator, IToolbarWidgetRegistry, IComponentsRendererFactory, ICommandPalette, IDocumentManager, IPersonaRegistry, IChatToolbarFactory | 主聊天面板（侧边栏+主区域） |
| `@jupyterlite/ai:input-toolbar-factory` | IInputToolbarRegistryFactory | IAISettingsModel, IToolRegistry, IProviderRegistry | ITranslator, IPersonaRegistry | 输入工具栏工厂 |

## 扩展点

第三方扩展可通过以下方式扩展 jupyterlite-ai：

1. **注册自定义 Provider**：依赖 `IProviderRegistry`，调用 `registerProvider()`
2. **注册自定义 Tool**：依赖 `IToolRegistry`，调用 `add(name, tool)`
3. **注册自定义 Skill**：依赖 `ISkillRegistry`，调用 `registerSkill()`
4. **自定义聊天组件**：通过 `IComponentsRendererFactory` 注入
5. **MCP 服务器**：通过 `IMcpManager` 添加 MCP 服务器，自动暴露工具给 Agent
