---
type: Example
title: 常见问题排查
description: sphinxcontrib-jsmath 使用中的常见错误、症状、原因分析与解决方案
tags: [sphinxcontrib-jsmath, example, troubleshooting, errors, debug, faq]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 常见问题排查

本页汇总 sphinxcontrib-jsmath 使用过程中的常见问题、诊断方法和解决方案。

## 错误：ExtensionError - jsmath_path must be set

### 症状

构建时抛出异常：

```
sphinx.errors.ExtensionError: jsmath_path config value must be set for the jsmath extension to work
```

### 原因

`conf.py` 中未设置 `jsmath_path`，或设置为空字符串。这个错误在 `install_jsmath` 函数中主动抛出，防止用户忘记配置路径后页面无法渲染数学公式。

### 解决方案

在 `conf.py` 中设置 `jsmath_path`：

```python
jsmath_path = '_static/jsMath/easy/load.js'
```

确保路径指向实际存在的 jsMath 加载器脚本。

## 问题：页面显示原始 LaTeX 代码

### 症状

浏览器打开页面后，数学公式显示为原始 LaTeX 代码（如 `E = mc^2`），而非排版后的数学公式。

### 可能原因与排查步骤

**1. jsMath 脚本未加载**

打开浏览器开发者工具（F12）→ Network 面板，刷新页面，检查 jsmath.js 或 load.js 是否返回 404。

如果 404：
- 检查 `jsmath_path` 路径是否正确（相对于 HTML 输出目录）
- 检查 jsMath 文件是否已复制到 `_static/` 目录
- 如果使用 `html_static_path`，确认 `_static` 在列表中

**2. JavaScript 被禁用**

检查浏览器是否禁用了 JavaScript。jsMath 完全依赖浏览器端 JS 渲染。

**3. jsMath 字体未加载**

如果脚本加载但公式显示为乱码或空白：
- 检查 jsMath/fonts/ 目录是否完整
- 打开浏览器 Console 面板查看是否有字体加载错误
- 尝试使用 `easy/load.js`（自动加载配置）而非直接引用 `jsmath.js`

**4. CSS class 不匹配**

检查 HTML 源码确认公式被包裹在 `class="math"` 元素中。如果不在，可能是 math renderer 未正确注册——确认 `extensions` 列表包含 `'sphinxcontrib.jsmath'`。

## 问题：jsMath.js 在无公式页面中出现（或不出现）

### 症状A：无公式页面也加载了 jsmath.js

这通常不是 sphinxcontrib-jsmath 的问题——sphinxcontrib-jsmath 从 1.0.1 版本开始已修复此问题（CHANGES.rst 记录："jsmath has not been loaded on incremental build"）。

如果仍然出现，检查：
- 是否有其他扩展也在添加 jsmath.js？
- 是否自定义模板中硬编码了 `<script>` 标签？

### 症状B：有公式页面没有加载 jsmath.js

1. 确认使用的是 HTML builder（`-b html`）
2. 确认 math renderer 是 jsmath 而非 MathJax（如果 `extensions` 中同时包含 `sphinx.ext.mathjax`，可能被 MathJax 覆盖）
3. 检查 `domain.has_equations()` 是否正确检测到公式——确认公式使用了正确的 rst 语法（`.. math::` 或 `` :math:``）

## 问题：与 MathJax 冲突

### 症状

同时启用了 `sphinx.ext.mathjax` 和 `sphinxcontrib.jsmath`，公式渲染异常或不渲染。

### 原因

Sphinx 同一时间只能使用一个 HTML math renderer。如果两个扩展都注册了 math renderer，行为取决于注册顺序和 Sphinx 内部选择逻辑。

### 解决方案

只启用一个数学渲染扩展：

```python
# 二选一：
extensions = ['sphinxcontrib.jsmath']     # 使用 jsMath
# 或
extensions = ['sphinx.ext.mathjax']        # 使用 MathJax（推荐用于现代项目）
```

## 问题：增量构建时公式不渲染

### 症状

首次完整构建时公式正常渲染，但修改文档后增量构建（`sphinx-build` 不使用 `-E` 参数）时公式显示为原始代码。

### 原因

