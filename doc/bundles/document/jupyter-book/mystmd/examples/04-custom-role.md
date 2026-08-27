---
type: example
title: 编写自定义 Role（行内角色）
description: 演示如何创建自定义 MyST 角色（RoleSpec），包括参数/选项验证和返回 MDAST 节点，并在 mystParse 中注册使用。
tags: [mystmd, role, custom-role, inline, extension]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-common-source.md"
    facts: [F-048, F-049, F-050, F-051, F-052, F-053, F-055]
  - path: "/concepts/06-directives-and-roles.md"
    facts: []
---

## 目标

创建一个自定义 MyST 行内角色（Role），并将其注册到解析器中。演示从简单到复杂的多个角色示例。

## 前置条件

- Node.js 16+
- 已安装 `myst-parser`、`myst-common`、`vfile`

```bash
npm install myst-parser myst-common vfile
```

## 角色基础回顾

RoleSpec 结构：

```ts
type RoleSpec = {
  name: string;                    // 角色名
  alias?: string[];                // 别名
  doc?: string;                    // 文档
  options?: Record<string, OptionDefinition>;  // 选项定义
  body?: BodyDefinition;           // 内容体定义
  validate?: (data, vfile) => data;
  run: (data, vfile) => GenericNode[];
};
```

与 DirectiveSpec 的关键区别：
- 无 `arg` 字段（行内角色只有 body）
- `run` 方法无 `ctx` 参数（不能直接递归解析 MyST）
- body 解析：type 可以是 `string`/`number`/`boolean`/`parsed`，**不能是** `'myst'`

## 示例 1：最简角色 — 缩写（abbr）

最简单的角色：接收文本 body，返回一个带有 title 属性的节点。

```ts
// abbr-role.ts
import type { RoleSpec } from 'myst-common';

const abbrRole: RoleSpec = {
  name: 'abbr',
  body: {
    type: 'string',
    required: true,
    doc: 'Abbreviation text followed by (title)',
  },
  run(data) {
    const body = data.body as string;
    // body 格式: "HTML (HyperText Markup Language)"
    const match = body.match(/^(.+?)\s*\((.+)\)$/);
    
    let text: string, title: string;
    if (match) {
      text = match[1].trim();
      title = match[2].trim();
    } else {
      text = body;
      title = body;
    }
    
    return [{
      type: 'abbr',
      children: [{ type: 'text', value: text }],
      data: {
        hName: 'abbr',
        hProperties: { title },
      },
    }];
  },
};

export default abbrRole;
```

使用方式：
```markdown
The web uses {abbr}`HTML (HyperText Markup Language)` and {abbr}`CSS (Cascading Style Sheets)`.
```

## 示例 2：带选项的角色 — 彩色文本

```ts
// color-role.ts
import type { RoleSpec } from 'myst-common';
import { fileError } from 'myst-common';

const colorRole: RoleSpec = {
  name: 'color',
  alias: ['col'],
  body: {
    type: 'parsed',  // 解析为内联 MDAST 节点
    required: true,
  },
  options: {
    // :class: 选项 — CSS 类名
    class: {
      type: 'string',
      doc: 'CSS class name',
    },
  },
  run(data, vfile) {
    const body = data.body;  // GenericNode[]（因为 type: 'parsed'）
    
    // 选项值
    const className = (data.options?.class as string) || 'color-default';
    
    return [{
      type: 'span',
      children: body as any[],
      data: {
        hName: 'span',
        hProperties: {
          className: [className],
        },
      },
    }];
  },
};

export default colorRole;
```

使用方式：
```markdown
This is {color}`red text` with default styling.
This is {color}`:class: warning  bold warning text`{color}.
```

## 示例 3：带验证的角色 — 键盘按键（kbd）

```ts
// kbd-role.ts
import type { RoleSpec, RoleData } from 'myst-common';
import { fileError } from 'myst-common';
import type { VFile } from 'vfile';

const kbdRole: RoleSpec = {
  name: 'kbd',
  body: {
    type: 'string',
    required: true,
  },
  validate(data: RoleData, vfile: VFile): RoleData {
    const body = data.body as string;
    
    // 验证：kbd 内容不能包含特殊字符组合
    if (/[<>]/.test(body)) {
      fileError(
        vfile,
        'kbd role content cannot contain < or > characters',
        data.node,
        'my-plugin:kbd',
        'invalidKbd' as any
      );
    }
    
    return data;
  },
  run(data) {
    const body = data.body as string;
    
    // 支持按键组合：Ctrl+K → 多个 <kbd> 元素
    const keys = body.split('+').map(k => k.trim());
    
    const children = keys.map((key, i) => {
      const kbdNode = {
        type: 'kbd',
        children: [{ type: 'text', value: key }],
        data: {
          hName: 'kbd',
        },
      };
      
      // 在按键之间添加 "+" 分隔
      if (i > 0) {
        return [
          { type: 'text', value: '+' },
          kbdNode,
        ];
      }
      return [kbdNode];
    }).flat();
    
    return [{
      type: 'kbdGroup',
      children,
      data: { hName: 'span', hProperties: { className: ['kbd-group'] } },
    }];
  },
};

export default kbdRole;
```

使用方式：
```markdown
Press {kbd}`Ctrl+Shift+P` to open the command palette.
Use {kbd}`Enter` to confirm.
```

