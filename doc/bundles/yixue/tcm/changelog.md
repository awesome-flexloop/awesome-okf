---
type: Changelog
title: "🌿 tcm 域版本更新日志"
description: "中医经典与理论域变更记录——v1.0.0 首版 5 个知识包（2026-08-30）、v1.1.0 域级指南与日志（2026-08-31）；含方法论摘要、V 阶段修复、质量门记录、遗留项与维护规则"
tags: [tcm, changelog, 版本日志]
generated: { by: reference_agent/trae-glm, at: 2026-08-31T10:00:00+08:00 }
status: stable
sources:
  - id: bundle-logs
    resource: /doc/bundles/tcm/classics/
    title: "5 个知识包各自的 log.md（束级变更明细）"
---

# 🌿 tcm 域版本更新日志

本文件记录「中医经典与理论」域（`bundles/tcm/`）的域级变更。**束级细节**（每束的文件清单、异文登记、审查记录）见各知识包内的 `log.md`；本文件只做域级汇总。

版本约定：`v主版本.次版本.修订号`——新束入域/结构性调整升次版本，内容订正与文档增补升修订号；首版为 v1.0.0。

---

## [v1.2.0] — 2026-09-02

### 新增

- **Mermaid 结构图 17 张（M1–M17）**，纯增量嵌入 5 束既有内容文档：
  - [tcm-overview](classics/tcm-overview/index.md) 4 张：[concepts/00](classics/tcm-overview/concepts/00-genealogy-layering.md) 域级经典谱层 1 张、[concepts/01](classics/tcm-overview/concepts/01-four-classics-guide.md) 四大经典导读 2 张、[examples/four-classics-reading-plan](classics/tcm-overview/examples/four-classics-reading-plan.md) 四年共研路线 1 张；
  - [nanjing](classics/nanjing/index.md) 3 张：[concepts/01](classics/nanjing/concepts/01-structure-81.md) 81 难六部结构、[concepts/02](classics/nanjing/concepts/02-relation-to-neijing.md) 与内经关系、[concepts/04](classics/nanjing/concepts/04-commentators.md) 注家谱；
  - [shanghan-zabinglun](classics/shanghan-zabinglun/index.md) 4 张：[concepts/01](classics/shanghan-zabinglun/concepts/01-textual-history.md) 文本流传史、[concepts/02](classics/shanghan-zabinglun/concepts/02-version-systems.md) 版本四系统、[concepts/03](classics/shanghan-zabinglun/concepts/03-six-channels-framework.md) 六经框架、[concepts/04](classics/shanghan-zabinglun/concepts/04-jingui-structure.md) 金匮结构；
  - [shennong-bencaojing](classics/shennong-bencaojing/index.md) 3 张：[concepts/01](classics/shennong-bencaojing/concepts/01-reconstruction-systems.md) 辑复层累链、[concepts/02](classics/shennong-bencaojing/concepts/02-three-grades.md) 三品理论数 365 与实计 363 分层、[examples/three-grades-comparison](classics/shennong-bencaojing/examples/three-grades-comparison.md) 水银雄黄两读并列；
  - [waijing-weiyan](classics/waijing-weiyan/index.md) 3 张：[concepts/01](classics/waijing-weiyan/concepts/01-discovery-and-circulation.md) 流传时序 timeline、[concepts/04](classics/waijing-weiyan/concepts/04-structure-guide.md) 九卷主题地图、[concepts/06](classics/waijing-weiyan/concepts/06-mingmen-fire-water.md) 命门说承应谱系。
- **水墨意象配图 8 张（I1–I8）**，存 `doc/_static/bundles/yixue/tcm/` 下对应 images/ 目录：域封面 1 张（[tcm/index.md](index.md) 首屏）、5 束封面各 1 张（各束 index.md 首屏）、tcm-overview 文献学章节意象图 1 张（[concepts/02](classics/tcm-overview/concepts/02-philology-basics.md)）、waijing-weiyan 颠倒顺逆章节意象图 1 张（[concepts/05](classics/waijing-weiyan/concepts/05-diandao-shunni.md)）。

### 说明

