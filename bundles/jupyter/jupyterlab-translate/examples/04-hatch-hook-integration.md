---
type: Example
title: Hatch构建钩子配置
description: 在JupyterLab语言包或扩展中配置Hatch Build Hook，实现构建时自动编译翻译文件
tags: [example, hatch, build-hook, pyproject, wheel, sdist, packaging]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-source
    resource: /references/plugin-source.md
    title: Hatch构建钩子源码映射
---

# Hatch构建钩子配置

本示例演示如何在JupyterLab语言包或扩展中正确配置Hatch Build Hook，使得在构建wheel时自动将PO文件编译为MO和JSON格式。

## 语言包完整pyproject.toml配置

以下是一个韩语语言包（jupyterlab-language-pack-ko-KR）的完整pyproject.toml配置：

```toml
[build-system]
requires = ["hatchling>=1.4.0", "jupyterlab-translate"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab_language_pack_ko_KR"
version = "1.0.post2"
description = "JupyterLab Korean Language Pack"
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.7"
dependencies = []

# 注册为JupyterLab语言包（运行时发现）
[project.entry-points."jupyterlab.languagepack"]
ko_KR = "jupyterlab_language_pack_ko_KR"

[project.urls]
homepage = "https://github.com/jupyterlab/language-packs"

# 版本从__init__.py读取
[tool.hatch.version]
path = "jupyterlab_language_pack_ko_KR/__init__.py"

# 构建时包含CONTRIBUTORS.md
[tool.hatch.build]
artifacts = [
    "CONTRIBUTORS.md"
]

# 启用jupyter-translate构建钩子
[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate"]

# Wheel包含编译后的翻译文件（.json和.mo）
[tool.hatch.build.targets.wheel]
artifacts = [
    "jupyterlab_language_pack_ko_KR/**/*.json",
    "jupyterlab_language_pack_ko_KR/**/*.mo",
]
exclude = [
    "jupyterlab_language_pack_ko_KR/**/*.po",
]
```

## 语言包包结构

```
jupyterlab-language-pack-ko-KR/
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTORS.md
└── jupyterlab_language_pack_ko_KR/
    ├── __init__.py      # 包含__version__
    └── locale/
        └── ko_KR/
            └── LC_MESSAGES/
                ├── jupyterlab.po        # 翻译源文件
                ├── jupyterlab.json      # 编译后（wheel构建时生成）
                ├── jupyterlab.mo        # 编译后（wheel构建时生成）
                ├── jupyterlab_git.po
                └── ...
```

### __init__.py内容

```python
__version__ = "1.0.post2"
```

## 扩展包自带翻译的配置

如果扩展选择自带翻译（不依赖集中语言包），配置如下：

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab-translate"]
build-backend = "hatchling.build"

[project]
name = "my-ext"
version = "0.1.0"
dependencies = []

# 注册为自带locale的扩展
[project.entry-points."jupyterlab.locale"]
my-ext = "my_ext"

[tool.hatch.version]
path = "my_ext/__init__.py"

[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate"]

[tool.hatch.build.targets.wheel]
packages = ["my_ext"]
artifacts = [
    "my_ext/**/*.json",
    "my_ext/**/*.mo",
]
exclude = [
    "my_ext/**/*.po",
]
```

## 构建命令

配置完成后，使用标准Python构建命令：

```bash
# 安装build工具
pip install build

# 构建sdist和wheel
python -m build --no-isolation

# 或分别构建
python -m build --sdist --no-isolation
python -m build --wheel --no-isolation
```

## 构建过程输出

构建wheel时，Hatch Hook会输出类似以下信息：

```
[tool.hatch.build.hooks.jupyter-translate]
ko_KR jupyterlab 85% compiling...
ko_KR jupyterlab_git 72% compiling...
Language translation bundles generated.
```

## 构建产物验证

### Wheel内容

wheel文件（.whl，本质是zip）应包含：

```
jupyterlab_language_pack_ko_KR/__init__.py
jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.json
jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.mo
jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/...
```

不包含 `.po` 文件。

### sdist内容

源码分发包（.tar.gz）应包含：

```
jupyterlab_language_pack_ko_KR/__init__.py
jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.po
CONTRIBUTORS.md
pyproject.toml
```

包含 `.po` 源文件（便于其他开发者基于此创建新语言包）。

### 验证命令

```bash
# 查看wheel内容
unzip -l dist/*.whl

# 查看sdist内容
tar tzf dist/*.tar.gz

# 验证JSON格式正确
python -c "import json; json.load(open('path/to/jupyterlab.json'))"
```

## 自动贡献者更新

如果设置了 `CROWDIN_API_KEY` 环境变量，构建sdist时会自动从Crowdin更新CONTRIBUTORS.md：

```bash
export CROWDIN_API_KEY="your-crowdin-api-key"
python -m build --sdist --no-isolation
```

输出中会包含：

```
Contributors list updated.
```

## 常见问题

### Q: wheel中没有.json/.mo文件？

检查：
1. `[tool.hatch.build.targets.wheel]` 中 `artifacts` 是否正确包含了glob模式
2. PO文件是否在 `locale/<locale>/LC_MESSAGES/` 目录下
3. PO文件是否有翻译内容（空翻译的条目会被跳过，但文件仍应生成）
4. 运行构建时是否有错误信息

### Q: 构建时提示"Unable to get the Python folder name"？

检查：
1. 包目录名是否符合 `jupyterlab_language_pack_??_??` 格式（双字母语言_双字母国家）
2. 三字母语言代码使用 `jupyterlab_language_pack_???_??` 格式（如 `ach_UG`）

### Q: 如何设置翻译编译阈值？

当前 `COMPILATION_THRESHOLD` 硬编码为0（编译所有PO文件）。如需修改，需要在安装后修改 `jupyterlab_translate/plugin.py` 中的常量值，或提交PR到上游项目。

### Q: 构建后清理编译产物？

使用 `hatch clean` 或 `python -m build --no-isolation -c` 清理：

```bash
python -m build --no-isolation -c
```

这会调用Hook的 `clean()` 方法，删除所有.json和.mo文件。

## 相关概念

- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
- [翻译目录管理](/concepts/05-catalog-management.md)
- [运行时语言包发现](/concepts/08-runtime-discovery.md)
- [双模式分发机制](/concepts/11-dual-mode-distribution.md)
- [Hatch构建钩子源码映射](/references/plugin-source.md)
