# 变更日志（Log）

## 2026-10-14

### 新增

- 首版知识包落盘：16 篇概念文档（[concepts/](concepts/index.md)）、3 篇实战走读（[examples/](examples/index.md)）、9 份信源/事实/洞察/验证文件（[references/](references/index.md)）与束根导航。
- 五份事实清单合计 **851 条**编号事实：R1 构建/启动/配置/打包 162 条、R2 后端/渲染/场景/输出 178 条、R3 输入/视图/工作区/XWayland 176 条、R4 特效/插件/安全 179 条、R5 协议/libkywc/portal/示例 156 条。
- [架构洞察](references/insights.md)沉淀五个四元组洞察（协议三态裁剪、补丁化 wlroots 钉版、libinput 独立线程、扩展三层 ABI、六级图形回退链）与 Mermaid 知识地图。

### 事实来源

- 唯一代码信源：openKylin Gitee 官方仓库固定提交 `4df656222427f3cd0101e41d828fb64805e66c15`（2026-10-12，openkylin/huanghe），四要素与规模口径见 [源码信源登记](references/source-code-map.md)。
- 二级事实源：仓库快照内 README、docs/PROTOCOLS.md、docs/ENV.md、docs/KNOWN_ISSUES.md、docs/CONTRIBUTING.md，登记与双源差异见 [项目文档登记](references/project-docs.md)。
- 方法：source-code-to-okf-wiki 五阶段（信源固定 → R 事实采集 → I 洞察 → E 分批生成 → V 独立验证），由 seven-concepts 方法论编排（场景：知识沉淀）。
- 证据边界：静态源码学习，未构建运行；采集与撰写中发现的文档/事实差异（D-R1/D-R3/D-R4/D-R5 编号疑点、wl_seat 版本、option_value 字段、xwayland_shell 注册归属等）以代码为最终层，在相关文档以差异块呈现并在 V 阶段复核。

### 独立审查与勘误（同日）

- V 阶段独立复核修正全仓物理行数口径（138417 → 165280，PowerShell `Measure-Object -Line` 少计）、view/ 文件数裁决（42）。
- R1 fresh-context 审查（fail→修复）：key_binding_type 真实类型 19→20（CUSTOM_DEF 非哨兵）；shared_module 「全树唯一」→ src/ 内唯一 security + examples 另有 simple（共 2 处）；scene 真实角色 22→23（22 为有调试名数）；INPUT_PANEL 标注枚举值 11；特效创建 23（分组块）/26（全函数）两口径分清；KYWC_* 唯一名 16→17；修复一处伪链接与底稿文件名引用；角色枚举补 UNDEF 注记。
- 修复轮另抓出并更正：MulanPSL-2.0 协议文件并非仅 security.xml 一个——13 个 openKylin 私有 XML（6 kywc-* + 7 ukui-*）同为 MulanPSL，security.xml 是第 14 个且唯一在 protocols/ 之外。
- R2 复审确认上述全部修复，另清除勘误段 3 个 C0 控制字符（U+0008/U+001B，PowerShell here-string 转义引入）并还原吞字；旧事实标题加内联「已勘误」标记。
- 每次勘误均在对应 facts 文件保留原文并追加注明日期的勘误小节（审计留痕），三处以上同步（facts/insights/concepts）。
