---
type: Example
title: 安装 ADHD 友好输出技能
description: 在 Claude Code、Cursor、Codex CLI 等 AI 编码助手中安装并配置 i-have-adhd 技能，包括各平台安装步骤、Session Hook 自动激活、10 条输出规则验证、临时关闭方法，以及验证安装是否生效的测试流程。
tags: [i-have-adhd, example, installation, session-hooks, adhd, claude-code, cursor, codex]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: i-have-adhd 源码事实清单
---

## 场景说明

你是 ADHD 开发者（或希望获得更结构化、低认知负荷输出风格的开发者），需要在日常使用的 AI 编码助手中启用 ADHD 友好的输出格式。本示例演示：
1. 理解 i-have-adhd 技能的工作原理
2. 在 Claude Code 中安装（四种方式）
3. 在 Cursor 中配置
4. 在 Codex CLI 中配置
5. 在 Windsurf / Cline / Roo Code 中配置
6. 使用 Session Hook 实现自动激活
7. 验证 10 条规则是否生效
8. 临时关闭/永久关闭
9. 自定义输出风格

## 什么是 i-have-adhd

i-have-adhd 是一个**输出风格技能**（Output Style Skill），它不提供新功能或工具，而是覆盖 AI 的默认输出格式，使其更适合 ADHD/神经发散型用户的认知模式。核心是 10 条输出规则：

1. 不使用大段连续文字（No walls of text）
2. 使用 2-3 句的短段落（2-3 sentences max per chunk）
3. 长输出必须用水平分隔符分段（Mandatory dividers）
4. 不嵌套项目符号（No nested bullets）
5. 使用**粗体标记关键内容**（Bold keywords）
6. 代码块必须有标题注释（Label code blocks）
7. 完成时给出明确的下一步动作（Clear "next action"）
8. 冗长输出使用短标题（Short headers）
9. 不重复用户已经知道的内容（No filler）
10. 复杂任务输出检查表（Checklists for multi-step）

## 安装前准备

### 兼容性

- **Claude Code**：✅ 原生支持 skills + session hooks（最佳体验）
- **Cursor / Windsurf / Cline / Roo Code**：✅ 通过 Rules/Instructions 文件支持
- **Codex CLI**：✅ 通过 AGENTS.md / instructions 支持
- **OpenCode**：✅ 通过 `AGENTS.md` + session hooks 支持
- **Gemini CLI**：✅ 通过 GEMINI.md + hooks 支持
- **其他 AI 助手**：通过系统提示词注入（参见下文"通用安装"）

### 前置依赖

- Node.js（用于运行一键安装脚本，Claude Code 场景）
- AI 编码助手已安装并可用

## 步骤 1：获取 Skill 文件

Skill 的核心文件是 `SKILL.md`（约 5.5KB，MIT 协议）。获取方式：

### 方式 A：GitHub 直接下载

```bash
# 下载核心 SKILL.md
curl -fsSL https://raw.githubusercontent.com/ContainerUpgrade/i-have-adhd/main/SKILL.md -o /tmp/i-have-adhd/SKILL.md
```

### 方式 B：Git Clone

```bash
git clone https://github.com/ContainerUpgrade/i-have-adhd.git ~/i-have-adhd
```

## 步骤 2：在 Claude Code 中安装

Claude Code 有**四种安装方式**，推荐程度从高到低：

### 方式 1：会话内安装（最简单）

在 Claude Code 会话中直接说：

```
/install skill i-have-adhd
```

这是最简单的方式，Claude Code 会自动完成安装。

### 方式 2：/plugin marketplace 安装

```bash
# 在 Claude Code CLI 中
/plugin marketplace add i-have-adhd
```

通过插件市场安装，支持自动更新。

### 方式 3：手动放置到 skills 目录

```bash
# macOS/Linux
mkdir -p ~/.claude/skills/i-have-adhd
cp ~/i-have-adhd/SKILL.md ~/.claude/skills/i-have-adhd/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\i-have-adhd"
Copy-Item "$env:USERPROFILE\i-have-adhd\SKILL.md" "$env:USERPROFILE\.claude\skills\i-have-adhd\"
```

