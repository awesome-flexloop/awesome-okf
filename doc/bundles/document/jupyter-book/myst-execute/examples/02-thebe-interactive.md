---
type: example
title: "Thebe 交互式代码执行"
description: "展示如何在 Web 页面中集成 thebe 实现交互式代码执行：从纯 JS 的 UMD 方式到 React 集成，覆盖 Binder、直连本地服务器两种连接模式"
tags: [thebe, interactive, binder, react, umd, code-execution]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-core-src.md"
    facts: [F-005, F-006, F-051, F-052, F-053, F-057, F-064]
  - path: "/references/thebe-react-src.md"
    facts: [F-008, F-076, F-077, F-078, F-079, F-080]
related_concepts:
  - /concepts/03-thebe-core-api.md
  - /concepts/04-thebe-configuration.md
  - /concepts/05-thebe-binder.md
  - /concepts/07-thebe-react.md
---

# Thebe 交互式代码执行

本示例展示如何在网页中集成 thebe，让读者可以在浏览器中运行和修改代码块。覆盖三种集成方式：纯 HTML/JS（UMD）、ES Module 导入、React 组件。

## 前置条件

### 方案选择

| 方案 | 后端需求 | 适合场景 | 首次启动时间 |
|------|---------|---------|-------------|
| Binder | 无（使用公共 BinderHub） | 公开文档、教程 | 30秒~数分钟（首次构建） |
| 直连 Jupyter | 需运行本地 Jupyter Server | 开发、内部部署 | 即时 |
| JupyterLite | 无（浏览器内 WASM） | 离线、零后端 | ~10秒（下载 Pyodide） |

### CDN 资源

```html
<!-- thebe-core UMD（最新版） -->
<script src="https://unpkg.com/thebe-core@latest/dist/lib/thebe-core.min.js"></script>

<!-- 可选：thebe-lite（JupyterLite/Pyodide 支持） -->
<script src="https://unpkg.com/thebe-lite@latest/dist/lib/thebe-lite.min.js"></script>
```

## 方式 1：纯 HTML/JS（UMD + Binder）

最简单的集成方式，无需构建工具，直接在 HTML 中使用。

```html
<!DOCTYPE html>
<html>
<head>
  <title>Thebe Demo</title>
  <!-- 1. 加载 thebe-core -->
  <script src="https://unpkg.com/thebe-core@latest/dist/lib/thebe-core.min.js"></script>
</head>
<body>
  <h1>交互式 Python 示例</h1>

  <!-- 激活按钮 -->
  <button id="activate-btn">点击激活交互式代码</button>
  <div id="status"></div>

  <!-- 代码块容器 -->
  <pre data-executable="true" data-language="python">
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2*np.pi, 100)
plt.figure(figsize=(6, 3))
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.legend()
plt.show()
  </pre>
  <div id="output-1"></div>

  <script>
    const btn = document.getElementById('activate-btn');
    const statusEl = document.getElementById('status');

    btn.addEventListener('click', async () => {
      btn.disabled = true;
      statusEl.textContent = '连接 Binder...';

      // 2. 创建配置（Binder 模式）
      const config = window.thebeCore.api.makeConfiguration({
        binderOptions: {
          repo: 'executablebooks/thebe-binder-base',
          ref: 'HEAD',
          binderUrl: 'https://mybinder.org',
          repoProvider: 'github',
        },
        kernelOptions: {
          kernelName: 'python',
          path: '/',
        },
        savedSessionOptions: {
          enabled: true,
          maxAge: 86400,  // 24小时缓存
        },
      });

      // 3. 连接 Binder
      const server = window.thebeCore.api.connectToBinder(config);

      // 监听状态事件
      config.events.on('status', (data) => {
        statusEl.textContent = `${data.subject}: ${data.status} - ${data.message}`;
      });

      await server.ready;
      statusEl.textContent = '✅ 已连接，可以执行代码';

      // 4. 创建 Notebook
      const rendermime = window.thebeCore.api.makeRenderMimeRegistry({
        mathjaxUrl: config.mathjax.mathjaxUrl,
        mathjaxConfig: config.mathjax.mathjaxConfig,
      });

      const notebook = window.thebeCore.api.setupNotebookFromBlocks(
        [
          {
            id: 'cell-1',
            source: document.querySelector('pre[data-executable]').textContent.trim(),
          },
        ],
        config,
        rendermime,
      );

      // 5. 附加 Session
      const session = await server.startNewSession(rendermime, {
        kernelName: config.kernels.kernelName,
        path: config.kernels.path,
      });
      notebook.attachSession(session);

      // 6. 将输出区域挂载到 DOM
      const cell = notebook.cells[0];
      const outputEl = document.getElementById('output-1');
      cell.attachToDOM(outputEl);

      // 7. 执行代码
      btn.textContent = '重新运行';
      btn.disabled = false;
      statusEl.textContent = '执行中...';

      const results = await notebook.executeAll(true);
      statusEl.textContent = `✅ 执行完成`;

      // 重新运行按钮
      btn.onclick = async () => {
        btn.disabled = true;
        await notebook.executeAll(true);
        btn.disabled = false;
      };
    });
  </script>
</body>
</html>
```

