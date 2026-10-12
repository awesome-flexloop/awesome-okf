---
okf_version: "0.2"
type: Concept
title: "平台分析域深层：Android/ADB/.NET/固件/Apple/Electron/Harmony 的精确版本、环境变量与命令族"
description: "REA 平台类分析域的深层细化 —— Android(JADX)、ADB 设备、.NET Managed、固件、Apple、Electron、HarmonyOS 七域的精确工具版本、环境变量、资源预算、生命周期限制与 CLI 命令族（证据：F-103~F-118）"
tags: [rea, analysis-domains, android, adb, dotnet, firmware, apple, electron, harmonyos, jadx, reverse-engineering]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T14:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: docs-full
    url: "file" # 本地官方文档全量：external/dao/rea/docs/
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# 平台分析域深层：精确版本、环境变量与命令族

> 本文是 [04 支持的分析目标域](04-analysis-domains.md) 八域总览的**深层细化**，但聚焦 docs 深层的**精确工具版本 / 环境变量 / 资源预算 / 生命周期限制 / CLI 命令族**，仅覆盖其中七个平台类域（Native/Ghidra 专项见 [08 专项 Ghidra 支持](08-native-ghidra-specialty.md)，Web 域细节见 [F-077~F-082](../concepts/index.md)）。04 给出"能分析什么跟各域边界"，本页给出"每条边界背后的可核验数字"。

## 一句话定位

REA 的平台类分析域通过**不加载、不执行工制**的原则统一起来——Android(JADX)、.NET Managed、固件（Binwalk/Unblob）、Apple、HarmonyOS 均为静态盘点与投影，ADB 与 Electron 则附加到既有设备/运行时做有界观测；本页把七域的**精确版本、环境变量、内存/时间预算、deadline 与命令族**逐条登记为 F-103~F-118 的可核验断言。

## Android(JADX) 域（F-103 / F-104）

REA 通过 `src/android/` 包装固定 headless JADX 引擎（F-046），CLI 与 MCP 共用统一应用工作流并返回绑定工制的 Evidence。

### 工具版本与环境变量（F-103）

- 五个等价 MCP 方法：`inspect_android_package` / `search_android_classes` / `inspect_android_class` / `inspect_android_method` / `trace_android_references`（F-103）。
- 前置要求：**JDK 17+（含编译器模块 `jdk.compiler`）** 与 **`jadx-headless-mcp 0.7.1`**（F-103）。
- 环境变量：`REA_JADX_MCP_JAR` 指向引擎 JAR（必填），可选 `JAVA_HOME` 选择既有 JDK（F-103）。REA 不安装 Java、Android SDK、JADX、设备服务或模拟器（源文档 android-analysis.md:16-18）。

### 资源与执行预算（F-104）

- 整次操作 deadline **120 秒**（队列排头起算），其中上游反编译限制 **90 秒**（F-104）。
- 解码后的清单与方法文本 **1 MiB** 上游字节预算，超出即报告截断（F-104）。
- 类名页面索引切片最多 **4096** 个名称（不改变完整、区分大小写的搜索契约）（F-104）。
- 协议帧上限 **8 MiB**、合并 stdout/stderr 上限 **32 MiB**/次，超出以诊断失败而非返回不完整清单（F-104）。
- 会话 **60 秒** 不活动即清理；APK/引擎摘要与 JVM 配置在复用前检查，变更即替换会话（F-104）。

## ADB 设备域（F-105 / F-106）

REA 通过调用方的 `adb` 二进制检查已连接 Android 设备、读取设备状态、传输文件与包；不启动/管理模拟器，不安装 platform tools（源文档 adb-device-analysis.md:4-7）。

### 工具版本与环境变量（F-105）

- 六个 ADB 设备操作：`inspect_adb_client` / `list_adb_devices` / `inspect_adb_device` / `inspect_adb_display` / `list_adb_features` / `list_adb_services`（F-105）。
- 支持 adb **34.0.5**；环境变量 `REA_ADB_PATH` 指定二进制绝对路径，缺省自 `PATH` 解析（F-105）。

### CLI 命令族（F-106）

- `rea inspect-adb-client`（运行 `adb version`，只探测二进制不接触 server）、`rea list-adb-devices`、`rea inspect-adb-device <serial>`、`rea pull-adb-package --output-directory`、`rea capture-adb-screen`、`rea collect-adb-bugreport`、`rea install-adb-package --replace`（F-106）。
- 每个调用组合**固定 adb 参数向量**，调用值仅作位置参数被引用，无工具接受任意 shell 命令行（F-106；源文档 adb-device-analysis.md:6-7）。

## .NET Managed 域（F-107 ~ F-109）

REA 不加载/不执行代码地检查 .NET PE/CLI 工制：识别程序集、检查元数据与 CIL、跨 build 比较成员、把声明原生调用关联到 native 证据（源文档 managed-code-analysis.md:3-5）。

### 七个 MCP 工具（F-107）

- MCP：`inspect_managed_artifact` / `inspect_managed_members` / `inspect_managed_native_boundaries` / `compare_managed_members` / `verify_managed_native_boundaries` / `import_managed_reconstruction` / `project_managed_application_graph`（F-107）。
- CLI 用连字符同名（下划线换连字符并加 `rea` 前缀），如 `rea inspect-managed-artifact`（F-107）。

### 资源预算与摘要（F-108 / F-109）

