---
type: "concept"
title: "打包流程与 Packer"
description: Packer 类如何逐个处理文件、判断文件类型、执行前缀替换、shebang 重写、添加激活脚本和生成 conda-unpack。
tags: [conda-pack, packer, packing, prefix-rewrite, shebang, conda-unpack]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
  - id: formats
    resource: /references/formats-source.md
    title: formats.py 归档格式模块源码
---

# 打包流程与 Packer

`Packer` 类是打包执行的核心，负责将 `CondaEnv.files` 列表中的每个文件添加到归档，处理前缀替换、shebang 重写，并在收尾阶段生成辅助脚本。

## Packer 初始化

```python
packer = Packer(self.prefix, arc, dest_prefix, parcel)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `prefix` | `str` | 源环境路径 |
| `archive` | `ArchiveBase` | 归档对象（TarArchive/ZipArchive/...） |
| `dest` | `str`/`None` | 目标前缀（指定则打包时替换，不生成 conda-unpack） |
| `has_dest` | `bool` | 是否指定了目标前缀 |
| `parcel` | `str`/`None` | Parcel 模式的三元组名称 |
| `prefixes` | `list` | 需要 conda-unpack 延迟修复的前缀记录 |
| `packages` | `list` | 已处理包的元数据（用于 parcel.json） |

## 打包执行流程

`CondaEnv.pack()` 中的打包流程 [F-020]：

```python
# 1. 解析输出路径和格式
output, format = self._output_and_format(output, format)

# 2. Parcel 模式特殊处理
if format == "parcel":
    dest_prefix, arcroot, parcel = self._parcel_output(...)

# 3. 检查输出位置
self._check_output_location(output, force)

# 4. 创建临时文件
fd, temp_path = tempfile.mkstemp()

# 5. 写入归档
with os.fdopen(fd, "wb") as temp_file:
    with archive(...) as arc:
        packer = Packer(prefix, arc, dest_prefix, parcel)
        for f in progressbar(files):
            packer.add(f)      # 逐个添加文件
        packer.finish()        # 收尾

