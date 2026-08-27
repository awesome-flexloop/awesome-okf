---
type: Concept
title: 数学公式渲染：KaTeX vs MathJax2
description: jupyter-renderers 提供两种 LaTeX 数学公式排版引擎——KaTeX（快速本地渲染）和 MathJax2（CDN加载+完整LaTeX支持），通过 ILatexTypesetter 接口集成到 JupyterLab，两者互斥
tags: [katex, mathjax, latex, math, typesetter, ilatextypesetter]
sources:
  - id: katex-index
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/index.ts
    title: katex-extension/src/index.ts
  - id: katex-autorender
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/autorender.ts
    title: katex-extension/src/autorender.ts
  - id: katex-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/package.json
    title: katex-extension/package.json
  - id: mathjax2-index
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/index.ts
    title: mathjax2-extension/src/index.ts
  - id: mathjax2-typesetter
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/typesetter.ts
    title: mathjax2-extension/src/typesetter.ts
  - id: mathjax2-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/package.json
    title: mathjax2-extension/package.json
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# 数学公式渲染：KaTeX vs MathJax2

jupyter-renderers 包含两个数学公式排版扩展：KaTeX 和 MathJax2。它们不是 MIME 文件渲染器，而是提供 `ILatexTypesetter` 服务的应用扩展，负责渲染 Notebook 和 Markdown 中的 LaTeX 数学公式。

## 两种排版引擎对比

| 特性 | KaTeX | MathJax2 |
|------|-------|----------|
| npm 包名 | @jupyterlab/katex-extension | @jupyterlab/mathjax2-extension |
| 版本 | 3.4.0 | 4.0.0 |
| 扩展类型 | extension（应用扩展） | extension（应用扩展） |
| 渲染引擎 | KaTeX（打包到扩展） | MathJax 2（CDN 动态加载） |
| 加载方式 | npm 依赖，随扩展打包 | 运行时动态注入 `<script>` |
| 渲染速度 | 快（本地同步渲染） | 慢（需加载 CDN 资源） |
| LaTeX 支持 | 常用命令，部分高级命令不支持 | 完整 LaTeX 数学模式 |
| 用户宏配置 | 支持（通过 Settings） | 不支持 |
| 配置来源 | ISettingRegistry | PageConfig（URL参数） |
| 异步处理 | 同步 | PromiseDelegate 等待加载 |
| 离线可用 | ✅ | ❌（需要 CDN 访问） |
| 安装大小 | 较大（KaTeX 打包） | 较小（仅加载逻辑） |
| 互斥 | 禁用 MathJax/MathJax2 | 被 KaTeX 禁用 |

## ILatexTypesetter 接口

两个排版器都实现同一个接口：

```typescript
interface ILatexTypesetter {
  typeset(node: HTMLElement): void;
}
```

JupyterLab 在渲染 Markdown 单元格、输出区域等包含数学公式的 DOM 节点时，调用 `typeset(node)` 对节点内的数学内容进行排版。

## KaTeX 实现

### KatexTypesetter 类

KaTeX 排版器极其简洁：[^katex-index]

```typescript
export class KatexTypesetter implements IRenderMime.ILatexTypesetter {
  typeset(node: HTMLElement): void {
    renderMathInElement(node, options);
  }
}
```

核心工作委托给 `autorender.ts` 中的 `renderMathInElement` 函数。

### 自动渲染算法

autorender.ts 实现了数学公式的自动发现和渲染，核心流程：[^katex-autorender]

1. **DOM 遍历**（`renderElem`）：递归遍历 DOM 树
   - 文本节点（nodeType === 3）：调用 `renderMathInText` 处理
   - 元素节点（nodeType === 1）：检查标签是否在忽略列表中，不在则递归处理
   - 忽略标签：`script`, `noscript`, `style`, `textarea`, `pre`, `code`

