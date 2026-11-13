---
type: concept
title: Windows COFF 裁剪与 wheel 重压缩
description: 为什么不能用 --strip-unneeded、COMDAT 保护清单、7-Zip 重压缩与 100 MB 预算
tags:
  - mlc-ai
  - windows
  - coff
  - compression
  - wheel-size
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/compact_coff.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/compress_wheel.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/build_wheels.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/packaging_tools.py"
---

# Windows COFF 裁剪与 wheel 重压缩

## 体积是硬门禁

`build_wheels.py` 在打包末尾做两条断言（F-090、F-091）：

```python
for wheel in wheels:
    if wheel.stat().st_size >= 100_000_000:
        raise RuntimeError(f"{wheel.name}: {wheel.stat().st_size:,} bytes exceeds the SDK's 100 MB wheel budget")
paths = []
for wheel in wheels:
    with zipfile.ZipFile(wheel) as archive:
        paths.append({name for name in archive.namelist() if name.startswith("mlc_llvm_static/")})
if paths[0] & paths[1]:
    raise RuntimeError(f"Wheels have overlapping file ownership: {sorted(paths[0] & paths[1])}")
```

100,000,000 字节（十进制 100 MB）不是 PyPI 的硬限制，而是本仓库自设的预算。理由在 Windows 那一段最明显：`clang-cl` 产出的对象比 MSVC 少约一半的 section 与 symbol，直接决定能否压进预算。

## Windows 为什么需要额外裁剪

LLVM 在 Windows 上产出的 `.lib` 归档里有大量：

- 只为调试或局部使用、没有任何重定位引用的**局部标签**；
- 声明了但从未被引用的**未定义外部符号**。

它们对链接结果没有贡献，但占体积。理想做法是"只删这两类"，而通用工具做不到。

### 为什么 `--strip-unneeded` 不行

`compact_coff.py` 的注释直接回答了：

> Generic `--strip-unneeded` removes unreferenced COMDAT section definitions required by MSVC.

具体机制：MSVC 链接器需要 **COMDAT 键符号**来确定哪些节可以合并、哪些必须保留。`--strip-unneeded` 会把"看起来没被引用"的 COMDAT 定义一并删除，结果是链接期才报错（甚至在某些配置下静默出错）。

## 可删集合的精确定义

`coff_contents()` 遍历归档成员，把符号分成三类（F-095）：

```python
if not auxiliaries and storage == 3 and number > 0:
    local_labels.append((number, name))          # STATIC + 有节号 = 局部标签
elif not auxiliaries and storage == 2 and number == 0 and value == 0:
    candidates.add(name)                          # EXTERNAL + 节 0 + 值 0 = 未定义声明
else:
    protected.add(name)                           # 其余一律保护
```

然后用 `removable=True` 时计算最终可删集合：

```python
return {name for name in candidates - protected
        if name and not any(byte in b' \t\r\n\v\f#,:="' for byte in name)}
```

三重过滤：

1. 从候选中减去保护集；
2. 剔除空名；
3. 剔除含空白、`#`、`,`、`:`、`=`、`"` 的名字——这些出现在 `.drectve` 指令或特殊符号里，删了会破坏链接指令。

### 保护集包含什么

| 保护对象 | 原因 |
|---|---|
| COMDAT 键符号（含 PCH 中 STATIC 存储类的键） | MSVC 需要它来决定节合并 |
| `.drectve` 中的 `/INCLUDE`、`/EXPORT`、`/ALTERNATENAME` 引用 | 这些指令没有普通重定位，删符号会静默失效 |
| 任何重定位目标 | 链接期必需 |
| weak 引用（storage 105） | 同上 |
| 公共定义（section 0 且 value≠0 的 COMMON、storage 3 且 number<0 的 `@feat.00` 等） | 是导出面的一部分 |

还有一个"拒答"分支：遇到 `.gfids`、`.giats`、`.gljmp`、`.gehcont` 这四类控制流保护表时直接抛错（F-096）——它们的表项含"正常重定位之外"的符号索引，重写会破坏语义，作者选择不处理而非猜。

## 变换前后的结构比对

删除之后必须证明"没改语义"（F-097）。`compact_coff()` 对每个归档做前后解析并逐项比对：

```python
contents = coff_contents(archive)          # 变换前：[(sections, definitions, comdats), ...]
names = coff_contents(archive, removable=True)
subprocess.run([executable, f"--strip-symbols={symbols_file}", str(archive)], check=True)
actual = coff_contents(archive)            # 变换后
if actual != contents:
    ...  # 打印首个差异后抛错
```

`contents` 的每一项是三部分：

| 部分 | 内容 |
|---|---|
| sections | `(节名, characteristics, raw_size, sha256(载荷))`，跳过 `.debug*` |
| definitions | 公共定义 `(name, value, section_id, symbol_type)` |
| comdats | `(name, 节索引, 辅助记录字节)` |

几处工程细节：

- **BSS 的载荷视为零**：`IMAGE_SCN_CNT_UNINITIALIZED_DATA` 只比对大小与标志，因为 objcopy 可能给它一个文件偏移而输入是空指针。
- **关联 COMDAT 的节号要重映射**：删除节后原索引失效，代码把辅助记录里的 `Associated` 字段改写成新索引（F-095 相关）。
- **bigobj 每条辅助记录 20 字节，普通 COFF 18 字节**：读取时分别处理，写入节定义字段时位置相同。

比对通过后更新元数据：

```python
metadata["files"][archive.relative_to(prefix).as_posix()] = {
    "sha256": sha256(archive), "size": archive.stat().st_size,
}
metadata["packaging"] = {"coff": "unreferenced-symbols-preserve-comdat-v1", "llvm_objcopy": version}
```

