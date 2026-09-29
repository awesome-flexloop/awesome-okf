# LobsterAI 知识束变更日志

## 2026-09-09 V 阶段独立验证（幂等重跑）

- **范围**：V1 frontmatter 九字段与 sources 路径真实性（14 篇）、V2 零虚构 API 符号级验证（60+ 符号）、V3 全部计数断言独立复核、V4 toctree/相对链接/四元组导航、V5 R/I 合规抽查（facts 抽 6 条溯源 + 74 条编号连续 + 推断词污染 + insights 证据锚定）。
- **修复**：无。断链 0、frontmatter 缺失 0、编号笔误 0，修复白名单三类均未触发，磁盘零写入。
- **未修观察项（内容级错误，超出修复白名单，如实上报）**：
  1. F-la-018：`agents` 表实为 20 列（CREATE TABLE 逐列计数 + 6 条 `ALTER TABLE` 均为幂等补列），非 21 列；concepts/03、concepts/06、references/insights.md 洞察 4 均沿袭该误。
  2. F-la-042：`src/renderer/store/slices/` 实为 21 个 `.ts`（Glob 实测），非 20 个；concepts/00、insights 洞察 1 沿袭。
  3. F-la-072：tests/ 顶层口径 38 个与 git ls-files 43 个（含子目录）矛盾，计数方法表述不严谨；insights 第 76 行沿袭。
  4. F-la-028：连通性测试方法实为 `testXxxOpenClawConnectivity`（9 平台全覆盖），非 `testTelegram`/`testDiscord` 等短名。
  5. concepts/09-skill-system.md：标题称 SkillManager「13 个方法」，下表实列 12 个；order 分段表 10-90 行混入 order=100 的 frontend-design（该行 11 个应为 10 个）。
- **结论**：五验证项 V1/V4/V5 PASS，V2/V3 PASS-with-findings（符号与计数主体真实，上述 5 项内容级偏差未修）；束整体可用，建议在 C 阶段或基线升级时修正上述计数/命名断言。
