# 更新日志

## 2026-10-21

**Mermaid 存量修复**: 清偿本 bundle 既有页面的 Mermaid 编码规范欠账——10 个页面 53 张图，304 error / 6 warning → **0 error / 0 warning**

- **修复范围**：`concepts/01-architecture.md`（12 图）、`concepts/02-llm-providers.md`（5 图）、`concepts/03-tools-mcp.md`（9 图）、`concepts/04-review-rules.md`（4 图）、`concepts/05-session-telemetry.md`（10 图）、`concepts/06-integrations.md`（7 图）、`concepts/12-official-runtime-model.md`（1 图）、`concepts/13-integration-contracts.md`（1 图）、`references/cli-reference.md`（2 图）、`references/faq-troubleshooting.md`（2 图）
- **修前违规分布**：`<br/>` 换行标签 158、未加引号边标签 64、块内空行 37、未加引号节点文本 27、裸中文 subgraph ID 14、participant 别名未加引号 4、warning 6（Unicode 箭头 3 + style 中文 ID 3）
- **修复方式分两类**：① 可自动修项（节点/边标签引号、块内空行、`<br/>` 移除、participant 别名引号）**复用主仓 `lib/checks/mermaid.py` 的 `DIAGRAM_FIXERS`**，与 CI 门禁同源同逻辑，不自造正则；② 需人工映射项（裸 subgraph ID 与其边引用 / style 引用、Unicode 箭头）按主仓规范 `subgraph EN_ID ["中文标题"]` 改写并同步引用点
- **Unicode 箭头按语义改写而非机械替换**：`→` 改为 ASCII `->` 而非自动修复器的连字符 `-`，避免把「五重门过滤顺序」「评论处理五步顺序」的流程方向降级为分隔符；`工具名 → Provider 映射` 改写为 `工具名对应 Provider 映射`
- **连带修正（解析期冲突）**：`03-tools-mcp.md` 的 `subgraph HTTP ["HTTP 传输"]` 与其内部节点 `HTTP["Streamable HTTP"]` 同名会造成 Mermaid 解析期 ID 冲突，subgraph ID 改为 `HTTP_TRANSPORT`
- **门禁盲区（欠账根因登记）**：主仓 `constants.EXCLUDED_DIRS` 含 `projects`，`check-mermaid.py` 按设计不越界扫描子模块；子模块自身仅有 `check-toctrees.py` / `check-utf8.py` / `check-bundles-index.py` 三项脚本，**无 Mermaid 门禁**——这正是存量违规得以长期累积的原因
- **文本语义保全**：`<br/>` 一律替换为单个空格（不引入新分隔符），节点与边标签的文字内容未改写，仅补双引号；图中承载的架构语义、门序、状态名均未变更
- **复验**：直调同一套 checker 复验全束 **0 error / 0 warning**；另补结构自检（subgraph/end 配平、块内节点 ID 唯一、节点 ID 与 subgraph ID 不冲突、style 引用可达）通过；子模块 `check-utf8.py`（12037 文件）/ `check-toctrees.py` / `check-bundles-index.py`（9 域 / 63 组 / 659 束）三项均通过
- **已知边界**：本轮为**纯格式修复**，未触碰任何事实陈述、编号事实（F-xxx）或口径裁决；主仓 Mermaid 门禁仍不覆盖子模块，本条目所记复验方式为直调 checker，非 CI 自动拦截

## 2026-10-21

**Source Code Layer**: 经 `alibaba/open-code-review` commit `375f64cd` 静态源码阅读，新增「源码层」6 页并建立与官方文档层的四处口径差裁决表（七概念方法论编排：R→I→E→V→C）

