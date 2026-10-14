---
type: Reference
title: "kywc 知识包 V 阶段独立验证报告"
description: "source-code-to-okf-wiki G4 验证记录：三道质量门、33 文档 dummy 构建、25 项符号 Grep、计数双口径复核、链接与路径纪律、facts 勘误台账"
tags: [verification, gate, review, provenance, openkylin]
generated: { by: "reference_agent/trae-solo", at: 2026-10-14T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00Z }
status: draft
stale_after: 2027-04-30
sources:
  - id: kywc-repo
    resource: /references/source-code-map.md
    title: kywc 固定快照 4df6562
---

# kywc 知识包 V 阶段独立验证报告

- **验证基准**：固定提交 `4df656222427f3cd0101e41d828fb64805e66c15`（远程 https://gitee.com/openkylin/kylin-wayland-compositor，分支 openkylin/huanghe，开工前与验证前各核一次 hash 一致、工作树干净）。
- **验证日期**：2026-10-14；**验证者**：主会话独立执行（独立于 5 个 R 采集与 4 个 E 撰写子代理的工具口径）。
- **束规模**：33 个 Markdown（束根 index+log、concepts 16+index、examples 3+index、references 9+index）。

## 1. 质量门（AC-1 / AC-6）

| 检查 | 命令（cwd=projects/awesome-okf-xs） | 结果 |
|---|---|---|
| 总索引三角计数 | `python scripts/check-bundles-index.py` | **rc=0**：「9 域 / 61 组 / 631 束，frontmatter、计数行、节标题、分组表、toctree 五面一致」 |
| UTF-8 编码 | `python scripts/check-utf8.py` | **rc=0**：11528 个文件均为有效 UTF-8（本束 33 文件含中文无 BOM） |
| toctree 完整性 | `python scripts/check-toctrees.py` | 全局 rc=1，红项 **27 处全部属于他束 WIP**（jishu/gui/tauri、jishu/ai 的 deepseek-harness/agent-self-evolution/microsoft-mxc、jishu/comm/wifit3、sheke/industry/ling-3-1/telecom-*）；过滤 `kylin-wayland-compositor` 关键词 **本束命中 0** |
| 束内 toctree 独立对账 | 自写脚本（spec 目录 check_bundle_toctree.py） | concepts 16=16、examples 3=3、references 9=9，根 toctree 4 目标全部存在；**BUNDLE TOCTREE PASS** |
| dummy Sphinx 构建（束定向） | `python -m sphinx -b dummy -E doc <tmp> bundles/jishu/systems/kylin-wayland-compositor/index.md` | **0 ERROR/WARNING**，`.doctrees` 生成本束 **33 个 .doctree**（16 concepts + 3 examples + 9 references + 根/子 index + log 全齐） |
| dummy Sphinx 构建（全工程） | `python -m sphinx -b dummy -E doc <tmp>` | exit 0；21 个 ERROR 全部位于他束 `jishu/ai/practice/ai-engineering-methodology/...`（「Document or section may not begin with a transition」），本束命中 **0** |

> **并行会话在途欠债归属说明**：验证期间目录树地面真值为 631 束（本任务开工基线 628），其中 +2 为并行会话新入库束（iot/hwe-bench 等）。总索引的分组表 ai/iot/gui/document 等计数已由并行会话更新且与目录树一致；主会话仅把 total/jishu 总计对齐地面真值（629 草稿值→631/468），未改动任何他束行内容。jishu/index.md 组首页中 ai(238)/document(7)/gui(5)/iot(8) 等组行计数落后于目录树（239/110/6/9），属他束在途欠债，不归属本任务，未代为修改；不影响 check-bundles-index（该校验以 doc/bundles/index.md 为准，已 rc=0）。

## 2. 零虚构符号核验（AC-2）

独立 Grep/Read 抽查 30 个高风险断言（跨 16 concept + 3 example），结果：

