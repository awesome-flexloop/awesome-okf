---
type: Concept
title: "插件系统：ABI 1.0、dlopen 加载器、hook 桥与唯一的 security 示例"
description: "拆解 kywc 外部 .so 插件的 ABI 契约、dlopen 加载规则、三类 hook 桥与 D-Bus 管理面，并说明 40 个特效为何全部静态编译"
tags: [plugin, dlopen, abi, dbus, security, extension]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r4
    resource: /references/facts-effect-plugin.md
    title: R4 特效/插件/安全簇事实清单
  - id: facts-r5
    resource: /references/facts-protocols-clients.md
    title: R5 协议/libkywc/portal/示例事实清单
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 源码信源登记与固定快照
---

> **本篇在数据流中的位置**：插件是合成器进程**内部**的扩展面——`.so` 被 dlopen 进主二进制，经 `kywc_*` 回调触达内部状态，与 [15 libkywc](/concepts/15-libkywc-clients.md) 那条「进程外稳定 ABI」路线互为对照。上游篇 [10 特效框架](/concepts/10-effects-framework.md) 讲静态特效链，本篇回答「外部插件到底能做什么、加载规则是什么、仓内有谁真的用了它」。

## 三层扩展 ABI 中的插件层

kywc 的扩展能力分布在三个稳定性不同的层面上（I-4 洞察）：

1. **内置静态层**：[10](/concepts/10-effects-framework.md) 讲的 40 个特效 `.c` 全部以 `wlcom_sources += files(...)` 静态编入主程序，没有任何一个以 `.so` 形式安装（F-R4-005）；
2. **外部插件层（本篇）**：dlopen 加载的 `.so`，ABI 硬编码 1.0，接口面很薄且高度偏向 security 用途；
3. **进程外客户端层**：[15](/concepts/15-libkywc-clients.md) 的 libkywc 67 个稳定 API。

理解本篇的第一结论是：插件机制真实存在、契约完整，但 src/ 主程序构建图内**唯一的 `shared_module` 是一个自认 "security demo" 的插件，而且不安装**（F-R4-016）；examples/meson.build:95 的 simple 插件示例同样是 shared_module 且 install:false。两处 `shared_module` 都不进发行安装，动效扩展的现实路径是改源码重编译，而不是丢一个 `.so` 进插件目录。

## 插件契约：一个必须导出的数据符号

插件契约全部写在公共头 [include/kywc/plugin.h](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/include/kywc/plugin.h)。一个合法插件只需：

- 导出名为 `<name>_plugin_data` 的 `struct kywc_plugin_data` 符号（头注释原文："plugins need export this data symbol: xxx_plugin_data"，F-R4-028，plugin.h:123-133）。加载器按文件名去掉 `.so` 后用 `"%s_plugin_data"` 拼符号名 dlsym（F-R4-038，src/plugin/plugin.c:252-259）；
- 提供 `info / options / setup / option / teardown` 五字段，其中 options 与 option 允许为 NULL（plugin.h:127-133）；
- setup/teardown 不能为空，否则判无效（F-R4-039，plugin.c:260-266）。

版本相关宏（F-R4-019、F-R4-020，plugin.h:14-24）：插件自身版本用 `PLUGIN_VERSION_NUMERIC(major,minor,micro)` 打包；接口兼容性用 `ABI_VERSION(maj,min)`（高 16 位 major、低 16 位 minor），`GET_ABI_MAJOR/MINOR` 解包。

`struct kywc_plugin_info` 7 字段（F-R4-023，plugin.h:35-44）：`name / vendor / class / description / version / abi_version / flags`。vendor 缺省串是 `"KylinSoft Multimedia"`（F-R4-021），flag 目前只有一位 `KYWC_PLUGIN_FIXED = 1 << 0`——运行时禁止 disable（F-R4-022，plugin.h:31-33）。

### 选项模型（以源码为准）

选项值是一个 4 成员联合 `option_value`（plugin.h:46-51）：

```c
typedef union {
    int32_t num;
    const char *str;
    double realnum;
    bool boolean;
} option_value;

typedef enum {
    option_type_null = 0,
    option_type_boolean,
    option_type_double,
    option_type_int,
    option_type_string,
} option_type;
```

`struct kywc_plugin_option` 含 `name / value / type / token` 四字段，token 是 int32 选项标识，头注释限定单个插件最多 64 个选项（F-R4-026、F-R4-028）。插件运行时经 `kywc_plugin_get_option_boolean/double/int/string` 四具名取值器读值（plugin.h:99-105）。三个回调 typedef 分别是 setup（每次 enable）、teardown（每次 disable）、option（运行时应用单个选项）（F-R4-027，plugin.h:111-121）。

