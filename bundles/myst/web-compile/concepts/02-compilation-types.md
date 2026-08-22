---
type: Concept
title: 三种编译类型
description: web-compile支持的三种编译能力详解：SCSS→CSS编译、JS压缩、Jinja2模板渲染
tags: [web, compile, sass, scss, css, javascript, minify, jinja2, template]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:22:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-source
    resource: /references/compile-source.md
    title: web-compile 源码路径映射
---

# 三种编译类型

web-compile 按顺序执行三种编译：SASS → JS → Jinja。每个编译管线独立执行。

## 1. SASS/SCSS 编译

将 SCSS/SASS 文件编译为 CSS。使用 `libsass`（Python `sass` 包）实现。

### 基本用法

```yaml
sass_files:
  src/style.scss: dist/style.css
```

### 输出格式

通过 `--sass-format` 指定：

| 格式 | 适用场景 | 示例 |
|------|---------|------|
| `compressed` | 生产环境（默认） | `body{color:red}` |
| `expanded` | 开发调试 | 多行格式化CSS |
| `compact` | 紧凑但可读 | 每条规则一行 |
| `nested` | SCSS风格缩进 | 反映嵌套层级 |

```bash
# 开发时使用expanded便于调试
web-compile --sass-format expanded

# 生产使用compressed最小化
web-compile --sass-format compressed
```

### Source Map

启用Source Map以便浏览器调试时映射回SCSS源文件：

```bash
web-compile --sass-sourcemap
```

生成 `.map.json` 文件，CSS末尾包含sourceMappingURL。

### 精度控制

```bash
web-compile --sass-precision 8
```

控制数值精度（默认5），如 `10px / 3` 保留小数位数。

### [hash]文件名

```yaml
sass_files:
  src/style.scss: dist/style.[hash].css
```

编译后文件名变为 `dist/style.a1b2c3d4.css`，哈希基于CSS内容。SCSS中`@import`的文件变化也会导致哈希变化。

### include_paths

默认包含源文件所在目录。如果引用了其他目录的SCSS文件（如node_modules中的SCSS），需要确保路径正确。

## 2. JavaScript 压缩

使用 `rjsmin` 库压缩JavaScript文件，去除空白、注释，缩短变量名（rjsmin主要去除空白和注释）。

### 基本用法

```yaml
js_files:
  src/app.js: dist/app.min.js
```

### 保留版权注释

```bash
web-compile --js-comments
```

保留以 `/*!` 开头的特殊注释（通常是版权声明）：

```javascript
/*!
 * My Library v1.0.0
 * Copyright 2024 Author
 * License: MIT
 */
function hello() { console.log("hello"); }
```

压缩后版权注释保留，其他注释和空白被移除。

### [hash]文件名

```yaml
js_files:
  src/app.js: dist/app.[hash].min.js
```

编译后变为 `dist/app.e5f6g7h8.min.js`。

## 3. Jinja2 模板渲染

使用 Jinja2 引擎渲染模板文件，支持变量注入。常用于HTML模板、配置文件生成等。

### 基本用法

```yaml
jinja_files:
  src/template.html: dist/output.html
jinja_variables:
  app_name: "My App"
  version: "1.0.0"
  debug: false
```

模板文件 `src/template.html`：

```html
<!DOCTYPE html>
<html>
<head>
  <title>{{ app_name }} v{{ version }}</title>
</head>
<body>
  {% if debug %}
  <div class="debug-banner">Debug Mode</div>
  {% endif %}
  <h1>Welcome to {{ app_name }}</h1>
</body>
</html>
```

编译后 `dist/output.html`：

```html
<!DOCTYPE html>
<html>
<head>
  <title>My App v1.0.0</title>
</head>
<body>
  <h1>Welcome to My App</h1>
</body>
</html>
```

### Jinja2 常用语法

- `{{ variable }}`：变量输出
- `{% if %}...{% endif %}`：条件判断
- `{% for item in items %}...{% endfor %}`：循环
- `{{ variable | filter }}`：过滤器（如 `{{ name | upper }}`）
- `{# comment #}`：注释（不会出现在输出中）

### 在模板中引用[hash]文件名

Jinja2渲染在SASS和JS编译**之后**执行，因此可以在Jinja变量中传递实际的哈希文件名。但web-compile本身不在Jinja变量中自动填充哈希文件名——你需要通过其他方式（如自定义构建脚本）实现。

## 编译执行顺序

```
1. compile_sass()   → 生成CSS（含[hash]文件名）
2. minify_js()      → 生成压缩JS（含[hash]文件名）
3. compile_jinja()  → 渲染模板（可使用jinja_variables）
```

三个步骤独立执行，每步的错误都会被收集。默认遇到错误立即停止，使用 `--continue-on-error` 继续处理后续文件。

## 文件变更检测

每次编译时：
1. 读取源文件，编译/压缩/渲染得到输出内容
2. 如果目标文件已存在且内容相同，跳过（无变更）
3. 如果内容不同或文件不存在，写入文件（标记为变更）
4. 只有真正有变更才会触发git add和非零退出码

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [配置文件详解](/concepts/03-configuration.md)
- [CI集成](/concepts/04-ci-integration.md)
- [资产编译流水线示例](/examples/asset-pipeline.md)
