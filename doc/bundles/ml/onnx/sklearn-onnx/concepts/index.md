---
type: concept_index
title: "sklearn-onnx 核心概念索引"
description: "sklearn-onnx 核心概念文档导航"
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# sklearn-onnx 核心概念


概念文档

本目录包含 sklearn-onnx 的 6 个核心概念文档，按学习路径排列：从架构总览到具体机制，最后到扩展实践。

## 架构总览

* [sklearn-onnx 整体架构：四阶段类编译器管线](00-overall-architecture.md) — 类编译器架构总览：Parse→Shape Infer→Convert→Assemble 四阶段管线，粗粒度 IR 到细粒度 ONNX 节点的两级粒度分离，模块导入即注册机制。
* [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](01-conversion-pipeline.md) — convert_sklearn 主流程详解：parse_sklearn 递归分发、_parse_sklearn_simple_model/pipepline/feature_union/column_transformer 各解析器、is_fed/is_evaluated 状态机驱动的固定点迭代调度、convert_topology 最终组装。

## 核心机制

* [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](02-topology-ir.md) — 内部 IR 核心类：Variable（数据流边）、Operator（粗粒度计算顶点）、Scope（命名空间与唯一命名）、Topology（IR容器）、ModelComponentContainer（细粒度节点收集器），DataType 类型体系，白/黑名单算子过滤。
* [转换器注册：别名→实现三级映射、shape_calculator 配对](03-converter-registration.md) — 双池设计（converter pool + shape_calculator pool）、别名命名规则与别名合并（解决类爆炸）、update_registered_converter 一站式注册、四级查找优先级链、options 两级作用域（类级+实例级）、导入副作用注册模式。

## 扩展与实践

* [OnnxOperator代数API：嵌入式DSL、类工厂、延迟求值、三件套自动生成](04-onnx-operator-algebra.md) — ClassFactory 动态生成算子类、OnnxOperator 延迟求值 AST、add_to() 递归展开、OnnxOperatorMixin 三件套自动桥接（parser/shape_calculator/converter 只需一个 to_onnx_operator）、运算符重载、wrap_as_onnx_mixin 动态混入。
* [Pipeline/FeatureUnion/ColumnTransformer处理、类型推断initial_types](05-pipeline-feature-union.md) — initial_types 类型声明与自动推断（guess_initial_types）、DataType 类型层次、ZipMap 注入机制（三种模式）、Pipeline 顺序串联（中间步骤自动 zipmap=False）、FeatureUnion 并行加权拼接、ColumnTransformer 列切片+条件合并+递归转换、final_types 输出覆盖。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-conversion-pipeline
02-topology-ir
03-converter-registration
04-onnx-operator-algebra
05-pipeline-feature-union
```
