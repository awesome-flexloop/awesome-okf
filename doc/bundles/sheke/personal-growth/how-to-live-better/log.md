# 生成日志（log.md）

## 2026-09-28：初始生成（R→I→E→V）

- **生成方式**：七概念方法论编排场景 4（知识沉淀），链路 R→I→E + 强制 V；按 `blog-article-to-okf-wiki` 技能七阶段工作流执行，Spec Mode 五阶段管理（spec/tasks 位于主仓库 `.trae/specs/okf-wiki-ecosystem/how-to-live-better-okf-wiki/`）。
- **触发**：用户给入 4 个公开 URL（mushroom 博文、官方检索页、dlgrv 翻译快照、cdyforever 镜像）要求"全面学习并生成 okf wiki 教程"；R 阶段按信源先行原则上溯至共同原仓 eternity4719/HowToLiveBetter。
- **内容敏感度**：公开内容（公开博客 + GitHub Pages + 公开仓库），标准工作流。
- **骨架判定**：操作可复现性两问任一不满足 → 不设 examples/，使用动作入 concepts/05。
- **归属判定**：sheke/personal-growth（候选对照表见 spec；主线为跨域循证人生决策，禁止单主题新建分组）。

### R 阶段（事实采集与核验）

- 采集：原仓 README（GitHub 网页+API）、book/ 第 1/8/10/13/19 章 raw 原文、docs/ 目录 API 清单、skills/life-decision-guide/README.md；4 个用户信源全文；GitHub API 仓库元数据（2026-09-28 实测）。
- 事实登记：**F-001~F-088 共 88 条**（元信息 15 + 版本计数 9 + 机制规则 18 + 精选条目 27 + 核验补充 17 + R1 修复补登 2），spec facts.md 与本包 references/article-source.md 双份登记。
- P0 核验：2 个独立上下文子代理执行 **19 项**（医学/安全 10 + 法规/社科 9）。
  - ✅ 通过 14 项；⚠️ 采用核验口径 5 项：F-072（溶栓 9 项 RCT 非 16）、F-073（20.3%/1.2% 为 BASIC-OHCA 全队列口径）、F-074（中国道路死亡 248,099 出自 WHO GSRRS 2023 模型估计，非 fact sheet）、F-076（燃气指定产品禁令为条例第 18 条第 6 项）、F-078（逃逸全责出自道交法实施条例第 92 条）。
  - ❌ 核心声明失败 0 项；10 项医学研究 DOI 全部可解析、效应值逐字吻合。
  - 版本差（498→608→615）单列为版本演进对照，不计勘误。

### I/E 阶段（知识拆分与成文）

- 三层拆分：事实/机制层（00–02）→ 导航/应用层（03–04）→ 使用/迁移层（05–06）。
- 信源先行：先写 references/ 两篇，再写 concepts/ 七篇，各级 index 最后写。
- 精选 21 条（四大板块 14+3+2+2），每条六要素齐备、挂 F 编号、标注原书"第 N 章第 M 条"定位。
- Mermaid 图 1 张（03 篇四大板块全景，节点文本引号包裹、无裸特殊字符）。

### V 阶段（对抗审查与机械门禁）

- 四视角自审：事实溯源 / 结构规范 / 读者可用 / 时效边界。
- 八项机械门禁：见本文件末尾"机械门禁记录"（Task 7 完成后回填）。
- 独立评审：Spec Mode Review 阶段由 fresh-context 子代理执行，结论见 spec `review.md`。

### C 阶段（交付）

- 用户决策：**仅落盘，不执行 git commit/push**。
- 新增文件（13）：
  - `how-to-live-better/index.md`、`log.md`
  - `how-to-live-better/concepts/`：index.md + 00~06 共 8 个
  - `how-to-live-better/references/`：index.md、article-source.md、verification.md 共 3 个
- 修改文件（3，三级索引接入）：
  - `sheke/personal-growth/index.md`（2→3 束）
  - `sheke/index.md`（45→46 束）
  - `bundles/index.md`（574→575 束）

---

## 机械门禁记录

**官方 gates（可用，已实际运行，非手动等效替代）**：在子模块根目录以 py314 环境执行 `python -m invoke gates.all`（2026-09-28）：

- ✅ `gates.utf8`：**10,668 个文件均为有效 UTF-8**（脚本内置 bad-utf8 自检探针同时验证了拦截能力）；
- ✅ `gates.toctrees`：**全部 index.md 引用有效，所有内容文档均可达**（pass/broken/orphan/missingidx/consistency/missingbundle 自检探针全部正确）；
- ✅ `gates.bundles`：**9 域 / 59 组 / 575 束，frontmatter、计数行、节标题、分组表、toctree 五面一致**（脚本内置 7 类计数漂移自检探针全部正确拦截）。

**技能§7 手动八项清单（官方 gates 之外逐项留痕，py314 脚本实测）**：

