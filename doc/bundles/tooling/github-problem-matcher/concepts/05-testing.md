---
type: Concept
title: 测试 Problem Matcher
description: test_matcher.js 逐行解析、Problem Matcher 的极简测试方法、如何为自定义 matcher 编写单元测试
tags: [github-problem-matcher, testing, nodejs, assert, unit-test]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-source
    resource: /references/github-problem-matcher-source.md
---

# 测试 Problem Matcher

## 测试理念

Problem Matcher 的核心是正则表达式，正则表达式的正确性直接决定了 matcher 能否准确捕获警告。不需要运行完整的 GitHub Actions workflow 来测试 matcher——因为正则匹配是纯计算逻辑，可以在本地用 Node.js 直接验证。

github-problem-matcher 的测试脚本 `test_matcher.js`（88行）展示了一种极简的测试方法：**零框架、零依赖、直接用正则匹配模拟日志**。

## test_matcher.js 完整解析

### 第一部分：导入依赖和加载 matcher

```javascript
var assert = require('assert');
var fs = require('fs');

const matcherJSON = fs.readFileSync('sphinx_matcher.json');
const matcher = JSON.parse(matcherJSON);
```

使用 Node.js 内置模块：
- `assert`：断言库（内置，无需 npm install）
- `fs`：文件系统模块（内置）

直接读取 JSON 文件并解析，不需要任何打包工具或测试运行器。

### 第二部分：提取 pattern

```javascript
let patterns = [];
for (const problemMatcher of matcher.problemMatcher) {
    patterns.push(problemMatcher.pattern[0]);
}

for (const pattern of patterns) {
    console.log("Patterns under test: ", pattern.regexp);
}
```

遍历 `problemMatcher` 数组，提取每个 matcher 的第一个 pattern（本项目每个 matcher 只有一个 pattern）。打印所有待测试的正则表达式，方便调试。

注意：这里提取的 pattern 对象包含 `regexp` 字符串和 `file`/`line`/`severity`/`message` 等映射字段。

### 第三部分：模拟日志数据

```javascript
const sphinx_log =
`/tmp/spam/warnings_and_errors/index.rst:16: WARNING: Error in "code-block" directive:
maximum 1 argument(s) allowed, 2 supplied.
.. code-block:: ruby
            as

/tmp/spam/warnings/index.rst:22: WARNING: Problems with "include" directive path:
InputError: [Errno 2] No such file or directory: 'I_DONT_EXIST'.


/tmp/spam/warnings/index.rst:24: WARNING: Unknown directive type "BADDIRECTIVE".
.. BADDIRECTIVE:: asdf

checking consistency... /tmp/spam/warnings/notintoc.rst: WARNING: document isn't included in any toctree`;
```

模拟了 4 种典型的 Sphinx 警告场景：

1. **多行错误详情**：code-block 指令参数错误，首行是警告摘要，后续行是详细说明和出错的代码片段
2. **多行异常信息**：include 指令路径错误，包含 Python InputError 堆栈信息
3. **单行警告**：未知指令类型，一行完整
4. **无行号警告**：consistency 检查输出，带有前缀文本

这些模拟数据故意包含空行和续行文本，测试 matcher 只匹配首行、忽略续行的行为。

### 第四部分：期望结果

```javascript
const expected_matches = [
    {
        'file': '/tmp/spam/warnings_and_errors/index.rst',
        'line': '16',
        'severity': 'WARNING',
        'message': 'Error in "code-block" directive:'
    },
    {
        'file': '/tmp/spam/warnings/index.rst',
        'line': '22',
        'severity': 'WARNING',
        'message': 'Problems with "include" directive path:'
    },
    {
        'file': '/tmp/spam/warnings/index.rst',
        'line': '24',
        'severity': 'WARNING',
        'message': 'Unknown directive type "BADDIRECTIVE".',
    },
    {
        'file': '/tmp/spam/warnings/notintoc.rst',
        'line': null,
        'severity': 'WARNING',
        'message': "document isn't included in any toctree"
    }
]
```

定义 4 个期望的匹配结果。关键观察：

- 前 3 个匹配来自严格模式，包含 line 字段
- 第 4 个匹配来自宽松模式，line 为 `null`（因为宽松模式不捕获行号）
- 多行消息的续行（"maximum 1 argument(s) allowed..."）**不在**期望结果中——只匹配首行摘要
- 空行和代码片段行（".. code-block:: ruby"）不产生匹配

### 第五部分：匹配函数

```javascript
function perform_match(pattern_object, line) {
    const match = line.match(pattern_object.regexp);

    if (!match) {
        return null;
    }

    return {
        file: pattern_object.file ? match[pattern_object.file] : null,
        line: pattern_object.line ? match[pattern_object.line] : null,
        severity: pattern_object.severity ? match[pattern_object.severity] : null,
        message: pattern_object.message ? match[pattern_object.message] : null
    };
}
```

这是核心的匹配逻辑，模拟 GitHub Actions runner 的行为：

1. 使用 JavaScript 的 `String.match()` 方法执行正则匹配
2. 如果不匹配，返回 `null`
3. 如果匹配，按照 pattern 对象中的映射字段（file/line/severity/message）从捕获组中提取值
4. 对于未定义的映射字段，返回 `null`

注意：`pattern_object.file` 的值是捕获组编号（如 1、2、3），`match[pattern_object.file]` 访问对应的捕获组。

### 第六部分：执行匹配和验证

```javascript
let matches = [];
for (const line of sphinx_log.split(/\n/)) {
    for (const pattern_object of patterns) {
        const match = perform_match(pattern_object, line);
        if (match) {
            matches.push(match);
        }
    }
}

