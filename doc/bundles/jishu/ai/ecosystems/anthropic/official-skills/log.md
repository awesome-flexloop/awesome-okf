# Anthropic Official Skills Bundle 更新日志

## 2026-10-24

### 背景

对 `external/libs/anthropics/skills` 目录做**全量逐文件实测**（482 个文件、72 个 `.py`、19 个 `SKILL.md` 合计约 4000 行），在原 4 篇概念 + 1 篇参考的基础上补齐**每个 skill 的用途/结构/编写规范/可复用模式**，并建立可复现的事实底账。

方法论：七概念方法论场景 4（知识沉淀），链路 R → I → E → V → C。

### 新增

- 📚 **概念文档（5 篇）**：
  - [Skill 编写规范与可复用模式](concepts/04-authoring-patterns.md) — 从 19 个官方 Skill 反向提炼：frontmatter 字段决策表、description 三种强度（场景枚举 / 反触发+可执行探测 / 关键词兜底）、正文四种内容模式（纯指令流程 / 命令+坑位速查 / 哲学驱动生成 / 产品化推荐）、资源目录分工与 reference 加载时机标注、黑盒脚本契约、FIXED vs VARIABLE 切分、双跑评估闭环、安全边界、骨架选择决策表
  - [文档处理类 Skills 详解](concepts/05-document-skills.md) — docx/pdf/pptx/xlsx/doc-coauthoring：共享 `office/` 子树与 39 个 XSD、XML 原地编辑原则、pptx 三层 QA、xlsx 公式强制重算、doc-coauthoring 三阶段读者测试
  - [设计与创意类 Skills 详解](concepts/06-design-skills.md) — algorithmic-art/canvas-design/theme-factory/frontend-design/brand-guidelines/slack-gif-creator/web-artifacts-builder：哲学生成骨架、FIXED/VARIABLE、主题 Markdown 格式、字体许可缺口
  - [API 与开发工具类 Skills 详解](concepts/07-dev-skills.md) — claude-api/mcp-builder/skill-creator/webapp-testing：105KB SKILL.md 结构全景、curl 目录例外、reference 加载时机、双跑评估、侦察—动作分离
  - [沟通与写作类 Skills 详解](concepts/08-communication-skills.md) — internal-comms/academy-guide/discernment-nudge：薄壳路由 + 兜底文件、正向推荐规则、反触发 9 类清单
- 🎯 **示例文档（2 篇）+ examples/index.md**：
  - [从零造一个 Skill](examples/01-author-a-skill.md) — 最小 Skill 全流程实操（frontmatter → 目录 → 校验 → 打包 → 评估 → 安装），命令可直接复制，含校验报错对照表与常见坑速查
  - [场景到 Skill 的选型决策树](examples/02-skill-selection.md) — 主决策树、六组边界误选对照、可复用命令示例、三个高频组合
- 📖 **参考文档（2 篇）**：
  - [事实登记表](references/facts.md) — F-001~F-098 逐条实测底账，含证据等级定义（S 实测 / D 文档明示 / U 社区单源）与可复现复核路径
  - [社区视角与勘误对照](references/community-view.md) — 知乎社区口径（单源）对照，12 条裁定 + 6 条源码独有事实 + 5 条复核命令

### 修改

