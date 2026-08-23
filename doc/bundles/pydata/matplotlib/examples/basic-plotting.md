---
okf_version: "0.2"
type: example
title: Matplotlib 基础绑图
description: 折线图/散点图/柱状图/直方图/子图/样式/注释/保存图片的完整可运行代码示例，覆盖 matplotlib 最常用的绑图功能
tags: [matplotlib, plotting, example, line-chart, scatter, bar, histogram, subplot]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: mpl-axes
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/axes/_axes.py
    title: matplotlib.axes._axes — Axes 绘图方法
  - id: mpl-pyplot
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/pyplot.py
    title: matplotlib.pyplot 模块
---

# Matplotlib 基础绑图

本文提供 matplotlib 最常用绑图类型的完整可运行代码示例，所有代码均使用面向对象接口（`fig, ax = plt.subplots()`）编写。建议在 Jupyter Notebook 或 Python 脚本中逐步运行。

## 前置导入

所有示例共用以下导入：

```python
import matplotlib.pyplot as plt
import numpy as np

# 如果使用 Jupyter Notebook，取消下行注释以显示内联图形
# %matplotlib inline
```

## 一、折线图（Line Plot）

最基础的绑图类型，使用 `ax.plot()`。

```python
# 生成数据
x = np.linspace(0, 2 * np.pi, 200)
y_sin = np.sin(x)
y_cos = np.cos(x)

# 创建 Figure 和 Axes
fig, ax = plt.subplots(figsize=(8, 5))

# 绘制多条线
ax.plot(x, y_sin, color='tab:blue', linewidth=2, linestyle='-', label='sin(x)')
ax.plot(x, y_cos, color='tab:red', linewidth=2, linestyle='--', label='cos(x)')

# 填充两条线之间的区域
ax.fill_between(x, y_sin, y_cos, alpha=0.1, color='gray')

# 设置标签和标题
ax.set_xlabel('x (弧度)', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title('正弦和余弦函数', fontsize=14, fontweight='bold')

# 添加图例和网格
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3, linestyle=':')

# 添加水平参考线
ax.axhline(y=0, color='black', linewidth=0.8)
ax.axvline(x=np.pi, color='green', linewidth=0.8, linestyle='--', alpha=0.7)
ax.text(np.pi + 0.05, 0.05, r'$\pi$', fontsize=12, color='green')

plt.tight_layout()
plt.show()
```

### MATLAB 风格格式字符串

`plot()` 支持 MATLAB 风格的格式字符串，快速指定颜色+线型+标记：

```python
fig, ax = plt.subplots(figsize=(8, 4))
x = np.arange(0, 10)

# 'r-o' = red, solid line, circle markers
# 'b--s' = blue, dashed line, square markers
# 'g:' = green, dotted line, no markers
# 'k^-' = black, solid line, triangle-up markers
ax.plot(x, x, 'r-o', label='y = x')
ax.plot(x, x**1.5, 'b--s', label='y = x^1.5')
ax.plot(x, x**2/10, 'g:^', label='y = x²/10')
ax.legend()
ax.set_title('格式字符串示例')
plt.show()
```

## 二、散点图（Scatter Plot）

使用 `ax.scatter()`，适合展示两个变量之间的关系，支持点大小/颜色映射。

```python
# 生成随机数据
np.random.seed(42)
n = 200
x = np.random.randn(n)
y = 2 * x + np.random.randn(n) * 0.8
colors = np.random.rand(n)       # 颜色映射值
sizes = 50 + 200 * np.random.rand(n)  # 点大小

fig, ax = plt.subplots(figsize=(8, 6))

# 散点图：c=颜色映射，s=大小，alpha=透明度，cmap=色图
scatter = ax.scatter(x, y, c=colors, s=sizes, alpha=0.6,
                     cmap='viridis', edgecolors='white', linewidth=0.5)

# 添加颜色条
fig.colorbar(scatter, ax=ax, label='随机颜色值')

ax.set_xlabel('X', fontsize=12)
ax.set_ylabel('Y', fontsize=12)
ax.set_title('散点图（大小/颜色映射）', fontsize=14)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.show()
```

## 三、柱状图（Bar Chart）

使用 `ax.bar()` 和 `ax.barh()`（水平柱状图）。

