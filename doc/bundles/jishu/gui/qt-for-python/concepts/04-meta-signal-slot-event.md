---
type: Concept
title: 元对象系统、信号槽机制与事件处理
description: Qt 元对象系统三要素（QObject/Q_OBJECT/moc）、信号槽连接语法与事件分发、事件过滤器机制
tags: [元对象系统, QObject, 信号槽, Signal, Slot, 事件, eventFilter]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T12:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: jianshu-qt-article-source
    resource: /references/article-source.md
    title: 简书文集事实登记（F-001 ~ F-111）
  - id: qt-official-docs
    resource: https://doc.qt.io/qtforpython-6/
    title: Qt for Python 官方文档
---

# 元对象系统、信号槽机制与事件处理

## 元对象系统（Meta-Object System）

Qt 的元对象系统为信号槽、运行时类型信息、动态属性提供基础，官方文档明确其基于**三要素**（F-103）：

1. **`QObject` 类**：所有需要元对象能力的类的根基类，提供父子对象树（内存管理）与信号槽能力；
2. **`Q_OBJECT` 宏**：类声明内放置该宏，声明启用元对象特性；
3. **元对象编译器 moc（Meta-Object Compiler）**：编译期扫描含 Q_OBJECT 的类，生成包含元信息的额外 C++ 代码。

> 在 Python 绑定（PySide2/PyQt5）中，moc 由绑定层自动处理，开发者无需手动运行，直接在 Python 类中用 `Signal`/`pyqtSignal` 定义信号即可。

## 信号槽（Signals & Slots）

信号槽是 Qt 组件间通信的核心机制：**对象状态变化时发射信号（signal），连接到该信号的槽函数（slot）被自动调用**。

```python
from PySide2.QtCore import Signal, QObject

class Counter(QObject):
    changed = Signal(int)          # 定义携带 int 参数的信号

    def add(self):
        self._n += 1
        self.changed.emit(self._n) # 发射信号

counter = Counter()
counter.changed.connect(lambda n: print("count =", n))  # 连接槽
```

要点：

- 信号可以**一对多**连接多个槽，也可以信号连信号；
- 连接类型决定调用时机：`DirectConnection`（同步立即）、`QueuedConnection`（排队到接收者线程事件循环，跨线程必用）、`AutoConnection`（默认，按线程关系自动选择）；
- 槽可以是任意可调用对象（Python 函数/lambda 无需装饰器，`@Slot()` 主要用于显式声明参数类型）。

## 事件处理（Events）

事件是更底层的输入/系统消息抽象（鼠标、键盘、绘制、定时器等）。处理方式有三种：

1. **重写事件处理器**：如 `mousePressEvent(self, event)`、`paintEvent(self, event)`、`keyPressEvent(...)`；
2. **事件过滤器**：`obj.installEventFilter(self)` 后在 `eventFilter(self, obj, event)` 中拦截目标对象事件，返回 `True` 表示截获；
3. **发送事件**：`QCoreApplication.sendEvent()` 同步立即派发；`postEvent()` 投递到事件队列，由主循环下次分发（F-104）。

### 信号与事件的关系

- **事件**是"发生了什么"的原始消息（底层、面向输入与系统）；
- **信号**是组件对外暴露的"状态变化通知"（高层、面向业务逻辑）；控件往往在内部处理事件后发射信号（例如按钮在鼠标释放事件后发射 `clicked`）。

## 可运行示例

- [示例 27：The Meta-Object System](../examples/27-5d44c5efa393.md)：元对象系统官方文档译注
- [示例 30：Qt signal 和 slot](../examples/30-04b6f4df1db5.md)：信号槽机制与写法
- [示例 28：Qt 事件](../examples/28-14a67fb71139.md) · [示例 29：Qt 事件管理](../examples/29-70b7d198b0e2.md)：事件处理与过滤器

## 事实溯源

F-103、F-104（Qt 官方文档核验），详见 [verification](../references/verification.md) 第 4~5 项。
