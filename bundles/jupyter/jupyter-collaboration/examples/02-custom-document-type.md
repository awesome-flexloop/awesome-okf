---
type: Example
title: 自定义文档类型协作支持
description: 为自定义文件类型添加协作支持，包括后端YDoc工厂注册和前端SharedModelFactory扩展
tags: [custom-type, extension, plugin, ydoc]
concepts: [/concepts/02-ydoc-extension.md, /concepts/09-frontend-provider.md, /concepts/03-document-room.md]
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# 自定义文档类型协作支持

## 概述

jupyter-collaboration 支持为自定义文件类型添加实时协作支持。这需要：
1. **后端**：注册YDoc工厂函数，定义如何从文件内容创建/读写CRDT文档
2. **前端**：注册SharedModelFactory，提供文档类型的共享模型

## 后端：注册YDoc工厂

YDoc工厂负责将文件内容解析为Yjs共享类型，并能将Yjs状态序列化回文件格式。

### 工厂函数签名

```python
from pycrdt import Doc
from jupyter_server_ydoc.ydoc import YBaseDoc

class MyCustomDoc(YBaseDoc):
    """自定义文档YDoc包装器"""
    
    def __init__(self, ydoc: Doc | None = None):
        super().__init__(ydoc)
        # 定义共享类型，例如Y.Text、Y.Array、Y.Map
        self._ytext = self._ydoc.get("mycontent", type=Y.Text)
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get(self) -> str:
        """将YDoc内容序列化为文件内容"""
        return str(self._ytext)
    
    def set(self, raw_value: str) -> None:
        """从文件内容初始化YDoc"""
        self._ytext.clear()
        self._ytext.insert(0, raw_value)
    
    # 可选：实现observe方法监听变更
    def observe(self, callback):
        self._ytext.observe(callback)
```

### 注册工厂到YDOCS字典

在server extension中注册：

```python
from jupyter_server_ydoc.ydoc import YDOCS

# 方式1：在activate中注册
def _load_jupyter_server_extension(serverapp):
    YDOCS["my-custom-type"] = lambda ydoc: MyCustomDoc(ydoc)

# 方式2：使用entry point（pyproject.toml）
# [project.entry-points."jupyter_server_ydoc.ydocs"]
# my-custom-type = "my_package:MyCustomDoc"
```

### 使用文件特定的clean_callback

如果需要在房间清理时执行自定义逻辑（如关闭数据库连接、刷新缓存）：

```python
from jupyter_server_ydoc.ydoc import YFILES_CLEAN_EVENTS

async def my_clean_callback(room_id, file_format, file_type, file_id, ydoc):
    """自定义清理回调"""
    # 例如：提交未保存的更改、释放资源
    my_doc = ydoc  # MyCustomDoc实例
    my_doc.flush()

YFILES_CLEAN_EVENTS.append(my_clean_callback)
```

## 前端：注册SharedModelFactory

### 定义共享模型

```typescript
import { YDocument, YFile } from '@jupyter/ydoc';
import { ISharedDocument } from '@jupyter/ydoc';

// 如果有特殊需求，可以扩展YFile
export interface ISharedCustomDoc extends ISharedDocument {
  readonly myContent: string;
}

export class YCustomDoc extends YFile implements ISharedCustomDoc {
  // 使用Y.Text存储自定义内容
  readonly ytext: Y.Text;
  
  constructor(options?: ISharedDocumentOptions) {
    super(options);
    this.ytext = this.ydoc.getText('mycontent');
  }
  
  get myContent(): string {
    return this.ytext.toString();
  }
  
  setMyContent(value: string): void {
    this.transact(() => {
      const ytext = this.ytext;
      ytext.delete(0, ytext.length);
      ytext.insert(0, value);
    });
  }
}
```

### 注册到ISharedModelFactory

```typescript
import { ISharedModelFactory } from '@jupyter/docprovider';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:collaboration',
  requires: [ISharedModelFactory],
  activate: (app, sharedModelFactory) => {
    // 注册文档类型工厂
    sharedModelFactory.registerDocumentFactory(
      'my-custom-type',
      (options) => {
        return new YCustomDoc(options);
      }
    );
  }
};
```

