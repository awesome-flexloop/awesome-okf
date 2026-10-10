---
okf_version: "0.2"
type: reference
title: 原文事实清单
description: 《又一个 skill 神级工具，帮我省了太多时间。》文章事实采集与官方核验补充登记，F-001 至 F-044，与 Spec facts.md 双份编号一致
tags: [skills-manager, skills, ai-coding, agent]
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
  - id: github-repo
    url: "https://github.com/xingkongliang/skills-manager"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-release-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager/releases/latest"
  - id: github-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager"
---

# 原文事实清单

> **信源**：微信公开文章《又一个 skill 神级工具，帮我省了太多时间。》（账号：开源日记，作者自称“熊叔”，发布于 2026-10-04 15:14）
> **文章链接**：https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg
> **核验日期**：2026-10-10
> **信源距离**：文章为第三方产品介绍，作者未声明其为开发者或亲自完成可复核测试；官方 README、GitHub API、Release API 与实现源码用于交叉核验
> **双份登记**：本文件与 Spec `.trae/specs/okf-wiki-ecosystem/skills-manager-blog-okf-wiki/facts.md` 使用相同、连续的 F 编号；V 阶段逐项比对。

---

## A. 文章页面事实与作者主张（F-001~F-020）

| 编号 | 事实陈述 | 类型 | 来源 | 定位 | P级/状态 |
|---|---|---|---|---|---|
| F-001 | 文章标题为《又一个 skill 神级工具，帮我省了太多时间。》 | page_fact | blog | 标题 | P1 |
| F-002 | 页面账号显示为“开源日记”，文章开头作者自称“熊叔”。 | page_fact | blog | 账号栏、开头 | P1 |
| F-003 | 页面没有明确称作者是 Skills Manager 开发者/维护者，也没有称其亲自安装、测试或验证该产品。 | page_fact | blog | 开头及产品介绍段 | P1；仅限已读页面 |
| F-004 | 页面发布时间显示为 2026-10-04 15:14。 | page_fact | blog | 页面元信息 | **P0** |
| F-005 | 文章将 Skills Manager 描述为集中管理 AI 编程工具 Skills 的桌面产品。 | page_fact | blog | 产品介绍段 | P1 |
| F-006 | 文章描述技能库以卡片形式呈现技能，并展示来源及同步目标等信息。 | page_fact | blog | 技能库界面段 | P1 |
| F-007 | 文章称产品支持 54 个 AI 编程工具/Agent。 | page_fact | blog | 支持工具数量段 | **P0**；核验口径见 F-024 |
| F-008 | 文章称产品可扫描已有 AI 工具并将技能集中纳入统一技能库。 | page_fact | blog | 首次启动与技能库段 | P1 |
| F-009 | 文章称 macOS、Windows、Linux 均可安装，并给出 macOS Homebrew 安装方式。 | page_fact | blog | 安装段 | **P0**；文章未标具体版本 |
| F-010 | 文章称 Windows 可用 junction 方式把技能连接到各工具；WSL 场景使用复制方式。 | page_fact | blog | Windows/WSL 兼容段 | **P0** |
| F-011 | 文章介绍可在 Dashboard 中启用 Agent 管理，并通过 `manage-skills` 能力和 CLI 管理 Agent。 | page_fact | blog | Agent 管理段 | P1 |
| F-012 | 文章称技能库可备份到私有 GitHub 仓库，并可跨设备同步。 | page_fact | blog | 备份同步段 | **P0** |
| F-013 | 文章描述 GitHub 设备授权流程用于连接备份仓库。 | page_fact | blog | 授权段 | **P0** |
| F-014 | 文章称同步会处理冲突，并在同步前建立快照。 | page_fact | blog | 同步与快照段 | **P0** |
| F-015 | 文章称超过 100 MB 的技能默认不会备份。 | page_fact | blog | 大文件限制段 | **P0**；实现适用范围见 F-025 |
| F-016 | 文章称产品会将 GitHub 凭证保存在操作系统钥匙串中。 | page_fact | blog | 凭证存储段 | **P0**；异常回退边界见 F-026 |
| F-017 | 文章称产品开源，并指向公开 GitHub 仓库。 | page_fact | blog | 开源地址段 | P1 |
| F-018 | 文章作者以“省了太多时间”表达个人体验/评价。 | author_claim | blog | 标题及结尾 | P2；非独立效率证据 |
| F-019 | 文章未标明所介绍功能对应的产品版本，也未提供完整测试环境、逐步输入输出或独立复核记录。 | page_fact | blog | 全文 | P1 |
| F-020 | 文章提供了概略安装和功能路径，但没有给出覆盖安装、同步、冲突恢复与回滚验证的完整操作规程。 | page_fact | blog | 安装、备份与 Agent 管理段 | P1 |

