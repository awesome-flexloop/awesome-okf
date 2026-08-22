---
type: Reference
title: 导航安全策略源码信源
description: src/main/navigationguard.ts 导航安全守卫源码登记，包含全局导航拦截、WebContents 声明机制、外部链接处理、WebView 阻止策略
tags: [security, navigation, guard, webcontents, shell, webview, openexternal]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: navigationguard-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/navigationguard.ts
    title: navigationguard.ts source on GitHub
---

# 导航安全策略源码信源

## 源码路径

`src/main/navigationguard.ts`

## 文件职责

实现 Electron 应用的导航安全策略，防止 webContents 被恶意导航到不受信页面，阻止未授权的新窗口弹出，确保 app chrome 不被网络页面替换。

## 设计原则

1. **默认拒绝**：未被声明的 webContents 默认拒绝所有导航
2. **声明式保护**：通过 `markGuarded()`/`guardAppOwnedView()` 显式声明安全策略
3. **外部链接处理**：http/https/mailto 链接在系统默认浏览器中打开，不在应用内导航
4. **WebView 阻止**：禁止所有 `<webview>` 标签的附加（`will-attach-webview` preventDefault）
5. **主框架 vs 子框架区分**：只有主框架的导航可以外部打开，子框架导航直接拒绝

## 核心类型

```typescript
type NavigationDecision = 'allow' | 'external' | 'deny';
```

- `allow`：允许在当前 webContents 内导航
- `external`：在系统默认浏览器中打开（仅主框架）
- `deny`：完全阻止导航

## 核心函数

### markGuarded(contents: WebContents): void

将 webContents 标记为"已声明"，使其在全局守卫中获得 `allow` 决策。使用 `WeakSet<WebContents>` 追踪，不阻止 GC。

### openUrlInSystemBrowser(url: string): void

在系统默认浏览器中打开 URL：
- 仅允许 `http:`、`https:`、`mailto:` 协议
- 使用 `new URL(url).href` 规范化 URL，防止空白和控制字符传递给 OS
- 调用 `shell.openExternal()` 打开

### guardNavigation(contents, decide): void

为指定 webContents 安装导航守卫：

监听以下事件：
1. **`will-navigate`**：主框架导航
2. **`will-redirect`**：HTTP 重定向
3. **`will-frame-navigate`**：子框架导航（仅处理非主框架）
4. **`will-attach-webview`**：阻止 webview 附加（preventDefault）

决策逻辑：
- `allow` → 不阻止，正常导航
- `external` + isMainFrame → preventDefault + `shell.openExternal()`
- `external` + 子框架 → preventDefault + debug 日志
- `deny` → preventDefault + warn 日志

### guardAppOwnedView(contents: WebContents): void

保护应用自有视图（TitleBarView、WelcomeView 等渲染打包文档的视图）：
1. 调用 `markGuarded(contents)` 声明为已保护
2. 安装守卫，所有导航决策为 `external`（在浏览器中打开）
3. 设置 `setWindowOpenHandler`：所有新窗口请求在系统浏览器打开并 deny 弹窗

### installGlobalNavigationGuard(): void

安装应用级全局导航守卫（在 JupyterApplication 构造函数最先调用）：

1. 监听 `app.on('web-contents-created')` 事件
2. 对每个新创建的 webContents：
   - 安装导航守卫：未 markGuarded 的 → `deny`（阻止导航）；已 markGuarded 的 → `allow`
   - 设置 `setWindowOpenHandler`：未声明的 webContents 的新窗口请求全部 deny 并 warn 日志
3. 安全时序：全局守卫在任何 webContents 创建之前安装，owner 设置自己的 handler 时会替换默认 deny handler

## 安全时序说明

```
app ready
  → installGlobalNavigationGuard()  // 最先安装，此时无任何 webContents
  → 创建 BrowserWindow/webContents  // 此时会触发 web-contents-created，默认 deny
  → 调用 markGuarded()/guardNavigation()/setWindowOpenHandler()  // 声明策略，替换默认 handler
```

## 典型使用场景

| View | 策略 | 说明 |
|------|------|------|
| TitleBarView | `guardAppOwnedView()` | 渲染打包 HTML，链接外部打开 |
| WelcomeView | `guardAppOwnedView()` | 渲染欢迎页，链接外部打开 |
| SettingsDialog 等 Dialog | `guardAppOwnedView()` | 渲染设置对话框 |
| LabView | 自定义策略 | 由 origin 校验决定（仅允许同 origin 导航） |
| AuthWindow | 自定义策略 | 允许跟随登录流程到任意 URL |

## 相关概念

- [安全与导航策略](/concepts/09-security-navigation.md)
- [会话窗口系统](/concepts/03-session-window-system.md)
