---
type: Example
title: 基本安装与配置
description: 从零开始安装 jupyterlite-pyodide-kernel，构建 JupyterLite 站点，并配置常用选项
tags: [install, build, configuration, getting-started]
prerequisites: ["01-getting-started"]
difficulty: beginner
expected_time: "10 minutes"
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: pyproject
    resource: /references/addon-source.md
    title: pyproject.toml
---

# 基本安装与配置

## 前置条件

- Python 3.12+
- pip
- 现代浏览器（Chrome/Firefox/Edge/Safari）

## 步骤 1：安装 jupyterlite-pyodide-kernel

```bash
pip install jupyterlite-pyodide-kernel
```

安装完成后，验证 Addon 是否注册：

```bash
jupyter lite list
```

应该能看到类似输出：

```
JupyterLite Addons:
  - jupyterlite-pyodide-kernel-pyodide (0.9.0a1)
  - jupyterlite-pyodide-kernel-piplite (0.9.0a1)
  - jupyterlite-pyodide-kernel-pyodide-lock (0.9.0a1)
```

## 步骤 2：创建项目目录

```bash
mkdir my-jupyterlite
cd my-jupyterlite
```

## 步骤 3：添加 Notebooks（可选）

将你已有的 `.ipynb` 文件放到项目目录中，构建时会自动包含：

```bash
# 示例：创建一个简单的 notebook
mkdir -p content
cp /path/to/your/notebook.ipynb content/
```

## 步骤 4：创建配置文件

在项目目录中创建 `jupyter-lite.json`：

### 最小配置（使用 CDN Pyodide）

```json
{
  "LiteBuildConfig": {
    "contents": [
      "content"
    ],
    "outputDir": "_output"
  }
}
```

这个配置会从 jsdelivr CDN 加载 Pyodide，无需下载本地 Pyodide 发行版。

### 离线/本地部署配置（包含 Pyodide）

```json
{
  "LiteBuildConfig": {
    "contents": ["content"],
    "outputDir": "_output",
    "PyodideAddon": {
      "pyodide_url": ""
    }
  },
  "litePluginSettings": {
    "@jupyterlite/pyodide-kernel-extension:kernel": {
      "disablePyPIFallback": true
    }
  }
}
```

设置 `pyodide_url` 为空字符串会触发下载完整 Pyodide 发行版到输出目录，适用于离线部署。`disablePyPIFallback: true` 禁用 PyPI 回退。

### 自定义 Pyodide 版本

```json
{
  "litePluginSettings": {
    "@jupyterlite/pyodide-kernel-extension:kernel": {
      "pyodideUrl": "https://cdn.jsdelivr.net/pyodide/v0.26.0/full/pyodide.mjs"
    }
  }
}
```

## 步骤 5：构建站点

```bash
jupyter lite build
```

构建过程中会看到类似输出：

```
...
[PyodideAddon] Status: pyodide will be loaded from CDN
[PipliteAddon] Building piplite wheel index...
[PipliteAddon] Generated pypi/all.json with 0 wheels
...
Wrote build outputs to: _output/
```

## 步骤 6：预览站点

```bash
jupyter lite serve
```

或使用任意静态服务器：

```bash
cd _output
python -m http.server 8000
```

然后在浏览器中打开 `http://localhost:8000`。

## 步骤 7：验证内核运行

1. 在 JupyterLab 界面中点击 "Notebook" → "Pyodide" 创建新 Notebook
2. 在第一个 cell 中输入：

```python
import sys
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
```

3. 运行 cell（Shift+Enter），应该看到类似输出：

```
Python version: 3.12.x (main, ...) [Clang ...] on wasm32
Platform: emscripten
```

4. 测试自动包加载（内置包无需安装）：

```python
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {arr.mean()}")
print(f"Sum: {arr.sum()}")
```

5. 测试包安装：

```python
%pip install regex
import regex
result = regex.findall(r'\w+', 'Hello, World!')
print(result)
```

## 常见配置选项速查

| 目标 | CLI 选项 | 配置文件写法 |
|------|---------|-------------|
| 使用本地 Pyodide | `--pyodide https://.../pyodide.tar.bz2` | `"PyodideAddon": {"pyodide_url": "..."}` |
| 添加自定义 wheels | `--piplite-wheels URL1 URL2` | `"PipliteAddon": {"piplite_urls": ["..."]}` |
| 禁用 PyPI 回退 | — | `"disablePyPIFallback": true` |
| 启用 lockfile 定制 | `--pyodide-lock` | `"PyodideLockAddon": {"enabled": true}` |
| 挂载 DriveFS | — | `"mountDrive": true`（需要 COOP/COEP 头） |

## 验证清单

- [ ] `jupyter lite build` 成功执行
- [ ] `_output/` 目录包含 `jupyter-lite.json` 和 `static/` 目录
- [ ] 启动服务器后浏览器能打开 JupyterLab 界面
- [ ] 能创建 Pyodide kernel 的 Notebook
- [ ] `print("hello")` 能正常输出
- [ ] `import numpy` 能自动加载包
- [ ] `%pip install` 能安装纯 Python 包

## 下一步

- [添加自定义 Wheel 包](custom-wheels.md)
- [构建时 Addon 系统](../concepts/04-build-addons.md)
- [浏览器端包管理](../concepts/05-package-management.md)
