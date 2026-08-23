---
type: example
title: "Thebe Lite：浏览器内 Pyodide 执行"
description: "展示如何使用 thebe-lite 实现完全无后端的浏览器内 Python 代码执行，包括 UMD 加载、React 集成和包安装"
tags: [thebe-lite, jupyterlite, pyodide, wasm, serverless]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-lite-src.md"
    facts: [F-007, F-071, F-072, F-073, F-074, F-075]
  - path: "/references/thebe-core-src.md"
    facts: [F-054]
  - path: "/references/thebe-react-src.md"
    facts: [F-076, F-077]
related_concepts:
  - /concepts/06-thebe-lite-pyodide.md
  - /concepts/03-thebe-core-api.md
  - /concepts/07-thebe-react.md
---

# Thebe Lite：浏览器内 Pyodide 执行

本示例展示如何使用 thebe-lite 在浏览器中通过 Pyodide（WebAssembly 版 CPython）执行 Python 代码，完全无需后端服务器。

## 工作原理

thebe-lite 在浏览器中：
1. 加载 JupyterLite Server 和 Pyodide Kernel 插件
2. 在 Web Worker 中启动 Pyodide 运行时（CPython WASM）
3. 创建内存中的虚拟 Jupyter Server（ServiceManager）
4. thebe-core 通过标准 JupyterLab 服务 API 与这个内存服务器通信
5. Python 代码在用户浏览器的 WASM 沙箱中执行

## 方式 1：纯 HTML/JS（UMD）

```html
<!DOCTYPE html>
<html>
<head>
  <title>Thebe Lite Demo</title>
  <style>
    .output { min-height: 50px; padding: 10px; border: 1px solid #eee; margin: 10px 0; }
    #status { padding: 10px; }
    button { padding: 8px 16px; font-size: 14px; cursor: pointer; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    pre { background: #f5f5f5; padding: 12px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>🐍 Pyodide 浏览器内 Python</h1>

  <button id="init-btn">初始化 Python 环境</button>
  <div id="status"></div>

  <h3>代码块：</h3>
  <pre id="code">
import sys
print(f"Python 版本: {sys.version}")

# 计算斐波那契数列
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

print("斐波那契数列前15项:")
print([fib(i) for i in range(15)])
  </pre>

  <button id="run-btn" disabled>▶ 运行代码</button>
  <div id="output" class="output"></div>

  <!-- 必须先加载 thebe-lite，再加载 thebe-core -->
  <script src="https://unpkg.com/thebe-lite@latest/dist/lib/thebe-lite.min.js"></script>
  <script src="https://unpkg.com/thebe-core@latest/dist/lib/thebe-core.min.js"></script>

  <script>
    let notebook = null;
    let session = null;
    const statusEl = document.getElementById('status');
    const outputEl = document.getElementById('output');

    document.getElementById('init-btn').addEventListener('click', async () => {
      const btn = document.getElementById('init-btn');
      btn.disabled = true;
      statusEl.textContent = '⏳ 正在加载 Pyodide 运行时（首次约 10-30 秒）...';

      try {
        // 1. 创建配置（JupyterLite 模式不需要 serverSettings/binderOptions）
        const config = window.thebeCore.api.makeConfiguration({
          kernelOptions: {
            kernelName: 'python',  // 注意：Pyodide 内核名称是 'python'，不是 'python3'
            path: '/demo',
          },
        });

        // 2. 连接到 JupyterLite
        // connectToJupyterLite 内部调用 window.thebeLite.startJupyterLiteServer()
        const server = window.thebeCore.api.connectToJupyterLite(config);

        // 监听状态
        config.events.on('status', (data) => {
          statusEl.textContent = `⏳ ${data.subject}: ${data.status}`;
        });

        await server.ready;
        statusEl.textContent = '✅ Python 环境就绪';

        // 3. 创建 Notebook
        const rendermime = window.thebeCore.api.makeRenderMimeRegistry({
          mathjaxUrl: config.mathjax.mathjaxUrl,
          mathjaxConfig: config.mathjax.mathjaxConfig,
        });

        notebook = window.thebeCore.api.setupNotebookFromBlocks(
          [{ id: 'cell-1', source: document.getElementById('code').textContent.trim() }],
          config,
          rendermime,
        );

        // 4. 创建 Session
        session = await server.startNewSession(rendermime, {
          kernelName: 'python',
          path: '/demo',
        });
        notebook.attachSession(session);

        // 5. 挂载输出
        notebook.cells[0].attachToDOM(outputEl);

        document.getElementById('run-btn').disabled = false;
        btn.textContent = '✅ 已初始化';

      } catch (err) {
        statusEl.textContent = `❌ 错误: ${err.message}`;
        btn.disabled = false;
      }
    });

    document.getElementById('run-btn').addEventListener('click', async () => {
      const btn = document.getElementById('run-btn');
      btn.disabled = true;
      statusEl.textContent = '⏳ 执行中...';

      try {
        // 更新代码内容（如果用户修改了）
        const code = document.getElementById('code').textContent.trim();
        await notebook.cells[0].execute(code);
        statusEl.textContent = '✅ 执行完成';
      } catch (err) {
        statusEl.textContent = `❌ 执行错误: ${err.message}`;
      }
      btn.disabled = false;
    });
  </script>
</body>
</html>
```