- 本次为**纯视觉增量，知识内容零改动**：未增删改正文、frontmatter、表格、链接与 references，各束 references/ 目录零资产变更。
- 质量门：V 阶段独立对抗审查 A/B/C 全通过——17 张 Mermaid 图六规则机检合规、图中事实逐字核验通过、Sphinx 构建 tcm 域零错误零告警、references 零资产、单页配图 ≤2 配额达标。
- 束级明细（含图片文件名与落位）见 5 束 log.md 的 2026-09-02 条目。

---

## [v1.1.0] — 2026-08-31

### 新增

- **域级使用指南** [guide.md](guide.md)：知识包地图、**5 条按读者身份分流的阅读路径**（零基础爱好者 / 临床从业者与院校学生 / 文献学版本学研究者 / AI 智能体与知识库构建者 / 专题兴趣读者，每条含"你是谁·预期收获·建议投入·阅读步骤"四段式）、束内三层结构读法、6 条文献学体例约定、信源体系、跨域互参、7 条 FAQ、AI 智能体使用提示。
- **本域级更新日志** changelog.md：汇总 5 束首版记录、V 阶段修复、质量门证据、遗留项与后续维护规则。

### 变更

- [tcm/index.md](index.md)：域内导航新增"域级文档"区块（指南/日志入口），隐藏 toctree 收录 `guide` 与 `changelog`，保证全域文档可达。
- [classics/index.md](classics/index.md)：简版"推荐阅读路径"同步改为按读者身份的 5 条摘要，与指南第 3 节口径一致。

### 说明

- 本次为文档增补，不涉及任何精读原文、事实登记与束内容的变更；5 束内容与 v1.0.0 完全一致。

---

## [v1.0.0] — 2026-08-30

### 新增——域与分组

- 新建 **tcm 域**（中医经典与理论）与 **classics 分组**（中医经典）：[tcm/index.md](index.md)、[classics/index.md](classics/index.md)。
- 更新 [bundles 总索引](../index.md)：total_bundles 296→300、新增 tcm 域分组表行与 mermaid 生态图节点（tcm ↔ think 医道互参）、toctree 收录 `tcm/index`。

### 新增——5 个知识包（60 篇内容文档：概念 34 · 示例 13 · 信源参考 13）

| 知识包 | 概念 | 示例 | 信源 | 核心内容 | 束日志 |
|---|---|---|---|---|---|
| [tcm-overview](classics/tcm-overview/index.md) 中医典籍总览 | 6 | 2 | 3 | 典籍谱系三层分层、四大经典导读（6 种组合并列）、版本学异文五分法、托名五问法、书目分级、3 个阅读模式完整落入 | [log](classics/tcm-overview/log.md) |
| [nanjing](classics/nanjing/index.md) 难经 | 6 | 2 | 2 | 81 难题名全录（正则验证恰好 81 条）、第一难"独取寸口"逐句精读、成书五说并列、20 难精读与 26 处实质异文、注家谱系 | [log](classics/nanjing/log.md) |
| [shanghan-zabinglun](classics/shanghan-zabinglun/index.md) 伤寒杂病论 | 7 | 2 | 3 | 成书流变（王叔和整理→宋代校订）、四版本系统并列（宋本/成注本/桂林古本/康平本）、六经辨证框架、398 条索引+金匮 25 篇存目、71 条双源核对条文（太阳篇 23 条精读）、8 处异文标注 | [log](classics/shanghan-zabinglun/log.md) |
| [shennong-bencaojing](classics/shennong-bencaojing/index.md) 神农本草经 | 6 | 2 | 2 | 辑复性质显著标注、四辑本系统与六类差异、三品理论、序录 13 句逐句精读、11 味代表药双源照录、药目存目 | [log](classics/shennong-bencaojing/log.md) |
| [waijing-weiyan](classics/waijing-weiyan/index.md) 黄帝外经（外经微言） | 9 | 5 | 3 | 九卷八十一篇双源核对、13 篇精读原文、68 篇一句提要、命门水火/颠倒顺逆/五行脏腑思想、著录-托名-文本三层分离、真伪两派并列 | [log](classics/waijing-weiyan/log.md) |

> 《黄帝内经》（素问/灵枢）阅读教程按执行决议**交叉引用** think 域已有束 [think/huangdi-neijing/neijing-reading](../huangdi-neijing/neijing-reading/index.md)，不重复建设；内经文献学事实（NGJ 前缀 43 条）沉淀于 tcm-overview 束。

