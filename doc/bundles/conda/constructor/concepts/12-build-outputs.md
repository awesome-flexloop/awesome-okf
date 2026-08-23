---
type: concept
title: "构建输出产物"
description: "constructor 的 build_outputs 机制：hash校验文件、info.json构建信息、licenses许可证集合、lockfile锁文件和pkgs_list包列表。"
tags: [build_outputs, hash, info.json, licenses, lockfile, pkgs_list, 构建产物]
status: stable
stale_after: 2027-12-31
level: intermediate
prerequisites: ["03-construct-yaml-schema", "06-fcp-fetch-and-solve"]
reading_time: 8
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-build-outputs
    resource: "constructor/build_outputs.py"
---

# 构建输出产物

除了安装程序本身，constructor 还可以通过 `build_outputs` 配置生成多种辅助产物，用于完整性校验、合规审计、环境复制等场景。

## 配置方式

```yaml
build_outputs:
  - hash
  - info.json
  - licenses
  - lockfile
  - pkgs_list
```

也可以带配置选项（单 key 字典）：

```yaml
build_outputs:
  - hash:
      algorithm: sha256
  - licenses:
      include_text: true
```

## 产物类型

### 1. hash — 哈希校验文件

生成安装程序文件的哈希校验和，用于验证下载完整性。

**输出文件**：
- `<installer>.sha256`（SHA-256 哈希）
- 如配置多算法，可输出 `.md5` 等

**内容格式**（标准 hash 工具兼容）：
```
<sha256-hash> <installer-filename>
```

**配置选项**：
```yaml
build_outputs:
  - hash:
      algorithm: sha256    # 哈希算法（支持 hashlib 所有算法）
```

使用方法：
```bash
sha256sum -c mypython-1.0-Linux-x86_64.sh.sha256
```

**实现函数**：`dump_hash(info, algorithm)` 在 `build_outputs.py` 中，使用 `utils.hash_files()` 计算。

### 2. info.json — 构建信息 JSON

包含安装程序的完整元数据 JSON 文件。

**输出文件**：`<installer>.info.json`

**包含字段**：
```json
{
  "name": "mypython",
  "version": "1.0.0",
  "platform": "linux-64",
  "installer_type": "sh",
  "constructor_version": "4.0.0",
  "channels": ["https://repo.anaconda.com/pkgs/main"],
  "specs": ["python 3.14.*", "pip"],
  "packages": {
    "base": [
      {"name": "python", "version": "3.14.6", "build": "h...", ...},
      ...
    ],
    "datascience": [...]
  },
  "approx_pkgs_size": 123456789,
  "approx_tarballs_size": 45678901,
  "build_platform": "linux-64",
  "build_date": "2026-08-21T00:00:00Z"
}
```

**实现函数**：`dump_info(info)` 从 info 字典和包记录中提取元数据。

**用途**：
- CI/CD 中的构建记录
- SBOM（Software Bill of Materials）
- 合规审计
- 安装程序版本追溯

### 3. licenses — 许可证集合

收集所有包含包的许可证文件，用于合规审计。

**输出文件**：
- `<installer>-licenses.tar.gz` 或 `<installer>-licenses/` 目录

**包含内容**：
- 每个包的 `info/licenses/` 目录
- 每个包的 `info/about.json`（包含 license 字段）
- 包的许可证文本文件（LICENSE、LICENSE.txt、COPYING 等）
- 索引文件（index.json 或 index.txt）

**配置选项**：
```yaml
build_outputs:
  - licenses:
      include_text: true     # 包含许可证文本（默认false，仅元数据）
      text_errors: "warn"    # 文本提取错误处理：warn/fail/ignore
```

**实现函数**：`dump_licenses(info, include_text, text_errors)` 遍历 `_all_pkg_records`，读取每个包的 `info/` 目录下的许可证文件。

**用途**：
- 开源合规审计（确认许可证兼容性）
- 法律审查
- 企业内部许可证管理

