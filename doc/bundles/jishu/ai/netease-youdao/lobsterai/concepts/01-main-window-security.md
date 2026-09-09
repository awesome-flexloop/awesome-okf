---
type: concept
title: "主进程窗口模型与安全基线"
description: "主窗口的跨平台无边框配置、主题化背景色，webPreferences 十项安全基线，以及 webview 挂载时的强制偏好重写策略。"
tags: [lobsterai, electron, main-process, security, browserwindow, webview]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# 主进程窗口模型与安全基线

LobsterAI 的主窗口在 `src/main/main.ts` 约第 13470 行以 `new BrowserWindow` 创建（F-la-010）。本篇讲解窗口的跨平台外观策略、严格的安全基线，以及第三类"内嵌网页容器"（webview）挂载时的偏好强制重写——三者共同构成应用的桌面壳安全边界。

## 一、跨平台窗口外观

窗口外观按操作系统分支处理（F-la-010）：

| 配置项 | Windows | macOS |
|---|---|---|
| `frame` | `false`（无边框） | 默认值（保留原生框架） |
| `titleBarStyle` | `'hidden'` | `'hiddenInset'` |
| `trafficLightPosition` | — | `{ x: 12, y: 20 }` |

Windows 下无边框意味着标题栏按钮（最小化/最大化/关闭）由渲染层自绘，对应 preload 暴露的 `window-minimize`/`window-maximize`/`window-close` 通道（F-la-037）。

窗口其余关键配置（F-la-012）：

- `backgroundColor` 按主题取色：暗色 `'#0F1117'`、亮色 `'#F8F9FB'`，避免启动白闪；
- `show: false`：窗口创建后不立即显示，待内容就绪后再展示；
- `autoHideMenuBar: true`：隐藏传统菜单栏；
- 最小宽高由 `MIN_APP_WINDOW_WIDTH` / `MIN_APP_WINDOW_HEIGHT` 常量约束。

## 二、webPreferences 安全基线

主窗口的 `webPreferences` 是 Electron 安全模型的第一道闸门（F-la-011）：

| 配置项 | 取值 | 安全含义 |
|---|---|---|
| `nodeIntegration` | `false` | 渲染层无 Node.js 能力 |
| `contextIsolation` | `true` | preload 与页面脚本隔离上下文 |
| `sandbox` | `true` | 渲染进程沙箱化 |
| `webSecurity` | `true` | 同源策略与 CORS 不放宽 |
| `preload` | `PRELOAD_PATH` | 仅注入白名单式 preload 桥 |
| `backgroundThrottling` | `false` | 后台时不停帧（保证流式输出连续） |
| `webviewTag` | `true` | 允许 `<webview>` 标签（受下文重写约束） |
| `enableWebSQL` | `false` | 关闭已废弃的 WebSQL |
| `autoplayPolicy` | `'document-user-activation-required'` | 媒体自动播放需用户激活 |
| `disableDialogs` | `true` | 禁用 alert/confirm 等阻塞对话框 |
| `navigateOnDragDrop` | `false` | 拖放文件不触发导航 |

值得注意的两个"产品化取舍"：`backgroundThrottling: false` 是体验优先——Agent 流式输出时窗口在后台也不能降帧；`webviewTag: true` 是功能优先——制品浏览器（artifact browser）需要内嵌网页，但放开 webview 的同时用第三节的重写机制兜底。

## 三、webview 强制偏好重写

`webContents.on('will-attach-webview')` 处理器在每次 webview 挂载前**强制重写**其 `webPreferences`（F-la-013）：

| 被重写项 | 强制值 |
|---|---|
| `nodeIntegration` / `contextIsolation` / `sandbox` / `webSecurity` | `false` / `true` / `true` / `true` |
| `plugins` | `false` |
| `devTools` | `isDev`（仅开发态可开） |
| `partition` | `ArtifactBrowserPartition.Default` |
| `preload` | `BROWSER_ANNOTATION_PRELOAD_PATH` |

教学要点：webview 是渲染层可通过 DOM 声明的"次级网页容器"，若只锁主窗口的 webPreferences 而不处理 webview，内嵌页面即可申请 `nodeIntegration: true` 逃逸沙箱。LobsterAI 的模式是"**主窗口从严、webview 重写兜底**"——挂载拦截点统一收口，且为制品浏览器指定独立存储分区（`ArtifactBrowserPartition.Default`）与专用注解 preload。

## 四、加载策略

- **开发模式**：`mainWindow.loadURL(DEV_SERVER_URL)`（Vite dev server，脚本 `electron:dev` 使用端口 5175），加载失败回退 `resources/error.html`（F-la-014、F-la-005）；
- **生产模式**：`mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))`（F-la-014）。

## 设计启示

1. 安全基线应按"十项全锁"为默认值书写，产品化例外（后台不节流、允许 webview）必须成对出现配套约束；
2. webview 偏好重写与主窗口配置属于同一安全域，应集中审查；
3. 主题色跟随窗口创建时确定，暗色/亮色常量与主进程托盘、边框等处保持一致。

## 相关概念

- [/concepts/00-overall-architecture.md](00-overall-architecture.md)
- [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)
