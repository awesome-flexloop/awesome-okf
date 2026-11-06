# WeChatBridge iOS 版知识包变更日志

## 2026-11-06 · 初版生成（微信博文 → OKF Bundle，status: flagged）

- **来源**：微信公众号「苍何」《开源微信流 APP，手机微信聊天记录，可以直接给 WorkBuddy 和 Obsidian 了》（2026-10-27 16:28 湖北，第 613 篇原创；F-001/F-002）
- **触发**：`/七概念` → 指令 `seven-concepts`（`.agents/commands/seven-concepts.md`）+ 门面 `seven-concepts-cmd`；能力注册表 `02-skills.md` / `03-commands-*.md` 两处登记行已核对。场景 4「知识沉淀」链路 **R→I→E→V→C**，由 `blog-article-to-okf-wiki` 七阶段执行
- **权威核验源**：`freestylefly/WeChatBridge` 官方一手件 —— GitHub REST API、`README.md`、`docs/design/ios-dev-spec.zh-CN.md`、`ios-schedule.zh-CN.md`、`ios-验收记录.zh-CN.md`、tree/contents API（F-062~F-080）；辅以权威第三方转述（F-081~F-084）
- **规模**：16 文件（6 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志）；F 编号事实 **84 条**（博文 F-001~F-061 + 官方/第三方核验补充 F-062~F-084）
- **归属**：`jishu/ai/products/wechatbridge-ios-relay/`（主线实体为终端工具产品的 iOS 版；同组已有 wigolo / agent-reach / craft-anything / wechat-intelligence-hub 等「微信博文经 OKF v0.2 转化」先例；单篇博文未新建分组）

### R（事实采集与核验）

- 强制回读磁盘原文：根 `AGENTS.md`、`.agents/context-routing.md`、`projects/AGENTS.md`、`projects/awesome-okf-xs/AGENTS.md`、内容敏感度预检规范、frontmatter 规范与子项目 `context-routing.md`（三锚点确认）。
- 内容敏感度预检：URL 为 `mp.weixin.qq.com/s/<id>` 公开短链，无 `code=` / `token=` / 邀请码 → **Public** → 标准 Spec Mode（spec 在 `.trae/specs/`，产出在子项目 `doc/bundles/`）。
- **流程偏差登记**：Skill Gotcha 记载 `mp.weixin.qq.com` 反爬确定、应直接改用 `browser_use` 取 `#js_content`；**本次 `WebFetch` 直接返回完整正文与元信息，未触发回退**。无内容损失，未启动浏览器，照实登记。
- 信源距离预判：源文为**产品方作者自述**（正文用「我们的产品」「我们把微信流搬上了手机」，F-008），属「厂商/作者自宣 + 作者一手实测」混合；全部成效数字默认 P0 必核验，bundle index 顶部设自述数据提示块。
- GitHub `git/trees/main?recursive=1` 返回**部分截断**：只登记可见条目，F-071 明确写「`ios/` 约百余条」，禁止写成精确值；`macos/Sources/WeChatBridgeCore` 路径改由 README 与 dev-spec 交叉印证。
- P0/P1 权威核验 **24 项：12✅ / 8⚠️ / 4❌**，详见 [references/verification.md](references/verification.md)。统计口径：✅ V-01~V-12、⚠️ V-13~V-20、❌ V-21~V-24。
- **勘误四张清单**齐全：日期/版本表、成效数字溯源表、口径对照表、引文逐字核对表。
- **4 项 ❌ 中的 2 项为核心声明**：V-21（iOS「开发完成 / 正在提审」）与 V-22（灵动岛入口）被官方 README 路线图、dev-spec §12、验收记录逐项收窄或证伪；V-23（「哪家都能吃」）与 V-24（10-27 称「开源模型」而权重 11-04 才公开）为范围/时点拔高。
- **动态数字三轴口径**：时间轴（1.7k star @10-27 vs 2024 @11-06）、主体轴（6 小时作者自述净运行时长 vs 18 工作日含真机验收的全职档期）、定义轴（10-27「开源模型」vs 11-04 权重公开）。明确**禁止相除得「提效倍数」**。

