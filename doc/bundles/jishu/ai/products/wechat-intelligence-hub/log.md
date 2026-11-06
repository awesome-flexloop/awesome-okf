# WeChat Intelligence Hub 知识包变更日志

## 2026-11-06 · 第二轮源码核验（本地源码 → OKF v0.2 Bundle 增量扩展）

- **触发**：用户指定 `external/dao/wechat/wechat-intelligence-hub` 为源码，要求对该主题做 `/七概念` 级别的源码级学习与核验
- **方法论**：`/七概念` 场景 4 知识沉淀链路 **R→I→E→V→C**，由 `source-code-to-okf-wiki`（v1.5.0）承载，并借用 `source-code-to-okf-adversarial-update` 的五步对账链路（复基线 → 对抗性对账 → 漂移分类 → 定向修复 → 落盘核对）
- **扩展方式**：按 §6.5「既有束的多轮增量扩展规范」——**增量扩展，不新建束、不重写已验证结论、不重排旧编号**
- **规模**：新增 **6 个 Markdown 文件**（4 concepts + 2 references）；定向修订 3 个既有文件（根 `index.md`、`concepts/index.md`+`concepts/02`+`references/index.md`+`references/verification.md`）；F 编号**续编 F-058~F-101（44 条）**，与首轮 F-001~F-057 衔接无跳号
- **信源固定**：commit `fb6a42c34160d2ffa66ed5f114f8d8cdabe7f5f9`（2026-10-17），remote `git@github.com:Rion-Wu-tech/wechat-intelligence-hub.git`，工作区 clean

### R（源码事实采集）

- **G0 信源稳定性预检**：固定不可变 commit hash（非 `main`/`master`）；`check-source-path-stability.py` 定向扫描本束 rc=0（`scanned_files=12`、`blocking_count=0`）。
- **⚠️ 关键发现**：源码 HEAD **领先唯一 tag `v0.9.2-preview.2` 共 13 个提交**（`6b73940a` → `fb6a42c`，64 文件 / +5569 −202 行）；tag 之后新增 `docs/USAGE.md`、`SECURITY.md`、`rion_wechat_access.py`、`report_security.py`、`providers/wxkey/`。README 声明的版本号是**发布口径**，工作副本是**开发态**——二者非同一快照。
- **采集手段**：Python `ast` 解析 38 个 `.py` 文件的类/函数/常量；`git ls-tree -r HEAD` 取 HEAD 口径规模；`grep` 交叉验证。
- **AST 脚本修正**：首探时脚本仅处理 `ast.Assign`，导致带类型注解的模块级常量（`TOOL_SPECS: dict[...] = {...}`）被整体漏掉、字段数误返回 0；修正为同时处理 `ast.AnnAssign` 后恢复 266。**「计数为 0」比「计数偏差」更易被误认为事实**。
- **核心事实**：仓库 126 文件（43 md / 38 py / 12 sh / 8 png）；非测试 py 18 个 16,007 行、测试 20 个 5,582 行；`TOOL_SPECS` **30 工具 / 266 字段 / 87 去重属性名 / 35 别名**；Reader CLI **36** 子命令、情报产品 CLI **37** 子命令；`PAGE_SPECS` **4** 条；旗舰 `SOURCE_RULES` **11** 条、HTML `SOURCE_RULES` **8** 条；`style-previews/` **10** 文件（**0 处运行时引用**）；`intelligence_views.py` **26** 顶层函数；`report_security.py` **4** 函数 / 96 行；`rion_wechat_access.py` **954** 行 / 24 函数 / 1 类。

### I（对抗性对账与漂移分类）

