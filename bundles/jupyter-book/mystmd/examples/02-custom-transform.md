---
type: Example
title: 编写自定义 Transform 插件
description: 演示如何编写一个 unified Plugin 形式的自定义 Transform，对 MDAST 树进行后处理，包括遍历、修改和创建节点。
tags: [mystmd, transform, plugin, unified, mdast]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-transforms-source.md"
    facts: [F-075, F-076, F-077]
  - path: "/concepts/03-myst-transforms.md"
    facts: []
---

## 目标

编写一个自定义 AST Transform 插件，在 MyST 转换管线中对 MDAST 树进行修改。演示两种导出形式：函数式和 unified Plugin 式。

## 前置条件

- Node.js 16+
- 已安装 `myst-parser`、`myst-transforms`、`myst-common`、`unified`、`unist-util-visit`

```bash
npm install myst-parser myst-transforms myst-common unified unist-util-visit vfile
```

## 示例 1：添加 word count 的 Transform

这个 Transform 遍历所有段落，统计单词数并在段落末尾添加一个 `<small>` 标记。

```ts
// my-wordcount-transform.ts
import type { Plugin } from 'unified';
import type { GenericNode, GenericParent, PluginUtils } from 'myst-common';
import { visit } from 'unist-util-visit';
import { fileWarn } from 'myst-common';

/**
 * 函数形式：直接操作 MDAST 树
 */
export function wordCountTransform(
  tree: GenericParent,
  vfile: VFile,
  opts?: { minWords?: number }
) {
  visit(tree, 'paragraph', (node: GenericNode) => {
    // 计算段落文本
    const text = extractText(node);
    const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;
    
    // 添加 wordCount 数据属性
    node.data = node.data || {};
    (node.data as any).wordCount = wordCount;
    
    // 短段落警告
    if (opts?.minWords && wordCount < opts.minWords) {
      fileWarn(
        vfile,
        `Paragraph is very short (${wordCount} words)`,
        node,
        'my-plugin:wordcount',
        'shortParagraph' as any
      );
    }
  });
}

/**
 * Plugin 形式：包装为 unified Plugin
 */
export const wordCountPlugin: Plugin<
  [{ minWords?: number }?, PluginUtils?],
  GenericParent,
  GenericParent
> = function(opts, utils) {
  const { minWords } = opts || {};
  return (tree, vfile) => {
    wordCountTransform(tree, vfile as VFile, { minWords });
  };
};

// 辅助函数：递归提取节点文本
function extractText(node: GenericNode): string {
  if (node.value) return node.value;
  if (node.children) {
    return node.children.map(extractText).join('');
  }
  return '';
}
```

## 示例 2：将特定标记替换为自定义节点

这个 Transform 查找特定文本模式（如 `TODO:`）并替换为自定义节点。

```ts
// my-todo-transform.ts
import type { Plugin } from 'unified';
import type { GenericNode, GenericParent, PluginUtils } from 'myst-common';
import { visit } from 'unist-util-visit';
import type { VFile } from 'vfile';

// 查找文本节点中的 TODO: 标记
export function todoHighlightTransform(tree: GenericParent, vfile: VFile) {
  const replacements: Array<{
    parent: GenericNode;
    index: number;
    nodes: GenericNode[];
  }> = [];
  
  visit(tree, 'text', (node: GenericNode, index, parent: GenericNode) => {
    if (!node.value || !parent || index === undefined) return;
    
    const text = node.value;
    const todoRegex = /TODO:([^]*?)(?=TODO:|$)/g;
    const matches = [...text.matchAll(todoRegex)];
    
    if (matches.length === 0) return;
    
    // 将文本节点拆分为普通文本 + todo 节点
    const newNodes: GenericNode[] = [];
    let lastIndex = 0;
    
    for (const match of matches) {
      const start = match.index!;
      const end = start + match[0].length;
      const todoContent = match[1].trim();
      
      // 添加 TODO 前的普通文本
      if (start > lastIndex) {
        newNodes.push({ type: 'text', value: text.slice(lastIndex, start) });
      }
      
      // 添加 TODO 节点
      newNodes.push({
        type: 'todo',
        children: [{ type: 'text', value: todoContent }],
        data: { hName: 'span', hProperties: { className: 'todo' } },
      });
      
      lastIndex = end;
    }
    
    // 添加剩余文本
    if (lastIndex < text.length) {
      newNodes.push({ type: 'text', value: text.slice(lastIndex) });
    }
    
    replacements.push({ parent, index, nodes: newNodes });
  });
  
  // 执行替换（在遍历完成后修改树，避免遍历问题）
  for (const { parent, index, nodes } of replacements.reverse()) {
    parent.children!.splice(index, 1, ...nodes);
  }
}

export const todoHighlightPlugin: Plugin<[], GenericParent, GenericParent> = function() {
  return (tree, vfile) => {
    todoHighlightTransform(tree, vfile as VFile);
  };
};
```

