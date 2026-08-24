---
type: Concept
title: 扩展类型：MIME 渲染器 vs 应用扩展
description: JupyterLab 扩展的两种类型——mimeExtension（文件/MIME渲染）和 extension（应用服务），ILatexTypesetter 服务模式，以及 KaTeX/MathJax2 的互斥机制
tags: [extension-type, mime-extension, application-extension, ilatextypesetter, katex, mathjax]
sources:
  - id: katex-index
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/index.ts
    title: katex-extension/src/index.ts
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
  - id: katex-autorender
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/autorender.ts
    title: katex-extension/src/autorender.ts
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# 扩展类型：MIME 渲染器 vs 应用扩展

jupyter-renderers 包含两种不同类型的 JupyterLab 扩展，它们在 package.json 中通过不同的标记区分，遵循不同的注册协议和生命周期。

## 两种扩展类型对比

| 特性 | MIME 渲染器（mimeExtension） | 应用扩展（extension） |
|------|---------------------------|---------------------|
| package.json 标记 | `"mimeExtension": true` | `"extension": true` |
| 代表包 | fasta, geojson, vega3 | katex, mathjax2 |
| 核心接口 | `IRenderMime.IRenderer` | `JupyterFrontEndPlugin<T>` |
| 触发方式 | 打开对应 MIME 类型的文件/输出 | JupyterLab 启动时自动激活 |
| 提供内容 | 渲染工厂（rendererFactory） | 服务（Token） |
| 数据输入 | `IMimeModel.data` | 通过 Token 依赖注入获取 |
| 文件类型注册 | `fileTypes` + `documentWidgetFactoryOptions` | 无文件关联 |
| 输出形式 | DOM Widget 显示文件/输出内容 | 全局服务（如数学排版） |

## MIME 渲染器扩展

fasta、geojson、vega3 属于 MIME 渲染器扩展，在 package.json 中配置为：

```json
{
  "jupyterlab": {
    "mimeExtension": true,
    "outputDir": "jupyterlab_fasta/labextension"
  }
}
```

这类扩展的入口文件默认导出一个或多个 `IRenderMime.IExtension` 对象，JupyterLab 在启动时扫描所有 mimeExtension，将它们注册到 rendermime 注册表中。当遇到对应 MIME 类型的数据时，JupyterLab 调用工厂创建渲染器 Widget。

详见[ MIME 渲染器开发模式](/concepts/02-mime-renderer-pattern.md)。

## 应用扩展（ILatexTypesetter 服务）

katex 和 mathjax2 属于应用扩展，它们不渲染特定文件，而是提供 `ILatexTypesetter` 全局服务，用于排版 Notebook 和 Markdown 中的数学公式（`$...$`、`$$...$$` 等）。

### package.json 配置

**KaTeX**：[^katex-pkg]

```json
{
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_katex/labextension",
    "schemaDir": "schema",
    "disabledExtensions": [
      "@jupyterlab/mathjax-extension:plugin",
      "@jupyterlab/mathjax2-extension:plugin"
    ]
  }
}
```

**MathJax2**：[^mathjax2-pkg]

```json
{
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_mathjax2/labextension"
  }
}
```

关键区别：
- KaTeX 有 `schemaDir`（用户可配置宏定义）和 `disabledExtensions`（禁用竞品）
- MathJax2 无额外配置，是基础回退选项

### JupyterFrontEndPlugin 结构

应用扩展导出 `JupyterFrontEndPlugin` 对象，这是 JupyterLab 应用插件的标准形式：

**KaTeX 插件**：[^katex-index]

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILatexTypesetter } from '@jupyterlab/rendermime';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

const katexPlugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: '@jupyterlab/katex-extension:plugin',
  requires: [ISettingRegistry],       // 依赖的 Token（必须提供）
  provides: ILatexTypesetter,          // 提供的服务 Token
  activate: (app, settingRegistry) => {
    // 激活函数：设置配置监听，返回服务实例
    function updateSettings(settings) {
      options.macros = settings.get('macros').composite;
    }
    settingRegistry.load(katexPluginId).then(settings => {
      settings.changed.connect(updateSettings);
      updateSettings(settings);
    });
    return new KatexTypesetter();
  },
  autoStart: true                      // 启动时自动激活
};
export default katexPlugin;
```

**MathJax2 插件**：[^mathjax2-index]

```typescript
const plugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: '@jupyterlab/mathjax2-extension:plugin',
  autoStart: true,
  provides: ILatexTypesetter,
  optional: [ITranslator],             // 可选依赖（可以为 null）
  activate: (app, translator) => {
    const url = PageConfig.getOption('fullMathjaxUrl');
    const config = PageConfig.getOption('mathjaxConfig');
    if (!url) {
      throw new Error(`${plugin.id} requires 'fullMathjaxUrl' in PageConfig`);
    }
    return new MathJaxTypesetter({ url, config });
  }
};
```

### Token 依赖注入模式

JupyterLab 使用 Lumino Token 系统进行依赖注入：

- `requires: [ISettingRegistry]`：必须的依赖，JupyterLab 在激活插件时注入对应的实例
- `optional: [ITranslator]`：可选依赖，如果不可用则传入 null
- `provides: ILatexTypesetter`：声明本插件提供 ILatexTypesetter 服务，其他插件可以通过 `requires: [ILatexTypesetter]` 注入使用

### ILatexTypesetter 接口

```typescript
interface ILatexTypesetter {
  typeset(node: HTMLElement): void;
}
```

JupyterLab 在渲染 Markdown 和 Notebook 输出时，会对包含数学公式的 DOM 节点调用 `typeset(node)`。实现此接口即可替换 JupyterLab 的数学排版引擎。

## KaTeX 实现分析

### KatexTypesetter

[^katex-index] KaTeX 的排版器实现非常简洁：

```typescript
export class KatexTypesetter implements IRenderMime.ILatexTypesetter {
  typeset(node: HTMLElement): void {
    renderMathInElement(node, options);
  }
}
```

实际工作委托给 `autorender.ts` 中的 `renderMathInElement` 函数。

### 自动渲染（autorender）

[katex-extension/src/autorender.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/autorender.ts) 实现了数学公式的自动发现和渲染：[^katex-autorender]

1. **分隔符识别**：支持5种数学公式分隔符：
   - `$...$` 和 `\(...\)`：行内公式
   - `$$...$$` 和 `\[...\]`：展示公式（块级）
   - `\begin{equation}...\end{equation}`：LaTeX equation 环境

2. **DOM 遍历**：`renderElem()` 递归遍历 DOM 树，跳过 `script`/`noscript`/`style`/`textarea`/`pre`/`code` 标签

3. **文本解析**：`splitWithDelimiters()` 按分隔符切分文本节点，区分文本和数学内容

4. **KaTeX 渲染**：对数学内容调用 `katex.render(math, span, options)`，失败时回退显示原始文本

5. **宏配置**：通过 `options.macros` 从 JupyterLab 设置系统读取用户自定义宏

### KaTeX 配置来源

| 配置项 | 来源 | 说明 |
|--------|------|------|
| `macros` | ISettingRegistry（用户设置） | 自定义 LaTeX 宏定义 |
| `delimiters` | 硬编码 defaultAutoRenderOptions | 5种分隔符 |
| `ignoredTags` | 硬编码 | script/noscript/style/textarea/pre/code |
| `throwOnError` | false | 渲染失败时不抛出异常 |
| `errorColor` | #CC0000 | 错误显示为红色 |

## MathJax2 实现分析

### MathJaxTypesetter

[mathjax2-extension/src/typesetter.ts](file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/typesetter.ts) 实现了基于 MathJax 2 的排版器。[^mathjax2-typesetter]

与 KaTeX 的关键区别：

1. **动态脚本加载**：MathJax2 不从 npm 包打包，而是在首次 `typeset()` 调用时动态创建 `<script>` 标签从 CDN 加载：

```typescript
private _init(): void {
  const script = document.createElement('script');
  script.src = `${this._url}?config=${this._config}&delayStartupUntil=configured`;
  head.appendChild(script);
  script.addEventListener('load', () => this._onLoad());
  this._initialized = true;
}
```

2. **异步初始化**：使用 `PromiseDelegate<void>` 等待 MathJax 加载完成后才执行排版：

```typescript
typeset(node: HTMLElement): void {
  if (!this._initialized) this._init();
  void this._initPromise.promise.then(() => {
    MathJax.Hub.Queue(['Typeset', MathJax.Hub, node]);
    MathJax.Hub.Queue(['Require', MathJax.Ajax, '[MathJax]/extensions/TeX/AMSmath.js'], () => {
      MathJax.InputJax.TeX.resetEquationNumbers();
    });
  });
}
```

3. **配置来自 PageConfig**：MathJax URL 和配置名从 JupyterLab 的页面配置中读取（`fullMathjaxUrl`、`mathjaxConfig`），而非用户设置

4. **MathJax Hub 配置**：加载完成后配置 MathJax 的行内/展示公式分隔符、字体、换行等

### MathJax2 配置项

| 配置 | 值 | 说明 |
|------|-----|------|
| inlineMath | `['$','$']`, `['\\(','\\)']` | 行内公式分隔符 |
| displayMath | `['$$','$$']`, `['\\[','\\]']` | 展示公式分隔符 |
| processEscapes | true | 处理转义字符 |
| displayAlign | center | 公式居中对齐 |
| webFont | STIX-Web | 使用 STIX-Web 网页字体 |
| skipStartupTypeset | true | 跳过初始自动排版（由 JupyterLab 控制） |
| messageStyle | none | 不显示加载消息 |

## 互斥机制

KaTeX 和 MathJax2 都提供 `ILatexTypesetter` 服务，但同一时间只能有一个生效。KaTeX 通过 `disabledExtensions` 机制确保互斥：

```json
"disabledExtensions": [
  "@jupyterlab/mathjax-extension:plugin",
  "@jupyterlab/mathjax2-extension:plugin"
]
```

安装并启用 KaTeX 扩展后，JupyterLab 会自动禁用 MathJax 和 MathJax2 插件。用户可以通过 JupyterLab 设置面板选择使用哪个排版引擎。

**排版引擎选择建议**：

| 引擎 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| KaTeX | 快速（本地渲染，无网络请求）、支持用户宏配置 | 不支持所有 LaTeX 命令 | 默认推荐，大多数使用场景 |
| MathJax2 | 完整 LaTeX 支持 | 需要网络加载 CDN、较慢、异步渲染 | 需要复杂 LaTeX 公式的场景 |

## 导出模式

两种扩展类型的导出方式也不同：

- **MIME 渲染器**：`export default extensions`（一个或多个 IExtension 对象数组）
- **应用扩展**：`export default plugin`（单个 JupyterFrontEndPlugin 对象）

此外，MathJax2 还具名导出了 `MathJaxTypesetter` 类，允许其他代码直接引用：

```typescript
export { MathJaxTypesetter } from './typesetter';
```

## 相关概念

- [MIME 渲染器开发模式](/concepts/02-mime-renderer-pattern.md)
- [数学公式渲染：KaTeX vs MathJax2](/concepts/06-math-renderers.md)
- [IRenderMime 核心 API 参考](/references/rendermime-interfaces-api.md)
- [package.json 扩展配置参考](/references/extension-config-reference.md)

[^katex-autorender]: katex-extension/src/autorender.ts
[^katex-index]: katex-extension/src/index.ts
[^katex-pkg]: katex-extension/package.json
[^mathjax2-index]: mathjax2-extension/src/index.ts
[^mathjax2-pkg]: mathjax2-extension/package.json
[^mathjax2-typesetter]: mathjax2-extension/src/typesetter.ts