### 方式 4：一键安装脚本（Node.js）

```bash
# 需要 Node.js
# 下载并运行安装脚本
npx https://github.com/ContainerUpgrade/i-have-adhd.git install
```

安装脚本自动完成：
1. 检测 Claude Code 安装目录
2. 创建 `~/.claude/skills/i-have-adhd/` 目录
3. 复制 SKILL.md
4. 可选：配置 session hook 自动激活
5. 可选：添加 @ symbol 快捷键

### 方式 5：Session Hook 自动激活（Always-on 模式）

手动安装后，添加 Session Hook 使技能在每次会话自动激活：

**方法 A：settings.json 配置**

编辑 Claude Code 的 settings 文件：

```bash
# macOS
code ~/Library/Application\ Support/Claude/settings.json

# Linux
code ~/.config/Claude/settings.json

# Windows
code "$env:APPDATA\Claude\settings.json"
```

添加以下配置：

```json
{
  "sessionhooks": {
    "UserPromptSubmit": [
      {
        "type": "prompt",
        "prompt_file": "~/.claude/skills/i-have-adhd/SKILL.md"
      }
    ]
  }
}
```

这会在每次你发送消息时自动注入 ADHD 输出规则。

**方法 B：CLAUDE.md 全局配置**

编辑（或创建）`~/.claude/CLAUDE.md`：

```markdown
# Global Claude Code Configuration

## Always-Active Skills

Always apply the i-have-adhd output style for every response.
Load the skill from: ~/.claude/skills/i-have-adhd/SKILL.md

Key rules to always follow:
- No walls of text
- Short paragraphs (2-3 sentences max)
- Bold key terms
- Clear next action at end
- Checklists for multi-step tasks
```

## 步骤 3：在 Cursor 中安装

Cursor 使用 `.cursorrules` 文件配置全局规则：

### 全局安装（所有项目）

```bash
# 创建/编辑全局 .cursorrules
cat >> ~/.cursorrules << 'EOF'

# ADHD-Friendly Output Style (i-have-adhd)

Apply these output rules for ALL responses:

1. **No walls of text** — Break long content into short chunks
2. **Short paragraphs** — 2-3 sentences maximum per paragraph
3. **Use dividers** for long outputs (--- between sections)
4. **No nested bullets** — Use flat bullet lists only
5. **Bold keywords** — Mark important terms with **bold**
6. **Label code blocks** — Add a title comment at the top
7. **Clear next action** — End with an explicit "Next:" action
8. **Short headers** — Use ## headers for verbose output
9. **No filler** — Skip "Great question!" and redundant explanations
10. **Checklists** for multi-step tasks — Use - [ ] format
EOF
```

### 项目级安装（仅当前项目）

在项目根目录创建 `.cursorrules` 文件，内容同上。这只影响该项目内的 Cursor 会话。

### Cursor + Composer

如果使用 Cursor Composer（Agent 模式），在 Composer 的 Custom Instructions 中添加上述规则。

## 步骤 4：在 Codex CLI 中安装

Codex CLI 通过 `AGENTS.md` 或 `~/.codex/instructions.md` 配置：

```bash
# 创建全局指令文件
mkdir -p ~/.codex
cat >> ~/.codex/instructions.md << 'EOF'

# ADHD-Friendly Output Style

Always format your responses following these rules:

- Break long text into short paragraphs (2-3 sentences max)
- Use **bold** for key terms and important information
- Use --- horizontal dividers between major sections
- Use flat bullet lists, no nesting
- Label every code block with a comment describing what it does
- End every response with a clear "Next:" action step
- Use ## headers for long outputs
- Skip filler phrases like "Great question!" or "I'd be happy to help"
- Present multi-step tasks as - [ ] checklists
- Do not repeat information the user already stated
EOF
```

