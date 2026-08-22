---
type: Example
title: 基础标签页
description: sphinx-tabs 基础用法示例：创建简单标签页、嵌套标签页、带代码块的标签页
tags: [sphinx, tabs, example, basic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:34:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 基础标签页

## 最简单的标签页

```rst
.. tabs::

   .. tab:: 第一个标签

      这是第一个标签页的内容。

   .. tab:: 第二个标签

      这是第二个标签页的内容。
```

## 包含格式化内容的标签页

标签页内支持任意 RST 标记：列表、代码块、表格、图片等。

```rst
.. tabs::

   .. tab:: 安装步骤

      按照以下步骤安装：

      1. 下载安装包
      2. 运行安装程序
      3. 配置环境变量

      .. code-block:: bash

         export PATH=/usr/local/bin:$PATH

   .. tab:: 配置说明

      .. list-table:: 配置项
         :header-rows: 1

         * - 选项
           - 说明
         * - host
           - 服务器地址
         * - port
           - 端口号
```

## 嵌套标签页

标签页可以嵌套使用：

```rst
.. tabs::

   .. tab:: Linux

      Linux 下的安装方式：

      .. tabs::

         .. tab:: Ubuntu/Debian

            .. code-block:: bash

               sudo apt install mypackage

         .. tab:: CentOS/RHEL

            .. code-block:: bash

               sudo yum install mypackage

   .. tab:: macOS

      .. code-block:: bash

         brew install mypackage
```

嵌套标签页通过 `temp_data` 中的 `tabs_stack` 实现层级隔离，每个嵌套层级有独立的 tabs_id。

## 相关示例

- [多语言代码标签页](/examples/code-tabs.md)
- [分组标签同步](/examples/group-tabs-sync.md)

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [四个指令详解](/concepts/02-directives.md)
