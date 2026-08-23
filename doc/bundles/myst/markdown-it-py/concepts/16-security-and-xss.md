---
type: Concept
title: 安全与 XSS 防护
description: markdown-it-py 的 HTML 处理选项、validateLink XSS防护机制、安全使用建议
tags:
- markdown-it-py
- security
- xss
- html
- sanitization
difficulty: 高级
estimated_time: 10分钟
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# 安全与 XSS 防护

使用 Markdown 解析器时，需要关注 XSS（跨站脚本）攻击风险。markdown-it-py 提供了多层防护。

## HTML 选项控制

| 选项 | commonmark | default | 效果 |
|------|-----------|---------|------|
| `html=True` | ✅ | ❌ | 允许源码中的 HTML 标签原样输出 |
| `html=False` | ❌ | ✅ | HTML 标签被转义为文本（`<` → `&lt;`） |

**面向不可信输入时，务必设置 `html=False`**：

```python
# 安全：用户输入的HTML被转义
md = MarkdownIt("commonmark", {"html": False})
```

commonmark 预设默认 `html=True`（因为 CommonMark 规范允许原始 HTML），但面向用户生成内容时建议关闭。

## validateLink——链接协议过滤

链接是 XSS 的主要向量之一：

```markdown
``[click](javascript:alert('xss')``)
```

`validateLink(url)` 方法过滤危险协议：
- ✅ 允许：`http:`, `https:`, `ftp:`, `mailto:`, `tel:`
- ✅ 允许：相对路径（`/path`, `./path`）、锚点（`#id`）
- ❌ 阻止：`javascript:`, `vbscript:`, `data:` 等

validateLink 在 link/image/autolink 规则中被调用，验证失败时链接不会输出为 `<a href>`，而是转为文本或 `<a>` 无 href。

### 更严格的链接策略

如果只允许 http/https：

```python
class SafeMarkdownIt(MarkdownIt):
    def validateLink(self, url: str) -> bool:
        import urllib.parse
        parsed = urllib.parse.urlparse(url.strip())
        if not parsed.scheme:
            return True  # 相对路径
        return parsed.scheme in ("http", "https")

md = SafeMarkdownIt("commonmark", {"html": False})
```

## 代码块安全

代码块（fence/code_block）中的内容会被 HTML 转义输出，`<script>` 等标签不会执行。但如果使用自定义 `highlight` 函数，需要确保高亮器不会输出未转义的恶意代码。

## 图片安全

`!`url`` 中的 URL 同样经过 validateLink 检查。注意 `data:` URI 图片：
- 可以包含 base64 编码的任意内容
- 默认 validateLink 通常允许（某些版本）
- 如需严格控制，在自定义 validateLink 中加入 `data:` 黑名单

## 推荐的安全配置

```python
md = MarkdownIt("commonmark", {
    "html": False,           # 禁用原始HTML
    "linkify": False,        # 谨慎开启自动链接
})

# 或使用自定义类覆盖 validateLink
```

如果需要更全面的 HTML 净化（即使 html=True 也安全），推荐在渲染后使用 HTML 净化库（如 bleach）进行后处理。

## 安全总结

| 攻击向量 | 默认防护 | 建议 |
|---------|---------|------|
| 原始HTML | commonmark允许，default禁用 | 不可信输入设 html=False |
| javascript:链接 | validateLink阻止 | 可自定义更严格策略 |
| data:URI | 视版本而定 | 考虑加入黑名单 |
| HTML属性注入 | attrs值被转义 | 自定义渲染时注意转义 |
| 代码块内容 | 自动转义 | highlight函数需注意 |
