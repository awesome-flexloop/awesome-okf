---
type: Concept
title: 多线程与定时器：保持界面响应
description: GUI 主线程阻塞导致卡顿的原理；QTimer 定时任务、QThread 工作线程与事件处理三种方案
tags: [QThread, QTimer, 多线程, 事件循环, 界面卡顿, 信号槽跨线程]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T12:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: jianshu-gui-article-source
    resource: /references/article-source.md
    title: 简书文集事实登记（F-001 ~ F-123）
  - id: pyqt5-official-docs
    resource: https://www.riverbankcomputing.com/static/Docs/PyQt5/
    title: PyQt5 官方文档
---

# 多线程与定时器：保持界面响应

## 为什么需要多线程

GUI 程序是**单线程事件循环**模型：如果在槽函数里执行特别耗时的操作（大批量计算、网络下载、文件处理），主事件循环被占住，界面无法响应重绘与输入——表现为**整个窗口卡顿/未响应**，用户误以为程序出错而关闭，Windows 还可能判定"程序无响应"自动结束它（F-116）。

## 三种技术手段

| 手段 | 适用场景 | 要点 |
|------|---------|------|
| **QTimer** | 周期性/延迟任务（轮询、动画帧、超时刷新） | `timeout` 信号连槽；`start(ms)`；单次 `setSingleShot(True)` |
| **QThread** | 真正的后台耗时任务 | 工作对象 moveToThread 或子类化 run()；**结果通过信号回传主线程** |
| **事件处理** | 分片执行长任务 | 在耗时循环中穿插 `QApplication.processEvents()` 保持响应（轻量替代） |

## QThread 推荐用法（worker + moveToThread）

```python
class Worker(QObject):
    progress = Signal(int)
    finished = Signal()

    def run_long_task(self):
        for i in range(100):
            ...                       # 耗时工作
            self.progress.emit(i)     # 信号跨线程投递（QueuedConnection 自动）
        self.finished.emit()

thread = QThread()
worker = Worker()
worker.moveToThread(thread)
thread.started.connect(worker.run_long_task)
worker.progress.connect(lambda v: bar.setValue(v))   # 槽在主线程执行
worker.finished.connect(thread.quit)
thread.start()
```

## 铁律

1. **QWidget 及其子类只能在主线程访问**——工作线程里绝不创建/操作控件，数据通过信号槽传递；
2. 跨线程信号槽自动使用 `QueuedConnection`：信号参数放入接收线程事件队列，槽在接收者线程执行；
3. 线程结束用 `finished` 信号清理，不要强行 `terminate()`。

## 可运行示例

- [示例 18：多线程](../examples/18-ea8c6d82862b.md)：卡顿成因 + QTimer/QThread/事件处理三种方案（8 张截图）

## 事实溯源

F-116（Qt 线程文档官方核验）；篇内事实 F-052 ~ F-054。
