---
type: Concept
title: 生成项目结构详解
description: 解析 Copier 生成的 JupyterLab 扩展项目的完整目录结构、每个文件/目录的作用以及不同扩展类型的结构差异。
tags: [project-structure, directory-layout, file-reference, configuration]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: package-source
    resource: /references/package-json-source.md
    title: package.json 模板字段解析
  - id: pyproject-source
    resource: /references/pyproject-source.md
    title: pyproject.toml 模板字段解析
---

## 生成项目结构详解

使用 `copier copy` 生成项目后，你会得到一个完整的 JupyterLab 扩展项目。以下以 frontend-and-server 类型（结构最完整）为例，说明每个文件和目录的作用。

## 顶层目录结构

```
myextension/
├── .github/                    # GitHub 配置
│   ├── workflows/              # CI/CD 工作流
│   │   ├── build.yml           # 构建、测试、打包
│   │   ├── check-release.yml   # 发布前检查
│   │   ├── enforce-label.yml   # PR 标签检查
│   │   ├── prep-release.yml    # 发布准备
│   │   └── publish-release.yml # 发布执行
│   └── scripts/
│       └── check_auth.py       # 端点认证检查脚本
├── binder/                     # Binder 配置（条件：has_binder）
│   ├── environment.yml         # conda 环境定义
│   └── postBuild               # 构建后脚本
├── jupyter-config/             # Jupyter 服务器配置（条件：frontend-and-server）
│   └── server-config/
│       └── myextension.json    # 自动启用服务端扩展
├── myextension/                # Python 包目录（名称为 python_name）
│   ├── __init__.py             # 包入口，注册扩展路径
│   ├── _version.py             # 自动生成的版本文件（不提交Git）
│   ├── routes.py               # API 路由（条件：frontend-and-server）
│   └── labextension/           # 构建产物（不提交Git）
│       └── ...                 # 编译后的前端文件
├── schema/                     # 设置 Schema（条件：has_settings）
│   └── plugin.json             # JSON Schema 定义用户设置
├── src/                        # TypeScript 源码
│   ├── index.ts                # 扩展入口点
│   ├── request.ts              # 后端 API 调用封装（条件：frontend-and-server）
│   └── __tests__/              # 前端单元测试（条件：test）
│       └── myextension.spec.ts # Jest 测试用例
├── style/                      # 样式文件
│   ├── base.css                # 基础样式（非 theme 类型）
│   ├── index.css               # 样式入口
│   ├── index.js                # 样式导入（非 theme 类型）
│   └── variables.css           # CSS 变量定义（条件：theme）
├── ui-tests/                   # 集成测试（条件：test）
│   ├── tests/
│   │   └── myextension.spec.ts # Playwright/Galata 测试
│   ├── jupyter_server_test_config.py
│   ├── playwright.config.js    # Playwright 配置
│   ├── package.json            # 测试依赖
│   └── yarn.lock
├── .copier-answers.yml         # Copier 回答记录（用于更新）
├── .eslintrc.js / eslint.config.mjs  # ESLint 配置
├── .gitignore                  # Git 忽略规则
├── .prettierignore             # Prettier 忽略规则
├── .yarnrc.yml                 # Yarn 配置
├── AGENTS.md                   # AI 编码规范（条件：has_ai_rules）
├── babel.config.js             # Babel 配置（Jest 用）
├── CHANGELOG.md                # 变更日志
├── CONTRIBUTING.md             # 贡献指南
├── install.json                # JupyterLab 扩展安装元数据
├── jest.config.js              # Jest 测试配置
├── LICENSE                     # BSD 3-Clause 许可证
├── package.json                # NPM 包配置
├── pyproject.toml              # Python 包配置
├── README.md                   # 项目说明
├── RELEASE.md                  # 发布指南
├── tsconfig.json               # TypeScript 编译配置
└── tsconfig.test.json          # TypeScript 测试配置（条件：test）
```

## 配置文件详解

### package.json

