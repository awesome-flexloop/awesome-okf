---
type: Concept
title: web-compile 简介
description: web-compile是什么——Python生态的Web静态资源编译CLI工具，支持SCSS→CSS、JS压缩、Jinja2模板渲染和[hash]缓存失效
tags: [web, compile, sass, scss, css, javascript, jinja2, cli, asset-pipeline, build-tool]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:18:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-source
    resource: /references/compile-source.md
    title: web-compile 源码路径映射
---

# web-compile 简介

web-compile 是 Executable Books 生态中的命令行工具，为 Python 项目（特别是 Sphinx 扩展和文档主题）提供静态Web资源编译能力。它支持 SCSS/SASS 编译为 CSS、JavaScript 压缩、Jinja2 模板渲染，内置内容哈希缓存失效和 Git 集成。

## 核心功能

| 功能 | 描述 |
|------|------|
| **SCSS编译** | 将SCSS/SASS文件编译为CSS，支持4种输出格式 |
| **JS压缩** | 使用rjsmin压缩JavaScript文件，可保留版权注释 |
| **Jinja2渲染** | 渲染Jinja2模板，支持全局变量注入 |
| **[hash]缓存失效** | 输出文件名自动包含内容哈希，旧文件自动清理 |
| **Git集成** | 编译后自动`git add`新文件 |
| **CI友好** | 文件变更时非零退出码，适合CI检测 |
| **多格式配置** | YAML/JSON/TOML配置文件 |
| **错误收集** | 批量编译时收集所有错误统一报告 |

## 为什么需要web-compile？

在Python/Sphinx生态中开发前端资源时，开发者通常不想引入Node.js/npm构建链。web-compile提供纯Python的最小化资产编译能力：

- **零Node依赖**：纯Python实现（libsass/rjsmin/jinja2都是Python包）
- **pip安装**：`pip install web-compile` 即可使用
- **Sphinx主题开发**：编译主题SCSS、压缩JS、生成最终CSS
- **配置驱动**：一个YAML文件管理所有编译映射，纳入版本控制

## 典型使用场景

- **Sphinx主题开发**：编译主题的SCSS为CSS，压缩主题JS
- **文档站点资源构建**：在文档构建前编译Web资源
- **Python包静态资源**：为Python Web应用编译前端资产
- **CI资产检查**：在CI中检测未提交的编译后资源
- **多文件批量编译**：一次编译多个SCSS/JS/模板文件

## 安装

```bash
pip install web-compile
```

## 快速示例

创建配置文件 `web-compile-config.yml`：

```yaml
sass_files:
  src/style.scss: dist/style.[hash].css
js_files:
  src/app.js: dist/app.[hash].min.js
jinja_files:
  src/template.html: dist/output.html
jinja_variables:
  version: "1.0.0"
```

运行编译：

```bash
web-compile
```

输出示例：

```
Compiled SASS: src/style.scss → dist/style.a1b2c3d4.css
Minified JS: src/app.js → dist/app.e5f6g7h8.min.js
Rendered Jinja: src/template.html → dist/output.html
Compilation succeeded!
```

## 相关概念

- [快速开始](01-getting-started.md)
- [三种编译类型](02-compilation-types.md)
- [配置文件详解](03-configuration.md)
- [CI集成](04-ci-integration.md)
- [资产编译流水线示例](../examples/asset-pipeline.md)
