---
type: Concept
title: CLI 命令参考
description: copier 命令行接口详解——主命令与子命令、所有选项、退出码、非交互模式、数据传递方式
tags: [copier, cli, command-line, options, reference, subcommands]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# CLI 命令参考

Copier 提供基于 plumbum.cli 构建的命令行接口。主命令 `copier` 会根据目标目录状态自动选择 `copy` 或 `update` 操作。[^copier-source]

## 命令总览

```
copier [GLOBAL_OPTIONS] [SUBCOMMAND] [ARGS...]
```

### 子命令

| 子命令 | 用途 |
|--------|------|
| `copier copy <src> <dst>` | 从模板引导新项目或覆盖已有项目 |
| `copier recopy [dst]` | 重新复制（保留答案，丢弃演化） |
| `copier update [dst]` | 更新已有项目到模板新版本（尊重演化） |
| `copier check-update [dst]` | 检查是否有可用的模板更新 |
| 无（直接 `copier`） | 智能选择：有 answers 文件 → update；否则 → copy |

无参数直接执行 `copier` 时：
- 当前目录有 `.copier-answers.yml` 且包含 `_src_path` → 等价于 `copier update .`
- 否则 → 显示帮助信息（需要提供子命令和参数）

## 全局选项（所有子命令共有）

这些选项定义在 `_Subcommand` 基类中，所有子命令都支持：

| 选项 | 短选项 | 类型 | 说明 |
|------|--------|------|------|
| `--answers-file PATH` | `-a` | str | 答案文件路径（相对 dst_path） |
| `--exclude PATTERN` | `-x` | str（可多次） | 排除文件/目录的 glob 模式 |
| `--vcs-ref REF` | `-r` | str | Git 引用（标签/commit/HEAD/:current:） |
| `--pretend` | `-n` | flag | 模拟运行，不做实际修改 |
| `--skip PATTERN` | `-s` | str（可多次） | 已存在时跳过的文件模式 |
| `--quiet` | `-q` | flag | 静默模式，抑制状态输出 |
| `--prereleases` | `-g` | flag | 比较标签时包含预发布版本 |
| `--UNSAFE` / `--trust` | | flag | 信任模板，允许不安全特性 |
| `--skip-tasks` | `-T` | flag | 跳过任务执行 |
| `--data K=V` | `-d` | str（可多次） | 通过命令行传递变量值 |
| `--data-file FILE` | | path | 从 YAML 文件加载变量值 |
| `--help` | `-h` | flag | 显示帮助信息 |

### --data 与 --data-file

`-d K=V` 传递变量值，可多次使用：
```bash
copier copy -d project_name=demo -d author_name=Bot template/ output/
```

`--data-file` 从 YAML 文件加载：
```yaml
# answers.yml
project_name: demo
author_name: Bot
```
```bash
copier copy --data-file answers.yml template/ output/
```

两者同时使用时，`--data` 的值优先级高于 `--data-file`（CLI 覆盖文件值）。

## copier copy

**用法**：`copier copy [OPTIONS] TEMPLATE_SRC DESTINATION_PATH`

从模板创建新项目。如果目标目录非空，会渲染到其中（可能覆盖文件）。

| 选项 | 短选项 | 类型 | 说明 |
|------|--------|------|------|
| `--no-cleanup` | `-C` | flag | 出错时不删除由 Copier 创建的目标目录 |
| `--defaults` | `-l` | flag | 使用默认答案，不交互询问 |
| `--force` | `-f` | flag | 等同于 `--defaults --overwrite` |
| `--overwrite` | `-w` | flag | 覆盖已有文件，不交互确认 |
| `--ask PATTERN` | | str（可多次） | 强制询问匹配 glob 的问题 |

示例：
```bash
# 交互式创建项目
copier copy gh:user/template my-project

# 非交互式，使用默认值覆盖已有内容
copier copy -f template/ existing-project/

# 指定版本
copier copy -r v2.0.0 gh:user/template my-project

# 传递变量
copier copy -d project_name=demo -d python_version="3.12" template/ output/
```

## copier recopy

**用法**：`copier recopy [OPTIONS] [DESTINATION_PATH]`（默认 `.`）

重新复制项目，保留答案文件中的变量值，但丢弃所有本地修改。适用于想"重置"项目到模板状态的场景。

| 选项 | 短选项 | 类型 | 说明 |
|------|--------|------|------|
| `--defaults` | `-l` | flag | 使用默认答案，不交互询问 |
| `--force` | `-f` | flag | 等同于 `--defaults --overwrite` |
| `--overwrite` | `-w` | flag | 覆盖已有文件，不确认 |
| `--skip-answered` | `-A` | flag | 跳过已回答的问题 |
| `--ask PATTERN` | | str（可多次） | 强制询问匹配 glob 的问题 |