- **新增页面 6 个**：`concepts/15-source-code-runtime-model.md`（源码层运行时模型）、`concepts/16-source-code-extension-contracts.md`（源码层扩展契约）、`concepts/17-source-code-verification-playbook.md`（源码层验证与口径裁决手册）、`references/source-code-layer.md`（信源登记与覆盖矩阵）、`references/source-code-facts.md`（F-101~F-178 编号事实）、`references/source-code-review.md`（源码层四视角 V 记录）
- **既有页面 0 改写**：12 概念 + 5 参考页 + 官方文档层 6 页保持原貌，源码层与文档层的差异集中登记在 D-1 ~ D-4 一节，**不回改对方页面**
- **源码层事实 78 条**：按差异获取链（10）、文件选择与过滤（12）、分组调度与主循环（14）、LLM 客户端与 Provider（12）、工具与输出契约（14）、扩展与集成面（11）六主题采集，每条带 `文件:起-止` 锚点 + 字面值 + L1/L2/L3 证据等级
- **口径差 4 处**：provider 数 25→**30**（D-1，多出 edenai/z-ai-coding/ollama-cloud/litellm/mistral）、静态过滤门 5→**6**（D-2，插入不可被用户规则放行的 secret 门）、排除原因码 7→**8**（D-3，多 `provider_directory`）、`MAX_TOOL_REQUEST_TIMES` 单一 100→**review 100 / scan 60**（D-4）
- **新增洞察 4 条**：I-5 不可覆盖安全门（区分可用性与可信赖性）、I-6 降级链必须单向、I-7 输出状态分层承载（进程/业务/覆盖三层互不替代）、I-8 文档与实现的分歧应登记而非抹平
- **可迁移模式 4 条**：M-1 元数据契约式分组、M-2 单向降级链、M-3 分层输出契约、M-4 不可覆盖安全门——每条含触发场景 + 核心步骤 + 反模式 + 检验标准 + 迁移面
- **索引对账**：`doc/bundles/jishu/ai/products/index.md` 表头为「知识包 | 束数 | 一句话简介」，每行束数取值为 1，分类首行「本类共 33 个知识包」；本次为**既有 bundle 内部增补**，分类束数 33 与总索引计数**均不变**
- **质量门**：G1（事实无因果词，78 条）/ G2（新增 4 条洞察四元组完整）/ G3（4 个模式含触发+步骤+反模式+检验标准+迁移）/ G4（行动项原子化）/ V 门（4 视角 9 条意见，8 条实质采纳 + 1 条核查后留痕）均通过
- **Mermaid 门禁**：本轮新增 3 张图（15 章 2 张、17 章 1 张）按主仓 `docs/tech/references/development-standards.md` 的 Mermaid 编码规范六规则重写并复验——**0 error / 0 warning**（节点标签双引号包裹、去除 `<br/>` 换行标签、边标签加引号、去除 Unicode 箭头）。主仓 `check-mermaid.py` 因 `EXCLUDED_DIRS` 含 `projects` 不越界扫描子模块，故以直调同一套 checker 的方式对目标文件校验
- **已知边界**：本轮**未运行 `ocr` 二进制、未调用任何 LLM、未发起任何网络请求**，源码层事实均为「代码中如此声明」；HEAD 领先发布 tag `v1.13.2` 共 4 个提交，D-1~D-4 的成因（未发布 vs 未穷举）未判定；`acp/internal/`、`extensions/` 实现、`*_test.go` 等未读边界已显式登记
- **存量欠账（已于同日修复，见上方「Mermaid 存量修复」条目）**：本 bundle 另有 10 个既有页面含 53 张 Mermaid 图违反同一编码规范（`<br/>` 换行标签 + 未加引号的中文节点/边标签，修前 304 error / 6 warning），分布于 `concepts/01`~`06`、`concepts/12`、`concepts/13`、`references/cli-reference.md`、`references/faq-troubleshooting.md`。成因是子模块无 Mermaid 门禁脚本（仅 `check-toctrees.py` / `check-utf8.py` / `check-bundles-index.py`），主仓检查器按设计不扫描 `projects/`。本轮新增页面已合规；存量修复已作为独立提交落地

## 2026-10-21

**Official Docs Layer**: 经 `open-codereview.ai` 官方文档站全站核验，新增「官方文档层」6 页并对既有页面建立口径勘误表（七概念方法论编排：R→I→E→V→C）

- **新增页面 6 个**：`concepts/12-official-runtime-model.md`（官方运行时模型）、`concepts/13-integration-contracts.md`（集成契约）、`concepts/14-verification-playbook.md`（可迁移模式与验证手册）、`references/official-doc-facts.md`（F-001~F-100 编号事实）、`references/official-doc-corrections.md`（E-01~E-11 勘误 + OK-01~OK-03 核对通过）、`references/adversarial-review.md`（四视角 V 记录）
- **既有页面 0 改写**：12 概念 + 5 参考页保持原貌，冲突数值统一由勘误表裁决（引用时以「官方口径」列为准）
- **勘误 11 条**：provider 数 19→**25**（E-01）、`azure-openai` 为虚构内置项（E-02）、协议 3→**4** 种（E-03）、review `max_tokens` 58888→**200000**（E-04）、`--max-tools` 模板默认 30→**100**（E-05）、`--timeout` 10→**15** 分钟（E-06）、`OCR_LLM_MAX_TOKENS` 提示词/输出语义颠倒（E-07）、plan 双阈值（E-08）、官方站点 `/docs/integrations/*` 断链（E-09）、首页动效占位值（E-10）、「六阶段」术语口径差异（E-11）
- **索引对账**：`doc/bundles/jishu/ai/products/index.md` 表头为「知识包 | 束数 | 一句话简介」，每行束数取值为 1，分类首行「本类共 33 个知识包」；本次为**既有 bundle 内部增补**，分类束数 33 与总索引计数**均不变**，仅刷新 open-code-review 行的简介口径
- **质量门**：G1（事实无因果词，100 条）/ G2（4 条洞察四元组完整）/ G3（3 个模式含触发+步骤+反模式+检验标准+迁移）/ G4（行动项原子化）/ V 门（4 视角 6 条意见，3 实质采纳 + 2 条件采纳 + 1 核查后留痕）均通过
- **已知边界**：本次未实机运行 `ocr` 二进制，事实均来自官方文档站与官方仓库静态文本；文档站 15 个可达页面已覆盖，贡献指南类页面无独立导航入口

## 2026-09-02

**Migration**: 从 SpecWeave docs/knowledge/learning/03-agent-platforms-tools 迁入 awesome-okf-xs

三源整合新建：03-code-devtools/open-code-review-wiki（19 章）、根级 open-code-review-wiki（14 章结构化）、分类根散文件（微信文章教程）。去重后保留 12 概念 + 5 参考；各源 log/README/index 属元数据不迁入。
