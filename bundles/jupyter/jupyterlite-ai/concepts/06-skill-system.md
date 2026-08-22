---
type: Concept
title: Skill 技能系统
description: Skill 系统支持从文件系统加载 Markdown 格式的 AI 技能（SKILL.md），AI 可以通过 discover_skills/load_skill 工具发现和使用这些技能
tags: [jupyterlite-ai, skill, SKILL.md, extensibility]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
  - id: tools
    resource: /references/built-in-tools.md
    title: 内置 AI 工具参考
---

# Skill 技能系统

Skill 系统允许用户和扩展开发者通过 Markdown 文件定义可复用的 AI 技能。AI 代理可以通过 `discover_skills` 和 `load_skill` 工具动态发现、加载和使用这些技能，无需修改代码。

## 核心概念

**技能（Skill）** 是一个包含指令和资源的目录，核心文件为 `SKILL.md`。技能定义了 AI 在特定场景下应遵循的步骤、指南和参考资料。

## ISkillRegistry 接口

```typescript
interface ISkillRegistry {
  readonly skillsChanged: ISignal<ISkillRegistry, void>;
  registerSkill(skill: ISkillRegistration): IDisposable;
  listSkills(query?: string): ISkillSummary[];
  getSkill(name: string): ISkillDefinition | null;
  getSkillResource(name: string, resource: string): Promise<ISkillResourceResult>;
}
```

### 数据结构

```typescript
// 技能摘要（列表展示用）
interface ISkillSummary {
  name: string;
  description: string;
}

// 完整技能定义
interface ISkillDefinition extends ISkillSummary {
  instructions: string;    // SKILL.md 中的指令内容
  resources: string[];     // 捆绑的资源文件路径列表
}

// 技能注册（含资源加载器）
interface ISkillRegistration extends ISkillDefinition {
  loadResource?: (resource: string) => Promise<ISkillResourceResult>;
}

// 资源加载结果
interface ISkillResourceResult {
  name: string;
  resource: string;
  content?: string;
  error?: string;
}
```

## SKILL.md 格式

技能通过 `parseSkillMd()` 函数解析 Markdown 文件，提取名称、描述和指令：

```markdown
---
name: my-skill
description: 这个技能的简短描述
---

# 技能指令

这里是给 AI 的详细指令，描述在什么场景下使用此技能以及具体步骤...

## 步骤

1. 第一步
2. 第二步
3. ...
```

解析规则：
- YAML frontmatter 中的 `name` 和 `description` 为元数据
- `name` 是技能的唯一标识符
- Markdown 正文作为 `instructions`（AI 执行指令）

## 技能加载流程

`skillsPlugin`（`@jupyternaut/persona:skills`）负责从文件系统发现和加载技能：

```
1. 监听 settingsModel.config.skillsPaths 配置
2. 调用 loadSkillsFromPaths(contentsManager, skillsPaths)
   │
   ├─ 遍历每个配置路径
   ├─ 列出路径下的目录（每个子目录是一个技能）
   ├─ 查找 SKILL.md 文件
   ├─ parseSkillMd() 解析元数据和指令
   ├─ 扫描目录下其他文件作为 resources
   └─ 返回 ISkillFileDefinition[]
3. 为每个技能创建带 loadResource 回调的 ISkillRegistration
4. 注册到 SkillRegistry
5. skillsChanged 信号触发 AgentManager.refreshSkills()
```

### 资源加载安全

`loadResource` 回调实现了路径安全校验：

```typescript
const validateResourcePath = (resourcePath: string): string | null => {
  if (resourcePath.startsWith('/')) return null;  // 禁止绝对路径
  const normalized = PathExt.normalize(resourcePath);
  if (normalized.startsWith('..') || normalized === '') return null;  // 禁止路径遍历
  return normalized;
};
```

确保 AI 无法通过 `load_skill` 工具访问技能目录之外的文件。

## 配置技能路径

用户通过设置面板配置技能搜索路径：

```typescript
interface IAIConfig {
  skillsPaths: string[];  // Jupyter 文件系统中的目录路径列表
}
```

技能路径变更时自动重新加载。提供"Refresh Agents Skills"命令（`CommandIds.refreshSkills`）手动刷新。

## AI 使用技能的流程

AI 通过 Tool Calling 使用技能：

```
用户提出问题
  → AI 判断需要使用某个技能
    → 调用 discover_skills(query?) 查找相关技能
      → 返回匹配的技能列表（name + description）
    → 调用 load_skill(name: "my-skill")
      → 返回技能的 instructions 和 resources 列表
    → AI 阅读 instructions，按照指令执行
      → 如果需要参考资料，调用 load_skill(name, resource: "references/xxx.md")
      → 获取资源内容，继续执行
    → AI 根据技能指令生成回复
```

技能指令被注入到系统提示词上下文中，AI 遵循指令操作。

## 技能目录结构

```
skills-path/
├── data-analysis/              # 技能目录名即技能名（或由 SKILL.md frontmatter 指定）
│   ├── SKILL.md               # 必需：技能定义文件
│   └── references/
│       ├── pandas-guide.md    # 可选：参考资源
│       └── visualization.md
├── code-review/
│   ├── SKILL.md
│   └── templates/
│       └── review-template.md
└── writing-assistant/
    └── SKILL.md
```

## 注册自定义技能（代码方式）

除了从文件系统加载，扩展也可以通过代码直接注册技能：

```typescript
import { ISkillRegistry } from '@jupyternaut/agent';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:register-skill',
  autoStart: true,
  requires: [ISkillRegistry],
  activate: (app, skillRegistry) => {
    skillRegistry.registerSkill({
      name: 'my-builtin-skill',
      description: '内置的代码生成技能',
      instructions: `
        当用户要求生成代码时：
        1. 首先分析需求
        2. 生成符合最佳实践的代码
        3. 添加必要的注释
      `,
      resources: ['templates/python.md', 'templates/typescript.md'],
      loadResource: async (resource) => {
        // 自定义资源加载逻辑
        const content = await loadBuiltinResource(resource);
        return { name: 'my-builtin-skill', resource, content };
      }
    });
  }
};
```

`registerSkill()` 返回 `IDisposable`，dispose 时自动注销技能。

## /skills 聊天命令

jupyterlite-ai 注册了 `/skills` 聊天命令，用户可以在聊天中直接列出可用技能：

```
/skills              # 列出所有技能
/skills search-term  # 搜索特定技能
```

## 与 Tool 系统的关系

- **Tool**：AI 可以执行的动作（执行命令、抓取网页等），有输入/输出 Schema
- **Skill**：AI 遵循的指令和知识包，通过 Tool（discover_skills/load_skill）访问

Skill 可以理解为"AI 的操作手册"，Tool 是"AI 的手和脚"。AI 先通过 Skill 获得操作指南，再使用 Tool 执行具体操作。

## 相关概念

- [Tool 工具系统](04-tool-system.md)
- [Agent 执行引擎](05-agent-engine.md)
- [配置与设置](07-settings-and-config.md)
