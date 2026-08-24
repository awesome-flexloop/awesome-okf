---
type: concept
title: 指令与角色系统（Directives & Roles）
description: MyST 的扩展语法机制——指令（块级）和角色（行内），通过 DirectiveSpec/RoleSpec 声明式定义，支持参数、选项、内容体，以及递归解析嵌套 MyST 内容。
tags: [mystmd, directive, role, extension, myst-directives, myst-roles]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-common-source.md"
    facts: [F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055]
  - path: "/references/myst-parser-source.md"
    facts: [F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025]
---

## 指令（Directives）和角色（Roles）概述

指令和角色是 MyST Markdown 的两大扩展机制：

| 特性 | 指令（Directive） | 角色（Role） |
|------|------------------|-------------|
| 语法 | ` ```{name} ` 或 `:::{name}` | `{name}`content`{name}` |
| 作用域 | 块级（Block） | 行内（Inline） |
| 参数（arg） | ✅ 第一行非选项文本 | ❌ 无独立参数 |
| 选项（options） | ✅ `:key: value` 格式 | ✅ 支持 |
| 内容体（body） | ✅ 围栏内的所有内容 | ✅ 反引号内的内容 |
| 递归解析 | ✅ ctx.parseMyst 回调 | ❌ 无 ctx 参数 |

## 指令语法

### 围栏指令（Fence）

````markdown
```{directive-name} argument text
:option1: value1
:option2: value2

Body content goes here.
Can be multiple lines and contain **Markdown**.
```
````

### 冒号围栏（Colon Fence）

```markdown
:::{directive-name} argument text
:option1: value1

Body content here.
:::
```

### 短形式（行内指令）

```markdown
```{directive-name} argument
```
（无 body，仅参数）
```

### 指令结构

````
```{name} <arg>                    ← 名称 + 参数
:key: value                       ← 选项（YAML 或键值对）
                                  ← 空行分隔选项和 body
Body content here...              ← 内容体
```
````

## 角色语法

```markdown
Some text with {role-name}`role content` inline.

Some text with {role-name}`:option: value role body` inline.
```

角色是行内元素，不能跨段落。内容体位于反引号内，选项通过 `:key: value` 前缀放在 body 前面。

## DirectiveSpec 定义

```ts
const myDirective: DirectiveSpec = {
  name: 'my-directive',
  alias: ['md'],                     // 别名
  doc: 'My custom directive',
  
  // 参数定义（第一行非选项文本）
  arg: {
    type: 'string',                  // ParseTypesEnum.string/number/boolean/parsed/'myst'
    required: false,
    doc: 'The argument description',
  },
  
  // 选项定义（:key: value 对）
  options: {
    width: {
      type: 'string',
      doc: 'Width of the element',
    },
    caption: {
      type: 'parsed',                // 解析为 MDAST 节点
      doc: 'Caption text',
    },
    numbered: {
      type: Boolean,                 // JS 构造函数形式
      doc: 'Whether to number',
    },
  },
  
  // 内容体定义
  body: {
    type: 'myst',                    // 递归解析为 MyST
    doc: 'The main content',
  },
  
  // 可选验证函数
  validate(data, vfile) {
    // 自定义验证逻辑，返回修正后的数据
    return data;
  },
  
  // 核心运行函数
  run(data, vfile, ctx) {
    // data.name - 指令名
    // data.node - 原始 mystDirective 节点
    // data.arg - 解析后的参数值
    // data.options - 解析后的选项对象
    // data.body - 解析后的内容体
    
    // ctx.parseMyst(source, offset?) - 递归解析 MyST 字符串
    const children = ctx.parseMyst(data.body);
    
    // 返回替换 children 的节点数组
    return [{
      type: 'myCustomNode',
      children: children.children,
      options: data.options,
    }];
  },
};
```

## RoleSpec 定义

```ts
const myRole: RoleSpec = {
  name: 'my-role',
  alias: ['mr'],
  doc: 'My custom role',
  
  options: {
    // 同 DirectiveSpec.options
  },
  
  body: {
    type: 'parsed',                  // 'myst' 不可用于角色（无 ctx）
    doc: 'Role content',
  },
  
  validate(data, vfile) {
    return data;
  },
  
  run(data, vfile) {
    // data.name - 角色名
    // data.node - 原始 mystRole 节点
    // data.body - 解析后的内容体
    // data.options - 解析后的选项
    
    return [{
      type: 'myCustomInline',
      children: data.body as GenericNode[],
    }];
  },
};
```

## 参数类型系统

| type 值 | 解析结果 | 适用位置 |
|---------|---------|---------|
| `ParseTypesEnum.string` 或 `String` | 字符串 | arg/options/body |
| `ParseTypesEnum.number` 或 `Number` | 数字（自动转换） | arg/options/body |
| `ParseTypesEnum.boolean` 或 `Boolean` | 布尔值（true/false） | options |
| `ParseTypesEnum.parsed` | GenericNode[]（已解析的内联节点） | arg/options/body |
| `'myst'` | GenericParent（递归解析 MyST 块级内容） | arg/body |

## 内置指令

myst-directives 包提供的核心内置指令：

| 指令 | 说明 |
|------|------|
| `figure` | 图片容器（含 caption） |
| `image` | 图片 |
| `table` | 表格 |
| `code-block` | 代码块（增强版） |
| `admonition`/`note`/`warning`/`tip` 等 | 提示块 |
| `math` | 块级数学公式 |
| `include` | 嵌入外部文件 |
| `embed` | 嵌入其他文档节点 |
| `iframe` | 嵌入 iframe |
| `tab-set`/`tab-item` | 选项卡 |
| `grid`/`card` | 网格布局 |
| `dropdown` | 可折叠内容 |
| `div` | 通用 div 容器 |
| `myst`/`raw` | 原始内容/格式特定内容 |
| `index` | 索引条目 |
| `glossary` | 术语表 |
| `bibliography` | 参考文献列表 |
| `footnote` | 脚注定义 |

## 内置角色

myst-roles 包提供的核心内置角色：

| 角色 | 说明 |
|------|------|
| `math` | 行内数学公式 |
| `cite`/`cite:p`/`cite:t` | 参考文献引用 |
| `ref`/`numref`/`eq`/`eqr` | 交叉引用 |
| `link` | 外部链接 |
| `download` | 下载链接 |
| `abbr` | 缩写 |
| `sub`/`sup` | 下标/上标 |
| `kbd` | 键盘按键 |
| `menuselection`/`guilabel` | GUI 元素 |
| `file`/`command`/`envvar` | 技术文档元素 |
| `si` | SI 单位 |

## 指令处理流程

```
Markdown 文本
     │
     ▼
