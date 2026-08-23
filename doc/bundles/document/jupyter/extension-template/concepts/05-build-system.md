---
type: Concept
title: 双包构建系统
description: 深入理解 JupyterLab 扩展的 NPM+Python 双包构建架构、hatchling + jupyter-builder + tsc 协同工作流程，以及开发模式与生产构建的区别。
tags: [build-system, hatchling, jupyter-builder, tsc, dual-package, npm, python]
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

## 双包构建系统

JupyterLab 扩展采用独特的"双包"分发架构：前端代码是 NPM 包（TypeScript/JavaScript），但通过 Python wheel 包分发给终端用户。这意味着用户只需 `pip install myextension` 即可安装扩展，不需要 Node.js 环境。理解这套构建系统是开发 JupyterLab 扩展的关键。

## 构建工具链

三个核心工具协同工作：

| 工具 | 职责 | 配置文件 |
|------|------|---------|
| **tsc**（TypeScript Compiler） | 将 TypeScript 编译为 JavaScript | tsconfig.json |
| **jupyter-builder** | 将编译后的 JS/CSS 打包为 JupyterLab 可加载的 labextension 格式 | package.json 的 `jupyterlab` 字段 + pyproject.toml 的 `[tool.hatch.build.hooks.jupyter-builder]` |
| **hatchling** | Python 包构建后端，将 labextension 打包进 wheel | pyproject.toml |

辅助工具：
- **hatch-nodejs-version**：从 package.json 读取版本号同步到 Python 包
- **jlpm**：JupyterLab 内置的 yarn，用于运行 NPM scripts 和安装 JS 依赖

## 构建流程详解

### 生产构建流程（`pip install` 或 `python -m build`）

```
1. pip/python -m build 触发 hatchling 构建
2. hatchling 执行 jupyter-builder 构建钩子
3. jupyter-builder 调用 jlpm build:prod
   a. jlpm clean → 清理旧构建产物
   b. tsc（生产模式）→ TypeScript 编译为 JS 到 lib/
   c. jupyter-builder build → 打包 labextension 到 myextension/labextension/
4. hatchling 将 labextension/ 内容复制到 wheel 的 share/jupyter/labextensions/ 目录
5. 生成 wheel/sdist 包
```

对应的 npm scripts：

```json
{
  "build:prod": "jlpm clean && jlpm build:lib:prod && jlpm build:labextension",
  "build:lib:prod": "tsc",
  "build:labextension": "jupyter-builder build ."
}
```

pyproject.toml 中的钩子配置：

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.ensured-targets]
# 构建完成后必须存在这些文件
"myextension/labextension/package.json" = ""
"myextension/labextension/static/style.js" = ""  # 非 theme 类型
```

### 开发构建流程（`pip install -e .`）

```
1. pip install -e . 以可编辑模式安装 Python 包
2. hatchling 执行 jupyter-builder 开发模式构建
3. jupyter-builder 调用 jlpm install:extension
   a. tsc --sourceMap → 编译 TS 到 JS（含 sourcemap）
   b. jupyter-builder build --development True → 开发模式打包
