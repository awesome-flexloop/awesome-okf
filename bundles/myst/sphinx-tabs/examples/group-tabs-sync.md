---
type: Example
title: 分组标签同步与配置
description: group-tab 跨页面同步用法、禁用 CSS 加载、禁用标签关闭等配置示例
tags: [sphinx, tabs, group-tab, configuration, example, sync]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:38:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 分组标签同步与配置

## 跨操作系统安装说明

在文档的多个页面中使用相同的 group-tab 名称，用户选择后跨页面保持同步：

**页面1（安装）**：
```rst
.. tabs::

   .. group-tab:: Linux

      .. code-block:: bash

         sudo apt install mypackage

   .. group-tab:: macOS

      .. code-block:: bash

         brew install mypackage

   .. group-tab:: Windows

      .. code-block:: bat

         choco install mypackage
```

**页面2（配置）**：
```rst
.. tabs::

   .. group-tab:: Linux

      .. code-block:: bash

         export MYAPP_HOME=/usr/local/myapp

   .. group-tab:: macOS

      .. code-block:: bash

         export MYAPP_HOME=/opt/homebrew/myapp

   .. group-tab:: Windows

      .. code-block:: bat

         set MYAPP_HOME=C:\Program Files\myapp
```

用户在页面1选择"macOS"后，页面2自动切换到"macOS"标签。

## 自定义主题禁用 CSS 加载

使用 pydata-sphinx-theme 或 sphinx-book-theme 等已内置 tabs 样式的主题时：

```python
# conf.py
extensions = ['sphinx_tabs.tabs']
sphinx_tabs_disable_css_loading = True
```

## 禁用标签关闭行为

默认情况下，点击已选中的标签会取消选中（内容区域折叠）。设为禁用后始终保持一个标签打开：

```python
# conf.py
sphinx_tabs_disable_tab_closing = True
```

效果对比：
- `False`（默认）：标签可关闭，tablist 有 `closeable` 类，适合 FAQ 折叠面板
- `True`：标签不可关闭，始终有一个面板可见，适合多语言代码示例

## 添加自定义 Builder 支持

如果使用自定义 HTML builder（如第三方主题的 builder）：

```python
# conf.py
sphinx_tabs_valid_builders = ['confluence', 'custom_html_builder']
```

不在兼容列表中的 builder 会降级为普通顺序输出。

## 全局资源强制加载

如果主题需要在所有页面加载 tabs JS（即使页面不含标签页）：

```python
# conf.py
html_assets_policy = 'always'  # Sphinx 5+
```

## 混合使用 tab 和 group-tab

同一标签组中不能混合普通 tab 和 group-tab，但同一页面可以同时存在独立的 tab 组和 group-tab 组：

```rst
独立标签组（不同步）：

.. tabs::

   .. tab:: 选项A
      独立内容A

   .. tab:: 选项B
      独立内容B

同步标签组（跨页记忆）：

.. tabs::

   .. group-tab:: Python
      Python 代码

   .. group-tab:: R
      R 代码
```

## 相关示例

- [基础标签页](/examples/basic-tabs.md)
- [多语言代码标签页](/examples/code-tabs.md)

## 相关概念

- [分组标签与代码标签](/concepts/03-group-and-code-tabs.md)
- [配置项参考](/concepts/04-configuration.md)
