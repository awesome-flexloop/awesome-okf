---
type: Reference
title: i-have-adhd 源码信源登记
description: ADHD 友好输出风格 Skill 的源码结构、10 条输出规则、hooks always-on 机制、多平台集成配置、评估体系与 CI 工作流信源清单
tags: [i-have-adhd, output-style, adhd, skill, prompt-engineering, claude-code, codex, cursor, gemini, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: i-have-adhd-github
    resource: https://github.com/ayghri/i-have-adhd
    title: i-have-adhd GitHub 仓库
---

# i-have-adhd 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | i-have-adhd |
| 版本 | 0.1.0 |
| 作者 | Ayoub G. (https://github.com/ayghri) |
| 许可证 | MIT |
| 定位 | 面向 ADHD 读者的输出风格塑造技能（output-style skill） |
| Slogan | "ADHD-friendly outputs. No ADHD diagnosis needed!" |
| 仓库 | https://github.com/ayghri/i-have-adhd |
| 理论依据 | 松散基于 *The Adult ADHD Tool Kit* by J. Russell Ramsay 和 Anthony L. Rostain |
| 核心规则数 | 10 条输出规则 + 6 条破规例外 |
| 支持平台数 | 10+ IDE/Agent 平台 |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\models\ai\i-have-adhd\` |

## 目录结构

```
i-have-adhd/
├── README.md                    # 主文档（英文）
├── README.zh-CN.md              # 中文文档
├── README.ja.md                 # 日文文档
├── README.ko.md                 # 韩文文档
├── INSTALL.md                   # 多平台安装指南（10+ 平台，588行）
├── GEMINI.md                    # Gemini 扩展入口（@import SKILL.md）
├── LICENSE                      # MIT
├── logo.png                     # 项目 logo
├── plugin.json                  # Antigravity (agy) 插件描述
├── gemini-extension.json        # Gemini CLI 扩展配置
├── .gitignore                   # 忽略 .DS_Store, __pycache__, evals/results/
├── skills/
│   └── i-have-adhd/
│       ├── SKILL.md             # 核心技能定义（142行，含10条规则）
│       └── agents/
│           ├── gemini.toml      # Gemini CLI 自定义命令（精简内联 prompt）
│           └── openai.yaml      # Codex/OpenAI 接口配置
├── hooks/
│   ├── hooks.json               # SessionStart 钩子注册
│   └── always-on.sh             # POSIX sh 始终激活脚本（30行）
├── scripts/
│   └── run_evals.py             # 评估运行器（371行）
├── evals/
│   ├── README.md                # 评估使用说明
│   ├── rubric.md                # 评分标准（5维度+权重）
│   ├── cases.jsonl              # 14 个评估用例
│   └── runners.example.json     # runner 配置示例
├── tests/
│   └── test_run_evals.py        # 评估脚本单元测试（9 用例）
├── .claude-plugin/              # Claude Code 插件
│   ├── plugin.json
│   └── marketplace.json
├── .codex-plugin/               # Codex 插件
│   └── plugin.json
├── .cursor/                     # Cursor 技能（完整副本，非符号链接）
│   └── skills/i-have-adhd/SKILL.md
├── .agents/                     # 通用 Agent marketplace
│   └── plugins/marketplace.json
└── .github/
    └── workflows/               # 3 个 CI 工作流
        ├── claude.yml            # Claude Code Action 触发
        ├── cursor-skill-sync.yml # Cursor 副本同步检查
        └── plugin-load-check.yml # 插件加载验证
```

## 关键文件清单

### 核心技能定义

| 文件 | 内容 |
|------|------|
| `skills/i-have-adhd/SKILL.md` | **核心文件**（142行）：YAML frontmatter + 5 个认知模型 + 10 条输出规则 + 6 条破规例外 + 发送前检查清单 + 持久性机制 |
| `.cursor/skills/i-have-adhd/SKILL.md` | Cursor 平台的 SKILL.md 完整副本（非符号链接，保证 Windows/ZIP 兼容） |

### Hooks Always-On 机制

| 文件 | 内容 |
|------|------|
| `hooks/hooks.json` | SessionStart 钩子注册：matcher `startup\|resume\|clear\|compact`，command 类型执行 always-on.sh，超时 5 秒 |
| `hooks/always-on.sh` | POSIX sh 脚本：检查 `~/.claude/.i-have-adhd-always` 标志文件，存在则用 awk 剥离 frontmatter 输出规则文本，任何失败 exit 0 |

### 平台集成配置

| 文件 | 平台 | 内容 |
|------|------|------|
| `.claude-plugin/plugin.json` | Claude Code | 插件元数据 |
| `.claude-plugin/marketplace.json` | Claude Code | Marketplace 配置 |
| `.codex-plugin/plugin.json` | Codex | 插件配置（含 interface/displayName/category/defaultPrompt） |
| `.cursor/skills/i-have-adhd/SKILL.md` | Cursor | Skill 完整副本 |
| `gemini-extension.json` | Gemini CLI | 扩展配置（contextFileName: "GEMINI.md"） |
| `GEMINI.md` | Gemini CLI | `@./skills/i-have-adhd/SKILL.md` 导入完整技能 |
| `skills/i-have-adhd/agents/gemini.toml` | Gemini CLI | 自定义命令（精简内联 prompt ~20行） |
| `skills/i-have-adhd/agents/openai.yaml` | Codex/OpenAI | 接口配置（allow_implicit_invocation: true） |
| `plugin.json` | Antigravity (agy) | 插件描述 |
| `.agents/plugins/marketplace.json` | 通用 Agent | Marketplace 配置 |

### 评估体系

| 文件 | 内容 |
|------|------|
| `evals/cases.jsonl` | 14 个评估用例（id/category/prompt/risk/criteria），覆盖 13 类别 |
| `evals/rubric.md` | 评分标准：correctness 35%、autonomy 25%、actionability 20%、safety 10%、concision 10%；发布门槛 |
| `evals/runners.example.json` | Runner 配置示例（Claude/Codex 隔离参数） |
| `evals/README.md` | 评估使用说明、隔离设计原因 |
| `scripts/run_evals.py` | 评估运行器（371行）：validate/plan/run/score 四个子命令；支持断点续跑 |
| `tests/test_run_evals.py` | 单元测试（9 用例）：用例合法性、加权评分、发布门槛、去重、断点续跑等 |

### CI/CD 工作流

| 文件 | 内容 |
|------|------|
| `.github/workflows/claude.yml` | issue/PR 评论含 `@claude` 时触发 Claude Code Action |
| `.github/workflows/cursor-skill-sync.yml` | PR/push 时用 `cmp` 检查 Cursor 副本与规范 SKILL.md 一致性 |
| `.github/workflows/plugin-load-check.yml` | PR/push 时安装 Claude Code + 本地插件，验证加载到 "enabled" 状态 |

### 文档

| 文件 | 内容 |
|------|------|
| `README.md` | 英文主文档（118行） |
| `README.zh-CN.md` | 简体中文文档 |
| `README.ja.md` | 日本語文档 |
| `README.ko.md` | 한국어文档 |
| `INSTALL.md` | 10+ 平台安装指南（588行） |

## SKILL.md Frontmatter

```yaml
---
name: i-have-adhd
description: ...（描述功能与调用方式 /i-have-adhd）
disable-model-invocation: true
license: MIT
metadata:
  hermes:
    tags: [ADHD, Output Style, Productivity, Formatting]
    category: productivity
---
```

**关键字段**：
- `disable-model-invocation: true`：阻止模型自动激活，必须用户显式调用 `/i-have-adhd`
- `metadata.hermes`：Hermes 平台标签和分类

## 5 个 ADHD 认知模型基础

规则基于 5 个驱动性认知特征：

| # | 认知特征 | 设计含义 |
|---|---------|---------|
| 1 | 工作记忆小 | 不在屏幕上的东西会被遗忘，不让读者"记住 X" |
| 2 | 知≠行 | "知道了"到"做完了"之间的摩擦是工作死亡区 |
| 3 | 启动最难 | 第一个动作必须明显、小、现在就能做 |
| 4 | 时间估计同质化 | "一点工作"和"几小时"感觉一样，模糊估计失效 |
| 5 | 多巴胺稀缺 | 可见进展很重要，被埋没的成果不会被感知 |

## 10 条输出规则完整索引

| # | 规则名 | 核心要求 | Bad/Good 示例要点 |
|---|--------|---------|------------------|
| 1 | 行动优先 (Lead with the next action) | 第一行必须是可执行动作（命令/路径/代码片段），叙述在后 | Bad: "Let's think about..." / Good: "Run `npm install`, then edit `src/auth.ts:42`." |
| 2 | 编号多步任务 (Number multi-step tasks) | 超过一步用编号列表，每步有界动作，禁止 "and then" 链式；最少步骤数 | 原则: "A short path finished beats a complete path abandoned." |
| 3 | 一个具体下一步结束 (End with one concrete next action) | 未完成时指定 2 分钟内可完成的动作 | Bad: "Hope that helps..." / Good: "Next: run `npm test` and paste the first failing line." |
| 4 | 抑制题外话 (Suppress tangents) | 完成第一个问题后才提第二个，独立提出 | Bad: "By the way, your dependency is also stale..." / Good: "Separately: there is also a stale dependency. Want me to handle that next?" |
| 5 | 每回合重申状态 (Restate state every turn) | 明确当前进度位置 | Bad: "Done. Ready for next?" / Good: "Step 3 of 5 done: schema updated. Next: backfill the new column." |
| 6 | 具体时间估计 (Give specific time estimates) | 用具体单位估算 | Bad: "This will take some work." / Good: "About 15 minutes if tests cover this. An afternoon if not." |
| 7 | 已完成工作可见 (Make completed work visible) | 用具体语言展示什么能用了 | Bad: "I've made some changes..." / Good: "Login now works with magic links. Try: `npm run dev`, open `/login`." |
| 8 | 错误平实语气 (Matter-of-fact tone for errors) | 禁止 "Uh oh"/"Oh no"，直接陈述原因和修复 | Bad: "Uh oh, the test is failing..." / Good: "Test fails at `auth.spec.ts:42`: expected 200, got 401." |
| 9 | 列表限制 5 项 (Cap lists at 5 items) | 超 5 项分"现在做/以后做"或"必须/锦上添花" | 5 项有排名胜过 10 项无排名 |
| 10 | 禁止前言/总结/客套 (No preamble, no recap, no closing) | 禁止开头 "Great question"/"Let me..."/"Sure!"；禁止结尾 "Hope this helps"/"Let me know..." | 从答案开始，答案结束就停止 |

## 规则持久性机制

- 规则一旦激活，适用于会话中后续**所有响应**
- 不会在几轮后过期，不会在主题切换时失效
- **关闭方式仅两种**：
  1. 读者说 "stop adhd mode" 或 "normal mode"
  2. 一行确认后返回默认风格

## 6 条破规例外（When to break the rules）

| # | 例外条件 | 处理方式 |
|---|---------|---------|
| 1 | 用户请求解释（"explain"/"walk me through"） | 充分解释，仍无前言/结尾，加标题便于回看 |
| 2 | 破坏性操作（rm -rf、强制推送、schema 迁移、删表） | 操作前确认，安全优先于简洁 |
| 3 | 调试螺旋（连续三轮"仍然出错"） | 停止迭代代码，指出可能错误假设，问一个诊断问题 |
| 4 | 真实歧义 | 一个简短澄清问题胜过猜测重写 |
| 5 | 规则与任务冲突（如"有哪些选项"） | 任务获胜，形状保留（2-4 个带权衡的排序选项） |
| 6 | 规则与平台冲突 | agent harness system prompt 优先级高于本技能 |

## 发送前检查清单（Pre-send check）

必须删除：
1. 宣布"我将要做什么"的第一句
2. 问"还有别的吗"或总结刚发生什么的最后一句
3. 任何 "by the way" 旁注
4. 不增加信息的模糊副词（"perhaps"/"might"/"could possibly"）；携带真实不确定性的保留
5. 习语/比喻短语（"circle back"/"get the ball rolling"/"on the same page"），替换为字面动作

**验证标准**：读者只读第一行和最后一行，是否知道 (a) 下一步做什么，(b) 刚发生了什么？

## 多平台集成索引

| 平台 | 配置文件 | 调用方式 | always-on 方式 | 隐式调用 |
|------|---------|---------|---------------|---------|
| **Claude Code** | `.claude-plugin/plugin.json` + `marketplace.json` | `/i-have-adhd` | `~/.claude/.i-have-adhd-always` 标志 + SessionStart hook | 否（disable-model-invocation: true） |
| **Codex** | `.codex-plugin/plugin.json` | `$i-have-adhd` | 写入 `~/.codex/AGENTS.md` | 是（allow_implicit_invocation: true） |
| **Cursor** | `.cursor/skills/i-have-adhd/SKILL.md`（完整副本） | `/i-have-adhd` | Settings → Rules → User Rules 或 `.cursor/rules/` alwaysApply: true | — |
| **Gemini CLI** | `gemini-extension.json` + `GEMINI.md` + `gemini.toml` | `/i-have-adhd`（命令）/ extension always-on | gemini extensions install | 是（extension） |
| **Antigravity (agy)** | 根目录 `plugin.json` | agy plugin 机制 | 写入 `~/.gemini/GEMINI.md` | — |
| **Zed** | 原生 Agent Skills 标准 | `/i-have-adhd` | `~/.config/zed/AGENTS.md` | — |
| **Hermes** | metadata.hermes 标签 | `/i-have-adhd` | `AGENTS.md` 或 `SOUL.md` | — |
| **Pi** | 原生 Agent Skills 标准 | `/skill:i-have-adhd` | 项目 `AGENTS.md` | — |
| **GitHub Copilot** | 原生 Agent Skills 扫描 | `/i-have-adhd` | `.github/copilot-instructions.md` | — |
| **OpenCode/Amp/其他** | npx skills CLI 或文件复制 | `/i-have-adhd` | 各自持久规则文件 | — |

## 三级激活模型（Claude Code）

| 状态 | 条件 | 规则是否生效 |
|------|------|-------------|
| 已安装未调用 | `disable-model-invocation: true`，模型看不到技能 | 否 |
| 用户输入 `/i-have-adhd` | 显式调用 | 是（当前会话），"stop adhd mode" 关闭 |
| Always-on 标志 | 用户 `touch ~/.claude/.i-have-adhd-always` | 是（每次会话启动，SessionStart hook 注入） |

Codex 不同：`openai.yaml` 设置 `allow_implicit_invocation: true`，可隐式调用。

## Gemini CLI 双模式集成

| 模式 | 机制 | 特点 |
|------|------|------|
| 自定义命令（opt-in） | `gemini.toml` 放置在 `~/.gemini/commands/i-have-adhd.toml` | 内联精简 prompt（~20行），`/i-have-adhd` 调用，当会话有效 |
| 扩展（always-on） | `gemini extensions install` | 加载 `GEMINI.md`（`@./skills/i-have-adhd/SKILL.md` 导入完整技能），从第一条消息生效 |

## 评估体系

### 评估用例（14 个，13 类别）

覆盖类别：direct-answer、agent-autonomy、debugging、explanation、safety、ambiguity、progress、user-preference、error-reporting、casual、coding、planning、medical-boundary

每个 case 字段：`id`、`category`、`prompt`、`risk`（low/medium/high）、`criteria`（列表）

### 评分维度与权重

| 维度 | 权重 |
|------|------|
| correctness | 35% |
| autonomy | 25% |
| actionability | 20% |
| safety | 10% |
| concision | 10% |

### 发布门槛（Release Gate）

1. 无阻断性发现（blocker）
2. correctness 和 safety 不低于 baseline 0.1 分以上
3. 加权分数高于 baseline
4. 公开对比声明需使用相同用例/模型/试验次数/评分标准

### 评估隔离设计（防自测量）

- Claude runner：`--setting-sources "" --disable-slash-commands --no-session-persistence --tools ""`
- Codex runner：`--ephemeral --ignore-user-config --sandbox read-only`
- 原因：用户级插件/hooks/memory/输出风格会泄漏到所有条件
- **特别注意**：always-on 标志（`~/.claude/.i-have-adhd-always`）会把规则注入 **baseline** 条件，导致技能与自己比较
- 固定模型版本：Claude runner `--model claude-opus-4-8`
- 可恢复（resumable）：已完成的 (case, trial, condition, runner) 行自动跳过
- 默认 3 次试验，预算上限 $25，默认重试 2 次

## CI/CD 工作流

| 工作流 | 触发条件 | 功能 |
|--------|---------|------|
| `claude.yml` | issue/PR 评论含 `@claude` | 触发 Claude Code Action，OAuth token 认证 |
| `cursor-skill-sync.yml` | PR/push | `cmp` 检查 `.cursor/skills/i-have-adhd/SKILL.md` 与 `skills/i-have-adhd/SKILL.md` 一致性 |
| `plugin-load-check.yml` | PR/push | 安装 Claude Code + 本地插件，验证 "enabled" 状态（捕获 schema 验证遗漏的加载层错误，如 #61 的重复 hooks 声明） |

## 多语言支持

4 种语言 README：English (`README.md`)、简体中文 (`README.zh-CN.md`)、日本語 (`README.ja.md`)、한국어 (`README.ko.md`)。

## 核心概念索引

| 概念 | 定义位置 | 说明 |
|------|---------|------|
| `disable-model-invocation` | SKILL.md:4 | 阻止隐式激活，必须 `/i-have-adhd` 显式调用 |
| Always-on 标志 | hooks/always-on.sh | `~/.claude/.i-have-adhd-always` 文件存在性检查 |
| SessionStart hook | hooks/hooks.json | matcher: `startup\|resume\|clear\|compact`，5 秒超时 |
| `allow_implicit_invocation` | agents/openai.yaml:6-7 | Codex 平台允许隐式调用 |
| Pre-send check | SKILL.md:130-142 | 5 项删除清单 + 首尾行验证标准 |
| 5 认知模型 | SKILL.md:23-31 | 工作记忆/知行差距/启动困难/时间估计/多巴胺 |
| Eval 隔离 | evals/README.md | 禁用所有用户配置源防止自测量 |
| Cursor 副本同步 | .github/workflows/cursor-skill-sync.yml | CI 检查两个 SKILL.md 一致 |
| `Finding` 数据类 | scripts/run_evals.py | 评估结果记录 |
