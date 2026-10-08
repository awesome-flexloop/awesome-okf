---
type: Review
title: V 阶段四视角对抗审查报告——杭州求姻缘地点知识包
description: 对本束全部 17 篇（束根、facts、insights、concepts 9 篇、examples 4 篇、references 4 篇）执行的魔鬼代言人/新人/老板（内容编辑）/未来四视角对抗审查结论——意见清单 10 条（4 条 P1、5 条 P2、1 条 P3），8 条采纳并已落盘修正，2 条不采纳转为开放问题；修正严守 facts.md 唯一事实源，未引入清单之外的新事实。
tags: [review, 杭州, 求姻缘, 对抗审查, V阶段, OKF]
created: 2026-10-01
generated: { by: "agent:trae-okf-review", at: "2026-10-01T20:00:00+08:00" }
verified: { by: "", at: "" }
status: stable
stale_after: 2027-10-01
sources:
  - id: facts-inventory
    resource: facts.md
    title: 本 bundle 事实清单（F-001 至 F-078，唯一事实源）
---

# V 阶段四视角对抗审查报告

## 一、审查概况

- **审查对象**：`hangzhou-qiuyinyuan-guide` 全束 17 篇（束根 index、facts.md、insights.md、concepts/ index+00~07、examples/ index+01~03、references/ index+01~03），另核对分组页 `sheke/minsu/index.md` 注册情况与 2 张配图在位情况。
- **审查方法**：四视角对抗审查——魔鬼代言人（事实准确性与红线）、新人视角（零基础可走通性）、老板视角/内容编辑（信源层级与元数据规范）、未来视角（低成本可维护性）。全部正文口径逐点对照 [facts.md](facts.md)（唯一事实源，含 P0 双源核验表 22 行）。
- **审查日期**：2026-10-01；**修正纪律**：正文与 facts.md 冲突时改正文不改 facts.md；facts.md 本身疑似错误只标注不臆改，列为开放问题。

## 二、审查意见清单（10 条）

