---
type: spec
title: web-compile 源码事实清单
description: web-compile 源码事实清单
tags:
- web-compile
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: web-compile-source
  resource: /references/compile-source.md
  title: web-compile compile-source
---

# web-compile 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 包名为 `web-compile`，当前版本 `0.2.3`（`__version__ = "0.2.3"`）
- F-002: 核心Python文件2个：`__init__.py`（CLI+编译逻辑）、`config.py`（配置文件解析）
- F-003: 基于Click框架实现CLI，入口命令为 `web-compile`
- F-004: 三种编译能力：SASS/SCSS→CSS编译、JavaScript压缩、Jinja2模板渲染
- F-005: 依赖：libsass（`sass`包）编译SCSS、rjsmin压缩JS、jinja2渲染模板、PyYAML解析配置、GitPython管理Git

## SASS编译

- F-006: 使用 `sass.compile()` 编译SCSS/SCSS文件为CSS
- F-007: 支持4种输出格式：nested、expanded、compact、compressed（默认compressed）
- F-008: 默认精度为5（`--sass-precision`）
- F-009: 支持Source Map生成（`--sass-sourcemap`），默认关闭
- F-010: 默认编码为utf8（`--sass-encoding`）
- F-011: include_paths默认包含源文件所在目录
- F-012: source_map_root使用源文件到输出文件的相对路径

## JS压缩

- F-013: 使用 `rjsmin` 库压缩JavaScript文件
- F-014: `--js-comments` 选项保留以 `/*!` 开头的注释（版权注释）
- F-015: 默认编码为utf8（`--js-encoding`）

## Jinja2模板渲染

- F-016: 使用 `jinja2` 渲染模板文件
- F-017: 支持全局变量注入（`--jinja-variables`）
- F-018: 默认编码为utf8（`--jinja-encoding`）

## 文件哈希（Cache Busting）

- F-019: 输出文件名中包含 `[hash]` 时，自动替换为文件内容的MD5哈希前8位
- F-020: 使用 `hashlib.md5` 计算文件哈希
- F-021: 重新编译时自动删除旧哈希版本的文件（通配符匹配 `[hash]→*`）
- F-022: 哈希策略确保文件名随内容变化，实现浏览器缓存失效

## Git集成

- F-023: `--git-add/--no-git-add` 选项控制是否自动将新文件添加到Git索引
- F-024: 默认启用 `--git-add`
- F-025: 使用GitPython的 `Repo(root, search_parent_directories=False)` 检测Git仓库
- F-026: 配置文件不在Git仓库根目录时抛出ClickException
- F-027: 编译成功后调用 `git_repo.index.add()` 添加新生成的文件

## 配置文件

- F-028: 默认配置文件名为 `web-compile-config.yml`（`-c/--config` 指定）
- F-029: 支持的配置格式：JSON、TOML、YML、YAML
- F-030: 配置文件通过 `config_callback` 回调解析
- F-031: 配置文件指定sass_files/js_files/jinja_files的输入输出映射和jinja_variables

## CLI选项

- F-032: `-q/--quiet`：静默模式，减少stdout输出
- F-033: `-v/--verbose`：详细模式，输出配置详情
- F-034: `--test-run`：测试模式，不创建/删除文件
- F-035: `--continue-on-error`：遇到错误时继续处理其他文件
- F-036: `--exit-code`：文件变更时的退出码（默认3），CI友好
- F-037: 所有sass/js/jinja的文件映射选项为"config only"（只能通过配置文件设置）

## 编译流程

- F-038: 按顺序执行：compile_sass() → minify_js() → compile_jinja()
- F-039: file_map字典在编译过程中累积，记录输入输出文件映射
- F-040: compilation_errors字典收集各编译步骤的错误
- F-041: 有编译错误时抛出ClickException，以YAML格式输出错误详情
- F-042: 文件有变更时以指定exit_code退出（默认3），无变更时退出码0

## 文件写入逻辑

- F-043: 写入前检查输出文件是否已存在且内容相同，相同则跳过（无变更）
- F-044: 内容不同时才写入文件，标记changed_files=True
- F-045: 输出目录不存在时自动创建（`mkdir(parents=True, exist_ok=True)`）
