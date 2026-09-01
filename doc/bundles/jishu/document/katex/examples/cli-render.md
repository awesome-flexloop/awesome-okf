---
type: Example
title: 命令行渲染示例
description: 使用 KaTeX CLI（npx katex）从 stdin/文件渲染 LaTeX 到 stdout/文件，覆盖 display-mode、macro、macro-file、no-throw-on-error 等常用选项及批量处理与安全场景。
tags: [katex, example, cli, command-line, npx, macros, error-handling]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:40:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-cli
    resource: /references/katex-website.md#web-cli
    title: KaTeX 官网 CLI 页面
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
  - id: web-security
    resource: /references/katex-website.md#web-security
    title: KaTeX 官网 Security 页面
---

## 前提条件

通过 npm、yarn 或 pnpm 安装 KaTeX 后，CLI 入口 `cli.js` 即可用[^web-cli]：

```bash
npm install katex
# 或
pnpm add katex
```

无需全局安装，使用 `npx katex` 即可调用；也可直接执行本地二进制 `./node_modules/.bin/katex`[^web-cli]。

> CLI 只生成数学公式的 HTML 片段，在浏览器中正确显示仍需引入 KaTeX CSS 和字体文件，详见 [Node.js 服务端渲染示例](node-ssr.md)。

## 从 stdin 到 stdout（最简用法）

CLI 默认从标准输入（stdin）读取 LaTeX，将 HTML 结果写入标准输出（stdout）[^web-cli]：

```bash
echo "c^2 = a^2 + b^2" | npx katex
```

输出一段 KaTeX HTML 标记，可重定向到文件：

```bash
echo "E = mc^2" | npx katex > formula.html
```

在 Windows PowerShell 中，`echo` 等价于 `Write-Output`，管道用法相同：

```powershell
"c^2 = a^2 + b^2" | npx katex
```

## 文件输入与输出（--input / --output）

使用 `-i, --input <path>` 从文件读取 LaTeX，`-o, --output <path>` 将 HTML 写入文件[^web-cli]：

```bash
# 从 formula.tex 读取，输出到 formula.html
npx katex --input formula.tex --output formula.html
```

短选项形式：

```bash
npx katex -i formula.tex -o formula.html
```

`input.tex` 内容示例：

```latex
\frac{1}{1 + e^{-x}}
```

也可只指定其中一个：从文件读取但输出到终端，或从 stdin 读取但写入文件：

```bash
# 文件 → 终端
npx katex -i formula.tex

# stdin → 文件
echo "\sqrt{x^2 + y^2}" | npx katex -o formula.html
```

## 显示模式（--display-mode）

`-d, --display-mode` 以显示模式渲染数学，`\int`、`\sum` 等符号变大，公式居中独占一行[^web-cli]：

```bash
# 行内模式（默认）
echo "\sum_{i=1}^n i" | npx katex

# 显示模式
echo "\sum_{i=1}^n i = \frac{n(n+1)}{2}" | npx katex --display-mode

# 短选项
echo "\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}" | npx katex -d
```

可与文件输入输出组合：

```bash
npx katex -d -i display.tex -o display.html
```

## 自定义宏（--macro）

`-m, --macro <def>` 定义自定义宏，格式为 `'\foo:expansion'`，可多次使用 `-m` 定义多个宏[^web-cli]：

```bash
echo "\RR^n" | npx katex -m '\RR:\mathbb{R}'
```

多个宏：

```bash
echo "\RR^n \to \NN" | npx katex \
  -m '\RR:\mathbb{R}' \
  -m '\NN:\mathbb{N}'
```

带参数的宏使用 `#1`、`#2` 占位符：

```bash
echo "\f{x}{\f{y}{z}}" | npx katex -m '\f:#1f(#2)'
```

> Shell 中单引号可避免反斜杠被转义；在 PowerShell 中建议同样使用单引号包裹宏定义。

## 宏文件（--macro-file）

`-f, --macro-file <path>` 从文件批量加载宏，每行一个，格式与 `--macro` 相同[^web-cli]：

`macros.txt`：

```text
\RR:\mathbb{R}
\NN:\mathbb{N}
\ZZ:\mathbb{Z}
\diff:\mathop{}\!\mathrm{d}
\f:#1f(#2)
```

使用：

```bash
npx katex --macro-file macros.txt -i input.tex -o output.html
```

短选项：

```bash
npx katex -f macros.txt -i input.tex -o output.html
```

`--macro` 和 `--macro-file` 可组合使用，命令行宏与文件宏合并：

```bash
npx katex -f macros.txt -m '\QQ:\mathbb{Q}' -i input.tex
```

## 错误处理（--no-throw-on-error）

默认情况下，遇到无效 LaTeX 时 CLI 抛出 `ParseError` 并以非零状态码退出。使用 `-t, --no-throw-on-error` 可改为渲染错误信息而非退出[^web-cli]：

```bash
# 默认：抛错并退出（\fracc 是拼写错误）
echo "\fracc{a}{b}" | npx katex
# 输出 ParseError，退出码非零

# 容错模式：渲染错误文本，正常退出
echo "\fracc{a}{b}" | npx katex --no-throw-on-error
```

短选项：

```bash
echo "\fracc{a}{b}" | npx katex -t
```

使用 `-c, --error-color <color>` 指定错误文本颜色，接受 `rgb` 或 `rrggbb` 格式（**不带 `#`**）[^web-cli]：