- **首轮 8 项 ⚠️ 逐项复核结果**：**6 项坐实**（#9、#16、#17、#19、#20，及 #18 的明暗主题部分）、**1 项拆分**（#18 明暗主题 ✅ / 四视图风格 ⚠️ 修正）、**2 项维持**（#5 星标、#6「5 天」，源码无法提供 star 时序）。
- **首轮可信度评估**：首轮把 5 项 UI 声明判为「图注单源」是**未 clone 源码下的审慎保守判定**，非官方文档缺失；**未发现首轮存在任何造假式断言或事实性错误**，仅 #18「四种视图风格」需从「运行时能力」修正为「设计期候选方案」。
- **漂移分类**：D1 文档漂移（#18 四视图风格，1 项）· D2 范围缺口（#9 边界细化、版本口径，2 项）· D3 计数口径（工具数 29 vs 30、CLI 36/37/73、`SOURCE_RULES` 11 vs 8）· D4 新增事实（只读结构性保证、报告安全模型、草稿模板机制、风格预览非运行时）· D5 维持（动态数字 2 项）。
- **反模式规避**：不做全量重写；`concepts/00`~`05` 首轮结论保留原文，仅在受影响处加 🔬 修订标记与链接。
- **增量修订规范条目（复盘补记）**：多轮增量时「受影响声明面」不止被直接引用的页；须机械扫描结论汇总页（如 `concepts/05`）、各级 `index.md` 的表格描述行、目标页 frontmatter 的 `description`/`tags`、以及「下一站」导航序列。只改被引用处，会让从结论页进入的读者读到旧口径。

### E（增量落盘）

- **信源先行**：`references/source-code-map.md` → `references/source-code-verification.md` → `concepts/06~09` → 三级 `index.md` → 根 `index.md` → 本日志。
- 新增概念：`06-readonly-contract-and-code-evidence.md`（模式 M4）· `07-flagship-renderer-and-view-model.md`（模式 M5）· `08-source-code-architecture-and-counts.md`（模式 M6）· `09-safety-and-adoption-boundaries-from-source.md`（模式 M7）。
- 定向修订：根 `index.md`（frontmatter、阅读路径、核心事实速查表、⚠️ 四条勘误、采用提示、信源可信度）· `concepts/02`（加源码轮结论框）· `concepts/index.md`、`references/index.md`（表格 + toctree 同步）· `references/verification.md`（追加「源码轮追记」节，首轮结论不改写）。
- 全部交叉引用使用相对路径，无 `file:///` 绝对路径，**无本机绝对路径**（源码路径以仓库相对路径表述）。

### V（质量门与计数复核）

| 检查项 | 结果 |
|--------|------|
| GATE-SPS 定向扫描 | ✅ rc=0：`scanned_files=12`、`blocking_count=0`、`env_bound_count=0`、`anchor_out_of_bounds_count=0` |
| 计数断言双口径复核 | ✅ 工具数 30（AST / awk+grep）、字段数 266（AST / 正则）、去重属性名 87、`PAGE_SPECS` 4（AST / grep 逐行核对）、`SOURCE_RULES` 11 与 8（AST / 块内 grep） |
| Grep 级 API 真实性验证 | ✅ 全部类名/函数名/常量名均在上游源码中验证存在：`read_only`（`tools_catalog`/`tool_schema`）、`mode=ro` 快照、`PAGE_SPECS`/`SOURCE_RULES`/`TOOL_SPECS`/`mobile-routes`/`theme-button`/`localStorage['wechat-flagship-theme']`/`nh3` 白名单、`_reply_draft` 六类 intent 模板 |
| 无写入能力验证 | ✅ Reader 源码中 `send_message`/`send_text`/`post_message`/`write_*` 均无匹配 |
| 风格预览非运行时验证 | ✅ 对 `style-previews/` 全仓库引用检索（`--include=*.py --include=*.sh --include=*.md`）命中 **0** 处运行时引用 |
| 只读统一置位验证 | ✅ `read_only: True` 位于列表推导式内，对全部 30 工具统一置位，非逐项开关 |
| F 编号连续性 | ✅ F-058~F-101 连续无跳号，与首轮 F-001~F-057 衔接无重叠 |
| frontmatter 完整 | ✅ **分文件口径**：根 `okf_version` 仍唯一；新增 6 文件中 `concepts/06`~`09` 4 篇仅含 `type`/`title`/`description`/`tags`（OKF v0.2 唯一必填 `type`，合规）；`references/source-code-map.md` 与 `references/source-code-verification.md` 2 篇另含 `generated`/`verified`/`status`/`stale_after`/`sources` |
| 相对链接可达 | ✅ 本束 18 文件、全部相对链接无断链、无绝对路径 |
| 敏感信息 | ✅ 无密钥、无真实聊天数据、无个人路径；仅仓库相对路径与 commit hash |

