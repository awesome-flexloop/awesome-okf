---
type: Example
title: 自定义Jinja模板
description: 定制rediraffe的重定向页面外观——品牌化页面、SEO优化、倒计时提示、自定义样式
tags: [sphinxext-rediraffe, jinja2, template, custom-template, seo, branding]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 自定义Jinja模板

本示例演示如何使用自定义Jinja2模板来定制重定向页面的外观和行为。

## 模板变量回顾

自定义模板中可用的变量：

| 变量 | 类型 | 说明 |
|------|------|------|
| `rel_url` | `str` | 到目标页面的相对URL（用于href和JS跳转） |
| `from_file` | `Path` | 源文件路径（如 `old-page.rst`） |
| `to_file` | `Path` | 目标文件路径（如 `new-page.rst`） |
| `from_url` | `Path` | 源HTML路径（如 `old-page.html`） |
| `to_url` | `Path` | 目标HTML路径（如 `new-page.html`） |

## 配置自定义模板

```python
# conf.py
extensions = ['sphinxext.rediraffe']

rediraffe_redirects = 'redirects.txt'
rediraffe_template = '_templates/redirect.html'  # 相对于源目录
```

模板文件路径相对于Sphinx源目录（`conf.py` 所在目录）。

## 示例1：品牌化重定向页面

创建 `_templates/redirect.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>页面已移动 - My Project</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 48px;
            max-width: 480px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        .icon { font-size: 64px; margin-bottom: 24px; }
        h1 { color: #333; font-size: 24px; margin-bottom: 16px; }
        p { color: #666; line-height: 1.6; margin-bottom: 24px; }
        .countdown {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin: 16px 0;
        }
        a {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
        }
        a:hover { background: #5a67d8; }
    </style>
    <noscript>
        <meta http-equiv="refresh" content="5; url={{rel_url}}">
    </noscript>
</head>
<body>
    <div class="card">
        <div class="icon">📄</div>
        <h1>页面已移动</h1>
        <p>此页面已移至新位置，我们正在为您跳转...</p>
        <div class="countdown"><span id="sec">5</span> 秒后自动跳转</div>
        <p><a href="{{rel_url}}">立即跳转 →</a></p>
    </div>
    <script>
        var sec = 5;
        var el = document.getElementById('sec');
        var timer = setInterval(function() {
            sec--;
            el.textContent = sec;
            if (sec <= 0) {
                clearInterval(timer);
                window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
            }
        }, 1000);
    </script>
</body>
</html>
```

特点：
- 5秒倒计时（给用户阅读时间）
- 品牌化紫色渐变背景
- 响应式设计
- 三层降级（JS跳转→meta refresh→手动链接）
- 使用 `location.replace()` 不保留重定向页在浏览器历史中
- 保留URL参数和hash

## 示例2：SEO优化模板

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <!-- SEO: 告诉搜索引擎目标页面是规范URL -->
    <link rel="canonical" href="{{rel_url}}">
    <!-- SEO: 不要索引此重定向页面 -->
    <meta name="robots" content="noindex, follow">
    <!-- 立即跳转（0秒） -->
    <meta http-equiv="refresh" content="0; url={{rel_url}}">
</head>
<body>
    <script>
        // 立即跳转，保留URL参数
        window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
    </script>
    <p>This page has moved. If you are not redirected, <a href="{{rel_url}}">click here</a>.</p>
</body>
</html>
```

SEO要点：
- `<link rel="canonical">`：告诉搜索引擎目标URL是规范地址
- `<meta name="robots" content="noindex, follow">`：不索引重定向页，但跟随链接
- `window.location.replace()`：从历史记录中移除重定向页
- 0秒跳转：减少用户等待

## 示例3：调试/信息展示模板

用于开发和调试，展示所有模板变量：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirect Debug</title>
    <style>
        body { font-family: monospace; max-width: 800px; margin: 40px auto; padding: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #f5f5f5; }
        .var { color: #0066cc; font-weight: bold; }
        .val { color: #333; }
    </style>
    <noscript>
        <meta http-equiv="refresh" content="0; url={{rel_url}}">
    </noscript>
</head>
<body>
    <h1>🔄 Redirect Information</h1>
    <table>
        <tr><th>Variable</th><th>Value</th></tr>
        <tr><td class="var">rel_url</td><td class="val">{{rel_url}}</td></tr>
        <tr><td class="var">from_file</td><td class="val">{{from_file}}</td></tr>
        <tr><td class="var">to_file</td><td class="val">{{to_file}}</td></tr>
        <tr><td class="var">from_url</td><td class="val">{{from_url}}</td></tr>
        <tr><td class="var">to_url</td><td class="val">{{to_url}}</td></tr>
    </table>
    <p>Redirecting to <a href="{{rel_url}}">{{rel_url}}</a>...</p>
    <script>
        setTimeout(function() {
            window.location.href = '{{rel_url}}' + window.location.search + window.location.hash;
        }, 3000);
    </script>
</body>
</html>
```

## 示例4：Apache/.htaccess 风格重定向页

简洁的传统风格：

```html
<!DOCTYPE html>
<html>
<head>
    <title>301 Moved Permanently</title>
    <meta http-equiv="refresh" content="0; url={{rel_url}}">
</head>
<body>
    <h1>301 Moved Permanently</h1>
    <p>The document has moved <a href="{{rel_url}}">here</a>.</p>
    <script>
        window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
    </script>
</body>
</html>
```

## 模板最佳实践

### 1. 始终包含三层降级

好的重定向页面应包含三层机制：

```html
<!-- 1. JavaScript跳转（首选，可保留URL参数） -->
<script>
    window.location.replace('{{rel_url}}' + window.location.search + window.location.hash);
</script>

<!-- 2. noscript meta refresh（无JS降级） -->
<noscript>
    <meta http-equiv="refresh" content="0; url={{rel_url}}">
</noscript>

<!-- 3. 手动链接（终极fallback） -->
<p><a href="{{rel_url}}">Click here if you are not redirected</a>.</p>
```

### 2. 保留URL参数

始终将 `window.location.search` 和 `window.location.hash` 附加到目标URL：

```javascript
window.location.href = '{{rel_url}}' + (window.location.search || '') + (window.location.hash || '');
```

这确保用户访问 `old-page.html?utm_source=docs#section-2` 时，参数不会丢失。

### 3. 使用location.replace()

使用 `window.location.replace()` 而非 `window.location.href`：

```javascript
// ✅ 推荐：replace()不保留重定向页在浏览器历史中
window.location.replace(url);

// ❌ 不推荐：href会让用户按返回按钮回到重定向页
window.location.href = url;
```

### 4. 模板可以在构建时生成

模板文件在 `build-finished` 阶段才被读取，所以可以在构建过程中动态生成：

```python
# 可以在其他扩展或conf.py中动态生成模板
# 例如根据项目配置生成品牌化模板
```

### 5. 模板不存在时的回退

如果模板文件不存在，rediraffe 会输出警告并使用默认模板：

```
rediraffe: rediraffe_template does not exist. The default will be used.
```

构建不会失败，但会使用内置默认模板。

## 测试自定义模板

```bash
# 构建后检查生成的重定向页面
sphinx-build -b html . _build/html

# 查看生成的重定向页面内容
cat _build/html/old-page.html

# 用浏览器验证（包含Selenium测试参考tests/test_ext.py中的test_jinja）
```

## 相关概念

- [Jinja2模板系统](../concepts/06-jinja-templates.md)
- [配置项详解](../concepts/04-configuration.md)
- [基础重定向配置](basic-redirects.md)
