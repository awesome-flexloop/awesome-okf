---
type: bundle
title: sklearn-onnx Scikit-learn 转换器
okf_version: "0.2"
---


# sklearn-onnx (skl2onnx) 知识库

本知识包是 scikit-learn 模型到 ONNX 格式转换库 [sklearn-onnx](https://github.com/onnx/sklearn-onnx)（skl2onnx，Apache-2.0 许可证）的系统化中文源码教程，基于 sklearn-onnx 1.21.0 源码深度阅读生成，覆盖从整体架构到转换管线、注册体系、代数API、复合模型处理的完整知识体系。所有内容均溯源至 skl2onnx Python 源码核心模块（convert.py、_topology.py、_registration.py、_container.py、_parse.py、algebra/ 子包等），遵循 [OKF v0.2 规范](concepts/00-overall-architecture.md)。

## 架构与管线篇（concepts/）

* [sklearn-onnx 整体架构：四阶段类编译器管线](concepts/00-overall-architecture.md) — 类编译器架构总览：Parse→Shape Infer→Convert→Assemble 四阶段管线，粗粒度 IR 到细粒度 ONNX 节点的两级粒度分离，模块导入即注册。
* [转换管线：解析sklearn→拓扑IR→数据流调度→ONNX组装](concepts/01-conversion-pipeline.md) — convert_sklearn 主流程：parse_sklearn 递归分发器、固定点迭代调度算法、shape_calculator 与 converter 的两阶段执行、convert_topology 最终组装、to_onnx 简化封装。

## 核心机制篇（concepts/）

* [Topology IR：Scope/Variable/Operator/Component/ModelComponentContainer](concepts/02-topology-ir.md) — 内部 IR 核心类：Variable（边、状态标志、双向链接）、Operator（顶点、OperatorList 自动链接）、Scope（命名空间、唯一命名、options 两级查找）、Topology（单Scope约束、四级查找链）、ModelComponentContainer（细粒度节点收集、拓扑排序、白/黑名单）、DataType 类型体系。
* [转换器注册：别名→实现三级映射、shape_calculator 配对](concepts/03-converter-registration.md) — 双池设计（converter pool + shape_calculator pool）、别名命名规则与别名合并（30+线性回归器共享 SklearnLinearRegressor）、update_registered_converter 一站式注册、四级查找优先级链（custom→mixin→global）、导入副作用注册模式。

## 扩展与实践篇（concepts/）

* [OnnxOperator代数API：嵌入式DSL、类工厂、延迟求值、三件套自动生成](concepts/04-onnx-operator-algebra.md) — ClassFactory 动态生成 ONNX 算子类、OnnxOperator 延迟求值 AST、add_to() 递归展开、OnnxOperatorMixin 自动提供 parser/shape_calculator/converter、运算符重载、wrap_as_onnx_mixin 动态混入。
* [Pipeline/FeatureUnion/ColumnTransformer处理、类型推断initial_types](concepts/05-pipeline-feature-union.md) — initial_types 类型声明与自动推断（guess_initial_types）、ZipMap 三种输出模式、Pipeline 顺序串联（中间步自动zipmap=False）、FeatureUnion 并行加权拼接、ColumnTransformer 列切片+条件合并、final_types 输出覆盖。

## 实战示例（examples/）

* [分类器转ONNX：LogisticRegression 完整示例](examples/classifier-conversion.md) — Iris 数据集训练 LogisticRegression，convert_sklearn 转换、onnxruntime 推理验证、zipmap 选项对比、一致性验证。
* [Pipeline 完整转换：预处理+分类器串联](examples/pipeline-conversion.md) — StandardScaler+PCA+LogisticRegression Pipeline 端到端转换（预处理内嵌ONNX），ColumnTransformer 异构特征 Pipeline（数值+分类列），to_onnx 自动类型推断，intermediate=True 调试。
* [自定义转换器开发：两种模式对比](examples/custom-converter.md) — ThresholdApplier 自定义估计器的 ONNX 导出：传统三件套（parser+shape_calculator+converter）vs OnnxOperatorMixin 代数API（一个方法搞定），Pipeline 嵌入自定义转换器，常见错误调试。

## 信源登记簿（references/）

* [convert_sklearn / to_onnx：转换入口 API](references/convert-api.md) — `skl2onnx/convert.py`、`skl2onnx/__init__.py`：convert_sklearn 17参数签名、to_onnx 简化封装、wrap_as_onnx_mixin、模块导入副作用注册。
* [Topology IR 核心类：Scope / Variable / Operator / Topology](references/topology-ir.md) — `common/_topology.py`、`common/_container.py`、`common/data_types.py`：Variable/Operator/Scope/Topology 类API、数据流调度算法、ModelComponentContainer 节点收集、OPSET_TO_IR_VERSION映射。
* [注册机制（register_converter）与 OnnxOperator 代数 API](references/registration-algebra.md) — `common/_registration.py`、`_supported_operators.py`、`algebra/onnx_ops.py`、`algebra/onnx_operator.py`、`algebra/onnx_operator_mixin.py`：双池注册、别名合并、ClassFactory类工厂、OnnxOperator延迟求值、OnnxOperatorMixin桥接。

## 信任与生命周期说明

* **status 判定依据**：全部 12 个内容文档（6 个概念 + 3 个示例 + 3 个信源登记）均 `status: stable`。内容基于对 sklearn-onnx 源码（`external/libs/models/onnx/sklearn-onnx/skl2onnx/` 目录）核心模块的逐文件阅读与事实提取（34 条源码事实 F-001~F-034），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。sklearn-onnx 核心架构（四阶段管线、Topology IR、双池注册、OnnxOperator 代数API）自 1.x 以来稳定，新转换器和算子支持不断添加但核心设计不变；该日期作为针对未来大版本的保守重新评估节点。

本知识包共收录 12 个内容文档（6 个概念 + 3 个示例 + 3 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
