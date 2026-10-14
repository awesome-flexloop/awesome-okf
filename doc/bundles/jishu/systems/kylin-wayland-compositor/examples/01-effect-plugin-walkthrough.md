---
type: Example
title: "跟写一个特效插件：simple_plugin / alpha_modifier / kde_keystate 走读"
description: "逐行走读 examples 下三个示例的真实身份：simple_plugin 是全树仅有的外部 .so 插件样例，另两个是独立 Wayland 客户端可执行文件，对照插件契约与静态特效路径"
tags: [kylin-wlcom, plugin, shared-module, key-binding, wayland-client, walkthrough]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: facts-r4
    resource: /references/facts-effect-plugin.md
    title: R4 特效/插件/安全事实清单
  - id: facts-r5
    resource: /references/facts-protocols-clients.md
    title: R5 协议/libkywc/portal/示例事实清单
  - id: facts-r1
    resource: /references/facts-build-startup.md
    title: R1 构建/启动/配置/打包事实清单
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 固定快照 4df6562
---

> **本篇在教程中的位置**：本篇是实战篇的第 1 篇，跟读 `examples/` 里与插件/私有协议有关的三个 C 示例。前置概念请先读 [11 插件系统](/concepts/11-plugin-system.md)（插件 ABI、加载器、D-Bus 配置）与 [10 特效框架](/concepts/10-effects-framework.md)（40 个内置特效为什么是静态编译）；本篇只"跟代码走"，不重复机制讲解。所有行号锚定固定提交 `4df6562`。

## 先厘清身份：三个示例里只有一个是插件

标题把三个文件并列，但读完 [examples/meson.build](https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df656222427f3cd0101e41d828fb64805e66c15/examples/meson.build) 必须先纠正一个暗示：**它们不是同一类东西**。

- `examples/meson.build:77-91` 是一个 `foreach` 循环，把字典里的 8 个条目（output-doctor、virtual-desktop、monitor、ukui-effect-test、thumbnail、kde_keystate、alpha_modifier、pipewire）全部声明为 `executable(...)`，`build_by_default: true`，且**没有** `install: true`。
- 循环结束、`subdir('gui')` 之后，`examples/meson.build:95-103` 单独声明了全文件唯一的 `shared_module`：

```meson
# examples/meson.build:95-103
shared_module(
  'simple',
  'simple_plugin.c',
  name_prefix: '',
  include_directories : wlcom_inc,
  install_dir: plugindir,
  install: false
)
```

即：`simple_plugin.c` 编译产物是 `simple.so`（`name_prefix: ''` 去掉默认的 `lib` 前缀），是唯一按"可被合成器 dlopen 的插件"形态构建的示例；而 `alpha_modifier.c`、`kde_keystate.c` 各自带 `main()`，是普通的 Wayland **客户端可执行文件**，只是演示的协议与合成器侧能力相邻。这与 R4 的全树口径一致：src 树里唯一的另一个 `shared_module` 是 security 插件（src/plugin/security/meson.build:86-95，F-R4-016），40 个内置特效则全部静态编入 `kylin-wlcom`（F-R4-005）。

## simple_plugin.c 走读：一个插件的完整骨架

文件只有 177 行，结构是教科书式的五段。

### 插件信息与选项表

`simple_plugin_info`（examples/simple_plugin.c:12-19）填充 `struct kywc_plugin_info` 的 7 个字段，注意它**没有**设置 `flags`，即不是 `KYWC_PLUGIN_FIXED` 插件，运行时允许被 disable：

```c
// examples/simple_plugin.c:12-19
static struct kywc_plugin_info simple_plugin_info = {
    .name = "simple",
    .vendor = PLUGINVENDORSTRING,
    .class = "example",
    .description = "A simple plugin example",
    .version = PLUGIN_VERSION_NUMERIC(1, 0, 0),
    .abi_version = ABI_VERSION(1, 0),
};
```

选项表 `simple_plugin_options`（:21-27）给出 4 种类型各一个示例，末行以 `{ NULL, { 0 }, option_type_null, -1 }` 哨兵收尾。这里要以头文件为准纠正一个易记混的点：`option_value` 联合的成员名是 `num / realnum / boolean / str`（include/kywc/plugin.h:46-51），不是 `i/f`；`option_type` 枚举 5 值为 `null/boolean/double/int/string`（plugin.h:53-59）。

