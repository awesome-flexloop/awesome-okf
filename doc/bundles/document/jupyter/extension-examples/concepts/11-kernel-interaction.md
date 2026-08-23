---
type: Concept
title: Kernel交互
description: 创建Kernel会话、执行代码、通过KernelMessage接收输出，实现前端与Kernel的双向通信
tags: [jupyterlab, kernel, messaging, ISessionContext, execute, KernelMessage]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: kernel-panel-src
    resource: /references/core-api-tokens.md
    title: kernel-messaging/src/panel.ts SessionContext创建
  - id: kernel-model-src
    resource: /references/core-api-tokens.md
    title: kernel-messaging/src/model.ts 代码执行与消息接收
---

## Kernel交互架构

JupyterLab扩展可以与Jupyter Kernel（如IPython）通信，执行代码并接收输出。核心流程：

1. 创建 `SessionContext`（管理kernel会话生命周期）
2. 初始化session并选择kernel
3. 通过 `sessionContext.session.kernel` 发送execute请求
4. 通过IOPub消息流接收输出结果

kernel-messaging示例完整演示了此模式。

## 创建SessionContext

```typescript
import { SessionContext, ISessionContext, SessionContextDialogs } from '@jupyterlab/apputils';
import { ServiceManager } from '@jupyterlab/services';

class ExamplePanel extends StackedPanel {
  constructor(manager: ServiceManager.IManager, translator?: ITranslator) {
    super();

    // 1. 创建SessionContext
    this._sessionContext = new SessionContext({
      sessionManager: manager.sessions,      // 会话管理器
      specsManager: manager.kernelspecs,     // Kernel规格管理器
      name: 'Extension Examples'             // 会话名称
    });

    // 2. 创建model和view
    this._model = new KernelModel(this._sessionContext);
    this._example = new KernelView(this._model);
    this.addWidget(this._example);

    // 3. 创建Kernel选择对话框
    this._sessionContextDialogs = new SessionContextDialogs({ translator });

    // 4. 初始化session
    void this._sessionContext.initialize().then(async value => {
      if (value) {
        // 如果需要选择kernel，弹出对话框
        await this._sessionContextDialogs.selectKernel(this._sessionContext);
      }
    }).catch(reason => {
      console.error(`Failed to initialize session.\n${reason}`);
    });
  }

  get session(): ISessionContext {
    return this._sessionContext;
  }

  dispose(): void {
    this._sessionContext.dispose();  // 必须清理session
    super.dispose();
  }

  private _sessionContext: SessionContext;
}
```

### 获取ServiceManager

在插件activate函数中通过 `app.serviceManager` 获取：

```typescript
function activate(app: JupyterFrontEnd, palette, translator, launcher) {
  const manager = app.serviceManager;  // IServiceManager实例

  async function createPanel(): Promise<ExamplePanel> {
    const panel = new ExamplePanel(manager, translator);
    shell.add(panel, 'main');
    return panel;
  }
}
```

## 执行代码并接收输出

KernelModel类封装了kernel通信逻辑：