- 🔧 **[concepts/01-skill-format.md](concepts/01-skill-format.md)** — 事实校正 4 处：
  - `name` 命名规则由误写的 `^[a-z0-9][a-z0-9-]*[a-z0-9]$` 改为实测的 `^[a-z0-9-]+$` + 长度/首尾/连续连字符三条附加约束
  - `compatibility` 由误写的"嵌套 map"改为**必须是字符串**（嵌套 map 会触发 `Compatibility must be a string, got dict`），并补 ≤500 字符约束
  - `license` 由误写的"官方 Skills 通常使用 MIT 许可证"改为**双轨事实**：14 个 Apache-2.0 + 4 个 Anthropic 专有（docx/pdf/pptx/xlsx，source-available 非开源）+ 1 个无 LICENSE.txt（doc-coauthoring）；仓库**不存在 MIT 许可**
  - 补充**允许字段总表**（6 字段 + 官方使用率）与「500 行无硬性要求」专节（`quick_validate.py` 无行数检查，claude-api 616 行可正常加载）
  - 资源引用示例中的 `extract_fields.py` / `fill_form.py` / `inspect.py` / `pypdf-cookbook.md` 等**不存在的路径**替换为实测真实路径
  - 目录职责表补 `assets/` `templates/` `core/` `LICENSE.txt` 与 `evals/` 的 root 级排除说明
  - 发布检查清单扩充为 10 项（含尖括号、compatibility 类型、大小写一致性）
- 🔧 **[references/skills-index.md](references/skills-index.md)** — **整体重写**。原版 19 个 skill 中约 15 个的资源路径不存在（如 `templates/lesson.md`、`references/colors.md`、`references/ooxml-schema.md`、`scripts/eval_mcp.py`、`themes/*.json`、`scripts/xlsx-*.py`、`scripts/extract_fields.py`、`references/playwright-patterns.md`、`scripts/init-artifact.py`、`scripts/build-artifact.py`、`scripts/easing.py` 等），全部替换为逐 `ls` 实测的真实路径；新增体量速查表与 5-plugin 分组表
- 🔧 **[index.md](index.md)** — 补源码目录全景图与指标表、9+2+3 篇导航、核心可复用模式速览（12 条带可复用性评级）、与 `anthropics-skills` 束的分工说明
- 🔧 **[concepts/index.md](concepts/index.md)**、[references/index.md](references/index.md)** — 导航同步

### 索引对账

- 本 bundle 文档数（内容文档口径，不含各层 index.md）：概念 9 / 示例 2 / 参考 3 = **14 篇**（原 5 篇）
- 束数不变（仍为 `official-skills` 一个 bundle），`doc/bundles/index.md` 总计数 **675 束 / 63 组 / 9 域** 无需变更
- 上级 [anthropic/index.md](../index.md) 的「文档统计」表已按实测口径重算并同步（official-skills 行：4/0/1/9 → 9/2/3/16；同时校正了原表 claude-code / cookbooks / prompt-engineering / financial-services / system-prompts 五行的偏差；合计 37/7/12/82 → 42/9/15/80）

### 门禁

- `scripts/check-toctrees.py` — 本 bundle 贡献 **0** 问题（基线 18 项问题全部来自他方未提交的 `zhihu-open-platform` WIP，按"谁添加谁对账"原则不代改）
- `scripts/check-bundles-index.py` — 通过（9 域 / 63 组 / 675 束，五面一致）
- `scripts/check-utf8.py` — 通过

---

## 2026-08-27

### 新增

- 🎉 初始化 official-skills bundle 首个版本
- ✅ 覆盖 Anthropic 官方 19 个 Skills 的完整中文文档索引
- 📚 概念文档（4 篇）：
  - [Skills生态概览](concepts/00-overview.md) — Skills 概念、触发机制、生态定位、分类总览
  - [SKILL.md格式规范](concepts/01-skill-format.md) — 目录结构、frontmatter 字段、description 最佳实践、打包分发
  - [Skill Creator工具详解](concepts/02-skill-creator.md) — 元技能 5 步流程、3 个评估代理、评估方法论
  - [Claude API Skill详解](concepts/03-claude-api-skill.md) — 多语言覆盖、API 漂移警告、"Never guess SDK usage"原则
- 📖 参考文档（1 篇）：
  - [全部Skills索引](references/skills-index.md) — 19 个 Skills 按 4 大类分组的完整索引表格，含触发关键词
- 🏗️ 导航结构：
  - 根 [index.md](index.md)（含 okf_version: 0.2）
  - concepts/index.md
  - references/index.md
  - 本 log.md
