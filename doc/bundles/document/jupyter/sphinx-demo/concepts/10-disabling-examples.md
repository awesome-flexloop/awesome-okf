---
type: Concept
title: 禁用交互示例的三级控制
description: 全局开关、页面级排除、函数级禁用三种控制 TryExamples 按钮显示的方式与适用场景
tags: [try-examples, disable, control, granularity, ignore_patterns]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: disabling
    resource: /references/conf-py-source.md
    title: 禁用示例代码与配置
---

## 为什么需要禁用

并非所有代码示例都适合在浏览器中运行。以下场景需要禁用 TryExamples：

- 示例依赖本地文件系统（`open("file.txt")`）
- 示例需要长时间计算（浏览器 WASM 性能有限）
- 示例涉及网络请求（CORS 限制）
- 示例使用了浏览器中不可用的系统 API
- API 页面不应显示交互按钮（如内部接口文档）

jupyterlite-sphinx 提供了从粗到细的三级控制机制。

## Level 1：全局开关

在 conf.py 中设置：

```python
global_enable_try_examples = False
```

关闭后，autodoc 不会自动为 docstring Examples 节插入 TryExamples 按钮。如需在特定位置使用，必须手动添加 `.. try_examples::` 指令：

```rst
.. automodule:: mymodule
   :members:

手动启用特定示例：

.. code-block:: python

    >>> 2 + 2
    4

.. try_examples::
   :button_text: 运行这段代码
```

**适用场景**：大部分文档不需要交互按钮，只在少数教程页面使用。

## Level 2：页面级排除

在 try_examples.json 中配置 `ignore_patterns`：

```json
{
  "global_min_height": "400px",
  "ignore_patterns": [
    "disabled_examples\\/demo.html",
    "api\\/internal\\/.*",
    "changelog\\.html"
  ]
}
```

### 正则匹配规则

- 匹配目标是页面的 URL 路径（相对于站点根），如 `disabled_examples/demo.html`
- 使用标准 JavaScript 正则语法
- `.` 匹配任意字符，需要用 `\\.` 匹配字面量点号
- `/` 在 JSON 字符串中需要写为 `\\/`
- 多个模式之间是"或"关系，匹配任一即排除

### 常用模式示例

```json
{
  "ignore_patterns": [
    "disabled_examples\\/demo\\.html",
    "api\\/.*",
    ".*\\-draft\\.html",
    "changelog\\.html$"
  ]
}
```

| 模式 | 效果 |
|------|------|
| `"api\\/.*"` | 排除 /api/ 下所有页面 |
| `".*\\-draft\\.html"` | 排除所有以 `-draft.html` 结尾的页面 |
| `"changelog\\.html$"` | 排除 changelog.html（$ 表示结尾匹配） |

**适用场景**：整个页面或一整组页面不需要交互按钮（如 API 参考页、更新日志）。

> **热更新提示**：try_examples.json 修改后不需要重新构建 Sphinx 文档，直接部署或刷新页面即可生效。

## Level 3：函数级禁用

在特定函数的 docstring 中添加 `.. disable_try_examples` 注释：

```python
def load_and_process_data(filepath):
    """Load data from a file and process it.

    Parameters
    ----------
    filepath : str
        Path to the data file.

    Returns
    -------
    dict
        Processed data.

    Examples
    --------
    .. disable_try_examples

    >>> data = load_and_process_data("local_data.csv")  # 依赖本地文件
    >>> data["summary"]
    """
    with open(filepath) as f:
        # 处理逻辑
        pass
```

### 语法要点

- `.. disable_try_examples` 写在 Examples 节内部，在示例代码之前
- 这是一个 RST 注释，不是指令（**不要**写成 `.. disable_try_examples::`）
- 它在渲染后的文档中不可见——读者看不到任何禁用标记
- 仅对所在函数/方法的 Examples 节生效，不影响其他函数

**适用场景**：页面上大部分示例可以交互，但个别函数的示例因依赖本地文件/系统调用等原因不能运行。

### demo 中的实际案例

`example.py` 的 `image_processing` 函数使用了函数级禁用：

```python
def image_processing(image_path):
    """...
    Examples
    --------
    .. disable_try_examples

    >>> img = Image.open("example.jpg")
    >>> processed = image_processing("example.jpg")
    """
```

该示例依赖 Pillow 的 Image.open 和本地图片文件，不适合在浏览器中运行。

`disabled_examples/disabled_example.py` 中的函数也使用了 `.. disable_try_examples`，同时该页面还被 `ignore_patterns` 排除——这是双重保险。

## 三级控制的选择指南

```
需要禁用 TryExamples？
│
├─ 整个站点都不需要 → Level 1: global_enable_try_examples = False
│
├─ 某类/某组页面不需要 → Level 2: ignore_patterns 正则排除
│
├─ 个别函数不适合交互 → Level 3: docstring 中加 .. disable_try_examples
│
└─ 多层组合使用（如全局开启+某些页面排除+个别函数禁用）→ demo 的做法
```

## 组合使用最佳实践

demo 同时使用了三级控制，形成防御性配置：

1. **Level 1**：`global_enable_try_examples = True`（全局开启，最大化交互性）
2. **Level 2**：`ignore_patterns: ["disabled_examples\\/demo.html"]`（排除专门展示禁用效果的页面）
3. **Level 3**：在 `image_processing` 等不适合浏览器运行的函数上添加 `.. disable_try_examples`

这种"默认开启+精确排除"的策略比"默认关闭+逐个开启"更适合教程类文档——用户在更多地方能看到交互按钮，同时不适合的示例被精确禁用。

## 手动添加 TryExamples 按钮

即使全局开启，你也可以在没有 autodoc 的位置手动添加 TryExamples 按钮：

````rst
.. code-block:: python

    import numpy as np
    x = np.linspace(0, 2*np.pi, 100)
    plt.plot(x, np.sin(x))

.. try_examples::
   :button_text: 运行这段绘图代码
   :min_height: 500px
````

在 MyST Markdown 中：

````markdown
```{code-cell} python
import numpy as np
x = np.linspace(0, 2*np.pi, 100)
```

```{try_examples}
:button_text: 运行
```
````

## 相关内容

- [06-try-examples](06-try-examples.md)
- [05-config-files](05-config-files.md)
- [/examples/04-matplotlib-notebook.md](../examples/04-matplotlib-notebook.md)
