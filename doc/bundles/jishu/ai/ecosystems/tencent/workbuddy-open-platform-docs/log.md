# 变更日志

## 2026-10-16

### 一、七阶段执行（R→I→E→V，附汇总）

- ✅ **R（事实采集）**：对 11 个已声明 URL（D0 `dashboard` 导航面 + D1～D10 十篇 `/docs/` 内容页）逐页采集，产出页级覆盖台账与逐页事实草稿（`- R-<slug>-NN`，共 513 条），并归并、去重、统一编定为 **F 编号事实表 F-001～F-439（439 条）**，落于 `references/article-source.md`。
- ✅ **I（归并 / 编定）**：来源代号表（D0～D10）与 `references/source-manifest.md` 的页级台账一一对齐；声明级事实与页级覆盖分立两文件，编号统计与来源覆盖（逐页 F 条数、去重口径）经机械核对。
- ✅ **E（concepts / examples）**：按十篇 `/docs/` 页的内容结构编定为 **11 篇概念**（`concepts/`，索引 + 00～10）与 **5 篇操作用例**（`examples/`，索引 + 00～04）。
- ✅ **V（核验 / 门禁）**：核验总表、勘误清单（E1～E3）、五类口径分层并列登记表、跨页口径不一致并列登记、官方未给清单、信源距离评估与 V 四视角对抗审查，落于 `references/verification.md`；`status` 裁决为 `stable`、`stale_after` = 2027-04-16。
- ✅ **汇总**：束根 `index.md`（含内容性质块、可信度状态块、分层导读表、已知边界、主题关联、一句话结论）与 `log.md` 于本日产出。

### 二、覆盖统计（机械真值）

- **已声明 URL**：**11 个**（D0 导航面 + D1～D10 十篇 `/docs/` 内容页），11 个全部返回 **HTTP 200**；D0 实测为**客户端渲染的 SPA 外壳**（20,367 字节，含 8 个 `<script>`、1 个应用挂载点），无正文、**不产生 F 编号**，仅登记为导航面。
- **站点侧栏 `/docs/` 页集合**：**17 篇 slug**——已声明并处理 **10**、本次未采集仅登记入口 **7**（`api-token` / `contact` / `developer-profile` / `legal-basis-and-examples` / `operations-data` / `service-categories-individual` / `service-categories-enterprise`）、非页面布局资源**排除 1**（`layout-216c2d1532f8d94c`）；`/docs/` 链接命中并集（去重后）**18 项 = 17 篇 slug + 1 项非页面资源**；`已声明 − 已处理` 与 `已处理 − 已声明` **双向差集为空**。
- **F 编号事实**：**F-001～F-439 共 439 条**，全部来自 D1～D10 十篇内容页。
- **全束 Markdown**：**24 个**——束根 **2**（`index.md` / `log.md`）+ `concepts/` **12**（index + 00～10）+ `examples/` **6**（index + 00～04）+ `references/` **4**（index + article-source + source-manifest + verification）。
- **正文提取量**：10 篇内容页（D1～D10）正文容器可解析文本合计 **97,917 字符**（单页 `extract_chars` 相加：416 + 1,739 + 2,087 + 2,284 + 13,675 + 11,006 + 15,641 + 5,908 + 16,992 + 28,169）；该量为「可解析文本字符数」，**不等同全文篇幅**，不构成完整性判定。

### 三、口径决策

- **范围收敛**（取自用户 2026-10-16 的批准门确认）：本束**严格按 11 个已声明 URL** 采集与登记，站点侧栏其余 **7 篇**仅**登记入口**——只证明「该 slug 存在于站点侧栏」，**不采集正文、不推断能力**。
- **束粒度裁定**（取自用户 2026-10-16 的批准门确认）：采用**单束**结构，且 **Open API 拆为 07（认证与通用约定）/ 08（接口目录）两篇**。
- **跨页冲突并列不择一**：签名填充算法 `PSS`（F-308）对 `PKCS#1 v1.5`（F-346）、凭证有效期 `24h`（F-285）对 `expires_in: 3600`（F-366）——两处均**并列表述、不择一、不替官方判定**（详见 `references/verification.md` 第四节）。
- **未写明一律标「官方未给」**：分成比例、结算周期、全局限流与配额、审核时长（除分享应用 7 个工作日 F-294）、移动端开放时间点等文档未给出者，一律标「**官方未给**」，**不得据页面名称、同组其他束或常识补全**，也**不得写成「默认无限制」**。

