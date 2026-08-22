---
type: Concept
title: 配置项参考
description: sphinx-proof 的全部配置项：主题选择、编号映射、标题格式、字体粗细、CSS定制
tags: [sphinx, proof, configuration, theme, css, styling]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:20:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 配置项参考

## proof_minimal_theme

**类型**：`bool`  
**默认值**：`False`  
**重建类型**：`html`

选择 CSS 主题。`False` 使用标准主题（带彩色背景的 admonition 风格），`True` 使用简约主题（仅边框，更轻量）。

```python
proof_minimal_theme = True  # 使用简约主题
```

两种主题对应不同的 CSS 文件：
- 标准：`_static/proof.css`
- 简约：`_static/minimal/proof.css`

## prf_realtyp_to_countertyp

**类型**：`dict`  
**默认值**：`{}`  
**重建类型**：`html`

跨类型编号映射，将某些类型映射到其他类型的计数器。详见[交叉引用与编号映射](/concepts/04-cross-references.md)。

```python
# 推论跟随定理编号
prf_realtyp_to_countertyp = {
    "corollary": "theorem",
    "lemma": "theorem",
}
```

配置验证规则：
- key 和 value 都必须是有效的 PROOF_TYPES 类型名
- 非法类型名输出警告并被忽略
- 未映射的类型默认独立计数

## proof_title_format

**类型**：`str`  
**默认值**：`" (%t)"`  
**重建类型**：`html`

自定义定理标题的显示格式。`%t` 占位符替换为定理的标题文本。

```python
# 默认格式：Theorem 1 (标题)
proof_title_format = " (%t)"

# 方括号格式：Theorem 1 [标题]
proof_title_format = " [%t]"

# 冒号格式：Theorem 1: 标题
proof_title_format = ": %t"

# 仅编号不显示标题（无副标题时的格式）
proof_title_format = ""  # 仅当没有标题参数时生效
```

注意：格式字符串必须包含 `%t`（当有标题参数时），否则输出警告。

## proof_number_weight

**类型**：`str`  
**默认值**：`""`  
**重建类型**：`html`

自定义定理编号部分的字体粗细 CSS 值。

```python
proof_number_weight = "bold"      # 加粗
proof_number_weight = "normal"    # 正常
proof_number_weight = "600"       # 数值
```

## proof_title_weight

**类型**：`str`  
**默认值**：`""`  
**重建类型**：`html`

自定义定理标题（admonition-title）的字体粗细 CSS 值。

```python
proof_title_weight = "bold"
```

### 工作原理

字体粗细通过构建后修改 CSS 文件实现：
1. `copy_asset_files()` 复制 CSS 到输出目录
2. 若设置了 weight 配置，读取输出的 proof.css
3. 用 `str.replace()` 将默认 font-weight 替换为用户配置值
4. 写回修改后的 CSS

## numfig 编号格式

sphinx-proof 自动为所有类型设置 numfig 格式：

```python
numfig_format = {
    "theorem": "theorem %s",
    "lemma": "lemma %s",
    "definition": "definition %s",
    # ... 其他类型
}
```

可在 `conf.py` 中覆盖为中文：

```python
numfig_format = {
    "theorem": "定理 %s",
    "lemma": "引理 %s",
    "definition": "定义 %s",
    "corollary": "推论 %s",
    "proof": "证明 %s",
    "axiom": "公理 %s",
}
```

## 国际化（i18n）

消息目录名为 `"proof"`，翻译文件位于 `translations/locales/`。

```python
# 定理类型标题的翻译通过 Sphinx 的 gettext 机制
# 翻译"theorem"、"lemma"等类型名需要配合 Sphinx 语言设置
language = "zh_CN"
```

## CSS 自定义

关键 CSS 选择器：

| 选择器 | 元素 |
|--------|------|
| `div.proof` | 所有定理/证明容器 |
| `div.proof.theorem` | 定理框 |
| `div.proof p.admonition-title` | 标题栏 |
| `span.caption-number` | 编号部分 |
| `span.caption-text` | 标题文本部分 |
| `div.theorem-content` | 定理内容区 |

自定义 CSS 示例：

```css
div.proof.theorem {
    border-left: 4px solid #1a73e8;
    background-color: #f8f9fa;
}

div.proof.definition {
    border-left: 4px solid #34a853;
}
```

## 相关概念

- [定理类型详解](/concepts/02-theorem-types.md)
- [交叉引用与编号映射](/concepts/04-cross-references.md)
- [自定义编号配置示例](/examples/custom-numbering.md)
