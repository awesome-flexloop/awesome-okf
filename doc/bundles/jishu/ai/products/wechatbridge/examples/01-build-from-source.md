---
type: Example
title: "从源码构建与开发验证（命令逐字）"
description: "官方 README「开发者」章节的构建前置、四行构建命令、产物路径、安装注册脚本、开发验证命令与项目结构，命令逐字引用不改写。"
tags: [wechatbridge, swiftpm, xcode, 源码构建, 逐字核对, 非实测]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki:E", at: "2026-11-06T12:08:16+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-06T12:08:16+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: official-readme
    resource: https://github.com/freestylefly/WeChatBridge
---

# 从源码构建与开发验证（命令逐字）

> ⚠️ **操作来源声明**：源文未提供任何命令（F-039）。本篇全部来自官方 README「开发者 → 从源码构建 / 开发与验证 / 项目结构」
> 章节，**非源文作者实测、非本知识包实机验证**。命令在 [verification.md ④ V-1/V-2/V-3](../references/verification.md)
> 做过逐字核对，本篇**原样引用、不改写、不补参数**。
> 构建语境为 **macOS + SwiftPM**；Windows 侧仅有一条 `dotnet test` 命令。

## 0. 构建前置

官方逐字：「需要 macOS 14+，以及 Xcode 16 或兼容 Swift 6 的 Command Line Tools。」（F-088）

| 项 | 要求 | F 编号 |
|----|------|--------|
| 系统 | macOS 14+ | F-088 |
| 工具链 | Xcode 16 或兼容 Swift 6 的 Command Line Tools | F-088 |
| 依赖管理 | Swift Package Manager（管理 macOS 源码与 Sparkle 依赖） | F-097 |

## 1. 四行构建命令（逐字）

```text
git clone https://github.com/freestylefly/WeChatBridge.git
cd WeChatBridge/macos
swift test
CONFIG=release Scripts/make-app.sh
```

（F-089，逐字核对见 verification.md ④ V-1）

产物位置（官方逐字）：「构建产物位于 `macos/dist/微信流.app`。」（F-090）

## 2. 安装到当前用户并注册分享扩展（逐字）

```text
Scripts/install-dev-build.sh
```

（F-091，逐字核对见 verification.md ④ V-2）

随后官方给出的路径（F-092）：

- 打开「**微信流 → 设置 → 入口**」，启用需要的分享入口；
- 或前往「**系统设置 → 通用 → 登录项与扩展 → 共享**」管理它们。

## 3. 签名说明（官方逐字要点，F-093）

> 本地构建会优先使用钥匙串中的 Apple Development 或 Developer ID 签名。
> 没有可用证书时会使用 ad-hoc 签名，macOS 可能要求重新授予辅助功能权限。

这条与 concepts/01 的权限模型直接相关：ad-hoc 签名会让辅助功能授权失效，需要重新授予。
**注意**：这是本地构建的签名策略，**不等于**源文所称「已签名公证」的完成态（F-015、F-103）。

## 4. 开发与验证命令（逐字，F-094）

```text
# macOS（在 macos/ 目录下运行）
cd macos
swift test                                    # 运行测试
swift Scripts/check-localizations.swift       # 校验中英文资源
Scripts/check-release-config.sh               # 签名 / Bundle ID / App Group 检查
Scripts/dev-preview.sh                        # 构建、安装并打开开发版本

# Windows
dotnet test windows/WeChatBridge.Windows.sln -c Release
```

四条 macOS 脚本的用途注释沿用官方原文。`make-app.sh` 的作用是把主程序与**十二个 Share Extension**
组装成完整的 `.app`（F-096）——这与入口矩阵的「十二个」是同一版本口径（F-067）。

## 5. 项目结构（官方目录树要点，F-095）

| 顶层目录 | 内容 |
|---------|------|
| `macos/` | 完整 SwiftPM 包；`Sources/` 下 `WeChatBridgeApp`（主应用、设置、转发编排与权限管理）、`WeChatBridgeCore`（批次、场景、归档和剪贴板核心逻辑）、`WeChatBridgeShare`（macOS Share Extension）；另有 `Resources/`、`Scripts/`、`Tests/` |
| `ios/` | 开发中，XcodeGen 工程，复用 `WeChatBridgeCore` |
| `windows/` | .NET WPF 解决方案：`src/WeChatBridge.Windows`（WPF 主程序）、`src/WeChatBridge.Windows.Core`（Inbox 契约/投递/场景/技能，无 UI 依赖）、`src/WeChatBridge.ShareTarget`（Windows Share Target 助手）、`packaging/SparsePackage`（稀疏包 MSIX）、`scripts/`、`tests/`（xUnit） |
| `shared/` | 多端共用资产与契约：`AppLogos/`、`Design/`、`Screenshots/`、`Skills/`、`README.md`（Inbox 共享契约 + 文件级端口对照表） |
| `site/` | Sparkle 更新源与版本说明 |

> 结构表可用于把 concepts/01 的「Share Extension + 场景配置 + 本地记录」三模块（F-027~F-030）
> 与真实代码目录对上号：`WeChatBridgeShare` / `WeChatBridgeApp` / `WeChatBridgeCore`。

## 6. 参与贡献（官方要点，F-094 附近）

官方「参与贡献」列五步：先看 Issues 是否已有讨论 → Fork 并从 `main` 建功能分支 → 保持改动聚焦并为行为变化补测试 →
提交前运行 `swift test` 与本地化检查 → 在 PR 说明动机、验证方式与界面变化；
安全问题走 GitHub Security Advisories 私下报告。本篇只登记该流程存在，不展开为贡献教程。

## 7. 本篇未覆盖

- 未在 macOS 实机执行上述任何命令，故不给出输出样例、耗时或失败排查。
- `USAGE.zh-CN.md`、`PRODUCT_CAPABILITIES.zh-CN.md` 未抓取正文（F-101）。
- 上游项目 Dukou（`github.com/qzz0518/Dukou`，F-099）未抓取，二次开发边界未评估。
- 路线图中的 Homebrew Cask、Universal 2 构建等条目（F-100）为规划项，本篇不作可用声明。
