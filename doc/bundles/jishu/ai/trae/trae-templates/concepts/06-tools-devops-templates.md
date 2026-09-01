---
type: Concept
title: 工具与 DevOps 模板
description: tools-devops 分类包含 4 个配置类模板：docker-compose（容器编排）、editor-config（编辑器统一配置）、gitignore（版本忽略规则）、superpowers-trae-init（AI 辅助开发工作流配置），它们不是可运行项目而是"复制即用"的开发工具配置。
tags: [trae-templates, devops, docker, editorconfig, gitignore, superpowers, trae-config]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 工具与 DevOps 模板总览

tools-devops 分类包含 4 个配置类模板，与其他分类的"项目模板"不同，它们是**配置模板**——不生成可运行的应用代码，而是提供开发工具和环境的配置：

| 模板 | 类型 | 核心文件 | 用途 |
|------|------|----------|------|
| docker-compose | 容器编排 | `docker-compose.yml` | 本地开发环境一键启动 |
| editor-config | 编辑器配置 | `.editorconfig` | 统一团队代码格式 |
| gitignore | 版本控制 | `Node.gitignore`、`Python.gitignore` | Git 忽略规则模板 |
| superpowers-trae-init | AI 工作流 | `.trae/rules/superpowers.md` + `.trae/skills/` | TRAE AI 辅助开发约束 |

这些模板可以与任何其他分类的项目模板组合使用。

## docker-compose：容器编排

**路径**：`templates/tools-devops/docker-compose/`

Docker Compose 启动配置，提供本地开发常用的服务编排。

**文件结构**（4 个文件）：
```
docker-compose/
├── docker-compose.yml    # Compose 服务定义
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**预定义服务**：

| 服务 | 镜像 | 端口 | 用途 |
|------|------|------|------|
| web | Nginx | 80 | Web 服务器 |
| db | PostgreSQL | 5432 | 关系型数据库 |

**常用命令**：
```bash
docker-compose up -d     # 后台启动所有服务
docker-compose down      # 停止并移除容器
docker-compose logs -f   # 查看日志
docker-compose ps        # 查看服务状态
```

**适用场景**：
- 本地开发需要数据库和 Web 服务器
- 快速搭建开发环境
- 团队统一本地服务配置

可以按需添加更多服务（Redis、MongoDB、RabbitMQ 等）到 compose 文件中。

## editor-config：编辑器统一配置

**路径**：`templates/tools-devops/editor-config/`

标准 .editorconfig 配置文件，统一不同编辑器的代码格式行为。

**文件结构**（3 个文件）：
```
editor-config/
├── .editorconfig    # 编辑器配置规则
├── README.md
└── README.zh-CN.md
```

**配置规则**：

| 规则 | 值 | 适用范围 |
|------|-----|----------|
| `root` | `true` | 根配置文件 |
| `charset` | `utf-8` | 所有文件 |
| `indent_style` | `space` | 所有文件 |
| `indent_size` | `2` | 所有文件（Python 除外） |
| `end_of_line` | `lf` | 所有文件 |
| `insert_final_newline` | `true` | 所有文件（Markdown 除外） |
| `trim_trailing_whitespace` | `true` | 所有文件（Markdown 除外） |
| `indent_size` | `4` | `*.py` 文件 |
| `insert_final_newline` | `false` | `*.md` 文件 |
| `trim_trailing_whitespace` | `false` | `*.md` 文件 |

**编辑器支持**：

| 编辑器 | 支持方式 |
|--------|----------|
| JetBrains IDE（IntelliJ/PyCharm/WebStorm） | 原生支持 |
| Visual Studio | 原生支持 |
| VS Code | 需安装 EditorConfig 插件 |
| Sublime Text | 需安装插件 |
| Vim | 需安装插件 |

**适用场景**：团队协作中统一代码格式，避免缩进/换行符/字符集等格式差异导致的 diff 噪音。

## gitignore：版本忽略模板

**路径**：`templates/tools-devops/gitignore/`

常用 .gitignore 模板集合。

**文件结构**（4 个文件）：
```
gitignore/
├── Node.gitignore       # Node.js 项目忽略规则
├── Python.gitignore     # Python 项目忽略规则
├── README.md
└── README.zh-CN.md
```

**使用方式**：选择对应技术栈的文件，复制到项目根目录并重命名为 `.gitignore`。

Node.gitignore 通常包含：`node_modules/`、`dist/`、`.env`、日志文件、锁文件（可选）、编辑器配置等。

Python.gitignore 通常包含：`__pycache__/`、`*.pyc`、`venv/`、`.env`、`*.egg-info/`、`dist/`、`build/` 等。

**最佳实践**：每个项目都应该有合适的 .gitignore 文件，避免将依赖目录、编译产物、密钥文件等提交到版本控制。

## superpowers-trae-init：AI 辅助开发工作流

**路径**：`templates/tools-devops/superpowers-trae-init/`

这是 templates 仓库中最特殊的模板——它不是代码项目模板，而是 **TRAE IDE 的 AI 开发工作流配置包**。改编自 obra/superpowers（MIT 许可证），裁剪为 TRAE 导向的设置。

**文件结构**：
```
superpowers-trae-init/
├── README.md
├── TEMPLATE_README.zh-CN.md
└── .trae/
    ├── rules/
    │   └── superpowers.md      # 核心规则文件（4条铁律+工具映射+触发器字典）
    └── skills/                 # 25+ 技能目录
        ├── brainstorming/
        ├── writing-plans/
        ├── test-driven-development/
        ├── systematic-debugging/
        ├── gardening-skills-wiki/
        ├── remembering-conversations/
        ├── using-superpowers/
        └── ...（共 25+ 个技能）
