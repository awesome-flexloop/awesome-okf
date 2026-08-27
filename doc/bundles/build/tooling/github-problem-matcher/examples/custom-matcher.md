---
type: Example
title: 自定义 Problem Matcher
description: 为 pylint/eslint/ruff/mypy/pytest 等工具创建自定义 GitHub Problem Matcher 的完整教程与模板
tags: [github-problem-matcher, example, custom-matcher, regex, ci, lint]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-source
    resource: /references/github-problem-matcher-source.md
---

# 自定义 Problem Matcher

当你需要为 Sphinx 之外的工具（pylint、eslint、ruff、mypy、pytest、TypeScript 编译器等）在 PR 中显示内联警告时，可以创建自定义 Problem Matcher。本示例演示完整的创建流程。

## 创建步骤总览

1. 分析目标工具的日志输出格式
2. 编写 matcher JSON 文件（正则表达式 + 捕获组映射）
3. 创建 composite action 注册 matcher
4. 编写测试脚本验证正则
5. 在 workflow 中使用

## 示例一：Pylint Problem Matcher

### 第一步：分析 Pylint 输出格式

Pylint 默认输出格式：

```
************* Module mypackage.mymodule
mypackage/mymodule.py:15:0: C0301: Line too long (120/100) (line-too-long)
mypackage/mymodule.py:42:4: W0612: Unused variable 'x' (unused-variable)
mypackage/mymodule.py:1:0: C0114: Missing module docstring (missing-module-docstring)
```

格式分析：
- `<文件路径>:<行号>:<列号>: <消息ID>: <消息> (<消息符号>)`
- 文件路径是相对路径
- 严重级别编码在消息 ID 中：C=Convention, W=Warning, E=Error, F=Fatal, R=Refactor

### 第二步：创建 matcher JSON

创建 `.github/matchers/pylint-matcher.json`：

```json
{
    "problemMatcher": [
        {
            "owner": "pylint-problem-matcher",
            "pattern": [
                {
                    "regexp": "^([^:]+):(\\d+):(\\d+):\\s+([CRWEF]\\d+):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "code": 4,
                    "message": 5
                }
            ]
        }
    ]
}
```

正则解析：
- `^([^:]+)`：捕获组 1 (file)，匹配一个或多个非冒号字符（文件路径）
- `:(\\d+)`：捕获组 2 (line)，行号
- `:(\\d+)`：捕获组 3 (column)，列号
- `:\\s+([CRWEF]\\d+)`：捕获组 4 (code)，消息 ID（C/W/E/R/F + 数字）
- `:\\s+(.*)$`：捕获组 5 (message)，消息内容

### 第三步：在 Workflow 中直接注册

不需要创建完整的 Action，可以在 workflow 中直接注册本地 matcher 文件：

```yaml
- name: Register pylint problem matcher
  run: echo "::add-matcher::.github/matchers/pylint-matcher.json"
  shell: bash

- name: Run pylint
  run: pylint mypackage/
```

这比创建完整 Action 更简单，适合项目内部使用。

## 示例二：Ruff Problem Matcher

