---
type: example
title: "03 - 富文本输出与 display()"
description: 使用 IPython 的富显示系统渲染 HTML、Markdown、SVG、图片、JSON、LaTeX，以及 display_id 更新、clear_output 和富显示协议实战
tags: [example, display, rich-output, html, markdown, svg, image, mime, display-handle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-display
    title: IPython/core/display.py
  - id: ipython-formatters
    title: IPython/core/formatters.py
  - id: ipython-displaypub
    title: IPython/core/displaypub.py
  - id: ipython-displayhook
    title: IPython/core/displayhook.py
related_concepts: [/concepts/06-display-system.md]
---

## 目标

本示例演示 IPython 的 MIME 富显示系统，覆盖以下内容：

1. 使用 `display()` 函数显示 HTML、Markdown、SVG、Image、JSON、LaTeX、Math、JavaScript 对象
2. 一次调用 `display()` 显示多个对象
3. 使用 `display_id` 和 `update_display()` / `DisplayHandle` 更新已显示内容
4. 使用 `clear_output()` 清除输出
5. 在自定义类中实现 `_repr_html_`、`_repr_svg_`、`_repr_png_` 等富显示协议方法
6. 使用 `capture_output` 捕获显示输出

## 完整代码

以下代码可直接在 IPython 终端或 Jupyter Notebook 中运行。注意：在终端中，HTML/Markdown/SVG/Image 等富类型会显示为纯文本或源码；在 Jupyter 中会完全渲染。

```python
# ============================================================
# 一、导入 display 相关对象
# ============================================================

from IPython.display import (
    display,
    HTML, Markdown, SVG, Image, JSON, Latex, Math,
    Javascript, Pretty, ProgressBar, Video,
    clear_output, update_display, DisplayHandle,
    publish_display_data,
)

# ============================================================
# 二、基本 DisplayObject 使用
# ============================================================

# --- HTML 渲染 ---
display(HTML('<b>粗体文本</b> <span style="color: red;">红色文字</span>'))
display(HTML('''
<table border="1" style="border-collapse: collapse;">
  <tr><th>名称</th><th>值</th></tr>
  <tr><td>PI</td><td>3.14159</td></tr>
  <tr><td>E</td><td>2.71828</td></tr>
</table>
'''))

# --- Markdown 渲染 ---
display(Markdown('# 一级标题\n\n这是 **Markdown** 文本，支持*斜体*、`代码`和[链接](https://ipython.org)。'))
display(Markdown('''
## 列表示例

- 第一项
- 第二项
  - 嵌套项
- 第三项

> 这是一段引用
'''))

# --- SVG 矢量图 ---
svg_content = '''
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="steelblue"/>
  <rect x="100" y="10" width="80" height="80" fill="coral" rx="5"/>
  <text x="100" y="95" fill="black">SVG!</text>
</svg>
'''
display(SVG(svg_content))

# --- JSON 数据 ---
data = {
    "name": "IPython",
    "version": "9.0",
    "features": ["magics", "display", "autocomplete", "history"],
    "nested": {"key": "value", "numbers": [1, 2, 3]}
}
display(JSON(data))

# --- LaTeX 公式 ---
display(Latex(r'\sum_{i=1}^{n} i = \frac{n(n+1)}{2}'))
display(Math(r'\alpha + \beta = \gamma'))
display(Math(r'\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}'))

# --- JavaScript（仅 Jupyter 环境执行）---
# 在 Jupyter 中会执行 JS，在终端中只显示源码
display(Javascript('console.log("Hello from JavaScript!");'))

# --- Pretty 格式化文本 ---
display(Pretty('普通格式化文本\n支持换行'))

# ============================================================
# 三、图片显示
# ============================================================

# 从文件显示图片（需要文件存在）
# display(Image(filename='chart.png'))

# 从 URL 显示图片
# display(Image(url='https://example.com/image.png'))

# 从原始字节数据显示图片（示例：生成一个简单的 PNG）
import base64
import struct
import zlib

def create_simple_png(width, height, color=(255, 0, 0)):
    """创建一个纯色 PNG 图片的字节数据（用于演示 Image(data=...)）"""
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc
    
    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)
    
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            raw_data += bytes(color)
    
    idat = chunk(b'IDAT', zlib.compress(raw_data))
    iend = chunk(b'IEND', b'')
    
    return signature + ihdr + idat + iend

# 创建并显示一个 50x50 的蓝色方块
png_data = create_simple_png(50, 50, color=(0, 100, 200))
display(Image(data=png_data, format='png'))

# 指定宽度和高度
# display(Image(data=png_data, format='png', width=100, height=100))

# ============================================================
# 四、一次显示多个对象
# ============================================================

# display() 接受多个参数，依次显示
display(
    HTML('<b>多个对象同时显示</b>'),
    Markdown('---\n这是一段 **Markdown**'),
    JSON({"status": "ok", "items": [1, 2, 3]})
)

# ============================================================
# 五、使用 display_id 更新显示内容
# ============================================================

# 方式 1：使用 DisplayHandle
import time

handle = display("准备开始...", display_id="progress-demo")
for i in range(11):
    time.sleep(0.2)
    handle.update(f"进度: {i*10}%")
handle.update(Markdown("**✅ 完成！**"))

# 方式 2：使用 update_display 函数
display("初始化...", display_id="status-bar")
time.sleep(0.3)
update_display("正在加载数据...", display_id="status-bar")
time.sleep(0.3)
update_display(HTML('<span style="color: green;">✓ 加载完成</span>'), display_id="status-bar")

# 方式 3：display() 返回 DisplayHandle
dh = display("Step 1", display_id="steps")
time.sleep(0.2)
dh.update("Step 2")
time.sleep(0.2)
dh.update(DisplayHandle if False else "Step 3")
time.sleep(0.2)
dh.update(HTML("<b>Done!</b>"))

# ============================================================
# 六、clear_output 清除输出
# ============================================================

# 清除当前输出区域
# clear_output()

# wait=True：等待下一个输出到达后再清除，避免闪烁
# 适用于循环中不断更新显示的场景
for i in range(5):
    clear_output(wait=True)
    print(f"Countdown: {5 - i}")
    time.sleep(0.3)
clear_output(wait=True)
print("Go!")

# ============================================================
# 七、富显示协议：自定义类的 _repr_*_ 方法
# ============================================================

class DataReport:
    """一个实现多种富显示协议的自定义类"""
    
    def __init__(self, title, data):
        self.title = title
        self.data = data
    
    def _repr_html_(self):
        """返回 HTML 表示（Jupyter 优先使用）"""
        rows = ""
        for key, value in self.data.items():
            rows += f"<tr><td>{key}</td><td><b>{value}</b></td></tr>"
        return f"""
        <div style="border: 2px solid #4a90d9; border-radius: 8px; padding: 12px; max-width: 400px;">
            <h3 style="margin-top: 0; color: #4a90d9;">{self.title}</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><th style="text-align: left; border-bottom: 1px solid #ddd;">指标</th>
                    <th style="text-align: left; border-bottom: 1px solid #ddd;">值</th></tr>
                {rows}
            </table>
        </div>
        """
    
    def _repr_markdown_(self):
        """返回 Markdown 表示"""
        lines = [f"## {self.title}\n"]
        lines.append("| 指标 | 值 |")
        lines.append("|------|-----|")
        for key, value in self.data.items():
            lines.append(f"| {key} | {value} |")
        return "\n".join(lines)
    
    def _repr_pretty_(self, p, cycle):
        """终端中使用的 pretty 格式化"""
        if cycle:
            p.text(f"{self.title}(...)")
            return
        p.text(f"=== {self.title} ===\n")
        for key, value in self.data.items():
            p.text(f"  {key}: {value}\n")
    
    def _repr_latex_(self):
        """返回 LaTeX 表示"""
        items = " \\\\ ".join(f"{k} = {v}" for k, v in self.data.items())
        return f"\\textbf{{{self.title}}}: {items}"
    
    def __repr__(self):
        return f"DataReport(title={self.title!r}, data={self.data!r})"

# 显示自定义对象（终端使用 _repr_pretty_，Jupyter 优先 _repr_html_）
report = DataReport("模型训练报告", {
    "准确率": "95.2%",
    "损失值": "0.034",
    "训练轮数": 100,
    "批次大小": 32,
})
display(report)

# ============================================================
# 八、_repr_mimebundle_ 高级接口
# ============================================================

class RichObject:
    """通过 _repr_mimebundle_ 一次性提供多种 MIME 表示"""
    
    def __init__(self, text, color="steelblue"):
        self.text = text
        self.color = color
    
    def _repr_mimebundle_(self, include=None, exclude=None):
        data = {
            'text/plain': f'RichObject({self.text!r})',
            'text/html': f'<span style="color: {self.color}; font-weight: bold;">{self.text}</span>',
            'text/markdown': f'**{self.text}**',
        }
        metadata = {
            'text/html': {'isolated': True},
        }
        return data, metadata

display(RichObject("多模态对象", "crimson"))

# ============================================================
# 九、注册自定义 Formatter
# ============================================================

class Metric:
    """指标类，我们将为其注册自定义 HTML formatter"""
    def __init__(self, name, value, unit=""):
        self.name = name
        self.value = value
        self.unit = unit

# 获取 IPython 实例和 HTML formatter
ip = get_ipython()
html_formatter = ip.display_formatter.formatters['text/html']

# 为 Metric 类型注册 HTML 格式化函数
def metric_to_html(metric):
    return (
        f'<div style="display: inline-block; padding: 4px 12px; '
        f'background: #f0f4f8; border-radius: 4px; margin: 2px;">'
        f'<span style="color: #666;">{metric.name}</span>: '
        f'<b style="color: #2d6cb3;">{metric.value}</b> '
        f'<span style="color: #999;">{metric.unit}</span></div>'
    )

html_formatter.for_type(Metric, metric_to_html)

# 现在 Metric 对象会以 HTML 卡片形式显示（Jupyter 中）
m1 = Metric("CPU", "42.5", "%")
m2 = Metric("Memory", "1.2", "GB")
m3 = Metric("Latency", "23", "ms")
display(m1, m2, m3)

# 也可以注册到 text/plain formatter（终端显示）
plain_formatter = ip.display_formatter.formatters['text/plain']
def metric_to_pretty(metric, p, cycle):
    p.text(f"{metric.name}={metric.value}{metric.unit}")
plain_formatter.for_type(Metric, metric_to_pretty)

# ============================================================
# 十、capture_output 捕获输出
# ============================================================

from IPython.utils.capture import capture_output

# 使用上下文管理器捕获 stdout、stderr 和 display 输出
with capture_output() as captured:
    print("这是 stdout 输出")
    import sys
    print("这是 stderr 输出", file=sys.stderr)
    display(HTML("<b>捕获的 HTML</b>"))
    x = 1 + 1
    print(f"计算结果: {x}")

# 访问捕获的内容
print("=== 捕获的 stdout ===")
print(captured.stdout)

print("=== 捕获的 stderr ===")
print(captured.stderr)

print("=== 捕获的 display 输出 ===")
for out in captured.outputs:
    print(f"  输出类型: {type(out).__name__}")
    # 对于 DisplayObject，可以访问其 data 属性
    if hasattr(out, 'data'):
        print(f"  数据: {out.data}")

# 重新显示捕获的内容
captured.show()

# capture_output 也可以不捕获 stdout/stderr，只捕获 display
with capture_output(stdout=False, stderr=False) as cap_display:
    display(Markdown("**只捕获 display 输出**"))
    print("这个 print 不会被捕获")

print(f"捕获了 {len(cap_display.outputs)} 个 display 对象")

# ============================================================
# 十一、ProgressBar 进度条
# ============================================================

# 创建进度条（Jupyter 中显示为小部件，终端中显示文本进度）
from IPython.display import ProgressBar
import time

# 注意：ProgressBar 在终端中效果有限，Jupyter 中效果最佳
# 简单的文本进度条
for i in range(21):
    if i == 0:
        pb = ProgressBar(20)
        pb.display()
    time.sleep(0.05)
    pb.progress = i

# ============================================================
# 十二、publish_display_data 底层 API
# ============================================================

# publish_display_data 是最底层的显示 API，直接发布 MIME bundle
publish_display_data(
    data={
        'text/plain': '底层 API 输出',
        'text/html': '<span style="color: purple;">通过 publish_display_data 发布</span>',
    },
    metadata={
        'text/html': {'isolated': True},
    }
)
```

## 代码解析

### 三层显示架构

IPython 显示系统采用三层解耦设计 [F-380][F-390][F-400]：

1. **数据层（DisplayObject）**：封装显示数据和对应的 MIME 类型。`HTML`、`Markdown`、`SVG`、`Image` 等类知道如何生成自己的 MIME bundle。
2. **传输层（DisplayPublisher）**：通过 `publish()` 方法将 MIME bundle 发送到前端。终端前端只消费 `text/plain`，Jupyter 发送完整 MIME bundle。
3. **渲染层（DisplayFormatter）**：管理 12 种 MIME formatter，将 Python 对象格式化为各 MIME 类型的表示。

### DisplayObject 类层次

所有富显示对象继承自 `DisplayObject` 基类 [F-410]：

```
DisplayObject
├── TextDisplayObject → Pretty、HTML、Markdown、Math、Latex、SVG、ProgressBar、Javascript
├── JSON（含 GeoJSON）
├── Image（png/jpeg/svg/pdf）[F-413]
├── Video
└── IFrame（来自 lib.display）
```

每个子类实现对应的 `_repr_xxx_()` 方法，如 `HTML._repr_html_()` 返回 HTML 字符串，`Image._repr_png_()` 返回 PNG 字节。

### display() 函数

顶层 `display()` 函数是最常用的显示 API [F-415]，它：
- 接受任意数量的位置参数，每个参数都会被单独显示
- 接受 `display_id` 参数，返回 `DisplayHandle` 对象
- 接受 `metadata`、`transient`、`update` 等参数控制发布行为
- 通过 `DisplayPublisher.publish()` 将格式化后的数据发送到前端

### display_id 与更新机制

使用 `display_id` 参数可以为显示内容指定唯一标识 [F-414]，之后通过 `DisplayHandle.update()` 或 `update_display()` 更新同一位置的内容。这在进度显示、动态仪表板等场景非常有用。底层通过 `publish()` 的 `update=True` 参数告知前端更新已有内容而非新增。

### clear_output()

`clear_output()` 清除当前输出区域的所有内容。`wait=True` 参数会延迟清除直到下一个输出到达，避免闪烁，在循环更新场景中推荐使用。

### 富显示协议

普通 Python 对象不需要继承 DisplayObject，只需实现以下 `_repr_xxx_()` 方法即可支持富显示：

| 方法 | MIME 类型 | 返回类型 |
|------|----------|---------|
| `_repr_html_` | text/html | str |
| `_repr_markdown_` | text/markdown | str |
| `_repr_svg_` | image/svg+xml | str |
| `_repr_png_` | image/png | bytes |
| `_repr_jpeg_` | image/jpeg | bytes |
| `_repr_latex_` | text/latex | str |
| `_repr_json_` | application/json | dict |
| `_repr_javascript_` | application/javascript | str |
| `_repr_pretty_(p, cycle)` | text/plain | 通过 p.text() 写入 |
| `_repr_mimebundle_(include, exclude)` | 多 MIME | (data_dict, metadata_dict) |

DisplayFormatter 按优先级依次调用这些方法，前端选择最适合的类型渲染。终端通常只消费 `text/plain`（`_repr_pretty_` 或 `__repr__`）。

### 注册自定义 Formatter

通过 `ip.display_formatter.formatters['mime/type'].for_type(cls, func)` 可以为任意类型注册格式化函数。这比在类上定义 `_repr_xxx_` 方法更灵活——可以为无法修改源码的第三方类添加富显示支持。

### capture_output

`IPython.utils.capture.capture_output` 利用 `CapturingDisplayPublisher` 和 `CapturingDisplayHook` [F-392][F-402] 在上下文管理器中捕获 stdout、stderr 和 display 输出，返回的对象可通过 `.stdout`、`.stderr`、`.outputs` 属性访问，也可通过 `.show()` 重新显示。

### 终端 vs Jupyter 显示差异

| 特性 | IPython 终端 | Jupyter |
|------|-------------|---------|
| HTML/Markdown | 显示源码/纯文本 | 完全渲染 |
| SVG/Image | 不显示图形 | 内联显示 |
| JavaScript | 不执行 | 浏览器执行 |
| update_display | 不支持 | 支持更新 |
| ProgressBar | 文本进度 | Widget 进度条 |

## 常见问题排查

**问题：`display(HTML(...))` 在终端中显示 HTML 源码而非渲染后的页面**

原因：终端 IPython 的 DisplayPublisher 只消费 `text/plain` MIME 类型 [F-390]，无法渲染 HTML。

解决方案：使用 Jupyter Notebook/Lab 以获得完整的富显示体验。终端中可使用 `_repr_pretty_` 方法提供漂亮的文本表示。

**问题：`Image(filename='...')` 报错 "No such file or directory"**

原因：文件路径相对于 IPython 当前工作目录解析，可能与预期目录不一致。

解决方案：使用 `%pwd` 确认当前目录，使用 `%cd` 切换到正确目录，或使用绝对路径。

**问题：`update_display()` 没有更新之前的显示内容**

原因：`display_id` 必须完全匹配，且此功能仅在 Jupyter 环境中有效（终端不支持）。

解决方案：确保 `display_id` 参数一致；在终端环境中不要依赖更新功能，使用 `clear_output(wait=True)` + 重新 `display()` 作为替代。

**问题：自定义类的 `_repr_html_` 方法没有被调用**

原因：DisplayFormatter 按优先级选择 MIME 类型，如果 `_repr_mimebundle_` 存在则优先使用；或者 formatter 被禁用。

解决方案：
1. 确认没有定义 `_repr_mimebundle_` 方法
2. 检查 formatter 是否启用：`get_ipython().display_formatter.formatters['text/html'].enabled`
3. 如果是第三方类，使用 `for_type()` 注册 formatter 而非修改类

**问题：`capture_output` 上下文中的 `print()` 输出仍然显示在终端**

原因：`capture_output` 通过替换 `sys.stdout`/`sys.stderr` 和 DisplayHook 来捕获输出，但某些 C 扩展的输出可能绕过 Python 的 stdout。

解决方案：确保在上下文管理器中执行 Python 级别的输出；对于特殊输出，可结合 `%%capture` 单元魔法使用。

## 相关概念

- [显示系统](/concepts/06-display-system.md)
- [代码执行管线](/concepts/05-execution-pipeline.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [信源参考 - 显示系统](/references/display-source.md)
