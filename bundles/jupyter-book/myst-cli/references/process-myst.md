---
type: reference
title: "myst-cli MyST解析处理源码"
description: "process/myst.ts 中的MyST Markdown解析、内置指令/角色注册与解析器选项配置"
tags: [myst-cli, process, parser, myst-parser, directives, roles]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/process/myst.ts"
    facts: [F-044, F-045, F-046]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/plugins.ts"
    facts: [F-055, F-056, F-057]
---

# MyST 解析处理源码分析

## parseMyst() 函数

`parseMyst()` 是 myst-cli 中将 Markdown 文本解析为 MDAST（Markdown Abstract Syntax Tree）的核心函数：

```ts
export function parseMyst(
  session: ISession,
  content: string,
  file: string,
  opts?: Options,
): GenericParent {
  const vfile = new VFile();
  vfile.path = file;
  const parserOptions = getMystParserOptions(session, opts);
  const parsed = mystParse(content, { ...parserOptions, vfile });
  logMessagesFromVFile(session, vfile);
  return parsed;
}
```

函数流程：
1. 创建 VFile（virtual file）并设置路径，用于收集解析消息
2. 通过 `getMystParserOptions()` 构建解析器选项
3. 调用 myst-parser 的 `mystParse()` 执行实际解析
4. 将 VFile 中的警告/错误消息输出到 session 日志
5. 返回 MDAST 树（`GenericParent` 类型）

## getMystParserOptions() 选项配置

```ts
export function getMystParserOptions(session: ISession, opts?: Options): Partial<AllOptions> {
  const parserOptions = selectCurrentProjectConfig(session.store.getState())?.settings?.parser;
  let mathExtension: boolean | { dollarmath?: boolean; amsmath?: boolean } = true;
  if (parserOptions?.dollarmath === false) {
    mathExtension = { dollarmath: false, amsmath: true };
  }

  return {
    markdownit: { linkify: true },
    directives: [
      cardDirective,           // myst-ext-card
      ...gridDirectives,       // myst-ext-grid: grid, grid-item
      proofDirective,          // myst-ext-proof
      ...exerciseDirectives,   // myst-ext-exercise: exercise, solution
      ...tabDirectives,        // myst-ext-tabs: tab-set, tab-item
      ...(session.plugins?.directives ?? []),  // 用户插件
    ],
    extensions: {
      frontmatter: !opts?.ignoreFrontmatter,
      math: mathExtension,
    },
    roles: [
      buttonRole,              // myst-ext-button
      ...(session.plugins?.roles ?? []),       // 用户插件
    ],
  };
}
```

### 内置指令（默认注册）

| 指令 | 来源包 | MDAST 节点类型 |
|------|--------|---------------|
| `card` / `grid-item-card` | myst-ext-card | `card` |
| `grid` | myst-ext-grid | `grid` |
| `grid-item` | myst-ext-grid | `grid-item` |
| `proof` / `prf:*` / `proof:*` | myst-ext-proof | `proof` |
| `exercise` | myst-ext-exercise | `exercise` |
| `solution` | myst-ext-exercise | `solution` |
| `tab-set` / `tabSet` | myst-ext-tabs | `tabSet` |
| `tab-item` / `tabItem` / `tab` | myst-ext-tabs | `tabItem` |

注意：myst-directives 包提供的核心指令（admonition、figure、code、math、table、embed、include、toc 等）是在 myst-parser 层面默认注册的，不在此处列表中。此处注册的是 myst-ext-* 扩展包提供的 UI 组件指令。

### 内置角色（默认注册）

| 角色 | 来源包 | MDAST 节点类型 |
|------|--------|---------------|
| `button` | myst-ext-button | `span`（无链接）或 `link`（有链接） |

myst-roles 包提供的核心角色（cite、ref、abbr、doc、math、term 等）同样在 myst-parser 层面默认注册。

### 扩展选项

- **markdownit.linkify**: 启用自动链接识别（URL 自动转为链接）
- **extensions.frontmatter**: 解析 YAML frontmatter（可通过 `ignoreFrontmatter` 选项禁用）
- **extensions.math**: 数学公式支持，默认启用 dollarmath（$...$）和 amsmath。可通过 `project.settings.parser.dollarmath: false` 禁用 $ 公式语法，仅保留 LaTeX 环境

## 插件加载（plugins.ts）

`loadPlugins()` 函数负责加载用户在 myst.yml 中声明的插件：

```ts
export async function loadPlugins(session, plugins: PluginInfo[]): Promise<ValidatedMystPlugin> {
  // 去重 + 过滤已加载
  const newPlugins = [...new Map(plugins.map(info => [info.path, info])).values()]
    .filter(({ path }) => !loadedPlugins.paths.includes(path));
  
  const modules = await Promise.all(
    newPlugins.map(async info => {
      switch (info.type) {
        case 'executable':
          // 可执行插件：验证文件可执行 → loadExecutablePlugin()
          return loadFromExecutable(info.path);
        case 'javascript':
          // JS 插件：验证 .mjs 文件 → 动态 import
          return import(pathToFileURL(path).toString());
      }
    })
  );
  // 从模块中提取 directives/roles/transforms 并注册
}
```

### 插件协议

| 类型 | 文件要求 | 加载方式 |
|------|----------|----------|
| `executable` | 可执行文件 | 通过 stdin/stdout 通信查询插件规范 |
| `javascript` | `.mjs` ES 模块 | `await import()` 动态加载 |

插件模块可导出：
- `default` 或 `plugin`：MystPlugin 对象（含 name、directives、roles、transforms）
- 直接导出 `directives`、`roles`、`transforms` 数组

## process 模块导出

process 模块重新导出6个子模块：
- `citations`：引用处理（BibTeX、DOI、Citation.js 集成）
- `file`：文件加载（.md/.ipynb/.bib/.myst.md 等格式）
- `loadReferences`：外部引用加载
- `mdast`：MDAST 工具函数
- `myst`：MyST 解析（parseMyst、getMystParserOptions）
- `notebook`：Jupyter Notebook 处理
- `site`：站点处理
