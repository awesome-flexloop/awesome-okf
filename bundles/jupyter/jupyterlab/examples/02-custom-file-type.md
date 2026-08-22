---
type: Example
title: "02 自定义文件类型：注册 .xyz 文件查看器"
description: 为自定义文件扩展名 .xyz 注册新的文件类型、模型工厂和 Widget 工厂，实现专用查看器，包含文件类型注册、Widget 创建和工具栏配置
tags: [jupyterlab, custom-file-type, widget-factory, model-factory, document-registry, extension]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T08:20:00Z" }
verified: { by: "process:grep-api-verification", at: "2026-08-22T08:20:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source-map
    resource: /references/source-code-map.md
    title: JupyterLab 源码文件地图
  - id: document-widget
    resource: /concepts/05-document-widget-system.md
    title: 文档注册与 Widget 工厂模式
---

# 自定义文件类型：注册 .xyz 文件查看器

本示例演示如何为 JupyterLab 注册一个新的自定义文件类型（.xyz），并为其创建专用的 Widget 查看器。我们将创建一个简单的 XYZ 文件查看器，能够显示 XYZ 格式的 3D 分子坐标文件（本示例以文本显示为主，可替换为实际渲染库如 3Dmol.js）。

## 目标

完成本示例后，你将能够：
1. 注册新的文件类型（.xyz）到 DocumentRegistry
2. 创建自定义 Widget 工厂
3. 创建自定义 Widget 显示文件内容
4. 配置工具栏按钮
5. 在文件浏览器中双击 .xyz 文件自动用我们的查看器打开

## 前置条件

- 完成 [01 最小扩展](01-minimal-extension.md)
- 理解 DocumentRegistry 和 Widget 工厂机制（参考 [05 文档注册与 Widget 工厂](/concepts/05-document-widget-system.md)）

## 项目结构

```
xyz-viewer/
├── package.json
├── pyproject.toml
├── tsconfig.json
└── src/
    ├── index.ts          # 插件入口
    └── widget.ts         # XYZ Widget 和工厂定义
```

## 步骤 1：创建 XYZ Widget

### src/widget.ts

```typescript
import { DocumentRegistry, ABCWidgetFactory, DocumentWidget } from '@jupyterlab/docregistry';
import { Widget } from '@lumino/widgets';
import { ToolbarButton } from '@jupyterlab/apputils';
import { PromiseDelegate } from '@lumino/coreutils';

/**
 * XYZ 文件模型接口
 */
interface IXYZData {
  atomCount: number;
  comment: string;
  atoms: { element: string; x: number; y: number; z: number }[];
}

/**
 * XYZ 查看器 Widget
 * 显示 XYZ 文件内容和解析后的原子信息
 */
export class XYZWidget extends Widget {
  private _context: DocumentRegistry.IContext<DocumentRegistry.IModel>;
  private _content: HTMLPreElement;
  private _info: HTMLDivElement;
  private _ready = new PromiseDelegate<void>();

  constructor(context: DocumentRegistry.IContext<DocumentRegistry.IModel>) {
    super();
    this._context = context;
    this.addClass('jp-xyzViewer');
    this.id = `xyz-viewer-${Private.id++}`;
    this.title.label = context.path.split('/').pop() || 'XYZ Viewer';
    this.title.closable = true;

    // 创建 DOM 结构
    const container = document.createElement('div');
    container.className = 'jp-xyzViewer-container';

    // 信息面板（原子数量等）
    this._info = document.createElement('div');
    this._info.className = 'jp-xyzViewer-info';
    container.appendChild(this._info);

    // 内容区域
    this._content = document.createElement('pre');
    this._content.className = 'jp-xyzViewer-content';
    container.appendChild(this._content);

    this.node.appendChild(container);

    // 监听模型变化
    context.ready.then(() => {
      this._onContentChanged();
      this._ready.resolve(undefined);
    });

    context.model.contentChanged.connect(this._onContentChanged, this);
    context.fileChanged.connect(this._onFileChanged, this);
  }

  /**
   * Promise that resolves when the widget is ready
   */
  get ready(): Promise<void> {
    return this._ready.promise;
  }

  /**
   * The widget's context
   */
  get context(): DocumentRegistry.IContext<DocumentRegistry.IModel> {
    return this._context;
  }

  /**
   * 解析 XYZ 文件内容
   * XYZ 格式：
   * 第1行：原子数量
   * 第2行：注释行
   * 第3+行：元素名 X Y Z
   */
  private _parseXYZ(text: string): IXYZData | null {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return null;

    const atomCount = parseInt(lines[0].trim(), 10);
    if (isNaN(atomCount)) return null;

    const comment = lines[1];
    const atoms: IXYZData['atoms'] = [];

    for (let i = 2; i < Math.min(lines.length, 2 + atomCount); i++) {
      const parts = lines[i].trim().split(/\s+/);
      if (parts.length >= 4) {
        atoms.push({
          element: parts[0],
          x: parseFloat(parts[1]),
          y: parseFloat(parts[2]),
          z: parseFloat(parts[3])
        });
      }
    }

    return { atomCount, comment, atoms };
  }

  /**
   * 内容变化处理
   */
  private _onContentChanged(): void {
    const text = this._context.model.toString();
    this._content.textContent = text;

    const data = this._parseXYZ(text);
    if (data) {
      // 统计元素
      const elements = new Map<string, number>();
      data.atoms.forEach(a => {
        elements.set(a.element, (elements.get(a.element) || 0) + 1);
      });
      const elementSummary = Array.from(elements.entries())
        .map(([el, count]) => `${el}: ${count}`)
        .join(', ');

      this._info.innerHTML = `
        <strong>XYZ File Info</strong><br/>
        Atoms: ${data.atomCount}<br/>
        Comment: ${data.comment}<br/>
        Elements: ${elementSummary}
      `;
    } else {
      this._info.innerHTML = '<strong>Invalid XYZ file format</strong>';
    }
  }

  /**
   * 文件路径变化处理
   */
  private _onFileChanged(): void {
    this.title.label = this._context.path.split('/').pop() || 'XYZ Viewer';
  }

  /**
   * 清理资源
   */
  dispose(): void {
    if (this.isDisposed) return;
    this._context.model.contentChanged.disconnect(this._onContentChanged, this);
    this._context.fileChanged.disconnect(this._onFileChanged, this);
    super.dispose();
  }
}

/**
 * XYZ 文档 Widget 类型（content=XYZWidget, model=IModel）
 */
type XYZDocumentWidget = DocumentWidget<XYZWidget, DocumentRegistry.IModel>;

/**
 * XYZ Widget 工厂
 * 继承 ABCWidgetFactory，实现 createNewWidget 方法
 */
export class XYZWidgetFactory extends ABCWidgetFactory<XYZDocumentWidget, DocumentRegistry.IModel> {
  constructor() {
    super({
      name: 'XYZ Viewer',
      label: 'XYZ Viewer',
      modelName: 'text',
      fileTypes: ['xyz'],
      defaultFor: ['xyz'],
      readOnly: true,
      toolbarFactory: (widget: XYZDocumentWidget) => {
        return [
          {
            name: 'refresh',
            widget: new ToolbarButton({
              iconClass: 'jp-RefreshIcon jp-Icon jp-Icon-16',
              onClick: () => {
                widget.context.revert();
              },
              tooltip: 'Refresh XYZ file'
            })
          }
        ];
      }
    });
  }

  /**
   * 创建新的文档 Widget
   * 框架在用户打开 .xyz 文件时调用此方法
   */
  protected createNewWidget(
    context: DocumentRegistry.IContext<DocumentRegistry.IModel>
  ): XYZDocumentWidget {
    const content = new XYZWidget(context);
    return new DocumentWidget({ content, context });
  }
}

/**
 * 私有命名空间，用于生成唯一 ID
 */
namespace Private {
  export let id = 0;
}
```

## 步骤 2：编写插件入口

### src/index.ts

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { XYZWidgetFactory } from './widget';

/**
 * XYZ 文件类型扩展插件
 * 注册 .xyz 文件类型和查看器 Widget 工厂
 */
const xyzPlugin: JupyterFrontEndPlugin<void> = {
  id: 'xyz-viewer:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    const { docRegistry } = app;

    // 1. 注册 .xyz 文件类型
    docRegistry.addFileType({
      name: 'xyz',
      displayName: 'XYZ File',
      extensions: ['.xyz'],
      mimeTypes: ['chemical/x-xyz'],
      contentType: 'file',
      fileFormat: 'text',
      iconClass: 'jp-MaterialIcon jp-CodeIcon'  // 复用代码文件图标
    });

    // 2. 创建并注册 Widget 工厂
    const factory = new XYZWidgetFactory();
    docRegistry.addWidgetFactory(factory);

    // 3. 添加 CSS 样式（通过注入 <style> 标签）
    const style = document.createElement('style');
    style.textContent = `
      .jp-xyzViewer {
        overflow: auto;
        height: 100%;
      }
      .jp-xyzViewer-container {
        padding: 10px;
        height: 100%;
        display: flex;
        flex-direction: column;
      }
      .jp-xyzViewer-info {
        background: var(--jp-layout-color2);
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-family: var(--jp-ui-font-family);
        font-size: var(--jp-ui-font-size1);
      }
      .jp-xyzViewer-content {
        flex: 1;
        background: var(--jp-layout-color0);
        border: 1px solid var(--jp-border-color1);
        border-radius: 4px;
        padding: 10px;
        overflow: auto;
        font-family: var(--jp-code-font-family);
        font-size: var(--jp-code-font-size);
        white-space: pre;
        margin: 0;
      }
    `;
    document.head.appendChild(style);

    console.log('XYZ Viewer extension activated!');
  }
};

