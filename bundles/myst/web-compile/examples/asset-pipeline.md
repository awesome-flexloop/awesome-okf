---
type: Example
title: 资产编译流水线
description: 使用web-compile构建Sphinx主题和文档站点静态资源的完整示例，包括配置、CI集成和开发工作流
tags: [web, compile, example, sphinx, theme, asset-pipeline, ci]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:28:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-source
    resource: /references/compile-source.md
    title: web-compile 源码路径映射
---

# 资产编译流水线

## 示例1：Sphinx主题资产编译

为一个Sphinx主题项目设置完整的资产编译流程。

### 项目结构

```
my-sphinx-theme/
├── src/
│   ├── scss/
│   │   ├── main.scss
│   │   ├── _variables.scss
│   │   ├── _layout.scss
│   │   └── _dark-mode.scss
│   ├── js/
│   │   ├── theme.js
│   │   └── search.js
│   └── templates/
│       └── layout.html
├── my_theme/
│   ├── __init__.py
│   └── static/
│       ├── css/       # 编译后CSS
│       └── js/        # 编译后JS
├── web-compile-config.yml
└── setup.py
```

### 配置文件

```yaml
# web-compile-config.yml
sass_files:
  src/scss/main.scss: my_theme/static/css/theme.[hash].css
js_files:
  src/js/theme.js: my_theme/static/js/theme.[hash].min.js
  src/js/search.js: my_theme/static/js/search.[hash].min.js
```

### SCSS源文件

```scss
// src/scss/_variables.scss
$primary: #2980b9;
$secondary: #27ae60;
$font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
$breakpoint-md: 768px;
```

```scss
// src/scss/main.scss
@import "variables";
@import "layout";
@import "dark-mode";

body {
  font-family: $font-stack;
  color: #333;
  line-height: 1.6;
}

a {
  color: $primary;
  text-decoration: none;
  &:hover { text-decoration: underline; }
}
```

### JS源文件

```javascript
// src/js/theme.js
/*!
 * My Sphinx Theme v1.0.0
 */
(function() {
  'use strict';

  // Dark mode toggle
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function() {
      document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme',
        document.documentElement.classList.contains('dark') ? 'dark' : 'light'
      );
    });
  }

  // Initialize theme from localStorage
  if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark');
  }
})();
```

### 编译

```bash
# 开发模式（格式化CSS）
web-compile --sass-format expanded --verbose

# 生产模式（压缩CSS/JS）
web-compile --sass-format compressed --js-comments
```

输出：

```
Compiled SASS: src/scss/main.scss → my_theme/static/css/theme.a1b2c3d4.css
Minified JS: src/js/theme.js → my_theme/static/js/theme.e5f6g7h8.min.js
Minified JS: src/js/search.js → my_theme/static/js/search.i9j0k1l2.min.js
Compilation succeeded!
```

## 示例2：带Jinja模板的完整站点

### 配置

```yaml
sass_files:
  src/scss/site.scss: dist/css/site.[hash].css
js_files:
  src/js/site.js: dist/js/site.[hash].min.js
jinja_files:
  src/templates/index.html: dist/index.html
  src/templates/docs.html: dist/docs.html
jinja_variables:
  site_name: "My Project Docs"
  version: "2.1.0"
  nav:
    - {title: "首页", url: "/"}
    - {title: "指南", url: "/guide/"}
    - {title: "API", url: "/api/"}
  css_file: "site.[hash].css"  # 注意：需要构建脚本替换为实际哈希
  js_file: "site.[hash].min.js"
```

### Jinja模板

```html
<!-- src/templates/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ site_name }} v{{ version }}</title>
  <link rel="stylesheet" href="/css/{{ css_file }}">
</head>
<body>
  <header>
    <nav>
      <strong>{{ site_name }}</strong>
      {% for item in nav %}
      <a href="{{ item.url }}">{{ item.title }}</a>
      {% endfor %}
    </nav>
  </header>
  <main>
    <h1>欢迎使用 {{ site_name }}</h1>
    <p>当前版本：v{{ version }}</p>
  </main>
  <script src="/js/{{ js_file }}"></script>
</body>
</html>
```

## 示例3：GitHub Actions 自动检查

```yaml
# .github/workflows/assets.yml
name: Web Assets

on:
  push:
    branches: [main]
  pull_request:
    paths:
      - 'src/**'
      - 'web-compile-config.yml'
      - '.github/workflows/assets.yml'

jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install web-compile

      - name: Compile assets
        run: web-compile --sass-format compressed

      - name: Check for changes
        run: |
          if ! git diff --exit-code; then
            echo "::error::Assets are not compiled. Run 'web-compile' and commit changes."
            exit 1
          fi
        shell: bash
```

## 示例4：Makefile 工作流

```makefile
.PHONY: all assets assets-dev assets-check clean

all: assets

# 生产编译
assets:
	web-compile --sass-format compressed --js-comments

# 开发模式（格式化CSS、详细输出）
assets-dev:
	web-compile --sass-format expanded --verbose

# 检查模式（不修改文件）
assets-check:
	web-compile --test-run

# 清理编译产物
clean:
	rm -f my_theme/static/css/theme.*.css
	rm -f my_theme/static/js/theme.*.min.js
	rm -f my_theme/static/js/search.*.min.js
```

使用：

```bash
make assets-dev   # 开发时
make assets       # 发布前
make assets-check # CI中
```

## 示例5：Python构建脚本集成

在 `setup.py` 或构建脚本中集成web-compile：

```python
# build_assets.py
import subprocess
import sys
from pathlib import Path

def build_assets():
    """Build web assets before package build."""
    result = subprocess.run(
        ["web-compile", "--sass-format", "compressed"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    if result.returncode not in (0, 3):  # 0=no changes, 3=changed (both OK)
        print("Asset compilation failed:", result.stderr, file=sys.stderr)
        sys.exit(1)
    print(result.stdout)

if __name__ == "__main__":
    build_assets()
```

在 `pyproject.toml` 中配置构建时自动编译：

```toml
[build-system]
requires = ["setuptools", "web-compile"]
build-backend = "setuptools.build_meta"

# 使用setuptools的build_hooks或手动调用build_assets.py
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [三种编译类型](/concepts/02-compilation-types.md)
- [配置文件详解](/concepts/03-configuration.md)
- [CI集成](/concepts/04-ci-integration.md)
