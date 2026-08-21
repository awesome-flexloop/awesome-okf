---
type: Reference
title: "v4 Notebook构造API源码"
description: "nbformat/v4/nbbase.py中的new_notebook/new_code_cell/new_markdown_cell/new_raw_cell/new_output等工厂函数源码"
tags: [v4, factory, new-notebook, new-cell, new-output, cell-id]
sources:
  - id: v4-nbbase
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/v4/nbbase.py"
    title: "nbformat/v4/nbbase.py"
  - id: v4-rwbase
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/v4/rwbase.py"
    title: "nbformat/v4/rwbase.py"
  - id: v4-nbjson
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/v4/nbjson.py"
    title: "nbformat/v4/nbjson.py"
generated: { by: "reference_agent/trae-cn", status: "stable", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# v4 Notebook构造API源码

## v4版本常量

```python
nbformat = 4
nbformat_minor = 5

nbformat_schema = {
    (None, None): "nbformat.v4.schema.json",
    (4, 0): "nbformat.v4.0.schema.json",
    (4, 1): "nbformat.v4.1.schema.json",
    (4, 2): "nbformat.v4.2.schema.json",
    (4, 3): "nbformat.v4.3.schema.json",
    (4, 4): "nbformat.v4.4.schema.json",
    (4, 5): "nbformat.v4.5.schema.json",
}
```

## 工厂函数

### new_notebook()

```python
def new_notebook(**kwargs):
    nb = NotebookNode(
        nbformat=nbformat,           # 4
        nbformat_minor=nbformat_minor, # 5
        metadata=NotebookNode(),
        cells=[],
    )
    nb.update(kwargs)
    validate(nb)
    return nb
```

### new_code_cell()

```python
def new_code_cell(source="", **kwargs):
    cell = NotebookNode(
        id=random_cell_id(),         # uuid4 hex[:8]
        cell_type="code",
        metadata=NotebookNode(),
        execution_count=None,
        source=source,
        outputs=[],
    )
    cell.update(kwargs)
    validate(cell, "code_cell")
    return cell
```

### new_markdown_cell()

```python
def new_markdown_cell(source="", **kwargs):
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="markdown",
        source=source,
        metadata=NotebookNode(),
    )
    cell.update(kwargs)
    validate(cell, "markdown_cell")
    return cell
```

### new_raw_cell()

```python
def new_raw_cell(source="", **kwargs):
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="raw",
        source=source,
        metadata=NotebookNode(),
    )
    cell.update(kwargs)
    validate(cell, "raw_cell")
    return cell
```

### new_output()

```python
def new_output(output_type, data=None, **kwargs):
    output = NotebookNode(output_type=output_type)
    # 根据output_type设置默认值
    if output_type == "stream":
        output.name = "stdout"; output.text = ""
    elif output_type == "display_data":
        output.metadata = NotebookNode(); output.data = NotebookNode()
    elif output_type == "execute_result":
        output.metadata = NotebookNode(); output.data = NotebookNode()
        output.execution_count = None
    elif output_type == "error":
        output.ename = "NotImplementedError"; output.evalue = ""; output.traceback = []
    output.update(kwargs)
    if data is not None:
        output.data = data
    validate(output, output_type)
    return output
```

### output_from_msg()

从Jupyter Kernel的IOPub消息创建输出NotebookNode，支持4种消息类型：`execute_result`、`stream`、`display_data`、`error`。

## 读写基础设施（rwbase.py + nbjson.py）

### NotebookReader/NotebookWriter 抽象基类

```python
class NotebookReader:
    def reads(self, s, **kwargs): raise NotImplementedError
    def read(self, fp, **kwargs): return self.reads(fp.read(), **kwargs)

class NotebookWriter:
    def writes(self, nb, **kwargs): raise NotImplementedError
    def write(self, nb, fp, **kwargs): return fp.write(self.writes(nb, **kwargs))
```

### split_lines/rejoin_lines 行拆分

- `split_lines(nb)`：将cell.source、output.text、mimebundle中的多行字符串按行拆分为列表（`splitlines(True)`保留换行符），方便VCS逐行diff
- `rejoin_lines(nb)`：将列表重新join为字符串，读取时调用
- `_split_mimebundle`/`_rejoin_mimebundle`：处理mime bundle中的文本数据，跳过 `application/json` 和 `*+json` MIME类型
- `_non_text_split_mimes`：`application/javascript`和`image/svg+xml`也按行拆分

### strip_transient()

读写时均调用，移除不应持久化的临时字段：
- `nb.metadata.orig_nbformat`/`orig_nbformat_minor`
- `nb.metadata.signature`
- `cell.metadata.trusted`

### JSONReader/JSONWriter（nbjson.py）

- `JSONReader`：`json.loads()` → `from_dict()` → `rejoin_lines()` → `strip_transient()`
- `JSONWriter`：深拷贝 → `split_lines()` → `strip_transient()` → `json.dumps(indent=1, sort_keys=True, separators=(",",": "))`
- `BytesEncoder`：处理bytes→ASCII解码（用于base64编码的图片数据）

## 相关信源

- [NotebookNode源码](notebooknode-source.md)
- [v4格式详解](../concepts/09-v4-format.md)
- [Notebook构造API](../concepts/07-notebook-construction.md)
