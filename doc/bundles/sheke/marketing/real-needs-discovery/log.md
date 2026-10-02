# 生成日志：real-needs-discovery

> **状态**：已定稿（R→I→E→V 全流程完成，质量门实测通过）。后续修订见变更日志。

## 变更日志

| 日期 | 阶段 | 变更 |
|------|------|------|
| 2026-10-01 | R | 双谱系调研与事实登记：facts.md 落盘（F-001~F-068，八区；S1~S31 信源登记；P0/P1/P2 三级标注） |
| 2026-10-01 | I | 洞察提炼：insights.md 落盘（8 条四元组洞察 + Mermaid 知识地图） |
| 2026-10-01 | E | bundle 骨架：根 index.md、concepts/、examples/、references/ 三个子目录 index.md、log.md 占位 |
| 2026-10-01 | E | 成文落盘：concepts 8 篇、examples 4 篇、references 2 篇；三级索引对账（marketing 2→3 束） |
| 2026-10-01 | 质量门 | 三门实测全绿（UTF-8 / toctree / bundles-index 五面对账 577 束·60 组·9 域） |
| 2026-10-01 | V | 对抗审查：修复根 index.md 概念导航表 F 编号张冠李戴一处（梁宁 F-005→F-007、俞军 F-004→F-005），四视角结论通过 |

## R 阶段记录（事实采集）

- **CMD-LOG 会话前缀**：`sc-20261001-real-needs`
- **调研方式**：基于模型训练知识直接整理，**未执行联网核验**（本会话无 WebSearch 通道、子代理通道不可用）——诚实降级：P0 条目集中列入 references/02 待核清单
- **谱系覆盖**：西方经典（科特勒/莱维特/马斯洛/Blank/Ries/Christensen/Ulwick/Kano/von Hippel/Blank 等）+ 增长营销组（Andreessen/Ellis/Intercom/PG/Savoia/亚马逊）+ 中文谱系（梁宁/俞军/小米/拼多多/中文案例媒体组）+ 考证组（Quote Investigator/BusinessWeek 1998）
- **事实登记**：68 条（F-001~F-068），八区：需求本体 10 / 问 10 / 看 7 / 算 8 / 试 10 / 正面案例 7 / 反面案例 8 / 边界与时代变量 8
- **信源登记**：31 项（S1~S31），唯一真源为 bundle 内 [facts.md](facts.md)（spec 目录 research-notes.md 只记过程、不用 F 编号，从结构上消除双份不一致风险）

## I 阶段记录（洞察提炼）

- **洞察产出**：8 条四元组洞察（陈述/证据/反常识点/行动启示），证据格全部挂 F 编号
- **贯穿主线**：①行为证据是真需求的判别通货；②真伪之辨的关键变量是替换成本；③问看算试四路径互补；④伪需求三温床全在供给方一侧；⑤名言误传暴露认知极化；⑥验证先于构建的可行性是时代变量；⑦需求是移动靶需持续校准；⑧元能力是悬置供给方视角
- **知识地图**：Mermaid flowchart——四道门（替代方案→行为证据→净优势→伪需求三问）+ 四路径分布 + pivot 回环 + 持续校准环

## E 阶段记录（成文）

- **骨架**：concepts/（8 篇）、examples/（4 篇）、references/（2 篇）、facts.md、insights.md、index.md、log.md
- **撰写顺序**：骨架 index → concepts 00-03 → concepts 04-07 → examples 01-04 → references 01-02 → 三级索引对账
- **落盘记录**：concepts/00~07 八篇（真需求定义→伪需求分类→方法地图→访谈→JTBD→验证闭环→排序→案例与边界）；examples/01~04 四篇（访谈脚本工作坊→JTBD 切换访谈→一周验证计划→需求自检清单）；references/01 经典与权威谱系（S1~S31、A-D 信源距离分级）、references/02 待核验清单与名言勘误（P0 集中管理）
- **索引对账**：marketing/index.md（2→3 束）、sheke/index.md、bundles/index.md 三级同步更新；对账中发现并行会话在途束 sheke/minsu/hangzhou-qiuyinyuan-guide 未登记，按 gate 目录树地面真值一并登记（只登记索引行，未改动其文件）

## 质量门记录

三门脚本实测通过（2026-10-01，awesome-okf-xs 仓库根执行）：

