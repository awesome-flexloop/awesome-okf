---
type: Concept
title: 容器控件与 Model/View：标签页/堆栈/停靠/MDI/滚动区 与 表格/列表/树
description: 窗口空间不足时的容器方案；Qt Model/View 架构中视图类与基于项的便利类的区别，排序与数据呈现
tags: [QTabWidget, QStackedWidget, QDockWidget, QTableView, QTableWidget, QTreeView, QListWidget, ModelView]
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

# 容器控件与 Model/View

## 容器控件：空间不够怎么办

当控件太多一个窗口装不下时，用容器分页/分区：

| 容器 | 形态 | 典型用途 |
|------|------|---------|
| **QTabWidget** | 标签页切换 | 设置对话框多分页 |
| **QStackedWidget** | 一次只显示一页的堆栈（无自带切换按钮） | 向导页、配合列表做导航 |
| **QDockWidget** | 可停靠/浮动/关闭的面板 | 主窗口四周工具面板（IDE 风格） |
| **QMdiArea / QMdiSubWindow** | 多文档界面（MDI） | 窗口内再开多个子窗口 |
| **QScrollArea** | 内容超出自动出滚动条 | 大图、长表单 |

```python
tabs = QTabWidget()
tabs.addTab(page1, "基本设置")
tabs.addTab(page2, "高级设置")
```

## 表格与树：有规律地呈现大量数据

Qt 提供**模型/视图（Model/View）**架构与一组**基于项的便利类**（F-117）：

| 便利类（数据界面一体，小数据量直接用） | 对应视图类（Model/View 分离，大数据/多视图共用数据用） |
|------|------|
| QListWidget | QListView |
| QTableWidget | QTableView |
| QTreeWidget | QTreeView |

- 便利类：`QTableWidget(row, col)` + `setItem(row, col, QTableWidgetItem("..."))`，上手快；
- Model/View：自定义 `QAbstractTableModel` 子类实现 `rowCount/columnCount/data`，同一 model 可挂多个视图；
- 排序：`sortItems(column, Qt.DescendingOrder)` 降序 / `Qt.AscendingOrder` 升序；视图类用 `setSortingEnabled(True)` 点击表头排序。

## 选择建议

- 数据量小、单表展示 → 便利类（QTableWidget 等）；
- 数据来自数据库/大文件、需要多视图同步、要自定义渲染/编辑 → Model/View 四件套（View + Model + SelectionModel + Delegate）。

## 可运行示例

- [示例 19：容器](../examples/19-23aa59d47237.md)：QTabWidget/QStackedWidget/QDockWidget/MDI/QScrollBar（9 张截图）
- [示例 20：表格与树](../examples/20-2a7de6f37672.md)：QTableWidget/QListWidget/QTreeView 全家族演示（21 段代码、27 张截图）

## 事实溯源

F-117（Model/View 官方核验）；篇内事实 F-055 ~ F-060。