| # | 项 | 结果 |
|---|---|---|
| 1 | UTF-8 strict roundtrip（13 个 bundle 文件 + 3 个改动索引 + spec facts.md） | ✅ 全部严格解码通过 |
| 2 | 双份 F 编号：facts.md 与 article-source.md 表行编号集合 | ✅ R1 后均 88 条（F-001~F-088），集合相等、连续无跳号 |
| 3 | 三级 toctree：根 3 条 + concepts 7 条 + references 2 条 + 组索引新增行 | ✅ 12 个 bundle 内目标 + 组索引 how-to-live-better/index 全部 Test-Path 为真 |
| 4 | 相对链接全可达 / 零 file:/// | ✅ 断链 0；file:/// 出现 0 次 |
| 5 | 三级计数同步 | ✅ personal-growth 实际目录 3 = toctree 3 = total_bundles 3；sheke 组表行求和 8+7+3+2+2+3+21=46 = 域节标题 = mermaid 节点；九域标题/mermaid 双路求和均=575=frontmatter total |
| 6 | 敏感信息零残留（Windows/Unix/macOS 用户目录绝对路径、.temp 引用；以描述性措辞执行扫描，避免字面枚举） | ✅ 真实家目录路径 0 命中 |
| 7 | 根 frontmatter 十要素 + sources | ✅ 齐备，sources 14 条（4 用户 URL + 原仓 + API + 8 权威核验源） |
| 8 | 勘误在正文落实 | ✅ 5 处核验口径（9 项 RCT / 全队列 20.3%·1.2% / GSRRS 2023 模型估计 / 燃气第 18 条第 6 项 / 实施条例第 92 条）+ 蘑菇 34 种口径精化均在 concepts 01/04 与 index 提示块呈现 |

**四视角自审**：

1. **事实溯源**：concepts 全部具体数字（RR/OR/百分比/金额/条号/日期/星数）均可回溯 F 行；06 篇方法迁移的盘问示范未引入任何新事实数字。
2. **结构规范**：根/子目录三层 toctree 齐备；无 examples/ 与两问判定一致；文件命名 kebab-case；frontmatter 裸日期格式。
3. **读者可用**：13 个文件相对链接全部可达；学习路径"事实→机制→导航→应用→使用→迁移"闭合；每个易过时数字带时点；每个镜像带滞后声明。
4. **时效边界**：非医疗/法律建议、地域法域、金额时点、C 级/TODO、抽样核验范围、Unlicense/CC BY 署名六条边界在 index 与 06 篇双重声明。
   - 自审发现并已修复：无（上述要素在成文时即按清单写入；唯一检查词形差异"第九十二条/第 92 条"经 Grep 确认正文与核验报告一致，非遗漏）。

### Review R1 与整改（2026-09-28）

- fresh-context 独立评审结论 **fail**：全部规则项与 rubric（U1=5/U2=4）通过，1 条 actionable（02 篇"97.2%"集外数字）+ 5 条 advisory。
- 整改（Issue I-1，已完成并经 R2 复核）：
  - F1：双份补登 F-087（带状疱疹疫苗 97.2% 标注为原书 README 举例、未独立核验），02 篇挂编号并加非建议提示；
  - F2：双份补登 F-088（12308/12356/12355 热线出自 README 章细目），03 篇两处挂编号；
  - F3：根 index/04/06 三处"三周内 498→615"压缩表述改为三时点精确写法（9-07 上线 / 9-17 快照 498 / 9-28 现行 615）；
  - F4：顺手修正 sheke/index.md relationships 行历史残留计数（6 束→7 束，物理目录与总索引均为 7）；
  - F5：本表第 6 项改为描述性措辞，消除朴素路径扫描噪音；
  - F6：facts.md F-049 补论文精确样本 1,738,886（article-source 保留 173.9 万约数、精确值见 verification）、F-067 定位改第 4–6 条、F-046 补"软管几十元"成本，双份口径对齐；
  - 联动更新：双份编号 86→88（根 index、组索引、references/index、本日志）。
- 防回归：整改后重跑 `invoke gates.all` 与八项手动脚本，仍全绿。

### R3：本地原始文档源复核（2026-09-28，用户指认本地完整克隆）

- 触发：用户指认真正的原始文档源为转化工作区本地完整克隆 `playground/books/tests/HowToLiveBetter`（commit **bad9e99**，2026-09-28 17:46，含 .git/book 33 章/docs 5 长文+核实记录 80+ 份/skills/tools）。R 阶段从"抽样 web 抓取 5 章"升级为"全书 33 章本地逐章核对"。
- 新增事实 F-089（双份）：33 章 `### N.` 条目数机器统计（36/42/25/18/39/26/21/43/23/18/17/23/41/9/8/9/8/6/17/12/11/11/23/12/10/11/16/8/13/13/16/10/20），**求和精确 615**；README 全部计数本地逐字一致；21 条精选 29 个关键 token **29/29 命中**；本地清点 docs/核实记录 80+ 份工件。
- **重要更正（F-078 重新定性）**：本地全文证实原书第 8 章第 1 条来源行**本就正确并列引用**《道路交通安全法实施条例》第 86/92 条——不是原书错误，而是本包 R 阶段 F-063 初稿凭 WebFetch 截断预览误归；已在 facts/article-source/verification/04 篇/index 同步诚实更正。法律核验结论（全责在 92 条）本身成立。
- 本地定谳维持：F-072（原书 16 项→论文 9 项）、F-073（20.3%/1.2% 全队列表述）、F-076（第 20 条→第 18 条第 6 项）三处确为原书问题；F-074/F-075 维持口径/出处精化。
- 读者可见更新：03 篇补逐章条目数表（F-089）、00 篇补"615 机器可数"、verification 新增"六、本地完整克隆全书结构审计"节、index 核验提示块改写；计数 88→89 全量同步。
- 门禁：R3 后复跑 gates.all 与 F 双份集合，仍全绿（见下行终检）。
