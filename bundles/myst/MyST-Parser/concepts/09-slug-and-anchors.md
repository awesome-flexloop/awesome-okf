---
type: Concept
title: Slug 与标题锚点
description: 三种 slug 预设算法（github/gitlab/docutils）、标题锚点自动生成、unique_slug 去重
tags: [myst, sphinx, slug, anchor, heading, id, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## Slug 与标题锚点

MyST-Parser 通过 `myst_heading_anchors` 配置自动为标题生成 HTML 锚点（ID），支持三种预设的 slug 生成算法。

## 启用标题锚点

```python
# conf.py
myst_heading_anchors = 3  # 为 H1-H3 生成锚点
myst_heading_slug_func = "github"  # 使用 GitHub 风格 slug（默认）
```

`myst_heading_anchors` 接受 0-7 的整数值：
- `0`：不生成自动锚点（默认）
- `1`-`7`：为该级别及以上标题生成锚点

## 三种 Slug 预设

### github_slugify（默认）

算法步骤：
1. 标题文本转为小写
2. 空格替换为连字符 `-`
3. 移除非 word 字符、非 CJK 汉字（U+4E00-U+9FFF）、非连字符、非空格的字符
4. **保留首尾空格生成的连字符**（如 `" a b "` → `"-a-b-"`）

```python
from myst_parser.slugs import github_slugify
github_slugify("Hello World!")  # "hello-world"
github_slugify(" a b ")         # "-a-b-"（保留首尾连字符）
```

### gitlab_slugify

算法步骤：
1. strip 后转为小写
2. 移除非 word 字符、非连字符、非空格
3. 空格替换为 `-`
4. 压缩连续 `-` 为单个
5. 纯数字结果添加 `anchor-` 前缀

```python
from myst_parser.slugs import gitlab_slugify
gitlab_slugify("Hello World!")   # "hello-world"
gitlab_slugify("123")            # "anchor-123"
```

### docutils_slugify

与 `docutils.nodes.make_id` 字节一致，确保混合 RST + Markdown 项目中锚点统一：

算法步骤：
1. 小写
2. 二合字母映射（ß→sz、æ→ae、œ→oe 等）
3. 33 个特殊拉丁字母映射（ø→o、đ→d 等）
4. NFKD 规范化，去除非 ASCII 字符
5. 非字母数字字符合并为 `-`
6. 去除首尾数字/连字符和尾部连字符

```python
from myst_parser.slugs import docutils_slugify
docutils_slugify("Hello World!")  # "hello-world"
docutils_slugify("中文标题")       # ""（空，无拉丁字母则无锚点）
```

### 预设注册表

三种预设注册在 `SLUG_PRESETS` 字典中：

```python
SLUG_PRESETS = {
    "docutils": docutils_slugify,
    "github": github_slugify,
    "gitlab": gitlab_slugify,
}
```

## 自定义 Slug 函数

除了预设名，`myst_heading_slug_func` 还接受：

**可调用对象**：
```python
def my_slugify(title: str) -> str:
    return title.lower().replace(" ", "-")

myst_heading_slug_func = my_slugify
```

**Python 导入路径**（遗留格式）：
```python
myst_heading_slug_func = "my_package.my_module.my_slugify"
```

## 锚点去重

`unique_slug(slug, existing)` 函数处理重复锚点：

```python
unique_slug("section", {"section"})  # "section-1"
unique_slug("section", {"section", "section-1"})  # "section-2"
```

规则：重复 slug 追加 `-1`、`-2` 后缀，基础 slug 不变。

## HTML ID 输出

`myst_heading_anchors_html_ids`（默认 True）控制是否将 slug 同时作为 HTML `id` 属性输出：

```html
<!-- myst_heading_anchors_html_ids=True -->
<h2 id="hello-world">Hello World</h2>
```

设为 False 时仅在 docutils 层面生成 ID，不输出 HTML id 属性。

## myst-anchors CLI

`myst-anchors` 命令行工具从 Markdown 文件提取标题锚点：

```bash
# 从 stdin 读取
cat file.md | myst-anchors

# 从文件读取
myst-anchors input.md -o output.html

# 指定最大标题级别
myst-anchors -l 4 file.md

# 指定 slug 函数
myst-anchors --slug-func gitlab file.md
```

参数：
- `input`：输入文件（默认 stdin）
- `-o, --output`：输出文件（默认 stdout）
- `-l, --level`：最大标题级别（默认 2）
- `--slug-func`：slug 预设（github/gitlab/docutils，默认 github）

## 显式锚点优先

除了自动锚点，还可以通过 MyST 标签语法显式定义锚点：

```markdown
(my-custom-label)=
## 我的标题

引用方式：[跳转](#my-custom-label)
```

显式标签通过 `PrioritiseExplicitIds` Transform 优先于自动锚点。

## 相关概念

- [配置系统](/concepts/04-config-system.md)
- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [CLI 工具](/concepts/10-cli-tools.md)
