# AgentMore × OpenMAIC 知识包变更日志

## 2026-10-28 · 初版生成（博文→OKF Bundle）

- **来源**：智谱清言 AgentMore 官方分享页《清言 × 清华 OpenMAIC，打造你的专属AI老师》（`agentmore.chatglm.cn`，约 700 字，采集时点 2026-10-28，分享页未标具体日期）
- **方法论**：七概念场景 4 知识沉淀链路 R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段执行
- **规模**：9 文件（3 concepts + 2 references + 2 目录 index + 根 index + 本日志）；F 编号事实 46 条（公告 24 + 官方核验补充 22）

### R（事实采集与核验）

- 公告位于 `agentmore.chatglm.cn` 分享页，正文经 iframe 内抓取后落盘为纯文本（约 700 字），确认为公告全文
- 信源距离预判：**厂商自述**（智谱清言 AgentMore 官方公告）；能力宣称与可核验事实交织，需分层登记
- 清晰度预检：URL 无访问控制参数（`shareFile/m/<id>` 为公开分享页）→ **公开内容**，标准工作流
- P0/P1 核验 13 项（OpenMAIC 官方仓库 README/News/LICENSE/`skills/` 与 `skills/agent-runtime/` 目录树 + Live Demo + 第三方测评 36氪 + App Store 开发者信息）：**7✅ / 6⚠️ / 0❌**（F 编号行级口径 ✅ 14 / ⚠️ 6 / ❌ 0）
- 6 项 ⚠️：Star 多口径互斥（F-030）；License 三源互斥（F-031）；「逆向教学设计」未逐字绑定（F-035）；「习题带练」未命中官方目录（F-036）；「学习搭子两项新技能」公告单源（F-044）；「Skill 广场安装机制」公告单源（F-045）
- 依据用户决策：① 不设 examples/（公告为能力上新说明，操作可复现性两问皆"否"）；② 以 OpenMAIC 官方仓库做 P0 核验、公告单源项显式标注

### I（骨架与归属）

- 操作可复现性两问皆"否" → 产品公告/能力解读类骨架，**不设 examples/**
- 归属：`jishu/ai/products/agentmore-openmaic/`（智谱清言 AI 产品能力上新，与 aitokenbus「产品自述资讯，非操作教程」先例一致，不新建分组）
- 命名区分：既有 spec `openmaic-wiki-20260909`（2026-09-09 GitHubDaily 报道）主体同为 OpenMAIC 但信源/文章/采集时点不同，本束以 `agentmore-` 前缀与独立 spec 区分，bundle 层互链不合并
- `stale_after: 2026-12-31`（Star/License/Skill 清单/版本号均为高时效字段）

### E（bundle 生成）

- 信源先行：article-source.md → verification.md → concepts（00/01/02）→ 各级 index → 根 index
- 全部事实/版本/技术栈声明携带 F 编号；厂商自述（S）与公告宣传语（V）与可核验事实（O）分层登记
- Star 数与 License 采用"多源并列 + 带时点观测"呈现，不写成单一权威值
- 四视角对抗审查与机械门禁见下（V 阶段）

### V（对抗审查与机械门禁）

四视角审查结论与采纳（厂商公告 / 能力解读类）：

1. 🟡 魔鬼代言人 → 区分"公告自述"与"官方仓库可核验"两条口径线：8 个 Skill 中 6 项可对应、"习题带练/逆向教学设计"未逐字命中，正文明确标注而非照搬公告
2. 🟠 老板视角 → 明确本束为厂商公告与开源项目交叉核验的**能力解读**（无 examples/、无部署教程），被点名项目事实一律以 OpenMAIC 官方仓库为准
3. 🔵 未来视角 → stale_after=2026-12-31 覆盖 Star 时点、License 统一、学习搭子能力集与 Skill 清单、OpenMAIC 版本号
4. 链接自检 → 本束内 3 concepts + 2 references 相对链接逐条可达；跨束关联仅引用已存在的 skills-manager / agent-reach / aitokenbus / knocket

机械门禁（2026-10-28）：

| 检查项 | 结果 |
|--------|------|
| 双份 F 编号正则核对（spec facts.md ↔ article-source.md） | ✅ 各 46、F-001~F-046 连续无跳号、集合相等 |
| UTF-8 严格编码 | ✅ `check-utf8.py` 通过 |
| toctree 三级完整 | ✅ 本束 4 个 index.md 指令块齐备，条目逐一对应磁盘 9 文件 |
| 相对链接可达 | ✅ 本束内/跨束链接逐一核对（跨束仅引用已存在目录） |
| frontmatter 完整 | ✅ okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 齐备，多信源 |
| 敏感信息 | ✅ 无家目录绝对路径、无密钥 |
| 勘误落实 | ✅ 6 项 ⚠️ 正文均呈现公告口径并标注；Star/License 并列登记；单源项标"公告单源" |
| 聚合计数（check-bundles-index.py / check-asset-baseline.py） | ✅ 见下方 C 段索引收尾口径 |

### C（提交）

- 索引收尾（已完成）：`products/index.md`（35→36，含 nav 表 + toctree + 计数）、`jishu/ai/index.md`（description 与正文 276→277、products 行 35→36）、`jishu/index.md`（ai 行 276→277）、`doc/bundles/index.md`（`total_bundles` 690→691、正文计数、mermaid jishu 509→510、jishu 节标题 509→510、ai 表行 276→277）、`doc/index.md`（两处 690→691）、`README.md`（badge、L26、L28、L89、jishu 510、合计 691）三处规模数字一致
- 门禁复跑：`check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` / `check-asset-baseline.py` 全部通过；双份 F 编号（spec `facts.md` ↔ 本束 `article-source.md`）各 46 条、F-001~F-046 连续且集合相等；束内 F 编号全覆盖；无 `file:///` 绝对路径
- **提交状态：待用户授权**。原子提交顺序：子模块 `projects/awesome-okf-xs`（本束 9 文件 + products/ai/bundles 索引）→ 主仓库 spec（`.trae/specs/okf-wiki-ecosystem/agentmore-openmaic-okf-wiki/`）→ 主仓库 gitlink；push 依用户指令，默认不推送
