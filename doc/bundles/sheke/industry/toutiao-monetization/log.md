# 更新日志

## 2026-10-23

**Generation**：由 `seven-concepts-cmd` 七概念方法论（场景 4 知识沉淀，链路 R→I→E→V→C）生成头条号变现体系知识包。

- **取证入口与降级**：用户给出入口页 `https://mp.toutiao.com/gf/exclusive?enter_from=menu`（今日头条「头条首发激励计划」）。浏览器实测游客态跳转 `auth/page/login`，正文不可复现（F-104）；其「详细规则」指向官方百科条目 `baike.toutiao.com/detail/242/566/0`。**规则原文取自百科条目全文 + 官方公告 + 官方规则页，不采用入口页快照**。此为抓取通道限制，非信源降级（入口页与百科同属头条官方域）。
- **骨架判定**：无 `examples/`。理由：信源本体为平台规则文本与公告，非分步教程；行动清单属设计产物，并入路径层 05 篇。同簇先例：`zhihu-monetization`、`monetization-essence` 均无 examples/。
- **归属决策**：`sheke/industry/`——单一平台的变现机制规则级解析，属行业/商业趋势分析型；与 `zhihu-monetization`（姊妹平台）、`ai-monetization`（总论）、`monetization-direction`（方法论）同簇。
- **四层结构**：事实层（00 总览 + 01/02/03 三篇）→ 机制层（04 洞察）→ 路径层（05/06）→ 勘误层（07）；references 2 篇（article-source + verification）+ index + log，共 15 个文件。
- **事实层规模**：121 条编号事实（F-001~F-121），挂 18 个官方源（百科 5 + 官方公告 10 + 官方规则页 2 + 官方解读文 1 + 官方目录结构 1），另含 8 组知乎社区口径（E 组 F-087~F-098，单源）与 3 条第三方商业站口径（F-101~F-103，单源）。
- **G3 生成顺序**：references/article-source.md → references/verification.md → concepts/00→07 → index.md → log.md。
- **社区口径通道**：按 `zhihu` Skill 的开放平台 CLI（`search zhihu --query ... --count 10` / `search global`）检索社区说法，全部登记为**单源对照**，一律不作为规则依据。
- **核验状态**：P0 核验结论、8 组口径冲突裁定依据、单源清单、3 项官方口径缺口、flagged 判定与 8 条复核建议详见 `references/verification.md`；据此设 `status: flagged`、`stale_after: 2027-06-30`（保守失败管理：核心结构多源确认，但 15 条 UGC / 商业站单源仍在包内，且 2024-06 至 2026-02 的 20 个月内规则至少变更六次）。
- **时效口径**：复核触发条件为「官方页面更新时间变化」，而非仅按日历到期——官方页面自身标注更新时间（创作者计划页 2026-08-27、收益常见问题页 2026-03-02），可直接作版本依据。
- **V 门对抗审查**：四视角（魔鬼代言人 / 新人 / 老板 / 未来）共提出 26 条问题（6 P0 / 9 P1 / 7 P2 / 4 P3）。8 条属事实或引用错误，已全部修正；修正记录见 `references/verification.md` 第 9 节。**首轮修正自身引入过「改对了一半」的错误**（3 倍保底引用张冠李戴、互动系数被写成可观察项、中视频存量处置结论反向、AI 内容认定版本差异被抹平、单价层与权益层混淆），已逐条复核并二次校准。
- **索引更新**：industry 组导航表 + toctree + description 三处 31→32 束；sheke 域方向列表与分组导航表同步；总 bundles index frontmatter `total_bundles`、正文计数行、mermaid 域节标题、分组表束数列、toctree 五面同步。
- **结构范式**：对齐同簇 `zhihu-monetization`（NN-kebab-case.md + 内容导航表 + toctree 含 log + 双 references 体例 + flagged/stale_after 约定）。

**Verification（2026-10-23）**：awesome-okf-xs 子模块无 invoke 任务定义（`tasks.py` 不存在，`invoke gates.all` 通道不可用）→ 按项目既有约定执行**手动等效验证**，逐条如下：

- [x] ① toctree 导航完整性（`scripts/check-toctrees.py`）：bundle 根 toctree 3 条目（concepts/index + references/index + log）、concepts 层 8 条目、references 层 2 条目全部解析到真实 `.md`；束内 15 篇文档经 doc/index.md 出发的 toctree 链全部可达；目录文件清单一致；bundle 根含子目录 → index.md 齐备。
- [x] ② 总索引五面对账（`scripts/check-bundles-index.py`）：frontmatter `total_bundles` / 正文计数行 / 14 个域节标题 / 各域分组表束数列之和 / 末尾 toctree 域集合，五面与目录树地面真值一致。
- [x] ③ UTF-8 严格往返（`scripts/check-utf8.py`）：束内 15 个 `.md` 零异常。
- [x] ④ F 编号连续性：F-001~F-121 无跳号；V 门补采条目以字母后缀插入原组（F-032h、F-005b、F-086i~F-086j），不重排既有编号，正文所有 F 引用均可回查。
- [x] ⑤ 相对链接可达 + 零 `file://` 绝对路径用法：束内全部链接为 `../` / 相对形式且解析可达（终检脚本逐条 `resolve()` 校验，零断链）；文中出现的 `file://` 字样仅为本条检查项的引述，非实际用法。
- [x] ⑥ 敏感信息零残留：键值赋值型敏感模式（token / password / secret / api_key / credential 后接 ≥8 位值）零命中。
- [x] ⑦ 内容敏感度：Public（公开平台规则与官方公告）→ 产出落 `doc/bundles/`，无内部会议内容混入。

**结论**：全绿，无失败项复修。**并发隔离说明**：提交时工作区存在他方会话的未提交增量（`jishu/ai` 侧计数变动与多个未跟踪束目录），且与本束的索引增量落在同一行。本束采用「暂存区 = HEAD + 仅本束增量」方式提交，工作区混合态保留给他方自行提交；计数口径以纯净树实测值为准。
