# 信源登记簿

本目录包含 nbformat 源码的关键信源登记文档，为 concepts/ 和 examples/ 中的溯源引用提供目标。

## 信源清单

* [包入口公共API](init-api.md) — `nbformat/__init__.py` 顶层 read/write/reads/writes/validate/convert/NO_CONVERT 等API。
* [NotebookNode与Struct源码](notebooknode-source.md) — NotebookNode类和Struct基类的属性访问、深度拷贝、from_dict递归转换。
* [验证器Validator源码](validator-source.md) — 双验证器后端(fastjsonschema/jsonschema)、Schema缓存、normalize归一化、iter_validate。
* [签名与信任机制源码](sign-source.md) — NotebookNotary、HMAC签名、SignatureStore存储、信任判断、jupyter-trust CLI。
* [v4构造API源码](v4-nbbase-source.md) — v4/nbbase.py工厂函数(new_notebook/new_code_cell等)、rwbase读写基础设施。
* [版本转换converter源码](converter-source.md) — converter.py中convert()递归逐步转换逻辑、升级/降级路径、版本模块接口契约。

```{toctree}
:hidden:
:maxdepth: 7

converter-source
init-api
notebooknode-source
sign-source
v4-nbbase-source
validator-source
```
