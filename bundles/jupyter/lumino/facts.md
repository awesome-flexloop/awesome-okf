---
type: Facts
okf_version: '0.2'
title: lumino 源码事实清单
tags:
- jupyter
- lumino
- typescript
- widget
- ui-framework
- phosphorjs
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/lumino/package.json
- ../../../../../external/libs/jupyter/lumino/packages/disposable/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/messaging/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/signaling/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/widgets/src/widget.ts
- ../../../../../external/libs/jupyter/lumino/packages/commands/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/application/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/coreutils/src/plugins.ts
- ../../../../../external/libs/jupyter/lumino/packages/coreutils/src/token.ts
- ../../../../../external/libs/jupyter/lumino/packages/keyboard/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/widgets/src/dockpanel.ts
- ../../../../../external/libs/jupyter/lumino/packages/datagrid/src/datagrid.ts
- ../../../../../external/libs/jupyter/lumino/packages/coreutils/src/promise.ts
- ../../../../../external/libs/jupyter/lumino/packages/properties/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/collections/src/linkedlist.ts
- ../../../../../external/libs/jupyter/lumino/packages/virtualdom/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/widgets/src/commandpalette.ts
- ../../../../../external/libs/jupyter/lumino/packages/algorithm/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/domutils/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/dragdrop/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/polling/src/index.ts
- ../../../../../external/libs/jupyter/lumino/packages/widgets/src/layout.ts
- ../../../../../external/libs/jupyter/lumino/packages/widgets/src/tabbar.ts
- ../../../../../external/libs/jupyter/lumino/packages/widgets/src/menu.ts
---

# Lumino 源码事实清单

## 项目元数据

- F-001: package.json:2 — 项目名 `lumino-top-level`，标记为 `"private": true`，是一个 Yarn workspaces monorepo。
- F-002: package.json:3 — 版本号 `2026.7.3`。
- F-003: package.json:5-8 — workspaces 包含 `examples/*`、`packages/*`、`buildutils` 三个目录。
- F-004: package.json:74 — 包管理器锁定为 `yarn@3.6.0`。
- F-005: package.json:44-58 — 开发依赖包括 TypeScript ~5.1.3、Rollup、Playwright、ESLint、Prettier、Typedoc、Lerna ^7.1.4、Husky ^8.0.0。
- F-006: package.json:23-24 — 使用 ESLint + Prettier 进行代码风格检查与格式化，ESLint 配置为 `--cache --fix`。
- F-007: package.json:32 — 发布流程：`yarn clean && yarn build:dist && node scripts/tag-versions.js && lerna publish --yes -m "Publish" from-package`。
- F-008: package.json:34-38 — 测试支持 Chromium、Firefox、WebKit 三浏览器，通过 Playwright 驱动，使用 `--no-bail --concurrency 1` 串行执行。
- F-009: package.json:60-73 — 集成 jupyter-releaser，在 `after-build-changelog` 和 `before-build-npm` 钩子中自动执行 `yarn build:dist`。

## 包结构与模块划分

