---
type: Concept
title: 配置文件详解
description: web-compile配置文件的完整格式：YAML/JSON/TOML支持、sass_files/js_files/jinja_files映射、jinja_variables配置
tags: [web, compile, configuration, yaml, config, sass, jinja]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:24:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-source
    resource: /references/compile-source.md
    title: web-compile 源码路径映射
---

# 配置文件详解

## 配置文件基础

### 默认文件名

web-compile 默认读取当前目录下的 `web-compile-config.yml`：

```bash
web-compile  # 自动读取 web-compile-config.yml
```

### 指定配置文件

```bash
web-compile --config path/to/config.yml
# 或
web-compile -c config.json
```

### 支持的格式

| 格式 | 扩展名 |
|------|--------|
| YAML | `.yml`, `.yaml` |
| JSON | `.json` |
| TOML | `.toml` |

## 配置结构

完整的YAML配置示例：

```yaml
# SASS/SCSS文件编译
sass_files:
  # 输入路径: 输出路径
  src/styles/main.scss: dist/css/main.[hash].css
  src/styles/theme.scss: dist/css/theme.[hash].css
  src/styles/print.scss: dist/css/print.css

# JavaScript文件压缩
js_files:
  src/js/app.js: dist/js/app.[hash].min.js
  src/js/vendor.js: dist/js/vendor.min.js

# Jinja2模板渲染
jinja_files:
  src/templates/index.html: dist/index.html
  src/templates/about.html: dist/about.html

# Jinja2全局变量
jinja_variables:
  app_name: "My Documentation"
  version: "2.0.0"
  author: "Team"
  debug: false
  analytics_id: "UA-XXXXX"
```

## sass_files 详解

`sass_files` 是输入→输出的映射字典：

```yaml
sass_files:
  # 基本用法
  src/input.scss: dist/output.css

  # [hash]缓存失效（推荐生产环境）
  src/main.scss: dist/main.[hash].css

  # 多个文件
  src/a.scss: dist/a.css
  src/b.scss: dist/b.css
```

### 路径规则

- 输入路径相对于**配置文件所在目录**（不是执行命令的目录）
- 输出路径同样相对于配置文件目录
- 输出目录不存在时自动创建
- 输入文件不存在时：默认报错退出，`--continue-on-error` 时跳过

### SCSS @import 路径

SCSS文件中`@import`引用其他文件时，搜索路径包含：
1. 当前源文件所在目录（自动添加到include_paths）
2. 如果引用了其他目录的SCSS（如通过pip安装的主题），需要确保路径正确

## js_files 详解

```yaml
js_files:
  src/app.js: dist/app.min.js
  src/utils.js: dist/utils.[hash].min.js
```

同样支持 `[hash]` 文件名。使用 `--js-comments` 保留 `/*!` 开头的版权注释。

## jinja_files 详解

```yaml
jinja_files:
  src/template.html: dist/output.html
```

### jinja_variables

注入到所有Jinja模板的全局变量：

```yaml
jinja_variables:
  site_name: "My Docs"
  version: "1.0"
  nav_items:
    - title: "Home"
      url: "/"
    - title: "API"
      url: "/api/"
  features:
    dark_mode: true
    search: true
```

在模板中使用：

```html
<nav>
{% for item in nav_items %}
  <a href="{{ item.url }}">{{ item.title }}</a>
{% endfor %}
</nav>

{% if features.dark_mode %}
<button id="theme-toggle">🌙</button>
{% endif %}

<footer>Version {{ version }}</footer>
```

## 配置示例场景

### 场景1：Sphinx主题开发

```yaml
sass_files:
  src/scss/theme.scss: sphinx_theme/static/css/theme.[hash].css
js_files:
  src/js/theme.js: sphinx_theme/static/js/theme.[hash].js
```

### 场景2：文档站点资源

```yaml
sass_files:
  docs/_static/styles/main.scss: docs/_build/html/_static/main.[hash].css
js_files:
  docs/_static/js/search.js: docs/_build/html/_static/search.[hash].min.js
jinja_files:
  docs/_templates/layout.html: docs/_build/html/_templates/layout.html
jinja_variables:
  theme_version: "2.0"
  # 实际哈希文件名需要构建脚本注入
```

### 场景3：纯JS/CSS库

```yaml
sass_files:
  src/index.scss: dist/mylib.[hash].css
js_files:
  src/index.js: dist/mylib.[hash].min.js
```

## CLI选项覆盖配置

部分选项可以通过CLI参数覆盖配置文件中的默认值：

```bash
# 临时使用expanded格式调试
web-compile --sass-format expanded

# 不生成sourcemap
web-compile --sass-sourcemap  # 启用sourcemap

# 不自动git add
web-compile --no-git-add

# 详细输出查看实际配置
web-compile --verbose
```

## 注意事项

1. **文件映射只能在配置文件中设置**：`--sass-files`、`--js-files`、`--jinja-files`标记为"config only"，不能通过CLI直接传入文件列表
2. **路径相对于配置文件**：确保配置文件放在项目根目录，路径从该目录开始计算
3. **[hash]文件名与Jinja**：如果Jinja模板需要引用带哈希的CSS/JS文件名，需要自定义构建脚本将实际文件名传入jinja_variables
4. **编码**：所有文件默认使用UTF-8编码，可通过 `--sass-encoding`/`--js-encoding`/`--jinja-encoding` 修改

## JSON格式示例

```json
{
  "sass_files": {
    "src/style.scss": "dist/style.[hash].css"
  },
  "js_files": {
    "src/app.js": "dist/app.[hash].min.js"
  },
  "jinja_variables": {
    "version": "1.0.0"
  }
}
```

## 相关概念

- [三种编译类型](/concepts/02-compilation-types.md)
- [CI集成](/concepts/04-ci-integration.md)
- [资产编译流水线示例](/examples/asset-pipeline.md)
