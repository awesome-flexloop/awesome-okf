---
type: Concept
title: "Native 域与专项 Ghidra 深度适配"
description: "REA 的 Native 调查能力与专项 Ghidra 支持 —— Mach-O 静态检查与运行时观测、离线二进制诊断、raw-binary 架构映射，以及 DOS/MIPS/PSP/.NET NativeAOT/Windows P0 专项 Ghidra 适配，外加 IDA/JEB/Apktool 等其他反编译 Provider（事实层 F-083~F-102）"
tags: [rea, native, ghidra, macho, binary-diagnostics, dos, mips, psp, nativeaot, ida, jeb, apktool]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T14:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: docs-full
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs"
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# Native 域与专项 Ghidra 深度适配

> 事实层（What / How）。本文只陈述从 `docs/` 深层登记的可核验事实（F-083~F-102）：Native 调查能力、离线二进制诊断、raw-binary 架构映射，以及专为 DOS/MIPS/PSP/.NET NativeAOT/Windows P0 定制的 Ghidra 适配，外加 IDA/JEB/Apktool 等其他反编译 Provider。工具与 Provider 的契约层机制见 [02 · MCP 契约层](02-mcp-contract.md)，适配器见 [03 · Provider 适配器](03-provider-adapters.md)。

## 一句话定位

REA 的 Native 能力层把「静态资源 + native 元数据 + 代码事实」结合，同时把运行时观测单独隔离；每条结果报告其 evidence、目标身份、覆盖率与 unknowns（F-043）。其中 Ghidra 是扫描最深的 Provider，REA 针对不同 loader 语言与 CPU 形态提供了专项适配（DOS/MIPS/PSP/NativeAOT），形成一条「通用二进制诊断 → 专项 Ghidra → 其他反编译器」的能力纵深。

## Native 调查：静态检查与运行时观测

### Mach-O 静态检查

`inspect_macho` 的 `selected_architecture` 报告所选 lipo slice 的 `container_file_offset` 与容器相对的各架构 `file_offset`（F-083）。`trace_dylib_resolution` 在 TypeScript 中解析 Mach-O load commands，为应用 bundle 内每个可执行（或目录内的单个 Mach-O）跟踪 dyld 的路径展开，报告每条 `@rpath`、`@loader_path`、`@executable_path` 候选及其结果（F-083）。

### asset catalog 与 keyed archive

`inspect_asset_catalog` 通过 macOS `assetutil --info` 读取编译后的 `Assets.car` 元数据（F-084）。`inspect_keyed_archive` 读取 XML 或 binary Foundation keyed archives（不实例化类），限制为 64 MiB 输入、200,000 objects/references、128 嵌套层级（F-084）。

### UI 动作追踪与运行时调用观测

`trace_native_ui_action` 接受 authored selector/object ID、native symbol 或精确 function address 作为锚点（F-085）。`observe_native_calls` 通过 LLDB 启动 Mach-O 并记录 breakpoints，限制 8 MiB retained event JSON、65,536 caller frames（F-085）。

## 离线二进制诊断：inspect_binary_layout

`inspect_binary_layout` 在无活动 Hopper/Ghidra/IDA 目标时回答问题「这个显式文件里是什么」，覆盖 section/segment 布局、原始符号/重定位、静态链接名与缓解指示（F-086）。它依赖用户自备的 pwntools **4.15.0**、pyelftools **0.33**、Unicorn **2.1.2**，可用环境变量 `REA_PWNTOOLS_PYTHON` 指定 Python 可执行文件；限制 32 MiB 输入、64 MiB 回复、1 MiB 组合诊断、30 秒命令期限，Python 进程限制 3 GiB 虚拟地址空间/30 CPU 秒/64 MiB 文件输出（F-086）。

## raw-binary：无头可执行文件的架构映射

raw-binary 模式经 `--target-format raw-binary` + `--architecture` 选择，映射表固定（F-087）：

| architecture | language_id | compiler_spec_id | 对齐 |
|---|---|---|---|
| `x86` | `x86:LE:32:default` | `gcc` | byte |
| `x86_64` | `x86:LE:64:default` | `gcc` | byte |
| `arm` | `ARM:LE:32:v7` | `default` | 4-byte |
| `arm64` | `AARCH64:LE:64:v8A` | `default` | 4-byte |

ARM/AArch64 须 4-byte 对齐、x86 可 byte 对齐；Ghidra 用 `BinaryLoader` 导入私有快照并在 entry 处 seed 一个 `entry` 函数（F-087）。Ghidra 的 x86 languages 没有名为 `default` 的 compiler spec。

## 专项 Ghidra 总览

Ghidra Provider 支持 Linux x64/arm64 与 macOS x64/arm64；实验性 Windows x64 P0 为**只读**、无 database mutation authority（F-088）。要求 Ghidra **12.1.x** 与 64-bit full JDK；`analyzeHeadless` import 产生 exactly one Program（F-088）。

