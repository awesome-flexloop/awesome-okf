---
type: log
title: onnxmltools 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2026-12-31
---

# Bundle Update Log

## 2026-08-22

* **Creation**: 建立 onnxmltools 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 onnxmltools 源码（`external/libs/models/onnx/onnxmltools/onnxmltools/`）核心模块：`__init__.py`（9个转换入口导出）、`convert/main.py`（延迟导入与6条路径调度）、`convert/common/_container.py`（Topology/Scope/Operator/Variable/RawModelContainer/ModelComponentContainer四核心类、名称生成、is_fed拓扑遍历）、`convert/common/_topology.py`（compile五阶段、identity消重、convert_topology、make_model_ex）、`convert/common/_registration.py`（双注册池）、`convert/common/data_types.py`（四层DataType、15种TensorType、三向类型猜测）、`convert/common/_apply_operation.py`（74个apply快捷函数）、`convert/common/tree_ensemble.py`（树模型属性模板）、`convert/common/onnx_ex.py`（OPSET_TO_IR_VERSION映射）、`convert/common/shape_calculator.py`（校验工具）、各框架子目录（lightgbm/xgboost/coreml/h2o/convert.py与operator_converters），提取 40 条源码事实（F-001~F-040），覆盖元数据入口/延迟导入/注册机制/Topology IR/模型构建/类型系统/树模型/框架流程/工具校验九大模块。
* **Add**: I阶段完成——提炼 3 个核心架构洞察（I-01 统一Topology IR是中间语言但只有树模型/CoreML走通自有路径、I-02 注册机制双注册池+导入副作用但custom参数存在双注册不对称风险、I-03 identity消重+延迟删除与is_fed数据驱动拓扑遍历的精巧工程决策），设计知识地图（架构总览1篇→核心机制3篇→类型系统1篇→树模型范式1篇→Pipeline/元数据1篇，共7概念+3示例+3信源）。
* **Add**: E阶段完成——concepts/ 下 7 个概念文档（00-overall-architecture/01-topology-ir/02-conversion-pipeline/03-converter-registration/04-type-system/05-tree-models/06-pipeline-metadata），examples/ 下 3 个实战示例（xgboost-conversion/lightgbm-pipeline/coreml-conversion），references/ 下 3 个信源登记（convert-entry/topology-ir/registration-types），加上 3 个子目录 index.md 和根 index.md、log.md。
