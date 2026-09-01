# 更新日志

## 2026-08-30

### 创建
- 初始化 waijing-weiyan bundle：《外经微言》（黄帝外经）阅读教程，落位 tcm/classics/（tcm 域首束）
- 概念文档 9 篇、精读示例 5 篇、信源文档 3 篇，外加 facts.md（90 条）、insights.md（4 条）

### 方法
- seven-concepts-cmd 场景 4（知识沉淀）链路 R→I→E→V→C：R 阶段双信源采集（维基文库为底本，古书网清抄本转录、古诗文网对校），13 篇精读原文逐字核对
- 卷一 9 篇双源实义异文 20 处、命门三章共同传抄疑误 8 条（标注"存疑，待纸本裁定"）、维基总目篇名讹脱 4 处订正
- 剔除维基页面近人批注 7 处（卷一 6 处、命门真火篇末 1 处，其中署名"凌波按"3 处、无署名现代夹批 4 处）
- 68 篇非精读篇章一句提要，基于维基文库卷二至卷九原文前 2–3 轮问答采集

### 结构
- concepts/：00-what-is-huangdi-waijing, 01-discovery-and-circulation, 02-authorship-and-dating, 03-authenticity-debate, 04-structure-guide, 05-diandao-shunni, 06-mingmen-fire-water, 07-wuxing-zangfu, 08-reading-method
- examples/：juan1-yangsheng-a, juan1-yangsheng-b, mingmen-three-chapters, shanyang, reading-path
- references/：sources-yuandian, sources-xiandai, catalog-81
- facts.md：90 条（WJ-BIB 26 / WJ-TEX 31 / WJ-RES 23 / WJ-SRC 10）
- insights.md：4 条四元组洞察 + 知识地图

### 合规
- 首屏医学免责声明；紅鉛損益篇附文献性质批判性说明
- 现代整理本仅书目登记与结论性引用，不转录注文译文
- 真伪两派并列不裁决；傅山说标注"何高民考证、学界有异议"

### V 阶段（对抗审查，2026-08-30）

**自动化扫描（3 项）**
- 因果词扫描：facts.md 全文扫描"因为/导致/所以/使得/因而/因此/从而/以致/造成/之所以"，零命中（G1 通过）
- 编码扫描：tcm 域 26 个 md 文件（束内 24 + 域/组索引 2）及 bundles/index.md 全部 UTF-8 无 BOM、LF 行尾，无 ISSUE
- 断链扫描：tcm 域 + bundles 总索引共 194 个相对链接，首轮发现 1 处断链（束根 `../classics/index.md` 路径多一层），已改为 `../index.md`；修复后复扫 0 断链

**V 阶段发现并修复的缺失（前序会话报告 applied 但磁盘实测缺失）**
- `tcm/index.md`（域索引，type: group）与 `tcm/classics/index.md`（组索引，无 frontmatter）实际未落盘，已按 think 域范式（think/index.md、think/laozi/index.md）补写，各含导航表与隐藏 toctree
- `bundles/index.md` 隐藏 toctree 漏 `tcm/index` 条目（域段表格与 mermaid 图已在），已补于 rust/index 与 think/index 之间

**人工抽查——原文 12 锚点（examples 原文 vs facts/concepts 引用逐字一致）**
- WJ-RES-02「阴阳之原，即颠倒之术」「我守其一，以处其和」、WJ-RES-03「五行顺生不生，逆死不死」「害生于恩」「仁生于义」「心死则身生」（juan1-yangsheng-a 原文板块逐字命中，与 facts 繁体引用为简繁体转录差异，非异文）
- WJ-RES-04「居两肾之间」「命门为十二经之主」、WJ-RES-06「命门为水火之府」「死生之窦」（mingmen-three-chapters 命中）、WJ-RES-07「在人不在时」（shanyang 命中）
- WJ-TEX-11 夭/天系统异文：juan1-yangsheng-a「寿夭」12 处、juan1-yangsheng-b 篇八校记「不生则天/夭」标注规范；WJ-TEX-23「阴为阳之天也」双源一致不改字，校记明示
- 校勘诚实性：小心真主篇原文照录底本讹字「为当日：」3 处（160/172/176 行），底本原作「为当曰：」4 处保留，校记 193 行标注「日」为「曰」形近之讹——原文不径改，符合 WJ-TEX-26
- 近人批注剔除：「凌波」全文仅 2 处，均为校记/凡例中的剔除说明（mingmen-three-chapters.md 凡例与异文校记两处），原文板块无批注残留（WJ-TEX-03 通过）

