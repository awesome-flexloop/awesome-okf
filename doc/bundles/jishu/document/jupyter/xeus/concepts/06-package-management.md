---
type: Concept
title: 浏览器内包管理
description: jupyterlite-xeus通过mambajs+empack在浏览器内实现%conda install/%pip install动态包管理，支持运行时安装conda和pip包，但存在重要限制
tags: [package-management, mambajs, empack, conda, pip, wasm, magic-commands]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: insight-4
    resource: /concepts/06-package-management.md
    title: 洞察I-4 浏览器内包管理
  - id: kernel-impl
    resource: /references/kernel-impl-source.md
    title: empack内核实现
  - id: conda
    resource: /references/conda-env-source.md
    title: Conda环境创建
---

## 包管理架构

jupyterlite-xeus 的包管理分为两个阶段，由两个不同组件负责：

```
┌──────────────────────────────────────────────────────────┐
│ 构建时 (Python/empack)                                    │
│ ┌─────────────┐    ┌────────────┐    ┌────────────────┐ │
│ │ micromamba  │───→│ empack     │───→│ tar.gz 包文件  │ │
│ │ 创建环境    │    │ 打包       │    │ kernel_packages/│ │
│ └─────────────┘    └────────────┘    └────────────────┘ │
│ 预装包 + 元数据锁文件                                      │
└──────────────────────────────────────────────────────────┘
                          ↓ 部署
┌──────────────────────────────────────────────────────────┐
│ 运行时 (浏览器/mambajs)                                   │
│ ┌─────────────┐    ┌────────────┐    ┌────────────────┐ │
│ │ mambajs     │───→│ updateFS   │───→│ Emscripten MEMFS│ │
│ │ 求解依赖    │    │ 更新文件系统│    │ /usr/local/... │ │
│ └─────────────┘    └────────────┘    └────────────────┘ │
│ %conda / %pip 魔法命令                                    │
└──────────────────────────────────────────────────────────┘
```

- **构建时**：micromamba创建conda环境，empack将环境打包为tar.gz + 锁文件（empack_env_meta.json）
- **运行时**：mambajs在浏览器内求解依赖、下载tar.gz包、解压到Emscripten MEMFS

## 魔法命令

在Notebook单元格中使用以下魔法命令管理包：

### conda 命令

```python
# 安装包
%conda install numpy pandas matplotlib

# 指定channel
%conda install -c https://prefix.dev/conda-forge some-package

# 删除包
%conda remove numpy

# 列出已安装包
%conda list
```

### pip 命令

```python
# 安装纯Python包
%pip install pure-python-package

# 卸载pip包
%pip uninstall some-package

# 列出已安装pip包
%pip list
```

### 魔法命令解析