地址格式为 `0x` 小写十六进制或 `<percent-encoded-space>:0x<hex>`；字符串搜索仅覆盖 Ghidra-defined string `Data`；p-code value flow 限制 3,000 operations、64 inputs/operation、12,000 def-use edges（F-089）。

## 专项一：DOS

DOS 支持 MZ executables 与显式 COM images（验证用 Ghidra 12.1.4 + JDK 21）——MZ 用 `MzLoader` + `x86:LE:16:Real Mode`；COM 用 `BinaryLoader`，文件 offset 0 映射到 `1000:0100`（linear `0x10100`），COM 大小限制 1..65280 bytes（F-090）。

## 专项二：MIPS

MIPS 支持 ELF32 `ET_EXEC`/`ET_REL`（little/big endian），要求 explicit o32 与 `EF_MIPS_ARCH_32R2`，拒绝 `EF_MIPS_FP64`/`EF_MIPS_NAN2008`；MIPS16 共享库支持 ELF32 `ET_DYN`（F-091）。soft-float 原型策略键值 `mips_soft_float_storage: o32-soft-float-prototype-v1`；可重定位对象轨道键值 `mips_support_lane: elf32-rel-o32-arch32r2-standard-v1`（F-092）。

## 专项三：PSP

PSP 支持 Linux x64、little-endian ELF32 `ET_EXEC`/`EM_MIPS`，PSPSDK `e_flags=0x10a23001`（MIPS II, Allegrex, EABI32, NOREORDER）。验证环境 PSPDEV v20261001（GNU readelf 2.44）+ Ghidra 12.1.3 + extension v21.4 + JDK 21；Loader `PspElfLoader`、language `Allegrex:LE:32:default`（F-093）。

## 专项四：.NET NativeAOT

NativeAOT 支持 x64 PE32+ 与 .NET 8 RTR 9.1 metadata，基于 Washi1337/ghidra-nativeaot commit `effeb734fc570c32650f88b159608979dc7b423e`，并交叉核对 .NET MethodTable.h commit `a3b2d40328be0be3f8dd43f0e5cc925b8827b044`（F-094）。ghidra-nativeaot 限制 128 MiB captured PE bytes、64 MiB-equivalent parser work、64 MiB overlay/index Buffers、4 MiB serialized JSON；Windows P0 无 database mutation authority（F-095）。

## 专项五：Windows P0（只读）

Windows P0 支持 Windows 10+ x64、本地 NTFS target 与 temporary volumes；Ghidra 12.1.x（验证 12.1.4）+ 64-bit full JDK 21+，提供 **25** 个只读 Ghidra inventory/memory/function-analysis 操作（F-096）。MCP `timeoutMs` 默认 300000；验证命令 `npm run verify:ghidra:windows`（F-096）。

## 其他反编译 Provider：IDA / JEB / Apktool

### IDA

基于 mrexodia/ida-pro-mcp，支持 upstream **1.4.0 legacy tools**（`get_metadata`/`list_functions`/`decompile_function`）；环境变量 `REA_IDA_MCP_CONFIG` 指定配置、`REA_ANALYSIS_PROVIDER=ida` 选择 provider；支持 attached（GUI）与 headless（`--stdio`）模式（F-097）。MCP `timeoutMs` 默认 300000（5 分钟）；验证环境 IDA 9.3（Windows）+ IDA Professional 9.1 build 9.1.250226（macOS arm64）；验证命令 `npm run verify:ida -- --target <path> --procedure main`（F-098）。

### JEB

默认 endpoint `http://127.0.0.1:8425/mcp`；验证版本 JEB 5.48.0（Linux x64）+ `jeb-mcp-server` 1.3.0；headless JEB 5.48 `-c` 模式不直接接受 `--mcp`；提供 4 个 MCP 工具/CLI 命令（`inspect_jeb_client`/`open_jeb_project`/`list_jeb_units`/`decompile_jeb_item`）（F-099）。`list_units` 分页上限 100（F-100）。

### Apktool

验证版本 **2.7.0**；环境变量 `REA_APKTOOL_COMMAND` 指定启动器；readiness 检查 `rea inspect-apktool-client`；Smali 被跳过（`apktool d --no-src`）（F-101）。解码限制 600 秒 deadline、4 MiB output capture、Manifest 读取 512 KiB、Strings XML 8 MiB、`decoded_file_count` 上限 100,000；验证命令 `npm run verify:apktool -- --apk PATH`（F-102）。

## 阅读下一篇

- [09 · 平台域深层适配](09-platform-domains-deep.md)——Android（JADX）/ADB/.NET Managed/固件/Apple 桥梁/Electron/HarmonyOS 等平台级深度适配（F-103~F-118）