### I（骨架、归属与洞察）

- **操作可复现性两问**：① 博文给出两段可逐字复制的提示词（F-046/F-047）与 iOS 五步流程（F-014/F-017/F-020/F-025/F-027）→ 是；② 明确模型版本、输入、`docs/design/` 产出路径与「确认理解 → 出文档 → 人审阅 → 按 T 编号执行 → 逐任务汇报 → 验收复跑」顺序（F-037/F-054/F-071/F-072/F-078）→ 是。→ **技术教程/方法论骨架，设 `examples/`**。
- **重要边界**：可复现的是**提示词驱动的文档/验收设计流程**，不是 iOS App 安装（App 未上架且完成态被官方收窄）。三篇 examples 顶部统一标「非官方模板、本知识包未实机验证」，不含 IPA / 签名 / TestFlight 步骤。
- 三层知识拆分：身份与信源距离（00）→ iOS 能力对照（01）→ 方法论链（02）→ 验收控制面（03）→ 验收记录与勘误落实（04）→ 可迁移模式与采用边界（05）。
- 归属决策：主线实体优先 + 查同组先例 + 单篇博文禁止新建分组；排除 `practice/`（方法论组）、`sheke/industry/`（行业趋势）。
- **并行会话避让（幂等规则）**：开工时 `products/wechatbridge/` 已存在并归属**另一篇**文章（`mp.weixin.qq.com/s/QdCiRiwjjc5uOvBW0nBZxw`，2026-09-24 产品推介文，见 `.trae/specs/okf-wiki-ecosystem/wechatbridge-okf-wiki/spec.md`）。按「目标目录已存在必须先读其 log/index 判定重建或更新、禁止静默覆盖」，改用带语义后缀的 `wechatbridge-ios-relay/`，并在两束 index 与 `references/article-source.md` 写明主题分工与互链。
- 洞察四元组（观察 / 机制 / 可迁移条件 / 反例边界）写入主仓库 `insights.md` 与 [concepts/05](concepts/05-transferable-patterns-and-boundaries.md)；G2 门通过。

### E（bundle 生成）

- **信源先行**：`references/article-source.md` → `references/verification.md` → `concepts/` → `examples/` → 各级 `index.md` → 根 `index.md` → 本日志，生成顺序严格遵守。
- 双份 F 编号：spec `facts.md` 为人工正本，bundle `article-source.md` 为带核验标注的第二份登记；V 阶段用正则 `^\|\s*F-(\d{3})\s*\|` 比对，集合相等、F-001~F-084 连续无跳号。
- 所有数字、版本、命令、文件名、日期携带 F 编号；`facts.md` 之外未新增事实；模板与伪代码标注为编者整理。
- **frontmatter 规范取舍**：按 `.agents/rules/frontmatter.md`，`okf_version` 仅允许出现在 bundle 根 `index.md`；12 篇内容文档均带唯一必填字段 `type`，三个目录 index 沿用同组现行惯例不带 frontmatter，登记备查。
- **V 阶段编号对齐修复**：`article-source.md` 的 11 条 F 行原引用 R 阶段早期 V 编号（如 F-009 → V-05、F-019 → V-11、F-037 → V-22），与最终核验表重排后的编号冲突。已按 [verification.md](references/verification.md) 逐条对齐：
  F-009/F-010→V-21、F-018→V-15、F-019→V-22、F-022→V-23（后半）/V-16（前半）、F-037→V-18/V-24、F-039/F-055→V-14、F-041→V-19、F-042→V-12、F-061→V-20。