### 四、采集方式与登录依赖对比

- 本次采集为**纯 HTTP GET**（`Invoke-WebRequest`），D1～D10 十篇 `/docs/` 页均为**服务端渲染**，纯 HTTP GET 即可取得正文，十页共用同一正文容器（容器类名 `prose-docs_root__dXUM0`，`div` 元素），本次**无页面采集通道变化**；**无登录会话依赖**。
- **对比同组公告束**：同组 `workbuddy-open-platform-sharing-and-promotion` 束的两篇平台公告位于 `/dashboard/contents/...`，需**已登录会话**方能读取渲染后正文；本束信源位于 `/docs/`，实测**无登录依赖**。两束采集条件不同，**不可互相套用**。
- **未实跑声明**：全过程**未注册开放平台账号、未申请任何认证与资质、未提交任何审核、未生成密钥与 token、未调用任何真实接口**。

### 五、勘误与偏差

- **勘误 E1～E3（文档自身缺陷）**：
  - **E1**：D5「连接器」页 `mcp.json` 远程 MCP 示例 URL 原文含乱入文本 `https://mcptokenSchema 字段.example.com/mcp`（F-105）；属站点编辑错误，**不得**作为可用端点照抄、不擅自更正。
  - **E2**：D2「入驻开放平台」页个人认证必填信息「开发者真实姓名 / 真实姓名」并列（F-040）；照抄并列、不合并、不推断哪项是笔误。
  - **E3**：D5/D6/D7 正文存在悬空章节引用（「见 6.3 / 6.4 / 第六节 / 第九节」），正文中找不到对应编号章节；登记为**文档内部引用缺陷**，**不得据编号推断被引用内容**。
- **偏差 / 张力登记（不裁决）**：
  - `concepts/05-buddy-app-develop-and-publish` 篇的「**六个维度**」措辞与该页实际 **5 个 h3** 存在张力，**并列登记、不裁决**。
  - `concepts/04-expert-and-expert-team` 篇的 **tags 存在两种口径**，**并列保留**。
  - `concepts/05-buddy-app-develop-and-publish` 篇的规格表述存在 **3–5 与 2–4 两种口径**，**并列保留、不择一**。
- 上述偏差均**如实登记、不改写原文**；如需判定须回源官方页面另行采集。

### 六、门禁运行方式

- **显式声明（据实记录，不谎报）**：本次**直接运行子模块底层脚本**——`python scripts/check-utf8.py`、`python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`；**未运行 `invoke gates.*`**（任务以脚本口径为准）。
- **已补充**：机械门禁与索引计数结果已落于「### 九、索引接入与门禁实测」（Task 6）与「### 十、机械门禁实测（Task 7）」两节。

### 七、独立评审结论（R1）

- **独立上下文评审 R1：`pass`（2026-10-16）**。评审者为 fresh-context 只读子代理，**未参与实施、未参考实施者自验结论**，全程未修改任何文件、无 git 写操作。
- **检查点结果**：CP-R1～CP-R6 六项 `rule` **全部 `pass`**；**CP-U1（教程可用性与知识分层质量）= 5/5**、**CP-U2（评审独立性与证据质量）= 5/5**（阈值均 ≥4）。
- **独立复核方式**：自跑 `check-bundles-index.py` / `check-toctrees.py` / `check-utf8.py`（均 EXIT 0）、定向 Sphinx dummy 构建（EXIT 0、本束 WARNING 0）、`git status` / `git diff --numstat`（两既有束各恰 +1 行）、自写正则脚本（F 双份集合 439/439 差集 0、24 文件 frontmatter 核对、242 条相对链接存活 242）；并**以 HTTP GET 回源 9 个官方页面做反证抽查，13 条 F 事实全部命中、无歪曲**。
- **可行动发现：0 条**。advisory **F1**（`references/verification.md` 门禁小结第 5 行 `file:///` 计数口径失准）已**当场收口**，改为精确口径「全束 12 行命中 / 3 处字面用法，每处均有相邻『引述原文协议形态』标注」。
- 评审记录见 `.trae/specs/okf-wiki-ecosystem/workbuddy-open-platform-docs-okf-wiki/review.md`。

