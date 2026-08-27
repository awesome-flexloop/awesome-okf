---
type: concept
title: "Claude API Skill 详解"
tags: [skills, claude-api, sdk, multi-language, api-reference, mcp, managed-agents]
sources:
  - id: anthropic-claude-api-skill
    title: Anthropic Claude API Official Skill
---

# Claude API Skill 详解

**claude-api** 是 Anthropic 官方提供的**多语言 API/SDK 参考权威来源** Skill。当用户需要编写调用 Claude API 的代码时，这个 Skill 会自动加载对应语言的最新 SDK 文档、代码示例、最佳实践和迁移指南，确保你使用的是**准确、最新**的 API 用法——避免依赖过时的记忆或猜测参数。

> ⚠️ **核心原则：Never guess SDK usage（永远不要猜测 SDK 用法）**——Claude API 和 SDK 在快速迭代，凭记忆写代码很容易用到已废弃的参数或错误的方法签名。当涉及 Claude API 调用时，始终使用 claude-api Skill 中的参考文档。

## claude-api Skill 是什么

claude-api Skill 是一个**活的 API 文档包**，它包含了 Claude API 所有主流编程语言的官方 SDK 参考、代码示例和使用指南。它解决了一个关键问题：AI 模型的训练数据有截止日期，而 Claude API 在持续更新——新模型、新参数、新功能不断推出，仅凭训练数据中的知识很容易写出过时或错误的代码。

### 核心价值

| 价值 | 说明 |
|------|------|
| **准确性** | 基于官方最新文档，避免使用废弃 API 或错误参数 |
| **多语言覆盖** | 支持 8 种主流语言，按需加载对应语言的参考 |
| **完整覆盖** | 从基础调用到高级功能（流式、工具调用、MCP、缓存等） |
| **迁移指南** | 包含版本间的迁移说明，帮助升级代码 |
| **最佳实践** | 内置官方推荐的错误处理、重试、配置等最佳实践 |

## 支持的语言

claude-api Skill 为以下编程语言提供专门的参考文档和代码示例：

| 语言 | SDK 包名 | 参考目录 |
|------|---------|---------|
| **Python** | `anthropic` | `references/python/` |
| **TypeScript/JavaScript** | `@anthropic-ai/sdk` | `references/typescript/` |
| **Java** | `com.anthropic:anthropic-java` | `references/java/` |
| **Go** | `github.com/anthropics/anthropic-sdk-go` | `references/go/` |
| **C# / .NET** | `Anthropic.SDK` | `references/csharp/` |
| **PHP** | `anthropic-php` | `references/php/` |
| **Ruby** | `anthropic-ruby` | `references/ruby/` |
| **cURL** | REST API 直接调用 | `references/curl/` |

每个语言目录下包含：
- 客户端初始化示例
- Messages API 基础调用
- 流式传输示例
- 工具调用（Tool Use）示例
- 视觉/文件处理示例
- 常见错误处理
- 该语言特有的用法和注意事项

## 核心文档内容

claude-api Skill 的 references/ 目录覆盖 Claude API 的两大块内容：

### 1. Claude API 基础文档

| 主题 | 内容 |
|------|------|
| **客户端初始化** | API key 配置、基础 URL、超时设置、重试策略 |
| **Messages API** | 消息格式、角色（user/assistant）、多轮对话 |
| **模型选择** | 模型 ID 列表（Opus/Sonnet/Haiku 各版本）、模型特性对比 |
| **流式传输（Streaming）** | SSE 流式、增量输出、打字机效果实现 |
| **工具调用（Tool Use）** | 定义工具、工具调用格式、并行工具调用、工具结果回传 |
| **视觉与文件** | 图片输入（base64/URL）、PDF 支持、文件格式要求 |
| **扩展思考（Extended Thinking）** | 思维链输出、思考 token 配置、adaptive thinking |
| **Token 计数** | 准确计算 token 用量、计费相关 |
| **提示缓存（Prompt Caching）** | 缓存配置、断点续用、成本优化 |
| **MCP（Model Context Protocol）** | MCP 概念、与 API 集成、工具扩展 |
| **错误处理** | 错误码列表、重试逻辑、速率限制处理 |
| **分页** | 列表类 API 的分页处理 |

