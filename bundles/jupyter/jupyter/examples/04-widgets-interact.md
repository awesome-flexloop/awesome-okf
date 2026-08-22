---
type: example
title: 使用 ipywidgets 构建交互式 Notebook
description: 使用 ipywidgets 创建滑块、按钮、图表等交互控件，实现参数调节、数据探索、动态可视化的交互式 Notebook
tags: [example, ipywidgets, interact, widgets, interactive, visualization]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T11:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# 使用 ipywidgets 构建交互式 Notebook

本示例演示如何使用 ipywidgets 在 Jupyter Notebook 中创建交互式控件，实现参数化的数据探索和可视化。

## 前置条件

- 已安装 JupyterLab 或 Notebook
- 安装 ipywidgets：`pip install ipywidgets` 或 `conda install ipywidgets`
- JupyterLab 用户需要安装扩展：`pip install jupyterlab_widgets`
- 已阅读 [交互式控件与富显示](../concepts/09-widgets-display.md)
- 建议安装：matplotlib、numpy、pandas

## 步骤 1：最简单的交互 — @interact 装饰器

`interact` 装饰器是创建交互式控件最快的方式，根据函数参数类型自动生成控件。

```python
from ipywidgets import interact
import ipywidgets as widgets
```

### 整数滑块

```python
@interact(x=(0, 100, 5))  # (最小值, 最大值, 步长)
def print_square(x=50):
    print(f"{x}² = {x**2}")
```

执行后会自动生成一个滑块，拖动滑块时函数自动重新执行，输出更新。

### 浮点数滑块

```python
@interact(frequency=(0.1, 10.0, 0.1))
def sine_wave(frequency=1.0):
    import numpy as np
    x = np.linspace(0, 2*np.pi, 200)
    y = np.sin(frequency * x)
    print(f"Frequency: {frequency} Hz, Period: {1/frequency:.2f}")
    print(f"Max value: {y.max():.3f}, Min value: {y.min():.3f}")
```

### 复选框

```python
@interact(show_details=False)
def greet(show_details):
    if show_details:
        print("这是一个交互式演示！")
        print("勾选复选框显示详细信息。")
    else:
        print("Hello!")
```

### 下拉选择

```python
@interact(city=['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'])
def show_population(city='Beijing'):
    populations = {
        'Beijing': 2189, 'Shanghai': 2487,
        'Guangzhou': 1868, 'Shenzhen': 1756
    }
    print(f"{city} 常住人口约 {populations[city]} 万")
```

### 下拉选择（显示名称映射到值）

```python
@interact(n_value={'one': 1, 'ten': 10, 'hundred': 100, 'thousand': 1000})
def power_of_two(n_value=10):
    print(f"2^{n_value} = {2**n_value}")
```

## 步骤 2：显式控件创建

使用 `interact` 便捷但有局限。显式创建控件对象提供更精细的控制。

```python
from ipywidgets import IntSlider, FloatSlider, Dropdown, Checkbox
from IPython.display import display

# 创建控件
slider = IntSlider(min=0, max=100, value=50, description='数值:', continuous_update=False)
check = Checkbox(value=False, description='显示平方')
dropdown = Dropdown(options=['加法', '乘法', '幂运算'], value='加法', description='运算:')

display(slider, check, dropdown)
```

参数说明：
- `continuous_update=False`：拖动滑块时不实时更新，只在释放鼠标时更新（性能更好）
- `description`：控件旁边的标签文本

### 将控件绑定到函数

使用 `interact` 的函数形式：

```python
def compute(value, show_square, operation):
    result = value
    if operation == '加法':
        result = value + 10
    elif operation == '乘法':
        result = value * 10
    else:  # 幂运算
        result = value ** 2
    
    print(f"结果: {result}")
    if show_square:
        print(f"平方: {value**2}")

interact(compute, value=slider, show_square=check, operation=dropdown);
```

## 步骤 3：交互式数据可视化

ipywidgets 与 Matplotlib 结合是最常见的使用场景。

