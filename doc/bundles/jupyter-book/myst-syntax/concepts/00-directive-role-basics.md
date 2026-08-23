---
type: concept
title: "指令与角色基础"
description: "MyST语法扩展的核心机制：DirectiveSpec/RoleSpec接口、指令和角色的声明式定义、通用选项、别名系统"
tags: [myst-syntax, directive, role, syntax-basics, directive-spec, role-spec]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/utils.ts"
    facts: [F-S009, F-S010, F-S011]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/utils.ts"
    facts: [F-S043, F-S044]
---

# 指令与角色基础

MyST Markdown 通过指令（Directive）和角色（Role）两套扩展机制丰富文档表达能力。指令是块级元素（类似 HTML 块），角色是行内元素（类似 HTML 行内标签）。

## 语法格式

### 指令语法

MyST 使用 fenced code block 语法定义指令：

````markdown
:::{directive-name} argument
:option1: value1
:option2: value2

指令体内容，可以包含 **MyST Markdown**。
:::
````

- 指令名在大括号中：`:::{figure}`
- 参数（argument）紧跟指令名：`:::{figure} image.png`
- 选项以 `:key: value` 格式在头部
- 空行后是指令体（body）
- 短指令可以使用反引号：``` ```{code-block} python ```

### 角色语法

行内角色使用大括号加反引号：

```markdown
{role-name}`角色内容`
```

- 角色名在大括号中
- 内容在反引号中
- 支持显示文本覆盖：`{ref}`显示文本<标签>`

## 声明式定义

### DirectiveSpec 接口

每个指令是一个符合 DirectiveSpec 接口的纯数据对象：

```ts
type DirectiveSpec = {
  name: string;                 // 主名
  doc?: string;                 // 文档字符串
  alias?: string[];             // 别名列表
  arg?: {                       // 参数定义
    type: String | 'myst';
    required?: boolean;
    doc?: string;
  };
  options?: Record<string, {    // 选项定义
    type: String | Boolean | Number;
    alias?: string[];
    doc?: string;
  }>;
  body?: {                      // 内容体定义
    type: String | 'myst';
    required?: boolean;
  };
  validate?: (data, vfile) => DirectiveData;  // 可选验证钩子
  run(data, vfile, ctx): GenericNode[];       // 核心转换逻辑
};
```

### RoleSpec 接口

角色接口更简化（无 body type 区分、无 validate、选项较少）：

```ts
type RoleSpec = {
  name: string;
  alias?: string[];
  options?: Record<string, OptionSpec>;
  body: { type: String; required?: boolean };
  run(data): GenericNode[];
};
```

## 参数和体的类型

| 类型 | 含义 | run() 接收的数据类型 |
|------|------|---------------------|
| `String` | 原始文本 | `string` |
| `Number` | 数字 | `number` |
| `Boolean` | 布尔标志（选项无值时为 true） | `boolean` |
| `'myst'` | MyST 内容（递归解析为 MDAST） | `GenericNode[]` |

对于指令体：
- `type: String` → 代码块、原始文本、数学公式等
- `type: 'myst'` → 提示框、表格、章节等需要格式化的内容

## 通用选项

### 指令通用选项

`commonDirectiveOptions(nodeType)` 为所有块级指令提供四个选项：

| 选项 | 别名 | 类型 | 用途 |
|------|------|------|------|
| `class` | - | String | CSS 类名（空格分隔多个） |
| `label` | `name` | String | 交叉引用标签 |
| `enumerated` | `numbered` | Boolean | 是否参与编号 |
| `enumerator` | `number` | String | 显式设置编号值 |

通过 `addCommonDirectiveOptions(data, node)` 统一应用到输出节点。

### 角色通用选项

`commonRoleOptions(nodeType)` 提供两个选项：

| 选项 | 别名 | 类型 | 用途 |
|------|------|------|------|
| `class` | - | String | CSS 类名 |
| `label` | `name` | String | 交叉引用标签 |

角色是行内元素，不参与编号，因此没有 enumerated/enumerator。

## 别名系统

指令和角色都支持丰富的别名，实现多生态兼容：

- **RST/Sphinx 兼容**：code-block（code）、literalinclude（include）、toctree（toc）、eq/numref（ref）
- **Jupyter Book 兼容**：figwidth/figclass
- **Docutils 兼容**：contents（toc）、sidebar/topic（aside）
- **Biblatex 引用风格**：cite:p/cite:t/cite:year/cite:author 等18个别名

别名在 run() 中通过 `data.name` 判断使用的是哪个名称，从而产生不同行为（如 admonition 的 kind 根据别名设定）。

## 指令 vs 角色：何时使用哪个？

| 特征 | 指令（Directive） | 角色（Role） |
|------|------------------|-------------|
| 语法 | `:::{name}...:::` | `{name}`...`` |
| 层级 | 块级（block-level） | 行内（inline） |
| 内容体 | 支持多行、结构化 | 单行文本 |
| 选项 | 支持 :key: value 选项 | 选项较简化 |
| 用途 | 提示框、代码块、图片、表格、章节容器 | 引用、缩写、数学、格式化文本 |
| 输出 | MDAST 容器节点（可包含子节点） | 行内 MDAST 节点 |
| 编号 | 支持 enumerated/enumerator | 不支持 |

## run() 方法约定

所有指令和角色的 run() 方法遵循相同约定：

1. **接收**：解析后的 data（包含 arg/options/body）
2. **处理**：根据 data 构建 MDAST 节点
3. **返回**：GenericNode[]（通常是一个节点）
4. **错误处理**：通过 vfile 的 fileError/fileWarn 报告问题
5. **通用选项**：通过 addCommonDirectiveOptions/addCommonRoleOptions 应用 class/label 等

## 注册机制

默认指令和角色通过数组导出：
- `defaultDirectives`：28 个预定义指令
- `defaultRoles`：20 个预定义角色

这些数组在 myst-cli 处理管线启动时注册到 MyST 解析器中。插件可以追加自定义指令和角色。

## 相关概念

- [提示框与标注](01-admonition-callouts.md)
- [代码块](02-code-blocks.md)
- [图片与图表](03-figures-images.md)
- [表格](04-tables.md)
- [数学公式](05-math.md)
