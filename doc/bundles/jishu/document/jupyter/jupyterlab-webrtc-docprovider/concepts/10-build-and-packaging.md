---
type: Concept
title: 构建与打包系统
description: jupyterlab-webrtc-docprovider使用TypeScript编译、jupyter labextension build、jupyter_packaging双端构建系统，同时发布npm包和Python包
tags: [build, typescript, webpack, jupyter-packaging, pip, npm, labextension, packaging]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: python-src
    resource: /references/python-source.md
    title: Python packaging source (pyproject.toml, setup.py, __init__.py)
  - id: pkg-json
    resource: /references/plugin-source.md
    title: package.json - Build scripts and dependencies
---

## 双包发布架构

jupyterlab-webrtc-docprovider 同时发布为两个包：

| 包管理器 | 包名 | 内容 |
|---------|------|------|
| npm | `@jupyterlite/webrtc-docprovider` | 编译后的 JS/CSS/资源文件 |
| PyPI/conda | `jupyterlab-webrtc-docprovider` | Python 包 + 预构建的 labextension 静态资源 |

Python 包包含完整的前端构建产物，安装后自动注册到 JupyterLab。

## 前端构建流程

### 构建脚本

package.json 中定义的构建脚本：

```json
{
  "scripts": {
    "build": "jlpm build:schema && jlpm build:lib && jlpm build:labextension:dev",
    "build:prod": "jlpm clean && jlpm build:schema && jlpm build:lib && jlpm build:labextension",
    "build:schema": "json2ts schema/plugin.json src/_schema.ts",
    "build:lib": "tsc",
    "build:labextension": "jupyter labextension build .",
    "build:labextension:dev": "jupyter labextension build --development True .",
    "watch": "jlpm build:schema && run-p watch:src watch:labextension"
  }
}
```

### 构建步骤（build:prod）

```
clean → build:schema → build:lib → build:labextension
  │         │               │              │
  │         │               │              └── jupyter labextension build
  │         │               │                  （webpack 打包 → labextension/）
  │         │               │
  │         │               └── tsc 编译 TypeScript → lib/
  │         │
  │         └── json2ts 将 JSON Schema 生成为 TypeScript 类型
  │
  └── 清理之前的构建产物
```

### Step 1: Schema 类型生成

```bash
jlpm build:schema
# 等价于：json2ts schema/plugin.json src/_schema.ts
```

使用 `json-schema-to-typescript` 将 JSON Schema 编译为 TypeScript 类型定义。生成的 `_schema.ts` 包含 `WebRTCSharing` 接口，提供设置项的类型安全。

> **注意**：`_schema.ts` 文件头标注 `DO NOT MODIFY IT BY HAND`，修改 schema 后需重新生成。

### Step 2: TypeScript 编译

```bash
jlpm build:lib
# 等价于：tsc
```

使用 TypeScript 编译器（tsc）将 `src/` 下的 `.ts/.tsx` 文件编译为 JavaScript，输出到 `lib/` 目录。配置在 `tsconfig.json` 中。

### Step 3: JupyterLab 扩展打包

```bash
jupyter labextension build .
```

这是 JupyterLab 的扩展构建命令，内部使用 webpack：
1. 读取 package.json 中的 `jupyterlab` 配置
2. 使用 `webpack.config.js` 中的自定义配置
3. 打包所有依赖（含 vendor 补丁）
4. 输出到 `jupyterlab_webrtc_docprovider/labextension/` 目录
5. 生成 `package.json`（元数据）、`static/`（打包后的 JS/CSS）

### 开发模式（watch）

```bash
jlpm watch
# 等价于：run-p watch:src watch:labextension
```

并行运行两个 watch 进程：
- `watch:src`：`tsc -w` 监听 TypeScript 变更
- `watch:labextension`：`jupyter labextension watch .` 监听扩展资源变更

## Webpack 配置

```javascript
module.exports = {
  resolve: {
    fallback: { crypto: false },
  },
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /y-webrtc\.js$/,
        loader: 'string-replace-loader',
        options: {
          search: 'simple-peer/simplepeer.min.js',
          replace: '../../../vendor/SimplePeerExtended.js',
        },
      },
    ],
  },
};
```

关键点：
- `devtool: 'source-map'`：生成 source map 便于调试
- `crypto: false`：禁用 Node.js crypto polyfill
- `string-replace-loader`：替换 simple-peer 为 SimplePeerExtended