2. **文本分割**（`splitWithDelimiters` + `splitAtDelimiters`）：
   - 按分隔符将文本分割为 text 段和 math 段
   - 支持嵌套大括号计数（`braceLevel`），正确处理 `\frac{a}{b}` 等包含大括号的公式
   - 支持转义符 `\` 跳过后续分隔符

3. **KaTeX 渲染**：
   - 对 math 段调用 `katex.render(math, span, options)` 渲染
   - 渲染失败时 catch 错误，显示原始文本（`throwOnError: false`）
   - 错误文本显示为红色（`errorColor: '#CC0000'`）

### 支持的分隔符

| 分隔符 | 显示模式 | 说明 |
|--------|---------|------|
| `$...$` | inline | 行内公式（默认） |
| `\(...\)` | inline | 行内公式（LaTeX 风格） |
| `$$...$$` | display | 块级展示公式 |
| `\[...\]` | display | 块级展示公式（LaTeX 风格） |
| `\begin{equation}...\end{equation}` | display | LaTeX equation 环境 |

### 宏配置系统

KaTeX 扩展通过 JupyterLab 的设置系统（ISettingRegistry）支持用户自定义宏：

```typescript
const katexPlugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: '@jupyterlab/katex-extension:plugin',
  requires: [ISettingRegistry],
  provides: ILatexTypesetter,
  activate: (app, settingRegistry) => {
    function updateSettings(settings) {
      options.macros = settings.get('macros').composite as IMacros;
    }
    settingRegistry.load(katexPluginId).then(settings => {
      settings.changed.connect(updateSettings);  // 设置变更时自动更新
      updateSettings(settings);
    });
    return new KatexTypesetter();
  },
  autoStart: true
};
```

用户可以在 JupyterLab Settings 面板中定义 LaTeX 宏，例如：

```json
{
  "macros": {
    "\\RR": "\\mathbb{R}",
    "\\vec": "\\mathbf{#1}"
  }
}
```

配置变更通过 `settings.changed` 信号实时生效，无需刷新。

### KaTeX 插件激活依赖

```typescript
requires: [ISettingRegistry]    // 必须：设置注册表
provides: ILatexTypesetter       // 提供：LaTeX 排版服务
autoStart: true                  // 自动启动
```

## MathJax2 实现

### MathJaxTypesetter 类

MathJax2 排版器处理了异步加载的复杂性：[^mathjax2-typesetter]

```typescript
export class MathJaxTypesetter implements IRenderMime.ILatexTypesetter {
  constructor(options: MathJaxTypesetter.IOptions) {
    this._url = options.url;       // MathJax CDN URL
    this._config = options.config; // MathJax 配置名
  }

