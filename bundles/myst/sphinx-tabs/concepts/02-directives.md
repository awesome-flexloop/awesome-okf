---
type: Concept
title: 四个指令详解
description: sphinx-tabs 的四个指令（tabs/tab/group-tab/code-tab）的语法、选项、继承关系和 HTML 输出结构
tags: [sphinx, tabs, directive, container, inheritance]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:26:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 四个指令详解

sphinx-tabs 通过四个指令构成完整的标签页功能体系，它们之间存在继承关系：

```
TabDirective (基础标签页)
  └── GroupTabDirective (分组同步)
        └── CodeTabDirective (代码标签页)

TabsDirective (容器，独立)
```

## tabs 指令（容器）

`.. tabs::` 是标签页的容器指令，本身不接受参数，所有 `.. tab::` 等子指令必须位于其内部。

```rst
.. tabs::

   .. tab:: 标签A
      内容A

   .. tab:: 标签B
      内容B
```

### 工作机制

1. 创建 `<div class="sphinx-tabs">` 容器
2. 分配唯一 `tabs_id`（自增计数器）
3. 解析所有子 tab 指令，收集标签标题
4. 在容器开头插入 tablist（标签按钮栏）
5. 第一个标签默认选中（`aria-selected="true"`），其余隐藏

## tab 指令

`.. tab:: 标题` 定义单个标签页面板。

### 语法

```rst
.. tab:: 标签标题

   标签内容（支持任意 RST 标记）
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| 标签标题 | 是 | 显示在标签按钮上的文本 |

### HTML 输出结构

```html
<button role="tab" id="tab-0-0" aria-selected="true"
        aria-controls="panel-0-0" tabindex="0"
        class="sphinx-tabs-tab">标签标题</button>

<div role="tabpanel" id="panel-0-0"
     aria-labelledby="tab-0-0" tabindex="0"
     class="sphinx-tabs-panel">
  标签内容
</div>
```

### 自动 ID 生成

标签 ID 通过 `self.env.new_serialno(tabs_key)` 生成序号，结合 tabs_id 形成唯一标识：`tab-{tabs_id}-{tab_id}`。若 ID 重复则自动追加 `-1`、`-2` 后缀。

## group-tab 指令

`.. group-tab:: 组名` 创建分组标签页，具有跨页面同步选中状态的能力。

### 语法

```rst
.. tabs::

   .. group-tab:: Python

      print("hello")

   .. group-tab:: R

      cat("hello")
```

### 同步机制

- 组名通过 base64 编码生成确定性 tab_id
- 用户点击分组标签时，组名存入 `sessionStorage['sphinx-tabs-last-selected']`
- 其他页面加载时，从 sessionStorage 读取并自动选中同名标签
- 效果：用户在文档中选择"Python"后，所有页面的 code-tab/group-tab 自动切换到 Python

## code-tab 指令

`.. code-tab:: lexer [标签名]` 是专为代码示例设计的指令，继承自 group-tab（自动具备跨页同步能力）。

### 语法

```rst
.. code-tab:: python

   print("Hello")

.. code-tab:: py My Python Label

   print("Custom label")
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| lexer | 是 | Pygments 语法高亮 lexer 名称（如 python、javascript、r） |
| 自定义标签名 | 否 | 覆盖自动检测的语言显示名称 |

### 选项（继承自 CodeBlock）

支持所有 code-block 选项：`:linenos:`、`:emphasize-lines:`、`:caption:`、`:dedent:`、`:lineno-start:`、`:class:`、`:name:`

### Lexer 名称解析顺序

1. 若提供第二个参数，使用该文本作为标签名
2. 否则在 `sphinx.highlighting.lexer_classes` 中查找正式名称
3. 最后在预构建的 `LEXER_MAP`（从 `pygments.lexers.get_all_lexers()` 生成）中查找短名映射

## 指令继承链的设计价值

| 层级 | 添加的功能 | CSS 类标记 |
|------|-----------|-----------|
| TabDirective | 基础标签页 | `sphinx-tabs-tab` |
| GroupTabDirective | 跨页同步（sessionStorage） | `+ group-tab` |
| CodeTabDirective | 代码块语法高亮 | `+ code-tab` |

每个子类只添加自己的功能，通过 CSS 类区分类型，前端 JS 检测 `group-tab` 类决定是否持久化选择。

## 相关概念

- [分组标签与代码标签](/concepts/03-group-and-code-tabs.md)
- [配置项参考](/concepts/04-configuration.md)
- [基础标签页示例](/examples/basic-tabs.md)
