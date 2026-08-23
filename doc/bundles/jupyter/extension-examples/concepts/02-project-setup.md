---
type: Concept
title: 项目结构与构建系统
description: 深入理解JupyterLab扩展的标准目录结构、npm+Python双构建系统和开发工作流
tags: [jupyterlab, project-structure, build-system, hatchling, jlpm]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: hello-pkg
    resource: /references/plugin-anatomy.md
    title: hello-world/package.json npm配置
  - id: hello-pyproject
    resource: /references/plugin-anatomy.md
    title: hello-world/pyproject.toml Python构建配置
---

## 双构建系统架构

JupyterLab 扩展是 **TypeScript前端 + Python包** 的双语言项目：

```
TypeScript源码 (src/*.ts)
    │
    ├── tsc编译 ──→ lib/*.js (CommonJS模块)
    │
    └── @jupyterlab/builder ──→ <python_pkg>/labextension/ (静态资源)
                                      │
                                      └── hatchling打包 ──→ .whl文件
```

构建流程：
1. **前端构建**：TypeScript → JavaScript → JupyterLab Builder 打包（webpack）
2. **Python打包**：hatchling 将 labextension 静态资源打入 wheel
3. **安装时**：pip install 将静态资源放到 `share/jupyter/labextensions/` 目录

## 目录结构详解

```
my-extension/
├── src/                    # TypeScript 源码（开发目录）
│   └── index.ts            # 插件入口，必须default export插件对象
├── lib/                    # tsc编译输出（自动生成，不提交git）
├── style/                  # CSS样式文件
│   ├── base.css            # 基础样式
│   ├── index.css           # 样式主文件（import其他css）
│   └── index.js            # 样式模块加载入口
├── schema/                 # JSON Schema设置定义（可选）
│   └── plugin.json         # 设置项的JSON Schema
├── jupyterlab_examples_my_ext/   # Python包（snake_case命名）
│   ├── __init__.py         # labextension路径声明
│   ├── labextension/       # 前端构建产物（自动生成）
│   └── _version.py         # 版本文件（自动生成）
├── ui-tests/               # Playwright集成测试（可选）
├── package.json            # npm包配置 + jupyterlab元数据
├── pyproject.toml          # Python构建配置
├── tsconfig.json           # TypeScript编译选项
├── install.json            # 安装元数据
└── README.md               # 文档
```

## package.json 关键字段

### jupyterlab 字段

```json
{
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_examples_hello_world/labextension"
  }
}
```

- `"extension": true`：标记为JupyterLab扩展（否则不会被发现）
- `"outputDir"`：前端构建产物输出目录，指向Python包内的labextension目录
- MIME渲染器扩展使用 `"mimeExtension": true` 代替 `"extension": true`
- 同时包含前后端的扩展可添加 `"discovery"` 字段

### files 字段

```json
{
  "files": [
    "lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}",
    "style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}",
    "src/**/*.{ts,tsx}"
  ]
}
```

发布到npm时包含的文件：编译后的JS、类型定义、样式、源码（含src用于sourcemap）。

### scripts 字段

| 命令 | 说明 |
|------|------|
| `jlpm build` | 完整构建（编译ts + 构建labextension开发版） |
| `jlpm build:prod` | 生产构建（清理 + 编译 + 构建labextension） |
| `jlpm build:lib` | 仅编译TypeScript（tsc --sourceMap） |
| `jlpm build:labextension` | 构建labextension到outputDir |
| `jlpm watch` | 监听模式（并行watch:src + watch:labextension） |
| `jlpm clean:all` | 清理所有构建产物 |

## pyproject.toml 详解

### 构建系统

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"
```

- **hatchling**：现代Python构建后端（替代setuptools）
- **hatch-nodejs-version**：从package.json读取版本号
- **hatch-jupyter-builder**：在Python构建时自动触发前端构建

### 共享数据映射

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlab_examples_hello_world/labextension" = "share/jupyter/labextensions/@jupyterlab-examples/hello-world"
"install.json" = "share/jupyter/labextensions/@jupyterlab-examples/hello-world/install.json"
```

wheel包安装时，将构建产物复制到JupyterLab的labextensions目录。

### Jupyter Builder钩子

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlab_examples_hello_world/labextension/static/style.js",
    "jupyterlab_examples_hello_world/labextension/package.json"
]
build_cmd = "build:prod"
npm = ["jlpm"]
```

构建wheel时自动调用 `jlpm build:prod` 构建前端，并验证目标文件存在。

### 可编辑安装钩子

```toml
[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlab_examples_hello_world/labextension"
```

`pip install -e .` 时使用开发模式构建，支持热重载。

## Python __init__.py

```python
def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlab-examples/hello-world"
    }]
```

`_jupyter_labextension_paths()` 是JupyterLab发现前端扩展的入口函数，返回静态文件路径映射。

**服务端扩展**还需要两个额外函数：

```python
def _jupyter_server_extension_points():
    return [{"module": "my_package"}]

def _load_jupyter_server_extension(server_app):
    setup_handlers(server_app.web_app)
```

## 开发工作流

### 首次安装

```bash
# 进入扩展目录
cd my-extension

# 创建yarn.lock（Yarn Berry PnP要求）
touch yarn.lock

# 可编辑安装Python包（自动构建前端）
pip install -e .

# 符号链接到JupyterLab（开发模式）
jupyter labextension develop . --overwrite
```

`jupyter labextension develop . --overwrite` 命令将扩展创建为符号链接，使得修改代码后不需要重新pip install。

### 开发迭代

```bash
# 终端1：启动TypeScript监听编译
jlpm watch

# 终端2：启动JupyterLab
jupyter lab
```

修改 `src/*.ts` 文件后，`jlpm watch` 自动重新编译，刷新浏览器即可看到变化。

### 生产构建

```bash
# 清理并构建生产版本
jlpm build:prod

# 构建Python wheel
pip install build
python -m build
```

### 一次性构建所有示例

```bash
# 在仓库根目录
jlpm              # 安装所有依赖
jlpm build-ext    # 构建所有扩展
jlpm install-py   # 安装所有Python包
jlpm install-ext  # 链接到JupyterLab
```

## install.json

```json
{
  "packageManager": "python",
  "packageName": "jupyterlab_examples_hello_world",
  "uninstallInstructions": "Use your Python package manager to uninstall"
}
```

告诉JupyterLab此扩展通过Python包管理器管理。纯前端扩展也可以通过npm直接分发，但官方示例统一使用Python包方式。

## 相关概念

- [Hello World：最小插件](/concepts/01-hello-world.md)
- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [插件解剖结构参考](/references/plugin-anatomy.md)
