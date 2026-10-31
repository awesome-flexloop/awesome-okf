# log.md — 变更日志

## 2026-10-31：初始创建

- **阶段**：R→I→E→V 七阶段完整执行
- **内容敏感度预检**：公开内容（无 `share?code=`/`token=`/邀请码等访问控制参数）→ 标准工作流
- **事实采集**：57 条 F 编号（F-001 至 F-057，博文 45 条 + 官方核验补充 12 条）
- **P0 核验**：22 项 P0，核心声明（仓库身份 / 42 notebook / 21 脚本 / 无 requirements.txt / License 非商用）✅ 确证，⚠️ 6 项口径/时效差异，❌ 0 项
- **勘误**：5 则，均为**口径/时点差异**而非源文硬错误——Star 增长（30,003→30,149）、七段归并篇数之和 35 与 42 个 `.ipynb` 的口径张力、CI 工作流时效（`github-test.yml` 博文时点存在、核验当日已移出）、配套书「400 页/Amazon 畅销书」为作者自述（第三方书目站记 250/427 页）、License 关键条款逐字命中且 GitHub API 标注 NOASSERTION
- **Bundle 结构**：concepts/（3 篇）+ references/（2 篇）+ index.md + log.md
- **examples/**：未设立——操作可复现性两问均「否」（仓库无 `requirements.txt`，博文安装流程仅 `git clone` + `cd` 且明言「没有然后了」，主体为 42 篇 notebook 的分类盘点，非逐步可复现的搭建教程）
- **归属**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/learning/rag-techniques/`
- **信源**：微信公众号博文（架构文摘，作者「小七」，2026-10-27）+ GitHub 仓库 `NirDiamant/RAG_Techniques` + GitHub API / README / 第三方书目站权威核验

## V 阶段对抗审查与机械门禁

### 机械门禁结果

| 检查项 | 结果 |
|--------|------|
| UTF-8 roundtrip（9 文件） | ✅ 全部 OK，无 BOM，无 file 协议绝对路径残留 |
| F 编号双份一致性 | ✅ spec `facts.md` 57 项 = bundle `article-source.md` 57 项，集合相等（F-001~F-057 连续无跳号） |
| 相对链接完整性 | ✅ 20 条相对链接，0 broken（自写解析器校验，按 `#` 截断锚点后做存在性判断） |
| 敏感路径扫描 | ✅ 0 命中（Windows 盘符、AppData/Temp、`share?code=`/`token=`/邀请码、绝对路径协议 均无） |
| 总索引五面对账 | ✅ `check-bundles-index.py` 输出「9 域 / 64 组 / 697 束，frontmatter、计数行、节标题、分组表、toctree 五面一致」（exit 0） |

> **门禁口径说明**：`invocations` 包缺 dist-info 元数据，`invoke gates.*` 不可用，故未执行 `invoke gates.*`；改以 `.agents/scripts/check-bundles-index.py` 直跑 + 自写等效检查（F 编号一致性 / UTF-8 roundtrip / 相对链接 / 敏感路径）替代。仓内亦**不存在** toctree 专项校验脚本（`bundle-project.ps1` 为打包用、`verify_md_links.py` 硬编码指向 `bundles/chaos`），toctree 合规性以自写相对链接与结构检查覆盖。

### 对抗审查结论

- **源文可信度**：第三方资讯类博文（架构文摘转述），主线实体为 GitHub 仓库 `NirDiamant/RAG_Techniques`；项目身份、Star、notebook 数经 GitHub 实测核验，作者机制解说（Graph RAG / LightRAG）标注为「作者解读」而非仓库官方文档口径
- **数据时效**：Star 数、CI 工作流清单持续变化，`stale_after` 设为 2027-04-30，index.md 顶部「数据来源说明」显式提示博文发布口径 30,003
- **口径张力留痕**：不静默照搬博文——「42 个 notebook」与七段篇数之和 35 的差异在 index.md 与 00-intro.md 双处显式说明（七段为按 pipeline 阶段的归并视图，`.ipynb` 实测 42 个；README 自身亦有口径张力）
- **合规红线**：License 为 Custom License Agreement（非商用，含 `exclusive, perpetual, irrevocable, worldwide, royalty-free license` 授权条款），已在 02-practice.md 设专节说明并给出用途可行性表
- **cross-reference 有效性**：三个兄弟 bundle 链接（qbs-book-to-skill / mattpocock-skills / free-llm-api-roundup）均已确认可达