- F-010: packages/ 目录包含 19 个包：algorithm、application、collections、commands、coreutils、datagrid、default-theme、disposable、domutils、dragdrop、keyboard、messaging、polling、properties、signaling、virtualdom、widgets，以及 tests 目录（每个包有独立的 tests/）。
- F-011: packages/signaling/ — Signal/Slot 发布-订阅机制，是 Lumino 事件系统的核心。
- F-012: packages/messaging/ — 消息循环与消息传递机制，是 Widget 生命周期的基础。
- F-013: packages/disposable/ — IDisposable 模式实现，提供资源生命周期管理。
- F-014: packages/commands/ — 命令注册表与键盘快捷键绑定系统。
- F-015: packages/widgets/ — Widget 基类、布局系统、DockPanel、Menu、TabBar、CommandPalette 等 UI 组件，是最大的包。
- F-016: packages/application/ — 应用壳与插件系统，依赖 CommandRegistry、ContextMenu、PluginRegistry、Widget。
- F-017: packages/coreutils/ — Token（类型标记）、PluginRegistry、PromiseDelegate、JSONExt、MimeData、UUID 等基础工具。
- F-018: packages/datagrid/ — 基于 Canvas 的高性能表格组件，使用 SectionList 管理行列尺寸，支持单元格渲染器、选择模型和单元格编辑。
- F-019: packages/virtualdom/ — 轻量 Virtual DOM 实现，提供 `h()` 函数创建 VirtualElement，支持 HTML 属性、ARIA 属性和 SVG 属性。
- F-020: packages/keyboard/ — 键盘布局抽象，基于 keyCode 提供 EN_US 布局映射，支持自定义键盘布局。
- F-021: packages/algorithm/ — 算法工具集：ArrayExt（数组操作）、StringExt（字符串操作）、iter/chain/filter/map/reduce/range/zip 等迭代器工具、topologicSort（拓扑排序）。
- F-022: packages/collections/ — LinkedList 双向链表实现，支持 Iterable 和反向迭代（IRetroable）。
- F-023: packages/properties/ — AttachedProperty 附加属性机制，通过 WeakMap 在外部对象上附加值，支持 create/coerce/compare/changed 回调。
- F-024: packages/domutils/ — DOM 工具：Platform 检测、Selector 匹配、ElementExt 尺寸/滚动计算、ClipboardExt 剪贴板操作。
- F-025: packages/dragdrop/ — Drag 拖拽支持，提供 IDragEvent 和 Drag 类。
- F-026: packages/polling/ — Poll 轮询器和 RateLimiter 限流器，用于周期性任务和节流。
- F-027: packages/default-theme/ — 默认 CSS 主题，包含 accordionpanel、commandpalette、datagrid、dockpanel、menu、menubar、scrollbar、tabbar 等组件样式。

## Disposable 模式（@lumino/disposable）

- F-028: packages/disposable/src/index.ts:19-40 — `IDisposable` 接口定义 `isDisposed: boolean` 和 `dispose(): void`；dispose 多次调用为 no-op。
- F-029: packages/disposable/src/index.ts:45-50 — `IObservableDisposable` 扩展 IDisposable，增加 `disposed: ISignal<this, void>` 信号。
- F-030: packages/disposable/src/index.ts:55-85 — `DisposableDelegate` 将 dispose 委托给回调函数 fn；dispose 后将 fn 置 null，防止重复执行。
- F-031: packages/disposable/src/index.ts:90-114 — `ObservableDisposableDelegate` 在 dispose 时 emit disposed 信号，并调用 `Signal.clearData(this)` 清理信号数据。
- F-032: packages/disposable/src/index.ts:119-188 — `DisposableSet` 管理一组 IDisposable，以 Set 存储；dispose 时按添加顺序逐一 dispose，然后 clear。
- F-033: packages/disposable/src/index.ts:14 — disposable 包依赖 `@lumino/signaling` 中的 ISignal 和 Signal。
- F-034: packages/disposable/src/index.ts:213-240 — `ObservableDisposableSet` 在 dispose 时 emit disposed 信号并清理 Signal 数据。

## Messaging 消息系统（@lumino/messaging）

