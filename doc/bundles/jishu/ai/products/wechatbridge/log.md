# WeChatBridge 知识包变更日志

## 2026-11-06 · 初版生成（微信博文 → OKF Bundle）

- **来源**：微信公众号「虾说AI实验室 / 虾哥」《微信聊天记录只能烂在手机里？开源 WeChatBridge 一键转给 AI 和 Obsidian》（2026-09-24 15:54 广东）
- **触发**：`/七概念` → 元指令 `seven-concepts` + 门面 `seven-concepts-cmd`；场景 4「知识沉淀」链路 **R→I→E→V→C**，由 `blog-article-to-okf-wiki` 七阶段执行
- **权威核验源**：`https://github.com/freestylefly/WeChatBridge` 默认分支 README 渲染页（抓取 2026-11-06）
- **规模**：16 文件（6 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志）；F 编号事实 **107 条**（源文 F-001~F-063 共 63 条 + 官方核验补充 F-064~F-107 共 44 条）
- **归属**：`jishu/ai/products/wechatbridge/`（主线实体为终端工具产品；同组已有 orca-ade / wigolo / knocket / octop / opencreator / agent-reach / craft-anything / wechat-intelligence-hub 等「微信博文经 OKF v0.2 转化」先例；未新建分组）

### R（事实采集与核验）

- 强制回读磁盘原文：根 `AGENTS.md`、`.agents/context-routing.md`、`projects/AGENTS.md`、`projects/awesome-okf-xs/AGENTS.md`、内容敏感度预检规范、frontmatter 规范两层路由。
- 内容敏感度预检：URL 无 `code=` / `token=` / 邀请码 → **Public** → 标准工作流；产出落 `doc/bundles/`（子项目 AGENTS.md 明确允许公开内容存放于此，按嵌套优先 + 用户显式目标路径消解父层「只读引用」边界）。
- WebFetch 抓取微信全文成功（本次未触发反爬），正文文字完整；「系统演示」四处图片内文字未随页面返回，按 **K 类缺口**登记（F-038），不补写。
- 信源距离预判：源文为**第三方公众号推介**（含 Star / 关注 CTA，未声明与项目方关系）；官方 README 为项目一手文档但同含推广元素；作者价值判断一律标 V/📝，不升级为事实。
- P0 权威核验 **18 项：14✅ / 4⚠️ / 0❌**。四项 ⚠️ 均为时点/口径漂移：
  ① 九个 → 十二个入口；② macOS-only → macOS + Windows + iOS 开发中；③「已签名公证」官方未逐字确认完成态；④「不调微信接口」非官方逐字措辞。
- **勘误四张清单**见 [references/verification.md](references/verification.md)：日期/版本表、成效数字溯源表（源文无成效数字，为空风险表）、口径对照表（C-1~C-7）、引文逐字/命令逐字核对表（V-1~V-8）。
- **无 ❌ 的关键原因**：README 渲染页未返回 commit SHA 与最后更新日期（F-105），无法回溯 2026-09-24 时点的入口数（F-102），故「九个」判时点差异而非失实；教程以官方当前十二个为主表并保留源文时点标注。

### I（骨架与归属）

- **操作可复现性两问**：① 官方 README 给出三步上手 / 构建 / 开发验证流程 → 是；② 带版本（macOS 14+、微信 4.1.13+、Xcode 16 / Swift 6）、带顺序、带产物路径 `macos/dist/微信流.app` → 是。
  → 技术教程/选型骨架，设 `examples/`。
- **重要边界**：源文本身无任何可照做步骤（F-039），examples 三篇全部来自官方 README 文档化流程，
  **非源文作者实测、非本知识包 macOS 实机验证**；三篇顶部均带该声明，UI 细节因截图不可补全一律不写。
- 三层知识拆分：发布事实（00）→ 链路机制（01）→ 入口矩阵（02）→ 沉淀机制（03）→ 批次收集（04）→ 边界与可迁移模式（05）。
- 归属决策：主线实体优先 + 查同组先例 + 单篇博文禁止新建分组；排除 `practice/`（方法论）、`frameworks/`（框架源码）、`comm/`（通信协议）。

### E（bundle 生成）

- **信源先行**：`references/article-source.md` → `references/verification.md` → `concepts/` → `examples/` → 各级 `index.md` 最后写。
- 双份 F 编号：spec `facts.md` 为人工正本，bundle `article-source.md` 正文由正本**机械同步**生成（不二次录入），避免「460 vs 458」式漂移。
- 所有数字/版本/命令/入口名/署名携带 F 编号；`facts.md` 之外未新增事实；伪代码与流程图标注为编者整理。
- **frontmatter 规范取舍**：按 `.agents/rules/frontmatter.md` §12（`okf_version` 仅允许出现在 bundle 根 `index.md`），
  本束 12 篇子文档**不带** `okf_version`，只在根 index 声明。同组旧束（如 `wigolo`）在每篇子文档都带该字段，属历史遗留；本次按现行规范执行，登记备查。
