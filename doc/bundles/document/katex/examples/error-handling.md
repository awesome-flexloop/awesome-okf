---
type: Example
title: 错误处理示例
description: KaTeX 的错误处理机制，包括 throwOnError、errorColor、strict 模式（默认 warn）、ParseError 捕获、错误消息 HTML 转义（& < >）、trust 安全配置和安全封装函数。
tags: [katex, example, error, ParseError, strict, throwOnError, security, xss]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-error
    resource: /references/katex-website.md#web-error
    title: KaTeX 官网 Handling Errors 页面
  - id: web-security
    resource: /references/katex-website.md#web-security
    title: KaTeX 官网 Security 页面
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
---

## KaTeX错误类型

KaTeX可能产生以下错误：

| 错误类型 | 触发场景 |
|---------|---------|
| `ParseError` | LaTeX语法错误（未知命令、参数缺失、花括号不匹配等） |
| `RangeError` | 栈溢出（极深嵌套） |
| 其他Error | 字体加载失败、DOM异常（浏览器端）等 |

其中 `ParseError` 是最常见的错误类型，由 [src/ParseError.ts](https://github.com/KaTeX/KaTeX/blob/main/src/ParseError.ts) 定义。

## throwOnError：控制异常抛出

### 默认行为（throwOnError: true）

默认情况下，遇到解析错误会抛出异常：

```javascript
try {
    katex.render("\\invalidCommand", element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        console.error("LaTeX解析错误:", e.message);
        // 显示友好错误消息
        element.textContent = "公式语法错误: " + e.message;
    } else {
        // 非ParseError（如DOM错误），重新抛出
        throw e;
    }
}
```

### 静默错误（throwOnError: false）

设为 `false` 时，KaTeX 不会抛异常，而是渲染红色错误文本：

```javascript
katex.render("\\invalidCommand", element, {
    throwOnError: false,
    errorColor: "#cc0000",  // 红色（默认）
});
```

渲染效果：`\invalidCommand` 以红色文本显示（带 `.katex-error` CSS类），不会中断页面其他内容。

### errorColor：自定义错误颜色

```javascript
// 橙色错误提示
katex.render(badLatex, el, {
    throwOnError: false,
    errorColor: "#ff8c00"
});

// 紫色错误提示
katex.render(badLatex, el, {
    throwOnError: false,
    errorColor: "#9932cc"
});

// 使用CSS自定义更丰富的错误样式
katex.render(badLatex, el, {
    throwOnError: false,
    errorColor: "#cc0000"
});
// 然后通过CSS：
// .katex-error {
//     background: #fff0f0;
//     border: 1px solid #cc0000;
//     border-radius: 3px;
//     padding: 2px 4px;
// }
```

## ParseError 对象

`ParseError` 实例包含：

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | string | `"ParseError"` |
| `message` | string | 错误描述消息 |
| `position` | number | 错误在输入字符串中的位置（字节偏移） |
| `length` | number | 错误Token的长度 |
| `input` | string? | 原始输入字符串 |

```javascript
try {
    katex.render("\\frac{a}{b", element);  // 缺少右花括号
} catch (e) {
    if (e instanceof katex.ParseError) {
        console.log("错误消息:", e.message);     // "Expected '}' or ']'"
        console.log("错误位置:", e.position);    // 数字（字符偏移）
        console.log("输入字符串:", e.input);     // "\frac{a}{b"

        // 可以显示错误位置指示器
        if (e.input && typeof e.position === "number") {
            const indicator = " ".repeat(e.position) + "^";
            console.log(e.input);
            console.log(indicator);
        }
    }
}
```

## strict模式：非标准用法警告

`strict` 选项控制 KaTeX 对不推荐用法的处理，默认值为 `"warn"`[^web-options]：

### strict: "warn"（默认）

在控制台输出警告，但继续渲染：

```javascript
katex.render("\\rm{旧字体命令}", el, {
    strict: "warn"  // 默认值
});
// Console: "LaTeX-incompatible input: \rm is an old font command"
```

strict模式警告的常见问题：
- 使用旧字体命令（`\rm`、`\bf`、`\it`），应使用 `\mathrm`、`\mathbf`、`\mathit`
- 在数学模式中使用文本模式命令
- 多余的花括号
- 不推荐的命令别名
- Unicode字符不支持

### strict: false / "ignore"

静默接受所有支持的命令，不输出警告：

```javascript
katex.render(latex, el, { strict: false });
// 或
katex.render(latex, el, { strict: "ignore" });
```

### strict: "error"

将警告升级为ParseError，抛出异常：

```javascript
try {
    katex.render("\\bf{bold}", el, {strict: "error"});
} catch (e) {
    // ParseError: "LaTeX-incompatible input..."
}
```

适用于：
- 严格LaTeX兼容要求的场景
- CI/CD 中验证LaTeX源码质量
- 教学环境（强制学习正确的LaTeX语法）

### strict: 自定义函数

完全自定义每种错误的处理方式：

```javascript
katex.render(latex, el, {
    strict: function(errorCode, errorMsg, token) {
        console.log("严格模式警告:", errorCode, errorMsg);

        switch (errorCode) {
            case "unknownSymbol":
                return "ignore";    // 未知符号：忽略
            case "oldFontCommand":
                return "warn";      // 旧字体命令：警告
            case "mathVsTextUnits":
                return "error";     // 单位错误：抛异常
            default:
                return "warn";
        }
    }
});
```

### 常见strict错误码

| errorCode | 含义 |
|-----------|------|
| `"unknownSymbol"` | 使用了不支持的Unicode字符 |
| `"unicodeTextInMathMode"` | 数学模式中使用文本Unicode字符 |
| `"mathVsTextUnits"` | 使用了文本模式单位（如em/ex/pt在数学中） |
| `"commentAtEnd"` | 注释`%`在行末的行为 |
| `"htmlExtension"` | 使用了html扩展命令 |
| `"oldFontCommand"` | 使用了`\rm`/`\bf`/`\it`等旧字体命令 |
| `"newLineInParagraph"` | 段落中的换行符 |
| `"doubleExponent"` | 双重上标（如`x^2^3`） |
| `"doubleSubscript"` | 双重下标（如`x_2_3`） |

## 宏展开错误

宏展开错误通常是递归宏或展开次数超限：

### 无限递归宏

```javascript
try {
    katex.render("\\def\\a{\\a}\\a", el);
} catch (e) {
    // "Too many expansions: infinite loop or need to increase maxExpand setting"
}
```

### 增大展开上限

对于合法但复杂的宏（如大量嵌套的`\newcommand`），可以增大 `maxExpand`：

```javascript
katex.render(complexLatex, el, {
    maxExpand: 5000,    // 默认1000，按需增大
    throwOnError: true,
});
```

注意：不要设置过大（如Infinity），否则恶意输入可能导致浏览器卡死。

## 花括号和分组错误

常见语法错误：

```javascript
// 缺少右花括号
katex.render("\\frac{a}{b", el, {throwOnError: false});  // 错误

// 多余右花括号
katex.render("\\frac{a}{b}}", el, {throwOnError: false}); // 错误

// \left\right不配对
katex.render("\\left(\\frac{a}{b}", el, {throwOnError: false});  // 缺少\right

// 正确
katex.render("\\left(\\frac{a}{b}\\right)", el);
```

## 安全相关错误（trust模式）

使用 `\href`、`\url`、`\includegraphics` 等可能导致XSS的命令时，需要设置trust：

```javascript
// 默认 trust: false，以下会渲染错误
katex.render("\\href{https://example.com}{link}", el, {throwOnError: false});
// 错误："The command '\href' is not allowed in a restricted environment"

// 启用trust
katex.render("\\href{https://example.com}{link}", el, {
    trust: true  // 允许所有链接（仅在可信内容时使用）
});

// 自定义trust策略（推荐）
katex.render(userInputLatex, el, {
    throwOnError: false,
    trust: function(context) {
        // 只允许https链接和相对路径
        if (context.command === "\\href" || context.command === "\\url") {
            const url = context.url;
            if (url.startsWith("https://") || url.startsWith("/")) {
                return true;
            }
            // 阻止 javascript:、data: 等危险协议
            return false;
        }
        // \includegraphics 也需要trust
        if (context.command === "\\includegraphics") {
            return context.url.startsWith("https://");
        }
        return false;
    }
});
```

## 错误消息的 HTML 转义

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
        element.innerHTML = '<span class="error">'
            + escapeHtml(e.message) + '</span>';
    } else {
        throw e;
    }
}
```

未转义的不可信 LaTeX 源码或异常消息可能包含 `<script>` 标签等恶意内容，直接通过 `innerHTML` 插入会导致 XSS。

## 封装安全渲染函数

实际项目中，建议封装一个安全的渲染函数统一处理错误：

```javascript
/**
 * 安全渲染KaTeX公式
 * @param {string} latex LaTeX字符串
 * @param {HTMLElement} element 目标DOM元素
 * @param {object} options 额外KaTeX选项
 * @returns {boolean} 渲染是否成功
 */