## 方式 2：ES Module + 直连本地 Jupyter

适用于本地开发或自托管 Jupyter Server 的场景。

### 安装依赖

```bash
npm install thebe-core
```

### 启动本地 Jupyter Server

```bash
jupyter lab --no-browser --ServerApp.token=dev-token --ServerApp.port=8888
```

### 代码实现

```ts
import {
  makeConfiguration,
  connectToJupyter,
  makeRenderMimeRegistry,
  setupNotebookFromBlocks,
} from 'thebe-core';

async function initThebeLocal() {
  // 1. 配置直连本地 Jupyter
  const config = makeConfiguration({
    serverSettings: {
      baseUrl: 'http://localhost:8888',
      token: 'dev-token',
      appendToken: true,
    },
    kernelOptions: {
      kernelName: 'python3',
      path: '/',
    },
  });

  // 2. 连接服务器
  const server = connectToJupyter(config);
  await server.ready;
  console.log('Connected to local Jupyter server');

  // 3. 创建 Notebook 和 Session
  const rendermime = makeRenderMimeRegistry();
  const notebook = setupNotebookFromBlocks(
    [{ id: 'demo-cell', source: 'print("Hello from local Jupyter!")' }],
    config,
    rendermime,
  );

  const session = await server.startNewSession(rendermime, {
    kernelName: 'python3',
  });
  notebook.attachSession(session);

  // 4. 挂载到 DOM 并执行
  const outputEl = document.getElementById('output');
  notebook.cells[0].attachToDOM(outputEl);
  await notebook.executeAll();

  return { server, notebook, session };
}

// 初始化
initThebeLocal().then(({ server }) => {
  console.log('Ready!', server.userServerUrl);
});
```

## 方式 3：React 集成

### 安装依赖

```bash
npm install thebe-core thebe-react
```

### 组件实现

```tsx
import React, { useState } from 'react';
import {
  ThebeBundleLoaderProvider,
  ThebeRenderMimeRegistryProvider,
  ThebeServerProvider,
  ThebeSessionProvider,
  useNotebookFromSource,
} from 'thebe-react';

// 内部组件：使用 Hook
function InteractiveNotebook() {
  const { ready, executing, cellRefs, executeAll, errors } = useNotebookFromSource([
    'import numpy as np\nprint("numpy version:", np.__version__)',
    'x = np.arange(10)\nprint("x =", x)\nprint("sum =", x.sum())',
    `import matplotlib.pyplot as plt
