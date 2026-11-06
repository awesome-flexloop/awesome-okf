# WeChat Intelligence Hub 知识包变更日志

## 2026-11-06 · 初版生成（微信博文 → OKF v0.2 Bundle）

- **来源**：微信公众号「开源食谱」《5 天攒 2000 星！让微信聊天变情报库，相见恨晚！》（原创，豆芽菜小萌，2026-09-24 07:02 北京）
- **方法论**：`/七概念` 场景 4 知识沉淀链路 **R→I→E→V→入库**，由 `blog-article-to-okf-wiki` 七阶段工作流承载；指令经 `specweave-slash-alias-resolution` 解析（`.agents/commands/seven-concepts.md` + `seven-concepts-cmd`）
- **规模**：10 个 Markdown 文件（6 concepts + 2 references + 2 目录 index + 根 index + 本日志）；F 编号事实 **57 条**（博文 40 + 官方核验 17）
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

机械门禁（2026-11-06，详见下方表格，结果以最终复跑为准）：

| 检查项 | 结果 |
|--------|------|
| 双份 F 编号正则核对（spec `facts.md` ↔ `references/article-source.md`） | ✅ 各 57，F-001~F-057 连续无跳号、集合相等 |
| 总索引计数对账 `check-bundles-index.py` | 见 V 阶段最终复跑记录 |
| toctree 完整性 `check-toctrees.py` | 见 V 阶段最终复跑记录 |
| UTF-8 严格编码 `check-utf8.py` | 见 V 阶段最终复跑记录 |
| 资产基线 `check-asset-baseline.py` | 见 V 阶段最终复跑记录 |
| 相对链接可达 / 无 `file:///` | ✅ 本束内与跨束链接逐一核对（跨束仅引用已存在的 wigolo / agent-reach / inkos / creatorhub） |
| frontmatter 完整 | ✅ 根 `okf_version`/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources` 齐备，3 个信源 |
| 敏感信息 | ✅ 无家目录绝对路径、无密钥、无真实聊天数据 |
| 勘误落实 | ✅ 8 项 ⚠️ 在正文均呈现官方口径并标注博文来源 |

### 并行会话计数登记

- 本次开工时总索引 `total_bundles` 已由并行会话更新为 **714**（此前记录为 713）；`check-bundles-index.py` 复跑确认地面真值为 **9 域 / 64 组 / 714 束**、五面一致，故本束入库后按地面真值记为 **715**（jishu 524 / ai 288 / products 39），不追加第三次数。
- `jishu/index.md` 域导航页的多数分组束数为历史过期值，页面自身声明「递归束数以知识包总索引为准」；本会话仅同步其 AI 行描述中的 287→288，不扩大变更范围。

### C（提交）

- 待原子提交（用户未要求执行，本会话不 commit / 不 push）：① 子模块 `projects/awesome-okf-xs` 内提交 bundle 10 文件 + `products/index.md` + `ai/index.md` + `jishu/index.md` + `bundles/index.md` + `README.md` + `doc/index.md` → ② 主仓库提交 spec（`.trae/specs/okf-wiki-ecosystem/wechat-intelligence-hub-blog-okf-wiki/`）→ ③ 主仓库更新子模块 gitlink。