## kywc_plugin_interface：15 个函数指针 + 2 个数据字段 + 3 个 hooks

插件向合成器要能力，不靠链接期符号，而是 setup 时调用 `const struct kywc_plugin_interface *kywc_plugin_get_interface(void *plugin);`（plugin.h:200，入参即加载器传给 setup 的 plugin 句柄）取回一张按需 calloc、缓存在 `struct plugin` 上的接口表（src/plugin/interface.c:160-198）。

接口表 `struct kywc_plugin_interface`（plugin.h:155-198）按职责分组：

| 组 | 字段 | 行号 |
|---|---|---|
| 数据 | `struct wl_display *display`、`uint32_t abi_version` | :157-158 |
| hook | `set_hooks(plugin, hooks)` | :160 |
| 全局过滤 | `security_add_global_filter`、`security_remove_global_filter` | :162-166 |
| 仲裁对象创建 | `security_view_create`、`security_output_create`、`security_selection_create` | :168-179 |
| 对象数据/生命周期 | `security_set_user_data`、`security_get_user_data`、`security_set_decision`、`security_ref`、`security_unref` | :181-189 |
| protector | `security_set_protector_mode`、`security_set_protector_color(r,g,b,a)`、`security_set_protector_image(w,h,data)` | :191-195 |
| seat | `get_default_seat(void)` | :197 |

合计 **2 个数据字段 + 15 个函数指针**（F-R4-030）。另外 `struct kywc_plugin_hooks` 有 3 个入向钩子：`new_view`、`new_output`、`layout_damage`（F-R4-029，plugin.h:140-144）。插件还可直接调用主程序导出的 `kywc_*` 内联/函数 API（如 `kywc_key_binding_create`），这条符号通道由主程序的版本脚本保障，见 [15](/concepts/15-libkywc-clients.md) 与 F-R5-009/F-R5-010。

> **差异块：接口表两处静态读码风险点（不做运行时判定）**
>
> 1. **`security_set_decision` 声明了但从未被赋值**。头文件 plugin.h:185 有该字段，但 interface.c:178-195 的填充段没有对应一行（F-R4-050、F-R4 疑点 6）。calloc 后该指针保持 NULL，插件若调用它取决于调用侧是否做了 NULL 检查。
> 2. **接口表里的 `abi_version` 取自插件自己**：interface.c:175 写的是 `interface->abi_version = p->info->abi_version`，而非管理器的 1.0。静态事实如此，其语义影响本篇不替上游定性。

## 加载器：只收 .so、单层扫描、ABI major 相等且 minor 不得更高

加载器实现在 [src/plugin/plugin.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/plugin/plugin.c)，规则全部是硬编码：

- **后缀门**：只接受 `.so`，大小写不敏感（`strcasecmp`），插件名取文件名去掉后缀（F-R4-033、F-R4-034，plugin.c:20-29、46-47）；
- **目录门**：`scan_all_plugins` 对编译期宏 `PLUGIN_DIR` 做**单层**目录扫描，不递归（F-R4-035，plugin.c:75-85）；
- **dlopen 标志**：`RTLD_NOW | RTLD_GLOBAL`，注释明示 RTLD_NOW 用于立即校验插件内符号；失败置 `invalid=true`（F-R4-037，plugin.c:243-249）；
- **符号门**：dlsym `<name>_plugin_data`，pdata/info/setup/teardown 任一为空即无效（F-R4-038、F-R4-039）；
- **ABI 门**：`major != manager.major || minor > manager.minor` 即拒绝（F-R4-040，plugin.c:268-277）。管理器 ABI 在 plugin_manager_create 中**硬编码 1.0**（F-R4-041，plugin.c:333-334），因此当前实际上只接受 ABI 1.0 的插件——注释 "major equal and minor not older" 比实现更宽松（F-R4 疑点 5）；
- **配置门**：FIXED flag 强制加载；否则查持久化配置，`plugin_need_load` 缺省返回 true（F-R4-042）。

创建顺序是「先扫描目录、再按链表顺序逐个 load + enable」，加载失败立即 unload；setup 在合并选项之后调用，卸载按 teardown → dlclose 收尾（F-R4-043，plugin.c:295-296、390-408）。另存在重扫描入口 `plugin_manager_rescan_plugin`（F-R4-036，plugin.c:87-90）。