### 方法论摘要（seven-concepts 场景 4：R→I→E→V→C）

- **R 事实采集**：域级登记 **264 条编号事实**（OV 总览谱系 47 / NGJ 内经 43 / NJ 难经 89 / SH 伤寒 36 / BC 本草 49），每条附信源 URL，纯客观描述（因果词扫描零命中，G1 通过）；外经束另立 **90 条**（WJ-BIB 26 / WJ-TEX 31 / WJ-RES 23 / WJ-SRC 10）。
- **I 洞察提炼**：5 条四元组洞察（陈述/证据/反常识/行动），核心立场包括"托名层/文本层/辑复层三层分离""网络电子文本是带版本立场的转录层""concepts=经/examples=注/references=簿录"。
- **E 模式萃取**：3 个可复用阅读模式——双源逐字核读法（L2-validated）、托名辑复分层法（L2-validated）、谱系分级阅读法（L1-draft），完整落入 tcm-overview/concepts/05（触发场景/核心步骤/反模式/检验标准/迁移示例齐备，G3 通过）。
- **双信源核对**：难经（维基文库校勘记本 × 国学导航六部分类本，古诗文网第三参证）、伤寒（ctext × 维基文库宋本转录，中医宝典对校）、本草（维基文库本 × 孙星衍辑本，中华文库/GitHub 中医古籍库参证）、外经（维基文库 × 古书网清抄本转录，古诗文网对校）。

### V 阶段——对抗审查发现并修复（2026-08-30）

**BLOCKER（1 项，已修复）**

- **本草经药目计数口径更正**：365 药存目初检仅据电子版目录标题誊录（353 条），独立复核发现 10 味药以"嵌入正文无标题"形式存在（石胆、五色石脂、菟丝子、枸杞、茯苓、蠡鱼、翘根、山茱萸、赤小豆、雷丸），补入后实计 **363 条**（上经 146/中经 114/下经 103），与序录 365 之数差 2；同步更正 shennong-bencaojing 束 9 个文件的计数表述。

**外经束修复（独立审查 + V 阶段）**

- 卷次硬伤 2 处：WJ-RES-17「卷七《紅鉛損益篇》」→「卷一第七篇」；reading-path 案例 A「卷四《天人壽夭篇》」→「卷一第四篇」（预防措施：卷次-篇名交叉核对纳入核读清单，凡"卷 X"字样须与 catalog-81 存目表对号）。
- 断链 1 处：束根 `../classics/index.md` 路径多一层 → `../index.md`（修复后 194 链接复扫 0 断链）。
- tcm/index.md（域索引）与 classics/index.md（组索引）前序报告已写但磁盘实测缺失，已按 think 域范式补落盘；bundles 总索引 toctree 补 `tcm/index` 条目。
- 剔除维基页面近人批注 7 处（"凌波按"3 处、无署名现代夹批 4 处）；维基总目篇名讹脱 4 处订正（catalog-81 同步）。
- 采纳优化 5 项：问答人物谱删衍、三模式补检验标准与成熟度标注、洞察标题订正、《黄帝外经解要与直译》书目信息订正（梅自强解要、廖冬晴直译，2016 云南人民版，ISBN 9787222143029，出版社官网与 CIP 核）等。

**抽查结论**

- 原文锚点抽查 13 处双源逐字复核通过（本草序录+11 味药条、难经 81 难/伤寒 398 条/金匮 25 篇存目与权威信源一致）。
- 事实抽查 10/10 条 URL 核验通过（OV-001/028、NGJ-001/020、NJ-014/020、SH-011/019、BC-018/019）；外经束另抽事实 10 条交叉一致。
- 分层审查：托名/成书/辑复/版本表述无混淆，学说并列合规，无"神农曰/黄帝说"式违规表述。

### C 阶段——质量门与提交（2026-08-30）