### 快捷键与手势：插件如何消费合成器 ABI

插件不是只能被动收事件。:29-40 的 `shortcuts[]` 定义 6 个字符串绑定（`Alt+t`、`Ctrl+t`、`Win+t` 及其 Shift 变体），:42-54 的 `gestures[]` 定义 7 条手势串（pinch/swipe，设备位 any/touch/touchpad）。注册发生在 `simple_plugin_register_shortcuts`（:73-107）：对每条绑定调 `kywc_key_binding_create(keybind, desc, FUNC_ID_CUSTOM, 0)`（:77-78），成功后 `kywc_key_binding_register(binding, KEY_BINDING_TYPE_CUSTOM_DEF, shortcut_action, shortcut)`（:83-84）；手势侧对应 `kywc_gesture_binding_create_by_string`（:95-96）与 `kywc_gesture_binding_register`（:101）。任一注册失败都走 destroy 回滚（:85、:102）。

回调本身只做一件事——打印描述串：`shortcut_action`（:56-62）签名带 `struct seat *` 与 `enum key_binding_stage`，`gesture_action`（:64-71）带 stage/device/方向/dx/dy。这些 `kywc_*` 符号由主程序经版本脚本导出（wlcom.syms 为 `global: kywc_*;`，F-R5-009/010），插件不链接任何库，dlopen 时从主程序解析。

### setup / option / teardown 三个生命周期回调

- `simple_plugin_setup`（:127-148）：加载时由合成器调用。它用四个 `kywc_plugin_get_option_*` 助手回读合并后的选项值（:133-143，声明见 include/kywc/plugin.h:99-105），再调注册函数。
- `simple_plugin_option`（:150-162）：运行时通过 D-Bus `SetPluginOption` 改值时回调，按 `option->type` 分支打印。
- `simple_plugin_teardown`（:164-169）：卸载时调 `simple_plugin_unregister_shortcuts`（:109-125）逐个销毁绑定。

### 唯一必须导出的符号

文件末尾导出数据符号（:171-177），名字严格等于 `<文件名去 .so>_plugin_data`：

```c
// examples/simple_plugin.c:171-177
struct kywc_plugin_data simple_plugin_data = {
    .info = &simple_plugin_info,
    .options = simple_plugin_options,
    .setup = simple_plugin_setup,
    .option = simple_plugin_option,
    .teardown = simple_plugin_teardown,
};
```

加载器不猜函数名：src/plugin/plugin.c 按 `"%s_plugin_data"` 拼出符号名再 `dlsym`（F-R4-038），并要求 `info/setup/teardown` 非空（F-R4-039）。所以产物文件名必须叫 `simple.so`——改成别的名字，导出符号也要跟着改。

## 契约对照：include/kywc/plugin.h 的真实字段

照抄之前先认全头文件（本节字段均经本次逐行核对）：

| 契约件 | 位置 | 内容 |
|---|---|---|
| 版本宏 | include/kywc/plugin.h:14-24 | `PLUGIN_VERSION_NUMERIC`、`ABI_VERSION(maj,min)` 及解包宏 |
| 厂商标识 | :27-29 | `PLUGINVENDORSTRING` 默认 `"KylinSoft Multimedia"` |
| 插件 flag | :31-33 | 仅 `KYWC_PLUGIN_FIXED = 1 << 0` |
| 信息结构 | :35-44 | `kywc_plugin_info` 7 字段 |
| 选项 | :46-66 | `option_value` 联合、`option_type` 5 值、`kywc_plugin_option` 4 字段（token 为 int32 标识） |
| 回调 typedef | :111-121 | setup/teardown/option 三个函数指针类型 |
| 导出数据 | :127-133 | `kywc_plugin_data`：info/options/setup/option/teardown，注释注明最多 64 个选项 |
| 事件钩子 | :140-144 | `kywc_plugin_hooks`：`new_view`、`new_output`、`layout_damage` |
| 宿主接口 | :155-198 | `kywc_plugin_interface`：2 个数据字段（`display`、`abi_version`）+ 15 个函数指针 |