## 方式 2：React 集成

### 安装依赖

```bash
npm install thebe-core thebe-lite thebe-react
```

> **注意**：如果使用 BundleLoaderProvider 动态加载 UMD，则无需 npm 安装 thebe-core/thebe-lite。

### React 组件

```tsx
import React from 'react';
import {
  ThebeBundleLoaderProvider,
  ThebeRenderMimeRegistryProvider,
  ThebeServerProvider,
  ThebeSessionProvider,
  useNotebookFromSource,
} from 'thebe-react';

function PyodideNotebook() {
  const { ready, executing, cellRefs, executeAll, errors } = useNotebookFromSource(
    [
      // 代码块 1：基础 Python
      `import sys
print("Python 版本:", sys.version)
print("平台:", sys.platform)`,

      // 代码块 2：使用 numpy（Pyodide 预装）
      `import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print("数组:", arr)
print("均值:", arr.mean())
print("标准差:", arr.std())`,

      // 代码块 3：使用 matplotlib（Pyodide 预装）
      `import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 4*np.pi, 200)
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')
ax.legend()
ax.set_title('Trigonometric Functions')
plt.show()`,
    ],
    { refsForWidgetsOnly: false }  // 为所有单元格创建 refs（默认仅 widget 标签单元格）
  );

  if (!ready) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ fontSize: '24px' }}>🐍</div>
        <p>正在加载 Python 环境（首次需下载 Pyodide，约 20MB）...</p>
        <p style={{ fontSize: '12px', color: '#666' }}>请耐心等待，后续刷新会使用缓存</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <button
        onClick={() => executeAll({ stopOnError: false })}
        disabled={executing}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          cursor: executing ? 'wait' : 'pointer',
          background: executing ? '#ccc' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          marginBottom: '20px',
        }}
      >
        {executing ? '⏳ 执行中...' : '▶ 运行所有代码'}
      </button>

      <div className="cells">
        {cellRefs.map((ref, i) => (
          <div
            key={i}
            ref={ref}
            style={{
              margin: '15px 0',
              padding: '10px',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
              minHeight: '40px',
            }}
          />
        ))}
      </div>

      {errors && (
        <div style={{ color: 'red', padding: '10px', background: '#ffebee' }}>
          {errors.map(e => (
            <p key={e.index}>Cell {e.index} 错误: {e.error?.evalue || e.error}</p>
          ))}
        </div>
      )}
    </div>
  );
}

export function ThebeLiteApp() {
  return (
    <ThebeBundleLoaderProvider
      start
      loadThebeLite={true}  // 关键：同时加载 thebe-lite
      publicPath="https://unpkg.com/thebe-core@latest/dist/lib/"
    >
      <ThebeRenderMimeRegistryProvider>
        <ThebeServerProvider
          connect
          useJupyterLite={true}  // 关键：使用 JupyterLite 模式
          options={{
            kernelOptions: {
              kernelName: 'python',  // 注意是 'python' 而非 'python3'
              path: '/lite-demo',
            },
          }}
        >
          <ThebeSessionProvider start path="/lite-demo.ipynb">
            <PyodideNotebook />
          </ThebeSessionProvider>
        </ThebeServerProvider>
      </ThebeRenderMimeRegistryProvider>
    </ThebeBundleLoaderProvider>
  );
}
```

