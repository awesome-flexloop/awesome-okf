---
type: Example
title: 创建第一个 Widget
description: 创建自定义Widget子类、管理DOM内容、处理生命周期钩子、挂载到页面
tags: [lumino, widget, hello-world, lifecycle, beginner]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: widget-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src/widget.ts
    title: @lumino/widgets Widget 源码
prerequisites:
  - /lumino/concepts/05-widget-lifecycle
  - /lumino/concepts/04-messaging-loop
---

# 示例：创建第一个 Widget

本示例演示如何创建一个自定义 Widget 并挂载到页面上。

## 目标

创建一个简单的问候 Widget，包含标题文本和一个按钮，点击按钮时更新内容。

## 完整代码

```typescript
import { Message, Widget } from '@lumino/widgets';
import '@lumino/default-theme/style/index.css';

// 1. 创建自定义Widget
class GreetingWidget extends Widget {
  private _count = 0;
  private _button: HTMLButtonElement;
  private _message: HTMLParagraphElement;

  constructor() {
    super();
    this.addClass('greeting-widget');
    this.id = 'greeting';
    this.title.label = '问候';
    this.title.closable = true;

    // 构建DOM结构
    this.node.innerHTML = `
      <h2>Hello, Lumino!</h2>
      <p class="message">你点击了 0 次按钮</p>
      <button class="click-btn">点击我</button>
    `;

    this._message = this.node.querySelector('.message')!;
    this._button = this.node.querySelector('.click-btn')!;
  }

  // 2. DOM挂载后添加事件监听
  protected onAfterAttach(msg: Message): void {
    super.onAfterAttach(msg);
    this._button.addEventListener('click', this._onClick);
  }

  // 3. DOM移除前清理事件监听
  protected onBeforeDetach(msg: Message): void {
    this._button.removeEventListener('click', this._onClick);
    super.onBeforeDetach(msg);
  }

  // 4. 处理尺寸变化
  protected onResize(msg: Widget.ResizeMessage): void {
    if (msg.width !== -1) {
      console.log(`Widget 尺寸: ${msg.width} x ${msg.height}`);
    }
  }

  private _onClick = () => {
    this._count++;
    this._message.textContent = `你点击了 ${this._count} 次按钮`;
  };
}

// 5. 创建实例并挂载到页面
function main(): void {
  const widget = new GreetingWidget();
  Widget.attach(widget, document.body);
  console.log('Widget 已挂载到页面');
}

window.addEventListener('DOMContentLoaded', main);
```

## HTML 入口

```html
<!DOCTYPE html>
<html>
<head>
  <title>Lumino Hello World</title>
  <style>
    body { margin: 0; padding: 20px; font-family: sans-serif; }
    .greeting-widget {
      padding: 20px;
      border: 1px solid #ccc;
      border-radius: 4px;
      max-width: 400px;
    }
    .greeting-widget h2 { margin-top: 0; }
    .click-btn {
      padding: 8px 16px;
      font-size: 14px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <script src="bundle.js"></script>
</body>
</html>
```

## 关键点说明

### 1. 构造函数中的初始化

- `super()` 调用父类构造，创建 `<div>` DOM 节点
- `addClass()` 添加 CSS 类（Widget 自动带有 `lm-Widget` 类）
- `this.title` 设置标题信息，供 TabBar/Menu 等容器使用
- 直接操作 `this.node.innerHTML` 构建内部 DOM

### 2. 生命周期钩子配对

**重要原则**：`onAfterAttach` 中添加的事件监听，必须在 `onBeforeDetach` 中移除。否则会导致内存泄漏。

```typescript
// ✅ 正确：配对添加和移除
onAfterAttach() { this.node.addEventListener('click', handler); }
onBeforeDetach() { this.node.removeEventListener('click', handler); }
```

### 3. 使用 Widget.attach() 挂载

不要直接将 `widget.node` appendChild 到 DOM——必须使用 `Widget.attach()`，否则生命周期消息不会被发送，isAttached 状态也不会正确设置。

```typescript
// ❌ 错误：不触发生命周期消息
document.body.appendChild(widget.node);

// ✅ 正确：触发完整生命周期
Widget.attach(widget, document.body);
```

### 4. dispose 清理

```typescript
// 当不再需要Widget时
widget.dispose();
// 自动完成：
// - 从DOM分离node
// - 移除parent引用
// - 清理Signal监听
// - 清理消息队列
// - 释放layout
```

## 运行方式

使用 Vite/webpack 等打包工具：

```bash
# 创建项目
mkdir lumino-hello && cd lumino-hello
npm init -y
npm install @lumino/widgets @lumino/default-theme
npm install -D typescript vite

# 运行
npx vite
```

## 扩展练习

1. 尝试添加 `widget.hide()` 和 `widget.show()` 方法切换显示
2. 在 `onCloseRequest` 中添加确认对话框
3. 使用 `widget.update()` 触发 `onUpdateRequest` 重绘
4. 添加一个 Signal 在点击次数变化时通知外部
