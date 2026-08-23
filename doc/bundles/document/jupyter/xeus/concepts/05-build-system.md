---
type: Concept
title: 构建系统详解
description: jupyterlite-xeus Python构建端的完整流程——micromamba环境创建、conda依赖解析、empack打包、内核文件复制、kernels.json生成
tags: [build, conda, micromamba, empack, python, deploy]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: insight-2
    resource: /concepts/05-build-system.md
    title: 洞察I-2 构建时Python
  - id: addon
    resource: /references/python-addon-source.md
    title: XeusAddon参考
  - id: conda
    resource: /references/conda-env-source.md
    title: Conda环境创建参考
---

## 构建系统概述

jupyterlite-xeus 的构建完全在**构建时**（开发机/CI）完成，执行 `jupyter lite build` 时触发。构建产物是纯静态文件，可部署到任意静态文件服务器。

构建系统核心是 `XeusAddon` 类，它继承自 JupyterLite 的 `FederatedExtensionAddon`，通过 `post_build` hook 参与构建流程。

## 构建前置依赖

| 依赖 | 用途 | 获取方式 |
|------|------|---------|
| Python >= 3.10 | 运行构建脚本 | 系统安装 |
| micromamba | 创建emscripten-wasm32 conda环境 | 需预安装到系统PATH |
| empack >= 5.1.1 | 打包conda环境为浏览器可用tar.gz | pip依赖自动安装 |
| Node.js | 构建JupyterLab前端扩展 | 系统安装 |

### micromamba 安装

构建系统通过 `shutil.which("micromamba")` 查找系统PATH中已安装的micromamba。如果未找到，会抛出RuntimeError：

> "micromamba is needed for creating the emscripten environment. Please install it using conda `conda install micromamba -c conda-forge` or from https://mamba.readthedocs.io/..."

安装方式：
- **conda安装**：`conda install micromamba -c conda-forge`
- **官方安装程序**：从 https://mamba.readthedocs.io/ 下载对应平台版本

## 构建流程详解

执行 `jupyter lite build` → `XeusAddon.post_build()` 按以下顺序执行：

### 步骤1：准备工作目录

```python
with TemporaryDirectory() as tmp_dir:
    prefix = Path(tmp_dir) / "env"       # conda环境目录
    pkg_dir = Path(tmp_dir) / "packed"   # 打包输出目录
    pack_extra_dir = Path(tmp_dir) / "packed_extra"  # 额外包目录
```

使用临时目录确保构建环境隔离，构建完成后自动清理。

### 步骤2：创建conda环境

