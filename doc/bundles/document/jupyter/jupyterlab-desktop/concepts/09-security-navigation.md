---
type: Concept
title: 安全与导航策略
description: Electron 导航安全守卫机制、WebContents 声明模式、外部链接处理、WebView 阻止、GetServerInfo origin 校验、HTTP 认证对话框
tags: [security, navigation, guard, webcontents, origin-validation, webview, external-links, auth]
prerequisites:
  - /concepts/08-event-ipc-system.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: navigation-source
    resource: /references/navigation-source.md
    title: 导航安全源码信源
  - id: app-source
    resource: /references/app-source.md
    title: 主应用类源码信源
---

# 安全与导航策略

## 概述

JupyterLab Desktop 运行不受信的 Jupyter Notebook 内容，因此需要严格的安全策略防止恶意页面逃离 Electron 沙箱、替换应用 chrome、窃取服务器 token 或打开恶意窗口。导航安全系统通过多层防御机制实现这些保护。

## 威胁模型

| 威胁 | 防御机制 |
|------|---------|
| Notebook 页面导航到恶意网站替换应用 UI | 导航守卫默认 deny |
| Notebook 弹出新窗口加载钓鱼页面 | setWindowOpenHandler 默认 deny |
| Notebook 通过 IPC 窃取服务器 token | GetServerInfo origin 校验 |
| Notebook 嵌入 webview 加载任意内容 | will-attach-webview 阻止 |
| 子框架（iframe）导航到外部 URL | 子框架导航仅 deny，不外部打开 |
| 恶意 URL 含控制字符传递给系统浏览器 | URL 规范化（new URL().href） |

## 三层导航安全架构

```
第1层：全局守卫（installGlobalNavigationGuard）
  ↓ 默认 deny，未声明的 webContents 完全阻止导航
第2层：视图声明（markGuarded / guardAppOwnedView / 自定义策略）
  ↓ 每个 webContents 显式声明自己的导航策略
第3层：IPC 安全校验（GetServerInfo origin 验证）
  ↓ 对安全敏感的 IPC 消息额外验证发送方身份
```

## 第1层：全局导航守卫

### 安装时机

`installGlobalNavigationGuard()` 在 `JupyterApplication` 构造函数的**第一行**调用，在任何 BrowserWindow 或 WebContentsView 创建之前。这确保所有后续创建的 webContents 都被守卫覆盖。

### 实现

```typescript
app.on('web-contents-created', (_event, contents) => {
  // 默认导航策略：未声明的 webContents → deny
  guardNavigation(contents, () =>
    guarded.has(contents) ? 'allow' : 'deny'
  );

  // 默认窗口策略：未声明的 webContents 阻止新窗口
  contents.setWindowOpenHandler(({ url }) => {
    log.warn(`Blocked window opening ${url} from an unguarded view`);
    return { action: 'deny' };
  });
});
```

**关键时序**：守卫在 `web-contents-created` 事件中安装，该事件在 webContents 创建时同步触发，在任何导航发生之前。视图创建后可以设置自己的 handler 替换默认 deny handler。

## 第2层：视图导航策略

### NavigationDecision 类型

```typescript
type NavigationDecision = 'allow' | 'external' | 'deny';
```

| 决策 | 行为 |
|------|------|
| `allow` | 允许在当前 webContents 内导航 |
| `external` | 主框架：在系统默认浏览器打开；子框架：阻止 |
| `deny` | 完全阻止导航 |

### guardNavigation() 函数

为指定 webContents 安装导航守卫，监听四个事件：

| 事件 | 处理 |
|------|------|
| `will-navigate` | 主框架导航，应用决策 |
| `will-redirect` | HTTP 重定向，应用决策 |
| `will-frame-navigate` | 子框架导航（仅处理非主框架） |
| `will-attach-webview` | 阻止所有 webview 附加（preventDefault） |

**主框架 vs 子框架处理差异**：
- 主框架 `external` → 系统浏览器打开（用户主动点击链接）
- 子框架 `external` → 阻止并记录 debug 日志（页面自身布局中的 iframe，非用户意图）

### markGuarded(contents)

将 webContents 标记为"已声明"，使其在全局守卫中获得 `allow` 导航决策。使用 `WeakSet<WebContents>` 追踪，不阻止 GC。

