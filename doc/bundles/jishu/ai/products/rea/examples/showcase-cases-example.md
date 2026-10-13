---
type: Example
title: "REA 官网五项 showcase 的证据与验证"
description: "DX-Ball、Notion、TH04、Aegis 与 CTF 的目标身份、调查路径、验证对象及剩余限制"
tags: [rea, example, showcase, dx-ball, notion, th04, reconstruction, electron, dos, pc-98]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T16:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: readme-zh
    resource: "https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/README_zh.md"
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: official-site
    resource: ../references/official-site-source.md
---

# REA 官网五项 showcase 的证据与验证

README 列 DX-Ball、Notion、TH04 三例（F-132），中文官网另有 Aegis 与 CTF，共五项。以下依据 F-153~F-172 和固定 website/evidence；大部分历史分析使用 REA 4.1.0，Aegis 使用 6.1.0。固定源码 6.4.0 只用于当前命令形态核对，不代表本轮重新分析了目标。

## 目标

理解原生函数、Electron 桥、DOS helper、APK 算法和 ELF 约束各自需要什么证据。各案例的上游成绩是公开记录；本轮未运行目标、历史编译器或求解器。

## 输入与前置

- Node 满足支持范围（F-007），已 `npx rea-agents setup` 注册 MCP（F-010/011）。
- 按目标准备分析工具：native 需 Hopper/Ghidra/IDA（F-030~F-032），Electron/JS 无需原生引擎（静态 JS 检查，F-135），DOS 16 位用 Ghidra 专项支持（F-090+）。

## 案例一：DX-Ball —— 重建声像计算

**路径**：沿声音调用追踪 → 定位按位置计算声像的辅助函数 → 检查指令 → 将不完整伪代码转为 C。

- 沿声音相关调用链向下追踪到负责把位置映射为声像（pan）的辅助函数。
- 检查该函数的 x86 指令，将不完整的伪代码补齐为可读 C。
- **验收**：重建结果通过 **3,205 个**原始 x86 测试用例，并**复现编译后函数的全部 63 个字节**。
- 重建仓库：`github.com/N0zoM1z0/dx-ball`。

**可照做 CLI 初探**（native 域）：

```powershell
rea function "D:/analysis/DXBALL.EXE" 0x406400 --provider ghidra --json
```

目标为 DX-Ball 1.07、PE i386。63 字节范围为 `0x406400..0x40643e`，含末地址。3,205 用例为整数 x=0..640 共 641 项乘五个 scale `{0,0.5,1,20,-1}`。历史 VC4.0 比较含已审重定位与引用常量；游戏级集成仍须另验（F-153~F-155）。示例地址不能套用其他版本，可读 sound-pan 名称未证明是目标符号。

## 案例二：Notion —— 追踪 Electron 剪贴板桥

**路径**：渲染进程剪贴板 API → preload → IPC → 主进程 → 富格式剪贴板数据。

- 在渲染进程定位剪贴板 API 入口。
- 沿 Electron 的 preload 暴露的桥（contextBridge 等）与 IPC 通道，追踪到主进程处理逻辑。
- 检查富格式（rich）剪贴板数据的构造与返回。

**可照做 CLI 初探**（Electron/JS 域）：

```powershell
rea analyze-javascript-application /path/to/notion.app.asar --json   # 模块/导入/Electron 边界（F-072）
rea list-electron-targets http://127.0.0.1:9223 --json
rea inspect-electron-page http://127.0.0.1:9223 TARGET_ID --observation-ms 5000 --include-script-sources --json
```

先由用户启动已授权的 Electron 调试实例，选发现结果中可用的 file-page target 替换 `TARGET_ID`；官网 Notion 静态案例未证明 Notion 总提供这种 target。端点不存在、页面不在支持范围时不能照此宣称已捕获剪贴板。

Desktop 7.6.1 的 preload 发现动态 `__electronApi` 和 `channel=null`。API trace 为 partial（17 nodes/16 edges/零 terminal），字面 channel seed 无 graph match。完整四步路线由额外 wrapper 阅读建立，未捕获 Desktop 执行（F-156/F-157）。

Web editor 是另一个缓存 build，不能与 Desktop 包当作同一运行版本。提取及提升 helper 的 stub harness 支持 marker/private MIME 匹配策略，不证明 OS 剪贴板 hydration、复杂 block 保真或持久化 Notion 页面。SQLite MessageChannel handoff 同样只有源码解释，未捕获 SQL 会话（F-158/F-159）。

## 案例三：TH04 —— 恢复 DOS 环形子弹计算

**路径**：检查原始 PC-98 游戏 16 位指令 → 恢复固定角度与瞄准角度计算 → 重建 C++ → 与当年编译器输出对比。