### 本轮局限（诚实登记）

- **未实机执行**：未运行 `install.sh` / `run_demo.sh` / `profile-init`，未在真实微信数据上验证；全部结论基于静态源码阅读 + AST 解析。
- **未运行测试**：20 个测试文件（5,582 行）仅统计规模，**未执行 pytest**，故本束不含任何「测试通过」类陈述。
- **未展开 tag 快照**：仅分析 HEAD，故「工具数 29→30」的具体差异项**未定位**（只登记口径差，不臆断是哪一项）。
- **未实看渲染产物**：HTML 渲染结果由源码与截图文件名推断，未在浏览器中实际打开。
- **star 时序缺口未补**：GitHub stargazers 时序接口本轮仍未取。

### C（提交与质量复盘收口）

- **触发**：对 `concepts/` 做七概念 `R→I→V→A` 系统性质量复盘（无新信源、不新增束、不改计数），用户下达「按 A1→A4 修复、再走 A5 原子提交收口」。
- **A1 口径缝合**：`concepts/05 §3.4` 加 🔬 源码轮修订指向、`concepts/index.md` 的 02 行补修订结论、`concepts/02` frontmatter `description` 加修订指向；三处均**不改写首轮原文结论**，措辞与 `references/verification.md`「源码轮追记」一致。
- **A2 导航对齐**：`00` 显式标注顺读起点、`03→04`、`05→06`、`09` 改标「回看 / 顺读终点」；机械抽取「下一站」链 = `00→01→…→09`。原 03→05 与 09→05 属有意的跳读/回看，改为显式标注而非判错。
- **A3 自证口径**：V 表 frontmatter 行由「新文件齐备」改为**分文件口径**；I 节新增「增量修订须扫全部声明面」规范条目。
- **A4 行尾归一**：字节级脚本把本束 4 个整文件 CRLF（`concepts/02`、`log.md`、`references/source-code-map.md`、`references/source-code-verification.md`）归一为 LF（HEAD 既有文件原即 LF），断言本束 18 个 `.md` 文件 `crlf=0`。
- **A5 原子提交**：子仓一笔提交收录本束 12 项在途文件 + 上述定向修订；父仓仅前移 gitlink；**未 push**。提交哈希以 `git log` 为准。
- **提交后门禁**：`check-toctrees.py` / `check-bundles-index.py` / `check-utf8.py` / `check-asset-baseline.py`（基线须提交后取自 HEAD 才自证）以提交后复跑为准，本日志不预先断言结果。

---

## 2026-11-06 · 初版生成（微信博文 → OKF v0.2 Bundle）

- **来源**：微信公众号「开源食谱」《5 天攒 2000 星！让微信聊天变情报库，相见恨晚！》（原创，豆芽菜小萌，2026-09-24 07:02 北京）
- **方法论**：`/七概念` 场景 4 知识沉淀链路 **R→I→E→V→入库**，由 `blog-article-to-okf-wiki` 七阶段工作流承载；指令经 `specweave-slash-alias-resolution` 解析（`.agents/commands/seven-concepts.md` + `seven-concepts-cmd`）
- **规模**：12 个 Markdown 文件（6 concepts + 2 references + 2 目录 index + 根 index + 本日志）；F 编号事实 **57 条**（博文 40 + 官方核验 17）
- **骨架**：概念骨架，**无 `examples/`**（操作可复现性两问皆「否」）
- **归属**：`jishu/ai/products/wechat-intelligence-hub/`

### R（事实采集与 P0 核验）

