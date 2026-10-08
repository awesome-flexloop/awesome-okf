# 变更日志（Log）

## 2026-08-28 - 初始版本

- ✅ 基于 **blog-article-to-okf-bundle** 方法论链路 **R→I→E→V** 生成
- ✅ 完成 R 阶段（事实采集）：从微信公众号"窥见比特"博文《字节把TRAE、扣子都并进豆包，图什么？》（作者"比特一哥"，2026-08-27，收录于"科技前沿"）采集 17 条事实（F-001 ~ F-017），事实基准为 `.trae/specs/bytedance-ai-consolidation-blog-okf-wiki/facts.md`（唯一合法事实集）
- ✅ 完成 V 阶段前置核验：8 项关键声明经 WebSearch 轻量核验（7 项通过，1 项年份错配），补充 4 条核验事实（F-018 ~ F-021），合计 21 条事实
- ✅ 完成 I 阶段（洞察提炼）：确定"整合时间线 → 成本驱动逻辑 → 竞争格局"的三篇 concepts 递进结构，不设 examples/（商业分析无可运行示例）
- ✅ 完成 E 阶段（信源先行成文）：references/（2篇 + index）→ concepts/（3篇 + index）→ 根 index → log

### 信源

- **主信源（博文）**：https://mp.weixin.qq.com/s/9D2R5MYbhLO8oYx5HSRvJg （微信公众号"窥见比特"，作者"比特一哥"，2026-08-27 09:11，收录于"科技前沿"，原创，作者标注"个人观点，仅供参考"）
- **核验信源**：
  - 36氪：https://36kr.com/p/3953230805876099 （TRAE/扣子并入豆包独家报道，2026-08-24）
  - 南华早报（SCMP）：2026 年 AI 基础设施预算 2000 亿元确认
  - 彭博社（Bloomberg）：2026-05-27 报道 700 亿美元讨论上限（区间 590-740 亿美元）
  - 金融时报（FT）：2025 年资本开支 1500 亿元总额确认
  - 第一财经、证券时报、China Daily、界面、财新：利润下滑报道与字节副总裁李亮回应
  - 21世纪经济报道、南方+：飞书整合与谢欣/谭待汇报线

### 文件清单（共 9 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | Bundle 根索引（性质声明、结构总览、分层导航、信任与生命周期、已知边界、toctree） |
| `concepts/index.md` | 概念文档子目录索引（学习路径 + toctree） |
| `concepts/00-consolidation-timeline.md` | 整合时间线与组织架构（7.30/8.17-21/8.24/8.25 四节点 + Mermaid 架构图 + 产品定位表） |
| `concepts/01-cost-driven-rationale.md` | 算力成本驱动的组织变革（赛马机制、人力vs算力成本、资本开支数据表含年份错配更正、利润影响与官方保留） |
| `concepts/02-competitive-landscape.md` | AI办公竞争格局（三方对标表、梁汝波战略、豆包能力拼图、TRAE保留、门票论） |
| `references/index.md` | 信源登记簿子目录索引（信源清单 + 事实编号段索引 + 可信度说明） |
| `references/article-source.md` | 博文信源事实清单（F-001~F-017 分客观事实/作者观点/外媒转述三类 + F-018~F-021 核验补充与勘误） |
| `references/verification.md` | 核验报告（8项逐项结论表 + 资本开支口径混杂详解 + 利润归因保留 + 权威来源URL汇总） |
| `log.md` | 本文件 |

### 质量门记录

- **事实溯源门**：所有具体数据/声明均带 F 编号引用，无 facts.md 之外编造的数字/人名/产品名；F-004/F-016 作者观点明确标注；F-007/F-009 外媒转述单独分类 — **通过**
- **年份错配处理门**：博文 850 亿元年份错配（F-018）已在 index.md 已知边界、concepts/01 资本开支表、references/article-source.md、references/verification.md 四处如实更正，不照搬博文错误 — **通过**
- **口径差异门**：彭博 700 亿美元（讨论上限）vs 南华早报 2000 亿元（确认目标）的口径差异（F-019）已明确标注"不可直接比较"；900/700 亿拆分标注为浙商证券估算 — **通过**
- **官方归因保留门**：利润暴跌 70%（F-009）同时呈现媒体口径与字节副总裁李亮的官方保留（F-020），未将"AI投入导致利润暴跌"作为确定因果链 — **通过**
- **交叉引用门**：全部使用相对路径，无 `file:///` 绝对路径；对同分组 trae-learning 的引用采用 `../trae-learning/index.md`；对 bundle 根引用采用 `../index.md` — **通过**
- **frontmatter 门**：bundle 根带 `okf_version: "0.2"` + 双信源 sources（博文 + 36氪）；子文档带 `type`/`title`/`description`/`sources`，格式参照 vision-model-selection bundle — **通过**
- **性质声明门**：index.md 顶部显著位置标注"商业分析/战略资讯类知识包，非源码教程"，已知边界四条（个人观点/资本开支口径混杂/利润归因保留/资讯时效性）齐全 — **通过**
- **toctree 门**：根 toctree 覆盖 concepts/index、references/index、log；concepts/index toctree 覆盖 3 篇概念文档；references/index toctree 覆盖 article-source、verification；父级 `ai/trae/index.md` toctree 已追加 bytedance-ai-consolidation/index，`bundles/index.md` 计数已更新（269→270）— **通过**

### 核验发现年份错配的处理说明

核验过程中发现博文 F-006 将"约 850 亿元专项 AI 芯片采购"归为 2026 年预算，但权威媒体报道显示 850 亿实为 **2025 年**芯片采购实际额，2026 年预计约 1000 亿元（约 140 亿美元）。处理方式：

1. 不修改 `.trae/specs/.../facts.md`（该文件忠实记录博文原文，博文错误以 F-018 勘误形式追加）；
2. 在 `references/article-source.md` 中 F-006 行内嵌标注"年份归属有误，见 F-018 勘误"，F-018 单列于"核验补充与勘误"节；
3. 在 `references/verification.md` 第 3 项详解三类口径问题，年份错配列为首条；
4. 在 `concepts/01-cost-driven-rationale.md` 资本开支数据表中采用更正后口径（850 亿归 2025 年、1000 亿归 2026 年预计），并以 ⚠️ 标注；
5. 在根 `index.md` 已知边界第 2 条明确告知读者该勘误；
6. 全 bundle 不出现"850 亿为 2026 年预算"的错误表述。

### 备注

- 本 bundle 为 `ai/trae/` 分组首个**资讯/战略背景类** bundle（该分组此前 bundle 均为源码教程），已在 frontmatter 与已知边界中明确非源码教程性质；trae/index.md 已新增"📰 战略资讯"板块予以归类；
- TRAE IDE/CLI 保留为豆包编程子产品（F-015）是归入 trae 分组的关键依据；
- 四视角对抗审查（事实/结构/读者/时效）发现并修复 1 处统计计数错误：references/article-source.md 事实分类统计表"客观事实"数量由 14 更正为 13（F-001~F-003=3 + F-005~F-006=2 + F-008=1 + F-010~F-015=6 + F-017=1 = 13），更正后 13+2+2+4=21 与总数一致；
- 已更新 `ai/trae/index.md`（total_bundles 12→13、total_content_docs 119→124、total_md_files 155→164、新增战略资讯板块与 toctree 条目）和 `bundles/index.md`（total_bundles 269→270、AI 域 96→97、TRAE 分组 12→13）。
