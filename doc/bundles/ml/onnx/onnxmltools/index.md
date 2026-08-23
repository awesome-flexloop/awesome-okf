---
type: bundle
title: ONNXMLTools 模型转换工具
okf_version: "0.2"
---


# onnxmltools 知识库

本知识包是多框架机器学习模型到 ONNX 格式转换库 [onnxmltools](https://github.com/onnx/onnxmltools)（Apache-2.0 许可证）的系统化中文源码教程，基于 onnxmltools 1.17.0 源码深度阅读生成，覆盖从整体架构到转换管线、注册体系、类型系统、树模型转换范式的完整知识体系。所有内容均溯源至 onnxmltools Python 源码核心模块（convert/main.py、common/_container.py、common/_topology.py、common/_registration.py、common/data_types.py、common/tree_ensemble.py 等），遵循 [OKF v0.2 规范](concepts/00-overall-architecture.md)。

## 架构与核心机制篇（concepts/）

* [onnxmltools 整体架构：9入口6自有IR+3委托的非对称转换工具](concepts/00-overall-architecture.md) — 非对称架构总览：9个convert入口中6个走自有Topology IR（CoreML/LightGBM/XGBoost/H2O/LibSVM/SparkML）、3个委托外部转换器（sklearn→skl2onnx、keras/TF→tf2onnx、catboost→内置导出），ONNX-ML传统ML算子集是IR实际能力边界。
* [Topology IR：三层核心类、C风格唯一名称、raw_name隐藏](concepts/01-topology-ir.md) — IR核心数据结构：Topology/Scope/Operator/Variable四核心类、C风格唯一名称生成算法、raw_name→onnx_name多对一隐藏机制模拟SSA、is_fed数据驱动拓扑遍历（反向标记初始化+Level-Order调度+优先级排序+动态图增长支持）。
* [编译流水线五阶段：createTopology→compile→convert_topology→make_model](concepts/02-conversion-pipeline.md) — 完整转换流程：parse创建IR→compile五阶段优化（剪枝→identity消重先替换后删除→形状补全→类型推断→结构校验）→convert_topology拓扑遍历调度→make_model_ex opset合并与IR版本映射。

## 注册体系与类型系统篇（concepts/）

* [转换器注册与分发：双注册池、导入副作用、委托路径](concepts/03-converter-registration.md) — 算子注册机制：双注册池（converter/shape_calculator）设计、导入副作用注册模式、字符串key弱类型风险、custom参数不对称风险（仅注册converter不注册shape_calculator会静默跳过形状推断）、多对一映射与内部分发、三条委托路径分析。
* [数据类型系统：四层DataType、TensorType维度规格、三向类型猜测](concepts/04-type-system.md) — 类型体系：DataType四层层次（标量固定shape=[1,1]/张量15种子类/序列/字典）、三类维度规格（int固定/str符号/None未知）、denotation语义标注、三向类型猜测函数族（proto/proto_str/numpy）、guess_data_type自动识别DataFrame/ndarray/Series。

## 范式与工具篇（concepts/）

* [树模型转换范式：LightGBM/XGBoost/CoreML算子集与属性模板](concepts/05-tree-models.md) — 树模型统一范式：TreeEnsembleClassifier/Regressor平行数组属性模板、nodes_modes节点模式（BRANCH_LEQ等7种）、add_node统一填充与tree_weight归一化、zipmap输出控制、split大数精度控制（分段double累加）、without_onnx_ml的Hummingbird后处理、CoreML 15+40个算子全景。
* [Pipeline转换、元数据传播与校验工具](concepts/06-pipeline-metadata.md) — 复合模型处理：SparkML/CoreML Pipeline串联、CoreML元数据自动提取（author/license/shortDescription→metadata_props）、模型I/O工具（load/save_model Protobuf序列化）、ONNX命名合规校验、check_input_and_output_numbers/types校验函数。

## 实战示例（examples/）

* [XGBoost模型转ONNX：从训练到推理验证](examples/xgboost-conversion.md) — XGBoost分类器/回归器转换、Booster原生对象自动包装、initial_types必填规则、输出结构说明（label+probabilities）、onnxruntime推理一致性验证。
* [LightGBM Pipeline转换实战：zipmap/split/without_onnx_ml选项](examples/lightgbm-pipeline.md) — LightGBM分类/回归/排序三类任务转换、zipmap=True/False对比（字典vs张量输出）、split=100大数精度控制（分段Cast+Sum）、without_onnx_ml=Hummingbird纯ONNX转换。
* [CoreML模型转换：从CoreML spec到ONNX](examples/coreml-conversion.md) — CoreML GLM/TreeEnsemble/神经网络转换、metadata自动传播验证、从.mlmodel文件加载转换、15个传统ML算子+40+神经网络层算子支持一览。

## 信源登记簿（references/）

* [9个转换入口与延迟导入机制](references/convert-entry.md) — `__init__.py`、`convert/main.py`、`common/utils.py`：9个convert_xxx函数签名、统一参数模式、延迟导入依赖检查、6条转换路径详解（自有IR/委托skl2onnx/委托tf2onnx/CatBoost内置导出）。
* [Topology IR 三层核心类与编译五阶段流水线](references/topology-ir.md) — `common/_container.py`、`common/_topology.py`、`common/onnx_ex.py`：四核心类API、C风格唯一名称正则替换算法、variable_name_mapping隐藏机制、is_fed数据驱动遍历核心循环、compile五阶段源码、convert_topology九步流程、OPSET_TO_IR_VERSION映射表。
* [双注册池、数据类型系统与apply快捷函数](references/registration-types.md) — `common/_registration.py`、`common/data_types.py`、`common/_apply_operation.py`、`common/tree_ensemble.py`、`common/shape_calculator.py`：双池register/get函数、DataType四层15+子类、TensorType三类维度规格、74个apply_xxx快捷函数、TreeEnsemble属性对默认模板、check_input_and_output校验工具。

## 信任与生命周期说明

* **status 判定依据**：全部 16 个内容文档（7 个概念 + 3 个示例 + 3 个信源登记，另含3个子目录index与根index、log），概念文档均基于对 onnxmltools 源码（`external/libs/models/onnx/onnxmltools/onnxmltools/` 目录）核心模块的逐文件阅读与事实提取（40 条源码事实 F-001~F-040），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。onnxmltools 核心架构（9入口非对称设计、Topology IR四核心类、双注册池、compile五阶段流水线、树模型属性模板）自1.x以来稳定，新转换器和算子支持不断添加但核心设计不变；该日期作为针对未来大版本的保守重新评估节点。

本知识包共收录 16 个内容文档（7 个概念 + 3 个示例 + 3 个信源登记 + 3 个子目录index + 根index + log）。
