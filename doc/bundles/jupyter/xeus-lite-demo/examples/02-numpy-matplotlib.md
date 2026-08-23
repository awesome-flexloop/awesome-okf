---
type: Example
title: 配置 Python 科学计算环境
description: 为 xeus-lite 添加 NumPy、Matplotlib、Pandas 等科学计算包，配置完整的数据科学环境
tags: [python, numpy, matplotlib, pandas, scientific-computing, data-science]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
  - id: env-source
    resource: /references/environment-source.md
    title: 运行时环境配置信源
---

## 目标

为 JupyterLite 站点配置 Python 科学计算环境，包含 numpy、matplotlib、pandas 等常用包，支持数据处理和可视化。

## 前置条件

- 已完成[第一个部署](01-first-deployment.md)
- 拥有仓库的写入权限

## 步骤1：编辑 environment.yml

1. 在 GitHub 仓库页面，点击根目录下的 `environment.yml` 文件
2. 点击编辑图标（铅笔 ✏️）
3. 将文件内容替换为：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - pandas
  - matplotlib
  - ipycanvas
```

4. 滚动到页面底部，填写 commit message：`add numpy, pandas, matplotlib for scientific computing`
5. 点击 **Commit changes**（直接 commit 到 main 分支）

## 步骤2：等待构建

1. 点击 **Actions** 标签
2. 等待新的构建完成（首次添加新包时构建时间较长，约5-8分钟，因为需要下载 WASM 包）
3. 构建完成后刷新站点

> 💡 后续添加更多包时，由于 conda 缓存机制，构建会快一些。

## 步骤3：验证环境

创建一个新的 Notebook 或新建 cell，运行以下代码验证：

```python
# 验证 numpy
import numpy as np
print(f"NumPy version: {np.__version__}")

# 创建数组
arr = np.array([1, 2, 3, 4, 5])
print(f"Array: {arr}")
print(f"Mean: {arr.mean()}")
```

```python
# 验证 pandas
import pandas as pd
print(f"Pandas version: {pd.__version__}")

# 创建 DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'score': [85, 92, 78]
})
df
```

```python
# 验证 matplotlib
import matplotlib
print(f"Matplotlib version: {matplotlib.__version__}")

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

plt.figure(figsize=(10, 4))
plt.plot(x, y, 'b-', linewidth=2)
plt.fill_between(x, y, alpha=0.3)
plt.title('Sine Wave')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True, alpha=0.3)
plt.show()
```

如果所有代码都正常运行并显示输出/图表，说明科学计算环境配置成功。

## 推荐的科学计算包组合

### 基础数据科学

```yaml
dependencies:
  - xeus-python
  - numpy
  - pandas
  - matplotlib
  - scipy
  - ipycanvas
  - ipywidgets
```

### 机器学习（轻量）

```yaml
dependencies:
  - xeus-python
  - numpy
  - pandas
  - scikit-learn
  - matplotlib
  - scipy
```

### 数据可视化增强

```yaml
dependencies:
  - xeus-python
  - numpy
  - pandas
  - matplotlib
  - bokeh
  - ipycanvas
```

## 常用包可用性参考

| 包 | WASM 可用性 | 说明 |
|----|------------|------|
| numpy | ✅ 可用 | 基础数值计算 |
| pandas | ✅ 可用 | 数据处理 |
| matplotlib | ✅ 可用 | 绘图（inline backend） |
| scipy | ✅ 可用 | 科学计算 |
| scikit-learn | ✅ 可用 | 机器学习 |
| sympy | ✅ 可用 | 符号计算 |
| pillow | ✅ 可用 | 图像处理 |
| scikit-image | ✅ 可用 | 图像算法 |
| bokeh | ✅ 可用 | 交互式可视化 |
| plotly | ⚠️ 需验证 | 可能需要额外配置 |
| seaborn | ⚠️ 需验证 | 基于 matplotlib，可能可用 |
| tensorflow | ❌ 不可用 | 无 WASM 构建 |
| pytorch | ❌ 不可用 | 无 WASM 构建 |
| opencv | ⚠️ 需验证 | 部分功能可用 |

> 不确定包是否可用时，可以访问 https://prefix.dev/channels/emscripten-forge-dev 搜索。

## 注意事项

1. **WASM 性能**：WASM 中的计算性能比原生 Python 慢（约 2-5 倍），适合教学和轻量计算，不适合大规模数据处理
2. **内存限制**：浏览器环境有内存限制（通常 2-4GB），处理大数组可能导致页面崩溃
3. **无网络请求限制**：WASM 环境中的网络请求受浏览器 CORS 限制，`pd.read_csv('https://...')` 可能需要目标服务器支持 CORS
4. **文件系统**：文件存储在浏览器 IndexedDB 中，清除浏览器数据会丢失用户创建的文件
5. **包体积**：添加的包越多，站点首次加载越慢，建议只添加真正需要的包

## 故障排查

**Q: 构建失败，提示包未找到？**
A: 该包可能没有 WASM 版本。检查 prefix.dev 上的 emscripten-forge-dev 通道是否有该包。

**Q: matplotlib 图表不显示？**
A: 确保使用 `plt.show()` 显示图表。JupyterLite 中 matplotlib 默认使用 inline backend。

**Q: 站点加载变慢了？**
A: 正常现象，numpy + pandas + matplotlib 增加了约 20-30MB 的 WASM 下载量。后续访问会使用缓存。

## 相关概念

- [运行时环境配置](/concepts/04-runtime-env-config.md) — environment.yml 配置详解
- [多语言内核支持](/concepts/07-kernel-options.md) — 其他语言内核配置
- [R 内核配置](03-r-kernel.md) — 如果需要 R 语言环境