- **引文链接去标记**：官方 dev-spec 首句原文含「档期文档」的 Markdown 链接标记（目标为 `ios-schedule.zh-CN.md`），逐字引文若保留会被 Sphinx 解析成本束相对链接并断链。已在 `facts.md`（正本）、`article-source.md`、`verification.md` 三处改为「去链接保留文字 + 括注原文链接目标」，事实语义不变；本日志描述该修复时同样只作文字说明，不复写链接语法。
- 相对链接按 bundle 深度逐一核对：`concepts/` 与 `examples/` 用 `../` 回束根，`references/` 内互链用同目录相对路径；跨仓库 spec 路径一律只作文字说明，不作相对链接。

### V（对抗审查与机械门禁）

**四视角审查**：

| 视角 | 发现与处置 |
|------|-----------|
| 🔴 魔鬼代言人 | 「iOS 已开发完成」会不会只是官方 README 未及时更新？→ 同时核对 README 路线图 `[ ] iOS 版`、dev-spec §10 交付定义未全打勾、§11 Q2「上架中国区需要 App 备案」仍待决、验收记录 R3–R6「待真机」四处独立一手件，均指向开发中；故判 ❌ V-21 而非 ⚠️ 时点差异 |
| 🟠 老板视角 | 源文是产品方自述，可信度够不够？→ index 顶部「四项不要照抄」+「厂商/作者自述数据提示」双块；四层信源距离写入 concepts/00；`status: flagged`；`stale_after` 缩短至 2027-01-31 |
| 🔵 未来视角 | iOS 状态与模型口径两周内就会变 → concepts/05 §6 四项到期复核清单（上架状态、灵动岛、R3–R6 真机、权重开放后措辞） |
| 🟣 新人视角 | 读者可能把「6 小时 vs 18 工作日」当成提效倍数，或把 examples 当成安装教程 → `article-source.md`「事实使用约束」6 条 + concepts/02 / 05 + examples/index.md 三处重复声明；iOS 未上架与「不是安装教程」在 index 与 examples/02 顶部各写一次 |
| ⚪ 证据强度 | 「待真机」是否被推测填补？→ 全文采用 ✅ / ⚠️ / ❌ 三态，官方 R3–R6 一律保留「待真机」，R7 保留「模拟器通过，待真机」；不以截图图注补写 UI 细节 |

**状态决策记录**：按 `blog-article-to-okf-wiki` §6 步骤 6.4，`flagged` 只在「P0 出现 ❌ **且**失败项为核心声明」时启用。本次 V-21/V-22 命中核心声明，
故设 **`status: flagged`** 并四处落地：① 根 index frontmatter；② verification.md 顶部；③ 根 index「阅读前必知」；④ concepts/00 读前须知。
对照同组 `wechatbridge`（0❌ → `stable`）与 `wechat-intelligence-hub`（0❌ → `stable`），**未滥用 flagged，也未把核心 ❌ 藏进 stable**。

**机械门禁结果**（2026-11-06 全部文件落盘并接线后终检复跑）：

| 门禁脚本 | 结果 | 说明 |
|---------|------|------|
| `scripts/check-bundles-index.py` | ✅ **rc=0** | `9 域 / 64 组 / 718 束`，frontmatter、计数行、域节标题、分组表、toctree 五面一致 |
| `scripts/check-toctrees.py` | ✅ **rc=0** | 接线前本束贡献 1 处红灯（根 index 的 `log` 引用未落盘）；本日志写入后消除，全库零残留 |
| `scripts/check-utf8.py` | ✅ **rc=0** | 终检复跑 12961 个文件均为有效 UTF-8（接线当次 12960，本日志落盘后 +1） |
| `scripts/check-asset-baseline.py` | ⚠️ rc=1（非本束缺陷） | 唯一失败项为「行尾归一失效，残差 +245636」；其**数字口径校验已通过**（读取 `total_bundles: 718`）。属工作树含并行 WIP + Windows `core.autocrlf` 环境级假红，脚本自身要求「提交或 stash 后复跑」 |
| `scripts/check-section-anchors.py` | ⚠️ 全库历史基线红 | 存量锚点/断链问题；按本束路径过滤后本束贡献为 **0 处**（详见主仓库 spec 目录下 `review.md`，跨仓库路径不作相对链接） |

