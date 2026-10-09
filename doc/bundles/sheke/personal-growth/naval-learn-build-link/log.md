# 变更日志（Log）

## 2026-10-08 - 初始版本

- ✅ 基于 **blog-article-to-okf-bundle** 方法论链路 **R→I→E→V** 生成（seven-concepts-cmd 场景 4 知识沉淀，session sc-20261008-wechat-okf-wiki）
- ✅ R 阶段（事实采集）：browser_use 打开微信文章（无验证码/付费墙，判定公开内容），提取 `#js_content` 全文约 1088 字逐字原文；采集博文事实 18 条（F-001 ~ F-018），事实基准为 `.trae/specs/okf-wiki-ecosystem/naval-learn-build-link-blog-okf-wiki/facts.md`（唯一合法事实集）
- ✅ R 阶段 P0 权威核验：WebSearch 多信源交叉，补充 9 条（F-019 ~ F-027），7 项关键声明 3 ✅ / 3 ❌ / 1 ⚠️；标题级框架"学造连"无 Naval 原始出处且遗漏杠杆/股权，整包判 **flagged**
- ✅ I 阶段：操作可复现性两问皆否 → 不设 examples/；归属 `sheke/personal-growth/`（排除 finance：无投资实操；排除 methodology：非方法论工具）
- ✅ E 阶段（信源先行成文）：references/（2 篇 + index）→ concepts/（3 篇 + index）→ 根 index → log

### 信源

- **主信源（博文）**：https://mp.weixin.qq.com/s/PuC1WJL0rc98a3EbnZj37w （微信公众号"洋洋读书成长记"，无独立作者署名，2026-10-02 11:15 湖北，约 1088 字，3 张配图无图注，全文无引用链接）
- **核验信源**：
  - sloww.co：https://sloww.co/how-to-get-rich-naval-ravikant/ （2018 tweetstorm 逐字，F-020/F-022/F-025）
  - podcastnotes.org：Naval 播客访谈要点（F-020/F-023）
  - studiolayerone.com：Specific Knowledge 专题（F-020/F-025）
  - kids.kiddle.co：https://kids.kiddle.co/Naval_Ravikant （生平，F-019）
  - usethebitcoin.com：生平交叉佐证（F-019）
  - navalmanack.com：《The Almanack of Naval Ravikant》Eric Jorgenson 编 2020，CC BY-NC（F-024/F-026）

### 文件清单（共 9 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | Bundle 根索引（okf_version + flagged 性质声明、结构总览、分层导航、主题关联、信任与生命周期、已知边界 5 条、toctree） |
| `concepts/index.md` | 概念文档子目录索引（学习路径 + toctree） |
| `concepts/00-naval-and-source-framework.md` | Naval 其人 + 原始财富公式（三支柱/四类杠杆/股权/build and sell/复利尺度 + Mermaid 框架图） |
| `concepts/01-learn-build-link-audit.md` | 学造连逐项对勘（七行对照表、剂量/截断/错位三处问题、数字勘误、校正行动映射） |
| `concepts/02-reading-secondhand-wealth.md` | 可信边界（事实/观点/话术三层、三陷阱、五条阅读纪律、与 pipeline-story 互链） |
| `references/index.md` | 信源登记簿子目录索引（信源清单 + F 编号段索引 + 可信度说明） |
| `references/article-source.md` | 博文事实 F-001~F-018 + 核验补充 F-019~F-027 双份登记与分类统计 |
| `references/verification.md` | flagged 明示 + 7 项逐项核验表 + Mermaid 双框架对勘图 + 失实危害分级 + 权威 URL |
| `log.md` | 本文件 |

### 质量门记录

V 阶段四视角自查（事实 / 结构 / 读者 / 时效）+ 仓库 gates 脚本执行结果如下：

