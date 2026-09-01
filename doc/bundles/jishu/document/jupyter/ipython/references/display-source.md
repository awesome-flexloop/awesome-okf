---
type: Reference
title: Display System API 参考
description: IPython 显示系统完整 API 参考，包括 DisplayFormatter 格式化器、DisplayObject 显示对象体系、DisplayPublisher 发布器、DisplayHook 显示钩子和公共显示函数
tags: [api, display, formatter, mimetype, reference, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ipython-formatters
    resource: /references/display-source.md
    title: IPython/core/formatters.py DisplayFormatter & Formatter Classes
  - id: ipython-display
    resource: /references/display-source.md
    title: IPython/core/display.py DisplayObject Hierarchy
  - id: ipython-display-functions
    resource: /references/display-source.md
    title: IPython/core/display_functions.py Public Display Functions
  - id: ipython-displaypub
    resource: /references/display-source.md
    title: IPython/core/displaypub.py DisplayPublisher
  - id: ipython-displayhook
    resource: /references/display-source.md
    title: IPython/core/displayhook.py DisplayHook
---

# Display System API 参考

IPython 显示系统由五大组件构成：DisplayFormatter（格式化器）、DisplayObject 体系（显示对象）、DisplayPublisher（发布器）、DisplayHook（sys.displayhook 实现）和公共显示函数。定义在 `IPython/core/` 目录下。

---

## DisplayFormatter

### 类定义

```python
class DisplayFormatter(Configurable):
    """返回对象的 MIME 格式数据字典"""
```

定义在 `IPython/core/formatters.py`，是所有格式化器的容器和调度中心。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `active_types` | List(Unicode) | 当前激活的 MIME 类型白名单 |
| `formatters` | Dict | MIME type → BaseFormatter 子类实例的映射 |
| `ipython_display_formatter` | IPythonDisplayFormatter | 最高优先级的自显示格式化器 |
| `mimebundle_formatter` | MimeBundleFormatter | MIME bundle 格式化器 |

### 默认格式化器

`formatters` 字典默认包含 10 个格式化器：

| MIME 类型 | 格式化器类 | print_method |
|-----------|-----------|-------------|
| `text/plain` | PlainTextFormatter | `_repr_pretty_` |
| `text/html` | HTMLFormatter | `_repr_html_` |
| `text/markdown` | MarkdownFormatter | `_repr_markdown_` |
| `image/svg+xml` | SVGFormatter | `_repr_svg_` |
| `image/png` | PNGFormatter | `_repr_png_` |
| `application/pdf` | PDFFormatter | `_repr_pdf_` |
| `image/jpeg` | JPEGFormatter | `_repr_jpeg_` |
| `text/latex` | LatexFormatter | `_repr_latex_` |
| `application/json` | JSONFormatter | `_repr_json_` |
| `application/javascript` | JavascriptFormatter | `_repr_javascript_` |

### 核心方法

#### format()

```python
def format(self, obj, include=None, exclude=None):
    """返回对象的格式数据字典和元数据字典

    Parameters
    ----------
    obj : object
        要格式化的 Python 对象
    include : list/tuple/set, optional
        白名单：仅包含这些 MIME 类型
    exclude : list/tuple/set, optional
        黑名单：排除这些 MIME 类型（优先级高于 include）

    Returns
    -------
    (format_dict, metadata_dict) : tuple(dict, dict)
        format_dict: {mimetype: data} 格式数据
        metadata_dict: {mimetype: metadata} 元数据
    """
```

格式化优先级：
1. `ipython_display_formatter`（`_ipython_display_`）—— 若触发，直接返回空
2. `mimebundle_formatter`（`_repr_mimebundle_`）—— 批量获取所有 MIME
3. 各独立 formatter（用户注册的 type_printers 优先于对象的 `_repr_*_` 方法）

#### format_types 属性

```python
@property
def format_types(self):
    """返回所有激活格式化器的 MIME 类型列表"""
    return list(self.formatters.keys())
```

---

## BaseFormatter

### 类定义

```python
class BaseFormatter(Configurable):
    """可配置的格式化器基类"""
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `format_type` | Unicode | 该格式化器的 MIME 类型 |
| `enabled` | Bool | 是否启用 |
| `print_method` | ObjectName | 对象上查找的格式化方法名 |
| `singleton_printers` | Dict | 单例对象 id → 格式化函数 |
| `type_printers` | Dict | 类型对象 → 格式化函数 |
| `deferred_printers` | Dict | (module, name) 元组 → 格式化函数（延迟加载） |

### 格式化查找优先级

1. **singleton_printers** — 按对象 id 查找（用于 None、True、False 等单例）
2. **type_printers** — 按对象类型在 MRO 中查找
3. **deferred_printers** — 按 `(module, classname)` 延迟查找（首次命中后移至 type_printers）
4. **print_method** — 对象自身的 `_repr_*_` 方法

### 核心方法

#### for_type()

```python
def for_type(self, typ, func=None):
    """为指定类型注册格式化函数

    Parameters
    ----------
    typ : type 或 str
        类型对象，或 'module.ClassName' 字符串
    func : callable, optional
        格式化函数；若为 None 则仅查询当前值

    Returns
    -------
    oldfunc : callable 或 None
        之前注册的函数（可用于恢复）
    """
```

#### for_type_by_name()

```python
def for_type_by_name(self, type_module, type_name, func=None):
    """按模块名和类名延迟注册格式化函数

    Parameters
    ----------
    type_module : str
        模块名（如 'numpy'）
    type_name : str
        类名（如 'ndarray'）
    func : callable, optional
        格式化函数
    """
```

#### pop()

```python
def pop(self, typ, default=_raise_key_error):
    """移除并返回指定类型的格式化函数"""
```

#### lookup() / lookup_by_type()

```python
def lookup(self, obj):
    """查找对象实例对应的格式化函数，找不到则抛 KeyError"""

def lookup_by_type(self, typ):
    """查找类型对应的格式化函数，找不到则抛 KeyError"""
```

---

## 各具体 Formatter 类

### PlainTextFormatter

```python
class PlainTextFormatter(BaseFormatter):
    """默认的美化打印机，使用 IPython.lib.pretty"""
    format_type = 'text/plain'
    print_method = '_repr_pretty_'
    pprint = Bool(True)           # 是否启用美化打印
    max_width = Integer(79)       # 最大宽度
    max_seq_length = Integer(pretty.MAX_SEQ_LENGTH)  # 集合截断长度
    verbose = Bool(False)         # 详细模式
    newline = Unicode('\n')       # 换行符
    float_precision = CUnicode('')  # 浮点数精度（可通过 %precision 设置）
```

### HTMLFormatter

```python
class HTMLFormatter(BaseFormatter):
    """HTML 格式化器，返回不含 <html>/<body> 的 HTML 片段"""
    format_type = 'text/html'
    print_method = '_repr_html_'
```

### MarkdownFormatter

```python
class MarkdownFormatter(BaseFormatter):
    """Markdown 格式化器"""
    format_type = 'text/markdown'
    print_method = '_repr_markdown_'
```

### SVGFormatter

```python
class SVGFormatter(BaseFormatter):
    """SVG 格式化器，返回包含 <svg> 标签的原始数据"""
    format_type = 'image/svg+xml'
    print_method = '_repr_svg_'
```

### PNGFormatter / JPEGFormatter / PDFFormatter

```python
class PNGFormatter(BaseFormatter):
    format_type = 'image/png'
    print_method = '_repr_png_'
    _return_type = (bytes, str)  # 返回原始 PNG 字节数据（非 base64）

class JPEGFormatter(BaseFormatter):
    format_type = 'image/jpeg'
    print_method = '_repr_jpeg_'
    _return_type = (bytes, str)

class PDFFormatter(BaseFormatter):
    format_type = 'application/pdf'
    print_method = '_repr_pdf_'
    _return_type = (bytes, str)
```

### LatexFormatter

```python
class LatexFormatter(BaseFormatter):
    """LaTeX 格式化器，返回 $...$ 或 $$...$$ 包裹的公式"""
    format_type = 'text/latex'
    print_method = '_repr_latex_'
```

### JSONFormatter

```python
class JSONFormatter(BaseFormatter):
    """JSON 格式化器，必须返回 dict 或 list（不允许标量）"""
    format_type = 'application/json'
    print_method = '_repr_json_'
    _return_type = (list, dict)
```

### JavascriptFormatter

```python
class JavascriptFormatter(BaseFormatter):
    """JavaScript 格式化器，返回不含 <script> 标签的 JS 代码"""
    format_type = 'application/javascript'
    print_method = '_repr_javascript_'
```

### IPythonDisplayFormatter

```python
class IPythonDisplayFormatter(BaseFormatter):
    """最高优先级的转义格式化器

    对象定义 _ipython_display_ 方法时，该方法直接调用 display() 自行显示，
    其他所有格式化器都不会被调用。适用于需要多次 display 调用的复杂对象。
    """
    print_method = '_ipython_display_'
    _return_type = (type(None), bool)
```

### MimeBundleFormatter

```python
class MimeBundleFormatter(BaseFormatter):
    """MIME bundle 格式化器（IPython 6.1+）

    _repr_mimebundle_(include=None, exclude=None) 返回:
    - dict: {mimetype: data}
    - tuple: (data_dict, metadata_dict)
    """
    print_method = '_repr_mimebundle_'
    _return_type = dict
```

### 注册自定义 Formatter 示例

```python
from IPython.core.formatters import BaseFormatter

class LLMFormatter(BaseFormatter):
    format_type = 'x-vendor/llm'
    print_method = '_repr_llm_'
    _return_type = (dict, str)

ip = get_ipython()
llm_fmt = LLMFormatter(parent=ip.display_formatter)
ip.display_formatter.formatters['x-vendor/llm'] = llm_fmt

# 为已有类型注册格式化函数
def format_int_for_llm(obj):
    return f'This is integer {obj}'

llm_fmt.for_type(int, format_int_for_llm)
```

---

## DisplayObject 类体系

### 继承关系

```
DisplayObject
├── TextDisplayObject
│   ├── Pretty          (text/plain via _repr_pretty_)
│   ├── HTML            (text/html via _repr_html_)
│   ├── Markdown        (text/markdown via _repr_markdown_)
│   ├── Math            (text/latex via _repr_latex_, wrapped in $...$)
│   ├── Latex           (text/latex via _repr_latex_)
│   └── Javascript      (application/javascript via _repr_javascript_)
├── SVG                 (image/svg+xml via _repr_svg_)
├── ProgressBar         (text/html progress 元素)
├── JSON                (application/json via _repr_json_)
│   └── GeoJSON         (application/geo+json via _ipython_display_)
├── Image               (image/png/jpeg/gif/webp)
└── Video               (HTML5 <video> 元素)
```

### DisplayObject 基类

```python
class DisplayObject:
    """封装待显示数据的基类"""

    def __init__(self, data=None, url=None, filename=None, metadata=None):
        """
        Parameters
        ----------
        data : str/bytes/Path
            原始数据，或 URL/文件路径（自动识别）
        url : str
            远程 URL
        filename : str
            本地文件路径
        metadata : dict
            关联的元数据
        """
```

#### 核心方法

| 方法 | 说明 |
|------|------|
| `reload()` | 从文件或 URL 重新加载数据（支持 gzip 编码） |
| `_check_data()` | 子类覆盖，校验数据类型 |
| `_data_and_metadata()` | 返回 (data, metadata) 或 data |

### TextDisplayObject

```python
class TextDisplayObject(DisplayObject):
    """文本型显示对象基类，要求 data 为 str"""
    def _check_data(self):
        if self.data is not None and not isinstance(self.data, str):
            raise TypeError(f"{self.__class__.__name__} expects text")
```

### HTML

```python
class HTML(TextDisplayObject):
    """HTML 显示对象

    示例:
        HTML('<b>Hello</b>')
        HTML(filename='report.html')
        HTML(url='https://example.com/widget.html')
    """
    def _repr_html_(self):
        return self._data_and_metadata()

    def __html__(self):
        """供 Markupsafe 等库识别，避免转义"""
        return self._repr_html_()
```

> ⚠️ 若 data 以 `<iframe` 开头，会发出警告建议使用 IFrame。

### Markdown

```python
class Markdown(TextDisplayObject):
    """Markdown 显示对象"""
    def _repr_markdown_(self):
        return self._data_and_metadata()
```

### Math / Latex

```python
class Math(TextDisplayObject):
    """行内数学公式，自动包裹 $\\displaystyle ...$"""
    def _repr_latex_(self):
        s = r"$\displaystyle %s$" % self.data.strip('$')
        return self._data_and_metadata() if self.metadata else s

class Latex(TextDisplayObject):
    """LaTeX 块（原样输出，由调用者自行包裹 $/$$）"""
    def _repr_latex_(self):
        return self._data_and_metadata()
```

### SVG

```python
class SVG(DisplayObject):
    """SVG 矢量图像，自动从 XML 中提取 <svg> 标签"""
    _read_flags = 'rb'

    @data.setter
    def data(self, svg):
        # 使用 minidom 解析并提取 <svg> 标签
        from xml.dom import minidom
        x = minidom.parseString(svg)
        found_svg = x.getElementsByTagName('svg')
        if found_svg:
            svg = found_svg[0].toxml()
        self._data = svg.decode() if isinstance(svg, bytes) else svg
```

### JSON / GeoJSON

```python
class JSON(DisplayObject):
    """JSON 显示对象（传入 dict/list，不是字符串）"""
    def __init__(self, data=None, url=None, filename=None,
                 expanded=False, metadata=None, root='root', **kwargs):
        """
        expanded : bool — 是否展开 JSON 树
        root : str — 根元素名称
        """

class GeoJSON(JSON):
    """GeoJSON 地图显示对象，通过 _ipython_display_ 输出 application/geo+json"""
    def _ipython_display_(self):
        bundle = {'application/geo+json': self.data, 'text/plain': '<GeoJSON object>'}
        metadata = {'application/geo+json': self.metadata}
        display(bundle, metadata=metadata, raw=True)
```

### Javascript

```python
class Javascript(TextDisplayObject):
    """JavaScript 代码显示对象"""
    def __init__(self, data=None, url=None, filename=None, lib=None, css=None):
        """
        lib : list/str — 前置加载的 JS 库 URL 列表
        css : list/str — 前置加载的 CSS 文件 URL 列表

        在 Notebook 中，`element` 变量指向输出区域的 DOM 容器，jQuery 可用。
        """

    def _repr_javascript_(self):
        # 自动注入 CSS <link> 和 JS <script> 加载器
        r = ''
        for c in self.css:
            r += f'var link=document.createElement("link");...href="{c}";...'
        for l in self.lib:
            r += f'new Promise(function(resolve,reject){{...script.src="{l}"...}}).then(()=>{{'
        r += self.data
        r += '});' * len(self.lib)
        return r
```

### Image

```python
class Image(DisplayObject):
    """PNG/JPEG/GIF/WEBP 图像显示对象

    支持格式: png, jpeg/jpg, gif, webp（通过 ImageFormat 枚举自动检测）
    """
    _read_flags = "rb"

    def __init__(self, data=None, url=None, filename=None, format=None,
                 embed=None, width=None, height=None, retina=False,
                 unconfined=False, metadata=None, alt=None):
        """
        Parameters
        ----------
        data : bytes/str/Path — 原始图像数据/URL/文件路径
        url : str — 远程图像 URL（embed=False 时仅生成 <img> 标签）
        filename : str — 本地文件路径（总是嵌入）
        format : str — 图像格式 (png/jpeg/jpg/gif/webp)
        embed : bool — 是否 base64 嵌入（url= 时默认 False，否则默认 True）
        width/height : int — HTML 显示尺寸（像素）
        retina : bool — 自动宽高减半（Retina 屏支持）
        unconfined : bool — 禁用 max-width 限制
        alt : str — 无障碍替代文本
        """

    def _repr_mimebundle_(self, include=None, exclude=None):
        if self.embed:
            return {self._mimetype: b64_data}, {self._mimetype: metadata}
        else:
            return {'text/html': self._repr_html_()}
```

### Video

```python
class Video(DisplayObject):
    """HTML5 视频显示对象"""
    def __init__(self, data=None, url=None, filename=None, embed=False,
                 mimetype=None, width=None, height=None,
                 html_attributes="controls"):
        """
        embed : bool — 是否 base64 嵌入（默认 False，视频较大时不推荐）
        mimetype : str — 嵌入式视频的 MIME 类型
        html_attributes : str — <video> 标签属性，默认 "controls"
            示例: "controls muted autoplay", "loop autoplay"
        """
```

### ProgressBar

```python
class ProgressBar(DisplayObject):
    """进度条显示对象，支持迭代更新"""
    def __init__(self, total):
        """total: 进度条最大值"""

    def display(self):
        """首次显示"""

    def update(self):
        """更新已有显示（通过 display_id 机制）"""

    def __iter__(self):
        """可迭代：for i in ProgressBar(100): ..."""

    @property
    def progress(self): ...
    @progress.setter
    def progress(self, value):
        """设置进度值时自动 update()"""
```

### IFrame

```python
class IFrame:
    """通用 iframe 嵌入（定义在 IPython.lib.display）"""
    def __init__(self, src, width, height, extras=None, **kwargs):
        """
        src : str — iframe 源 URL
        width/height : int — 尺寸
        extras : list[str] — 额外属性
        **kwargs — URL 查询参数
        """
    def _repr_html_(self): ...
```

---

## DisplayPublisher

### 类定义

```python
class DisplayPublisher(Configurable):
    """将显示数据发布到前端的可配置类"""
```

定义在 `IPython/core/displaypub.py`。

### 核心方法

#### publish()

```python
def publish(self, data, metadata=None, source=_sentinel, *,
            transient=None, update=False, **kwargs) -> None:
    """发布数据和元数据到所有前端

    Parameters
    ----------
    data : dict — {mimetype: data} MIME 字典
    metadata : dict — {mimetype: metadata} 元数据字典
    transient : dict, keyword-only — 临时数据（如 display_id），不持久化
    update : bool, keyword-only — True 时更新已有同 display_id 输出
    source : str — 已废弃（IPython 3.0 起，9.0 开始警告）
    """
```

发布逻辑：
1. 若注册了 `mime_renderers`，调用匹配的处理器
2. 将输出记录到 `history_manager.outputs`
3. 默认回退：打印 `text/plain` 内容

#### clear_output()

```python
def clear_output(self, wait=False):
    """清除当前输出区域

    wait : bool — True 时等待新输出可用后再清除（避免闪烁）
    """
```

### CapturingDisplayPublisher

```python
class CapturingDisplayPublisher(DisplayPublisher):
    """捕获显示输出的发布器（用于测试和内核捕获）"""
    outputs = List()  # 存储所有发布的 {data, metadata, transient, update}

    def publish(self, data, metadata=None, source=None, *, transient=None, update=False):
        self.outputs.append({
            "data": data, "metadata": metadata,
            "transient": transient, "update": update
        })
```

---

## DisplayHook

### 类定义

```python
class DisplayHook(Configurable):
    """IPython 的 sys.displayhook 实现

    用户代码返回值时自动调用，负责格式化输出、缓存结果、写入历史
    """
```

定义在 `IPython/core/displayhook.py`。

### 核心属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `shell` | InteractiveShell | None | 关联的 Shell 实例 |
| `exec_result` | ExecutionResult | None | 当前执行结果对象 |
| `cache_size` | int | 1000 | 输出缓存大小（_1, _2, ...） |
| `cull_fraction` | Float | 0.2 | 缓存满时淘汰比例 |
| `do_full_cache` | bool | 1 | 是否启用完整缓存 |

### __call__ 执行流程

```python
def __call__(self, result=None):
    self.check_for_underscore()          # 1. 检查用户是否手动设置了 _
    if result is not None and not self.quiet():  # 2. 检查行尾分号静默
        self.start_displayhook()         # 3. 标记激活状态
        self.write_output_prompt()       # 4. 写入 Out[n]: 提示符
        format_dict, md_dict = self.compute_format_data(result)  # 5. 格式化
        self.update_user_ns(result)      # 6. 更新 _, __, ___, _oh, _n
        self.fill_exec_result(result)    # 7. 填充执行结果
        if format_dict:
            self.write_format_data(format_dict, md_dict)  # 8. 写入输出
            self.log_output(format_dict) # 9. 记录到历史
        self.finish_displayhook()        # 10. 结束
```

### 关键方法

#### quiet()

```python
def quiet(self):
    """检测输入是否以 ';' 结尾，是则静默输出"""
```

使用 `tokenize` 模块解析，跳过注释和空行后检查最后一个 token 是否为 `;`。

#### compute_format_data()

```python
def compute_format_data(self, result):
    """调用 display_formatter.format() 计算 MIME 数据"""
    return self.shell.display_formatter.format(result)
```

#### write_format_data()

```python
def write_format_data(self, format_dict, md_dict=None):
    """默认实现：将 text/plain 写入 sys.stdout

    多行输出时自动在前面添加换行，对齐到输出区域左边界
    """
```

#### update_user_ns()

```python
def update_user_ns(self, result):
    """更新用户命名空间:
    - _ = result（最近结果）
    - __ = 上一个 _
    - ___ = 上一个 __
    - _N = result（按执行编号，_1, _2, ...）
    - _oh[N] = result（Out 字典）
    """
```

#### cull_cache()

```python
def cull_cache(self):
    """缓存满时淘汰最旧的 cull_fraction（默认20%）条记录"""
```

#### flush()

```python
def flush(self):
    """清空所有输出缓存，删除 _1, _2, ... 变量，回收 GC"""
```

### CapturingDisplayHook

```python
class CapturingDisplayHook:
    """捕获显示钩子（用于测试和单元格捕获）"""
    def __init__(self, shell, outputs=None):
        self.outputs = outputs or []

    def __call__(self, result=None):
        if result is None:
            return
        format_dict, md_dict = self.shell.display_formatter.format(result)
        self.outputs.append({'data': format_dict, 'metadata': md_dict})
```

---

## 公共显示函数

定义在 `IPython/core/display_functions.py`，通过 `IPython.display` 模块导出。

### display()

```python
def display(
    *objs,
    include=None, exclude=None, metadata=None,
    transient=None, display_id=None,
    raw=False, clear=False, **kwargs,
):
    """在所有前端显示 Python 对象

    Parameters
    ----------
    *objs — 要显示的对象（可变参数）
    raw : bool — objs 是否已为 {mimetype: data} 原始字典
    include : list — MIME 类型白名单
    exclude : list — MIME 类型黑名单
    metadata : dict — 附加元数据（合并优先级高于对象自身的 metadata）
    transient : dict — 临时数据（不保存到 notebook）
    display_id : str/bool — 显示区域 ID；True 自动生成；用于 update_display
    clear : bool — 显示前先清除输出区域

    Returns
    -------
    DisplayHandle 或 None — 指定 display_id 时返回句柄
    """
```

使用示例：
```python
from IPython.display import display, HTML, Markdown

# 显示多个对象
display(HTML('<b>Hello</b>'), Markdown('# Title'))

# 只显示 HTML 表示
display(obj, include=['text/html'])

# 带 display_id 的可更新显示
handle = display('Loading...', display_id='progress')
handle.update('Done!')
```

### update_display()

```python
def update_display(obj, *, display_id, **kwargs):
    """更新已存在的显示区域

    Parameters
    ----------
    obj — 新的显示对象
    display_id : str — 目标显示区域 ID（keyword-only）
    """
```

### clear_output()

```python
def clear_output(wait=False):
    """清除当前单元格输出

    wait : bool — True 时等待新输出再清除，避免闪烁
    """
```

### publish_display_data()

```python
def publish_display_data(data, metadata=None, *, transient=None, **kwargs):
    """直接发布原始 MIME 数据（底层函数）

    Parameters
    ----------
    data : dict — {mimetype: data}
    metadata : dict — {mimetype: metadata}
    transient : dict — 临时数据（如 display_id）
    """
```

### DisplayHandle

```python
class DisplayHandle:
    """可更新显示区域的句柄"""

    def __init__(self, display_id=None):
        """display_id 为 None 时自动生成随机 ID"""

    def display(self, obj, **kwargs):
        """创建新显示并更新已有同 ID 实例"""

    def update(self, obj, **kwargs):
        """仅更新已有同 ID 实例"""
```

### 便捷 display_* 函数

定义在 `IPython/core/display.py`：

| 函数 | MIME 类型 | 说明 |
|------|-----------|------|
| `display_pretty(*objs, raw=False, metadata=None)` | text/plain | 显示美化文本 |
| `display_html(*objs, raw=False, metadata=None)` | text/html | 显示 HTML |
| `display_markdown(*objs, raw=False, metadata=None)` | text/markdown | 显示 Markdown |
| `display_svg(*objs, raw=False, metadata=None)` | image/svg+xml | 显示 SVG |
| `display_png(*objs, raw=False, metadata=None)` | image/png | 显示 PNG |
| `display_jpeg(*objs, raw=False, metadata=None)` | image/jpeg | 显示 JPEG |
| `display_webp(*objs, raw=False, metadata=None)` | image/webp | 显示 WEBP |
| `display_latex(*objs, raw=False, metadata=None)` | text/latex | 显示 LaTeX |
| `display_json(*objs, raw=False, metadata=None)` | application/json | 显示 JSON |
| `display_javascript(*objs, raw=False, metadata=None)` | application/javascript | 显示 JavaScript |
| `display_pdf(*objs, raw=False, metadata=None)` | application/pdf | 显示 PDF |

---

## ImageFormat 枚举

```python
class ImageFormat(Enum):
    """图像格式自动检测枚举"""
    png  = (b"\x89PNG\r\n\x1a\n",), _pngxy
    jpeg = (b"\xff\xd8",), _jpegxy
    jpg  = jpeg  # 别名
    gif  = (b"GIF87a", b"GIF89a"), _gifxy
    webp = (b"WEBP",), _webpxy

    @property
    def mime_type(self): return f"image/{self.name}"

    @classmethod
    def from_data(cls, data: bytes) -> Self | None:
        """通过文件头魔数检测图像格式"""
```

---

## 辅助函数

### format_display_data()

```python
def format_display_data(obj, include=None, exclude=None):
    """便捷函数：获取对象的 MIME 格式数据（自动获取 InteractiveShell 实例）"""
    from .interactiveshell import InteractiveShell
    return InteractiveShell.instance().display_formatter.format(obj, include, exclude)
```

### catch_format_error 装饰器

```python
def catch_format_error(method):
    """格式化方法错误捕获装饰器

    NotImplementedError → 返回 None
    其他异常 → 显示 traceback 并返回 None
    """
```

---

## 相关概念

- **MIME 表示协议**：`_repr_*_` 方法命名约定与返回值规范
- **显示系统架构**：Formatter → Publisher → Frontend 数据流
- **[InteractiveShell](interactiveshell-source.md)**：Shell 中 display_formatter/display_pub/displayhook 的初始化
- **[魔法命令](magic-source.md)**：`%precision` 等控制显示行为的魔法命令
