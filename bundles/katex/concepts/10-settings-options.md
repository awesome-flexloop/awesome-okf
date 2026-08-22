---
type: Concept
title: 配置系统
description: KaTeX 的 Settings 与 Options 双配置层，SETTINGS_SCHEMA选项定义，Strict/Trust处理，以及Options不可变状态传递模型。
tags: [katex, settings, options, configuration, strict, trust]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:35:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:35:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 配置系统双层模型

KaTeX 使用两个层次的配置对象：

- **Settings**：用户传入的原始配置（`katex.render()` 的第三个参数），定义在 [src/Settings.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Settings.ts)
- **Options**：渲染过程中内部使用的状态对象（包含当前样式、字号、颜色等），定义在 [src/Options.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Options.ts)

```
用户配置 (SettingsOptions)
      │
      ▼
  new Settings(options)   验证+默认值填充
      │
      ▼
optionsFromSettings(settings)  创建渲染Options
      │
      ▼
buildTree / buildHTML / buildMathML  渲染阶段使用
```

## Settings：用户配置层

### SETTINGS_SCHEMA

所有可用选项通过 `SETTINGS_SCHEMA` 数组定义（类似JSON Schema），每个选项包含：

```typescript
{
    "key": "displayMode",
    "type": "boolean",
    "default": false
}
```

Settings 构造函数根据 SCHEMA 验证用户输入并填充默认值。

### 完整选项列表

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `displayMode` | boolean | `false` | 显示模式（块级居中，大符号） |
| `output` | `"html" \| "mathml" \| "htmlAndMathml"` | `"htmlAndMathml"` | 输出格式 |
| `leqno` | boolean | `false` | 公式编号左侧（leqno = left equation numbers） |
| `fleqn` | boolean | `false` | 公式左对齐（fleqn = flush left equations） |
| `throwOnError` | boolean | `true` | 解析错误时抛异常 |
| `errorColor` | string | `"#cc0000"` | 错误文本颜色（throwOnError=false时） |
| `macros` | object | `{}` | 自定义宏映射 |
| `colorIsTextColor` | boolean | `false` | `\color` 行为类似 `\textcolor` |
| `strict` | boolean\|string\|function | `false` | 严格模式级别 |
| `trust` | boolean\|function | `false` | 是否信任输入（控制\href等） |
| `maxSize` | number | `Infinity` | 最大尺寸（em），防止超大元素 |
| `maxExpand` | number | `1000` | 宏展开次数上限 |
| `minRuleThickness` | number | — | 线条最小粗细（em） |
| `globalGroup` | boolean | `false` | CLI用：全局命名空间 |
| `allowedProtocols` | object | — | 允许的URL协议白名单 |

### strict 严格模式

`strict` 选项控制 KaTeX 对非标准 LaTeX 用法的处理：

| 值 | 行为 |
|----|------|
| `false`（默认） | 静默忽略不推荐的用法 |
| `"warn"` | 在 console 输出警告 |
| `"error"` | 抛出 ParseError |
| `function(errorCode, errorMsg, token)` | 自定义处理函数，返回 `"warn"`/`"error"`/`"ignore"` |

strict 模式会检查的问题包括：
- 未知的LaTeX命令
- 在数学模式中使用文本命令
- 命令参数类型错误
- 已废弃的语法

示例：
```javascript
katex.render(expr, el, {
    strict: function(errorCode, errorMsg, token) {
        if (errorCode === "unknownSymbol") return "ignore";
        return "warn";
    }
});
```

### trust 信任模式

`trust` 选项控制是否允许潜在危险的命令（可能导致XSS的链接/图片命令）：

| 值 | 行为 |
|----|------|
| `false`（默认） | 禁止 `\href`、`\url`、`\includegraphics` |
| `true` | 允许所有链接/图片命令 |
| `function(context)` | 自定义判断，返回 true/false |

context 对象包含：
- `command`：命令名（`"\\href"`、`"\\url"`、`"\\includegraphics"`）
- `url`：目标URL
- `protocol`：URL协议

示例（只允许同域链接）：
```javascript
katex.render(expr, el, {
    trust: function(context) {
        if (context.protocol === "https://") return true;
        if (context.url.startsWith("/")) return true;  // 相对路径
        return false;
    }
});
```

### 错误处理

当 `throwOnError` 为 `false` 时，解析错误不会中断渲染，而是：
1. 渲染错误消息文本（使用 `errorColor` 颜色）
2. 保留原始输入文本
3. 添加 `.katex-error` CSS类

