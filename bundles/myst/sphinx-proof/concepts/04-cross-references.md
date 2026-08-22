---
type: Concept
title: 交叉引用与编号映射
description: 使用 label/numref 引用定理，配置跨类型编号共享（如推论跟随定理编号）
tags: [sphinx, proof, cross-reference, numbering, numref, label]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:18:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: proof-source
    resource: /references/proof-source.md
    title: sphinx-proof 源码路径映射
---

# 交叉引用与编号映射

## 交叉引用基础

使用 `:label:` 选项标记定理，通过 `:ref:` 或 `:numref:` 引用。

### :ref: 引用——显示标题文本

```rst
.. theorem:: 勾股定理
   :label: th-pythagoras

   直角三角形两直角边平方和等于斜边平方。

根据:ref:`th-pythagoras`...
```

输出："根据 勾股定理..."

### :numref: 引用——显示编号

```rst
如:numref:`th-pythagoras`所示...
```

输出："如 Theorem 1 所示..."

### 自定义引用文本

```rst
:numref:`勾股定理 <th-pythagoras>`
```

## ProofDomain 注册机制

sphinx-proof 注册了自定义 `ProofDomain`，在 `doctree-read` 阶段将所有定理节点注册到域中：

1. 每个带 `:label:` 的定理在 `env.proof_list` 中创建条目
2. 条目存储 docname、countertype、realtype、ids、nonumber 等信息
3. 通过 StandardDomain 的 labels 机制实现标准 Sphinx 交叉引用

## 跨类型编号映射

默认情况下，每种类型独立编号。通过 `prf_realtyp_to_countertyp` 配置可实现跨类型共享编号。

### 场景：推论跟随定理编号

数学文档中，推论（Corollary）通常继承定理的编号序列：

```python
# conf.py
prf_realtyp_to_countertyp = {
    "corollary": "theorem",
}
```

效果：
- Theorem 1（定理1）
- Theorem 2（定理2）
- Corollary 3（推论3，与定理连续编号）

而非独立编号：
- Theorem 1 → Theorem 2
- Corollary 1（独立序列）

### 场景：引理和定理统一编号

```python
prf_realtyp_to_countertyp = {
    "lemma": "theorem",
    "corollary": "theorem",
    "proposition": "theorem",
}
```

所有逻辑类型（定理/引理/推论/命题）共享连续编号。

### 工作原理

1. 指令解析时，`countertyp = prf_realtyp_to_countertyp.get(realtyp, realtyp)`
2. 创建节点时使用 `NODE_TYPES[countertyp]` 而非 `NODE_TYPES[realtyp]`
3. Sphinx 的 enumerable node 系统根据节点类型（countertyp）分配编号
4. 视觉上通过 CSS 类（`proof lemma`）区分类型，但编号使用共享计数器

### 配置验证

`check_config_values()` 验证映射中的 key 和 value 都必须是有效的 PROOF_TYPES 类型名，非法键值对输出警告并被移除。

## 无编号定理的引用

使用 `:nonumber:` 的定理仍然可以通过 `:ref:` 引用（跳转到锚点），但 `:numref:` 不会显示编号。

```rst
.. theorem:: 预备知识
   :label: th-prelim
   :nonumber:

   这里是预备知识...

详见:ref:`th-prelim`。  # ✅ 可跳转
```

## 并行构建安全

sphinx-proof 正确实现了：
- `env-purge-doc` → `purge_proofs()`：清理当前文档的注册表条目
- `env-merge-info` → `merge_proofs()`：合并并行构建的注册表
- 返回 `parallel_read_safe: True, parallel_write_safe: True`

## 相关概念

- [定理类型详解](/concepts/02-theorem-types.md)
- [配置项参考](/concepts/05-configuration.md)
- [自定义编号配置示例](/examples/custom-numbering.md)
