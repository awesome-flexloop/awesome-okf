---
type: Concept
title: 按钮与输入控件：QPushButton/QRadioButton/QCheckBox/ComboBox/SpinBox/Slider/ProgressBar/日历
description: QAbstractButton 按钮基类体系；选择类、数字调节类与进度展示类控件的用法与典型信号
tags: [QPushButton, QRadioButton, QCheckBox, QComboBox, QSpinBox, QSlider, QProgressBar, QCalendarWidget]
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

# 按钮与输入控件

## 按钮类控件（基类 QAbstractButton）

按钮是 GUI 中最常用的动作触发方式。`QAbstractButton` 提供通用功能但为抽象类不能实例化，按场景派生子类：

| 控件 | 场景 | 关键信号 |
|------|------|---------|
| **QPushButton** | 普通命令按钮（确定/取消） | `clicked()` |
| **QRadioButton** | 单选（同组互斥，放入 `QButtonGroup` 或同一父容器自动成组） | `toggled(bool)` |
| **QCheckBox** | 多选/开关（可三态） | `stateChanged(int)` / `toggled(bool)` |

```python
btn = QPushButton("确定", self)
btn.clicked.connect(self.on_ok)          # 信号槽连接
check = QCheckBox("记住密码", self)
check.setChecked(True)
```

## 选择与数字输入

- **QComboBox（下拉列表框）**：集按钮与下拉选项于一体；`addItem()`/`addItems()` 填充、`currentTextChanged` 信号、可 `setEditable(True)` 允许输入；
- **QSpinBox（计数器）**：整数调节——默认范围 0~99、步长 1，可 `setRange()`/`setSingleStep()`；支持键盘上下箭头与直接输入；浮点用 `QDoubleSpinBox`；
- **QSlider（滑动条）**：水平/垂直有界整数值调节；比 SpinBox 更"自然"的连续量调节（音量、亮度）；`valueChanged(int)` 信号；常与 SpinBox 双向同步。

## 进度与日期

- **QProgressBar（进度条）**：展示任务进度，水平/垂直均可；`setRange(min,max)`，默认 0~99；`setValue()` 更新；忙碌态用 `setMinimum(0).setMaximum(0)` 显示滚动动画；
- **QCalendarWidget（日历）**：内置月历控件，`selectedDate()` 取日期、`selectionChanged` 信号；配套 `QDateEdit` 做下拉式日期输入。

## 控件选型速查

| 需求 | 首选控件 |
|------|---------|
| 触发动作 | QPushButton |
| 互斥单选 | QRadioButton + QButtonGroup |
| 独立开关/多选 | QCheckBox |
| 从固定列表选一项 | QComboBox（项少可用 QRadioButton） |
| 输入/调节整数 | QSpinBox（精确）或 QSlider（直觉） |
| 后台任务进度 | QProgressBar |
| 选日期 | QCalendarWidget / QDateEdit |

## 可运行示例

- [示例 29：按钮类控件](../examples/29-0174da3adc87.md)
- [示例 28：QComboBox](../examples/28-37e5e54474a9.md)
- [示例 27：计数器 QSpinBox](../examples/27-3a67ef2c315f.md)
- [示例 26：滑动条 QSlider](../examples/26-0883cf04b32b.md)
- [示例 25：进度条](../examples/25-d3ac07c635d3.md) · [示例 24：日历](../examples/24-e9d2a2cc1d2b.md)

## 事实溯源

篇内事实 F-073 ~ F-096，见 [article-source](../references/article-source.md)。