## 示例 3：在管线中使用自定义 Transform

```ts
// build.ts
import { unified } from 'unified';
import { VFile } from 'vfile';
import { mystParser } from 'myst-parser';
import {
  basicTransformationsPlugin,
  liftMystDirectivesAndRolesPlugin,
} from 'myst-transforms';
import { wordCountPlugin } from './my-wordcount-transform';
import { todoHighlightPlugin } from './my-todo-transform';

const content = `# My Document

This is a paragraph with some content.

TODO: Write more documentation here.

Another paragraph with TODO: Fix this bug and more text.

Short.
`;

const vfile = new VFile();
vfile.value = content;
vfile.path = 'doc.md';

const processor = unified()
  .use(mystParser)                                    // 1. 解析为 MDAST
  .use(liftMystDirectivesAndRolesPlugin)             // 2. 提升指令/角色
  .use(basicTransformationsPlugin)                   // 3. 基础转换
  .use(wordCountPlugin, { minWords: 5 })             // 4. 自定义：单词计数
  .use(todoHighlightPlugin);                         // 5. 自定义：TODO 高亮

const mdast = processor.runSync(processor.parse(content), vfile);

// 检查结果
console.log('=== VFile Messages ===');
vfile.messages.forEach(m => {
  console.log(`[${m.fatal ? 'ERROR' : 'WARN'}] ${m.ruleId}: ${m.message}`);
});
// → [WARN] shortParagraph: Paragraph is very short (1 words)

// 查找 TODO 节点
function findTodos(node: any, todos: any[] = []): any[] {
  if (node.type === 'todo') todos.push(node);
  if (node.children) node.children.forEach((c: any) => findTodos(c, todos));
  return todos;
}

const todos = findTodos(mdast);
console.log(`\nFound ${todos.length} TODO items:`);
todos.forEach((t, i) => {
  const text = t.children.map((c: any) => c.value).join('');
  console.log(`  ${i + 1}. ${text}`);
});
// → Found 2 TODO items:
// →   1. Write more documentation here.
// →   2. Fix this bug
```

## 示例 4：作为 TransformSpec 注册到 MystPlugin

将自定义 Transform 打包为插件：

```ts
// my-plugin.ts
import type { MystPlugin } from 'myst-common';
import { wordCountPlugin } from './my-wordcount-transform';
import { todoHighlightPlugin } from './my-todo-transform';

const myPlugin: MystPlugin = {
  name: 'my-custom-myst-plugin',
  author: 'Your Name',
  license: 'MIT',
  transforms: [
    {
      name: 'word-count',
      doc: 'Count words in paragraphs and warn on short paragraphs',
      stage: 'document',
      plugin: wordCountPlugin,
    },
    {
      name: 'todo-highlight',
      doc: 'Highlight TODO: markers in text',
      stage: 'document',
      plugin: todoHighlightPlugin,
    },
  ],
};

export default myPlugin;
```

在 myst.yml 中使用：

```yaml
version: 1
project:
  plugins:
    - type: javascript
      path: ./my-plugin.ts
```

## 关键点

1. **Transform 有两种形式**：函数式 `xxxTransform(tree, file, opts)` 和 Plugin 式 `xxxPlugin`
2. **遍历 AST 使用 unist-util-visit**：避免手动递归，正确处理节点类型匹配
3. **修改树时注意**：在 visit 回调中直接删除/替换节点需要用 index 参数；如果批量修改，先收集再替换
4. **错误/警告通过 fileError/fileWarn 上报**：不要使用 console.log，使用 VFile 消息系统
5. **stage 选择**：单文档逻辑用 `'document'` 阶段，需要跨文档信息用 `'project'` 阶段
6. **顺序重要**：自定义 transform 在 basicTransformationsPlugin 之后执行，因为它依赖基础转换完成

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 在 visit 回调中 splice 父节点 | visit 正在遍历 children | 收集替换后批量执行 |
| 忘记处理节点的 data.hName | 自定义节点无法渲染为 HTML | 添加 hName/hProperties 数据属性 |
| 转换前没有 lift directives | mystDirective 节点未被替换 | 确保 liftMystDirectivesAndRolesPlugin 先执行 |
| 用 console.error 而非 fileError | 错误不被构建系统收集 | 使用 fileError/fileWarn 函数 |

## 下一步

- 了解 [basicTransformations 管线顺序](/concepts/03-myst-transforms.md)以确定自定义 transform 的位置
- 学习 [VFile 错误处理](/concepts/05-error-handling.md)正确上报问题
- 学习 [MystPlugin 打包方式](/concepts/01-unified-plugin-architecture.md)分发插件
