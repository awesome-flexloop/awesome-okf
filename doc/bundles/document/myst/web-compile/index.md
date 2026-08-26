---
type: bundle
title: web-compile
description: "Python生态的Web静态资源编译CLI工具，支持SCSS→CSS、JS压缩、Jinja2模板渲染、[hash]缓存失效和CI集成"
tags:
- web
- compile
- sass
- scss
- css
- javascript
- jinja2
- cli
- asset-pipeline
- build-tool
- sphinx
- executable-books
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T05:30:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: wc-repo
  resource: "https://github.com/executablebooks/web-compile"
  title: web-compile GitHub Repository
okf_version: '0.2'
---

# web-compile

web-compile 是 Executable Books 生态中的命令行工具，为 Python 项目（特别是 Sphinx 扩展和文档主题）提供纯 Python 的 Web 静态资源编译能力。无需 Node.js 构建链，通过 pip 安装即可使用。

## 核心功能

- **SCSS/SASS编译**：libsass驱动，支持4种输出格式、Source Map
- **JS压缩**：rjsmin压缩JavaScript，可保留版权注释
- **Jinja2模板渲染**：变量注入，HTML/配置文件生成
- **[hash]缓存失效**：输出文件名包含内容哈希，旧文件自动清理
- **Git集成**：编译后自动`git add`新文件
- **CI友好**：文件变更非零退出码（默认3），检测未提交资源
- **多格式配置**：YAML/JSON/TOML配置文件，声明式文件映射
- **错误收集**：批量编译收集所有错误统一报告

## 文档导航

| 章节 | 链接 |
|------|------|
| 📖 入门 | [概念文档](/concepts/index.md) |
| 💡 示例 | [示例代码](/examples/index.md) |
| 📚 参考 | [源码参考](/references/index.md) |
| 🔬 规格 | [事实清单](/spec/facts.md) · [架构洞察](/spec/insights.md) |

## 快速开始

```bash
pip install web-compile
```

创建 `web-compile-config.yml`：

```yaml
sass_files:
  src/style.scss: dist/style.[hash].css
js_files:
  src/app.js: dist/app.[hash].min.js
```

运行编译：

```bash
web-compile
```

## 更新日志

见 [log.md](/log.md)。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
