---
type: log
id: china-art-therapy-log
title: 中国艺术疗愈知识包编纂日志
description: 中国艺术疗愈 OKF 知识包 R/I/E/V/C 各阶段执行记录、古籍异文处理与讹传修正项清单、年份口径与话语边界处理记录。
tags: [china-art-therapy, 中国艺术疗愈, 编纂日志, 异文处理, 讹传修正]
generated: { by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }
created: 2026-09-01
status: stable
stale_after: 2027-09-01
---

# 中国艺术疗愈 OKF 知识包编纂日志

## 2026-09-01 R 阶段（事实复核与信源确认）

- 工作基础：facts.md（CN-01 ~ CN-11）已由前置调研完成登记——古籍引文逐字核对（ctext.org 四部丛刊初编本 × 古诗文网/通行整理本对读）、异文显式标注、平台约定（zysj.com.cn 禁用，承 daoyi-reading FRG-006；异文处理承接 yixue/tcm 束 NGJ-028 两读并列先例）均已就位。本阶段任务为**复核而非重登**：逐条读取 facts，未修改 facts.md 已核对内容。
- 古籍引文复核要点：
  - CN-01《素问·阴阳应象大论》东方段逐字全文（“在藏为肝”“在音为角”“在志为怒。怒伤肝，悲胜怒”等）；南方/中央/西方/北方四段音—志—胜复字段核对一致，正文引用未逐字登记的中段文字一律以“……”省略，不自行补全。
  - CN-03《素问·举痛论》九气段逐字全文（句号读）；九气名目与六个情志之气划分照录。
  - CN-04《儒门事亲》以情胜情五法逐字（古今图书集成医部全录情志门转录源）。
  - CN-05 张介宾《类经·疾病类》按语逐字（北中医翟双庆文转录源）。
- 异文登记确认（八组＋年份口径三组）：见 [references/sources.md](references/sources.md) 第四节台账；正文“某本作某”格式自本台账派生。
- 讹传修正项确认：①“中央音乐学院 1988 设立”→ 中国音乐学院 1988 大专班（CN-06 双源：音乐周报文 × 张鸿懿《发展中的音乐治疗》，《中央音乐学院学报》2000 年第 2 期）；②《儒门事亲》篇名“衍”非“术”（CN-04 三源版本目录）。

## 2026-09-01 I 阶段（洞见与框架萃取）

- 核心洞见 3 条：①分层框架——“传统中医情志话语”与“现代循证 music therapy/艺术治疗”须显式分判，互不冒充（CN-05、CN-11）；②引文不越出核对范围——facts 未逐字登记的段落以省略号处理，不自行补全；③讹传双源修正须留痕——年份、篇名、导师三类口径差异全部并列登记不裁决。
- 可复用模式 2 条：①古籍异文“某本作某”登记法（承接 NGJ-028 先例）；②术语边界自检清单法（表述类错误逐问回改）。

## 2026-09-01 E 阶段（成稿展开）

- 产出 12 个新文件：束根 index.md；concepts/（index + 00-overview、01-wuyin-classics、02-qingzhi-xiangsheng、03-modern-introduction、04-east-west-dialogue 共 5 篇）；examples/（index + 01-reading-plan）；references/（index + sources）；log.md。
- 分层框架落地：概念 00 承担边界声明（四条术语边界清单），概念 01/02为传统语境层（原文＋异文），概念 03为现代语境层（建制节点），概念 04为对读层（三维对照表＋互不冒充声明）。
- 跨束链接落地：concepts 内以 `../../../../yixue/tcm/index.md`、`../../../../yixue/daoyi/index.md` 链接 yixue 束；束根以 `../../../yixue/...` 形态；姊妹束用 `../music-therapy/index.md`、`../art-therapy/index.md`、`../dance-drama-therapy/index.md`；liaoyu-overview 与 expressive-arts 无 index.md，链接指向其 facts.md。
- 版权分层执行：古籍（公共领域）全文/逐字引用；现代文献仅结论性引用＋书目（张鸿懿 2000、龙泽云等 2006、张晓敏/尹爱青 2014 均以书目形式登记）。

## 2026-09-01 V 阶段（一致性与合规自查）