plt.plot(x, x**2)
plt.title("y = x²")
plt.show()`,
  ]);

  if (!ready) {
    return <div className="thebe-loading">⏳ 正在连接内核...</div>;
  }

  return (
    <div className="thebe-notebook">
      <button
        className="thebe-run-btn"
        onClick={() => executeAll()}
        disabled={executing}
      >
        {executing ? '⏳ 执行中...' : '▶ 运行所有代码'}
      </button>

      <div className="thebe-cells">
        {cellRefs.map((ref, i) => (
          <div key={i} className="thebe-cell-output" ref={ref} />
        ))}
      </div>

      {errors && (
        <div className="thebe-errors">
          {errors.map(e => (
            <p key={e.index} className="error">
              Cell {e.index}: {e.error}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

// 外层 Provider 包装
export function ThebeBinderDemo() {
  return (
    <ThebeBundleLoaderProvider
      start
      publicPath="https://unpkg.com/thebe-core@latest/dist/lib/"
    >
      <ThebeRenderMimeRegistryProvider>
        <ThebeServerProvider
          connect
          useBinder
          options={{
            binderOptions: {
              repo: 'executablebooks/thebe-binder-base',
              ref: 'HEAD',
            },
            kernelOptions: { kernelName: 'python' },
          }}
        >
          <ThebeSessionProvider start path="/demo.ipynb">
            <InteractiveNotebook />
          </ThebeSessionProvider>
        </ThebeServerProvider>
      </ThebeRenderMimeRegistryProvider>
    </ThebeBundleLoaderProvider>
  );
}

// 本地 Jupyter 模式（需要本地运行 Jupyter Server）
export function ThebeLocalDemo() {
  return (
    <ThebeRenderMimeRegistryProvider>
      <ThebeServerProvider
        connect
        options={{
          serverSettings: {
            baseUrl: 'http://localhost:8888',
            token: 'dev-token',
          },
          kernelOptions: { kernelName: 'python3' },
        }}
      >
        <ThebeSessionProvider start path="/demo.ipynb">
          <InteractiveNotebook />
        </ThebeSessionProvider>
      </ThebeServerProvider>
    </ThebeRenderMimeRegistryProvider>
  );
}
```

## 状态监听与错误处理

```ts
import { makeEvents } from 'thebe-core';

const events = makeEvents();

// 监听所有状态变化
events.on('status', (data) => {
  console.log(`[${data.subject}] ${data.status}: ${data.message}`);
});

// 监听错误
events.on('error', (data) => {
  console.error('Thebe error:', data.message);
});

const config = makeConfiguration({ ...options }, events);
```

常见状态事件：
- `server launching`：Binder 正在构建环境
- `server ready`：服务器已就绪
- `session launching`：正在启动内核会话
- `kernel ready`：内核已就绪
- `kernel busy`：内核正在执行代码
- `kernel idle`：内核空闲，执行完成

## 清理资源

```ts
// 关闭所有会话并断开
async function cleanup(server, session?) {
  if (session) await session.shutdown();
  await server.shutdownAllSessions();
  server.dispose();
}

// React 中自动清理
useEffect(() => {
  return () => {
    // disconnect 来自 useThebeServer()
    disconnect();
  };
}, []);
```

## 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Binder 连接超时 | BinderHub 负载高或仓库构建慢 | 等待重试，或使用本地 Jupyter |
| "Kernel not found" | kernelName 配置错误 | 使用 `server.getKernelSpecs()` 查询可用内核 |
| WebSocket 连接失败 | CORS 或网络问题 | 检查 Jupyter Server 的 CORS 设置 |
| 数学公式不渲染 | MathJax 未加载 | 确保配置了 mathjaxUrl 和 mathjaxConfig |
| 图表不显示 | 缺少 matplotlib inline | 代码中添加 `%matplotlib inline` |

## 相关文档

- [03-thebe-core-api.md](/concepts/03-thebe-core-api.md)：核心 API 详解
- [04-thebe-configuration.md](/concepts/04-thebe-configuration.md)：所有配置选项
- [05-thebe-binder.md](/concepts/05-thebe-binder.md)：Binder 连接机制
- [07-thebe-react.md](/concepts/07-thebe-react.md)：React Provider 和 Hook 详解
- [03-thebe-lite.md](/examples/03-thebe-lite.md)：JupyterLite 无服务器模式
