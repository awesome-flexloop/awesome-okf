---
type: example
title: 使用 mystParse 解析 MyST Markdown
description: 演示如何使用 myst-parser 的 mystParse 函数解析 MyST Markdown 字符串为 MDAST 树，并访问解析结果。
tags: [mystmd, parser, mystParse, mdast, vfile]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-parser-source.md"
    facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-045]
  - path: "/concepts/02-myst-parser.md"
    facts: []
---

## 目标

使用 `myst-parser` 的 `mystParse` 函数将 MyST Markdown 字符串解析为 MDAST（Markdown Abstract Syntax Tree），并检查解析结果和错误。

## 前置条件

- Node.js 16+
- 已安装 `myst-parser`、`myst-common`、`myst-directives`、`myst-roles` 包

```bash
npm install myst-parser myst-common myst-directives myst-roles
```

## 示例代码

### 最小解析示例

```ts
import { mystParse } from 'myst-parser';

const content = `# Hello MyST

This is **bold** and *italic* text with {math}`e=mc^2`{math}.

(sec:intro)=

## Introduction

Some paragraph text with a [link](https://example.com).

\`\`\`{note}
This is a note admonition.
\`\`\`
`;

// 最简单的调用——使用默认配置
const mdast = mystParse(content);

console.log(mdast.type);  // 'root'
console.log(mdast.children.length);  // 5（H1 + paragraph + target + H2 + paragraph + note directive）
```

### 使用 VFile 收集错误

```ts
import { mystParse } from 'myst-parser';
import { VFile } from 'vfile';

const content = `# Test

\`\`\`{unknown-directive}
This uses a directive that doesn't exist.
\`\`\`
`;

const vfile = new VFile();
vfile.value = content;
vfile.path = 'test.md';

const mdast = mystParse(content, { vfile });

// 检查错误
vfile.messages.forEach(msg => {
  console.log(`[${msg.fatal ? 'ERROR' : 'WARN'}] ${msg.ruleId}: ${msg.message}`);
  console.log(`  at line ${msg.line}:${msg.column}`);
});

// 输出:
// [ERROR] unknownDirective: Unknown directive: {unknown-directive}
//   at line 3:1
```

### 传入自定义指令和角色

```ts
import { mystParse, createDirectives, createRoles } from 'myst-parser';
import { VFile } from 'vfile';
import type { DirectiveSpec, RoleSpec } from 'myst-common';

// 自定义指令
const colorDirective: DirectiveSpec = {
  name: 'color',
  arg: { type: 'string', required: true, doc: 'The color name' },
  body: { type: 'myst', doc: 'The colored content' },
  run(data, vfile, ctx) {
    const color = data.arg as string;
    const body = data.body as any;  // GenericParent（因为 type:'myst' 自动解析）
    return [{
      type: 'colorBlock',
      color,
      children: body.children,
    }];
  },
};

// 自定义角色
const highlightRole: RoleSpec = {
  name: 'highlight',
  body: { type: 'parsed' },
  run(data, vfile) {
    return [{
      type: 'highlight',
      children: data.body as any[],
    }];
  },
};

const content = `# Custom Extensions

\`\`\`{color} red
This text is **red** and contains {highlight}`highlighted text`{highlight}.
\`\`\`
`;

const vfile = new VFile();
const mdast = mystParse(content, {
  vfile,
  directives: [colorDirective],
  roles: [highlightRole],
});

console.log(JSON.stringify(mdast.children[1], null, 2));
// {
//   "type": "colorBlock",
//   "color": "red",
//   "children": [
//     {
//       "type": "paragraph",
//       "children": [
//         { "type": "text", "value": "This text is " },
//         { "type": "strong", "children": [{ "type": "text", "value": "red" }] },
//         { "type": "text", "value": " and contains " },
//         { "type": "highlight", "children": [{ "type": "text", "value": "highlighted text" }] },
//         { "type": "text", "value": "." }
//       ]
//     }
//   ]
// }
```

### 遍历 MDAST 树

```ts
import { mystParse } from 'myst-parser';
import { selectAll } from 'unist-util-select';
import type { GenericNode } from 'myst-common';

const content = `# Title

## Section 1
Text in section 1 with a [link](https://example.com).

\`\`\`{figure} image.png
Figure caption with **bold**.
\`\`\`

## Section 2
Some math: $\\alpha + \\beta$.
`;

const mdast = mystParse(content);

// 使用 unist-util-select 查询节点
const headings = selectAll('heading', mdast) as GenericNode[];
console.log('Headings:', headings.map(h => {
  // toText 工具将子节点树转为文本
  const text = h.children?.map((c: any) => c.value || '').join('');
  return `H${(h as any).depth} ${text}`;
}));
// → Headings: ['H1 Title', 'H2 Section 1', 'H2 Section 2']

const links = selectAll('link', mdast) as GenericNode[];
console.log('Links:', links.map(l => (l as any).url));
// → Links: ['https://example.com']

const mathNodes = selectAll('inlineMath', mdast) as GenericNode[];
console.log('Math:', mathNodes.map(m => (m as any).value));
// → Math: ['\\alpha + \\beta']
```

### 使用 markdown-it 扩展

```ts
import { mystParse } from 'myst-parser';
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';

const content = `# Emoji Test :smile:

Hello :wave:!
`;

// markdown-it 插件通过 extensions 选项传入
const mdast = mystParse(content, {
  extensions: [emoji],
  markdownit: { linkify: true },
});

// emoji 插件将 :smile: 渲染为内容
```

### 禁用 HTML

```ts
import { mystParse } from 'myst-parser';

const contentWithHtml = `# Test

<div>This is raw HTML</div>
`;

// 默认 html: false — HTML 被转义或拒绝
const mdastDefault = mystParse(contentWithHtml);
// HTML 节点不会出现在输出中，或被转为 text

// 允许 HTML
const mdastWithHtml = mystParse(contentWithHtml, { html: true });
// html 类型节点出现在 AST 中
```

## 预期输出

### 简单解析的 AST 结构

```json
{
  "type": "root",
  "children": [
    {
      "type": "heading",
      "depth": 1,
      "children": [{ "type": "text", "value": "Hello MyST" }]
    },
    {
      "type": "paragraph",
      "children": [
        { "type": "text", "value": "This is " },
        { "type": "strong", "children": [{ "type": "text", "value": "bold" }] },
        { "type": "text", "value": " and " },
        { "type": "emphasis", "children": [{ "type": "text", "value": "italic" }] },
        { "type": "text", "value": " text with " },
        { "type": "inlineMath", "value": "e=mc^2" },
        { "type": "text", "value": "." }
      ]
    }
  ]
}
```

## 关键点

1. **mystParse 返回 GenericParent（root 节点）**，不是统一的 Processor 实例
2. **VFile 用于错误收集**：传入已有 VFile 实例可在后续阶段继续使用消息
3. **指令/角色在 mystParse 内部完成后处理**：返回的 AST 中 mystDirective/mystRole 节点已被具体节点替换（但未被 lift，需要 basicTransformations 提升）
4. **builtin directives/roles 自动包含**：不需要手动注册 note/figure/table/math 等内置指令
5. **位置信息默认记录**：每个节点有 position.start/end 记录行号列号

## 下一步

- 解析后的 MDAST 需要通过 [basicTransformations](/concepts/03-myst-transforms.md) 处理才能得到最终语义
- 自定义指令的完整示例见 [自定义指令](/examples/05-custom-directive.md)
- 自定义角色的完整示例见 [自定义角色](/examples/04-custom-role.md)