export default xyzPlugin;
```

## 步骤 3：配置 package.json

```json
{
  "name": "xyz-viewer",
  "version": "0.1.0",
  "description": "XYZ file viewer for JupyterLab",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension",
    "build:lib": "tsc",
    "build:labextension": "jupyter labextension build .",
    "watch": "tsc -w",
    "clean": "rimraf lib tsconfig.tsbuildinfo"
  },
  "dependencies": {
    "@jupyterlab/application": "^4.0.0",
    "@jupyterlab/apputils": "^4.0.0",
    "@jupyterlab/docregistry": "^4.0.0",
    "@lumino/widgets": "^2.0.0",
    "@lumino/coreutils": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "~5.0.0",
    "rimraf": "~5.0.0",
    "@jupyterlab/builder": "^4.0.0"
  },
  "jupyterlab": {
    "extension": true,
    "outputDir": "xyz_viewer/labextension",
    "_buildConfig": {
      "sharedPackages": {
        "@jupyterlab/application": { "singleton": true, "bundled": false },
        "@jupyterlab/apputils": { "singleton": true, "bundled": false },
        "@jupyterlab/docregistry": { "singleton": true, "bundled": false },
        "@lumino/widgets": { "singleton": true, "bundled": false },
        "@lumino/coreutils": { "singleton": true, "bundled": false }
      }
    }
  }
}
```

## 步骤 4：创建 Python 包

参考 [01 最小扩展](01-minimal-extension.md) 的 pyproject.toml 和 __init__.py，将包名改为 `xyz_viewer`。

## 关键代码解析

### 文件类型注册

```typescript
docRegistry.addFileType({
  name: 'xyz',               // 内部唯一标识
  displayName: 'XYZ File',   // 用户可见名称
  extensions: ['.xyz'],      // 扩展名列表
  mimeTypes: ['chemical/x-xyz'],  // MIME 类型
  contentType: 'file',       // 内容类型：'file'|'notebook'|'directory'
  fileFormat: 'text',        // 文件格式：'text'|'json'|'base64'
  iconClass: '...'           // CSS 图标类
});
```

### Widget 工厂配置

```typescript
class XYZWidgetFactory extends ABCWidgetFactory<XYZDocumentWidget, DocumentRegistry.IModel> {
  // 在构造函数中传入工厂选项
  constructor() {
    super({
      name: 'XYZ Viewer',           // 工厂名（在 "Open With" 菜单中显示）
      modelName: 'text',            // 使用的模型（'text' 是内置文本模型）
      fileTypes: ['xyz'],           // 支持的文件类型
      defaultFor: ['xyz'],          // 作为 .xyz 文件的默认打开方式
      readOnly: true,               // 只读查看器
      toolbarFactory: (widget) => [...]  // 工具栏按钮工厂
    });
  }