## Python 包构建

### pyproject.toml

```toml
[build-system]
requires = ["jupyter_packaging>=0.10,<1", "jupyterlab>=3.1,<4"]
build-backend = "jupyter_packaging.build_api"

[tool.jupyter-packaging.builder]
factory = "jupyter_packaging.npm_builder"

[tool.jupyter-packaging.build-args]
build_cmd = "build:prod"
npm = ["jlpm"]
```

使用 `jupyter_packaging` 作为构建后端，`npm_builder` 工厂在 Python 包构建时自动调用 npm/yarn 构建前端资源。

### 构建流程（pip install）

```
pip install jupyterlab-webrtc-docprovider
  │
  ├── 1. jupyter_packaging 调用 jlpm install 安装前端依赖
  ├── 2. 调用 jlpm build:prod 构建前端资源
  │     ├── build:schema → _schema.ts
  │     ├── build:lib → lib/ (TypeScript 编译)
  │     └── build:labextension → labextension/static/ (webpack 打包)
  ├── 3. 将 labextension/ 目录复制到 Python 包中
  └── 4. 安装 Python 包到 site-packages
```

### ensured-targets

构建系统确保以下文件存在：
- `jupyterlab_webrtc_docprovider/labextension/package.json`
- `jupyterlab_webrtc_docprovider/labextension/static/style.js`

### skip-if-exists

如果 `labextension/static/style.js` 已存在（如预构建的 wheel 包），跳过前端构建步骤，加速安装。

### _version.py 版本同步

```python
__js__ = json.loads(
    (Path(__file__).parent / "labextension/package.json").read_text(encoding="utf-8")
)
__version__ = (
    __js__["version"]
    .replace("-alpha.", "a")
    .replace("-beta.", "b")
    .replace("-rc.", "rc")
)
```

Python 包版本从前端构建产物的 `package.json` 读取，确保 JS 和 Python 版本号一致。预发布标签转换为 PEP 440 格式。

### 数据文件安装

Python 包将 labextension 资源安装到 JupyterLab 的扩展目录：

```python
data_files_spec = [
    ("share/jupyter/labextensions/@jupyterlite/webrtc-docprovider",
     "jupyterlab_webrtc_docprovider/labextension", "**"),
    ("share/jupyter/labextensions/@jupyterlite/webrtc-docprovider", ".", "install.json"),
]
```

安装路径：`{sys.prefix}/share/jupyter/labextensions/@jupyterlite/webrtc-docprovider/`。

### _jupyter_labextension_paths()

```python
def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": __js__["name"]}]
```

JupyterLab 通过此钩子函数发现扩展路径。`__js__["name"]` 是 `@jupyterlite/webrtc-docprovider`。

## 代码质量工具

package.json 中配置了完整的 lint 工具链：

| 工具 | 命令 | 检查范围 |
|------|------|---------|
| ESLint | `jlpm eslint` | TypeScript 代码质量 |
| Stylelint | `jlpm stylelint` | CSS 样式规范 |
| Prettier | `jlpm prettier` | 代码格式化（TS/JS/CSS/JSON/MD/YAML） |
| yarn-deduplicate | `jlpm deduplicate` | 依赖去重 |

## 发布渠道

| 渠道 | 命令/链接 | 说明 |
|------|----------|------|
| PyPI | `pip install jupyterlab-webrtc-docprovider` | Python 包（含预构建前端） |
| npm | `npm install @jupyterlite/webrtc-docprovider` | JS 包（源码分发） |
| conda-forge | `conda install -c conda-forge jupyterlab-webrtc-docprovider` | Conda 包 |

## 开发安装流程

```bash
# 1. 克隆源码
git clone https://github.com/jupyterlite/jupyterlab-webrtc-docprovider.git
cd jupyterlab-webrtc-docprovider

# 2. 安装 Python 包（开发模式）
python -m pip install -e .

# 3. 链接到 JupyterLab（开发模式）
jupyter labextension develop . --overwrite

# 4. 构建前端
jlpm build

# 5. 监听模式（开发时）
jlpm watch
```

`jupyter labextension develop . --overwrite` 创建符号链接，使源码修改后无需重新安装 Python 包。

## 相关概念

- [Vendor补丁与大消息传输](08-vendor-patches.md)
- [安装与快速开始](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