## B. 官方来源补充事实（F-021~F-032）

| 编号 | 事实陈述 | 类型 | 来源 | 定位 | P级/状态 |
|---|---|---|---|---|---|
| F-021 | 官方仓库为 `xingkongliang/skills-manager`，公开许可为 MIT；2026-10-10T04:40:27Z 读取的 GitHub API 描述为“50+ coding tools”，仓库 `updated_at` 为 `2026-10-10T04:32:24Z`。 | page_fact | github-api | repository metadata | P0；API 快照，观察时间见来源清单 |
| F-022 | 官方 README 将产品描述为统一技能库，并说明技能可以在支持的 AI 编程工具之间复用。 | page_fact | github-readme | Features | P1 |
| F-023 | 官方英文 README 在 `Supported Tools` 节称支持 54 个内置 Agent，并列出部分具名集成；还说明设置中可添加自定义工具。该 README 快照对应主分支提交 `9e03d833829bc5e004263f61dec75f3bc8e39062`。 | page_fact | github-readme | `Supported Tools` | **P0**；快照观察于 2026-10-10 |
| F-024 | 文章称支持 54 个 AI 编程工具/Agent；本次读取的 README 明确为“54 agents ... out of the box”，仓库 API 描述为“50+ coding tools”。数量口径在字面上相互支持，但 README 使用 Agent、API 使用 coding tools，不能据此断言两者统计对象完全相同。 | page_fact | blog, github-readme, github-api | 支持数量 / `Supported Tools` / repository description | **P0**；口径保留 |
| F-025 | 实现定义 100 MiB 阈值；新加入 Git 管理前的超限技能会被备份流程排除，已跟踪技能不会仅因超过阈值而被自动取消跟踪。 | page_fact | backup-source | `git_backup.rs` | **P0** |
| F-026 | 凭证处理因入口而异：PAT/Device Flow 连接路径要求将令牌写入操作系统钥匙串，失败时返回错误；旧式含凭证 URL 的净化路径在钥匙串不可用时会保留原含凭证 URL。 | page_fact | oauth-source | `connect_with_token`、`sanitize_url_to_keychain` | **P0**；仅描述源码分支，不代表安全审计 |
| F-027 | Windows 链接实现优先尝试目录符号链接，在本地 NTFS 上可回退到 junction；远程/UNC（包括 `\\wsl.localhost`）无法使用该 junction 路径时走复制回退。 | page_fact | sync-source | `sync_engine.rs` | **P0** |
| F-028 | README 对 WSL 场景的建议为复制技能，而非依赖 Windows junction。 | page_fact | github-readme | WSL | **P0** |
| F-029 | 官方 README 记载支持 macOS、Windows、Linux，并列出相应桌面安装方式。 | page_fact | github-readme | Installation | **P0** |
| F-030 | 2026-10-10 复核时重新读取的 `releases/latest` API、Release 列表首项及网页 `/releases/latest` 均指向 `v1.40.3`，发布日期为 `2026-10-01T23:49:29Z`；三个视图在本次新快照中一致。此前记录的 `v1.22.1`、`v1.28.3`、`v1.17.0` 没有保留原始响应，无法复现，作为未验证旧记录处理。 | page_fact | release-api, release-list-api, release-page | latest API / releases collection / rendered latest page | **P0**；动态快照；旧值不可复现 |
| F-031 | 仓库 API 的 `updated_at` 为 `2026-10-10T04:32:24Z`；主分支 README 快照对应提交 `9e03d833829bc5e004263f61dec75f3bc8e39062`（提交时间 `2026-10-09T21:34:41Z`）。文章没有给出可将其功能描述绑定到某个产品版本的证据。 | page_fact | github-api, github-readme, blog | repository metadata / main README / 全文 | P1；API 与 README 快照观察于 2026-10-10 |
| F-032 | 官方备份命令的同步流程在仓库锁内执行 Git 提交、获取远端、合并、创建快照及推送等操作。 | page_fact | oauth-source | `commands/git_backup.rs` | P1；源码实现快照，非实机验证 |

