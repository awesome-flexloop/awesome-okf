---
type: Reference
title: Conda环境创建与pip依赖参考
description: create_conda_env.py中micromamba环境创建逻辑和_pip.py中pip依赖安装的实际实现
tags: [python, conda, micromamba, pip, emscripten, build]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:35:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: conda-src
    resource: /references/conda-env-source.md
    title: jupyterlite_xeus/create_conda_env.py and _pip.py
---

## 概述

conda环境创建模块位于 create_conda_env.py，pip依赖处理位于 _pip.py。

## 常量

```python
# create_conda_env.py
MICROMAMBA_COMMAND = shutil.which("micromamba")  # 查找系统已安装的micromamba
PLATFORM = "emscripten-wasm32"

# constants.py（由create_conda_env.py导入）
DEFAULT_CHANNELS = [
    "https://prefix.dev/emscripten-forge-4x",
    "https://prefix.dev/conda-forge"
]
```

**重要**：micromamba必须预先安装在系统PATH中（通过`shutil.which("micromamba")`查找）。如果未找到，会抛出RuntimeError提示用户安装：

> "micromamba is needed for creating the emscripten environment. Please install it using conda `conda install micromamba -c conda-forge` or from https://mamba.readthedocs.io/..."

## create_conda_env_from_env_file 函数

从environment.yml文件创建conda环境。

```python
def create_conda_env_from_env_file(root_prefix, env_file_content, env_file_location):
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| root_prefix | Path | micromamba根前缀目录 |
| env_file_content | dict | 解析后的YAML内容（dict） |
| env_file_location | Path | environment.yml所在目录（用于解析相对路径） |

### 执行流程

1. 从env_file_content获取 `name`（默认"xeus-env"）和 `channels`（默认DEFAULT_CHANNELS）
2. 调用 `_extract_specs()` 解析dependencies，分离conda specs和pip dependencies
3. 调用 `create_conda_env_from_specs()` 创建环境并安装pip依赖

## create_conda_env_from_specs 函数

从specs列表创建conda环境。

```python
def create_conda_env_from_specs(env_name, root_prefix, specs, channels, pip_dependencies=None):
```

### 执行流程

1. 调用 `_create_conda_env_from_specs_impl()` 创建conda环境
2. 如果有pip_dependencies，调用 `_install_pip_dependencies()` 安装pip包

### _create_conda_env_from_specs_impl 实现

实际执行micromamba命令：

```python
def _create_conda_env_from_specs_impl(env_name, root_prefix, specs, channels):
    prefix_path = Path(root_prefix) / "envs" / env_name
    Path(root_prefix).mkdir(parents=True, exist_ok=True)

    channels_args = []
    for channel in channels:
        channels_args.extend(["-c", channel])

    subprocess_run([
        MICROMAMBA_COMMAND,
        "create",
        "--yes",
        "--no-pyc",           # 不生成.pyc文件
        "--prefix", prefix_path,
        "--relocate-prefix", "",  # 重定位前缀（为空表示使用时重定位）
        "--root-prefix", root_prefix,
        f"--platform={PLATFORM}",  # emscripten-wasm32
        *channels_args,
        *specs,
    ], check=True)
```

**注意**：环境实际创建在 `{root_prefix}/envs/{env_name}/` 目录下。

## _extract_specs 函数

从environment.yml的dependencies中分离conda specs和pip依赖：

```python
def _extract_specs(env_location, env_data):
    specs = []
    pip_dependencies = []
    for dependency in env_data.get("dependencies", []):
        if isinstance(dependency, str):
            specs.append(dependency)  # conda包
        elif isinstance(dependency, dict) and "pip" in dependency:
            for pip_dependency in dependency["pip"]:
                if (env_location / pip_dependency).is_dir():
                    pip_dependencies.append((env_location / pip_dependency).resolve())
                else:
                    pip_dependencies.append(pip_dependency)
    return specs, pip_dependencies