console.log("Matches: ", matches);
console.log("Expected matches: ", expected_matches);
assert.deepEqual(expected_matches, matches);

console.log("[x] All good!");
```

1. 将模拟日志按换行符分割为行数组
2. 对每一行，尝试所有 pattern
3. 收集所有匹配结果
4. 使用 `assert.deepEqual()` 进行深度相等比较
5. 打印匹配结果和期望结果
6. 如果完全一致，输出 `[x] All good!`

`assert.deepEqual` 会递归比较两个对象或数组的所有属性，任何不匹配都会抛出异常并显示差异。

## 运行测试

在项目根目录下执行：

```bash
node test_matcher.js
```

成功输出：
```
Patterns under test:  ^(.*):(\d+):\s+(\w*):\s+(.*)$
Patterns under test:  (/.*\.rst):\s+(\w*):\s+(.*)$
Patterns under test:  ^(.*\.rst):(\d+):(.*)$
Matches:  [ {...}, {...}, {...}, {...} ]
Expected matches:  [ {...}, {...}, {...}, {...} ]
[x] All good!
```

如果正则不匹配或捕获组错误，`assert.deepEqual` 会抛出 AssertionError 并显示具体差异。

## 为自定义 Matcher 编写测试

基于 test_matcher.js 的模式，你可以为自己的 Problem Matcher 编写测试。基本模板：

```javascript
var assert = require('assert');
var fs = require('fs');

// 1. 加载你的 matcher JSON
const matcher = JSON.parse(fs.readFileSync('your_matcher.json', 'utf8'));
const patterns = matcher.problemMatcher.map(pm => pm.pattern[0]);

// 2. 定义模拟日志（包含正例和反例）
const test_log = `
/path/to/file.py:42: ERROR: Something went wrong
/path/to/file.py: WARNING: Missing docstring
normal line that should not match
`;

// 3. 定义期望匹配结果
const expected = [
    { file: '/path/to/file.py', line: '42', severity: 'ERROR', message: 'Something went wrong' },
    { file: '/path/to/file.py', line: null, severity: 'WARNING', message: 'Missing docstring' },
];

// 4. 执行匹配（复用 perform_match 函数）
function perform_match(pattern_object, line) {
    const match = line.match(pattern_object.regexp);
    if (!match) return null;
    return {
        file: pattern_object.file ? match[pattern_object.file] : null,
        line: pattern_object.line ? match[pattern_object.line] : null,
        severity: pattern_object.severity ? match[pattern_object.severity] : null,
        message: pattern_object.message ? match[pattern_object.message] : null
    };
}

const matches = [];
for (const line of test_log.split('\n')) {
    for (const p of patterns) {
        const m = perform_match(p, line);
        if (m) matches.push(m);
    }
}

// 5. 验证
assert.deepEqual(expected, matches);
console.log('[x] All tests passed!');
```

## 测试要点

编写 Problem Matcher 测试时应覆盖：

| 测试场景 | 说明 |
|---------|------|
| **标准格式匹配** | 最常见的日志格式，确保 file/line/severity/message 正确提取 |
| **边界格式匹配** | 无行号、无级别、带前缀文本等特殊格式 |
| **多行消息** | 验证只匹配首行，续行不产生重复匹配 |
| **反例（不应匹配）** | 正常日志行、代码片段行、空行不应被匹配 |
| **路径格式** | 绝对路径、相对路径、含特殊字符的路径 |
| **特殊消息内容** | 消息中包含冒号、引号、括号等特殊字符 |

## CI 集成建议

在你的 GitHub Actions workflow 中添加 matcher 测试步骤：

```yaml
- name: Test problem matcher
  run: node test_matcher.js
```

这确保对 matcher JSON 的任何修改都不会破坏现有的匹配行为。

## 相关概念

- [三种正则模式详解](/concepts/04-regex-patterns.md)
- [Problem Matcher JSON 格式](/concepts/03-matcher-json.md)
- [自定义 Problem Matcher 示例](/examples/custom-matcher.md)
- [源码信源登记](/references/github-problem-matcher-source.md)