- F-035: packages/messaging/src/index.ts:24-101 — `Message` 类包含 `type: string`，支持 `isConflatable` 属性和 `conflate()` 方法实现消息合并；默认为不可合并。
- F-036: packages/messaging/src/index.ts:116-136 — `ConflatableMessage` 自动可合并的消息类，`isConflatable` 始终返回 true，`conflate()` 始终返回 true。
- F-037: packages/messaging/src/index.ts:148-155 — `IMessageHandler` 接口定义 `processMessage(msg: Message): void`。
- F-038: packages/messaging/src/index.ts:173-185 — `IMessageHook` 接口定义 `messageHook(handler, msg): boolean`，返回 false 阻止消息传递；支持对象和函数两种形式（MessageHook 类型别名）。
- F-039: packages/messaging/src/index.ts:201-641 — `MessageLoop` 命名空间实现全局单例消息循环，使用 Promise.resolve().then() 调度异步处理。
- F-040: packages/messaging/src/index.ts:241-260 — `sendMessage()` 立即同步处理消息：先执行 hooks（最新安装的优先），全部通过后调用 handler.processMessage。
- F-041: packages/messaging/src/index.ts:276-304 — `postMessage()` 异步投递消息：可合并消息尝试 conflate，未合并则入队；不可合并消息直接入队。
- F-042: packages/messaging/src/index.ts:322-340 — `installMessageHook()` 安装消息钩子，追加到数组末尾（执行时从后往前，即最新优先）；重复安装为 no-op。
- F-043: packages/messaging/src/index.ts:475-483 — 消息队列使用 `LinkedList<PostedMessage>`，消息钩子使用 `WeakMap<IMessageHandler, Array<MessageHook|null>>`。
- F-044: packages/messaging/src/index.ts:565-596 — 消息循环使用哨兵值（sentinel）机制：每轮处理前在队列末尾插入哨兵，处理到哨兵即停止，确保运行中新增的消息在下一轮处理。
- F-045: packages/messaging/src/index.ts:214-223 — 异步调度函数通过 `Promise.resolve()` 实现，返回取消函数可阻止回调执行。
- F-046: packages/messaging/src/index.ts:415-429 — `flush()` 立即处理所有待处理消息，使用 flushGuard 标志防止递归。
- F-047: packages/messaging/src/index.ts:385-402 — `clearData(handler)` 清除指定 handler 的所有消息钩子和队列中待处理消息。
- F-048: packages/messaging/src/index.ts:493-495 — 默认异常处理器为 `console.error`，可通过 setExceptionHandler 替换。

## Signaling 信号系统（@lumino/signaling）

- F-049: packages/signaling/src/index.ts:27 — `Slot<T, U>` 类型为 `(sender: T, args: U) => void`，即接收 sender 和 args 的回调。
- F-050: packages/signaling/src/index.ts:38-79 — `ISignal<T, U>` 接口定义 connect/disconnect 方法；连接具有唯一性（同 slot+thisArg 重复连接返回 false），按连接顺序同步调用。
- F-051: packages/signaling/src/index.ts:84 — `IStream<T, U>` 同时继承 ISignal 和 AsyncIterable<U>，支持信号与异步迭代器双模式。
- F-052: packages/signaling/src/index.ts:135-191 — `Signal<T, U>` 类持有 sender 对象，connect/disconnect/emit 委托给 Private 命名空间实现。
- F-053: packages/signaling/src/index.ts:209-261 — Signal 命名空间提供 disconnectBetween、disconnectSender、disconnectReceiver、disconnectAll、clearData 静态方法用于批量断开连接。
- F-054: packages/signaling/src/index.ts:343-382 — `Stream<T, U>` 扩展 Signal 实现 IStream，通过 PromiseDelegate 链式结构实现 async iterator；emit 时 resolve 当前 pending 并创建新 PromiseDelegate；stop() 方法 reject 当前 pending 终止迭代。
- F-055: packages/signaling/src/index.ts:668-673 — 信号连接使用双向 WeakMap 存储：receiversForSender（sender→connections）和 sendersForReceiver（receiver→connections），确保 GC 自动回收。
- F-056: packages/signaling/src/index.ts:626-641 — emit 时遍历 receivers 数组（长度在 emit 开始时快照，新连接不在当前 emit 中触发），异常被捕获并通过 exceptionHandler 记录。
- F-057: packages/signaling/src/index.ts:683-686 — 异步清理优先使用 requestAnimationFrame，回退到 setImmediate（Node.js 环境）。
- F-058: packages/signaling/src/index.ts:490-492 — disconnect 时将 connection.signal 设为 null，通过 scheduleCleanup 异步清理死连接。
- F-059: packages/signaling/src/index.ts:15 — signaling 包依赖 `@lumino/algorithm`（ArrayExt、find）和 `@lumino/coreutils`（PromiseDelegate）。

## Widget 基类（@lumino/widgets Widget）