- 针对 PC-98 的 16 位指令逐条检查。
- 恢复环形子弹生成所需的固定角度 / 瞄准角度计算逻辑。
- 用重建 C++ 与历史编译器输出比对，记录具体匹配范围。
- 重建仓库：`github.com/N0zoM1z0/th04`。

**可照做 CLI 初探**（16 位 DOS 专项，Ghidra 深度适配）：

```bash
rea decompile /path/to/MAIN.EXE 0x2cfc8 --provider ghidra --json
```

此调用形态按固定 6.4.0 核对，未实跑；需已按 DOS MZ 配置适当 Ghidra 主机与 load-image profile，不能套用 Windows PE 只读支持。`--function` 不在 schema 中，ring_bullets 未证为原始符号（F-179）。

MAIN.EXE 共 156258 字节=6144 header+150114 module。load segment 为 0x1000，helper 线性地址 0x2cfc8 对应文件 offset 0x1e7c8；body 两范围共 503 字节，包围 span 517 字节。教学 `aimed_ring_angle` 非完整 helper。16 是 tune 前模板初值，不代表所有难度固定 16 发。

历史 Turbo C++ 4.0J 两次 cold build 匹配完整 bullet-add extent 2139 字节及 MAP/relocation，范围含 helper 与周边函数，不是整 EXE 或全游戏。目标出处为 `candidate-local-attested`，不新增独立 pristine 证明；近调用 segment alias 还可能误导静态图边（F-170~F-172）。

## 案例四 Aegis 默认验证码

目标为 Aegis 3.4.3 APK；上游环境 REA 6.1.0、jadx-headless-mcp 0.7.1、OpenJDK 21、Linux x64。从 TotpInfo timestamp overload 跟到 counter、HMAC 与格式化。发布包的 generateOTP/getHash 位于 `kotlin.ExceptionsKt`，不能只按原源码 HOTP 类名寻找（F-160/F-161）。

133 输入=0..120 每整秒 121 输入+六个 RFC 八位向量+对应六个六位结果。检查对象是提取方法的 Java harness、独立 Python 和 WebCrypto，不是 APK 执行。公共 key `12345678901234567890`，30/59 秒为 287082，60 秒为 359152。六位、SHA1、30 秒只是默认参数；不覆盖 vault、Android UI、签名或 native libraries（F-162~F-164）。

可独立检查的公开算法见 [官网实验](official-site-labs.md)，不要输入真实账户 secret。

## 案例五 CTF masked squares

目标为 DownUnderCTF 2023 stripped ELF x86-64、15248 字节。先搜字符串，再沿 xrefs 找输入转换与两个 helper，读 mask/target 数据。36 个输入字符，26 个 mask，每项 24 字节；目标读取 144 字节中只取前 104 字节的 26 个 little-endian int，mask 总读取 624 字节（F-165~F-167）。

正 run 写 1，负 run 写 0，零结束。第七项 `eb 01 f2 00` 对应 -21,+1,-14，唯一选 index 21，target 55 即字符 7。官网 [完整 solver](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/public/showcase/ctf/solve.py) 把方程交给 Z3；alphabet 与 DUCTF 前后缀是分析者附加假设，不是二进制约束。

候选 `DUCTF{ezzzpzzz_07bcda7bfe81faf43caa}` 满足 26 方程。上游原程序正例 Correct!/exit0，改一字符负例 Incorrect!/exit255。第二模型搜索超时，未证明唯一解。本轮只解析脚本常量回验方程，不运行 solver 或原 ELF（F-168/F-169）。

## 共同模式：从调查到重建

按声明对象选择验证，衔接 [工程与管理](../concepts/10-engineering-workflow.md)：

1. **调查（Investigation）**：`analyze`/`trace` 定位目标功能与调用链，获取结构化证据。
2. **证据驱动重建**：把不完整伪代码 / 指令转为可编译源码，用返回值覆盖测试用例（DX-Ball 的 3,205 用例）或编译器输出比照（TH04）验证。
3. **义务台账收口**：若走完整重建，用 `build_reconstruction_obligation_ledger` 记录 artifacts/providers/scenarios 与 unknowns（F-130），产出 `closure_digest`。

## 边界与注意事项

- 这些是官方研究案例，不构成对读者行为的法律授权；使用目标前须取得授权并遵守适用法律。
- 命令为 README/源码核对后的示意路径，未在本机实跑；实际以 `rea <command> --help` 与官方 showcase 为准。
- 运行时观测（浏览器/进程）会以**你的用户权限**运行目标（F-135），注意隔离与授权。

## 相关概念

- [三类调查](../concepts/12-evidence-driven-investigation.md)
- [比较器与重建验证](../concepts/13-reconstruction-verification.md)
- [本轮核验记录](../references/official-site-verification.md)