| 编号 | 视角 | 严重度 | 问题描述 | 定位 |
|---|---|---|---|---|
| R-01 | 魔鬼代言人 | P1 | **免票范围越界表述**：F-027 仅登记"灵隐飞来峰景区"免票，facts.md 未登记永福寺/韬光寺日常入场口径（F-071 仅为 2026 春节期间灵隐、永福、韬光三寺免费的年度特例）；但 examples/01 费用小计首行断言"灵隐飞来峰景区（含灵隐寺、永福寺、韬光寺区域）0 元"、时间轴永福寺行标"0 元（景区范围内）"、references/01 预约渠道提示同款区域列举，均超出 facts.md 登记范围 | examples/01-faxi-lingyin-one-day-route.md 时间轴 10:30—11:30 行与费用小计首行；references/01-temple-official-sources.md「预约渠道提示」段 |
| R-02 | 魔鬼代言人 | P1 | **年票覆盖误述**：concepts/03 错峰思路称"永福寺、灵顺寺同属寺院年票覆盖（F-020）"，但 F-020"九寺一观"名单（灵隐寺、净慈寺、法喜寺、法净寺、法镜寺、灵顺寺、香积寺、余杭径山万寿禅寺、葛岭抱朴道院）中无永福寺——正文与 facts.md 直接冲突 | concepts/03-lingyin-feilaifeng-scenic-guide.md 第五节第 3 条 |
| R-03 | 新人视角 | P1 | **术语无解释**："香花券"（杭州寺院门票的本地叫法）全束高频出现（concepts/02、concepts/04 门票表格、examples/01 费用小计等 11 处），但全束无任何解释或指向，零佛教常识的首次赴杭者不知所云 | concepts/02-faxi-temple-and-tianzhu-line.md 第三节门票表格（全束首现处） |
| R-04 | 老板视角 | P1 | **frontmatter 缺失**：examples/index.md 完全没有 YAML frontmatter（直接以 `# 实践示例` 开头），违反 frontmatter 规范（type 非空），且与 concepts/index.md、references/index.md 两个同级目录页不一致 | examples/index.md 文件头 |
| R-05 | 老板视角 | P2 | **sources.resource 路径不一致**：insights.md、concepts/ 9 篇、examples/ 3 篇共 13 个文件用根相对 `/facts.md`（按 doc 目录解析将指向不存在的 doc/facts.md），references/ 各篇用 `../facts.md`，同束两种写法 | 各文件 frontmatter sources 段 |
| R-06 | 魔鬼代言人 | P2 | **现场购票外推**：examples/03 行前检查表把黄龙洞、万松书院与四座寺院并列后统称"均现场购票"；facts.md 仅登记法喜寺（F-009）、净慈寺（F-042）现场购票口径，香积寺/灵顺寺/黄龙洞/万松书院购票方式未登记 | examples/03-preparation-checklist-and-pitfalls.md 第一节第 1 张表 |
| R-07 | 新人视角 | P2 | **转场指引不足**：examples/01 转场行仅写"换乘公交 103/121/1314 路往天竺方向（F-075）"，F-075 是各目的地线路口径的汇总登记，未登记灵隐→天竺的上车点与直达衔接关系；首次赴杭者照字面执行可能找不到换乘车站 | examples/01-faxi-lingyin-one-day-route.md 时间轴 12:30—13:00 行 |
| R-08 | 老板视角 | P2 | **verified 字段不齐**：concepts/ 各篇均有空值 `verified: { by: "", at: "" }`，examples/ 01-03、references/ 01-03 与 references/index.md 缺该字段；references/index.md 同时缺 sources 段 | 各文件 frontmatter |
| R-09 | 未来视角 | P2 | **stale_after 一刀切**：全束统一 `stale_after: 2027-10-01`，与 insights 洞察六"除夕内容保鲜期不足 12 个月、需年度触发器"自相矛盾——F-069/F-070 除夕口径约在 2027-01/02 新通告发布时即事实性过期，早于 stale_after | 全束 frontmatter；insights.md 洞察六；facts.md F-069、F-070 |
| R-10 | 未来视角 | P3 | **票价数字多点重复**：同一票价数字同时存在于 facts.md、concepts 各篇表格、examples 费用小计与 examples/03 检查表，门票政策调整时需多点同步；现靠"口径回指 F 编号 + 以官方公告为准"缓解，但 F 编号引用无机器可校验的同步机制 | 全束结构性问题 |

**抽查确认无误项**（魔鬼代言人视角逐点核对后确认）：① 门票/开放时间正文口径与 facts.md P0 表一致——法喜寺 10 元/06:30—18:00（F-009）、灵隐 7:30—17:30/17:00 停止入园（F-028）、净慈 10 元（F-038）、香积 20 元（F-044）、灵顺 8 元（F-037）、黄龙洞 15 元（F-051）、万松书院 10 元（F-060）、除夕 2025 票价制 vs 2026 领票制双年口径（F-069、F-070）；② "灵验"表述全部归因信源作"网络热门说法的客观记录"，未越界为真实性断言；③ 相亲角内容（concepts/06、examples/02）无可识别个人信息，不拍摄/不传播红线完整；④ 无营销号混入一级信源（河南日报客户端头条号转载、凤凰网等均正确列入二级"仅线索"）；⑤ 冲突口径（造像尊数 345 vs 390 余、净慈/香积开放时间、相亲角时间、预约平台停用之辨）均忠实于 facts.md 并列登记、未擅自取舍。

## 三、采纳与落盘记录（8 条采纳，均已修正）

