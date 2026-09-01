---
type: Example
title: 本地开发环境搭建
description: 从零搭建 jupyterlite-lsp 的本地开发环境，包括 conda 环境、依赖安装、构建流程和调试技巧
tags: [example, development, setup, debug, local]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: build
    resource: /references/build-source.md
    title: 构建系统源码引用
---

## 环境要求

| 工具 | 版本要求 |
|------|---------|
| Node.js | >=18, <19 |
| Python | >=3.8, <3.12 |
| conda/mamba | 推荐 Mambaforge |
| Git | 任意版本 |

## 步骤一：克隆源码

```bash
git clone https://github.com/jupyterlite/lsp.git jupyterlite-lsp
cd jupyterlite-lsp
```

## 步骤二：创建 conda 环境

使用项目提供的 .binder/environment.yml：

```bash
mamba env update --file .binder/environment.yml --prefix .venv
source activate ./.venv
```

这会安装：
- Node.js 18.x
- Python 3.8-3.11
- JupyterLab 3.5-4.0
- jupyterlab-lsp >=3.10.2
- doit-with-toml、flit（构建工具）
- black、isort、ssort（代码格式化）
- pydata-sphinx-theme、myst-nb（文档）
- jupyterlite ==0.1.0b15（通过 pip 安装）

## 步骤三：安装 JS 依赖

```bash
jlpm setup:js
```

该命令执行：
```bash
jlpm --prefer-offline --ignore-optional --registry=https://registry.npmjs.org
yarn-deduplicate -s fewer --fail
```

`jlpm` 是 JupyterLab 定制的 yarn 版本。`--prefer-offline` 优先使用缓存加速安装。

## 步骤四：安装 Python 包（开发模式）

```bash
jlpm setup:py:pip
jlpm setup:py:ext
```

- `setup:py:pip` 执行 `pip install -e . --no-deps --ignore-installed --no-build-isolation`，以可编辑模式安装
- `setup:py:ext` 执行 `jupyter labextension develop . --overwrite`，将 labextension 链接到 JupyterLab

## 步骤五：一键就绪（推荐）

使用 doit 自动化以上步骤：

```bash
doit binder
```

这会运行所有 setup 任务并输出就绪提示：

```
ready to start work with:
    jupyter lab --no-browser --debug
to rebuild the extension when sources change, run this in another terminal:
    jlpm watch
```

## 步骤六：构建扩展

首次运行需要编译 TypeScript 和 webpack：

```bash
jlpm build:lib    # tsc 编译 TS → JS
jlpm build:ext    # webpack 构建 labextension
```

或者使用 doit：

```bash
doit build       # 运行所有 build:* 任务
```

## 步骤七：启动开发服务器

在终端1启动 JupyterLab：

```bash
jupyter lab --no-browser --debug
```

在终端2启动 TypeScript 监听模式：

```bash
jlpm watch       # lerna run --parallel --stream watch
```

`watch` 模式会在源文件变更时自动重新编译，JupyterLab 刷新页面即可看到变更。

## 步骤八（可选）：构建 JupyterLite 示例站点

```bash
jlpm lite:build
```

这会在 `examples/` 目录执行 `jupyter lite build`，输出到 `build/lite/`。构建过程包括：
1. 收集所有 labextension
2. 构建 JupyterLite 静态站点
3. doit 自动执行 `hack:connection.js` 任务（WebSocket patch）

构建完成后可以用任何静态服务器预览：

```bash
cd build/lite
python -m http.server 8000
# 访问 http://localhost:8000
```

## 调试技巧

### 启用 LSP 调试日志

在 URL 中添加 `LSP_LITE_DEBUG` 参数：

```
http://localhost:8888/lab?LSP_LITE_DEBUG
```

这会启用 console.debug/console.error 输出，包括：
- WebSocket 连接建立/关闭
- LSP 消息收发（writing/yielding 日志）
- ServerConnection settings 信息
- LanguageServers 状态

### 查看已安装的 labextension

```bash
jupyter labextension list
```

确认 `@jupyterlite/lsp` 和 `@jupyterlite/lsp-yaml` 已启用。

### 查看 pip freeze

setup:py:pip 任务会将 pip freeze 输出写入 `build/pip-freeze.txt`：

```bash
cat build/pip-freeze.txt
```

### 代码格式化

```bash
jlpm fix:js:prettier   # JS/TS/JSON/Markdown 格式化
jlpm fix:py:black      # Python black 格式化
jlpm fix:py:isort      # Python import 排序
jlpm fix:py:ssort      # Python 语句排序
```

### 清理构建产物

```bash
rm -rf build/ dist/ src/jupyterlite_lsp/_d/
jlpm run clean  # 如果有 clean 脚本
```

### 查看可用的 doit 任务

```bash
doit list          # 列出所有任务
doit list --deps   # 显示任务依赖
doit info <task>   # 查看任务详情
```

## 常见问题

### Q: jupyter labextension list 中看不到扩展

确保已运行 `jlpm setup:py:ext`（即 `jupyter labextension develop . --overwrite`），并重新启动 JupyterLab。

### Q: WebSocket 连接失败

确认 `doit hack` 任务已执行（在 `lite:build` 后自动执行），检查 build/lite/ 中 connection.js 是否包含 `new window.MockWebSocket`。

### Q: YAML 补全不工作

打开浏览器控制台查看是否有 Worker 加载错误。yaml-language-server 的 Worker 需要通过 webpack 正确打包。

### Q: Node.js 版本不对

使用 `node --version` 确认版本为 18.x。可以通过 conda 安装指定版本：`mamba install nodejs=18`。

## 相关概念

- [快速开始](../concepts/01-getting-started.md)
- [构建系统详解](../concepts/07-build-system.md)
- [Mock-Socket 桥接机制](../concepts/05-mock-socket-bridge.md)
- [构建系统源码引用](../references/build-source.md)
