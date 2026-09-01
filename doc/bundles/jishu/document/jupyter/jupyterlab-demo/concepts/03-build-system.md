---
type: Concept
title: "build.py 与 talks.yml 配置化组装系统"
description: "掌握 build.py + talks.yml 的声明式文件组装模式：从共享素材库按 YAML 配置为不同演讲场景自动组装演示材料，实现一次准备、多场景复用"
tags: [build, talks.yml, configuration, automation, python, ruamel-yaml]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: build, resource: "/references/build-py-source.md", title: "build.py源码信源" }
  - { id: talks, resource: "/references/talks-yml-source.md", title: "talks.yml信源" }
---

# build.py 与 talks.yml 配置化组装系统

jupyterlab-demo 的核心设计模式是**配置化文件组装**：用一个简短的 Python 脚本（build.py，约100行）加一个声明式 YAML 文件（talks.yml），实现从共享素材库为不同演讲场景自动组装演示材料。这种模式让"同一套素材，多场会议复用"变得简单可控。

## 设计问题

在技术会议上演示 JupyterLab 时，面临以下挑战：

1. **素材来源多样**：部分文件在本仓库（notebooks/、data/），部分来自外部开源仓库（PythonDataScienceHandbook、bqplot等）
2. **场景差异**：不同会议（SciPy、JupyterCon、QCon AI）受众不同，需要展示不同的文件组合
3. **文件命名友好**：演示时文件名应简洁有意义（如 `big.csv` 而非深层路径），但源文件名需要保持原始结构
4. **环境干净**：Binder 镜像中不应暴露内部构建文件，只保留演示需要的内容

传统做法是为每个会议准备一个独立目录，手动复制重命名文件——这导致大量重复、容易遗漏、修改不同步。build.py + talks.yml 用配置化方式解决了这些问题。

## talks.yml 配置格式

talks.yml 定义了演讲场景的文件组装规则，每个场景（talk）支持三种操作：

```yaml
<talk_name>:
    files:                        # 直接复制的文件列表
        - <源文件路径>
    folders:                      # 递归复制的文件夹映射
        <源文件夹路径>: <目标文件夹名>
    rename:                       # 复制后重命名的文件映射
        <源文件路径>: <目标文件名>
```

### 三种操作的语义区别

| 操作 | 源路径处理 | 目标位置 | 典型用途 |
|------|-----------|---------|---------|
| `files` | 取 `os.path.basename(f)` | `talk_name/<basename>` | 直接使用的文件 |
| `folders` | 整个目录树 | `talk_name/<dst>` | 数据目录、notebook目录 |
| `rename` | 从 talk 目录或原始路径 | `talk_name/<newname>` | 需要友好命名的文件 |

### rename 的双重策略

`rename` 操作处理两种情况：
1. 如果文件已被 files/folders 复制到 talk 目录，执行 `os.rename()`（重命名）
2. 如果文件尚未复制（来自 demofiles/ 的外部仓库），执行 `shutil.copy()`（复制+重命名）

这个设计确保了：
- 内部文件（files列表中的）先复制再改名
- 外部文件（demofiles/中的）直接复制到新名称
- 不会重复复制

## build.py 实现解析

### 核心函数一：setup_demofiles()

负责下载外部演示数据：

```python
def setup_demofiles():
    demo_folder = Path("demofiles")
    demo_folder.mkdir(parents=True, exist_ok=True)

    reponames = [
        "jakevdp/PythonDataScienceHandbook",
        "swissnexSF/Urban-Data-Challenge",
        "altair-viz/altair",
        "QuantEcon/QuantEcon.notebooks",
        "theandygross/TCGA",
        "aymericdamien/TensorFlow-Examples",
        "bloomberg/bqplot",
    ]
    for repo in reponames:
        target_path = demo_folder / Path(repo.split("/")[1])
        if not target_path.is_dir():
            subprocess.check_call([
                "git", "clone", "--depth", "1",
                f"https://github.com/{repo}.git"
            ], cwd=demo_folder)

    Path("move_this_file.txt").touch()
    Path("move_it_here").mkdir(exist_ok=True)
```

**关键设计决策**：
- **浅克隆**：`--depth 1` 只下载最新版本，大幅减少构建时间和镜像体积
- **幂等性**：`if not target_path.is_dir()` 检查已存在则跳过，支持重复运行
- **拖放演示**：创建空文件和空目录用于演示 JupyterLab 的拖放功能

### 核心函数二：setup_talks()

按 YAML 配置组装各演讲目录：

