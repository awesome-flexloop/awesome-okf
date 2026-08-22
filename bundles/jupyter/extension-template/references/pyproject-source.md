---
type: Reference
title: pyproject.toml 模板字段解析
description: extension-template 中 pyproject.toml.jinja 模板的构建系统、依赖管理、Hatch 配置和 Jupyter 构建钩子的完整参考。
tags: [python, pyproject, hatchling, jupyter-builder, packaging, wheel]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:15:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject-template
    resource: /references/pyproject-source.md
    title: pyproject.toml.jinja 模板源码
---

## pyproject.toml 模板字段参考

pyproject.toml 是 Python 包的标准配置文件（PEP 621），使用 Hatchling 作为构建后端，集成了 hatch-nodejs-version 实现版本同步和 jupyter-builder 实现前端构建自动化。

## 构建系统配置

```toml
[build-system]
requires = ["hatchling>=1.5.0", "hatch-nodejs-version>=0.3.2", "jupyter-builder>=1.2.0,<2"]
build-backend = "hatchling.build"
```

| 依赖 | 作用 |
|------|------|
| `hatchling>=1.5.0` | PEP 517 构建后端 |
| `hatch-nodejs-version>=0.3.2` | 从 package.json 读取版本号同步到 Python 包 |
| `jupyter-builder>=1.2.0,<2` | JupyterLab 扩展构建工具，处理 NPM 编译和 labextension 打包 |

## 项目元数据

| 字段 | 值/模板 | 说明 |
|------|---------|------|
| `name` | `"{{ python_name }}"` | Python 包名 |
| `readme` | `"README.md"` | README 文件 |
| `license` | `"BSD-3-Clause"` | 许可证 |
| `requires-python` | `">=3.10"` | 最低 Python 版本 |
| `dynamic` | `["version", "description", "authors", "urls", "keywords"]` | 由 hatch-nodejs-version 动态填充 |

### classifiers（分类器）

无条件包含：
- `Framework :: Jupyter`
- `Framework :: Jupyter :: JupyterLab`
- `Framework :: Jupyter :: JupyterLab :: 4`
- `Framework :: Jupyter :: JupyterLab :: Extensions`
- `Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt`
- Python 3.10 ~ 3.14 分类器

条件包含：
- `Mime Renderers`：当 `kind == 'mimerenderer'`
- `Themes`：当 `kind == 'theme'`

### dependencies（运行时依赖）

- 当 `kind == 'frontend-and-server'`：`"jupyter_server>=2.13.0,<3"`
- 其他类型：空列表

### optional-dependencies（可选依赖）

**dev 组**：
- `"jupyterlab>=4"`
- `"jupyter-builder>=1.2.0"`

**test 组**（当 `test` 且 `kind == 'frontend-and-server'`）：
- `"coverage"`
- `"pytest"`
- `"pytest-asyncio"`
- `"pytest-cov"`
- `"pytest-jupyter[server]>=0.6.0"`

## Hatch 版本配置

```toml
[tool.hatch.version]
source = "nodejs"

[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls", "keywords"]
```

版本号从 package.json 中读取，元数据字段也从 NPM 包同步。

## Hatch 构建目标

### sdist（源码分发包）

- artifacts：`["{{ python_name }}/labextension"]`
- exclude：`[".github", "binder"]`

### wheel（二进制包）

shared-data 映射将构建产物安装到 JupyterLab 的扩展目录：

| 源路径 | 目标路径 |
|--------|---------|
| `{{ python_name }}/labextension` | `share/jupyter/labextensions/{{ labextension_name }}` |
| `install.json` | `share/jupyter/labextensions/{{ labextension_name }}/install.json` |
| `jupyter-config/server-config`（仅 frontend-and-server） | `etc/jupyter/jupyter_server_config.d` |

## Jupyter Builder 构建钩子

### 版本钩子

```toml
[tool.hatch.build.hooks.version]
path = "{{ python_name }}/_version.py"
```

自动生成 `_version.py` 文件，包含 `__version__`。

### NPM 构建钩子

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
```

**ensured-targets**（构建完成后必须存在的文件）：
- `"{{ python_name }}/labextension/package.json"`
- `"{{ python_name }}/labextension/static/style.js"`（非 theme 类型）

**skip-if-exists**：`["{{ python_name }}/labextension/static/style.js"]`（开发模式已构建时跳过）

### 构建参数

**生产构建**（pip install / build）：
- `build_cmd`: `"build:prod"`
- `npm`: `["jlpm"]`

**可编辑安装**（pip install -e）：
- `build_cmd`: `"install:extension"`
- `npm`: `["jlpm"]`
- `source_dir`: `"src"`
- `build_dir`: `"{{python_name}}/labextension"`

## Jupyter Releaser 配置

```toml
[tool.jupyter-releaser.options]
version_cmd = "hatch version"

[tool.jupyter-releaser.hooks]
before-build-npm = [
    "python -m pip install 'jupyter-builder>=1.2.0,<2'",
    "jlpm",
    "jlpm build:prod"
]
before-build-python = ["jlpm clean:all"]
```

## Wheel 内容检查

```toml
[tool.check-wheel-contents]
ignore = ["W002"]
```

W002 警告（wheel 包含顶层模块）被忽略，因为 Jupyter 扩展通过 shared-data 安装而非标准 Python 包路径。

## 相关概念

- [双包构建系统](/concepts/05-build-system.md)
- [服务端扩展开发](/concepts/07-server-extension.md)
- [打包与发布](/concepts/13-packaging-release.md)
- [package.json 模板解析](/references/package-json-source.md)