- 内容敏感度预检：`mp.weixin.qq.com/s/<id>` 公开文章，无 `share?code=`/`token=`/邀请码 → **Public**，走标准 Spec Mode。
- **流程偏差登记**：Skill Gotcha 记载微信反爬确定、应直接用 `browser_use` 取 `#js_content`；本次 **WebFetch 直接返回完整正文与元信息，未触发反爬回退**，无内容损失。
- 归属探查：检索出现 `echoD886/wechat-intelligence-hub` 同名仓库；以官方 README clone 地址与 GitHub API `full_name` 确认主线为 `Rion-Wu-tech/wechat-intelligence-hub`（F-057）。
- 权威源：GitHub REST API（created_at / language / license / Star 时点快照）+ main 分支 README（能力、命令、隐私与许可证条款）。
- **22 项 P0/P1 → 14✅ / 8⚠️ / 0❌**；无核心声明被证伪 → `status: stable`。
- 8 项 ⚠️ 分类：① 动态时点/成效数字（星标 1976/2000→2764、「5 天」无 star 时序）；② 口径范围（「不重签名」仅 Reader 核心）；③ UI 层单源（四入口名、四视图、移动端、回复草稿、检索五维度）。
- 关键判定：API `created_at=2026-09-04`，发文 2026-09-24，相隔约 20 天 → **「5 天」不得写成「仓库创建后 5 天」**。

### I（骨架与归属）