> 🔗 Python SDK 详细用法参见 [/python-sdk/concepts/00-overview.md](/python-sdk/concepts/00-overview.md)

### 2. Managed Agents 文档

Managed Agents（托管代理）是 Claude API 的高级功能，提供：

- **持久化代理会话**：跨多轮交互保持代理状态
- **内置工具执行**：API 层面管理工具调用循环
- **文件搜索与代码解释器**：内置的高级工具
- **Vaults 凭证管理**：安全存储和使用第三方服务凭证
- **会话历史管理**：自动管理对话历史和上下文窗口

## API 漂移警告（2025-2026）

Claude API 和 SDK 在 2025-2026 年间有**重大更新**，很多旧代码和旧教程中的用法已经过时。以下是需要特别注意的变化——这也是为什么必须使用 claude-api Skill 而不是凭记忆写代码：

### 1. Adaptive Thinking 替代 budget_tokens

**旧用法（已废弃）**：
```python
# ❌ 旧写法，不再推荐
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # 固定预算
    }
)
```

**新用法（推荐）**：
```python
# ✅ 新写法：adaptive thinking
response = client.messages.create(
    model="claude-opus-4-0",  # 使用最新模型 ID
    max_tokens=20000,
    thinking={
        "type": "adaptive"  # 自适应，模型自动决定思考深度
    }
)
```

### 2. Web Search 工具版本更新

Web Search 工具经历了多个版本迭代，参数格式有变化：
- 早期版本使用 `type: "web_search"` 简单配置
- 新版本支持搜索范围定制、结果数量控制、区域设置
- 始终参考对应语言 SDK 文档中的最新工具定义格式

### 3. PHP SDK 参数命名：camelCase

PHP SDK 与其他语言不同，参数使用 **camelCase** 命名而非 snake_case：

```php
// ❌ 其他语言用 snake_case，但 PHP 是 camelCase
$response = $client->messages()->create([
    'model' => 'claude-opus-4-0',
    'maxTokens' => 20000,  // 注意是 maxTokens 不是 max_tokens
    'messages' => [...]
]);
```

### 4. Vaults 凭证管理

Vaults 是新推出的凭证管理功能，用于安全存储 API key、数据库连接串等敏感信息，避免在代码中硬编码。参考 Managed Agents 文档中的 Vaults 章节了解最新用法。

### 5. 模型 ID 更新

模型 ID 命名规则有调整，新版本使用更简洁的命名：

| 旧命名 | 新命名 |
|--------|--------|
| `claude-3-7-sonnet-20250219` | `claude-sonnet-4-0`（或最新版本号） |
| `claude-3-opus-20240229` | `claude-opus-4-0` |

> 💡 **始终使用 claude-api Skill 中的模型列表**获取最新的模型 ID，不要硬编码旧的模型 ID。

## 默认配置建议

claude-api Skill 推荐以下默认配置，适用于大多数场景：

### 推荐默认模型

**首选**：`claude-opus-4-0`（或最新的 Opus 版本）——最强大的能力，适合复杂任务
**平衡选择**：`claude-sonnet-4-0`——速度与能力的平衡，适合大多数生产场景
**快速/低成本**：`claude-haiku-4-0`——最快速度、最低成本，适合简单任务

### 推荐默认参数

```python
import anthropic

client = anthropic.Anthropic()  # 自动从 ANTHROPIC_API_KEY 环境变量读取

response = client.messages.create(
    model="claude-opus-4-0",
    max_tokens=20000,  # 给足输出空间，避免被截断
    thinking={
        "type": "adaptive"  # 启用自适应思考
    },
    stream=True,  # 默认使用流式，提供更好的用户体验
    messages=[...]
)
```

| 参数 | 推荐值 | 理由 |
|------|--------|------|
| `model` | 最新 Opus 版本 | 最强能力，减少因模型能力不足导致的问题 |
| `max_tokens` | 20000+ | Claude 3.7+ 支持大输出，给足空间避免截断 |
| `thinking.type` | `"adaptive"` | 让模型自动决定思考深度，质量与速度平衡 |
| `stream` | `True` | 流式输出提供更好的用户体验，超时风险更低 |