**人工抽查——事实 10 条（facts ↔ concepts/references 交叉一致）**
- WJ-BIB-05（1980 年发现、天津市卫生职工医学院图书馆）↔ concepts/01；WJ-BIB-08/09（1984-04 中医古籍出版社影印、32 开 340 页、印 5500 册、限国内发行）↔ concepts/01
- WJ-BIB-04（卷首题署"岐伯天师传，山阴陈士铎号远公又号朱华子述"）、WJ-BIB-11（《山阴县志》"邑诸生……年八十余卒"）↔ concepts/02
- WJ-TEX-28（命门三章共同疑误 8 条"存疑，待纸本裁定"）↔ concepts/06；WJ-TEX-30（总目 4 处篇名讹脱）↔ catalog-81：52 六氣分門篇、54 三合篇、55 四時六氣異同篇、69 傷寒同異篇、75 亡陽亡陰篇均已订正
- WJ-RES-13（脏六腑七说）、WJ-RES-19（五行生克六变局）↔ concepts/07；WJ-BIB-22（傅山说，何高民考证、学界有异议）↔ concepts/03；WJ-RES-17（红铅方术批判）↔ juan1-yangsheng-b

**合规审查（4 项）**
- 医学免责：束根 index.md 首屏免责声明在位（2 处）
- 红铅批判：juan1-yangsheng-b 紅鉛損益篇附文献性质说明，明示明代道教方术、现代医学与伦理不取（6 处）
- 三层分离：著录层（汉志外经 37 卷已佚）/托名层（岐伯天师传）/文本层（陈士铎述）在 concepts/00、03 贯彻（7 处）；真伪两派各 5 条依据并列不裁决
- 版权边界：sources-xiandai.md 声明 1949 年后注本仅书目登记与结论性引用、不转录译文，白话大意与注解均为依据公版原文自撰（第 3、38–43 行）

**遗留项（待纸本/后续）**
- WJ-TEX-28 命门三章共同传抄疑误 8 条、WJ-TEX-12「贼夭/贼天」反向异文、WJ-TEX-15「咎/晷」等存异条，均标"存疑，待纸本裁定"，需 1984 年影印本或《陈士铎医学全书》排印本复核
- WJ-RES-18「命门 94 处、10 篇专论」网络统计数据待纸本复核；WJ-BIB-26「梅自强 1980 年天津获见抄本」说学术出处待核

### C 阶段（交付收尾，2026-08-30）

**gates.toctrees——全量与范围双验证**
- 范围检查（带路径参数，仅断链检查）：`scripts/check-toctrees.py doc/bundles/tcm` 与 `... doc/bundles/tcm/classics/waijing-weiyan` 均输出"toctree 检查通过：全部 index.md 引用有效，所有内容文档均可达。"
- 全量四检查（断链/可达/一致/束根 index）报 14 处错误，逐条归因：12 处"未收录(不可达)"全部位于 think/confucian/four-books/（concepts 00–08、examples/02、facts.md、insights.md），2 处"缺失 index.md"为 think/confucian 与 think/confucian/four-books——**全部归并行会话 think/confucian 在建 WIP；tcm 侧 0 错误**。该 14 处非本任务引入，不修复。
- check-utf8：前置全量 6124 文件通过（UTF-8 无 BOM、LF 行尾）。