| 编号 | 处置 | 修正落盘明细 |
|---|---|---|
| R-01 | ✅ 采纳 | examples/01：费用小计首行删去"（含灵隐寺、永福寺、韬光寺区域）"，表后新增注"景区内永福寺、韬光寺的日常入场口径 facts.md 未单独登记（F-071 仅登记 2026 春节期间三寺免费的年度特例），以现场与官方通告为准"；时间轴永福寺行费用列改"日常入场口径 facts.md 未登记，以现场为准（见费用小计注）"。references/01：预约渠道提示同款软化，删区域列举并加同款注 |
| R-02 | ✅ 采纳 | concepts/03 第五节第 3 条改"其中灵顺寺在寺院年票'九寺一观'适用范围内，永福寺、韬光寺是否在年票适用范围 facts.md 未登记（F-020）" |
| R-03 | ✅ 采纳 | concepts/02 门票表格后新增术语注："'香花券'是杭州寺院门票的本地叫法（信源原文用词，见 F-009、F-038、F-044），购券即购票入场；本束各篇沿用信源原词。" |
| R-04 | ✅ 采纳 | examples/index.md 按 concepts/index.md 基线补齐完整 frontmatter（type: Example、title、description、tags、created、generated、verified 空值、status、stale_after、sources） |
| R-05 | ✅ 采纳 | 13 个文件 frontmatter `resource: /facts.md` 统一改为相对路径：concepts/ 9 篇与 examples/ 3 篇改为 `../facts.md`；束根 insights.md 改为同目录 `facts.md` |
| R-06 | ✅ 采纳 | examples/03 收费点位行改"法喜寺、净慈寺为现场购票口径（F-009、F-042），其余点位购票方式 facts.md 未登记，一律以现场公告为准"，行首标签同步改"收费点位门票预算已备"（黄龙洞/万松书院非寺院、其门票不称香花券） |
| R-07 | ✅ 采纳 | examples/01 转场行补注"F-075 为各目的地线路口径汇总；灵隐至天竺的上车点与直达衔接 facts.md 未登记，以实时地图查询为准" |
| R-08 | ✅ 采纳 | examples/ 01-03、references/ 01-03、references/index.md 补 `verified: { by: "", at: "" }`；references/index.md 同时补 sources 段（指向 ../facts.md） |
| R-09 | ❌ 不采纳落盘 | stale_after 属全束元数据策略，单独改除夕相关篇目会造成同束尺度不一；应与"年度触发器"维护机制整体设计，转开放问题 OQ-1 |
| R-10 | ❌ 不采纳落盘 | 票价多点重复的机器校验属工具链建设，超出本束修正范围；现行"回指 F 编号 + 以官方公告为准"已是可接受的缓解，转开放问题 OQ-2 |

**修正合规自检**：全部修正仅软化或对齐 facts.md 已登记口径，未引入 facts.md 之外的新事实；frontmatter type 均非空、双引号字符串内无 ASCII 双引号；全部引用为相对路径、无 file:///；文件保持 UTF-8 无 BOM；未改动 facts.md 与束外任何文件。

## 四、遗留开放问题

| 编号 | 严重度 | 问题 | 建议处置 |
|---|---|---|---|
| OQ-1 | P2 | stale_after 全束 2027-10-01 一刀切，除夕年度通告类内容（F-069、F-070）实际保鲜期约至 2027-01/02 新通告发布，与 insights 洞察六的"年度触发器"主张未落到元数据 | 后续为除夕/春节类时效内容单设更短 stale_after 或在束级维护机制中设年度复核触发器，需与 OKF 元数据规范协同 |
| OQ-2 | P3 | 票价等高频数字在 facts.md 与正文多点重复，F 编号回指无机器校验，政策调整时靠人工同步 | 工具链层面考虑"正文数字 vs facts.md"一致性检查脚本；现阶段维持"回指 F 编号 + 以官方公告为准"纪律 |
| OQ-3 | P3 | F-020 信源原文称"九寺一观"，但所列名单实为 8 寺 1 观（灵隐、净慈、法喜、法净、法镜、灵顺、香积、径山 + 抱朴道院）——名称与数目存在字面差异。本束忠实引用信源原词不改 facts.md，仅标注 | 建议 facts.md 后续维护时为 F-020 补一条"名单数目与称呼差异"注记（facts.md 疑似问题只标注不臆改，留待下轮事实维护） |

## 五、回归验证

- 2026-10-01 修正后执行 `conda run --no-capture-output -n py314 invoke gates.toctrees`（工作目录 `projects/awesome-okf-xs`），退出码 0，输出原文：`toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。`
- 结果判读：无新增断链错误，本束内部链接干净；门控未报任何 minsu 相关"未被索引引用"类警告/错误——该门控校验的是既有 toctree 条目的引用有效性与可达性，bundles/index.md 与 sheke/index.md 尚未注册本束属后续任务范围，不影响本次通过结论。

返回 [束根导航](index.md)｜[事实清单](facts.md)｜[架构洞察](insights.md)。