| 质量门 | 检查内容 | 结果 |
|-------|---------|------|
| 事实溯源门 | spec `facts.md` 与 `references/article-source.md` 的 F 编号集合正则比对，双份均为 F-001~F-027 连续 27 条，无缺号/重号/孤儿编号 | ✅ 通过 |
| flagged 处理门 | 核心框架核验失败已按方法论处理：博文事实不改写（F-001~F-018 忠于原文），失败项以 F-019~F-027 勘误追加；根 index 与 verification.md 顶部双 flagged 声明块；正文呈现正确值并标注博文口径 | ✅ 通过 |
| 交叉引用门 | 跨包链接 `finance/pipeline-story` 物理 Test-Path 双向层级可达（根 index 两级 `../../`、concepts/02 三级 `../../../`）；无 `file:///` 绝对链接（出现 0 次）；互链依据属实（pipeline-story facts F-040 列《纳瓦尔宝典》） | ✅ 通过 |
| frontmatter 门 | 9 文件均含规范 YAML frontmatter（okf_version "0.2"、type、status: flagged、stale_after 2026-12-31、时间戳统一 2026-10-08T15:30:00+08:00）；source 溯源字段齐备 | ✅ 通过 |
| 性质声明门 | 单源二手博文、无独立作者署名、3 图无图注、全文零引用链接等局限已在根 index「已知边界」5 条与 verification.md 明示；不设 examples/（操作可复现性两问皆否） | ✅ 通过 |
| toctree 门 | 三级 toctree 全部 `:hidden:` `:maxdepth: 7`，条目为 stem；gates `check-toctrees.py` 全库校验通过 | ✅ 通过 |
| UTF-8 门 | gates `check-utf8.py`：10990 个文件均为有效 UTF-8 | ✅ 通过 |
| 总索引计数门 | gates `check-bundles-index.py`：9 域 / 61 组 / 592 束，frontmatter、计数行、节标题、分组表、toctree 五面一致 | ✅ 通过 |

**计数变更（本包接入）**：total_bundles 591→592；sheke 域 57→58；personal-growth 组 9→10（域束数加总 3+49+7+17+2+10+58+9+437=592 自洽；groups 61 / domains 9 不变）。

**gates 执行方式备注**：`invoke gates.*` 在本机不可用（`invoke.exe` 不在 PATH，且 tasks 依赖未安装的 `invocations` 包），改为在 `projects/awesome-okf-xs/` 下以 `PYTHONDONTWRITEBYTECODE=1` 直接执行 gates 封装的三个脚本（`scripts/check-utf8.py`、`scripts/check-toctrees.py`、`scripts/check-bundles-index.py`），退出码均为 0，与 invoke 门禁等效。

**并行会话竞态处置**：V 阶段执行期间，另一并行会话在 `sheke/relationships/` 新增 `wechat-probability-mindset-dating` 包并整体重写了共享文件 `bundles/index.md`、`sheke/index.md`，一度覆盖本包的计数编辑（计数退回 591/sheke57）。处置原则为不破坏并行包内容，在其版本（已含 dating 包、基线 591/57）基础上叠加本包 naval 增量至 592/58，relationships 行保持其声明的 9 束不动，重跑 `check-bundles-index.py` 至五面一致通过。

### flagged 判定与处理说明

博文标题即框架主张（"发财就是每天循环干这3件事……学、造、连"），该框架核验失败（F-020/F-021），按 blog-article-to-okf-bundle 方法论"核心声明失败 → 整包 flagged"规则处理：

1. 不修改 spec `facts.md` 中博文事实（F-001~F-018 忠于原文），失败项以 F-019~F-027 勘误追加；
2. 根 index 顶部 flagged 性质声明块明示三条失败项与正确框架；
3. verification.md 顶部 flagged 明示块说明影响范围与"不得当作 Naval 本人观点引用"；
4. concepts 正文呈现**正确值**（三支柱、1–2 小时、10–20 年）并在旁标注博文口径；
5. stale_after 设 2026-12-31，到期前复核。
