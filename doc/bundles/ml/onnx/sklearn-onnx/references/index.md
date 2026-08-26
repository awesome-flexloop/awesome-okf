---
okf_version: "0.2"
type: reference_index
title: sklearn-onnx 源码信源参考
sources:
  - external/libs/models/onnx/sklearn-onnx/skl2onnx/
---

# 信源登记簿

本目录登记本知识包所有内容据以派生的 sklearn-onnx 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 sklearn-onnx 源码（`external/libs/models/onnx/sklearn-onnx/` 目录）的核心模块，版本 1.21.0，作者 Microsoft，Apache-2.0 许可证。

* [convert_sklearn / to_onnx：转换入口 API](convert-api.md) — `skl2onnx/__init__.py`、`skl2onnx/convert.py`：convert_sklearn 17参数签名与四阶段主流程、to_onnx Mixin检测+自动类型推断简化封装、wrap_as_onnx_mixin动态混入、模块导入副作用触发注册。
* [Topology IR 核心类：Scope / Variable / Operator / Topology](topology-ir.md) — `skl2onnx/common/_topology.py`、`common/_container.py`、`common/data_types.py`：Variable 双向链接与状态标志、Operator 粗粒度节点与 OperatorList、Scope 唯一命名与options两级查找、Topology单Scope约束与四级查找链、convert_operators固定点迭代调度算法、ModelComponentContainer细粒度节点收集与拓扑排序、OPSET_TO_IR_VERSION映射。
* [注册机制（register_converter）与 OnnxOperator 代数 API](registration-algebra.md) — `common/_registration.py`、`_supported_operators.py`、`operator_converters/__init__.py`、`algebra/onnx_ops.py`、`algebra/onnx_operator.py`、`algebra/onnx_operator_mixin.py`：双池设计与RegisteredConverter、别名命名规则与别名合并、update_registered_converter一站式注册、ClassFactory动态类生成、OnnxOperator延迟求值AST与add_to递归展开、OnnxOperatorMixin三件套自动桥接。

```{toctree}
:maxdepth: 7

convert-api
registration-algebra
topology-ir
```
