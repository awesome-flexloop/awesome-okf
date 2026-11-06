# 变更日志

## 2026-11-06　创建：单篇微信博文 → OKF v0.2 知识包

- **触发**：用户要求用 `/七概念` 方法论对 `https://mp.weixin.qq.com/s/BvTuiZelPTb1ZgLT3NoMHQ` 做「全面学习」，生成 OKF wiki 教程并落到 `doc/bundles/` 恰当位置。session=`sc-20261106-wechat-workbuddy-forward-skills`。
- **链路**：七概念「知识沉淀/方法论」场景 → `R → I → E → V → C`；具体工作流由 `blog-article-to-okf-wiki` Skill 七阶段驱动（预检 / R / I / E / V / C）。
- **S0 预检**：URL 无 `code`/`token`/邀请码、无内部域名 → 公开内容；spec 落主仓库 `.trae/specs/okf-wiki-ecosystem/workbuddy-wechat-forward-skills-blog-okf-wiki/`，产出落子模块 `doc/bundles/`。
- **信源获取**：本次 `WebFetch` 对 `mp.weixin.qq.com` 全文抓取成功（未触发反爬，与 Skill Gotchas 所述 13/13 拦截的历史经验不同，属本次实际结果）；正文文字完整，**图片内文字未随页面返回**。
- **归属判定**：主线实体为「微信转发到 WorkBuddy 的产品入口 + 两个工具型 skill」→ 落 `jishu/ai/products/`（该组已有 39 个同类先例）；候选位置对照表（含 `ecosystems/tencent`、`sheke/industry`、`practice`、新建分组的排除理由）见 spec `spec.md` §3。单篇博文不新建分组。
- **骨架判定**：操作可复现性两问 = 是 / **否**（zip 仅评论区置顶、无版本/源码/输入输出/运行日志、「三条硬规矩」等为图片未转录）→ **不设 `examples/`**，10 文件骨架。
- **R 事实与核验**：F-001~F-120 共 120 条，双份登记于 spec `facts.md` 与本束 `references/article-source.md`；20 项 P0/P1 权威核验，勘误四张清单收敛为 E-1~E-6。
- **核验关键结论**：① 官方入口路径 ✅ 多源第三方佐证但**无官方公告**（F-103~F-106）；② 「不怕封号」❌ 无官方依据、属因果跳跃（F-030/F-111）；③ 「两个都开源」❌ 不可验证（F-037/F-120）；④ 100 条上限 ⚠️ 存在 iOS 100 / 安卓 99 与企业微信 2MB 体积上限的口径差异（F-101/F-102）；⑤ ETC 与微信收费两条引文 ⚠️ 结论成立但出处/措辞不符（F-117/F-118）；⑥ 淡盐水「光明网转载 @健康上海12320」✅ 全文唯一逐字对应（F-115）；⑦ 2026-01-22 腾讯 DMCA 投诉下架 ✅ 官方回应 + GitHub 项目 README 双重直证（F-107~F-110）。
- **状态裁决**：E-1/E-2 命中标题级核心声明 → `status: flagged`，`stale_after: 2026-12-31`；flagged 三处明示（根 index 提示块 / frontmatter / verification.md 顶部）。
- **I 阶段**：6 条洞察四元组（陈述/证据/反常识/行动）写入 spec `spec.md` §6；四篇 concepts 的知识地图见 §5。
- **E 阶段**：严格信源先行——`references/article-source.md` → `references/verification.md` → `concepts/00~03` → 各级 `index.md`。全部具体声明回指 F 编号；作者观点（V）、自述（S）、结构核验（K）、核验补充（H）显式分层。
- **文件集（10 个新文件）**：根 `index.md`、`log.md`（2）；`concepts/` 4 篇 + `index.md`（5）；`references/` 2 篇 + `index.md`（3）。
- **并行会话协调**：开工时工作树已有他人在途束 `agent-autoloop`、`wechat-intelligence-hub`、`ai-comic-drama-opc-transition` 与多个已改索引文件；基线计数已从 712→714→**715**。本束不修改、不回滚、不提交他方 WIP；计数以写盘时重读现值为准 `+1`。

## 2026-11-06　V 阶段：四视角对抗审查与机械门禁

### 四视角审查意见（10 条，采纳 8 条）

