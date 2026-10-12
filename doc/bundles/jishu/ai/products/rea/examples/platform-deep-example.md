---
okf_version: "0.2"
type: Example
title: "REA：平台深层分析示例"
description: "对 Apple(macOS/iOS)、Electron、HarmonyOS、Android、固件五类平台目标的代表性 CLI 深层分析命令与资源限制——每条命令附事实编号 F-103~F-118，并给出对应资源限制/环境变量"
tags: [rea, example, platform, apple, electron, harmonyos, android, firmware, cli]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T15:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: docs-full
    url: "file" # 本地官方文档全量：external/dao/rea/docs/（platform 域文档深层）
---

# 示例：平台深层分析示例

> ⚠️ **可复现性说明**：本示例的**输入（命令）/步骤明确**，理论上可独立复现。命令来自源码与官方文档核对（references/facts.md），**未在本机实际运行**。执行时以官方文档、`rea <command> --help`、`rea doctor` 当前输出为准，并确认对应分析工具（Ghidra/JADX/Binwalk/Unblob/Playwright 等）已就绪。

## 目标

用 REA 的代表性 CLI 命令对 Apple（macOS/iOS）、Electron、HarmonyOS、Android、固件五类平台目标做深层分析，掌握每条命令的调用形态、对应环境变量与资源/生命周期限制。命令均来自 facts 清单 M 章（F-103~F-118），禁止超出清单臆造。

## 输入

- 一台满足 Node 支持范围的机器（`^22.19.0 || ^24.11.0 || >=26.0.0`，F-007），npm 存量 `npm@11.16.0`（F-008）。
- 相应目标工件：macOS `.app` / IPA（Apple）、已启动的 Electron/Chromium CDP 端点（Electron）、`.hap`/`.hsp`/`.app` 包（HarmonyOS）、`.apk` 与对应 JADX 引擎（Android）、原始固件二进制（固件）。
- 各域外部分析工具需先就绪（JADX/Binwalk/Unblob/Playwright 等），见 [provider-setup.md](provider-setup.md)。

## 平台一：Apple（macOS/iOS）应用清单投影与 dylib 解析

Apple 应用清单投影将认证的 `inventory_artifact` Evidence 无损投影为应用清单，不做执行；`trace_dylib_resolution` 用 TypeScript 解析 Mach-O/FAT 头来回答每个 dylib 装载命令实际命中的文件，不执行任何代码、也不需要 Apple 工具（F-112）。

CLI 命令（F-112，命令来源 `apple-application-analysis.md`）：

```bash
# 投影应用清单图（以 inventory_evidence 作为输入）
rea project-apple-application-graph '{"inventory_evidence":[<inventory_artifact Evidence>]}'

# 逐可执行程序解析 dylib 装载，指定 process root 与架构
rea trace-dylib-resolution MyApp.app --json
rea trace-dylib-resolution MyApp.app --root Contents/MacOS/MyApp --architecture arm64 --json
```

- MCP 工具 `project_apple_application_graph` 接受 `inventory_evidence`（`inventory_artifact` Evidence 数组）（F-112）。
- `trace_dylib_resolution` 支持 `--root`（如 `Contents/MacOS/MyApp`）与 `--architecture`（如 `arm64`）；`bundles` 报告每 bundle 的 `parent_path`/`layout`/`info_plist_path`/`executable_candidates`/`signing_paths`（F-112）。
- 到运行时族的判定：框架提示只匹配完整路径段（`React.framework`/`Flutter.framework` 等），子串（`Preact.framework`）不构成家族提示。

**资源/验证限制（F-113）**

- 桥接候选序列化数组限制 2 MiB UTF-8 JSON，超出保留确定性前缀并报 `bridge_candidate_coverage` 计数（F-113）。
- 路径角色 `role_basis` 值为 `"path-convention"`（F-113）。
- `verify:macos-bundle` 针对 `otool -l` 的解析器验证（F-113）。

## 平台二：Electron 文件页观测

REA 附加到 Electron/Chromium CDP 端点，观测既有 `file://` 渲染页面，不执行 JavaScript、不调用 Electron API；端点只接受 literal-port 的 loopback HTTP 端点（F-114、来源 `electron-observation.md`）。

