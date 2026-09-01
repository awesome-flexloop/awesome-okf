---
type: Concept
title: "仓库目录结构详解"
description: "全面解析 jupyterlab-demo 的目录组织：配置文件层、构建层、素材层、输出层的分层结构，理解每个文件和目录的作用"
tags: [repository, structure, directory, binder, notebooks, data, narrative]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: readme, resource: "/references/repo-readme.md", title: "README 信源" }
  - { id: build, resource: "/references/build-py-source.md", title: "build.py 源码信源" }
---

# 仓库目录结构详解

jupyterlab-demo 的目录设计遵循**分层组织**原则，将配置、构建逻辑、源素材和输出产物清晰分离。

## 顶层目录树

```
jupyterlab-demo/
├── .binder/              # Binder 环境配置层
│   ├── environment.yml   # Conda 依赖定义
│   ├── postBuild         # 构建后脚本
│   └── workspace.json    # 工作区布局预设
├── .github/
│   └── workflows/        # CI/CD 配置
│       ├── main.yml      # 构建与测试流水线
│       └── binder_on_pr.yml  # PR Binder 徽章
├── data/                 # 内置演示数据
├── narrative/            # 演示脚本（演讲稿）
├── notebooks/            # Jupyter Notebook 示例
├── slides/               # 演示幻灯片
├── .gitignore
├── LICENSE               # BSD-3-Clause
├── README.md
├── build.py              # 构建脚本（核心）
├── jupyter_notebook_config.py  # Jupyter 服务器配置
└── talks.yml             # 演讲场景配置
```

## 分层解析

### 第一层：环境配置层（.binder/）

这是 Binder 识别并构建环境的关键目录。Binder 在构建镜像时会自动查找 `.binder/` 目录（或根目录）下的配置文件。

| 文件 | 职责 | 类比 |
|------|------|------|
| `environment.yml` | 定义所有 conda/pip 依赖 | 项目的 package.json / requirements.txt |
| `postBuild` | 镜像构建完成后执行的脚本 | Dockerfile 的 RUN 指令 |
| `workspace.json` | JupyterLab 工作区布局定义 | IDE 的工作区配置文件 |

这三个文件共同构成了 Binder 配置的"三要素"——环境依赖、构建步骤、界面布局。详见 [Binder 环境配置三要素](02-binder-config.md)。

### 第二层：构建逻辑层

| 文件 | 职责 |
|------|------|
| `build.py` | Python 构建脚本：克隆外部仓库、复制文件、按 talks.yml 组装演讲目录 |
| `talks.yml` | 声明式配置：定义每种演讲场景需要哪些文件/文件夹，以及重命名映射 |

build.py 是唯一有"逻辑"的 Python 文件，但它非常精简（约100行），职责明确：
1. 克隆外部数据仓库到 `demofiles/`
2. 读取 talks.yml
3. 按配置复制/重命名文件到各演讲输出目录

### 第三层：源素材层

这是演示者手工维护的内容，按类型分目录存放：

#### data/ — 演示数据文件

| 文件 | 类型 | 许可证 | 演示用途 |
|------|------|--------|---------|
| `iris.csv` | CSV表格 | CC0（Fisher鸢尾花数据集） | DataGrid/CSV查看器 |
| `hubble.jpg` | JPEG图片 | NASA/ESA公共领域 | 图片查看器 |
| `Museums_in_DC.geojson` | GeoJSON | CC-BY 4.0 | GeoJSON地图查看器 |
| `bar.vl.json` | Vega-Lite JSON | BSD-3 | Vega-Lite可视化 |
| `zika_assembled_genomes.fasta` | FASTA序列 | 公开数据 | FASTA序列查看器 |
| `jupiter.mp4` | 视频 | CC0 | 视频播放器 |
| `rocket.wav` | 音频 | CC0 | 音频播放器 |
| `japan_meteorological_agency_*.json` | JSON | CC-BY 4.0 | JSON查看器 |
| `Dockerfile` | Dockerfile | - | 文件编辑器语法高亮 |

#### narrative/ — 演示脚本

四份 Markdown 文件，作为演讲者的参考脚本：

