---
type: concept
title: "Thebe React：声明式集成"
description: "详解 thebe-react 的 Context Providers 和 Hooks：ThebeBundleLoaderProvider、ThebeServerProvider、ThebeSessionProvider、ThebeRenderMimeRegistryProvider 及 useNotebook、useThebeServer 等 Hook"
tags: [thebe, thebe-react, react, hooks, context, provider, notebook]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-react-src.md"
    facts: [F-008, F-076, F-077, F-078, F-079, F-080, F-081]
---

# Thebe React：声明式集成

thebe-react 提供了一套 React Context Providers 和 Hooks，以声明式方式将 thebe 的服务器连接、会话管理和 Notebook 执行集成到 React 应用中。开发者通过嵌套 Provider 组件和在子组件中调用 Hook 即可使用，无需手动管理底层对象的生命周期。

## Provider 层次结构

Provider 必须按以下顺序嵌套，内层依赖外层：

```tsx
<ThebeBundleLoaderProvider>      {/* 1. 动态加载 thebe-core/thebe-lite JS */}
  <ThebeRenderMimeRegistryProvider>  {/* 2. 创建 IRenderMimeRegistry */}
    <ThebeServerProvider>          {/* 3. 连接 Jupyter Server */}
      <ThebeSessionProvider>       {/* 4. 创建 Kernel Session */}
        <YourApp />               {/* 5. 你的组件：使用 Hooks 执行代码 */}
      </ThebeSessionProvider>
    </ThebeServerProvider>
  </ThebeRenderMimeRegistryProvider>
</ThebeBundleLoaderProvider>
```

每个 Provider 自动管理其负责的资源的创建、就绪检测和清理，子组件通过 Hook 访问上下文数据。

## ThebeBundleLoaderProvider

动态加载 thebe-core（和可选的 thebe-lite）UMD bundle。适用于不想通过 npm 安装而通过 CDN 加载的场景。

```tsx
<ThebeBundleLoaderProvider
  start={true}                  // 是否立即开始加载
  loadThebeLite={false}        // 是否同时加载 thebe-lite
  publicPath="https://unpkg.com/thebe-core@latest/dist/"  // UMD 文件所在目录
  config={...}                 // CoreOptions 透传
>
  {children}
</ThebeBundleLoaderProvider>
```

### 工作机制

1. 当 `start={true}` 且 thebe 尚未加载时，创建 `<script>` 标签动态加载 `thebe-core.min.js`（以及可选的 `thebe-lite.min.js`）
2. 轮询检查 `window.thebeCore` 和 `window.thebeLite` 是否存在
3. 加载完成后，设置内部状态标记 core/lite 可用
4. 子组件通过 `useThebeLoader()` Hook 访问：

```tsx
const { core, loading, error } = useThebeLoader();
// core: thebe-core 模块 API（含 makeConfiguration、makeServer 等）
// loading: 是否正在加载
// error: 加载错误
```

> **注意**：如果项目使用 npm 安装了 thebe-core 和 thebe-lite（通过 import），则不需要 BundleLoaderProvider，可以直接传递配置和事件。

## ThebeServerProvider

管理 ThebeServer 的创建和连接，自动根据 props 选择连接模式（Binder/直连/JupyterLite）。

```tsx
<ThebeServerProvider
  connect={true}                          // 是否立即连接
  config={myConfig}                       // 已有的 Config 对象（可选）
  options={{                              // CoreOptions（config 未提供时使用）
    binderOptions: { repo: '...', ref: 'main' },
    kernelOptions: { kernelName: 'python' },
  }}
  useBinder={true}                        // 使用 Binder 模式
  useJupyterLite={false}                  // 使用 JupyterLite 模式
  customConnectFn={(server) => {...}}     // 自定义连接逻辑
  customRepoProviders={[...]}             // 自定义 RepoProvider
  events={myEvents}                       // 自定义事件总线
>
  {children}
</ThebeServerProvider>
```

### 连接逻辑

Provider 内部在 `connect` prop 为 true 时：

1. 使用 `config` 或 `core.makeConfiguration(options, events)` 创建 Config
2. `new core.ThebeServer(thebeConfig)` 创建服务器实例
3. 根据模式调用：
   - `customConnectFn(server)`（如果提供了自定义函数）
   - `server.connectToServerViaBinder(customRepoProviders)`（useBinder=true）
   - `server.connectToJupyterLiteServer()`（useJupyterLite=true）
   - `server.connectToJupyterServer()`（默认直连）
