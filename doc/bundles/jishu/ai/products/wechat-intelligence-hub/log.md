# WeChat Intelligence Hub 知识包变更日志

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