```bash
echo "\fracc{a}{b}" | npx katex -t -c cc0000
```

> 容错模式适合批处理不希望因单条公式错误中断整个流程的场景；但构建脚本中通常应保持默认抛错行为，以便及时发现问题。

## 输出格式（--format）

`-F, --format <type>` 决定输出标记语言，对应 Settings 的 `output` 选项[^web-cli] [^web-options]：

```bash
# 默认：HTML + MathML（无障碍）
echo "x^2" | npx katex

# 仅 HTML
echo "x^2" | npx katex --format html

# 仅 MathML
echo "x^2" | npx katex --format mathml
```

## 其他常用选项

### 严格模式（--strict）

`-S, --strict` 开启严格/LaTeX 忠实模式，对非 LaTeX 标准特性抛出错误[^web-cli]：

```bash
echo "x → y" | npx katex --strict
```

不传 `-S` 时使用 Options 默认值 `"warn"`（通过 console.warn 警告）[^web-options]。

### 信任输入（--trust）

`-T, --trust` 信任输入，启用 `\url`、`\href` 等可能产生外部链接的 HTML 特性[^web-cli]：

```bash
echo "\url{https://katex.org}" | npx katex --trust
```

不可信输入请勿启用 `--trust`，详见[安全信任示例](security-trust.md)。

### 限制尺寸与宏展开（安全场景）

`-s, --max-size <n>` 限制用户指定尺寸的上限（单位 em），`-e, --max-expand <n>` 限制宏展开次数以防止无限宏循环[^web-cli]：

```bash
npx katex \
  --max-size 50 \
  --max-expand 1000 \
  -i untrusted.tex \
  -o output.html
```

`--max-expand Infinity` 可让宏展开器像 LaTeX 一样完全展开，但不可信输入不建议使用[^web-cli]。

### 编号与对齐

`--leqno` 将显示数学的 tag 渲染在左侧，`--fleqn` 将显示数学左对齐（而非居中）[^web-cli]：

```bash
npx katex -d --leqno --fleqn -i input.tex -o output.html
```

## 批量处理脚本

结合 shell 循环批量渲染多个 `.tex` 文件：

```bash
# Bash: 将当前目录所有 .tex 渲染为同名 .html
for f in *.tex; do
  npx katex -d -t -i "$f" -o "${f%.tex}.html"
done
```

```powershell
# PowerShell 等效写法
Get-ChildItem -Filter *.tex | ForEach-Object {
    npx katex -d -t -i $_.FullName -o ($_.BaseName + ".html")
}
```

使用宏文件为批量渲染提供统一宏定义：

```bash
for f in chapters/*.tex; do
  npx katex -d -f macros.txt -i "$f" -o "build/$(basename "$f" .tex).html"
done
```

## 组装完整 HTML 页面

CLI 输出的是公式片段，需包裹在含 CSS 的完整 HTML 文档中才能正确显示：

```bash
# 渲染公式片段
echo "\frac{a}{b} + \sqrt{c}" | npx katex -d > formula.html

# 用简单脚本拼装完整页面（Node.js）
node -e "
const fs = require('fs');
const { execSync } = require('child_process');
const math = execSync('echo \"\\\\frac{a}{b}\" | npx katex -d').toString();
const html = \`<!DOCTYPE html>
<html>
<head>
<meta charset='UTF-8'>
<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css'>
</head>
<body>\${math}</body>
</html>\`;
fs.writeFileSync('page.html', html);
"
```

## 查看版本与帮助

```bash
# 输出版本号
npx katex --version

# 输出使用信息与全部选项
npx katex --help
```

## 选项速查

| 选项 | 短选项 | 说明 |
|------|--------|------|
| `--input <path>` | `-i` | 从文件读取 LaTeX（默认 stdin） |
| `--output <path>` | `-o` | 输出 HTML 到文件（默认 stdout） |
| `--display-mode` | `-d` | 显示模式渲染 |
| `--macro <def>` | `-m` | 定义宏，可重复 |
| `--macro-file <path>` | `-f` | 从文件加载宏 |
| `--no-throw-on-error` | `-t` | 遇错渲染而非抛出 |
| `--error-color <color>` | `-c` | 错误文本颜色（无 `#`） |
| `--format <type>` | `-F` | 输出格式：html/mathml/htmlAndMathml |
| `--strict` | `-S` | 严格模式 |
| `--trust` | `-T` | 信任输入 |
| `--max-size <n>` | `-s` | 尺寸上限（em） |
| `--max-expand <n>` | `-e` | 宏展开上限 |
| `--leqno` | — | 左侧编号 |
| `--fleqn` | — | 左对齐 |
| `--min-rule-thickness <size>` | — | 线条最小粗细（em） |
| `--color-is-text-color` | `-b` | `\color` 参数式行为 |
| `--version` | `-V` | 输出版本号 |
| `--help` | `-h` | 输出帮助 |

## 相关内容

- [命令行接口](../concepts/16-command-line.md)
- [安装与运行时](../concepts/15-installation-and-runtime.md)
- [Node.js 服务端渲染示例](node-ssr.md)
- [配置系统](../concepts/10-settings-options.md)
- [安全与错误处理](../concepts/18-security-and-errors.md)
- [安全信任示例](security-trust.md)
- [自动渲染使用示例](auto-render-usage.md)

[^web-cli]: 官网 CLI 页面，https://katex.org/docs/cli
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
[^web-security]: 官网 Security 页面，https://katex.org/docs/security
