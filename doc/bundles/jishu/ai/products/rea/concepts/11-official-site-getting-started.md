---
type: Concept
title: "REA 官网上手与安装边界"
description: "从 Node、客户端配置计划和目标类型开始，连接 REA 并区分静态分析、原生引擎及运行时权限"
sources:
  - id: site
    resource: ../references/official-site-source.md
  - id: facts
    resource: ../references/facts.md
generated: {by: "process:seven-concepts-e", at: "2026-10-12"}
status: draft
---

# REA 官网上手与安装边界

REA 给编程助手提供逆向工具与结构化证据。第一次使用时，可以先调查一个小型 JavaScript 应用的文件导出路径，无需先配置原生反编译器。官网上手页、首次调查页与 FAQ 对应 W02/W03/W04；本页依据 F-007、F-135、F-137~F-140。

## 连接客户端

先准备 Node.js 与 npm。固定源码 6.4.0 的支持范围为 `^22.19.0 || ^24.11.0 || >=26.0.0`，不要把它简化为“所有 Node 22 以上”。官网使用最新版命令；需要保留可重复环境时，应另记录实际安装版本与客户端配置。

```powershell
npx rea-agents@latest setup
```

这条命令会获取并执行 npm 包，不能当作纯读取。查看计划，确认选择的客户端、MCP 连接与调查技能，确认后再写入配置。官网说明会备份已有配置，结束后须完全退出并重启客户端。备份不代替审阅配置：尤其要核对 `command`、`args`、环境变量以及分析工具路径。

助手看不到工具时，先重连会话，再检查客户端注册。下面以 Codex 为例，其他客户端应使用其真实 ID：

```powershell
npx -y rea-agents@latest doctor --client codex --json
```

`doctor` 的成功结果应按检查对象解释。客户端注册正常不代表所有分析后端都能处理当前目标；IDA 的 doctor 仅检查注册，不会启动 IDA（F-139）。

## 按目标准备后端

| 目标 | 起点 | 前置与边界 |
|---|---|---|
| JS 目录或 ASAR | `analyze-javascript-application` | 读取文件，不启动 Electron；动态关系可能未解析 |
| 原生程序或 DLL | Ghidra、Hopper 或 IDA | 用户自备工具；按格式、架构及主机确认支持 |
| 已启动网页 | 浏览器调试端点与 page target | 观察窗口内行为；用户或独立控制器负责动作 |
| APK | Android provider | 依赖主机与 JDK 要求见既有平台教程；静态调查不等于运行 APK |

Windows Ghidra 官网范围为实验性只读支持：固定本地 NTFS 驱动器上的 x86/x64 PE 应用与 DLL，已有 Ghidra 12.1.x、64 位 JDK 21 或更高版本。示例路径必须替换为真实安装位置：

```powershell
$env:GHIDRA_INSTALL_DIR = "C:/tools/ghidra_12.1.4_PUBLIC"
$env:JAVA_HOME = "C:/tools/jdk-21"
npx -y rea-agents@latest doctor --provider ghidra --json
```

通过后再运行 setup，并检查计划是否保存这些有效路径。不要把 Windows 范围推广到 DOS、固件或任意磁盘路径。Linux/macOS 的 loader、架构与原生反编译器要求见 [Native 专项](08-native-ghidra-specialty.md)。

2026-10-12 官网快照的 IDA headless 记录只列 Windows x64 的 IDA 9.3 supervisor，并称 Linux/macOS headless 未验证（F-139）。固定 6.4.0 技术文档另记录 macOS arm64 headless IDA Professional 9.1 build 9.1.250226（F-124）；这是两个来源的覆盖差异，不能用官网旧范围否定源码记录，也不能推广到其他版本。attached 与 headless 模式须分别核对；Linux headless 和真实 HTTP supervisor 仍未验证。

## 提出第一个问题

把绝对路径和一个可检查的问题交给助手，例如：

> 用 REA 检查这个已授权的应用目录。导出笔记时，哪些文件参与？CSV 写到哪里、有哪些字段？回答附源码位置，区分静态推断与实际执行。

CLI 用户可分析目录或 ASAR。含空格的路径必须加引号：

```powershell
npx -y rea-agents@latest analyze-javascript-application "D:/analysis/notes-example" --json
```

查看图中的源码位置，再读取相应函数。原生 one-shot CLI 每次导入、分析后关闭会话；MCP 在会话仍打开时能复用导入（F-140）。重复原生查询的成本不能按静态 JS 查询来估计。

## 权限与证据

REA 不提供目标执行沙箱。静态 JS/.NET 读取与 Process Capture 启动命令是不同动作；浏览器调试端口也暴露当前浏览器控制面，宜使用独立配置与本地回环端口。遇到陌生程序，应先取得授权并安排隔离。

“本地优先”描述分析工具的部署位置，不保证编程助手不会向模型服务商发送证据。输入涉及源码、令牌或个人资料时，还须检查客户端的数据策略。

本轮仅核对网页与固定源码，未运行这里的安装、doctor 或分析命令。读者实际运行后应保留版本、目标身份和失败项，不能只记录“连接成功”。

## 相关概念

- [Notes 首次调查](../examples/notes-first-investigation.md)
- [三类证据驱动调查](12-evidence-driven-investigation.md)
- [CLI 与 setup 原理](05-cli-and-setup.md)