| 类别 | 抽查点 | 结果 |
|---|---|---|
| 启动/装配 | main() src/main.c:184；server_init/start/run include/server.h:70；wlr_compositor_create(...,6) src/server.c:269；com.kylin.Wlcom src/util/dbus.c:123 | 全命中 |
| 后端/输入 | backend_autocreate src/backend/backend.c:427；libinput 线程 src/backend/libinput/backend.c:121；INPUT_QUEUE_CAPACITY=64 input_queue.h:147 | 全命中 |
| 渲染 | KYWC_RENDERER renderer.c:12 与 src/render/opengl/egl.c（二次 getenv）；SWAPCHAIN_CAP 4 src/render/allocator/swapchain.c:18；scene_output_do_render src/scene/output.c:273 | 全命中（早期核验脚本误假定 egl.c/swapchain.c 在 render/ 根，实际在 opengl/、allocator/ 子目录，文档路径书写正确） |
| 输出/输入 | configure_outputs src/output/configure.c:166；function_manager_handle_key_binding src/input/function.c:1336；text_input 全局注册 src/input/text_input.c:30 区 | 全命中 |
| 插件/安全 | kywc_plugin_interface include/kywc/plugin.h:155；kywc_plugin_get_interface(void *plugin) :200；option 联合 num/str/realnum/boolean :49；RTLD_NOW|RTLD_GLOBAL src/plugin/plugin.c:245；ABI 1.0；security wl_global_create src/plugin/security/security.c:466；protector {r,b,g,a} src/security/protector.c:295 | 全命中 |
| XWayland/客户端 | xwayland_shell 手写 wl_global_create src/xwayland/shell.c:163；libkywc 双 roundtrip libkywc/libkywc.c:79；provider 能力表 provider.h:10；portal D-Bus name portal/main.c:15；screencast portal/screencast.c:16 | 全命中 |
| 特效 | blur priority 999 src/effect/blur.c:724；zoom priority 122 src/effect/zoom.c:933；17 钩子函数指针 include/effect/effect.h:37 起 | 命中 |

**核心枚举独立点算**（python 解析头文件，非人工目测）：

