---
type: Concept
title: Skills 与 AGENTS.md 约定
description: >
  Codex CLI 通过文件系统约定注入 agent 上下文：AGENTS.md 沿目录树自动发现
  并拼接项目指令，SKILL.md 定义可复用技能（支持显式 @mention 和隐式触发）。
  本文详解发现算法、加载机制、大小限制与信任边界。
tags: [openai-codex, skills, agents-md, context, convention, instructions]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Skills 与 AGENTS.md 约定

Codex CLI 不使用集中式数据库管理 agent 指令，而是通过文件系统约定实现"文件即上下文"。两个核心机制是 **AGENTS.md**（项目指令）和 **Skills**（可复用技能），两者都从文件加载、有大小上限、受信任边界控制。

## AGENTS.md

### 文件名常量

```rust
pub const DEFAULT_AGENTS_MD_FILENAME: &str = "AGENTS.md";
pub const LOCAL_AGENTS_MD_FILENAME: &str = "AGENTS.override.md";
```

- `AGENTS.md`：标准项目指令文件
- `AGENTS.override.md`：本地覆盖文件（优先级更高）
- 可通过 `project_doc_fallback_filenames` 配置备选文件名

### 发现算法

AGENTS.md 的发现遵循精确的目录树遍历规则：

1. **确定项目根**：从当前工作目录向上遍历，寻找 `project_root_markers` 配置的标记文件/目录
   - 默认标记为 `.git`
   - 可配置其他标记
   - 空标记列表禁用父目录遍历
2. **收集文件**：从项目根到 CWD（含），收集路径上的每一个 `AGENTS.md`
3. **拼接顺序**：按从根到叶的顺序拼接（根目录的指令在前，子目录的在后）
4. **不越过根**：不会遍历到项目根之上

```
项目根/
├── .git/                    ← 项目根标记
├── AGENTS.md                ← 第 1 个加载（全局项目约定）
├── src/
│   ├── AGENTS.md            ← 第 2 个加载（src 目录特定指令）
│   └── components/
│       └── Button/
│           └── AGENTS.md    ← 第 3 个加载（CWD 在此处时）
```

当 CWD 为 `src/components/Button/` 时，三个 AGENTS.md 按顺序拼接。

### 拼接与分隔

用户指令和项目文档之间用显式分隔符拼接：

```rust
const AGENTS_MD_SEPARATOR: &str = "\n\n--- project-doc ---\n\n";
```

### 大小与并发限制

```rust
const MAX_CONCURRENT_ANCESTOR_PROBES: usize = 256;
// 总大小受 config.project_doc_max_bytes 限制
```

- 总字节数受 `project_doc_max_bytes` 配置限制，达到上限后停止加载更多文件
- 并发祖先探测上限 256，避免远程文件系统调用过载

### 信任边界

不可信项目完全跳过 AGENTS.md 加载：

```rust
if config.active_project.is_untrusted() {
    return Ok((!loaded.is_empty()).then_some(loaded));
}
```

这确保了在未被用户信任的项目中，恶意 AGENTS.md 不能注入指令。

### 多环境支持

AGENTS.md 通过 exec-server 的文件系统接口读取，支持：
- 本地文件系统
- 远程环境（通过 exec-server 传输）
- 沙箱内的受限文件系统视图

沙箱权限 profile 决定了哪些路径可读。

## Skills 系统

Skills 是打包的指令集，通过 `SKILL.md` 文件定义，可以在对话中被显式调用或根据命令隐式触发。

### Skills crate 架构

`codex-skills` crate 包含以下模块：

| 模块 | 职责 |
|------|------|
| `loading` | Skill 根目录加载、快照缓存、异步加载 |
| `parser` | SKILL.md frontmatter 解析 |
| `model` | `SkillMetadata`、`SkillPolicy`、`SkillInterface` 数据模型 |
| `mentions` | `@mention` 语法提取、路径规范化 |
| `selection` | 显式 skill 提及收集 |
| `invocation` | 隐式 skill 调用检测 |
| `interface` | Skill 接口资产（文件、策略）解析 |
| `name_counts` | Skill 名称计数 |

