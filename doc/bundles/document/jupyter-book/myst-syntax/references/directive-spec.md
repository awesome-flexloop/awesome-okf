---
type: reference
title: "DirectiveSpec 接口与指令注册"
description: "myst-common中DirectiveSpec接口定义、指令数据结构(DirectiveData)和通用选项工具(utils.ts)源码参考"
tags: [reference, directives, api, directive-spec, utils]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/utils.ts"
    facts: [F-S009, F-S010, F-S011]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/index.ts"
    facts: [F-S012]
---

# DirectiveSpec 接口与指令注册

本文档提供 myst-directives 中指令规范接口和注册机制的源码参考。

## defaultDirectives 导出

[directives/index.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/index.ts#L1-L76) 导出 `defaultDirectives` 数组，包含 28 个预定义指令：

```ts
export const defaultDirectives = [
  admonitionDirective,
  bibliographyDirective,
  csvTableDirective,
  codeDirective,
  codeCellDirective,
  dropdownDirective,
  embedDirective,
  blockquoteDirective,
  figureDirective,
  iframeDirective,
  imageDirective,
  includeDirective,
  indexDirective,
  genIndexDirective,
  tableDirective,
  listTableDirective,
  asideDirective,
  glossaryDirective,
  mathDirective,
  mdastDirective,
  mermaidDirective,
  mystdemoDirective,
  rawDirective,
  rawLatexDirective,
  rawTypstDirective,
  divDirective,
  tocDirective,
  widgetDirective,
];
```

## 通用选项工具

[directives/utils.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/utils.ts#L1-L82) 提供选项混入和应用工具：

### commonDirectiveOptions()

```ts
export function commonDirectiveOptions(nodeType = 'node'): Required<DirectiveSpec>['options'] {
  return {
    ...classDirectiveOption(nodeType),    // class: CSS类名（空格分隔）
    ...labelDirectiveOption(nodeType),    // label/name: 交叉引用标签
    ...enumerationDirectiveOptions(nodeType), // enumerated/numbered + enumerator/number
  };
}
```

### classDirectiveOption()

```ts
export function classDirectiveOption(nodeType = 'node') {
  return {
    class: {
      type: String,
      doc: `Annotate the ${nodeType} with a set of space-delimited class names.`,
    },
  };
}
```

### labelDirectiveOption()

```ts
export function labelDirectiveOption(nodeType = 'node') {
  return {
    label: {
      type: String,
      alias: ['name'],
      doc: `Label the ${nodeType} to be cross-referenced or explicitly linked to.`,
    },
  };
}
```

### enumerationDirectiveOptions()

```ts
export function enumerationDirectiveOptions(nodeType = 'node'): Required<DirectiveSpec>['options'] {
  return {
    enumerated: {
      type: Boolean,
      alias: ['numbered'],
      doc: `Turn on/off the numbering for the specific ${nodeType}`,
    },
    enumerator: {
      type: String,
      alias: ['number'],
      doc: `Explicitly set the ${nodeType} number`,
    },
  };
}
```

### addCommonDirectiveOptions()

```ts
export function addCommonDirectiveOptions(data: DirectiveData, node: GenericNode) {
  addClassOptions(data, node);          // node.class = data.options.class
  addLabelOptions(data, node);          // normalizeLabel → node.label + node.identifier
  addEnumerationOptions(data, node);    // node.enumerated + node.enumerator
  return node;
}
```

addLabelOptions 使用 `normalizeLabel()` 从 label 字符串提取规范化标签和标识符。

## 关键类型

### DirectiveSpec

```ts
type DirectiveSpec = {
  name: string;                    // 指令主名
  doc?: string;                    // 文档字符串
  alias?: string[];                // 别名列表
  arg?: {                          // 参数定义
    type: String | 'myst';
    doc?: string;
    required?: boolean;
  };
  options?: Record<string, {       // 选项定义
    type: String | Boolean | Number;
    doc?: string;
    alias?: string[];
  }>;
  body?: {                         // 内容体定义
    type: String | 'myst';
    doc?: string;
    required?: boolean;
  };
  validate?: (data: DirectiveData, vfile: VFile) => DirectiveData;
  run(data: DirectiveData, vfile: VFile, ctx: DirectiveContext): GenericNode[];
};
```

### DirectiveData

```ts
type DirectiveData = {
  node: GenericNode;    // 解析器生成的原始指令节点
  name: string;         // 实际使用的指令名（可能是别名）
  arg?: any;            // 解析后的参数
  options?: Record<string, any>;  // 解析后的选项
  body?: any;           // 解析后的内容体
};
```
