# 变更日志（log.md）

## 2026-09-16 初始生成

- **信源**：杰克王聊AI博文《2.8万Star！AI Agent 教材来了：10章94实验，中科大博士免费开源》（2026-08-01 07:30，作者杰克王，原创；正文 2811 字）
- **工作流**：blog-article-to-okf-wiki Skill 七阶段，seven-concepts 场景4（知识沉淀）元编排 R→I→E→V→C
- **信源获取**：微信域名反爬确定（Skill 13/13 记录），未尝试 WebFetch，直接 browser_use 子代理提取 `#js_content`，交叉核对元信息/2 代码块/2 表/6 图 alt 一致
- **信源距离预判**：第三方公众号推荐文（非厂商赞助、无提效倍数类营销叙事），但核验对象开源仓库一手可得——GitHub API、历史 commit 快照、原书正文、作者官方页（ring0.me/01.me）直接交叉，核验强度高于一般博文
- **骨架判定**：操作可复现性两问——Q1 边界性是（有 clone/uv/PDF 命令），Q2 否（公众号作者未实测、无运行输入输出、命令引自官方 README）→ **无 examples/**，技术综述/资源盘点骨架
- **归属判定**：`jishu/ai/ai-agent/` 📰 产品资讯板块（matrix-zero-person-company/pi-agent-harness 等博文转化先例）；与 ai-agent-fundamentals（跨框架模式）、book-to-skill（书籍→技能）互链
- **事实登记**：F-001~F-041 共 41 条（博文 24 + 核验补充 17）；作者观点 2 条（F-021/F-023 性质标注）
- **P0 核验**：18 项 = 13 ✅ + 2 ❌ + 3 ⚠️，另 1 项 P2 单源（F-040 中科大 LUG 未检出，正文不采用）。关键核验手法：用博文发布前 9 小时的 commit `8c2b7f5`（2026-07-31 22:47 北京时间）README 快照锁定时点口径，用 GitHub API 锁定仓库元信息，用 book/images 目录列表核对工作流图资产
- **勘误（6 条，正文已全部落实正确值）**：
  - E1 ❌ 博文"94 实验"——时点官方头条为 95，博文自表合计 98 自相矛盾；现行 2.0 为 109（F-014/F-015/F-025/F-029）
  - E2 ❌ 第 6 章博文写 11，官方编号 6-1~6-12 为 12（F-026/F-027）
  - E3 ⚠️ "四种工作流模式"——仓库实有 5 张 fig1-wf 图（多 routing/evaluator），2.0 正文改"工作流 vs 自主 Agent"二分（F-033）
  - E4 ⚠️ "每个实验一条命令能跑"——实验分 ✅/📖/🚧 三类，22 个外部仓库、API Key/GPU 等前置（F-027/F-030）
  - E5 ⚠️ 时效漂移：13→15 语言、Python 3.10+→3.11–3.13、1.4→2.0 章节重组（博文时点均正确，F-028/F-029/F-041）
  - E6 单源：中科大 Linux 用户组成员官方页未检出（F-040）
- **状态决策**：2 处 ❌ 均为非核心数字失准（书的主声明全部成立；实验数当周处于 88→92→95→109 快速增补期），按 Skill 规则 status: stable + 完整勘误，不触发 flagged；stale_after=2026-11-30（6 周内 95→109、1.4→2.0，迭代极快）
- **文件集**：根 index + log + concepts/（index + 5 篇）+ references/（index + article-source + verification）= **11 文件**，无 examples/

## V 阶段审查记录

- **四视角审查**：
  - 事实溯源：所有具体数字/版本/名称均带 F 编号或标注"核验补充/作者观点"；2 处 ❌ 勘误在 concepts/03 正文以正确值呈现并标注博文口径；93%/$37M 等 Pine AI 数字标注"作者 CV 自述、非第三方审计"
  - 结构规范：frontmatter 十字段齐备（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），sources 含博文+仓库+API+快照+作者页；3 个 index.md 均含隐藏 toctree
  - 读者可用性：bundle 内相对链接全部 Test-Path 通过；跨束链接（ai-agent-fundamentals/book-to-skill/agent-communication-protocols/orca/veadk-python）均存在
  - 时效边界：双时点提示块置于根 index 与 concepts/00；6 条已知边界；stale_after 与复核要点明确
- **双份 F 编号一致性**：spec `facts.md` 与 `references/article-source.md` 正则提取均为 F-001~F-041（各 41 条，连续无跳号），集合比对相等 PASS
- **门禁结果（stdlib 脚本，仓库自带 gate）**：
  - `check-utf8.py`：PASS（10327 文件均为合法 UTF-8，含本束 11 文件）
  - `check-bundles-index.py`：PASS——9 域 / 59 组 / 546 束，frontmatter/计数行/节标题/分组表/toctree 五面一致
  - `check-toctrees.py`：本束 0 问题（log.md 落盘后"引用不存在：log"已消除）；输出中残余 13 项全部为**他会话并行 WIP**（free-llm-api-hands-on 缺 index.md 且 7 文件未收录、inurl-unified-token 1 文件、tencent/workbuddy-sandbox-public-endpoint 2 文件），与本束无关，按 gate 脚本"工作树含未提交 WIP 时谁添加谁对账"原则不在本束处理
- **并发说明**：生成期间子模块工作树存在他会话活动（openviking 已先行入组：组 total_bundles 48/342 文档；另有 free-llm-api-hands-on、gpt6-astra-usage-guide、llama-cpp-local-inference、loopx 等未跟踪束）。本束计数以 gate 目录树地面真值为准（组 49 束/349 文档，总 546 束），组索引内容统计行已按 openviking 校正后的口径增量（+5 概念 +2 信源）
- **敏感信息**：博文文末作者私人微信号属引流信息，按 F-002 登记但不入 bundle 正文；全束无家目录路径、无 file:/// 绝对路径