```python
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import interactive

def plot_sine(frequency=1.0, amplitude=1.0, phase=0.0, show_grid=True):
    x = np.linspace(0, 4*np.pi, 500)
    y = amplitude * np.sin(frequency * x + phase)
    
    plt.figure(figsize=(10, 4))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.title(f'Sine Wave: A={amplitude}, f={frequency}, φ={phase:.2f}')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.ylim(-3, 3)
    if show_grid:
        plt.grid(True, alpha=0.3)
    plt.show()

interactive_plot = interactive(
    plot_sine,
    frequency=FloatSlider(min=0.1, max=5.0, step=0.1, value=1.0, description='频率:'),
    amplitude=FloatSlider(min=0.1, max=2.5, step=0.1, value=1.0, description='振幅:'),
    phase=FloatSlider(min=0, max=2*np.pi, step=0.1, value=0.0, description='相位:'),
    show_grid=Checkbox(value=True, description='显示网格')
)

output = interactive_plot.children[-1]
output.layout.height = '350px'  # 固定输出区域高度，避免页面跳动
interactive_plot
```

`interactive` 与 `interact` 的区别：`interactive` 返回控件对象，可以编程访问控件值。

## 步骤 4：按钮和事件回调

按钮是最常用的触发型控件，通过 `.on_click()` 绑定回调函数。

```python
from ipywidgets import Button, IntText, Output
from IPython.display import display

# 创建控件
count_display = IntText(value=0, description='计数:', disabled=True)
increment_btn = Button(description='+1', button_style='success')
decrement_btn = Button(description='-1', button_style='danger')
reset_btn = Button(description='重置', button_style='warning')
output = Output()

# 定义回调函数
def on_increment(b):
    count_display.value += 1
    with output:
        output.clear_output()
        print(f"计数增加到 {count_display.value}")

def on_decrement(b):
    count_display.value -= 1
    with output:
        output.clear_output()
        print(f"计数减少到 {count_display.value}")

def on_reset(b):
    count_display.value = 0
    with output:
        output.clear_output()
        print("计数器已重置")

# 绑定事件
increment_btn.on_click(on_increment)
decrement_btn.on_click(on_decrement)
reset_btn.on_click(on_reset)

# 布局显示
from ipywidgets import HBox, VBox
controls = HBox([increment_btn, decrement_btn, reset_btn])
display(VBox([count_display, controls, output]))
```

`button_style` 可选值：`'success'`（绿）、`'info'`（蓝）、`'warning'`（橙）、`'danger'`（红）、`''`（默认灰）。

## 步骤 5：使用 Output 控件管理输出

`Output` 控件是一个强大的输出容器，可以捕获 stdout/stderr 和 display() 的内容。

```python
from ipywidgets import Output

out = Output()
display(out)

# 写入输出
with out:
    print("这段文字显示在 Output 控件中")
    display(pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}))

# 清空输出
out.clear_output()

# 追加输出
with out:
    print("新的输出行")
```

### 动态更新图表

使用 Output 控件和 clear_output 实现动态刷新：

```python
from IPython.display import clear_output
import time

out = Output()
display(out)

for i in range(50):
    with out:
        clear_output(wait=True)  # wait=True 避免闪烁
        x = np.linspace(0, 4*np.pi, 200)
        y = np.sin(x + i*0.1)
        plt.figure(figsize=(8, 3))
        plt.plot(x, y)
        plt.ylim(-1.2, 1.2)
        plt.title(f'Frame {i}')
        plt.show()
    time.sleep(0.05)
```

## 步骤 6：布局组织控件

### HBox 和 VBox

```python
from ipywidgets import HBox, VBox, Label

# 水平排列
row1 = HBox([Label('参数 A:'), IntSlider(value=50)])
row2 = HBox([Label('参数 B:'), FloatSlider(value=0.5, min=0, max=1)])
row3 = HBox([Label('选项:'), Dropdown(options=['A', 'B', 'C'])])

# 垂直堆叠
form = VBox([row1, row2, row3], layout=widgets.Layout(padding='10px', border='1px solid #ccc'))
display(form)
```

### Tab 和 Accordion

```python
from ipywidgets import Tab, Accordion

# 标签页
tab1 = VBox([IntSlider(description='滑块1'), FloatSlider(description='滑块2')])
tab2 = VBox([Checkbox(description='选项1'), Checkbox(description='选项2')])
tab3 = Text(description='输入:')

tabs = Tab(children=[tab1, tab2, tab3])
tabs.set_title(0, '参数设置')
tabs.set_title(1, '开关选项')
tabs.set_title(2, '文本输入')
display(tabs)

# 手风琴（可折叠面板）
acc = Accordion(children=[tab1, tab2, tab3])
acc.set_title(0, '基础参数')
acc.set_title(1, '高级选项')
display(acc)
```

