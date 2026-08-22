---
type: Concept
title: 快速开始
description: 安装web-compile、创建配置文件、执行第一次编译、理解输出和退出码
tags: [web, compile, installation, getting-started, quickstart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:20:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-source
    resource: /references/compile-source.md
    title: web-compile 源码路径映射
---

# 快速开始

## 安装

```bash
pip install web-compile
```

验证安装：

```bash
web-compile --version
```

## 最小配置

在项目根目录创建 `web-compile-config.yml`：

```yaml
sass_files:
  src/style.scss: dist/style.css
```

创建源文件 `src/style.scss`：

```scss
$primary-color: #3498db;

body {
  font-family: sans-serif;
  color: $primary-color;

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

## 执行编译

```bash
web-compile
```

输出：

```
Compiled SASS: src/style.scss → dist/style.css
Compilation succeeded!
```

编译后的 `dist/style.css`（compressed格式默认）：

```css
body{font-family:sans-serif;color:#3498db}body .container{max-width:1200px;margin:0 auto}
```

## 使用[hash]缓存失效

修改配置使用hash文件名：

```yaml
sass_files:
  src/style.scss: dist/style.[hash].css
```

运行：

```bash
web-compile
```

输出：

```
Compiled SASS: src/style.scss → dist/style.a1b2c3d4.css
Compilation succeeded!
File(s) changed
```

文件名 `style.a1b2c3d4.css` 中的 `a1b2c3d4` 是CSS内容的MD5哈希前8位。内容不变时哈希不变，内容变化时哈希变化——浏览器自动加载新版本。

再次运行（文件未变化）：

```bash
web-compile
echo $?  # 退出码
```

输出：

```
Compilation succeeded!
```

退出码为 `0`（无变更）。

## 退出码含义

| 退出码 | 含义 |
|--------|------|
| 0 | 编译成功，文件无变更 |
| 1 | 编译错误 |
| 3（默认） | 编译成功，文件有变更 |

可以通过 `--exit-code` 自定义变更退出码。

## 常用选项

### 详细输出

```bash
web-compile --verbose
```

显示完整配置信息。

### 测试模式（不修改文件）

```bash
web-compile --test-run --verbose
```

### 静默模式

```bash
web-compile --quiet
```

### 指定配置文件

```bash
web-compile --config path/to/my-config.yml
```

### 不自动git add

```bash
web-compile --no-git-add
```

### SASS使用expanded格式（便于调试）

```bash
web-compile --sass-format expanded
```

输出CSS格式：

```css
body {
  font-family: sans-serif;
  color: #3498db;
}
body .container {
  max-width: 1200px;
  margin: 0 auto;
}
```

### 保留JS版权注释

```bash
web-compile --js-comments
```

保留以 `/*!` 开头的注释（如版权声明）。

## 完整示例配置

```yaml
sass_files:
  src/styles/main.scss: dist/css/main.[hash].css
  src/styles/theme.scss: dist/css/theme.[hash].css
js_files:
  src/js/app.js: dist/js/app.[hash].min.js
jinja_files:
  src/templates/index.html: dist/index.html
jinja_variables:
  app_name: "My App"
  version: "1.0.0"
```

运行：

```bash
web-compile --sass-format compressed
```

## 相关概念

- [简介](/concepts/00-introduction.md)
- [三种编译类型](/concepts/02-compilation-types.md)
- [配置文件详解](/concepts/03-configuration.md)
- [资产编译流水线示例](/examples/asset-pipeline.md)