[EmpackedXeusRemoteKernel.processMagics()](../references/kernel-base-source.md#魔法命令处理) 使用mambajs-core的`parse()`函数解析代码前缀：

1. 检测代码是否以 `%conda` 或 `%pip` 开头
2. 解析子命令（install/remove/list/uninstall）
3. 调用对应方法执行包操作
4. 返回剥离魔法命令后的代码（conda命令通常返回空字符串，不执行后续代码）

## 运行时包管理实现

### conda install 流程

[EmpackedXeusRemoteKernel.install()](../references/kernel-impl-source.md#动态包管理方法) 执行：

```typescript
protected async install(options: IInstallationCommandOptions): Promise<void> {
  if (options.type === 'conda') {
    // 1. mambajs求解依赖并下载包
    const newLock = await install(options.specs, this._lock, {
      channels: options.channels,
      rootUrl: this._pkgRootUrl,
      logger: this._mambajsLogger,
    });
    // 2. 更新Emscripten文件系统
    await this._reloadPackagesInFS(newLock);
  } else if (options.type === 'pip') {
    // pip安装...
    const newLock = await pipInstall(options.specs, this._lock, {
      rootUrl: this._pkgRootUrl,
      logger: this._mambajsLogger,
    });
    await this._reloadPackagesInFS(newLock);
  }
}
```

### _reloadPackagesInFS 实现

[EmpackedXeusRemoteKernel._reloadPackagesInFS()](../references/kernel-impl-source.md#_reloadpackagesinfs-方法)：

1. 保存当前工作目录 `pwd = FS.cwd()`
2. `FS.chdir('/')` 切换到根目录（避免触发自定义DriveFS操作）
3. 调用 `updatePackagesInEmscriptenFS()`：
   - 对比新旧lock文件
   - 下载新包的tar.gz
   - 解压到Emscripten MEMFS
   - 删除已移除的包文件
4. 过滤出新增的共享库（排除已预链接的内核共享库）
5. emscripten < 4时调用 `loadSharedLibs()` 加载新的.so文件
6. 更新 `this._lock = newLock`
7. 恢复工作目录 `FS.chdir(pwd)`

### 锁文件（Lock File）

`this._lock` 是 mambajs 的 `ILock` 类型，包含：

```typescript
interface ILock {
  packages: Array<{
    name: string;
    version: string;
    url: string;
    sha256: string;
    depends: string[];
    files: string[];
    // ...
  }>;
  // channels, platforms等
}
```

初始锁文件通过 `empackLockToMambajsLock()` 从构建时生成的 `empack_env_meta.json` 转换而来。

## 重要限制

### 1. 仅内存持久化（刷新即失）

运行时安装的包存储在 Emscripten MEMFS 中——这是一个纯内存文件系统。**页面刷新后所有通过%conda/%pip安装的包都会丢失**。

**解决方案**：
- 需要持久化的包，在构建时通过 environment.yml 预安装
- 未来可能支持 IDBFS（IndexedDB文件系统）持久化，但当前未实现

### 2. pip 仅支持纯Python包

[pip安装会检查wheel内容](../references/conda-env-source.md#_install_pip_dependencies-函数)，拒绝包含编译二进制文件的包（仅检查以下后缀）：

| 禁止的后缀 | 说明 |
|-----------|------|
| `.so` | Linux/Unix共享库（WASM环境下也是编译的二进制） |
| `.a` | 静态链接库 |
| `.dylib` | macOS动态库 |
| `.lib` | Windows静态库 |
| `.exe.dll` | Windows可执行DLL |

> **注意**：构建时pip检查仅检测上述二进制文件后缀，不检查源码文件（.c/.cpp/.rs等）。运行时`%pip install`由xeus内核中的mambajs执行。

包含二进制文件的包必须通过conda安装（emscripten-forge频道有预编译的WASM版本）。

错误信息：
> "Cannot install binary PyPI package, only pure Python packages are supported"

### 3. conda包来源限制

运行时 `%conda install` 由mambajs在浏览器内运行libsolv依赖求解器：
- 预装包：从 `{baseUrl}xeus/{envName}/kernel_packages/` 下载empack打包的conda包
- 新包：从channels配置的远程URL下载（需要网络连接，必须有emscripten-wasm32版本）

离线使用时，只能安装构建时已打包到kernel_packages中的包。

### 4. 共享库加载限制

Emscripten 4+ 版本支持动态链接（dlopen），但：
- emscripten < 4时，新安装包含共享库的包需要调用 `loadSharedLibs()` 手动加载
- 某些核心库（如libpython、libxeus）已预链接到内核WASM，不能重复加载
- `_sharedLibsToNotLink` 集合排除了这些核心库

### 5. 性能考虑

- 包下载受网络速度限制（每个包是独立的tar.gz）
- 解压tar.gz到MEMFS是CPU密集型操作，大包可能导致UI短暂卡顿
- 包安装过程中Worker会阻塞消息处理，无法执行代码

## 包管理 vs 构建时预装对比

| 维度 | 运行时安装 (%conda/%pip) | 构建时预装 (environment.yml) |
|------|------------------------|---------------------------|
| 持久化 | ❌ 刷新丢失 | ✅ 永久可用 |
| 需要网络 | ✅ （新包需要下载） | ❌ （构建后离线可用） |
| C扩展支持 | ✅ conda支持 | ✅ conda支持 |
| 纯Python pip包 | ✅ | ✅ |
| 灵活性 | ✅ 按需安装 | ❌ 需重新构建 |
| 首次加载速度 | ⚠️ 下载+解压 | ✅ 预解压到kernel_packages |
| 部署包体积 | ✅ 初始包体积小 | ⚠️ 预装所有包体积大 |

## 最佳实践

1. **常用包预装**：数据科学生态（numpy、pandas、matplotlib等）在environment.yml中预装，保证快速启动
2. **临时探索用运行时安装**：%conda install用于Notebook中临时尝试新包
3. **避免pip安装大包**：有C扩展的包用conda，pip只用于纯Python工具
4. **重要环境固化**：如果某个包组合很重要，在environment.yml中锁定版本，不要依赖运行时安装
5. **离线部署注意**：完全离线场景下，预装所有需要的包——运行时%conda install无法下载新包

## Emscripten ABI版本检测

[EmpackedXeusRemoteKernel.emscriptenMajorVersion](../references/kernel-impl-source.md#emscriptenmajorversion-getter) 从lock文件中检测Emscripten ABI版本：

```typescript
get emscriptenMajorVersion(): number {
  for (const pkg of this._lock.packages) {
    if (pkg.name === 'emscripten-abi') {
      return parseInt(pkg.version.split('.')[0]);
    }
  }
  return 0; // fallback: 加载所有共享库
}
```

这决定了共享库加载策略：
- **emscripten >= 4**：动态链接器自动处理共享库加载
- **emscripten < 4**：手动调用 `loadSharedLibs()` 加载新增的.so文件

## 相关API

- [processMagics()](../references/kernel-base-source.md#魔法命令处理) - 魔法命令解析
- [install()/uninstall()/listInstalledPackages()](../references/kernel-impl-source.md#动态包管理方法) - 包管理方法
- [_reloadPackagesInFS()](../references/kernel-impl-source.md#_reloadpackagesinfs-方法) - 文件系统更新
- [create_conda_environment()](../references/conda-env-source.md#create_conda_environment-函数) - 构建时环境创建
- [collect_packages_to_pack()](../references/conda-env-source.md#collect_packages_to_pack-函数) - pip包验证

## 相关概念

- [内核生命周期](04-kernel-lifecycle.md)
- [文件系统桥接](07-filesystem-bridge.md)
- [构建系统详解](05-build-system.md)
