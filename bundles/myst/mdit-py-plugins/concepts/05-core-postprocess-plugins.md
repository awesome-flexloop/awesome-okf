---
type: Concept
title: 核心后处理插件
description: footnote_tail、tasklists、wordcount等在Core链注册的后处理插件
tags:
- mdit-py-plugins
- core-plugins
- footnote
- tasklists
- wordcount
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 01-plugin-basics
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins 源码路径映射
---

# 核心后处理插件

Core规则在所有块级和行内解析完成后执行，操作完整的Token流。

## footnote（三链协作）

footnote是最复杂的插件，同时注册了Block、Inline和Core三种规则：

1. **Block规则（footnote_def）**：识别 `[^label]:` 开头的行，将脚注内容用 `footnote_reference_open/close` 包裹标记，递归解析内容
2. **Inline规则（footnote_ref + footnote_inline）**：识别 `[^label]` 引用和 `^[content]` 行内脚注，分配 footnoteId
3. **Core规则（footnote_tail）**：将被footnote_reference_open/close包裹的脚注定义Token从正文中移除，收集到末尾生成脚注列表

**env数据结构**：
```python
env["footnotes"] = {
    "refs": {":label1": 0, ":label2": 1},  # 标签→脚注ID
    "list": {
        0: {"label": "label1", "count": 1},     # ID→脚注数据
        1: {"content": "^[inline]", "tokens": [...], "count": 0}
    }
}
```

**渲染输出**：
- 引用：`<sup class="footnote-ref"><a href="#fn1" id="fnref1">[1]</a></sup>`
- 脚注块：`<hr class="footnotes-sep"><section class="footnotes"><ol class="footnotes-list">`
- 脚注项：`<li id="fn1" class="footnote-item">...<a href="#fnref1" class="footnote-backref">↩</a></li>`
- 支持docId环境变量用于多文档场景

## tasklists

**注册位置**：after "inline"（Core链）

**工作流程**：
1. 遍历Token流，查找模式：`list_item_open → paragraph_open → inline`
2. 检查inline Token的content是否以 `[ ] `、`[x] `或`[X] `开头
3. 匹配时：
   - 在inline.children开头插入html_inline Token（含checkbox input）
   - 移除前3字符（`[ ]`或`[x]`+空格）
   - 给list_item_open添加 `class="task-list-item"`
   - 给父列表Token添加 `class="contains-task-list"`
4. label=True时在checkbox前后添加`<label>`包裹
5. label_after=True时用uuid生成checkbox ID和label for属性

**注意**：tasklists不注册新的解析规则，而是在Core后处理中**修改已有Token**。这意味着它不需要在Ruler中添加规则，只需要遍历tokens查找模式。

## wordcount

**注册位置**：push到Core链末尾

**工作流程**：
1. 遍历所有Token，累加text Token的content词数
2. 遍历inline Token的children中的text Token
3. 词数统计：按空格split，过滤纯标点元素，仅计含字母的词
4. 结果存入 `env["wordcount"] = {"words": N, "minutes": M}`
5. 支持自定义count_func和per_minute参数
6. store_text=True时将所有文本存入env["wordcount"]["text"]列表

**核心设计**：这是最简单的Core后处理插件，只读取Token不修改Token，统计结果通过env输出。

## anchors（标题锚点）

为标题添加锚点ID，类似GitHub的标题链接功能。在Core链注册后处理规则，遍历heading_open Token，根据标题文本生成slug并设置id属性。

## Core后处理插件通用模式

```python
def core_postprocess_plugin(md, **options):
    def postprocess(state: StateCore) -> None:
        tokens = state.tokens
        for i, token in enumerate(tokens):
            # 遍历tokens进行后处理
            # - 查找模式（tasklists）
            # - 收集数据（wordcount）
            # - 移动Token（footnote_tail）
            # - 添加属性（anchors）
            pass
    md.core.ruler.after("inline", "my_plugin", postprocess)
```

Core规则的特点：
- **不返回值**（返回None），直接修改state.tokens
- **可以修改Token列表**（增删改）
- **在所有解析完成后执行**，Token流完整
- **可以访问env**，用于收集统计数据
- **注册位置**：通常after "inline"（行内解析完成后）或push到链尾
