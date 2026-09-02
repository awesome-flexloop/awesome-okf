# 工作日志：《黄帝内经》阅读教程

- CMD 会话：`sc-20260830-huangdi-neijing`
- 方法论：seven-concepts-cmd 场景 4「知识沉淀」，链路 R → I → E → V → C
- Spec：`.trae/specs/huangdi-neijing-okf/`（spec.md、tasks.md 经用户审批；review.md 由独立审查生成）

## R 阶段（事实采集，2026-08-29 ~ 08-30）

- 信源网络：ctext 四部丛刊本《素问》《灵枢》（S1/S2，一级电子文本）、gushiwen 全文页（S3）、huangdineijing.org（S4）、qihuang.vip 与丁香园校勘帖（S5/S6）、cloudtcm《素问悬解》（S12）、itcmc《类经》、王洪图讲课 PDF、版本史文献（文摘报、北中医翟双庆文、大医网）
- 弃用信源：zysj.com.cn（SEO 垃圾占用）、zh.wikisource（抓取持续失败）；ctext 连续抓取约 6 页后间歇性限流，改为多源互校
- 产出：facts.md 共 137 条事实（F-001~F-137），G1 门通过（零现代因果连词，引号内文言豁免）

## I 阶段（架构洞察，08-30）

- 产出：insights.md（核心洞察四元组＋知识地图），G2 门通过
- 关键洞察：原文权威以"底本＋异文双录"保证而非择一；解读必须三层分离；《内经》文本是模型语言而非定律；非医疗边界贯穿全包

## E 阶段（萃取生成，08-30）

- 结构：1 bundle 根 index（type: OKF, okf_version 0.2）＋ concepts/ 13 文件（index + 00~11）＋ examples/ 10 文件（index + 8 精读 + 09 通读计划）＋ references/ 5 文件（index + editions/commentaries/modern-studies/electronic-sources）＋ facts.md / insights.md / log.md
- 原文核对：八篇精读引文逐字转录 ctext 底本（繁体原貌）；用字规则严格执行——鍼（非針）、麤（非粗）、云（非雲）、寫（瀉）、藏（臟）、府（腑）、鬭（鬥）、无（恬惔虛无）、痒（非癢）、栗（非慄）、太衝脈（脈名作"衝"；肝经原穴"太沖"底本即作"沖"，勿改）、穀（非谷）
- 异文双录：F-111"热因热用/热因寒用"两存；病机十九条属火 5/属热 4/属五脏 5/上下 2/风寒湿 3 = 19，无属燥，刘完素补燥条、高世栻心/火改读均登记
- 引文归属纠错："上守機者知守氣也""粗守關上守機"系《灵枢·小针解》语，concept 05 已改为转述，不冒充《九针十二原》本经
- 事故与恢复：E 阶段中途本 bundle 目录被外部隔离脚本移入 `.temp/active/daoyi-wip-quarantine/`，发现后整体移回正式位置，21 文件经字节数与内容校验完好（facts.md 26090 字节为最新版），随后完成 examples 与根 index

## V 阶段（独立审查）

- 由独立上下文执行对抗审查，产出 `.trae/specs/huangdi-neijing-okf/review.md`
- 重点：AC-5 抽 ≥20 段原文与 ctext/信源逐字比对；用字规则；异文双录；frontmatter 合规；非医疗声明覆盖

## C 阶段（整改闭环）

- 依 review.md（V 阶段独立审查：1 Blocker + 10 Major + 5 Minor）逐项定点修复并复验：
  - B-1：史崧献《灵枢》年份 1135→1155（南宋绍兴乙亥即 1155 年；1135 为乙卯年），facts/insights/concepts 00·01/references 共 5 处
  - M-1：F-110 信源 S7/S12→S7（"熱因熱用"读法仅见于王洪图 S7；S12《素问悬解》经文实作"熱因寒用"，异文双录见 F-111）
  - M-2：examples/06 底本行与本日志信源 legend 的 S7/S12 编号纠正（S7=王洪图教材/讲课，S12=cloudtcm《素问悬解》）
  - M-3~M-6：底本用字——恬惔虛"无"、"鬭"而鑄錐、精氣溢"寫"、治"五藏"（4 处 5 字）
  - M-7：examples/02 冬三月引文补回脱文 14 字"使志若伏若匿，若有私意，若已有得"（ctext 直核）
  - M-8：F-088 与 examples/03"天運當以日光明"补"日"字（ctext 直核）
  - M-9：十九条"膹鬱""逆衝上"繁体正字与 concepts/08 统一，并出字形校记（同篇"衝"字 ctext 已核；十九条整段页限流未直核，如实标注）
  - M-10：insights 事实计数 128→137
  - m-1：concepts/06 篇末补阅读边界段；m-2："膨脹而喘咳"从 ctext《灵枢·经脉》底本（审查翻案正确）；m-3：facts 凡例补简体信源繁体化说明；m-4："冬為飱泄"从底本并出异体注记；m-5：用字规则"太衝"限定为"太衝脈"（穴名太沖勿改）
- 修复后复跑 check-toctrees（本包范围）与关键字归零搜索；子模块内原子提交（docs(think): 中文主体），只 add 本包文件，不动主仓库 gitlink

## 信源编号对照

