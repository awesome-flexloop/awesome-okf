---
type: Concept
title: Monorepo 架构与构建系统
description: jupyter-renderers 的 Lerna monorepo 组织方式、Yarn Workspaces 依赖管理、TypeScript 编译流水线和 Python wheel 构建流程
tags: [monorepo, lerna, yarn, build-system, typescript]
sources:
  - id: root-pkg
    resource: external/libs/jupyter/jupyter-renderers/package.json
    title: root package.json
  - id: lerna
    resource: external/libs/jupyter/jupyter-renderers/lerna.json
    title: lerna.json
  - id: release
    resource: external/libs/jupyter/jupyter-renderers/RELEASE.md
    title: RELEASE.md
  - id: fasta-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/package.json
    title: fasta-extension/package.json
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# Monorepo 架构与构建系统

jupyter-renderers 使用 Lerna + Yarn Workspaces 管理 monorepo，5个扩展包共享构建工具和依赖，同时独立版本化发布。

## 目录结构

```
jupyter-renderers/
├── packages/                    # 所有扩展包
│   ├── fasta-extension/        # FASTA 渲染器
│   │   ├── src/index.ts        # TypeScript 源码
│   │   ├── style/              # CSS 样式和图标
│   │   ├── jupyterlab_fasta/   # Python 包
│   │   │   ├── __init__.py     # 扩展入口点
│   │   │   └── labextension/   # 编译产物（构建生成）
│   │   ├── package.json        # npm 包配置
│   │   └── pyproject.toml      # Python 包配置
│   ├── geojson-extension/      # GeoJSON 渲染器（结构同上）
│   ├── katex-extension/        # KaTeX 排版器（结构同上）
│   ├── mathjax2-extension/     # MathJax2 排版器（结构同上）
│   └── vega3-extension/        # Vega3 渲染器（结构同上）
├── notebooks/                   # 示例 Notebook
├── scripts/                     # 维护脚本
├── package.json                 # 根 package.json（workspaces 配置）
├── lerna.json                   # Lerna 配置
├── install.json                 # 元包安装配置
└── requirements.txt             # Python 依赖
```

## Lerna 配置

lerna.json 配置：[^lerna]

```json
{
  "npmClient": "yarn",
  "useWorkspaces": true,
  "version": "independent"
}
```

| 配置项 | 值 | 含义 |
|--------|-----|------|
| `npmClient` | `"yarn"` | 使用 yarn 作为包管理器（JupyterLab 使用 `jlpm`，即 yarn 的固定版本） |
| `useWorkspaces` | `true` | 委托 Yarn Workspaces 管理依赖提升和符号链接 |
| `version` | `"independent"` | 每个包独立版本号，非统一版本模式 |

**独立版本模式**意味着5个扩展可以各自发布不同版本，例如 katex-extension v3.4.0 和 mathjax2-extension v4.0.0 可以同时存在。

## Yarn Workspaces

根 package.json 通过 `"workspaces": ["packages/*"]` 声明所有子包。[^root-pkg] Yarn 会：

1. 将所有子包的公共依赖提升（hoist）到根 `node_modules/`
2. 在包间创建符号链接，支持跨包引用
3. 通过 `yarn install` 一次性安装所有包的依赖

## 构建流水线

### 两阶段构建

每个包的构建分为两个阶段：[^fasta-pkg]

```
TypeScript 源文件 (src/*.ts)
       │
       ▼  tsc (TypeScript 编译器)
JavaScript 编译产物 (lib/*.js + *.d.ts)
       │
       ▼  jupyter labextension build
JupyterLab 扩展包 (jupyterlab_<name>/labextension/)
       │
       ▼  hatch-jupyter-builder
Python wheel (dist/jupyterlab_<name>-*.whl)
```

**阶段1：TypeScript 编译**

```bash
jlpm build:lib       # tsc --sourceMap（开发模式，生成 source map）
jlpm build:lib:prod  # tsc（生产模式，无 source map）
```

`tsc` 读取包根目录的 `tsconfig.json`，将 `src/` 下的 `.ts` 文件编译为 `lib/` 下的 `.js` 和 `.d.ts`。

**阶段2：JupyterLab 扩展构建**

