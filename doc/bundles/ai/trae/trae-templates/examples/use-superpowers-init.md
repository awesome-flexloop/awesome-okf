---
type: Example
title: 使用 superpowers-trae-init 初始化 AI 辅助开发环境
description: 将 superpowers-trae-init 的 .trae/ 目录复制到项目，配置核心记忆，验证 4 条铁律生效，建立 AI 辅助开发的质量门禁。
tags: [trae-templates, example, superpowers, ai-workflow, trae-config, iron-rules]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 示例目标

将 `superpowers-trae-init` 模板集成到一个已有项目（或新项目），配置 TRAE AI 辅助开发环境，验证 4 条铁律生效。

## 步骤 1：复制 .trae/ 目录

在项目根目录执行：

```bash
# 进入项目目录
cd your-project-root

# 复制 .trae/ 目录（从 trae-templates 仓库）
cp -r /path/to/trae-templates/templates/tools-devops/superpowers-trae-init/.trae .
```

复制后项目结构：

```
your-project/
├── .trae/
│   ├── rules/
│   │   └── superpowers.md       # 4条铁律+工具映射+触发器字典
│   └── skills/                   # 25+ 项目级技能
│       ├── brainstorming/
│       ├── writing-plans/
│       ├── test-driven-development/
│       ├── systematic-debugging/
│       ├── remembering-conversations/
│       └── ...
├── src/                          # 你的项目代码
├── package.json
└── ...
```

## 步骤 2：在 TRAE 中打开项目

用 TRAE IDE 打开项目根目录。TRAE 会自动识别 `.trae/` 目录结构。

## 步骤 3：添加项目级核心记忆

在 TRAE 中手动添加项目级核心记忆（Core Memory）：

1. 打开 Core Memory 管理界面
2. 添加新记忆条目：
   - **标题**：Superpowers 严格工作流约束
   - **关键词**：`superpowers|workflow|tdd|debugging|skills`
   - **内容**：
     ```
     本项目使用 Superpowers 严格工作流：
     1. 严禁未经设计直接写代码，必须执行 brainstorming→using-git-worktrees→writing-plans→test-driven-development→code-review→finish-branch 闭环
     2. Debug 时禁止猜测，必须调用 systematic-debugging 技能
     3. 技能必须通过 Skill 工具真实执行，不能只口头提及
     4. 遇到卡壳使用 when-stuck 等技能求助
     ```

关键词 `superpowers|workflow|tdd|debugging|skills` 确保在相关对话中自动召回这些约束。

## 步骤 4：新开会话加载规则

关闭当前会话，新开一个会话。TRAE 会：
1. 自动加载 `.trae/rules/superpowers.md` 规则文件
2. 识别 `.trae/skills/` 下的项目级技能
3. 通过关键词召回核心记忆中的 Superpowers 约束

## 步骤 5：验证铁律生效

通过以下测试验证 4 条铁律是否生效：

### 测试铁律 1（NO FIX WITHOUT ROOT CAUSE）

**测试方法**：对 AI 说"这个函数报错了，帮我加个 try-catch 修好"

**期望反应**：AI 不应直接加 try-catch，而应该先询问错误信息、执行 systematic-debugging 流程定位根因。

### 测试铁律 2（NO PRODUCTION CODE WITHOUT RED TEST）

**测试方法**：对 AI 说"帮我实现一个用户登录功能"

**期望反应**：AI 不应直接写实现代码，而应该先编写失败的测试用例，然后再写代码使测试通过。

### 测试铁律 3（NO BLIND MOCKING）

**测试方法**：对 AI 说"写一个数据库查询的单元测试，mock 掉数据库"

**期望反应**：AI 应该警告不要盲目 Mock，建议使用测试数据库或集成测试。

### 测试铁律 4（NO GUESSING THE OUTPUT）

**测试方法**：AI 写完代码后，观察它是否会主动运行测试/构建来验证结果。

**期望反应**：AI 写完代码后应该执行 `npm test`、`npm run build` 等验证命令，而不是直接说"完成了"。

## 步骤 6：体验触发器字典

在开发过程中，观察 AI 是否按触发器字典加载对应技能：

### 架构设计场景

对 AI 说"我需要设计一个用户认证系统"

期望：自动加载 brainstorming 和 writing-plans 技能，先进行设计讨论和计划编写。

### Bug 调试场景

对 AI 说"登录接口返回 500 错误"

期望：自动加载 systematic-debugging 和 root-cause-tracing 技能，执行系统化调试流程。

### 代码完成场景

对 AI 说"这个功能写完了"

期望：自动加载 requesting-code-review 和 verification-before-completion 技能，请求代码审查并运行验证。

## 步骤 7：根据项目定制

### 调整铁律

编辑 `.trae/rules/superpowers.md`，根据团队规范调整：
- 添加代码风格约束（如"必须使用 ESLint 检查"）
- 添加安全规则（如"禁止在代码中硬编码密钥"）
- 添加提交规范（如"commit message 必须符合 Conventional Commits"）

### 添加项目特定技能

在 `.trae/skills/` 下创建项目特定技能目录：

```
.trae/skills/
└── my-project-workflow/
    └── SKILL.md    # 项目特定的工作流技能
```

### 移除不需要的技能

删除不适用的技能目录。例如，如果项目不使用子代理开发，可以移除 subagent-driven-development。

## remembering-conversations 技能

25+ 技能中最值得关注的是 remembering-conversations，它提供对话记忆能力：

### 安装钩子

```bash
cd .trae/skills/remembering-conversations
# 运行安装脚本设置会话结束钩子
```

### 功能

- **install-hook**：安装会话结束时的自动索引钩子
- **index-conversations**：将历史对话索引到向量数据库
- **search-conversations**：语义搜索历史对话内容

这个技能包含完整的 TypeScript 实现（13 个 .ts 文件），使用 SQLite 和向量嵌入存储对话历史。

## 常见问题

**Q: 新开会话后规则没有生效？**
A: 确认核心记忆已正确添加且关键词匹配。可以在新会话开头提到"superpowers"或"TDD"来触发记忆召回。

**Q: 4 条铁律太严格了，可以放宽吗？**
A: 可以。编辑 `.trae/rules/superpowers.md` 修改铁律内容。但建议先尝试严格模式，遇到问题再逐步放宽。

**Q: 可以在已有项目中添加 superpowers 吗？**
A: 可以。直接复制 `.trae/` 目录即可，不影响已有代码。

**Q: superpowers 和 trae-skills 社区技能有什么区别？**
A:
- trae-skills 社区技能是全局共享的技能，安装在 `~/.trae/skills/`
- superpowers 技能是项目级的，安装在 `.trae/skills/`，随项目版本控制
- superpowers 更强调工作流约束和质量门禁

**Q: 不使用 superpowers 可以吗？**
A: 可以。superpowers-trae-init 是可选模板。简单项目可以只使用代码模板（如 nextjs-starter），不需要 AI 工作流配置。

## 相关概念

- [AGENTS.md 开发契约](/concepts/07-agents-contract.md)
- [工具与 DevOps 模板](/concepts/06-tools-devops-templates.md)

## 相关内容

- [源码信源索引](/references/templates-source.md)
- [使用 Next.js 模板创建项目](/examples/use-nextjs-template.md)
- [AGENTS.md 配置示例](/examples/agents-md-config.md)
