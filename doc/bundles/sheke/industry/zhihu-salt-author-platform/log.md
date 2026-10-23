# 生成日志：zhihu-salt-author-platform

> **状态**：已定稿（R→I→E→V→C 全流程完成，质量门实测通过）。后续修订见变更日志。

## 变更日志

| 日期 | 阶段 | 变更 |
|------|------|------|
| 2026-10-23 | R | 知乎双入口采集与事实登记：facts.md 落盘（F-001~F-111，13 节；S1~S6 信源登记；5 项口径缺口明示） |
| 2026-10-23 | I | 洞察提炼：insights.md 落盘（6 条四元组洞察 + 洞察间关系表） |
| 2026-10-23 | E | bundle 骨架：根 index.md、concepts/、examples/、references/ 三个子目录 index.md、log.md |
| 2026-10-23 | E | 成文落盘：concepts 9 篇、examples 3 篇、references 1 篇 |
| 2026-10-23 | 质量门 | 三门实测（UTF-8 / toctree / bundles-index 五面对账） |
| 2026-10-23 | V | 四视角对抗审查（4 个独立代理并发）：去重后 40 条意见，P0×9 / P1×21 / P2×7 / P3×3 |
| 2026-10-23 | V | 采纳修正 17 项 + 连带一致性修正 4 项 + 全包 `status`/`stale_after` 统一；未采纳项登记为剩余风险 R1~R7 |
| 2026-10-23 | E | 补齐 references/02-verification.md 与 log.md；三级索引对账（industry 32→33、sheke 78→79、bundles 673→675，计数按目录树地面真值，含并行会话在途束） |
| 2026-10-23 | C | 子模块内原子提交（Conventional Commits，中文主体） |

## R 阶段记录（事实采集）

- **CMD-LOG 会话前缀**：`sc-20261023-zhihu-salt-author-platform`
- **采集对象**：用户指定的两个知乎入口及其子页面——① `zhihu.com/parker/campaign/1886006781253224212`（「盐选作者平台升级使用手册」）；② `zhihu.com/author-platform/home`（「盐言作者平台」）及其可见子页面。
- **采集方式**：知乎对静态抓取（WebFetch）全部失败（JS 渲染 + 反爬），改由**真实浏览器驱动**访问并逐屏转录页面可见正文；`parker` 页首次未渲染，改用 `?zh_hide_nav_bar=true` + 等待 + 脚本提取后取得全文。
- **信源登记**：6 项（S1~S6）——S1 手册（采全）／S2 征稿活动页（采全，经顶部导航点击进入）／S3 作者平台主页（结构层采全）／S4 作者福利页（部分）／S5 创作风向页（部分）／S6 长篇创作马拉松（仅框架）。
- **事实登记**：111 条（F-001~F-111），十三节——总览 5 / 创作流程 15 / 签约与完结 10 / 曝光 6 / 平台导航 10 / 福利页 4 / 创作风向 5 / 马拉松 3 / 活动定位与要求 13 / 奖项与评选 14 / 流量激励 4 / 参与方式与细则 13 / 权利条款 12。
- **采集边界（不补写）**：S4 权益明细、S5 TOP50 明细、S6 各板块正文、平台内登录态页面（作品管理/社区故事管理/创作规则/常见问题/合同管理/收益管理共 6 项）、《盐言故事用户协议》等上位协议文本——全部按缺口登记，本包不作任何补写或推测。
- **G1 自检**：事实条目全部为客观转录，无因果词；推断集中于 insights.md 与 concepts/ 层。

## I 阶段记录（洞察提炼）

- **洞察产出**：6 条四元组洞察（陈述/证据/反常识/行动），证据格全部挂 F 编号。
- **六条洞察**：I-01 双门槛+强制完结（非「写够字数」）／I-02「申请签约」的投稿与签约双语义／I-03 曝光是「被推荐后可见」的二次分配／I-04 AI 校对（工具侧）与禁止 AI 创作（合规侧）分属两个维度／I-05 评审把「数据」显式降级为参考维度／I-06 平台信息架构是会漂移的活文档。
- **贯穿主线**：字数与完结是**资格线**、元素融合是**排名线**、频道曝光是**不可自控线**；叠加「快照非契约」的时效约束。
- **洞察间关系表**：I-01/I-02 属流程层（数值闸门 vs 语义歧义）；I-03/I-05/I-01 构成「资格线 + 排名线 + 曝光线」三层；I-04 与 I-05 的 F-060 共同构成活动合规双清单；I-06 为横切时效维度。

## E 阶段记录（成文）

