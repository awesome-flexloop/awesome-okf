---
type: Concept
title: Jinja2模板系统
description: rediraffe的重定向页面模板机制——默认模板结构、自定义模板变量、URL参数保留、模板加载时机
tags: [sphinxext-rediraffe, jinja2, template, redirect-page, url-parameters]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# Jinja2模板系统

rediraffe 使用 Jinja2 模板引擎渲染重定向HTML页面。默认提供一个功能完整的重定向模板，同时支持用户通过 `rediraffe_template` 配置项自定义模板。

## 默认模板分析

默认模板定义在源码中，是一个 `jinja2.Template` 对象：

```html
<html>
    <head>
        <noscript>
            <meta http-equiv="refresh" content="0; url={{rel_url}}"/>
        </noscript>
    </head>
    <body>
        <script>
            window.location.href = '{{rel_url}}' + (window.location.search || '') + (window.location.hash || '');
        </script>
        <p>You should have been redirected.</p>
        <a href="{{rel_url}}">If not, click here to continue.</a>
    </body>
</html>
```

### 三层降级策略

默认模板包含三层重定向机制，确保在各种环境下都能跳转：

1. **JavaScript 跳转（首选）**：
   ```javascript
   window.location.href = '{{rel_url}}' + (window.location.search || '') + (window.location.hash || '');
   ```
   - 保留查询参数（`?key=value`）和片段标识（`#section`）
   - 使用 `window.location.href` 跳转，浏览器记录历史（用户可返回）

2. **`<noscript>` + meta refresh（无JS降级）**：
   ```html
   <meta http-equiv="refresh" content="0; url={{rel_url}}"/>
   ```
   - 当JavaScript被禁用时，通过HTML meta标签实现跳转
   - `content="0"` 表示0秒后立即跳转
   - 缺点：**不保留URL参数和片段**（meta refresh的限制）

3. **手动点击链接（终极fallback）**：
   ```html
   <a href="{{rel_url}}">If not, click here to continue.</a>
   ```
   - 即使JS和meta refresh都不工作，用户仍可手动点击链接

### URL参数保留机制

默认模板的JavaScript代码中有一个重要细节：

```javascript
window.location.href = '{{rel_url}}' + (window.location.search || '') + (window.location.hash || '');
```

这行代码将当前页面的查询字符串（`window.location.search`）和片段标识（`window.location.hash`）附加到目标URL后面。例如：

- 用户访问 `old-page.html?utm_source=docs#section-2`
- 重定向到 `new-page.html?utm_source=docs#section-2`

这个特性通过测试用例验证：
- `test_pass_url_fragments`：验证 `#hash` 在跳转后保留
- `test_pass_url_queries`：验证 `?query` 在跳转后保留
- `test_pass_url_fragment_and_query`：验证 `?query#hash` 同时保留

## 模板可用变量

自定义模板中可以使用以下5个变量：

| 变量 | 类型 | 示例值 | 说明 |
|------|------|--------|------|
| `rel_url` | `str` | `../new-page.html` | 从重定向页面到目标页面的相对URL，用于`href`和`window.location` |
| `from_file` | `Path` | `old-page.rst` | 源文件的RST/MD路径（即配置中写的源路径） |
| `to_file` | `Path` | `new-page.rst` | 目标文件的RST/MD路径（即配置中写的目标路径） |
| `from_url` | `Path` | `old-page.html` 或 `old-page/index.html` | 源HTML路径（相对于outdir，已转换为构建器对应的格式） |
| `to_url` | `Path` | `new-page.html` 或 `new-page/index.html` | 目标HTML路径（相对于outdir） |

### 变量的实际值（html构建器）

以 `another.rst → index.rst` 为例：

| 变量 | 值 |
|------|-----|
| `rel_url` | `index.html` |
| `from_file` | `another.rst` |
| `to_file` | `index.rst` |
| `from_url` | `another.html` |
| `to_url` | `index.html` |

### 变量的实际值（dirhtml构建器）

同样的配置在 dirhtml 构建器下：

| 变量 | 值 |
|------|-----|
| `rel_url` | `../index.html` |
| `from_file` | `another.rst` |
| `to_file` | `index.rst` |
| `from_url` | `another/index.html` |
| `to_url` | `index.html` |

注意 `rel_url` 变为 `../index.html`，因为源文件在子目录 `another/` 中，需要回到上级目录。

### 嵌套目录下的变量值

以 `docs/folder1/tof1.rst → docs/folder1/f1.rst`（嵌套目录）为例：

**html构建器**：
| 变量 | 值 |
|------|-----|
| `rel_url` | `f1.html` |
| `from_url` | `docs/folder1/tof1.html` |
| `to_url` | `docs/folder1/f1.html` |

**dirhtml构建器**：
| 变量 | 值 |
|------|-----|
| `rel_url` | `f1/index.html` |
| `from_url` | `docs/folder1/tof1/index.html` |
| `to_url` | `docs/folder1/f1/index.html` |