NPM 包的核心配置，包含：
- **元数据**：name、version、description、license、author、repository
- **scripts**：构建（build/build:prod）、测试（test）、Lint（lint/eslint/prettier/stylelint）、监听（watch）、清理（clean）等命令
- **dependencies**：运行时依赖（@jupyterlab/* 包）
- **devDependencies**：开发依赖（TypeScript、ESLint、Jest 等）
- **jupyterlab**：JupyterLab 扩展元数据（extension/mimeExtension、outputDir、schemaDir、themePath、discovery）
- **prettier/stylelint**：代码格式化配置

### pyproject.toml

Python 包的核心配置（PEP 621 标准），包含：
- **build-system**：使用 hatchling 构建后端
- **project**：包名、Python 版本要求、依赖、分类器
- **tool.hatch**：版本从 package.json 同步（hatch-nodejs-version）、构建目标（sdist/wheel）
- **tool.hatch.build.hooks.jupyter-builder**：集成 jupyter-builder，构建时自动执行 NPM 编译
- **tool.jupyter-releaser**：自动化发布配置

### tsconfig.json

TypeScript 编译配置：
- `target: ES2018`、`module: esnext`、`moduleResolution: node`
- `strict: true`、`strictNullChecks: true`、`noImplicitAny: true`（严格模式）
- `jsx: react`（支持 React TSX）
- `outDir: lib`、`rootDir: src`

### install.json

JupyterLab 扩展的安装元数据：
```json
{
  "packageManager": "python",
  "packageName": "myextension",
  "uninstallInstructions": "Use your Python package manager..."
}
```

告诉 JupyterLab 这个扩展通过哪个 Python 包管理，卸载时应使用什么命令。

## 源码目录详解

### src/（TypeScript 源码）

- **index.ts**：扩展入口点，默认导出一个 JupyterFrontEndPlugin 或 IRenderMime.IExtension 对象
- **request.ts**（frontend-and-server）：封装与后端通信的 requestAPI 函数
- **__tests__/**：Jest 单元测试，文件名匹配 `*.spec.ts` 或 `*.spec.tsx`

### style/（样式）

- **index.css**：样式入口文件，@import 其他样式文件
- **base.css**（非 theme）：扩展自定义样式
- **index.js**（非 theme）：`import './base.css'`，用于 webpack 打包 CSS
- **variables.css**（theme）：CSS 变量定义，覆盖 JupyterLab 默认变量

### myextension/（Python 包）

- **__init__.py**：包含 `_jupyter_labextension_paths()` 函数（必须），告诉 JupyterLab 前端静态资源位置；frontend-and-server 类型还包含 `_jupyter_server_extension_points()` 和 `_load_jupyter_server_extension()`
- **routes.py**（frontend-and-server）：定义继承自 APIHandler 的路由处理器和 setup_route_handlers 函数
- **tests/**（frontend-and-server + test）：pytest 测试

### schema/（设置系统）

- **plugin.json**：JSON Schema 格式，定义扩展的用户可配置项。JupyterLab 的设置编辑器会根据此 schema 自动生成设置界面。

## 条件文件/目录

以下文件/目录根据 copier 参数决定是否生成：

| 文件/目录 | 生成条件 |
|-----------|---------|
| `src/request.ts` | kind == 'frontend-and-server' |
| `myextension/routes.py` | kind == 'frontend-and-server' |
| `jupyter-config/` | kind == 'frontend-and-server' |
| `.github/scripts/check_auth.py` | kind == 'frontend-and-server' |
| `style/variables.css` | kind == 'theme' |
| `schema/plugin.json` | has_settings == true |
| `binder/` | has_binder == true |
| `ui-tests/` | test == true |
| `src/__tests__/` | test == true |
| `babel.config.js` | test == true |
| `jest.config.js` | test == true |
| `tsconfig.test.json` | test == true |
| `conftest.py` | test == true and kind == 'frontend-and-server' |
| `AGENTS.md` | has_ai_rules == true |
| `CLAUDE.md`（符号链接） | has_ai_rules and create_claude_symlink |
| `GEMINI.md`（符号链接） | has_ai_rules and create_gemini_symlink |

## 构建产物（不提交 Git）

以下文件/目录由构建过程生成，已在 .gitignore 中排除：

- `lib/`：TypeScript 编译输出（JS 文件和类型声明）
- `node_modules/`：NPM 依赖
- `myextension/labextension/`：打包后的前端扩展（安装到 JupyterLab 的最终产物）
- `myextension/_version.py`：自动生成的版本文件
- `*.tsbuildinfo`：TypeScript 增量编译信息
- `coverage/`、`htmlcov/`、`.pytest_cache/`：测试覆盖率产物
- `dist/`：Python 打包产物（wheel/sdist）
- `.eslintcache`、`.stylelintcache`：Lint 缓存

## 相关概念

- [双包构建系统](05-build-system.md)
- [前端扩展开发](06-frontend-extension.md)
- [四种扩展类型对比](03-four-extension-types.md)
- [三层测试策略](11-testing-strategy.md)
