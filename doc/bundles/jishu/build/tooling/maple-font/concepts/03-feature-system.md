---
type: Concept
title: "特征系统"
description: "scripts/feature 包的组织方式、生成式与文件式两条特征应用路径，以及特征标签的命名结构"
tags: ["opentype", "feature", "calt", "cv", "ss", "fea"]
sources:
  - id: feature-readme
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/feature/README.md
    title: Maple Mono Feature Module
  - id: ot-features
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/opentype-features.md
    title: OpenType Features
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 特征系统

## 1. 为什么需要特征系统

Maple Mono 的连字与字形变体数量多、版本迭代频繁。若全部手写 `.fea`：

- 新增一个 `cvXX` 需要在多个位置同步修改；
- 常规体与斜体的类定义大量重复；
- 文档中的特性清单容易与实现脱节。

v8 因此把特征规则拆成“Python 对象定义 + 编译为 `.fea` 源码”，同时保留直接编辑 `.fea` 的文件式路径，供高级用户使用。

## 2. 模块布局

```
scripts/feature/
├── ast.py          # 小型 AST：Line / Clazz / Lookup / Feature / FeatureWithDocs
├── regular.py      # 常规体拉丁特征定义
├── italic.py       # 斜体拉丁特征定义
├── base/           # 共享基础特征：ccmp、locl、case、数字等
├── calt/           # 上下文连字与纯文本标签
├── cv/             # 字符变体 cv01–cv99
├── ss/             # 风格集 ss01–ss13
├── compiler.py     # 组装完整特征源码，暴露生成入口
└── apply.py        # 在构建中选择生成式或文件式应用
```

对照关系：

| 目录/模块 | 产出 | 典型标签 |
|-----------|------|----------|
| `base/` | 基础替换与语言系统 | `ccmp`、`locl`、`case` |
| `calt/` | 上下文连字、无限箭头、纯文本标签 | `calt` |
| `cv/` | 字符变体 | `cv01`–`cv68`、`cv96`–`cv99` |
| `ss/` | 风格集 | `ss01`–`ss13` |

## 3. 三条特征层级

1. **Glyph class（字形类）**：`Clazz` 声明可复用的字形集合，例如 `@Digit = [zero one two three];`。
2. **Lookup（查找）**：`Lookup` 把一个或多个替换组织为命名块，便于在特征内引用与复用。
3. **Feature（特征）**：`Feature` 以 OpenType 标签（`calt`、`cv01`、`ss07`）包裹内容，并携带版本文档信息。

`FeatureWithDocs` 在其上增加 `id`、`desc`、`example` 与 `version`，用于生成 `documentation/opentype-features.md` 的特性清单；`CharacterVariant` 与 `StylisticSet` 进一步约束 `id` 范围并生成 `cvParameters` / `featureNames` 名称块。

## 4. 两条应用路径

### 4.1 生成式（默认）

- 构建前为 regular 与 italic 各准备一份特征源码；
- 启用的单一替换把目标字形轮廓与前进宽度复制到源字形，写入**每个 UFO master**；
- 启用的上下文/连字查找挂到 `calt`；
- `disable` 的特征规则被移除；
- `ignore` 的特征保留为普通 OpenType 特征（默认不激活）。

### 4.2 文件式（`--apply-fea-file`）

- 读取 `sources/features/regular.fea` 或 `sources/features/italic.fea`；
- 在同一源准备步骤中应用，`include` 在冻结规则之前解析；
- CJK 静态字体在字形合并之后改用 `regular_cn.fea` / `italic_cn.fea`，只在该边界冻结 CJK 专属替换。

两条路径的共同点是“在 Fontmake 编译前进入源”，因此静态与变量输出得到一致的轮廓结果。

## 5. 特征标签命名

| 标签 | 含义 | 示例 |
|------|------|------|
| `calt` | 上下文连字 | `->`、`=>`、`::`、`[TODO]` |
| `cvXX` | 字符变体 | `cv01` 规范化符号、`cv12` 无尾 `u`（v8 新增） |
| `cv3X` | 斜体专属变体 | `cv31`–`cv45` |
| `cv9X` | CJK 专属变体 | `cv96` 全角引号、`cv99` 传统居中标点 |
| `ssXX` | 风格集 | `ss07` 放宽多大于号连字、`ss12/ss13` 西里尔字形 |

v8 代码库中较新的特性包括 `cv12`、`cv45`、`cv67`、`cv68`、`ss12`、`ss13`。完整清单由 `task.py fea` 从特性定义自动生成到 `documentation/opentype-features.md`，不应手工维护。

## 6. 同步与再生成

修改 `scripts/feature/` 后运行：

```sh
uv run task.py fea
```

该任务会刷新以下签入产物：

- `sources/features/regular.fea`
- `sources/features/italic.fea`
- `sources/features/cn.fea`
- `sources/features/regular_cn.fea`
- `sources/features/italic_cn.fea`
- `documentation/opentype-features.md`
- `sources/schema.json` 与 `config.json` 中的 feature-freeze 段
- `scripts/in_browser.py` 中的 moving-rule 列表

生成后必须逐文件审查 diff，避免保留无关波动。

## 7. 相关文档

- AST 类与辅助函数：[特征 AST 生成器](04-feature-ast-generator.md)、[特征生成 API](../references/feature-generator-api.md)
- 冻结模式与生效时机：[特征冻结机制](05-freeze-mechanism.md)
- 动手修改特征：[自定义特征构建示例](../examples/custom-feature-build.md)