  // 实现抽象方法：创建新的文档 Widget
  protected createNewWidget(context) {
    return new DocumentWidget({ content: new XYZWidget(context), context });
  }
}
```

关键要点：
- 继承 `ABCWidgetFactory<T, U>` 抽象类（`T` 是 Widget 类型，`U` 是 Model 类型）
- 构造函数中通过 `super(options)` 传入工厂配置
- 必须实现 `protected createNewWidget(context)` 方法，返回一个 `DocumentWidget` 实例
- `DocumentWidget` 构造函数接收 `{content, context}`，自动处理工具栏、reveal 信号等
- `toolbarFactory` 返回工具栏按钮数组，按钮在 Widget 创建后自动添加

### Widget 创建

`createNewWidget(context)` 方法在用户打开 .xyz 文件时被调用：
1. 创建内容 Widget（XYZWidget）
2. 包装为 DocumentWidget（包含 toolbar、context）
3. DocumentRegistry 自动为 Widget 应用已注册的 WidgetExtension

### Context 的使用

`context` 提供：
- `context.model.toString()`：获取文件文本内容
- `context.model.contentChanged`：内容变化信号
- `context.fileChanged`：文件路径变化信号
- `context.path`：文件路径
- `context.revert()`：恢复到磁盘上的版本
- `context.save()`：保存文件
- `context.ready`：Context 初始化完成 Promise

## 测试

1. 构建并安装扩展：`jlpm build && pip install -e .`
2. 创建一个测试文件 `test.xyz`：

```xyz
5
Methane (CH4)
C      0.000000    0.000000    0.000000
H      0.640101    0.640101    0.640101
H     -0.640101   -0.640101    0.640101
H     -0.640101    0.640101   -0.640101
H      0.640101   -0.640101   -0.640101
```

3. 启动 JupyterLab：`jupyter lab`
4. 在文件浏览器中双击 `test.xyz`
5. 应该看到我们的 XYZ Viewer 打开，显示文件信息面板和原始内容

## 扩展思路

1. **可编辑支持**：将 `readOnly: false`，在 XYZWidget 中添加 CodeMirror 编辑器
2. **3D 渲染**：集成 3Dmol.js 或 Three.js 渲染分子 3D 结构
3. **MIME 渲染器**：作为 MIME 渲染扩展，在 Notebook 输出中渲染内联 XYZ
4. **设置支持**：添加设置项控制显示样式
5. **导出功能**：工具栏添加导出为其他格式（PDB、JSON）按钮

## 相关概念

- [05 文档注册与 Widget 工厂模式](/concepts/05-document-widget-system.md)
- [03 插件系统与依赖注入](/concepts/03-plugin-system.md)
- [01 最小扩展示例](01-minimal-extension.md)
- [源码文件地图](/references/source-code-map.md)
