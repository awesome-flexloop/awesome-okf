---
type: HowTo
title: 自定义 LaTeX 排版器
description: 开发自定义 ILatexTypesetter 替换默认数学公式排版引擎，以一个极简 MathML 渲染器为例展示应用扩展模式
tags: [tutorial, latex, typesetter, ilatextypesetter, howto]
prerequisites:
  - 理解 [扩展类型对比](/concepts/03-extension-types.md)
  - 理解 [数学公式渲染机制](/concepts/06-math-renderers.md)
  - 熟悉 [IRenderMime API](/references/rendermime-interfaces-api.md)
sources:
  - id: katex-index
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/src/index.ts
  - id: mathjax2-index
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/src/index.ts
  - id: katex-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/package.json
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# 自定义 LaTeX 排版器

本示例演示如何开发一个自定义的 `ILatexTypesetter` 应用扩展，替换 JupyterLab 默认的数学公式排版引擎。以一个将 LaTeX 公式渲染为 MathML 的极简排版器为例。

## 与 MIME 渲染器的区别

| 特性 | ILatexTypesetter（本示例） | MIME 文件渲染器 |
|------|---------------------------|----------------|
| 扩展类型 | `extension`（应用扩展） | `mimeExtension`（MIME扩展） |
| provides token | `ILatexTypesetter` | 无 |
| 注册方式 | `provides: ILatexTypesetter` | `mimeExtension: true` |
| 触发时机 | Markdown 单元格/输出中包含数学公式 | 打开特定文件或输出特定 MIME 类型 |
| 接口方法 | `typeset(node: HTMLElement): void` | `renderModel(model): Promise<void>` |

## 步骤 1：配置 package.json

```json
{
  "name": "@myorg/mathml-typesetter",
  "version": "0.1.0",
  "description": "MathML-based LaTeX typesetter for JupyterLab",
  "jupyterlab": {
    "extension": true,
    "outputDir": "myorg_mathml/labextension",
    "disabledExtensions": [
      "@jupyterlab/katex-extension:plugin",
      "@jupyterlab/mathjax2-extension:plugin"
    ]
  },
  "dependencies": {
    "@jupyterlab/rendermime": "^4.0.0",
    "@lumino/coreutils": "^2.0.0"
  }
}
```

关键点：
- `"extension": true`（非 `mimeExtension`）
- `disabledExtensions` 禁用 KaTeX 和 MathJax2，确保只有一个排版器生效
- 需要依赖 `@jupyterlab/rendermime` 获取 `ILatexTypesetter` Token

## 步骤 2：实现 src/index.ts

```typescript
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILatexTypesetter } from '@jupyterlab/rendermime';

/**
 * 极简 MathML 排版器
 * 将 $...$ 和 $$...$$ 中的 LaTeX 公式转换为 MathML 显示
 * 注意：这只是一个教学示例，真实实现需要 LaTeX 解析器
 */
class MathMLTypesetter implements ILatexTypesetter {
  typeset(node: HTMLElement): void {
    // 遍历所有文本节点，查找 $...$ 和 $$...$$ 分隔符
    this._processNode(node);
  }

  private _processNode(node: Node): void {
    const childNodes = node.childNodes;
    const toReplace: { node: Text; math: string; display: boolean }[] = [];

    for (let i = 0; i < childNodes.length; i++) {
      const child = childNodes[i];

      // 跳过不应处理的标签
      if (child.nodeType === Node.ELEMENT_NODE) {
        const tag = (child as Element).tagName.toLowerCase();
        if (['script', 'noscript', 'style', 'textarea', 'pre', 'code'].includes(tag)) {
          continue;
        }
        this._processNode(child);
        continue;
      }

      // 处理文本节点
      if (child.nodeType === Node.TEXT_NODE) {
        const text = child.textContent || '';
        const results = this._findMath(text);
        if (results.length > 0) {
          // 标记需要替换的节点
          toReplace.push(...results.map(r => ({
            node: child as Text,
            math: r.math,
            display: r.display
          })));
        }
      }
    }

    // 替换找到的数学公式（逆序处理避免索引偏移）
    for (const item of toReplace.reverse()) {
      this._replaceMath(item.node, item.math, item.display);
    }
  }

  /**
   * 简单查找 $...$ 和 $$...$$ 公式（教学用，生产环境需处理转义、大括号等）
   */
  private _findMath(text: string): Array<{ math: string; display: boolean }> {
    const results: Array<{ math: string; display: boolean }> = [];
    let i = 0;
    while (i < text.length) {
      // $$...$$ (display math)
      if (text[i] === '$' && text[i + 1] === '$') {
        const end = text.indexOf('$$', i + 2);
        if (end > i + 2) {
          results.push({ math: text.substring(i + 2, end), display: true });
          i = end + 2;
          continue;
        }
      }
      // $...$ (inline math)
      if (text[i] === '$' && text[i - 1] !== '\\') {
        const end = text.indexOf('$', i + 1);
        if (end > i + 1) {
          results.push({ math: text.substring(i + 1, end), display: false });
          i = end + 1;
          continue;
        }
      }
      i++;
    }
    return results;
  }

  /**
   * 用 MathML 元素替换文本中的公式
   */
  private _replaceMath(textNode: Text, _math: string, display: boolean): void {
    const parent = textNode.parentNode;
    if (!parent) return;

    // 这里应该使用 LaTeX → MathML 转换器（如 temml/laramath）
    // 教学示例：仅创建一个占位 MathML
    const mathEl = document.createElementNS('http://www.w3.org/1998/Math/MathML', 'math');
    mathEl.setAttribute('display', display ? 'block' : 'inline');
    const mi = document.createElementNS('http://www.w3.org/1998/Math/MathML', 'mi');
    mi.textContent = '[MathML]';
    mathEl.appendChild(mi);

    parent.insertBefore(mathEl, textNode);
    // 注意：完整实现需要分割文本节点并正确插入
  }
}

/**
 * 插件定义
 */
const plugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: '@myorg/mathml-typesetter:plugin',
  autoStart: true,
  provides: ILatexTypesetter,
  activate: () => {
    console.log('MathML Typesetter activated');
    return new MathMLTypesetter();
  }
};

export default plugin;
```