- 操作可复现性两问：Q1 博文层无任何命令/版本/步骤顺序 → 否；Q2 作者明确「全虚构 Demo」「macOS 新机器路径官方未实测」→ 否。→ **概念骨架，不设 examples/**。
- 官方 README 命令作为「路径说明」写入 `concepts/04`，逐条标注「未实机验证」，不包装成实战示例。
- 归属决策：主线是具体终端工具/产品 → `products/`；查 `wigolo`/`open-code-review`/`agent-reach`/`creatorhub` 等先例；单篇博文不新建分组；排除 `practice/`（工程实践/方法论/行业洞察）。

### E（bundle 生成）

- **信源先行**：`references/article-source.md` → `references/verification.md` → `concepts/00~05` → 三级 `index.md` → 根 `index.md` → 本日志。
- 勘误四张清单（日期/版本、成效数字溯源、口径对照、引文逐字）齐备，8 项 ⚠️ 在正文均有对应表述。
- 所有数字、命令、版本、许可证、日期携带 F 编号；`okf_version: "0.2"` 仅出现在 bundle 根 `index.md`。
- 交叉引用全部使用相对路径，无 `file:///` 绝对路径，无本机绝对路径（示例路径用占位符）。

### V（对抗审查与机械门禁）

四视角审查采纳并落实：

1. 🔴 魔鬼代言人 → 补充 **AGPL-3.0-only 商业授权边界**（闭源/OEM/白标需授权、SaaS 触发网络开源义务），写入 `concepts/05 §3.1` 与根 index 采用提示。
2. 🟠 老板视角 → 补充 **preview 版本成熟度与命令漂移风险**（`v0.9.2-preview.2`，本束命令为文档快照未实机验证）。
3. 🔵 未来视角 → 强化时效与复核（`stale_after: 2027-03-06`，复核 Star、preview→GA、macOS/Windows 首次接入进展）。
4. 🟣 证据强度 → 区分「官方可核验事实 / 官方截图经博文转述 / 博主观点」四层；标题 hook 与 UI 命名显著标注未独立核验。

机械门禁（2026-11-06 终检）：

| 检查项 | 结果 |
|--------|------|
| 双份 F 编号正则核对（spec `facts.md` ↔ `references/article-source.md`） | ✅ 各 57，F-001~F-057 连续无跳号、集合相等、双向差集为空 |
| 总索引计数对账 `check-bundles-index.py` | ✅ rc=0：9 域 / 64 组 / **715 束**，五面一致 |
| toctree 完整性 `check-toctrees.py` | ✅ 本束入库当次 rc=0（全部 index.md 引用有效、内容文档可达）；**终检复跑 rc=1**，4 处报错全部来自并行在途束（见下节），本束命中 0 处 |
| UTF-8 严格编码 `check-utf8.py` | ✅ rc=0：12919 个文件均为有效 UTF-8 |
| 资产基线 `check-asset-baseline.py` | ⚠️ rc=1「行尾归一失效，残差 +299202」——工作树已干净、无 WIP 可 stash，属 Windows `core.autocrlf=true` 环境级假红；其规模数字校验（total_bundles=715）已通过 |
| 全局锚点 `check-section-anchors.py` | ⚠️ rc=1：全库 6557 处既有断链 / 413 处 MyST 锚点警告；报告检索本束名命中 **0** 处，未引入新断链 |
| 相对链接可达 / 无 `file:///` | ✅ 本束 12 文件 / 42 条相对链接，断链 0、绝对路径 0、锚点引用 0；跨束仅引用已存在的 wigolo / agent-reach / inkos / creatorhub |
| frontmatter 完整 | ✅ 根 `okf_version` 唯一，`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources`(3) 齐备 |
| 敏感信息 | ✅ 无家目录绝对路径、无密钥、无真实聊天数据；示例路径均为占位符 |
| 勘误落实 | ✅ 8 项 ⚠️ 在正文均呈现官方口径并标注博文来源 |

### 并行会话计数与提交登记

- 本次开工时总索引 `total_bundles` 已由并行会话更新为 **714**（更早记录为 713）；`check-bundles-index.py` 复跑确认地面真值为 **9 域 / 64 组 / 714 束**、五面一致，故本束入库后按地面真值记为 **715**（jishu 524 / ai 288 / products 39），不追加第三次数。
- 生成期间**并行会话把在途文件一并提交**：子模块 HEAD `12efe455 docs(bundles): 新增三束 OKF 知识包并同步计数（712→715）` 已包含本束 12 个文件与各级索引改动，说明同期另有两束并行入库；绝对值以地面真值脚本为准。本会话不重复提交、不改写该提交。
- 终检时又出现两个**并行在途束**：`jishu/ai/products/wechatbridge/`（缺 index.md）与 `jishu/ai/products/workbuddy-wechat-chat-forward-skills/`（缺 index.md，且 `references/article-source.md`、`verification.md` 未收录），使 `check-toctrees.py` 由 rc=0 转 rc=1 并报 4 处问题。这 4 处**均不属于本束**，按「谁添加谁接线」不代修；`check-bundles-index.py` 仍 rc=0（715 束，二者因无 index.md 尚未计入树），若二者完工需再各 +1 并同步计数。
- `jishu/index.md` 域导航页的多数分组束数为历史过期值，页面自身声明「递归束数以知识包总索引为准」；本会话仅同步其 AI 行描述中的 287→288，不扩大变更范围。

### C（提交）

用户随后下达「提交」指令，本会话按原子提交「单一职责」收尾，**仅提交本任务范围内的文件**：

- **① 子模块**：`12efe455` 已由并行会话收录 bundle 12 文件与四级索引；本会话单独提交 `log.md` 的 V 阶段门禁结果与规模修正（10→12 文件），使记录与实际产物一致。
- **② 主仓库**：提交 spec 四件（`.trae/specs/okf-wiki-ecosystem/wechat-intelligence-hub-blog-okf-wiki/` 下的 `spec.md` / `facts.md` / `tasks.md` / `review.md`），并把子模块 gitlink 指向 ① 产生的新 HEAD。
- **③ 排除范围**：工作区中并行会话的在途改动（`products/wechatbridge/`、`products/wechatbridge-ios-relay/`、`sheke/industry/ai-comic-drama-opc-transition/`、716→718 计数，以及主仓库 3 个并行 spec 目录）**不属于本任务，未纳入提交**。
- **④ 推送**：未执行，是否 `git push` 由用户决定。
- **提交哈希**：共三笔（子模块 `docs` 1 笔；主仓库 `docs(spec)` 与 `chore(submodule)` 各 1 笔），以 `git log` 为准；提交信息遵循 Conventional Commits。
