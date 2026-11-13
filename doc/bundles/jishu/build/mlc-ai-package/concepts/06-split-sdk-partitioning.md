---
type: concept
title: "SDK 分片：一次构建、两个 wheel"
description: 组件图解析、依赖闭包、文件所有权互斥与 build_id 一致性
tags:
  - mlc-ai
  - llvm
  - split
  - wheel
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/split_sdk.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/build_wheels.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/extra-targets/README.md"
---

# SDK 分片：一次构建、两个 wheel

## 问题设定

一份完整 All-target 的 LLVM 静态 SDK 体积远超单个 PyPI 文件上限（逻辑上的约束），而绝大多数消费者只需要本机后端。于是要拆成两个可独立安装、又能协同工作的分发：

| 分发 | 内容 | 体积策略 |
|---|---|---|
| `mlc-llvm-static` | 通用库 + 本机后端 + 头文件 + CMake 导出 + zlib/zstd + ORC 运行时 | 必须独立可用 |
| `mlc-llvm-static-extra-targets` | 其余标准后端库 + 其导出 + profile 元数据 | 只在需要跨目标时安装 |

难点不在"拆"，而在**拆得可证明正确**：

1. 两个 wheel 不能拥有同一个文件（否则卸载一方会损坏另一方）；
2. 两个 wheel 必须来自同一份编译（否则 ABI/配置不一致）；
3. 安装态决定 profile，所以拆分必须与派发逻辑对齐。

## 依赖图从哪里来

LLVM 在构建时生成 `tools/llvm-config/LibraryDependencies.inc`，内容形如：

```c
{ "core", "LLVMCore", true, {"support", ...} },
{ "x86codegen", "LLVMX86CodeGen", true, {"core", "support", ...} },
{ "all", nullptr, true, { ... } },
```

`read_components()` 用一条正解析它（F-073）：

```python
pattern = r'\{ "([^"]+)", (nullptr|"[^"]+"), true, \{([^}]*)\} \}'
```

解析结果是一个字典：`{组件名: {"library": "LLVMxxx" | None, "requires": [...]}}`。两个健全性检查：

- 必须同时存在 `all` 与 `core`，否则抛 `"Unrecognized LLVM component table"`；
- 单元测试用一个"未来格式"字符串验证会抛错（`test_component_table_requires_complete_graph`）。

## 划分算法

`partitions(graph, targets, native)` 分三步（F-074、F-075）：

### 第一步：找出"被后端独占的依赖"

```python
other = {dep for target in targets if target != native
         for dep in graph[target.lower()]["requires"]}
```

这里取的是每个**非本机后端**组件的直接依赖集合。这些依赖只被其他后端需要，因此应随 add-on 走。

### 第二步：把其余库做闭包，得到 base

```python
roots = {name for name, entry in graph.items() if entry["library"] and name not in other}
base_names = closure(graph, roots)
base_libraries = {graph[name]["library"] for name in base_names if graph[name]["library"]}
extra_libraries = {entry["library"] for entry in graph.values() if entry["library"]} - base_libraries
```

`closure()` 是朴素 DFS。含义：**凡是本机后端或通用组件可达的库，都归 base**。这保证 base 单独安装就能完整链接本机目标。

`extra_libraries` 则是"全部库减去 base 库"——精确互补，没有第三类。

### 第三步：为 native 档重建组件表

```python
for name, entry in graph.items():
    if name in ("all", "all-targets"):
        continue
    if name in {target.lower() for target in targets if target != native}:
        continue
    required = closure(graph, [name])
    if all(graph[dep]["library"] not in extra_libraries for dep in required):
        native_graph[name] = entry
native_graph["all-targets"] = {"library": None, "requires": [native.lower()]}
native_graph["all"] = {"library": None, "requires": [name for name in graph["all"]["requires"] if name in native_graph]}
```

