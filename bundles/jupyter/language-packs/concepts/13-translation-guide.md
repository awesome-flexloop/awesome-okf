---
type: Concept
title: "翻译规范与 PO 文件格式"
description: "PO 文件的语法规则、翻译最佳实践、特殊格式处理（占位符/Markdown/快捷键/复数）以及翻译质量注意事项"
tags: [jupyterlab, i18n, gettext, po, translation, localization-best-practices]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: gettext-format, resource: /references/gettext-format-source.md, title: "Gettext 翻译格式信源" }
---

# 翻译规范与 PO 文件格式

JupyterLab 语言包的翻译文件使用标准 gettext PO 格式。理解 PO 文件的语法规则和翻译规范是贡献高质量翻译的基础。虽然大部分翻译工作在 Crowdin Web 界面完成（不需要直接编辑 PO 文件），但理解底层格式有助于处理复杂翻译场景。

## PO 文件条目结构

每个翻译条目由以下部分组成：

```gettext
#  翻译者注释（Translator comment）— 可选
#. 提取器注释（Extracted comment）— 源码中的注释，给译者看的
#: 源文件引用（Reference）— 字符串在源码中的位置
#, 标志位（Flags）— 如 fuzzy、python-brace-format、no-python-format
msgctxt "上下文"（Context）— 可选，用于消歧
msgid "英文原文"
msgstr "翻译文本"
```

### 注释类型

| 前缀 | 含义 | 示例 |
|------|------|------|
| `# ` | 翻译者注释 | `# 这是按钮标签` |
| `#.` | 提取器自动注释 | `#. TRANSLATORS: 这是文件大小显示` |
| `#:` | 源文件引用 | `#: /packages/apputils-extension/src/index.ts:123` |
| `#,` | 格式标志 | `#, python-brace-format, fuzzy` |
| `#|` | 前值引用（旧msgid）| `#| msgid "Old string"` |

## 特殊格式处理

### 1. 占位符（Placeholders）

JupyterLab 中常见的占位符类型：

**Python 大括号格式（`{}`）**：
```gettext
#, python-brace-format
msgid "Saved {count} files in {directory}"
msgstr "在 {directory} 中保存了 {count} 个文件"
```
- 必须保留所有 `{variable}` 占位符，不能省略
- 占位符顺序可以调整（中文习惯可能需要调换）
- 不要翻译占位符内的变量名

**百分号格式（`%s`/`%d`）**：
```gettext
#, c-format
msgid "File %s not found"
msgstr "未找到文件 %s"
```
- `%s` = 字符串，`%d` = 整数，`%f` = 浮点数
- 顺序可通过 `%1$s`、`%2$s` 显式指定

**HTML/XML 标签**：
```gettext
msgid "Click <a>here</a> to continue"
msgstr "点击<a>此处</a>继续"
```
- 保留所有 HTML 标签，不要删除
- 标签内的文本需要翻译
- 注意标签嵌套正确性

### 2. 快捷键标记（`&` 和 `_`）

菜单项中的 `&` 标记 Alt+快捷键：
```gettext
msgid "&File"
msgstr "文件(&F)"
```
- 保留 `&` 符号，放在对应字符前
- 中文通常用括号标注快捷键字符
- 同一菜单下的快捷键字符不能重复

### 3. 多行字符串

长字符串使用多个双引号行：
```gettext
msgid ""
"This is a very long message that spans "
"multiple lines in the PO file."
msgstr ""
"这是一条很长的消息，"
"在PO文件中跨越多行。"
```
- 每行末尾的 `\n` 表示换行符（字面换行）
- 没有 `\n` 的跨行只是为了 PO 文件可读性，拼接后无换行

### 4. 复数形式（Plural Forms）

```gettext
#, python-brace-format
msgid "{count} file"
msgid_plural "{count} files"
msgstr[0] "{count} 个文件"
```
- 中文 `Plural-Forms: nplurals=1; plural=0;`，只有一个复数形式
- 英文有两个形式（0: 1个，1: 其他数量）
- 俄语/阿拉伯语等有3-6个复数形式

### 5. 上下文消歧（msgctxt）

同一英文单词在不同语境下需要不同翻译：
```gettext
msgctxt "verb"
msgid "Run"
msgstr "运行"

msgctxt "noun"
msgid "Run"
msgstr "运行记录"

msgctxt "menu"
msgid "Close"
msgstr "关闭"

msgctxt "button"
msgid "Close"
msgstr "关闭"
```
- msgctxt 帮助译者理解语境
- 不同 msgctxt 的条目即使 msgid 相同，也是独立翻译
- JupyterLab 中常见 msgctxt：`schema`、`settings`、`menu`、`command`、`toolbar`

### 6. Markdown 和代码标记

