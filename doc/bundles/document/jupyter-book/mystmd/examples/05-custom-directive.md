---
type: example
title: 编写自定义 Directive（块级指令）
description: 演示如何创建自定义 MyST 指令（DirectiveSpec），包括参数、选项、内容体解析、递归 MyST 解析，以及在 mystParse 和 MystPlugin 中注册。
tags: [mystmd, directive, custom-directive, block, extension]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-common-source.md"
    facts: [F-047, F-049, F-050, F-051, F-052, F-053, F-054]
  - path: "/concepts/06-directives-and-roles.md"
    facts: []
---

## 目标

创建自定义 MyST 块级指令（Directive），从简单到复杂，覆盖参数、选项、内容体、递归解析等核心功能。

## 前置条件

- Node.js 16+
- 已安装 `myst-parser`、`myst-common`、`myst-directives`、`vfile`

```bash
npm install myst-parser myst-common myst-directives vfile unist-util-visit
```

## DirectiveSpec 结构回顾

```ts
type DirectiveSpec = {
  name: string;
  alias?: string[];
  doc?: string;
  arg?: ArgDefinition;       // 参数（指令名后的第一行文本）
  options?: Record<string, OptionDefinition>;  // :key: value 选项
  body?: BodyDefinition;     // 内容体（围栏内文本）
  validate?: (data, vfile) => data;
  run: (data, vfile, ctx) => GenericNode[];
};
```

指令的 `run` 方法接收 `ctx: DirectiveContext`，其中包含 `parseMyst(source)` 回调，可递归解析嵌套的 MyST 内容。

## 示例 1：最简指令 — 横幅提示（banner）

无参数、无选项、无 body 的简单指令。

```ts
// banner-directive.ts
import type { DirectiveSpec } from 'myst-common';

const bannerDirective: DirectiveSpec = {
  name: 'banner',
  run() {
    return [
      {
        type: 'banner',
        children: [
          {
            type: 'paragraph',
            children: [
              { type: 'text', value: '⚠️ ' },
              {
                type: 'strong',
                children: [{ type: 'text', value: '注意' }],
              },
              { type: 'text', value: '：这是一个重要提示横幅。' },
            ],
          },
        ],
        data: {
          hName: 'div',
          hProperties: {
            className: ['banner', 'banner-warning'],
          },
        },
      },
    ];
  },
};

export default bannerDirective;
```

使用方式：
````markdown
```{banner}
```
````

## 示例 2：带 body 的指令 — 提示框（callout）

body type 为 `'myst'`，支持嵌套 MyST 内容。

```ts
// callout-directive.ts
import type { DirectiveSpec } from 'myst-common';

const calloutDirective: DirectiveSpec = {
  name: 'callout',
  alias: ['note', 'tip', 'warning', 'danger', 'info'],
  arg: {
    type: String,  // 可选标题
    doc: 'Optional title for the callout',
  },
  options: {
    type: {
      type: String,
      doc: 'Callout type: note/tip/warning/danger/info',
    },
    icon: {
      type: Boolean,
      doc: 'Whether to show icon',
    },
  },
  body: {
    type: 'myst',  // 递归解析为 MyST MDAST
    required: true,
    doc: 'Callout body content (MyST Markdown)',
  },
  run(data, vfile, ctx) {
    // 确定类型：优先使用 :type: 选项，其次使用指令别名
    const type = (data.options?.type as string) || data.name || 'note';
    const title = data.arg as string;
    const body = data.body as any;  // GenericParent（因为 type:'myst'）
    const showIcon = data.options?.icon !== false;
    
    // 图标映射
    const icons: Record<string, string> = {
      note: 'ℹ️',
      tip: '💡',
      warning: '⚠️',
      danger: '🚫',
      info: 'ℹ️',
    };
    
    const children: any[] = [];
    
    // 添加标题（如果有 arg 或默认标题）
    const titleText = title || type.charAt(0).toUpperCase() + type.slice(1);
    children.push({
      type: 'calloutTitle',
      children: [
        ...(showIcon ? [{ type: 'text', value: `${icons[type] || ''} ` }] : []),
        { type: 'text', value: titleText },
      ],
      data: { hName: 'div', hProperties: { className: ['callout-title'] } },
    });
    
    // 添加 body（已递归解析为 MDAST 节点）
    children.push({
      type: 'calloutBody',
      children: body.children,
      data: { hName: 'div', hProperties: { className: ['callout-body'] } },
    });
    
    return [
      {
        type: 'callout',
        kind: type,
        children,
        data: {
          hName: 'div',
          hProperties: {
            className: ['callout', `callout-${type}`],
          },
        },
      },
    ];
  },
};

export default calloutDirective;
```

