---
type: Concept
title: 自定义文档类型
description: 创建自定义文件类型（.example），实现文档Model、WidgetFactory和协作编辑支持
tags: [jupyterlab, documents, docregistry, model-factory, widget-factory, yjs, collaboration]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: docs-index-src
    resource: /references/core-api-tokens.md
    title: documents/src/index.ts 文档注册
  - id: docs-model-src
    resource: /references/core-api-tokens.md
    title: documents/src/model.ts 自定义DocumentModel
---

## 自定义文档类型概述

JupyterLab的文档系统支持创建自定义文件类型，实现打开、编辑、保存和协作功能。documents示例展示了一个完整的自定义文档类型——`.example`文件，包含位置(x,y)和文本内容，支持多人协作编辑。

### 核心组件

创建自定义文档类型需要实现以下组件：

| 组件 | 类 | 职责 |
|------|-----|------|
| FileType | 注册到docRegistry | 声明文件扩展名、MIME类型 |
| DocumentModel | 继承 `YDocument<...>` | 数据模型，处理Yjs共享数据 |
| ModelFactory | 实现 `IModelFactory` | 创建Model实例 |
| DocumentWidget | 继承 `DocumentWidget` | UI视图，渲染和编辑内容 |
| WidgetFactory | 继承 `ABCWidgetFactory` | 创建Widget实例 |
| DocumentRegistry | `app.docRegistry` | 注册以上所有组件 |
| WidgetTracker | `WidgetTracker` | 追踪Widget实例，支持布局恢复 |

## 注册文件类型

```typescript
// 注册文件类型
app.docRegistry.addFileType({
  name: 'example',                 // 类型标识名
  displayName: 'Example',          // 显示名称
  mimeTypes: ['text/json', 'application/json'],
  extensions: ['.example'],        // 文件扩展名
  fileFormat: 'text',              // 文件格式
  contentType: 'exampledoc' as any // 内容类型标识（需与sharedModelFactory一致）
});
```

## 自定义DocumentModel

Model负责数据存储和变更通知，使用Yjs作为底层共享文档：

```typescript
import { YDocument, DocumentChange } from '@jupyter/ydoc';

// 定义Model属性接口
interface IExampleDoc {
  position: { x: number; y: number };
  content: string;
}

// 定义变更参数
interface ExampleDocChange extends DocumentChange {
  positionChange?: { x?: number; y?: number };
  contentChange?: boolean;
}

class ExampleDoc extends YDocument<ExampleDocChange> {
  constructor(options?: {}) {
    super();
    this._position = { x: 0, y: 0 };
    this._content = '';
  }

  get position(): { x: number; y: number } {
    return this._position;
  }

  set position(value: { x: number; y: number }) {
    this._position = value;
    this.triggerContentChange();
  }

  get content(): string {
    return this._content;
  }

  set content(value: string) {
    this._content = value;
    this.triggerContentChange();
  }

  // 创建共享模型的工厂方法
  public static create(): ExampleDoc {
    return new ExampleDoc();
  }

  private _position: { x: number; y: number };
  private _content: string;
}
```

### 协作支持

documents示例支持可选的多人协作功能（使用 `@jupyter/collaborative-drive`）：

```typescript
// 在插件activate中
const drive: ICollaborativeDrive | null = args[0];  // optional dependency

if (drive) {
  const sharedExampleFactory = () => {
    return ExampleDoc.create();
  };
  drive.sharedModelFactory.registerDocumentFactory(
    'exampledoc',       // 与contentType一致
    sharedExampleFactory
  );
}
```

协作是**可选**的——如果未安装collaboration包，文档仍可独立工作。

## ModelFactory

ModelFactory负责创建Model实例：

