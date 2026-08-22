---
type: Reference
title: Python构建端XeusAddon参考
description: jupyterlite_xeus Python包的XeusAddon构建addon，负责conda环境创建、内核复制和empack打包
tags: [python, build, addon, conda, empack, jupyterlite]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: addon-src
    resource: /references/python-addon-source.md
    title: jupyterlite_xeus/add_on.py
---

## XeusAddon 类

继承自 `jupyterlite.addons.federated_extension_addon.FederatedExtensionAddon`，定义在 [add_on.py](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/jupyterlite_xeus/add_on.py)。

### 配置项（Traitlets）

| 配置名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| log_level | str | "INFO" | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| environment_file | ListLike | ["environment.yml"]或["environment.yaml"] | conda环境配置文件路径列表，支持多个环境文件 |
| default_channels | list[str] | `["https://prefix.dev/emscripten-forge-4x", "https://prefix.dev/conda-forge"]` | 默认conda channels |
| mount_jupyterlite_content | Bool | True（仅voici app） | 是否将JupyterLite输出目录打包为/mount |
| empack_config | Union\[Unicode, dict\] | None | empack打包配置（文件路径或dict） |

### post_build 主流程

`post_build` 是一个generator（yield任务进度），执行顺序：

```
1. 获取/创建工作目录（cwd_name，包含_env子目录存放micromamba环境）
2. 对每个environment_file：
   a. create_prefix(env_file) → 调用create_conda_env_from_env_file()创建emscripten-wasm32 conda环境
   b. copy_kernels_from_prefix(env_name, prefix) → 从conda环境复制内核二进制（yield copy任务）
      - 查找prefix/share/jupyter/kernels/下的内核目录
      - copy_kernel()复制内核JS/WASM/DATA文件
      - 复制libxeus.so
      - pack_prefix() → empack打包conda环境
3. 处理extra packages（额外包打包）
4. 处理mount_jupyterlite_content：将output_dir/files打包
5. write_kernelspecs(output_dir) → 写入kernel.json
6. write_empack_config(...) → 写kernels.json和empack配置
```

**前置条件**：系统PATH中必须已安装micromamba（通过conda install micromamba -c conda-forge或官方安装程序），构建不会自动下载。

### 关键方法

#### copy_kernels_from_prefix

```python
def copy_kernels_from_prefix(self, env_name, prefix):
```

从conda环境的 `prefix/share/jupyter/kernels/` 目录查找所有内核（通过kernel.json）：
- 调用 `get_kernel_binaries(kernel_dir)` 从kernel.json的argv[0]定位.js/.wasm/.data文件
- yield copy任务：`copy_kernel()` 复制JS/WASM/DATA文件到 `{output_dir}/xeus/kernels/{kernel_name}/`
- yield copy任务：复制 `lib/libxeus.so` 到 `{output_dir}/xeus/{env_name}/libxeus.so`
- yield pack_prefix()任务：empack打包conda环境

#### get_kernel_binaries（工具函数）

```python
def get_kernel_binaries(path):
```

从内核目录读取kernel.json，从argv[0]推导JS/WASM/DATA文件路径。返回`(js_path, wasm_path, data_path_or_None)`，文件不存在时返回None并warn。

#### pack_prefix

```python
def pack_prefix(self, env_name, prefix):
```

使用empack将conda环境打包为浏览器可用的tar.gz包（配置通过self属性传入）：

1. 创建 `cwd_name/packed_env/{env_name}` 输出目录
2. 处理empack_config（支持URL和本地文件路径），生成file_filters；未配置时使用DEFAULT_CONFIG_PATH
3. 调用 `pack_env(env_prefix=prefix, relocate_prefix="/", outdir=out_path, use_cache=False, **pack_kwargs)` 打包conda环境
4. 处理mounts配置（格式为`"<host_path>:<mount_path>"`字符串列表）：
   - 目录：调用 `pack_directory(host_dir, mount_dir, outname, outdir)` 打包目录
   - 文件：调用 `pack_file(host_file, mount_dir, outname, outdir)` 打包文件
   - 通过 `add_tarfile_to_env_meta()` 注册到环境元数据
   - mount_path必须是绝对路径，不能以`/files`开头
5. 如果mount_jupyterlite_content启用（voici app默认为True）：
   - 将 `{output_dir}/files` 目录打包为tarball
   - 通过 `add_tarfile_to_env_meta()` 注册为 `/files` 挂载点
6. 将打包结果移动到 `{output_dir}/xeus/{env_name}/kernel_packages/`

#### write_empack_config

```python
def write_empack_config(prefix, pkg_dir, pack_extra_dir, output_dir)
```

生成 `{output_dir}/xeus/kernels.json`，包含所有可用内核的规格列表。

#### create_config

```python
def create_config() -> dict
```

读取empack_config配置：
- 如果是dict直接使用
- 如果是文件路径则YAML加载
- 如果未设置则返回空dict

### 输出目录结构

构建后在 `output_dir/xeus/` 下生成：

```
xeus/
├── kernels.json              # 内核清单（所有可用内核规格）
├── {env_name}/               # 如 xpython/
│   ├── kernel_packages/      # empack打包的conda包tar.gz
│   │   └── ...
│   ├── libxeus.wasm          # xeus共享库
│   ├── extra-packages/       # 额外包和挂载内容tar.gz
│   └── kernel.json           # 内核规格（由write_kernelspecs写入）
└── kernels/
    └── {kernel_name}/        # 内核二进制文件
        ├── xpython.wasm
        ├── xpython.data
        ├── xpython.js
        ├── kernel-64x64.png
        ├── logo-64x64.png
        └── logo-svg.svg
```

## 相关概念

- [构建系统](../concepts/05-build-system.md)
- [入门指南](../concepts/01-getting-started.md)
- [包管理](../concepts/06-package-management.md)
- [Conda环境创建参考](conda-env-source.md)