```typescript
import { ISessionContext } from '@jupyterlab/apputils';
import { KernelMessage } from '@jupyterlab/services';

class KernelModel {
  constructor(sessionContext: ISessionContext) {
    this._sessionContext = sessionContext;
  }

  private _onKernelStatusChanged = () => {
    this.stateChanged.emit(void 0);  // 通知UI kernel状态变化
  };

  async execute(code: string): Promise<void> {
    // 获取kernel引用（可能还未就绪）
    const kernel = this._sessionContext.session?.kernel;
    if (!kernel) {
      throw new Error('Kernel not available.');
    }

    // 发送execute请求，返回Future对象
    const future = kernel.requestExecute({
      code: code,
      silent: false,
      store_history: true,
      stop_on_error: true,
      allow_stdin: false
    });

    // 监听IOPub消息（输出、状态更新等）
    future.onIOPub = (msg: KernelMessage.IIOPubMessage) => {
      const msgType = msg.header.msg_type;
      switch (msgType) {
        case 'execute_result':
          // 执行结果（print输出、表达式返回值）
          const result = msg.content as KernelMessage.IExecuteResultMsg['content'];
          console.log('Result:', result.data['text/plain']);
          break;
        case 'display_data':
          // 富媒体显示数据（图表、HTML等）
          const display = msg.content as KernelMessage.IDisplayDataMsg['content'];
          break;
        case 'stream':
          // 流式输出（stdout/stderr）
          const stream = msg.content as KernelMessage.IStreamMsg['content'];
          console.log(`${stream.name}: ${stream.text}`);
          break;
        case 'error':
          // 执行错误
          const error = msg.content as KernelMessage.IErrorMsg['content'];
          console.error(error.ename, error.evalue);
          break;
        case 'status':
          // 状态变化（idle/busy）
          const status = (msg as KernelMessage.IStatusMsg).content.execution_state;
          break;
      }
    };

    // 等待执行完成
    await future.done;
  }

  get kernelStatus(): string {
    return this._sessionContext.kernelDisplayStatus || 'unknown';
  }

  private _sessionContext: ISessionContext;
}
```

### requestExecute 选项

| 选项 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `code` | `string` | — | 要执行的代码（必需） |
| `silent` | `boolean` | `false` | 是否静默执行（不记录历史） |
| `store_history` | `boolean` | `true` | 是否存入执行历史 |
| `stop_on_error` | `boolean` | `true` | 出错时是否停止执行 |
| `allow_stdin` | `boolean` | `false` | 是否允许stdin输入 |
| `user_expressions` | `JSONObject` | `{}` | 用户表达式 |

### 常见Kernel消息类型

| msg_type | 说明 | content关键字段 |
|----------|------|----------------|
| `execute_result` | 执行结果 | `data` (mime类型→内容), `execution_count` |
| `display_data` | 显示数据 | `data`, `metadata` |
| `stream` | 标准输出/错误 | `name` ('stdout'/'stderr'), `text` |
| `error` | 错误信息 | `ename`, `evalue`, `traceback` |
| `status` | 执行状态 | `execution_state` ('busy'/'idle') |
| `execute_input` | 正在执行的代码 | `code`, `execution_count` |
| `clear_output` | 清除输出 | `wait` |

## Kernel状态监听

```typescript
this._sessionContext.statusChanged.connect(() => {
  // kernel状态变化时更新UI
  const status = this._sessionContext.kernelDisplayStatus;
  // 'idle' | 'busy' | 'starting' | 'restarting' | 'dead' | 'unknown'
});
```

或者使用Signal连接：

```typescript
this._sessionContext.connectionStatusChanged.connect(() => {
  // 连接状态：'connected' | 'connecting' | 'disconnected'
});

this._sessionContext.kernelChanged.connect((sender, args) => {
  // kernel切换事件
  // args.oldValue: 旧kernel
  // args.newValue: 新kernel
});
```

## 带变量的交互式执行

Kernel示例的典型模式：
1. 用户点击按钮触发代码执行
2. Model通过kernel.requestExecute发送代码
3. onIOPub收集输出结果
4. stateChanged信号通知View更新
5. View从model中读取结果并渲染DOM

```typescript
// View中
private _onClick = () => {
  const code = 'print("Hello from kernel!")';
  this._model.execute(code).then(() => {
    // 执行完成后更新UI
    this._output.textContent = this._model.output;
  });
};

// Model中onIOPub收集输出
private _output = '';
future.onIOPub = (msg) => {
  if (msg.header.msg_type === 'stream') {
    this._output += (msg.content as any).text;
  }
};
```

## 资源清理

```typescript
dispose(): void {
  this._sessionContext.statusChanged.disconnect(this._onStatusChanged);
  this._sessionContext.dispose();
  super.dispose();
}
```

## 相关概念

- [命令系统](/concepts/04-commands.md)
- [Widget与Shell布局](/concepts/05-widgets-shell.md)
- [信号与事件通信](/concepts/06-signals.md)
- [服务端扩展](/concepts/13-server-extension.md)
- [核心API与Token参考](/references/core-api-tokens.md)
