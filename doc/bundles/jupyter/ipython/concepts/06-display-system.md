---
type: concept
title: "06 - 显示系统"
description: IPython MIME 多模态显示体系——DisplayObject 层次、DisplayPublisher 发布、DisplayFormatter 渲染三层解耦架构
tags: [display, mime, formatter, displayobject, publisher, rich-output]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-formatters
    title: IPython/core/formatters.py
  - id: ipython-display
    title: IPython/core/display.py
  - id: ipython-displaypub
    title: IPython/core/displaypub.py
  - id: ipython-displayhook
    title: IPython/core/displayhook.py
---

## 三层解耦显示架构

IPython 的显示系统基于 MIME 类型实现多态渲染，采用三层解耦设计 [F-380][F-390][F-400]：

```
┌─────────────────────────────────────────────────────────────┐
│ 数据层: DisplayObject                                        │
│                                                             │
│ 封装不同类型的显示数据，知道如何生成自己的 MIME bundle          │
│ DisplayObject → TextDisplayObject → HTML/Markdown/SVG/...    │
│ DisplayObject → Image/Video/JSON/...                        │
│                                                             │
│ 富显示协议: _repr_html_/_repr_svg_/_repr_png_ 等方法          │
└─────────────────────────┬───────────────────────────────────┘
                          │ MIME bundle (data + metadata)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 传输层: DisplayPublisher                                     │
│                                                             │
│ 将 MIME bundle 发布到前端                                      │
│ ├── 终端: 直接写入 stdout（仅消费 text/plain）                 │
│ ├── Jupyter: 通过 ZeroMQ 发送 display_data 消息              │
│ └── CapturingDisplayPublisher: 捕获到列表（%capture）         │
└─────────────────────────┬───────────────────────────────────┘
                          │ 前端选择消费的 MIME 类型
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 渲染层: DisplayFormatter + 12 种 Formatter                   │
│                                                             │
│ 将 Python 对象格式化为各 MIME 类型的表示                       │
│ PlainTextFormatter → text/plain                             │
│ HTMLFormatter → text/html                                   │
│ MarkdownFormatter → text/markdown                           │
│ ...（共 12 种 MIME formatter）                               │
└─────────────────────────────────────────────────────────────┘
```

三层各司其职：DisplayObject 知道"我有什么数据"，DisplayPublisher 知道"数据发给谁"，DisplayFormatter 知道"怎么格式化数据"。

## DisplayObject 类层次

DisplayObject 是所有可显示对象的基类 [F-410]，类层次结构如下：

```
DisplayObject [F-410]
├── TextDisplayObject [F-411]
│   ├── Pretty          ← 格式化文本（pretty printing）
│   ├── HTML            ← HTML 富文本 [F-412]
│   ├── Markdown        ← Markdown 文本 [F-412]
│   ├── Math            ← 数学公式（LaTeX 语法）[F-412]
│   ├── Latex           ← LaTeX 文档 [F-412]
│   ├── SVG             ← SVG 矢量图 [F-412]
│   ├── ProgressBar     ← 进度条 [F-412]
│   └── Javascript      ← JavaScript 代码 [F-412]
├── JSON [F-412]
│   └── GeoJSON         ← 地理 JSON [F-412]
├── Image [F-412]       ← 图片（png/jpeg/svg/pdf）
├── Video [F-412]       ← 视频
└── IFrame              ← 内嵌网页（由 lib.display 提供）
```

### 常用 DisplayObject 示例

```python
from IPython.display import HTML, Markdown, SVG, Image, JSON, Latex, Math, Javascript

# HTML
HTML('<b>粗体文本</b> <a href="https://ipython.org">链接</a>')

# Markdown
Markdown("## 标题\n\n这是 **Markdown** 文本，支持*斜体*和`代码`。")

# SVG
SVG('<svg><circle cx="50" cy="50" r="40" fill="red"/></svg>')

# 图片
Image(filename='chart.png')  # 从文件
Image(url='https://example.com/img.png')  # 从 URL
Image(data=png_bytes, format='png')  # 从字节数据

# LaTeX / Math
Latex(r'\sum_{i=1}^{n} i = \frac{n(n+1)}{2}')
Math(r'\alpha + \beta = \gamma')

# JSON
JSON({'name': 'IPython', 'version': '9.0', 'features': ['magics', 'display']})

# JavaScript
Javascript('alert("Hello from IPython!")')
```

每个 DisplayObject 子类实现了对应 MIME 类型的 `_repr_xxx_()` 方法，例如 `HTML._repr_html_()` 返回 HTML 字符串，`Image._repr_png_()` 返回 PNG 字节数据。

