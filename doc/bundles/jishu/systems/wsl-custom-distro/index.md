---
okf_version: "0.2"
type: bundle
title: "WSL 自定义 Linux 发行版构建教程"
description: "从 Linux 根文件系统到可安装 WSL 发行版的中文教程：rootfs tar、/etc/wsl-distribution.conf、OOBE、/etc/wsl.conf 与 systemd、Windows Terminal 模板、.wsl 安装、ModernDistributions 清单、企业注册表分发与发布门禁"
tags: [wsl, custom-distro, rootfs, tar, oobe, systemd, windows-terminal, manifest, enterprise]
generated: { by: "reference_agent/trae-solo", at: "2026-11-06T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-06T00:00:00Z" }
status: draft
stale_after: "2027-05-31"
sources:
  - id: ms-zh
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro
    title: 为 WSL 生成自定义 Linux 分发版（中文）
    last_modified: "2025-10-04"
  - id: ms-en
    resource: https://learn.microsoft.com/en-us/windows/wsl/build-custom-distro
    title: Build a Custom Linux Distribution for WSL（英文）
  - id: facts
    resource: /references/facts.md
    title: 事实清单（81 条）
---

# WSL 自定义 Linux 发行版构建教程

本知识包系统讲解 Microsoft Learn 官方指南《为 WSL 生成自定义 Linux 分发版》：怎样把一个 Linux 根文件系统打包成 `.wsl` 文件，并让它具备 OOBE 首次启动体验、Windows Terminal 配置、开始菜单快捷方式，最终进入 `wsl --install` 的分发清单。

- **适用版本**：WSL 2.4.4 及以上（F-004）。
- **事实底座**：81 条编号事实，来自中英文官方页面双源核对（[事实清单](references/facts.md)）。
- **证据边界**：未从零构建并发布发行版；OOBE 脚本为语义重建；本机 WSL 3.0.4.0 仅证明版本前提。详见 [核验报告](references/verification.md)。

## 内容概览（concepts/，10 篇）

**入门与载荷**

- [00 全景](concepts/00-overview.md) — 四层交付物、术语表、五步最短路径与阅读路线
- [01 准备与打包 rootfs tar](concepts/01-rootfs-tar.md) — tar 内容、官方命令、gzip、去宿主化检查与打包验证

**安装期契约**

- [02 编写 /etc/wsl-distribution.conf](concepts/02-wsl-distribution-conf.md) — oobe / shortcut / windowsterminal 三节七键
- [03 编写 OOBE 首次启动脚本](concepts/03-oobe.md) — 幂等短路、创建/加组/回滚、测试矩阵
- [04 编写 /etc/wsl.conf 并处理 systemd](concepts/04-wsl-conf-systemd.md) — `[boot] systemd` 与 9 个问题单元
- [05 生成 Windows Terminal 配置文件](concepts/05-terminal-profile.md) — profileTemplate JSON 与配色方案

**安装与分发**

- [06 创建 .wsl 文件并安装](concepts/06-wsl-file-install.md) — 扩展名、双击、`--from-file`、在线列表
- [07 分发清单结构与本地测试](concepts/07-manifest-local-test.md) — ModernDistributions、flavor、注册表覆盖与 `file://`
- [08 三档分发与企业/公开上架](concepts/08-enterprise-and-publishing.md) — 成员资格、PR、企业清单治理
- [09 官方建议、发布门禁与故障排查](concepts/09-recommendations-checklist.md) — 20 项检查与失败模式表

## 五条核心洞察（摘要）

1. **四件套契约**：交付物不是「一个镜像」，而是载荷 + 首次启动契约 + 安装入口 + 分发元数据（I-1）。
2. **OOBE 单点否决**：`oobe.command` 非零即拒绝 shell，脚本必须幂等、可回滚、可诊断（I-2）。
3. **配置按时点分层**：`wsl-distribution.conf` 管首次安装，`wsl.conf` 管每次启动（I-3）。
4. **分发三档控制权**：直传文件 → 企业注册表清单 → 官方 PR 上架（I-4）。
5. **质量底线是去宿主耦合**：排除 `resolv.conf`、内核、initramfs 与密码哈希（I-5）。

完整四元组与可迁移模式「四段式分发契约」见 [洞察与模式](references/insights.md)。

## 建议阅读路径

- **第一次做发行版**：00 → 01 → 02 → 03 → 04 → 05 → 06 → 09
- **企业内分发**：00 → 01 → 02 → 07 → 08 → 09
- **排障导向**：09 的失败模式表 → 对应章节
- **只看设计取舍**：references/insights.md

## 信任与生命周期

- 全部文档 `status: draft`、`stale_after: 2027-05-31`：官方页面最后更新 2025-10-04，WSL 与清单格式迭代较快，建议每半年或 WSL 主版本升级后复核。
- 6 处源页面问题（重复字段、单复数不一致、脚本换行丢失、翻译痕迹、键名大小写、`file://` 格式差异）已在本库统一口径并给出处置落点；4 项官方缺口保持登记、不做推断。详见 [核验报告](references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
