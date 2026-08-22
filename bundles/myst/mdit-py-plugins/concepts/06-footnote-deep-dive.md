---
type: Concept
title: 脚注插件深入
description: footnote插件的三链协作机制、env数据结构、Token流变换、渲染输出
tags:
- mdit-py-plugins
- footnote
- deep-dive
- env
- three-chain
difficulty: 高级
estimated_time: 20分钟
prerequisites:
- 05-core-postprocess-plugins
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins 源码路径映射
---

# 脚注插件深入

footnote 是 mdit-py-plugins 中最复杂的插件，同时使用了 Block、Inline、Core 三种规则类型，是理解多链协作的最佳案例。

## 完整工作流程

```
Markdown 文本
    ↓
[Core: normalize → block]
    ↓
[Block链: footnote_def 规则]
    - 识别 [^label]: 开头的行
    - 输出 footnote_reference_open/close Token 包裹脚注内容
    - 递归解析脚注内部块级内容
    - 在 env["footnotes"]["refs"] 中注册标签
    ↓
[Core: inline]
    ↓
[Inline链: footnote_ref + footnote_inline 规则]
    - 识别 [^label] 引用 → footnote_ref Token
    - 识别 ^[content] 行内脚注 → footnote_ref Token + 解析children
    - 分配 footnoteId，记录到 env["footnotes"]["list"]
    ↓
[Core: footnote_tail 规则]
    - 将 footnote_reference_open/close 包裹的Token移出正文
    - 在tokens末尾生成脚注列表（footnote_block_open→footnote_open...→footnote_block_close）
    - 为多次引用生成多个 anchor
    ↓
[Renderer]
    - 引用渲染为上标链接
    - 脚注块渲染为<hr>+<section><ol><li>列表
    - anchor渲染为反向链接↩
```

## Block规则：footnote_def

footnote_def块规则负责识别脚注定义：

```
[^label]: Footnote content
    Continued paragraph (indented 4 spaces)
```

处理步骤：
1. 检查行首是否为 `[^x]:` 模式（x是label，不含空格）
2. silent模式返回True（用于预判）
3. 在env.refs中注册 `":" + label → -1`（-1表示尚未分配ID）
4. 创建 footnote_reference_open Token（meta.label=label）
5. 修改 state.bMarks/tShift/sCount/blkIndent/parentType，让 `: ` 后的内容被当作块级内容解析
6. 递归调用 `state.md.block.tokenize()` 解析脚注体
7. 恢复state修改，创建 footnote_reference_close Token
8. 设置open_token.map为脚注行范围

关键点：脚注定义的内容在解析后被 footnote_reference_open/close 标记包裹，但此时它们仍然在正文Token流中，直到footnote_tail规则移动它们。

## Inline规则：footnote_ref 和 footnote_inline

### footnote_ref：引用匹配

匹配 `[^label]` 模式：
1. 检查 `[^...\]` 格式（label中无空格和换行）
2. 在env.refs中查找label
3. 如果未定义且always_match_refs=False，返回False
4. 分配footnoteId（新标签）或获取已有ID
5. subId递增（同一脚注多次引用计数）
6. 输出 footnote_ref Token（meta={id, subId, label}）

### footnote_inline：行内脚注

匹配 `^[content]` 模式（inline=True时注册）：
1. 检查 `^[` 起始
2. 用 parseLinkLabel 解析到 `]`（支持嵌套方括号）
3. 创建新Token列表，调用 `state.md.inline.parse()` 解析content
4. 分配footnoteId，存储content和tokens到env.list
5. 输出 footnote_ref Token（meta={id}）

## Core规则：footnote_tail

footnote_tail是最复杂的后处理步骤：

### 第一步：收集脚注内容

遍历所有tokens：
- 遇到 `footnote_reference_open` → 开始收集，记录label
- 遇到 `footnote_reference_close` → 停止收集，将收集的tokens存入refTokens[":"+label]
- 过滤掉这些标记Token和它们之间的Token（tok_filter=False）

正文tokens中只保留非脚注定义的内容。

### 第二步：生成脚注列表

如果env.list不为空：
1. 输出 `footnote_block_open` Token → `<hr><section class="footnotes"><ol>`
2. 遍历env.list中每个脚注：
   - 输出 `footnote_open`（meta.id/meta.label）→ `<li id="fnN">`
   - 如果是行内脚注（有"tokens"键）：创建paragraph_open+inline(children)+paragraph_close
   - 如果是块级脚注（有"label"键）：从refTokens获取解析后的tokens
   - 输出 t 个 footnote_anchor（t=count，引用次数）→ 反向链接
   - 输出 `footnote_close` → `</li>`
3. 输出 `footnote_block_close` → `</ol></section>`

## 渲染规则

| Token类型 | 渲染输出 |
|-----------|---------|
| footnote_ref | `<sup class="footnote-ref"><a href="#fn{id}" id="fnref{refid}">[n]</a></sup>` |
| footnote_block_open | `<hr class="footnotes-sep">\n<section class="footnotes">\n<ol class="footnotes-list">\n` |
| footnote_block_close | `</ol>\n</section>\n` |
| footnote_open | `<li id="fn{id}" class="footnote-item">` |
| footnote_close | `</li>\n` |
| footnote_anchor | ` <a href="#fnref{id}" class="footnote-backref">↩︎</a>` |

辅助渲染规则：
- `footnote_anchor_name`：生成 `fn{id}` 格式的锚点名（docId支持）
- `footnote_caption`：生成 `[n]` 或 `[n:subId]` 格式的编号

## 多次引用处理

同一脚注被引用多次时：
- count递增
- 每个引用有独立的 subId
- 每个引用有独立的 fnref 锚点（`fnref1:0`, `fnref1:1`）
- 脚注项末尾生成多个 footnote_anchor（每个引用一个反向链接）

## 行内脚注 vs 块级脚注

| 特性 | 块级脚注 `[^n]` | 行内脚注 `^[content]` |
|------|----------------|---------------------|
| 定义位置 | 文档任意位置（`[^n]: content`） | 引用处内联 |
| 内容解析 | Block规则递归解析（支持多段落） | Inline规则解析（仅行内容器） |
| 标签 | 自定义label | 自动分配数字ID |
| 内容token来源 | refTokens（block解析结果） | 内联创建paragraph+inline |
