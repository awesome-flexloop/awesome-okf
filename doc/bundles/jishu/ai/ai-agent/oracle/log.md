# 变更日志

## 2026-09-16 · 知识包创建

- 来源：微信公众号「Leon学AI」2026-08-30 原创博文《太炸裂了！这是哪个大佬发现的 CodeX这个神仙用法，居然能将gpt-plus发挥到极致！》（1684 字）+ 官方源核验（GitHub main 分支 docs/install.md、docs/browser-mode.md、docs/agents.md、skills/oracle/SKILL.md、npm 官方包页）
- 事实登记：F-001~F-041（博文 21：含 7 条作者观点；官方补充 20）；P0 核验 10 项全通过，0 ❌、0 硬勘误；博文 5 项信息缺口（Node 24+、brew 平台限定、多 Provider/MCP、版本时效、安全边界）由官方源补齐并显式标注
- 结构：concepts 3 篇 + examples 2 篇 + references 2 篇（根 index + 3 子目录 index + log，共 12 文件），导航计数 3+2+2+1=8
- 归属：jishu/ai/ai-agent 分组「📰 产品资讯」（同形态先例：wigolo / openviking / zhihu-cli / claude-vision-skill）
- 工作流：seven-concepts-cmd 元编排（场景 4 知识沉淀 R→I→E→V→C）+ blog-article-to-okf-wiki 七阶段（敏感度预检→骨架两问→归属决策→F 编号+P0 核验→三层拆分→信源先行生成→对抗审查）
- 骨架判定：博文作者为转述推荐（非一手实测），但全部操作命令经官方文档逐行核验一致，故设 examples/ 2 篇并在文首显著声明
- V 阶段机械门禁（直接运行子模块 scripts/ 官方门禁）：
  - 双份 F 编号集合比对 ✅（spec facts.md 与 references/article-source.md 均 F-001~F-041 连续 41 条）
  - 束内相对链接全部可达、无 file:/// 与家目录绝对路径；12 文件 UTF-8 strict 无乱码 ✅
  - `check-utf8.py` ✅ 10412 文件通过；oracle 束自身在 `check-toctrees.py` 零违规（12 文件经组索引 toctree BFS 全部可达）
  - 本会话期间曾将总索引修复至 `check-bundles-index.py` 全绿（555 束五面一致）；随后并行会话将 bundles/index.md 计数回退/改写为旧值（539/407，sheke 37）、jishu/ai/index.md 尚有 8 个他束 toctree 条目在途（aitokenbus/firecrawl/gpt6-astra-usage-guide/inurl×2/loopx/uumit-a2a-marketplace/wigolo）——漂移均非本束引入、非本束文件，最终状态以并行会话收敛后重跑 gates 为准
  - 转化期间多个并行会话同时落束（ai-agent-book/openhuman/show-me-skill 等），共享组索引/总索引一度出现计数竞态与行粘连，已按目录树地面真值修复过投影；他束内容未代写
- 主仓库侧规划底稿：`.trae/specs/okf-wiki-ecosystem/oracle-blog-okf-wiki/`（spec.md + facts.md）