## C. 文章补充事实与主张（F-033~F-044）

| 编号 | 事实陈述 | 类型 | 来源 | 定位 | P级/状态 |
|---|---|---|---|---|---|
| F-033 | 文章称技能可从 Git 仓库、本地文件夹及 `.zip`/`.skill` 压缩包导入，并可在内置 skills.sh 市场浏览、按关键词搜索技能。 | page_fact | blog | “一个中央库”段 | P1 |
| F-034 | 文章称中央技能库默认位于 `~/.skills-manager`。 | page_fact | blog | 中央技能库介绍 | **P0**；路径主张，README 同一快照亦记载默认路径 |
| F-035 | 文章称首次启动时应用会自动创建中央技能库并扫描电脑上已有的 AI 工具。 | page_fact | blog | 安装后首次启动 | P1 |
| F-036 | 文章称每个工具有独立工作区，可列出该工具实际可见的技能，包括非经该应用安装的技能。 | page_fact | blog | “一键分发”段 | P1；文章陈述 |
| F-037 | 文章称启用 Agent 管理时，应用会安装 `manage-skills` 技能，并将 CLI 放在 `~/.skills-manager/bin/`，Agent 可不配置 PATH 调用。 | page_fact | blog | Agent 管理段 | P1；文章陈述 |
| F-038 | 文章称 WSL 中桌面应用只能复制技能；若要使用 Linux 软链接，应安装 Linux 版 CLI。 | page_fact | blog | WSL 注意事项 | **P0**；仅文章陈述，边界待官方资料核验 |
| F-039 | 文章称 GitHub Releases 提供 `.dmg`、`.exe`、`.msi`、`.AppImage`、`.deb`、`.rpm` 安装包并覆盖 x64 与 arm64。 | page_fact | blog | 安装段 | **P0**；发布资产随版本变化 |
| F-040 | 文章称技能可分组为命名预设，并可按当前工具一键启用或停用整组技能。 | page_fact | blog | 预设段 | P1；官方 README 同一快照也描述预设功能 |
| F-041 | 文章称真实同步冲突可由用户选择保留本地版本、使用远端版本或两者都保留，且应用会在选择前创建快照。 | page_fact | blog | 备份与多设备同步段 | **P0**；README 同一快照描述相同选项 |
| F-042 | 文章称产品作者曾任腾讯优图高级研究员、拥有机器学习博士学位并获得 ICCV 挑战赛冠军；文章未提供可独立核实的身份材料。 | author_claim | blog | “写在最后” | P1；仅文章单源，不作为已核实履历 |
| F-043 | 文章转述同步状态偶尔误报、部分工具适配器更新较慢，并评价作者修复较勤；未提供可复核案例或时间范围。 | author_claim | blog | 使用体验与注意事项 | P2；作者/转述观点 |
| F-044 | 文章引用第三方软件站称多工具用户使用该产品“基本就是刚需”，并认为只使用一个工具时 Git 仓库加软链接可能更简单。 | author_claim | blog | 适用性评价段 | P2；价值判断，不作普遍结论 |

## 疑点与边界

- 文章未标注所介绍功能对应的产品版本（F-019）；官方 README 的 README commit SHA 已固定为宜（F-031）。
- 版本结论完全依赖 2026-10-10 动态快照（F-030）；旧记录 `v1.22.1`/`v1.28.3`/`v1.17.0` 无原始响应、不可复现，按未验证历史处理。
- 作者履历（F-042）与体验/转述（F-018、F-043、F-044）均为单源或价值判断，未升级为已核实事实。