### Image 格式

Image 支持 png、jpeg、svg、pdf 四种格式，由 `ImageFormat` 枚举定义 [F-413]。支持三种数据来源：文件路径、URL、原始数据（bytes）。

## DisplayFormatter 与 12 种 MIME Formatter

`DisplayFormatter` 管理一组 BaseFormatter 实例 [F-380][F-384]，每个 Formatter 负责将 Python 对象格式化为一种 MIME 类型。

### Formatter 类层次

```
FormatterABC（抽象基类）[F-382]
└── BaseFormatter（Configurable + FormatterABC）[F-383]
    ├── PlainTextFormatter     → text/plain [F-384]
    ├── HTMLFormatter          → text/html
    ├── MarkdownFormatter      → text/markdown
    ├── SVGFormatter           → image/svg+xml
    ├── PNGFormatter           → image/png
    ├── JPEGFormatter          → image/jpeg
    ├── LatexFormatter         → text/latex
    ├── JSONFormatter          → application/json
    ├── JavascriptFormatter    → application/javascript
    ├── PDFFormatter           → application/pdf
    ├── IPythonDisplayFormatter → application/x-ipython
    └── MimeBundleFormatter    → 自定义 MIME bundle
```

### Formatter 工作机制

每个 Formatter 维护一个类型注册表，将 Python 类型映射到格式化函数：

```python
# 为自定义类型注册 formatter
ip = get_ipython()
html_formatter = ip.display_formatter.formatters['text/html']

class MyData:
    def __init__(self, value):
        self.value = value

def mydata_to_html(obj):
    return f"<div class='mydata'><b>{obj.value}</b></div>"

html_formatter.for_type(MyData, mydata_to_html)
```

### PlainTextFormatter

PlainTextFormatter 是最基础的 formatter [F-385]，负责 `text/plain` 输出：
- 控制是否使用 pretty printing（`pprint` trait）
- 在终端 IPython 中是唯一默认激活的 formatter（因为终端只支持文本）
- 使用 `IPython.lib.pretty` 库进行结构化格式化

## DisplayPublisher 显示发布器

`DisplayPublisher` 负责将 MIME bundle 发布到前端 [F-390][F-391]：

```python
class DisplayPublisher(Configurable):
    def publish(self, data, metadata=None, source=None, *, 
                transient=None, update=False):
        """发布显示数据到前端 [F-391]
        data: dict, MIME 类型到表示的映射
        metadata: dict, 各 MIME 类型的元数据
        update: bool, 是否更新已有的 display（同 display_id）
        """
        ...
```

终端和 Jupyter 有不同的 Publisher 实现：

- **终端**：将 `text/plain` 数据写入 stdout
- **Jupyter**：将完整 MIME bundle 序列化为 ZeroMQ `display_data` 消息发送给前端
- **CapturingDisplayPublisher**：将发布的数据捕获到列表中，用于 `%capture` 魔法 [F-392]

## DisplayHook 表达式结果显示

`DisplayHook` 实现了 Python 的 `sys.displayhook` 协议 [F-400][F-401]，控制交互式表达式结果的自动显示：

```python
class DisplayHook(Configurable):
    """sys.displayhook 实现"""
    def __call__(self, result=None):
        """当交互输入中表达式产生非 None 结果时被调用"""
        if result is None:
            return
        # 1. 更新 Out[N]、_、__、___
        # 2. 调用 DisplayFormatter 格式化
        # 3. 通过 DisplayPublisher 发布
        # 4. 写入 stdout（终端）
```

`CapturingDisplayHook` 是用于捕获输出的变体，与 `CapturingDisplayPublisher` 配合使用 [F-402]。

## display() 函数与公共 API

顶层 `IPython/display.py` 提供统一的显示公共 API [F-415]：

```python
from IPython.display import (
    display,           # 通用显示函数
    display_pretty,    # 显示 Pretty 对象
    display_html,      # 显示 HTML
    display_markdown,  # 显示 Markdown
    display_svg,       # 显示 SVG
    display_png,       # 显示 PNG 图片
    display_jpeg,      # 显示 JPEG 图片
    display_latex,     # 显示 LaTeX
    display_json,      # 显示 JSON
    display_javascript,# 显示 JavaScript
    display_pdf,       # 显示 PDF
    clear_output,      # 清除当前输出区域
    publish_display_data,  # 底层发布 API
    update_display,    # 更新已显示内容
    DisplayHandle,     # 显示句柄，支持后续更新
    # DisplayObject 类
    DisplayObject, TextDisplayObject,
    Pretty, HTML, Markdown, Math, Latex, SVG,
    Image, Video, JSON, GeoJSON, Javascript, ProgressBar
)
```

