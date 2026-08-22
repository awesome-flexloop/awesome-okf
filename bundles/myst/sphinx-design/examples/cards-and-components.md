---
type: Example
title: 卡片与交互组件示例
description: card/card-carousel/dropdown/tab-set/button/徽章的综合用法示例
tags:
- sphinx
- design
- card
- dropdown
- tabs
- button
- badge
- example
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/cards.py
- sphinx_design/dropdown.py
- sphinx_design/tabs.py
- sphinx_design/badges_buttons.py
---

# 卡片与交互组件示例

## 示例1：完整卡片（header/body/footer/图片/链接）

```rst
.. card:: 产品介绍
   :img-top: _static/product.jpg
   :img-alt: 产品截图
   :link: https://example.com/product
   :link-type: url
   :shadow: lg
   :text-align: center

   版本
   ^^^^
   :bdg-info:`v2.0` :bdg-success:`稳定`

   产品描述文字，介绍核心功能和优势。

   +++

   .. button-link:: https://example.com/docs
      :color: primary
      :align: center
      :expand:

      查看文档
```

## 示例2：无标题卡片 + 背景图

```rst
.. card::
   :img-background: _static/hero-bg.jpg
   :text-align: center

   .. raw:: html

      <h2 style="color:white">欢迎使用</h2>
      <p style="color:white">这是一个带背景图的Hero卡片</p>
```

## 示例3：卡片轮播

```rst
.. card-carousel:: 3

   .. card:: 卡片 A
      :shadow: sm

      内容 A。

   .. card:: 卡片 B
      :shadow: sm

      内容 B。

   .. card:: 卡片 C
      :shadow: sm

      内容 C。

   .. card:: 卡片 D
      :shadow: sm

      内容 D。
```

## 示例4：折叠面板（FAQ样式）

```rst
.. dropdown:: 如何安装？
   :color: primary
   :icon: download
   :animate: fade-in

   使用 pip 安装：

   .. code-block:: bash

      pip install sphinx-design

   然后在 conf.py 中添加 ``"sphinx_design"`` 到 extensions。

.. dropdown:: 支持哪些主题？
   :color: info
   :icon: question

   sphinx-design 与所有主流 Sphinx 主题兼容，包括 furo、
   pydata-sphinx-theme、sphinx-rtd-theme、sphinx-book-theme、
   sphinx-immaterial 等。因为使用 ``sd-`` 前缀命名空间，不会与主题冲突。

.. dropdown:: 非HTML输出支持哪些组件？
   :chevron: down-up

   在 LaTeX/PDF 输出中，dropdown 和 tab 会降级为"标题+内容"的线性结构；
   SVG图标（Octicon/Material）被跳过；FontAwesome图标在配置
   ``sd_fontawesome_latex`` 后可渲染；卡片显示为带框内容。
```

## 示例5：多语言代码标签页

````rst
.. tab-set-code::

   .. code-block:: python

      def hello():
          print("Hello, World!")

   .. code-block:: javascript

      function hello() {
          console.log("Hello, World!");
      }

   .. code-block:: rust

      fn hello() {
          println!("Hello, World!");
      }
````

## 示例6：自定义同步标签组

```rst
.. tab-set::
   :sync-group: os

   .. tab-item:: macOS
      :sync: mac

      .. code-block:: bash

         brew install sphinx-design

   .. tab-item:: Linux
      :sync: linux
      :selected:

      .. code-block:: bash

         pip install sphinx-design

   .. tab-item:: Windows
      :sync: windows

      .. code-block:: powershell

         pip install sphinx-design
```

页面上其他使用 `:sync-group: os` 的 tab-set 会自动同步选择。

## 示例7：徽章组合使用

```rst
状态: :bdg-success:`运行中` :bdg-warning:`维护中` :bdg-danger:`已下线`

版本: :bdg-primary:`v3.0` :bdg-secondary-line:`v2.x` :bdg-muted-line:`v1.x`

链接: :bdg-link-primary:`GitHub <https://github.com>` :bdg-link-info-line:`文档 <https://docs.example.com>`

内引: :bdg-ref-success:`快速上手 <getting-started>`
```

## 示例8：按钮组

```rst
.. button-link:: https://example.com
   :color: primary
   :shadow:

   主要按钮

.. button-link:: https://example.com
   :color: primary
   :outline:

   轮廓按钮

.. button-ref:: getting-started
   :color: success
   :align: center
   :tooltip: 前往入门教程

   开始使用

.. button-link:: https://example.com
   :color: danger
   :expand:

   全宽危险按钮
```

## 示例9：文章信息栏

```rst
.. article-info::
   :avatar: _static/avatar.png
   :avatar-outline: primary
   :author: 张三 :octicon:`verified;1em`
   :date: 2024年1月15日
   :read-time: 约 10 分钟
```

## 示例10：综合——文档首页Hero区

```rst
.. grid::
   :margin: 4
   :padding: 4

   .. grid-item::
      :columns: 12 8
      :child-direction: column
      :child-align: center

      .. card::
         :shadow: lg
         :text-align: center
         :padding: 5

         文档中心
         ^^^^^^^^

         这是项目的文档中心，包含入门指南、API参考和示例。

         +++

         .. grid:: 2
            :gutter: 2

            .. grid-item::

               .. button-ref:: getting-started
                  :color: primary
                  :expand:
                  :shadow:

                  :octicon:`rocket;1em` 快速开始

            .. grid-item::

               .. button-ref:: api-reference
                  :color: secondary
                  :outline:
                  :expand:

                  :octicon:`book;1em` API 参考
```