- **UTF-8 检查**：全树 6245 文件通过（UTF-8 无 BOM、LF 行尾）。
- **toctree 检查**：tcm 域 4 束（当时范围）零错误；全量拦截的 16 处问题全部归并行会话 think/buddhism、think/confucian/four-books 在建中间态文件，非本域引入，未干预。
- **Sphinx 构建验证**：以隔离迷你工程（myst_parser + tcm 全树副本）执行 `sphinx-build -b html -E`，退出码 0；waijing-weiyan 24 页全部生成、0 warning / 0 error。
- **原子提交**（Conventional Commits 中文描述，git-commit-utf8.py bytes 通道，存储字节验证无乱码）：

| 仓库 | Commit | 内容 |
|---|---|---|
| awesome-okf-xs（子模块） | `7264c3d4` | 新增《外经微言》知识包（waijing-weiyan，24 文件） |
| awesome-okf-xs | `f439d9d9` | 新增《难经》知识包（nanjing） |
| awesome-okf-xs | `cd18b05e` | 新增《伤寒杂病论》知识包（shanghan-zabinglun） |
| awesome-okf-xs | `538ca450` | 新增《神农本草经》知识包（shennong-bencaojing） |
| awesome-okf-xs | `3c93af22` | 新增中医典籍总览知识包（tcm-overview） |
| awesome-okf-xs | `713d109f` | 登记 tcm 域导航与总索引（classics 分组 5 束就位，bundles 计数 296→300，内经交叉引用 think 域） |
| SpecWeave（主仓） | `bbbb9547c` | docs(specs)：中医经典 OKF 知识包规格与七概念方法论工作记录 |
| SpecWeave（主仓） | `e4df36dc8` | chore(submodule)：同步 awesome-okf-xs gitlink 至上述 6 提交 |

### 合规基线（全域适用）

- 每束首屏医学免责声明（"古籍文献学习资料，非医疗建议；方药剂量仅为文献记录"），精读文档逐篇复置。
- 现代整理本（1949 年后注本）仅书目登记与结论性引用，不转录受版权保护的题解/译文/注解。
- 束自包含：本地链接均在 bundles/ 树内、相对路径带 .md 后缀，无 file:/// 绝对路径。

---

## 遗留项（待后续处理）

| 束 | 遗留项 | 处置条件 |
|---|---|---|
| nanjing | 徐大椿《难经经释》《难经疏证》《古本难经阐注》作者/版本信息未纳入事实采集 | 补源后升级 commentary-grades 条目 |
| nanjing | 二十七难"霈"上字符维基文库页面显示不全（国学导航本作"留需"） | 存疑待纸本/第三源核定 |
| nanjing | 命门学说后世发挥（注家具体论证）未采集，05-legacy 仅登记起点与框架 | 后续专题补充 |
| shennong-bencaojing | 药目实计 363 条与序录 365 之数差 2，差异原因（菜部归属/传本缺漏）待考 | 辑本系统研究时一并考证 |
| waijing-weiyan | 命门三章共同传抄疑误 8 条、"贼夭/贼天"反向异文、"咎/晷"等存异条 | 标注"存疑，待纸本裁定"，需 1984 年影印本或《陈士铎医学全书》排印本复核 |
| waijing-weiyan | "命门 94 处、10 篇专论"网络统计数据；梅自强 1980 年天津获见抄本说学术出处 | 待纸本复核/出处核 |
| 域级 | 扩展书目占位：《温病条辨》等温病学派、《本草纲目》、《针灸甲乙经》、《脉经》 | 新束立项时从 tcm-overview/concepts/04 书目分级出发 |

---

## 维护规则（后续变更如何记录）

1. **新增知识包**：在本文件追加版本条目（次版本号 +1），登记束名、文档数、事实数、提交哈希；同步更新 [classics/index.md](classics/index.md) 统计表、[tcm/index.md](index.md) 导航与 [bundles 总索引](../index.md) 计数。
2. **束内内容修订**：先记该束 `log.md`（含修订原因与信源），域级日志仅汇总影响全域口径的变更（如计数、体例、导航结构）。
3. **原文/异文订正**：必须经双源复核并在束 log 记录复核过程；义理级异文维持"并列不裁决"体例。
4. **体例变更**（如新增文献学约定）：同步更新 [guide.md](guide.md) 第 5 节与本文件。
5. 每条目保持时间倒序，注明日期、变更类型（新增/变更/修复/废弃）与提交哈希。