> **读数纪律**：全部计数以落盘后重新扫描的**目录树地面真值**为准，不沿用会话摘要快照。
> 接线前回读为 717 束（并行会话已从 715 推进到 717），本束落盘后 `scan_tree` 确认为 718，故按 **+1** 增量接线，未整体重写、未重复累加。
> 全库级红灯一律先做**归属核对**（按本束路径过滤）再记结论，避免把外部 WIP 误记为本束缺陷。

**`invoke gates.*` 不可用**：`python -c "import invoke"` → `ModuleNotFoundError: No module named 'invoke'`（沿用仓库既有结论）。
按 `blog-article-to-okf-wiki` §7，**不声称「gates 通过」**，改以上述脚本直跑 + 下列手动等效验证替代。

**手动等效验证**（全部通过）：

| 项 | 结果 |
|----|------|
| 文件清单 | **16 个 md**（6 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志） |
| F 编号双份登记 | spec `facts.md` 84 条 / bundle `article-source.md` 84 条，**集合相等、F-001~F-084 连续无跳号、双向差集为空** |
| 全文 F 引用越界 | 16 篇共引用 84 个编号，**越界 0**（不存在引用未登记事实） |
| V 编号交叉引用 | 修正 11 处早期编号后，全文 V-01~V-24 引用与核验表逐条对应，无悬空编号 |
| 相对链接 | 全束 `](...)` 逐条解析，**断链 0**（含 4 处 `log.md` 待本日志落盘、2 处引文链接标记已去链接） |
| `index.md` toctree | 4 个 index 全部含 `{toctree}`；计数排除 `:hidden:` / `:maxdepth:` 等 `:` 开头指令行 |
| OKF v0.2 frontmatter | `okf_version` **仅**出现在根 `index.md`；12 篇内容文档均带 `type` |
| 章节体量 | 最长 `index.md` 156 行，无超 600 行文档，符合概念型 ≤300 行分层 |
| flagged 四处落地 | frontmatter / verification 顶部 / index 边界 / concepts/00 读前须知，逐项勾对 |

**外部未提交变更登记（不计入本束结论）**：

1. `wechatbridge/`：另一会话维护的**同项目不同博文**束，本次未修改、未代接线；两束已在各自 index 做主题分工互链。
2. `workbuddy-wechat-chat-forward-skills/` 等并行 WIP 造成 `check-asset-baseline.py` 的字节残差；待各会话提交后基线门禁可自行转绿。

### C（提交顺序与并行会话隔离）

- 本次**仅落盘，未提交、未 push**（用户未要求提交）。子模块 `projects/awesome-okf-xs` 为 gitlink 追踪；
  若后续提交，顺序应为：① 子模块内提交（本束 16 文件 + `products`/`ai`/`jishu`/`bundles` 四级 index + `README.md` + `doc/index.md`）→ ② 主仓库提交 spec 目录 `.trae/specs/okf-wiki-ecosystem/wechatbridge-ios-relay-blog-okf-wiki/` → ③ 主仓库更新 gitlink；
  且 `git-commit-utf8.py` 必须显式列全文件，不传目录参数、不 push。
- **索引接线与计数同步**（以磁盘真值做增量，未整体重写）：
  `doc/bundles/index.md` 717→718（`total_bundles`、计数行）、526→527（mermaid + 域节标题）、290→291（ai 分组表束数列）；
  `products/index.md` 41→42（束数行 + 本束导航行 + toctree `wechatbridge-ios-relay/index`）；
  `jishu/ai/index.md` 290→291（description + 正文 + products 41→42；六大类求和 105+95+29+42+12+8 = 291 ✓）；
  `jishu/index.md` 290→291（分组表描述）；`README.md` 717→718 / jishu 526→527 / ai 290→291（7 处）；`doc/index.md` 717→718（2 处）。
  树真值经 `scan_tree` 机械确认为 `jishu.ai = 291 / jishu = 527 / 全库 718`。
