---
type: OKF
title: 编纂日志
description: '手势辅助声乐教学教程编纂日志：2026-09-02 R/F/I 阶段（双源调研、33 条 GV 事实、信源冲突裁决、束骨架与架构洞察）；2026-09-03 E/V 阶段（concepts 8 篇 + examples 3 篇、5 张配图、四视角对抗审查 10 项反馈与 8 项修复）。'
tags: [log, 声乐教学, 柯尔文手势, 编纂日志, OKF]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-03T20:00:00+08:00" }
status: stable
stale_after: 2027-09-02
---

# 编纂日志

倒序日期分组；本束目前两个编纂日（2026-09-02、2026-09-03）。

## 2026-09-03

**E（萃取/撰写）**
- concepts 8 篇全部完成：00 入门地图（三读者路径 + 术语对照表）、01 手势为什么有效（具身认知/概念隐喻/脚手架理论，阳性与阴性实证并列）、02 柯尔文七唱名手势（源流 + 七型总表 + 逐型详解 + 镜面约定）、03 声乐课堂五类手势（呼吸/打开/共鸣/线条/咬字起收，四元组组织）、04 指挥手势基础（2/3/4 拍图式 + ictus + 合唱排练手势）、05 达尔克罗兹体态律动（三分支 + 三个课堂简易活动）、06 手势教学五序列（准备/呈现/练习/内化/撤除 + 教师规范）、07 反模式与安全（12 条反模式 + 嗓音安全节）。
- examples 3 篇全部完成：01 视唱每日手势练习（四周剂量表，Day0–Day30，含每阶段分步流程/可观察自检/常见错误回指）、02 二十分钟练声手势流程、03 儿童集体课例（45 分钟，按五序列编排）。
- 全部正文 GV 回指经脚本核验：33 条定义/33 次引用双向闭合；跨束链接 11 处（姊妹束 meitong-yanyin-pedagogy）、束内相对链接与锚点 14 处逐一核对文件存在与标题 slug 闭合。
- concepts/index.md、examples/index.md、references/index.md 导航表与束根 toctree 的 HTML 注释占位全部解开，toctree 仅引用已存在文件。

**Task 6（配图）**
- seedream 生成 5 张配图并嵌入：束根封面 hero-gesture-voice.jpg、02 篇 curwen-hand-signs-chart.jpg、03 篇 vocal-breath-ball.jpg、04 篇 conducting-patterns.jpg、示例 03 child-class-gestures.jpg；统一暖灰纸纹、柔和光线、无文字风格；图片存于 doc/_static/bundles/yishu/vocal/gesture-vocal-pedagogy/images/，以 /_static/ 绝对路径引用。

**V（四视角对抗审查）**
- 机械化体检：frontmatter 七字段齐全（log.md 无 verified 从惯例）、okf_version 仅束根 index.md、UTF-8 无 BOM、链接/图片路径全闭合、锚点 slug 与标题逐一匹配。
- 四视角审查产出 10 项反馈（P1×3 / P2×4 / P3×3），修复 8 项：
  - V-01（P1）facts.md 正文采集时间与 frontmatter 日期矛盾 → 全束 20 文件时间戳统一为 2026-09-03；
  - V-02（P1）中文读者熟悉 si 而本束用 ti 未说明 → 02 篇增"唱名写法说明"，显式标注 si=ti、re=ré（GV-03）；
  - V-03（P1）日志缺 E/V 阶段 → 本日志补齐；
  - V-04（P2）洞察四"四阶"与 06 篇"五序列"表述不对齐 → 教学行动段改为五阶段展开并标注四阶为压缩表述；
  - V-05（P2）AI 手型示意图可能不准 → 02 篇图下增"示意图、精确规格以文字总表为准"声明；
  - V-06（P2）verified 时间戳未反映真实 V 阶段 → 统一更新为 2026-09-03T23:30+08:00；
  - V-07（P2）Day 编号与"练 6 休 1"关系不明 → 示例 01 阶段总表增"Day 为练习日编号"说明；
  - V-08（P3）示例 01 阶段 2 内容表 la-ti 与步骤 la-do′ 不一致 → 内容表补 la-do′ 并将 la-ti 定位为级进对照。
