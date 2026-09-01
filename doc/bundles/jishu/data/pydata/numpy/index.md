---
okf_version: "0.2"
---

# NumPy 科学计算库知识库

本知识包是 [NumPy](https://numpy.org)（Numerical Python，Python科学计算基础库）的系统化中文教程，基于 NumPy 2.x 源码（`numpy/_core/` 目录）深度阅读生成，覆盖从 ndarray 内存布局到线性代数与随机数的完整知识体系。所有内容均溯源至 NumPy 源码（`numpy/__init__.py`、`numpy/_core/multiarray.py`、`numpy/_core/umath.py`、`numpy/_core/_dtype.py`、`numpy/_core/numerictypes.py` 等核心模块），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 入门基础（concepts/）

* [NumPy简介](concepts/00-introduction.md) — 科学计算基础库定位、BSD许可证、ndarray核心概念、NumPy vs Python list、核心子包概览。
* [ndarray多维数组](concepts/01-ndarray.md) — 内存布局（C/F顺序）、shape/strides/dtype/nbytes属性、视图vs副本、flags标志位详解。
* [dtype数据类型系统](concepts/02-dtype-system.md) — 类型层次（int/float/complex/bool/string/datetime）、kind字符码、类型提升规则、结构化dtype。
* [ufunc通用函数](concepts/03-ufunc.md) — 逐元素运算机制、一元/二元ufunc分类、out/where参数、reduce/accumulate/outer/reduceat/at方法。

## 核心机制（concepts/）

* [广播规则](concepts/04-broadcasting.md) — 广播的4条核心规则、形状对齐过程、stride=0零拷贝实现、常见广播模式（外积、中心化、距离矩阵）与错误诊断。
* [索引与切片](concepts/05-indexing.md) — 基本切片、布尔索引、花式索引（fancy indexing）、np.where条件选择、np.take沿轴提取、视图/副本行为。
* [数组创建](concepts/06-array-creation.md) — array/asarray、arange/linspace/logspace/geomspace、zeros/ones/empty/full、_like函数、fromfunction/fromiter/frombuffer、np.mgrid/np.ogrid、identity/eye/diag。
* [线性代数与随机数](concepts/07-linear-algebra.md) — dot/matmul/einsum/tensordot张量运算、linalg子包（分解/求逆/特征值/SVD）、FFT变换、random模块（Generator/BitGenerator/SeedSequence/分布采样）。

## 实战示例（examples/）

* [基础数组操作](examples/basic-array-ops.md) — 数组创建、属性查看、索引切片、逐元素运算、形状变换、统计计算、视图与副本验证，全部代码可直接运行。
* [广播实战](examples/broadcasting-practice.md) — 外积计算、数据中心化与Z-score标准化、欧氏/Manhattan距离矩阵、网格函数评估、批量运算、stride=0验证。

## 信源登记簿（references/）

* [NumPy核心初始化源码](references/core-init.md) — `numpy/__init__.py` 和 `numpy/_core/__init__.py` 核心初始化逻辑、版本号、子包惰性加载机制、公开API清单、Array API版本。
* [ndarray与数组创建API源码](references/ndarray-source.md) — `_core/multiarray.py`、`_core/numeric.py`、`_core/fromnumeric.py` 中的ndarray类定义、数组创建函数签名、规约包装机制。
* [ufunc通用函数系统源码](references/ufunc-source.md) — `_core/umath.py` ufunc列表、ufunc属性（nin/nout/nargs/identity）、frompyfunc工厂、errstate错误控制。
* [dtype与数值类型系统源码](references/dtype-source.md) — `_core/_dtype.py`、`_core/numerictypes.py` 中的kind字符映射、类型层次树、genericTypeRank、标志位常量、结构化dtype字符串表示。

## 学习路径建议

1. **新手入门**：00-introduction → 01-ndarray → 06-array-creation → 运行 examples/basic-array-ops.md
2. **运算核心**：02-dtype-system → 03-ufunc → 04-broadcasting → 运行 examples/broadcasting-practice.md
3. **数据处理**：05-indexing → 07-linear-algebra
4. **源码溯源**：阅读 references/ 中的信源文档，理解API的底层实现

## 信任与生命周期说明

* **status 判定依据**：全部 16 个内容文档（8 个概念 + 2 个示例 + 4 个信源登记 + 3 个子目录 index + 根 index.md + log.md），非 index/log 文件均 `status: stable`。内容基于对 NumPy 2.x 源码（`external/libs/python/NumPy/numpy/numpy/` 目录）核心子系统的逐模块阅读与事实提取（43个编号源码事实 F-001 ~ F-043）。
* **stale_after 解释**：统一设置为 `2027-12-31`。NumPy 核心 API（ndarray、ufunc、dtype、广播）自 NumPy 1.0 以来保持高度稳定；NumPy 2.0 做了一些清理但核心概念不变，该日期作为对未来大版本变化的保守重新评估节点。
* **核验链路**：`generated.at` 记录原始生成时刻（2026-08-22）；`verified.at` 记录过程核验事件（2026-08-22），所有类名、函数名、参数名均通过源码Grep验证。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
