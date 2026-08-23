---
type: log
title: sklearn-onnx 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 sklearn-onnx 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 sklearn-onnx 源码（`external/libs/models/onnx/sklearn-onnx/skl2onnx/`）核心模块：`convert.py`（转换入口API）、`__init__.py`（版本元信息与顶层导出）、`common/_topology.py`（Topology/Scope/Variable/Operator IR核心类与数据流调度）、`common/_container.py`（ModelComponentContainer ONNX图构建器）、`common/_registration.py`（双池注册机制）、`common/data_types.py`（DataType类型体系）、`_supported_operators.py`（别名映射与update_registered_converter）、`_parse.py`（sklearn对象树递归解析、Pipeline/FeatureUnion/ColumnTransformer/ZipMap处理）、`algebra/onnx_ops.py`（ClassFactory动态类生成）、`algebra/onnx_operator.py`（OnnxOperator延迟求值AST）、`algebra/onnx_operator_mixin.py`（OnnxOperatorMixin三件套自动桥接）、`operator_converters/`与`shape_calculators/`（60+内置转换器导入副作用注册）等，提取34条源码事实，覆盖转换入口/Topology IR/注册体系/类型系统/复合模型解析/代数API等全栈模块。
* **Add**: I阶段完成——提炼3个核心架构洞察（I-01 四阶段类编译器管线而非直接翻译/I-02 别名三级映射+四级覆盖注册体系/I-03 OnnxOperator嵌入式DSL延迟求值桥接sklearn与ONNX），设计知识地图（架构总览2篇→核心机制2篇→扩展实践2篇，共6概念+3示例+3信源）。
* **Add**: E阶段完成——concepts/下6个概念文档（00-overall-architecture/01-conversion-pipeline/02-topology-ir/03-converter-registration/04-onnx-operator-algebra/05-pipeline-feature-union），examples/下3个实战示例（classifier-conversion/pipeline-conversion/custom-converter），references/下3个信源登记（convert-api/topology-ir/registration-algebra），加上3个子目录index.md和根index.md、log.md。
