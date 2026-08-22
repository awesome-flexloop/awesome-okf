---
type: concept
title: "模型检查器 Checker"
description: "check_model 验证规则、ir_version/opset_import 校验、full_check 模式、Python→C++ 委托机制、局部函数检查、外部数据路径安全检查"
sources:
  references: [../references/checker.md, ../references/shape-inference.md, ../references/op-schema.md]
  facts: [F-033, F-034, F-035, F-036, F-037, F-038, F-074, F-082, F-083]
---

# 模型检查器 Checker

## 核心理解

ONNX Checker 是模型验证的核心组件，负责验证 ModelProto 是否符合 ONNX 规范。其核心逻辑全部在 C++ 实现（checker.cc），Python checker.py 只是将 proto 序列化后委托给 C++ 层。理解 Checker 的验证范围和 full_check 模式的区别，是避免"check_model 通过但模型无法运行"问题的关键。

## 机制详解

### Python→C++ 委托架构

Python checker.py 中所有检查函数均为薄层封装（F-034）：

```
Python 层 (checker.py)
│
├── check_model(model)
├── check_graph(graph)
├── check_node(node)
├── check_tensor(tensor)
├── check_value_info(vi)
├── check_attribute(attr)
└── check_sparse_tensor(st)
         │
         │  1. proto.SerializeToString() → bytes
         │  2. C.check_model(bytes, ...)  ← 委托给 pybind11 模块
         ↓
C++ 层 (checker.cc, 通过 onnx_cpp2py_export.checker)
│
├── 反序列化 bytes → proto 对象
├── 执行实际验证逻辑
└── 验证失败 → 抛出 ValidationError (传递到 Python)
```

这种设计的优势：
- 验证逻辑只在 C++ 维护一份，避免 Python/C++ 双重实现不一致
- C++ 验证速度更快
- Python 端可以方便地对任意 proto 子对象进行检查

### check_model 基础验证规则（full_check=False）

基础验证（默认模式）检查以下内容（F-033）：

| 检查项 | 规则 | 对应IR约束 |
|--------|------|-----------|
| ir_version 存在 | 必须设置且 > 0 | 所有版本 |
| ir_version 有效 | ≤ 当前 IR_VERSION | 所有版本 |
| metadata_props 唯一性 | 不能有重复 key | 所有版本 |
| opset_import 要求 | IR ≥ 3 必须指定 opset_import | IR ≥ 3 |
| opset_import 禁止 | IR < 3 不能有 opset_import（默认版本1） | IR < 3 |
| graph 存在 | 必须设置 graph 字段 | 所有版本 |
| 节点输入有效 | 每个 input 引用的名字必须在图中定义 | 所有版本 |
| 节点 op 存在 | op_type 在对应域和 opset 版本的注册表中存在 | 所有版本 |
| initializer 名字唯一 | 不能有重复名字 | 所有版本 |
| 图输入名字唯一 | 不能有重复名字 | 所有版本 |
| 节点输出名字唯一 | 不能有重复名字 | 所有版本 |
| 函数唯一性 | (domain, name, overload) 三元组唯一 | IR ≥ 8 |

**关键认知**：基础验证**不检查形状和类型兼容性**——它只验证结构合法性。

### full_check 模式：形状推断+类型检查

当 `full_check=True` 时，Checker 在基础验证后额外执行（F-037）：

```
check_model(model, full_check=True) 流程：

1. 执行基础验证（同 full_check=False）
      │
      ↓ (通过)
2. 克隆模型（不修改原始模型）
      │
      ↓
3. 对克隆执行形状推断：
   ShapeInferenceOptions{
     check_type: true,         ← 类型一致性检查
     error_mode: 1,            ← 严格模式，节点级错误抛异常
     data_prop: false          ← 不启用数据传播
   }
      │
      ↓
4. 形状推断结果包含在克隆模型中
   （检查类型兼容性、形状可推断性）
      │
      ↓
5. 如果形状推断成功 → 模型完整有效
   如果形状推断失败 → 抛出 ValidationError
```

**full_check 能发现的问题**：
- 算子输入类型不匹配（如 Add 输入类型不同）
- 输入形状不兼容（如 MatMul 的维度不匹配）
- 形状推断链断裂（某个节点无法推断输出形状）

### 局部函数检查与循环检测

IR_VERSION ≥ 8 时（F-038）：

1. **check_model_local_functions**：验证模型中定义的所有局部函数
   - 函数内部节点的 op_type 在函数 opset_import 中存在
   - 函数内部名字引用合法
   - 属性引用正确

