---
okf_version: "0.2"
type: reference
title: "工具函数源码（utils.py）"
description: "pytest_jupyter/utils.py 中的 mkdir 工具函数：在临时路径下创建多级目录"
tags: [utils, mkdir, tmp-path, directory-creation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: utils-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/utils.py"
    title: "pytest_jupyter/utils.py"
---

# 工具函数源码（utils.py）

本信源登记 `pytest_jupyter/utils.py`（约13行）的核心函数。utils.py 是 pytest-jupyter 最基础的工具模块，目前只提供一个目录创建辅助函数。

## 核心函数

### mkdir(tmp_path: Path, *parts: str) -> Path

在给定的临时路径 `tmp_path` 下，按 `parts` 指定的路径段逐级创建目录。

**参数：**
- `tmp_path` (Path): pytest 提供的临时目录基准路径
- `*parts` (str): 可变数量的路径段，用于拼接多级子目录

**返回：**
- `Path`: 创建完成的完整目录路径

**行为细节：**
1. 使用 `tmp_path.joinpath(*parts)` 拼接目标路径
2. 调用 `new_path.mkdir(parents=True)` 递归创建所有父目录
3. 如果目录已存在则不报错（`exist_ok` 未显式设置为 True，但因父目录可能已存在而需要 `parents=True`）
4. 返回最终创建的 Path 对象

[F-001]

## 设计要点

1. **极简设计**：整个 utils.py 只有一个函数，职责单一
2. **Path 优先**：使用 pathlib.Path 而非 os.path 进行路径操作
3. **parents=True**：确保多级目录能一次性创建，无需逐级调用 mkdir
4. **被 jupyter_core.py 大量使用**：所有临时目录 fixtures（`jp_home_dir`、`jp_data_dir` 等）都通过此函数创建
