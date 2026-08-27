---
type: Reference
title: Copier 配置参数全参考
description: extension-template 中 copier.yml 定义的所有模板参数、类型、默认值、条件和校验规则的完整参考。
tags: [copier, template-config, parameters, jinja2]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:15:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: copier-yml
    resource: /references/copier-config.md
    title: copier.yml 参数定义
---

## Copier 模板配置参考

extension-template 使用 [Copier](https://copier.readthedocs.io) 作为项目模板引擎，最低要求 Copier 版本 7.1.0（推荐 9.2+）。模板文件位于 `template/` 子目录，使用 Jinja2 语法（`.jinja` 后缀）进行条件渲染。

## 元配置字段

| 字段 | 值 | 说明 |
|------|-----|------|
| `_min_copier_version` | `"7.1.0"` | 最低 Copier 版本要求 |
| `_subdirectory` | `"template"` | 模板内容所在子目录 |
| `_jinja_extensions` | `["jinja2_time.TimeExtension"]` | 启用的 Jinja2 扩展（提供 `{% now %}` 等时间函数） |

## 用户交互参数

### 扩展类型选择

**`kind`** (str, 默认: `"frontend"`)

选择要生成的扩展类型，可选值：

- `frontend`：纯前端扩展（TypeScript）
- `mimerenderer`：MIME 类型渲染器扩展
- `frontend-and-server`：前端 + Python 后端的全栈扩展
- `theme`：JupyterLab 主题扩展（CSS 变量）

### 作者信息

**`author_name`** (str, 必填)

- placeholder: `"My Name"`
- 校验：不能为空字符串或以空白字符开头（正则 `^[^\s].*$`）

**`author_email`** (str, 默认: `""`)

- placeholder: `"me@test.com"`
- 校验：允许空值；非空时必须匹配标准 email 正则

### 包命名

**`labextension_name`** (str)

- JavaScript/NPM 包名
- 默认值：`kind=='theme'` 时为 `"mytheme"`，否则为 `"myextension"`

**`python_name`** (str)

- Python 包名
- 默认值：从 `labextension_name` 自动转换——将 `-` 和 `/` 替换为 `_`，去除开头的 `@`（用于 scoped package 如 `@org/name` → `org_name`）

### 项目描述

**`project_short_description`** (str, 默认: `"A JupyterLab extension."`)

扩展的一句话简短描述，用于 package.json、pyproject.toml 和 README。

### 功能开关

**`has_settings`** (bool, 默认: `no`)

- 条件：`kind != 'mimerenderer'` 时才出现
- 是否包含用户设置系统（schema/plugin.json + ISettingRegistry 集成）

**`has_binder`** (bool, 默认: `no`)

- 是否生成 Binder 示例配置（binder/environment.yml + postBuild）

**`test`** (bool, 默认: `yes`)

- 是否生成测试配置（Jest 单元测试、pytest 后端测试、Playwright/Galata 集成测试）

**`has_ai_rules`** (bool, 默认: `no`)

- 是否生成 AGENTS.md AI 编码规范文件

**`create_claude_symlink`** (bool, 默认: `yes`)

- 条件：`has_ai_rules` 为 true 时才出现
- 是否创建 CLAUDE.md → AGENTS.md 符号链接（Claude Code 兼容性）

**`create_gemini_symlink`** (bool, 默认: `yes`)

- 条件：`has_ai_rules` 为 true 时才出现
- 是否创建 GEMINI.md → AGENTS.md 符号链接（Gemini Code Assist 兼容性）

### 高级选项

**`advanced`** (bool, 默认: `no`)

- 是否配置高级选项（控制 `yarn_linker` 参数的显示）

**`yarn_linker`** (str, 默认: `"node-modules"`)

- 条件：`advanced` 为 true 时才出现
- 可选值：`node-modules`（经典 node_modules）、`pnpm`（使用 pnpm linker）

### 仓库信息

**`repository`** (str)

- Git 远程仓库 URL
- placeholder: `"https://github.com/github_username/my-extension"`

### MIME 渲染器专用参数

以下参数仅在 `kind == 'mimerenderer'` 时出现：

**`viewer_name`** (str)

- MIME 类型查看器的显示名称，placeholder: `"My Viewer"`

**`mimetype`** (str)

- MIME 类型标识符，placeholder: `"application/vnd.my_organization.my_type"`

**`mimetype_name`** (str)

- MIME 类型简短名称（用于文件类型注册和 CSS 类名），placeholder: `"my_type"`

**`file_extension`** (str)

- 关联的文件扩展名，placeholder: `".my_type"`

**`data_format`** (str, 默认: `"string"`)

- MIME 内容的数据格式，可选值：`string`、`json`

## 后处理任务

Copier 生成文件后会执行 `_tasks` 中定义的命令：

1. **CLAUDE.md 符号链接**：当 `has_ai_rules && create_claude_symlink` 时，执行 Python 命令创建 `CLAUDE.md` → `AGENTS.md` 的符号链接
2. **GEMINI.md 符号链接**：当 `has_ai_rules && create_gemini_symlink` 时，执行 Python 命令创建 `GEMINI.md` → `AGENTS.md` 的符号链接

## 相关概念

- [Copier 模板引擎基础](../concepts/02-copier-basics.md)
- [四种扩展类型对比](../concepts/03-four-extension-types.md)
- [生成项目结构详解](../concepts/04-project-structure.md)
- [快速开始](../concepts/01-getting-started.md)