- **骨架**：concepts/（9 篇 + index）、examples/（3 篇 + index）、references/（2 篇 + index）、facts.md、insights.md、index.md、log.md。
- **撰写顺序**：骨架 index → concepts 00~08 → examples 01~03 → references/01 → 三级索引对账。
- **落盘记录**：
  - **concepts/**：00 总览与阅读地图／01 平台功能地图／02 中长篇创作五步流程／03 签约与完结的闸门与反馈链／04 曝光与作品展示渠道／05 创作风向与选题信号／06 征稿活动规则解剖／07 权利、合规与 AI 红线／08 平台演进与迁移风险。
  - **examples/**：01 投稿前合规自查表（8 组 47 项）／02 中长篇连载排期表（A/B/C 三表 + 闸门状态机）／03 参赛决策树（Q0 资格自检 → Q1 是否参赛 → Q2 载体 → Q3 关联回答 → Q4 常规路径旁路）。
  - **references/**：01 信源清单与采集边界／02 对抗审查报告。
- **落位判断**：`doc/bundles/sheke/industry/`——与既有 `zhihu-monetization`（站内创作激励）、`zhihu-ai-science-workshop`（AI 活动样本）、`big-tech-pontzi-track-selection`（赛道选择）同属知乎平台簇可互链；`sheke/marketing/` 组收录原则明确排除「平台玩法等时效性内容」，故不落 marketing。
- **索引对账**：industry/index.md（32→33 束）、sheke/index.md（78→79 束）、bundles/index.md（673→675 束）三级同步更新；计数一律以 `check-bundles-index.py` 的目录树递归口径为地面真值（含并行会话在途束）。

## 质量门记录

三门脚本实测（2026-10-23，awesome-okf-xs 仓库根执行）：

| 门禁 | 结果 |
|------|------|
| `scripts/check-utf8.py` | ✅ 12334 个文件均为有效 UTF-8 |
| `scripts/check-toctrees.py` | ⚠️ 本束 21 个文件全部可达、无断链；剩余 14 条报错全部属并行会话在途的 `jishu/ai/frameworks/ai-agent/zhihu-open-platform`（该束根与 examples/ 尚未生成 index.md），非本束问题 |
| `scripts/check-bundles-index.py` | ✅ 9 域 / 63 组 / 675 束；frontmatter、计数行、节标题、分组表、toctree 五面一致 |

手动等效补充检查：本 bundle 内 `file:///` 零出现；保留文件名仅 index.md / log.md；`okf_version` 仅出现在 bundle 根 index.md；`sources[].resource` 与 `generated.by` 全文件齐备；全包 F 编号引用种类 111，未定义引用 0。

## V 阶段记录（对抗审查）

四个**独立**代理并发执行，各承担一个视角，各自读取本包全部文件后独立输出问题清单（避免单代理扮演多角色的表演式审查）。去重后 40 条：P0×9 / P1×21 / P2×7 / P3×3。完整清单与逐条处置见 [references/02-verification.md](references/02-verification.md)。

**采纳并已修正的 P0（9 项）**

1. I-01 行动 3「因为中篇才要求『全部公开』，长篇不要求」与 F-029 正面矛盾 → 改为「申签阶段不强制，完结阶段仍要求全部小节已公开」。
2. I-01「申签字数门槛（小节级）」层级错标 → 改为「作品总量级」。
3. examples/01 伪 F 编号（`F-086-1`/`F-086-7`/`F-089 上下文`）与以洞察编号 `I-04` 作依据 → 全部改挂真实 F 编号。
4. examples/01 项数声明「34 项」与实际 47 项不符 → 改为「8 组 47 项（A~G 43 项 + H 4 项）」。
5. concepts/07 无据豁免「平台自带 AI 校对不在禁令射程内」→ 删除，改为「官方未明确该功能豁免于 F-044，从严解释建议参赛期间不使用（含平台校对）」并标注「（推断，无 F 支撑）」；insights.md I-04 同步修正。
6. F-083 指向的《盐言故事用户协议》《知乎协议》《盐选作者管理规范》既未采集也未登记 → references/01 未采集清单与 index.md 已知边界双处登记，concepts/07 顶部加声明。
7. `references/02-verification.md` 与 `log.md` 缺失导致 toctree 悬空 → 本轮补齐。
8. `status: stable` 掩盖单源时效 → 全包 19 文件统一改为 `status: flagged`，`stale_after` 统一为 `"2026-12-31"`（与同簇 zhihu-monetization 等四包惯例一致）。
9. 本束未登记进父级 `sheke/industry/index.md` → 三级索引对账时补登记。

**采纳并已修正的 P1（摘主要）**：活动 30000 字边界与申签「大于 3w」的相冲说明（concepts/06）；长篇路线越界与 F-077 误引（examples/03 Q4 改为常规路径旁路）；F-060 第 3 条误引（改第 1 种情形）；examples/index.md「F 编号互不重叠」失实（改「共享 12~23 条判据、视角不同」）；index.md 与 concepts/index.md 的 F 范围互斥 5 处（以 concepts/index.md 为准）；需登录页面数四处不一致（统一 6 项）；concepts/00 补「第一步：现在做什么」与「术语速查」14 词表；examples/01 与 concepts/03 补「未通过时的处理动作 / 兜底动作」；index.md 互链描述失实（删除「AIGC 标识、竞业」）；index.md 新增「机制层与数据层的可用性分层」。

**未采纳/部分采纳**：详见 references/02 的 R1~R7 剩余风险表（盐气值语义未知、入口漂移实证可能源自渲染噪声、入驻门槛与分成口径全缺、S6 正文全缺、Q1 无法量化、二阶效应未展开、承诺书细则未逐条登记）。

**V 门判定**：四视角全覆盖 ✅｜意见 ≥5 条（实际 40 条）✅｜采纳 ≥2 条（实际 17+4 项）✅｜**通过**。

## 已知遗留

1. **平台单源**：本包全部内容来自知乎自身页面，无第三方独立复核源；转述时须连同「平台单源 + 采集日期 2026-10-23」一并给出。
2. **活动样本已先于整包失效**：采样活动「津派文化」主题征文活动截止 2026-10-25 24:00（F-038），其字数区间、奖项表与评选条款到期后应视作历史样本；`stale_after: 2026-12-31` 早于本包其余内容的主要有效期，故取更保守值。
3. **未采集部分不得补写**：S4 权益明细、S5 TOP50 明细、S6 各板块正文、6 项登录态页面、上位协议文本——任何引用场景中不得由推测补齐。
4. **零收益承诺**：本包不含任何收益金额、分成比例或获奖概率的推断；F-050 为活动方公布标价，F-076 明确发放以主办方通知为准且为税前金额。
5. **复核触发条件**：见 [references/02-verification.md](references/02-verification.md) 第六节。

## 文件清单

| 路径 | 职责 |
|---|---|
| [index.md](index.md) | bundle 根：导航、互链、机制/数据分层、已知边界、toctree |
| [facts.md](facts.md) | 事实层 F-001~F-111（13 节 + 5 项口径缺口） |
| [insights.md](insights.md) | 分析层 I-01~I-06（四元组 + 关系表） |
| [concepts/index.md](concepts/index.md) | 概念目录与三条阅读路径 |
| [concepts/00-overview.md](concepts/00-overview.md) | 总览、起手动作、术语速查、三层结构 |
| [concepts/01-platform-map.md](concepts/01-platform-map.md) | 平台导航与功能地图 |
| [concepts/02-creation-workflow.md](concepts/02-creation-workflow.md) | 中长篇创作五步流程 |
| [concepts/03-signing-finalization.md](concepts/03-signing-finalization.md) | 签约与完结闸门、审核复提循环、兜底动作 |
| [concepts/04-exposure-display.md](concepts/04-exposure-display.md) | 三 App 曝光路径与流量券作用面 |
| [concepts/05-creation-direction.md](concepts/05-creation-direction.md) | 创作风向与选题信号 |
| [concepts/06-campaign-rules.md](concepts/06-campaign-rules.md) | 征稿活动规则解剖（活动样本） |
| [concepts/07-rights-compliance.md](concepts/07-rights-compliance.md) | 权利条款、AI 红线、授权与账号资格 |
| [concepts/08-migration-risk.md](concepts/08-migration-risk.md) | 演进风险分级与季度复核清单 |
| [examples/index.md](examples/index.md) | 示例目录 |
| [examples/01-pre-submission-checklist.md](examples/01-pre-submission-checklist.md) | 投稿前合规自查表（8 组 47 项） |
| [examples/02-longform-schedule.md](examples/02-longform-schedule.md) | 中长篇连载排期表与闸门状态机 |
| [examples/03-campaign-decision.md](examples/03-campaign-decision.md) | 参赛决策树 |
| [references/index.md](references/index.md) | 信源目录 |
| [references/01-source-manifest.md](references/01-source-manifest.md) | 6 信源采集方式、实际内容与未采集边界 |
| [references/02-verification.md](references/02-verification.md) | 四视角对抗审查报告与剩余风险 |
| [log.md](log.md) | 本文件：执行日志与 CMD-LOG 会话记录 |
