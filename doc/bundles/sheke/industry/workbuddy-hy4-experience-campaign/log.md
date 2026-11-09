# 更新日志

## 2026-11-09

**Generation**：由 `/七概念` 方法论编排（`scenario=auto`、`depth=standard`、`with_validation=true`，组合为 **R→F→I→E→V→A→C**）生成 WorkBuddy × 混元 Hy4「体验官」征集活动的规则解构 Wiki 教程与定制参赛方案知识包。

- **启动协议**：按 SpecWeave `AGENTS.md` PRIORITY ZERO 从磁盘原文回读，确认「启动协议 / 根 `docs/` 为唯一文档中心 / 内容敏感度预检」三个锚点；按 `.agents/context-routing.md` 读取七概念方法论入口与 OKF bundles 概念查阅路由；按 `projects/AGENTS.md` 与 `projects/awesome-okf-xs/AGENTS.md` 进入子项目规范。
- **公开性预检**：`https://www.workbuddy.link/p/tmLIChKEjyBNv8UQXxD29c?source=2` 为公开活动页，无 `share?code=` / `token=` / `invite=` / `pwd=` 等访问控制参数；`source=2` 是来源标记而非访问控制参数；`userinfo` 对未登录返回 `code: 11607 / not login` 只影响登录态用户信息，不影响公开规则正文 → **Public**，走标准公开知识沉淀路径，产出落 `doc/bundles/`，不进 `playground/`。
- **归属决策**：`sheke/industry/` 新建独立束 `workbuddy-hy4-experience-campaign`。理由：`docs/knowledge/index.md` 明确「系统化学习 Wiki 一律沉淀至 `projects/awesome-okf-xs/doc/bundles/`」；本束与同组 `workbuddy-1024-contest`（同平台、同活动页单源、同「事实→机制→路径→方案」结构）、`zhihu-ai-science-workshop`、`toutiao-monetization` 同类；与 `retrospective-okf-content-creation-three-rules-20261106.md` 记录的同类请求流水线一致。不并入 `workbuddy-opc-whitepaper`（后者是产品定位白皮书解读，与征集活动规则是不同实体）。
- **采集链路（L1 → L3 SPA 引导数据逆向）**：`WebFetch` 只返回页面标题、正文为空；改用静态请求得到 5,844 字节外壳，从 `window.__PUBLISH_BOOTSTRAP__` 取 `artifact.url`（`workbuddy-space-static.codebuddy.work/page/tmLIChKEjyBNv8UQXxD29c/axS-bAKLmFby/`、`publishVersion: 12`）→ 下载正文 HTML 186,585 字节与 `janus.data.json` 235,566 字节 → 状态树 `TOP_KEYS=264` / `NODES_WITH_CONTENT=62` / `TOTAL_TEXT_CHARS=134737`，最大文本节点为 91,684 字符 JS → 从 `ruleHTML()` 解码出 9,590 字符细则 HTML（纯文本 5,716 字符），并定位 `openForm()`、`FORM_OPTIONS`、`SUBMIT_END` / `PHASES` / `pDate()`、`submitWork()`、`buildSubmissionProperties()`、`auditSubmission()`。未使用 L4 浏览器渲染（M-02~M-06）。**若止步首屏，会漏掉 8 类资格取消、8 项表单字段、撤回与投诉邮箱、知识产权三条、刷量剔除规则——即方案里全部「可能直接出局」的部分。**
- **事实登记**：**72 条编号事实 F-001~F-072 连续无跳号**，分 7 节（主体与时间轴 14 条／参与方式与授权 11 条／评分核验 7 条／奖项发放 8 条／表单与前端 13 条／资格与发放 6 条／内容与知识产权 13 条）；另 **13 条官方口径缺口 G-01~G-13 + 8 条采集元数据 M-01~M-08**。
- **G1 门禁（含声明式豁免，已机械复验）**：精确词表正则 `导致|因此|所以|由于|因为|使得|从而|因而|故而|故此` 扫描 F 行，命中恰 **6 条、集合 `{F-012, F-038, F-058, F-062, F-063, F-069}`**，其余 66 条零因果词。6 条全部是规则原文或前端源码注释中「条件—后果」条款的逐字／等义压缩转录，已在 `facts.md §1` 逐条列表声明。初稿曾写「5 条 / 其余 67 条」，漏 F-012 且词表把「系统故障」误判为因果词，已按 E-01／E-02 更正。
- **结构**：12 个文件——概念 6 篇（00 总览／01 活动事实与采集链路／02 评分与奖项／03 表单与合规／04 机制洞察／05 参赛方案）、信源 2 篇（facts + verification）、束根 `index.md`、`concepts/index.md`、`references/index.md`、`log.md`。其中 **11 个含 frontmatter**（`log.md` 按体例无）。**无 `examples/`**：信源为规则文本与前端表单定义，无命令、无版本、无实际输出，未满足「操作可复现」两问；表单字段与前端机制由 03 篇承载。
- **F 阶段**：把 100 分拆为不可再分的两类量——相对项 70（分母由全场最高者定义）与绝对项 30（评委打分，取值不显式含他人数据）。该拆分为本包推导 I-01，不写成主办方口径。
- **机制层纪律**：I-01~I-04 四条洞察，每条含**陈述 / 证据（挂 F）/ 反直觉推断 / 行动**四元组；G3 门列出可迁移到至少 1 个非本赛事场景的判定，并把「提交即定稿」标为有限迁移。「521 名算术」明示不可迁移。
- **核验**：**C-01~C-10 共 10 项（✅7 / ⚠️3 / ❌0）**。三项 ⚠️：C-03 口径张力（细则固定 500 名／第 22—521 名 vs 首屏「参与奖名额与排名范围以活动公告为准」，两处并列登记、不调和）、C-08 状态树遗留代码张力（`auditSubmission()` / `saveDraft()` / `renderLinkGuide()` / 截图上传链路为旧活动残留，不作本活动规则；但内容安全检查确在 `submitWork()` 中被调用）、C-09 单源与证据等级。C-05 验算 1+5+15+500=521 且四个排名区间连续无重叠——纯算术自洽检查，不含名次预测。
- **V 阶段对抗审查**：四视角 7 条实质意见，**6 采纳 + 1 部分采纳**，含两项方向性纠偏（V-1 把社媒 70 分误读为传播打法、V-2 把归一化分母当可控变量）。V 门「意见 ≥5、采纳 ≥2」通过；勘误 **E-01~E-09**（V 阶段 E-01~E-05、落盘后复核 E-06~E-09）全部留痕于 `verification.md §5`。
- **方案层（参赛作战手册七步）**：判型为「单阶段投稿 / 自选型 / 内容体验型 / 相对分+绝对分 / 截止后快照核验 / 提交即定稿」；资产基线锚定 `git ls-tree -r -l HEAD -- doc/bundles` 实测，与 `check-asset-baseline.py` 唯一合法基线口径一致——**720 束、9 域 / 64 组、12,985 个 md、9,740 篇内容文档、100,324,957 字节 ≈ 95.68 MiB、8 个 HTML**（本包落盘后工作树为 721 束；他方会话完成对账后共享工作树最终稳定为 722 束）；三条口径纪律（锚定 HEAD / 字节只在 HEAD 口径内引用 / 对外只用量级表述「七百余束・近万篇内容文档・九大领域」）。三个选题候选中主选 A「规则页 → 可核验 Wiki」，吸收 B 的版图式呈现，排除 C；明确不可选分支为 `guoxue/liaofan/liaofan-shengyi-jing`、`guoxue/zhouyi`、`guoxue/daojia/daojiao/baopuzi`、`yixue/medicine/ishinpo-reading`、`sheke/minsu/*` 的正文主画面。产出 12 步材料依赖链、合规四层 L-A / L-A′ / L-B / L-C、七日双轨倒排（11-09→11-15）、五个阻塞决策点 B-1~B-5 与总兜底、G-01~G-13 待核清单。
- **三条硬边界**：不输出获奖概率、名次预测、评审口味；不把推断写成规则；规则未确认前不做不可逆投入。本包只产出计划，**未代为公开发布、未代为提交投稿**。执行前置门为「预检 → 确认 → 执行」。
- **flag 状态**：`status: flagged`、`stale_after: 2026-11-25`。复核触发条件写「**活动页公告变更**」而非日历到期（F-005、F-006、F-070、M-08），并落成可机械执行的 **T-1~T-7 复核触发检测表**（含当前基线：publishVersion 12、SUBMIT_END、FORM_OPTIONS 6/7 项、参与奖名额、PDF 直链、结果公示）。
- **索引对账**：industry 组 45→**46** 束；sheke 域 94→**95** 束；总索引 720→**721** 束（分组 64、域 9 不变）。计数面涉及 `doc/bundles/index.md`（frontmatter `total_bundles`、正文计数行、mermaid sheke 节点、域节标题、域分组表 industry 行）、`doc/bundles/sheke/index.md`（AI 行业方向描述与分组导航行的 45 束）、`doc/bundles/sheke/industry/index.md`（description、导航表新行、toctree 新条目）。
- **并发隔离**：工作区存在他方会话在途 WIP（`.trae/specs/okf-wiki-ecosystem/wechat-intelligence-hub-source-deepening/`，以及本束落盘过程中新增的未跟踪束 `doc/bundles/jishu/ml/tvm-tirx/`）。按「**谁添加谁对账**」原则，本束**不代改**他方 WIP 的计数面；本束完成时先落到 720→721 / sheke 94→95 / industry 45→46，随后他方会话自行把总索引对账到 722 / jishu 528，共享工作树最终五面一致（见下方 Verification）。共享索引文件只做与本束增量直接相关的修改，保留他方已有内容。
- **落盘后复核修正（E-06／E-07／E-08／E-09）**：① 概念页与参考页初稿沿用同簇旧束的 `/concepts/…`、`/references/…` 根相对链接，`check-section-anchors.py` 报 30 处「目标文件不存在」；已全部改为目录相对链接，复跑 12 文件全通过。② 方案 §0 资产数字初稿为全库口径，已对齐 `check-asset-baseline.py` 的 `doc/bundles/` 子树唯一合法基线。③ 收尾机械复核实测本包 **12 个 `.md` 文件 / 11 个含 frontmatter**，初稿多处误写「11 个文件／11 篇文档」「索引与日志 3」「10 个含 frontmatter」，已全量改为 12／4／11。④ F 编号扫描声明补上口径限定：全文正则得 78 行，其中 6 行是 §1 G1 豁免表的引用行；**主事实表 72 行、1..72 连续无重号**。四条勘误同步登记于 [核验报告 §5](references/verification.md)。
- **前端事实与规则事实分离**：细则正文只写「提交以下信息：社媒发布链接、作品介绍、UserID、联系方式**等**」（F-022）；8 项字段、字段长度限制、校验顺序、UserID 与登录账号一致性、提交即定稿等均来自前端代码（S3/S4），已在 03 篇与 F-041~F-053 明确标注信源，不伪装成细则明文。

