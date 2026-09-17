# 变更日志（Log）

## 2026-09-16 - 初始版本

- ✅ 基于 **blog-article-to-okf-bundle** 方法论链路 **R→I→E→V** 生成（Skill: blog-article-to-okf-wiki，L2 模式 blog-article-to-okf-bundle，validation_count=13 后第 14 篇）
- ✅ 阶段 0 敏感度预检：微信公开博文 URL（无 token/邀请码参数）→ 公开内容 → 标准工作流（spec 在主仓库 `.trae/specs/okf-wiki-ecosystem/sell-before-build-blog-okf-wiki/`，产出在子模块 doc/bundles/）
- ✅ R-1 信源获取：mp.weixin.qq.com 反爬确定，直接 browser_use 取 `#js_content` innerText（2621 字，节点长度校验通过），时间戳 ct=1789014791 与页面时间交叉验证
- ✅ R-2 事实采集与核验：采集博文事实 29 条（F-001~F-029，分博文陈述/作者观点/元信息三类）；信源距离预判为"个人自媒体观点文+引流钩子"；6 项 P0 经 WebSearch 核验，补充事实 7 条（F-030~F-036），合计 36 条
- ✅ I 阶段：操作可复现性两问第②问为否（无作者实测、无输入输出样例、平台动作强时效）→ **不设 examples/**；归属 `sheke/marketing/`（主线为需求验证/营销顺序方法论，候选对照表见 spec）；三层拆分：论点→证据核验→落地与边界
- ✅ E 阶段（信源先行成文）：references/（2 篇 + index）→ concepts/（3 篇 + index）→ 根 index → 本 log

### 信源

- **主信源（博文）**：https://mp.weixin.qq.com/s/f6xHxUiHVgpIbifKSOQ3FQ （微信公众号"黄唯起"，署名"财富解密"，2026-09-10 12:33，广西，原创，页面标注"标题已修改"）
- **核验信源**：
  - HBS 官方新闻稿（2021-03-01）：https://www.hbs.edu/news/releases/Pages/spring-2021-executive-fellows.aspx （"Lecturer Lou Shipley"头衔原始出处）
  - AWS 官方：https://aws.amazon.com/executive-insights/content/product-management-at-amazon/ （Working Backwards/PR FAQ 与领导力准则英文原句）
  - 《Working Backwards》官方书站：https://workingbackwards.com/concepts/working-backwards-pr-faq-process/
  - Nira Dropbox 公司史：https://nira.com/dropbox-history/ （大巴原型、Digg 发布、75,000/24h）
  - 芒格 1986-06-13 Harvard School 演讲：https://jameslau88com.wordpress.com/2020/05/12/charlie-munger-on-invert-always-invert/
  - Lou Shipley 播客 #1395（2025-12）：https://index.fame.so/show/the-account-experience-podcast
  - Ash Maurya sell-before-you-build playbook（2026-07）：https://leanspark.ai/playbooks/how-to-sell-before-you-build
  - 歌德句反面证据（仅证中文网络流传）：https://www.meipian.cn/5oeeo5a4

### 核验结论（6 项 P0，勘误四清单）

| 项 | 结论 |
|---|---|
| 芒格引雅各比"反过来想"（F-006/F-032） | ✅ 属实，归属正确（Jacobi 德语 "man muss immer umkehren"，1986 Harvard School 演讲） |
| Lou Shipley 观点（F-008/F-031） | ✅ 观点属实（2025《Unlikely Entrepreneurs》、播客原话）；⚠️ 头衔勘误：官方为 Lecturer（讲师），非"高级讲师" |
| Dropbox 5,000→75,000 一夜（F-012/F-030） | ✅ 数字多源属实（Eric Ries/TechCrunch 转述、Nira）；补充：团队原期望 15,000、2008 年、Digg/HN 渠道、视频约 3 分 41 秒 |
| Dropbox"没写一行代码/产品不存在"（F-011/F-030） | ⚠️ 夸张失实：视频前已有粗略可运行原型、产品在 private beta 开发中，正文改为"完整产品开发前低成本验证" |
| 亚马逊 PR/FAQ 机制（F-015/F-033） | ✅ 属实（AWS 官方白皮书 + 《Working Backwards》2020） |
| 亚马逊"18 个月迭代文档"（F-016/F-033） | ❌ 所有权威来源均无此数字，不予采信 |
| 贝佐斯中文引语（F-017/F-033） | ⚠️ 领导力准则"start with the customer and work backwards"之意译，非逐字引语，正文去引号改转述 |
| 歌德句（F-027/F-034） | ⚠️ 出处不可考、疑似中文网络伪托，不作为歌德言论采信 |
| 标题"一天"vs 正文"一周"（F-029） | 页面自证口径差异（标注"标题已修改"），作标题党记录 |

状态判定：❌/⚠️ 项均为非核心细节，核心论点有精益创业/逆向思维多源谱系支撑 → **status: stable（不触发 flagged）**，勘误在正文完整落实。

### 文件清单（bundle 共 9 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | 根索引（性质声明、勘误提示、结构总览、分层导航、信任与生命周期、5 条已知边界、toctree） |
| `concepts/index.md` | 概念子目录索引（学习路径 + toctree） |
| `concepts/00-sell-before-build-thesis.md` | 核心论点：两种顺序对照+Mermaid、芒格/雅各比核验、Lou Shipley 观点与头衔勘误、需求发现论、可采信边界分层表 |
| `concepts/01-evidence-and-case-studies.md` | 证据核验：Dropbox 核验版时间线与"零代码"勘误、亚马逊 PR/FAQ 与两处勘误、共同结构 Mermaid 图 |
| `concepts/02-one-week-validation-playbook.md` | 7 天方案表、方法论谱系对照（精益创业/YC/Buchheit/Ash Maurya）、批判边界（零成效证据/幸存者偏差/标题党/引流/平台合规）、适用判断表 |
| `references/index.md` | 信源子目录索引（信源清单 + F 编号段索引 + 可信度说明） |
| `references/article-source.md` | F-001~F-029 博文事实三类登记 + F-030~F-036 核验补充与勘误 |
| `references/verification.md` | 6 项 P0 结论总表、勘误四张清单逐项落点、信源距离评估、9 个来源与方法边界 |
| `log.md` | 本文件 |

另：主仓库 spec 2 个文件（`.trae/specs/okf-wiki-ecosystem/sell-before-build-blog-okf-wiki/`：spec.md、facts.md）。

### 质量门记录（手动等效验证）

> 环境说明：`invoke gates.*` 依赖 optional-dependencies.doc 的 `invocations` 包，当前环境未确认安装；按 Skill §7 执行**清单化手动等效验证**（与先例 bytedance-ai-consolidation 同路径），不声称 gates 通过。

- **双份 F 编号一致性**：正则提取 spec `facts.md` 与 `references/article-source.md` 的 F 编号集合——两边均为 36 个（F-001~F-036）、集合相等、无跳号 — **通过**
- **UTF-8 strict roundtrip**：以 DecoderExceptionFallback 严格解码 bundle 全部 9 个 .md，无异常、无 BOM — **通过**
- **相对链接全可达**：正则提取全部 Markdown 链接（排除 http/https/mailto/锚点）逐一 Test-Path；跨 bundle 链接深度已核对（concepts/ 引兄弟 bundle 为 `../../marketing-fundamentals/index.md`，根 index 为 `../marketing-fundamentals/index.md`）— **通过**；file 协议绝对链接零出现
- **三级 toctree 完整**：根 index 收录 concepts/index、references/index、log；concepts/index 收录 3 篇概念；references/index 收录 article-source、verification；父级 marketing/index.md toctree 已追加本束 — 条目逐一对应存在文件 — **通过**
- **三级计数同步**：marketing 组 frontmatter total_bundles 1→2；sheke/index.md 导航表 1 束→2 束；bundles/index.md total_bundles 538→539、正文计数 538→539、mermaid sheke 37→38、社科域节标题 37→38、marketing 行 1→2（groups 59、domains 9 不变）；sheke 域各组束数和 8+6+3+2+2+2+15=38 自洽 — **通过**
- **frontmatter 门**：根 index 含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources（博文 + 8 个外部核验/佐证源：7 权威 + 1 反面证据）；子文档含 type/title/description/sources，concepts/01 与 verification.md 已补 VentureMage 溯源（红杉种子轮数字）— **通过**
- **勘误落实门**：4 处 ⚠️/❌（零代码夸张、头衔、18 个月、歌德句）在 index 顶部勘误提示、concepts 正文、article-source、verification 四处一致呈现核验值，无一处照搬源文错误 — **通过**
- **性质声明门**：index 顶部显著标注"个人自媒体方法论观点，非实测 SOP"；不设 examples/ 理由与两问判定记录在 spec — **通过**
- **敏感信息门**：bundle 内无家目录绝对路径（用户名目录模式扫描零命中；本 log 对扫描规则本身采用文字转述，避免模式自指）— **通过**

### 已知遗留（非本次范围）

- `sheke/index.md` 导语"14 束行业分析"与 `bundles/index.md` industry 组 15 束存在**本次任务之前的既有计数漂移**，按最小变更原则未在本次改动，建议后续专项核对 industry 组实际束数后统一。

### 提交建议（C 阶段，待用户确认，未执行）

1. 子模块 `projects/awesome-okf-xs`：bundle 9 个新文件 + sheke/marketing/index.md + sheke/index.md + bundles/index.md
2. 主仓库：`.trae/specs/okf-wiki-ecosystem/sell-before-build-blog-okf-wiki/`（spec.md + facts.md）
3. 主仓库：子模块 gitlink 更新