4. jupyter-builder develop . --overwrite 创建符号链接
5. 现在 JupyterLab 可以通过符号链接找到扩展
```

对应的 npm scripts：

```json
{
  "build": "jlpm build:lib && jlpm build:labextension:dev",
  "build:lib": "tsc --sourceMap",
  "build:labextension:dev": "jupyter-builder build --development True .",
  "install:extension": "jlpm build"
}
```

可编辑安装的 pyproject.toml 配置：

```toml
[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "myextension/labextension"
```

## 版本同步机制

双包架构要求 NPM 和 Python 包版本一致。hatch-nodejs-version 插件自动完成这个同步：

```toml
[tool.hatch.version]
source = "nodejs"

[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls", "keywords"]
```

- `package.json` 的 `version` 字段是唯一版本真值（"0.1.0"）
- 构建时 hatch-nodejs-version 读取 package.json 的 version，写入 `_version.py`
- description、authors、urls、keywords 也从 package.json 同步
- **不要手动编辑 pyproject.toml 中的版本**——始终修改 package.json

版本更新命令：
```bash
hatch version <new-version>  # 更新 package.json 中的版本
```

## Wheel 包内容

构建生成的 wheel 包中，扩展文件安装到以下位置：

| 源路径（项目中） | 目标路径（安装后） | 说明 |
|-----------------|-------------------|------|
| `myextension/labextension/` | `share/jupyter/labextensions/myextension/` | 前端静态资源（JS/CSS/fonts） |
| `install.json` | `share/jupyter/labextensions/myextension/install.json` | 扩展元数据 |
| `myextension/`（Python 源码） | `site-packages/myextension/` | Python 包（含 `__init__.py`） |
| `jupyter-config/server-config/` | `etc/jupyter/jupyter_server_config.d/` | 服务端自动启用配置（仅 frontend-and-server） |

关键点：
- 前端资源安装到 `share/jupyter/labextensions/<labextension-name>/`，这是 JupyterLab 扫描扩展的标准路径
- `_jupyter_labextension_paths()` 返回 `{"src": "labextension", "dest": "<labextension-name>"}`，告诉 JupyterLab 在 Python 包的 `labextension/` 子目录中找前端资源
- 通过 `shared-data` 机制而非标准 Python 包路径安装前端资源

## 开发模式 watch 工作流

开发时最常用的模式：

```bash
# 终端 1：启动 TypeScript 监听 + labextension 监听
jlpm run watch
```

`jlpm run watch` 并行执行：
- `tsc -w --sourceMap`：监听 src/ 中 .ts 文件变化，增量编译到 lib/
- `jupyter-builder watch .`：监听 lib/ 变化，自动重新打包 labextension

```bash
# 终端 2：启动 JupyterLab
jupyter lab
```

修改 TypeScript 代码后：
1. tsc 检测到变化，增量编译到 lib/（约1-2秒）
2. jupyter-builder 检测到 lib/ 变化，重新打包 labextension
3. 在浏览器中刷新页面（Ctrl+R/Cmd+R）即可看到变化

修改 Python 代码后（frontend-and-server）：
1. **重启 JupyterLab 服务器**（Ctrl+C 然后 `jupyter lab`）
2. 不需要重新构建前端

记忆口诀：**"改了什么，重启什么"**
- 改了 JS/TS → 构建（watch 自动完成）→ 刷新浏览器
- 改了 Python → 重启 JupyterLab 服务

## 关键构建命令速查

| 命令 | 作用 | 何时使用 |
|------|------|---------|
| `jlpm install` | 安装 NPM 依赖 | 首次克隆或 package.json 变更后 |
| `jlpm build` | 开发模式完整构建 | 首次设置或 build 产物损坏时 |
| `jlpm build:prod` | 生产模式构建 | 发布前验证 |
| `jlpm run watch` | 监听模式自动构建 | 日常开发 |
| `jlpm clean:all` | 清理所有构建产物 | 构建状态异常时重置 |
| `pip install -e ".[dev]"` | 可编辑安装 Python 包 | 首次设置 |
| `jupyter-builder develop . --overwrite` | 符号链接扩展到 JupyterLab | pip install -e 后执行 |
| `python -m build` | 生成 wheel/sdist 包 | 发布前打包 |

## 常见构建问题

### 扩展安装了但 JupyterLab 不显示

最常见的原因是**只构建了前端但没有安装到 JupyterLab**：

```bash
# ❌ 错误：只运行 jlpm build 不够
jlpm build

# ✅ 正确：需要安装 + 开发链接
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
jupyter labextension list  # 确认显示 OK
```

### 修改代码后不生效

- 改了 TS：确认 `jlpm run watch` 在运行，等待构建完成后刷新浏览器
- 改了 Python：必须重启 JupyterLab 服务器（不是只刷新浏览器）
- 检查 `lib/` 目录是否有最新编译的 .js 文件
- 检查 `myextension/labextension/` 是否有最新构建

### 构建状态损坏

```bash
jlpm clean:all
jlpm install
jlpm build
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
```

## 相关概念

- [项目结构详解](/concepts/04-project-structure.md)
- [前端扩展开发](/concepts/06-frontend-extension.md)
- [打包与发布](/concepts/13-packaging-release.md)
- [pyproject.toml 模板解析](/references/pyproject-source.md)
- [package.json 模板解析](/references/package-json-source.md)