### 4. lockfile — Conda Lock 文件

生成 [conda-lock](https://github.com/conda/conda-lock) 格式的锁文件，记录所有包的精确版本和哈希。

**输出文件**：`<installer>-<platform>.lock` 或 `<installer>-lock.yml`

**内容格式**（conda-lock 兼容）：
```yaml
metadata:
  content_hash:
    linux-64: abc123...
  channels:
  - url: https://conda.anaconda.org/conda-forge
  platform:
  - linux-64
package:
- name: python
  version: 3.14.6
  manager: conda
  platform: linux-64
  dependencies:
    libffi: '>=3.4'
    openssl: '>=3.0'
  url: https://conda.anaconda.org/.../python-3.14.6-h...tar.bz2
  hash:
    md5: abc123...
    sha256: def456...
  category: main
  optional: false
```

多环境时，为每个环境生成独立的锁文件。

**实现函数**：`dump_lockfile(info, env="base")` 从 `_records` 中提取包信息，生成锁文件。

**用途**：
- 可重现构建（其他人可用 lockfile 创建相同环境）
- 安全审计（精确知道安装了什么版本的包）
- 与 conda-lock/mamba 生态集成

### 5. pkgs_list — 包列表

生成包含的包列表（CSV 或 JSON 格式）。

**输出文件**：
- `<installer>-pkgs_list.csv`
- `<installer>-pkgs_list.json`

**内容格式**（CSV）：
```
name,version,build,channel,size
python,3.14.6,habc123_0,conda-forge,15234567
pip,25.3,py314_0,conda-forge,2345678
openssl,3.5.0,h123_0,conda-forge,3456789
```

**实现函数**：`dump_packages_list(info, env="base")` 从 `_records` 中提取包名、版本、build字符串、通道和大小。

**用途**：
- 快速查看安装程序包含的包
- 版本比较（不同构建之间的差异）
- 电子表格/BI 工具分析

## OUTPUT_HANDLERS 注册机制

build_outputs 使用注册机制管理处理函数：

```python
# build_outputs.py
OUTPUT_HANDLERS = {
    BuildOutputs.HASH: dump_hash,
    BuildOutputs.INFO_JSON: dump_info,
    BuildOutputs.LICENSES: dump_licenses,
    BuildOutputs.LOCKFILE: dump_lockfile,
    BuildOutputs.PKGS_LIST: dump_packages_list,
}
```

`process_build_outputs(info)` 根据 `info["_build_outputs"]` 调用对应的处理函数。

Schema 中的 `BuildOutputs` 枚举与 `OUTPUT_HANDLERS` 字典通过 `checks()` 函数保持同步——如果两边不一致会直接 AssertionError。

## 多安装类型时的处理

当构建多种安装程序类型时（如 macOS 上同时构建 .sh 和 .pkg），build_outputs 会为每种类型生成对应的产物。某些类型特有的键值差异（如 pkg 有 welcome_file 而 sh 没有）会以列表形式存储在 info 中，process_build_outputs 正确处理这些差异。

## 内部辅助函数

### get_build_env_records(prefix)

获取指定前缀中所有已安装包的 PackageRecord 列表（用于 environment 模式，从已有环境复制包信息）。

### _validate_output(output)

验证 build_outputs 配置项是否合法：
- 字符串必须是 BuildOutputs 枚举值之一
- 字典必须只有一个 key，且 key 是合法的 BuildOutputs 值
- 抛异常终止构建

### _needed_hash_algorithms(info)

从 build_outputs 配置中提取所有需要的哈希算法集合。

## 下一步

- [14-工具集与辅助函数](../14-utils-and-helpers.md)：了解 hash_files、yaml 处理等工具函数
- [06-FCP 依赖求解与包下载](../06-fcp-fetch-and-solve.md)：了解 build_outputs 数据来源（_records/_all_pkg_records）