```bash
# 列出端点提供的全部可观测 target（单个内联数组返回）
rea list-electron-targets http://127.0.0.1:9223 --json

# 检查指定 target 页面，可指定观测时长
rea inspect-electron-page http://127.0.0.1:9223 TARGET_ID \
  --observation-ms 100 --json

# 默认排除脚本源；显式开启才返回脚本源
rea inspect-electron-page http://127.0.0.1:9223 TARGET_ID \
  --include-script-sources \
  --json

# 主动 Electron 场景（传入 JSON 请求文件，走 Playwright 官方 API 启动并接管生命周期）
rea capture-electron-scenario scenario.json --json
```

- `list_electron_targets` 返回由端点提供的每个合格 target 的单个内联数组（F-114）。
- `inspect_electron_page` 仅当设置 `include_script_sources` 才返回脚本源（F-114）。
- CLI `rea list-electron-targets` 接受 `http://127.0.0.1:9223` 端点、`rea inspect-electron-page` 支持 `--observation-ms`/`--include-script-sources`（F-114）。
- Electron 44.7.0 已验证的可选内部预加载描述符（F-114）。

**资源/生命周期限制（F-114/F-115）**

- `capture-electron-scenario` CLI 接受 JSON 请求文件（F-115）。
- Electron 启动超时 60 秒；动作等待完成或请求取消（F-115）。
- 这些操作是被动逆向而非通用浏览器自动化：不保留 DOM 值、不执行渲染代码、不导航/点击/调用 IPC/结束目标（出处同上）。

## 平台三：HarmonyOS 静态包清单盘点