这是 sphinxcontrib-jsmath 1.0.0 版本的已知 Bug（CHANGES.rst 记录："jsmath has not been loaded on incremental build"）。在增量构建时，`env-updated` 事件可能未正确触发或 `has_equations()` 返回错误结果。

### 解决方案

- 升级到 sphinxcontrib-jsmath >= 1.0.1（此 Bug 已修复）
- 如果无法升级，使用 `-E` 参数强制完全重建：`sphinx-build -E -b html . _build/html`

## 问题：公式编号不正确

### 症状

公式编号不是预期的 `(1), (2), (3)...` 或 `(1.1), (1.2)...` 格式。

### 排查

**编号不按章节分组（没有 1.1 格式）：**
- 需要设置 `numfig = True` 和 `math_numfig = True`
- 确认文档使用了正确的章节结构（`==` 下划线的标题作为章节分隔）

**编号从非1开始：**
- 清除构建缓存后重新构建：`sphinx-build -E -b html . _build/html`
- 删除 `_build/` 目录后完全重建

**有标签的公式没有编号：**
- 标签名称不能重复，重复标签会导致编号异常
- 标签名称中不要使用特殊字符

## 问题：构建速度慢

### 症状

使用 jsmath 后 HTML 构建明显变慢。

### 分析

sphinxcontrib-jsmath 本身是轻量级扩展，不会显著影响构建速度。如果构建变慢，可能是：

1. **大量公式导致解析时间增加**：这不是 jsmath 的问题，而是 Sphinx MathDomain 处理公式本身的开销
2. **静态文件复制**：jsMath 字体文件较多（数十个文件），首次构建时需要复制到输出目录
3. **并行构建未启用**：使用 `-j auto` 启用并行构建（jsmath 支持 `parallel_read_safe=True` 和 `parallel_write_safe=True`）

### 优化

```bash
# 启用并行构建
sphinx-build -j auto -b html . _build/html
```

## 问题：特殊字符显示异常

### 症状

公式中的 `<`、`>`、`&` 等字符显示异常或被解释为 HTML。

### 原因

sphinxcontrib-jsmath 使用 `self.encode()` 对公式内容进行 HTML 实体编码：
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`

jsMath 在解析时会正确处理这些实体。如果显示异常，可能是：
- 自定义模板或其他扩展绕过了编码
- 浏览器在 jsMath 处理前将实体渲染为 HTML 标签

## 诊断检查清单

遇到问题时，按以下顺序检查：

1. **版本检查**：`pip show sphinxcontrib-jsmath` 确认版本 >= 1.0.1
2. **Sphinx版本**：确认 Sphinx >= 5.0（`sphinx-build --version`）
3. **配置检查**：`jsmath_path` 已设置且路径正确
4. **扩展列表**：`extensions` 中包含 `'sphinxcontrib.jsmath'`，且不与 `sphinx.ext.mathjax` 冲突
5. **构建模式**：使用 `sphinx-build -b html`（非 LaTeX/PDF 等其他格式）
6. **文件存在**：jsMath JS 和字体文件在 `_static/` 目录中
7. **HTML验证**：查看输出 HTML 源码，确认公式在 `class="math"` 元素中，页面包含 jsMath script 标签
8. **完全重建**：`rm -rf _build/ && sphinx-build -E -b html . _build/html`
9. **浏览器控制台**：打开 F12 → Console，查看是否有 JavaScript 错误

## 测试验证方法

项目测试用例提供了验证扩展功能的参考方法：

```python
# 使用 sphinx.testing.fixtures 进行测试
@pytest.mark.sphinx('html', testroot='basic')
def test_my_docs(app):
    app.builder.build_all()
    content = (app.outdir / 'math.html').read_text(encoding='utf-8')
    # 验证公式渲染
    assert '<div class="math notranslate nohighlight">' in content
    # 验证JS加载
    assert 'jsmath.js' in content  # 或你的 jsmath_path 文件名
```

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [智能JS加载机制](/concepts/04-smart-js-loading.md)
- [数学节点访问者](/concepts/03-math-node-visitors.md)
- [基础使用示例](/examples/basic-usage.md)
- [公式编号与引用](/examples/equation-numbering.md)
