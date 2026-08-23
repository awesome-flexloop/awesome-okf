---
type: Reference
title: package.json 模板字段解析
description: extension-template 中 package.json.jinja 模板的所有字段、条件分支和默认值的完整参考。
tags: [npm, package.json, build-scripts, dependencies, jupyterlab-metadata]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:15:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: package-json-template
    resource: /references/package-json-source.md
    title: package.json.jinja 模板源码
---

## package.json 模板字段参考

package.json 是 NPM 包的配置文件，同时包含 JupyterLab 扩展的元数据。模板通过 Jinja2 条件块根据扩展类型（`kind`）和功能开关（`has_settings`、`test`、`yarn_linker`）动态生成不同内容。

## 基础元数据

| 字段 | 值/模板 | 说明 |
|------|---------|------|
| `name` | `"{{ labextension_name }}"` | NPM 包名，来自 copier 参数 |
| `version` | `"0.1.0"` | 初始版本号 |
| `description` | `"{{ project_short_description }}"` | 包描述（自动转义双引号） |
| `license` | `"BSD-3-Clause"` | 许可证 |
| `main` | `"lib/index.js"` | 入口文件（编译后） |
| `types` | `"lib/index.d.ts"` | TypeScript 类型声明入口 |
| `publishConfig.access` | `"public"` | 公开发布 |

## files 字段（发布文件清单）

无条件包含：
- `lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}`
- `style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}`
- `src/**/*.{ts,tsx}`

条件包含：
- `schema/*.json`：当 `has_settings` 为 true 时

## jupyterlab 元数据

这是 JupyterLab 扩展发现机制的关键字段：

| 子字段 | 条件 | 值 |
|--------|------|-----|
| `extension` | `kind != 'mimerenderer'` | `true`（标记为普通扩展） |
| `mimeExtension` | `kind == 'mimerenderer'` | `true`（标记为 MIME 扩展） |
| `outputDir` | 无条件 | `"{{python_name}}/labextension"`（构建输出目录） |
| `schemaDir` | `has_settings` | `"schema"`（设置 schema 目录） |
| `themePath` | `kind == 'theme'` | `"style/index.css"`（主题 CSS 入口） |
| `discovery` | `kind == 'frontend-and-server'` | 包含 `server.managers: ["pip"]` 和 `base.name: "{{ python_name }}"` |

## 构建脚本

| 脚本名 | 命令 | 说明 |
|--------|------|------|
| `build` | `jlpm build:lib && jlpm build:labextension:dev` | 开发模式构建 |
| `build:prod` | `jlpm clean && jlpm build:lib:prod && jlpm build:labextension` | 生产构建 |
| `build:labextension` | `jupyter-builder build .` | 构建 JupyterLab 扩展包 |
| `build:labextension:dev` | `jupyter-builder build --development True .` | 开发模式构建扩展包 |
| `build:lib` | `tsc --sourceMap` | 编译 TS → JS（含 sourcemap） |
| `build:lib:prod` | `tsc` | 编译 TS → JS（生产模式） |
| `watch` | `run-p watch:src watch:labextension` | 并行监听源码和扩展 |
| `watch:src` | `tsc -w --sourceMap` | 监听 TS 文件变化 |
| `watch:labextension` | `jupyter-builder watch .` | 监听扩展变化 |

## 代码质量脚本

| 脚本名 | 命令 |
|--------|------|
| `lint` | `jlpm stylelint && jlpm prettier && jlpm eslint` |
| `lint:check` | `jlpm stylelint:check && jlpm prettier:check && jlpm eslint:check` |
| `eslint` | `jlpm eslint:check --fix` |
| `prettier` | `jlpm prettier:base --write --list-different` |
| `stylelint` | `jlpm stylelint:check --fix` |
| `test` | `jest --coverage`（当 `test` 为 true） |

## 依赖项

### dependencies（运行时依赖）

**所有非 mimerenderer 类型**：
- `@jupyterlab/application: ^4.0.0`

**theme 额外依赖**：
- `@jupyterlab/apputils: ^4.0.0`

**frontend-and-server 额外依赖**：
- `@jupyterlab/coreutils: ^6.0.0`
- `@jupyterlab/services: ^7.0.0`

**has_settings 额外依赖**：
- `@jupyterlab/settingregistry: ^4.0.0`

**mimerenderer 类型**：
- `@jupyterlab/rendermime-interfaces: ^3.8.0`
- `@lumino/widgets: ^2.1.0`

### devDependencies（开发依赖）

核心开发依赖：
- `@jupyter/builder: ^1.2.0`
- `@jupyter/eslint-plugin: ^1.1.0`
- `typescript: ~5.5.4`
- `eslint: ^9.0.0`、`prettier: ^3.0.0`、`stylelint: ^15.10.1`
- `npm-run-all2: ^7.0.1`、`rimraf: ^5.0.1`
- `yjs: ^13.5.0`

条件依赖：
- `@jupyterlab/testutils: ^4.0.0`、`@types/jest: ^29.2.0`、`jest: ^29.2.0`（当 `test` 为 true）
- `@jupyterlab/core-meta: ^4.6.0`、`css-loader: ^6.7.1`、`source-map-loader`、`style-loader`、`@module-federation/runtime-tools`（当 `yarn_linker == 'pnpm'`）
- `mkdirp: ^1.0.3`（当 `kind == 'frontend-and-server'`）

## resolutions（版本锁定）

- `lib0`: `"0.2.111"`
- `webpack`: `"5.106.0"`

## 相关概念

- [双包构建系统](/concepts/05-build-system.md)
- [前端扩展开发](/concepts/06-frontend-extension.md)
- [pyproject.toml 模板解析](/references/pyproject-source.md)
