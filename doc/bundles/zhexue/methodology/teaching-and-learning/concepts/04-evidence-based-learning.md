---
type: concept
name: 学习科学循证策略
title: 学习科学循证策略：让学真实发生的证据清单
aliases: ["evidence-based learning", "学习科学", "检索练习", "间隔效应", "主动学习", "认知负荷"]
group: zhexue/methodology
sources:
  - id: manchester
    resource: https://www.elearning.fse.manchester.ac.uk/fseta/factsheet-how-students-learn/
    title: "Factsheet: How Students Learn（FSE Teaching Academy, University of Manchester）"
  - id: ntu
    resource: https://www.ntu.edu.sg/education/inspire/learning-sciences-evidence-based-teaching-strategies
    title: "Science of Learning - Evidence-based Teaching Strategies（NTU Singapore）"
  - id: bnu-brain
    resource: https://brain.bnu.edu.cn/shfw/kpxx/a65fb173e2eb4a2fbac8689c1308aeb1.htm
    title: "北京师范大学认知神经科学与学习国家重点实验室：间隔激活神经元"
  - id: brain-friendly
    resource: http://m.jyb.cn/rmtzgjyb/202609/t20260921_2111523733_wap.html
    title: "教学'脑友好'，学习更高效（中国教育新闻网）"
  - id: zju-ls
    resource: https://www.zju.edu.cn/_upload/article/files/b9/2d/dfbce44b4d05a3aa48687ae2723c/dfe57e87-335e-4292-b269-f1c54dba9d99.pdf
    title: "学习科学：正在进行的学习革命（浙江大学）"
  - id: cnaes
    resource: https://www.cnaes.edu.cn/post/151757
    title: "人工智能时代的教育价值与功能省思（中国教育科学研究院）"
created_at: 2026-10-20
---

# 学习科学循证策略：让学真实发生的证据清单

学习科学（Learning Sciences）是近三十年来发展起来的关于教和学的跨学科研究领域，涉及教育学、脑科学、心理学、信息科学等，核心问题是"人究竟是如何学习的"以及"如何支持和促进学习"[^zju-ls]。以下策略均有机构级信源支持，是"怎么做"的循证答案。

## 策略清单

| 策略 | 核心机制 | 证据要点 | 执行建议 |
|------|---------|---------|---------|
| **检索练习（测试效应）** | 主动回忆比被动重读更巩固 | 花时间练习的学生比重读/高亮/摘录的学生学得显著更多，跨能力、跨任务成立[^manchester] | 用自测、闪卡、闭卷回忆替代反复阅读 |
| **间隔效应** | 分散练习优于集中突击 | 学习期间的休息和睡眠可增强学习、减少遗忘；相比不间断连续练习，间隔分段的检索效果更好[^bnu-brain] | 把 3 小时拆成 3 个 1 小时，跨天分布 |
| **交错练习** | 混合不同类型题目优于同类集中 | 交错练习是"How Students Learn"事实表中的核心效应之一[^manchester] | 复习时混合题型/主题，不按章节顺序刷 |
| **样例效应** | 研读已解样例优于空手解题（新手期） | 样例效应被列为关键学习效应[^manchester] | 新手先研读样例→再独立解题 |
| **主动学习** | 直接参与而非被动接收 | think-pair-share、同伴互教、问题式学习均属主动学习[^ntu] | 讨论、互教、真实问题协作 |
| **认知负荷管理** | 控制内在/外在/关联三类负荷 | 教学要把控内在负荷（内容复杂性）、外在负荷（设计干扰）、关联负荷（图式建构资源）[^brain-friendly] | 分解复杂任务、消除冗余设计、用支架逐步推进 |
| **双重编码** | 语言+视觉双通道编码 | "脑友好"教学建议运用双重编码原理组织信息[^brain-friendly] | 图文结合、概念图、图示化 |
| **元认知监控** | 对自己思维过程的觉察与调节 | 反思能力是抵御认知卸载、保持主体自觉的关键防线[^cnaes] | 自问"我真的理解了吗""依据是什么" |

## 关键结论

1. **输出 > 输入**：练习与检索的效果系统性优于重读、高亮、摘录[^manchester]——这是"以输出驱动输入"（费曼学习法）的科学基础，与 [教学相长](05-teaching-learning-relationship.md) 的机制同构。
2. **设计 > 努力**：认知负荷管理表明，学习的成败很大程度取决于**学习材料与任务的设计**（教的一侧），而不只是学习者的意志（学的一侧）。
3. **证据有边界**：以上效应主要来自教育心理学实验与系统综述，真实课堂中的效应量受学生前备知识、动机与教师执行质量调节；不可宣称普适（对抗审查视角）。

实操执行手册见 [examples/02-learning-strategy-playbook](../examples/02-learning-strategy-playbook.md)。

[^zju-ls]: 浙江大学《学习科学：正在进行的学习革命》：学习科学是近三十年发展起来的关于教和学的跨学科研究领域，研究如何支持和促进人在整个生命历程中的学习活动。
[^manchester]: University of Manchester FSE Teaching Academy《Factsheet: How Students Learn》：testing, spacing, worked-example, interleaving 四效应；实践学习的学生显著优于重读/高亮/摘录的学生。
[^bnu-brain]: 北京师范大学认知神经科学与学习国家重点实验室：学习期间休息和睡眠可增强学习、减少遗忘；间隔练习时段内检索优于不间断连续练习。
[^ntu]: NTU Singapore《Science of Learning》：主动学习直接让学生参与学习过程而非被动接收信息，如 think-pair-share、同伴互教、问题式学习。
[^brain-friendly]: 中国教育新闻网《教学"脑友好"，学习更高效》：依据认知负荷理论，教学要把控好内在、外在、关联三类负荷；运用支架策略分解复杂任务、双重编码原理组织信息。
[^cnaes]: 中国教育科学研究院《人工智能时代的教育价值与功能省思》：反思能力要求个体对自身思维方式、认知过程及行为模式持续审视；元认知活动是防止认知卸载、避免思维退化的关键防线。
