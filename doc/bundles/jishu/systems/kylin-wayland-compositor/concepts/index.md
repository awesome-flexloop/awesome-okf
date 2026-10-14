# 概念文档（Concepts）

16 篇概念文档按合成器数据流编号：全景与基础（00-02）→ 启动与后端渲染（03-07）→ 输入与窗口（08-09）→ 扩展面（10-12）→ 兼容与外部接口（13-15）。

| 编号 | 文档 | 主题 |
|---|---|---|
| 00 | [kywc 全景与学习路径](00-overview.md) | 项目定位、规模口径、分层架构与 16+3 篇学习路线 |
| 01 | [构建、运行与打包](01-build-run.md) | 依赖、44 个 meson 选项、CLI、环境变量、双层配置、systemd 会话单元与 Debian 5 包 |
| 02 | [Wayland 与 wlroots 基础](02-wayland-wlroots-basics.md) | 合成器模型、unstable API、协议 XML 代码生成与 global 注册 |
| 03 | [启动序列与总体架构](03-startup-architecture.md) | main 函数级启动链、server_init 18 步装配与 D-Bus 方法 |
| 04 | [后端层](04-backends.md) | 后端自动选择、DRM KMS、fbdev、logind session、EIS 与 libinput 线程边界 |
| 05 | [渲染体系](05-rendering.md) | renderer 选择、GBM allocator、drm_syncobj timeline、direct scanout 与 painter |
| 06 | [场景图与 surface](06-scene-graph.md) | tree/rect/buffer 三节点、xdg_shell、装饰节点、损伤与场景渲染 |
| 07 | [输出与多显示器管理](07-output-management.md) | 热插拔、配置编排、硬件色彩三通道与五套输出协议汇聚 |
| 08 | [输入系统](08-input.md) | SPSC 输入队列、seat、键盘/IME、指针/触摸/手势、绑定与动作分发 |
| 09 | [视图、工作区与窗口管理](09-view-workspace.md) | view 状态机、workspace、21 个窗口动作、各家 shell 接线与 widget |
| 10 | [特效框架与内置特效](10-effects-framework.md) | 17 钩子、动画时钟、transform 体系、40 个内置特效与 14 个 shader |
| 11 | [插件系统](11-plugin-system.md) | ABI 1.0 契约、dlopen 加载器、hook 桥与 security 示例插件 |
| 12 | [协议全景与私有协议族](12-protocols.md) | 34 XML/77 interface、六族协议、三态编译裁剪与双源差异表 |
| 13 | [XWayland 兼容层](13-xwayland.md) | rootless 进程模型、xwm、atom/_NET_WM、INCR/Xdnd 选择桥 |
| 14 | [安全模型与门户](14-security-portal.md) | 安全四层仲裁、xdg-desktop-portal-wlcom 五接口、PipeWire 与 EI |
| 15 | [libkywc 客户端生态](15-libkywc-clients.md) | 67 个稳定 API、provider 能力位、示例、自带工具与 i18n |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-build-run
02-wayland-wlroots-basics
03-startup-architecture
04-backends
05-rendering
06-scene-graph
07-output-management
08-input
09-view-workspace
10-effects-framework
11-plugin-system
12-protocols
13-xwayland
14-security-portal
15-libkywc-clients
```