### 系统 Skills

系统 skills 编译时嵌入二进制：

```rust
const SYSTEM_SKILLS_DIR: Dir = include_dir::include_dir!("$CARGO_MANIFEST_DIR/src/assets/samples");
const SYSTEM_SKILLS_DIR_NAME: &str = ".system";
```

首次运行时安装到 `$CODEX_HOME/skills/.system/`，通过指纹标记避免重复写入：

```rust
pub fn install_system_skills(codex_home: &AbsolutePathBuf) -> Result<(), SystemSkillsError> {
    let marker_path = dest_system.join(SYSTEM_SKILLS_MARKER_FILENAME);
    let expected_fingerprint = embedded_system_skills_fingerprint();
    if marker_matches {
        return Ok(());  // 已安装，跳过
    }
    // 清除旧目录，写入新 skills，写入标记
}
```

### 项目本地 Skills

项目可在 `.codex/skills/<name>/SKILL.md` 放置本地 skills。仓库中包含示例：

```
.codex/skills/
└── test-tui/
    └── SKILL.md
```

### 显式调用（@mention）

用户在对话中使用 `@skill-name` 语法显式调用 skill：

1. `mentions` 模块从消息中提取 `@` 提及
2. `selection` 模块匹配到已加载的 `SkillMetadata`
3. `core/skills.rs` 将 skill 内容注入模型上下文
4. 发送分析事件 `codex.skill.injected`，标签 `invoke_type="explicit"`

```rust
for skill in mentioned_skills {
    turn_context.session_telemetry.counter(
        "codex.skill.injected",
        1,
        &[("status", status), ("skill", &skill_name), ("invoke_type", "explicit")],
    );
}
```

### 隐式调用

Skills 也可根据 shell 命令和工作目录自动触发：

```rust
pub(crate) async fn maybe_emit_implicit_skill_invocation(
    sess: &Session,
    turn_context: &TurnContext,
    command: &str,
    workdir: &PathUri,
    native_workdir: Option<&AbsolutePathBuf>,
    environment_id: &str,
) {
    let Some(invocation) = detect_implicit_skill_invocation(
        turn_context.extension_data.as_ref(),
        environment_id, command, workdir, native_workdir,
    ) else { return; };
    // 注入 skill 并记录分析事件
}
```

隐式调用基于命令模式匹配——用户不需要知道 skill 存在，系统在检测到相关命令时自动加载对应指令。

### Skill 元数据

```rust
pub struct SkillMetadata {
    pub name: String,
    pub path_to_skills_md: PathBuf,
    pub scope: SkillScope,
    pub plugin_id: Option<String>,
    pub remote_plugin_id: Option<String>,
    // ...
}
```

Skill 可以来自：
- 系统内置（`.system`）
- 项目本地（`.codex/skills/`）
- 插件（plugin）
- 远程插件

## AGENTS.md 与 Skills 的协同

两者共同构成 Codex 的上下文注入体系，但角色不同：

| 维度 | AGENTS.md | Skills |
|------|-----------|--------|
| 触发方式 | 自动（按 CWD 发现） | 显式 @mention 或隐式命令匹配 |
| 范围 | 项目/目录级全局指令 | 特定任务/命令的专项指令 |
| 加载时机 | 会话启动时 | 按需（显式）或命令执行时（隐式） |
| 版本控制 | 随项目代码版本控制 | 可随项目或全局安装 |
| 大小限制 | `project_doc_max_bytes` | 单个 skill 有界 |

## 相关概念

- [Rust 核心与 TUI](./02-rust-core-tui.md)
- [沙箱执行模型](./04-sandbox-execution.md)
- [工作区架构](./01-workspace-architecture.md)
- [Python SDK](./06-python-sdk.md)
- [简介](./00-introduction.md)
