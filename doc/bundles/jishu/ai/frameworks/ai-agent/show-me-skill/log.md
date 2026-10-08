# 变更日志 — show-me-skill

## 2026-09-16 · 初始转化（R→I→E→V 完成，待 C）

- **工作流**：blog-article-to-okf-wiki 七阶段；seven-concepts-cmd 场景 4（知识沉淀 R→I→E→V→C）
- **信源**：微信公众号"阿胖 AI 手记"《我发现一个神仙 Skill……》（2026-09-06），browser_use 提取 #js_content 全文 3477 字符（微信反爬，未走 WebFetch）
- **事实登记**：39 条（博文 F-001~F-030 共 30 条 + 核验补充 F-031~F-039 共 9 条），spec 双份登记：`.trae/specs/okf-wiki-ecosystem/show-me-skill-okf-wiki/facts.md`
- **P0 核验**：7 项全部 ✅，0 ❌（HumanLayer 官方博客 2026-08-12/Dex Horthy、安装命令逐字、两种斜杠调用、官方问题口径、9 类视觉形态、WorkBuddy 环境）
- **精度处理**：F-037（Grill Me 实为 Matt Pocock /grill-me，防读者误归因，博文本身未误述）；F-039（仓库内 SKILL.md 路径未直取，github.com 抓取失败 + jsdelivr 路径 404，以官方博客为裁决依据）
- **骨架判定**：操作可复现性两问皆"是"（安装命令+三种调用可照做，作者三轮实测有顺序有输出）→ 含 examples/ 的工具教程骨架；归属 `jishu/ai/ai-agent/`（📰 产品资讯·工具教程），先例 claude-vision-skill / openviking
- **文件集**：11 个文件（3 概念 + 1 示例 + 2 信源 + 3 子目录索引 + 根 index + 本日志）
- **V 阶段门禁**：直接运行子模块 gates 底层脚本（tasks/gates.py 的调用目标），三项全过
  - [x] `scripts/check-bundles-index.py` ✅ 五面一致（9 域/59 组/555 束，含本束）
  - [x] `scripts/check-toctrees.py` ✅ 全部 index.md 引用有效、内容文档均可达
  - [x] `scripts/check-utf8.py` ✅ 10412 文件均为有效 UTF-8
  - [x] 双份 F 编号集合一致（F-001~F-039 连续，spec facts.md ↔ article-source.md，正则比对相等）
  - [x] 20 条本地相对链接按文件目录基准逐一 Test-Path，0 断链；无绝对路径链接、无家目录路径
  - [x] frontmatter 齐备，sources 含博文 + 官方博客双信源以上
  - [x] 计数同步（含并行会话他束）：ai-agent 49→52（本束 +1）、ai 行 201→203、jishu 420→422、全库 546→555；本束贡献 3 概念/1 示例/2 信源
  - 注：转化期间有并行会话注册 openhuman/oracle 等他束，本会话只对 show-me-skill 自身注册行与其计数增量负责；最终五面一致以 gate 通过为准
- **状态**：verified；stale_after 2026-12-31