| 文件 | 用途 |
|------|------|
| `jupyterlab.md` | 核心演示脚本（9个功能章节） |
| `markdown_python.md` | Markdown+Python 混编示例（可执行） |
| `scipy2017.md` | SciPy 2017 会议专用脚本 |
| `QConAI.md` | QCon AI 会议专用脚本（最完整） |

#### notebooks/ — Notebook 示例

| 文件 | 内核 | 演示内容 |
|------|------|---------|
| `Data.ipynb` | Python | 数据处理基础（CI验证） |
| `Fasta.ipynb` | Python | FASTA 生物信息学（CI验证） |
| `R.ipynb` | R | R 语言数据科学（CI验证） |
| `Cpp.ipynb` | C++ (xeus-cling) | C++ 交互式编程 |
| `Julia.ipynb` | Julia | Julia 语言（postBuild中删除） |
| `Lorenz.ipynb` | Python | 洛伦兹吸引子3D可视化（默认打开） |
| `lorenz.py` | Python | Lorenz 求解辅助模块 |
| `audio/audio.wav` | - | 音频嵌入示例 |
| `images/` | - | Notebook 中引用的图片资源 |

#### slides/ — 幻灯片

| 文件 | 格式 |
|------|------|
| `jupyterlab-slides.key` | Keynote |
| `jupyterlab-slides.pdf` | PDF |
| `jupyterlab-slides_scipy19.pdf` | PDF（SciPy 2019版） |

### 第四层：构建输出层（运行时生成，.gitignore排除）

这些文件/目录由 `build.py` 和 `postBuild` 生成，不纳入版本控制：

| 输出 | 来源 | 生命周期 |
|------|------|---------|
| `demofiles/` | build.py: setup_demofiles() | 构建中间产物，postBuild中删除 |
| `test_talk/` | build.py: setup_talks() | 测试输出 |
| `scipy2017/` | build.py: setup_talks() | SciPy演讲输出 |
| `jupytercon2017/` | build.py: setup_talks() | JupyterCon演讲输出 |
| `demo/` | build.py: setup_talks() | 通用演示输出（Binder最终产物） |
| `move_this_file.txt` | build.py | 拖放演示空文件 |
| `move_it_here/` | build.py | 拖放演示空目录 |

### 第五层：CI与配置

| 文件 | 职责 |
|------|------|
| `.github/workflows/main.yml` | 使用 micromamba 安装环境，执行3个Notebook验证，运行build.py |
| `.github/workflows/binder_on_pr.yml` | PR 打开时自动评论 Binder 链接 |
| `jupyter_notebook_config.py` | 启用协作模式（`c.LabApp.collaborative = True`）和隐藏文件访问 |

## 构建数据流

```
源素材层                    构建层                     输出层
─────────                  ──────                     ──────
data/ ─────────┐
narrative/ ────┤
notebooks/ ────┤            ┌──────────┐
slides/ ───────┤            │ build.py │           demo/
               ├─── talks.yml ──→ setup_talks() ──→  ├── notebooks/
外部7个仓库 ────┘            │          │            ├── data/
       │                    │ setup_   │            ├── TCGA_Data/
       └─ git clone ──→ demofiles/ ────┤            ├── *.csv
                            └──────────┘            ├── *.ipynb
                                                      └── ...
```

构建过程中，源文件被复制和重命名（而非移动），保持源素材层的干净。postBuild 在构建完成后清理 `demofiles/` 等中间目录，最终镜像中只保留 `demo/` 目录作为用户可见的内容。

## .gitignore 策略

`.gitignore` 文件明确排除了：
- Python 编译产物（`__pycache__/`、`*.pyc`）
- 打包产物（`dist/`、`*.egg-info/`）
- 虚拟环境（`venv/`、`ENV/`）
- Notebook 检查点（`.ipynb_checkpoints`）
- **构建产物**：`demofiles/`、`test_talk/`、`scipy2017/`、`demo/`

这确保只有源素材和配置文件被版本控制，构建输出始终是可重现的。

## 相关概念

- [项目定位与设计理念](00-introduction.md)
- [Binder 环境配置三要素](02-binder-config.md)
- [build.py 与 talks.yml 配置化组装](03-build-system.md)