- 相对链接按 bundle 深度逐一核对：`concepts/` 与 `examples/` 用 `../` 回到束根，`references/` 内互链用同目录相对路径；
  曾发现并移除一处跨仓库 `../../../../.trae/...` 越界链接（改为纯文字说明）。

### V（对抗审查与机械门禁）

**四视角审查**：

| 视角 | 发现与处置 |
|------|-----------|
| 魔鬼代言人 | 「十二个入口」会不会是另一个时点的口径？→ 用 `make-app.sh` 组装十二个 Share Extension（F-096）互证；并登记 F-102/F-105 说明无法回溯源文时点，不判 ❌ |
| 新人视角 | 读者可能把「一键转发 / AI 处理 / 本地沉淀」误读成串联流水线 → [concepts/03](concepts/03-scenes-skills-and-deposition.md) 明确指出 Agent 路径与笔记路径是**并列分支**（官方流程图 F-081） |
| 老板视角 | 源文是推介文，可信度够不够？→ index 顶部四条口径差异块 + 信源距离表 + `stale_after` 缩短至 2026-12-31；examples 顶部统一「未实机验证」声明 |
| 未来视角 | 入口数 6 周内 9→12，会继续变 → [concepts/05 §6](concepts/05-boundaries-selection-and-patterns.md) 六项到期复核清单，第一项即入口数量 |

**状态决策记录**（重要取舍）：按 `blog-article-to-okf-wiki` §6 步骤 6.4，`flagged` 只在「P0 出现 ❌ **且**失败项为核心声明」时启用。
本次 0❌，故设 **`status: stable`**；四项 ⚠️ 改由 index 顶部差异块 + 短 `stale_after` 兜住。
同类先例 `wigolo`（18 项 14✅/4⚠️/0❌）亦为 stable。**未滥用 flagged，也未把时点差异藏进 stable**。

**机械门禁结果**（2026-11-06 落盘并接线后复跑；工作树含并行会话 WIP）：

| 门禁脚本 | 结果 | 说明 |
|---------|------|------|
| `scripts/check-bundles-index.py` | ✅ **通过** | `9 域 / 64 组 / 717 束`，frontmatter、计数行、域节标题、分组表、toctree 五面一致 |
| `scripts/check-toctrees.py` | ✅ **本束 0 处残留** | 接线前全库 18 处中，本束贡献 17 处（16 个内容文件不可达 + `products/index.md` 缺 `wechatbridge/index`）**已全部消除**。剩余红灯随并行 WIP 写入进度波动（连续复跑观测 4 → 14 条），逐条核对归属：`wechatbridge-ios-relay/` 占比 100%，**非该 WIP 的条目 0**，按隔离原则未触碰 |
| `scripts/check-asset-baseline.py` | ⚠️ 3 项 → **1 项** | `README.md` / `doc/index.md` 中 716 与总索引 717 矛盾的两项**已修复**；剩余「行尾归一失效」为工作区未提交内容漂移（残差随并行 WIP 增长：+165176 B → +227056 B），脚本自身要求「提交或 stash 后复跑」，属环境态、非本束文档缺陷 |
| `scripts/check-utf8.py` | ✅ **通过** | 全库万余文件均为有效 UTF-8（复跑计数 12949 → 12958，随并行 WIP 增长） |
| `scripts/check-section-anchors.py` | ⚠️ 全库历史基线红 | 存量约 6521+ 处锚点问题（guoxue 了凡 / 阴阳家等）；`grep -i wechatbridge` **零命中**，本束贡献 0 处 |

> **读数纪律**：以上含工作树动态观测值，均以复跑时磁盘原文为准，不沿用会话摘要快照；
> 全库级红灯一律先做**归属核对**（`grep` 过滤本束路径）再记结论，避免把外部 WIP 误记为本束缺陷。

**`invoke gates.*` 不可用**：`python -c "import invoke"` → `ModuleNotFoundError: No module named 'invoke'`。
按 `blog-article-to-okf-wiki` §7 规定，**不声称「gates 通过」**，改以上述脚本直跑 + 下列手动等效验证替代。

**手动等效验证**（全部通过）：

| 项 | 结果 |
|----|------|
| 文件清单 | 16 个 md（6 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志） |
| F 编号双份登记 | spec `facts.md` 107 条 / bundle `article-source.md` 107 条，**集合相等、F-001~F-107 连续无跳号** |
| 全文 F 引用越界 | 16 篇共引用 107 个编号，**越界 0**（不存在引用未登记事实的情况） |
| OKF v0.2 frontmatter | `okf_version` 仅出现在根 `index.md`；16 篇均带唯一必填字段 `type` |
| 相对链接 | 全束 `](...)` 逐条解析，**断裂 0**（含此前移除的跨仓库越界链接） |
| 章节体量 | 最长 `references/article-source.md` 196 行，无超 600 行文档，符合概念型 ≤300 行分层 |