# 6. 原子移动到目标位置
shutil.move(temp_path, output)
```

## Packer.add() 文件处理逻辑

`add(file)` 方法是核心的文件分发逻辑，根据 `file.file_mode` 和文件类型决定处理方式 [F-035]：

```
file.file_mode is None?
├── YES → 是 conda-meta/*.json?
│   ├── YES → rewrite_conda_meta() 清除绝对路径 → add_bytes()
│   └── NO → 直接 archive.add()（无需前缀处理）
│
└── NO →
    ├── 是目录或符号链接? → archive.add()
    ├── file_mode == 'unknown'? →
    │   ├── 读取文件内容
    │   ├── 尝试 UTF-8 解码 → 判断 text/binary
    │   └── 走 text/binary 处理路径
    └── file_mode in ('text','binary')? →
        ├── has_dest 或 (text AND 在 bin/ 目录)?
        │   └── 读取内容 → 替换前缀/重写shebang → add_bytes()
        └── 不需要当前替换 → archive.add() + 记录到 self.prefixes
```

### file_mode=None 的文件

这类文件不需要前缀替换处理，直接添加到归档。conda-meta JSON 文件例外——需要先清除绝对路径字段 [F-034]：

```python
def rewrite_conda_meta(source):
    data = json.load(f)
    for field in ["extracted_package_dir", "package_tarball_full_path"]:
        data[field] = ""
    if "link" in data and data["link"] and "source" in data["link"]:
        data["link"]["source"] = ""
    return json.dumps(data, indent=True, sort_keys=True).encode()
```

### file_mode='text' 或 'binary' 的文件

需要前缀替换，但分为两种情况：

1. **立即替换**（`has_dest=True` 或 bin/ 目录下的文本文件）：
   - `has_dest=True`：用 `dest_prefix` 替换 placeholder，打包后直接可用
   - bin/ 下文本文件：尝试 shebang 重写

2. **延迟替换**（其他情况）：
   - 文件原样添加到归档
   - 将 `(target, placeholder, mode)` 记录到 `self.prefixes`
   - 由 conda-unpack 脚本在部署时替换

### file_mode='unknown' 的文件

非 conda 托管文件（pip 安装/手动放置）的类型不确定 [F-023]：

```python
if is_binary_file(data):  # 尝试 UTF-8 解码，失败则为二进制
    if on_win:
        file_mode = 'binary'  # Windows 仅对 distlib shebang 做二进制替换
else:
    file_mode = 'text'
```

> **跨平台差异**：Unix 上不对 unknown 类型的二进制文件做前缀替换（安全原因，二进制替换要求长度约束），但 Windows 上例外——仅处理 distlib 生成的入口点 exe。

## Shebang 重写

`rewrite_shebang()` 处理 bin/ 目录下脚本的 shebang 行 [F-036]：

1. 用 `SHEBANG_REGEX` 匹配 shebang 行
2. 检查前缀在文件中是否只出现一次（多次出现无法安全清理）
3. 如果可执行文件路径指向前缀内部（如 `/home/user/env/bin/python`）：
   - 提取可执行文件名（如 `python`）
   - 重写为 `#!/usr/bin/env python`
   - 返回修复后的数据和 `fixed=True`
4. 如果 shebang 不指向环境内部，不做修改

```python
new_shebang = "#!/usr/bin/env {}{}".format(
    executable_name, options.decode("utf-8")
)
```

这意味着打包后，脚本的 shebang 会被改为 `#!/usr/bin/env python` 形式，依赖 PATH 中的 python，更加可移植。

## Windows 路径处理

Packer.add() 中对 Windows 扩展长度路径前缀做了特殊处理 [F-035]：

```python
if on_win and placeholder and placeholder.startswith('//?/'):
    placeholder = placeholder[4:]
elif on_win and placeholder.startswith('\\\\?\\'):
    placeholder = placeholder[4:]
```

`\\?\` 是 Windows 的扩展长度路径前缀，需要剥离后再做替换。

## Packer.finish() 收尾

所有文件添加完成后，`finish()` 执行收尾工作 [F-037]：

### Parcel 模式

如果是 Parcel 格式 [F-057]：
1. 添加 `meta/conda_env.sh`（parcel 激活脚本）
2. 从 `self.packages` 收集包信息
3. 生成 `meta/parcel.json`（使用 `_parcel_json_template`）
4. 直接返回（不添加激活脚本和 conda-unpack）

### 标准模式

1. **添加激活/停用脚本** [F-040]：
   - POSIX：`bin/activate`、`bin/deactivate`、`bin/activate.fish`
   - Windows：`Scripts/activate.bat`、`Scripts/deactivate.bat`
   - 如果环境中已有 conda 包且指定了 dest_prefix，则不添加

2. **生成 conda-unpack 脚本**（仅在 `not has_dest` 时）[F-038]：
   - 写入 `bin/conda_unpack_progress.py`（进度条模块的副本）
   - 将 `self.prefixes` 中的前缀记录嵌入脚本
   - 内嵌 `prefixes.py` 的 `update_prefix()` 函数代码
   - POSIX：生成 `bin/conda-unpack`（可执行 Python 脚本）
   - Windows：生成 `Scripts/conda-unpack-script.py` + `Scripts/conda-unpack.exe`（setuptools 的 cli-64.exe 启动器）

3. **SquashFS 特殊处理**：
   - SquashFS 不支持迭代添加，调用 `mksquashfs_from_staging()` 批量压缩

## conda-unpack 脚本

自动生成的 conda-unpack 脚本是部署时修复前缀的关键 [F-038]。它的结构：

```python
#!/usr/bin/env python          # 或 Windows: #!python.exe
from conda_unpack_progress import progressbar

# 内嵌的 prefixes.py 代码（update_prefix 等函数）

_prefix_records = [
    ('bin/conda', '/opt/anaconda1anaconda2anaconda3', 'text'),
    ('lib/python3.10/os.py', '/opt/anaconda1anaconda2anaconda3', 'text'),
    # ... 所有需要前缀修复的文件记录
]

if __name__ == '__main__':
    # 解析参数：--version、--verbose
    # new_prefix = 脚本所在目录的父目录（即环境根目录）
    # 对每条记录调用 update_prefix(new_path, new_prefix, placeholder, mode)
```

注意：Python 可执行文件本身（`bin/python`）被排除在 `_prefix_records` 之外，避免修改正在运行的文件 [F-038]。

## _write_text_file() 辅助方法

Packer 使用 `_write_text_file()` 将内存中的文本内容写入归档 [F-037]：

1. 创建临时文件
2. 写入文本内容
3. 设置可执行权限（如果需要）
4. 添加到归档
5. 删除临时文件

这个方法用于生成 conda-unpack、parcel.json 等动态内容。

## 相关概念

- [CondaEnv 与 File 数据模型](03-conda-env-and-file.md)
- [前缀替换机制](06-prefix-replacement.md)
- [归档格式体系](07-archive-formats.md)
- [conda-unpack 与部署流程](09-conda-unpack.md)