- frontmatter：束根 index.md 携 version: "1.0.0"、sources（resource: facts.md）、okf_version: "0.2"；概念/示例/信源文档携 type: OKF、version、sources；Index 文档 type: Index；log.md 用 type: log + created。generated 统一为 `{ by: "agent:general_purpose_task", at: "2026-09-01T20:00:00+08:00" }`；status: stable；stale_after: 2027-09-01。
- YAML 安全：双引号标量内无 ASCII 双引号；中文语境引号一律全角“”；古籍引文内全角引号直接使用。
- 链接：全部站内相对链接带 .md 后缀；concepts 内跨束链接回溯层级核对无误（concepts→bundles 四级）；无 file:/// 绝对路径。
- toctree：根 index 收 concepts/index、examples/index、references/index、facts、log 五项；concepts/index 收 00—04 五篇；examples/index 收 01-reading-plan；references/index 收 sources——与目录实际文件一一对应。
- 字数：概念文档各约 2500—3500 字，符合 1500—4000 字区间。
- 单源与异说：五级分级（单源待核）、学会挂靠单位、1988/1989、1996/1997、Maranto/Dileo 各项在正文与 sources 台账双重披露。

## 2026-09-01 C 阶段（闭环与遗留项）

- 古籍异文处理记录：八组异文全部“两读并列不裁决”，无静默统一、无径改；义理级异文（③④⑥组）在正文显式提示“引用时注明所依读法”。
- 讹传修正闭环：讹传修正项（校名、篇名）在束根简介、概念 00/03、信源台账、阅读计划自检清单四处冗余呈现，确保任一入口读者均可见修正结论；预防性机制为表述自检清单八问（examples/01-reading-plan.md）。
- 遗留项与披露：①音乐治疗师五级分级维持（单源待核），待权威规章来源核补；②对照表“职业体系”维中“周代乐正、太医院”为框架性概括（facts 未立专条），已在正文与表格双处注明“框架性概括”身份，后续可增补专门事实条目；③研究生专业目录中艺术治疗尚未独立成专业（CN-09），后续年度目录发布时须复核更新。
- 写权限边界：全部文件位于 bundles/yishu/liaoyu/china-art-therapy/ 内；未修改 facts.md 已核对内容；未触碰其他目录。

## 口径说明

- 本束 facts 编号体系为 CN-01 ~ CN-11（区别于姊妹束 MT-xx、OV-xx、NGJ-xx、FRG-xx、CAN-xx），正文引用一律“facts CN-xx”形态。
- 古籍底本：ctext.org 所据《四部丛刊初编》本《重广补注黄帝内经素问》；简体行文，繁体底本用字（藏、徵）保持原字照录。

## 2026-09-02 视觉增补（R/E/V 阶段）

- 增补束封面配图 1 张：seedream 生成暖灰纸感水墨插画 `china-guqin-inkwash.jpg`（案头古琴置于长幅宣纸之上，旁有墨碟，纸上淡墨山水留白，传统文人书斋氛围），落 `doc/_static/bundles/yishu/liaoyu/china-art-therapy/images/`，以引导句＋图片行插入束根 [index.md](index.md) 免责声明 blockquote 之后、「📚 快速导航」之前。
- 增补 Mermaid 图 1 张：M10 五志相胜循环（[concepts/02-qingzhi-xiangsheng.md](concepts/02-qingzhi-xiangsheng.md)「二、《素问·阴阳应象大论》情志相胜五句」小节内、五句表与异文提醒段后、「三、张从正」前；怒→思→恐→喜→忧（异文：悲）→怒 五志克制环）。
- 方法：seven-concepts 链路 R（视觉点盘点）→ I（高价值可视化点洞察）→ E（配图与图产出、插入）→ V（对抗验证）；图中五志-五脏-五音-方位-五行对应与相胜五句均可溯源至本束正文与 facts（CN-01），环序严格依五行相克，无新造事实、无因果演绎；末边标签「悲胜怒」为东方段原文、西方段「忧/悲」两读并列，引导句已随图插入并声明本图属中医情志学说文献梳理、不构成现代临床建议；Mermaid 源码遵循主仓库门禁（单行标签、含中文标签双引号包裹、无 `<br/>`、块内无空行），逐字采用视觉方案单行版本，未作改写。
- 增量边界：本次仅新增引导句、图片引用行与 Mermaid 围栏块，未改动 frontmatter、事实正文、免责声明、toctree、facts.md 与 references/。
