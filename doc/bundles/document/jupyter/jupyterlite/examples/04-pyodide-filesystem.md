---
type: Example
title: Pyodide内核中操作文件系统
description: 在Pyodide内核中读写文件、理解DriveFS挂载点、使用JS互操作
tags: [pyodide, filesystem, drivefs, emscripten, js-interop]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:36:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contents-source
    resource: /references/contents-source.md
    title: 内容管理信源
  - id: kernel-source
    resource: /references/kernel-source.md
    title: 内核系统信源
---

## DriveFS 挂载点

在Pyodide内核中，浏览器存储通过DriveFS挂载到 `/drive/` 目录：

```python
import os
# 查看根目录
print(os.listdir('/'))
# ['drive', 'pyodide', 'tmp', 'home', ...]

# 查看drive目录（JupyterLite文件存储）
print(os.listdir('/drive'))
# 浏览器中JupyterLite文件浏览器里的文件和目录
```

所有在Notebook界面中创建/上传的文件都在 `/drive/` 目录下。

## 文件读写

### 读取文件

```python
# 读取文本文件
with open('/drive/data.txt', 'r') as f:
    content = f.read()
print(content)

# 读取JSON/Notebook
import json
with open('/drive/notebooks/welcome.ipynb', 'r') as f:
    nb = json.load(f)
print(nb['nbformat'])  # 4

# 读取二进制文件（如图片）
with open('/drive/image.png', 'rb') as f:
    data = f.read()
print(len(data), 'bytes')
```

### 写入文件

```python
# 写入文本文件
with open('/drive/output.txt', 'w') as f:
    f.write('Hello from Pyodide!\n')

# 写入CSV
import csv
with open('/drive/data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'value'])
    writer.writerow(['pi', 3.14159])

# 写入JSON
data = {'key': 'value', 'numbers': [1, 2, 3]}
with open('/drive/result.json', 'w') as f:
    json.dump(data, f)
```

### 创建目录

```python
import os
os.makedirs('/drive/my-project/data', exist_ok=True)
os.makedirs('/drive/my-project/scripts', exist_ok=True)
```

### 列出目录

```python
import os
for entry in os.listdir('/drive'):
    path = os.path.join('/drive', entry)
    if os.path.isdir(path):
        print(f'[DIR]  {entry}')
    else:
        size = os.path.getsize(path)
        print(f'[FILE] {entry} ({size} bytes)')
```

### 删除文件

```python
import os
os.remove('/drive/temp.txt')
os.rmdir('/drive/empty-folder')  # 只能删除空目录

# 删除非空目录
import shutil
shutil.rmtree('/drive/old-project')
```

### 重命名/移动

```python
import os
os.rename('/drive/old-name.txt', '/drive/new-name.txt')
os.rename('/drive/file.txt', '/drive/subfolder/file.txt')
```

## 重要注意事项

### 写入时机（close时持久化）

DriveFS 的文件写入是**延迟**的：
- `write()` 操作写入Worker内存中的Uint8Array缓冲区
- 文件内容在 `close()` 时通过Service Worker同步XHR持久化到IndexedDB

```python
# 正确：使用with语句确保close被调用
with open('/drive/important.txt', 'w') as f:
    f.write('important data')
# 文件在with块退出时自动close → 触发持久化

# 错误：不close可能导致数据丢失
f = open('/drive/data.txt', 'w')
f.write('data')
# 如果内核崩溃或页面刷新，data可能不会保存
f.close()  # 必须手动close
```

### 路径前缀

- DriveFS挂载点是 `/drive/`，不是 `/`
- JupyterLab文件浏览器中的路径 `notebooks/test.ipynb` 对应 `/drive/notebooks/test.ipynb`
- BrowserStorageDrive中的JupyterLab路径是 `BrowserStorage:notebooks/test.ipynb`

### 同步操作

所有文件操作在Worker中是同步阻塞的（POSIX API），但底层通过同步XHR转发到主线程。这意味着：
- 大文件读写可能阻塞内核执行（主线程IndexedDB操作通常很快，但不是零开销）
- 网络文件系统不适合（DriveFS只在Worker内同步操作）

### 符号链接不支持

DriveFS 的 `symlink` 和 `readlink` 操作抛出 EPERM/EINVAL 错误：

```python
# 这会失败！
os.symlink('/drive/file.txt', '/drive/link.txt')
# OSError: [Errno 1] Operation not permitted
```

## Python包安装

### 使用 micropip（运行时安装）

```python
import micropip
# 从Pyodide仓库安装WASM包
await micropip.install('numpy')
# 安装纯Python包
await micropip.install('pandas')
# 安装指定版本
await micropip.install('scikit-learn==1.3.0')
```

安装的WASM包位于 `/drive/pyodide/` 或 Pyodide 包目录中。

## JavaScript 互操作

Pyodide的独特能力：直接访问浏览器JavaScript API。

### DOM操作

```python
from js import document

# 创建输出元素
div = document.createElement('div')
div.innerHTML = '<h2>Hello from Python!</h2>'
document.body.appendChild(div)
```

### Fetch API（网络请求）

```python
from js import fetch
import json

async def fetch_data(url):
    response = await fetch(url)
    data = await response.json()
    return data

# 调用
data = await fetch_data('https://api.example.com/data')
print(data)
```

### 访问浏览器控制台

```python
from js import console
console.log('Hello from Python!')
console.warn('Warning message')
console.error('Error message')
```

### 使用JavaScript库

```python
import js
# 调用全局JS函数
result = js.eval('1 + 2')
# 如果页面加载了d3.js等JS库，可以直接调用
# js.d3.select(...)
```

## 文件持久化验证

写入文件后，可以通过以下方式确认数据已保存：

```python
# 1. 重新读取验证
with open('/drive/test.txt', 'w') as f:
    f.write('persisted')

with open('/drive/test.txt', 'r') as f:
    print(f.read())  # "persisted"

# 2. 刷新页面后，文件仍在JupyterLab文件浏览器中可见
# 3. 下载文件验证内容正确
```

## 相关概念

- [内容管理与文件系统](../concepts/03-contents-and-filesystem.md)
- [Service Worker桥接](../concepts/04-service-worker-bridge.md)
- [内核类型](../concepts/07-kernel-types.md)
- [浏览器存储](../concepts/05-browser-storage.md)