| # | 视角 | 具体攻击点 | 裁决 |
|---|------|-----------|------|
| 1 | 魔鬼代言人 | `verification.md` 文首写「三项 ❌ 中两项命中核心声明」，但 §3 汇总表只有 E-1/E-2 两个 ❌，F-111 被解释成「同源不重复计数」；根 index 又写「2 项核心失败」——三处口径不一致 | ✅ **采纳**：文首统一为「两项核心声明核验失败」，明确 F-111 是 E-1 的证据补充、不另立勘误 |
| 2 | 魔鬼代言人 | 把「两个都开源」判 ❌ 是否过度？无法验证 ≠ 证伪，可能误导读者以为开源是假的 | ✅ **采纳**：verification 文首与 §3、根 index 三处补「**不可验证（unverifiable）而非已证伪**」的性质区分 |
| 3 | 魔鬼代言人 | F-104「多篇第三方实测文」发表于 2026-09-04~06 同一时间窗，可能彼此转载，不能当完全独立样本 | ✅ **采纳**：verification §1 增「独立性限定」段，根 index 已知边界同步；只作路径一致性旁证，不升格为官方确认 |
| 4 | 新人 | 只看根 index 会以为「100 条」是微信全平台硬规则；端差异与 2MB 上限只写在 concepts/00 | ✅ **采纳**：根 index「已知边界」新增一条，写明企业微信 100 条 + 2MB、iOS 100 / 安卓 99 与勘误 E-3 |
| 5 | 新人 | 机械门禁扫描报「concepts/index.md、references/index.md 缺 tags/generated/...、log.md 无 frontmatter」，新人会误判为缺陷 | ✅ **采纳（记录不改文件）**：对照既有模板 `workbuddy-content-system`，子目录 index 仅需 `type/title/description` + toctree，`log.md` 无 frontmatter 是仓库惯例；**全字段要求只适用于 bundle 根 index**（本束根 index 全字段齐备，含 `okf_version`） |
| 6 | 新人 | concepts/03 用代码块列出四组提示词，容易被当成「可复制执行」；警示只在章节开头 | ✅ **采纳**：紧邻代码块前补一段「原文照录、依赖未公开 zip、复制不会得到文中效果」的强提示 |
| 7 | 老板 | 读者最关心「我到底能不能用」，但根 index 缺一句决策级结论，要读完 00 篇 §8 才有 | ✅ **采纳**：根 index 顶部新增「一句话决策摘要」（入口可采信 / 两项断言不可当承诺 / 不提供安装教程） |
| 8 | 老板 | `stale_after: 2026-12-31` 距核验日约 8 周，但 flagged 复核项 6 条，节奏是否过松 | ✅ **部分采纳**：维持年末（仓库惯例），在 verification §5 增第 7 条「约 2026-12-06 前先做一轮轻量复核，年末完整复核」 |
| 9 | 未来维护者 | 主题关联只做了出站链接，五个目标束都没有反向入站链接，未来从对侧找不到本束 | ⚠️ **不采纳修改，改记录**：目标束属其他会话/他人维护范围，且工作树有并行 WIP，本束不修改他束；反向入站链接列为后续独立任务 |
| 10 | 未来维护者 | 若日后取得图片 OCR 或找到公开仓库，F 编号如何扩写没有明文规则；骨架/状态是否重评也只散落在 §5 | ✅ **采纳**：`references/article-source.md` 双份登记声明后补「未来增量规则」——F-121 起顺延、两处同步、不回改，并重评 E-1/E-2/E-6 与两问 |

**采纳落地 8 处**：`references/verification.md`（文首、§1、§3、§5 共 4 处）、`index.md`（文首、已知边界共 2 处）、`concepts/03`（1 处）、`references/article-source.md`（1 处）。意见 5 为「记录性采纳」、意见 9 为「不修改但留痕」，均如实登记。

### 机械门禁（本束级，脚本实测）

| 检查项 | 结果 |
|--------|------|
| UTF-8 严格 roundtrip（本束 10 文件 + spec 2 文件） | ✅ PASS |
| 双份 F 编号集合比对（正则 `^\|\s*F-(\d{3})\s*\|`） | ✅ bundle 120 / spec 120，集合相等、无重复、**F-001~F-120 连续无跳号** |
| 三级 toctree | ✅ 根 3 条 + concepts 4 条 + references 2 条，共 9 条逐一可达 |
| 相对链接全可达 | ✅ 0 断链（含 5 个跨 bundle 主题关联目标，写前已逐一验证存在） |
| frontmatter | ✅ 根 index 全字段（含 `okf_version`）齐备；子 index / log 按仓库模板惯例（见意见 5） |
| 敏感信息 / `file:///` | ✅ 0 命中 |
| 勘误落实 | ✅ 正文呈现正确口径：100 条端差异 + 2MB、ETC/微信收费引文出处不符、淡盐水逐字对应、E-1/E-2 三处 flagged 明示 |
| Mermaid | ✅ 仅 00 篇 1 图，节点单行、边标签加引号、无 `<br/>`、无 emoji |