或者在当前项目目录创建 `AGENTS.md`，内容同上。

## 步骤 5：在其他平台安装

### Windsurf

编辑 `~/.windsurf/rules.md`（全局）或项目根目录的 `.windsurfrules`，添加与步骤 3 相同的 10 条规则。

### Cline / Roo Code

在 VS Code 扩展设置中找到 "Custom Instructions" 字段，粘贴 10 条规则。

### Gemini CLI

```bash
# 编辑全局 GEMINI.md
cat >> ~/.gemini/GEMINI.md << 'EOF'
# ADHD-Friendly Output
[10条规则同上]
EOF
```

### OpenCode

编辑 `~/.config/opencode/AGENTS.md` 或项目 `AGENTS.md`。

### 通用方式（任何 AI 助手）

如果 AI 助手支持自定义系统提示词（Custom Instructions / System Prompt），将以下内容粘贴到设置中：

```
Apply these output rules for ALL responses in this conversation:
1. No walls of text — use short chunks (2-3 sentences max per paragraph)
2. Use --- dividers between major sections for long outputs
3. No nested bullet points — use flat lists only
4. Bold key terms with **asterisks**
5. Add a title comment at the top of every code block
6. End with a clear "Next:" action step
7. Use ## headers for verbose output sections
8. Skip filler/redundant text — don't repeat what I already know
9. Use - [ ] checklists for multi-step tasks
10. Be direct and concise
```

## 步骤 6：验证安装生效

安装后，发送一个容易触发长输出的请求来测试：

```
帮我写一个 Python 的 REST API 服务，包含用户注册、登录、数据CRUD功能，
使用 FastAPI + SQLAlchemy + PostgreSQL，需要完整的错误处理。
```

**未启用 ADHD 风格的典型输出**（反例）：

> 当然可以！下面我将为你创建一个完整的 REST API 服务。首先我们需要了解几个关键概念...（以下是500字的连续段落，没有分段，嵌套项目符号，没有粗体标记）

**启用 ADHD 风格的正确输出**：

> ## FastAPI REST API 搭建
>
> 我将创建包含用户认证和 CRUD 的完整服务。
>
> ────────────────────
>
> **项目结构**
>
> ```python
> # main.py - FastAPI application entry point
> from fastapi import FastAPI
> from database import engine
> import models
>
> models.Base.metadata.create_all(bind=engine)
> app = FastAPI(title="User API")
> ```
>
> **核心依赖**
>
> - fastapi + uvicorn
> - sqlalchemy + asyncpg
> - python-jose (JWT)
> - passlib (password hashing)
>
> ────────────────────
>
> **Step 1: 数据库模型**
>
> ```python
> # models.py - SQLAlchemy ORM models
> from sqlalchemy import Column, Integer, String, DateTime
> from sqlalchemy.ext.declarative import declarative_base
> from datetime import datetime
>
> Base = declarative_base()
>
> class User(Base):
>     __tablename__ = "users"
>     id = Column(Integer, primary_key=True)
>     email = Column(String, unique=True, index=True)
>     hashed_password = Column(String)
>     created_at = Column(DateTime, default=datetime.utcnow)
> ```
>
> ────────────────────
>
> **检查清单**
>
> - [ ] 安装依赖: `pip install fastapi uvicorn sqlalchemy asyncpg python-jose passlib`
> - [ ] 配置 PostgreSQL 连接字符串
> - [ ] 实现 JWT token 生成/验证
> - [ ] 添加用户注册端点 POST /users
> - [ ] 添加登录端点 POST /login
> - [ ] 添加 CRUD 端点（需要认证）
>
> **Next:** 创建 `requirements.txt` 并安装依赖后运行 `uvicorn main:app --reload`

逐条验证：

