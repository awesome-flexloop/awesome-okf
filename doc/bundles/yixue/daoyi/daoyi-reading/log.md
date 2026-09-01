# 更新日志

## 2026-09-02

### 视觉增强（事实内容零变更）
- 新增 8 张 AI 生成水墨意境插图：束首页 index.md（hero-daoyi）与概念 01-07（history-yidao、classics-roots、daoist-physicians、daozang-canon、neidan-cultivation、excavated-texts、yidao-schools）；图片存放于 doc/_static/bundles/yixue/daoyi/daoyi-reading/images/，以站点绝对路径 /_static/bundles/yixue/daoyi/daoyi-reading/images/ 引用，统一配图注"AI 生成意境图，非历史图像，仅作阅读氛围辅助"；插图位置均在各页开篇引言之后、第一个二级小节之前。
- 新增 9 张 Mermaid 图表（概念 00/01/03-08 与示例 02）。
- 以上均为视觉增强：正文事实文字、交叉链接、frontmatter、toctree、表格与引用块零变更。

## 2026-08-30

### 创建
- 初始化 daoyi-reading 知识包：道医经典权威阅读教程，覆盖广义道医六层——医道同源（黄帝内经体系）、道-理-术三层、道门医家（葛洪/陶弘景/孙思邈）、道藏医书与养生文献、内丹与身神传统、出土方技（马王堆/张家山/天回/敦煌）。
- 方法链路：seven-concepts-cmd 场景4（知识沉淀），R（事实采集）→ F（事实登记）→ I（洞察提炼）→ E（教程生成）→ V（验证）→ C（沉淀）。
- 生成9篇概念文档、3篇示例文档、4篇信源文档。

### 结构
- concepts/：00-what-is-daoyi, 01-history-yidao-tongyuan, 02-classics-daolist-roots, 03-daoist-physicians, 04-daozang-medical, 05-neidan-medical, 06-excavated-fangji, 07-yidao-schools, 08-authenticity-and-sources
- examples/：01-classic-passages（10段逐字原文）, 02-reading-paths（三档阅读路径）, 03-modern-study-practice（现代学术地图）
- references/：01-online-sources（27部典籍×平台矩阵）, 02-print-editions（点校本与出土整理本）, 03-modern-scholarship（研究著作）, 04-authenticity-register（辨伪登记）
- facts.md：116条事实，七组编号（AX学术体系/CAN医经医家/DAO道藏内丹/EXC出土/FLW流派/FRG辨伪/SRC信源），零因果推测措辞
- insights.md：6条四元组洞察（陈述/证据/反常识/行动）+ 知识地图 + 三档阅读顺序

### 信源核验与辨伪原则
- 在线信源按"识典古籍＞维基文库＞ctext 主库＞道藏阁"分级使用；zysj.com.cn 全站禁用；ctext res=161524《本草纲目》OCR 乱码禁用。
- 10段精选原文全部逐字核验：段1、5、10 经 ctext（四部丛刊底本）核验；段2"治未病"经维基文库《黃帝內經·素問第一卷》核验；段3"普同一等"经维基文库《大醫精誠》单篇与道藏阁《千金要方·论大医精诚第二》双重核验；段6 经道藏阁《黄庭内景玉经》录文核验；段7、8 经维基文库《周易參同契》《悟真篇》核验；段4、9 以纸本整理本为据。异文标注两说（如《黄庭经》"含明/台明"、《悟真篇》"迷途/迷涂"、《云笈七签》122卷本与120/121卷本卷次差异）。
- V 阶段补充信源：道藏阁《千金要方》30卷本（/xuanxuewushu/qianjinyaofang/，含大医精诚章）实测可达，已登入在线信源矩阵；维基文库《備急千金要方》全书卷子页内容不全，但《大醫精誠》独立单篇全文可用。
- 五部争议书（《中藏经》《辅行诀》《医道还元》《扁鹊心书》《华佗神医秘传》）两说并陈；低权威读物（祝守明《道医讲义》、王爱品《道医论》）单列警示；未证实说法（《道医集成》版次、陈撄宁《道教与养生》版本、《汉志》房中卷数、潘毅著作年份）标"待考"不入结论。
- 束根与全部涉医页面含非医疗声明：本知识包为文化与文献研究内容，不构成医疗、诊断、用药、针灸或练功指导。

### 修订（fresh-context 独立审查后）
- T16 独立审查（结论 pass）6 条建议全部修复：
  1. 《千金要方》道藏本卷数统一为双口径并注——"识典 DZ1163 道藏本著录为93卷，钟肇鹏统计作95卷，卷数分合口径不同"（facts AX-021、concepts/01、03、04、references/02 共5处）。
  2. 典籍计数统一为"27部"（束根 index、insights 知识地图，与 references/01 矩阵实际收录数一致）。
  3. 《周易参同契》维基文库分章统一为"35章分章本"（concepts/05，与 facts DAO-012、references/01、examples/01 一致）。
  4. 《针灸甲乙经》穴数改为"记349穴（一说348穴）"两说并陈（concepts/02，与 facts CAN-010 一致）。
  5. concepts/08 方法论页补非医疗声明（辨伪结论不构成疗效背书）。
  6. facts.md SRC-001 标点多余空格删除。