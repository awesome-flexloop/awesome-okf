---
type: Example
title: 安全与信任配置示例
description: KaTeX 不可信输入的安全配置实践，包括 trust 函数策略、maxSize/maxExpand 防御、错误消息 HTML 转义、输出消毒白名单和持久宏隔离。
tags: [katex, example, security, trust, xss, sanitization, maxSize, maxExpand, untrusted-input]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:40:00+08:00 }
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
  - id: web-api
    resource: /references/katex-website.md#web-api
    title: KaTeX 官网 API 页面
---

## 何时需要安全配置

KaTeX 生成的 HTML 设计上可防止 `<script>` 注入，但处理不可信输入（用户评论、论坛帖子、聊天消息、第三方内容）时仍需配置安全防线[^web-security]。

| 输入来源 | trust | 输出消毒 | macros 隔离 |
|---------|-------|---------|------------|
| 自己编写的可信文档 | `true` 或按需 | 不需要 | 可共享 |
| 团队内部可信内容 | 函数策略 | 建议 | 按文档隔离 |
| 已登录用户（半可信） | 函数策略 | 需要 | 每会话/每文档隔离 |
| 匿名用户/公开评论 | `false` | **必须** | **每消息独立** |

## 三层防御纵深

KaTeX 提供三个独立的安全配置项[^web-security]：

| 配置 | 默认值 | 防御目标 |
|------|--------|---------|
| `maxSize` | `Infinity` | 超大宽高视觉攻击（如 `\rule{1000em}{1000em}`） |
| `maxExpand` | `1000` | 无限宏循环拒绝服务 |
| `trust` | `false` | 可能加载外部资源或修改 HTML 属性的命令 |

### 不可信输入基线配置

```javascript
const secureOptions = {
    throwOnError: false,
    errorColor: "#cc0000",
    strict: "warn",
    maxSize: 20,
    maxExpand: 1000,
    trust: false,
    macros: {},
    globalGroup: false,
};
```

- `maxSize: 20` 将用户指定尺寸限制在 20em 以内，防止视觉破坏
- `maxExpand: 1000` 保持默认值，阻止无限宏循环
- `trust: false` 阻止 `\url`、`\href`、`\includegraphics` 等可能产生外部链接或资源加载的命令
- `macros: {}` 每次创建独立对象，防止宏污染
- `globalGroup: false` 阻止顶层 `\def` 逃逸到 macros 对象

## trust 配置详解

### trust: false（默认）

`trust: false` 时，以下命令以 errorColor 渲染为错误文本而非正常执行[^web-options]：

- `\url{...}` — 插入 URL
- `\href{...}{...}` — 创建超链接
- `\includegraphics{...}` — 插入外部图片
- `\htmlClass{...}{...}` — 添加 HTML class
- `\htmlId{...}{...}` — 添加 HTML id
- `\htmlStyle{...}{...}` — 添加 inline style
- `\htmlData{...}{...}` — 添加 data 属性

```javascript
katex.render("\\url{https://example.com}", el, {
    trust: false,
    throwOnError: false,
});
```

### trust: true（完全信任）

`trust: true` 允许所有上述命令，仅在内容完全可信时使用（如自己编写的文档）：

```javascript
katex.render("\\href{https://example.com}{链接}", el, {
    trust: true,
});
```

> **警告**：对不可信输入设 `trust: true` 可能允许 `javascript:` 协议链接或外部图片追踪。

### trust 函数（精细控制）

`trust` 接受函数，接收 context 对象并返回布尔值，可按命令和协议精细授权[^web-options]：

```javascript
katex.render(userInput, el, {
    throwOnError: false,
    trust: function(context) {
        switch (context.command) {
            case "\\url":
            case "\\href":
                return isSafeUrl(context.url, context.protocol);
            case "\\includegraphics":
                return context.protocol === "https";
            case "\\htmlClass":
            case "\\htmlId":
            case "\\htmlStyle":
            case "\\htmlData":
                return false;
            default:
                return false;
        }
    },
});

function isSafeUrl(url, protocol) {
    if (protocol === "_relative") {
        return true;
    }
    return protocol === "http" || protocol === "https";
}
```