这段是为了让 Python 前端的 `ordered_libraries()` 在 native 档不会查到一个已被移走的组件。`all-targets` 被重定义为只依赖本机后端，`all` 被裁剪为只含仍在 native 图中的名字。

## 文件搬运与头文件三分

`split_sdk()` 的顺序（F-083 ~ F-086）：

```text
1. copytree(source → base)                  # 全量复制到 base
2. 删除 base 的 LLVMReferenceExports*.cmake  # 参照导出不进 wheel
3. 遍历 base/lib/*，把 extra_libraries 的 .a/.lib 移动到 extra
4. 移动 LLVMExtraExports*.cmake 到 extra
5. 必须存在 extra/lib/cmake/llvm/LLVMExtraExports.cmake，否则抛错
6. filter_headers(base, extra, native)      # 头文件三分
7. profile_cmake(base, data, base_libs, all_libs)  # 注入 profile 派发
8. 删除 base/bin/，只放 llvm-config.py（Unix 另放 llvm-config）
9. 删除 base/share/mlc-llvm-static/build.json（内部构建图，不进 wheel）
10. 生成 base.json / extra.json / staticlib.json，复制 licenses
```

第 3 步是文件所有权互斥的来源：库被**移动**而不是复制。第 8 步保证上游 `llvm-config` 可执行文件不进任何 wheel——它已在 Reference 分发里，只用于构建期比对。

### 头文件的三份

`filter_headers()` 处理两类文件：`*.def` 且含 `LLVM_<NAME>(<name>)` 行的，以及 `Targets.h`。对每个文件生成三份：

| 位置 | 内容 | 归属 |
|---|---|---|
| `include/llvm/Config/mlc-native/<name>` | 只保留本机后端的行 | base |
| `include/llvm/Config/mlc-all/<name>` | 全量 | extra |
| `include/llvm/Config/<name>` | `__has_include` 派发器 | base |

派发器内容（注释「Profile dispatcher: immutable files are owned by separate wheels」）：

```c
#if !defined(MLC_LLVM_STATIC_NATIVE_ONLY) && __has_include("llvm/Config/mlc-all/Targets.def")
#include "llvm/Config/mlc-all/Targets.def"
#else
#include "llvm/Config/mlc-native/Targets.def"
#endif
```

这样"是否装了 add-on"由预处理器在编译期回答，不需要重新安装或改写文件。`test_header_dispatch_does_not_overwrite_another_wheels_files` 专门断言 base 与 extra 的文件集合不相交。

## 安装态元数据：base.json / extra.json

两个 wheel 各自带一份 profile 记录（F-085）：

```json
{
  "schema_version": 2,
  "sdk_version": "23.1.1",
  "build_id": "<metadata 规范化 JSON 的 SHA-256>",
  "targets": ["X86"],
  "llvm_version": "23.1.1",
  "system": "Linux",
  "files": { "lib/libLLVMCore.a": {"size": 123, "sha256": "..."} },
  "archive_count": 87,
  "flags": {...}, "host_target": "...",
  "profiles": { "native": {...}, "all": {...} }
}
```

`build_id` 的算法值得记住：

```python
identity = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
```

`metadata` 是 `staticlib.json` 中除 `files` 外的键。因此同一个 SDK 的 base 与 extra 必然得到相同 `build_id`；不同编译（哪怕版本号相同）几乎必然不同。这是"版本号相同但内容不同"的防线。

`extra.json` 只含 `targets`、`files`、`archive_count` 等，不含 `profiles`——组件图由 base 提供。

## 文件所有权互斥的三重检查

| 检查点 | 位置 | 失败表现 |
|---|---|---|
| 构建期：zip 成员集合交集为空 | `build_wheels.py`（F-091） | `Wheels have overlapping file ownership` |
| 安装期：base/extra 元数据版本一致 | `profile_cmake()` 与 `Configuration`（F-080、F-101） | CMake `FATAL_ERROR` / `ConfigurationError` |
| 验证期：再次比对 zip 交集并跑四态 | `verify_split_wheels.py`（F-153） | 抛错中止发布 |