> 全仓 `check-toctrees.py` / `check-bundles-index.py` 在 C 阶段索引联动后复跑，结果与「本束零失败 vs 全仓并行 WIP 失败」的区分见下节。

## 2026-11-06　C 阶段：索引计数联动、全仓门禁与原子提交

### 索引计数联动（写盘前重读现值，不凭记忆）

C 阶段开工时 `check-bundles-index.py` 报 3 处漂移（`frontmatter total_bundles=715` vs 树 716；`jishu/` 节标题 524 vs 525；`jishu/` 分组表束数之和 524 vs 525）。用脚本 `scan_tree()` 导出目录树地面真值 = **716 束 / jishu 525 / ai 289 / products 40**（本束 10 文件已落盘并被递归计数看见）。据此同步 6 个索引文件：

| 文件 | 改动 |
|------|------|
| `doc/bundles/index.md` | `total_bundles` 715→716；正文计数行 715→716；mermaid 技术域 524→525；技术域节标题 524→525 束；ai 分组表行 288→289 并同步说明文字 |
| `doc/index.md` | 两处 715→716（本轮前已完成，`git diff` 复核为纯数字替换） |
| `README.md` | badge / 简介 / 规模说明 / 完整清单 / 合计行 715→716（本轮前已完成）；技术域表行 524→525；**额外修正**精选推荐「AI & 大模型生态（171 束）」→（289 束）——历史遗留陈旧计数，不属本次 +1 链路，顺手对齐地面真值 |
| `doc/bundles/jishu/index.md` | ai 分组简介 288→289 束 |
| `doc/bundles/jishu/ai/index.md` | frontmatter `description` 与正文 288→289；products 行 `39 / 39`→`40 / 40` |
| `doc/bundles/jishu/ai/products/index.md` | 「39 个知识包 / 39 个生态目录」→ 40 / 40；导航表新增本束 1 行；toctree 追加 `workbuddy-wechat-chat-forward-skills/index` |

自检：products 导航表 40 行 ≡ toctree 40 条 ≡ 声明 40，toctree 条目 0 断链。

### 全仓门禁（Python 脚本直跑，非 `invoke`）

| 门禁 | 结果 |
|------|------|
| `check-bundles-index.py` | ✅ **通过**：`9 域 / 64 组 / 716 束`，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| `check-toctrees.py` | ⚠️ 全仓 10 处失败，**100% 来自并行会话在途束** `doc/bundles/jishu/ai/products/wechatbridge/`（concepts 6 + examples 1 + references 2 共 9 篇不可达 + 该目录缺 `index.md`）；**本束 0 命中**。上一轮基线失败项 `wechat-intelligence-hub` 已由并行会话补齐 `index.md`，本次不再报错。按仓库惯例不修他方 WIP |
| `check-utf8.py` | ✅ 通过：12940 个文件均为有效 UTF-8 |
| `check-asset-baseline.py` | ⚠️ 1 项 `[行尾归一失效]`：归一后工作区字节与 HEAD 残差 `+198274` 超容差；成因是**本束 12 个新/改文件 + 他会话 WIP 尚未提交**，脚本自身处置建议即「先提交或 stash 工作区变更再复跑」。**规模数字对账（检查 2）零矛盾**，716 三处一致；属提交前工作区快照口径问题，非计数错误 |
| `check-section-anchors.py` | ⚠️ 全仓既有 6520+ 处历史锚点问题（非 `gates.all` 成员）；**本束 0 命中** |

> `invoke gates.*` 未安装（Skill Gotchas：可选依赖 `invocations`），按 §7 手动等效清单以脚本直跑验证，此处如实注明，不宣称「gates.all 通过」。

### 本束级复核（C 阶段重跑）

- 双份 F 编号：bundle 120 / spec 120，集合相等、连续 `F-001~F-120`、无重复 ✅
- 相对链接 0 断链 ✅　三级 toctree：根 3 / `concepts` 4 / `references` 2，共 9 条逐一可达 ✅
- 四级索引接入：`products → ai → jishu → bundles` 计数与导航全部对齐 ✅

### 原子提交

- 顺序：① 子模块 `projects/awesome-okf-xs`（bundle 10 文件 + 6 个索引文件 + 本 `log.md`）→ ② 主仓库提交 spec（`spec.md` / `facts.md`）→ ③ 主仓库更新子模块指针；**用户未要求，不 push**。
- 使用 `git-commit-utf8.py` 携带**显式文件清单**（路径级提交），提交前两仓库暂存区均为空；他会话文件（`wechatbridge/`、`wechat-intelligence-hub/log.md`、其余 3 个 `.trae/specs/` 目录）一律不暂存、不提交。
- 具体提交哈希以两仓库 `git log -1` 为准。