- F-060: packages/widgets/src/widget.ts:36 — `Widget` 类实现 IMessageHandler 和 IObservableDisposable 接口，构造时创建 DOM 节点（默认 `<div>`），添加 CSS 类 `lm-Widget`。
- F-061: packages/widgets/src/widget.ts:55-85 — dispose() 方法流程：标记 IsDisposed → emit disposed → 从父移除或 detach → dispose layout → dispose title → 清理 Signal/Message/AttachedProperty 数据。
- F-062: packages/widgets/src/widget.ts:109-111 — `isAttached` 通过 Flag.IsAttached 位标志判断节点是否已挂载到 DOM。
- F-063: packages/widgets/src/widget.ts:134-144 — `isVisible` 自 2.7.0 起递归检查所有祖先：自身不隐藏、已挂载，且所有父级都可见（不再依赖 IsVisible 标志）。
- F-064: packages/widgets/src/widget.ts:185-214 — `hiddenMode` 支持三种模式：Display（添加 lm-mod-hidden CSS 类）、Scale（transform: scale(0) + aria-hidden）、ContentVisibility（content-visibility: hidden + z-index:-1 + opacity:0）。
- F-065: packages/widgets/src/widget.ts:234-253 — `parent` setter 发送 child-removed/child-added 消息通知旧父和新父，并向自身发送 ParentChanged 消息；禁止循环父子关系。
- F-066: packages/widgets/src/widget.ts:271-286 — `layout` 为单次赋值属性，设置后不可更改；设置 DisallowLayout 标志的 widget 不能设置 layout。
- F-067: packages/widgets/src/widget.ts:542-616 — `processMessage` 处理 15 种消息类型：resize、update-request、fit-request、before-show、after-show、before-hide、after-hide、before-attach、after-attach、before-detach、after-detach、activate-request、close-request、child-added、child-removed；每种消息先 notifyLayout 再调用对应的 on* 处理器。
- F-068: packages/widgets/src/widget.ts:640-646 — `onCloseRequest` 默认实现：有 parent 则从 parent 移除（parent=null），已挂载则 detach。
- F-069: packages/widgets/src/widget.ts:391-423 — 便捷方法：update() 投递 update-request、fit() 投递 fit-request、activate() 投递 activate-request、close() 发送 close-request。
- F-070: packages/widgets/src/widget.ts:433-477 — show()/hide() 方法发送 before-show/after-show 或 before-hide/after-hide 消息，并向 parent 发送 child-shown/child-hidden 消息。
- F-071: packages/widgets/src/widget.ts:504-532 — 标志位系统使用位运算：testFlag（&）、setFlag（|）、clearFlag（&~）；Flag 枚举包含 IsDisposed、IsAttached、IsHidden、IsVisible（已废弃）、DisallowLayout。
- F-072: packages/widgets/src/widget.ts:849 — HiddenMode 枚举：Display=0、Scale=1、ContentVisibility=2。
- F-073: packages/widgets/src/widget.ts:822-830 — Widget.IOptions 支持传入已有的 HTMLElement（node）或标签名（tag，默认 div）。

## Command Registry（@lumino/commands）

- F-074: packages/commands/src/index.ts:39 — `CommandRegistry` 管理命令集合，提供 commandChanged、commandExecuted、keyBindingChanged 三个信号。
- F-075: packages/commands/src/index.ts:111-134 — `addCommand(id, options)` 注册命令，id 重复则抛错；返回 DisposableDelegate 用于移除命令；注册/移除时 emit commandChanged 信号。
- F-076: packages/commands/src/index.ts:167-175 — `describedBy(id, args)` 返回命令描述 Promise，支持异步描述（如从 JSON Schema 生成参数文档）。
- F-077: packages/commands/src/index.ts:427-453 — `execute(id, args)` 执行命令并返回 Promise；异常被捕获并 reject；执行后 emit commandExecuted 信号。
- F-078: packages/commands/src/index.ts:476-494 — `addKeyBinding(options)` 注册键盘快捷键；同序列多个绑定时，选择器特异性最高的优先，同特异性则最新添加的优先；使用 DisposableDelegate 返回移除函数。
- F-079: packages/commands/src/index.ts:467-474 — 和弦键（chord）使用超时消歧：如同时存在 `Ctrl D` 和 `Ctrl D Ctrl W`，按下 Ctrl D 后启动定时器等待和弦完成，超时则执行单键绑定。
- F-080: packages/commands/src/index.ts:513-599 — `processKeydownEvent(event)` 处理键盘事件流程：规范化按键→过滤纯修饰键→匹配 exact/partial→部分匹配时存储事件等待→精确匹配且无部分匹配时立即执行→exact+partial 时启动定时器。
- F-081: packages/commands/src/index.ts:26 — CommandRegistry 依赖 `@lumino/keyboard` 的 getKeyboardLayout 获取键盘布局。
- F-082: packages/commands/src/index.ts:30 — CommandRegistry 依赖 `@lumino/virtualdom` 的 VirtualElement 用于命令标签渲染。
- F-083: packages/commands/src/index.ts:510-511 — 若事件目标或祖先有 `data-lm-suppress-shortcuts` 属性，则不触发快捷键命令。

