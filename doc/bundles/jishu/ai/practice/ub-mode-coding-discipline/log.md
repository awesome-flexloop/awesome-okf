# 变更日志（Log）

## 2026-11-04 · 初始创建

- 经 wechat-public-okf + seven-concepts（场景 4 知识沉淀：R→I→E→V→C）转化公众号「开源日记」2026-10-28《只有一个 Skill 的仓库，竟然斩获 2900 Star！》（署名作者「熊叔」）博文；
- 一级信源：公众号博文；二级权威信源：GitHub 官方仓库 `unclebob/ub-mode`（`README.md` / `SKILL.md` / `LICENSE`，`master` 分支）+ GitHub REST API 元数据（采集于 2026-11-04）；
- 登记 F-001–F-037 共 37 条事实（[references/article-source.md](references/article-source.md)）；
- 完成 13 项 P0 核验：**7 ✅ / 6 ⚠️ / 0 ❌**，登记勘误 E-1–E-4 与补充事实三项（[references/verification.md](references/verification.md)）；
- **勘误摘要**：
  - E-1（口径）：博文「两个文件 6KB」→ 实为 3 个文件（含 LICENSE）≈7.2 KB；
  - E-2（漏提）：检查工具 3 → 4 个（补 `uml-viewer`）；
  - E-3（时效）：Star 2,900（发文）→ 3,951（核验）；
  - E-4（单源）：三条检查命令与 `.metrics` 产物无官方文档对拍；
- **骨架判定**：按「操作可复现性两问」判定为**概念骨架**（Q1 是 / Q2 否——检查工具需单独安装而博文未给方式，照做链路断裂），故**不设 `examples/`**，采用 `index + concepts/5 篇 + references/2 篇 + log` 结构；
- **归属判定**：落位 `jishu/ai/practice/`（AI 工程方法论与博文核验转化束），依据「文章主线实体优先」+ 组内同型非例（`answer-me-with-html`、`docx-report-skill`、`planning-with-files`）；排除 `products/`（其 Skill 束均产出终端交付物）与 `frameworks/`、`ecosystems/`、`models/`；
- 状态：`status: draft`（未真机复测、未运行 CI 门禁），待独立审查后转 stable；
- 机械门禁说明：本次执行 V 阶段手动等效验证（UTF-8、双份 F 编号一致性、三级 toctree 完整性、相对链接可达性、四处计数同步）；**未运行 `invoke gates.*`（环境未安装 `.[doc]` 依赖）时不声称 gates 通过**。

## 2026-11-04 · V 阶段对抗审查与机械门禁

### 四视角对抗审查（结论：无 P0/P1；P2/P3 项均「记录接受」或「已内建处置」，不阻塞通过）

| 视角 | 攻击点 | 结论与处置 |
|------|--------|-----------|
| 魔鬼代言人 | ① `01` 的「24 组原则」是派生数字（8 组 + Architecture 5 条 + 7 条 + 4 条），官方与博文**均未直接声明 24**，且「组/条」单位混用；② 骨架判定是否过于保守（是否该设 `examples/`）；③ E-3「Star 不是错误」是否为博文开脱 | ① 属可验算派生，`01` 已逐节拆解明细，读者可自行相加——**记录为 P3 表述**（不上调为结论性数字）；② Q2 不满足（官方未给工具安装方式，照做链路仍断裂），判定**维持**；③ 博文 2900 为发文时点事实、核验 3,951 为增长，**维持「时效非错误」** |
| 新人 | ① 读者拿到 ub-mode 后「四个工具怎么装」无从下手；② Dryer 阈值方向（≥0.8 是合格线还是告警线）是否会被误读 | ① 本包已明确「工具需单独安装且博文未给方式」，**避免误导**；② `02` 已写「消除相似度 ≥ 0.8 的重复代码」，**方向明确**；③ 阅读路径 index → ideas 00→04 线性可达 |
| 老板 | 一个 3 文件仓库配 11 文件知识包是否过度工程 | **辩护成立**：OKF 骨架为标准化最小结构（index + concepts/ + references/ + log 三层索引不可再删）；增量价值明确（补齐第 4 个工具 `uml-viewer`、登记 E-1~E-4 四项勘误、Star 双时点）。**无进一步精简空间** |
| 未来 | ① 仓库无 Release/tag，`SKILL.md` 若被改动，24 条原则名可能**静默失效**；② 博文 URL 受反爬（二次抓取已被拦截），原文可能不可再取 | ① 已用 `stale_after: 2027-01-31` 覆盖，再核验触发条件：`SKILL.md` 内容变更、`master` 分支文件树变化；② 事实已固化在 [references/article-source.md](references/article-source.md) 的 F 编号登记中，**不依赖原文可再抓取** |

### 机械门禁实测记录

- **相对链接可达性**：主仓 `check-links.py` 因 `EXCLUDED_DIRS` 含 `projects` 且本路径位于 `projects/awesome-okf-xs` 子模块内，**扫描为 0 文件（结构性不覆盖子模块）**；改用子模块等价检查器 `.agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py`，首轮 **11 文件 / 61 链接 / 2 broken** → 修复后 **11 文件 / 60 链接 / 0 broken（退出码 0）**；
- **首轮 2 项 broken 的处置**：
  - `index.md` 的 `../references/verification.md` 为**真实断链**（根 `index.md` 应为 `references/verification.md`）→ **已修正**；
  - `concepts/00-*.md` 的脚注定义 `[^ref]:` 被检查器误判为「引用式定义目标不存在」→ 经核验，先例 `live-transcription-agent` 同型命中，属**检查器对脚注的已知误报**；本次改为行内引用，消除误报；
- **UTF-8**：11 文件全部合法 UTF-8、无 BOM（自写脚本逐文件校验）；
- **双份 F 编号一致性**：spec `facts.md` ↔ `references/article-source.md` 逐条比对，唯一差异 F-004（spec 侧多「GitHub user id 36901」）→ **已回填 bundle 侧**，现 F-001~F-037 完全一致；
- **未运行项**：`invoke gates.*`（`toctrees`/`bundles`/`utf8`/`assetbaseline`/`redline`）因环境未安装 `.[doc]` 依赖未执行，**不声称通过**。