```python
# 数据
categories = ['Python', 'C++', 'Java', 'JavaScript', 'Rust']
values = [85, 72, 68, 60, 78]
errors = [5, 8, 6, 7, 4]  # 误差棒

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 垂直柱状图
bars = ax1.bar(categories, values, yerr=errors, capsize=5,
               color=['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#CCB974'],
               edgecolor='black', linewidth=0.8)
ax1.set_ylabel('评分', fontsize=12)
ax1.set_title('编程语言评分（柱状图）', fontsize=13)
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3)

# 在柱子上方添加数值标签
for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
             f'{val}', ha='center', va='bottom', fontsize=11)

# 水平柱状图
y_pos = np.arange(len(categories))
ax2.barh(y_pos, values, xerr=errors, capsize=5,
         color=['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#CCB974'],
         edgecolor='black', linewidth=0.8)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(categories)
ax2.set_xlabel('评分', fontsize=12)
ax2.set_title('编程语言评分（水平柱状图）', fontsize=13)
ax2.set_xlim(0, 100)
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.show()
```

### 分组柱状图与堆叠柱状图

```python
# 分组柱状图
categories = ['Q1', 'Q2', 'Q3', 'Q4']
product_a = [120, 135, 145, 160]
product_b = [90, 100, 110, 125]
x = np.arange(len(categories))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 分组
ax1.bar(x - width/2, product_a, width, label='产品A', color='steelblue')
ax1.bar(x + width/2, product_b, width, label='产品B', color='coral')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.set_ylabel('销售额（万元）')
ax1.set_title('分组柱状图')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 堆叠
ax2.bar(categories, product_a, label='产品A', color='steelblue')
ax2.bar(categories, product_b, bottom=product_a, label='产品B', color='coral')
ax2.set_ylabel('销售额（万元）')
ax2.set_title('堆叠柱状图')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()
```

## 四、直方图（Histogram）

使用 `ax.hist()` 展示数据分布。

```python
# 生成不同分布的数据
np.random.seed(42)
data_normal = np.random.normal(loc=0, scale=1, size=1000)
data_bimodal = np.concatenate([
    np.random.normal(-2, 0.8, 500),
    np.random.normal(2, 0.8, 500)
])
data_uniform = np.random.uniform(-3, 3, 1000)
data_exponential = np.random.exponential(scale=1, size=1000)

fig, axs = plt.subplots(2, 2, figsize=(10, 8))

# 基本直方图
axs[0,0].hist(data_normal, bins=30, color='steelblue', edgecolor='white',
              alpha=0.8, density=True)
axs[0,0].set_title('正态分布')
axs[0,0].set_ylabel('概率密度')

# 双峰分布 + 密度曲线
axs[0,1].hist(data_bimodal, bins=40, color='coral', edgecolor='white',
              alpha=0.8, density=True, label='直方图')
# 添加核密度估计曲线
from scipy.stats import gaussian_kde
kde = gaussian_kde(data_bimodal)
xx = np.linspace(-5, 5, 200)
axs[0,1].plot(xx, kde(xx), 'k-', linewidth=2, label='KDE')
axs[0,1].set_title('双峰分布')
axs[0,1].legend()

# 累积直方图
axs[1,0].hist(data_normal, bins=50, color='seagreen', cumulative=True,
              edgecolor='white', alpha=0.8, density=True)
axs[1,0].set_title('累积分布')

# 多数据集直方图
axs[1,1].hist(data_normal, bins=30, alpha=0.5, label='正态', color='blue',
              edgecolor='white', density=True)
axs[1,1].hist(data_uniform, bins=30, alpha=0.5, label='均匀', color='orange',
              edgecolor='white', density=True)
axs[1,1].hist(data_exponential, bins=30, alpha=0.5, label='指数', color='green',
              edgecolor='white', density=True)
axs[1,1].set_title('多分布对比')
axs[1,1].legend(fontsize=9)

for ax in axs.flat:
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()
```

## 五、饼图（Pie Chart）

使用 `ax.pie()`。