## Application 应用壳（@lumino/application）

- F-084: packages/application/src/index.ts:42-60 — `Application<T extends Widget>` 构造时创建 CommandRegistry、ContextMenu，接收 shell widget 和可选的 PluginRegistry。
- F-085: packages/application/src/index.ts:282-302 — `start()` 方法流程：防止重复启动→标记 _started→激活 startup plugins→attachShell→addEventListeners→resolve started Promise。
- F-086: packages/application/src/index.ts:106-108 — `activateDeferredPlugins()` 激活所有 autoStart='defer' 的插件。
- F-087: packages/application/src/index.ts:357-362 — 默认事件监听：document 上监听 contextmenu、keydown、keyup；window 上监听 resize；keydown/keyup 默认在捕获阶段（!bubblingKeydown）。
- F-088: packages/application/src/index.ts:403-411 — evtContextMenu：按住 Shift 键时打开浏览器默认菜单；否则尝试打开应用上下文菜单，成功则 preventDefault+stopPropagation。
- F-089: packages/application/src/index.ts:421-423 — evtResize 默认调用 shell.update()。
- F-090: packages/application/src/index.ts:341-346 — attachShell：若提供 hostID 则挂载到对应元素，否则挂载到 document.body。
- F-091: packages/application/src/index.ts:199-201 — `registerPlugin(plugin)` 委托给 pluginRegistry.registerPlugin，重复 ID 或循环依赖会抛错。

## Plugin Registry（@lumino/coreutils）

- F-092: packages/coreutils/src/plugins.ts:25-117 — `IPlugin<T, U>` 接口定义：id（唯一）、description、autoStart（boolean|'defer'）、requires（Token[]）、optional（Token[]）、provides（Token|null）、activate 函数、可选 deactivate 函数。
- F-093: packages/coreutils/src/token.ts:18-47 — `Token<T>` 类在运行时捕获编译时类型信息，通过私有属性 `_tokenStructuralPropertyT` 实现类型标记；用于服务的类型安全依赖注入。
- F-094: packages/coreutils/src/plugins.ts:122-500 — `PluginRegistry` 管理插件注册、激活、停用、服务解析；使用 Map 存储 plugins 和 services（Token→pluginId 映射）。
- F-095: packages/coreutils/src/plugins.ts:285-325 — activatePlugin 流程：检查已注册→已激活则直接返回→有 pending promise 则返回→解析 required 和 optional 服务→Promise.all 并行获取→调用 activate→存储 service→标记 activated。
- F-096: packages/coreutils/src/plugins.ts:373-419 — deactivatePlugin 检查所有下游依赖插件是否支持 deactivate，按拓扑逆序逐一 deactivate，返回被停用的插件 ID 列表。
- F-097: packages/coreutils/src/plugins.ts:440-454 — resolveRequiredService：无 provider 则抛 TypeError；未激活则自动激活；返回单例 service。
- F-098: packages/coreutils/src/plugins.ts:475-494 — resolveOptionalService：无 provider 返回 null；激活失败 catch 后返回 null；否则返回 service。
- F-099: packages/coreutils/src/plugins.ts:720-759 — ensureNoCycle 使用 DFS 检测循环依赖，检测到则 throw ReferenceError 并输出 trace 路径。
- F-100: packages/coreutils/src/plugins.ts:823 — 插件激活排序使用 `@lumino/algorithm` 的 topologicSort 拓扑排序。
- F-101: packages/coreutils/src/plugins.ts:356 — startup 插件激活失败不阻塞其他插件，错误通过 console.error 记录。

