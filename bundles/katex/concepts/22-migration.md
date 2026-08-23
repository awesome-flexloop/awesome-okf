---
type: Concept
title: 版本迁移
description: KaTeX v0.13.0 至 v0.18.0 的迁移指南，涵盖 CSS 类名 katex- 前缀、__defineFunction API 变更、contrib 路径调整、\relax 行为变化、宏参数解析行为、copy-tex CSS 移除、\def 语法收紧等破坏性变更。
tags: [katex, migration, upgrade, breaking-changes, v0.13, v0.18]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-migration
    resource: /references/katex-website.md#web-migration
    title: KaTeX 官网 Migration Guide 页面
  - id: facts
    resource: /spec/facts.md
    title: KaTeX 事实清单
---

## 概述

KaTeX 官网 [Migration Guide](https://katex.org/docs/migration) 覆盖 v0.13.0 至 v0.18.0 共 6 个版本段的迁移要点[^web-migration]。本文档按版本顺序整理破坏性变更和迁移建议，帮助维护已有 KaTeX 集成的开发者顺利升级。

本 bundle 基于 KaTeX **v0.18.4**（源码 package.json 确认）[^facts]。从更早版本升级时请逐版本阅读。

## v0.18.0：CSS 类名前缀

v0.18.0 是影响面最大的版本之一，KaTeX 内部 CSS 类名统一加了 `katex-` 前缀，避免与页面其他样式冲突[^web-migration]。

### 类名迁移表

| v0.17 及之前 | v0.18+ |
|-------------|--------|
| `.accent` | `.katex-accent` |
| `.base` | `.katex-base` |
| `.root` | `.katex-root` |
| `.rule` | `.katex-rule` |
| `.tag` | `.katex-tag` |
| `.underline` | `.katex-underline` |
| `.vbox` | `.katex-vbox` |

共 20 个类名被重命名[^facts]。完整列表见官网 Migration Guide。

### 迁移影响

- **自定义 CSS**：如果项目中编写了覆盖 KaTeX 内部类名的 CSS 规则，需将选择器更新为 `katex-` 前缀版本
- **JavaScript 查询**：使用 `querySelector`、`classList` 等操作 KaTeX 内部元素的代码需更新类名
- **第三方扩展**：依赖 KaTeX 内部类名的第三方库可能需要升级版本

> 公共稳定的类名（如 `.katex`、`.katex-display`、`.katex-error`）保持不变。

## v0.17.0：__defineFunction API 变更

v0.17.0 变更了内部扩展 API `__defineFunction` 的参数结构[^web-migration]。

### 变更内容

属性不再包裹在 `props` 对象中，需将 `props` 成员移到定义对象顶层：

```javascript
// v0.16 及之前
katex.__defineFunction("\\mycmd", {
    props: {
        numArgs: 1,
        handler: ({parser}, args) => { ... }
    }
});

// v0.17+
katex.__defineFunction("\\mycmd", {
    numArgs: 1,
    handler: ({parser}, args) => { ... }
});
```

### 迁移影响

- 使用 `__defineFunction` 添加自定义命令的扩展代码需要调整
- 该 API 标注为内部使用，可能发生非向后兼容的变更

## v0.16.0：copy-tex CSS 移除

v0.16.0 起，copy-tex 扩展不再拥有（也不需要）单独的 CSS 文件[^web-migration]。

### 迁移影响

- 移除对 `copy-tex.css` 的导入或 `<link>` 引用
- 只需引入 copy-tex 的 JavaScript 文件即可

```html
<!-- v0.15 及之前 -->
<link rel="stylesheet" href="katex.min.css">
<link rel="stylesheet" href="contrib/copy-tex.css">
<script src="contrib/copy-tex.min.js"></script>

<!-- v0.16+ -->
<link rel="stylesheet" href="katex.min.css">
<script src="contrib/copy-tex.min.js"></script>
```

## v0.15.0：\relax 行为变化

v0.15.0 中，`\relax` 现在实现为函数，会停止展开和解析[^web-migration]。

### 破坏性变更

以下用法不再工作：

```latex
% v0.14 及之前可用，v0.15 后报错
\kern2\relax em
```

`\relax` 会吞掉后续的 `em`，导致单位解析失败。

### 解决方案

直接写完整单位，不插入 `\relax`：

```latex
\kern2em
```

## v0.14.0：模块路径与 ESM

v0.14.0 涉及模块加载方式和 contrib 路径的调整[^web-migration]。

### ESM 导入变更

在支持条件导出和 ESM 的模块加载器中，`import katex from 'katex'` 将导入 ESM 版本。

### contrib 路径变更

contrib 扩展的导入路径发生变化：

| v0.13 及之前 | v0.14+ |
|-------------|--------|
| `katex/dist/contrib/[name].js` | `katex/contrib/[name]` |
| `katex/dist/katex.mjs` | `katex`（通过包名导入） |

### 迁移示例

```javascript
// v0.13 及之前
import katex from 'katex/dist/katex.mjs';
import 'katex/dist/contrib/mhchem.js';

// v0.14+
import katex from 'katex';
import 'katex/contrib/mhchem';
```

## v0.13.0：多项行为收紧

v0.13.0 包含多项影响 LaTeX 语义的变更[^web-migration]：

### 1. 宏参数不再展开

解析宏参数时 token 不再展开。这意味着：

```latex
% v0.12: \frac\foo\foo（\foo 定义为 12）解析为 \frac{1}{2}12
% v0.13: 解析为 \frac{12}{12}
```

如需在解析前展开参数，使用 `\expandafter`。

### 2. \def 语法收紧

- 不再接受花括号包裹的控制序列：`\def{\foo}{}` 需改为 `\def\foo{}`
- 不再接受未用花括号包裹的替换文本：`\def\foo1` 需改为 `\def\foo{1}`

### 3. \newline 和 \cr 不再接受可选尺寸参数

垂直间距应使用 `\\[size]`：

```latex
% v0.12
\newline[10pt]

% v0.13+
\\[10pt]
```

### 4. 原始命令参数限制

`\cfrac`、`\color`、`\textcolor`、`\colorbox`、`\fcolorbox` 不再允许作为原始命令（如无可选参数的 `\sqrt` 和上下标）的参数[^web-migration]：

```latex
% v0.12 可用，v0.13 后错误
\sqrt\textcolor{red}{x}

% v0.13+ 正确写法
\sqrt{\textcolor{red}{x}}
```

## 迁移检查清单

从旧版本升级到 v0.18.x 时，逐项检查：

- [ ] **CSS 类名**：搜索代码中所有引用 KaTeX 内部类名的地方，添加 `katex-` 前缀（v0.18）
- [ ] **自定义函数**：使用 `__defineFunction` 的代码调整 props 结构（v0.17）
- [ ] **copy-tex**：移除 copy-tex.css 的引用（v0.16）
- [ ] **\relax**：检查是否有 `\relax` 用于分隔数字和单位的写法（v0.15）
- [ ] **模块路径**：更新 import 路径（v0.14）
- [ ] **宏参数**：检查依赖宏参数展开行为的代码（v0.13）
- [ ] **\def 语法**：检查 `\def` 语法是否符合收紧后的规范（v0.13）
- [ ] **版本一致性**：JS、CSS、contrib 扩展版本号保持一致

## 相关概念

- [安装与运行时](/concepts/15-installation-and-runtime.md) — 最新版安装方式
- [常见问题](/concepts/21-common-issues.md) — 集成排障
- [函数注册表](/concepts/08-function-registry.md) — defineFunction 机制
- [宏系统](/concepts/09-macro-system.md) — \def、\newcommand 语义
- [KaTeX 源码信源](/references/katex-source.md) — 源码版本基准 v0.18.4

[^web-migration]: 官网 Migration Guide 页面，https://katex.org/docs/migration
[^facts]: KaTeX 事实清单，F-001（源码版本 0.18.4）、W-143~W-152（Migration 全页）