## 步骤 3：JupyterFrontEndPlugin 详解

应用扩展使用 `JupyterFrontEndPlugin` 接口注册，核心字段：

| 字段 | 类型 | 说明 | 本示例值 |
|------|------|------|---------|
| `id` | `string` | 唯一标识符（`package-name:plugin-name`） | `'@myorg/mathml-typesetter:plugin'` |
| `autoStart` | `boolean` | JupyterLab 启动时自动激活 | `true` |
| `provides` | `Token<T>` | 提供的服务 Token | `ILatexTypesetter` |
| `requires` | `Token<any>[]` | 必需的依赖服务 | 无 |
| `optional` | `Token<any>[]` | 可选的依赖服务 | 可选添加 `[ITranslator]` |
| `activate` | `Function` | 激活函数，返回服务实例 | `() => new MathMLTypesetter()` |

### activate 函数签名

```typescript
activate: (
  app: JupyterFrontEnd,      // JupyterLab 应用实例（始终注入）
  ...requiredDeps: any[]     // requires 中声明的服务，按顺序注入
) => T;                      // 返回 provides 声明的服务类型
```

### 使用 requires 和 optional

如果排版器需要访问设置或翻译服务：

```typescript
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ITranslator, nullTranslator } from '@jupyterlab/translation';

const plugin: JupyterFrontEndPlugin<ILatexTypesetter> = {
  id: '@myorg/mathml-typesetter:plugin',
  autoStart: true,
  requires: [ISettingRegistry],        // 必需：设置注册表
  optional: [ITranslator],             // 可选：翻译服务
  provides: ILatexTypesetter,
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry,  // requires 注入
    translator?: ITranslator            // optional 注入（可能 undefined）
  ) => {
    const trans = translator ?? nullTranslator;
    // ...加载设置、注册配置变更监听
    return new MathMLTypesetter();
  }
};
```

## 步骤 4：异步排版器模式

如果排版引擎需要异步加载（类似 MathJax2），使用 PromiseDelegate：

```typescript
import { PromiseDelegate } from '@lumino/coreutils';

class AsyncTypesetter implements ILatexTypesetter {
  constructor() {
    this._initialized = false;
    this._initPromise = new PromiseDelegate<void>();
  }

  typeset(node: HTMLElement): void {
    if (!this._initialized) {
      this._init();
    }
    void this._initPromise.promise.then(() => {
      // 引擎加载完成后执行排版
      this._doTypeset(node);
    });
  }

  private _init(): void {
    this._initialized = true;
    // 动态加载脚本
    const script = document.createElement('script');
    script.src = 'https://cdn.example.com/math-engine.js';
    script.charset = 'utf-8';
    script.onload = () => {
      this._engine = (window as any).MathEngine;
      this._initPromise.resolve();
    };
    script.onerror = () => {
      this._initPromise.reject(new Error('Failed to load math engine'));
    };
    document.head.appendChild(script);
  }

  private _doTypeset(node: HTMLElement): void {
    // 使用 this._engine 排版
    this._engine.render(node);
  }

  private _initialized: boolean;
  private _initPromise: PromiseDelegate<void>;
  private _engine: any;
}
```

## 步骤 5：Python 打包

与 MIME 渲染器的 Python 打包方式完全相同（参见 [Python 打包规范](/concepts/08-python-packaging.md)）：

- pyproject.toml 使用 hatchling + hatch-jupyter-builder
- `__init__.py` 实现 `_jupyter_labextension_paths()`
- `_version.py` 由构建自动生成

## 步骤 6：安装与测试

```bash
# 构建
jlpm install
jlpm run build:prod
pip install -e .

# 启动 JupyterLab（确认 KaTeX/MathJax2 被禁用）
jupyter lab

# 在 Notebook 中测试
# 创建 Markdown 单元格，输入：$E = mc^2$
# 应使用自定义 MathML 排版器渲染
```

## 互斥机制详解

package.json 中的 `disabledExtensions` 声明了冲突扩展：

```json
"jupyterlab": {
  "extension": true,
  "disabledExtensions": [
    "@jupyterlab/katex-extension:plugin",
    "@jupyterlab/mathjax2-extension:plugin"
  ]
}
```

JupyterLab 加载时，如果检测到当前扩展被激活，自动禁用列表中的扩展。这确保同一时间只有一个 `ILatexTypesetter` 提供者生效，避免重复排版冲突。

## 相关资源

- [扩展类型对比](/concepts/03-extension-types.md)
- [数学公式渲染机制](/concepts/06-math-renderers.md)
- [MIME 渲染器开发教程](/examples/01-custom-mime-renderer.md)
- [IRenderMime API 参考](/references/rendermime-interfaces-api.md)
- [Python 打包规范](/concepts/08-python-packaging.md)