## 示例 4：布尔选项 — 标记角色

```ts
// mark-role.ts
import type { RoleSpec } from 'myst-common';

const markRole: RoleSpec = {
  name: 'mark',
  body: { type: 'parsed', required: true },
  options: {
    // 布尔选项：:bold: 或 :bold: true
    bold: { type: Boolean },
    // 字符串选项：:color: yellow
    color: { type: 'string' },
  },
  run(data) {
    const body = data.body as any[];
    const isBold = data.options?.bold === true;
    const color = data.options?.color as string;
    
    const properties: Record<string, any> = {
      className: ['highlight'],
    };
    if (color) properties.style = `background-color: ${color}`;
    
    const innerNodes: any[] = isBold
      ? [{ type: 'strong', children: body }]
      : body;
    
    return [{
      type: 'mark',
      children: innerNodes,
      data: { hName: 'mark', hProperties: properties },
    }];
  },
};

export default markRole;
```

使用方式：
```markdown
This is {mark}`:bold: very important`{mark} text.
This is {mark}`:color: yellow  highlighted`{mark} text.
```

## 示例 5：在 mystParse 中注册和使用

```ts
// test-roles.ts
import { mystParse } from 'myst-parser';
import { VFile } from 'vfile';
import { selectAll } from 'unist-util-select';
import abbrRole from './abbr-role';
import colorRole from './color-role';
import kbdRole from './kbd-role';
import markRole from './mark-role';

const content = `# Test Custom Roles

The web uses {abbr}`HTML (HyperText Markup Language)`{abbr} standards.

Press {kbd}`Ctrl+C`{kbd} to copy, then {kbd}`Ctrl+V`{kbd} to paste.

This is {mark}`:bold: critical`{mark} information.
`;

const vfile = new VFile();
vfile.path = 'test.md';

const mdast = mystParse(content, {
  vfile,
  roles: [abbrRole, colorRole, kbdRole, markRole],
});

// 检查自定义节点
const abbrs = selectAll('abbr', mdast);
console.log(`Found ${abbrs.length} abbr nodes`);

const kbds = selectAll('kbd', mdast);
console.log(`Found ${kbds.length} kbd nodes`);

const marks = selectAll('mark', mdast);
console.log(`Found ${marks.length} mark nodes`);

// 检查 VFile 错误
if (vfile.messages.length > 0) {
  console.log('\nWarnings/Errors:');
  vfile.messages.forEach(m => {
    console.log(`  [${m.fatal ? 'ERROR' : 'WARN'}] line ${m.line}: ${m.message}`);
  });
}
```

## 示例 6：打包为 MystPlugin

将多个角色打包为可分发插件：

```ts
// my-roles-plugin.ts
import type { MystPlugin } from 'myst-common';
import abbrRole from './abbr-role';
import colorRole from './color-role';
import kbdRole from './kbd-role';
import markRole from './mark-role';

const myRolesPlugin: MystPlugin = {
  name: 'my-custom-roles',
  author: 'Your Name',
  license: 'MIT',
  roles: [abbrRole, colorRole, kbdRole, markRole],
  directives: [],  // 无指令
  transforms: [],  // 无转换
};

export default myRolesPlugin;
```

在 myst.yml 中注册：
```yaml
project:
  plugins:
    - type: javascript
      path: ./my-roles-plugin.ts
```

## RoleSpec body type 说明

| type | data.body 类型 | 说明 |
|------|---------------|------|
| `'string'` | `string` | 原始文本字符串 |
| `'number'` | `number` | 自动转为数字 |
| `'boolean'` | `boolean` | 布尔值 |
| `'parsed'` | `GenericNode[]` | 解析为行内 MDAST 节点（支持粗体/斜体/行内代码等） |

> 注意：Role 的 body 不支持 `'myst'` 类型（角色是行内元素，不能递归解析块级 MyST）。如果需要在角色中嵌入复杂内容，应使用指令。

## 关键点

1. **RoleSpec 比 DirectiveSpec 简单**：无 arg、无 ctx，仅 body + options
2. **body type 选择**：纯文本用 `'string'`，需要格式化（粗体等）用 `'parsed'`
3. **返回 GenericNode[]**：可以返回多个节点（如 kbd 组合键返回多个 kbd+文本节点）
4. **HTML 渲染通过 data.hName/hProperties**：指定 HTML 标签和属性
5. **验证在 validate 中做**：错误通过 fileError 上报
6. **alias 支持多个别名**：同一角色可通过多个名称调用

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `unknownRole` 错误 | 角色未注册到 mystParse 的 roles 选项 | 将 RoleSpec 添加到 roles 数组 |
| body 是 string 而非节点数组 | body.type 设置为 'string' 而非 'parsed' | 将 body.type 改为 'parsed' |
| 选项值始终为 undefined | 选项语法错误或未定义 OptionDefinition | 检查选项定义和选项语法（`:key: value`） |
| 自定义节点在 HTML 中渲染为空 | 缺少 data.hName | 添加 data.hName 和 data.hProperties |

## 下一步

- 学习 [自定义指令](05-custom-directive.md) 创建块级扩展
- 了解 [统一插件架构](../concepts/01-unified-plugin-architecture.md) 中 MystPlugin 的完整结构
- 学习 [基本解析示例](00-basic-parsing.md) 了解 mystParse 的完整用法
