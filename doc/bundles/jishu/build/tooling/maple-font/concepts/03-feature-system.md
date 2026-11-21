---
type: Concept
title: "OpenType Feature 系统"
description: "Maple Mono 三层 OpenType Feature——calt 连字查找表 + cv 语义变体 + ss 样式集的触发机制与 Python 代码组织"
tags: ["maple-mono", "opentype", "feature", "calt", "cv", "ss", "ligature"]
sources:
  - id: FEATURE-INIT
    resource: "source/py/feature/__init__.py"
    description: "generate_fea_string 主函数与 normal_enabled_features 预设"
  - id: FEATURE-README
    resource: "source/features/README.md"
    description: "特征列表与使用说明"
  - id: FEATURE-CALT
    resource: "source/py/feature/calt/"
    description: "calt 连字查找表生成（asciitilde/cross/equal_arrow/pipe/tag 等）"
prerequisites:
  - "01-build-pipeline"
  - "02-config-system"
next:
  - "04-feature-ast-generator"
related:
  - "../examples/custom-feature-build.md"
status: draft
---

# OpenType Feature 系统

Maple Mono 的 OpenType Feature 系统是一个**三层结构**——从最基础的上下文感知连字到独立语义变体，每一层解决不同的排版需求。

## 三层结构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenType Feature 三层                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: calt (Contextual Alternates)                          │
│  ┌─────────────────────────────────────────────────┐            │
│  │  上下文感知连字——最复杂、最核心的层                 │            │
│  │  按周围字形上下文决定替换为哪种连字                 │            │
│  │  python 模块: source/py/feature/calt/           │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Layer 2: cvXX (Character Variants)                              │
│  ┌─────────────────────────────────────────────────┐            │
│  │  语义化字形变体——独立于上下文的字形替换              │            │
│  │  cv01="@$%&Q→" 风格统一                         │            │
│  │  cv02="a" 顶部一横变体                           │            │
│  │  cv96-99 中文变体（全角标点、居中标点）            │            │
│  │  python 模块: source/py/feature/cv/             │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Layer 3: ssXX (Stylistic Sets)                                  │
│  ┌─────────────────────────────────────────────────┐            │
│  │  样式集——组合多个字形变换成一个可选样式              │            │
│  │  ss01="===" 等号连字断裂                         │            │
│  │  ss05="\\" 反斜杠还原细线条                      │            │
│  │  ss08=">>=" 双头箭头 + 反向箭头                   │            │
│  │  python 模块: source/py/feature/ss/             │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer 1: calt 上下文感知连字

calt（Contextual Alternates）是 Maple Mono 最核心也最复杂的 OpenType Feature。它不是简单的"两字合一"，而是**根据周围字形的上下文**决定是否替换为连字。

### 代码组织

`source/py/feature/calt/` 目录按连字类型拆分子模块：

| 模块 | 连字类型 | 示例 |
|------|---------|------|
| `asciitilde.py` | `~=` 近似等于 | `a ~= b` |
| `cross.py` | `≠ ≡ ≤ ≥` | `x ≠ y` |
| `equal_arrow.py` | `⇒ ⇐ ⇒` 等号箭头 | `a => b => c` |
| `escape.py` | `\\ \. \" \(` 转义符 | `path\\to\\file` |
| `hyphen_arrow.py` | `→ ← ↔` 箭头 | `a -> b` |
| `markup_like.py` | `[TODO] [FIXME]` 标签 | `[import os]` |
| `pipe.py` | `|>= ||>= |>|` 管道箭头 | `text \|> pipe \|> output` |
| `tag.py` | HTML 标签样式 | `<html>` `<html/>` |
| `italic.py` | 斜体连字中断规则 | 避免 `al` `il` 等斜体字母连体 |
| `whitespace/` | 空白相关连字 | `###` 注释标记、`___` 下划线连续、`:` 冒号 |
| `_infinite_utils.py` | 无限箭头辅助 | `---->------>` 连续箭头 |

### calt 的触发条件

calt 查找表通常包含多条规则，每条规则有**匹配模式**和**替换动作**：

```feature
# 简化示例：`=` 后跟 `>` 替换为 `=>`
lookup hyphen_arrow {
    sub [=] by =>_arrow_1;
    sub =>_arrow_1 [=] => by =>_arrow_2;
} hyphen_arrow;
```