```bash
jupyter labextension build .                  # 生产构建
jupyter labextension build --development True . # 开发构建
```

此步骤由 `@jupyterlab/builder` 执行，使用 webpack 打包 `lib/` 中的 JS 和 `style/` 中的 CSS，输出到 `jupyterlab_<name>/labextension/static/` 目录。

### 构建命令矩阵

根目录脚本提供批量操作能力：[^root-pkg]

| 命令 | 作用 |
|------|------|
| `jlpm build` | 并行构建所有包（开发模式） |
| `jlpm build:prod` | 并行构建所有包（生产模式） |
| `jlpm watch` | 并行监听所有包的变化 |
| `jlpm build-py` | 全量构建所有 Python wheel 到 `dist/` |
| `jlpm install-ext` | 构建并安装所有 labextension（开发模式） |
| `jlpm install-py` | pip install -e . 安装所有 Python 包（可编辑模式） |

单个包的命令：

| 命令 | 作用 |
|------|------|
| `jlpm build` | TS编译 + labextension开发构建 |
| `jlpm build:prod` | clean + TS生产编译 + labextension生产构建 |
| `jlpm watch` | 并行监听 TS 变化和 labextension 变化 |
| `jlpm clean:all` | 清理所有编译产物和缓存 |

## 开发工作流

```bash
# 克隆仓库
git clone https://github.com/jupyterlab/jupyter-renderers.git
cd jupyter-renderers

# 安装依赖
yarn

# 安装某个扩展进行开发
cd packages/fasta-extension
pip install -e .                                    # 可编辑模式安装 Python 包
jupyter labextension develop . --overwrite          # 链接到 JupyterLab
jlpm run watch                                      # 监听模式（自动重编译）

# 另一个终端启动 JupyterLab
jupyter lab
```

修改 TypeScript 源码后，`jlpm run watch` 自动重编译，刷新浏览器即可看到效果。

## Python wheel 构建

通过 `hatch-jupyter-builder`，Python 包构建时自动调用 npm 构建：

1. `pip install .` 或 `python -m build` 触发 hatchling 构建
2. `hatch-jupyter-builder` 钩子执行 `jlpm build:prod`
3. webpack 产物被复制到 `share/jupyter/labextensions/@jupyterlab/<name>/`
4. 生成包含 JS/CSS 静态资源的 wheel 包

构建后的 wheel 包安装时，JupyterLab 自动从 `share/jupyter/labextensions/` 目录发现预构建扩展，无需 Node.js 环境。

详见 [Python 入口点与打包参考](../references/python-entrypoint-reference.md)。

## 发布流程

### npm 发布 [^release]

```bash
git clean -dfx
yarn
yarn exec lerna version              # 交互式更新版本号
yarn exec lerna publish from-package -m "Publish"  # 发布到 npm
```

### PyPI 发布

```bash
# 创建发布环境
conda create -q -y -n jupyter-renderers-release -c conda-forge twine nodejs jupyter-packaging yarn jupyterlab
conda activate jupyter-renderers-release

# 构建所有包
git clean -dfx
yarn
yarn run build-py
twine upload dist/*
```

## Lint 和代码质量

根目录配置了完整的代码质量工具链：

| 工具 | 命令 | 检查内容 |
|------|------|---------|
| ESLint | `jlpm eslint:check` | TypeScript 代码规范 |
| Prettier | `jlpm prettier:check` | 代码格式化 |
| Stylelint | `jlpm stylelint:check` | CSS 样式规范 |
| `jlpm lint:check` | 三者并行执行 | 全量检查 |

所有工具配置文件在根目录（`.eslintrc.js`、`.prettierrc`、`.stylelintrc`），子包继承根配置。

## 相关概念

- [MIME 渲染器开发模式](02-mime-renderer-pattern.md)
- [扩展类型：MIME 渲染器 vs 应用扩展](03-extension-types.md)
- [Python 入口点与打包参考](../references/python-entrypoint-reference.md)
- [package.json 扩展配置参考](../references/extension-config-reference.md)

[^fasta-pkg]: fasta-extension/package.json
[^lerna]: lerna.json
[^release]: RELEASE.md
[^root-pkg]: root package.json