S1=ctext《素问》四部丛刊本；S2=ctext《灵枢》四部丛刊本；S3=gushiwen 全文页；S4=huangdineijing.org；S5=qihuang.vip；S6=丁香园校勘帖；S7=王洪图《内经选读》教材/讲课；S12=cloudtcm《素问悬解》；S13=itcmc《类经》。详见 [references/electronic-sources.md](references/electronic-sources.md)。

## 配图与可视化增强（2026-09-02）

- 范围：全包增补 6 张 Seedream AI 意境图 + 11 张 Mermaid 图（其中 concepts/08 篇 2 张），仅做新增，既有正文、引文、表格、frontmatter 一字未改
- 分布清单：
  - index.md：hero 图 hero-qibo.jpg（岐黄对坐问答，置于首要声明之后、快速导航之前）
  - concepts/01：editions-slips.jpg（简牍版本意境图）
  - concepts/02：全书板块与三级阅读路径 flowchart
  - concepts/03：yinyang-landscape.jpg（阴阳山水意境图）+ 五行环 flowchart
  - concepts/05：nine-needles.jpg（九针意境图）+ 十二经流注环 flowchart
  - concepts/06：病因分类 flowchart
  - concepts/08：病机十九条归类 flowchart + 正治反治 flowchart（2 张）
  - concepts/09：女七男八盛衰 flowchart + four-seasons.jpg（四季山水长卷意境图）
  - concepts/10：五运六气 flowchart + yunqi-celestial.jpg（运气天象意境图）
  - concepts/11：注本导航 flowchart
  - examples/09：十二周通读计划 gantt（四阶段 section、每周任务，周次主题出正文表格）
  - insights.md：知识地图 mindmap（文献层/理论层/实践层/边界层四分支，原有树状图保留）
- 图片存放：doc/_static/bundles/yixue/huangdi-neijing/images/，Markdown 引用路径 /_static/bundles/yixue/huangdi-neijing/images/<name>.jpg
- 风格说明：6 张图均为宋代院体工笔/水墨浅绛意境图，画面无文字；图前引导语克制，alt 文本注明意境图性质
- Mermaid 编码：围栏全小写、块内无空行、中文文本双引号（flowchart）、节点 ID 全英文、subgraph 用 EN_ID ["中文标题"]、边标签 -->|"标签"|、无 <br/>、无带圈数字、无【】、无 Unicode 箭头；mindmap 节点文本不加引号、无冒号
- 门禁状态：本批 4 个文件（index.md、examples/09、insights.md、log.md）经主仓库 .agents/scripts/lib/checks/mermaid.py 的 _process_file 原位校验，errors=0、warnings=0；gantt 一次通过未降级
- V 审查结论：独立 V 对抗审查（2026-09-02，未参与制图的黑盒审查上下文）完成。① Mermaid 门禁：13 个变更文件经主仓库 .agents/scripts/lib/checks/mermaid.py 的 _process_file 原位校验，errors=0、warnings=0；② 事实核验：11 张 Mermaid 图逐项与 facts.md（F-001~F-137）及正文对照一致——五行相生相胜环、十二经流注环、全书板块与三级阅读路径、病因分类、病机十九条归类（火5/热4/五脏5/上下2/风寒湿3=19，无属燥）、女七男八盛衰、五运六气配属、注本导航、examples/09 十二周 gantt（周次主题出正文表格）、insights 知识地图 mindmap（四分支），未发现事实错误；③ 图片目检：6 张 AI 意境图逐张打开核验，均无文字、无现代元素、主题匹配；修复 1 项——concepts/01 editions-slips.jpg alt「青铜油灯」→「青铜灯台」（与画面实际器物一致）；④ 已闭环：nine-needles.jpg 初版偏写实摄影风，与其余 5 张宋代院体工笔/水墨浅绛风格统一性略弱；主控按院体工笔重出一版（绢本工笔、漆匣靛垫九针、葫芦竹简卷，无文字无现代元素）。替换过程中发现 edit_file_rename 类文本模式搬运工具会损坏二进制（高位字节被 UTF-8 替换符 EF BF BD 取代，JPEG 文件头失效），遂删除损坏件、以同 prompt 重新生成落盘 nine-needles.jpg；终态验证：JPEG 文件头 FF D8 FF E0（JFIF）有效、729KB 非空、逐张目检工笔风格与其余 5 张统一；⑤ 侵入面：变更均在本束范围内，仅新增图块/图引/引导语与本日志回填，既有正文、引文、表格、frontmatter、toctree 未动，无 git 写操作
- Sphinx 构建：子项目 doc/conf.py 配置确认（myst_parser + sphinxcontrib.mermaid，myst_fence_as_directive=['mermaid']，mermaid 11.4.1 CDN 运行时渲染、零本地构建依赖；依赖见 pyproject.toml [doc] extra，py314 环境齐备）。全树解析构建（py314：python -m sphinx -b dummy -E doc，真实 conf.py 全量 7516 文档）结果 build succeeded、共 2 warnings，均位于 yishu/vocal/meitong-yanyin-pedagogy（并行会话他方束，H2 起始/过渡线，与本包无关）；本包 28 个文档全部解析通过，13 个变更文件逐一确认 READ_OK、0 warning，无 Malformed YAML、无 Mermaid 指令解析错误；6 张图片引用 /_static/bundles/yixue/huangdi-neijing/images/<name>.jpg 路径逐一解析命中现存文件（522KB~1.2MB 非空）。注：Mermaid 图形语法由 CDN 端渲染，构建期不校验图内语法，其语法正确性以门禁（errors=0）与人工事实核验为准