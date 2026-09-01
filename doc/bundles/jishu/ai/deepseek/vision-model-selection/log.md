# 变更日志（Log）

## 2026-08-28 - 对抗性审查（四视角）

- 🔍 按事实 / 结构 / 读者 / 时效四视角对全部 12 个内容文档执行对抗性审查；事实基准为 `.trae/specs/deepseek-vision-blog-okf-wiki/facts.md`（F-001 ~ F-036 唯一合法事实集）
- **事实视角**：36 条事实逐条比对全部与 facts.md 一致，未发现编造数字 / 模型名 / API 声明；`pipeline-output-structure.md` 伪代码已在正文与 docstring 双重标注"非官方 API 文档"——通过
- **结构视角**：frontmatter、toctree 覆盖、Mermaid 决策树语法均合规；但 bundle 为**孤立文档**（父级 `ai/deepseek/index.md` 与 `bundles/index.md` 未接入）——修复：
  - `ai/deepseek/index.md`：导航表"应用模型与资源"新增本 bundle 条目、toctree 追加 `vision-model-selection/index`、`total_bundles` 12 → 13
  - `bundles/index.md`：DeepSeek 分组束数 12 → 13、ai 域 95 束 → 96 束、全库 total_bundles 268 → 269（含正文计数）
- **溯源补全**：`concepts/01-selection-landscape.md`（引用 F-034）、`concepts/02-scenario-matrix.md`（引用 F-036）、`examples/cost-scenario-walkthrough.md`（引用 F-034、F-036）frontmatter `sources` 补充对应官方核验信源条目（DeepSeek 官方新闻 / 火山引擎价格文档），与 `concepts/00` 的登记口径对齐
- **读者视角**：全部相对链接经 Glob/Read 验证目标存在（含 `../../deepseek-ocr2/index.md`、`../../deepseek-ocr/index.md` 跨 bundle 引用，且描述与目标 bundle 实际内容相符）；选型矩阵与决策树可独立 follow——通过
- **时效视角**：Exp 实验模型边界、2026-08 价格时点、权重未开源（含 F-035 弱信源）、单源声明（Gemini/GPT-5 nano/MiniCPM/OCR 专用）在已知边界与 references 中均到位——通过
- 根 `index.md` 的 `verified` 升级为列表，追加本次审查事件（`agent-trae/glm-5.3`）
- 修复后复核：`invoke gates.toctrees` 通过（无孤立文档、无断链）

## 2026-08-28 - 初始版本

- ✅ 基于 seven-concepts-cmd 方法论链路 **R→I→E→V** 生成
- ✅ 完成R阶段（事实采集）：从微信博文《DeepSeek 多模态视觉实验模型发布！》采集 33 条事实（F-001 ~ F-033），并完成三项关键声明的官方轻量核验（核验日期 2026-08-28），补充 3 条核验事实（F-034 ~ F-036），合计 36 条事实
- ✅ 完成I阶段（洞察提炼）：确定"模型详解 → 选型全景 → 场景矩阵 → 协作架构"的知识地图与 concepts / examples / references 三层结构
- ✅ 完成E阶段（信源先行成文）：references/（2篇）→ concepts/（4篇）→ examples/（3篇）→ 各级 index → log
- ✅ 完成V阶段（核验）：全文事实编号交叉核对——所有模型名、价格、能力声明均可回溯至 facts.md（F-001 ~ F-036），无编造数字/模型名；单源声明已在 references/verification.md 显式标注
- ✅ 覆盖范围：
  - 概念文档：4篇（模型详解 + 选型全景 + 场景矩阵 + 协作架构）
  - 实战示例：3个（成本演练 + 输出结构 + 决策树）
  - 信源登记：2个（博文事实清单 + 核验报告）
- ✅ 信源：
  - 博文：https://mp.weixin.qq.com/s/iqoikK7m7arGSHnso-q9hQ （微信公众号"湖北"，2026-08-21，收录于"AI开发笔记"）
  - 官方核验来源：https://api-docs.deepseek.com/news/news260821/ （DeepSeek 官方新闻）、智谱官方文档（docs.bigmodel.cn）、z.ai 定价页、火山引擎官方价格文档
- ✅ 质量门记录：
  - 事实溯源门：所有具体声明带 F 编号，无 facts.md 之外的数字/模型名 — **通过**
  - 交叉引用门：全部使用相对路径，无 `file:///` 绝对路径；对 deepseek-ocr2 / deepseek-ocr 的跨 bundle 引用采用 `../../` 相对路径 — **通过**
  - frontmatter 门：bundle 根带 `okf_version: "0.2"` + 完整溯源字段；子文档带 `type` / `title` / `description` / `sources`，与 agnes-ai-models 格式一致 — **通过**
  - toctree 门：根 / concepts / examples / references 的 toctree 覆盖全部内容文档 — **待主流程接入 `ai/deepseek/index.md` 与 `bundles/index.md` 后运行 `invoke gates.toctrees` 复核**（本任务按约定未修改这两个父索引）
- 备注：`pipeline-output-structure.md` 中的 JSON Schema 与 Python 代码为基于 F-028 推导的示意伪代码，已在文内显著标注"非官方 API 文档"。