- `enum layer`（include/view/view.h:20 起）：真实层级 **18**（LAYER_FIRST=0 … LAYER_ON_SCREEN_DISPLAY=17，另有 UNKNOWN=-1 与 NUMBER=18 哨兵）。
- `enum kywc_view_role`（include/kywc/view.h:46-64）：**17 枚举器 = 16 真实角色**（UNDEF + NORMAL..AUTHENTICATION）。
- `enum kywc_view_capabilities`（include/kywc/view.h:87-101）：**12 个能力位**（1<<0..1<<11 + CAPABILITIES_ALL）。
- libkywc.h `kywc_*` 函数声明：**67**。
- protocols/*.xml 的 `<interface>`：**77**（34 文件）。

**核验中发现并已修复的文档问题**：concepts/09 曾把角色/能力枚举位置简写为 view.h（实际 include/kywc/view.h；行号 46-64、87-101 正确），已改为完整路径并补 enum 名。

## 3. 数量断言双口径复核（AC-3）

R 阶段 PowerShell 口径 → V 阶段 python 独立口径（脚本 verify_counts_links.py，物理行/正则解析）：

| 指标 | R（PS） | V（python） | 裁决 |
|---|---|---|---|
| *.c/*.h 文件 | 465 | 465 | 一致 |
| 全仓行数 | 138417（`Get-Content \| Measure-Object -Line`） | **165280 物理行**（字节 LF 165276 + 4 个无尾换行文件补 1） | **勘误**：实测 `Measure-Object -Line` 对字符串数组系统性少计（src/view/view.c 实际 3022 行被计 2578；`(Get-Content).Count`=3022 正确）。已同步修正束根 index、00-overview、source-code-map、insights 四处 |
| src/ 递归 C/H | 283 | 283（15 子目录 281 + 根 2） | 一致 |
| view/ C/H | 42（基线）/ 41（F-R3） | 42（根 38 含 view_p.h + tile/ 4 含 tile_manager_p.h） | **42 为准**，D-R3-01 已就地裁决，09 篇目录口径已修 |
| protocols XML | 34 | 34（77 interface） | 一致；第 35 个 XML src/plugin/security/security.xml 另行说明 |
| effect .c / shaders | 40 / 14 | 40 / 14 | 一致 |
| meson 选项 | 44 | 44 | 一致 |
| LINGUAS / .po | 16 / 27 | 16 / 27 | 一致（portal/po 独立域 19 另计） |
| libkywc / portal / examples C/H | 17 / 14 / 34 | 17 / 14 / 34 | 一致 |
| libkywc 公开 API | 67 | 67 | 一致 |

## 4. 路径纪律与链接（AC-4 / AC-5）

- **路径纪律**：对束内全部 .md 正则扫描五类禁用形态——file 协议绝对链接（file 加冒号三斜杠）、external 下 dao 路径段、d 盘 spaces 本地绝对路径、`.tmp` 与 `.chaos` 临时目录段 —— **0 违规**。R 阶段底稿中 4 处本地审计副本路径表述在发布时已替换为信源登记引用。
- **束内链接**：扫描全部「圆括号包裹、斜杠开头、点 md 结尾」的束内绝对链接，初检 1 处断链（concepts/00 引 `/examples/02-wlu-utilities.md`，实际 `02-wlu-utilities-walkthrough.md`），**已修复并复验 NONE**。
- **外部链接**：束内 30 个外链全部指向 `gitee.com/openkylin/kylin-wayland-compositor/blob|/tree/4df6562...` 固定提交（外加 1 个 wlroots 上游官网链接），无分支名 HEAD 链接。

## 5. facts 勘误台账（三处同步留痕）

E 撰写与 V 核验中发现 7 处事实清单偏差，均**以源码为最终层**：正文已按源码书写，事实清单保留原始发现并追加「V 阶段勘误」小节：

1. F-R4-024/025 option_value 成员（num/str/realnum/boolean）与 option_type 枚举（null/boolean/double/int/string）→ facts-effect-plugin.md。
2. F-R4-031 get_interface 签名带 `(void *plugin)` → 同上。
3. F-R5-060 wl_seat 支持列原文为 8（非 6）→ facts-protocols-clients.md。
4. xwayland_shell_v1 为手写 wl_global_create（src/xwayland/shell.c:155-167），非 wlr 助手注册 → R3/R5 两份 facts。
5. examples/monitor.c 是 libkywc 客户端（不绑 kde/wlr 协议）→ facts-protocols-clients.md。
6. F-R3-121 证据路径多一层 view/；F-R3-112 view_mode_interface 实为 17 个回调 → facts-input-view.md。
7. LOC 口径（见第 3 节）与 view=42（D-R3-01 就地裁决）→ 四份正式文档 + insights 闭合表。

上游自陈差异（D-R1 的 libseat/CLI/ENV/NOTICE、D-R5-150/151/156 等）为项目文档与代码不一致，本束不替上游裁决运行时影响，已在 concepts 01/12/14/15 与 project-docs.md 以差异块呈现。

## 6. 遗留项与边界

- 未做运行时验证：插件 dlopen 实际加载、protector 通道序 `{r,b,g,a}` 的画面表现、meson 重复键（linux-dmabuf-v1）在具体 meson 版本的合并行为、portal 安装路径实际命中——均为静态读码结论，已在正文标注。
- 全局 toctrees/dummy 的他束红项不归属本任务（见第 1 节归属说明）。
- 验证脚本留存在 spec 工作目录（`.trae/specs/okf-wiki-ecosystem/kylin-wlcom-okf-wiki/`：check_bundle_toctree.py、verify_counts_links.py、verify_symbols.py），非束内文件。

## 7. 独立审查闭环（同日三轮）

- R1 fresh-context 全面审查判 **fail**（3 actionable + 6 advisory）：绑定类型 19→20、shared_module 1→2 处、scene 角色 22→23 等，全部修复并在 facts 留勘误；修复中另自查出 MulanPSL 协议文件数量错误（实为 14 个：13 个私有 XML + security.xml）并更正。
- R2 复审确认 9 项 fixed，但新发现 3 个 C0 控制字符（U+0008/U+001B，PowerShell here-string 反引号转义引入）损坏勘误文本，窄口径再判 **fail**；已用字节级脚本清除并还原吞字。
- R3 窄口径终审判 **pass**（7/7）：控制字符 NONE、393 链接 0 断链、门禁 rc0、dummy 本束 0 error/0 warning；AC-7/AC-8 两个 rubric 均 4/5。
- 完整三轮检查点、证据与 finding 台账见 spec 工作目录 `.trae/specs/okf-wiki-ecosystem/kylin-wlcom-okf-wiki/review.md`；变更过程亦摘要于束根 [log.md](/log.md)。
