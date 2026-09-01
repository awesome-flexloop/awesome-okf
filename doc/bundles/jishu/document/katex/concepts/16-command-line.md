---
type: Concept
title: 命令行接口
description: KaTeX CLI 的输入输出、全部 18 个命令行选项、与 Settings 选项的映射关系、宏文件格式和常见用法示例。
tags: [katex, cli, command-line, rendering]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T21:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T21:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-cli
    resource: /references/katex-website.md#web-cli
    title: KaTeX 官网 CLI 页面
---

## 概述

KaTeX 通过 npm 包内置了命令行接口（CLI），入口文件为 `cli.js`，可在安装后直接从终端将 LaTeX 表达式渲染为 HTML 标记。CLI 默认从标准输入（stdin）读取 LaTeX 输入，将结果写入标准输出（stdout）。

## 基本用法

通过 `npx` 或本地安装的二进制执行：

```bash
# 使用 npx（无需全局安装）
echo "c^2 = a^2 + b^2" | npx katex

# 本地安装后
echo "c^2 = a^2 + b^2" | ./node_modules/.bin/katex
```

输出为一段可直接嵌入 HTML 页面的 KaTeX 标记（仍需引入 KaTeX CSS 和字体才能正确显示）。

## 全部选项

KaTeX CLI 共提供 18 个选项（含 `--version` 与 `--help`）。

### 信息选项

| 选项 | 说明 |
|------|------|
| `-V, --version` | 输出版本号 |
| `-h, --help` | 输出使用信息 |

### 渲染模式

| 选项 | 说明 |
|------|------|
| `-d, --display-mode` | 以显示模式渲染数学（`\int`、`\sum` 等符号变大，数学居中独占一行） |
| `-F, --format <type>` | 决定输出标记语言 |
| `--leqno` | 将显示数学的 tag 渲染在左侧 |
| `--fleqn` | 将显示数学左对齐（而非居中） |

### 错误处理

| 选项 | 说明 |
|------|------|
| `-t, --no-throw-on-error` | 遇到错误时渲染错误（颜色由 `--error-color` 指定）而非抛出 ParseError |
| `-c, --error-color <color>` | 接受 `rgb` 或 `rrggbb` 格式颜色字符串（不带 `#`），指定 `-t` 选项渲染的错误颜色 |
| `-S, --strict` | 开启严格/LaTeX 忠实模式，输入使用 LaTeX 不支持的特性时抛出错误 |

### 宏

| 选项 | 说明 |
|------|------|
| `-m, --macro <def>` | 定义自定义宏，格式为 `'\foo:expansion'`；可多次使用 `-m` 参数定义多个宏 |
| `-f, --macro-file <path>` | 从指定文件读取宏定义，每行一个 |
| `-e, --max-expand <n>` | 限制宏展开次数以防止无限宏循环；设为 `Infinity` 时宏展开器尝试像 LaTeX 一样完全展开 |

### 安全与尺寸

| 选项 | 说明 |
|------|------|
| `-T, --trust` | 信任输入，启用所有 HTML 特性如 `\url` |
| `-s, --max-size <n>` | 非零时将用户指定尺寸（如 `\rule{500em}{500em}`）上限设为 maxSize ems；为零时元素和间距可任意大 |

### 外观

| 选项 | 说明 |
|------|------|
| `--min-rule-thickness <size>` | 以 em 为单位指定分数线、`\sqrt` 顶线、array 竖线、`\hline`、`\hdashline`、`\underline`、`\overline` 及 `\fbox`/`\boxed`/`\fcolorbox` 边框的最小粗细 |
| `-b, --color-is-text-color` | 使 `\color` 行为类似 LaTeX 两参数 `\textcolor` 而非单参数模式切换 |

### 输入输出

| 选项 | 说明 |
|------|------|
| `-i, --input <path>` | 从指定文件读取 LaTeX 输入（不指定时从 stdin 读取） |
| `-o, --output <path>` | 将 HTML 输出写入指定文件（不指定时写入 stdout） |

## CLI 选项与 Settings 映射

大多数 CLI 选项直接对应 `katex.render()` / `renderToString()` 的 Settings 选项：

| CLI 选项 | Settings 选项 | 默认值 |
|---------|--------------|--------|
| `-d, --display-mode` | `displayMode` | `false` |
| `-F, --format <type>` | `output` | `"htmlAndMathml"` |
| `--leqno` | `leqno` | `false` |
| `--fleqn` | `fleqn` | `false` |
| `-t, --no-throw-on-error` | `throwOnError`（取反） | `true` |
| `-c, --error-color <color>` | `errorColor` | `"#cc0000"` |
| `-m, --macro <def>` | `macros`（累加） | `{}` |
| `-f, --macro-file <path>` | `macros`（从文件加载） | `{}` |
| `--min-rule-thickness <size>` | `minRuleThickness` | 未设置 |
| `-b, --color-is-text-color` | `colorIsTextColor` | `false` |
| `-S, --strict` | `strict` | `"warn"`（传 `-S` 设为 `true`/`"error"`） |
| `-T, --trust` | `trust` | `false`（传 `-T` 设为 `true`） |
| `-s, --max-size <n>` | `maxSize` | `Infinity` |
| `-e, --max-expand <n>` | `maxExpand` | `1000` |

> 注意：`-S, --strict` 是布尔开关，传入即开启 true/error 模式，对应 Options 的 `strict: true`；不传时使用 Options 默认值 `"warn"`。Settings 选项的完整说明见 [配置系统](10-settings-options.md)。

## 宏文件

使用 `--macro-file`（或 `-f`）可从文件批量加载宏定义，文件中每行一个宏，格式与 `--macro` 参数相同：

```text
\RR:\mathbb{R}
\f:#1f(#2)
\Z:\mathbb{Z}
```

在命令行中使用：

```bash
npx katex --macro-file ./my-macros.txt -i input.tex -o output.html
```

`--macro` 和 `--macro-file` 可以组合使用，命令行 `-m` 定义的宏与文件中的宏合并。

## 常见用法

### 从文件读取并输出到文件

```bash
npx katex --display-mode --input formula.tex --output formula.html
```

### 显示模式 + 错误容错

```bash
echo "\fracc{a}{b}" | npx katex -d -t -c cc0000
```

### 定义多个宏

```bash
echo "\\RR^n" | npx katex -m '\RR:\mathbb{R}' -m '\NN:\mathbb{N}'
```

### 严格模式渲染

```bash
echo "x → y" | npx katex --strict
```

### 限制宏展开和尺寸（安全场景）

```bash
npx katex --max-expand 1000 --max-size 50 -i untrusted.tex -o output.html
```

## 相关概念

- [快速开始](01-getting-started.md)
- [安装与运行时](15-installation-and-runtime.md)
- [配置系统](10-settings-options.md)
- [宏系统](09-macro-system.md)
- [安全与错误处理](18-security-and-errors.md)
- [CLI 渲染示例](../examples/cli-render.md)
