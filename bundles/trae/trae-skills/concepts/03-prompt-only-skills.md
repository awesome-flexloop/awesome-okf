---
type: Concept
title: 纯 Prompt 型技能
description: 纯 Prompt 型技能仅依靠 SKILL.md 中的自然语言指令指导 Agent 行为，无需任何脚本。社区中 cn-punctuation-checker、git-commit-generator、web-design-teroop、wechat-mini-program-development、cloudbase 均为此模式，是最简单也最常用的技能形态。
tags: [trae-skills, pure-prompt, cn-punctuation-checker, git-commit-generator, web-design-teroop]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 纯 Prompt 型的本质

纯 Prompt 型技能是最简单的技能形态——仅包含 `SKILL.md` 指令文件和可选的文本资源（examples/templates/resources 中的 Markdown/文本文件），不含任何可执行脚本。Agent 利用自身的内置能力（文件读写、Shell 执行、代码编辑、WebFetch、MCP 工具调用等）来完成 SKILL.md 中描述的任务。

这种模式的核心洞察是：**Agent 本身已经具备丰富的执行能力**，大多数场景不需要额外的代码来"扩展能力"，只需要精确的指令来"引导行为"。SKILL.md 的作用就像是给 Agent 的一份详细操作手册。

## 社区纯 Prompt 型技能一览

| 技能 | name | 核心能力 | Agent 内置能力依赖 |
|------|------|----------|-------------------|
| git-commit-generator | `git-commit-generator` | 基于 git diff 生成 Conventional Commits 提交信息 | Shell（git diff）、文件读取、模板填充 |
| cn-punctuation-checker | `"cn-punctuation-checker"` | 中文标点错误检测与修复 | 文件读写、正则匹配、文本替换 |
| web-design-teroop | `web-design-teroop` | 创建/维护设计规范文档 | 文件写入（.design-spec.md）、Core Memory 更新、AskUserQuestion 交互、代码生成 |
| wechat-mini-program-development | `"wechat-mini-program-development"` | 微信小程序项目结构搭建与代码生成 | 文件/目录创建、代码编写、配置文件生成 |
| cloudbase | `cloudbase` | 腾讯云开发应用构建/部署/调试 | MCP 工具调用（CloudBase MCP） |

## 编写模式解析

### 模式一：分析→生成型（git-commit-generator）

git-commit-generator 是纯 Prompt 型技能的典型代表，采用经典的"分析→生成→输出"三步流程：

1. **分析变更**：读取 `git diff` 输出，分析变更范围、确定 scope（影响范围）、参考 `resources/conventional-commits-types.md` 确定 type（feat/fix/docs 等）
2. **构造提交信息**：遵循 `templates/commit-message.txt` 模板结构 `<type>(<scope>): <subject>`，使用祈使语气、无句号、50 字符以内；正文用 bullet points 说明 what/why
3. **输出结果**：代码块格式输出，多逻辑变更建议拆分

**关键设计**：
- 使用 `resources/conventional-commits-types.md` 作为规范参考文件，避免在 SKILL.md 中重复大段类型定义
- 使用 `templates/commit-message.txt` 作为输出模板，确保格式一致性
- 提供 `examples/input.md` 和 `examples/output.md` 作为参考样例

### 模式二：规则检查型（cn-punctuation-checker）

cn-punctuation-checker 采用规则驱动的检查模式，甚至没有遵循标准的 Description/Usage Scenario/Instructions 章节结构，而是自定义了 Features/Supported Punctuation Marks/Usage/Execution Flow/Smart Detection Rules 结构：

1. **Features**：列出核心功能（精确位置报告、Markdown 格式报告、批量修复、项目级扫描）
2. **Supported Punctuation Marks**：定义 12 组英文→中文标点映射规则（`,→，` `.→。` `?→？` `!→！` `:→：` `;→；` `"→"/"` `'→'/ '` `( )→（）` `[ ]→【】` `-→—` `...→……`）
3. **Execution Flow**：定义执行步骤
4. **Smart Detection Rules**：智能检测规则（仅检查含中文的行、排除 URL/路径/代码字符串/Markdown 代码块等）

**关键设计**：
- 默认检查文件类型和排除目录都在 SKILL.md 中穷举列出
- 智能检测规则详细到可直接指导 Agent 进行精确匹配
- 虽然不遵循标准章节结构，但功能描述足够精确，仍能正常触发和工作

### 模式三：多步骤代码生成型（wechat-mini-program-development）

wechat-mini-program-development 采用 8 步线性指令指导 Agent 从零搭建微信小程序项目：

