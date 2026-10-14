---
okf_version: "0.2"
type: bundle
title: "kylin-wayland-compositor 源码中文教程"
description: "openKylin 默认 Wayland 合成器 kywc（kylin-wlcom）基于 wlroots 0.17 的架构精读：启动、后端、渲染、场景、输出、输入、视图工作区、特效、插件、协议、XWayland、安全门户与 libkywc 客户端库"
tags: [wayland, wlroots, openkylin, kylin-wlcom, compositor, graphics, linux-desktop]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 固定快照 4df6562
---

# kylin-wayland-compositor 源码中文教程

**kylin-wayland-compositor**（可执行名与简称 **kylin-wlcom / kywc**）是 openKylin 操作系统的默认 Wayland 显示服务器，基于 [wlroots](https://gitlab.freedesktop.org/wlroots/wlroots) 0.17 系列编写，主许可 GPL-1.0-or-later，随 openKylin 系统积极开发并默认发布。

本知识包是对固定提交 **`4df6562`**（2026-10-12，分支 openKylin/huanghe）的静态源码精读：465 个 C/H 文件、约 16.5 万行（165280 物理行）、15 个 `src/` 子系统、34 个协议 XML、40 个内置特效源文件。全部技术陈述可回溯到 [信源登记](references/source-code-map.md) 中的文件与行号；851 条编号事实见 references 层。

> **证据边界**：本束为静态源码学习，未在 DRM/openKylin 环境构建运行，未验证渲染效果与性能数据；README、docs/PROTOCOLS、ENV 等自陈内容均按「项目文档口径」标注，文档与代码不一致处集中保留为差异条目（见 [12 协议全景](concepts/12-protocols.md) 与 [项目文档登记](references/project-docs.md)）。

## 内容概览（concepts/，16 篇）

**入门与基础**

* [00 kywc 全景与学习路径](concepts/00-overview.md) — 定位、规模、分层架构与阅读路线
* [01 构建、运行与打包](concepts/01-build-run.md) — 依赖、meson 选项、CLI、环境变量、systemd 与 Debian 包
* [02 Wayland 与 wlroots 基础](concepts/02-wayland-wlroots-basics.md) — 合成器模型、unstable API、协议代码生成

**启动到上屏的图形主线**

* [03 启动序列与总体架构](concepts/03-startup-architecture.md) — main 启动链与 server 装配
* [04 后端层](concepts/04-backends.md) — DRM/fbdev/logind/EIS 与后端自动选择
* [05 渲染体系](concepts/05-rendering.md) — renderer、GBM、drm_syncobj、direct scanout、painter
* [06 场景图与 surface](concepts/06-scene-graph.md) — 三节点场景树、xdg_shell、损伤渲染
* [07 输出与多显示器管理](concepts/07-output-management.md) — 热插拔、配置编排、硬件色彩、五套输出协议

**输入与窗口**

* [08 输入系统](concepts/08-input.md) — libinput 独立线程、键盘/IME、指针/手势、绑定与动作
* [09 视图、工作区与窗口管理](concepts/09-view-workspace.md) — view 状态机、workspace、21 个窗口动作

**扩展面、兼容与外部接口**

* [10 特效框架与内置特效](concepts/10-effects-framework.md) — 17 钩子、transform 体系、40 特效与 shader
* [11 插件系统](concepts/11-plugin-system.md) — ABI 1.0、加载器与 security 示例
* [12 协议全景与私有协议族](concepts/12-protocols.md) — 34 XML/77 interface、六族协议与编译裁剪
* [13 XWayland 兼容层](concepts/13-xwayland.md) — rootless xwm 与选择/DND 桥
* [14 安全模型与门户](concepts/14-security-portal.md) — 安全四层、portal 五接口、PipeWire/EI
* [15 libkywc 客户端生态](concepts/15-libkywc-clients.md) — 67 个稳定 API、示例、工具与 i18n

## 实战走读（examples/，3 篇）

* [跟写一个特效插件](examples/01-effect-plugin-walkthrough.md) — simple.so 插件结构与最小骨架
* [wlu 工具库与协议客户端](examples/02-wlu-utilities-walkthrough.md) — 直连 Wayland 协议的四个小工具
* [libkywc + QML 缩略图客户端](examples/03-libkywc-qml-thumbnail.md) — 稳定客户端库与 Qt/QML 桥接

## 信源与事实（references/）

* [源码信源登记与固定快照](references/source-code-map.md) · [仓库自带文档登记](references/project-docs.md)
* 五份事实清单（R1-R5，共 851 条）与[架构洞察/知识地图](references/insights.md)
* [V 阶段独立验证报告](references/verification.md)

## 五个核心洞察（摘要）

1. **协议三态裁剪**：XML 存在 ≠ 编进二进制 ≠ 运行时 global 可 bind——44 个 meson 选项经 30+ 个 `HAVE_*` 宏控制协议面。
2. **钉死补丁化 wlroots**：`>=0.17,<0.18` 加 `WLR_USE_UNSTABLE`，Debian 依赖 openKylin 自打包的 `0.17.4-ok19`。
3. **输入绕开单线程模型**：libinput 独立线程 + 容量 64 的 SPSC 无锁队列 + eventfd 回主线程。
4. **扩展三层 ABI**：40 个特效静态编入主程序、外部插件 ABI 停在 1.0、真正稳定的外部面是 libkywc 的 67 个 `kywc_*` API。
5. **正确性来自六级回退链**：DRM→fbdev、atomic→legacy、GPU→pixman、GBM→dumb、direct scanout→swapchain、硬件色彩→GL blit。

## 建议阅读路径

- **想快速建立全局**：00 → 02 → 03 → 04 → 06 → 08。
- **图形栈方向**：04 → 05 → 06 → 07 → 10。
- **二开/集成方向**：10 → 11 → 12 → 15，配合 examples 三篇。
- **兼容与远程桌面方向**：13 → 14 → 08（IME/EIS 段）。

## 信任与生命周期

* 全部文档 `status: draft`、`stale_after: 2027-04-30`：上游处于活跃开发且依赖 wlroots unstable API，建议每半年或 openKylin 发版后复核。
* 事实由 5 个独立采集工作流分簇采集（R1-R5），经主会话计数闭合与独立 Review 复核；验证过程见 [verification.md](references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