插件目录来自 meson 选项 `plugin_directory`，空值回退 `<prefix>/lib/kylin-wlcom/plugins`，经 `-DPLUGIN_DIR="..."` 注入编译（F-R4-018，meson.build:99-103）。

## hook 桥：3 个挂点、引用计数、一个缺 break 的分支

[src/plugin/interface.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/plugin/interface.c) 把合成器内部信号桥成插件 hook。挂点枚举只有 3 个真实点加 LAST 哨兵：`NEW_VIEW / NEW_OUTPUT / LAYOUT_DAMAGE`（F-R4-044，src/plugin/plugin_p.h:10-21）。

工作机制：

- 分发器遍历所有 `loaded && enabled && hooks` 的插件，按 `hook->point` switch 调对应非空函数指针（F-R4-045，interface.c:14-45）；
- 三个挂点分别接到 `kywc_view_add_new_listener`、`output_manager_add_new_enabled_listener`、`output_manager_add_layout_damage_listener`（F-R4-047，interface.c:91-103）；
- 每个挂点带引用计数，允许多个插件订阅同一点，计数归零才摘除监听（F-R4-048，interface.c:67-104）；
- `set_hooks` 每插件只生效一次，已有 hooks 直接返回（F-R4-049，interface.c:126-135）。

> **差异块：LAYOUT_DAMAGE 分支缺 break（F-R4-046，interface.c:37-42）**
>
> `case PLUGIN_HOOK_LAYOUT_DAMAGE` 调完 `layout_damage(data)` 后没有 `break;`，直接落入 `default: break;`。当前 default 为空，功能上无差异，属于风格/告警层面的可疑写法（编译选项含 `-Wimplicit-fallthrough=2`），静态读码到此为止，不推断运行时影响。

## D-Bus 管理面：/com/kylin/Wlcom/Plugin 的 6 个方法

插件配置面在 [src/plugin/config.c](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/src/plugin/config.c)：对象路径 `/com/kylin/Wlcom/Plugin`、接口 `com.kylin.Wlcom.Plugin`（F-R4-051，config.c:10-11）。vtable 暴露 6 个方法且**全部带 `SD_BUS_VTABLE_UNPRIVILEGED`**（F-R4-052，config.c:241-250）：

| 方法 | 入参 → 出参 |
|---|---|
| ListAllPlugins | `b` → `a(sbb)` |
| PrintPluginInfo | `s` → `sssuu` |
| PrintPluginConfig | `s` → `s` |
| LoadPlugin | `sb` → — |
| EnablePlugin | `sb` → — |
| SetPluginOption | `ssv` → — |

持久化配置节名为 `"plugins"`，JSON 结构 `{enabled, options}`（F-R4-053）。FIXED 插件拒绝 unload 与 disable（F-R4-054，config.c:132-136、162-166）。另注意 SetPluginOption 非 string 分支写作 `entry->option.value.str = opt.value.str;`，依赖 union 共享存储（F-R4-055，config.c:229，F-R4 疑点 11）。

## 构建边界：40 特效静态、src/ 内唯一 shared_module 且 install:false

这是评估插件机制成熟度时最关键的一组事实：

- src/effect 下 40 个特效 `.c` 全部静态编入 `wlcom`，无一带插件化安装路径；其中 34 个无条件编译，screenshot/watermark/slide/ukui_effect 4 个受各自 `have_ukui_*/have_kde_slide` 门控，另有 ky_capture.c、ky_stream.c 两个无条件块（F-R4-002、F-R4-005~011）；
- src/plugin 的 config.c/interface.c/plugin.c 编入主程序（F-R4-013）；
- src/plugin/security 下的 security 插件是 **src/ 主程序构建图内唯一 `shared_module`**：`shared_module('security', …, name_prefix:'', install_dir: plugindir, install:false)`，产物名 security.so；同目录的 gui 可执行文件同样 `install:false`（F-R4-016，src/plugin/security/meson.build:86-95、57-64）；
- examples/meson.build:95 的 simple 插件示例是仓内第二个 `shared_module`（name_prefix:''、install:false），仅作可 dlopen 形态的演示，同样不安装；
- 该插件构建依赖 C++ 与 Qt5（Core/Gui/Widgets 及 Gui 私有头），缺任一依赖即 `subdir_done()` 整个跳过——但这不影响 src/security 内置安全子系统，后者无条件编译（F-R4-014、F-R4-017）。

