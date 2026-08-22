---
type: Reference
title: LiteTerminalAPIClient API信源
description: LiteTerminalAPIClient类的完整API、属性、方法和Private命名空间
tags: [api, client, websocket, terminal, mock-socket]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: client-ts
    resource: /../../../../../../external/libs/jupyter/terminal/src/client.ts
    title: src/client.ts
---

# LiteTerminalAPIClient API信源

## 类签名

```typescript
export class LiteTerminalAPIClient implements ILiteTerminalAPIClient
```

## 构造函数

```typescript
constructor(options: { serverSettings?: ServerConnection.ISettings } = {})
```

- `serverSettings`：可选，默认调用`ServerConnection.makeSettings()`获取默认设置
- 注入mock-socket的WebSocket到serverSettings中（由plugin层完成）

## 公共属性

| 属性 | 类型 | 访问修饰 | 说明 |
|------|------|---------|------|
| `serverSettings` | `ServerConnection.ISettings` | readonly | 服务器设置（包含mock WebSocket） |
| `isAvailable` | `boolean` | getter | 读取PageConfig `terminalsAvailable` 是否为 `'true'` |
| `browsingContextId` | `string` | setter | 设置Service Worker通信标识符 |
| `contentsManager` | `Contents.IManager` | setter | 设置JupyterLite内容管理器 |
| `terminalDisposed` | `ISignal<this, string>` | getter | 终端关闭信号，参数为shellId/name |

## 公共方法

### startNew

```typescript
async startNew(options?: Terminal.ITerminal.IOptions): Promise<Terminal.IModel>
```

创建新的交互式终端。

**参数**：
- `options.name`：终端名称，默认自动生成（从"1"开始递增）
- `options.cwd`：初始工作目录

**流程**：
1. 生成/使用name
2. 获取baseUrl和wsUrl
3. 调用`createShell()`创建TerminalShell实例（mountpoint='/drive'）
4. 设置outputCallback将stdout输出包装为`['stdout', text]`消息通过WebSocket发送
5. 将shell存入Private.shells Map
6. 创建hook函数处理WebSocket连接：
   - 设置shell.socket
   - 监听message事件：解析JSON，处理'stdin'消息调用shell.input()、'set_size'消息调用shell.setSize()
   - 发送handshake消息`['setup']`
   - 调用shell.start()
7. 在`${wsUrl}/terminals/websocket/${name}`创建mock-socket WebSocketServer
8. 连接shell.disposed信号到shutdown、wsServer.close和terminalDisposed信号发射
9. 返回`{ name }`

### listRunning

```typescript
async listRunning(): Promise<Terminal.IModel[]>
```

返回所有运行中终端的模型列表`[{ name }]`。

### shutdown

```typescript
async shutdown(name: string): Promise<void>
```

关闭指定名称的终端：
1. 从Private.shells获取shell
2. 发送`['disconnect']`消息
3. 关闭socket
4. 从Map中删除
5. 调用shell.dispose()

### registerAlias

```typescript
registerAlias(key: string, value: string): void
```

注册shell别名，对所有终端生效（包括后续创建的）。key重复则覆盖。

### registerEnvironmentVariable

```typescript
registerEnvironmentVariable(key: string, value: string | undefined): void
```

注册环境变量。value为undefined时删除已存在的key。

### registerExternalCommand

```typescript
registerExternalCommand(options: IExternalCommand.IOptions): void
```

注册外部命令（添加到_externalCommands数组）。

### createHeadlessShell

```typescript
async createHeadlessShell(options: {
  shellId: string;
  cwd?: string;
  environment?: { [key: string]: string | undefined };
  outputCallback: IOutputCallback;
  readyTimeoutMs?: number;
}): Promise<IShell>
```

创建无头shell（无UI），用于编程式命令执行。

**参数**：
- `shellId`：shell标识符
- `cwd`：可选工作目录
- `environment`：可选环境变量（合并到全局_environment）
- `outputCallback`：输出回调（必填）
- `readyTimeoutMs`：就绪超时，默认30000ms（DEFAULT_READY_TIMEOUT_MS）

**流程**：
1. 合并environment
2. 调用createShell()，设置`color: true`以保留TERM/TERMINFO
3. Promise.race等待shell.ready或超时
4. 超时则reject并dispose shell
5. 就绪后调用shell.start()
6. 返回shell

### themeChange

```typescript
themeChange(isDarkMode?: boolean): void
```

遍历所有运行中shell，调用shell.themeChange(isDarkMode)通知主题变更。

### handleStdin

```typescript
async handleStdin(request: IStdinRequest): Promise<IStdinReply>
```

委托给Private.shellManager.handleStdin(request)，处理来自Service Worker的stdin请求。

### createShell（protected）

```typescript
protected async createShell(options: ITerminalShell.IOptions): Promise<ITerminalShell>
```

工厂方法，返回`new TerminalShell(options)`。可被子类覆盖。

## 私有成员

```typescript
private _aliases?: { [key: string]: string };
private _environment?: { [key: string]: string | undefined };
private _browsingContextId?: string;
private _contentsManager?: Contents.IManager;
private _externalCommands: IExternalCommand.IOptions[] = [];
private _terminalDisposed = new Signal<this, string>(this);
```

### _nextAvailableName（private）

从i=1开始递增，返回第一个不在Private.shells中的`${i}`。

## Private命名空间

```typescript
namespace Private {
  export const shellManager: IShellManager = new ShellManager();  // 来自@jupyterlite/cockle
  export const shells = new Map<string, ITerminalShell>();
}
```

- `shellManager`：模块级单例ShellManager，管理所有shell的stdin路由
- `shells`：模块级Map，存储所有交互式终端（不包含headless shell）