- 静态提供者承认最大 **128 MiB** 常规输入；元数据 / CIL 解码 / 投影检查各 **64 MiB** 表示预算（F-108）。
- `il_sha256` 基于精确 `il_size` 原始 CIL 字节（tiny/fat 方法头之后）；`normalized_il_sha256` 基于 UTF-8 `JSON.stringify` 的 `[opcode, operand_kind, operand]` 指令数组（F-108）。
- 解码 `nop; ret` 序列化为 `[["nop","none",null],["ret","none",null]]`，摘要为 `5e5fad7741cb44bca3a4f045546b7449990da343f612f5f34c0ca30e9eee0636`（F-109）。

## 固件域（F-110 / F-111）

REA 接受 **Binwalk 3.1.x** 做分区检查、**Unblob 26.6.x** 做显式提取；解析器对 Binwalk 3.1.0 与 Unblob 26.6.4 验证；首个固件里程碑在 Linux x64 验证（F-110；源文档 firmware-analysis.md:3-7）。

### 环境变量与命令行（F-110）

- 环境变量：`REA_BINWALK_COMMAND` / `REA_UNBLOB_COMMAND` 指定工具可执行文件绝对路径（F-110）。
- 检查与提取都需 util-linux `prlimit`（正常路径 `/usr/bin/prlimit`），可用 `REA_FIRMWARE_PRLIMIT_COMMAND` 覆盖（F-110）。

### CLI 与资源限制（F-111）

- CLI：`rea inspect-firmware-regions <path>`、`rea extract-firmware <in> <out>`（支持 `--offset` / `--length` / `--max-depth`）（F-111）。
- 输入上限 **128 MiB**（复制并哈希进私有工作区）、deadline **120 秒**、继承地址空间 **1 GiB**/进程、默认临时预算 **256 MiB** / **10,000 条目**、每命令合并 stdout+stderr **8 MiB**（F-111）。

## Apple 域（F-112 / F-113）

REA 把一或多个认证的 `inventory_artifact` Evidence 投影为 Apple 应用清单（IPA / macOS `.app` / ZIP / DMG），执行自由、不解析 plist/CMS 语义（源文档 apple-application-analysis.md:3-8）。

### 投影与 dylib 解析（F-112）

- MCP `project_apple_application_graph` 接受 `inventory_evidence`（`inventory_artifact` Evidence 数组）（F-112）。
- `trace_dylib_resolution` 支持 `--root`（如 `Contents/MacOS/MyApp`）与 `--architecture`（如 `arm64`）（F-112）。
- `bundles` 报告每 bundle 的 `parent_path` / `layout` / `info_plist_path` / `executable_candidates` / `signing_paths`（F-112）。

### 桥接限制与路径角色（F-113）

- 桥接候选序列化数组限制 **2 MiB** UTF-8 JSON，超出保留确定性前缀（F-113）。
- 路径角色 `role_basis` 值为 `"path-convention"`（F-113）。
- `verify:macos-bundle` 针对 `otool -l` 的解析器验证（F-113）。

## Electron 域（F-114 / F-115）

REA 附加到 Electron/Chromium CDP 端点，只检查既有 `file://` 渲染页面，不执行 JS、不调用 Electron API；接受仅字面端口 loopback HTTP 端点（源文档 electron-observation.md:3）。

### 工具与参数（F-114）

- `list_electron_targets` 返回单个内联数组（该端点服务的全部合格 target）；`inspect_electron_page` 需 `include_script_sources` 才返回脚本源（F-114）。
- CLI：`rea list-electron-targets` 接受 `http://127.0.0.1:9223` 端点、`rea inspect-electron-page` 支持 `--observation-ms` / `--include-script-sources`（F-114）。
- Electron **44.7.0** 已验证预加载描述符（F-114）。

### 场景捕获与超时（F-115）

- `capture-electron-scenario` CLI 接受 JSON 请求文件（`rea capture-electron-scenario scenario.json --json`）（F-115）。
- Electron 主动启动超时 **60 秒**（含启动 deadline）（F-115）。

## HarmonyOS 域（F-116 ~ F-118）

REA 经 `src/artifacts/` 共享 ZIP 工制读取器盘点 HarmonyOS 应用包，把认证清单投影为不执行的程序图；HarmonyOS roadmap(#1431) 第一期增量（F-054；源文档 harmony-analysis.md:3-7）。

### 根格式识别（F-116）

- 三种根格式：`.hap`（可安装应用模块）/ `.hsp`（运行时共享包）/ `.app`（分发 App Pack）（F-116）。
- `.har` 因也命名 HTTP Archive JSON 而故意不按后缀分类，须验证 ZIP 字节并显式 defer（F-116）。

### CLI、MCP 与打包模型提示（F-117）

- CLI `rea inspect-artifact /path/Example.hap --format json`；MCP `project_harmony_application_graph` 接受 `inventory_evidence`（F-117）。
- 打包模型提示仅从 `module.json` 条目声明 Stage、仅从 `config.json` 声明 FA，否则 `unknown`；FA 资源在 `assets/<module>/resources/`、Stage 资源在 `resources/`（F-117）。

### 运行时族提示与验证（F-118）

- 运行时族提示（`ark` / `native` / `javascript`）来自路径与格式；桥接假设为路径级 N-API（字节码与 `libs/<abi>` 原生库间）（F-118）。
- `npm run fixtures:harmony` 下载 SHA-256 固定的 **1.0.1** HAP；验证用 `REA_HARMONY_TEST_HAP` 指向 `_reference/harmony-integration/entry-default-unsigned.hap`（F-118）。

## 阅读下一篇

- [10 · 工程与管理工作流](10-engineering-workflow.md)——从平台域的具体命令，上升到安装契约、测试/CI、发布与迁移的工程侧工作流。