15 个接口函数指针的顺序是：`set_hooks`，security 系 11 个（add/remove_global_filter、view/output/selection_create、get/set_user_data、set_decision、ref/unref、set_protector_mode/color/image），以及 `get_default_seat`（plugin.h:160-197）。simple_plugin 一个都没调用——它演示的是"自包含插件"；要用宿主能力时通过 `kywc_plugin_get_interface(void *plugin)`（plugin.h:200）取接口表。security 插件是这套接口的唯一完整使用者（F-R4-056 至 F-R4-065）。

## 加载侧约束：.so 后缀、ABI 1.0、PLUGIN_DIR

写好插件后，能否被加载由 src/plugin/plugin.c 决定（F-R4-033 至 F-R4-043）：

1. 只扫描 `PLUGIN_DIR` 单层目录，且文件后缀必须是 `.so`（大小写不敏感）；
2. `dlopen` 用 `RTLD_NOW | RTLD_GLOBAL`，符号在加载时就要全部解析到；
3. ABI 规则：major 必须与管理器相等，插件 minor 不得高于管理器；管理器 ABI 在本快照硬编码为 **1.0**（F-R4-040/041），所以示例填 `ABI_VERSION(1, 0)` 是唯一能通过校验的组合；
4. `PLUGIN_DIR` 由 meson 选项 `plugin_directory` 决定，空值回退 `<prefix>/lib/kylin-wlcom/plugins`，经 `-DPLUGIN_DIR` 编译注入（F-R4-018）。

一个必须知道的部署缺口：simple 插件的 `shared_module` 声明是 **`install: false`**（examples/meson.build:102），security 插件同样不安装（F-R4 疑点 3）。也就是说默认 `meson install` 后插件目录里没有它，开发态需要手动把构建树里的 `simple.so` 放进 PLUGIN_DIR，再通过 D-Bus `LoadPlugin` 或重启合成器加载。

## alpha_modifier.c：Wayland 客户端，不是插件

`alpha_modifier.c`（146 行，门控 `have_alpha_modifier`，examples/meson.build:60-68，依赖 libwlu + cairo）是一个带 `main()`（:110）的客户端，演示的是合成器在 src/scene/alpha_modifier.c 注册的 `wp_alpha_modifier_v1` 全局。走读路线：

1. `handle_global`（:56-63）在 registry 里按名匹配 `wp_alpha_modifier_v1_interface.name`，以 version 1 bind；
2. `handle_window_create`（:65-70）拿到 wlu 窗口的 `wl_surface` 后调 `wp_alpha_modifier_v1_get_surface`；
3. `handle_keyboard`（:72-99）响应 `=`/`-` 键，以 0.1 为步进改 `factor`，再 `wp_alpha_modifier_surface_v1_set_multiplier(surface, factor * UINT32_MAX)`（:95）——协议值是 0..UINT32_MAX 的定点倍率；
4. 绘制 `draw_frame`（:16-54）用 cairo 在 SHM 缓冲上画半透明蓝底与不透明方块，使 alpha 倍率肉眼可见。

## kde_keystate.c：77 行的键盘状态监听客户端

它同样是可执行文件（examples/meson.build:51-58，门控 `have_kde_keystate`，链接 kde-keystate 协议生成码），全文件仅 77 行：`wl_display_connect`（:48）→ registry bind `org_kde_kwin_keystate`（:35-38，注意这里直接用通告的 `version`，不做钳制）→ `org_kde_kwin_keystate_fetchStates()` 主动拉一次（:64）并 `add_listener` 订阅 `stateChanged`（:65）→ `wl_display_dispatch` 死循环打印（:67-71）。状态名表有 8 键 4 态（:14-16：capslock/numlock/scrolllock/alt/ctrl/shift/meta/right_alt × unlock/latched/locked/pressed），对应协议 v5（F-R5-017，服务端 src/input/kde_keystate.c:317）。

不要把它和 R1 里另一个带 `main()` 的文件搞混：src/config/qtkey_mapper.c 是**构建期代码生成器**（构建主机上执行，产出 Qt↔xkb 键映射表头，F-R1-086），与 examples/kde_keystate.c 这个运行时客户端毫无关系。

