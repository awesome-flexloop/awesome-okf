---
type: Reference
title: "kylin-wayland-compositor 源码信源登记与固定快照"
description: "kywc 知识包的唯一代码信源：Gitee openKylin 官方仓库固定提交 4df6562，含版本、规模口径、目录地图与外部链接规则"
tags: [wayland, wlroots, openkylin, kylin-wlcom, source-map, provenance]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: kywc-repo
    resource: https://gitee.com/openkylin/kylin-wayland-compositor
    title: openKylin kylin-wayland-compositor 官方仓库
    last_modified: 2026-10-12
---

# kylin-wayland-compositor 源码信源登记与固定快照

本束全部代码事实的唯一代码信源为 openKylin 官方 Gitee 仓库的一次固定提交。教程所有技术陈述均可回溯到该快照的文件与行号。

## 固定快照四要素

| 项 | 值 |
|---|---|
| 远程仓库 | https://gitee.com/openkylin/kylin-wayland-compositor.git |
| Web 入口 | https://gitee.com/openkylin/kylin-wayland-compositor |
| 固定提交（全 hash） | `4df656222427f3cd0101e41d828fb64805e66c15` |
| 短 hash | `4df6562` |
| 分支 | `openkylin/huanghe` |
| 提交时间 | 2026-10-12 21:07:53 +0800（Weblate 傣仂文 khb_CN 翻译提交） |
| `git describe` | `build/1.3.1-ok21-761-g4df65622`（在构建标签之后 761 个提交） |
| meson 工程版本 | `1.3.0`（meson.build `project(... version: '1.3.0')`） |
| Debian changelog 顶端 | `1.3.1-ok36`（huanghe，2026-09-04；75 个版本条目） |
| 主许可 | GPL-1.0-or-later；单文件另有 LGPL-2.1-or-later、MIT-CMU、MulanPSL-2.0（见仓库 LICENSES/） |

**为何固定 commit 而非 release tag**：仓库标签是 Debian 构建标签（`build/1.3.1-ok21` 等），HEAD 在其之后 761 个提交，无可覆盖本教程引用集合（协议矩阵、EIS、portal、libkywc 当前 API）的正式 release tag；按「文档引用集合 ∩ 版本变更集合 = ∅」判据，固定精确 commit hash，并同时记录远程 URL、分支与日期。

**外部源码链接规则**：本束正文引用源码一律使用固定 hash 的 Gitee blob 地址：

```text
https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/<path>#L<a>-L<b>
```

不使用分支名 HEAD 链接（会随上游前进漂移）；事实清单（facts-*.md）内的 `路径:行号` 均相对该快照根目录。

## 规模口径（2026-10-14 主会话脚本实测）

