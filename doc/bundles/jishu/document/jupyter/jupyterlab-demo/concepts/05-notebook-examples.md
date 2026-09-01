---
type: Concept
title: "Notebook 示例解析"
description: "逐篇解析 notebooks/ 目录下的6个 Jupyter Notebook 示例：Data、Fasta、R、Cpp、Julia、Lorenz，理解每个示例展示的 JupyterLab 能力及其教学目的"
tags: [notebooks, examples, lorenz, data, fasta, R, C++, Julia, multi-kernel]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: ci, resource: "/references/ci-workflow-source.md", title: "CI工作流信源" }
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
---

# Notebook 示例解析

jupyterlab-demo 的 `notebooks/` 目录包含6个精心选择的 Jupyter Notebook 示例，覆盖多语言内核、不同数据科学领域和 JupyterLab 的特定功能。CI 工作流会自动执行其中3个验证环境正确性。

## Notebook 清单与验证状态

| Notebook | 内核 | 领域 | CI验证 | 演示用途 |
|----------|------|------|:------:|---------|
| Data.ipynb | Python | 数据处理 | ✅ | 基础数据处理工作流 |
| Fasta.ipynb | Python | 生物信息学 | ✅ | FASTA查看器扩展 |
| R.ipynb | R | 统计计算 | ✅ | R 语言内核 |
| Cpp.ipynb | C++ | 系统编程 | ❌ | C++ 交互式编程 |
| Julia.ipynb | Julia | 科学计算 | ❌ (构建后删除) | Julia 语言内核 |
| Lorenz.ipynb | Python | 可视化 | ❌ (默认打开) | 3D可视化与工作区布局 |

## Data.ipynb — 数据处理基础

### 定位

基础 Python 数据处理示例，是 CI 第一个验证的 Notebook。

### 教学目的

- 验证 Python 数据科学栈（pandas、matplotlib 等）正确安装
- 展示 JupyterLab 中最常见的数据处理工作流
- 作为新用户打开 Notebook 时的第一个参考示例

### CI 验证

```bash
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --stdout notebooks/Data.ipynb > /dev/null
```

- 执行超时：60秒
- 验证方式：无异常即通过（stdout重定向到/dev/null）

## Fasta.ipynb — 生物信息学序列分析

### 定位

展示 jupyterlab-fasta 扩展的使用，演示 JupyterLab 如何通过扩展支持专业领域文件格式。

### 数据来源

- `data/zika_assembled_genomes.fasta`：110条寨卡病毒基因组序列
- 来源：2017年 Nature 论文 "Zika virus evolution and spread in the Americas"
- 数据描述：从10个国家和地区的临床和蚊子样本中组装的基因组，经过系统发育分析推断病毒在美洲的进化

### 教学目的

1. 展示第三方扩展（jupyterlab-fasta）如何无缝集成到 JupyterLab
2. 演示特定领域（生物信息学）文件格式的渲染
3. 证明扩展开发的简便性——几十行代码即可添加新文件类型支持（参见演示脚本QConAI.md）

### 引用方式

Notebook 中可能引用论文：
```bibtex
@article{metsky2017zika,
  title={Zika virus evolution and spread in the Americas},
  author={Metsky, Hayden C and Matranga, Christian B and ...},
  journal={Nature},
  year={2017}
}
```

### CI 验证

```bash
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --stdout notebooks/Fasta.ipynb > /dev/null
```

## R.ipynb — R 语言统计计算

### 定位

展示 Jupyter 的多语言内核能力——在同一 JupyterLab 界面中运行 R 代码。

### 依赖包

- `r-irkernel`：R 语言 Jupyter 内核
- `r-ggplot2`：R 最流行的绘图包

### 教学目的

1. 证明 Jupyter 不仅限于 Python——支持多种编程语言
2. 展示 R 中 ggplot2 可视化在 Notebook 中的输出效果
3. 让使用 R 的数据科学家感受到 JupyterLab 的兼容性

### 多内核切换

在 JupyterLab 中切换内核的方式：
- 新建 Notebook 时通过 Launcher 选择内核
- 已有 Notebook 通过右上角内核指示器切换
- Console 可以绑定到任意 Notebook 的相同内核

### CI 验证

```bash
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --stdout notebooks/R.ipynb > /dev/null
```

## Cpp.ipynb — C++ 交互式编程

### 定位

展示 xeus-cling C++ 内核，这是基于 Cling（C++ 解释器）的交互式 C++ 编程环境。

### 依赖关系（已注释）

```yaml
# - xeus-cling       # C++内核
# - xtensor          # C++张量计算库（类似NumPy）
# - xtensor-blas     # BLAS后端
# - xwidgets         # C++版ipywidgets
# - xleaflet         # C++版ipyleaflet地图
```

### 教学目的