- **不触碰**并行会话在途目录 `wechatbridge/`、`workbuddy-wechat-chat-forward-skills/`，不代其修 toctree。

## 复核清单（`stale_after: 2027-01-31` 前）

- [ ] 官方 README「iOS 版正在开发中」与路线图 `- [ ] iOS 版` 是否已变更；若已上架，重判 V-21 并更新 `status`
- [ ] 灵动岛 / Live Activity 是否进入后续版本；若是，重判 V-22
- [ ] 验收记录 R3–R6 是否补齐真机结论、R7 长按是否真机通过
- [ ] 模型权重公开后的「开源」措辞复核（V-24）；星标、档期等动态数字刷新
- [ ] 证伪/证实后调整 `status`，并在本日志追加一条变更记录

## 方法论编排日志（CMD-LOG）

session `sc-20261106-wechatbridge-ios-relay-okf`，`cmd=seven-concepts`：

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261106-wechatbridge-ios-relay-okf | msg=方法论编排开始：微信博文 WeChatBridge iOS 版 → OKF v0.2 知识包 | ctx={"scenario":"knowledge","topic":"wechatbridge-ios-relay-blog-okf-wiki","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=命中触发词「全面学习」「生成 wiki 教程」，识别为场景4 知识沉淀 | ctx={"trigger":["七概念","全面学习","okf wiki 教程"],"scenario":"knowledge"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=选定标准链路 R→I→E→V→C | ctx={"chain":"R-I-E-V-C","skipped":["F","A"],"reason":"场景4 知识沉淀不需要 F 第一性原理；C 仅登记不执行"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R0 | event=SUB_CMD_INVOKED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=调用 blog-article-to-okf-wiki 七阶段工作流 | ctx={"source":"mp.weixin.qq.com/s/94FP4Cl7JIQbxU5-i3B6og","sensitivity":"Public"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=R 事实采集与 P0 核验完成 | ctx={"facts":84,"verification_items":24,"verdict":{"ok":12,"warn":8,"fail":4},"errata_tables":4}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=事实门通过 | ctx={"facts_continuous":true,"dual_registry_equal":true,"no_inference_words":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I0 | event=CONCEPT_COMPLETED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=I 骨架与归属判定完成 | ctx={"skeleton":"tutorial-with-examples","reproducibility_two_questions":[true,true],"target":"jishu/ai/products/wechatbridge-ios-relay","insight_quadruples":4}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=洞察与归属门通过 | ctx={"no_new_group":true,"precedent_bundles":4,"parallel_session_avoided":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E0 | event=CONCEPT_COMPLETED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=E 信源先行生成 bundle 完成 | ctx={"files":16,"concepts":6,"examples":3,"references":2,"indexes":4,"status":"flagged"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=模式可迁移门通过 | ctx={"source_first":true,"transferable_patterns":4,"counterexamples_declared":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V0 | event=CONCEPT_COMPLETED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=V 对抗审查完成，修复 11 处 V 编号漂移与 2 处引文断链 | ctx={"four_views":true,"v_id_alignment":11,"quote_link_fixes":3,"flagged_grounding":4}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G4 | event=GATE_PASSED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=对抗审查与机械门禁通过 | ctx={"bundles_index":"rc=0","toctrees":"rc=0","utf8":"rc=0","manual_equivalent":"all-pass","global_gate_exceptions":2}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C0 | event=CONCEPT_COMPLETED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=C 阶段仅登记原子提交顺序，未执行（用户未授权） | ctx={"committed":false,"pushed":false,"commit_order_documented":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261106-wechatbridge-ios-relay-okf | msg=全链路完成 | ctx={"documents":16,"facts":84,"insights":4,"verification":"12/8/4","status":"flagged","C":"deferred"}
```
