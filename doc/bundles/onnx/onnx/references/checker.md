---
type: reference
title: "checker.py/checker.cc/checker.h：模型检查器实现"
description: "checker 的 C++ 核心验证逻辑、Python 委托机制、full_check 形状推断、MAXIMUM_PROTOBUF 限制、CheckerContext、LexicalScopeContext、外部数据路径安全"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/checker.cc"
    facts: [F-033, F-037, F-038, F-074]
  - path: "external/libs/models/onnx/onnx/onnx/checker.py"
    facts: [F-034, F-035, F-036]
  - path: "external/libs/models/onnx/onnx/onnx/checker.h"
    facts: [F-082, F-083]
---

# checker.py/checker.cc/checker.h：模型检查器实现

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnx/checker.h` | C++ 头文件 | CheckerContext、LexicalScopeContext 类声明、验证函数签名 |
| `onnx/checker.cc` | C++ 实现 | check_model 核心验证逻辑、路径安全检查、形状推断集成 |
| `onnx/checker.py` | Python 模块 | 薄层封装，将 proto 序列化后委托给 C++ 实现 |

## 关键事实登记

### F-033：check_model 验证规则

**信源**：`onnx/checker.cc` L1265-L1296

`check_model` 函数对 ModelProto 执行以下验证：
1. `ir_version` 必须设置且不能超过当前 `IR_VERSION`
2. `metadata_props` 中不能有重复的 key
3. IR >= 3 时必须指定 `opset_import`
4. IR < 3 时不能有 `opset_import`（此时默认 opset 域版本为1）
5. 递归验证 graph 中的节点、输入输出、initializer
6. 验证每个节点的 op_type 在对应域的 opset 版本中存在

### F-034：Python checker 全委托 C++ 实现

**信源**：`onnx/checker.py` L54-L117

Python 端所有检查函数均为薄层封装：
- `check_value_info`、`check_tensor`、`check_attribute`、`check_node`、`check_graph`、`check_sparse_tensor`、`check_model`
- 实现方式：将 proto 对象序列化为字符串（`SerializeToString()`），然后调用 C++ 绑定模块 `onnx.onnx_cpp2py_export.checker`（别名 `C`）中的对应函数
- C++ 端反序列化后执行实际检查逻辑
- 这种设计避免了 Python/C++ 双重维护检查逻辑

### F-035：MAXIMUM_PROTOBUF 常量

**信源**：`onnx/checker.py` L35；`onnx/serialization.py` L105-L109

```python
MAXIMUM_PROTOBUF = 2147483647  # 2^31 - 1 = 2 GiB - 1 byte
```

protobuf 序列化的硬限制为 2 GiB。超过此大小的 protobuf 会触发 ValueError，提示使用外部数据（external data）。

### F-036：DEFAULT_CONTEXT 初始化

**信源**：`onnx/checker.py` L39-L42

默认检查上下文初始化时：
- `ir_version` 设为当前 `IR_VERSION`
- `opset_imports` 设为 `{"": onnx.defs.onnx_opset_version()}`（标准域当前版本）

### F-037：full_check 模式执行形状推断

**信源**：`onnx/checker.cc` L1326-L1329；L1341-L1347

当 `check_model` 的 `full_check=True` 时：
1. 对模型副本（clone）执行形状推断，不修改原始模型
2. 使用 `ShapeInferenceOptions{check_type=true, error_mode=1, data_prop=false}`
3. `check_type=true`：检查输入输出类型一致性
4. `error_mode=1`：节点级错误抛出异常
5. `data_prop=false`：不启用数据传播（仅使用形状信息，不使用实际数据值）
6. 形状推断结果写入 graph 的 `value_info` 字段

### F-038：局部函数检查与调用循环检测

**信源**：`onnx/checker.cc` L1301-L1304

当 IR_VERSION >= 8 时，check_model 额外执行：
1. `check_model_local_functions`：验证模型中定义的所有局部函数（FunctionProto）
2. `check_function_call_cycles`：检测函数调用是否存在循环（A→B→A 等递归循环）

### F-074：外部数据路径安全验证

**信源**：`onnx/checker.cc` L1364-L1409

C++ checker 中实现了两层路径安全防护：

1. **verify_path_containment**：
   - 对路径进行规范化（`weakly_canonical`）
   - 验证解析后的路径不超出模型所在目录范围
   - 防止路径遍历攻击（如 `../../etc/passwd`）

2. **resolve_external_data_location**：
   - 要求 `location` 为相对路径
   - 禁止路径中包含 `".."` 组件
   - 结合 model_dir 解析绝对路径

### F-082：CheckerContext 结构

**信源**：`onnx/checker.h` L40-L103

```cpp
class CheckerContext {
  int ir_version_;
  std::unordered_map<std::string, int> opset_imports_;
  bool is_main_graph_;
  const ISchemaRegistry* schema_registry_;  // 默认 OpSchemaRegistry::Instance()
  std::string model_dir_;
  bool skip_opset_compatibility_check_;
  bool check_custom_domain_;
  // ...
};
```

CheckerContext 携带检查过程中的上下文信息，包括 IR 版本、opset 导入表、schema 注册表、模型目录（用于外部数据解析）等。

### F-083：LexicalScopeContext 词法作用域

**信源**：`onnx/checker.h` L105-L145

```cpp
class LexicalScopeContext {
  LexicalScopeContext* parent_context_;  // 指向父作用域，构成链
  std::unordered_set<std::string> output_names_;
  // ...
  bool this_or_ancestor_graph_has(const std::string& name) const;
};
```

LexicalScopeContext 支持词法作用域链：
- 通过 `parent_context_` 指针形成作用域链
- `this_or_ancestor_graph_has()` 方法递归查找当前图和所有祖先图中的名字
- 用于在子图（如 If/Loop 的 body 属性）中解析名字引用时，正确处理作用域嵌套