使用方式：
````markdown
```{warning} 小心！
:icon: true

这个操作**不可逆**，请确保已备份数据。

- 确认文件已保存
- 确认权限正确
```
````

## 示例 3：带参数和选项的指令 — 自定义图片（figurex）

```ts
// figurex-directive.ts
import type { DirectiveSpec, DirectiveData } from 'myst-common';
import { fileError } from 'myst-common';
import type { VFile } from 'vfile';

const figurexDirective: DirectiveSpec = {
  name: 'figurex',
  arg: {
    type: String,
    required: true,
    doc: 'Image URL/path (required)',
  },
  options: {
    width: {
      type: String,
      doc: 'Image width (CSS value, e.g. 80%, 300px)',
    },
    height: {
      type: String,
      doc: 'Image height',
    },
    alt: {
      type: String,
      doc: 'Alt text for accessibility',
    },
    align: {
      type: String,
      doc: 'Alignment: left/center/right',
    },
    caption: {
      type: 'parsed',  // 解析为内联节点
      doc: 'Figure caption (inline MyST)',
    },
    numbered: {
      type: Boolean,
      doc: 'Whether to number the figure',
    },
  },
  body: {
    type: 'parsed',
    doc: 'Optional body content (rendered as caption if no :caption: option)',
  },
  validate(data: DirectiveData, vfile: VFile): DirectiveData {
    const arg = data.arg as string;
    if (!arg.match(/^https?:\/\//) && !arg.match(/^[\w./-]+\.(png|jpg|jpeg|gif|svg|webp)$/i)) {
      fileError(
        vfile,
        `figurex arg must be a URL or image file path, got: ${arg}`,
        data.node,
        'my-plugin:figurex',
        'invalidFigurePath' as any
      );
    }
    
    const align = data.options?.align as string;
    if (align && !['left', 'center', 'right'].includes(align)) {
      fileError(
        vfile,
        `figurex align must be left, center, or right, got: ${align}`,
        data.node,
        'my-plugin:figurex',
        'invalidAlign' as any
      );
    }
    
    return data;
  },
  run(data, vfile, ctx) {
    const src = data.arg as string;
    const width = data.options?.width as string | undefined;
    const height = data.options?.height as string | undefined;
    const alt = (data.options?.alt as string) || '';
    const align = (data.options?.align as string) || 'center';
    const numbered = data.options?.numbered === true;
    const captionOption = data.options?.caption;
    const bodyContent = data.body;
    
    // 构建 image 节点
    const imageNode: any = {
      type: 'image',
      url: src,
      alt,
      data: {
        hProperties: {
          ...(width ? { width } : {}),
          ...(height ? { height } : {}),
        },
      },
    };
    
    // 确定 caption 来源
    let captionChildren: any[] | undefined;
    if (captionOption) {
      captionChildren = captionOption as any[];
    } else if (bodyContent) {
      captionChildren = bodyContent as any[];
    }
    
    const children: any[] = [imageNode];
    
    // 添加 caption
    if (captionChildren && captionChildren.length > 0) {
      children.push({
        type: 'caption',
        children: captionChildren,
      });
    }
    
    return [
      {
        type: 'container',
        kind: 'figure',
        align,
        numbered,
        children,
        data: {
          hName: 'figure',
          hProperties: {
            className: ['figure', `figure-align-${align}`],
          },
        },
      },
    ];
  },
};

export default figurexDirective;
```

使用方式：
````markdown
```{figurex} images/photo.jpg
:width: 80%
:alt: 一张美丽的风景照片
:align: center
:numbered: true

这张照片拍摄于**2024年**的春天。
```
````

## 示例 4：嵌套 MyST 解析 — 选项卡（tabs）

指令内部使用 `ctx.parseMyst()` 解析嵌套内容。