`packaging` 字段进入 `build_id` 的计算范围（`split_sdk` 用除 `files` 外的 metadata 做哈希），因此**压缩过的 SDK 与未压缩的 SDK 不会被误认为同一次构建**（F-098）。

## Linux/macOS 为什么不裁剪

该包 README 明确：「Linux/macOS archives retain their original symbols and sections」。

原因有两条：

1. ELF/Mach-O 的归档工具链（`ar`/`ld`）对未引用符号的处理本就宽容，体积压力主要来自 Windows 的 COFF 结构冗余；
2. `--gc-sections` / `-dead_strip` 在链接期已经能丢弃未用代码，无需在打包期冒险改归档。

## wheel 重压缩

### 为什么需要重压缩

`python -m wheel tags` 重打标签时**会用默认参数重写整个 zip**，把之前的高压缩比丢掉。因此顺序必须是"先 retag、后重压缩"，`compress_wheel()` 的注释写明了这一点（F-093）：

> Retagging with `wheel tags` recompresses the archive with default settings, so apply this after all metadata/tag changes.

### 7-Zip 参数

```python
subprocess.run([executable, "a", "-tzip", "-mm=Deflate", "-mx=9", "-mfb=258",
                "-mpass=3", "-mmt=2", "-scsUTF-8", "-bd", "-bb0", "-y",
                str(output), "@" + str(listing)], cwd=payload, check=True, timeout=1200)
```

| 参数 | 含义 |
|---|---|
| `-mm=Deflate` | 只用标准 DEFLATE（wheel 规范只允许 STORE/DEFLATE） |
| `-mx=9` | 最高压缩级别 |
| `-mfb=258` | 最大 fast-byte 数（DEFLATE 上限） |
| `-mpass=3` | 多遍搜索更优匹配 |
| `-mmt=2` | 双线程 |
| `-scsUTF-8` | 文件名按 UTF-8 |
| `-bd` / `-bb0` | 关闭进度输出 |

### 完整性校验

重压缩后逐项比对（F-092）：

```python
if set(target.namelist()) != set(source.namelist()):
    raise RuntimeError("7-Zip changed the wheel member list")
for member in target.infolist():
    original = source.getinfo(member.filename)
    if member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise RuntimeError("Only standard STORE/DEFLATE wheel compression is allowed")
    if (member.CRC, member.file_size) != (original.CRC, original.file_size):
        raise RuntimeError(f"7-Zip changed wheel payload: {member.filename}")
    member.external_attr = original.external_attr
    member.internal_attr = original.internal_attr
    member.create_system = original.create_system
    member.date_time = original.date_time
    member.comment = original.comment
target.comment = source.comment
```

关键逻辑：**RECORD 哈希的是解压后的字节**，所以只要每个成员的 CRC 与 `file_size` 不变，RECORD 就依然有效。但权限位、时间戳、注释属于 zip 元数据，RECORD 不管它们，必须显式恢复，否则会出现"解压后权限丢失"或"每次构建的 wheel 哈希不同"。

`target.comment = source.comment` 这行看似赋值给同一字段，实际是借 Python 的 setter 触发中央目录重写——注释里写明了这个"副作用式"用法。

### 无 7-Zip 时的退化路径

```python
with zipfile.ZipFile(wheel) as source, zipfile.ZipFile(
    temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9,
) as destination:
    destination.comment = source.comment
    for member in source.infolist():
        destination.writestr(member, source.read(member),
                             compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
```

注意这是**退化**而不是等价：Python 的 zlib 默认策略在大型二进制上通常不如 7-Zip 的 3-pass 搜索。CI 的 Linux/macOS 会下载钉扎的 7-Zip（F-054），Windows 用本机安装的 7-Zip。

## 并行与顺序

```python
with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(lambda wheel: compress_wheel(wheel, seven_zip=executable), wheels))
```

两个 wheel 并行压缩。之所以能并行，是因为压缩不修改解压内容，只重写归档；两个 wheel 的文件所有权互斥，所以不会读写同一文件。

## 自检方式

```bash
# 1) COFF 压缩只影响 Windows
grep -n 'system.*Windows' packages/mlc-llvm-static/scripts/compact_coff.py

# 2) 单元测试覆盖结构比对
pytest packages/mlc-llvm-static/tests/python/test_coff.py \
       packages/mlc-llvm-static/tests/python/test_compression.py -q

# 3) 体积与文件所有权断言仍在
grep -n "100_000_000\|overlapping file ownership" packages/mlc-llvm-static/scripts/build_wheels.py

# 4) 重压缩后 RECORD 仍然有效（安装不会报错）
python -m pip install --force-reinstall dist/*.whl
python -c "import mlc_llvm_static, hashlib; print(len(mlc_llvm_static.metadata()['files']))"
```

## 陷阱

- **不要在 retag 之前压缩**：`wheel tags` 会覆盖压缩结果。
- **不要把 7-Zip 产物直接换名**：必须先校验成员集合/CRC/属性，否则可能得到"能解压但 RECORD 不匹配"的坏 wheel。
- **不要给 Linux/macOS 也跑 COFF 裁剪**：`compact_coff()` 首行就按 `system != "Windows"` 直接返回。
- **不要无脑加 `--strip-symbols` 的名字**：任何进入 `.drectve` 的名字都可能破坏链接指令。
- **`-mfb=258` / `-mpass=3` 会增加压缩时间**：两个 wheel 并行已是上限，再高并发只会争 CPU。

## 延伸阅读

- 分片后为何还要压缩：[SDK 分片](06-split-sdk-partitioning.md)
- 打包工具的钉扎：[上游源码钉扎与供应链校验](04-source-pinning-and-provenance.md)
- 验证如何检查安装完整性：[验证体系](14-verification-strategy.md)