- 不改 2 项（经核原文已足）：V-09 调音器 App 描述、V-10 指挥"里/外"参照系（已以练习者右手为基准说明）。
- V 二次复审（图片专项，TR-6.2/CP-24）：5 张配图逐图人工审查——均无六指/多指融合等严重解剖错误，暖灰纸纹风格统一、无乱码文字；curwen-hand-signs-chart 七型手型与 child-class-gestures 课堂手势为示意级别（AI 手部简化：平掌类细分与单/双食指不精确），按 Task 6 预案接受并以文字规格为准；本次补齐封面/呼吸/指挥/课堂 4 处图注（连同 V-05 的 02 篇声明，5 处配图全部诚实标注"示意、以文字为准"）。

**C（注册/门控/提交）**
- 三处注册完成：vocal/index.md 知识包表与 toctree 收录本束；yishu/index.md 声乐教学组更新为两束并列（美通咽音·手势教学）；bundles/index.md total_bundles 498→499、mermaid yishu 行与域节标题束数同步（8 束）。
- 门控：定向 Sphinx dummy 构建（新束全部 .md + 三处注册文件）退出码 0，**本束零 warning**（输出中的 warning 全部位于既有束 zhexue/methodology/first-principles 的 H1→H3 标题惯例，以及他会话 untracked 的 jishu/ai/agent-platform-notes）；.temp/dummy 构建产物已清理。
- `invoke gates.all` 全库运行退出码非 0：11 处 toctree 问题全部位于 `doc/bundles/jishu/ai/agent-platform-notes/`，经 `git status`/`git ls-files` 证实该束为 untracked 的他会话 WIP，不在本任务范围；本束自身 UTF-8/toctree/束计数经 gv_check 脚本（frontmatter 可解析、GV 引用双向闭合、链接/图片路径闭合）与 Sphinx 构建双重验证通过。
- 原子提交：暂存集精确限定为本束目录、_static 5 张配图与三处注册文件；排除他会话 WIP（agent-platform-notes、baseline-errors.txt、full-errors.txt）；工作区中 meitong-yanyin-pedagogy/facts.md 被某 Markdown 格式化工具污染（frontmatter `---`→`***`、YAML 键被反斜杠转义、URL 被尖括号包裹、表格重排），非本会话改动，已排除出暂存集，留待用户核查处置（建议 `git checkout` 恢复）。

**待办（遗留事项）**
- GV-15、GV-22 单源待核项与 GV-25 支点七类待核项继续补源（stale_after 2027-09-02 前复核）。
- 主仓库 SpecWeave 的子模块指针 bump 留用户决定（Open Question Q3）。
- 他会话 untracked 束 agent-platform-notes 的 11 处 toctree 问题需该会话修复后 gates.all 方可全库全绿。

## 2026-09-02

**R（研究/事实登记）**
- 双源（多源）Web 公开信源调研完成，产出 [facts.md](facts.md) 共 33 条事实，编号 GV-01 至 GV-33，分五组：一、人物与体系源流（GV-01~GV-12）；二、柯尔文手势体系手型与空间高度（GV-13~GV-15）；三、机构与国际推广（GV-16~GV-20）；四、教学法实践：指挥图式、课标与中国民族声乐教学（GV-21~GV-25）；五、科学基础：具身认知、垂直空间隐喻与实证研究（GV-26~GV-33）。
- 信源按四轨组织：源流轨（Norfolk Record Office、BKA/Waterhouse、Kodály HUB、Internet Archive 原书）、机构轨（Kodály Institute、IKS、UMD 档案馆、BKA、Dalcroze 官网）、科学轨（JRME、Music Perception、Frontiers in Psychology、PMC）、中国轨（教育部课标 PDF、中央音乐学院、燕赵都市报）。
- 信源冲突裁决（均在 facts.md 按语中留痕）：
  - Glover 生年采教区档案与 BKA 论文的 **1786–1867** 说：Norwich 教区登记 1786-11-13 受洗、1867-10-20 去世；中文资料 1793 说与档案不合，Southcott 章节作 1786–1865（卒年异说）并列存目（GV-01）。
  - 柯尔文手势定型年采 Waterhouse 考证 **1870** 说（"手势是 Curwen 为数不多的原创要素之一，直到 1870 年才发明"）；与教学站点"1858 年随《Standard Course》定型"说调和为：课程首版 1858、手势 1870 年补入体系（GV-06）。
  - OAKE 成立年采马里兰大学档案馆藏行政史与 OAKE 自我介绍的 **1975（Milwaukee 成立大会）** 说；任务书 1977 说与档案不合，1973 说系 Oakland 首届研讨会而非组织成立（GV-19）。
  - BKA 成立年 **1981/1983 两说并存**不裁决：Vajda 传记作 1981 创立，BKA 官方材料称培训课程自 1983 年运行（GV-20）。
  - "支点分七类"细分说未复核到权威公开原文，标注待核（GV-25）；手势引入顺序（GV-15）与沪教版指挥图式课例（GV-22）为单源待核，已逐条标注。