调用 [create_conda_environment()](../references/conda-env-source.md#create_conda_environment-函数)：

```bash
micromamba create -y -p {prefix} -r {prefix} \
  --platform emscripten-wasm32 \
  -c https://prefix.dev/emscripten-forge-4x \
  -c https://prefix.dev/conda-forge \
  -f {environment_file} \
  xeus-python  # required_packages
```

**关键点**：
- `--platform emscripten-wasm32`：创建**WebAssembly 32位**平台的conda环境，不是host平台环境
- 这是一个**交叉编译**环境——包是预编译为WASM的，不能在host机器上直接运行
- 默认channels是prefix.dev的emscripten-forge-4x和conda-forge
- 如果指定了environment_file，同时安装其中的包

### 步骤3：处理pip依赖

如果environment.yml中有pip section：

```python
pip_deps = pip_dependencies(env_file)
if pip_deps:
    await install_pip_packages(prefix, pip_deps)
```

pip安装命令：
```bash
pip install \
  --python-version 3.12 \
  --platform emscripten_3_1_58_wasm32 \
  --target {prefix}/site-packages \
  --only-binary :all: \
  --abi cp312 \
  --implementation py \
  --no-deps \
  {packages}
```

**关键约束**：
- `--only-binary :all:`：只安装wheel，不允许sdist
- `--no-deps`：不安装依赖（conda负责依赖管理）
- `--platform emscripten_3_1_58_wasm32`：下载WASM平台的wheel
- [collect_packages_to_pack()](../references/conda-env-source.md#collect_packages_to_pack-函数)会检查包内容，拒绝含C扩展的包

### 步骤4：复制内核静态文件

调用 `copy_xpython_static()`：

1. 读取 `{prefix}/conda-meta/xeus-{name}-{version}.json` 获取内核文件清单
2. 将清单中的文件复制到 `{output_dir}/xeus/kernels/{kernel_name}/`
3. **所有文件平铺到同一目录**（不保留conda环境中的子目录结构）
4. ELF二进制文件创建 `.wasm` 软链接（empack将ELF转为WASM格式）

复制的文件包括：
- `xpython.js`（Emscripten生成的JS加载器）
- `xpython.wasm`（WASM二进制）
- `xpython.data`（预加载数据文件）
- 内核logo图片（kernel-64x64.png、logo-64x64.png、logo-svg.svg）

### 步骤5：打包conda环境（empack）

调用 `pack_prefix()`：

1. 创建 `pack_dir/pack` 目录
2. 初始化 `PackManager()`（empack的核心打包器）
3. **处理mounts配置**：
   - 目录 → `pack_directory(path, mount_path)`：将目录打包为tarball，启动时解压到mount_path
   - 文件 → `pack_file(filename, mount_path)`：将单个文件打包
4. **处理JupyterLite内容挂载**（如果mount_jupyterlite_content=true）：
   - 将 `{output_dir}/files` 目录打包为tarball
   - 通过 `add_tarfile_to_env_meta()` 注册为 `/files` 挂载点
5. 设置package_url_template（告诉WASM端从哪里下载包）：
   - kernel_packages: `'xeus/' + env_name + '/kernel_packages/{filename}'`
   - extra-packages: `'xeus/' + env_name + '/extra-packages/{filename}'`
6. 调用 `pack_env()` 执行打包：
   - 扫描prefix中所有安装的包
   - 将每个包打包为独立的tar.gz（包含包文件+元数据）
   - 生成 `empack_env_meta.json`（环境元数据：prefix、包列表、channels、mounts等）
7. 将打包结果移动到 `{output_dir}/xeus/{env_name}/kernel_packages/`

### 步骤6：打包额外内容

额外包（如JupyterLite内容目录）打包到 `{output_dir}/xeus/{env_name}/extra-packages/`。

### 步骤7：写入kernel.json

为每个内核在 `{output_dir}/xeus/kernels/{kernel_name}/kernel.json` 写入内核规格：

```json
{
  "argv": ["xeus/kernels/xpython/xpython.js"],
  "display_name": "Python (XPython)",
  "language": "python",
  "metadata": {
    "shared": { /* 预链接共享库映射 */ },
    "kernel_type": "xeus"
  },
  "resources": {
    "kernel-64x64.png": "xeus/kernels/xpython/kernel-64x64.png",
    "logo-64x64.png": "xeus/kernels/xpython/logo-64x64.png",
    "logo-svg.svg": "xeus/kernels/xpython/logo-svg.svg"
  }
}
```

### 步骤8：写入kernels.json

在 `{output_dir}/xeus/kernels.json` 写入所有可用内核的清单：

```json
{
  "kernels": [
    {
      "name": "xpython",
      "dir": "xpython",
      "display_name": "Python (XPython)",
      "language": "python"
    }
  ]
}
```

## 构建产物目录结构

```
{output_dir}/
├── xeus/
│   ├── kernels.json                    # 内核清单
│   ├── kernels/
│   │   └── xpython/
│   │       ├── kernel.json             # 内核规格
│   │       ├── xpython.js              # Emscripten JS加载器
│   │       ├── xpython.wasm            # WASM内核二进制
│   │       ├── xpython.data            # 预加载数据
│   │       ├── libxeus.wasm → libxeus.so  # WASM软链
│   │       ├── kernel-64x64.png        # 小图标
│   │       ├── logo-64x64.png
│   │       └── logo-svg.svg            # SVG logo
│   └── xpython/                        # env_name
│       ├── kernel_packages/            # empack打包的conda包
│       │   ├── empack_env_meta.json    # 环境元数据
│       │   ├── python-3.12-*.tar.gz
│       │   ├── numpy-*.tar.gz
│       │   └── ... (每个conda包一个tar.gz)
│       ├── libxeus.wasm                # xeus共享库
│       └── extra-packages/             # 额外包和挂载内容
│           └── ...
├── jupyterlite/                        # JupyterLite核心文件
├── lab/                                # JupyterLab前端
├── retro/                              # RetroLab
├── repl/                               # REPL
├── files/                              # 用户文件目录
├── api/
│   └── contents/                       # Contents API（Service Worker）
├── config-utils.js
├── package.json
└── index.html
```

## 配置详解

### environment_file

指定conda环境配置文件路径。文件格式为标准conda environment.yml：

```yaml
name: xeus-python-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - pandas
  - matplotlib
  - pip:
    - some-pure-python-wheel-package
```

**注意**：
- channels必须包含emscripten-forge频道（提供WASM编译的包）
- pip依赖只支持纯Python包
- conda依赖支持C扩展（预编译为WASM）

### default_channels

覆盖默认的conda channels。列表中的URL按优先级排序。

### mount_jupyterlite_content

控制是否将JupyterLite的files目录打包挂载到WASM文件系统的 `/files`。
- 默认为 `True` 仅当app是voici（Voilà静态化）
- 其他app默认为 `False`
- 启用后，构建时 `{output_dir}/files/` 中的所有文件会打包到内核启动时自动挂载

### empack_config

empack打包的过滤配置，可以是文件路径（YAML）或dict。用于排除不需要打包的文件、配置包过滤规则等。

### mounts配置（高级）

在environment.yml或empack_config中配置自定义挂载点：

```yaml
# 示例：挂载本地数据目录
mounts:
  - from: ./data
    to: /home/xeus/data
  - from: ./config.json
    to: /etc/myapp/config.json
```

约束：
- `to` 路径必须是绝对路径
- `to` 路径不能以 `/files` 开头（保留给JupyterLite内容）
- 目录会被打包为tar.gz，启动时解压

## 构建性能优化

1. **conda包缓存**：micromamba使用自己的包缓存（在root_prefix的pkgs目录），重复构建时复用已下载的包
2. **empack缓存**：pack_env默认`use_cache=False`，每次重新打包
3. **增量构建**：如果环境配置未变化，可以复用已有的_env目录（但当前实现在cwd_name下创建，每次build可能重建）

## 常见构建错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| "micromamba is needed" RuntimeError | 系统未安装micromamba | `conda install micromamba -c conda-forge` 或从官方下载 |
| 包冲突 | conda依赖求解失败 | 检查environment.yml中的版本约束，使用更宽松的版本 |
| "Cannot install binary PyPI package" | pip包含编译的二进制文件（.so/.dll等） | 将该包改为conda依赖，从emscripten-forge安装 |
| "Package not found" | emscripten-forge中没有该包 | 检查包名是否正确，或确认该包是否有WASM版本 |
| empack打包失败 | 包元数据异常 | 检查conda环境是否正确创建，prefix下文件是否完整 |
| 内核启动后FileNotFound | 内核文件复制路径错误 | 检查copy_kernels_from_prefix是否正确识别了内核目录中的kernel.json |

## 相关API

- [XeusAddon.post_build()](../references/python-addon-source.md#post_build-主流程)
- [create_conda_environment()](../references/conda-env-source.md#create_conda_environment-函数)
- [install_pip_packages()](../references/conda-env-source.md#install_pip_packages-函数)
- [pack_prefix()](../references/python-addon-source.md#pack_prefix)

## 相关概念

- [快速开始](01-getting-started.md)
- [双语言分层架构](02-architecture.md)
- [包管理](06-package-management.md)
- [基础部署示例](../examples/basic-deploy.md)
