---
type: Concept
title: 安全与错误处理
description: KaTeX 的三层安全防御（maxSize/maxExpand/trust）、trust 控制的 HTML/URL/资源命令、HTML 消毒白名单风险、ParseError 异常类型、throwOnError 行为与错误消息 HTML 转义要求。
tags: [katex, security, trust, xss, parse-error, error-handling, sanitization]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-security
    resource: /references/katex-website.md#web-security
    title: KaTeX 官网 Security 页面
  - id: web-error
    resource: /references/katex-website.md#web-error
    title: KaTeX 官网 Handling Errors 页面
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
---

## 概述

KaTeX 生成的 HTML 设计为可防止 `<script>` 或其他代码注入攻击[^web-security]，但在处理不可信输入时仍需正确配置安全选项并对输出进行消毒。本文档融合官网 Security 与 Handling Errors 两个页面，说明三层防御纵深、trust 控制的命令范围、HTML 消毒白名单要求，以及 ParseError 的正确处理方式。

## 三层安全防御

KaTeX 在源码层面提供三个独立的安全配置项，构成防御纵深[^web-security]：

| 防线 | 选项 | 默认值 | 防御目标 |
|------|------|--------|---------|
| 视觉攻击 | `maxSize` | `Infinity` | 防止超大宽高元素（如 `\rule{500em}{500em}`）撑爆页面 |
| 宏循环 DoS | `maxExpand` | `1000` | 防止无限宏展开耗尽 CPU |
| 危险命令 | `trust` | `false` | 控制可能加载外部资源或改变 HTML 属性的命令 |

### maxSize

`maxSize` 限制用户指定尺寸（单位 em）的上限。默认 `Infinity`（不限制），设为非零值时元素和间距不超过该上限；设为零时不限制[^web-options]：

```javascript
katex.render(expr, element, {
    maxSize: 24  // 所有用户指定尺寸不超过 24em
});
```

### maxExpand

`maxExpand` 限制宏展开次数，防止恶意构造的无限宏循环（如 `\def\foo{\foo}\foo`）导致拒绝服务。默认 `1000`，设为 `Infinity` 时像 LaTeX 一样完全展开[^web-options]：

```javascript
katex.render(expr, element, {
    maxExpand: 1000  // 默认值，生产环境保持此值
});
```

`\edef` 展开计入所有展开 token。

### trust

`trust` 控制可能产生不良行为的命令（如加载外部图片、修改 HTML 属性）。默认 `false`，阻止这些命令并以 `errorColor` 渲染；设为 `true` 时允许所有此类命令[^web-options]：

```javascript
// 完全信任输入（仅在输入完全可信时使用）
katex.render(expr, element, { trust: true });

// 不可信输入（默认，安全）
katex.render(expr, element, { trust: false });
```

#### trust 控制的命令

`trust` 影响以下七类命令，每类在 trust 函数中接收对应的 context 对象[^web-options]：

| 命令 | context 字段 | 风险 |
|------|-------------|------|
| `\url{url}` | `{command: "\\url", url, protocol}` | 外部链接 |
| `\href{url}{text}` | `{command: "\\href", url, protocol}` | 外部链接 |
| `\includegraphics{url}` | `{command: "\\includegraphics", url, protocol}` | 外部图片资源 |
| `\htmlClass{class}{content}` | `{command: "\\htmlClass", class}` | 修改 CSS 类 |
| `\htmlId{id}{content}` | `{command: "\\htmlId", id}` | 修改元素 ID |
| `\htmlStyle{style}{content}` | `{command: "\\htmlStyle", style}` | 修改内联样式 |
| `\htmlData{key=value}{content}` | `{command: "\\htmlData", attributes}` | 修改 data 属性 |

其中 `protocol` 为小写字符串（如 `"http"`、`"https"`）；相对 URL 的 protocol 为 `"_relative"`。

#### trust 自定义函数

`trust` 可以是函数，接收 context 对象并返回布尔值，实现细粒度控制[^web-options]：

```javascript
katex.render(expr, element, {
    trust: function(context) {
        // 只允许相对路径的 \url 和 \href
        if (context.command === "\\url" || context.command === "\\href") {
            return context.protocol === "_relative"
                || context.protocol === "https";
        }
        // 允许 \includegraphics 但仅允许 https 图片
        if (context.command === "\\includegraphics") {
            return context.protocol === "https";
        }
        // 阻止所有 HTML 修改命令
        return false;
    }
});
```

> **安全提示**：持久宏（`\gdef`/`\global\let`）可改变 KaTeX 行为（如重定义标准命令），应仅在共同信任的多个元素间使用，不应跨多用户消息启用。详见 [宏系统](/concepts/09-macro-system.md)。

## HTML 消毒