  typeset(node: HTMLElement): void {
    if (!this._initialized) {
      this._init();                // 首次调用时加载 MathJax
    }
    void this._initPromise.promise.then(() => {
      // MathJax 加载完成后排版
      MathJax.Hub.Queue(['Typeset', MathJax.Hub, node]);
      MathJax.Hub.Queue(
        ['Require', MathJax.Ajax, '[MathJax]/extensions/TeX/AMSmath.js'],
        () => {
          MathJax.InputJax.TeX.resetEquationNumbers();  // 重置公式编号
        }
      );
    });
  }
}
```

### 异步初始化机制

MathJax2 使用 `PromiseDelegate` 处理异步加载：

1. **首次 typeset 调用**：`_initialized = false` → 调用 `_init()`
2. **动态脚本注入**：创建 `<script>` 标签，src 指向 CDN URL（`?config=TeX-AMS-MML_HTMLorMML&delayStartupUntil=configured`）
3. **加载完成回调**：script 的 load 事件触发 `_onLoad()`
4. **MathJax 配置**：`_onLoad()` 中配置 MathJax Hub，调用 `MathJax.Hub.Configured()` 完成初始化
5. **Promise 解析**：`_initPromise.resolve()` 通知等待的 typeset 调用
6. **后续 typeset 调用**：`_initialized = true`，直接通过 `_initPromise.promise` 排队

### MathJax Hub 配置

```typescript
private _onLoad(): void {
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      processEnvironments: true
    },
    displayAlign: 'center',
    CommonHTML: { linebreaks: { automatic: true } },
    'HTML-CSS': {
      availableFonts: [],
      imageFont: null,
      preferredFont: null,
      webFont: 'STIX-Web',
      styles: { '.MathJax_Display': { margin: 0 } },
      linebreaks: { automatic: true }
    },
    skipStartupTypeset: true,      // 跳过初始自动排版（JupyterLab 控制）
    messageStyle: 'none'           // 不显示加载消息
  });

  // 删除导致 Chromium 性能问题的 hover 样式
  MathJax.Hub.Register.StartupHook('End Config', () => {
    delete MathJax.Hub?.config?.MathEvents?.styles['.MathJax_Hover_Arrow:hover span'];
    delete MathJax.Hub?.config?.MathMenu?.styles['.MathJax_MenuClose:hover span'];
  });

  MathJax.Hub.Configured();
  this._initPromise.resolve(void 0);
}
```

**性能优化**：删除了 Chromium 浏览器中导致性能问题的 `:hover span` 样式（参见 [jupyterlab/jupyterlab#9757](https://github.com/jupyterlab/jupyterlab/issues/9757)）。

### URL 和配置来源

MathJax2 的 CDN URL 和配置名从 JupyterLab 的 PageConfig 中读取：[^mathjax2-index]

```typescript
const [urlParam, configParam] = ['fullMathjaxUrl', 'mathjaxConfig'];
const url = PageConfig.getOption(urlParam);      // 如 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js'
const config = PageConfig.getOption(configParam); // 如 'TeX-AMS-MML_HTMLorMML'

if (!url) {
  throw new Error(`${plugin.id} requires 'fullMathjaxUrl' in PageConfig`);
}
```

PageConfig 中的参数通常由 JupyterLab 服务器端配置，用户可通过命令行参数 `--MathjaxUrl` 和 `--MathjaxConfig` 指定。

### MathJax2 插件激活依赖

```typescript
optional: [ITranslator]    // 可选：翻译器（为错误消息提供国际化）
provides: ILatexTypesetter
autoStart: true
```

注意 `ITranslator` 是 `optional`——如果翻译服务不可用，使用 `nullTranslator`。

## 互斥机制

KaTeX 扩展在 package.json 中声明了禁用列表：[^katex-pkg]

```json
"disabledExtensions": [
  "@jupyterlab/mathjax-extension:plugin",
  "@jupyterlab/mathjax2-extension:plugin"
]
```

启用 KaTeX 时，JupyterLab 自动禁用内置的 MathJax 扩展和 MathJax2 扩展，确保同一时间只有一个排版器生效。用户可在 JupyterLab Extension Manager 中启用/禁用扩展来切换排版引擎。

## 使用建议

1. **默认使用 KaTeX**：渲染速度快、离线可用、支持用户宏配置
2. **需要复杂 LaTeX 时切换 MathJax2**：如使用 `\usepackage`、TikZ、高级化学公式等
3. **MathJax2 需要网络**：确保服务器可访问 CDN，或在 PageConfig 中配置本地 MathJax 路径
4. **公式编号**：MathJax2 自动加载 AMSmath 扩展并重置公式编号；KaTeX 不支持自动编号

## 相关概念

- [扩展类型：MIME 渲染器 vs 应用扩展](03-extension-types.md)
- [MIME 渲染器开发模式](02-mime-renderer-pattern.md)
- [自定义数学公式排版器](../examples/02-custom-latex-typesetter.md)
- [IRenderMime 核心 API 参考](../references/rendermime-interfaces-api.md)

[^katex-autorender]: katex-extension/src/autorender.ts
[^katex-index]: katex-extension/src/index.ts
[^katex-pkg]: katex-extension/package.json
[^mathjax2-index]: mathjax2-extension/src/index.ts
[^mathjax2-typesetter]: mathjax2-extension/src/typesetter.ts
