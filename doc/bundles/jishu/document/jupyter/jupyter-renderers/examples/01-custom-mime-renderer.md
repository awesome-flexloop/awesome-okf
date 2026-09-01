---
type: HowTo
title: 开发自定义 MIME 渲染器扩展
description: 从零开始开发一个 JupyterLab MIME 渲染器扩展的完整示例，基于 jupyter-renderers 提炼的四要素模式
tags: [tutorial, mime-renderer, custom-extension, howto]
prerequisites:
  - 理解 [MIME 渲染器开发模式](../concepts/02-mime-renderer-pattern.md)
  - 熟悉 [IRenderMime API](../references/rendermime-interfaces-api.md)
  - Node.js 14+、Python 3.7+、JupyterLab 3.0+
sources:
  - id: fasta-index
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/src/index.ts
  - id: geojson-index
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/src/index.ts
  - id: fasta-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/package.json
  - id: fasta-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/pyproject.toml
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# 开发自定义 MIME 渲染器扩展

本示例演示如何从零开始开发一个自定义 MIME 文件渲染器，以一个简单的 CSV 表格渲染器为例，完整展示四要素模式和预构建扩展打包。

## 场景假设

我们要开发一个 `@myorg/csv-renderer` 扩展，为 `text/csv` MIME 类型提供美观的表格渲染。

## 步骤 1：初始化项目

```bash
# 使用 cookiecutter 模板（推荐）
pip install cookiecutter
cookiecutter https://github.com/jupyterlab/extension-cookiecutter-ts
# 按照提示填写：
#   author_name: Your Name
#   extension_name: csv-renderer
#   project_short_description: CSV table renderer for JupyterLab

# 或手动创建目录结构
mkdir csv-renderer && cd csv-renderer
jlpm init
```

## 步骤 2：配置 package.json

```json
{
  "name": "@myorg/csv-renderer",
  "version": "0.1.0",
  "description": "CSV table renderer for JupyterLab",
  "keywords": ["jupyter", "jupyterlab", "jupyterlab-extension"],
  "jupyterlab": {
    "mimeExtension": true,
    "outputDir": "myorg_csv/labextension"
  },
  "scripts": {
    "build": "tsc -b",
    "build:prod": "jupyter labextension build .",
    "clean": "rimraf lib myorg_csv/labextension tsconfig.tsbuildinfo"
  },
  "dependencies": {
    "@jupyterlab/rendermime-interfaces": "^3.8.0",
    "@lumino/widgets": "^2.1.0"
  },
  "devDependencies": {
    "@jupyterlab/builder": "^4.0.0",
    "typescript": "~5.0.0",
    "rimraf": "^4.0.0"
  }
}
```

关键点：
- `"mimeExtension": true` 标记这是 MIME 渲染器（非应用扩展）
- `outputDir` 指向 Python 包内的 labextension 目录
- 依赖 `@jupyterlab/rendermime-interfaces` 和 `@lumino/widgets`

## 步骤 3：实现 src/index.ts

```typescript
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

// ============================================================
// 要素 1：MIME 类型常量
// ============================================================
const MIME_TYPE = 'text/csv';
const CSS_CLASS = 'myorg-RenderedCSV';

// ============================================================
// 要素 2：渲染器 Widget 类
// ============================================================
export class RenderedCSV extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this.addClass(CSS_CLASS);
  }

  /**
   * 渲染 CSV 数据为 HTML 表格
   */
  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const data = model.data[this._mimeType] as string;
    const rows = this._parseCSV(data);

    // 创建表格
    const table = document.createElement('table');
    table.className = 'myorg-CSVTable';

    // 表头
    if (rows.length > 0) {
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      for (const cell of rows[0]) {
        const th = document.createElement('th');
        th.textContent = cell;
        headerRow.appendChild(th);
      }
      thead.appendChild(headerRow);
      table.appendChild(thead);
    }

    // 数据行
    const tbody = document.createElement('tbody');
    for (let i = 1; i < rows.length; i++) {
      const tr = document.createElement('tr');
      for (const cell of rows[i]) {
        const td = document.createElement('td');
        td.textContent = cell;
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    this.node.innerHTML = '';
    this.node.appendChild(table);
    return Promise.resolve();
  }

  /**
   * 简单 CSV 解析（生产环境建议使用专业库如 papaparse）
   */
  private _parseCSV(text: string): string[][] {
    return text.trim().split('\n').map(line => line.split(','));
  }

  private _mimeType: string;
}

// ============================================================
// 要素 3：渲染器工厂
// ============================================================
const rendererFactory: IRenderMime.IRendererFactory = {
  safe: true,                    // textContent 渲染，无 XSS 风险
  mimeTypes: [MIME_TYPE],
  createRenderer: (options: IRenderMime.IRendererOptions) =>
    new RenderedCSV(options),
};

// ============================================================
// 要素 4：扩展描述符
// ============================================================
const extension: IRenderMime.IExtension = {
  id: '@myorg/csv-renderer:plugin',
  description: 'CSV table renderer',
  documentWidgetFactoryOptions: {
    name: 'CSV Table',
    primaryFileType: 'csv',
    fileTypes: ['csv', 'tsv'],
    defaultFor: ['csv'],
  },
  fileTypes: [
    {
      name: 'csv',
      mimeTypes: [MIME_TYPE],
      extensions: ['.csv'],
      iconClass: 'jp-MaterialIcon jp-SpreadsheetIcon',
    },
    {
      name: 'tsv',
      mimeTypes: ['text/tab-separated-values'],
      extensions: ['.tsv'],
      iconClass: 'jp-MaterialIcon jp-SpreadsheetIcon',
    },
  ],
  rendererFactory,
  rank: 0,                       // 最高优先级
  dataType: 'string',
};

export default [extension];
```

