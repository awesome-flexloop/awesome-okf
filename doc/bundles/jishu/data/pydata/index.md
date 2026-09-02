---
okf_version: "0.2"
---

# PyData 科学计算生态

本分组包含 Python 科学计算与数据科学生态中 9 个核心库的系统化中文教程，全部基于源码深度阅读或 2020 年前后教程生成，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 库清单

| 库名 | 简介 | 入口 |
|------|------|------|
| **NumPy** | 科学计算基础库——N维数组、向量化运算、线性代数、随机数 | [numpy/](numpy/index.md) |
| **SymPy** | 符号计算库——符号代数、微积分、方程求解、矩阵、化简 | [sympy/](sympy/index.md) |
| **pandas** | 数据分析核心库——DataFrame/Series、分组聚合、时间序列、IO | [pandas/](pandas/index.md) |
| **matplotlib** | 绑图基础库——Artist层级、多后端、OO/pyplot双接口 | [matplotlib/](matplotlib/index.md) |
| **NetworkX** | 网络/图分析库——节点/边属性、绘制与布局、有向无环图（DAG） | [networkx/](networkx/index.md) |
| **Pillow** | 图像处理库——Image基础、缩放合成、ImageDraw绘制、图像特效 | [pillow/](pillow/index.md) |
| **Plotly.py** | 交互式可视化——声明式API、plotly.js渲染、Express高级接口 | [plotly/](plotly/index.md) |
| **Dash** | Web应用框架——React+Flask/FastAPI、响应式回调、组件系统 | [dash/](dash/index.md) |
| **PyTables** | HDF5数据管理——TB级数据集、Blosc2压缩、索引查询、NumPy集成 | [pytables/](pytables/index.md) |

## 生态依赖关系

```
PyTables ──→ NumPy ←── pandas ←── matplotlib ←── NetworkX
                  ↑↖        ↖           ↖
           SymPy  plotly.py ──→ Dash     Pillow
```

- **NumPy** 是整个生态的数值计算基础（ndarray + ufunc）
- **SymPy** 纯Python符号计算库，不依赖NumPy；可通过lambdify()将符号表达式转为NumPy函数
- **pandas** 基于 NumPy 构建，提供表格数据结构（DataFrame）
- **matplotlib** 是 pandas 默认绑图后端，底层操作 NumPy 数组
- **NetworkX** 的网络绘制依赖 matplotlib（`nx.draw`），其图数据模型基于 Python 容器、部分布局/算法依赖 NumPy
- **Pillow** 的图像处理独立于 matplotlib；其特效示例（手绘/石雕）依赖 NumPy 的 `np.gradient`
- **plotly.py** 提供交互式可视化替代 matplotlib，底层不依赖matplotlib
- **Dash** 基于 plotly.py + Flask/FastAPI 构建Web数据应用
- **PyTables** 基于HDF5和NumPy，提供高性能持久化存储

## 学习路径建议

1. **符号计算**：SymPy（符号 → 表达式树 → 微积分 → 求解器）
2. **科学计算基础**：NumPy（ndarray → dtype → ufunc → 广播）
3. **数据分析**：NumPy → pandas（DataFrame → GroupBy → 时间序列）
4. **静态可视化**：matplotlib（Artist → 后端 → pyplot）
5. **图与网络分析**：NetworkX（节点/边 → 绘制布局 → DAG 神经网络绘制）
6. **图像处理**：Pillow（Image 基础 → 缩放合成 → ImageDraw 绘制 → 特效）
7. **交互式可视化**：plotly.py（Figure → Express → 渲染）
8. **Web应用**：plotly.py → Dash（回调 → 组件 → 多页面）
9. **数据存储**：NumPy → PyTables（HDF5 → Table → 压缩索引）

```{toctree}
:hidden:
:maxdepth: 7

numpy/index
sympy/index
pandas/index
matplotlib/index
networkx/index
pillow/index
plotly/index
dash/index
pytables/index
```