markdown-it (mystDirectivePlugin)
     │ 识别 ```{name} 和 :::{name} 语法
     │ 生成 parsed_directive_open/close Token
     ▼
tokensToMyst (MarkdownParseState)
     │ Token → mystDirective 节点
     │ { name, arg, options, body: raw-string, children: [] }
     ▼
applyDirectives(tree, directives, vfile, stack, ctx)
     │ 遍历 mystDirective[processed=false]
     │ 1. 查找 DirectiveSpec
     │ 2. 解析 options（YAML 或键值对）
     │ 3. 按 type 解析 arg/body
     │ 4. 调用 spec.validate(data, vfile)
     │ 5. 调用 spec.run(data, vfile, ctx) → GenericNode[]
     │ 6. 赋值给 node.children，标记 processed=true
     ▼
mystDirective 节点被 children 填充
     │
     ▼
liftMystDirectivesAndRoles (在 basicTransformations 中)
     │ 将 mystDirective 节点的 children 提升到父层级
     ▼
最终 AST（包含具体节点如 figure/admonition/tab-set 等）
```

## 选项解析格式

指令选项支持两种格式：

### 键值对格式（简单值）
```markdown
:width: 100%
:height: 200
:name: test
```

### YAML 格式（复杂值，以 `:---:` 开头）
```markdown
:---
:width: 100%
:figwidth: 80%
:alt: Multi-line
  description here
:options:
  key1: val1
  key2: val2
:---
```

## ctx.parseMyst 递归解析

指令的 run 方法接收 `ctx: DirectiveContext`，其中 `parseMyst` 允许递归解析嵌套的 MyST 内容：

```ts
run(data, vfile, ctx) {
  // body 是 MyST 字符串（如未自动解析）
  const innerTree = ctx.parseMyst(data.body, {
    // 可选的起始行偏移（用于正确的位置信息）
    startingLineNumber: data.node.position.start.line + 3,
  });
  // innerTree 是一个完整的 GenericParent（root 节点）
  // 使用 innerTree.children 作为子节点
  return [{ type: 'myNode', children: innerTree.children }];
}
```

如果 body 的 type 声明为 `'myst'`，解析器会自动调用 parseMyst 递归解析，data.body 直接是 GenericParent 类型。

## 别名处理

指令和角色都支持 alias 数组。在 applyDirectives/applyRoles 阶段，会将原始名称和所有别名都注册到查找映射中。例如 `cite:p` 和 `cite:t` 是 `cite` 角色的别名变体。

## 相关概念

- [统一插件架构](/concepts/01-unified-plugin-architecture.md)
- [MyST 解析器](/concepts/02-myst-parser.md)
- [公共类型系统](/concepts/04-myst-common-types.md)
- [自定义指令示例](/examples/05-custom-directive.md)
- [自定义角色示例](/examples/04-custom-role.md)
