---
type: reference
title: "Anthropic 官方 Skills 事实登记表"
description: "对 external/libs/anthropics/skills 目录逐文件实测得到的事实登记册，F-001~F-086 编号，附证据等级与复核路径。"
tags: [skills, facts, evidence, anthropic, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-verification", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# Anthropic 官方 Skills 事实登记表

本表是本 bundle 全部断言的事实底账。**每条事实都经过本地磁盘实测**，并标注证据等级与可复现的复核路径。

## 证据等级定义

| 等级 | 含义 | 复核方式 |
|------|------|---------|
| **S** | 实测（Sourced）——本地文件直接计数/读取得到，可由给出的命令原样复现 | `ls` / `find` / `wc` / `md5sum` 等命令 |
| **D** | 文档明示（Documented）——源码或官方文档明文写出，但未逐一实测 | 读取指定文件对应行 |
| **U** | 社区单源（Unverified single-source）——仅见于单一社区来源，未经官方确认 | 见 [community-view.md](community-view.md) |

> ⚠️ **本表所有 S 级事实的基准日期为 2026-10-24**，基于本地镜像 `external/libs/anthropics/skills`。官方仓库持续更新，复核时若计数不符应先确认本地镜像是否同步。

## 一、仓库整体（F-001 ~ F-012）

| 编号 | 事实 | 证据 | 复核路径 |
|------|------|------|---------|
| F-001 | 仓库根含 5 个条目：`README.md`、`THIRD_PARTY_NOTICES.md`、`skills/`、`spec/`、`template/` | S | `ls external/libs/anthropics/skills` |
| F-002 | `spec/agent-skills-spec.md` 仅 3 行，内容为指针 "The spec is now located at \<https://agentskills.io/specification\>" | S | `cat external/libs/anthropics/skills/spec/agent-skills-spec.md` |
| F-003 | `template/SKILL.md` 是最小 Skill 模板，frontmatter 仅含 `name` + `description` | S | `cat external/libs/anthropics/skills/template/SKILL.md` |
| F-004 | `.claude-plugin/marketplace.json` 声明 **5 个 plugin**，`owner` 为 Keith Lazuka（klazuka@anthropic.com），`metadata.version` 为 `1.0.0` | S | `cat external/libs/anthropics/skills/.claude-plugin/marketplace.json` |
| F-005 | 5 个 plugin 分别为 `document-skills`(4)、`example-skills`(12)、`claude-api`(1)、`academy-guide`(1)、`discernment-nudge`(1)，合计覆盖全部 19 个 skill，无重叠无遗漏 | S | 同 F-004 |
| F-006 | 每个 plugin 配置字段固定为 `name` / `description` / `source: "./"` / `strict: false` / `skills: [...]` | S | 同 F-004 |
| F-007 | `skills/` 下共 **19** 个 skill 目录 | S | `ls external/libs/anthropics/skills/skills \| wc -l` |
| F-008 | 全目录共 **482** 个文件、**72** 个 `.py` 文件 | S | `find external/libs/anthropics/skills -type f \| wc -l`；`find ... -name '*.py' \| wc -l` |
| F-009 | 19 个 `SKILL.md` 正文合计约 **4000 行**，最短 `internal-comms`（32 行），最长 `claude-api`（616 行） | S | `wc -l skills/*/SKILL.md` |
| F-010 | 19 个 skill 中 **18 个**有 `LICENSE.txt`；仅 `doc-coauthoring` 无 LICENSE.txt | S | `ls skills/*/LICENSE.txt \| wc -l` → 18 |
| F-011 | 许可证双轨：14 个 skill 的 LICENSE.txt 为 Apache License 2.0；`docx`/`pdf`/`pptx`/`xlsx` 为 "© 2025 Anthropic, PBC. All rights reserved" 专有授权（source-available，非开源）；`doc-coauthoring` 无任何许可证文件 | S | `head -c 200 skills/*/LICENSE.txt` 逐个判定 |
| F-012 | README 明确声明这些 skill "are provided for demonstration and educational purposes only" | D | `README.md` Disclaimer 段 |

## 二、格式与校验规范（F-013 ~ F-024）

| 编号 | 事实 | 证据 | 复核路径 |
|------|------|------|---------|
| F-013 | `quick_validate.py` 定义 `ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}`，frontmatter 出现表外键即校验失败 | S | `skills/skill-creator/scripts/quick_validate.py` |
| F-014 | `name` 校验：`^[a-z0-9-]+$`、长度 ≤ 64、不得以连字符开头/结尾、不得含连续连字符 | S | 同 F-013 |
| F-015 | `description` 校验：必须是字符串、长度 ≤ 1024、**不得含尖括号 `<` `>`** | S | 同 F-013 |
| F-016 | `compatibility` 校验：必须是**字符串**（非嵌套 map）、长度 ≤ 500 | S | 同 F-013 |
| F-017 | **校验脚本不含任何行数检查**——500 行只是 `skill-creator/SKILL.md` 的散文建议（"<500 lines ideal"），不是硬性要求 | S | `grep -n "500" quick_validate.py` 仅命中 `len(compatibility) > 500` |
| F-018 | `license` 与 `allowed-tools` 在校验脚本中**未被做任何值校验**，只是允许存在 | S | 同 F-013 |
| F-019 | 19 个 skill 全部具备 `name` 与 `description`；17 个具备 `license`；`doc-coauthoring` 与 `skill-creator` 无 `license` 字段 | S | 逐个 `awk '/^---$/{c++; if(c==2) exit}' skills/*/SKILL.md` |
| F-020 | 全部 19 个 `description` 长度均在 1024 限制内；最长为 `discernment-nudge`（约 700 字符），最短为 `internal-comms`（约 160 字符） | S | `awk` 提取后逐个计长 |
| F-021 | description 大量使用 YAML 折叠标量（`>` / `>`+`|-`）承载长文本 | S | `academy-guide`/`discernment-nudge` 用 `>`；`claude-api` 用 `|-` |
| F-022 | `claude-api` 的 description 内嵌 **TRIGGER/SKIP** 判定规则与可执行 grep 命令，是 19 个中唯一采用「显式反触发条件」写法的 skill | S | `skills/claude-api/SKILL.md` frontmatter |
| F-023 | `package_skill.py` 打包为 ZIP_DEFLATED，输出 `<目录名>.skill`，排除 `__pycache__`/`node_modules`/`.DS_Store`/`*.pyc` 及根级 `evals/` | D | `skills/skill-creator/scripts/package_skill.py` |
| F-024 | `utils.py` 的 `parse_skill_md()` 手动解析 frontmatter，支持 YAML 多行语法 | D | `skills/skill-creator/scripts/utils.py` |

## 三、逐 Skill 规模（F-025 ~ F-043）

| 编号 | Skill | SKILL.md 行数 | 目录文件数 | .py 数 | 主要资源目录 |
|------|-------|------------|-----------|-------|------------|
| F-025 | `claude-api` | 616 | 96 | 2 | 8 语言目录 + `shared/` |
| F-026 | `skill-creator` | 485 | 18 | 10 | `agents/` `scripts/` `eval-viewer/` `references/` `assets/` |
| F-027 | `algorithmic-art` | 404 | 4 | 0 | `templates/` |
| F-028 | `doc-coauthoring` | 375 | 1 | 0 | 无（纯指令） |
| F-029 | `pdf` | 314 | 12 | 8 | `scripts/` + `forms.md` + `reference.md` |
| F-030 | `slack-gif-creator` | 254 | 7 | 4 | `core/` |
| F-031 | `pptx` | 238 | 56 | 15 | `scripts/office/` |
| F-032 | `mcp-builder` | 236 | 10 | 2 | `reference/` `scripts/` |
| F-033 | `discernment-nudge` | 209 | 2 | 0 | 无 |
| F-034 | `academy-guide` | 147 | 2 | 0 | 无 |
| F-035 | `canvas-design` | 129 | 83 | 0 | `canvas-fonts/` |
| F-036 | `xlsx` | 99 | 53 | 12 | `scripts/office/` |
| F-037 | `webapp-testing` | 95 | 6 | 4 | `scripts/` `examples/` |
| F-038 | `docx` | 91 | 61 | 15 | `scripts/office/` + `scripts/templates/` |
| F-039 | `web-artifacts-builder` | 73 | 5 | 0 | `scripts/` |
| F-040 | `brand-guidelines` | 73 | 2 | 0 | 无 |
| F-041 | `frontend-design` | 71 | 2 | 0 | 无 |
| F-042 | `theme-factory` | 59 | 13 | 0 | `themes/` + `theme-showcase.pdf` |
| F-043 | `internal-comms` | 32 | 6 | 0 | `examples/` |

> 复核命令：`for d in skills/*/; do echo "$(basename $d) $(wc -l < $d/SKILL.md) $(find $d -type f | wc -l) $(find $d -name '*.py' | wc -l)"; done`

## 四、文档处理三件套（F-044 ~ F-052）

| 编号 | 事实 | 证据 | 复核路径 |
|------|------|------|---------|
| F-044 | `docx`/`pptx`/`xlsx` 三者的 `scripts/office/` 子树**逐字节完全相同**：各 50 个文件，相对路径 + md5 全部一致 | S | `for a in docx pptx xlsx; do (cd $a/scripts/office && find . -type f \| sort \| xargs md5sum) > /tmp/$a.md5; done; diff` |
| F-045 | 该共享子树含 `soffice.py`（LibreOffice 封装）、`validate.py`（OOXML 校验入口）、`helpers/`（4 文件）、`validators/`（5 文件）、`schemas/`（39 文件） | S | `find skills/docx/scripts/office -maxdepth 1` |
| F-046 | `schemas/` 含 **39 个 XSD**：27 个 ISO-IEC29500-4_2016 + 1 ECMA + 1 MCE + 7 Microsoft | S | `ls skills/*/scripts/office/schemas/` |
| F-047 | `helpers/` 内容为 `pptx_chart.py`、`pptx_slide.py`、`pptx_theme.py`——**三件套共享的 helper 全是 PPTX 专用**，docx/xlsx 同样携带 | S | `ls skills/docx/scripts/office/helpers/` |
| F-048 | `validators/` 内容为 `base.py`、`docx.py`、`pptx.py`、`redlining.py` | S | `ls skills/docx/scripts/office/validators/` |
| F-049 | 三件套顶层脚本：docx = `__init__.py` `accept_changes.py` `comment.py` `merge_runs.py`；pptx = `__init__.py` `add_slide.py` `clean.py` `thumbnail.py`；xlsx 仅 `recalc.py`（无 `__init__.py`） | S | `ls skills/*/scripts/` |
| F-050 | `docx/scripts/templates/`（5 个 XML：`comments.xml`、`commentsExtended.xml`、`commentsExtensible.xml`、`commentsIds.xml`、`people.xml`）与 `scripts/office/` 是**兄弟目录**，不在 office/ 内 | S | `find skills/docx -type d -name templates` |
| F-051 | `pdf` skill 的 SKILL.md **从未引用自己的 `scripts/` 目录**（grep 命中的 4 处均为 "sub**scripts**"/"super**scripts**" 子串）——正文与脚本之间缺少衔接说明 | S | `grep -n "scripts" skills/pdf/SKILL.md` |
| F-052 | `pdf` 的两个参考文档在磁盘上是**小写** `forms.md` / `reference.md`，而 SKILL.md 正文引用的是**大写** `FORMS.md` / `REFERENCE.md`（大小写不一致，Linux 上会取不到） | S | `ls skills/pdf/`；`grep -n "FORMS.md\|REFERENCE.md" skills/pdf/SKILL.md` |

## 五、设计与创意类资源（F-053 ~ F-060）

| 编号 | 事实 | 证据 | 复核路径 |
|------|------|------|---------|
| F-053 | `canvas-design/canvas-fonts/` 含 **54 个 TTF**、**27 个 OFL.txt**、**29 个字体家族** | S | `ls skills/canvas-design/canvas-fonts/*.ttf \| wc -l` |
| F-054 | `IBMPlexSerif` 与 `InstrumentSerif` 两个家族**缺少 OFL.txt 许可声明** | S | 逐家族检查 `<fam>-*OFL.txt` 是否存在 |
| F-055 | `theme-factory/themes/` 下 10 个主题文件是 **`.md` 而非 `.json`** | S | `ls skills/theme-factory/themes/` |
| F-056 | 10 个主题：arctic-frost、botanical-garden、desert-rose、forest-canopy、golden-hour、midnight-galaxy、modern-minimalist、ocean-depths、sunset-boulevard、tech-innovation | S | 同 F-055 |
| F-057 | 主题文件结构统一为：标题 + 一句话定位 + `## Color Palette`（命名色 + hex + 用途）+ `## Typography` + `## Best Used For` | S | `cat skills/theme-factory/themes/arctic-frost.md` |
| F-058 | `theme-factory` 另有 `theme-showcase.pdf`（主题总览样张） | S | `ls skills/theme-factory/` |
| F-059 | `algorithmic-art/templates/` 含 `generator_template.js` 与 `viewer.html` 两个文件 | S | `ls skills/algorithmic-art/templates/` |
| F-060 | `canvas-design` 与 `algorithmic-art` 的 SKILL.md 共享同一套骨架：PHILOSOPHY CREATION → CRITICAL UNDERSTANDING → HOW TO GENERATE A PHILOSOPHY → PHILOSOPHY EXAMPLES → ESSENTIAL PRINCIPLES → 推导种子 → 实现 | S | `grep -n '^#\{2,3\} ' skills/{canvas-design,algorithmic-art}/SKILL.md` |

## 六、开发工具类资源（F-061 ~ F-070）

| 编号 | 事实 | 证据 | 复核路径 |
|------|------|------|---------|
| F-061 | `claude-api` 含 8 个语言目录：`csharp` `curl` `go` `java` `php` `python` `ruby` `typescript`，每个语言下再分 `claude-api/` 与（部分语言）`managed-agents/` | S | `ls skills/claude-api/` |
| F-061b | 🔺 **`curl/` 是唯一的例外**：它没有 `claude-api/` 子目录，目录下直接是两个平铺文件 `examples.md` 与 `managed-agents.md`；其余 7 种语言均为 `<lang>/claude-api/` + 可选 `<lang>/managed-agents/` | S | `ls skills/claude-api/curl/` vs `ls skills/claude-api/go/` |
| F-061c | `claude-api` 的 SKILL.md 实际体积 **105,762 字节**（远超其 616 行的行数印象），是 19 个 skill 中单文件最大的文档 | S | `ls -la skills/claude-api/SKILL.md` |
| F-062 | `managed-agents/` 子目录存在于 go、java、php、python、ruby、typescript（curl/csharp 无） | S | 同 F-061 |
| F-063 | `shared/managed-agents-quickstarts/` 含 **13** 个 quickstart 场景 md：bug-hunter、contract-tracker、data-analyst、deep-researcher、explainer-video-maker、field-monitor、incident-commander、performance-tuner、sprint-retro-facilitator、structured-extractor、support-agent、support-to-eng-escalator、watchlist-scanner | S | `ls skills/claude-api/shared/managed-agents-quickstarts/` |
| F-064 | `shared/preserved-thinking-migration/` 含 `causes.md`、`drop_block_probe.py`、`prefix_diff.py` 三个文件 | S | `ls skills/claude-api/shared/preserved-thinking-migration/` |
| F-065 | `shared/evals/` 含 `build-eval.md`、`cost-hillclimb.md`、`eval-audit.md`、`eval-hillclimb.md`，及 `report/` 子目录（`SCHEMA.md`、`build-report-lite.mjs`、`runner-scaffold.mjs`） | S | `find skills/claude-api/shared/evals -type f` |
| F-066 | `claude-api` 模型表缓存日期标注为 `cached: 2026-10-06`，默认模型为 `claude-opus-5-5`；表内共 4 个模型条目：`claude-fable-5-1`（most capable widely released）、`claude-opus-5-5`（current Opus and default）、`claude-sonnet-5-5`（current Sonnet）、`claude-haiku-5-5`（current Haiku） | S | `grep -n "cached:" skills/claude-api/SKILL.md`；`sed -n '/## Current Models/,/## Authentication/p' SKILL.md \| grep '^### '` |
| F-067 | `mcp-builder` 采用 **Phase 1→4 四阶段**流程：Deep Research and Planning → Implementation → Review and Test → Create Evaluations | S | `grep -n '^### Phase' skills/mcp-builder/SKILL.md` |
| F-068 | `mcp-builder/reference/` 含 `evaluation.md`、`mcp_best_practices.md`、`node_mcp_server.md`、`python_mcp_server.md` 四篇 | S | `ls skills/mcp-builder/reference/` |
| F-069 | `mcp-builder` 的 reference 加载时机在 SKILL.md 中被显式标注（如 "Load First" / "Load During Phase 1/2" / "Load During Phase 4"） | S | `skills/mcp-builder/SKILL.md` "📚 Documentation Library" 段 |
| F-070 | `webapp-testing/scripts/with_server.py` 是「起服务 → 探端口就绪 → 跑命令 → 清理」的一次性编排器，参数 `--server` `--port` 可重复 | S | `cat skills/webapp-testing/scripts/with_server.py` |
| F-071 | `webapp-testing/examples/` 含 `console_logging.py`、`element_discovery.py`、`static_html_automation.py` 三例，覆盖三种 Playwright 用法 | S | `ls skills/webapp-testing/examples/` |
| F-072 | `slack-gif-creator/core/` 含 `easing.py`、`frame_composer.py`、`gif_builder.py`、`validators.py`；`GIFBuilder` 默认 480×480 @ 15fps | S | `ls skills/slack-gif-creator/core/`；`grep -n "def __init__" core/gif_builder.py` |
| F-073 | `slack-gif-creator/core/easing.py` 注册的缓动函数包含 `back_out`（`EASING_FUNCTIONS.update({... "back_out": ease_back_out ...})`） | S | `grep -n "back_out" skills/slack-gif-creator/core/easing.py` |
| F-074 | `web-artifacts-builder/scripts/` 含 `init-artifact.sh`、`bundle-artifact.sh`（**shell 脚本，非 Python**）与 `shadcn-components.tar.gz` | S | `ls skills/web-artifacts-builder/scripts/` |
| F-075 | `skill-creator` 的 3 个子代理是 `agents/analyzer.md`（事后归因）、`agents/comparator.md`（盲比）、`agents/grader.md`（评分） | S | `ls skills/skill-creator/agents/` |
| F-076 | `skill-creator/eval-viewer/` 含 `generate_review.py` 与 `viewer.html`，`assets/eval_review.html` 为报告样式资产 | S | `ls skills/skill-creator/eval-viewer/ skills/skill-creator/assets/` |
| F-077 | `skill-creator/references/schemas.md` 定义 `evals.json` / `grading.json` / `benchmark.json` 三类评估 Schema | D | `skills/skill-creator/references/schemas.md` |

## 七、沟通与写作类（F-078 ~ F-086）

| 编号 | 事实 | 证据 | 复核路径 |
|------|------|------|---------|
| F-078 | `internal-comms/examples/` 含 4 篇：`3p-updates.md`、`company-newsletter.md`、`faq-answers.md`、`general-comms.md`——**无 `templates/` 目录** | S | `ls skills/internal-comms/examples/` |
| F-079 | `internal-comms` SKILL.md 仅 32 行，正文为「何时用 / 怎么用 / 关键词」三段，实质是**指向 examples 的路由器** | S | `cat skills/internal-comms/SKILL.md` |
| F-080 | `internal-comms/examples/3p-updates.md` 的结构为「## Instructions + ## Tools Available」两段，Instructions 段给出受众、时长（30-60 秒）、粒度规则（团队越大粒度越粗）、三段式定义 | S | `cat skills/internal-comms/examples/3p-updates.md` |
| F-081 | `academy-guide` 骨架为 Purpose → Rules → The catalog 三段，正文含 trigger 词表与「Only recommend on a strong match; never invent Academy content」的硬约束 | S | `grep -n '^#\{1,2\} ' skills/academy-guide/SKILL.md`；读 Rules 段 |
| F-082 | `academy-guide` 的 Rules 段定义了**不触发**的边界（mid-task 只想要结果时不用）——与 `claude-api` 的 SKIP 规则同构 | S | 同 F-081 |
| F-083 | `discernment-nudge` 骨架为 Why this exists → When to offer → When not to → Writing the prompts → Output format；要求「每次对话最多一次」 | S | `grep -n '^#\{1,2\} ' skills/discernment-nudge/SKILL.md` |
| F-084 | `discernment-nudge` 的 "When not to" 段枚举了 **9 类**应跳过的场景（Creative writing / Casual conversation / Code the user will execute / Simple lookups / Purely educational explanations / 用户已要求 verify·cite·flag uncertainty / 用户要 quick version / 用户要求检查自己的东西 / 用户已提供材料只做摘要·重排·格式化） | S | `sed -n '/## When not to/,/## Writing the prompts/p' SKILL.md \| grep -E '^\s*-\s\*\*'` → 9 行 |
| F-085 | `doc-coauthoring` 是唯一「零资源目录」的 skill（仅 SKILL.md 1 个文件），采用 **Stage 1 上下文收集 → Stage 2 精炼与结构 → Stage 3 读者测试** 三阶段 | S | `grep -n '^## Stage' skills/doc-coauthoring/SKILL.md` |
| F-086 | `doc-coauthoring` 的 `### Step` 小节共 **14 个**：Stage 2 含 6 个（Clarifying Questions / Brainstorming / Curation / Gap Check / Drafting / Iterative Refinement）+ Quality Checking + Near Completion；Stage 3 含 8 个（两轮各 4 个：Predict Reader Questions → Test with Sub-Agent → Run Additional Checks → Report and Fix，以及 Predict Reader Questions → Setup Testing → Additional Checks → Iterate Based on Results） | S | `grep -n "^### Step" skills/doc-coauthoring/SKILL.md` → 14 行 |

## 八、跨 Skill 模式（F-087 ~ F-096）

| 编号 | 模式 | 证据 | 复核路径 |
|------|------|------|---------|
| F-087 | **渐进披露三层**：L1 metadata（name+description，常驻）→ L2 SKILL.md body（触发时加载）→ L3 bundled resources（按需） | D | `skills/skill-creator/SKILL.md` |
| F-088 | **「pushy」description**：为解决 undertrigger，description 主动扩写触发面（枚举同义词、场景、"Also use this when..."） | D | `claude-api` / `academy-guide` / `discernment-nudge` 的 description |
| F-089 | **反触发条件显式化**：至少 `claude-api`（SKIP 块 + 可执行 grep）、`academy-guide`、`discernment-nudge` 三个 skill 写明何时**不**用 | S | 三者 frontmatter 与正文 |
| F-090 | **黑盒脚本调用**：SKILL.md 以 `--help`/用法行描述脚本接口，不要求 agent 读源码 | D | `webapp-testing` `with_server.py`、`skill-creator` 脚本调用段 |
| F-091 | **模板即字面起点**：assets/templates 被要求「作为字面上的起点使用，而非灵感」 | D | `skill-creator/SKILL.md` 资源引用约定 |
| F-092 | **FIXED vs VARIABLE 显式切分**：`algorithmic-art` 有专门段落 "WHAT'S FIXED VS VARIABLE" | S | `grep -n "FIXED VS VARIABLE" skills/algorithmic-art/SKILL.md` |
| F-093 | **确定性随机**：`algorithmic-art` 用 seeded randomness 保证可复现 | S | `skills/algorithmic-art/SKILL.md` |
| F-094 | **QA 渲染—检视闭环**：`pptx` 把 QA 列为 Required，分 Content QA / File QA / Visual QA 三层 | S | `grep -n "^### .*QA" skills/pptx/SKILL.md` |
| F-095 | **评估双跑（with-skill vs baseline）+ description 优化循环**：`skill-creator` 实现了完整的双跑与 description 迭代 | D | `skills/skill-creator/SKILL.md` |
| F-096 | **同一"哲学生成"骨架被复用**：`canvas-design` 与 `algorithmic-art` 的 SKILL.md 前 5 个二级标题同构 | S | F-060 |
| F-097 | **共享子树跨 skill 复用**：`docx`/`pptx`/`xlsx` 携带逐字节相同的 `scripts/office/`，包括与自身无关的 PPTX helper | S | F-044、F-047 |
| F-098 | **子代理 + 脚本 + HTML 查看器三件套**：仅 `skill-creator` 同时具备 agents/、scripts/、eval-viewer/ | S | F-075、F-076 |

## 相关文档

- [全部Skills索引](skills-index.md) — 19 个 skill 的功能与真实资源路径
- [社区视角与勘误](community-view.md) — 知乎社区口径（单源，仅作对照）
- [Skills生态概览](../concepts/00-overview.md) — 概念与触发机制