```typescript
class ExampleDocModelFactory implements IModelFactory {
  name = 'example-model';
  contentType = 'exampledoc';
  fileFormat = 'text';

  createNew(languagePreference?: string, modelDB?: IModelDB): ExampleDoc {
    return ExampleDoc.create();
  }

  preferredPath(path: string): string {
    return path;
  }
}

// 注册
const modelFactory = new ExampleDocModelFactory();
app.docRegistry.addModelFactory(modelFactory);
```

## DocumentWidget

Widget负责UI渲染和用户交互：

```typescript
class ExampleDocWidget extends DocumentWidget<Widget, ExampleDoc> {
  constructor(options: DocumentWidget.IOptions<Widget, ExampleDoc>) {
    super(options);
    // this.context 提供对DocumentModel和文件操作的访问
    // this.content 是主内容Widget
  }
}
```

更完整的实现包含内部Widget处理DOM渲染和事件监听，与model通过Signal连接（见[信号与事件通信](/concepts/06-signals.md)）。

## WidgetFactory

WidgetFactory负责创建DocumentWidget实例：

```typescript
import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';

class ExampleWidgetFactory extends ABCWidgetFactory<ExampleDocWidget, ExampleDoc> {
  protected createNewWidget(context: DocumentRegistry.IContext<ExampleDoc>): ExampleDocWidget {
    const content = new ExampleContentWidget();  // 你的内容Widget
    const widget = new ExampleDocWidget({ content, context });
    return widget;
  }
}

// 注册
const widgetFactory = new ExampleWidgetFactory({
  name: FACTORY,                 // 'Example editor'
  modelName: 'example-model',    // 对应ModelFactory的name
  fileTypes: ['example'],        // 对应FileType的name
  defaultFor: ['example']        // 默认打开此类型文件
});

// 追踪Widget创建
widgetFactory.widgetCreated.connect((sender, widget) => {
  widget.context.pathChanged.connect(() => {
    tracker.save(widget);  // 路径变化时更新恢复数据
  });
  tracker.add(widget);
});

app.docRegistry.addWidgetFactory(widgetFactory);
```

## 布局恢复

使用ILayoutRestorer确保页面刷新后恢复打开的文档：

```typescript
const tracker = new WidgetTracker<ExampleDocWidget>({ namespace: 'documents-example' });

restorer.restore(tracker, {
  command: 'docmanager:open',           // 恢复时执行的命令
  args: widget => ({
    path: widget.context.path,          // 文件路径
    factory: FACTORY                    // WidgetFactory名称
  }),
  name: widget => widget.context.path   // 唯一标识
});
```

## 导出Token供其他扩展使用

```typescript
// 定义并导出Token
export const IExampleDocTracker = new Token<IWidgetTracker<ExampleDocWidget>>(
  'exampleDocTracker'
);

const extension: JupyterFrontEndPlugin<void> = {
  id: 'documents',
  provides: IExampleDocTracker,  // 声明提供此Token
  requires: [ILayoutRestorer],
  optional: [ICollaborativeDrive],
  activate: (app, restorer, drive) => {
    const tracker = new WidgetTracker<ExampleDocWidget>({ namespace: 'documents-example' });
    // ...注册所有组件...
    return tracker;  // provides要求返回实例
  }
};
```

其他扩展可以通过 `requires: [IExampleDocTracker]` 注入这个tracker，访问你的文档Widget。

## 完整数据流

```
用户点击.example文件
  → DocumentManager根据扩展名找到WidgetFactory
  → WidgetFactory.createNewWidget(context)
  → 创建ExampleDocWidget，内部使用ExampleDoc(Model)
  → Widget添加到Shell主区域
  → tracker.add(widget)
  → 用户操作（拖动方块/编辑文本）
  → 更新Model（position/content setter）
  → Model发出contentChanged信号
  → Widget收到信号更新DOM
  → 自动保存（通过Context）
  → 协作：Yjs同步到其他客户端
```

## 相关概念

- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [信号与事件通信](/concepts/06-signals.md)
- [设置与状态持久化](/concepts/09-settings-state.md)
- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [核心API与Token参考](/references/core-api-tokens.md)