### 八、并行在途观测

- 若观察到同组其他束或总索引被并行会话改写，本束将以「**披露不修复**」（归属隔离）方式记录于本节，不代改、不扩大修复范围。
- **本时点观测（2026-10-16）**：Task 6 接入索引计数后复跑门禁 2 / 3 **均零失败**，**未见既有束或并行会话导致的索引 / toctree 漂移**；「信源」基数不可由显式口径复现的观察已记入「### 九」（按增量登记、不重定基数）。后续若观察到并行改写的束或索引，将在此逐条登记。

### 九、索引接入与门禁实测（2026-10-16）

本次将本束接入五级索引（tencent 分组页 → ecosystems 分类页 → jishu/ai 类别页 → jishu 域页 → bundles 总索引），并回补同组两束互链；全程只做索引计数同步，未改动任何内容文件。所有数字以 `scripts/check-bundles-index.py` 的目录树地面真值与增量机械复算为准，未手工估算。

**改动前 → 改动后各层计数**

| 层级 | 位置 | 改动前 | 改动后 |
| --- | --- | --- | --- |
| 束根分组页 | `tencent/index.md`「关于本分组」 | 16 束 / 124 概念 / 43 示例 / 72 信源 / 2393 事实 | 17 束 / 135 概念 / 48 示例 / 76 信源 / 2832 事实 |
| 生态分类页 | `ecosystems/index.md` | 类总 92；腾讯行 16 | 类总 93；腾讯行 17 |
| AI 类别页 | `jishu/ai/index.md` | 类别 244；ecosystems 行 92 | 类别 245；ecosystems 行 93 |
| 技术域页 | `jishu/index.md` | ai 行简介 244 | ai 行简介 245 |
| 总索引 | `doc/bundles/index.md` | total_bundles 639 / 计数行 639 / mermaid jishu 473 / 节标题 473 / ai 行 244 | 640 / 640 / 474 / 474 / 245 |

增量口径（机械复算）：束 +1、`concepts/` 内容文档 +11、`examples/` 内容文档 +5、`references/` 文件 +4（含 index.md）、编号事实 +439（F-001～F-439，取 `references/article-source.md` 最大 F 编号）。

**`check-bundles-index.py`**

- 改动前：退出码 **1**，3 处漂移——`frontmatter total_bundles=639，目录树实际 640 束`、`jishu/ 节标题（L135）声明 473 束，目录树实际 474 束`、`jishu/ 分组表束数列之和=473，目录树实际 474 束`。
- 改动后：退出码 **0**，输出 `bundles 总索引对账通过: 9 域 / 61 组 / 640 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`

**`check-toctrees.py`**

- 改动前：退出码 **1**，25 处——24 条「未收录(不可达)」与 1 条「缺失条目（`tencent/index.md` 的 toctree 未收录 `workbuddy-open-platform-docs/index`）」，**全部归属本束**（新束文件已落盘、索引尚未收录所致）。
- 改动后：退出码 **0**，输出 `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。`；无任何失败项残留，本束相关命中为零；未发现属于既有束或并行在途新束的问题。

**「信源基数是否可复现」观察**

- 依据 `references/` 目录文件数（含 `index.md`）逐束机械求和，变更前同组 16 束 references 文件数之和为 **79**，而 `tencent/index.md`「关于本分组」声明基数为 **72**，二者不一致——**「信源」基数不可由显式目录口径复现**（历史上即属此例）。故本次**按增量登记 +4（72 → 76）、不重定基数**。
- 对照：束数 16、概念 124、示例 43 **均可由目录树口径机械复现**，故按 +1/+11/+5 精确同步；事实按 F 编号增量 +439 同步（2393 → 2832）。

**改动范围核对（`git status --short`）**：5 个索引文件的计数面被同步（`doc/bundles/index.md`、`jishu/index.md`、`jishu/ai/index.md`、`jishu/ai/ecosystems/index.md`、`jishu/ai/ecosystems/tencent/index.md`），另 2 个既有束 `index.md` 各回补 1 行互链（`workbuddy-official-docs`、`workbuddy-open-platform-sharing-and-promotion`，`git diff --numstat` 各为 `1  0`），共 7 个受跟踪文件被修改；本束其余 23 个文件未被改动（仅本 `log.md` 追加本节，且本束整体仍为未跟踪新目录）；未发现既有索引存在需披露的并行会话不一致（门禁五面全通过）。未执行任何 `git commit` / `push`。