1. 展示 C++ 也可以像 Python 一样交互式编写和执行（无需编译-链接-运行循环）
2. 介绍 xtensor——C++ 中的 NumPy 风格张量计算
3. 配合 images/xeus-cling.png、xtensor.png、xwidgets.png 截图展示 C++ 交互式生态

### 当前状态

由于构建稳定性问题，C++ 内核依赖在 environment.yml 中被注释掉。`Cpp.ipynb` 保留在仓库中，供手动安装 xeus-cling 环境的用户使用。

### 相关图片资源

`notebooks/images/` 目录包含：
- `xeus-cling.png`：C++ 内核截图
- `xtensor.png`：xtensor 库截图
- `xwidgets.png`：C++ 交互控件截图
- `marie.png`：演示用图片

## Julia.ipynb — Julia 科学计算

### 定位

展示 Julia 语言内核。

### 当前状态：构建后删除

postBuild 脚本中有明确的删除操作：

```bash
rm demo/notebooks/Julia.ipynb
```

**设计逻辑**：
1. 源仓库保留 Julia.ipynb（供本地安装Julia环境的开发者使用）
2. Binder 环境中不包含 Julia 内核（安装Julia会大幅增加构建时间和镜像体积）
3. 如果不删除，用户在 Binder 中打开会看到"找不到 Julia 内核"错误
4. 防御性删除确保用户不会遇到令人困惑的错误信息

这是一个很好的"用户体验优先"的工程决策——宁可少一个功能，也不让用户遇到错误。

## Lorenz.ipynb — 洛伦兹吸引子3D可视化

### 定位

**Binder 默认打开的 Notebook**，也是 workspace.json 中预设的主面板内容。

### 配套模块

`notebooks/lorenz.py` 提供了求解洛伦兹微分方程的辅助函数：

```python
def solve_lorenz(sigma=10.0, beta=8./3, rho=28.0):
    """Plot a solution to the Lorenz differential equations."""
    max_time = 4.0
    N = 30
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection='3d')
    # ... 设置坐标轴范围
    def lorenz_deriv(x_y_z, t0, sigma=sigma, beta=beta, rho=rho):
        x, y, z = x_y_z
        return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]
    # ... 求解ODE并绘制3D轨迹
```

### 为什么选洛伦兹吸引子？

1. **视觉震撼**：3D 蝴蝶形状的混沌轨迹，第一印象极佳
2. **计算有趣**：展示 SciPy 的 `integrate.odeint` 求解常微分方程
3. **3D绘图**：展示 matplotlib 的 3D 投影能力
4. **参数可调**：sigma/beta/rho 三个参数可以交互调整
5. **轻量快速**：求解和渲染速度快，不需要大数据文件

### 工作区布局中的角色

workspace.json 将 Lorenz.ipynb 放在左侧主面板（50%宽度），与右侧的 JupyterLab 文档并排。这创造了一个"边学边练"的界面：
- 左侧：可以立即运行和修改代码
- 右侧：可以查阅 JupyterLab 官方文档

## 外部 Notebook（通过 build.py 引入）

除了 notebooks/ 目录自带的示例，`demo/` 场景还通过 rename 映射引入外部仓库的 Notebook：

| 目标路径 | 来源仓库 | 内容 |
|---------|---------|------|
| `notebooks/pandas.ipynb` | PythonDataScienceHandbook | Pandas 数据聚合与分组 |
| `notebooks/bqplot.ipynb` | bqplot | 基础交互式绘图 |

这些 Notebook 通过 build.py 的浅克隆从外部仓库获取，展示了如何将第三方教学材料整合到演示环境中。

## Notebook 资源文件

| 文件/目录 | 用途 |
|----------|------|
| `notebooks/audio/audio.wav` | 音频嵌入演示 |
| `notebooks/images/marie.png` | 通用演示图片（居里夫人） |
| `notebooks/images/xeus-cling.png` | C++内核截图 |
| `notebooks/images/xtensor.png` | xtensor库截图 |
| `notebooks/images/xwidgets.png` | C++控件截图 |

## CI 验证策略

CI 只执行3个 Notebook（Data、Fasta、R），覆盖三个关键维度：
- ✅ Python 数据科学基础（Data.ipynb）
- ✅ 第三方扩展+数据文件（Fasta.ipynb）
- ✅ 非Python内核（R.ipynb）

未执行的 Notebook：
- Cpp.ipynb / Julia.ipynb：对应内核未安装（或不稳定）
- Lorenz.ipynb：3D可视化在无头CI环境中可能有渲染问题

这种选择体现了"验证核心路径，不追求100%覆盖"的务实策略。

## 相关概念

- [演示能力维度与多内核支持](04-demo-capabilities.md)
- [数据文件与多格式查看器](06-data-files.md)
- [工作区布局与交互体验](07-workspace-layout.md)
- [实战：在 Binder 启动 JupyterLab 演示](../examples/01-launch-binder.md)
