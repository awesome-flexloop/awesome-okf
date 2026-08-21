---
title: 构建系统
type: concept
bundle: jupyter-notebook
okf-version: "0.2"
chapter: "08"
difficulty: intermediate
tags: ["build", "hatchling", "lerna", "packaging"]
prerequisites: ["00-introduction"]
sources: ["F-002", "F-005", "F-040"]
next: ["00-quickstart"]
---

# 08 | 构建系统

Jupyter Notebook v7 使用 Hatchling 构建Python包，Lerna管理前端monorepo，jupyter-releaser处理发布流程。

## Python包构建：Hatchling

### 为什么选择Hatchling

Notebook v7 从setuptools迁移到Hatchling（F-002），原因：
- PEP 621标准：`pyproject.toml` 唯一配置源
- 现代构建后端：更快、更可靠
- 插件生态：hatch-jupyter-builder 专门支持Jupyter项目
- 与jupyter-releaser深度集成

### pyproject.toml 核心配置

```toml
[build-system]
requires = ["hatchling>=1.18.0", "hatch-jupyter-builder>=0.9.0", "hatch-nodejs-version>=0.4.1"]
build-backend = "hatchling.build"
```

> **信源**: 基于pyproject.toml构建系统声明（F-002）

关键构建依赖：

| 包 | 作用 |
|----|------|
| `hatchling` | Python包构建后端 |
| `hatch-jupyter-builder` | Jupyter专用构建插件（编译前端、安装labextension） |
| `hatch-nodejs-version` | 从package.json同步版本号到Python包 |

### 构建流程

```
pip install notebook
    │
    ├─ 1. Hatchling读取pyproject.toml
    │
    ├─ 2. hatch-jupyter-builder触发前端构建
    │   ├─ npm install (安装前端依赖)
    │   ├─ npm run build (webpack/rollup打包)
    │   └─ 将构建产物复制到notebook/labextension/
    │
    ├─ 3. hatch-nodejs-version从package.json读取版本
    │   └─ 写入notebook/_version.py
    │
    └─ 4. Hatchling构建wheel/sdist
        ├─ 包含Python源码
        ├─ 包含labextension静态文件
        └─ 包含templates模板目录
```

### hatch-jupyter-builder配置

```toml
[tool.hatch.build.hooks.jupyter-builder]
# 告诉构建器在哪个npm包目录执行构建
# 自动处理labextension安装到Python包
```

这个插件会自动：
1. 调用npm构建前端
2. 将构建产物放到 `notebook/labextension/` 目录
3. 确保 `_jupyter_labextension_paths()` 指向的路径存在

## 前端Monorepo：Lerna

Notebook前端使用Lerna管理13个npm包（F-040）。

### 为什么使用Monorepo

- **代码共享**：多个包共享TypeScript配置、构建脚本、依赖版本
- **原子提交**：跨包修改可以在一个PR中完成
- **一致版本**：所有包使用相同版本号
- **本地链接**：包间引用使用workspace协议，开发时无需发布

### Monorepo结构

```
packages/
├── application/              # 核心应用与Shell
├── application-extension/    # 主应用插件
├── notebook-extension/       # Notebook专属功能
├── tree-extension/           # 文件浏览器
├── tree/                     # Tree页面
├── terminal-extension/       # 终端
├── console-extension/        # 控制台
├── docmanager-extension/     # 文档管理
├── documentsearch-extension/ # 文档搜索
├── help-extension/           # 帮助
├── lab-extension/            # Lab切换
├── ui-components/            # UI组件
└── _metapackage/             # 元包（依赖聚合）
```

> **信源**: 前端包列表（F-040）

### 包间依赖关系

```
_metapackage
  └─ depends on all @jupyter-notebook/* packages

application-extension
  ├─ depends on @jupyter-notebook/application
  ├─ depends on @jupyter-notebook/ui-components
  └─ depends on @jupyterlab/* packages

notebook-extension
  ├─ depends on @jupyter-notebook/application
  └─ depends on @jupyterlab/notebook

tree-extension
  ├─ depends on @jupyter-notebook/application
  ├─ depends on @jupyter-notebook/tree
  └─ depends on @jupyter-notebook/ui-components

terminal-extension
  └─ depends on @jupyter-notebook/application

console-extension
  └─ depends on @jupyter-notebook/application

lab-extension
  ├─ depends on @jupyter-notebook/application
  └─ depends on @jupyter-notebook/ui-components
```

### package.json脚本

```json
{
  "scripts": {
    "build": "lerna run build",
    "build:prod": "lerna run build:prod",
    "clean": "lerna run clean",
    "test": "lerna run test",
    "lint": "lerna run lint",
    "watch": "lerna run watch --parallel"
  }
}
```