三层都保留是有意的：第一层防编码错误，第二层防混装，第三层防"打包后又改了文件"。

## 四个必须验证的安装态

`verify_split_wheels.py` 的序列（F-153）：

```text
① 只装 base                 → profile 必须是 native
② 装 extra                   → profile 必须是 all，且目标集合等于 all-targets 的 requires
③ 显式 MLC_LLVM_STATIC_PROFILE=native（extra 仍在） → 必须能用，且带 NATIVE_ONLY 宏
④ 卸载 extra                 → profile 必须回到 native
```

每一态都会跑一次 `verify_wheel.py`（真正链接 + JIT 执行返回 42）。第 ③ 态是最容易被忽略的：它证明"装了 add-on 也允许显式退回 native"，同时验证头文件派发不会因 extra 存在而强制走 all。

## 分片的边界：什么没被包含

`extra-targets` 只带**代码生成后端**，不带任何目标平台运行时。该包 README 明确：

- 不含 Clang、链接器、目标 sysroot 或其他 LLVM 工具；
- x86_64 wheel 里的 AArch64 后端是"x86_64 代码，生成 AArch64 目标文件"；
- 跨平台链接仍需合适的链接器、sysroot 与目标运行时。

`DEPENDENCIES.md` 进一步说明这些库不提供目标 libc/libm/C++ 运行时、编译器内建、unwinder、sanitizer、启动对象、链接器、OS 头文件、设备库或 sysroot。

## 自检方式

```bash
# 1) 单元测试覆盖划分与派发
pytest packages/mlc-llvm-static/tests/python/test_profiles.py -q

# 2) 真实 wheel 的四态验证（需要已构建的 wheelhouse）
python packages/mlc-llvm-static/scripts/verify_split_wheels.py wheelhouse

# 3) 手工检查两个 wheel 文件集合不相交
python - <<'PY'
import zipfile, pathlib
w = sorted(pathlib.Path("packages/mlc-llvm-static/wheelhouse").glob("*.whl"))
sets = [{n for n in zipfile.ZipFile(p).namelist() if n.startswith("mlc_llvm_static/")} for p in w]
print("overlap:", sets[0] & sets[1])
print("counts:", [len(s) for s in sets])
PY

# 4) 两个 build_id 一致
unzip -p <base.whl> mlc_llvm_static/static/share/mlc-llvm-static/base.json | grep build_id
unzip -p <extra.whl> mlc_llvm_static/static/share/mlc-llvm-static/extra.json | grep build_id
```

## 陷阱

- **`partitions()` 的 `other` 集合是"直接依赖"而非闭包**：这是有意的——闭包会通过通用库把整个图拉平，导致 extra 为空。改这里前先跑 `test_profiles.py` 的 fixture 图。
- **`native_graph` 必须保留 `all-targets`**：Python 前端会查询该伪组件，缺失会导致 `all-targets` 不可用。
- **`build.json` 必须在打包前删除**：它含本机路径与完整组件图，既不该进 wheel，也会泄漏构建环境信息。
- **`extra.json` 不写 `profiles`**：写两份组件图会产生不一致风险，组件图只认 base。
- **不要手动 `pip install` 两个不同版本的 wheel**：CMake/Python 都会拦，但最好在依赖层就用 `==` 阻止（见 [版本单一源](02-single-version-source.md)）。

## 延伸阅读

- profile 如何在三处派发：[profile 选择与派发](07-profile-selection.md)
- 分片后的压缩与体积预算：[Windows COFF 裁剪与 wheel 重压缩](09-windows-coff-and-wheel-recompression.md)
- 官方分片说明：[`extra-targets/README.md`](https://github.com/mlc-ai/package/blob/main/packages/mlc-llvm-static/extra-targets/README.md)
