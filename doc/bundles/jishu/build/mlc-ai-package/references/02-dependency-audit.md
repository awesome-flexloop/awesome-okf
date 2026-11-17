---
type: reference
title: 依赖审计要点
description: mlc-llvm-static 的可选依赖取舍、静态链接闭包与下游要求
tags:
  - mlc-ai
  - llvm
  - dependencies
  - reference
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/DEPENDENCIES.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/prepare_llvm.py"
---

# 依赖审计要点

> 本文是 `packages/mlc-llvm-static/DEPENDENCIES.md` 的结构化摘要。原文含逐项上游链接与 PR 记录，需要引用时请回原文核对。

## 审计对象

| 项 | 值 |
|---|---|
| LLVM tag | `llvmorg-23.1.1` |
| 审计下游 | TVM-FFI `29c01dc8…`、TIRx `3dbcef3c…`、TVM `18ec45ed…` |
| 引入配方 | package PR 115 |

## 依赖矩阵

| 依赖 | LLVM 归属与特性 | 对本 SDK 的影响 | 策略 |
|---|---|---|---|
| zlib 1.3.1 | `LLVMSupport`；Object/DWARF 等读写路径的压缩 | 必需。关闭后无法处理 zlib 压缩节 | 捆绑 PIC 静态库 + 头文件 + notice |
| zstd 1.5.7 | `LLVMSupport`；Zstandard 压缩（含 ELF 调试节） | 必需。关闭后失去 zstd 处理能力 | 捆绑 PIC 静态库 + 头文件 + CMake 导出 + notice；关闭多线程 zstd |
| libxml2 | `LLVMWindowsManifest`；Windows manifest 合并 | 可选。`windows_manifest::isAvailable()` 变 false，合并返回错误；所选 Core/ORC/native 与 TIRx 代码生成路径不依赖 | 保持关闭 |
| libedit（及可能的 curses/terminfo） | `LLVMLineEditor`；交互编辑、补全、历史 | 可选。回退实现仍可读行；本 SDK 场景不含交互工具 | 保持关闭，不捆绑 libedit/ncurses/libtinfo |
| libffi | `LLVMInterpreter`；解释执行时调用任意外部函数 | 可选。关闭后仍可用已知包装器，但不能做通用 libffi 调用；ORC 走原生机器码不受影响 | 保持关闭 |
| Z3 | `LLVMSupport` 的 SMT 接口；Clang 分析 | 可选。LLVM 的 Z3 求解器工厂不可用；TIRx 的 Z3 集成独立于 `LLVM_ENABLE_Z3_SOLVER` | 保持 LLVM 侧 Z3 关闭 |
| libcurl | `LLVMHTTP` 客户端（`LLVMDebuginfod`） | 可选。本地 Object/DWARF 读取不受影响；Windows 另有 WinHTTP | 保持关闭 |
| cpp-httplib | `LLVMHTTP` 服务端 | 可选。JIT/代码生成路径不需要 | 保持关闭 |
| libpfm | `LLVMExegesis`（`tools/llvm-exegesis`） | 仅该被排除工具的性能计数器需要 | 保持关闭 |
| DIA SDK | `LLVMDebugInfoPDB` 的 DIA 实现 | 可选。LLVM 原生 PDB/CodeView/MSF 实现仍在 | 保持关闭 |
| ICU / iconv | `LLVMSupport` 的文本编码转换 | 可选。内置 UTF-8/IBM-1047 转换仍在；其他转换可能失败 | 两者都关闭 |
| 绑定 / 测试 / 文档 / 生成器 | 构建期或排除产物 | 不是下游静态链接需求 | 全部关闭，只保留选定的分发产物 |
| BLAKE3/xxHash/SipHash 等 | 随 LLVM 源码编译进来 | 不需要额外宿主库 | 保持与 LLVM 源码/版本一致并附 notice |

## 静态链接闭包

原文给出的依赖路径：

```text
consumer -> Core / Passes / native / OrcJIT / Object / DebugInfoDWARF
         -> ... -> LLVMSupport -> ZLIB::ZLIB + zstd::libzstd_static
                             -> LLVMDemangle + host system libraries
```

原文实测（Linux aarch64）的 Support 接口：

```cmake
INTERFACE_LINK_LIBRARIES
  "rt;dl;-lpthread;m;ZLIB::ZLIB;zstd::libzstd_static;LLVMDemangle"
```

对应 `llvm-config --link-static --system-libs` 输出 `-lrt -ldl -lpthread -lm -lz -lzstd`。

## 平台剩余依赖

| 宿主 | 仍需提供 |
|---|---|
| Linux x86_64/aarch64 | glibc、所选 C++ 运行时/编译器支持、`rt`/`dl`/pthread/math；`libatomic` 视编译器与架构条件而定；不要捆绑第二份 glibc |
| macOS arm64 | Apple SDK/系统库、libc++、libSystem；部署下限 macOS 14.0；静态 LLVM/zlib/zstd 不意味着静态 libc++ |
| Windows AMD64/ARM64 | Support 链接 `psapi`、`shell32`、`ole32`、`uuid`、`advapi32`、`ws2_32`、`ntdll`，CMake 接口另带 `delayimp` 与延迟加载选项；`LLVMHTTP` 另链 `winhttp`/`crypt32`；归档用 `/MD`，下游需匹配的发布版 CRT |