开发时常用命令：

```bash
# 安装所有依赖
npm install

# 构建所有包
npm run build

# 开发模式（监听文件变化自动构建）
npm run watch

# 运行测试
npm run test

# 清理构建产物
npm run clean
```

## 开发安装模式

### 可编辑安装（开发模式）

```bash
# 克隆源码
git clone https://github.com/jupyter/notebook.git
cd notebook

# 安装Python包（开发模式）
pip install -e ".[dev,test]"

# 安装前端依赖并构建
npm install
npm run build

# 开发模式（自动重新构建前端）
npm run watch
# 在另一个终端启动Notebook
jupyter notebook
```

开发模式下：
- Python包使用 `pip install -e` 链接到源码
- 前端构建产物链接到 `notebook/labextension/`
- `npm run watch` 监听文件变化自动重建

### JupyterLab开发链接

```bash
# 链接到JupyterLab开发版本
jupyter labextension develop . --overwrite

# 监听前端变化
jupyter labextension watch
```

这使得Notebook使用本地开发版本的JupyterLab包，而非npm安装版本。

## 发布流程：jupyter-releaser

Notebook使用 `jupyter-releaser` 自动化发布流程（F-005）。

### 发布步骤自动化

jupyter-releaser自动执行以下步骤：

1. **版本检查**：确认CHANGELOG、版本号一致性
2. **构建验证**：运行完整构建和测试
3. **前端构建**：npm install + build
4. **Python构建**：构建sdist和wheel
5. **NPM发布**：发布所有 `@jupyter-notebook/*` 包到npm
6. **PyPI发布**：上传wheel到PyPI
7. **GitHub Release**：创建Release和Git标签
8. **Changelog更新**：自动生成CHANGELOG

### 发布配置

```toml
[tool.jupyter-releaser]
# 发布配置
# - npm包前缀: @jupyter-notebook
# - Python包名: notebook
# - 跳过某些步骤的配置
```

## 前端构建工具链

### TypeScript

所有前端代码使用TypeScript编写，每个包有独立的 `tsconfig.json`，继承自根配置。

### CSS/SCSS

样式使用CSS+CSS变量，支持主题定制：
- `base.css` — 基础样式
- `index.css` — 导入样式
- `index.js` — 样式入口（被webpack处理）

### Webpack/Rollup

前端包使用JupyterLab的构建工具链（基于webpack），输出格式：
- ES Module（prebuilt extension）
- 包含JS、CSS、SVG图标等资源

## 版本管理

版本号在三个地方同步：
1. `notebook/_version.py` — Python版本
2. `package.json`（根目录） — JS版本
3. Git tag — 发布标签

`hatch-nodejs-version` 插件确保Python版本自动从package.json读取，避免手动同步。

## 产物结构

### Wheel包内容

安装后的Python包结构：

```
site-packages/notebook/
├── __init__.py
├── _version.py
├── app.py                    # 后端应用（366行）
├── py.typed                  # PEP 561类型标记
├── static/                   # 静态文件
├── templates/                # Jinja2 HTML模板
│   ├── tree.html
│   ├── notebooks.html
│   ├── edit.html
│   ├── consoles.html
│   └── terminals.html
├── labextension/             # 前端构建产物
│   ├── package.json
│   ├── static/               # JS/CSS bundle
│   └── schemas/              # JSON Schemas
└── custom/
    └── custom.css            # 默认自定义CSS
```

### Prebuilt Extension

Notebook v7使用JupyterLab的prebuilt extension机制（不需要 `jupyter labextension install`）：
- 前端JS bundle直接打包在Python wheel中
- 安装后自动被JupyterLab/Notebook发现
- 不需要Node.js环境
- 不需要重新build JupyterLab

## CI/CD

GitHub Actions工作流：

```yaml
# 典型CI流程
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - uses: actions/setup-node@v4
      - run: pip install -e ".[test]"
      - run: npm install && npm run build
      - run: pytest
      - run: npm run test
```

## 常见构建问题

### 前端构建失败

```bash
# 清理并重新安装
npm run clean
rm -rf node_modules
npm install
npm run build
```

### Python包找不到labextension

```bash
# 确保前端已构建
npm run build
# 重新安装Python包
pip install -e .
# 验证labextension路径
jupyter labextension list
```

### 版本不一致

```bash
# 检查版本号
python -c "import notebook; print(notebook.__version__)"
cat package.json | grep version
# 应该一致
```

## 下一步

- → [快速开始](../examples/00-quickstart.md) 从源码构建和启动Notebook