```python
def setup_talks():
    with open("talks.yml", "r") as stream:
        talks = yaml.load(stream)
    for talk_name in talks:
        Path(talk_name).mkdir(parents=True, exist_ok=True)

        if "files" in talks[talk_name]:
            for f in talks[talk_name]["files"]:
                copied_path = os.path.join(talk_name, os.path.basename(f))
                shutil.copy(f, copied_path)
                assert os.path.isfile(copied_path), f"{f} failed to copy"

        if "folders" in talks[talk_name]:
            for src, dst in talks[talk_name]["folders"].items():
                dst = os.path.join(talk_name, dst)
                if not os.path.exists(dst):
                    shutil.copytree(src, dst)

        if "rename" in talks[talk_name]:
            for old_file, new_file in talks[talk_name]["rename"].items():
                moved_file = os.path.join(talk_name, os.path.basename(old_file))
                if os.path.isfile(moved_file):
                    os.rename(moved_file, os.path.join(talk_name, new_file))
                elif os.path.isfile(old_file):
                    shutil.copy(old_file, os.path.join(talk_name, new_file))
```

**关键设计决策**：
- **防御性断言**：文件复制后用 `assert` 验证，CI 中构建失败可立即发现
- **文件夹存在检查**：`if not os.path.exists(dst)` 避免覆盖已有目录
- **顺序依赖**：files → folders → rename，rename 在最后执行以确保文件已到位

## 四种演讲场景对比

| 配置项 | test_talk | scipy2017 | jupytercon2017 | demo |
|--------|-----------|-----------|----------------|------|
| 目的 | 测试验证 | SciPy会议 | JupyterCon | 通用演示 |
| files数量 | 1 | 4 | 4 | 3 |
| folders | 1(TCGA) | 0 | 0 | 3 |
| rename数量 | 1 | 4 | 4 | 8 |
| 包含notebooks | ❌ | ❌ | ❌ | ✅ |
| 包含slides | ❌ | ❌ | ❌ | ✅ |
| 包含data/ | ❌ | ❌ | ❌ | ✅ |

### demo 场景的完整组装逻辑

`demo` 配置是最完整的，也是 Binder 实际使用的场景：

1. **files 复制**：
   - `slides/jupyterlab-slides.pdf` → `demo/jupyterlab-slides.pdf`
   - `narrative/jupyterlab.md` → `demo/jupyterlab.md`
   - `narrative/markdown_python.md` → `demo/markdown_python.md`

2. **folders 复制**：
   - `demofiles/TCGA/Extra_Data` → `demo/TCGA_Data/`
   - `notebooks/` → `demo/notebooks/`
   - `data/` → `demo/data/`

3. **rename 重命名/复制**（8项）：
   - 大数据CSV → `big.csv`
   - 小数据CSV → `smaller.csv`
   - Vega-Lite JSON → `vega.vl.json`
   - Pandas手册Notebook → `notebooks/pandas.ipynb`
   - bqplot示例Notebook → `notebooks/bqplot.ipynb`
   - 哈勃图片 → `hubble.jpg`
   - Lorenz Notebook → `Lorenz.ipynb`
   - lorenz.py → `lorenz.py`

### 为什么需要 rename 映射？

rename 的核心价值是**友好命名**：

| 原始路径（深层、含特殊字符） | 演示用名（简洁、清晰） |
|---------------------------|---------------------|
| `demofiles/Urban-Data-Challenge/public-transportation/geneva/schedule-real-time.csv` | `big.csv` |
| `demofiles/tcga/extra_data/c2.cp.v3.0.symbols_edit.csv` | `smaller.csv` |
| `demofiles/PythonDataScienceHandbook/notebooks/03.08-Aggregation-and-Grouping.ipynb` | `notebooks/pandas.ipynb` |
| `"demofiles/bqplot/examples/Basic Plotting/Basic Plotting.ipynb"` | `notebooks/bqplot.ipynb` |

演示时看到 `big.csv` 和 `smaller.csv`，观众立刻理解"这是一个大文件、一个小文件"的对比意图，而不需要理解深层目录结构。

## 模式总结：声明式素材组装

build.py + talks.yml 实现了一个通用的**声明式文件组装模式**，可以复用于类似场景：

```
素材源（多个位置） → 声明式配置（YAML） → 组装器（Python） → 场景输出目录
```

这种模式的优势：
1. **零逻辑配置**：添加新演讲只需在 YAML 中增加几行，无需写代码
2. **素材共享**：同一文件可在多个场景中使用，不重复存储
3. **构建可重现**：同一配置每次生成相同的输出目录
4. **易于审查**：YAML 是人类可读的，代码审查时一目了然
5. **CI 可验证**：build.py 的断言确保构建失败时快速发现

## 相关概念

- [Binder 环境配置三要素](02-binder-config.md)
- [演示能力维度与文件处理器](04-demo-capabilities.md)
- [数据文件与多格式查看器](06-data-files.md)
- [实战：创建自定义演讲配置](../examples/02-custom-demo-talk.md)