## 步骤 4：添加样式 style/index.css

```css
.myorg-RenderedCSV {
  width: 100%;
  height: 100%;
  overflow: auto;
  padding: 8px;
}

.myorg-CSVTable {
  border-collapse: collapse;
  width: 100%;
  font-family: var(--jp-ui-font-family);
  font-size: var(--jp-ui-font-size1);
}

.myorg-CSVTable th {
  background-color: var(--jp-layout-color2);
  font-weight: 600;
  text-align: left;
  padding: 6px 12px;
  border: 1px solid var(--jp-border-color1);
  position: sticky;
  top: 0;
}

.myorg-CSVTable td {
  padding: 4px 12px;
  border: 1px solid var(--jp-border-color2);
}

.myorg-CSVTable tr:nth-child(even) {
  background-color: var(--jp-layout-color1);
}

.myorg-CSVTable tr:hover {
  background-color: var(--jp-layout-color2);
}
```

在 `src/index.ts` 中导入 CSS：

```typescript
import '../style/index.css';
```

## 步骤 5：配置 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2018",
    "module": "commonjs",
    "lib": ["ES2018", "DOM"],
    "moduleResolution": "node",
    "declaration": true,
    "outDir": "lib",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts"]
}
```

## 步骤 6：Python 打包

### pyproject.toml

```toml
[build-system]
requires = ["hatchling>=1.5.0", "hatch-jupyter-builder>=0.5"]
build-backend = "hatchling.build"

[project]
name = "myorg-csv"
version = "0.1.0"
description = "CSV table renderer for JupyterLab"
requires-python = ">=3.7"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["myorg_csv"]
artifacts = ["myorg_csv/labextension"]

[tool.hatch.build.hooks.version]
path = "package.json"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = ["myorg_csv/labextension"]
skip-if-exists = ["myorg_csv/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "build"
npm = ["jlpm"]
```

### myorg_csv/__init__.py

```python
import json
import pathlib
from ._version import __version__

HERE = pathlib.Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]
```

## 步骤 7：构建与安装

```bash
# 安装依赖
jlpm install

# 开发模式安装（热更新）
jlpm run build
pip install -e .

# 启动 JupyterLab 测试
jupyter lab

# 生产构建（生成 wheel）
pip install build
python -m build
# wheel 在 dist/myorg_csv-0.1.0-py3-none-any.whl
```

## 步骤 8：测试验证

1. 打开 JupyterLab，在文件浏览器中创建一个 `.csv` 文件
2. 双击打开，应看到表格渲染
3. 在 Notebook 中输出 CSV 数据：

```python
from IPython.display import display, Markdown
csv_data = "name,age,city\nAlice,30,Beijing\nBob,25,Shanghai\nCharlie,35,Guangzhou"
display({"text/csv": csv_data}, raw=True)
```

## 常见问题

### Q: safe 设为 true 还是 false？

- `safe: true`：渲染器使用 `textContent` 或经 `ISanitizer.sanitize()` 净化的 HTML，无 XSS 风险
- `safe: false`：渲染器直接使用 `innerHTML` 插入不可信数据，需要 sandboxed 输出

### Q: dataType 选什么？

- `'string'`：原始文本数据（CSV、FASTA 等）
- `'json'`：JSON 对象（GeoJSON、Vega 等）
- 如果渲染器能直接处理 JSON 对象，选 `'json'` 省去手动解析

### Q: rank 如何设置？

- `0`：最高优先级（该 MIME 类型的首选渲染器）
- `50+`：较低优先级（备选渲染器）
- 当多个渲染器注册同一 MIME 类型时，rank 小的优先

### Q: 是否需要 resolver、linkHandler、sanitizer？

从 `IRendererOptions` 中按需解构：
- `resolver`：需要处理相对路径 URL（如加载外部数据文件）时使用
- `linkHandler`：需要自定义链接点击行为时使用
- `sanitizer`：需要渲染 HTML 内容（如 GeoJSON popup）时使用

## 相关资源

- [MIME 渲染器开发模式](../concepts/02-mime-renderer-pattern.md)
- [扩展类型对比](../concepts/03-extension-types.md)
- [IRenderMime API 参考](../references/rendermime-interfaces-api.md)
- [Python 打包规范](../concepts/08-python-packaging.md)
- [扩展配置参考](../references/extension-config-reference.md)
