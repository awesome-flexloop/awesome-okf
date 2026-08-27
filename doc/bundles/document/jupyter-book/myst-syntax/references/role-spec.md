---
type: reference
title: "角色系统：RoleSpec 接口与默认角色"
description: "myst-roles中RoleSpec接口定义、RoleData结构、通用角色选项和defaultRoles数组源码参考"
tags: [reference, roles, api, role-spec, cite, ref]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/index.ts"
    facts: [F-S045]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/utils.ts"
    facts: [F-S043, F-S044]
---

# 角色系统：RoleSpec 接口与默认角色

本文档提供 myst-roles 中角色规范接口和注册机制的源码参考。

## defaultRoles 导出

roles/index.ts 导出 `defaultRoles` 数组，包含 20 个预定义角色：

```ts
export const defaultRoles = [
  spanRole,              // 行内容器
  abbreviationRole,      // 缩写（abbr）
  chemRole,              // 化学式（chemicalFormula/chem）
  citeRole,              // 引用（cite/cite:p/cite:t/...）
  deleteRole,            // 删除线
  mathRole,              // 行内数学
  refRole,               // 交叉引用（ref/eq/numref）
  docRole,               // 文档引用
  downloadRole,          // 下载链接
  indexRole,             // 索引条目
  termRole,              // 术语引用
  siRole,                // SI单位
  evalRole,              // 行内表达式
  smallcapsRole,         // 小型大写
  subscriptRole,         // 下标
  superscriptRole,       // 上标
  underlineRole,         // 下划线
  keyboardRole,          // 键盘按键
  rawLatexRole,          // 行内LaTeX（raw:latex/raw:tex）
  rawTypstRole,          // 行内Typst（raw:typst/raw:typ）
];
```

## 通用角色选项

roles/utils.ts 提供角色通用选项工具：

### commonRoleOptions()

角色通用选项比指令少（不含 enumeration 相关）：

```ts
export function commonRoleOptions(nodeType = 'node'): Required<RoleSpec>['options'] {
  return {
    ...classRoleOption(nodeType),    // class: CSS类名
    ...labelRoleOption(nodeType),    // label/name: 标签
  };
}
```

### addCommonRoleOptions()

```ts
export function addCommonRoleOptions(data: RoleData, node: GenericNode) {
  addClassOptions(data, node);       // node.class = data.options.class
  addLabelOptions(data, node);       // normalizeLabel → node.label + node.identifier
  return node;
}
```

## Cite 角色详解

roles/cite.ts 实现了最复杂的角色，支持 BibTeX/biblatex 风格引用：

### 别名列表（18个）

```ts
alias: [
  'cite:p', 'cite:t',        // parenthetical / narrative
  'cite:ps', 'cite:ts',      // short form
  'cite:ct', 'cite:cts',     // capitalized
  'cite:alp', 'cite:alps',   // alpha style
  'cite:label', 'cite:labelpar',
  'cite:year', 'cite:yearpar',       // partial: year only
  'cite:author', 'cite:authors',     // partial: author only
  'cite:authorpar', 'cite:authorpars',
  'cite:cauthor', 'cite:cauthors',   // capitalized author
]
```

### kind 判定逻辑

```ts
const kind: CiteKind =
  data.name.startsWith('cite:p') || data.name.includes('par') || data.name.includes('cite:alp')
    ? 'parenthetical'
    : 'narrative';
```

### 前缀后缀语法

```ts
// {cite:p}`{see}1977:nelson{p. 1166}`
const groups = /^(?:\{([^{]*)\})?([^{]*)(?:\{([^{]*)\})?$/;
const [, prefix, l, suffix] = c.match(groups) ?? ['', '', c];
```

### 分组逻辑

- 单引用且角色名为 'cite'：直接返回 Cite 节点
- cite:alp 风格：返回独立的 Cite 节点数组
- 其他情况：多引用包裹在 CiteGroup 中

## Ref 角色详解

roles/reference.ts：

```ts
const REF_PATTERN = /^(.+?)<([^<>]+)>$/;  // 'Labeled Reference <ref>'

run(data) {
  const match = REF_PATTERN.exec(body);
  const [, modified, rawLabel] = match ?? [];
  const { label, identifier } = normalizeLabel(rawLabel ?? body) || {};
  const crossRef = { type: 'crossReference', kind: data.name, identifier, label };
  if (modified) crossRef.children = [{ type: 'text', value: modified.trim() }];
  return [crossRef];
}
```

别名：['eq', 'numref', 'prf:ref', 'proof:ref']。

## 关键类型

### RoleSpec

```ts
type RoleSpec = {
  name: string;
  alias?: string[];
  options?: Record<string, {
    type: String | Boolean | Number;
    doc?: string;
    alias?: string[];
  }>;
  body: {
    type: String;
    required?: boolean;
  };
  run(data: RoleData): GenericNode[];
};
```

### RoleData

```ts
type RoleData = {
  node: GenericNode;
  name: string;
  options?: Record<string, any>;
  body: string;
};
```