```python
labels = ['苹果', '香蕉', '橙子', '葡萄', '其他']
sizes = [30, 25, 20, 15, 10]
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
explode = (0.05, 0, 0, 0, 0)  # 突出第一块

fig, ax = plt.subplots(figsize=(7, 7))

wedges, texts, autotexts = ax.pie(
    sizes,
    explode=explode,
    labels=labels,
    colors=colors,
    autopct='%1.1f%%',       # 显示百分比
    startangle=90,
    shadow=True,
    textprops={'fontsize': 12}
)

# 设置百分比文本颜色为白色
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax.set_title('水果销售占比', fontsize=14, fontweight='bold')
ax.axis('equal')  # 保证饼图是正圆形

plt.tight_layout()
plt.show()
```

## 六、子图（Subplots）

matplotlib 提供多种子图布局方式。

### 6.1 plt.subplots() 网格布局

```python
fig, axs = plt.subplots(2, 3, figsize=(12, 7))
x = np.linspace(0, 2*np.pi, 100)

# axs 是 2x3 的二维数组
plot_funcs = [np.sin, np.cos, np.tan, np.exp, np.log1p, np.square]
titles = ['sin(x)', 'cos(x)', 'tan(x)', 'exp(x)', 'log(1+x)', 'x²']

for ax, func, title in zip(axs.flat, plot_funcs, titles):
    ax.plot(x, func(x), linewidth=2)
    ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.3)
    if func == np.tan:
        ax.set_ylim(-5, 5)  # tan 有渐近线，限制Y范围

fig.suptitle('2×3 子图网格', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
```

### 6.2 共享坐标轴

```python
fig, axs = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
x = np.linspace(0, 10, 200)

axs[0].plot(x, np.sin(x), 'b-')
axs[0].set_ylabel('sin(x)')
axs[0].grid(alpha=0.3)

axs[1].plot(x, np.cos(x), 'r-')
axs[1].set_ylabel('cos(x)')
axs[1].grid(alpha=0.3)

axs[2].plot(x, np.sin(x)*np.cos(x), 'g-')
axs[2].set_ylabel('sin(x)·cos(x)')
axs[2].set_xlabel('x')
axs[2].grid(alpha=0.3)

fig.suptitle('共享X轴的子图', fontsize=13)
plt.tight_layout()
plt.show()
```

### 6.3 subplot_mosaic() 复杂布局

```python
# 用字符串定义布局
fig, axd = plt.subplot_mosaic(
    [
        ['line', 'scatter'],
        ['hist', 'hist'],
        ['bar', 'pie']
    ],
    figsize=(12, 10)
)

x = np.linspace(0, 10, 100)
# axd 是字典，通过名称访问 Axes
axd['line'].plot(x, np.sin(x))
axd['line'].set_title('折线图')

axd['scatter'].scatter(np.random.rand(50), np.random.rand(50))
axd['scatter'].set_title('散点图')

axd['hist'].hist(np.random.randn(500), bins=20, edgecolor='white')
axd['hist'].set_title('直方图（跨两列）')

axd['bar'].bar(['A','B','C'], [3,7,2])
axd['bar'].set_title('柱状图')

axd['pie'].pie([1,2,3], labels=['x','y','z'])
axd['pie'].set_title('饼图')

plt.tight_layout()
plt.show()
```

## 七、样式与主题

### 7.1 使用预定义样式

```python
# 查看所有可用样式
print(plt.style.available)

# 使用 ggplot 风格
with plt.style.context('ggplot'):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label='sin(x)')
    ax.plot(x, np.cos(x), label='cos(x)')
    ax.set_title('ggplot 样式')
    ax.legend()
    plt.show()
```

### 7.2 常用样式一览

```python
styles_to_show = ['default', 'ggplot', 'seaborn-v0_8', 'bmh',
                  'fivethirtyeight', 'dark_background']
fig, axs = plt.subplots(2, 3, figsize=(14, 8))
x = np.linspace(0, 10, 100)

for ax, style in zip(axs.flat, styles_to_show):
    with plt.style.context(style):
        ax.plot(x, np.sin(x), linewidth=2)
        ax.plot(x, np.cos(x), linewidth=2)
        ax.set_title(style, fontsize=10)
        ax.tick_params(labelsize=8)

plt.tight_layout()
plt.show()
```

### 7.3 自定义 rcParams