JupyterLab 的描述文本中常包含 Markdown 语法：
```gettext
msgid ""
"**Bold text** and *italic text* with `code` "
"and [link](url) in markdown."
msgstr ""
"**粗体文本**和*斜体文本*，以及`代码`"
"和 Markdown 中的[链接](url)。"
```
- 保留 `**`、`*`、`` ` ``、`[]()` 等 Markdown 标记
- `` ` `` 中的代码/变量名不翻译
- 链接 URL 不翻译

### 7. 空白字符

```gettext
msgid "  Indented text  "
msgstr "  缩进文本  "
```
- 前导/尾随空格必须保留
- Tab 字符通常不要添加
- `\n` 换行符必须保留

## 翻译质量注意事项

### 术语一致性

JupyterLab 有固定的技术术语翻译，应保持一致：

| 英文 | 推荐中文翻译 |
|------|-------------|
| Notebook | 笔记本 |
| Kernel | 内核 |
| Cell | 单元格 |
| Extension | 扩展 |
| Command Palette | 命令面板 |
| File Browser | 文件浏览器 |
| Launcher | 启动器 |
| Sidebar | 侧边栏 |
| Workspace | 工作区 |
| Debugger | 调试器 |
| Variable Inspector | 变量检查器 |
| Output | 输出 |
| Console | 控制台 |
| Terminal | 终端 |
| Interrupt | 中断 |
| Restart | 重启 |
| Shutdown | 关闭 |
| Execute | 执行 |
| Run | 运行 |

### 标点符号规范（中文）

- 中文句子使用全角标点：`，。：；！？（）`
- 中英文之间加空格：`点击 File 菜单`
- 中文与数字之间加空格：`保存了 3 个文件`
- 代码/变量名保持半角：`` 变量 `count` 的值 ``
- 句末英文缩写保留英文点号：`使用 JupyterLab 4.x.`（末尾点号是英文句号）

### 不要翻译的内容

- 变量名：`{count}`、`{path}`
- 代码标识符：`jupyterlab-lsp`、`ipywidgets`
- 文件路径：`/home/user/notebook.ipynb`
- URL：`https://jupyter.org`
- 命令名：`jupyter lab`、`pip install`
- 快捷键：`Shift+Enter`、`Ctrl+C`
- 版本号：`4.5.0`、`v4.6`

### Fuzzy 翻译

```gettext
#, fuzzy
msgid "New string"
msgstr "旧的翻译（需要更新）"
```
- `fuzzy` 标志表示翻译可能不准确（通常是 msgid 变更后自动匹配的旧翻译）
- fuzzy 的翻译不会被编译进 MO 文件（即运行时不会使用）
- 译者需要检查并更新翻译，然后移除 fuzzy 标志
- Crowdin 中 fuzzy 翻译标记为"需要审核"

### 未翻译字符串

空的 msgstr 表示未翻译：
```gettext
msgid "Untranslated string"
msgstr ""
```
- 运行时 JupyterLab 会回退到英文原文
- 不要保留机器翻译的半成品，空翻译比错误翻译好
- 不确定时查阅 JupyterLab 文档或其他语言的翻译参考

## 特殊翻译场景

### In-Context 伪语言（ach-UG）

`ach-UG` 语言包不是真正的翻译，而是 Crowdin 的 in-context 工具：
- 安装后界面显示特殊标记的字符串
- 用于在运行的 JupyterLab 中直接点击翻译
- 普通用户不要安装
- 其 PO 文件内容是 Crowdin 生成的特殊标记，不是阿乔利语

### 大小写处理

JupyterLab 中字符串的大小写通常有语义：
- Title Case（如 "Run Selected Cell"）：菜单项、命令名、按钮标签
- Sentence case（如 "Are you sure?"）：对话框消息、描述文本
- lowercase（如 "cell"）：普通文本中的单词
- 中文不区分大小写，但要注意专有名词的正确写法

### 性别/敬语

英文不分性别，中文也基本不需要处理。但某些语言（如法语、德语）需要根据用户性别或正式程度选择不同形式。中文使用通用表达即可。

## 贡献翻译的工作流

通过 Crowdin 贡献翻译时：
1. 注册 Crowdin 账号
2. 加入 JupyterLab 项目：https://crowdin.com/project/jupyterlab
3. 选择目标语言
4. 在 Web 编辑器中翻译字符串
5. 参考翻译记忆（TM）和术语库（TB）保持一致性
6. 保存翻译
7. 翻译会在下一次 Crowdin 同步时自动进入 GitHub

无需手动编辑 PO 文件或创建 Git PR。

## 相关概念

- [Gettext 国际化基础](06-gettext-i18n.md)
- [Crowdin 翻译平台集成](04-crowdin-integration.md)
- [贡献翻译](../examples/03-contribute-translation.md)