### 十、机械门禁实测（Task 7）

本节为 Task 7 机械门禁实测记录。**门禁运行方式**：本次**直接运行子模块底层脚本**（`python scripts/check-*.py`）与定向 Sphinx 构建，**未运行 `invoke gates.*`**——如后续文档提及，须以此说明为准。全部命令在 `projects/awesome-okf-xs/` 下执行，下列数字为实跑原值。

1. **UTF-8**：`python scripts/check-utf8.py` → 退出码 **0**；关键输出 `UTF-8 检查通过: 11675 个文件均为有效 UTF-8。`
2. **toctree**：`python scripts/check-toctrees.py` → 退出码 **0**；关键输出 `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。`；**本束名零命中**，无既有束或并行在途失败项须归属披露。
3. **bundles 总索引**：`python scripts/check-bundles-index.py` → 退出码 **0**；关键输出 `bundles 总索引对账通过: 9 域 / 61 组 / 640 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`
4. **链接存活**：对束内 **24 个 `.md`** 递归提取全部 Markdown 相对链接（提取括号内目标，跳过 `http`/`mailto:`）并解析为绝对路径后逐条 `Test-Path` → **存活 242 / 失败 0**，失败项列表为空。
5. **`file:///` 与本机绝对路径**：Grep `file:///` 与 `C:\Users` → `C:\Users` **0 命中**；`file:///` 原始文档内容命中 **6 行 / 分布于 3 个文件**——`concepts/08-openapi-endpoint-catalog.md` L283、L291；`examples/03-oauth-and-call-openapi.md` L191、L192、L233；`references/article-source.md` L479（F 表 F-423 行）。其中 **5 行为经显式标注的「引述原文协议形态」例外**（官方文档所述 Artifact `uri` 协议形态字面量，非仓库路径），第 6 行（F-423 行）**原缺标注，已当场补标注收口**。连同本节记录、`verification.md` 小结与 `article-source.md` 补标注等**标签性提及**，全束 grep 共 **12 行**，**无未标注的路径用法**。
6. **frontmatter 逐文件核对（24 文件）**：`okf_version` **仅 1 处**（束根 `index.md`）；`log.md` 与 `concepts/`、`examples/`、`references/` 三个子目录 `index.md` **无 frontmatter**；11 篇 concepts（`type: Concept`）、5 篇 examples（`type: Example`）、3 篇 references（`type: Reference`）均含 `generated` / `verified` / `status` / `stale_after` 四项字段，`sources` 条目齐备。
7. **F 编号双份集合比对**：正则提取 `specs/…/workbuddy-open-platform-docs-okf-wiki/facts.md` 的 `F-\d{3}` 唯一集合，与 `references/article-source.md` 表行集合（`^\|\s*F-\d{3}\s*\|`）比对 → 两侧 **439 / 439**，差集 **0**，区间 **F-001–F-439** 连续、**无跳号、无重复**。
8. **定向 Sphinx dummy 构建**：`python -m sphinx -b dummy -E doc _build/dummy-bundle doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-open-platform-docs/index.md` → 退出码 **0**（构建输出 `build succeeded`）；构建输出汇总 **245 warnings**（全库既有/并行，属非本束），**过滤提及本束名 `workbuddy-open-platform-docs` 或其文件名的 WARNING = 0**；构建产物在 `_build/`（已 gitignore），本记录**不声称全库通过**。

**门禁抓出的本束缺陷**：**1 项**（advisory 类）——`references/article-source.md` F 表 F-423 行的 `file:///…` 原缺「引述原文协议形态」标注，**已当场补标注**；其余各项零失败。**本束内部口径一致性复核**：全束「已支持」类表述均处限定/禁止性语境（当前 PC 端已支持、移动端按「后续开放」列规划态），未见与 `references/verification.md` 第三节口径 ③ 冲突的断言式表述。

**并行在途观测**：门禁 2 / 门禁 3 零失败，本时点未见既有束或并行会话引起的索引/toctree 漂移，无需披露项。

**纪律**：本任务**未执行任何 `git commit` / `push`**。