## Keyboard Layout（@lumino/keyboard）

- F-102: packages/keyboard/src/index.ts:18-71 — `IKeyboardLayout` 接口定义 keys()、isValidKey()、isModifierKey()、keyForKeydownEvent() 方法。
- F-103: packages/keyboard/src/index.ts:81-96 — getKeyboardLayout/setKeyboardLayout 管理全局键盘布局实例，默认为 EN_US。
- F-104: packages/keyboard/src/index.ts:109-181 — `KeycodeLayout` 基于 keyCode 的布局实现，接收 CodeMap（keycode→key 映射）和 modifierKeys 数组。
- F-105: packages/keyboard/src/index.ts:249-353 — EN_US 布局为预定义 KeycodeLayout 实例，映射 0-9、A-Z、F1-F12、方向键、修饰键（Shift/Ctrl/Alt/Meta）、数字键盘和标点符号的 keycode 到键名。

## DockPanel（@lumino/widgets）

- F-106: packages/widgets/src/dockpanel.ts:39 — `DockPanel` 继承 Widget，提供灵活的停靠区域，支持多文档模式（multiple-document）和单文档模式（single-document）。
- F-107: packages/widgets/src/dockpanel.ts:45-82 — 构造函数创建 DockLayout 作为布局，设置 renderer（createTabBar/createHandle），添加 Overlay 拖放指示器。
- F-108: packages/widgets/src/dockpanel.ts:128-130 — `layoutModified` 信号在布局配置变更时异步合并触发（多次同步修改只触发一次）。
- F-109: packages/widgets/src/dockpanel.ts:136-138 — `addRequested` 信号在 TabBar 添加按钮被点击时触发。
- F-110: packages/widgets/src/dockpanel.ts:63 — dataset['mode'] 属性反映当前停靠模式。
- F-111: packages/widgets/src/dockpanel.ts:87-101 — dispose 时释放鼠标、隐藏 overlay、取消进行中的拖拽、调用 super.dispose()。

## DataGrid（@lumino/datagrid）

- F-112: packages/datagrid/src/datagrid.ts:59 — `DataGrid` 继承 Widget，实现高性能 Canvas 绘制的表格组件，文档明确标注"不适合子类化"。
- F-113: packages/datagrid/src/datagrid.ts:65-100 — 内部使用三个 Canvas（主 canvas、缓冲 buffer、叠加 overlay），通过 SectionList 管理行高、列宽、行表头宽、列表头高。
- F-114: packages/datagrid/src/datagrid.ts:127-149 — DataGrid 由 viewport、vScrollBar、hScrollBar、scrollCorner 四个内部 Widget 组合而成；为 viewport 和 scrollBar 安装 MessageHook。
- F-115: packages/datagrid/src/datagrid.ts:134 — CellEditorController 管理单元格编辑交互。

## PromiseDelegate & 其他核心工具

- F-116: packages/coreutils/src/promise.ts:18-56 — `PromiseDelegate<T>` 将 Promise 的 resolve/reject 暴露为方法，适用于 resolve/reject 逻辑无法在 Promise 构造器内定义的场景。
- F-117: packages/properties/src/index.ts:29 — `AttachedProperty<T, U>` 通过 WeakMap 将值附加到外部对象，支持 create（默认值工厂）、coerce（值转换）、compare（变更检测）、changed（变更回调）四个钩子。
- F-118: packages/collections/src/linkedlist.ts:15 — `LinkedList<T>` 实现双向链表，支持 O(1) 的 addFirst/addLast/removeFirst/removeLast，同时实现 Iterable 和 IRetroable（反向迭代）。
- F-119: packages/virtualdom/src/index.ts:29-125 — VirtualDOM 预定义了 96 个 HTML5 属性名（ElementAttrNames 类型），包括 abbr 到 wrap 的标准属性。
- F-120: packages/widgets/src/commandpalette.ts:32 — `CommandPalette` 继承 Widget，监听 CommandRegistry 的 commandChanged 和 keyBindingChanged 信号自动刷新；设置 DisallowLayout 标志。
