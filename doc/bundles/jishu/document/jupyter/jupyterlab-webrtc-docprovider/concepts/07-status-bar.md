---
type: Concept
title: 状态栏UI与RetroLab适配
description: WebRtcStatus是基于VDomRenderer的React状态栏组件，在JupyterLab状态栏和RetroLab工具栏中显示peer数量、共享图标和房间名
tags: [status-bar, vdom, react, ui, retrolab, toolbar, widget-extension, css]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: status-src
    resource: /references/status-source.md
    title: src/status.tsx - Status bar component
  - id: icons-src
    resource: /references/icons-schema-source.md
    title: src/icons.ts - Icon definitions
  - id: plugin-src
    resource: /references/plugin-source.md
    title: src/plugin.ts - Plugin registration including status plugins
---

## WebRtcStatus 组件架构

`WebRtcStatus` 采用 JupyterLab 的 **VDom（Virtual DOM）** 模式，这是 JupyterLab 中基于 React 的轻量级 UI 组件模式。

```
VDomRenderer<Model> (JupyterLab/VirtualDOM)
    │  提供：React 渲染、生命周期管理、信号驱动更新
    │
    ▼
WebRtcStatus
    │  render(): JSX.Element  →  根据 manager 状态渲染 UI
    │
    └── Model (extends VDomModel)
           manager: IWebRtcManager  →  连接 stateChanged 信号
```

## VDomRenderer 模式

JupyterLab 的 `VDomRenderer<T>` 是一个抽象类：
- 泛型参数 `T` 是 Model 类型，必须继承 `VDomModel`
- 子类实现 `render()` 方法返回 JSX 元素
- Model 的 `stateChanged` 信号触发自动重渲染

## WebRtcStatus 渲染逻辑

```typescript
protected render(): JSX.Element {
  this.addClass('jp-WebRTCStatus');
  const { manager } = this.model;
  if (!manager) return <></>;

  const { username, disabled, roomName, usercolor, peerCount } = manager;
  const icon = disabled ? shareOffIcon : shareIcon;
  const userStyle = { textDecoration: 'underline', textDecorationColor: usercolor };

  const title = disabled
    ? 'Not Sharing'
    : `Sharing with ${peerCount} peers in ${roomName} as ${username}`;

  return disabled ? (
    <div title={title}>
      <icon.react tag="span" />
    </div>
  ) : (
    <div title={title}>
      <label>{peerCount}</label>
      <icon.react tag="span" />
      <strong style={userStyle}>{roomName}</strong>
    </div>
  );
}
```

### 两种显示状态

**禁用状态**：
- 只显示 `shareOffIcon`（灰色分享关闭图标）
- tooltip: "Not Sharing"
- 不显示 peer 数和房间名

**启用状态**：
- 显示 peer 连接数（`<label>` 元素）
- 显示 `shareIcon`（蓝色分享图标）
- 显示房间名（`<strong>` 元素），文字带下划线，颜色为用户颜色
- tooltip: "Sharing with N peers in ROOM as USERNAME"

### 图标组件

使用 LabIcon 的 `.react` 属性创建 React 元素：

```jsx
<icon.react tag="span" />
```

`tag="span"` 指定渲染为 `<span>` 元素而非默认标签。

### 用户颜色下划线

房间名的下划线颜色被设置为用户的光标颜色，提供视觉上的身份标识：

```typescript
const userStyle = { textDecoration: 'underline', textDecorationColor: usercolor };
```

## Model 类

```typescript
export class Model extends VDomModel {
  get manager(): IWebRtcManager | null { return this._manager; }

  set manager(manager: IWebRtcManager | null) {
    this._manager = manager;
    this.stateChanged.emit(void 0);                     // 立即触发重渲染
    this._manager?.stateChanged.connect(
      () => this.stateChanged.emit(void 0)              // 连接状态变更信号
    );
  }

  private _manager: IWebRtcManager | null = null;
}
```

### 信号连接模式

Model 设置 manager 时执行两个动作：
1. **立即触发重渲染**：`stateChanged.emit(void 0)` 确保组件初始渲染
2. **连接状态信号**：`manager.stateChanged.connect(...)` 当 manager 状态变化时自动重渲染

这是 JupyterLab VDom 组件的标准模式——Model 监听数据变化信号，自动驱动 UI 更新。

## 三个图标定义

```typescript
export const webrtcIcon = new LabIcon({
  name: 'webrtc-docprovider:webrtc',
  svgstr: WEBRTC_SVG,
});
export const shareIcon = new LabIcon({
  name: 'webrtc-docprovider:share',
  svgstr: SHARE_SVG,
});
export const shareOffIcon = new LabIcon({
  name: 'webrtc-docprovider:share-off',
  svgstr: SHARE_OFF_SVG,
});
```

