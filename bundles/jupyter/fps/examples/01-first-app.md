---
type: Example
title: 第一个FPS应用
description: 创建最简单的FPS应用，体验模块生命周期（start/stop）和CLI参数传递。
tags: [example, getting-started, lifecycle, cli]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:55:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-guide
    resource: /references/module-source.md
    title: docs/guide.md The simplest application
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
---

## 概述

本示例创建一个最简FPS应用，演示模块的start/stop生命周期和CLI参数传递。

## 完整代码

创建 `simple.py`：

```python
from fps import Module

class Main(Module):
    def __init__(self, name, greeting="Hello!", farewell="Goodbye!"):
        super().__init__(name)
        self.greeting = greeting
        self.farewell = farewell

    async def start(self):
        print(self.greeting)

    async def stop(self):
        print(self.farewell)
```

## 运行

```bash
fps simple:Main --set greeting="Hello, World!" --set farewell="See you later!"
```

输出：
```
Hello, World!
```

应用持续运行，按 `Ctrl+C` 停止：
```
See you later!
```

## 代码解析

### 1. 继承Module类

```python
class Main(Module):
```

所有FPS模块都继承自 `fps.Module`。

### 2. 调用super().__init__

```python
def __init__(self, name, greeting="Hello!", farewell="Goodbye!"):
    super().__init__(name)
```

**必须**调用 `super().__init__(name)`，否则进入异步上下文时会抛出RuntimeError。额外的参数（greeting, farewell）成为可配置的模块参数。

### 3. 覆盖start方法

```python
async def start(self):
    print(self.greeting)
```

`start()` 是模块生命周期的启动阶段，在所有模块完成prepare后执行。这里简单打印问候语。

### 4. 覆盖stop方法

```python
async def stop(self):
    print(self.farewell)
```

`stop()` 在应用关闭时执行（Ctrl+C触发），用于清理资源。

### 5. CLI参数传递

```bash
fps simple:Main --set greeting="Hello, World!" --set farewell="See you later!"
```

- `simple:Main` 指定模块路径（文件名:类名）
- `--set key=value` 将参数传递给模块的 `__init__`

## 关键要点

- FPS模块的 `start()` 和 `stop()` 都是 async 方法
- `start()` 中打印后方法自然返回，框架自动标记阶段完成（无需手动调用done()）
- Ctrl+C触发优雅关闭，所有模块的stop()方法都会被执行
- 模块参数通过CLI的 `--set` 传递，也可以通过JSON配置文件设置

## 相关概念

- [安装与快速开始](/concepts/01-getting-started.md)
- [模块系统](/concepts/02-module-system.md)
- [生命周期阶段](/concepts/04-lifecycle-phases.md)
- [模块间共享对象](02-sharing-objects.md)