### trust context 字段

| 命令 | context 字段 |
|------|-------------|
| `\url`、`\href`、`\includegraphics` | `{command, url, protocol}` |
| `\htmlClass` | `{command, class}` |
| `\htmlId` | `{command, id}` |
| `\htmlStyle` | `{command, style}` |
| `\htmlData` | `{command, attributes}` |

`protocol` 为小写字符串（`"http"`、`"https"`、`"javascript"` 等）；相对 URL 的 protocol 为 `"_relative"`[^web-options]。

### 常见 trust 策略

```javascript
const trustPolicies = {
    httpsOnly(context) {
        if (context.command === "\\includegraphics") {
            return context.protocol === "https";
        }
        if (context.command === "\\url" || context.command === "\\href") {
            return context.protocol === "https"
                || context.protocol === "_relative";
        }
        return false;
    },

    allowLinksBlockImages(context) {
        if (context.command === "\\url" || context.command === "\\href") {
            return context.protocol !== "javascript"
                && context.protocol !== "data";
        }
        return false;
    },

    blockAll(context) {
        return false;
    },
};
```

## 错误处理与消息转义

KaTeX 抛出的 `ParseError` 消息可能包含**未转义的 LaTeX 源码**。将错误消息显示到页面前必须进行 HTML 转义，否则可能导致 `<script>` 注入[^web-error]。

```javascript
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function renderSafely(latex, element) {
    try {
        katex.render(latex, element, {
            throwOnError: true,
            strict: "warn",
            maxSize: 20,
            maxExpand: 1000,
            trust: false,
            macros: {},
        });
        return true;
    } catch (e) {
        if (e instanceof katex.ParseError) {
            element.innerHTML =
                '<span class="katex-error" title="'
                + escapeHtml(e.message) + '">'
                + escapeHtml(latex) + '</span>';
            return false;
        }
        throw e;
    }
}
```

关键点：
- 使用 `e instanceof katex.ParseError` 判断是否为 KaTeX 解析错误
- 非 ParseError 错误应重新抛出，不要静默吞掉
- `e.message` 和原始 LaTeX 源码都需转义后再插入 DOM

## 输出 HTML 消毒

即使 KaTeX 自身防止 `<script>` 注入，官网仍建议对输出 HTML 进行消毒。消毒白名单需要相当宽松，必须包含部分 SVG 和 MathML 标签以支持全部 KaTeX 功能[^web-security]。

### 使用 DOMPurify 消毒

```javascript
import DOMPurify from "dompurify";

const KATEX_TAGS = [
    "span", "a", "svg", "path", "line", "img",
    "math", "semantics", "annotation", "mrow", "mi", "mo",
    "mn", "msup", "msub", "mfrac", "msqrt", "mtable",
    "mtr", "mtd", "mtext", "mspace", "mstyle", "merror",
    "mpadded", "mphantom",
];

const KATEX_ATTR = [
    "class", "style", "href", "xlink:href",
    "width", "height", "viewBox", "d", "fill",
    "stroke", "stroke-width", "aria-hidden", "role",
    "encoding", "title",
];

function sanitizeKatexHtml(html) {
    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: KATEX_TAGS,
        ALLOWED_ATTR: KATEX_ATTR,
        ADD_URI_SAFE_ATTR: ["xlink:href"],
    });
}

const raw = katex.renderToString(userInput, {
    throwOnError: false,
    trust: false,
});
const safe = sanitizeKatexHtml(raw);
element.innerHTML = safe;
```

### 服务端消毒（Node.js）

```javascript
const katex = require("katex");
const createDOMPurify = require("dompurify");
const {JSDOM} = require("jsdom");

const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);

function safeRenderToString(latex, options = {}) {
    const raw = katex.renderToString(latex, {
        throwOnError: false,
        maxSize: 20,
        maxExpand: 1000,
        trust: false,
        macros: {},
        ...options,
    });
    return DOMPurify.sanitize(raw, {
        ADD_TAGS: ["svg", "path", "line", "math", "mrow", "mi", "mo"],
        ADD_ATTR: ["class", "style", "viewBox", "d", "aria-hidden"],
    });
}
```