> **部署缺口（F-R4 疑点 3，静态读码）**：运行时加载器只扫描 PLUGIN_DIR（plugin.c:75-85），而 security 这个唯一的 FIXED 插件 `install:false`，默认安装产物中没有东西把它放进插件目录；开发态构建树能否被扫描到未经验证。这意味着「安装即用的外部插件」在当前提交上没有闭环样本。

## include/kywc/ 公共头地图：7 个头

插件与主程序共享的稳定面集中在 include/kywc/ 下共 7 个公共头（F-R4-173~179）：

| 头 | 内容 |
|---|---|
| plugin.h | 本篇全部插件契约 |
| view.h | role 17 枚举器、capabilities 12 位、23 个 events 信号、kywc_view 与监听 API |
| output.h | 8 组输出能力/状态枚举、kywc_output_state/prop 与 8 个输出函数 |
| binding.h | key_binding_type 20 个实际类型、快捷键/手势绑定 API |
| boxes.h | int/float 两种 box 与内联几何工具（`KYWC_API` 为 static inline） |
| identifier.h | UUID_SIZE=37，generate/time/rand/uuid/md5/base64 共 8 函数 |
| log.h | 6 个日志级别加 SILENT/LAST |

这些头里声明的 `kywc_*` 函数由主程序经 `export_dynamic: true` + 版本脚本 wlcom.syms 导出（`global: kywc_*; local: *;`），dlopen 的插件可直接解析（F-R5-009、F-R5-010）。security 插件与 examples/simple_plugin 都实际这样调用（F-R5-126）。

## 唯一的真实样本：security demo 插件

[src/plugin/security/](https://gitee.com/openkylin/kylin-wayland-compositor/tree/4df656222427f3cd0101e41d828fb64805e66c15/src/plugin/security) 给出了插件契约的完整用法（安全语义细节见 [14](/concepts/14-security-portal.md)）：

- 导出 `security_plugin_data`，name="security"、class="security"、description="security demo"、version 1.0.0、`ABI_VERSION(1,0)`、`KYWC_PLUGIN_FIXED`（F-R4-056，security.c:504-520）；
- setup 里注册快捷键 "Alt+Shift+d:no"（描述 "Show security gui"），经 `kywc_plugin_get_interface(plugin)` 取接口、`set_hooks` 订阅 new_view、`security_add_global_filter` 限制自定义 global 仅对 gui 进程可见、创建 SOFT_DENY selection 仲裁，并 `wl_global_create` 注册第 35 个 XML 协议 `kywc_security_configuration_v1`（F-R4-057、F-R4-063，security.c:452-467、481-486）；
- GUI 是一个被 memfd_create + 双 fork + setsid 从内存中启动的 Qt5 程序，Wayland 连接经 socketpair + `WAYLAND_SOCKET` 传入（F-R4-058、F-R4-059，security.c:51-135；构建期整体 embed 为 gui_exe.h，F-R1-162）。

## 给二开者的现实路径建议

结合 I-4 的行动结论：

1. **要加窗口/场景动效** → 进 src/effect 照 40 个范例加一个静态 `.c` 并挂到 meson，这是唯一有充分样例的路径（见 [10](/concepts/10-effects-framework.md) 与 [示例走读 01](/examples/01-effect-plugin-walkthrough.md)）；
2. **要在进程外消费合成器能力（截图、流、窗口/工作区管理）** → link libkywc 或裸连协议，见 [12](/concepts/12-protocols.md)、[15](/concepts/15-libkywc-clients.md)；
3. **确实要写外部 `.so`** → 以 examples/simple_plugin.c 为模板（导出 `<name>_plugin_data`、ABI_VERSION(1,0)、只依赖 include/kywc/ 头），但需自行解决「安装到 PLUGIN_DIR」这一仓内没有先例的部署环节，并接受接口面偏向 security、ABI 停在 1.0 的现实。[示例走读 01](/examples/01-effect-plugin-walkthrough.md) 对 simple_plugin 的注册过程有逐步拆解。

## 相关概念

- [10 特效框架：40 个静态特效与 effect 链](/concepts/10-effects-framework.md)
- [14 安全模型与 xdg-desktop-portal-wlcom](/concepts/14-security-portal.md)
- [15 libkywc 客户端库、示例生态与自带工具](/concepts/15-libkywc-clients.md)
- [12 协议全景：34 个 XML 与编译期裁剪](/concepts/12-protocols.md)
- [示例走读 01：插件与特效](/examples/01-effect-plugin-walkthrough.md)