```python
# 设置全局参数
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'lines.linewidth': 2,
    'lines.color': 'steelblue',
    'figure.figsize': (8, 5),
    'figure.dpi': 100,
    'grid.alpha': 0.3,
})

# 绑图
fig, ax = plt.subplots()
x = np.linspace(0, 2*np.pi, 100)
ax.plot(x, np.sin(x), label='sin')
ax.plot(x, np.cos(x), label='cos')
ax.set_title('自定义 rcParams 样式')
ax.legend()
ax.grid(True)
plt.show()

# 恢复默认
plt.rcdefaults()
```

## 八、注释与文本标注

### 8.1 基本文本与注释

```python
fig, ax = plt.subplots(figsize=(9, 6))
x = np.linspace(0, 10, 200)
y = np.sin(x) * np.exp(-0.1*x)

ax.plot(x, y, 'b-', linewidth=2)
ax.set_xlabel('x')
ax.set_ylabel('阻尼振荡')
ax.set_title('注释示例', fontsize=14)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linewidth=0.5)

# 最大值点
max_idx = np.argmax(y)
max_x, max_y = x[max_idx], y[max_idx]
ax.plot(max_x, max_y, 'ro', markersize=8)
ax.annotate(
    f'最大值\n({max_x:.2f}, {max_y:.2f})',
    xy=(max_x, max_y),          # 箭头指向点
    xytext=(max_x + 1, max_y + 0.1),  # 文本位置
    arrowprops=dict(
        arrowstyle='->',
        color='red',
        lw=1.5,
        connectionstyle='arc3,rad=0.2'
    ),
    fontsize=11,
    color='red',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='red', alpha=0.8)
)

# 文本标注
ax.text(7, 0.3, r'$y = \sin(x) \cdot e^{-0.1x}$',
        fontsize=14, color='blue',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='blue'))

# 添加数学公式
ax.text(0.5, -0.5, r'$\int_0^{10} \sin(x) e^{-0.1x}\, dx \approx 0.99$',
        fontsize=12)

plt.tight_layout()
plt.show()
```

### 8.2 LaTeX 数学公式

matplotlib 原生支持 LaTeX 数学公式（使用内置 mathtext 引擎，无需系统安装 LaTeX）：

```python
fig, ax = plt.subplots(figsize=(8, 5))
x = np.linspace(-3, 3, 200)
y = np.exp(-x**2/2) / np.sqrt(2*np.pi)

ax.plot(x, y, 'b-', linewidth=2)
ax.fill_between(x, y, alpha=0.2)
ax.set_title(r'正态分布：$\mathcal{N}(\mu=0, \sigma^2=1)$', fontsize=14)
ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$',
              fontsize=13)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
```

## 九、图像显示（imshow）

```python
# 生成二维图像数据
np.random.seed(42)
# 创建一个简单的图案
x = np.linspace(-5, 5, 200)
y = np.linspace(-5, 5, 200)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-0.1*(X**2 + Y**2))

fig, ax = plt.subplots(figsize=(8, 6))

# imshow 显示二维数组
im = ax.imshow(Z,
               extent=[-5, 5, -5, 5],  # 坐标范围
               origin='lower',          # Y轴向上为正
               cmap='RdBu_r',          # 色图
               aspect='auto')
# 添加等高线
ax.contour(X, Y, Z, levels=10, colors='black', linewidths=0.5, alpha=0.5)

fig.colorbar(im, ax=ax, label='Z值')
ax.set_title('二维函数图像 + 等高线', fontsize=14)
ax.set_xlabel('X')
ax.set_ylabel('Y')

plt.tight_layout()
plt.show()
```

## 十、保存图片

使用 `fig.savefig()` 将图形保存到文件。

```python
x = np.linspace(0, 2*np.pi, 100)
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(x, np.sin(x), 'b-', linewidth=2)
ax.set_title('保存图片示例')
ax.grid(alpha=0.3)

# 保存为不同格式
# fig.savefig('output.png', dpi=150, bbox_inches='tight')     # PNG 位图
# fig.savefig('output.pdf', bbox_inches='tight')              # PDF 矢量
# fig.savefig('output.svg', bbox_inches='tight')              # SVG 矢量
# fig.savefig('output.eps', bbox_inches='tight')              # EPS 矢量
# fig.savefig('output.jpg', dpi=200, quality=95)              # JPEG
# fig.savefig('output.tiff', dpi=150)                         # TIFF

# 重要参数说明：
# - dpi: 分辨率（每英寸点数），默认100
# - bbox_inches='tight': 自动裁剪空白边距
# - transparent=True: 透明背景
# - facecolor: 背景色
# - edgecolor: 边框色
# - pad_inches: bbox_inches='tight' 时的填充边距

print("支持的输出格式:", fig.canvas.get_supported_filetypes().keys())
plt.show()
```