> **注意**：白名单需根据实际使用的 KaTeX 功能调整。过于严格的白名单会破坏 MathML 无障碍输出和 SVG 渲染（如根号、大括号）。

## 持久宏隔离

持久宏通过共享 `macros` 对象实现，该对象会被 `\gdef`、`\global\let` 修改。在多用户场景中，共享 macros 对象意味着一个用户可重定义标准命令影响其他用户[^web-api]。

### 危险：跨用户共享 macros

```javascript
const sharedMacros = {};

function renderUserMessage(userId, message, el) {
    katex.render(message, el, {
        macros: sharedMacros,
        throwOnError: false,
    });
}
```

用户 A 发送 `\gdef\frac#1#2{#1/#2}` 后，用户 B 的所有分数都会被篡改。

### 正确：每消息独立 macros

```javascript
function renderUserMessage(message, el) {
    katex.render(message, el, {
        macros: {},
        throwOnError: false,
        trust: false,
        maxExpand: 1000,
        maxSize: 20,
        globalGroup: false,
    });
}

messages.forEach(msg => {
    const el = document.createElement("div");
    renderUserMessage(msg.latex, el);
    container.appendChild(el);
});
```

### 同一可信文档内共享

同一作者的同一篇文档中，多个公式块可安全共享 macros 以支持 `\gdef` 跨块：

```javascript
function renderArticle(blocks) {
    const articleMacros = {};
    return blocks.map(block =>
        katex.renderToString(block, {
            macros: articleMacros,
            throwOnError: false,
            trust: true,
        })
    );
}
```

## 完整安全封装

```javascript
const katex = require("katex");

const SECURE_DEFAULTS = Object.freeze({
    throwOnError: false,
    errorColor: "#cc0000",
    strict: "warn",
    maxSize: 20,
    maxExpand: 1000,
    trust: false,
    globalGroup: false,
});

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function renderUntrusted(latex, overrides = {}) {
    const options = {
        ...SECURE_DEFAULTS,
        macros: {},
        ...overrides,
    };

    try {
        return {
            ok: true,
            html: katex.renderToString(latex, options),
        };
    } catch (e) {
        if (e instanceof katex.ParseError) {
            return {
                ok: false,
                html: '<span class="katex-error" title="'
                    + escapeHtml(e.message) + '">'
                    + escapeHtml(latex) + '</span>',
                error: e.message,
            };
        }
        throw e;
    }
}

const result = renderUntrusted(userInput, {
    displayMode: true,
});
container.innerHTML = result.html;
```

## 安全检查清单

处理不可信 LaTeX 输入时逐项确认：

- [ ] `trust` 设为 `false` 或白名单函数，不对匿名用户设 `true`
- [ ] `maxSize` 设为合理上限（如 20em），不使用 `Infinity`
- [ ] `maxExpand` 保持 1000 或更低，不设为 `Infinity`
- [ ] `macros` 每次创建独立 `{}`，不跨用户共享
- [ ] `globalGroup` 保持 `false`
- [ ] `throwOnError: false` 或捕获 ParseError 后转义错误消息
- [ ] 错误消息和原始 LaTeX 在插入 DOM 前经过 HTML 转义
- [ ] 输出 HTML 经过消毒（白名单包含 MathML 和 SVG）
- [ ] 不使用 `__defineMacro` 注册全局宏（影响所有调用）
- [ ] CSS/字体从可信源加载，不允许用户控制资源 URL

## 漏洞报告

发现 KaTeX 安全漏洞时，私下通过 GitHub security advisory 或邮件 katex-security@mit.edu 报告；修复发布前不公开披露[^web-security]。

## 相关内容

- [安全与错误处理](/concepts/18-security-and-errors.md)
- [配置选项](/concepts/10-settings-options.md)
- [错误处理示例](/examples/error-handling.md)
- [自定义宏示例](/examples/custom-macros.md)
- [Node.js 服务端渲染示例](/examples/node-ssr.md)

[^web-security]: 官网 Security 页面，https://katex.org/docs/security
[^web-error]: 官网 Handling Errors 页面，https://katex.org/docs/error
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
[^web-api]: 官网 API 页面，https://katex.org/docs/api
