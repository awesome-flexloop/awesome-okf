---
type: Reference
title: mdformat-myst 指令格式化模块
description: _directives.py 实现 MyST 指令选项 YAML 格式化和 fence 渲染覆写。
tags: [source-code, myst, directive, yaml, formatting]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-directives
    resource: /spec/facts.md
    title: mdformat-myst 事实清单
---

## 模块概览

`mdformat_myst/_directives.py` 实现 MyST 指令（directive）的代码围栏渲染和选项 YAML 格式化（139行）。

## 核心函数

### `fence(node, context) -> str`

fence token 的渲染函数，从 mdformat 上游复制并仅添加了两行代码：当 info 字符串以 `{` 开头、以 `}` 结尾时识别为 MyST 指令，调用 `format_directive_content` 格式化选项 YAML。

### `format_directive_content(raw_content: str) -> str`

格式化指令内容：
1. 调用 `parse_opts_and_content` 分离 YAML 选项和正文内容
2. 使用 ruamel.yaml 解析并重新序列化 YAML，实现缩进规范化
3. 移除 ruamel.yaml 自动添加的 YAML 结束标记 `\n...\n`
4. 空 YAML（`null\n`）精简为空字符串
5. 用 `---` 包裹格式化后的 YAML，追加正文内容

### `parse_opts_and_content(raw_content: str) -> tuple[str, str] | None`

解析指令内容的两种选项格式：

1. **YAML 围栏格式**：以 `---`（≥3个连字符）开头和结尾包裹的 YAML 块
2. **冒号选项格式**：以 `:` 开头的选项行，每行一个键值对

返回 `(yaml_content, body_content)` 元组，若无法解析则返回 `None`。

### `render_fence_html(self, tokens, idx, options, env) -> str`

返回空字符串的桩函数，用于覆盖 fence/code_block 的 HTML 渲染规则，绕过 mdformat 的 CommonMark AST 验证。

### `longest_consecutive_sequence(seq: str, char: str) -> int`

工具函数，返回字符串中指定字符的最长连续出现次数，用于确定围栏字符长度（避免与内容冲突）。

## YAML 配置

ruamel.yaml 配置为：
- mapping 缩进：2空格
- sequence 缩进：4空格
- offset：2

## 源码位置

- 文件路径：`mdformat_myst/_directives.py`
- 代码行数：139行

## 相关概念

- [指令选项 YAML 格式化](/concepts/03-directive-formatting.md)
