---
type: Concept
title: URL 与链接处理
description: markdown-it-py 的链接规范化、验证、安全过滤机制，以及对 mdurl 库的依赖
tags:
- markdown-it-py
- url
- link
- mdurl
- security
- normalize
difficulty: 高级
estimated_time: 10分钟
prerequisites:
- 09-inline-rules
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

# URL 与链接处理

markdown-it-py 通过 mdurl 库处理 URL 解析，并内置了链接规范化和安全验证机制。

## 三个核心链接方法

MarkdownIt 类提供三个链接处理方法：

| 方法 | 签名 | 作用 |
|------|------|------|
| `normalizeLink(url)` | `(str) → str` | 规范化URL（百分号编码、协议小写等） |
| `validateLink(url)` | `(str) → bool` | 验证URL安全性（阻止 javascript: 等XSS向量） |
| `normalizeLinkText(link)` | `(str) → str` | 规范化链接文本（实体解码等） |

这些方法在 link/image/autolink 规则中被调用，也可以被自定义规则和插件使用。

## normalizeLink——URL 规范化

normalizeLink 调用 mdurl 的 encode/decode 功能：
1. 解码已编码的字符（如 `%40` → `@`）
2. 对需要编码的字符重新编码
3. 主机名（域名）不进行百分号编码
4. 协议（scheme）小写化

```python
md.normalizeLink("HTTP://Example.COM/Path%20File")
# → "http://example.com/Path%20File"
```

## validateLink——XSS 防护

validateLink 是安全关键函数，用于阻止危险的 URL scheme：

- **允许的 scheme**：`http:`, `https:`, `ftp:`, `mailto:`, `tel:`, 以及相对路径（`/path`, `./path`, `//host/path`）、锚点（`#anchor`）
- **阻止的 scheme**：`javascript:`, `vbscript:`, `data:`（某些配置下）, `file:` 等可能执行代码的协议
- **处理逻辑**：
  1. 去除前导空白和控制字符
  2. 解码 HTML 实体和百分号编码
  3. 检查 scheme 是否在白名单中
  4. 无 scheme 的相对路径默认允许

```python
md.validateLink("https://example.com")   # True
md.validateLink("javascript:alert(1)")   # False
md.validateLink("/path/to/page")         # True（相对路径）
md.validateLink("#anchor")               # True（锚点）
```

> ⚠️ **安全提示**：validateLink 是默认的安全防线，但如果需要更严格的策略（如只允许 http/https），可以在渲染时额外检查或覆盖此方法。

## 链接解析辅助函数

`markdown_it/helpers/` 目录包含三个链接解析工具：

| 文件 | 函数 | 作用 |
|------|------|------|
| `parse_link_destination.py` | `parseLinkDestination()` | 解析链接目标（处理括号嵌套、尖括号URL） |
| `parse_link_label.py` | `parseLinkLabel()` | 解析链接标签（`[text]` 中的内容，最多999嵌套） |
| `parse_link_title.py` | `parseLinkTitle()` | 解析链接标题（双引号、单引号、括号包裹） |

这些函数遵循 CommonMark 的精确解析规则，处理各种边界情况。

## 链接引用机制

reference 块级规则收集链接引用定义到 `env.references`：
```python
# [label]: https://example.com "title"
env.references["label"] = {
    "href": "https://example.com",
    "title": "title",
    "label": "label"
}
```

标签通过 normalizeReference 规范化（小写化、空白合并），匹配时也对引用标签做相同规范化。

## 自定义链接处理

可以覆盖链接相关方法来自定义行为：

```python
import urllib.parse

class CustomMarkdownIt(MarkdownIt):
    def validateLink(self, url: str) -> bool:
        # 只允许 http/https 和相对路径
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme in ("http", "https", ""):
            return True
        return False

md = CustomMarkdownIt()
```

## 与 mdurl 的关系

markdown-it-py 运行时唯一依赖是 mdurl~=0.1，用于：
- URL 解析：`url_parse()` 将 URL 拆解为 protocol/auth/hostname/port/pathname/search/hash
- URL 格式化：`url_format()` 将 URL 重组为字符串
- URL 编码：`encode()` 百分号编码
- URL 解码：`decode()` 百分号解码

详细用法参见 [mdurl 文档](https://github.com/executablebooks/mdurl)。
