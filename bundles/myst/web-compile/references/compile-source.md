---
type: Reference
title: web-compile 源码路径映射
description: web-compile 核心源文件、编译函数、CLI选项和配置格式索引
tags: [web, compile, sass, scss, javascript, jinja2, cli, build]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:16:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: wc-repo
    resource: https://github.com/executablebooks/web-compile
    title: web-compile GitHub Repository
---

# web-compile 源码路径映射

源路径相对于 `external/libs/ai/executablebooks/web-compile/web_compile/`。

## 核心文件清单

| 文件 | 职责 |
|------|------|
| `__init__.py` | CLI入口、三种编译函数、主编译流程 |
| `config.py` | 配置文件解析（YAML/JSON/TOML） |

## 编译函数

| 函数 | 功能 |
|------|------|
| `run_compile()` | CLI主函数，按顺序执行三种编译 |
| `compile_sass()` | SCSS/SASS→CSS编译，支持[hash]命名 |
| `minify_js()` | JavaScript压缩，使用rjsmin |
| `compile_jinja()` | Jinja2模板渲染，支持变量注入 |
| `hash_file()` | MD5哈希计算，用于[hash]占位符 |

## CLI选项总览

| 分类 | 选项 | 默认值 | 说明 |
|------|------|--------|------|
| 配置 | `-c/--config` | `web-compile-config.yml` | 配置文件路径 |
| SASS | `--sass-format` | `compressed` | 输出格式 |
| SASS | `--sass-precision` | `5` | 数值精度 |
| SASS | `--sass-sourcemap` | false | 生成Source Map |
| SASS | `--sass-encoding` | `utf8` | 文件编码 |
| JS | `--js-comments` | false | 保留版权注释 |
| JS | `--js-encoding` | `utf8` | 文件编码 |
| Jinja | `--jinja-encoding` | `utf8` | 文件编码 |
| 通用 | `-q/--quiet` | false | 静默模式 |
| 通用 | `-v/--verbose` | false | 详细输出 |
| 通用 | `--git-add/--no-git-add` | true | 自动git add |
| 通用 | `--test-run` | false | 测试模式 |
| 通用 | `--continue-on-error` | false | 错误时继续 |
| 通用 | `--exit-code` | `3` | 变更时退出码 |

## SASS输出格式

| 格式 | 说明 |
|------|------|
| `nested` | 嵌套缩进 |
| `expanded` | 展开多行 |
| `compact` | 紧凑单规则单行 |
| `compressed` | 压缩无空白（生产用） |

## 相关概念

- [简介](/concepts/00-introduction.md)
- [三种编译类型](/concepts/02-compilation-types.md)
- [配置文件详解](/concepts/03-configuration.md)