```ts
// tabs-directive.ts
import type { DirectiveSpec } from 'myst-common';

const tabDirective: DirectiveSpec = {
  name: 'tab',
  arg: {
    type: String,
    required: true,
    doc: 'Tab title',
  },
  body: {
    type: 'myst',
    required: true,
  },
  run(data, vfile, ctx) {
    const title = data.arg as string;
    const body = data.body as any;  // GenericParent
    
    return [
      {
        type: 'tabItem',
        title,
        children: body.children,
      },
    ];
  },
};

const tabSetDirective: DirectiveSpec = {
  name: 'tab-set',
  alias: ['tabs'],
  body: {
    type: 'myst',
    required: true,
  },
  run(data, vfile, ctx) {
    const body = data.body as any;
    
    // tab-set 的 body 包含多个 tab 子指令
    // 由于 body type 是 'myst'，tab 指令已被解析为 tabItem 节点
    return [
      {
        type: 'tabSet',
        children: body.children.filter((n: any) => n.type === 'tabItem'),
      },
    ];
  },
};

export { tabDirective, tabSetDirective };
```

使用方式：
````markdown
```{tab-set}

```{tab} JavaScript
\`\`\`js
console.log("Hello");
\`\`\`
```

```{tab} Python
\`\`\`python
print("Hello")
\`\`\`
```
```
````

## 示例 5：动态解析 — 代码片段嵌入

指令中使用 ctx.parseMyst 动态生成内容。

```ts
// snippet-directive.ts
import type { DirectiveSpec } from 'myst-common';
import { fileError } from 'myst-common';
import { readFileSync } from 'fs';
import { join } from 'path';

const snippetDirective: DirectiveSpec = {
  name: 'snippet',
  arg: {
    type: String,
    required: true,
    doc: 'File path to include',
  },
  options: {
    lang: {
      type: String,
      doc: 'Language for syntax highlighting',
    },
    lines: {
      type: String,
      doc: 'Line range, e.g. "5-15" or "1,3,5-10"',
    },
    start: {
      type: Number,
      doc: 'Starting line number for display',
    },
  },
  run(data, vfile, ctx) {
    const filePath = data.arg as string;
    const lang = (data.options?.lang as string) || detectLang(filePath);
    const lineRange = data.options?.lines as string | undefined;
    const startLine = (data.options?.start as number) || 1;
    
    // 读取文件（注意：实际实现应考虑相对路径和安全限制）
    let content: string;
    try {
      content = readFileSync(filePath, 'utf-8');
    } catch (err) {
      fileError(
        vfile,
        `Cannot read file: ${filePath}`,
        data.node,
        'my-plugin:snippet',
        'fileNotFound' as any
      );
      return [];
    }
    
    // 解析行范围
    if (lineRange) {
      content = filterLines(content, lineRange);
    }
    
    return [
      {
        type: 'code',
        lang,
        value: content,
        data: {
          hName: 'pre',
          hProperties: {
            className: ['snippet', `language-${lang}`],
            'data-line-start': startLine,
          },
        },
      },
    ];
  },
};

function detectLang(filePath: string): string {
  const ext = filePath.split('.').pop()?.toLowerCase();
  const map: Record<string, string> = {
    ts: 'typescript', js: 'javascript', py: 'python',
    rs: 'rust', go: 'go', md: 'markdown', json: 'json',
    yml: 'yaml', yaml: 'yaml', sh: 'bash', bash: 'bash',
  };
  return map[ext || ''] || 'text';
}

function filterLines(content: string, range: string): string {
  const lines = content.split('\n');
  const selected: string[] = [];
  const parts = range.split(',');
  for (const part of parts) {
    if (part.includes('-')) {
      const [start, end] = part.split('-').map(Number);
      for (let i = start - 1; i < Math.min(end, lines.length); i++) {
        selected.push(lines[i]);
      }
    } else {
      const lineNum = Number(part);
      if (lineNum >= 1 && lineNum <= lines.length) {
        selected.push(lines[lineNum - 1]);
      }
    }
  }
  return selected.join('\n');
}

export default snippetDirective;
```

使用方式：
````markdown
```{snippet} src/main.ts
:lang: typescript
:lines: 10-25
```
````

## 示例 6：在 mystParse 中注册和使用

````ts
// test-directives.ts
import { mystParse } from 'myst-parser';
import { VFile } from 'vfile';
import { selectAll } from 'unist-util-select';
import bannerDirective from './banner-directive';
import calloutDirective from './callout-directive';
import figurexDirective from './figurex-directive';
import { tabDirective, tabSetDirective } from './tabs-directive';
import snippetDirective from './snippet-directive';

const content = `# Custom Directive Test

```{banner}
```

```{note} 提示
:icon: true

这是一个**自定义**提示框。
```

