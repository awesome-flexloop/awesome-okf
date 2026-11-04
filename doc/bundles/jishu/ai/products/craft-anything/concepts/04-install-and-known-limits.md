---
okf_version: "0.2"
type: Concept
title: "安装与已知边界：早期 alpha 的现实预期"
description: "Craft Anything 的安装包形态（Windows/macOS/Linux/WASM）、许可与前置依赖，以及早期 alpha 阶段的能力边界与使用前须知"
tags: [craft-anything, install, license, alpha, boundaries]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-04T09:38:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-04T09:38:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
  - id: github-releases
    url: "https://api.github.com/repos/storytold/craft-anything/releases"
  - id: official-status
    url: "https://github.com/storytold/craft-anything/blob/main/STATUS.md"
---

# 安装与已知边界：早期 alpha 的现实预期

## 安装包形态（博文口径）

博文列出项目提供的分发形态（F-023）：

| 平台 | 形态 |
|------|------|
| Windows | `.msi` 安装包 + 便携版 |
| macOS | `.dmg` |
| Linux | AppImage / `.deb` / Flatpak |
| 浏览器 | WASM 查看器 |

**部分核验**：官方 releases API（v0.3.0，2026-11-02）抓取到的资产包含 Linux（aarch64 AppImage + `.zsync`、`.deb`、`.flatpak`、`.pkg.tar.zst`、`.rpm`、`.tar.gz`）与 FreeBSD（aarch64 / x86_64 `.tar.gz`）系列（F-035）。

> ⚠️ 本次仅抓到上述样例，**未穷尽全部平台资产**；Windows `.msi`/便携版、macOS `.dmg`、WASM 查看器的存在性以博文为准，使用前请在 [releases 页](https://github.com/storytold/craft-anything/releases) 核对当前资产。另注：第三方报道提到项目亦提供 FreeBSD 构建（F-043），博文未提。

## 前置依赖与许可

- **前置依赖**：**Rust 1.97+**（F-028）。
- **许可**：**Apache-2.0**（GitHub API `license.spdx_id=Apache-2.0`），仓库页另标注 "Apache-2.0, MIT licenses found"（F-030）。宽松许可，便于使用与商用（许可为官方标注，非法律意见；商用前建议做 License 复核）。

## 早期 alpha 的现实边界（必须知道）

| 边界 | 依据 |
|------|------|
| **处于早期 alpha**，功能与形态可能快速变化 | 博文（F-009）；官方 README Status 段 "Works today / Partly there / Next"（F-026 语境） |
| **构建需安装并登录 Claude Code** | F-018 / F-039 |
| **Codex 适配器未在真实安装中验证** | F-019 |
| **净室模式的"完整实跑"，官方状态页写着"还没做过"** | F-021（博文自述，未获一手页面原文核对） |
| 博文另称"官方记录过一次跑通在 10 月 18 日、96%、一分半" | F-022（**时间线存疑**：早于建仓日 2026-10-31；与 F-021 口径存在张力） |
| 版本高频迭代 | v0.3.0 发布于 2026-11-02，距建仓（10-31）仅两日（F-034/F-032） |

## 工具数口径提醒

使用前若看到不同"工具数"，请注意**三源并存**：博文 314（F-017）/ 第三方 314（F-041）/ 官方 STATUS.md 300 引擎、320 含 AI+setup 层（F-036）。统计层不同，非矛盾造假。

## 采用建议

1. **把它当作"可度量的复刻流水线"试用**，而非"一键生成整站"的成熟产品——先在一个小页面跑通 Study→Build→Check→Ready 全流程。
2. **以官方 releases 与 README 为安装/命令的最终依据**（本包命令来自官方口径核对，未在本机实测）。
3. **关注 `stale_after` 复核**：本项目迭代快，`stale_after=2026-12-31` 前应复核版本、安装包资产与工具数口径收敛情况。

## 阅读下一篇

- [实操示例 · 安装与重建](../examples/00-install-and-run.md)
- [P0 权威核验报告](../references/verification.md)