Maple Mono 的 Python 代码将这些规则组织成 AST 对象（详见 [04-Feature AST 生成器](04-feature-ast-generator.md)）。

## Layer 2: cvXX 语义化字形变体

cv（Character Variants）提供**独立于上下文**的字形替换。每个 cv 控制一个或一组相关字形的备选样式。

### cv 编号规则

```
cv01-cv11:    常规字形变体（正则风格）
cv31-cv44:    斜体专用变体
cv61-cv66:    标点与符号变体
cv96-cv99:    中文专用变体
```

### 典型 cv 变体

| 编码 | 版本 | 控制字形 | 备选样式 |
|------|------|---------|---------|
| cv01 | v7.0 | `@ $ % & Q =>` | 品牌化圆角风格 |
| cv02 | v7.0 | `a` | 顶部加一横（类似 Consolas） |
| cv35 | v7.0 | 斜体 `l` | 去掉底部尾部 |
| cv61 | v7.1 | `, ;` | 直尾巴风格 |
| cv99 | v7.0 | 中文标点 | 居中对齐（传统风格） |

### 与 calt 的区别

- **calt** 有**上下文条件**——只有在"两个等号连写"时才触发连字
- **cv** 无上下文——只要字形出现就按规则替换，除非被后续规则覆盖

## Layer 3: ssXX 样式集

ss（Stylistic Sets）是**组合多个 cv / 连字变换为一个可选样式**。每个 ss 可以理解为"一键应用的风格预设"。

### 典型 ss 样式集

| 编码 | 版本 | 效果 | 适用场景 |
|------|------|------|---------|
| ss01 | v7.0 | `=== !== ====` 连字断裂 | 不想要多行连字 |
| ss05 | v7.0 | `\ \" \.` 反斜杠还原细线条 | 还原 JetBrains Mono 风格 |
| ss08 | v7.0 | `>>= -<< ->> >>-` 双头箭头 + 反向箭头 | 更丰富的箭头集合 |
| ss03 | v7.0 | 标签允许任意大小写 | `[TODO]` `[todo]` `[Todo]` 都触发 |

### 与 Normal 预设的关系

`--normal` 预设会自动启用以下特征（详见 `normal_enabled_features`）：

```python
normal_enabled_features = [
    "cv01", "cv02", "cv33", "cv34", "cv35", "cv36",
    "cv61", "cv62", "ss05", "ss06", "ss07", "ss08",
]
```

Normal 预设让 Maple Mono 看起来更像 JetBrains Mono——去掉"品牌化"的字形变体，回归朴素。

## Python 代码组织

三层 Feature 在 Python 中的组织方式：

```
source/py/feature/
├── __init__.py            ← generate_fea_string() 主函数
├── ast.py                 ← FeatureWithDocs / Lookup / ClassDef AST
├── calt/                  ← Layer 1: calt 连字模块
│   ├── __init__.py        ← get_calt() / get_calt_lookup()
│   ├── asciitilde.py      ← ~= 近似等于
│   ├── cross.py           ← ≠ ≡ ≤ ≥
│   ├── equal_arrow.py     ← 等号箭头
│   ├── pipe.py            ← 管道箭头
│   └── ...
├── cv/                    ← Layer 2: cvXX 变体
│   ├── cv01.py ... cv11.py
│   ├── cv31.py ... cv44.py
│   └── cv61.py ... cv99.py
├── ss/                    ← Layer 3: ssXX 样式集
│   └── ss01.py ... ss11.py
├── base/                  ← 基础查找表（case/ccmp/clazz/lang/locl/number）
├── regular.py             ← 正则风格的 class_list / cv_list / ss_list
└── italic.py              ← 斜体风格的 class_list / cv_list / ss_list
```

每层各有 `regular` 和 `italic` 两套变体列表——斜体的 cv 有完全不同的编号（cv31-cv44）。

## 关键设计洞察

1. **三层解耦**：calt 管上下文、cv 管单字形、ss 管组合样式——每层独立维护，互不干扰
2. **regular / italic 双轨**：同一个 cv 对 regular 和 italic 字形有完全独立的备选，这在其他编程字体中很少见
3. **Python 模块按功能拆分**：每个连字（asciitilde/cross/pipe）独立成模块——你要修改某种连字规则，改对应的 .py 文件即可
4. **中文独立 cv 编号（cv96-99）**：避免与 ASCII 层冲突，语义清晰
