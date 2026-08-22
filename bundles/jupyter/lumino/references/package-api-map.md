---
type: Reference
title: Lumino 包依赖关系与 API 速查表
description: Lumino 各包之间的依赖关系图、核心 API 签名速查、关键类型定义
tags: [lumino, api, reference, dependency, typescript]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T12:55:00+08:00" }
verified: { by: "process:grep-api-validation", at: "2026-08-22T13:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: lumino-repo
    resource: /external/libs/jupyter/lumino/
    title: Lumino 本地源码镜像
---

# Lumino 包依赖关系与 API 速查

## 包依赖关系图

Lumino 的包遵循严格的分层依赖，无循环依赖：

```mermaid
graph TB
    subgraph "基础设施层"
        ALG[algorithm]
        COL[collections]
        DIS[disposable]
    end

    subgraph "核心工具层"
        SIG[signaling]
        MSG[messaging]
        PROP[properties]
        DOM[domutils]
        KB[keyboard]
        CU[coreutils]
    end

    subgraph "渲染抽象层"
        VDOM[virtualdom]
    end

    subgraph "UI组件层"
        WID[widgets]
        CMD[commands]
        DD[dragdrop]
        POL[polling]
    end

    subgraph "高级组件层"
        DG[datagrid]
        TH[default-theme]
    end

    subgraph "应用框架层"
        APP[application]
    end

    ALG --> COL
    DIS --> COL
    SIG --> DIS
    MSG --> ALG
    MSG --> COL
    PROP --> COL
    DOM --> ALG
    KB --> ALG
    CU --> DIS
    CU --> ALG
    CU --> COL
    VDOM --> ALG
    CMD --> ALG
    CMD --> CU
    CMD --> DIS
    CMD --> DOM
    CMD --> KB
    CMD --> SIG
    CMD --> VDOM
    WID --> ALG
    WID --> MSG
    WID --> DIS
    WID --> DOM
    WID --> SIG
    WID --> PROP
    WID --> VDOM
    DD --> DIS
    DD --> DOM
    POL --> DIS
    POL --> SIG
    POL --> ALG
    DG --> ALG
    DG --> DOM
    DG --> DIS
    DG --> SIG
    DG --> KB
    DG --> WID
    DG --> VDOM
    APP --> CMD
    APP --> CU
    APP --> WID

    style ALG fill:#e3f2fd,stroke:#1565c0
    style COL fill:#e3f2fd,stroke:#1565c0
    style DIS fill:#e3f2fd,stroke:#1565c0
    style SIG fill:#e8f5e9,stroke:#2e7d32
    style MSG fill:#e8f5e9,stroke:#2e7d32
    style PROP fill:#e8f5e9,stroke:#2e7d32
    style DOM fill:#e8f5e9,stroke:#2e7d32
    style KB fill:#e8f5e9,stroke:#2e7d32
    style CU fill:#e8f5e9,stroke:#2e7d32
    style VDOM fill:#fff3e0,stroke:#e65100
    style WID fill:#fce4ec,stroke:#c62828
    style CMD fill:#fce4ec,stroke:#c62828
    style DD fill:#fce4ec,stroke:#c62828
    style POL fill:#fce4ec,stroke:#c62828
    style DG fill:#f3e5f5,stroke:#6a1b9a
    style TH fill:#f3e5f5,stroke:#6a1b9a
    style APP fill:#fff8e1,stroke:#ff8f00
```

## 核心接口签名速查

### IDisposable（disposable 包）

```typescript
interface IDisposable {
  readonly isDisposed: boolean;
  dispose(): void;
}

class DisposableDelegate implements IDisposable {
  constructor(fn: () => void);
  readonly isDisposed: boolean;
  dispose(): void;  // 调用一次后 fn 置 null，幂等安全
}
```

### Signal（signaling 包）

```typescript
class Signal<T, U> implements ISignal<T, U> {
  constructor(sender: T);
  readonly sender: T;
  connect(slot: Slot<T, U>, thisArg?: any): boolean;
  disconnect(slot: Slot<T, U>, thisArg?: any): boolean;
  emit(args: U): void;
}

type Slot<T, U> = (sender: T, args: U) => void;
```

### Message / MessageLoop（messaging 包）

```typescript
class Message {
  constructor(type: string);
  readonly type: string;
  readonly isConflatable: boolean;  // 默认 false
  conflate(other: Message): boolean;  // 默认 false
}

class ConflatableMessage extends Message {
  readonly isConflatable: boolean;  // 始终 true
  conflate(other: ConflatableMessage): boolean;  // 始终 true
}

interface IMessageHandler {
  processMessage(msg: Message): void;
}

namespace MessageLoop {
  function sendMessage(handler: IMessageHandler, msg: Message): void;    // 同步立即
  function postMessage(handler: IMessageHandler, msg: Message): void;    // 异步排队
  function installMessageHook(handler, hook: MessageHook): void;
  function removeMessageHook(handler, hook: MessageHook): void;
  function flush(): void;
  function clearData(handler: IMessageHandler): void;
}
```

### Widget（widgets 包）

```typescript
class Widget implements IMessageHandler, IObservableDisposable {
  constructor(options?: Widget.IOptions);
  readonly node: HTMLElement;
  readonly disposed: ISignal<this, void>;
  readonly isDisposed: boolean;
  readonly isAttached: boolean;
  readonly isHidden: boolean;
  readonly isVisible: boolean;
  readonly title: Title<Widget>;
  id: string;
  dataset: DOMStringMap;
  hiddenMode: Widget.HiddenMode;
  parent: Widget | null;
  layout: Layout | null;

  dispose(): void;
  show(): void;
  hide(): void;
  setFlag(flag: Widget.Flag): void;
  clearFlag(flag: Widget.Flag): void;
  testFlag(flag: Widget.Flag): boolean;
  update(): void;       // 发送 update-request 消息
  fit(): void;          // 发送 fit-request 消息
  activate(): void;     // 发送 activate-request 消息
  close(): void;        // 发送 close-request 消息
  addClass(name: string): void;
  removeClass(name: string): void;
  toggleClass(name: string, force?: boolean): boolean;

  // 静态方法
  static attach(widget: Widget, host: HTMLElement): void;
  static detach(widget: Widget): void;

  // 生命周期消息类型
  // 'before-attach' → 'after-attach' → 'before-show' → 'after-show' →
  // 'resize' / 'update-request' →
  // 'before-hide' → 'after-hide' → 'before-detach' → 'after-detach'
}
```

### Layout（widgets 包）

```typescript
abstract class Layout implements Iterable<Widget>, IDisposable {
  constructor(options?: Layout.IOptions);
  parent: Widget | null;
  fitPolicy: Layout.FitPolicy;  // 'set-no-constraint' | 'set-min-size'
  abstract [Symbol.iterator](): IterableIterator<Widget>;
  abstract removeWidget(widget: Widget): void;
  processParentMessage(msg: Message): void;
  protected init(): void;
  protected onResize(msg: Widget.ResizeMessage): void;
  protected onUpdateRequest(msg: Message): void;
  // ... 其他生命周期钩子
}

class LayoutItem implements IDisposable {
  constructor(widget: Widget);
  readonly widget: Widget;
  readonly minWidth: number;
  readonly minHeight: number;
  readonly maxWidth: number;
  readonly maxHeight: number;
  fit(): void;
  update(left, top, width, height): void;
}
```

### CommandRegistry（commands 包）

```typescript
class CommandRegistry {
  readonly commandChanged: ISignal<this, ICommandChangedArgs>;
  readonly commandExecuted: ISignal<this, ICommandExecutedArgs>;
  readonly keyBindingChanged: ISignal<this, IKeyBindingChangedArgs>;
  readonly keyBindings: ReadonlyArray<IKeyBinding>;

  addCommand(id: string, options: ICommandOptions): IDisposable;
  addKeyBinding(options: IKeyBindingOptions): IDisposable;
  execute(id: string, args?: ReadonlyPartialJSONObject): Promise<any>;
  hasCommand(id: string): boolean;
  listCommands(): string[];
  label(id: string, args?): string;
  icon(id: string, args?): VirtualElement.IRenderer | undefined;
  isEnabled(id: string, args?): boolean;
  isToggled(id: string, args?): boolean;
  isVisible(id: string, args?): boolean;
  notifyCommandChanged(id?: string): void;
  processKeydownEvent(event: KeyboardEvent): boolean;
}
```

### Application（application 包）

```typescript
class Application<T extends Widget = Widget> {
  constructor(options: Application.IOptions<T>);
  readonly commands: CommandRegistry;
  readonly contextMenu: ContextMenu;
  readonly shell: T;
  readonly started: Promise<void>;
  readonly deferredPlugins: string[];

  registerPlugin(plugin: IPlugin<this, any>): void;
  registerPlugins(plugins: IPlugin<this, any>[]): void;
  activatePlugin(id: string): Promise<void>;
  deactivatePlugin(id: string): Promise<string[]>;
  hasPlugin(id: string): boolean;
  isPluginActivated(id: string): boolean;
  listPlugins(): string[];
  resolveRequiredService<U>(token: Token<U>): Promise<U>;
  resolveOptionalService<U>(token: Token<U>): Promise<U | null>;
  start(options?: IStartOptions): Promise<void>;
}
```

### Token / Plugin（coreutils 包）

```typescript
class Token<T> {
  constructor(name: string, description?: string);
  readonly name: string;
  readonly description?: string;
  // 利用 TypeScript 结构化类型系统在运行时捕获编译时类型 T
  private _tokenStructuralPropertyT: T;
}

interface IPlugin<T, U> {
  id: string;
  autoStart?: boolean | 'startUp' | 'defer';
  requires?: Token<any>[];
  optional?: Token<any>[];
  provides?: Token<U>;
  activate: (app: T, ...args: any[]) => U | Promise<U>;
  deactivate?: (app: T, ...args: any[]) => void | Promise<void>;
}
```

### Virtual DOM（virtualdom 包）

```typescript
class VirtualElement {
  readonly type = 'element';
  readonly tag: string;
  readonly attrs: ElementAttrs;
  readonly children: ReadonlyArray<VirtualNode>;
  readonly renderer?: VirtualElement.IRenderer;
}

class VirtualText {
  readonly type = 'text';
  readonly content: string;
}

type VirtualNode = VirtualElement | VirtualText;

function h(tag: string, ...children: h.Child[]): VirtualElement;
function h(tag: string, attrs: ElementAttrs, ...children: h.Child[]): VirtualElement;
// 标签简写
h.div, h.span, h.a, h.button, h.input, h.ul, h.li, h.table, ...等

namespace VirtualDOM {
  function realize(node: VirtualNode): HTMLElement | Text;
  function render(content: VirtualNode | VirtualNode[] | null, host: HTMLElement): void;
}
```

## Widget 生命周期消息序列

```
Widget.attach(widget, host)
  → 'before-attach' (onBeforeAttach)
  → 'after-attach'  (onAfterAttach)
  → 'before-show'   (onBeforeShow)  [如果未隐藏]
  → 'after-show'    (onAfterShow)   [如果未隐藏]
  → 'resize'        (onResize)      [首次尺寸计算]

widget.update()
  → 'update-request' (onUpdateRequest) → 触发重布局/重绘

widget.hide()
  → 'before-hide'   (onBeforeHide)
  → 'after-hide'    (onAfterHide)

widget.show()
  → 'before-show'   (onBeforeShow)
  → 'after-show'    (onAfterShow)
  → 'resize'

Widget.detach(widget)
  → 'before-hide'   [如果可见]
  → 'after-hide'    [如果可见]
  → 'before-detach' (onBeforeDetach)
  → 'after-detach'  (onAfterDetach)

widget.dispose()
  → 从父移除/从DOM分离
  → layout.dispose()
  → title.dispose()
  → Signal.clearData(widget)
  → MessageLoop.clearData(widget)
  → 'disposed' 信号发射
```