| 门禁 | 结果 |
|------|------|
| `scripts/check-utf8.py` | ✅ 10716 个文件均为有效 UTF-8 |
| `scripts/check-toctrees.py` | ✅ 全部 index.md 引用有效，所有内容文档均可达 |
| `scripts/check-bundles-index.py` | ✅ 9 域 / 60 组 / 577 束；frontmatter、计数行、节标题、分组表、toctree 五面一致 |

手动等效补充检查：本 bundle 内 `file:///`、家目录绝对路径、Windows 盘符路径零出现；保留文件名仅 index.md / log.md；性质声明与信源说明置顶根 index；【P0】/【P1】/【P2】标注全包 103 处分布 17 文件，P0 条目与 references/02 清单一一对应。

## V 阶段记录（对抗审查）

四视角结论（2026-10-01）：

1. **事实准确性**：机械核验发现根 index.md 概念导航表 F 编号张冠李戴一处——"梁宁真需求三角（F-005）、俞军用户价值公式（F-004）"与 facts.md 权威登记不符，已修复为俞军 F-005、梁宁 F-007（F-004 为莱维特《营销短视症》）；全包 Grep `F-00x` 交叉核对 26 行，其余 concepts / examples / insights / references 全部正确；F 编号越界（F-069+）零命中。**结论：修订闭环，通过。**
2. **结构完整性**：21 个文件齐备（8 概念 + 4 实操 + 2 信源 + 3 子目录索引 + facts + insights + 根 index + log）；根 index toctree 六引用（concepts/index、examples/index、references/index、facts、insights、log）与磁盘一一对应；check-toctrees 实测通过。**结论：通过。**
3. **误导风险**：未联网核验已在根 index 信源说明、references/02 置顶声明、本日志 R 阶段记录三处显式披露；P0 条目集中管理并附复核 SOP；福特 / 乔布斯名言误传以勘误条目（F-063 / F-064）正向呈现并给出正确引用方式；媒体数字统一保持"约"字口径。**结论：风险已前置对冲，通过。**
4. **版权合规**：全部内容为方法论综述与案例事实性重述，无大段逐字转录；名言仅短句引用且附考证；信源登记表（references/01）给出完整出处。**结论：通过。**

## 已知遗留

1. 全部【P0】条目未联网核验，待核清单见 references/02；后续有 WebSearch 通道时应按清单逐项复核并回填
2. 梁宁《真需求》出版月份、"刚需痛点高频"归属等中文谱系细节待查原书

## 文件清单

| 路径 | 说明 |
|------|------|
| [index.md](index.md) | 根索引（性质声明、知识结构树、分层导航、toctree） |
| [facts.md](facts.md) | 事实登记表（F-001~F-068 八区 + S1~S31 信源） |
| [insights.md](insights.md) | 8 条四元组洞察 + Mermaid 知识地图 |
| [log.md](log.md) | 本日志 |
| [concepts/index.md](concepts/index.md) | 概念层导航 |
| [concepts/00-what-is-real-need.md](concepts/00-what-is-real-need.md) | 什么是真需求 |
| [concepts/01-fake-need-taxonomy.md](concepts/01-fake-need-taxonomy.md) | 伪需求分类学 |
| [concepts/02-discovery-method-map.md](concepts/02-discovery-method-map.md) | 发现方法地图 |
| [concepts/03-interview-playbook.md](concepts/03-interview-playbook.md) | 访谈 Playbook |
| [concepts/04-jtbd-framework.md](concepts/04-jtbd-framework.md) | JTBD 框架 |
| [concepts/05-validation-loop.md](concepts/05-validation-loop.md) | 验证闭环 |
| [concepts/06-need-prioritization.md](concepts/06-need-prioritization.md) | 需求排序 |
| [concepts/07-cases-and-boundaries.md](concepts/07-cases-and-boundaries.md) | 案例与边界 |
| [examples/index.md](examples/index.md) | 实操层导航 |
| [examples/01-interview-script-workshop.md](examples/01-interview-script-workshop.md) | 访谈脚本工作坊 |
| [examples/02-jtbd-switch-interview.md](examples/02-jtbd-switch-interview.md) | JTBD 切换访谈 |
| [examples/03-one-week-validation-plan.md](examples/03-one-week-validation-plan.md) | 一周验证计划 |
| [examples/04-need-self-check-list.md](examples/04-need-self-check-list.md) | 需求自检清单 |
| [references/index.md](references/index.md) | 信源层导航 |
| [references/01-classics-and-authorities.md](references/01-classics-and-authorities.md) | 经典与权威谱系 |
| [references/02-source-verification.md](references/02-source-verification.md) | 待核验清单与名言勘误 |

合计 21 个文件。
