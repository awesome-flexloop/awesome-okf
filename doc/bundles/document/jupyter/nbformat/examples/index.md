# 示例索引

本目录包含nbformat的实战示例代码，每个示例均可独立运行。

## 示例清单

* [创建和写入Notebook](01-create-and-write.md) — 使用`new_notebook`/`new_code_cell`/`new_output`等工厂函数从零构建Notebook，包含Markdown、代码单元、多种输出类型。
* [读取、验证与转换](02-read-validate-convert.md) — 读取现有.ipynb文件、Schema验证、版本转换(v4↔v3)、验证错误处理、normalize归一化。
* [Notebook批处理与信任管理](03-batch-processing-and-trust.md) — 批量遍历目录、标签管理、输出清除、NotebookNotary签名信任、合并Notebook。

```{toctree}
:maxdepth: 7

01-create-and-write
02-read-validate-convert
03-batch-processing-and-trust
```