[Ruff](https://github.com/astral-sh/ruff) 是 Python 的快速 linter，输出格式：

```
mypackage/mymodule.py:15:80: E501 Line too long (120 > 79 characters)
mypackage/mymodule.py:42:5: F841 Local variable `x` is assigned to but never used
```

创建 `.github/matchers/ruff-matcher.json`：

```json
{
    "problemMatcher": [
        {
            "owner": "ruff-problem-matcher",
            "pattern": [
                {
                    "regexp": "^([^:]+):(\\d+):(\\d+):\\s+([A-Z]\\d+):?\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "code": 4,
                    "message": 5
                }
            ]
        }
    ]
}
```

注意 Ruff 的消息 ID 后面可能有可选的冒号（`E501:` 或 `E501 `），用 `:?` 匹配可选冒号。

## 示例三：TypeScript/ESLint Problem Matcher

ESLint 格式化输出（`--format stylish`）：

```
src/index.ts
  15:10  error    'x' is defined but never used  @typescript-eslint/no-unused-vars
  42:5   warning  Missing return type on function   @typescript-eslint/explicit-function-return-type

✖ 2 problems (1 error, 1 warning)
```

这种格式比较复杂——文件名单独占一行，错误信息在下一行。需要多行 pattern：

```json
{
    "problemMatcher": [
        {
            "owner": "eslint-problem-matcher",
            "pattern": [
                {
                    "regexp": "^([^\\s].*)$",
                    "file": 1
                },
                {
                    "regexp": "^\\s+(\\d+):(\\d+)\\s+(error|warning|info)\\s+(.*?)\\s{2,}(.*)$",
                    "line": 1,
                    "column": 2,
                    "severity": 3,
                    "message": 4,
                    "code": 5,
                    "loop": true
                }
            ]
        }
    ]
}
```

多行 pattern 工作方式：
1. 第一个 pattern 匹配文件名行（不以空白开头的行），设置 `file` 上下文
2. 第二个 pattern 匹配后续的错误行，继承上一个 pattern 的 `file` 值
3. `"loop": true` 表示第二个 pattern 可以重复匹配多行续行（一个文件有多个错误）

## 示例四：pytest Problem Matcher

pytest 失败输出：

```
FAILED tests/test_math.py::test_add - AssertionError: assert 1 + 1 == 3
FAILED tests/test_utils.py::test_format - ValueError: Invalid input
```

注意 pytest 默认输出不包含行号。需要使用 `--tb=short` 格式：

```
tests/test_math.py:10: in test_add
    assert 1 + 1 == 3
E   AssertionError: assert 1 + 1 == 3
```

创建 `.github/matchers/pytest-matcher.json`：

```json
{
    "problemMatcher": [
        {
            "owner": "pytest-problem-matcher",
            "pattern": [
                {
                    "regexp": "^([^:]+):(\\d+):\\s+in\\s+(.+)$",
                    "file": 1,
                    "line": 2,
                    "message": 3
                },
                {
                    "owner": "pytest-problem-matcher-error",
                    "pattern": [{
                        "regexp": "^E\\s+(.*)$",
                        "message": 1
                    }]
                }
            ]
        }
    ]
}
```

pytest 的错误格式较复杂，可能需要两个独立的 matcher 或多行 pattern 组合。实际使用中，可以使用社区已有的 [`pytest-problem-matcher`](https://github.com/xcambar/pytest-problem-matcher) Action。

## 创建独立 Action（可复用）

如果你希望将自定义 matcher 发布为可复用的 Action（类似 sphinx-doc/github-problem-matcher），创建以下文件结构：

```
your-problem-matcher/
├── action.yml
├── your_matcher.json
├── test_matcher.js
├── README.md
└── LICENSE
```

### action.yml 模板

```yaml
name: Your Tool Problem Matcher
description: Attaches a problem matcher for your-tool warnings/errors
author: Your Name
branding:
  icon: check-circle
  color: green
runs:
  using: composite
  steps:
  - name: Activate the problem matcher
    run: echo '::add-matcher::${{ github.action_path }}/your_matcher.json'
    shell: sh
```

### test_matcher.js 模板

复用 github-problem-matcher 的测试方法：

```javascript
var assert = require('assert');
var fs = require('fs');

const matcher = JSON.parse(fs.readFileSync('your_matcher.json', 'utf8'));
const patterns = matcher.problemMatcher.map(pm => pm.pattern[0]);

// 你的工具的模拟日志
const tool_log = `
path/to/file.py:15:0: E123 Some error message
path/to/file.py:42:0: W456 Some warning message
`;

const expected = [
    { file: 'path/to/file.py', line: '15', severity: 'E', message: 'Some error message' },
    { file: 'path/to/file.py', line: '42', severity: 'W', message: 'Some warning message' },
];

function perform_match(pattern_object, line) {
    const match = line.match(pattern_object.regexp);
    if (!match) return null;
    return {
        file: pattern_object.file ? match[pattern_object.file] : null,
        line: pattern_object.line ? match[pattern_object.line] : null,
        column: pattern_object.column ? match[pattern_object.column] : null,
        severity: pattern_object.severity ? match[pattern_object.severity] : null,
        code: pattern_object.code ? match[pattern_object.code] : null,
        message: pattern_object.message ? match[pattern_object.message] : null
    };
}

const matches = [];
for (const line of tool_log.split('\n')) {
    for (const p of patterns) {
        const m = perform_match(p, line);
        if (m) matches.push(m);
    }
}

// 过滤 null 结果（expected 中不应包含 null）
const validMatches = matches.filter(m => m !== null);
assert.deepEqual(expected, validMatches);
console.log('[x] All matcher tests passed!');
```

## 正则表达式编写技巧

### 1. 文件路径匹配

- **相对路径**：`([^:]+)` — 匹配到第一个冒号为止（适合类 Unix 路径）
- **绝对路径（Unix）**：`(/\\S+)` — 以 / 开头，后续非空白字符
- **Windows 路径**：`([A-Za-z]:[/\\\\][^:]+)` — 盘符开头
- **特定扩展名**：`(.*\\.py)` / `(.*\\.ts)` — 以特定扩展名结尾，减少误报

### 2. 行号和列号

- `(\\d+)`：匹配一个或多个数字
- 列号是可选的时：`(?::(\\d+))?` — 用可选组

### 3. 严重级别

- 直接捕获级别词：`(error|warning|info|note)` — 使用选择匹配
- 捕获级别代码：`([Ee]rror|[Ww]arning|[Ff]atal)` — 支持大小写变体
- 从代码推断级别（如 pylint 的 C/R/W/E/F）：捕获代码后在 message 中显示

### 4. 消息匹配

- `(.*)`：匹配剩余所有内容（到行尾）
- 消息中有特殊字符（冒号、括号等）时通常不需要特殊处理，因为是最后一个捕获组

### 5. 锚定

- `^` 行首锚定：减少误报，要求格式从行首开始
- `$` 行尾锚定：确保匹配到行末
- 无前缀文本的工具（如 pylint）使用 `^` 锚定
- 有前缀文本的工具（如 `checking consistency...`）不使用 `^`

## 测试正则的方法

1. **Node.js 命令行快速测试**：
   ```bash
   node -e "console.log('file.py:15:0: W123 test'.match(/^([^:]+):(\d+):(\d+):\s+(\w+):?\s+(.*)$/))"
   ```

2. **在线正则测试器**：使用 [regex101.com](https://regex101.com/)（选择 JavaScript 风味）

3. **自动化测试**：使用上述 test_matcher.js 模板，配合 `node test_matcher.js`

## 社区已有的 Problem Matchers

在创建自定义 matcher 之前，先检查是否已有社区实现：

| 工具 | Matcher Action |
|------|---------------|
| Sphinx | [sphinx-doc/github-problem-matcher](https://github.com/sphinx-doc/github-problem-matcher) |
| ESLint | 内置支持（`eslint` 格式自动识别） |
| TypeScript (tsc) | 内置支持 |
| Python (mypy) | [ms-python problem-matcher](https://github.com/microsoft/vscode-python/tree/main/source/tsc) |
| Pylint | [JosephLenton/problem-matcher-pylint](https://github.com/JosephLenton/problem-matcher-pylint) |
| Ruff | [conda/problem-matchers/ruff.json](https://github.com/conda/infrastructure/blob/main/.github/matchers/ruff.json) |
| pytest | [xcambar/pytest-problem-matcher](https://github.com/xcambar/pytest-problem-matcher) |

## 相关概念

- [Problem Matcher JSON 格式](../concepts/03-matcher-json.md)
- [三种正则模式详解](../concepts/04-regex-patterns.md)
- [测试 Problem Matcher](../concepts/05-testing.md)
- [Action 结构解析](../concepts/02-action-structure.md)
- [基础使用示例](basic-usage.md)
- [源码信源登记](../references/github-problem-matcher-source.md)
