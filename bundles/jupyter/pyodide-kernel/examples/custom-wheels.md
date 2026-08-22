---
type: Example
title: 添加自定义 Wheel 包
description: 将本地或自定义的 Python wheel 包添加到 JupyterLite 站点，使其在浏览器中可安装
tags: [wheel, piplite, custom-package, install, deploy]
prerequisites: ["basic-install-config", "04-build-addons", "05-package-management"]
difficulty: intermediate
expected_time: "15 minutes"
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: addon-piplite
    resource: /references/addon-source.md
    title: addons/piplite.py
---

# 添加自定义 Wheel 包

## 场景

你有一个纯 Python 的 wheel 包（`my_package-1.0.0-py3-none-any.whl`），想在 JupyterLite 站点中使用它。这个包不在 PyPI 上（或者你不想依赖 PyPI），需要将它打包到站点中。

## 前置条件

- 已完成[基本安装与配置](/examples/basic-install-config.md)
- 有一个纯 Python wheel 文件（`py3-none-any.whl`）
  - 含 C 扩展的包需要预先编译为 WASM，详见[注意事项](#注意事项纯-python-vs-wasm-wheel)

## 方法一：通过 pypi/ 目录（推荐）

最简单的方式是将 wheel 文件放到项目目录的 `pypi/` 子目录中。

### 步骤

1. **创建 pypi 目录**：

```bash
cd my-jupyterlite
mkdir -p pypi
```

2. **将 wheel 文件复制到 pypi/ 目录**：

```bash
cp /path/to/my_package-1.0.0-py3-none-any.whl pypi/
cp /path/to/another_package-2.0.0-py3-none-any.whl pypi/
```

3. **构建站点**：

```bash
jupyter lite build
```

构建时 `PipliteAddon` 会自动扫描 `lite_dir/pypi/` 目录中的所有 `.whl` 文件，将它们复制到输出目录并生成索引。

4. **验证索引**：构建完成后检查 `_output/pypi/all.json`，应该包含你的包：

```json
{
  "my-package": {
    "filename": "my_package-1.0.0-py3-none-any.whl",
    "url": "./pypi/my_package-1.0.0-py3-none-any.whl",
    "sha256": "...",
    "md5": "...",
    "releases": [ ... ]
  }
}
```

5. **在 Notebook 中安装使用**：

```python
import piplite
await piplite.install("my-package")
import my_package
my_package.do_something()
```

或者使用 `%pip`：

```python
%pip install my-package
import my_package
```

## 方法二：通过 CLI 参数

对于不在本地但可通过 URL 下载的 wheels，使用 `--piplite-wheels`：

```bash
jupyter lite build --piplite-wheels https://example.com/packages/my_package-1.0.0-py3-none-any.whl
```

多个 URL 用空格分隔：

```bash
jupyter lite build \
  --piplite-wheels https://example.com/pkg1-1.0.whl https://example.com/pkg2-2.0.whl
```

构建时 `PipliteAddon.post_init()` 会下载这些 URL 指向的 wheel 文件，然后在 `build()` 阶段将它们复制到输出目录。

## 方法三：通过配置文件

在 `jupyter-lite.json` 中配置：

```json
{
  "LiteBuildConfig": {
    "PipliteAddon": {
      "piplite_urls": [
        "https://example.com/packages/my_package-1.0.0-py3-none-any.whl",
        "./local-wheels/extra-0.1.0-py3-none-any.whl"
      ]
    }
  }
}
```

`piplite_urls` 支持远程 URL 和本地路径。

## 含依赖的包

如果你的包依赖其他包，piplite 会自动处理：

- **依赖是 Pyodide 内置包**（numpy/pandas 等）：自动从 pyodide-lock.json 加载
- **依赖在 all.json 索引中**：自动安装
- **依赖在 PyPI 上**（且未禁用 PyPI 回退）：自动从 PyPI 下载纯 Python wheel
- **依赖不可用**：安装失败，会提示缺失的依赖

### 示例：包含依赖的包

假设 `my_package` 依赖 `numpy` 和 `pydantic`：

1. numpy 是 Pyodide 内置包，无需额外操作
2. pydantic 如果是纯 Python wheel，可以也放入 `pypi/` 目录，或者依赖 PyPI 回退

```
pypi/
├── my_package-1.0.0-py3-none-any.whl
└── pydantic-2.0.0-py3-none-any.whl  （如果不使用 PyPI 回退）
```

## 开发自己的包

如果你在开发自己的 Python 包想在 JupyterLite 中使用：

### 1. 确保包是纯 Python

检查 `setup.py` 或 `pyproject.toml` 中没有 C 扩展：
- 没有 `ext_modules`
- 不依赖 `cffi`/`cython` 等编译工具
- wheel 文件名是 `py3-none-any.whl`（不是 `cp312-cp312-linux_x86_64` 等平台标签）

### 2. 构建 wheel

```bash
pip install build
python -m build --wheel
```

生成的 wheel 在 `dist/` 目录中。

### 3. 复制到 pypi/

```bash
cp dist/my_package-1.0.0-py3-none-any.whl /path/to/my-jupyterlite/pypi/
```

### 4. 重新构建并测试

```bash
cd /path/to/my-jupyterlite
jupyter lite build
jupyter lite serve
```

## 注意事项：纯 Python vs WASM Wheel

| 类型 | wheel 标签 | 放置位置 | 加载方式 |
|------|-----------|---------|---------|
| 纯 Python | `py3-none-any.whl` | `pypi/` 目录或 piplite_urls | piplite.install() 按需下载 |
| WASM 编译 | `cp312-cp312-emscripten_wasm32.whl` | lockfile 定制（wheels 选项） | loadPyodide 预加载 |

纯 Python wheel 是平台无关的，在任何 Python 实现上都能运行。但包含 C 扩展的包（如 numpy 的 C 代码）需要编译为 WebAssembly，生成 emscripten_wasm32 标签的 wheel。这类包不能通过 piplite 安装，必须通过 PyodideLockAddon 添加到 lockfile 中。

### 添加 WASM 编译包（高级）

如果你有编译好的 WASM wheel，使用 lockfile 定制：

```bash
jupyter lite build --pyodide-lock \
  --pyodide-lock-wheels ./wasm-wheels/my_wasm_pkg-1.0.0-cp312-cp312-emscripten_wasm32.whl
```

## 离线部署最佳实践

对于完全离线的部署环境：

1. **禁用 PyPI 回退**：

```json
{
  "litePluginSettings": {
    "@jupyterlite/pyodide-kernel-extension:kernel": {
      "disablePyPIFallback": true
    }
  }
}
```

2. **将所有需要的包放入 pypi/ 目录**（包括传递依赖的纯 Python 包）：

```bash
# 先在有网络的环境下分析依赖
pip download my_package -d ./pypi/ --no-deps
pip download my_package -d ./pypi/ --only-binary=:all: --python-version 3.12 --platform any
```

3. **本地包含 Pyodide 发行版**（避免 CDN 依赖）：

```bash
jupyter lite build --pyodide ""
```

4. **验证站点完整性**：

```bash
jupyter lite check
```

## 验证清单

- [ ] wheel 文件是 `py3-none-any.whl` 格式（纯 Python）
- [ ] wheel 文件在 `pypi/` 目录或通过 piplite_urls 配置
- [ ] 构建后 `_output/pypi/all.json` 包含你的包
- [ ] 构建后 `_output/pypi/` 目录包含 wheel 文件
- [ ] Notebook 中 `await piplite.install("package-name")` 成功
- [ ] `import package_name` 正常工作
- [ ] 离线部署时所有依赖都已包含

## 下一步

- [浏览器端包管理](/concepts/05-package-management.md)
- [构建时 Addon 系统](/concepts/04-build-addons.md)
- [Lockfile 定制](/concepts/08-lockfile-customization.md) — 添加 WASM 编译包
