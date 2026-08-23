---
type: Example
title: 内容管理API使用
description: 在浏览器端使用BrowserStorageDrive进行文件CRUD操作、检查点管理
tags: [contents-api, browserstoragedrive, crud, checkpoint, localforage]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:34:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contents-source
    resource: /references/contents-source.md
    title: 内容管理信源
---

## 获取BrowserStorageDrive实例

在JupyterLab扩展中，通过Token获取驱动器：

```typescript
import { IContentsManager } from '@jupyterlab/services';

// 在插件activate中
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:drive',
  autoStart: true,
  requires: [IContentsManager],
  activate: (app, contentsManager) => {
    // BrowserStorageDrive注册为默认drive
    // 可以通过drive名称获取
    const drive = contentsManager.drive as any; // BrowserStorageDrive实例
  }
};
```

## 文件CRUD操作

### 创建新Notebook

```typescript
// 创建新的未命名Notebook
const model = await drive.newUntitled({
  path: '',              // 在根目录创建
  type: 'notebook'       // 'notebook' | 'file' | 'directory'
});
console.log('Created:', model.name);  // "Untitled.ipynb"
console.log('Path:', model.path);     // "Untitled.ipynb"
```

### 创建新目录

```typescript
const folder = await drive.newUntitled({
  path: '',
  type: 'directory'
});
// folder.name = "Untitled Folder"
```

### 创建文本文件

```typescript
const textFile = await drive.newUntitled({
  path: '',
  type: 'file',
  ext: '.py'  // 指定扩展名
});
// textFile.name = "untitled.py"
```

### 读取文件

```typescript
// 读取文件内容
const notebook = await drive.get('Untitled.ipynb', {
  content: true,          // 获取content（false只获取元数据）
  format: 'json'          // 可选：请求特定格式
});

console.log(notebook.type);        // 'notebook'
console.log(notebook.content);     // Notebook JSON结构
console.log(notebook.last_modified); // ISO时间戳
```

### 读取目录

```typescript
const folder = await drive.get('', { content: true });
// folder.type === 'directory'
// folder.content 是 IModel[] 数组
for (const item of folder.content) {
  console.log(item.name, item.type, item.size);
}
```

### 保存文件

```typescript
// 保存/更新文件
const saved = await drive.save('test.py', {
  type: 'file',
  format: 'text',
  content: 'print("Hello, JupyterLite!")\n',
  mimetype: 'text/x-python'
});
console.log('Saved:', saved.path);
```

### 保存Notebook

```typescript
import { nbformat } from '@jupyterlab/coreutils';

const nb: nbformat.INotebookContent = {
  nbformat: 4,
  nbformat_minor: 5,
  metadata: { orig_nbformat: 4 },
  cells: [
    {
      cell_type: 'code',
      execution_count: null,
      metadata: {},
      outputs: [],
      source: 'print("Hello!")'
    }
  ]
};

await drive.save('hello.ipynb', {
  type: 'notebook',
  format: 'json',
  content: nb
});
```

### 重命名/移动文件

```typescript
const renamed = await drive.rename('Untitled.ipynb', 'my-notebook.ipynb');
// 移动到子目录
await drive.rename('test.py', 'scripts/test.py');
```

### 复制文件

```typescript
const copy = await drive.copy('my-notebook.ipynb', '');
// 自动命名为 "my-notebook (copy).ipynb"
// 如果已存在，继续添加 "(copy)" 后缀
```

### 删除文件

```typescript
await drive.delete('old-file.py');
// 删除目录及其内容
await drive.delete('old-folder/');
```

## 检查点管理

### 创建检查点

```typescript
const checkpoint = await drive.createCheckpoint('my-notebook.ipynb');
console.log('Checkpoint ID:', checkpoint.id);           // "0", "1", ...
console.log('Last modified:', checkpoint.last_modified);
```

### 列出检查点

```typescript
const checkpoints = await drive.listCheckpoints('my-notebook.ipynb');
for (const cp of checkpoints) {
  console.log(cp.id, cp.last_modified);
}
// 每个文件最多保留5个检查点
```

### 恢复检查点

```typescript
// 恢复到ID为"0"的检查点
await drive.restoreCheckpoint('my-notebook.ipynb', '0');
```

### 删除检查点

```typescript
await drive.deleteCheckpoint('my-notebook.ipynb', '0');
```

## 文件下载

```typescript
// 获取文件的下载URL（Blob URL）
const url = await drive.getDownloadUrl('my-notebook.ipynb');

// 在浏览器中下载
const a = document.createElement('a');
a.href = url;
a.download = 'my-notebook.ipynb';
a.click();
URL.revokeObjectURL(url);
```

## 监听文件变更

```typescript
// 监听文件变更事件
drive.fileChanged.connect((_, args) => {
  switch (args.type) {
    case 'new':
      console.log('File created:', args.newValue.path);
      break;
    case 'save':
      console.log('File saved:', args.newValue.path);
      break;
    case 'rename':
      console.log('Renamed:', args.oldValue.path, '→', args.newValue.path);
      break;
    case 'delete':
      console.log('Deleted:', args.oldValue.path);
      break;
  }
});
```

## 清除所有存储

```typescript
// 警告：清除所有文件、计数器和检查点
await drive.clearStorage();
```

## 格式转换注意事项

BrowserStorageDrive 自动处理三种文件格式的转换：

| 格式 | MIME类型 | 用途 |
|------|----------|------|
| `'json'` | application/json | .ipynb、.json文件 |
| `'text'` | text/* | .py、.md、.txt等文本 |
| `'base64'` | application/octet-stream | 图片、二进制文件 |

保存时根据文件扩展名自动推断format，也可以显式指定。读取时如果请求的format与存储格式不同，会自动转换。

## 相关概念

- [内容管理与文件系统](/concepts/03-contents-and-filesystem.md)
- [浏览器存储](/concepts/05-browser-storage.md)
- [内容管理信源](/references/contents-source.md)
