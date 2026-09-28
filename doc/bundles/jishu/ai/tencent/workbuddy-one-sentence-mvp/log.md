# Log：WorkBuddy 一句话做 MVP

## 2026-09-28

- 建立 `workbuddy-one-sentence-mvp` 知识包（归属 `jishu/ai/tencent/`：主线实体为腾讯 WorkBuddy，同组已有 tencent-buddy-family、workbuddy-sandbox-public-endpoint、codebuddy 等 7 束同主体先例）。
- 敏感度预检：微信公众号公开文章（无 token/code 访问控制参数）→ 公开内容，标准工作流；spec 落 `.trae/specs/okf-wiki-ecosystem/workbuddy-one-sentence-blog-okf-wiki/`。
- 信源距离预判：厂商自宣相邻——第三方产品经理媒体（网易号同步源「人人都是产品经理社区」）发布的腾讯 WorkBuddy 正面实测软文，与 2026-09-24 小程序发布能力官宣同日，文末含导流 CTA（F-022）。
- R 阶段：WebFetch 成功提取微信全文（browser_use 因子代理环境 Chrome 扩展未连接失败，按回退序直接 WebFetch 命中）；登记 F-001~F-022 博文事实，客观叙述/作者观点/营销 CTA 三层标注。
- P0/P1 核验 8 项（WebSearch 多源交叉）：沙利文报告双榜第一（央广网/21 世纪经济报道/雷锋网，报告日期补全 2026-09-20）、腾讯产品身份（腾讯云/官网）、小程序发布能力（IT 之家/Tech 星球：2026-09-24、5.6.1+、14 天试用版不可转正式版、微信第三方服务商、一期 9-17 网页应用）、专家团（官网 100+ 专家旁证，团名博文口径）、AICPB 月活（科技日报 2026-08-18）、Omdia/IDC 转述级背书；补充 F-023~F-032。
- 核验结论：**6✅ / 2⚠️ / 0❌，源文零硬错误**；两个 ⚠️ 为「腾讯问卷」连接器单源（F-031）与微信原文账号/精确发布时间缺口（F-032，经网易号 2026-09-24 17:17 同步页确认标题与时间）。
- I 阶段：操作可复现性两问皆否（无版本/输入输出/可照做步骤，步骤以截图承载）→ 不设 `examples/`，商业/产品体验资讯骨架；三层知识地图：事件背景（00）、五阶段实测（01）、能力判读与软文读法（02）。
- E 阶段：信源先行生成 9 文件——references/ 2 篇 + index、concepts/ 3 篇 + index、根 index.md、log.md；全部文件带 okf_version 0.2 frontmatter、generated/verified 双信源、status stable、stale_after 2026-12-31。
- 四视角自审（事实溯源/结构规范/读者可用/时效边界）：F 编号引用逐篇核对（00 用 F-001/002/023~028/032，01 用 F-004~020/029~031，02 用 F-002/003/021/024~029）；作者观点 5 条全部保留性质标注；两个单源项在概念正文与根索引已知边界双处落实；mermaid 节点全部引号包裹。
- 机械门禁（本束专项，全部通过）：12 个新文件 UTF-8 strict roundtrip 0 失败；F 编号双份集合比对 facts.md ↔ article-source.md 均为 32 条且集合相等、无跳号；本束 3 个 toctree 共 8 个条目逐一 Test-Path 存在；束内 28 条相对链接全部可达（初稿 concepts/ 互链同级束少一级 `../`，4 处已修为 `../../`）；零 `file:///`、零敏感绝对路径；7 个内容文件 frontmatter 完整。
- 父级索引：tencent/index.md 加导航行/toctree/相关链接，束数 7→8、信源 29→31、事实 470→502；概念数按磁盘真值校正为 45（原索引 41 有 +1 历史漂移：workbuddy-sandbox 横向对标增强时新增的 concepts/03 未计入，本次一并补登，sandbox 导航行 3→4 概念）；bundles/index.md total 572→573、jishu 432→433、ai 212→213（frontmatter/粗体行/mermaid/节标题/分组表五处）。
- 全库门禁（直接运行底层脚本，`invoke gates.*` 在 Anaconda 环境因 `invocations` 元数据缺失不可导入，同组 sandbox 束 2026-09-16 同样处置，未声称 invoke 通过）：
  - `python scripts/check-utf8.py` ✅ 10657 个文件全部有效 UTF-8；
  - `python scripts/check-toctrees.py` ⚠️ 失败 10 处，**全部指向另一会话未跟踪、未接入父级索引的 `jishu/ai/tencent/lightvela-personal-agent/` 束**（其 9 文件自成体系但未登记进 tencent/index.md 与 bundles 计数），失败清单不含本束任何路径；
  - `python scripts/check-bundles-index.py` ⚠️ 失败 3 处（total/jishu 节标题/分组表和各 +1），同一根因：目录树地面真值 574 = 已登记 572 + 本束 + lightvela；本束提交不包含、不代接 lightvela（非本任务产物），其会话完成接入后总计数应收敛为 574/434/214、tencent 9 束。
