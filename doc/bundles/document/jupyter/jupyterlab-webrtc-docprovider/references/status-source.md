---
type: Reference
title: 状态栏组件源码（src/status.tsx）
description: WebRtcStatus VDomRenderer组件，在JupyterLab状态栏和RetroLab工具栏中显示协作状态
tags: [status, vdom, react, statusbar, retrolab, ui]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: status-tsx
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/src/status.tsx
    title: src/status.tsx - Status bar component
---

## status.tsx 源码分析

状态栏组件基于 JupyterLab 的 `VDomRenderer` 模式，使用 React/JSX 渲染。

### WebRtcStatus 类

```typescript
export class WebRtcStatus extends VDomRenderer<WebRtcStatus.Model> {
  protected render(): JSX.Element { ... }
}
```

继承自 `VDomRenderer<Model>`，通过 `render()` 方法返回 JSX 元素。

### 渲染逻辑

1. 添加 CSS 类 `jp-WebRTCStatus`
2. 从 model 获取 manager 引用
3. 如果 manager 不存在，返回空片段 `<></>`
4. 提取 `username`、`disabled`、`roomName`、`usercolor`、`peerCount`
5. 根据 disabled 状态选择图标：`shareOffIcon` 或 `shareIcon`
6. 用户名下划线颜色设置为 `usercolor`

**禁用状态渲染**：
```jsx
<div title="Not Sharing">
  <icon.react tag="span" />
</div>
```

**启用状态渲染**：
```jsx
<div title="Sharing with N peers in ROOM as USERNAME">
  <label>{peerCount}</label>
  <icon.react tag="span" />
  <strong style={userStyle}>{roomName}</strong>
</div>
```

- 显示 peer 连接数量
- 显示分享图标
- 显示房间名（带下划线，颜色为用户颜色）
- tooltip 显示完整信息：peer 数量、房间名、用户名

### Model 类

```typescript
export namespace WebRtcStatus {
  export class Model extends VDomModel {
    get manager(): IWebRtcManager | null { ... }
    set manager(manager: IWebRtcManager | null) {
      this._manager = manager;
      this.stateChanged.emit(void 0);
      this._manager?.stateChanged.connect(() => this.stateChanged.emit(void 0));
    }
    private _manager: IWebRtcManager | null = null;
  }
}
```

- 继承自 `VDomModel`
- 设置 manager 时：触发状态变更、连接 manager 的 `stateChanged` 信号
- 当 manager 状态变化时自动触发 VDom 重渲染

### CSS 样式

定义在 `style/base.css`：
- `.jp-WebRTCStatus`: flexbox 水平布局，8px 左右间距
- hover 效果：`var(--jp-layout-color3)` 背景色
- room name 文本：最大宽度 `7 * var(--jp-ui-font-size1)`，溢出省略号

## 相关概念

- [状态栏UI与RetroLab适配](../concepts/07-status-bar.md)
- [4个JupyterLab插件架构](../concepts/06-plugin-system.md)