示例：
```bash
# 在项目目录中重新复制
cd my-project && copier recopy -f
```

## copier update

**用法**：`copier update [OPTIONS] [DESTINATION_PATH]`（默认 `.`）

智能更新项目到模板新版本，保留本地修改。需要 `.copier-answers.yml` 中的 `_src_path` 和 `_commit`。

| 选项 | 短选项 | 类型 | 默认 | 说明 |
|------|--------|------|------|------|
| `--conflict MODE` | `-o` | inline/rej | inline | 冲突解决方式：inline 标记或 .rej 文件 |
| `--context-lines N` | `-c` | int | 3 | 冲突检测的上下文行数 |
| `--defaults` | `-l`/`-f` | flag | | 使用默认答案 |
| `--skip-answered` | `-A` | flag | false | 跳过已回答的问题 |
| `--ask PATTERN` | | str（可多次） | | 强制询问匹配 glob 的问题 |

注意：`update` 默认 `overwrite=True`（与 copy 不同）。

示例：
```bash
# 交互式更新
cd my-project && copier update

# 使用 .rej 文件处理冲突
copier update -o rej

# 非交互式更新，跳过已回答的问题
copier update -l -A
```

## copier check-update

**用法**：`copier check-update [OPTIONS] [DESTINATION_PATH]`（默认 `.`）

检查是否有模板更新可用，不做实际修改。

| 选项 | 短选项 | 类型 | 默认 | 说明 |
|------|--------|------|------|------|
| `--quiet` | `-q` | flag | false | 静默模式，有更新时退出码 2 |
| `--prereleases` | `-g` | flag | false | 检查预发布版本 |
| `--output-format FMT` | | plain/json | plain | 输出格式 |

退出码：
- `0`：项目已是最新，或检查完成（非 quiet 模式）
- `2`：有新版本可用（仅 quiet 模式）
- `1`：发生错误

示例：
```bash
# 人类可读输出
copier check-update
# 输出: New template version available. Current version is v1.0.0, latest version is v2.0.0.

# JSON 输出
copier check-update --output-format json
# 输出: {"update_available": true, "current_version": "v1.0.0", "latest_version": "v2.0.0"}

# CI 中使用（静默模式，有更新时失败）
copier check-update -q || echo "Update available!"
```

## VCS 引用（--vcs-ref）

`-r/--vcs-ref` 指定模板版本：

| 值 | 说明 |
|-----|------|
| 标签名 | 如 `v1.0.0`、`v2.1.3` |
| commit hash | 完整或短 hash |
| `HEAD` | 最新提交 |
| `:current:` | 已有项目使用的当前版本（VcsRef.CURRENT） |

不指定时，默认检出最新的 PEP440 版本标签；无标签时使用 HEAD。

## 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 成功 |
| `1` | 用户消息错误（UserMessageError） |
| `4` | 不安全模板错误（UnsafeTemplateError），需要 `--trust` |
| `2` | check-update 子命令：有更新可用（仅 quiet 模式） |

## 异常处理

CLI 通过 `_handle_exceptions()` 统一处理异常：
- `UserMessageError` → 红色输出错误消息，退出码 1
- `UnsafeTemplateError` → 红色输出不安全特性列表，退出码 4
- `KeyboardInterrupt` → 包装为 `UserMessageError("Execution stopped by user")`，退出码 1

启动警告：CopierApp 的 `DESCRIPTION_MORE` 包含黄色警告，提醒用户仅使用可信模板。

## 常用命令组合

### 首次创建项目（交互模式）
```bash
copier copy gh:org/template my-new-project
cd my-new-project
git init && git add . && git commit -m "Initial commit"
```

### CI/CD 中非交互式创建
```bash
copier copy --defaults --overwrite \
  --data-file ./config/answers.yml \
  -r v2.0.0 \
  gh:org/template ./output
```

### 更新已有项目
```bash
cd my-project
copier update --skip-answered
# 解决冲突后
git add . && git commit -m "Update template to latest"
```

### 检查更新（脚本集成）
```bash
if copier check-update -q 2>/dev/null; then
  echo "Project is up to date"
else
  echo "Update available, running copier update..."
  copier update -l -A --trust
fi
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [问题与答案系统](03-questions-and-answers.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [安全与信任机制](09-security-and-safety.md)
- [基础模板创建与使用示例](/examples/basic-template.md)
- [Python API 使用示例](/examples/python-api-usage.md)
- [Copier 源码信源登记](/references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
