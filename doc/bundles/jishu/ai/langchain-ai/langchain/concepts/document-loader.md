---
type: concept
title: 文档与加载器
description: Document 数据模型、Blob 二进制抽象、BaseLoader 懒加载接口与 BaseBlobParser 解析器协议
tags: [langchain, document, loader, blob, parser]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: ref-po
    resource: /references/prompts-output.md
    title: 提示词、模型与输出解析源码信源
  - id: ref-rc
    resource: /references/runnables-callbacks.md
    title: 回调、追踪与检索源码信源
---

# 文档与加载器

文档（Document）是检索工作流的基本数据单元，加载器（Loader）负责从外部数据源产生 Document。langchain-core 在 `documents/base.py` 定义 `Document` 和 `Blob`，在 `document_loaders/base.py` 定义 `BaseLoader` 和 `BaseBlobParser` 两个抽象接口。

## Document

`Document`（`documents/base.py:288`）继承 `BaseMedia`（继承 `Serializable`），用于存储一段文本及其关联元数据。

### 字段

| 字段 | 类型 | 行号 | 说明 |
|---|---|---|---|
| `page_content` | `str` | 306 | 文本内容（必填，位置参数） |
| `metadata` | `dict` | 继承 | 元数据（来源、页码、URL 等） |
| `id` | `str \| None` | 继承 | 文档唯一标识 |
| `type` | `Literal["Document"]` | 309 | 序列化鉴别字段，固定 `"Document"` |

### 关键方法

- `__init__(self, page_content: str, **kwargs)`（第311行）：`page_content` 作为位置参数传入，其余字段（metadata、id）通过 kwargs。
- `is_lc_serializable` 返回 `True`（第318行），`get_lc_namespace` 返回 `["langchain", "schema", "document"]`（第323行）。
- `__str__`（第331行）：当有 metadata 时返回 `page_content='...' metadata={...}`，否则返回 `page_content='...'`。这种格式确保将 Document 直接传入 prompt 时的行为稳定。

### 设计定位

文档字符串明确说明（第291-294行）：`Document` 用于**检索工作流**，而非聊天 I/O。向 LLM 发送对话文本应使用消息类型（`HumanMessage`、`SystemMessage` 等），不要把 Document 当消息用。

### 构造示例

```python
from langchain_core.documents import Document

doc = Document(
    page_content="LangChain 是一个 LLM 应用框架",
    metadata={"source": "https://example.com", "page": 1},
)
doc.page_content
doc.metadata["source"]
doc.id = "doc_001"
```

## BaseMedia 与 Blob

`BaseMedia`（`documents/base.py:34`）是 `Document` 和 `Blob` 的共同基类，提供 `metadata`、`id` 等字段。

`Blob`（`documents/base.py:59`）表示二进制大对象，用于加载器处理非文本文件（PDF、图片、音频等）：

| 成员 | 行号 | 说明 |
|---|---|---|
| `source` 属性 | 137 | 数据来源标识（路径或 URL） |
| `check_blob_is_valid` 类方法 | 151 | 校验 Blob 有效性 |
| `as_string()` | 158 | 以字符串形式读取（解码） |
| `as_bytes()` | 176 | 以字节形式读取 |
| `as_bytes_io()` | 195 | 返回 `BytesIO`/`BufferedReader` 生成器 |
| `from_path(path, ...)` 类方法 | 214 | 从文件路径构造 |
| `from_data(data, ...)` 类方法 | 251 | 从内存数据构造 |

`Blob` 封装了数据来源和 MIME 类型，使解析器无需关心数据来自文件还是内存。

## BaseLoader 加载器接口

`BaseLoader`（`document_loaders/base.py:26`）是文档加载器的抽象基类。核心设计理念是**懒加载**——子类应实现生成器方法 `lazy_load`，避免一次性将所有文档载入内存。

### 方法

