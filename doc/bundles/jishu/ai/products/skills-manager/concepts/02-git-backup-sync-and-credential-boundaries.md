---
okf_version: "0.2"
type: concept
title: Git 备份、同步与凭证边界
description: Skills Manager 的私有 GitHub 备份、设备授权、同步冲突/快照、大小限制与凭证机制
tags: [skills-manager, backup, sync, git, keychain, credential, snapshot]
generated:
  by: process:seven-concepts
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: flagged
stale_after: "2026-12-31"
sources:
  - id: wechat-article
    url: "https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-repo
    url: "https://github.com/xingkongliang/skills-manager"
---

# Git 备份、同步与凭证边界

## 私有 GitHub 备份与跨设备同步

- 文章称技能库可备份到**私有 GitHub 仓库**，并可跨设备同步（F-012）。
- 文章描述 GitHub **设备授权**流程用于连接备份仓库（F-013）。
- 官方备份命令的同步流程在仓库锁内执行 Git 提交、获取远端、合并、创建快照及推送等操作（F-032，**源码实现快照，非实机验证**）。

## 同步冲突与快照

- 文章称同步会处理冲突，并在同步前建立快照（F-014）。
- 文章称真实同步冲突可由用户选择**保留本地版本、使用远端版本或两者都保留**，且应用会在选择前创建快照；官方 README 同一快照描述相同选项（F-041）。

## 大小限制边界

- 文章称超过 100 MB 的技能默认不会备份（F-015）。
- 实现层面的精确边界：实现定义 **100 MiB 阈值**；新加入 Git 管理前的超限技能会被备份流程排除，**已跟踪技能不会仅因超过阈值而被自动取消跟踪**（F-025）。只读“超过限制会排除”容易忽略“已跟踪状态”这个前提。

## 凭证存储边界

- 文章称产品会将 GitHub 凭证保存在操作系统钥匙串中（F-016）。
- 实现层面的分支差异：PAT/Device Flow 连接路径要求将令牌写入操作系统钥匙串，失败时返回错误；旧式含凭证 URL 的净化路径在钥匙串不可用时**会保留原含凭证 URL**（F-026）。不同的连接入口有不同失败行为，仅凭“使用系统钥匙串”不足以判定每种凭证路径与故障情形下的保护强度。此结论来自**源码分支描述，不代表安全审计**。

## 作者体验主张（非官方事实）

- 文章转述同步状态偶尔误报、部分工具适配器更新较慢，并评价作者修复较勤；未提供可复核案例或时间范围（F-043）。此为作者/转述观点，不构成官方事实。

## 实务边界

- 备份安全性取决于**状态**（是否已跟踪）与**平台路径**（本地 NTFS 与 UNC/WSL 差异，见「工具集成与平台边界」）。建议重要技能备份后检查仓库内容并执行恢复演练。
- 对敏感仓库使用最小权限令牌，并遵循组织凭证政策；部署前检查所用平台的实际凭证后端与回退行为。