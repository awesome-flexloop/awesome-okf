---
type: Concept
title: 宏系统
description: KaTeX 宏系统的工作原理，包括内置宏、自定义宏（settings.macros 和 __defineMacro）、Namespace 分组作用域、参数展开和展开计数防护。
tags: [katex, macro, namespace, defineMacro, expansion]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:35:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:35:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 宏系统的角色

宏（Macro）是 TeX 中最强大的抽象机制之一。KaTeX 的宏系统位于 MacroExpander 层，提供：

- **字符串替换**：简单的命令别名（如 `\to` → `\rightarrow`）
- **参数化宏**：带参数的命令定义（如 `\newcommand{\vec}[1]{\mathbf{#1}}`）
- **作用域管理**：通过分组（`{...}`）控制宏定义的可见范围
- **动态展开**：函数宏可以执行复杂的展开逻辑

与函数（通过 defineFunction 注册）的区别：
- **宏在 gullet 层展开**：展开结果是 Token 流，再交给 Parser 解析
- **函数在 stomach 层处理**：直接消费参数生成 ParseNode
- 宏是"语法糖"，最终还是要靠函数来实际渲染

## 内置宏

内置宏定义在 [src/macros.ts](https://github.com/KaTeX/KaTeX/blob/main/src/macros.ts) 中。常见的内置宏包括：

### 简单别名

| 宏名 | 展开为 |
|------|--------|
| `\to` | `\rightarrow` |
| `\gets` | `\leftarrow` |
| `\land` | `\wedge` |
| `\lor` | `\vee` |
| `\ne` | `\neq` |
| `\notin` | `\not\in` |
| `\bigl` | `\mathopen{}\mathclose\bgroup\left` |
| `\bigr` | `\aftergroup\egroup\right` |

### 带参数宏

| 宏名 | 参数 | 展开效果 |
|------|------|---------|
| `\textbf{#1}` | 1个 | 切换 bold 字体族 |
| `\textit{#1}` | 1个 | 切换 italic 形状 |
| `\mathbb{#1}` | 1个 | 切换 blackboard bold 字体 |
| `\mathrm{#1}` | 1个 | 切换 roman 字体 |

### 控制结构

| 宏名 | 作用 |
|------|------|
| `\newcommand` | 定义新命令（支持可选参数） |
| `\def` | TeX原语风格的宏定义 |
| `\let` | 命令别名（将一个命令绑定到另一个） |
| `\gdef` / `\global\def` | 全局定义（不受分组作用域限制） |
| `\relax` | 无操作（占位命令） |
| `\expandafter` | 控制展开顺序 |
| `\noexpand` | 阻止下一个Token被展开 |

## 自定义宏的两种方式

### 方式1：通过 settings.macros 配置（推荐）

渲染时在 options 中传入 macros 对象：

```javascript
katex.render("\\RR^n", element, {
    macros: {
        "\\RR": "\\mathbb{R}",
        "\\vec": "\\mathbf{#1}",
        "\\diff": "\\mathop{}\\!\\mathrm{d}",
    }
});
```

macros 对象的值可以是：
- **字符串**：直接展开为该字符串的 Token 序列
- **函数**：动态计算展开内容（函数形式）

#### 字符串宏参数

字符串宏中使用 `#1`~`#9` 引用参数，`##` 转义为 `#`：

```javascript
macros: {
    // \dd{x} 展开为 dx（微分d）
    "\\dd": "\\mathop{}\\!\\mathrm{d}#1",
    // \paren{(} 自动调整大小的括号
    "\\paren": "\\mathopen{}\\mathclose{}\\left#1",
}
```

#### 函数宏

值为函数时，可以实现动态逻辑：

```javascript
macros: {
    "\\ifstar": function(context) {
        // 检查下一个Token是否为*
        const nextToken = context.consumeIfStar();
        // 根据是否有*返回不同展开
        return nextToken ? "有星号版本" : "无星号版本";
    }
}
```

### 方式2：通过 katex.__defineMacro() 全局注册

使用公开API全局注册宏，对所有后续渲染生效：

```javascript
katex.__defineMacro("\\Re", "\\mathfrak{R}");
katex.__defineMacro("\\Im", "\\mathfrak{I}");
```

## Namespace：分组作用域

宏的作用域通过 [Namespace](https://github.com/KaTeX/KaTeX/blob/main/src/Namespace.ts) 类实现，采用分层查找模型：

```
全局层（globalMacros）
  └─ 当前层（beginGroup时创建新层）
       └─ 更内层（嵌套分组）
            └─ ...
```

### beginGroup() / endGroup()

```typescript
class MacroExpander {
    beginGroup() {
        this.macros.beginGroup();  // 创建新的命名空间层
    }
    endGroup() {
        this.macros.endGroup();    // 弹出命名空间层
    }
}
```

### 作用域规则

1. **花括号创建分组**：每次 Parser 遇到 `{` 时调用 `beginGroup()`，遇到 `}` 时调用 `endGroup()`
2. **内层定义遮蔽外层**：在内层定义的同名宏遮蔽外层定义
3. **endGroup 恢复外层**：分组结束后，内层定义被丢弃，外层定义重新可见
4. **\global 前缀**：`\gdef` 或 `\global\def` 将宏定义写入全局层，不受分组影响

示例：
```
{
  \def\a{hello}    % 定义局部宏 \a
  \a               % 输出 "hello"
  {
    \def\a{world}  % 内层定义 \a，遮蔽外层
    \a             % 输出 "world"
  }
  \a               % 输出 "hello"（外层恢复）
}
\a                 % 错误！\a 未定义（全局层没有）
```

## 宏展开流程

当 MacroExpander.expandNextToken() 遇到宏时，展开流程为：

1. **查询宏定义**：在 Namespace 中从当前层向全局层查找宏名
2. **判断参数数量**：根据宏定义的 numArgs 决定需要消费多少参数
3. **消费参数**：通过 consumeArg() 消费参数（支持花括号组和单Token）
4. **展开主体**：
   - 字符串宏：将字符串转为Token序列，替换 `#1`~`#9`为实际参数Token
   - 函数宏：调用函数，传入MacroContextInterface，获取展开Token序列
5. **压入栈**：将展开结果逆序压入Token栈
6. **计数递增**：`_expandCount++`，检查是否超过 maxExpand
7. **继续展开**：循环回到步骤1（展开结果中可能包含其他宏）

### 参数消费规则

- 参数通常是一个花括号组 `{...}`（剥去花括号）
- 花括号可以嵌套，consumeArg 正确处理嵌套层级
- 如果参数位置不是花括号，则取单个Token
- 某些参数类型（如 `\url` 的url类型）有特殊处理

## 展开计数防护

```typescript
this._expandCount++;
if (this._expandCount > this.settings.maxExpand) {
    throw new ParseError("Too many expansions: infinite loop or " +
        "need to increase maxExpand setting");
}
```

`settings.maxExpand`（默认 1000）限制单次渲染中宏展开的总次数，防止：
- 递归宏死循环（如 `\def\a{\a}\a`）
- 恶意构造的展开炸弹
- 复杂宏定义的意外爆炸

可以通过设置增大上限：
```javascript
katex.render(expr, el, {maxExpand: 5000});
```

## \newcommand 实现

`\newcommand` 是内置宏，它本身的展开会创建新的宏定义。它的处理流程：

1. 解析命令名（`\newcommand{\cmdname}`）
2. 检查是否存在可选参数数量（`[n]`）
3. 检查是否存在默认值（`[default]`，仅第一个可选参数）
4. 解析定义体（`{definition}`）
5. 在当前 Namespace 层注册新宏

`\renewcommand` 与 `\newcommand` 类似，但要求命令必须已存在（覆盖而非新建）。

## \def vs \newcommand

| 特性 | `\def` | `\newcommand` |
|------|--------|---------------|
| 语法 | `\def\cmd#1#2{body}` | `\newcommand{\cmd}[2][default]{body}` |
| 参数分隔符 | 支持任意分隔符模式 | 仅支持花括号参数 |
| 已存在时 | 静默覆盖 | 报错（需用 `\renewcommand`） |
| 可选参数 | 需手动实现 | 原生支持 `[]` 语法 |
| TeX兼容性 | 完全兼容 | LaTeX命令 |

KaTeX 对 `\def` 的支持有限（主要支持基本形式），复杂 TeX 模式（如 `\def\a#1plus#2{#1+#2}`）不完全支持。

## 宏与函数的选择

何时用宏，何时用 defineFunction？

| 场景 | 选择 |
|------|------|
| 简单别名/缩写 | 宏（settings.macros） |
| 字符串替换+参数 | 宏 |
| 需要创建新的ParseNode类型 | 函数（defineFunction） |
| 需要自定义HTML渲染 | 函数（必须有htmlBuilder） |
| 需要控制展开顺序 | 宏（配合\expandafter等） |
| 条件逻辑/动态内容 | 函数宏（settings.macros中的函数） |
| 全局可用（跨渲染调用） | `__defineMacro` 全局宏 |

## 相关概念

- [宏展开器（MacroExpander）](/concepts/04-macro-expander.md)
- [函数注册表](/concepts/08-function-registry.md)
- [配置系统](/concepts/10-settings-options.md)
- [自定义宏示例](/examples/custom-macros.md)