| 方法 | 行号 | 说明 |
|---|---|---|
| `load() -> list[Document]` | 37 | 立即加载全部文档，实现为 `list(self.lazy_load())`，**不应重写** |
| `aload() -> list[Document]` | 45 | 异步加载，实现为 `[d async for d in self.alazy_load()]` |
| `load_and_split(text_splitter=None) -> list[Document]` | 53 | 加载并切分，默认用 `RecursiveCharacterTextSplitter`（需 `langchain-text-splitters` 包） |
| `lazy_load() -> Iterator[Document]` | 91 | **子类应实现**的懒加载生成器 |
| `alazy_load() -> AsyncIterator[Document]` | 102 | 异步懒加载，默认在线程池中迭代同步 `lazy_load` |

### lazy_load 的后备逻辑

`lazy_load`（第91行）不是 `@abstractmethod`，而是有后备实现：如果子类重写了 `load`（旧式写法），则返回 `iter(self.load())`；否则抛出 `NotImplementedError`。文档注释说明这是为了向后兼容，未来所有子类都实现 `lazy_load` 后会升级为抽象方法。

### alazy_load 默认实现

`alazy_load`（第102行）通过 `run_in_executor` 在线程池中逐个迭代同步 `lazy_load` 的结果：

```python
async def alazy_load(self):
    iterator = await run_in_executor(None, self.lazy_load)
    done = object()
    while True:
        doc = await run_in_executor(None, next, iterator, done)
        if doc is done:
            break
        yield doc
```

因此自定义加载器只需实现 `lazy_load`，自动获得异步能力。需要原生异步性能时可 override `alazy_load`。

### load_and_split

`load_and_split`（第53行）被标注为 **deprecated**（文档注释 `!!! danger`，第58-60行），不建议重写。它调用 `self.load()` 后用 `TextSplitter.split_documents` 切分。推荐做法是加载器和切分器分离使用：

```python
docs = loader.load()
splits = text_splitter.split_documents(docs)
```

## BaseBlobParser

`BaseBlobParser`（`document_loaders/base.py:117`）是 Blob 解析器抽象，将原始二进制数据解析为 Document。

| 方法 | 行号 | 说明 |
|---|---|---|
| `lazy_parse(blob: Blob) -> Iterator[Document]`（抽象） | 128 | 子类必须实现，懒解析生成器 |
| `parse(blob: Blob) -> list[Document]` | 140 | 立即解析，实现为 `list(self.lazy_parse(blob))`，不应重写 |

Blob 解析器与 Blob 加载器解耦——同一解析器可复用在不同来源的 Blob 上（文件、内存、网络）。例如 PDF 解析器不关心 PDF 来自本地文件还是 S3，只接收 `Blob` 对象。

## 与 VectorStore 的协作

加载器产出的 Document 列表可直接传入 `VectorStore.add_documents`：

```python
loader = MyCustomLoader(...)
docs = loader.load()
vectorstore.add_documents(docs)
```

或用懒加载逐批添加以控制内存：

```python
for batch in _batch(loader.lazy_load(), size=100):
    vectorstore.add_documents(batch)
```

## 代码示例

```python
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

# 1. 自定义加载器
class ListLoader(BaseLoader):
    def __init__(self, texts: list[str]):
        self.texts = texts

    def lazy_load(self):
        for text in self.texts:
            yield Document(page_content=text)

loader = ListLoader(["文档1", "文档2", "文档3"])
docs = loader.load()  # [Document(...), Document(...), Document(...)]

# 2. 懒加载（适合大文件）
for doc in loader.lazy_load():
    process(doc)

# 3. 异步加载
docs = await loader.aload()

# 4. 自定义 Blob 解析器
from langchain_core.document_loaders import BaseBlobParser
from langchain_core.documents.base import Blob

class SimpleTextParser(BaseBlobParser):
    def lazy_parse(self, blob):
        yield Document(page_content=blob.as_string())

parser = SimpleTextParser()
blob = Blob.from_data(b"hello world")
docs = parser.parse(blob)
```

## 相关概念

- 检索器与向量库 —— Document 存入 VectorStore 供检索
- 总览 —— Document 在数据层中的位置
- Runnable 协议 —— run_in_executor 实现异步适配
