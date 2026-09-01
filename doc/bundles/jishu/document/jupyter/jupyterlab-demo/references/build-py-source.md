---
type: Reference
title: "build.py 构建脚本源码解析"
description: "jupyterlab-demo 构建脚本 build.py 的源码级信源，包含 setup_demofiles 和 setup_talks 两个核心函数"
tags: [build, python, talks, demo-setup, git-clone]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: build-source, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/build.py", title: "build.py source code" }
---

# build.py 构建脚本源码信源

## 源码路径

`external/libs/jupyter/jupyterlab-demo/build.py`

## 文件元信息

- Shebang: `#!/usr/bin/env python3`
- 依赖: `pathlib.Path`, `subprocess`, `ruamel.yaml.YAML`, `shutil`, `os`
- 常量: `DEMO_FOLDER = "demofiles"`
- YAML 解析器: `ruamel.yaml.YAML()` 实例

## 函数清单

### setup_talks()

**功能**：读取 `talks.yml`，按照 YAML 配置将文件和文件夹移动到以演讲名称命名的目录中。

**YAML 配置格式**：
```python
{
    'talk_name': {
        'folders': {'src0': 'dest0', 'src1': 'dest1'},
        'files': ['file0', 'file1'],
        'rename': {'oldname': 'newname'}
    }
}
```

**执行步骤**：
1. 打开 `talks.yml` 并用 ruamel.yaml 解析
2. 遍历每个 talk_name：
   - 创建 `Path(talk_name).mkdir(parents=True, exist_ok=True)`
   - 如果有 `files` 键：复制列出的文件到 talk_name 目录，使用 `os.path.basename(f)` 作为目标名
   - 如果有 `folders` 键：使用 `shutil.copytree` 复制源目录到目标路径（仅当目标不存在时）
   - 如果有 `rename` 键：重命名或复制文件到新名称

**断言检查**：文件复制后使用 `assert os.path.isfile(copied_path)` 验证。

### setup_demofiles()

**功能**：创建 `demofiles/` 目录并克隆7个外部演示仓库。

**克隆仓库列表**（共7个，使用 `--depth 1` 浅克隆）：
1. `jakevdp/PythonDataScienceHandbook`
2. `swissnexSF/Urban-Data-Challenge`
3. `altair-viz/altair`
4. `QuantEcon/QuantEcon.notebooks`
5. `theandygross/TCGA`
6. `aymericdamien/TensorFlow-Examples`
7. `bloomberg/bqplot`

**拖放演示文件**：
- 创建空文件 `move_this_file.txt`（Path.touch()）
- 创建空目录 `move_it_here/`
- 用于演示 JupyterLab 的文件拖放功能

### main()

按顺序调用 `setup_demofiles()` 然后 `setup_talks()`。

## 关键实现细节

- 浅克隆策略：`git clone --depth 1` 减少下载量
- 仓库仅在目标目录不存在时克隆（`if not target_path.is_dir()`）
- rename 操作处理两种情况：文件已被复制到 talk 目录（直接 rename）或需要从原始路径复制