2. **check_function_call_cycles**：检测函数调用循环
   - 如果函数 A 调用函数 B，函数 B 又调用函数 A（直接或间接），则检测到循环
   - 函数调用循环会导致内联时无限递归

### CheckerContext：检查上下文

CheckerContext 携带检查过程中的全局上下文信息（F-082）：

```cpp
class CheckerContext {
  int ir_version_;                                    // 当前 IR 版本
  std::unordered_map<std::string, int> opset_imports_; // 域→版本映射
  bool is_main_graph_;                                // 是否在主图中
  const ISchemaRegistry* schema_registry_;            // OpSchema 注册表
  std::string model_dir_;                             // 模型目录（外部数据路径解析）
  bool skip_opset_compatibility_check_;               // 跳过opset兼容检查
  bool check_custom_domain_;                          // 检查自定义域算子
};
```

- 检查子图时，CheckerContext 会被传递，ir_version 和 opset_imports 继承自父图
- `model_dir_` 用于解析外部数据文件的相对路径

### LexicalScopeContext：词法作用域

LexicalScopeContext 处理子图嵌套的名字解析（F-083）：

```cpp
class LexicalScopeContext {
  LexicalScopeContext* parent_context_;  // 父作用域，形成链
  std::unordered_set<std::string> output_names_;

  // 递归查找：当前图 → 父图 → 祖先图
  bool this_or_ancestor_graph_has(const string& name) const;
};
```

子图（如 If 的 then/else branch、Loop 的 body）可以引用外层图中定义的值。LexicalScopeContext 通过作用域链实现嵌套名字查找，类似于编程语言的词法作用域。

### 外部数据路径安全检查

Checker 对外部数据路径进行两层安全防护（F-074）：

1. **resolve_external_data_location**：
   - 要求 `location` 是相对路径
   - 禁止路径包含 `".."` 组件（防止 `../../../etc/passwd` 式遍历）

2. **verify_path_containment**：
   - 对解析后的绝对路径执行 `weakly_canonical`（规范化）
   - 验证规范化路径不超出模型所在目录范围
   - 防止符号链接等方式绕过路径限制

```python
# 不安全的外部数据路径——会被 checker 拒绝
tensor.external_data.append(
    make_attribute("location", "../../../etc/passwd")
)
# checker 报错：路径包含 ".." 或超出模型目录
```

### MAXIMUM_PROTOBUF 限制

```python
MAXIMUM_PROTOBUF = 2147483647  # 2^31 - 1 = 2 GiB - 1
```

超过 2 GiB 的 protobuf 序列化会触发 ValueError（F-035）。这不是 Checker 特有的限制，而是 protobuf 库本身的硬限制。大模型必须使用外部数据格式。

### 使用示例

```python
import onnx

# 基础检查（结构验证，不检查形状类型）
model = onnx.load("model.onnx")
onnx.checker.check_model(model)  # 结构验证
print("基础检查通过")

# 完整检查（结构 + 形状 + 类型）
try:
    onnx.checker.check_model(model, full_check=True)
    print("完整检查通过——模型形状类型兼容")
except onnx.checker.ValidationError as e:
    print(f"完整检查失败: {e}")
    # 通常意味着模型有形状不兼容或类型错误

# 检查单个张量
tensor = onnx.helper.make_tensor("x", onnx.TensorProto.FLOAT, [2,3], [1,2,3,4,5,6])
onnx.checker.check_tensor(tensor)
```

## 关键洞察/反常识

1. **check_model 通过 ≠ 模型可运行**：这是最常见的误解。默认 check_model 只验证结构合法性，不验证形状和类型兼容性。始终使用 `full_check=True` 做最终验证。
2. **Python checker 是纯委托层**：所有 Python 检查函数最终调用 C++ 实现。不要在 Python 层搜索验证逻辑——它在 checker.cc 中。
3. **full_check 不修改原模型**：形状推断在模型副本上进行。如果需要推断结果（value_info），必须显式调用 `infer_shapes()`。
4. **路径安全是内置的**：checker 自动防止路径遍历攻击，不要尝试绕过——这是安全特性不是 bug。
5. **自定义算子需要 OpSchema**：使用自定义域算子（domain 非空且非内置域）时，checker 默认不验证这些算子的签名（除非设置 check_custom_domain_）。自定义算子需要注册 OpSchema 才能通过 full_check。

## 关联概念

- [形状推断实现](06-shape-inference.md) — full_check 使用的形状推断机制
- [算子定义与注册机制 OpSchema](05-operator-schema.md) — checker 如何使用 OpSchema 验证节点
- [序列化与外部数据](08-serialization.md) — 外部数据机制和安全防御
- [模型加载、检查与形状推断](../examples/load-check-model.md) — check_model 的实际使用