调用 `markGuarded()` 后，全局守卫会允许该 webContents 的导航，但视图通常还会叠加自己的更具体策略。

### guardAppOwnedView(contents)

保护应用自有视图（TitleBarView、WelcomeView、对话框等渲染打包 HTML 的视图）：

1. 调用 `markGuarded(contents)` 声明为已保护
2. 安装导航守卫，所有导航决策为 `external`（链接在系统浏览器打开）
3. 设置 `setWindowOpenHandler`：新窗口请求在系统浏览器打开并 deny 弹窗

**设计意图**：这些视图渲染的是应用内置 HTML（非 notebook 内容），不应导航到其他页面。新闻订阅等外部链接应在系统浏览器中打开，而不是替换应用 chrome。

```typescript
export function guardAppOwnedView(contents: WebContents): void {
  markGuarded(contents);
  guardNavigation(contents, () => 'external');
  contents.setWindowOpenHandler(({ url }) => {
    openUrlInSystemBrowser(url);
    return { action: 'deny' };
  });
}
```

### LabView 的自定义策略

LabView 渲染 notebook 内容，采用更精细的导航策略：
- 同 origin（Jupyter Server）导航 → allow
- 外部链接 → external（系统浏览器）
- 其他 → deny

### openUrlInSystemBrowser(url)

在系统默认浏览器中打开 URL，有严格的协议白名单：

```typescript
export function openUrlInSystemBrowser(url: string): void {
  if (matchesScheme(url, 'http:', 'https:', 'mailto:')) {
    shell.openExternal(new URL(url).href);  // URL 规范化
  }
}
```

安全措施：
- 仅允许 `http:`、`https:`、`mailto:` 协议（阻止 `file:`、`javascript:` 等危险协议）
- 使用 `new URL(url).href` 规范化 URL，去除空白和控制字符

## 第3层：IPC 安全校验

### GetServerInfo 的 Origin 校验

`GetServerInfo` IPC 事件返回服务器 token，是最敏感的信息。处理时区分 webContents：

| webContents 类型 | 校验方式 |
|-----------------|---------|
| TitleBarView | 对象身份验证（`event.sender === titleBarView.webContents`） |
| LabView | origin 校验：`new URL(event.senderFrame.url).origin === server.info.url.origin` |
| 其他 | 拒绝返回 |

**为什么 LabView 需要 origin 校验**：
- LabView 加载的是 Jupyter Server 返回的 notebook 页面
- 但 notebook 中可能包含恶意 JavaScript 代码
- 恶意代码可以通过 IPC 调用 `get-server-info` 获取 token
- origin 校验确保只有 Jupyter Server 同源的 frame 才能获取 token
- 如果 notebook 被嵌入 iframe（不同 origin），iframe 无法获取 token

## HTTP 认证对话框

当 Jupyter Server 启用 HTTP Basic Auth 时，Electron 触发 `app.on('login')` 事件：

- 应用弹出认证对话框（AuthDialog）
- 用户输入用户名和密码
- 凭据通过 `callback(username, password)` 提供给 Electron
- AuthWindow 类专门处理需要复杂登录流程的场景（如 OAuth 重定向）

## WebView 阻止

所有 webContents 都阻止 `<webview>` 标签附加：

```typescript
contents.on('will-attach-webview', event => {
  event.preventDefault();
});
```

webview 是 Electron 中一个强大但危险的标签，可以加载任意网页并拥有 Node.js 访问权限（取决于配置）。阻止 webview 附加消除了这个攻击面。

## 相关信源

- [Navigation 信源](../references/navigation-source.md)
- [App 信源](../references/app-source.md)
- [Event 信源](../references/event-source.md)

## 下一篇

- [多窗口与会话管理](10-multi-window-multisession.md)

## 相关概念

- [事件与IPC系统](08-event-ipc-system.md) — GetServerInfo origin 校验依赖 IPC 事件处理机制
- [会话窗口系统](03-session-window-system.md) — guardAppOwnedView 在 SessionWindow 构造时安装
- [多窗口与会话管理](10-multi-window-multisession.md) — 多窗口环境下安全守卫的安装与维护