**F（公理/命题提炼）**
- 从事实组提炼三条束内公理，作为 I 阶段洞察与 E 阶段撰写的组织主线：
  1. 手势 = "声音参数→身体动作"的转译器（音高→垂直空间映射有具身认知与实验证据，GV-26~GV-28）；
  2. 两套逻辑不可混用：柯尔文手势是符号化音高系统（GV-13~GV-15），声乐课堂手势是机能提示（GV-24~GV-25），指挥图式是节拍组织（GV-21）；
  3. 脚手架终须撤除：实证阳性结果集中在初学建立阶段（Steeves 1984、Cassidy 1993，GV-29~GV-30），充分训练后阴性（McClung 2008、Martin 1991、Cousins & Persellin 1999，GV-31~GV-32）。

**I（架构设计）**
- 定型三层结构：concepts 计划 8 篇（00 入门地图 / 01 手势为什么有效 / 02 柯尔文七唱名手势 / 03 声乐课堂五类手势 / 04 指挥手势基础 / 05 达尔克罗兹体态律动 / 06 手势教学五序列 / 07 反模式与安全）；examples 计划 3 篇（01 视唱每日手势练习 / 02 二十分钟练声手势流程 / 03 儿童集体课例）；references 2 篇（R 阶段已产出）。
- 产出 6 个文件：束根 [index.md](index.md)（frontmatter 含 okf_version: "0.2"、嗓音安全 blockquote、HERO_IMAGE_SLOT HTML 注释占位、快速导航三表、三读者路径 mermaid、与姊妹束关系说明）；[concepts/index.md](concepts/index.md) 与 [examples/index.md](examples/index.md)（导航骨架，8+3 行预填，toctree 以 HTML 注释占位）；[references/index.md](references/index.md)（收录已存在两篇信源，toctree 含 2 条目）；[insights.md](insights.md)（5 条四元组洞察：转译器本质 / 两套逻辑 / 脚手架撤除 / 身体经验先于符号 / 指挥组织群体与柯尔文发展个体分工）；本日志。
- 诚实记录：references/01、02 两文由 R 阶段产出，但 references/index.md 导航页由本 I 阶段任务补齐；concepts/ 与 examples/ 下 8+3 篇正文待 E 阶段（Task3/5）创建，届时取消两处 index 与束根 toctree 中的 HTML 注释占位；封面图待 Task6 插入束根 HERO_IMAGE_SLOT 处。
- 与姊妹束《美通唱法与咽音体系教学教程》（../meitong-yanyin-pedagogy/）确立交叉分工：本束管手势（转译/提示/组织），姊妹束管发声机能训练与嗓音保健；束根已设交叉链接。
- 体例对齐：frontmatter 双引号标量内无 ASCII 双引号（description 用单引号单行）；除束根 index.md 外任何文件不含 okf_version 字段；mermaid 节点标签单行、中文双引号包裹、无 `<br/>`、块内无空行；toctree 仅引用已存在文件。
- 未执行 git add/commit；facts.md 与 references/01、02 两文全程只读未改。

**待办（遗留事项）**
- E 阶段：撰写 concepts 8 篇与 examples 3 篇，完成后将 concepts/index、examples/index 并入束根 toctree 并解开子目录 toctree 注释。
- V 阶段：正文撰写时逐条核对 GV 编号回指；GV-15、GV-22 单源待核项与 GV-25 支点七类待核项继续补源。
- Task6：束根封面图插入 HERO_IMAGE_SLOT 占位处。
