# 变更日志

## 2026-09-16 · 知识包创建

- 来源：微信公众号「macrozheng」（梦想de星空）2026-09-09 博文《字节又开源了一个顶级 Agent 项目！》+ 官方源核验（GitHub REST API、README、docs.openviking.ai、阿里云百炼文档）
- 事实登记：F-001~F-048（博文 32：含 F-031/F-032 两条作者观点；核验补充 16）；P0 核验 10 项全通过，0 ❌；2 项口径差异（/health 响应字段、VikingBot 工具名 openviking_memory_commit/openviking_search 不见于官方 15 工具集）
- 结构：concepts 3 篇 + examples 3 篇 + references 2 篇（根 index + 3 子目录 index + log，共 13 文件）
- 归属：jishu/ai/ai-agent 分组「📰 产品资讯」（同形态先例：wigolo / claude-vision-skill / zhihu-cli）
- 工作流：blog-article-to-okf-wiki 七阶段（敏感度预检→骨架两问→归属决策→F 编号+P0 核验→三层拆分→信源先行生成→对抗审查）
- 机械门禁（直接运行子模块 scripts/ 官方门禁脚本，非仅手动等效）：
  - `check-bundles-index.py` ✅ 末次复跑通过（9 域/59 组/549 束五面一致）。说明：转化期间有并行批量转化会话持续落其他束（loopx、uumit-a2a-marketplace、firecrawl、gpt6-astra、llama-cpp、openhuman、oracle、ai/wigolo 重复目录等十余个在途束），本束多次按目录树地面真值帮总索引收敛计数，未代写任何他束内容；若该并行会话在本束之后继续新增束，总计数需由其继续滚动
  - `check-utf8.py` ✅ 通过（10369 文件全部有效 UTF-8、无 BOM）
  - `check-toctrees.py` ❌ 全库问题全部属于并行会话在途束（缺根 index、未注册 toctree、重复 wigolo 目录等）；**openviking 束零违规，全部文档经组索引 toctree BFS 可达**（已用门禁输出过滤 openviking 复核）
  - `check_mermaid.py` 因引用已废止的 `.agents/docs/` 历史路径无法运行（迁移遗留工具缺陷，与本次改动无关）；束内 6 个 Mermaid 块已按"中文/特殊字符标签一律双引号"规范人工修正（含时序图 participant 别名）
  - 双份 F 编号集合比对 ✅（facts.md 与 article-source.md 均为 F-001~F-048 连续 48 条）；束内相对链接全部可达；无 file:/// 与家目录绝对路径
- V 阶段独立对抗审查（独立上下文子代理）：P0=0/P1=0/P2=12，已修复其中 10 项（/ready 不含 vlm 检查项、AGFS/RAGFS 命名口径、3 处 F 编号错配、信源补 paper-vikingrag、Mermaid 引号、无出处"90%"措辞、示例 IP 标注、F-041/F-047/F-048 双份登记补全等）；2 项信息级（reference 页 frontmatter 对齐、F-032 未在正文消费）不阻断