| 图标 | 用途 | 位置 |
|------|------|------|
| `webrtcIcon` | 设置面板图标、命令图标 | 设置编辑器、命令面板 |
| `shareIcon` | 分享启用状态 | 状态栏启用状态 |
| `shareOffIcon` | 分享禁用状态 | 状态栏禁用状态 |

SVG 文件位于 `style/img/` 目录。

## CSS 样式

```css
.jp-WebRTCStatus,
.jp-WebRTCStatus div {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: calc(var(--jp-ui-font-size0) * 0.5);
  flex-direction: row;
  font-size: var(--jp-ui-font-size1);
  padding: 0 calc(var(--jp-ui-font-size0) * 0.5);
}

.jp-WebRTCStatus:hover {
  background-color: var(--jp-layout-color3);
}

.jp-WebRTCStatus strong {
  max-width: calc(7 * var(--jp-ui-font-size1));
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}
```

### 样式要点

- 使用 **flexbox** 水平布局，内容居中对齐
- 间距使用 JupyterLab CSS 变量（`--jp-ui-font-size0/1`）
- **hover 效果**：鼠标悬停时背景色变化（`--jp-layout-color3`）
- **房间名截断**：`max-width` 限制为约7个字符宽度，超出部分省略号显示
- 使用 JupyterLab 设计系统的颜色变量，自动适配明暗主题

## RetroLab 工具栏适配

RetroLab（现称 Notebook 7 前身）没有底部状态栏，因此需要将状态组件添加到工具栏：

```typescript
const retropage = PageConfig.getOption('retroPage');
if (!retropage) return;  // 非 RetroLab 环境

const ext: DocumentRegistry.IWidgetExtension<any, any> = {
  createNew: (widget) => {
    const toolbar = (widget as any).toolbar as Toolbar;
    if (!toolbar) return;

    const model = new WebRtcStatus.Model();
    model.manager = manager;
    const item = new WebRtcStatus(model);

    if (retropage === RETRO_EDIT_PAGE) {
      toolbar.addItem(`${RETRO_STATUS_PLUGIN_ID}-spacer`, Toolbar.createSpacerItem());
    }
    toolbar.addItem(RETRO_STATUS_PLUGIN_ID, item);
    return new DisposableDelegate(() => item.dispose());
  },
};

app.docRegistry.addWidgetExtension('Notebook', ext);
app.docRegistry.addWidgetExtension('Editor', ext);
```

### RetroLab 适配要点

1. **环境检测**：通过 `PageConfig.getOption('retroPage')` 判断是否在 RetroLab 中
2. **Widget Extension 模式**：使用 `DocumentRegistry.IWidgetExtension` 在 widget 创建时添加工具栏项
3. **Editor 页面 Spacer**：编辑器页面添加 spacer 项将状态推到右侧，Notebook 页面不需要（已有其他项占据左侧空间）
4. **生命周期管理**：返回 `DisposableDelegate` 在 widget 销毁时清理组件
5. **双文档类型**：同时注册到 'Notebook' 和 'Editor' 类型

### JupyterLab vs RetroLab 位置对比

| 环境 | 位置 | 注册方式 | 插件 |
|------|------|---------|------|
| JupyterLab | 底部状态栏右侧 | `status.registerStatusItem()` | statusPlugin |
| RetroLab | Notebook/Editor 工具栏 | `docRegistry.addWidgetExtension()` | retroStatusPlugin |

两个插件使用**同一个** `WebRtcStatus` 组件类和 `WebRtcStatus.Model`，仅注册位置和容器不同。

## Toggle 命令

命令面板中的 "Toggle WebRTC Sharing" 命令（ID: `webrtc-docprovider:disable`）：

```typescript
commands.addCommand(CommandIds.disable, {
  isToggleable: true,
  icon: webrtcIcon,
  label: 'Toggle WebRTC Sharing',
  isToggled: () => !settings.composite.disabled,
  execute: () => settings.set('disabled', !settings.composite.disabled),
});
```

- `isToggleable: true`：标记为切换命令
- `isToggled()`：返回当前是否启用（非 disabled）
- `execute()`：切换 disabled 状态
- 设置变更触发 `settings.changed` 信号 → manager 监听 → stateChanged → UI 自动更新

## 相关概念

- [4个JupyterLab插件架构](06-plugin-system.md)
- [WebRtcManager配置管理](03-webrtc-manager.md)
- [架构总览](02-architecture-overview.md)
