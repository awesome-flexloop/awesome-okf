# 变更日志

## 2026-10-15 - 初始版本

- ✅ 按方法论编排知识沉淀链路 `R→I→E→V` 完成（七概念场景 4：知识沉淀；结构：根 `index.md` + `log.md` + `concepts/`（索引 + 11 篇）+ `examples/`（索引 + 7 篇）+ `references/`（索引 + 3 篇），共 **26 个 Markdown**）。
- ✅ 内容敏感度预检：分享页 `www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA` 无访问控制（无 `code/token` 参数），WebFetch 可直接读取 → 判定**公开内容（Public）**，走标准工作流；spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/workbuddy-hardware-integration-whitepaper-okf-wiki/`（spec.md / tasks.md / facts.md，Review 后补 review.md）。
- ✅ 知识包归属：`jishu/ai/ecosystems/tencent/workbuddy-hardware-integration-whitepaper/`（腾讯生态分组，与既有 5 个 WorkBuddy 束同组；未新建分组、未在 `jishu/ai/products/` 重复建束）。
- ✅ 信源获取：W0 分享页为 **SPA 壳页**（纯 HTTP 仅得 4.6 KB，`<div id="root">` + `publish-bootstrap-loading` 占位，`noindex, nofollow`）；依 `window.__PUBLISH_BOOTSTRAP__` 暴露的制品基址取得 **P0 `janus.data.json`**（708 KB，`publishVersion: 20`）与 **P1 `WorkBuddy_v4__.html`**（202 KB，备用）。解析 P0 节点树（3573 节点，其中 2085 个 text 节点）按 HTML 标签语义还原正文，提取 **1330 行 / 21432 字符**，含标题层级、列表、表格、代码块与 §4.2 ASCII 决策图。
- ✅ 覆盖范围：白皮书 **0~13 章 + 附录 A/B 共 16 个章节单元**全部登记归属；已覆盖 15、**未取得 1**（附录 A 引用的随册文件 `assistant-openapi.html`，本分享页未随附）；信源 5 项中已学习 2（W0/P0）、备用 1（P1）、**未核验 1**（O1 `open.workbuddy.cn`）、**未取得 1**（X1）。章节集合与已登记集合**双向差集 0**。
- ✅ 登记事实 **F-001 ~ F-190**（190 条），编号连续无跳号无重复（脚本验证：190 行 / 唯一 190 / 连续 1..190 = True）。分区区间：§0 F-001~F-010（10）、§1 F-011~F-026（16）、§2 F-027~F-034（8）、§3 F-035~F-039（5）、§4 F-040~F-081（42）、§5 F-082~F-094（13）、§6 F-095~F-109（15）、§7 F-110~F-118（9）、§8 F-119~F-131（13）、§9 F-132~F-147（16）、§10 F-148~F-150（3）、§11 F-151~F-160（10）、§12 F-161~F-176（16）、§13 F-177~F-188（12）、附录 F-189~F-190（2）。spec `facts.md` 与 `references/article-source.md` **同源机械生成，各 190 行表行**，编号集合相等。
- ✅ **五类口径分层**全部落实：
  1. **厂商自宣 vs 第三方数据**：§0.1 三项指标来源分列——「日活第一」= 腾讯 2026 Q1 财报（F-006，`第三方数据`）、「2097 万/月，约为 TRAE 的 1.63 倍」= 易观分析（F-007，`第三方数据`）、「2.2 万+ Skills」= WorkBuddy 平台（F-008，`厂商自宣口径`）；**两份原始报告本束均未获取**。用户画像 6 项（F-020 ~ F-026）白皮书自述为「定性画像示意」，标 `厂商自宣口径`。
  2. **同文档 Skills 数量矛盾**：§0.1「2.2 万+」（F-008）vs §1.1、§5.4「7 万余」（F-019、F-092）；并列表述、不互相替换，引用须带章节位置。
  3. **匿名化伙伴场景**：§6.1 六个场景品牌与产品名已匿名（F-102 ~ F-108），全束标注 `匿名化场景` 并明确「不得反推真实品牌」。
  4. **商务结构框架性参考**：F-065「以双方协议为准」原样保留；F-069 ~ F-071 三条商业路径、F-072/F-076/F-077 结算口径、F-160 推广分佣、F-186 联合宣发权益均标 `商务框架性参考`；**白皮书未给出任何具体金额或分成比例**，本束不补全。
  5. **接口以官网为准 + 发行日期/发布日时序矛盾**：§7 明示接口清单以官网开发者文档最新版本为准（F-113，标 `以官网为准`）；页脚发行日期 2026 年 08 月（F-002）早于 §7 声称的 2026-09-02 发布日（F-112），登记为勘误 E-1。
- ✅ 勘误清单 **E-1 ~ E-6**：E-1 发行日期早于发布日；E-2 Skills 数量双口径；**E-3（新发现）§10 端到端示例第 1 步写「按 6.3 节构造授权链接」，但白皮书无 §6.3 节，实际位置为 §8.3（F-124）——属白皮书内部交叉引用错误**，本束 concepts/07 已按 §8.3 归位并登记；E-4 附录 A 随册文件未取得；E-5 分享页 `noindex, nofollow`；E-6 转引的第三方原始报告未核验。
- ✅ 无核心声明证伪；`status` 定 `stable`，`stale_after: 2027-04-15`（按快速迭代的开放平台产品设定）。信源距离评估明示「单一厂商自述、无第三方独立核验、O1 未核验、X1 未取得」。
- ✅ 操作可复现性两问判定为「**是**」（白皮书提供 OAuth 2.0 授权、接口调用、端到端流程、自助接入与审核的可照做链路）→ **设 `examples/`**，7 篇；但本束**未在本机实跑**（未注册应用、未申请凭证、未调用接口），所有用例逐段标注「未在本机实跑，依据白皮书（F-xxx）」，凭证一律占位符。
- ✅ 产出 26 个 Markdown：根 `index.md` + `log.md` + `concepts/`（index + 00~10 共 11 篇）+ `examples/`（index + 00~06 共 7 篇）+ `references/`（index + article-source + source-manifest + verification）。concepts 逐篇 1.1k–2.0k 中文字；examples 逐篇 804–1300 中文字，四段固定结构（前置条件 / 操作步骤 / 结果判据 / 限制与边界）齐备。
- ✅ 绘图：**Mermaid 2 张**——concepts/02 合作模式决策 `flowchart`（由 §4.2 ASCII 决策图转换，节点文本全部双引号包裹，分支与 F-046/F-047 一致）、concepts/05 OAuth 2.0 授权 `sequenceDiagram`（参与者 用户 / 合作方 App / WorkBuddy / WorkBuddy API，消息与 F-123 五步一致）。
- ✅ 与同分组既有束的关系：**互链不覆写**——本束根 `index.md`「主题关联」链 `workbuddy-official-docs`、`workbuddy-open-platform-sharing-and-promotion`、`workbuddy-one-sentence-mvp`、`workbuddy-sandbox-public-endpoint`、`tencent-buddy-family`、`wecom-5-0-12-release`、`codebuddy`、`octop`；本束独立复核确认开放平台入口与白皮书所述一致方向（官方文档站亦以 `open.workbuddy.cn` 为开发者入口），与既有束**互证不冲突**。
- ⚠️ 机械门禁记录：`invoke gates.*` 未运行（子项目可选文档依赖 invocations 未确认安装）；改为**直接运行底层门禁脚本**（`check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py`）+ 自包含束内校验脚本（frontmatter 必填字段、`okf_version` 位置、F 引用越界、本机绝对路径与绝对协议引用、相对链接 Test-Path、BOM/CRLF）完成等效核对。首轮束内校验抓出并已修复 1 处缺陷：`references/article-source.md` 因 Python 文本模式写入被转为 CRLF，导致头部 `---` 不匹配被判定为「缺 frontmatter」→ 生成器改 `newline=""` 重跑后复验通过。
- ⚠️ 临时产物隔离：抓取缓存（`wb-janus.json`、`wb-v4.html`、正文提取文本）、提取脚本、生成脚本、校验脚本全部位于工作区 `.temp/` 与系统临时目录，未落入仓库交付物。
- ⚠️ 观测记录（不扩大修复，非本束引入）：`projects/awesome-okf-xs/` 子模块在本任务开始前即存在并行在途变更（`doc/bundles/index.md`、`jishu/ai/ecosystems/index.md`、`jishu/ai/ecosystems/tencent/index.md`、`jishu/ai/ecosystems/tencent/workbuddy-official-docs/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`sheke/index.md` 处于 modified，另有未跟踪目录 `workbuddy-open-platform-sharing-and-promotion/`）；本束索引计入 **Task 6** 时以「无并行写入窗口」的脚本输出为准。
- ✅ 五级索引接入与计数复算（Task 6）：`python scripts/check-bundles-index.py` **终采通过**——「9 域 / 61 组 / **638 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致」。五级索引全部更新：`tencent/index.md`（导航表 +1 行、toctree +1 条、相关链接 +1 行、「关于本分组」15→**16** 束 / 113→**124** 概念 / 36→**43** 示例 / 68→**72** 信源 / 2203→**2393** 事实，并追加本束生成说明）→ `jishu/ai/ecosystems/index.md`（类总 91→**92**、腾讯行 15→**16**）→ `jishu/ai/index.md`（frontmatter 与正文 243→**244**、ecosystems 行 91→**92**）→ `jishu/index.md`（ai 行简介 243→**244**）→ `doc/bundles/index.md`（`total_bundles` 637→**638**、正文计数行 637→**638**、mermaid `jishu` 节点 472→**473**、节标题 472→**473**、分组表 ai 行 243→**244**）。本束计数按机械真值：11 概念 + 7 示例 + 4 信源（index.md frontmatter 的 W0/P0/P1/O1）+ 190 事实。
- ⚠️ 并行束 toctree 观测（**非本束引入、不修复**）：`python scripts/check-toctrees.py` 报 5 处导航问题，**全部属并行在途束 `sheke/industry/workbuddy-opc-whitepaper`**（`references/index.md` 的 toctree 引用不存在的 `verification`；`references/article-source.md`、`references/index.md`、`references/source-manifest.md` 未收录不可达；该束缺根 `index.md`）。过滤本束名 `workbuddy-hardware-integration-whitepaper` **零命中**——本束 26 个 Markdown 的 toctree 与可达性无问题。按归属隔离原则只披露不修复。
- ✅ 编码门禁：`python scripts/check-utf8.py` 通过（**11640 个文件**均为有效 UTF-8；R1 评审复核时点为 11649，此后因并行写入增至 11651，均通过）。
- ⚠️ **并行漂移观测（R1 之后，非本束引入、不修复）**：本束接入后首次 `check-bundles-index.py` **退出码 0**（9 域 / 61 组 / **638 束**五面一致），**该一致性窗口**即 AC-4 的通过证据。此后并行会话在 `sheke/industry/` 新增 `workbuddy-opc-whitepaper` 束且尚未同步索引，导致全库门禁出现 **3 处 sheke 相关漂移**（`total_bundles` 638 vs 目录树 639；`sheke/` 节标题与分组表均 68 vs 69）。**本束相关的五级计数面（总 638、jishu 473、jishu/ai 244、ecosystems 92、tencent 16）在该次复算中仍逐项一致**——残留 +1 全部归属 `sheke/` 并行束。按 spec「并行漂移只披露不修复」与归属隔离原则处理，不代改 `sheke/index.md` 与 `total_bundles`。
- ✅ V 阶段定向构建（Task 7）：Sphinx 8.2.3 + myst_parser 5.1.0，`-b dummy -E -D exclude_patterns=<非 jishu 域>` → `build succeeded`；本束 **26 篇全部被读入与写出**，**提及本束名的 WARNING = 0**（输出中提及本束的行全部为进度行）。构建产物 `_build/dummy-t`（及被中止的全量构建 `_build/dummy`）已删除。
- ✅ 束内自包含校验（脚本，26 文件）：绝对协议引用（file 协议）与用户目录本机路径 **0**；Markdown 相对链接与全部 `{toctree}` 条目 **0 断链**；frontmatter 必填字段齐备且 `okf_version` **仅出现在根 `index.md`**；BOM **0**、CRLF **0**；**F 编号双份 190 = 190 且集合相等、连续 1..190**；全部 `F-\d{3}` 引用**越界 0**。
- ✅ TR 抽查：五类口径标签计数 `厂商自宣口径` 25 / `第三方数据` 10 / `匿名化场景` 10 / `商务框架性参考` 21 / `以官网为准` 23（另 `未核验` 30、`未取得` 28）；7 篇 examples 的「前置条件 / 操作步骤 / 结果判据 / 限制与边界 / 未在本机实跑」五段标记全部为 True。

## 备注

- 本束的 `references/article-source.md` 体量较大（约 40 KB，190 行事实表），属**刻意**设计：口径分层与「未核验 / 未取得」逐条登记需要完整台账；检索时建议按 `F-\d{3}` 定位，或先读[核验报告](references/verification.md)按口径跳转。
- 复核时点建议：`stale_after: 2027-04-15`。复核优先级：①分享页 `publishVersion` 是否更新（P0 制品 URL 变化）；②Skills 数量口径是否统一（E-2）；③发行日期与正式发布日是否修正（E-1）；④附录 A 随册 OpenAPI 文件是否随页提供（E-4）；⑤ `open.workbuddy.cn` 官网开发者文档接口清单与白皮书快照的差异（F-113）。