### display() 基本用法

```python
from IPython.display import display

# 显示单个对象
display(HTML('<b>Hello</b>'))

# 显示多个对象
display(HTML('<b>Hello</b>'), Markdown('*World*'), Image('img.png'))

# 指定 metadata
display(HTML('<b>Hello</b>'), metadata={'text/html': {'isolated': True}})

# 指定 display_id 用于后续更新
handle = display('Loading...', display_id='my-progress')
handle.update('Done!')  # 更新之前的显示
```

### clear_output() 清除输出

```python
from IPython.display import clear_output

# 清除当前 cell 的所有输出
clear_output()

# wait=True 等待新输出后再清除（避免闪烁）
clear_output(wait=True)
```

### DisplayHandle 更新显示

`DisplayHandle` 持有一个 `display_id` 引用，允许后续更新同一位置的显示内容 [F-414]：

```python
from IPython.display import DisplayHandle, display
import time

handle = display("Starting...", display_id="progress")
for i in range(10):
    time.sleep(0.5)
    handle.update(f"Progress: {i*10}%")
handle.update("Done!")
```

`update_display()` 是 DisplayHandle.update() 的函数式版本。

## 富显示协议（_repr_*_ 方法）

普通 Python 对象不需要继承 DisplayObject 就能被 IPython 富显示——只需实现特定的 `_repr_xxx_()` 方法：

```python
class DataFrame:
    """pandas DataFrame 实现了多个 _repr_*_ 方法"""
    
    def _repr_html_(self):
        """返回 HTML 表格表示（Jupyter 中显示为表格）"""
        return "<table>...</table>"
    
    def _repr_latex_(self):
        """返回 LaTeX 表格表示"""
        return "\\begin{tabular}..."
    
    def _repr_pretty_(self, p, cycle):
        """pretty 格式化（终端中使用）"""
        p.text("...")
    
    # 其他可选方法：
    # _repr_svg_(self) → SVG 字符串
    # _repr_png_(self) → PNG 字节
    # _repr_jpeg_(self) → JPEG 字节
    # _repr_json_(self) → JSON 可序列化对象
    # _repr_javascript_(self) → JavaScript 字符串
    # _repr_mimebundle_(self, include=None, exclude=None) → 完整 MIME bundle dict
```

DisplayFormatter 按 MIME 类型优先级依次调用对象的 `_repr_xxx_()` 方法，前端选择支持的类型进行渲染。终端前端通常只消费 `text/plain`（由 `_repr_pretty_` 或 `__repr__` 提供）。

### _repr_mimebundle_ 高级接口

`_repr_mimebundle_()` 方法允许对象一次性返回多个 MIME 表示，以及 metadata：

```python
class MyRichObject:
    def _repr_mimebundle_(self, include=None, exclude=None):
        data = {
            'text/plain': 'MyRichObject()',
            'text/html': '<div class="my-obj"><b>Rich</b> object</div>',
            'text/markdown': '**Rich** object',
        }
        metadata = {
            'text/html': {'isolated': True},
        }
        return data, metadata
```

## %capture 输出捕获

`%%capture` 单元魔法利用 CapturingDisplayPublisher 和 CapturingDisplayHook 捕获输出 [F-392][F-402]：

```python
%%capture captured
print("This goes to stdout")
print("This goes to stderr")
display(HTML("<b>Captured HTML</b>"))

# captured.stdout → "This goes to stdout\n"
# captured.stderr → "This goes to stderr\n"
# captured.outputs → [DisplayObject 列表]
captured.show()  # 重新显示捕获的内容
```

## 终端 vs Jupyter 显示差异

| 特性 | IPython 终端 | Jupyter 前端 |
|------|-------------|-------------|
| **MIME 类型** | 仅 text/plain | 完整 MIME bundle |
| **HTML/Markdown** | 显示源码或纯文本 | 渲染为富文本 |
| **图片** | 不支持（终端特殊处理） | 内联显示 |
| **JavaScript** | 不执行 | 执行 |
| **display()** | text/plain 写入 stdout | 发送 display_data 消息 |
| **clear_output()** | 终端清屏 | 清除 cell 输出 |
| **update_display()** | 不支持 | 更新指定 display_id 的输出 |

## 相关概念

- [代码执行管线](/concepts/05-execution-pipeline.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [事件与钩子](/concepts/10-events-hooks.md)
- [信源参考 - 显示系统](/references/display-source.md)