```javascript
katex.render("\\invalid", el, {
    throwOnError: false,
    errorColor: "#ff0000"
});
// 渲染结果：红色的 "\invalid" 文本
```

## Options：渲染状态层

Options 是渲染阶段的内部状态对象，携带当前渲染上下文的所有视觉属性：

```typescript
class Options {
    static BASESIZE = 6;  // normalsize 对应索引6

    style: Style;              // 当前TeX样式
    color: string | undefined;
    size: number;              // 字号索引 0-10
    textSize: number;          // 文本模式字号
    phantom: boolean;          // 幻影模式（保留间距不显示）
    font: string;              // 数学字体（mathbf、mathit等）
    fontFamily: string;        // 字体族
    fontWeight: string;        // 字重
    fontShape: string;         // 字形（italic/upright）
    sizeMultiplier: number;    // 当前字号倍数
    maxSize: number;
    minRuleThickness: number;
}
```

### 不可变设计模式

Options 采用**不可变（immutable）**设计：所有修改方法返回新实例，不修改自身。

```typescript
// ❌ 错误：直接修改options（会破坏其他分支的渲染状态）
options.color = "red";

// ✅ 正确：使用 with* 方法创建新实例
const redOptions = options.withColor("red");
buildGroup(childNode, redOptions);
```

Options 提供的 with*/having* 方法：

| 方法 | 作用 |
|------|------|
| `havingStyle(style): Options` | 返回指定Style的新Options |
| `withColor(color): Options` | 返回指定颜色的新Options |
| `withColorTentative(color): Options` | 暂设颜色（color为undefined时不改变） |
| `havingSize(size): Options` | 返回指定字号的新Options |
| `havingCrampedStyle(): Options` | 返回压缩（cramped）样式的新Options |
| `havingPhantom(): Options` | 返回幻影模式的新Options |
| `withFont(font): Options` | 返回指定数学字体的新Options |
| `withTextFont(...): Options` | 返回指定文本字体的新Options |
| `withStyle(style): Options` | 同havingStyle |

### extend()：浅拷贝实现

所有 with* 方法内部调用 `extend()` 创建新实例：

```typescript
extend(attributes: Partial<Options>): Options {
    return new Options(this, attributes);
}

// 构造函数通过原型链实现"继承+覆盖"
constructor(base?: Options, override?: Partial<Options>) {
    if (base) {
        Object.setPrototypeOf(this, base);
    }
    if (override) {
        Object.assign(this, override);
    }
}
```

这里使用了一个巧妙的原型链技巧：新Options对象以原Options为原型，覆盖属性直接设置在实例上。这实现了浅拷贝的效果，同时避免了逐个复制所有属性。

### optionsFromSettings()

从 Settings 创建初始 Options：

```typescript
function optionsFromSettings(settings: Settings): Options {
    const style = settings.displayMode
        ? Style.DISPLAY     // 显示模式：D样式
        : Style.TEXT;       // 行内模式：T样式
    return new Options({
        style,
        size: Options.BASESIZE,       // normalsize = 6
        textSize: Options.BASESIZE,
        sizeMultiplier: 1.0,
        maxSize: settings.maxSize,
        minRuleThickness: settings.minRuleThickness,
        phantom: false,
        // ...
    });
}
```

## 样式与字号映射

字号索引 0-10 对应 LaTeX 中的 `\tiny` 到 `\HUGE`：

| 索引 | 命令 | 倍数 |
|------|------|------|
| 0 | `\tiny` | 0.5 |
| 1 | `\scriptsize` | 0.6 |
| 2 | `\footnotesize` | 0.7 |
| 3 | `\small` | 0.8 |
| 4 | `\normalsize`-1 (`\small`) | 0.9 |
| 5 | — | — |
| 6 | `\normalsize` | 1.0 |
| 7 | `\large` | 1.2 |
| 8 | `\Large` | 1.44 |
| 9 | `\LARGE` | 1.728 |
| 10 | `\huge` | 2.074 |
| 10 | `\HUGE` | 2.488 |

sizeStyleMap 进一步将每个字号在不同Style下映射到实际的字号索引（处理 script/scriptscript 样式下的字号缩放）。

## 相关概念

- [样式系统](/concepts/11-style-system.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [虚拟DOM树](/concepts/07-dom-tree.md)
- [错误处理示例](/examples/error-handling.md)