原文强调：「Capture each platform's actual exported interface when producing metadata; do not infer flags from the target triple.」

## 链接顺序规则

```text
对象文件 → LLVM 归档（依赖顺序）→ 压缩归档 → 平台库
```

原文的警告：

- 字母序归档不适用于普通单遍 ELF 链接；
- 显式 groups 或 whole-archive 语义不同，不要为了绕过顺序问题给普通消费者开 whole-archive；
- `--link-static` 只选择 LLVM 的静态模式；Unix 上如果捆绑归档没被先找到，后面的 `-lz` 仍可能选中共享库；
- CMake 的 `ZLIB::ZLIB` 在常见 `FindZLIB` 实现里是 `UNKNOWN IMPORTED`，要检查其 `location` 而不是相信目标名。

## 已知的配置建议（原文标注为建议，非当前配方变更）

- 当前 CMake 导出会调用 `find_package(ZLIB)` / `find_package(zstd)`，因此可能复用已有的同名目标或找到系统包；
- 后续配置实现应把 SDK 自带的归档路径绑定到前缀相对路径，并在依赖目标冲突时明确失败。

## 额外后端与目标运行时

LLVM 23.1.1 的标准后端集合：

```text
AArch64, AMDGPU, ARM, AVR, BPF, Hexagon, Lanai, LoongArch, Mips,
MSP430, NVPTX, PowerPC, RISCV, Sparc, SPIRV, SystemZ, VE,
WebAssembly, X86, XCore
```

实验性（被排除）：ARC、CSKY、DirectX、M68k、Xtensa。

关键限定（原文）：

- 这些库是"宿主代码，生成目标代码"，**不提供**目标 libc/libm/C++ 运行时、编译器内建、unwinder、sanitizer 运行时、启动对象、链接器、OS 头文件、设备库或 sysroot；
- 生成 AMDGPU/NVPTX 代码不需要把厂商运行时装进 SDK，但使用这些目标的应用可能需要另备厂商工具与设备库；
- 跨编译与跨目标 JIT 执行是不同能力。

## 配置前端需要哪些元数据

原文列出五类（结论）：

1. 每个 profile 的组件名、伪组件展开、归档相对路径、有序传递闭包；单独记录非组件导出（如 `LLVMHTTP`、`LLVMDebuginfod`）；
2. 每个库的外部需求：导入依赖目标、已解析的捆绑归档、平台库名、链接选项组、frameworks、库与选项的区分；
3. `--system-libs` 的保守上游行为（只由 Support 与 WindowsManifest 构造，且不随组件变化）＋更丰富的逐组件闭包；
4. 压缩与可选特性旗标、编译器/CRT/C++ ABI 信息、部署/ABI 下限、RTTI/EH/assertions/PIC/LTO 设置、默认与宿主 triple、可用目标、版本、精确 profile 指纹；
5. 路径重定位与输出格式规则（`--libfiles`/`--libs`/`--ldflags`/includes/system-libs），含 Windows 的引号与空格处理。

## 下游可见性与验证

原文的核心论断：

- 静态链接只对"实际被并入"的归档成员消除共享库依赖，**不会自动隐藏符号**；
- 下游 DSO 应导出自己的 API，把 LLVM/zlib/zstd 保持私有，避免与同进程内另一个 LLVM 发生符号插入；
- ELF 用版本脚本 + `--exclude-libs,ALL`；macOS 用导出符号列表；Windows 用显式 DLL 导出；
- 仅在编译消费者时设 hidden visibility 无法改变已编译归档的可见性；
- Windows ORC 消费者需额外接受 `__jit_debug_descriptor` 与 `__jit_debug_register_code`（`LLVM_ALWAYS_EXPORT` 嵌入了 `/EXPORT` 指令）。

验证探针的覆盖面（原文）：

- IR/优化/bitcode/JIT；
- zlib 与 zstd 往返、畸形流报错、真实 ELF `SHF_COMPRESSED` 节中的 DWARF 编译单元；
- 重定位后每个可用导入归档的位置；
- 导出符号与 Windows 调试器例外；
- Linux ABI 版本上限。

## 保留的验证要求（改动 SDK 时必须继续满足）

1. 引入配置前端后，两种发现路径（CMake / `llvm-config`）都要继续可用，并扩展到更多代表根与 `all`；
2. 在存在竞争的系统 zlib/zstd 与已定义依赖目标的环境下测试，要求"用 SDK 路径或明确冲突报错"；
3. 用严格未定义符号检查链接全部归档，检查依赖、导出符号与 ABI 版本；与普通消费者链接分开；
4. All 档要生成并检查代表性跨目标对象/汇编，含压缩调试信息；不执行外部机器码，也不宣称包含目标 sysroot；
5. 重跑 FFI ORC addon 与 TIRx 的真实发现路径，检查宿主 ORC 运行时初始化/终结、C/C++ 符号导入、压缩外部对象、依赖可见性、与另一个含 LLVM 扩展同进程共存。

## 延伸阅读

- 构建选项落地位置：[LLVM SDK 构建配方](../concepts/05-llvm-sdk-build-recipe.md)
- 验证实现：[验证体系](../concepts/14-verification-strategy.md)
- 前端输出语义：[llvm-config 兼容前端](../concepts/08-llvm-config-frontend.md)