**并行会话边界（同盘并发，四重证据确认）**
- 本束开发期间，另一会话（spec：create-tcm-classics-okf-wiki）在同一子模块内实时建设 tcm/classics 其余 4 束（tcm-overview、nanjing、shanghan-zabinglun、shennong-bencaojing），并两度改写 classics/index.md、增强 tcm/index.md、更新 bundles/index.md（296→300 知识包）。
- 处置：本束提交边界收窄为 **仅 doc/bundles/tcm/classics/waijing-weiyan/ 24 文件**；共有导航文件（classics/index.md、tcm/index.md、bundles/index.md）与 think/* 全部内容一律只读、不提交。本会话曾写入的 classics/index.md 单束版（1552B）已被他会话五束版取代，归其所有。

**Sphinx 构建验证**
- 全量 `invoke build`（sphinx-build -b html -E，全树 6244 个 md 源）在 Windows 上单轮约小时级，远超单束验证所需；改用隔离迷你工程（最小 conf.py + myst_parser v5.1.0 + tcm 全树 89 文件副本 + 根 toctree）执行 `sphinx-build -b html -E`：**退出码 0，build succeeded**；waijing-weiyan **24 页全部生成、0 warning / 0 error**。
- 迷你工程中仅有的 7 条 warning 均非本束：tcm-overview/concepts/01 frontmatter YAML 畸形 1 条（他会话文件），think/ 树 xref_missing 6 条（迷你工程未复制 think/ 副本所致的环境假象，全量构建中目标存在）。
- 24 文件代码围栏配对自检：全部偶数闭合，无 Jinja 冲突 token；4 个 toctree 指令块（束根 + concepts/examples/references 三个子索引）。

**提交记录**
- 子模块（awesome-okf-xs）：`docs(bundles): 新增《外经微言》知识包（tcm/classics/waijing-weiyan）`——24 文件首版：90 条事实、4 洞察、9 概念、5 示例（13 篇双源核对精读原文）、3 信源页、81 篇存目；三层分离（著录/托名/文本）、真伪两派并列不裁决、红铅方术批判、医学免责与版权边界齐备。
- 主仓（SpecWeave）：同步 awesome-okf-xs gitlink 至上述提交。

**方法学（seven-concepts 场景 4：R→I→E→V→C）**
- R 事实采集 90 条（BIB 26 / TEX 31 / RES 23 / SRC 10，双源逐字核对、异文标注、存疑待纸本）→ I 架构洞察 4 四元组（同名异书三层分离/托名写作策略/逆向操作与命门水火同构/同源复制须异谱系对校）→ E 批量生成 24 文件束 → V 对抗审查（194 链接 0 断链、原文 12 锚点逐字一致、合规 4 项、G1–G4 全过）→ C 原子提交交付。

**独立审查与修复闭环（fresh context 只读子代理，24 文件全读）**
- 审查结论：7 大项（结构/链接 138 条 0 失效/facts 90 条编号连续且因果词零命中/insights 四元组经全库比对确认为"陈述+证据+反常识+行动"权威格式/合规六项/原文质量/编码无 BOM 纯 LF）全部 PASS。
- 必须修复 2 处（卷次硬伤，已修）：WJ-RES-17「卷七《紅鉛損益篇》」→「卷一第七篇」（facts.md，catalog/juan1-b/concepts/05 三处反证）；reading-path 案例 A「卷四《天人壽夭篇》」→「卷一第四篇」（该案例自述底本为一卷，自相矛盾）。
- 建议优化已采纳 5 项：①concepts/04 问答人物谱「少师」重复，删衍；②concepts/08 三模式补【检验标准】小节与成熟度标注（模式一 L2、模式二 L2、模式三 L1），达 G3 六要素完整形态；③log 方法学摘要 4 洞察标题订正为实际标题（同名异书/托名策略/逆向操作/同源复制）；④「凌波 2 处」坐标由不可定位行号改为文件名锚点；⑤juan1-yangsheng-a 两处「陈士铎曰；」补出校说明，与 shanyang「岐伯曰；」体例统一；⑥WJ-BIB-25 与 sources-xiandai 云南人民版订正为《黄帝外经解要与直译》（梅自强解要、廖冬晴直译、梅忠恕校订，2016-06 第 1 版，ISBN 9787222143029；2018 修订版 978-7-222-14302-9，出版社官网与 CIP 核）。
- 预防：卷次-篇名交叉核对纳入核读清单——凡 facts/concepts/examples 中出现"卷 X"字样，须与 catalog-81 存目表对号（本次两处错误均因凭印象写卷次、未对存目表）。