### Verification（落盘自检）

- ✅ `references/facts.md` **主事实表**：F-001~F-072 连续无跳号（正则 `^\| F-(\d{3}) \|` 限定主事实表实测 72 行、集合等于 1..72、无重号；若扫全文则得 78 行——多出的 6 行是 §1 G1 豁免声明表的引用行，见 E-09）；G-01~G-13、M-01~M-08 均连续。
- ✅ G1 机械扫描：精确词表命中恰 6 条且编号集合等于 `{F-012, F-038, F-058, F-062, F-063, F-069}`，与豁免声明一致。
- ✅ `scripts/check-toctrees.py`：束内 12 个文件零断链、零孤立内容；束根 toctree 的 `concepts/index`、`references/index`、`log` 三条均可达；concepts / references 子索引 toctree 完整覆盖各自目录内容。
- ✅ `scripts/check-bundles-index.py`：**9 域 / 64 组 / 722 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致。其中本束贡献 1 束（720→721、sheke 94→95、industry 45→46），他方会话的 `tvm-tirx` 贡献另 1 束（jishu 527→528）并自行完成对账；本束未代改其计数面。
- ✅ `scripts/check-section-anchors.py`（本束范围）：12 个文件全部章节锚点可解析，零断链。
- ⚠️ `scripts/check-asset-baseline.py`：三处规模数字单一真相源对账通过、`.spec/` 泄漏守卫通过；但「行尾归一校验」因**工作区存在未提交内容漂移**（本束 12 个新文件 + 他方 WIP）而报残差超过容差，提示「请先提交或 stash 工作区变更再复跑」。残差是随工作区增量漂移的量、非固定值：首次复跑 +248,860，最终复跑 **+310,787**。这是未提交新束的预期状态，非本束数字口径错误；C 阶段按体例**不做 git 提交**，故留待提交后复跑。方案 §0 已改用该门禁打印的 HEAD 基线值。
- ✅ `scripts/check-utf8.py`：全部文件为有效 UTF-8、无 BOM。
- ✅ frontmatter：11 个含 frontmatter 文件开闭围栏齐备、`type` 必填字段齐备；`log.md` 按体例无 frontmatter；`okf_version` 仅出现在束根 `index.md` 的 frontmatter 中。
- ✅ 相对链接可达、零 `file:///` 绝对路径链接；四个跨束互链目标（`workbuddy-1024-contest`、`zhihu-ai-science-workshop`、`ai-project-submission-and-content-publishing-guide`、`workbuddy-opc-whitepaper`）实测均存在。
- ✅ 敏感信息零残留：未写入任何 token / 密钥 / 本机绝对路径 / 真实 UserID / 手机号；方案页引用的敏感束目录名均经目录存在性核验。
- ✅ 编号族无撞号：F / G / M / C / I / V / B / T / E / L 各族互不重叠（L-A~L-C 为层名而非编号族）。
- ✅ **收尾复跑**：`check-bundles-index.py`（9 域 / 64 组 / 722 束）、`check-toctrees.py`、`check-utf8.py`（13,037 个文件）、`check-section-anchors.py`（本束 12 文件）四项均 `exit 0`；`check-asset-baseline.py` 因未提交内容漂移 `exit 1`，属已登记的预期状态。