**外部未提交变更登记**（不计入本束结论）：

1. `wechatbridge-ios-relay/`：另一会话的 bundle（主仓库 spec `wechatbridge-ios-relay-blog-okf-wiki/`）。本次会话期间由空三层骨架逐步填充；**截至提交时点已由该会话补齐 16 篇文档（含 `index.md`）并接入父级 `products/index.md`**。早期 toctree 红灯的动态波动即来自这一写入过程；本次未触碰、未替它接线，也**未将它的文件纳入本次提交**。
2. `workbuddy-wechat-chat-forward-skills/`、`wechat-intelligence-hub/log.md` 等并行 WIP 造成 `check-asset-baseline.py` 的字节残差；待各会话提交后基线门禁可自行转绿。

### C（提交与并行会话隔离）

- 本次**已提交、未 push**（用户明确要求「提交」）。子模块 `projects/awesome-okf-xs` 为 gitlink 追踪；
  提交顺序按 Skill §C 执行：① 子模块内提交 bundle + 各级 index → ② 主仓库提交 spec → ③ 主仓库更新 gitlink；
  `git-commit-utf8.py` 显式列全文件、不传目录参数，以**路径级提交**钉死提交集、隔离并行会话 WIP。
- **落盘前重新回读磁盘真值**：会话早期读到总索引 714 束，基线门禁时为 715 束（并行 WIP 已提交 `12efe455`），
  故按当前磁盘值做 **+1**，不沿用会话摘要快照。
- **并行会话 WIP 隔离**：工作树存在另一会话的 `workbuddy-wechat-chat-forward-skills/`
  （源文为 `mp.weixin.qq.com/s/BvTuiZelPTb1ZgLT3NoMHQ`「林月半子的AI笔记」，与本次**不同源**），
  以及 `wechatbridge-ios-relay/`（另一会话写入、提交时点已补齐 `index.md` 的 bundle）。本次**未触碰**两者目录，
  也不替它们修 toctree；由后者造成的全部 gate 报错在上方门禁记录中显式标注为外部未提交变更。
- **索引接线与计数同步**（本次收尾，以落盘前重新回读的磁盘真值做**增量**，未整体重写、未覆盖并行 WIP）：
  `doc/bundles/index.md` 回读时已为 717 且五面一致，故**不再改动**（避免与并行会话重复 +1）；
  补 `products/index.md` 束导航行 + toctree `wechatbridge/index`、束数 40→41；
  `jishu/ai/index.md` 289→290 且 products 40→41（六大类求和 105+95+29+41+12+8 = 290 ✓）；
  `jishu/index.md` 289→290；`README.md` 716→717 / jishu 525→526 / ai 289→290；
  `doc/index.md` 716→717。树真值经 `scan_tree` 机械确认为 `jishu.ai = 290 / 全库 717`。

> **上段数字是「落盘收尾时点」的操作史实，不是提交时点的最终值。** 提交前按「磁盘原文优先」再次回读：
> 并行会话已把六个索引统一推进到 `718 / jishu 527 / ai 291 / products 42`（新增 `wechatbridge-ios-relay/` 一束），
> 并补上了本束与它的导航行。本次提交**直接采用提交时刻的磁盘原文**（718 口径），未回退、未重复 +1；
> 本知识包相对总索引仍只贡献 **1 束**。规模数字一律以 `doc/bundles/index.md` frontmatter 为单一真相源。

**提交时点门禁复核**（如实登记，不声称「gates 全绿」）：`check-bundles-index.py` 因并行会话在
`sheke/industry/` 的新增内容报「节标题 / 分组表 92 vs 目录树 93」计数漂移 2 项；
`check-asset-baseline.py` 报「行尾归一失效」（工作区未提交漂移，脚本自身要求提交或 stash 后复跑）。
两者经归属核对**本束贡献 0 项**，属并行 WIP 的环境态，按隔离原则不代修。
`check-toctrees.py` 中本束 16 篇内容文档均可达，`products/index.md` 已含 `wechatbridge/index`。

**本次提交集**（路径级点名，不含任何并行会话的 bundle 目录与 spec 目录）：

- 子模块：`wechatbridge/` 16 篇 md + `README.md`、`doc/index.md`、`doc/bundles/index.md`、
  `doc/bundles/jishu/index.md`、`doc/bundles/jishu/ai/index.md`、`doc/bundles/jishu/ai/products/index.md`；
- 主仓库：`.trae/specs/okf-wiki-ecosystem/wechatbridge-okf-wiki/{spec.md, facts.md}`；
- 主仓库 gitlink：`projects/awesome-okf-xs`。

> **交接态说明**：六个共享索引提交时处于 718 口径，其中已被并行会话写入
> `wechatbridge-ios-relay/index` 的导航与 toctree 条目；该 bundle 的文件由**其所属会话随后提交**，
> 在此之前 toctree 会短暂报 1 处目标缺失。这是共享索引耦合下的预期交接态，不是本束文档缺陷。
