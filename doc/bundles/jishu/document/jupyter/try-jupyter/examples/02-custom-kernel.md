---
type: Example
title: "自定义内核环境"
description: "为Try Jupyter站点添加新的Xeus内核（如Julia）、修改现有内核的包依赖、配置Pyodide预装包的完整步骤。"
tags: [example, custom-kernel, xeus, environment-yml, kernel-configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-ecosystem
    resource: "/concepts/04-kernel-ecosystem.md"
    title: "内核生态"
  - id: config
    resource: "/concepts/03-configuration-system.md"
    title: "配置系统"
  - id: scripts
    resource: "/references/scripts-source.md"
    title: "构建脚本信源"
---

# 示例：自定义内核环境

本示例演示如何修改Try Jupyter的内核配置：添加新内核、修改现有内核的包依赖、调整内核过滤规则。

## 场景A：添加新的Xeus内核（以Julia为例）

### 步骤1：确认内核包存在

在 [emscripten-forge](https://prefix.dev/emscripten-forge-4x) 或 [conda-forge](https://prefix.dev/conda-forge) 中搜索对应的xeus内核包。常见的Xeus内核包括：

| 内核 | 包名 | 语言 |
|------|------|------|
| Xeus-Python | `xeus-python` | Python |
| Xeus-Cpp | `xeus-cpp` | C++ |
| Xeus-R | `xeus-r` | R |
| Xeus-SQLite | `xeus-sqlite` | SQLite |
| Xeus-Julia | `xeus-julia`（如存在） | Julia |
| Xeus-Lua | `xeus-lua`（如存在） | Lua |

### 步骤2：创建环境文件

在项目根目录创建 `environment-julia.yml`：

```yaml
name: xeus-julia-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-julia
  # 添加Julia需要的额外包
  # - julia-dataframes
  # - julia-plots
```

> **注意**：channels必须包含 `emscripten-forge-4x`（WASM包来源）和 `conda-forge`（通用依赖）。

### 步骤3：注册环境文件

编辑 `jupyter_lite_config.json`，在 `XeusAddon.environment_file` 数组中添加新文件：

```json
{
  "LiteBuildConfig": {
    "output_dir": "dist",
    "contents": ["content"]
  },
  "XeusAddon": {
    "environment_file": [
      "environment-cpp.yml",
      "environment-python.yml",
      "environment-r.yml",
      "environment-sqlite.yml",
      "environment-julia.yml"
    ]
  }
}
```

### 步骤4：更新内核过滤脚本

编辑 `scripts/filter_xeus_kernels.py`，在 `KERNELS_TO_KEEP` 集合中添加新内核ID：

```python
KERNELS_TO_KEEP = {"xcpp23", "xc23", "xr", "xpython", "xsqlite", "xjulia"}
```

> **注意**：内核ID（如 `xjulia`）需要先构建一次，查看 `dist/xeus/kernels.json` 中构建出的实际内核ID是什么，可能需要调整。

### 步骤5：重新构建并测试

```bash
pixi run clean
pixi run build
pixi run filter-kernels
pixi run python -m http.server 8000 --directory dist
```

在浏览器中检查内核选择器是否出现Julia内核。

## 场景B：修改现有内核的包依赖

### 示例：为Python内核添加pandas

编辑 `environment-python.yml`：

```yaml
name: xeus-python-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - matplotlib
  - pillow
  - ipywidgets>=8.1.6
  - ipyleaflet
  - scipy
  - pandas          # 新增pandas
```

然后重新构建：

```bash
pixi run clean && pixi run build && pixi run filter-kernels
```

> **注意**：不是所有Python包都有WASM版本。添加包前先在 emscripten-forge 上确认包是否存在于 `emscripten-wasm32` 平台。

### 示例：为R内核添加dplyr

编辑 `environment-r.yml`：

```yaml
name: xeus-r-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-r >= 0.7.0
  - r-ggplot2
  - r-dplyr    # 新增dplyr
```

R包通常以 `r-` 为前缀命名。

## 场景C：移除不需要的内核

如果不需要某个内核（如不需要SQLite）：

### 步骤1：从环境配置中移除

编辑 `jupyter_lite_config.json`，从 `environment_file` 数组中移除对应的yml文件：

```json
{
  "XeusAddon": {
    "environment_file": [
      "environment-cpp.yml",
      "environment-python.yml",
      "environment-r.yml"
      // 移除 "environment-sqlite.yml"
    ]
  }
}
```

### 步骤2：从过滤脚本中移除

编辑 `scripts/filter_xeus_kernels.py`：

```python
KERNELS_TO_KEEP = {"xcpp23", "xc23", "xr", "xpython"}  # 移除 "xsqlite"
```

### 步骤3：删除环境文件（可选）

```bash
rm environment-sqlite.yml
```

## 场景D：配置禁用的扩展

编辑 `jupyter-lite.json`，在 `disabledExtensions` 中添加或移除扩展ID：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My Custom JupyterLite!",
    "disabledExtensions": [
      "@jupyterlab/server-proxy",
      "jupyterlab-server-proxy",
      "nbdime-jupyterlab"
      // 可添加更多需要禁用的扩展
    ],
    "terminalsAvailable": false
  }
}
```

## 场景E：禁用终端以减小体积

设置 `terminalsAvailable: false`，同时可从 `pyproject.toml` 中移除 `jupyterlite-terminal` 依赖。

## 验证自定义配置

构建后，验证更改是否生效：

```bash
# 检查构建是否成功
ls dist/

# 检查过滤后的内核列表
cat dist/xeus/kernels.json | python -m json.tool

# 启动预览
pixi run python -m http.server 8000 --directory dist
```

在浏览器中：
1. 打开Lab界面
2. 检查内核选择器中的内核列表
3. 测试每个内核能正常启动和执行代码
4. 检查终端是否按预期启用/禁用
5. 检查扩展是否正确禁用

## 相关示例

- [本地构建与预览](01-local-build.md)
- [添加新Notebook](03-add-notebook.md)