## 自定义模板

### 配置方式

在 `conf.py` 中指定模板文件路径：

```python
rediraffe_template = 'rediraffe_template.html'
```

路径相对于 Sphinx 源目录（`conf.py` 所在目录）。

### 模板加载机制

```python
rediraffe_template = app.config.rediraffe_template
if isinstance(rediraffe_template, str):
    template_path = Path(app.srcdir) / rediraffe_template
    if template_path.exists():
        file_loader = FileSystemLoader(template_path.parent)
        env = Environment(loader=file_loader)
        rediraffe_template = env.get_template(template_path.name)
    else:
        logger.warning('rediraffe: rediraffe_template does not exist. The default will be used.')
        rediraffe_template = DEFAULT_REDIRAFFE_TEMPLATE
else:
    rediraffe_template = DEFAULT_REDIRAFFE_TEMPLATE
```

关键细节：
- 使用 `FileSystemLoader` 加载模板，模板文件的父目录作为模板搜索路径
- 模板文件**在 build-finished 阶段才被读取**，可以在构建过程中动态生成
- 如果模板文件不存在，输出警告并回退到默认模板（不会构建失败）

### 自定义模板示例

#### 示例1：品牌定制的重定向页面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>页面已移动 - My Project</title>
    <meta http-equiv="refresh" content="3; url={{rel_url}}">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 600px;
            margin: 100px auto;
            padding: 40px;
            text-align: center;
            background: #f5f5f5;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; font-size: 24px; }
        p { color: #666; line-height: 1.6; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .countdown { font-weight: bold; color: #0066cc; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📄 页面已移动</h1>
        <p>此页面已移至新位置。</p>
        <p><span class="countdown" id="countdown">3</span> 秒后自动跳转到新页面...</p>
        <p><a href="{{rel_url}}">立即跳转 →</a></p>
    </div>
    <script>
        var seconds = 3;
        var el = document.getElementById('countdown');
        var timer = setInterval(function() {
            seconds--;
            el.textContent = seconds;
            if (seconds <= 0) {
                clearInterval(timer);
                window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
            }
        }, 1000);
    </script>
    <noscript>
        <meta http-equiv="refresh" content="3; url={{rel_url}}">
        <p><a href="{{rel_url}}">点击这里跳转到新页面</a></p>
    </noscript>
</body>
</html>
```

这个模板的特点：
- 3秒延迟跳转（给用户阅读提示的时间）
- 倒计时显示
- 品牌化的UI样式
- 使用 `window.location.replace()`（不保留重定向页在浏览器历史中）

#### 示例2：SEO友好的重定向页面

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Page Moved</title>
    <link rel="canonical" href="{{rel_url}}">
    <meta http-equiv="refresh" content="0; url={{rel_url}}">
    <meta name="robots" content="noindex">
</head>
<body>
    <script>
        window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
    </script>
    <p>This page has moved. If you are not redirected, <a href="{{rel_url}}">click here</a>.</p>
</body>
</html>
```

SEO要点：
- `<link rel="canonical">` 告诉搜索引擎目标页面是规范URL
- `<meta name="robots" content="noindex">` 防止重定向页面被索引
- `window.location.replace()` 从浏览器历史中移除重定向页面

## 模板渲染过程

模板在 `build_redirects` 函数中被渲染：

```python
with build_redirect_from.open('w', encoding='utf-8') as f:
    f.write(
        rediraffe_template.render(
            rel_url=str(PurePosixPath(PureWindowsPath(
                relpath(build_redirect_to, build_redirect_from.parent)
            ))),
            from_file=src_redirect_from,
            to_file=src_redirect_to,
            from_url=redirect_from,
            to_url=redirect_to,
        )
    )
```

关键路径计算：
1. `relpath(build_redirect_to, build_redirect_from.parent)`：计算从源HTML所在目录到目标HTML的相对路径（OS原生格式）
2. `PureWindowsPath(...)`：将路径标准化为Windows格式（处理反斜杠）
3. `PurePosixPath(...)`：转换为POSIX格式（正斜杠），确保URL中使用正斜杠
4. `str(...)`：最终转为字符串

这种"Windows→POSIX"的双重转换确保了在Windows、Linux、macOS上生成的URL路径都使用正斜杠。

## Jinja2测试验证

测试用例 `test_jinja` 验证自定义模板的变量值正确：

```python
# html构建器
assert 'rel_url: index.html' in text
assert 'from_file: another.rst' in text
assert 'to_file: index.rst' in text
assert 'from_url: another.html' in text
assert 'to_url: index.html' in text

# dirhtml构建器
assert 'rel_url: ../index.html' in text
assert 'from_url: another/index.html' in text
```

## 相关概念

- [Builder体系详解](/concepts/05-builders.md)
- [路径处理与跨平台兼容](/concepts/07-path-and-cross-platform.md)
- [自定义Jinja模板示例](/examples/custom-jinja-template.md)
- [基础重定向示例](/examples/basic-redirects.md)
