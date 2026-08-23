---
type: Concept
title: "构建管线：Pixi编排与后处理脚本"
description: "详解Try Jupyter的构建流程：Pixi作为环境管理和任务编排器、jupyter lite build静态站点生成、两个后处理Python脚本（内核过滤+分析注入）的执行机制。"
tags: [build-pipeline, pixi, jupyter-lite-build, post-build, beautifulsoup, kernel-filtering, task-orchestration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml信源"
  - id: scripts
    resource: "/references/scripts-source.md"
    title: "构建脚本信源"
  - id: ci
    resource: "/references/ci-source.md"
    title: "CI/CD工作流信源"
---

# 构建管线：Pixi编排与后处理脚本

Try Jupyter 使用 **Pixi** 作为统一的包管理器和任务编排工具，构建过程分为三个阶段：JupyterLite静态站点生成 → 内核过滤 → 分析代码注入。

## Pixi：构建环境与任务编排

[Pixi](https://pixi.sh) 是基于conda-forge生态的跨平台包管理器，它在本项目中承担双重角色：

1. **环境管理**：创建包含Python 3.12+、Node.js 22+、JupyterLite CLI等所有构建工具的隔离环境
2. **任务编排**：通过 `[tool.pixi.tasks]` 定义可组合的构建任务

### 为什么选择Pixi？

JupyterLite构建需要**混合技术栈**：
- Python工具（JupyterLite CLI、BeautifulSoup）
- Node.js工具（JupyterLab前端构建）
- conda包（Xeus内核的WASM环境）

传统方案需要组合pip/npm/conda三种包管理器，而Pixi基于libmamba，能统一管理所有依赖，跨平台一致。

### Pixi工作区配置

```toml
[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "win-64", "osx-arm64"]
```

- 单一channel：conda-forge（Pyodide/Xeus WASM包通过prefix.dev镜像获取）
- 4个目标平台：Linux x64、macOS Intel、Windows x64、macOS ARM

### Pixi依赖分层

pyproject.toml中的 `[tool.pixi.dependencies]` 按功能分组管理30+依赖包：

| 分组 | 代表包 | 用途 |
|------|--------|------|
| JupyterLite核心 | jupyterlite-core, jupyterlite-pyodide-kernel, jupyterlite-xeus | 站点框架+内核 |
| JupyterLab界面 | jupyterlab, notebook, jupyterlab-night | 主界面+经典界面+暗色主题 |
| 可视化库 | bqplot, ipycanvas, ipyleaflet, ipympl, ipywidgets, plotly | 交互式数据可视化 |
| 语言包 | jupyterlab-language-pack-fr-fr, jupyterlab-language-pack-zh-cn | 国际化 |
| 文件查看器 | jupyterlab-fasta, jupyterlab-geojson | FASTA/GeoJSON文件预览 |
| 终端 | jupyterlite-terminal | Cockle WASM终端 |
| 构建工具 | python>=3.12, nodejs>=22, mamba, micromamba | 构建运行时 |
| 文档主题 | pydata-sphinx-theme, myst-parser | Sphinx文档（RTD使用） |
| 测试框架 | playwright, pytest-playwright, pytest-html, pytest-rerunfailures | E2E测试 |
| 后处理 | beautifulsoup4 | HTML解析修改 |

## 构建任务详解

6个pixi任务构成完整的构建管线：

### 1. clean — 清理构建产物

```bash
rm -rf .jupyterlite.doit.db dist
```

删除：
- `.jupyterlite.doit.db`：JupyterLite使用doit作为构建系统的任务数据库
- `dist/`：上一次构建的输出目录

### 2. build — JupyterLite站点构建

```bash
jupyter lite build
```

这是核心构建步骤，执行以下操作：

1. **读取配置**：加载 `jupyter_lite_config.json` 和 `jupyter-lite.json`
2. **收集内容**：将 `contents` 指定的目录（默认 `content/`）打包到站点
3. **安装JupyterLab扩展**：根据依赖安装和编译所有JupyterLab扩展
4. **编译Xeus内核**：根据 `environment-*.yml` 文件下载emscripten-forge的WASM包
5. **打包Pyodide**：包含Pyodide Python运行时
6. **生成静态文件**：输出完整静态站点到 `dist/` 目录

构建产物结构：
```
dist/
├── lab/                    # JupyterLab界面
│   ├── index.html
│   ├── packages/           # JupyterLab前端包
│   └── extensions/         # 已安装的扩展
├── repl/                   # REPL控制台
├── xeus/                   # Xeus内核
│   └── kernels.json        # 内核列表（后处理修改）
├── pyodide/                # Pyodide运行时和包
├── notebooks/              # 打包的notebook
├── data/                   # 打包的数据文件
├── index.html              # 入口重定向
└── ...                     # 其他静态资源
```

> **注意**：CI构建中在build前会执行 `cp README.md content`，将README复制到content目录使其可在站点中访问。

### 3. filter-kernels — 内核过滤

```bash
python scripts/filter_xeus_kernels.py dist
```

修改 `dist/xeus/kernels.json`，将Xeus内核列表从全部可用内核精简为5个精选内核。详见 [构建后处理脚本](#后处理脚本详解) 部分。

### 4. add-plausible — 分析注入

```bash
python scripts/add_plausible.py dist
```

向dist/中所有HTML文件注入Plausible隐私友好的分析脚本。本地开发通常不需要执行此步骤。

### 5. test — UI测试

```bash
pytest
```

运行Playwright E2E测试，自动验证所有notebook在浏览器中执行无错误。详见 [UI测试框架](07-ui-testing.md)。

### 6. readthedocs — RTD部署

```bash
rm -rf $READTHEDOCS_OUTPUT/html && cp -r dist $READTHEDOCS_OUTPUT/html
```

将dist/复制到ReadTheDocs输出目录，专供ReadTheDocs构建使用。

## 后处理脚本详解

构建完成后，两个Python脚本修改构建产物：

### filter_xeus_kernels.py — 内核白名单过滤

**问题**：jupyterlite-xeus默认会构建并打包所有可用的Xeus内核（包括可能未测试或体积过大的内核），导致站点体积膨胀。

**解决方案**：构建后用脚本过滤kernels.json，只保留经过测试的内核。

```python
KERNELS_TO_KEEP = {"xcpp23", "xc23", "xr", "xpython", "xsqlite"}

def filter_kernels(dist_dir: Path) -> None:
    kernels_file = dist_dir / "xeus" / "kernels.json"
    kernels = json.loads(kernels_file.read_text())
    filtered = [k for k in kernels if k["kernel"] in KERNELS_TO_KEEP]
    kernels_file.write_text(json.dumps(filtered))
```

执行流程：
1. 读取 `dist/xeus/kernels.json` 中的内核数组
2. 过滤出kernel字段在白名单中的条目
3. 写回过滤后的JSON
4. 打印过滤前后的内核数量和ID列表

> 此脚本不删除WASM文件本身（它们仍在dist中），只从内核列表中移除，从而在UI中隐藏。如果需要彻底减小体积，需要额外清理未使用的WASM文件。

### add_plausible.py — Plausible分析注入

**问题**：需要了解站点使用情况（页面访问量、notebook使用率），但不想使用Google Analytics等侵犯隐私的分析工具。

**解决方案**：构建后向所有HTML页面注入[Plausible](https://plausible.io)（隐私友好的开源分析）脚本。

```python
PLAUSIBLE_SRC = "https://plausible.io/js/pa-B75UO5--FNXYQSG7GBWkf.js"
PLAUSIBLE_INIT = "window.plausible=window.plausible||function(){...};plausible.init()"

def inject_plausible(dist_dir: Path) -> None:
    for html_file in dist_dir.rglob("*.html"):
        soup = BeautifulSoup(html_file.read_text(), "html.parser")
        head = soup.find("head")
        # 添加外部script标签（async加载）
        external_script = soup.new_tag("script", async_="", src=PLAUSIBLE_SRC)
        head.append(external_script)
        # 添加内联初始化script
        init_script = soup.new_tag("script")
        init_script.string = PLAUSIBLE_INIT
        head.append(init_script)
        html_file.write_text(str(soup))
```

执行流程：
1. 递归查找dist/下所有 `.html` 文件
2. 用BeautifulSoup的html.parser解析HTML
3. 找到 `<head>` 标签
4. 创建并追加两个 `<script>` 标签：
   - 外部脚本：`async` 属性加载Plausible客户端
   - 内联脚本：初始化plausible对象（支持hash-based路由）
5. 写回修改后的HTML

初始化脚本支持JupyterLite的hash路由模式（`#/lab/...`），确保SPA导航被正确追踪。

## 完整构建管线流程图

```
┌─────────────────────────────────────────────────────────────┐
│                     开发/CI 环境                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  pixi install ──→ 安装所有构建依赖（Python/Node/JupyterLite）  │
│       │                                                     │
│       ↓                                                     │
│  ┌─────────────────────────────────────────────┐            │
│  │         pixi run build                      │            │
│  │  (cp README.md content → jupyter lite build) │            │
│  └────────────────────┬────────────────────────┘            │
│                       ↓                                     │
│              ┌─────────────────┐                            │
│              │    dist/ 目录    │  完整静态站点（含全部内核）    │
│              └────────┬────────┘                            │
│                       ↓                                     │
│  ┌─────────────────────────────────────────────┐            │
│  │     pixi run filter-kernels                 │            │
│  │  修改 dist/xeus/kernels.json → 只保留5个内核  │            │
│  └────────────────────┬────────────────────────┘            │
│                       ↓                                     │
│  ┌─────────────────────────────────────────────┐            │
│  │     pixi run add-plausible（仅CI正式部署）    │            │
│  │  BeautifulSoup注入Plausible脚本到所有HTML     │            │
│  └────────────────────┬────────────────────────┘            │
│                       ↓                                     │
│              ┌─────────────────┐                            │
│              │  dist/（最终）   │  可部署的静态站点            │
│              └────────┬────────┘                            │
│                       ↓                                     │
│         ┌─────────────┼─────────────┐                       │
│         ↓             ↓             ↓                       │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│   │本地预览   │  │GitHub    │  │ReadTheDocs│                 │
│   │http.server│  │Pages     │  │PR预览     │                 │
│   └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
│  ── CI Only ──                                              │
│  pixi run test → Playwright E2E测试 → 通过后才部署           │
└─────────────────────────────────────────────────────────────┘
```

## CI与本地构建的差异

| 步骤 | 本地开发 | CI（GitHub Actions） | RTD |
|------|---------|-------------------|-----|
| `cp README.md content` | 手动（如需） | ✅ 自动 | ❌ 无 |
| `pixi run build` | ✅ | ✅ | ✅ |
| `pixi run filter-kernels` | ✅ 推荐 | ✅ | ✅ |
| `pixi run add-plausible` | ❌ 通常不需要 | ✅ | ❌ |
| `pixi run test` | 可选 | ✅ 必须通过 | ❌ |
| `pixi run readthedocs` | ❌ | ❌ | ✅ |

## 构建命令速查

```bash
# 首次设置
pixi install

# 完整构建（本地开发）
pixi run build && pixi run filter-kernels

# 本地预览
pixi run python -m http.server 8000 --directory dist

# 清理
pixi run clean

# 运行测试
pixi run playwright install --with-deps chromium  # 首次
pixi run test
```

## 相关概念

- [快速开始](01-getting-started.md)
- [配置系统](03-configuration-system.md)
- [内核生态](04-kernel-ecosystem.md)
- [UI测试框架](07-ui-testing.md)
- [部署](08-deployment.md)