### GridBox（网格布局）

```python
from ipywidgets import GridBox, Button, Layout

buttons = [Button(description=str(i), layout=Layout(width='50px', height='50px')) for i in range(9)]
grid = GridBox(buttons, layout=Layout(
    grid_template_columns='repeat(3, 50px)',
    grid_template_rows='repeat(3, 50px)',
    grid_gap='5px'
))
display(grid)
```

## 步骤 7：常用控件速查

```python
# 文本输入
from ipywidgets import Text, Textarea, Password
Text(value='', placeholder='输入文本', description='文本:')
Textarea(value='', placeholder='多行文本', rows=5)
Password(placeholder='密码')

# 颜色选择器
from ipywidgets import ColorPicker
ColorPicker(value='#ff0000', description='颜色:')

# 日期选择
from ipywidgets import DatePicker
DatePicker(description='日期:')

# 文件上传
from ipywidgets import FileUpload
FileUpload(accept='.csv,.xlsx', multiple=False, description='上传:')

# 进度条
from ipywidgets import IntProgress, FloatProgress
progress = IntProgress(min=0, max=100, value=0, description='加载中:')
display(progress)
import time
for i in range(101):
    progress.value = i
    time.sleep(0.02)

# 范围滑块
from ipywidgets import IntRangeSlider
IntRangeSlider(value=(20, 80), min=0, max=100, description='范围:')

# 播放控件（动画）
from ipywidgets import Play, jslink
play = Play(value=0, min=0, max=100, step=1, interval=100, description="播放")
slider = IntSlider(min=0, max=100)
jslink((play, 'value'), (slider, 'value'))  # JS 端联动（无需往返 Kernel）
HBox([play, slider])
```

### jslink：前端联动（不经过 Python）

`jslink` 在浏览器端直接同步控件值，不需要发送消息到 Kernel，响应更快：

```python
# 两个滑块同步
a = IntSlider(description='A')
b = IntSlider(description='B')
jslink((a, 'value'), (b, 'value'))
display(a, b)
```

`link` 是 Python 端同步（经过 Kernel），`jslink` 是 JS 端同步（性能更好但功能有限）。

## 步骤 8：导出交互式 Notebook 为独立应用（Voilà）

安装 Voilà：`pip install voila`

将 Notebook 转为独立 Web 应用（隐藏代码，只显示控件和输出）：

```bash
voila your_notebook.ipynb
```

Voilà 会：
1. 执行 Notebook 中的所有单元格
2. 隐藏代码单元格（只显示 Markdown 和输出）
3. 保留 ipywidgets 交互功能
4. 每个访问者获得独立的 Kernel 实例

## 验证清单

完成本示例后，你应该能够：

- [ ] 使用 `@interact` 快速创建交互式函数
- [ ] 显式创建滑块、按钮、下拉等控件
- [ ] 将控件与数据可视化函数绑定
- [ ] 使用按钮回调和 Output 控件
- [ ] 使用 HBox/VBox/Tab 组织控件布局
- [ ] 理解 `interact`、`interactive` 和手动创建控件的区别
- [ ] 知道 `jslink` 和 `link` 的使用场景

## 常见问题

### 控件不显示/显示为文本

如果控件显示为 `IntSlider(...)` 文本而非交互控件：
1. 确认安装了 `ipywidgets` 和 `jupyterlab_widgets`
2. JupyterLab 用户：`pip install jupyterlab_widgets` 后重启 JupyterLab
3. 经典 Notebook：运行 `jupyter nbextension enable --py widgetsnbextension`
4. 刷新浏览器页面

### 拖动滑块卡顿

使用 `continuous_update=False` 减少更新频率，或使用 `jslink` 做前端联动。

### 图表闪烁

在更新图表时使用 `clear_output(wait=True)` 或固定 Output 控件高度。

## 相关概念

- [交互式控件与富显示](../concepts/09-widgets-display.md) — Widget 架构和富显示原理
- [Kernel 架构](../concepts/06-kernel-architecture.md) — Widget 同步与 Comm 通道
- [Notebook 作为文档与转换](../concepts/10-notebook-doc-convert.md) — Voilà 部署