REA 通过 `src/artifacts/` 共享加固 ZIP 工制读取器盘点 HarmonyOS 应用包，再把认证清单投影为不执行的程序图；这是 HarmonyOS roadmap(#1431) 第一增量：仅做包识别与组件清单（F-116/F-117、来源 `harmony-analysis.md`）。

```bash
# 盘点 HAP 包并输出 JSON 清单
rea inspect-artifact /path/Example.hap --format json > inspection.json

# 把 inspection.json 包装为 inventory_evidence 后投影为应用图
rea project-harmony-application-graph projection-input.json --format json
```

- CLI `rea inspect-artifact /path/Example.hap --format json`（F-117）。
- MCP 工具 `project_harmony_application_graph` 接受同样的 `inventory_evidence` 输入（F-117）。
- 识别三种根格式：`.hap`（可安装应用模块）/`.hsp`（运行时共享包）/`.app`（分发 App Pack）；`.har` 因也命名 HTTP Archive JSON 而故意不按后缀分类（F-116）。
- 打包模型提示：仅从 `module.json` 条目声明 Stage、仅从 `config.json` 声明 FA，否则 `unknown`；FA 资源在 `assets/<module>/resources/`、Stage 资源在 `resources/`（F-117）。

**运行时族与验证（F-118）**

- 运行时族提示（`ark`/`native`/`javascript`）来自路径与格式；路径在字节码与 `libs/<abi>` 原生库间基于 N-API 桥接假设（F-118）。
- 验证用 `REA_HARMONY_TEST_HAP` 指向 `_reference/harmony-integration/entry-default-unsigned.hap`；`npm run fixtures:harmony` 下载 SHA-256 固定的 1.0.1 HAP（F-118）。

## 平台四：Android（JADX）静态 APK 分析

REA 通过 `src/android/` 包装固定 headless JADX 引擎，CLI 与 MCP 共用统一应用工作流、返回绑定工制的 Evidence；需要完整 JDK 17+ 与 `jadx-headless-mcp 0.7.1`（F-103、来源 `android-analysis.md`）。

```bash
# 供应环境变量（指向 engine JAR，可选选择既有 JDK）
export REA_JADX_MCP_JAR=/absolute/path/jadx-headless-mcp-0.7.1-all.jar
export JAVA_HOME=/absolute/path/existing-jdk

# 代表性 CLI 命令
rea inspect-android-package /path/Example.apk
rea search-android-classes /path/Example.apk MainActivity
rea inspect-android-class /path/Example.apk example.MainActivity
rea inspect-android-method /path/Example.apk example.MainActivity onCreate
rea inspect-android-method /path/Example.apk example.MainActivity select --overload-index 1
rea trace-android-references /path/Example.apk example.MainActivity
rea trace-android-references /path/Example.apk example.MainActivity --method-name onCreate
```

- `inspect_android_package`/`search_android_classes`/`inspect_android_class`/`inspect_android_method`/`trace_android_references` 为等价 MCP 方法；需 JDK 17+ 与 `jadx-headless-mcp 0.7.1`；环境变量 `REA_JADX_MCP_JAR` 指向 JAR、可选 `JAVA_HOME`（F-103）。

**资源/生命周期限制（F-103/F-104）**

- 环境变量 `REA_JADX_MCP_JAR` 必需、`JAVA_HOME` 可选（F-103）。
- 执行受限：deadline 120 秒（上游反编译 90 秒）、清单与方法文本预算 1 MiB、类名页面索引切片最多 4096 名称、协议帧 8 MiB、stdout/stderr 32 MiB、会话 60 秒不活动清理（F-104）。

## 平台五：固件区域检查与显式提取

REA 接受 Binwalk 3.1.x 做分区/区域检查、Unblob 26.6.x 做显式提取；检查与提取都需 util-linux `prlimit`（F-110、来源 `firmware-analysis.md`）。

```bash
# 供应外部工具（绝对路径、作用域到当前 shell）
export REA_BINWALK_COMMAND=/absolute/path/to/binwalk
export REA_UNBLOB_COMMAND=/absolute/path/to/unblob

# 代表性 CLI 命令
rea inspect-firmware-regions /path/to/firmware.bin
rea extract-firmware /path/to/firmware.bin /path/to/new-output
rea extract-firmware /path/to/firmware.bin /path/to/selected-output \
  --offset 64 --length 4096 --max-depth 3
```

- 固件 CLI：`rea inspect-firmware-regions <path>`、`rea extract-firmware <in> <out>`（支持 `--offset`/`--length`/`--max-depth`）（F-111）。

**环境变量与资源/生命周期限制（F-110/F-111）**

- 环境变量 `REA_BINWALK_COMMAND`/`REA_UNBLOB_COMMAND` 指定外部工具；检查与提取都需 util-linux `prlimit`（正常路径 `/usr/bin/prlimit`，可用 `REA_FIRMWARE_PRLIMIT_COMMAND` 覆盖）（F-110）。
- 限制：输入 128 MiB、deadline 120 秒、继承地址空间 1 GiB、默认临时预算 256 MiB/10,000 条目、每命令 8 MiB stdout+stderr（F-111）。

## 输出 / 验收

- [ ] Apple：`rea trace-dylib-resolution MyApp.app --root Contents/MacOS/MyApp --architecture arm64 --json` 返回解析边与各候选路径结果（F-112）
- [ ] Electron：`rea list-electron-targets http://127.0.0.1:9223` 返回单个内联数组；`rea inspect-electron-page --observation-ms` 支持显式观测时长（F-114）
- [ ] HarmonyOS：`rea inspect-artifact /path/Example.hap --format json` 输出认证清单，打包模型提示（Stage/FA/unknown）正确（F-117）
- [ ] Android：设置 `REA_JADX_MCP_JAR`（JDK 17+）后 `rea inspect-android-package /path/Example.apk` 返回清单与 Evidence（F-103）
- [ ] 固件：设置 `REA_BINWALK_COMMAND`/`REA_UNBLOB_COMMAND` 后 `rea extract-firmware <in> <out> --max-depth` 在当前深度内完成提取（F-110/F-111）

## 反模式提醒

- 不要把各平台限制当成建议值：Android/Firmware 的 deadline（120 秒）、输入/文本/协议帧预算（1 MiB/8 MiB/128 MiB/8 MiB）等都是内存安全边界，超限会报错而非返回不完整结果当完整（F-104/F-111）。
- 不要忽略平台外部工具的环境变量：Android（`REA_JADX_MCP_JAR`）、固件（`REA_BINWALK_COMMAND`/`REA_UNBLOB_COMMAND`/`REA_FIRMWARE_PRLIMIT_COMMAND`）都依赖调用方供应工具（F-103/F-110）。
- HarmonyOS `.har` 不按后缀分类为 Harmony 共享库——`.har` 也命名 HTTP Archive JSON，需验证 ZIP 字节并延迟并附显式 limitation（F-116）。

## 阅读下一步

- [重建工作流示例](reconstruction-workflow-example.md)——把盘点/观测得到的 Evidence 依序推进重建就绪流程