```

### 快速开始

1. 复制 `.trae/` 目录到项目根
2. 在 TRAE 中打开项目
3. 手动添加项目级核心记忆（标题"Superpowers 严格工作流约束"，关键词 `superpowers|workflow|tdd|debugging|skills`）
4. 新开会话让 TRAE 加载规则和技能集

核心记忆内容包含 4 条约束：
1. 严禁未经设计直接写代码，必须执行 brainstorming→using-git-worktrees→writing-plans→test-driven-development→code-review→finish-branch 闭环
2. Debug 时禁止猜测，必须调用 systematic-debugging
3. 技能必须通过 Skill 工具真实执行
4. 遇到卡壳使用 when-stuck 等技能

### 4 条铁律

superpowers.md 定义了不可违反的 4 条铁律：

| 铁律 | 含义 | 对应技能 |
|------|------|----------|
| **NO FIX WITHOUT ROOT CAUSE** | 禁止不查根因直接修复，必须系统化调试 | systematic-debugging |
| **NO PRODUCTION CODE WITHOUT RED TEST** | 禁止测试失败前写生产代码（TDD） | test-driven-development |
| **NO BLIND MOCKING** | 禁止 Mock 行为，必须测试真实行为 | testing-anti-patterns |
| **NO GUESSING THE OUTPUT** | 禁止未实际运行就宣布完成 | verification-before-completion |

这 4 条铁律本质上是 TDD（测试驱动开发）和系统化调试方法论在 AI 编码场景下的强制性转译。

### Trae 工具适配映射

superpowers.md 定义了 Agent 通用工具到 TRAE 特定实现的强制映射：

| Agent 通用工具 | TRAE 替代方案 | 要求 |
|----------------|---------------|------|
| CLI 输出跟踪 | TodoWrite | 使用 TodoWrite 跟踪任务进度 |
| spawn_agent（派发子代理） | Task 工具 | 必须两阶段审查：Spec 对齐度 + 代码质量 |
| 本地知识库 | manage_core_memory | 使用 Core Memory 持久化项目知识 |

### 触发器字典

将开发场景分类到三组触发器，每组对应应加载的技能：

**架构与计划**（4 个技能）：
- `brainstorming`：创意头脑风暴
- `writing-plans`：编写实现计划
- `when-stuck`：卡壳时求助
- `simplification-cascades`：简化级联

**开发与审查**（4 个技能）：
- `subagent-driven-development`：子代理驱动开发
- `test-driven-development`：测试驱动开发
- `testing-anti-patterns`：测试反模式识别
- `requesting-code-review`：代码审查请求

**排错与闭环**（4 个技能）：
- `systematic-debugging`：系统化调试
- `root-cause-tracing`：根因追踪
- `condition-based-waiting`：条件等待
- `verification-before-completion`：完成前验证

### 25+ 技能生态

`.trae/skills/` 目录下包含 25+ 个技能子目录，其中较完整的包括：

| 技能 | 包含内容 |
|------|----------|
| gardening-skills-wiki | Shell 脚本：analyze-search-gaps.sh、check-links.sh、garden.sh 等 |
| remembering-conversations | 完整 TypeScript 实现（13个 .ts 文件：db.ts/embeddings.ts/indexer.ts/search.ts/summarizer.ts），含 install-hook/index-conversations/search-conversations 入口 |
| condition-based-waiting | example.ts 示例文件 |
| requesting-code-review | code-reviewer.md 参考文件 |
| root-cause-tracing | find-polluter.sh 脚本 |
| systematic-debugging | CREATION-LOG.md 和 test-pressure 文件 |
| using-superpowers | find-skills 和 skill-run 可执行脚本 |
| writing-skills | graphviz-conventions.dot 和 persuasion-principles.md |

**注意**：与 trae-skills 社区技能不同，`.trae/skills/` 下的技能可以包含真正的可执行代码实现（如 remembering-conversations 的 TypeScript 实现），因为它们是项目级配置的一部分。

## 非项目模板的价值

tools-devops 分类的存在揭示了一个重要洞察：模板库的收录标准是**"复制即用"**而非"必须是可运行项目"。这扩展了模板库的边界：

1. **配置即模板**：.editorconfig、.gitignore、docker-compose.yml 都是开发必需品
2. **AI 配置即模板**：superpowers-trae-init 将 AI 开发工作流也纳入模板范畴
3. **可组合**：配置模板可以与任何项目模板叠加使用

## 模板组合推荐

每个项目建议至少添加：

| 模板 | 是否推荐 | 理由 |
|------|----------|------|
| editor-config | ✅ 推荐 | 统一格式，减少 diff 噪音 |
| gitignore | ✅ 必需 | 避免提交不应版本控制的文件 |
| docker-compose | 按需 | 需要本地数据库/服务时添加 |
| superpowers-trae-init | 推荐（AI 辅助开发） | 建立 AI 编码质量门禁 |

## 相关概念

- [五维分面分类体系](01-template-classification.md)
- [AGENTS.md 开发契约](07-agents-contract.md)

## 相关内容

- [源码信源索引](../references/templates-source.md)
- [使用 superpowers-trae-init 初始化环境](../examples/use-superpowers-init.md)
- [AGENTS.md 配置示例](../examples/agents-md-config.md)