| 规则 | 验证点 |
|------|--------|
| 1. 无大段文字 | ✅ 每段 2-3 句 |
| 2. 短段落 | ✅ 段间有空行 |
| 3. 水平分隔符 | ✅ `---` 分节 |
| 4. 不嵌套列表 | ✅ 扁平列表 |
| 5. 粗体关键词 | ✅ **Step 1**, **核心依赖** |
| 6. 代码块标题注释 | ✅ `# main.py - ...` |
| 7. 明确下一步 | ✅ `**Next:** ...` |
| 8. 短标题 | ✅ `## FastAPI REST API 搭建` |
| 9. 无填充语 | ✅ 没有"好的！我来帮你..." |
| 10. 多步任务用检查表 | ✅ `- [ ]` 列表 |

## 步骤 7：临时关闭技能

有时你需要 AI 给出更详细/更学术的输出，临时关闭 ADHD 风格：

### Claude Code

```
暂时关闭 i-have-adhd 风格，给我一份详细的技术方案文档
```

或：

```
/off i-have-adhd
```

### Cursor / 其他平台

在消息开头加上：

```
Ignore the ADHD output rules for this response. I want a detailed,
academic-style answer with nested structure.
```

恢复 ADHD 风格：

```
恢复 ADHD 输出风格
```

## 步骤 8：永久卸载

### Claude Code

```bash
# 删除 skill 目录
rm -rf ~/.claude/skills/i-have-adhd

# 如果使用了 session hook，编辑 settings.json 移除 hook 配置
# 如果添加了 CLAUDE.md，编辑移除相关行
```

### Cursor

```bash
# 删除 .cursorrules 中 i-have-adhd 相关内容
# 或直接删除项目级 .cursorrules
```

### Codex CLI

```bash
# 编辑 ~/.codex/instructions.md 移除 ADHD 规则
```

## 高级配置

### 自定义分隔符

默认使用 `---`（Markdown 水平分隔线）。如果你的渲染环境不支持，可以修改 SKILL.md：

```markdown
<!-- 替换 -->
Use --- as dividers between major sections.

<!-- 改为 -->
Use ■ as dividers between major sections.
```

### 添加 Emoji 标记

如果你喜欢 emoji 视觉提示，可以在规则中添加：

```markdown
11. **Use emojis sparingly** for visual anchors: 📝 for notes, ⚠️ for warnings, ✅ for success
```

### 调整段落长度

默认 2-3 句。如果你觉得太短：

```markdown
<!-- 修改 SKILL.md 第 4 行附近 -->
- Keep paragraphs short: maximum 3 sentences before a line break
<!-- 改为 -->
- Keep paragraphs short: maximum 4 sentences before a line break
```

### 配合 Session Hooks 实现条件激活

如果只在特定项目需要 ADHD 风格，可以使用项目级 `.claude/settings.json`：

```json
{
  "sessionhooks": {
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "type": "prompt",
        "prompt_file": ".claude/skills/i-have-adhd/SKILL.md"
      }
    ]
  }
}
```

将 SKILL.md 放在项目 `.claude/skills/` 目录下，只在该项目自动激活。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 安装后输出没有变化 | Skill 没被正确加载 | 重启 AI 助手会话，检查文件路径是否正确 |
| Cursor 中不生效 | `.cursorrules` 位置不对 | 全局放 `~/.cursorrules`，项目级放项目根目录 |
| Claude Code hook 报错 | JSON 格式错误 | 验证 settings.json 是合法 JSON |
| 代码块没有标题注释 | AI 偶尔遗漏规则 | 在提示中强调 "remember to label code blocks" |
| 想在某些项目关闭 | 全局安装影响所有项目 | 改用项目级安装，或在消息中临时关闭 |
| 输出太短缺少信息 | ADHD 规则太激进 | 调整段落长度限制（见"高级配置"） |
| Session hook 导致 token 消耗过高 | SKILL.md 每次注入 | ADHD SKILL.md 仅 5.5KB，约 1.3K tokens，影响很小 |

## 相关概念

- 输出风格技能模式
- Session Hook 机制
- [跨平台技能集成](../concepts/multi-platform-integration.md)
- 渐进式加载与 Always-on 模式
