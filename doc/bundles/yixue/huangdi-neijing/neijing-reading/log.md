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