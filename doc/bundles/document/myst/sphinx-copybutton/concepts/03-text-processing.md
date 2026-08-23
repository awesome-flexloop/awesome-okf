---
type: Concept
title: 文本处理与提示符剥离
description: sphinx-copybutton 的核心智能——如何剥离 shell/REPL 提示符、处理行续接和 HERE 文档、排除行号等不需要的内容
tags: [sphinx, sphinx-extension, copybutton, text-processing, prompt, regex, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-source
    resource: /references/copybutton-source.md
    title: sphinx-copybutton 源码路径映射
---

# 文本处理与提示符剥离

sphinx-copybutton 的真正价值不仅在于"放一个按钮在代码块旁"，更在于点击按钮时对文本的**智能清洗**。当代码块包含 shell 提示符（`$`）、Python REPL 提示符（`>>>`、`...`）、行号等内容时，直接复制会导致粘贴后无法直接运行。sphinx-copybutton 通过 `formatCopyText()` 函数实现了多层文本处理逻辑。

## 为什么需要文本处理？

考虑以下 Bash 代码块：

```bash
$ pip install sphinx
$ cd my-project
$ sphinx-build -b html . _build
```

如果直接复制 `innerText`，粘贴到终端会得到带 `$` 提示符的文本，终端会报错。sphinx-copybutton 能识别并剥离这些提示符，让用户复制到的是干净可执行的命令：

```
pip install sphinx
cd my-project
sphinx-build -b html . _build
```

## 核心文本处理函数

文本处理的核心是 `copybutton_funcs.js` 中的两个函数：

### filterText() —— DOM 节点过滤

```javascript
export function filterText(target, exclude) {
    const clone = target.cloneNode(true);
    if (exclude) {
        clone.querySelectorAll(exclude).forEach(node => node.remove());
    }
    return clone.innerText;
}
```

这个函数在提取文本前，先克隆 DOM 节点，然后移除匹配 `exclude` CSS 选择器的子元素（默认是 `.linenos` 行号元素），最后返回 `innerText`。这样可以排除代码块中的行号列，避免复制到无关内容。

### formatCopyText() —— 逐行文本清洗

这是核心函数，签名如下：

```javascript
function formatCopyText(
    textContent,           // 原始文本
    copybuttonPromptText,  // 提示符文本
    isRegexp,              // 提示符是否为正则
    onlyCopyPromptLines,   // 是否只复制含提示符的行
    removePrompts,         // 是否移除提示符前缀
    copyEmptyLines,        // 是否保留空行
    lineContinuationChar,  // 行续接字符
    hereDocDelim           // HERE 文档分隔符
)
```

## 提示符匹配机制

### 字面量匹配（默认）

默认情况下，`copybutton_prompt_text` 作为字面量字符串匹配行首。函数先调用 `escapeRegExp()` 转义正则特殊字符，然后构建正则表达式：

```javascript
regexp = new RegExp('^(' + escapeRegExp(copybuttonPromptText) + ')(.*)')
```

这匹配"以指定文本开头"的行，捕获两个分组：提示符本身（group 1）和提示符后的内容（group 2）。

### 正则表达式匹配

当 `copybutton_prompt_is_regexp = True` 时，`copybutton_prompt_text` 直接作为正则表达式使用，可以匹配多种提示符：

```python
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
```

这个正则可以同时匹配 Python REPL 的 `>>>` 和 `...`、Bash 的 `$`、IPython 的 `In [1]:` 等多种提示符。

## 逐行处理逻辑

`formatCopyText()` 将文本按换行符分割后逐行处理，维护三个状态标志：

- `promptFound`：当前行是否匹配提示符
- `gotLineCont`：上一行是否以续接符结尾
- `gotHereDoc`：是否处于 HERE 文档内

处理规则：

| 条件 | 行为 |
|------|------|
| 行匹配提示符 OR 处于续接状态 OR 处于 HERE 文档内 | 处理该行：根据 `removePrompts` 决定是否去掉提示符前缀 |
| 行不匹配提示符 AND `onlyCopyPromptLines=True` | 跳过该行（不复制） |
| 行不匹配提示符 AND `onlyCopyPromptLines=False` | 保留该行（复制输出内容） |
| 行为空行 AND `copyEmptyLines=True` | 保留空行 |

### 行续接处理

Shell 和 Python 都支持用反斜杠 `\` 续接长行：

```bash
$ echo "这是一行很长的命令 \
> 被分成了多行"
```

配置 `copybutton_line_continuation_character = "\\"` 后，续接行也会被正确识别为命令的一部分，提示符被剥离后拼接为完整命令。

### HERE 文档处理

Shell HERE 文档（here-document）是一种特殊的多行输入：

```bash
$ cat << EOF
这行没有提示符
这行也没有
EOF
```

配置 `copybutton_here_doc_delimiter = "EOF"` 后，分隔符之间的行也会被识别为命令内容。

## 特殊处理：无提示符时的回退

如果整段文本中没有任何行匹配提示符（`lineGotPrompt` 数组中没有 `true`），函数直接返回原始文本，不做任何处理。这确保了对不含提示符的普通代码块没有副作用。

## 末尾换行处理

返回前会移除末尾的换行符：

```javascript
if (textContent.endsWith("\n")) {
    textContent = textContent.slice(0, -1)
}
```

这是为了避免在终端中粘贴时自动执行命令（换行符会触发回车）。

## 配置项完整参考

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `copybutton_prompt_text` | str | `""` | 要匹配的提示符文本（字面量或正则） |
| `copybutton_prompt_is_regexp` | bool | `False` | prompt_text 是否按正则表达式解析 |
| `copybutton_only_copy_prompt_lines` | bool | `True` | True 时只复制含提示符的行（跳过输出）；False 时复制所有行 |
| `copybutton_remove_prompts` | bool | `True` | True 时从行首移除匹配的提示符；False 时保留提示符 |
| `copybutton_copy_empty_lines` | bool | `True` | 在 `onlyCopyPrompt_lines=True` 模式下是否保留空行 |
| `copybutton_line_continuation_character` | str | `""` | 行续接字符（如 Shell 中的 `\`） |
| `copybutton_here_doc_delimiter` | str | `""` | HERE 文档分隔符 |
| `copybutton_exclude` | str | `".linenos"` | 复制前要排除的 DOM 元素 CSS 选择器 |

## 典型场景配置

### 场景1：纯 Bash 文档（只有命令，无输出）

```python
copybutton_prompt_text = "$ "
```

### 场景2：Bash 文档（含命令输出）

```python
copybutton_prompt_text = "$ "
copybutton_only_copy_prompt_lines = True  # 只复制命令行，跳输出
```

### 场景3：Python REPL 文档

```python
copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True
```

### 场景4：混合多种 REPL（如 IPython 教程）

```python
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
```

## 相关概念

- [扩展架构与注册机制](/concepts/02-extension-architecture.md)
- [自定义样式与图标](/concepts/04-customization.md)
- [Shell 提示符配置示例](/examples/shell-prompts.md)
