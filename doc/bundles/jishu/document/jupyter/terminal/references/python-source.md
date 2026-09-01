---
type: Reference
title: Python端源码信源
description: Python包入口、JupyterLite构建插件（TerminalAddon）和labextension路径注册
tags: [python, addon, build, wasm, jupyterlite, labextension]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: init-py
    resource: /../../../../../../external/libs/jupyter/terminal/jupyterlite_terminal/__init__.py
    title: jupyterlite_terminal/__init__.py
  - id: addon-py
    resource: /../../../../../../external/libs/jupyter/terminal/jupyterlite_terminal/add_on.py
    title: jupyterlite_terminal/add_on.py
---

# Python端源码信源

## __init__.py

### 版本获取

```python
try:
    from ._version import __version__
except ImportError:
    import warnings
    warnings.warn("Importing 'jupyterlite_terminal' outside a proper installation.")
    __version__ = "dev"
```

构建时hatch-nodejs-version从package.json读取版本写入_version.py。开发模式下未安装时回退为"dev"并发出警告。

### 导出

```python
__all__ = ["__version__", "_jupyter_labextension_paths"]
```

### labextension路径注册

```python
def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlite/terminal"
    }]
```

JupyterLab扩展发现函数，返回labextension元数据。`src`是Python包内的相对路径，`dest`是JupyterLab扩展的目标目录名。

## add_on.py：TerminalAddon

```python
class TerminalAddon(FederatedExtensionAddon):
    __all__ = ["post_build"]
```

继承自`jupyterlite_core.addons.federated_extensions.FederatedExtensionAddon`。

### post_build 方法

```python
def post_build(self, manager):
```

JupyterLite构建的post_build钩子，是一个**生成器函数**，yield dict格式的action供构建框架执行。

**执行流程**：

1. **确定cockle工具路径**：
   ```python
   cockleTool = Path("node_modules", "@jupyterlite", "cockle", "lib", "tools", "prepare_wasm.js")
   ```

2. **cockle未安装时临时安装**：
   ```python
   if not cockleTool.is_file():
       cockleTool = ".cockle_temp" / cockleTool
       cmd = ["npm", "install", "--no-save", "--prefix", cockleTool.parts[0], "@jupyterlite/cockle"]
       subprocess.run(cmd, check=True, cwd=lite_dir)
   ```
   - `--no-save`：不写入package.json
   - `--prefix .cockle_temp`：安装到临时目录
   - 这确保了即使没有预装cockle也能完成构建

3. **确定WASM输出目录**：
   ```python
   assetDir = output_dir / "extensions" / "@jupyterlite" / "terminal" / "static" / "wasm"
   ```

4. **获取WASM文件列表**：
   ```python
   tempFilename = lite_dir / 'cockle-files.txt'
   cmd = ["node", str(cockleTool), "--list", str(tempFilename)]
   subprocess.run(cmd, check=True, cwd=lite_dir)
   ```
   - 调用prepare_wasm.js的--list模式
   - 输出文件列表到临时文本文件
   - 文件格式：每行source路径，下一行packageName，交替

5. **yield复制动作**：
   ```python
   with open(tempFilename, 'r') as f:
       for source in f:
           source = Path(source.strip())
           basename = source.name
           packageName = next(f).strip()
           yield dict(
               name=f"copy:{basename}",
               actions=[(self.copy_one, [lite_dir / source, assetDir / packageName / basename])],
           )
   ```
   - 逐行读取，每两行一组（source路径 + packageName）
   - 每个文件yield一个copy action：`copy_one(source, assetDir/packageName/basename)`
   - 按packageName分子目录存放WASM文件

6. **清理临时文件**：
   ```python
   os.remove(tempFilename)
   ```

### 构建时关键路径

| 路径 | 说明 |
|------|------|
| `manager.lite_dir` | JupyterLite项目目录 |
| `manager.output_dir` | 构建输出目录（通常是`_output/`） |
| `.cockle_temp/` | 临时npm安装目录（cockle不存在时） |
| `cockle-files.txt` | 临时WASM文件列表 |
| `extensions/@jupyterlite/terminal/static/wasm/` | 最终WASM文件输出目录 |

## 构建配置（pyproject.toml）

### Entry Point注册

```toml
[project.entry-points."jupyterlite.addon.v0"]
jupyterlite-terminal = "jupyterlite_terminal.add_on:TerminalAddon"
```

注册到`jupyterlite.addon.v0`组，JupyterLite构建时自动发现。

### Wheel共享数据

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlite_terminal/labextension" = "share/jupyter/labextensions/@jupyterlite/terminal"
"install.json" = "share/jupyter/labextensions/@jupyterlite/terminal/install.json"
```

将labextension静态资源和install.json打包到wheel的共享数据目录。

### hatch-jupyter-builder配置

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlite_terminal/labextension/static/style.js",
    "jupyterlite_terminal/labextension/package.json",
]
skip-if-exists = ["jupyterlite_terminal/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlite_terminal/labextension"
```

- 生产构建：执行`jlpm build:prod`（TypeScript编译+Worker打包+labextension构建）
- 开发安装（pip install -e）：执行`jlpm install:extension`
- ensured-targets：构建完成后必须存在的文件（验证构建成功）

## install.json

```json
{
  "packageManager": "python",
  "packageName": "jupyterlite_terminal",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package jupyterlite_terminal"
}
```

JupyterLab扩展安装元数据，告诉JupyterLab如何管理此扩展。