4. 等待 `server.ready` Promise resolve
5. 同时注册 error 事件监听器，捕获 server/session/kernel 错误

### useThebeServer Hook

```tsx
const {
  server,           // ThebeServer 实例（连接成功后可用）
  config,           // Config 对象
  events,           // ThebeEvents 事件总线
  connecting,       // boolean: 是否正在连接
  ready,            // boolean: 服务器是否就绪
  error,            // string | undefined: 错误信息
  connect,          // () => void: 手动触发连接
  disconnect,       // () => Promise<void>: 断开并重建服务器
  subscribe,        // (fn) => void: 订阅状态事件
  unsubAll,         // () => void: 取消所有订阅
} = useThebeServer();
```

**事件订阅示例**：

```tsx
const { subscribe, unsubAll } = useThebeServer();
useEffect(() => {
  subscribe((data) => {
    console.log(`${data.subject} ${data.status}: ${data.message}`);
  });
  return () => unsubAll();
}, [subscribe, unsubAll]);
```

### useThebeConfig Hook

```tsx
const { config } = useThebeConfig();
// 仅返回 config 对象
```

### useDisposeThebeServer Hook

```tsx
const disposed = useDisposeThebeServer();
// 组件挂载后自动关闭所有会话并 dispose server
// 返回 disposed: boolean 表示是否完成清理
```

## ThebeSessionProvider

在内核服务器连接就绪后，自动创建并管理一个 ThebeSession（内核会话）。

```tsx
<ThebeSessionProvider
  start={true}                  // 服务器就绪后是否自动启动会话
  path="/notebooks/demo.ipynb"  // Session 路径
  shutdownOnUnmount={false}     // 组件卸载时是否关闭会话
>
  {children}
</ThebeSessionProvider>
```

### useThebeSession Hook

```tsx
const {
  session,          // ThebeSession 实例（就绪后可用）
  path,             // string: Session 路径
  starting,         // boolean: 是否正在启动
  ready,            // boolean: Session 是否就绪
  error,            // string | undefined: 错误信息
  start,            // () => Promise<void>: 启动或重启会话
  shutdown,         // () => Promise<void>: 关闭会话
} = useThebeSession();
```

启动失败时，如果 server 可达但内核名称错误，会自动通过 `server.getKernelSpecs()` 查询可用内核列表并显示在错误信息中。

## ThebeRenderMimeRegistryProvider

创建一个 IRenderMimeRegistry 实例（来自 @jupyterlab/rendermime），用于渲染 Jupyter 输出（HTML、图片、Markdown、MathJax 等）。Session 和 Notebook 创建都需要 rendermime 实例。

```tsx
<ThebeRenderMimeRegistryProvider>
  {children}
</ThebeRenderMimeRegistryProvider>
```

### useRenderMimeRegistry Hook

```tsx
const rendermime = useRenderMimeRegistry();
// rendermime: IRenderMimeRegistry | undefined
```

## Notebook Hooks

thebe-react 提供两个主要 Hook 来管理 Notebook 的创建和执行。

### useNotebook：从 ipynb 文件加载

```tsx
const {
  ready,              // boolean: notebook 创建并附加到 session
  loading,            // boolean: 正在加载 ipynb
  attached,           // boolean: session 是否已附加
  executing,          // boolean: 是否正在执行
  executed,           // boolean: 是否已执行完成
  errors,             // IThebeNotebookError[] | null: 执行错误
  notebook,           // ThebeNotebook 实例
  cellRefs,           // callback refs 数组，用于挂载到 DOM
  cellIds,            // cell ID 数组
  executeAll,         // (options?) => Promise<execReturns>
  executeSome,        // (predicate, options?) => Promise<execReturns>
  clear,              // () => void: 清空所有输出
} = useNotebook(
  'demo.ipynb',                                         // notebook 名称
  async (name) => {                                     // 异步获取函数
    const resp = await fetch(`/notebooks/${name}`);
    return await resp.json();                          // 返回 INotebookContent
  },
  { refsForWidgetsOnly: true }                          // 选项
);
```

**执行选项 NotebookExecuteOptions**：