| 指标 | 值 | 口径 |
|---|---|---|
| 全仓 *.c/*.h | 465 个 | 递归 Get-Childier -Include，无 build/ 检出 |
| 全仓物理行数 | 165280 行 | python 物理行口径（字节 LF 165276 + 4 个无尾换行文件补 1）。勘误：R 阶段 PowerShell `Get-Content \| Measure-Object -Line` 得 138417，V 阶段证实该 cmdlet 对字符串数组系统性少计（view.c 3022→2578），以 165280 为准 |
| `src/` | 283 个 C/H | 15 个子系统目录 281 + 根 main.c、server.c 2 |
| `libkywc/` | 17 个 C/H | 13 .c + 4 .h；67 个非 static `kywc_*` 导出 |
| `portal/` | 14 个 C/H | 11 .c + 3 .h |
| `examples/` | 34 个 C/C++/H | 14 .c + 14 .cpp + 6 .h |
| `protocols/*.xml` | 34 个 / 77 个 interface | 另有仓内第 35 个 XML：src/plugin/security/security.xml |
| 内置特效 .c | 40 个 | 36 无条件编译 + 4 条件编译（screenshot/watermark/slide/ukui_effect） |
| 特效 shader | 14 个（7 对 vert/frag） | src/effect/shaders/；DRM shader 另 4 个 |
| meson 选项 | 44 个 | 37 boolean + 3 feature + 4 string |
| po 翻译 | 主 po/ 27 个 .po；LINGUAS 16 语言 | portal/po 为独立翻译域 19 个 .po |

## 顶层目录地图

| 目录/文件 | 角色 | 对应概念文档 |
|---|---|---|
| `src/main.c`、`src/server.c` | 进程入口与 server 装配（292/432 行） | [03 启动与总体架构](/concepts/03-startup-architecture.md) |
| `src/backend/`（34 C/H） | wlroots 后端：drm/fbdev/session(logind)/libinput/eis | [04 后端层](/concepts/04-backends.md) |
| `src/render/`（26） | renderer/allocator/EGL/pixman/pass/drm_syncobj | [05 渲染体系](/concepts/05-rendering.md) |
| `src/scene/`（17） | 场景树、surface、xdg_shell、装饰与图形节点 | [06 场景图](/concepts/06-scene-graph.md) |
| `src/output/`（13） | 输出发现/配置/热插拔/五套输出协议 | [07 输出管理](/concepts/07-output-management.md) |
| `src/input/`（35） | seat/键盘/指针/触摸/平板/手势/IME/binding | [08 输入系统](/concepts/08-input.md) |
| `src/view/`（42，含 tile/） | view 状态机、workspace、窗口菜单、各家 shell | [09 视图与工作区](/concepts/09-view-workspace.md) |
| `src/widget/`（4）、`src/theme/`（5）、`src/util/`（24） | 菜单 widget、主题、基础设施（SPSC 队列等） | [08](/concepts/08-input.md)/[09](/concepts/09-view-workspace.md) |
| `src/effect/`（41 C/H + 14 shader） | 特效框架与 40 个内置特效 | [10 特效框架](/concepts/10-effects-framework.md) |
| `src/plugin/`（9 文件） | 动态插件加载器与唯一 security 示例插件 | [11 插件系统](/concepts/11-plugin-system.md) |
| `src/security/`（6）、`src/config/`（9）、`src/painter/`（4） | 内置安全四层、配置适配、CPU 绘图 | [14 安全与门户](/concepts/14-security-portal.md)/[01 构建运行](/concepts/01-build-run.md)/[05 渲染](/concepts/05-rendering.md) |
| `src/xwayland/`（16） | rootless XWayland 与 xwm | [13 XWayland](/concepts/13-xwayland.md) |
| `protocols/`（34 XML） | 六族协议定义与 wayland-scanner 生成 | [12 协议全景](/concepts/12-protocols.md) |
| `libkywc/`（17 C/H） | 进程外稳定客户端库（capture/stream/thumbnail/toplevel/workspace） | [15 libkywc 客户端生态](/concepts/15-libkywc-clients.md) |
| `portal/`（14 C/H + data） | xdg-desktop-portal-wlcom（5 个 impl 接口） | [14 安全与门户](/concepts/14-security-portal.md) |
| `examples/`（34 文件） | 插件示例、wlu 工具库、QML 缩略图 GUI、9 个独立示例 | [examples/](/examples/index.md) |
| `data/`、`debian/`、`tools/`、`po/` | systemd/udev/桌面入口、5 个二进制包、wlcctrl/wldialog/放大镜、i18n | [01 构建运行](/concepts/01-build-run.md)/[15 客户端生态](/concepts/15-libkywc-clients.md) |

## 证据边界

- 本束为**静态源码学习**：未在 openKylin/DRM 环境构建运行该提交、未执行其测试、未验证渲染效果与性能数字；README/docs/PROTOCOLS 的自陈能力一律按「项目文档口径」标注。
- `wlr_*`、`libinput_*`、`xkb_*` 等为外部库符号，事实只记录 kywc 调用点；外部库行为以 wlroots 0.17 系列公开 API 为准，受 [架构洞察 I-2](/references/insights.md) 所述 openKylin 补丁后缀约束。

## 相关概念

- [项目文档信源登记](/references/project-docs.md)
- [架构洞察与知识地图](/references/insights.md)
- [项目全景与学习路径](/concepts/00-overview.md)