```

支持本地Python包目录（相对路径），会自动转为绝对路径。

## _pip.py 模块

### _install_pip_dependencies 函数

在emscripten conda环境中安装纯Python pip包。

```python
def _install_pip_dependencies(prefix_path, dependencies, log=None):
```

**重要说明**：该函数带有experimental警告：
> "Installing pip dependencies. This is very much experimental so use this feature at your own risks. Note that you can only install pure-python packages."

### 执行流程

1. 创建临时目录 `pkg_dir = TemporaryDirectory()`
2. 从 `{prefix_path}/conda-meta/python-3.*.json` 获取Python版本号
3. 使用当前Python（`sys.executable -m pip`）下载包到临时目录：
   ```bash
   {sys.executable} -m pip install {dependencies} \
     --target {pkg_dir.name} \
     --python-version {python_version} \
     --no-deps \
     --no-input \
     --verbose
   ```
   **注意**：没有指定`--platform`、`--only-binary`、`--abi`等cross-platform参数——pip安装时使用当前Python版本，不强制wasm平台。

4. 遍历临时目录中的 `.dist-info` 目录：
   - 读取RECORD文件获取包内所有文件列表
   - 修正RECORD路径（`../../`替换为`../../../`，处理路径偏移）
   - 检查文件后缀：如果包含 `.so`、`.a`、`.dylib`、`.lib`、`.exe.dll` 则报错
   - 区分site-packages内文件和外部文件（以`../../`开头的为外部文件）
   - 将文件复制到prefix对应位置：
     - site-packages内文件 → `{prefix_path}/lib/python{version}/site-packages/`
     - 外部文件 → `{prefix_path}/`（保持相对路径）

### 二进制文件检查

```python
non_supported_files = [".so", ".a", ".dylib", ".lib", ".exe.dll"]
```

如果包内包含以上后缀的文件，抛出错误：
> "Cannot install binary PyPI package, only pure Python packages are supported"

**注意**：实际检查的后缀列表比概念文档中列出的短——只检查编译的二进制文件（.so/.a/.dylib/.lib/.exe.dll），不检查C/C++/Fortran/Rust/Go源码文件后缀（如.c/.cpp/.f/.rs等）。这意味着pip包中的.c/.h等源码文件不会被拒绝（但它们在WASM环境中无用）。

### _get_python_version 函数

```python
def _get_python_version(prefix_path):
    path = glob.glob(f"{prefix_path}/conda-meta/python-3.*.json")
    if not path:
        raise RuntimeError("Python needs to be installed for installing pip dependencies")
    version = json.load(open(path[0]))["version"].split(".")
    return f"{version[0]}.{version[1]}"  # 如 "3.12"
```

从conda-meta中读取Python版本号。

## 关键约束（基于实际代码）

1. **micromamba必须预安装**：不会自动下载，需要用户通过conda或官方安装程序预先安装到PATH
2. **pip只检查二进制文件**：`.so/.a/.dylib/.lib/.exe.dll`会被拒绝，源码文件(.c/.cpp等)不会被拦截
3. **pip安装是experimental**：代码中有明确的warning
4. **pip使用--no-deps**：不自动安装依赖，用户需确保pip包的依赖已通过conda安装
5. **环境路径**：conda环境在 `{root_prefix}/envs/{env_name}/`，不是直接在root_prefix
6. **--no-pyc**：micromamba create使用--no-pyc避免生成.pyc文件
7. **--relocate-prefix ""**：允许重定位前缀（empack打包时需要）
8. **RECORD修正**：pip包的RECORD文件路径被修正以适配WASM环境中的路径结构

## 与add_on.py的协作

XeusAddon.post_build()调用流程：
1. `self.create_prefix(env_file)` → 调用 `create_conda_env_from_env_file()`
2. prefix路径管理由XeusAddon负责（使用临时目录）
3. 构建完成后环境被复制/打包到输出目录

## 相关概念

- [构建系统详解](../concepts/05-build-system.md)
- [包管理](../concepts/06-package-management.md)
- [快速开始](../concepts/01-getting-started.md)
- [XeusAddon参考](python-addon-source.md)
