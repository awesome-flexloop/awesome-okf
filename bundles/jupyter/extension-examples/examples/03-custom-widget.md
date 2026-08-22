---
type: Example
title: 示例3：创建自定义Widget
description: 创建一个显示在主工作区的自定义Widget，包含DOM事件监听和工具栏按钮
tags: [example, widget, main-area, toolbar, ReactWidget]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
status: stable
sources:
  - id: react-widget-src
    resource: /references/core-api-tokens.md
    title: react-widget/src/*.tsx
---

## 目标

创建一个主区域Widget，使用React渲染内容，带工具栏按钮，支持鼠标交互。

## 前置知识

- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [信号与事件通信](/concepts/06-signals.md)
- [进阶UI模式](/concepts/14-advanced-ui.md)

## 完整代码

### src/widget.tsx

```tsx
import React, { useState, useCallback } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { CommandToolbarButton } from '@jupyterlab/apputils';

export const CounterComponent = ({
  onReset
}: {
  onReset: () => void;
}): JSX.Element => {
  const [count, setCount] = useState(0);
  const [hover, setHover] = useState(false);

  const handleReset = useCallback(() => {
    setCount(0);
    onReset();
  }, [onReset]);

  return (
    <div className="jp-example-counter">
      <h2>Counter Widget</h2>
      <div
        className="counter-display"
        style={{
          padding: '20px',
          fontSize: '48px',
          textAlign: 'center',
          background: hover ? '#e3f2fd' : '#f5f5f5',
          borderRadius: '8px',
          cursor: 'pointer',
          transition: 'background 0.2s'
        }}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        onClick={() => setCount(c => c + 1)}
      >
        {count}
      </div>
      <p style={{ textAlign: 'center', color: '#666' }}>
        Click the number to increment
      </p>
      <button
        className="jp-Button jp-mod-styled jp-mod-warn"
        onClick={handleReset}
        style={{ display: 'block', margin: '10px auto' }}
      >
        Reset
      </button>
    </div>
  );
};

export class CounterWidget extends ReactWidget {
  private _resetCount: number = 0;

  get resetCount(): number {
    return this._resetCount;
  }

  protected onReset = (): void => {
    this._resetCount++;
    console.log(`Reset clicked! Total resets: ${this._resetCount}`);
  };

  render(): JSX.Element {
    return <CounterComponent onReset={this.onReset} />;
  }
}
```

### src/index.ts

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette, MainAreaWidget, CommandToolbarButton } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { refreshIcon, reactIcon } from '@jupyterlab/ui-components';
import { CounterWidget } from './widget';

const CommandIds = {
  open: 'my-counter:open'
};

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@my-org/counter-widget:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ILauncher],
  activate: (app, palette, launcher) => {
    const { commands, shell } = app;
    const category = 'My Extension';

    commands.addCommand(CommandIds.open, {
      label: 'Open Counter Widget',
      icon: reactIcon,
      execute: () => {
        // 防止重复打开
        let widget = [...shell.widgets('main')].find(
          w => w.id === 'my-counter-widget'
        ) as MainAreaWidget<CounterWidget>;

        if (!widget) {
          const content = new CounterWidget();
          widget = new MainAreaWidget<CounterWidget>({ content });
          widget.id = 'my-counter-widget';
          widget.title.label = 'Counter';
          widget.title.closable = true;
          widget.title.icon = reactIcon;

          // 添加工具栏按钮
          widget.toolbar.addItem('refresh', new CommandToolbarButton({
            commands,
            id: 'my-counter:reset'
          }));

          shell.add(widget, 'main');
        }

        shell.activateById(widget.id);
        return widget;
      }
    });

    palette.addItem({ command: CommandIds.open, category });

    if (launcher) {
      launcher.add({ command: CommandIds.open, category, rank: 1 });
    }
  }
};

export default plugin;
```

## 验证

1. `jlpm build`
2. 刷新JupyterLab
3. 从命令面板执行"Open Counter Widget"或点击Launcher卡片
4. 点击数字递增，悬停变色，Reset按钮重置
5. 工具栏有刷新按钮

## 相关概念

- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [进阶UI模式（React）](/concepts/14-advanced-ui.md)
- [命令系统](/concepts/04-commands.md)
