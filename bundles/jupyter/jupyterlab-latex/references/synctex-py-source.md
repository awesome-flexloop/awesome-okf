---
type: reference
title: "SyncTeX 同步处理器源码（jupyterlab_latex/synctex.py）"
description: "LatexSynctexHandler 实现编辑器与 PDF 之间的正向/反向同步，parse_synctex_response 解析 SyncTeX 命令行输出"
tags: [synctex, synchronization, forward-search, reverse-search, editor-pdf, parse]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: synctex-py
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/synctex.py"
    title: "jupyterlab_latex/synctex.py"
---

# SyncTeX 同步处理器源码（jupyterlab_latex/synctex.py）

本信源登记 `jupyterlab_latex/synctex.py`（约233行），实现 SyncTeX 双向同步的服务端处理器和响应解析函数。

## LatexSynctexHandler 类

继承自 `jupyter_server.base.handlers.APIHandler`，处理 GET `/latex/synctex/{path}` 请求。

### initialize(root_dir)

设置 `self.root_dir`。

### build_synctex_cmd(base_name, ext)

根据文件扩展名构建 SyncTeX 命令：

| 扩展名 | 方向 | 位置参数 | 构建方法 |
|--------|------|---------|---------|
| `.pdf` | 反向（PDF→编辑器） | page, x, y（query 参数） | `build_synctex_edit_cmd` |
| `.tex` | 正向（编辑器→PDF） | line, column（query 参数） | `build_synctex_view_cmd` |

返回 `(cmd_tuple, pos_dict)`。

### build_synctex_edit_cmd(pdf_name, pos)

反向同步命令：从 PDF 坐标定位到编辑器位置。

```python
(synctex_command, 'edit', '-o', f'{page}:{x}:{y}:{pdf_path}')
```

- pdf_path = `os.path.join(root_dir, pdf_name + '.pdf')`

### build_synctex_view_cmd(tex_name, pos)

正向同步命令：从编辑器行列定位到 PDF 坐标。

```python
(synctex_command, 'view', '-i', f'{line}:{column}:{tex_path}', '-o', f'{pdf_path}')
```

- tex_path = `os.path.join(root_dir, tex_name + '.tex')`
- pdf_path = `os.path.join(root_dir, tex_name + '.pdf')`

### run_synctex(cmd)

`@gen.coroutine` 异步执行 SyncTeX 命令：
- 调用 `run_command(cmd)`
- 返回码非0时设置 500 状态码
- 返回 stdout 输出（字符串）

### get(path='')

`@web.authenticated` + `@gen.coroutine`，主请求处理器：

1. 解析路径：
   - `relative_file_path = str(Path(path.strip('/'))) `
   - `relative_base_path = os.path.splitext(relative_file_path)[0]`
   - `full_file_path = os.path.join(root_dir, relative_file_path)`
   - workdir = 文件所在目录
2. 提取 base_name 和 ext
3. 验证：
   - 文件不存在 → 403
   - `.synctex.gz` 文件不存在 → 403
   - 扩展名不是 `.tex` 或 `.pdf` → 400
4. 调用 `build_synctex_cmd()` 构建命令
5. 执行 `run_synctex()`
6. 用 `parse_synctex_response()` 解析输出
7. 返回 JSON 结果

## parse_synctex_response(response, pos) 函数

解析 SyncTeX 命令行输出为位置字典。

### 解析逻辑

SyncTeX 输出格式：
```
SyncTeX result begin
...
line:123
column:45
page:1
x:123.45
y:678.90
...
SyncTeX result end
```

1. 用正则 `r'SyncTeX result begin\r?\n(.*?)\nSyncTeX result end'`（DOTALL 模式）提取结果块
2. 转为小写、去除空格、按换行分割
3. 按 `:` 分割 key:value
4. 已知字段：`["line", "column", "page", "x", "y"]`
5. 未返回的字段使用输入 pos 中的默认值填充
6. 返回 `{line, column, page, x, y}` 字典

### 异常处理

- 正则匹配失败时抛出 `Exception(f'Unable to parse SyncTeX response: {response}')`

## 位置参数默认值

| 参数 | 来源 | 默认值 |
|------|------|--------|
| page | query string | `'1'` |
| x | query string | `'0'` |
| y | query string | `'0'` |
| line | query string | `'1'` |
| column | query string | `'1'` |

## 依赖导入

```python
from tornado import gen, web
from pathlib import Path
from jupyter_server.base.handlers import APIHandler
from .config import LatexConfig
from .util import run_command
```