```{figurex} https://example.com/photo.jpg
:width: 500px
:alt: Example photo
:align: center

Example photo with **bold caption**.
```
`;

const vfile = new VFile();
vfile.path = 'test.md';

const mdast = mystParse(content, {
  vfile,
  directives: [
    bannerDirective,
    calloutDirective,
    figurexDirective,
    tabDirective,
    tabSetDirective,
    snippetDirective,
  ],
});

// 注意：mystParse 返回的 AST 中指令节点仍然是 mystDirective 类型
// 需要 basicTransformations 来 lift 指令子节点
// 但此时 node.children 已经包含了 run() 返回的节点
const directives = selectAll('mystDirective', mdast);
console.log(`Found ${directives.length} directives:`);
directives.forEach((d: any) => {
  console.log(`  - {${d.name}}: ${d.children?.length || 0} children`);
});

// 检查错误
vfile.messages.forEach(m => {
  console.log(`[${m.fatal ? 'ERROR' : 'WARN'}] line ${m.line}: ${m.message}`);
});
````

## 示例 7：打包为 MystPlugin

```ts
// my-directives-plugin.ts
import type { MystPlugin } from 'myst-common';
import bannerDirective from './banner-directive';
import calloutDirective from './callout-directive';
import figurexDirective from './figurex-directive';
import { tabDirective, tabSetDirective } from './tabs-directive';
import snippetDirective from './snippet-directive';
import kbdRole from './kbd-role';  // 来自前一个示例
import { wordCountPlugin } from './my-wordcount-transform';

const myPlugin: MystPlugin = {
  name: 'my-myst-plugin',
  author: 'Your Name',
  license: 'MIT',
  directives: [
    bannerDirective,
    calloutDirective,
    figurexDirective,
    tabDirective,
    tabSetDirective,
    snippetDirective,
  ],
  roles: [kbdRole],
  transforms: [
    {
      name: 'word-count',
      stage: 'document',
      plugin: wordCountPlugin,
    },
  ],
};

export default myPlugin;
```

在 myst.yml 中使用：
```yaml
project:
  plugins:
    - type: javascript
      path: ./my-directives-plugin.ts
```

## Arg/Option/Body type 说明

| type | data 中类型 | 适用位置 | 说明 |
|------|-----------|---------|------|
| `String`/`'string'` | `string` | arg/options/body | 字符串值 |
| `Number`/`'number'` | `number` | arg/options/body | 自动转换为数字 |
| `Boolean`/`'boolean'` | `boolean` | options | true/false（选项仅需键名即为 true） |
| `'parsed'` | `GenericNode[]` | arg/options/body | 解析为行内 MDAST 节点 |
| `'myst'` | `GenericParent` | arg/body | 递归解析为完整 MyST 树（仅指令可用） |

## 关键点

1. **DirectiveSpec 有 arg，RoleSpec 没有**：arg 是指令名后第一行的文本
2. **ctx.parseMyst**：指令独有，用于递归解析嵌套 MyST 内容
3. **body type 'myst'**：自动调用 parseMyst 递归解析，data.body 直接是 GenericParent
4. **返回 GenericNode[]**：可以返回多个节点替换指令位置
5. **data.hName/hProperties**：控制 HTML 渲染输出
6. **alias 注册别名**：同一实现可通过多个名称调用
7. **验证在 validate 中**：错误通过 fileError 上报到 VFile
8. **mystParse 后需要 lift**：basicTransformations 中的 liftMystDirectivesAndRoles 将 children 提升

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `unknownDirective` | 指令未注册 | 添加到 mystParse 的 directives 数组 |
| children 是字符串而非节点 | body.type 设置错误 | 使用 `'myst'` 或 `'parsed'` |
| 选项值为 true 但未传值 | Boolean 选项只需 `:key:` 即 true | 这是正确行为，data.options.key === true |
| 嵌套指令未解析 | body 未用 `'myst'` 类型 | 将 body.type 设为 `'myst'` |
| run 中 ctx.parseMyst 报错 | 角色无 ctx | 角色不能递归解析，用指令替代 |

## 下一步

- 学习 [自定义角色](/examples/04-custom-role.md) 了解行内扩展
- 学习 [自定义 Transform](/examples/02-custom-transform.md) 进行 AST 后处理
- 了解 [指令与角色系统](/concepts/06-directives-and-roles.md)完整机制
- 了解 [MDAST 转换管线](/concepts/03-myst-transforms.md)中 lift 步骤的作用