## 安装第三方包

在 Pyodide 中安装包使用 `%pip install` 或 `piplite`：

```python
# 方式1：使用 magic 命令（推荐）
%pip install pandas

import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
print(df)
```

```python
# 方式2：使用 piplite API
import piplite
await piplite.install('scikit-learn')

from sklearn.linear_model import LinearRegression
print("sklearn loaded successfully")
```

> **注意**：
> - 只有提供 Pyodide wheel（emscripten/wasm32 平台）的包才能安装
> - 纯 Python 包通常可以直接安装
> - 包含 C 扩展的包需要有对应 Pyodide 兼容版本
> - 默认从 `pipliteUrls` 指定的索引（默认指向 JupyterLite 官方 CDN）

### 自定义包索引

```ts
const config = makeConfiguration({
  kernelOptions: { kernelName: 'python' },
});

// 在 connectToJupyterLite 时传入自定义配置
const server = connectToJupyterLite(config);
// 或在 React 中通过 options 传入 lite 配置
```

如果使用 ESM 直接导入：

```ts
import { startJupyterLiteServer } from 'thebe-lite';

const serviceManager = await startJupyterLiteServer({
  litePluginSettings: {
    '@jupyterlite/pyodide-kernel-extension:kernel': {
      pipliteUrls: ['https://your-mirror.example.com/pypi/all.json'],
      pipliteWheelUrl: 'https://your-mirror.example.com/pypi/piplite-xxx.whl',
    },
  },
});
```

## Pyodide 预装包

Pyodide 默认预装以下常用包：
- numpy、scipy、pandas、matplotlib
- 标准库（sys、os、json、math、re 等）
- 部分 micropip 安装的包

更多预装包列表见 [Pyodide 文档](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)。

## 注意事项与限制

1. **内核名称**：Pyodide 内核名称为 `'python'`，不是 `'python3'`。配置错误会导致 "Kernel not found"。

2. **首次加载时间**：Pyodide 运行时约 20MB，首次加载需要时间。浏览器会缓存后续加载很快。建议添加加载提示。

3. **内存限制**：WASM 代码运行在浏览器沙箱中，可用内存有限（通常 2GB 以内）。处理大数据集时可能遇到 OOM。

4. **文件系统**：使用内存文件系统，页面刷新后数据丢失。可以通过 IndexedDB 持久化。

5. **不支持的功能**：
   - 多线程/多进程（`threading` 受限）
   - 网络请求（`requests` 库不可用，使用 `pyfetch` 替代）
   - 文件系统操作（受沙箱限制）
   - C 扩展需要 Pyodide 兼容的 wheel

6. **路径处理**：JupyterLite 模式下路径中 `/` 会被替换为 `-`（thebe-core 内部处理），因为 JupyterLite 对子目录支持尚不完全。

7. **MathJax**：默认配置加载 MathJax 2.7.5 CDN 用于数学公式渲染。如果页面已有其他数学渲染方案（如 KaTeX），注意冲突。

## 对比三种连接模式

| 特性 | Binder | 直连 Jupyter | JupyterLite |
|------|--------|-------------|-------------|
| 需要后端 | 是（BinderHub） | 是（本地/远程） | 否 |
| 首次启动 | 30秒~数分钟 | 即时 | ~10-30秒（下载 WASM） |
| 支持任意内核 | ✅ | ✅ | ❌（仅 Pyodide Python） |
| 支持 C 扩展 | ✅ | ✅ | 有限（需 Pyodide wheel） |
| 离线可用 | ❌ | ❌（需本地 Jupyter） | ✅（缓存后） |
| 适合公开部署 | ✅ | ❌（需要 token） | ✅ |
| 会话持久化 | localStorage | 无 | 内存（刷新丢失） |

## 相关文档

- [06-thebe-lite-pyodide.md](/concepts/06-thebe-lite-pyodide.md)：JupyterLite/Pyodide 架构详解
- [03-thebe-core-api.md](/concepts/03-thebe-core-api.md)：核心 API
- [04-thebe-configuration.md](/concepts/04-thebe-configuration.md)：配置选项
- [02-thebe-interactive.md](/examples/02-thebe-interactive.md)：Binder 和直连模式示例
