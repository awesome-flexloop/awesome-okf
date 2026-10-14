---
type: Reference
title: "kywc 仓库自带文档登记与口径说明"
description: "README、docs/PROTOCOLS、ENV、KNOWN_ISSUES、CONTRIBUTING 的信源登记：文档事实层与代码事实层的关系及已记录的双源差异"
tags: [wayland, openkylin, documentation, protocols, env]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 固定快照 4df6562
---

# kywc 仓库自带文档登记与口径说明

仓库随附的文档是本束的**二级事实源**：凡文档与代码均可核验的主题，以固定提交的代码为最终事实层，文档按「项目自陈」引用；两者出入一律保留为差异条目，不替上游裁决。

## 文档清单（均在 4df6562 快照内）

| 文件 | 内容 | 本束使用方式 |
|---|---|---|
| `README.md` | 项目一句话定位（基于 wlroots 的 Wayland 合成器、openKylin 默认显示服务器）、8 条功能特点、依赖列表、meson/ninja 构建三步、CLI 用法、多语言流程、致谢（wlroots/sway/wayfire/labwc） | [01 构建运行](/concepts/01-build-run.md)、[00 全景](/concepts/00-overview.md) 引用为项目口径 |
| `docs/PROTOCOLS.md` | 协议支持矩阵，10 节 118 数据行：Wayland core 7、stable 3、staging 20、unstable 24、wlr 10、kde 24、weston 10、external 8、ukui 7、kywc 5 | [12 协议全景](/concepts/12-protocols.md) 的对账对象（XML/代码为最终层） |
| `docs/ENV.md` | 21 个环境变量：日志 1、显示 7、渲染 4、输出 2、应用侧 4、其他 3 | [01 构建运行](/concepts/01-build-run.md)/[04 后端](/concepts/04-backends.md)/[05 渲染](/concepts/05-rendering.md)/[07 输出](/concepts/07-output-management.md) |
| `docs/KNOWN_ISSUES.md` | 已知问题清单 | [00 全景](/concepts/00-overview.md) 证据边界处引用 |
| `docs/CONTRIBUTING.md` | 贡献流程 | 不作为教程主体 |
| `data/kylin-wlcom.1.scd`、`data/kylin-wlcom-wrapper.1.scd` | scdoc 格式 man page（程序与 wrapper 各一） | CLI/会话启动事实的文档交叉源 |
| `NOTICE` | 第三方代码归属声明 | 合规引用；其中提及的个别历史文件在当前快照已不存在（见差异） |
| `LICENSES/` | GPL-1.0-or-later、LGPL-2.1-or-later、MIT-CMU、MulanPSL-2.0 四份协议文本 | 许可说明 |

## 已记录的双源差异（不裁决，随事实清单保留）

> 以下条目来自 5 簇事实采集的「疑点与矛盾」节（D-R1/D-R5 编号），均有快照内行号证据；上游修复前，教程正文以代码事实为准并显式提示。

1. **环境变量文档缺录**：`KYWC_XWAYLAND`、`KYWC_EIS_SOCKET` 在源码有 getenv 消费点而 ENV.md 无条目（D-R1-04）。
2. **CLI 文档不符**：README/man 的 `-D` 调试项与源码实际 6 个 flag 不一致（缺 3 个、长形描述不符）（D-R1-03）。
3. **依赖列表出入**：README 列 libseat，meson.build 无此 dependency（D-R1-02）。
4. **PROTOCOLS.md 矩阵问题**（D-R5-145~156 共 12 条），要点：
   - kywc 节缺 `kywc_stream_manager_v1`（XML 与代码均存在）；
   - staging 表 `xwayland_shell_v1` 重复两行；
   - `protocols/kywc-stream-v1.xml` 的 `<protocol name>` 误写为 `kywc_capture_v1`；
   - `protocols/meson.build` 中 `linux-dmabuf-v1` 键重复赋值（L24/L163）；
   - 若干 `no` 行的说明列仍填版本号；text-input-v2/virtual-keyboard 被归入 external 节。
5. **NOTICE 历史引用**：所列 `src/output/gamma.c`、`src/render/shm_buffer.c` 在当前快照不存在（D-R1-05）。
6. **打包路径不一致**：portal 的 .service Exec 路径、D-Bus service 文件与 meson libexecdir 三处口径不一（D-R5-150）。
7. **i18n 口径差**：根 po/ 27 个 .po 但 LINGUAS 仅 16 语言；portal/po 19 个 .po 且 LINGUAS 仅 zh_CN（D-R1-06、D-R5-152）。

## 相关概念

- [源码信源登记](/references/source-code-map.md)
- [协议全景与私有协议族](/concepts/12-protocols.md)
- [构建、运行与打包](/concepts/01-build-run.md)
