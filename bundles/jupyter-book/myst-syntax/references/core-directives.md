---
type: reference
title: "核心指令源码：Admonition/Code/Figure/Table"
description: "myst-directives中admonition、code/code-cell、figure、table/list-table/csv-table、math等核心指令的实现源码参考"
tags: [reference, directives, admonition, code, figure, table, math]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/admonition.ts"
    facts: [F-S013]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/code.ts"
    facts: [F-S014, F-S015, F-S016, F-S017]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/figure.ts"
    facts: [F-S018]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/table.ts"
    facts: [F-S020, F-S021, F-S022]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/math.ts"
    facts: [F-S023]
---

# 核心指令源码参考

本文档提供 myst-directives 中最常用核心指令的实现细节参考。

## Admonition 指令

[admonition.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/admonition.ts#L1-L78)

### 别名（10种）

attention、caution、danger、error、important、hint、note、seealso、tip、warning

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| class | String | CSS 类名。特殊类：`dropdown`（转为details元素）、`simple`（简单样式）、admonition 名称（如 `tip`） |
| icon | Boolean | false 时隐藏图标 |
| open | Boolean | 将 admonition 转为可折叠并设置初始状态 |
| label/name | String | 交叉引用标签 |
| enumerated | Boolean | 编号开关 |

### run() 逻辑

```ts
run(data) {
  const children = [];
  if (data.arg) {
    // 参数作为标题（admonitionTitle）
    // 无 body 时参数作为段落
    children.push({ type: data.body ? 'admonitionTitle' : 'paragraph', children: data.arg });
  }
  if (data.body) children.push(...data.body);
  
  const admonition: Admonition = {
    type: 'admonition',
    kind: data.name !== 'admonition' ? data.name : undefined,  // 别名作为kind
    children,
  };
  if (data.options?.icon === false) admonition.icon = false;
  addCommonDirectiveOptions(data, admonition);
  
  // open选项 → 自动添加dropdown类名
  if (typeof data.options?.open === 'boolean') {
    if (!admonition.class?.includes('dropdown')) {
      admonition.class = `${admonition.class ?? ''} dropdown`.trim();
    }
    if (data.options.open) admonition.open = true;
  }
  return [admonition];
}
```

## Code 和 Code-Cell 指令

[code.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/code.ts#L1-L281)

### CODE_DIRECTIVE_OPTIONS

```ts
{
  caption: { type: 'myst' },           // 解析后的标题
  linenos: { type: Boolean },          // 显示行号
  'lineno-start': { type: Number },    // 起始行号
  'number-lines': { type: Number },    // 起始行号（别名方案）
  'emphasize-lines': { type: String }, // 高亮行 "3,5,7-9"
  filename: { type: String },          // 文件名标签
}
```

### codeDirective.run()

```ts
run(data, vfile) {
  const opts = getCodeBlockOptions(data, vfile);
  const code: Code = {
    type: 'code',
    lang: data.arg,           // 语言类型
    ...opts,                   // emphasizeLines/showLineNumbers/startingLineNumber/filename
    value: data.body,          // 代码内容
  };
  if (!data.options?.caption) {
    addCommonDirectiveOptions(data, code);
    return [code];
  }
  // 有caption时包裹在container(kind:'code')中
  const container: Container = {
    type: 'container',
    kind: 'code',
    children: [code, { type: 'caption', children: [{ type: 'paragraph', children: data.options.caption }] }],
  };
  addCommonDirectiveOptions(data, container);
  return [container];
}
```

### codeCellDirective.run()

```ts
run(data, vfile) {
  const code: Code = {
    type: 'code',
    lang: data.arg,
    executable: true,          // 标记为可执行
    value: data.body ?? '',
    ...getCodeBlockOptions(data, vfile),
  };
  const outputs = { type: 'outputs', id: nanoid(), children: [] };
  const block = {
    type: 'block',
    kind: NotebookCell.code,
    children: [code, outputs],
    data: {},
  };
  addCommonDirectiveOptions(data, block);
  if (data.options?.caption) block.data.caption = [...];
  const tags = parseTags(data.options?.tags, vfile, data.node);
  if (tags) block.data.tags = tags;
  return [block];
}
```

### parseEmphasizeLines()

支持单数字和范围：

```ts
"3,5,7-9" → [3, 5, 7, 8, 9]
```

范围 start > end 产生警告。无效值产生警告。

### parseTags()

支持三种格式：
1. 逗号/空格分隔字符串：`"remove-input, hide-cell"`
2. YAML 数组字符串：`"[remove-input, hide-cell]"`
3. 直接 YAML 数组（通过解析器传入）

## Figure 指令

[figure.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/figure.ts#L1-L113)

### 选项

| 选项 | 类型 | 别名 | 说明 |
|------|------|------|------|
| class | String | figclass | CSS类名，full-width跨两列 |
| width | String | w, figwidth | CSS宽度 |
| height | String | h | CSS高度 |
| alt | String | - | 替代文本 |
| align | String | - | left/center/right |
| remove-input | Boolean | - | Notebook单元格移除输入 |
| remove-output | Boolean | - | Notebook单元格移除输出 |
| placeholder | String | - | 静态导出占位图 |
| no-subfigures | Boolean | no-subfig, no-subfigure | 禁止隐式子图创建 |
| kind | String | - | 覆盖枚举类型 |

### run() 输出结构

有 arg（图片路径）时：
```
container(kind:'figure'|自定义kind)
  ├── image(url, alt, width, height, align, remove-input, remove-output)
  ├── image(placeholder, placeholder=true)  [可选]
  └── body中的caption内容
```

无 arg 时，body 中的图片解析为子图（subfigure）。

## Table 指令系列

[table.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/table.ts#L1-L331)

### tableDirective

- arg：可选标题（myst）
- body：MyST 表格内容（必填）
- 输出：container(kind:'table') → caption + table

### listTableDirective

- body 必须是嵌套列表（list of lists），validate() 强制验证
- header-rows 选项指定表头行数
- 从嵌套列表结构生成 table → tableRow → tableCell(header: true/false)

### csvTableDirective

- 使用 csv-parse 库解析 CSV body
- 支持 header（补充表头行）、header-rows、delim（分隔符，tab/space/自定义）、keepspace、quote、escape
- 每个单元格通过 ctx.parseMyst() 递归解析为 MyST 内容
- CSV 解析错误产生 fileError

## Math 指令

[math.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/math.ts#L1-L28)

```ts
run(data) {
  const math = addCommonDirectiveOptions(data, {
    type: 'math',
    value: data.body,    // LaTeX 数学表达式
  });
  if (data.node.tight) math.tight = data.node.tight;
  if (data.options?.typst) math.typst = data.options.typst;  // Typst 备用内容
  return [math];
}
```