```ts
interface NotebookExecuteOptions {
  stopOnError?: boolean;    // 遇错是否停止，默认 true
  before?: () => void;      // 执行前回调
  after?: () => void;       // 执行后回调
  preprocessor?: (source: string) => string;  // 代码预处理函数
}
```

**组件中使用示例**：

```tsx
function NotebookDemo() {
  const { ready, executing, executed, cellRefs, executeAll, errors } = useNotebook(
    'demo.ipynb',
    (name) => fetch(`/notebooks/${name}`).then(r => r.json())
  );

  if (!ready) return <div>Loading notebook...</div>;

  return (
    <div>
      <button onClick={() => executeAll()} disabled={executing}>
        {executing ? 'Running...' : 'Run All'}
      </button>
      {cellRefs.map((ref, i) => (
        <div key={i} ref={ref} className="cell-output" />
      ))}
      {errors && errors.map(e => (
        <div key={e.index} className="error">
          Cell {e.index}: {e.error}
        </div>
      ))}
    </div>
  );
}
```

`cellRefs` 是 callback ref 数组，挂载到 DOM 元素时会自动调用 `cell.attachToDOM(node)`，将单元格的输出区域渲染到对应的 DOM 节点。

### useNotebookFromSource：从代码字符串数组创建

```tsx
const {
  ready, attached, executing, executed, errors,
  notebook, cellRefs, cellIds,
  executeAll, executeSome, clear,
} = useNotebookFromSource(
  ['x = 1\nprint(x)', 'y = x + 1\nprint(y)'],  // 代码块数组
  { refsForWidgetsOnly: false }                  // 默认只生成 widget cell 的 refs
);
```

与 `useNotebook` 几乎相同，但不通过 fetch 加载 ipynb，而是直接从字符串数组创建 Notebook。适用于内嵌代码块的场景。

**executeSome 选择性执行**：

```tsx
executeSome(
  (cell) => cell.tags?.includes('exercise'),  // 只执行标记为 exercise 的单元格
  { stopOnError: false }
);
```

## interpolate Hook

thebe-react 还导出了一个 `interpolate` 工具（来自 hooks/interpolate），用于在文本模板中插入执行结果，常见于 MyST 的 `{eval}` role 和内联表达式场景。

## 完整使用示例

```tsx
import {
  ThebeBundleLoaderProvider,
  ThebeRenderMimeRegistryProvider,
  ThebeServerProvider,
  ThebeSessionProvider,
  useNotebookFromSource,
} from 'thebe-react';

function InteractiveCells() {
  const { ready, executing, cellRefs, executeAll } = useNotebookFromSource([
    'import numpy as np\nimport matplotlib.pyplot as plt\nprint("Hello!")',
    'x = np.linspace(0, 2*np.pi, 100)\nplt.plot(x, np.sin(x))',
  ]);

  return (
    <div>
      <button onClick={() => executeAll()} disabled={!ready || executing}>
        {executing ? 'Executing...' : 'Run Code'}
      </button>
      <div className="outputs">
        {cellRefs.map((ref, i) => <div key={i} ref={ref} />)}
      </div>
    </div>
  );
}

function App() {
  return (
    <ThebeBundleLoaderProvider
      start
      publicPath="/thebe/"
    >
      <ThebeRenderMimeRegistryProvider>
        <ThebeServerProvider
          connect
          useBinder
          options={{
            binderOptions: { repo: 'executablebooks/thebe-binder-base', ref: 'HEAD' },
            kernelOptions: { kernelName: 'python' },
          }}
        >
          <ThebeSessionProvider start path="/demo.ipynb">
            <InteractiveCells />
          </ThebeSessionProvider>
        </ThebeServerProvider>
      </ThebeRenderMimeRegistryProvider>
    </ThebeBundleLoaderProvider>
  );
}
```

## 相关概念

- [03-thebe-core-api.md](03-thebe-core-api.md)：thebe-core 核心 API
- [04-thebe-configuration.md](04-thebe-configuration.md)：配置选项
- [05-thebe-binder.md](05-thebe-binder.md)：Binder 连接
- [06-thebe-lite-pyodide.md](06-thebe-lite-pyodide.md)：JupyterLite 模式
- [02-thebe-interactive.md](../examples/02-thebe-interactive.md)：完整 React 集成示例