1. 项目结构搭建
2. 创建 `utils/config.js`（baseUrl/timeout/appId，CommonJS 语法）
3. 创建 `utils/api.js`（集中端点管理，user/goods/order 模块）
4. 创建 `utils/request.js`（统一请求/响应拦截器）
5. 创建 `utils/util.js`（工具函数：formatTime/showLoading 等）
6. 设置全局登录检查（`app.js` 中 onLaunch 调用 checkLoginStatus）
7. 配置 tabBar（`app.json` 中配置 pages/window/tabBar）
8. 使用示例

**关键设计**：
- 每步明确要创建的文件路径和文件内容要点
- 对关键实现细节（如 request.js 拦截器特性）做详细说明
- 提供标准项目结构约定（app.js/app.json/pages/components/utils/assets/.trae/）

request.js 拦截器特性被详细描述：
- 自动拼接完整 URL、添加 Content-Type、注入 token
- 响应端 HTTP 200-299 为成功、业务 code===0 为成功、自动返回 data
- 401 自动跳转登录页清 token、5xx 和网络错误统一处理

### 模式四：角色扮演+流程型（web-design-teroop）

web-design-teroop 将 Agent 定位为"首席设计架构师"角色，采用 5 步设计流程：

1. **预检**：查找根目录 `.design-spec.md` 或 Core Memory 中已有设计
2. **发现阶段**：搜索 4 种流行网页设计风格，让用户选择视觉风格和氛围
3. **生成规范**：5 个维度（设计风格、色彩方案、字体排版、图标策略、Logo 概念）写入 `.design-spec.md` 并更新 Core Memory
4. **布局调整**：调用 AskUserQuestion 确认调整方向，同步更新文件和内存
5. **技术合成**：转换为 tailwind.config.js 配置，提供 React 组件实现

**关键设计**：
- 通过角色定位设定 Agent 的专业视角
- 设计规范持久化到 `.design-spec.md` 文件和 Core Memory 双重存储
- 维护规则：所有后续 UI 开发必须先读 `.design-spec.md`；设计变更必须同步更新文件和内存
- 使用 AskUserQuestion 工具进行交互式确认

### 模式五：MCP 工具集成型（cloudbase）

cloudbase 技能指导 Agent 使用 CloudBase MCP 工具完成腾讯云开发操作，采用 7 步流程：

1. 确认场景（Web/小程序/云函数/CloudRun 等）
2. 确保 CloudBase MCP 可用（提供配置 JSON）
3. 显式绑定环境（调用 envQuery 解析 EnvId）
4. 优先使用 MCP 工具做管理工作
5. 加载匹配的已发布 CloudBase skill
6. 按顺序实现（资源准备→前后端代码→本地验证→部署）
7. 收尾（运行 cloudbase-code-review、报告 EnvId 和 URL）

**关键设计**：
- 提供 MCP 配置 JSON 供 Agent 配置：`{"mcpServers":{"cloudbase-mcp":{"command":"npx","args":["-y","@cloudbase/cloudbase-mcp@latest"],"env":{}}}}`
- 约束条款（防越界）：不得编造 API 路径或参数、不得暴露凭证、同一路径 2-3 次失败后停止并重路由

## 纯 Prompt 型技能的编写要点

从社区实例中总结的编写要点：

1. **触发条件精确**：description 字段必须包含功能+触发场景双重信息
2. **步骤编号清晰**：使用有序列表或编号明确执行顺序
3. **关键细节详尽**：对文件路径、配置格式、API 参数等具体细节不能含糊
4. **约束条款明确**：列出"什么不能做"与"什么能做"同等重要
5. **参考文件分离**：大段的规范定义（如 Conventional Commits 类型、标点映射表）可放入 resources/ 目录
6. **输出模板化**：用 templates/ 目录定义输出格式模板
7. **示例引路**：examples/ 目录提供 input/output 样例，帮助 Agent 理解期望产出

## 什么时候应该升级到脚本辅助型

当出现以下情况时，纯 Prompt 型技能应该考虑引入脚本升级为脚本辅助型：

- 需要调用外部 HTTP API 获取数据（Agent 虽然可以用 WebFetch，但复杂 API 交互用脚本更可靠）
- 需要进行复杂数学计算或数据处理（如视频帧分析、图像处理）
- 需要处理二进制数据（如视频抽帧、文件格式转换）
- 需要多步骤数据流水线处理（如抓取→清洗→格式化）
- 纯指令描述的规则过于复杂，用代码表达更精确

## 相关概念

- [技能分类与模板模式](/concepts/02-skill-categories.md)
- [脚本辅助型技能](/concepts/04-script-assisted-skills.md)
- [Workflow 编排型技能](/concepts/05-workflow-skills.md)
- [SKILL.md 格式规范](/concepts/01-skill-format.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)
- [创建第一个 Skill](/examples/create-first-skill.md)
- [触发条件设计示例](/examples/trigger-condition-design.md)