## 对比：内置 40 特效走的是静态编译路径

simple_plugin 演示的"薄插件 ABI"与动效扩展的现实路径形成对照（洞察 I-4，另见 [10 特效框架](/concepts/10-effects-framework.md)）：

| 维度 | 内置特效（src/effect/） | 外部插件（simple_plugin） |
|---|---|---|
| 构建形态 | 40 个 `.c` 全部 `wlcom_sources += files(...)` 静态编入主程序（F-R4-005/006） | `shared_module` 产物 `simple.so`，运行时 dlopen |
| 可用接口 | effect 框架内部 17 钩子（include/effect/effect.h:36-66，F-R4-098） | 仅 plugin.h 的 3 hooks + 15 interface 函数指针 |
| 注册方式 | 各 `*_effect_create` 在 effect_manager_create 固定顺序调用（F-R4-110） | 扫描 PLUGIN_DIR，按文件名导出符号加载 |
| ABI 承诺 | 无（内部实现，随版本变） | ABI 1.0，major 相等校验 |

想加一个"内置动效"，现实做法是进 src/effect 照 40 个范例加静态 `.c`；想在不改主二进制的前提下挂快捷键/手势或做安全决策，才走本篇的 `.so` 路线。

## 动手：照此改造一个最小插件的步骤骨架

1. 新建 `my_plugin.c`，`#include <kywc/plugin.h>`，需要按键/手势再加 `<kywc/binding.h>`；
2. 定义静态 `struct kywc_plugin_info`，`name` 与将来的文件名一致，`abi_version = ABI_VERSION(1, 0)`；
3. 选项可为 `NULL`；若提供，以 `option_type_null` 哨兵结束，token 在 0..63 内；
4. 实现 `bool setup(void *plugin, void **teardown_data)` 与 `void teardown(void *teardown_data)`——两者为必填，缺失会被判 invalid（F-R4-039）；`option` 回调可空；
5. 导出 `struct kywc_plugin_data my_plugin_data`（非 static）；
6. 仿 examples/meson.build:95-103 写 `shared_module('my', name_prefix: '', install_dir: plugindir)`；
7. 把 `my.so` 放入 PLUGIN_DIR（默认 `<prefix>/lib/kylin-wlcom/plugins`），经 D-Bus 接口 `com.kylin.Wlcom.Plugin` 的 `LoadPlugin`/`EnablePlugin` 控制（F-R4-051/052）。

以上每个名字都能在 include/kywc/plugin.h 或 simple_plugin.c 中命中；头文件未声明的接口不要凭印象调用。

## 构建与运行前置（本次未执行）

以下命令与现象**本次未执行**，仅给出经构建文件核对的前置条件：

- 在 openKylin 上准备 wlroots 0.17 系列 ok 系打包（依赖约束 `>=0.17.0,<0.18.0`，F-R1-008）及 wayland-client、cairo 等开发包；
- 配置时启用 examples：`meson setup build -Dexamples=true`（`examples` 为 boolean 选项，默认 true，F-R1-018/020）；examples/meson.build 还引用了 libkywc 子目录定义的依赖变量，静态阅读看 `-Dlibkywc=true`（默认即 true）需同时成立；
- alpha_modifier 额外要求 `-Dalpha_modifier=true`，kde_keystate 要求 `-Dkde_keystate=true`（均默认 true）；
- simple 插件不安装，需手动复制 `build/examples/simple.so` 到插件目录后再加载。

## 相关概念

- [11 插件系统](/concepts/11-plugin-system.md)：加载器、ABI 校验、D-Bus 配置与 FIXED 插件
- [10 特效框架](/concepts/10-effects-framework.md)：17 钩子、40 个静态特效与 effect D-Bus
- [15 libkywc 与客户端生态](/concepts/15-libkywc-clients.md)：另一条带稳定 ABI 承诺的扩展路线
- [R4 特效/插件/安全事实清单](/references/facts-effect-plugin.md)
- [R5 协议/libkywc/portal/示例事实清单](/references/facts-protocols-clients.md)