### 注册到DocumentRegistry

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:document-registry',
  requires: [IDocumentRegistry, ISharedModelFactory],
  activate: (app, docRegistry, sharedModelFactory) => {
    // 创建factory使用collaborative=true
    const factory = new MyCustomDocFactory({
      name: 'My Custom Document',
      fileTypes: ['my-custom-type'],
      sharedModelFactory,  // 使用协作共享模型工厂
      collaborative: true, // 关键：启用协作模式
    });
    docRegistry.addWidgetFactory(factory);
  }
};
```

### 文件类型注册

```typescript
docRegistry.addFileType({
  name: 'my-custom-type',
  displayName: 'My Custom Document',
  extensions: ['.mycust'],
  mimeTypes: ['application/x-my-custom'],
  contentType: 'file',  // 或自定义contentType
  fileFormat: 'text',
});
```

## 完整示例：Markdown文件协作

jupyter-collaboration已内置Markdown文件支持，以下是类似实现：

### 后端

```python
from pycrdt import YText
from jupyter_server_ydoc.ydoc import YBaseDoc

class YMarkdownDoc(YBaseDoc):
    def __init__(self, ydoc=None):
        super().__init__(ydoc)
        self._ysource = self._ydoc.get("source", YText)
    
    @property
    def version(self):
        return "1.0.0"
    
    def get(self):
        return str(self._ysource)
    
    def set(self, value):
        with self._ydoc.transaction():
            self._ysource.clear()
            self._ysource.insert(0, value)
    
    def observe(self, callback):
        self._ysource.observe(callback)

# 注册
YDOCS["markdown"] = lambda ydoc: YMarkdownDoc(ydoc)
```

### 前端

```typescript
import { YFile } from '@jupyter/ydoc';

// Markdown文件直接使用YFile（Y.Text存储在"source"key下）
sharedModelFactory.registerDocumentFactory('markdown', (options) => {
  return new YFile(options);
});
```

## 自定义YStore（可选）

如果默认的SQLiteYStore不满足需求，可以实现自定义YStore：

```python
from jupyter_server_ydoc.stores import BaseYStore
from typing import AsyncIterator, Tuple

class RedisYStore(BaseYStore):
    """使用Redis作为CRDT更新存储"""
    
    def __init__(self, redis_url: str, path: str = ""):
        super().__init__(path)
        self._redis = aioredis.from_url(redis_url)
        self._key = f"ystore:{path}"
    
    async def write(self, data: bytes) -> None:
        await self._redis.rpush(self._key, data)
    
    async def read(self) -> AsyncIterator[Tuple[bytes, str, str, float]]:
        # 返回 (update_data, decoder_name, room_id, timestamp) 元组流
        items = await self._redis.lrange(self._key, 0, -1)
        for item in items:
            yield (item, "RedisYStore", self.path, time.time())
    
    async def clear(self) -> None:
        await self._redis.delete(self._key)
```

注册自定义YStore：

```python
c.YDocExtension.store_class = "my_package.RedisYStore"
c.YDocExtension.ystore_kwargs = {"redis_url": "redis://localhost:6379"}
```

## 自定义FileLoader（不推荐）

通常不需要自定义FileLoader，但如果需要特殊的文件I/O逻辑，可以：

1. 继承FileLoader
2. 重写load_content/maybe_save_content
3. 提供自定义的FileLoaderMapping

但这需要更多的内部API理解，一般建议通过ContentsManager扩展实现自定义文件I/O。

## 最佳实践

1. **版本号管理**：YBaseDoc的version属性用于向前兼容，格式变化时递增版本号
2. **事务原子性**：在set()中使用transaction()批量操作，避免生成过多增量更新
3. **错误处理**：文件解析失败时抛出明确异常，由上层处理
4. **双向同步**：确保get()和set()互为逆操作（`set(get(doc)) == doc`）
5. **观察回调**：正确实现observe方法，确保变更能被UndoManager追踪
6. **内容类型注册**：确保前端fileType和后端YDOCS的key一致
