---
type: Concept
title: Problem Matcher JSON 格式
description: sphinx_matcher.json 完整结构解析、problemMatcher/pattern/regexp 字段说明与捕获组映射机制
tags: [github-problem-matcher, json-schema, problem-matcher, regexp, pattern]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-source
    resource: /references/github-problem-matcher-source.md
---

# Problem Matcher JSON 格式

## JSON 顶层结构

`sphinx_matcher.json` 是 Problem Matcher 的配置文件，定义了如何用正则表达式匹配日志输出。顶层结构如下：

```json
{
    "problemMatcher": [
        { ... matcher 1 ... },
        { ... matcher 2 ... },
        { ... matcher 3 ... }
    ]
}
```

顶层只有一个字段 `problemMatcher`，它是一个**数组**，可以包含一个或多个 matcher 对象。GitHub Actions runner 会注册数组中的所有 matcher，对后续日志行**并行尝试**所有 matcher 的 pattern。

## matcher 对象结构

每个 matcher 对象描述一组相关的正则匹配规则：

```json
{
    "owner": "sphinx-problem-matcher",
    "pattern": [
        {
            "regexp": "^(.*):(\\d+):\\s+(\\w*):\\s+(.*)$",
            "file": 1,
            "line": 2,
            "severity": 3,
            "message": 4
        }
    ]
}
```

### owner 字段

`owner` 是 matcher 的唯一标识符，用于：
- 在 `::remove-matcher owner=<owner>::` 命令中指定要移除的 matcher
- 在 GitHub Actions 日志中标识哪个 matcher 匹配了某条日志
- 避免不同 Action 的 matcher 冲突

owner 命名惯例：`<工具名>-problem-matcher` 或更具体的名称。sphinx_matcher.json 中三个 matcher 的 owner 分别为：

| owner | 含义 |
|-------|------|
| `sphinx-problem-matcher` | 主 matcher（严格模式） |
| `sphinx-problem-matcher-loose` | 宽松 matcher（无行号） |
| `sphinx-problem-matcher-loose-no-severity` | 兜底 matcher（无严重级别） |

### pattern 数组

`pattern` 是一个数组，包含一个或多个 pattern 对象。数组中的 pattern 按顺序组成**多行匹配规则**：
- 单 pattern（如本项目）：每一行独立匹配
- 多 pattern：用于匹配跨越多行的错误信息，第一个 pattern 匹配起始行，后续 pattern 匹配续行

sphinx_matcher.json 的每个 matcher 都只有一个 pattern，这意味着每个 matcher 只匹配单行日志。

## pattern 对象字段

每个 pattern 对象定义一个正则表达式及其捕获组到注解字段的映射：

```json
{
    "regexp": "^(.*):(\\d+):\\s+(\\w*):\\s+(.*)$",
    "file": 1,
    "line": 2,
    "severity": 3,
    "message": 4,
    "_comment": "这是注释"
}
```

### regexp 字段

`regexp` 是 **JavaScript 风格的正则表达式字符串**（注意是字符串而非正则字面量）。这意味着：
- 反斜杠需要双写转义：`\d` 写成 `\\d`，`\s` 写成 `\\s`
- 不需要写 `/regex/flags` 格式的字面量分隔符
- 默认不使用多行模式（`^` 和 `$` 匹配每行的开头和结尾）

### 捕获组映射字段

以下字段的值是**正则表达式中捕获组的编号**（1-based，即第1对括号为组1），告诉 GitHub 如何从匹配结果中提取信息：

| 字段 | 类型 | 说明 | sphinx matcher 中的使用 |
|------|------|------|------------------------|
| `file` | number | 捕获文件路径的组号 | 三个 matcher 都有 |
| `line` | number | 捕获行号的组号 | 主 matcher 和兜底 matcher 有 |
| `column` | number | 捕获列号的组号 | 本项目未使用 |
| `severity` | number | 捕获严重级别的组号 | 主 matcher 和宽松 matcher 有 |
| `code` | number | 捕获错误代码的组号 | 本项目未使用 |
| `message` | number | 捕获错误消息的组号 | 三个 matcher 都有 |

所有映射字段都是**可选的**——如果某个字段不存在，对应的注解字段将为空。例如宽松 matcher 没有 `line` 字段，匹配结果中 line 为 null，注解不会关联到具体行号。

### _comment 字段

以**下划线开头**的字段会被 GitHub runner 忽略，可以用作注释：

```json
{
    "_comment": "A bit of a looser pattern, doesn't look for line numbers"
}
```

这是因为 JSON 标准不支持注释（`//` 或 `/* */`），Problem Matcher 约定以下划线开头的字段为注释字段。

## 完整支持的 pattern 字段

除了本项目使用的字段外，GitHub Problem Matcher 还支持以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `fromPath` | number | 捕获源文件路径（用于 diff 匹配） |
| `toPath` | number | 捕获目标文件路径（用于重命名场景） |
| `loop` | boolean | 是否循环匹配（多行 pattern 中使用） |

## 多行匹配（本项目未使用）

Problem Matcher 支持跨多行匹配错误信息，这是通过在 `pattern` 数组中提供多个 pattern 对象实现的：

```json
{
    "owner": "example-matcher",
    "pattern": [
        {
            "regexp": "^(.*):(\\d+):\\s+(\\w+):\\s+(.*)$",
            "file": 1,
            "line": 2,
            "severity": 3,
            "message": 4,
            "loop": true
        },
        {
            "regexp": "^\\s+(.*)$",
            "message": 1
        }
    ]
}
```

多行匹配规则：
1. 第一个 pattern 匹配起始行（必须包含 `file` 字段）
2. 后续 pattern 按顺序匹配续行
3. 续行的捕获内容追加到前一行的 message 中
4. `loop: true` 表示最后一个 pattern 可以重复匹配多行续行

sphinx_matcher.json 没有使用多行匹配。这是因为 Sphinx 的警告消息首行就包含了所有关键信息（文件、行号、级别、消息摘要），后续行是详细描述。GitHub UI 会在首行注解中折叠显示后续的相关日志行。

## 注册多个 Matcher 的效果

sphinx_matcher.json 注册了 3 个 matcher，GitHub runner 的行为是：

1. 对日志中的**每一行**，依次尝试所有已注册的 matcher（来自所有 Action）
2. 如果某个 matcher 的 pattern 匹配成功，生成一条注解
3. 多个 matcher 可以匹配同一行（不会互斥）
4. 匹配失败的 matcher 静默跳过，不产生任何输出

这意味着同一行日志可能被多个 matcher 匹配，产生多条注解。在 sphinx_matcher.json 中：
- 标准格式的日志行（如 `/path/file.rst:16: WARNING: ...`）会被主 matcher（sphinx-problem-matcher）匹配
- 无行号的一致性检查行（如 `checking consistency... /path/file.rst: WARNING: ...`）会被宽松 matcher 匹配
- 无严重级别的行（如 `file.rst:42:Undefined label`）会被兜底 matcher 匹配
- 某些行可能同时匹配多个 pattern（设计上允许）

## 相关概念

- [三种正则模式详解](04-regex-patterns.md)
- [测试 Problem Matcher](05-testing.md)
- [Action 结构解析](02-action-structure.md)
- [自定义 Problem Matcher 示例](../examples/custom-matcher.md)
- [源码信源登记](../references/github-problem-matcher-source.md)