## 十一、完整综合示例

一个完整的数据可视化工作流程：

```python
import matplotlib.pyplot as plt
import numpy as np

# 1. 设置样式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 中文支持
plt.rcParams['axes.unicode_minus'] = False  # 负号正常显示

# 2. 生成/加载数据
np.random.seed(42)
t = np.arange(0, 24, 0.5)
temp_day = 20 + 8 * np.sin((t - 6) * np.pi / 12) + np.random.normal(0, 1, len(t))
humidity = 60 - 20 * np.sin((t - 6) * np.pi / 12) + np.random.normal(0, 3, len(t))

# 3. 创建 Figure 和 Axes
fig, ax1 = plt.subplots(figsize=(10, 6))

# 4. 主图：温度（左Y轴）
color_temp = '#E74C3C'
ax1.set_xlabel('时间（小时）', fontsize=12)
ax1.set_ylabel('温度 (°C)', color=color_temp, fontsize=12)
line1 = ax1.plot(t, temp_day, '-', color=color_temp, linewidth=2,
                 label='温度', alpha=0.8)
ax1.fill_between(t, temp_day, alpha=0.1, color=color_temp)
ax1.tick_params(axis='y', labelcolor=color_temp)
ax1.set_ylim(0, 35)

# 5. 双Y轴：湿度
ax2 = ax1.twinx()
color_hum = '#3498DB'
ax2.set_ylabel('湿度 (%)', color=color_hum, fontsize=12)
line2 = ax2.plot(t, humidity, '--', color=color_hum, linewidth=2,
                 label='湿度', alpha=0.8)
ax2.tick_params(axis='y', labelcolor=color_hum)
ax2.set_ylim(0, 100)

# 6. 标注特殊点
max_temp_idx = np.argmax(temp_day)
ax1.plot(t[max_temp_idx], temp_day[max_temp_idx], 'o', color='darkred', markersize=8)
ax1.annotate(f'最高温 {temp_day[max_temp_idx]:.1f}°C',
             xy=(t[max_temp_idx], temp_day[max_temp_idx]),
             xytext=(t[max_temp_idx]+2, temp_day[max_temp_idx]+2),
             arrowprops=dict(arrowstyle='->', color='darkred'),
             fontsize=10, color='darkred',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor='darkred'))

# 7. 合并图例
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', fontsize=11)

# 8. 标题和布局
ax1.set_title('24小时温度与湿度变化', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlim(0, 24)
ax1.set_xticks(range(0, 25, 3))
ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## 常见问题速查

| 问题 | 解决方案 |
|------|---------|
| 中文显示为方块 | 设置字体：`plt.rcParams['font.sans-serif'] = ['SimHei']`，或 `['Noto Sans CJK SC']` |
| 负号显示异常 | `plt.rcParams['axes.unicode_minus'] = False` |
| 保存图片有白边 | `fig.savefig(..., bbox_inches='tight', pad_inches=0.1)` |
| 图片模糊 | 提高 DPI：`fig.savefig(..., dpi=300)` |
| 图例遮挡数据 | `ax.legend(loc='best')` 或手动调整位置 |
| 子图重叠 | `plt.tight_layout()` 或 `fig.tight_layout(pad=2)` |
| 后端不显示窗口 | 切换后端：`matplotlib.use('TkAgg')` |
| 无头环境报错 | 使用 Agg 后端：`matplotlib.use('Agg')` 且不调用 `plt.show()` |

## 相关概念

- [Artist 体系](../concepts/01-artist-hierarchy.md)
- [pyplot 状态机](../concepts/03-pyplot-state-machine.md)
- [后端系统](../concepts/02-backend-system.md)
- [Matplotlib 简介](../concepts/00-introduction.md)
- [Artist 层级源码参考](../references/artist-hierarchy.md)