> ⚠️ 注意：`max_tokens` 是**必须参数**，不要遗漏——它限制的是最大输出 token 数，设置大一些不会增加成本，只会避免输出被截断。

## "Never Guess SDK Usage" 原则

这是使用 claude-api Skill 时最重要的原则：

### 为什么不能猜？

1. **API 快速迭代**：Claude API 每月都有新功能、新参数、新模型发布，训练数据很快过时
2. **多语言差异**：不同语言 SDK 的命名习惯、参数格式、异步支持可能不同
3. **废弃周期短**：旧参数可能很快被废弃，代码会在 SDK 升级后突然失效
4. **微妙差异**：有些参数名很像但行为完全不同（如 `temperature` 在不同模型版本的行为变化）

### 正确的使用流程

当你需要编写调用 Claude API 的代码时：

1. **检测项目使用的语言**：看 `package.json`（TS/JS）、`requirements.txt`/`pyproject.toml`（Python）、`pom.xml`（Java）等
2. **读取对应语言的参考文档**：加载 claude-api Skill 中该语言的 references 目录
3. **从示例开始修改**：复制官方示例代码，在此基础上修改，不要从零开始写
4. **检查迁移指南**：如果是升级现有代码，先读对应语言的迁移文档
5. **验证错误处理**：参考错误处理最佳实践，确保代码能优雅处理异常

### 反模式：要避免的做法

❌ **凭记忆写代码**："我记得参数是叫 budget_tokens..."——可能已经改了
❌ **用其他语言的写法类推**："Python 里是 max_tokens，PHP 里应该也是..."——PHP 用的是 camelCase
❌ **复制旧博客/教程代码**：网上的教程可能是基于一年前的 API 版本
❌ **省略必须参数**："max_tokens 应该是可选的吧..."——在 Messages API 中它是必填的
❌ **硬编码模型 ID**：`"claude-3-sonnet-20240229"`——应该使用最新的模型版本

## 使用方法

### 自动触发场景

claude-api Skill 会在以下场景自动触发：

- 用户询问如何调用 Claude API
- 用户需要用 Python/TypeScript/Java 等语言写 Claude SDK 代码
- 用户提到 tool use、streaming、prompt caching 等 API 功能
- 用户需要 SDK 安装、初始化、配置示例
- 用户遇到 API 错误需要排查
- 用户需要从旧版本 SDK 迁移到新版本
- 用户询问 Managed Agents、MCP 等高级功能
- 用户项目代码中出现 `import anthropic` 或 `@anthropic-ai/sdk` 等导入

### 使用时的工作流程

当 claude-api Skill 被激活后，代理会：

1. **检测语言**：分析用户项目或询问用户使用什么编程语言
2. **加载参考**：读取对应语言的 `references/<lang>/` 目录下的文档
3. **提供示例**：基于官方示例给出代码，而不是凭记忆生成
4. **遵循最佳实践**：应用错误处理、重试、配置等最佳实践
5. **提示更新**：如果用户代码中有过时用法，指出并给出迁移建议

### 手动触发

如果你明确需要使用 claude-api Skill，可以直接说：

- "参考 claude-api Skill，帮我写一个 Python 流式调用的示例"
- "用 Claude API 最新的用法实现工具调用"
- "帮我检查这段 Claude API 代码有没有过时的用法"

## 相关概念

- [Skills 生态概览](00-overview.md) — Skills 的基本概念和触发机制
- [SKILL.md 格式规范](01-skill-format.md) — 了解 claude-api 的 SKILL.md 是如何组织的
- [Skill Creator 工具详解](02-skill-creator.md) — 如果你想为其他 API 创建类似的参考 Skill
- [Python SDK 概览](/python-sdk/concepts/00-overview.md) — Python SDK 的详细文档
- [Python SDK Beta Agents](/python-sdk/concepts/08-beta-agents.md) — Managed Agents 相关的 Beta API
- [全部 Skills 索引](/official-skills/references/skills-index.md) — 查看其他官方 Skills