function safeRenderKatex(latex, element, options = {}) {
    const defaultOptions = {
        throwOnError: false,
        errorColor: "#cc0000",
        strict: "warn",
        maxExpand: 1000,
        macros: {},
        trust: false,
        ...options,
    };

    try {
        katex.render(latex, element, defaultOptions);

        // 检查是否有错误标记
        if (element.querySelector(".katex-error")) {
            console.warn("KaTeX渲染有错误:", latex);
            return false;
        }
        return true;
    } catch (e) {
        console.error("KaTeX渲染异常:", e.message, "公式:", latex);
        // 降级显示：显示原始LaTeX文本
        element.textContent = latex;
        element.classList.add("katex-fallback");
        return false;
    }
}

// 使用
safeRenderKatex("x^2 + y^2 = z^2", document.getElementById("formula"));
safeRenderKatex(userInput, document.getElementById("user-formula"), {
    displayMode: true
});
```

### 服务端渲染安全封装

```javascript
const katex = require('katex');

function safeRenderToString(latex, options = {}) {
    try {
        return katex.renderToString(latex, {
            throwOnError: false,
            strict: "warn",
            trust: false,
            maxExpand: 1000,
            macros: {},
            ...options,
        });
    } catch (e) {
        console.error("KaTeX SSR错误:", e.message);
        // 返回编码后的纯文本作为降级
        return `<span class="katex-error" title="${escapeHtml(e.message)}">${escapeHtml(latex)}</span>`;
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
```

## auto-render中的错误处理

auto-render的errorCallback可以逐个公式处理错误：

```javascript
renderMathInElement(document.body, {
    delimiters: [{left: "$", right: "$", display: false}],
    throwOnError: false,
    errorCallback: function(err, mathText, el) {
        console.warn("公式渲染失败:", mathText.substring(0, 80), err.message);
        // 自定义：将错误公式标记出来
        el.style.background = "#fff0f0";
        el.title = "公式错误: " + err.message;
    },
    errorColor: "#cc0000",
});
```

## 调试技巧

1. **使用strict: "warn"**：在开发阶段启用严格模式警告，及早发现不兼容用法
2. **控制台错误消息**：ParseError.message 通常包含具体的位置信息
3. **简化复现**：将复杂公式逐步删减，定位导致错误的最小片段
4. **使用KaTeX在线编辑器**：https://katex.org 上的demo可以交互式测试
5. **验证花括号配对**：最常见的错误是花括号不匹配，可以用文本编辑器的括号匹配功能检查

## 相关内容

- [快速开始](/concepts/01-getting-started.md)
- [配置系统](/concepts/10-settings-options.md)
- [安全与错误处理](/concepts/18-security-and-errors.md)
- [基础渲染示例](/examples/basic-render.md)
- [自动渲染使用示例](/examples/auto-render-usage.md)
- [常见问题](/concepts/21-common-issues.md)

[^web-error]: 官网 Handling Errors 页面，https://katex.org/docs/error
[^web-security]: 官网 Security 页面，https://katex.org/docs/security
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