### 消毒建议

即使 KaTeX 自身设计防止 `<script>` 注入，官网仍建议对 KaTeX 生成的 HTML 进行消毒[^web-security]。但消毒器必须使用**相当宽松的白名单**，因为 KaTeX 输出包含：

- **MathML** 元素（`<math>`、`<semantics>`、`<annotation>` 等）——屏幕阅读器需要
- **部分 SVG** 元素（可伸缩分隔符、根号等几何图形使用）
- KaTeX 自定义 CSS 类名（v0.18+ 均以 `katex-` 为前缀）

过于严格的消毒器（如默认只允许标准 HTML 标签）会破坏 MathML 语义或 SVG 图形，导致无障碍功能失效或渲染异常。

### 消毒白名单风险

配置消毒白名单时需注意：

1. **MathML 标签**必须保留，否则屏幕阅读器无法识别公式
2. **SVG 标签和属性**（`viewBox`、`preserveAspectRatio`、`d` 路径数据等）必须保留，否则可伸缩分隔符渲染失败
3. **KaTeX CSS 类**（`.katex`、`.katex-display`、`.mord`、`.mbin` 等）不应被剥离
4. **`aria-hidden`** 等无障碍属性需保留

### 三层防护与消毒的协作

```
不可信输入
    │
    ├── maxSize（限制尺寸）
    ├── maxExpand（限制展开次数）
    └── trust（控制危险命令）
            │
            ▼
    KaTeX 渲染输出（HTML + MathML）
            │
            ▼
    HTML 消毒（宽松白名单，保留 SVG/MathML）
            │
            ▼
    安全嵌入页面
```

## 错误处理

### ParseError 异常

当 KaTeX 遇到不支持的命令或无效 LaTeX，且 `throwOnError` 未设为 `false` 时，`render` 和 `renderToString` 抛出 `katex.ParseError` 类型异常[^web-error]：

```javascript
try {
    katex.render(expr, element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        // KaTeX 解析错误，安全处理
        console.error("KaTeX 解析错误:", e.message);
    } else {
        // 其他错误（如网络、DOM 异常），重新抛出
        throw e;
    }
}
```

### throwOnError: false

设 `throwOnError: false` 时，KaTeX 不抛异常，而是将不支持的命令渲染为文本、无效 LaTeX 以源码形式渲染（hover 文本显示错误消息），颜色由 `errorColor` 指定（默认 `#cc0000`）[^web-options]：

```javascript
katex.render(expr, element, {
    throwOnError: false,
    errorColor: "#cc0000"  // 错误文本颜色，默认红色
});
```

### 错误消息的 HTML 转义

KaTeX 抛出的错误消息可能包含**未转义的 LaTeX 源码**[^web-security]。将错误消息显示到页面前，必须进行 HTML 转义，否则可能导致 `<script>` 注入攻击[^web-error]：

```javascript
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

try {
    katex.render(expr, element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        // 必须转义后再插入 DOM
        element.innerHTML = '<span class="error">'
            + escapeHtml(e.message) + '</span>';
    } else {
        throw e;
    }
}
```

未转义的不可信 LaTeX 源码或异常消息可能包含 `<script>` 标签等恶意内容，直接通过 `innerHTML` 插入会导致 XSS。

## 安全配置清单

处理不可信输入时，推荐以下基线配置：

```javascript
katex.render(untrustedExpr, element, {
    throwOnError: false,       // 不抛异常，渲染错误状态
    errorColor: "#cc0000",     // 错误文本颜色
    maxSize: 24,               // 限制超大尺寸
    maxExpand: 1000,           // 保持默认，防宏循环
    trust: false,              // 禁止危险命令
    strict: "warn",            // 默认，对非标准特性警告
    macros: {}                 // 每条消息独立 macros 对象，不跨用户共享
});
```

渲染后对输出 HTML 进行消毒（白名单需包含 MathML 和部分 SVG）。

## 漏洞报告

发现 KaTeX 安全漏洞时，应私下通过 GitHub Security Advisory 或邮件 `katex-security@mit.edu` 报告，评估后发布修复和安全公告；修复发布前不公开披露[^web-security]。

## 相关概念

- [配置系统](/concepts/10-settings-options.md) — strict、trust、maxSize、maxExpand 等选项的完整参考
- [宏系统](/concepts/09-macro-system.md) — 持久宏机制与 macros 对象共享安全
- [错误处理示例](/examples/error-handling.md) — 可复制的错误处理代码
- [自动渲染扩展](/concepts/13-auto-render.md) — errorCallback 钩子与宏持久化

[^web-security]: 官网 Security 页面，https://katex.org/docs/security
[^web-error]: 官网 Handling Errors 页面，https://katex.org/docs/error
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
