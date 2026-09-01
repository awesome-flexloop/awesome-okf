---
type: Reference
title: 前端 JavaScript jupyterlite_sphinx.js 源码索引
description: jupyterlite-sphinx 前端交互 JavaScript 源码索引，包含全局函数、IIFE 模块和事件处理
tags: [source, javascript, frontend, iframe, interaction]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source-js
    resource: /references/js-source.md
    title: jupyterlite_sphinx.js source
---

## 源码文件位置

- **文件**：`jupyterlite_sphinx/jupyterlite_sphinx.js`
- **加载方式**：通过 `app.add_js_file("jupyterlite_sphinx.js")` 注册到 Sphinx HTML 输出

## 全局函数（window 上挂载）

| 函数名 | 行号 | 参数 | 说明 |
|--------|------|------|------|
| `jupyterliteShowIframe` | 1-25 | `(tryItButtonId, iframeSrc)` | PromptedIframe 点击后创建 iframe 替换按钮 |
| `jupyterliteConcatSearchParams` | 27-53 | `(iframeSrc, params)` | 将页面搜索参数合并到 iframe URL |
| `tryExamplesShowIframe` | 55-113 | `(examplesContainerId, iframeContainerId, iframeParentContainerId, iframeSrc, iframeHeight)` | TryExamples：切换显示嵌入 notebook iframe |
| `tryExamplesHideIframe` | 115-126 | `(examplesContainerId, iframeParentContainerId)` | TryExamples：切回显示示例内容 |
| `openInNewTab` | 130-142 | `(examplesContainerId, iframeParentContainerId)` | TryExamples：新标签页打开 notebook |
| `isMobileDevice` | 155-201 | 无参数（IIFE 返回函数） | 检测是否为移动设备 |
| `loadTryExamplesConfig` | 313 | 指向 `ConfigLoader.loadConfig` | 加载 try_examples.json 运行时配置 |
| `toggleTryExamplesButtons` | 315-323 | 无参数 | 调试用：切换按钮可见性 |

## jupyterliteShowIframe 实现细节

- 隐藏点击按钮（`display: none`）
- 创建 50×50 px spinner（class=`jupyterlite_sphinx_spinner`），通过负 margin 居中
- 创建 iframe（width/height=100%, class=`jupyterlite_sphinx_iframe`）
- 将 spinner 和 iframe 追加到按钮父节点

## jupyterliteConcatSearchParams 参数处理

- `params === true`：传递所有页面 URL 搜索参数
- `params === false`：不传递任何参数
- `params` 为数组：只传递指定名称的参数
- 非法值（非布尔非数组）：console.error 输出错误

## tryExamplesShowIframe 实现细节

- 首次调用时创建 spinner 和 iframe，后续调用仅切换可见性
- iframe 高度计算：指定值 > max(globalMinHeight, examples.offsetHeight)
- Spinner 位置：在视口内居中（0.5 × min(视口底部-examplesTop, height)）
- 隐藏 examples 内容（添加 hidden class），显示 iframe 容器（移除 hidden class）

## tryExamplesHideIframe 实现细节

- 给 iframe 父容器添加 hidden class
- 从 examples 容器移除 hidden class

## openInNewTab 实现细节

- 获取 iframe 元素的 src 属性
- `window.open(src)` 打开新标签页
- 调用 `tryExamplesHideIframe` 切回 examples 视图

## isMobileDevice（IIFE 单例）

- 使用 14 种移动设备 User-Agent 正则模式检测
- 屏幕尺寸兜底：宽 ≤480px 或高 ≤480px
- 检测到移动设备时隐藏所有 `.try_examples_button`
- 缓存首次检测结果（cachedUAResult）
- 首次检测为移动设备时输出 console.log 提示

**UA 正则模式列表（14种）：**
Android, webOS, iPhone, iPad, iPod, BlackBerry, IEMobile, Windows Phone, Opera Mini, SamsungBrowser, UC.*Browser/UCWEB, MiuiBrowser, Mobile, Tablet

## ConfigLoader（IIFE 模块）

| 方法/属性 | 行号 | 说明 |
|-----------|------|------|
| `configLoadPromise` | 205 | 请求去重 Promise 缓存 |
| `loadConfig(configFilePath)` | 207-280 | 加载配置的主方法 |
| `resetState()` | 285-288 | 重置状态（仅供测试/调试） |

**loadConfig 流程：**

1. 先检查 `isMobileDevice()`，是移动设备则直接隐藏按钮返回
2. 检查 `tryExamplesConfigLoaded`，已加载则直接返回
3. 如有正在进行的请求（configLoadPromise），返回该 Promise 实现去重
4. 创建新 Promise：
   - 添加时间戳查询参数防缓存（`?cb=<timestamp>`）
   - fetch 配置文件（404 不报错，仅 log）
   - 解析 JSON：
     - `global_min_height` → 设置 `tryExamplesGlobalMinHeight`
     - `ignore_patterns` → 对当前页面 URL pathname 做正则匹配，匹配成功则隐藏按钮
   - finally 中设置 `tryExamplesConfigLoaded = true`

## 全局变量

| 变量 | 初始值 | 行号 | 说明 |
|------|--------|------|------|
| `tryExamplesGlobalMinHeight` | `0` | 146 | iframe 最小高度，由配置文件设置 |
| `tryExamplesConfigLoaded` | `false` | 150 | 配置是否已加载（防重复请求） |

## 事件监听

- `resize` 事件（250ms debounce）：配置加载后，根据 isMobileDevice() 结果切换所有 `.try_examples_button` 的 hidden class

## CSS 类名引用

| CSS 类 | 使用位置 |
|--------|---------|
| `jupyterlite_sphinx_spinner` | 加载指示器 |
| `jupyterlite_sphinx_iframe` | 嵌入的 iframe 元素 |
| `jupyterlite_sphinx_iframe_container` | iframe 容器 div |
| `jupyterlite_sphinx_raw_iframe` | 无 prompt 模式的直接 iframe |
| `jupyterlite_sphinx_try_it_button` | "Try It" 按钮 |
| `jupyterlite_sphinx_try_it_button_unclicked` | 未点击状态按钮 |
| `try_examples_button` | TryExamples 操作按钮 |
| `try_examples_button_container` | 按钮容器 |
| `try_examples_outer_container` | TryExamples 外部容器 |
| `try_examples_content` | 原始示例内容区域 |
| `try_examples_outer_iframe` | iframe 外部容器（初始隐藏） |
| `hidden` | 通用隐藏类 |

## 相关概念

- [前端 JavaScript 交互机制](../concepts/12-frontend-js.md)
- [try_examples 指令](../concepts/08-try-examples-directive.md)
- [核心模块源码](main-source.md)
