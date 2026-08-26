---
type: reference_index
title: "onnxmltools API 参考索引"
description: "onnxmltools API 参考文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# onnxmltools API 参考


信源登记簿

本目录登记本知识包所有内容据以派生的 onnxmltools 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 onnxmltools 源码（`external/libs/models/onnx/onnxmltools/onnxmltools/` 目录）的核心模块。

* [9个转换入口与延迟导入机制](convert-entry.md) — `onnxmltools/__init__.py`、`onnxmltools/convert/main.py`、`onnxmltools/convert/common/utils.py`：9个 convert_xxx 函数签名、统一参数模式、延迟导入依赖检查、6条转换路径（自有IR/委托skl2onnx/tf2onnx/内置导出）。
* [Topology IR 三层核心类与编译五阶段流水线](topology-ir.md) — `common/_container.py`、`common/_topology.py`、`common/onnx_ex.py`：Topology/Scope/Operator/Variable 四核心类、C风格唯一名称、raw_name隐藏、is_fed拓扑遍历、compile五阶段（_prune→_resolve_duplicates→_fix_shapes→_infer_all_types→_check_structure）、convert_topology、make_model_ex。
* [双注册池、数据类型系统与apply快捷函数](registration-types.md) — `common/_registration.py`、`common/data_types.py`、`common/_apply_operation.py`、`common/tree_ensemble.py`、`common/shape_calculator.py`：双注册池（converter/shape_calculator）、导入副作用注册、DataType四层体系（标量/张量/序列/字典）、15种TensorType、三向类型猜测、74个apply快捷函数、树模型属性模板。

```{toctree}
:maxdepth: 7

convert-entry
registration-types
topology-ir
```
