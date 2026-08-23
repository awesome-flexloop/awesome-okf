---
type: Example
title: "自定义 AI 人设 (Persona)"
description: "使用 Jupyternaut Persona 系统自定义 AI 的角色设定、提示词和行为模式"
tags: [jupyterlite-ai, persona, customization, prompt, jupyternaut]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: plugin
    resource: /references/plugin-architecture.md
    title: 插件架构参考
---

# 自定义 AI 人设 (Persona)

JupyterLite AI 通过 `@jupyternaut/persona` 包支持自定义 AI 人设（Persona），允许你定义 AI 的角色、系统提示词、可用技能和行为模式。

## Persona 是什么？

Persona 定义了 AI 助手的"人格"，包括：
- **系统提示词**：AI 的角色设定和行为指令
- **可用技能集**：AI 可以使用哪些技能
- **工具访问权限**：AI 可以使用哪些工具
- **回复风格**：AI 的语言风格和格式偏好
- **领域专长**：AI 的专业领域知识

## 安装 Persona 包

Persona 系统通过 `jupyternaut-persona` Python 包分发：

```bash
pip install jupyternaut-persona
```

或者作为 JupyterLite AI 的一部分自动安装。

## 使用内置 Persona

JupyterLite AI 提供了默认的 Jupyternaut 人设，专门面向数据科学和 Jupyter 环境。

切换 Persona：
1. 打开 AI Chat 设置面板
2. 找到 **Persona** 选项
3. 从下拉列表中选择已安装的 Persona

## 开发自定义 Persona

### 方式一：通过配置文件定义

创建一个 Python 包或模块来定义你的 Persona：

```python
# my_persona.py
from jupyternaut_persona import Persona

my_persona = Persona(
    name="Python 导师",
    description="一位耐心的 Python 编程导师，专注于帮助初学者",
    system_prompt="""你是一位经验丰富的 Python 编程导师。

你的教学风格：
- 使用简单易懂的语言解释概念
- 总是提供可运行的代码示例
- 鼓励学生思考，而不是直接给出答案
- 遇到错误时，引导学生自己发现问题
- 使用类比和实际例子来说明抽象概念

你的专业领域：
- Python 基础语法和数据结构
- 面向对象编程
- 数据分析（pandas, numpy）
- 数据可视化（matplotlib, seaborn）
- Jupyter Notebook 使用技巧

回复格式要求：
- 代码示例必须完整可运行
- 复杂概念分步骤解释
- 重要提示使用 💡 标记
- 警告注意使用 ⚠️ 标记
""",
    tools=["execute_command", "browser_fetch"],
)
```

### 方式二：注册为 JupyterLab 扩展

创建 JupyterLab 扩展插件来提供 Persona：

```typescript
// src/index.ts
import { IJupyternautPersona } from '@jupyternaut/persona';

const myPersona: IJupyternautPersona = {
  id: 'my-python-mentor',
  name: 'Python 导师',
  description: '耐心的 Python 编程教学助手',
  systemPrompt: `你是一位经验丰富的 Python 编程导师...`,
  tools: ['execute_command', 'browser_fetch'],
  skills: ['code-explanation', 'debugging'],
};

const plugin: JupyterFrontEndPlugin<IJupyternautPersona> = {
  id: '@my-org/my-python-mentor',
  autoStart: true,
  provides: IJupyternautPersona,
  activate: (app: JupyterFrontEnd): IJupyternautPersona => {
    return myPersona;
  },
};

export default plugin;
```

## Persona 配置字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符 |
| `name` | string | 显示名称 |
| `description` | string | 简短描述 |
| `systemPrompt` | string | 系统提示词（核心） |
| `tools` | string[] | 允许使用的工具 ID 列表 |
| `skills` | string[] | 加载的技能列表 |
| `provider` | string | 默认提供商（可选） |
| `model` | string | 默认模型（可选） |
| `temperature` | number | 生成温度，0-2（可选） |
| `maxTokens` | number | 最大生成长度（可选） |

## 编写高效的系统提示词

### 好的提示词结构

```
1. 角色定义 — 你是谁
2. 核心任务 — 你做什么
3. 行为准则 — 你怎么做
4. 专业领域 — 你擅长什么
5. 约束条件 — 你不做什么
6. 输出格式 — 你怎么回复
```

### 示例：数据分析专家 Persona

```text
你是一位资深数据分析师，精通 Python 数据科学生态系统。

## 角色
- 你是用户的数据分析搭档
- 你擅长数据清洗、探索性分析、可视化和统计建模

## 工作流程
1. 理解分析目标
2. 检查数据质量
3. 提出分析思路
4. 编写代码并解释
5. 解读结果
6. 给出后续建议

## 代码规范
- 使用 pandas 和 numpy 进行数据处理
- 使用 matplotlib/seaborn/plotly 进行可视化
- 代码中添加必要的注释
- 每个代码块前说明目的

## 约束
- 不编造数据
- 分析结果要有统计依据
- 可视化要清晰标注坐标轴和标题
- 遇到数据问题主动指出

## 输出格式
- 使用 Markdown 格式
- 代码块标注语言类型
- 关键发现使用 **加粗** 强调
```

## Persona 与 Skill 的关系

Persona 可以选择性加载特定的技能集：

- **Persona** 定义 AI 的"身份"和全局行为
- **Skill** 定义 AI 在特定场景下的能力和知识

Persona 通过 `skills` 字段声明要加载的技能，技能管理器按需加载。

## 动态切换 Persona

在对话中可以切换 Persona：
1. 使用命令面板搜索 "Switch Persona"
2. 或在设置面板中选择不同的 Persona
3. 切换后新消息将使用新 Persona 的设定

## 最佳实践

1. **提示词具体明确**：避免模糊描述，给出具体的行为指令
2. **控制提示词长度**：过长的系统提示词会占用上下文窗口，建议控制在 1000-2000 字
3. **测试迭代**：先试用默认 Persona，根据实际体验逐步调整
4. **合理限制工具**：不需要的工具不要开放，减少 AI 的错误选择
5. **使用示例**：在提示词中给出期望回复的示例（few-shot learning）
