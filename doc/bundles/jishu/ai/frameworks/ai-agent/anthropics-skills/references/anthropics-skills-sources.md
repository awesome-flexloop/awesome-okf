---
type: Reference
title: Anthropic Skills 参考实现源码信源登记
description: Anthropic Agent Skills 参考实现仓库结构、SKILL.md 格式规范、Progressive Disclosure 加载机制、.skill 打包格式、19 个 Skill 清单与 Python 工具脚本信源
tags: [anthropic-skills, agent-skills, skill.md, claude-code, progressive-disclosure, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T23:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: anthropic-skills-github
    resource: https://github.com/anthropics/skills
    title: Anthropic Skills GitHub 仓库
  - id: agent-skills-spec
    resource: https://agentskills.io/specification
    title: Agent Skills 开放规范
---

# Anthropic Skills 参考实现源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | Anthropic Skills（参考实现） |
| 描述 | Anthropic 官方 Agent Skills 参考实现仓库，包含 19 个可用 Skill 和 Skill 创建/验证/打包工具 |
| 仓库 | <https://github.com/anthropics/skills> |
| 规范地址 | <https://agentskills.io/specification> |
| Skill 总数 | 19 个 |
| Python 文件数 | 72 个（各 Skill 自带领域工具脚本） |
| 源码位置 | `d:\spaces\SpecWeave\external\libs\anthropics\skills\` |

## 目录结构

```
skills/
├── README.md                    # 项目说明、基础 Skill 创建教程
├── THIRD_PARTY_NOTICES.md       # 第三方声明
├── .gitignore
├── .claude-plugin/
│   └── marketplace.json         # Claude Code 插件市场配置（5 个 plugin 分组）
├── spec/
│   └── agent-skills-spec.md     # 规范指针（指向 agentskills.io）
├── template/
│   └── SKILL.md                 # 最小 Skill 模板（6行）
└── skills/                      # 19 个 Skill 实现目录
    ├── academy-guide/            # Claude Academy 课程推荐
    ├── algorithmic-art/         # p5.js 算法艺术生成
    ├── brand-guidelines/        # Anthropic 品牌色彩/字体
    ├── canvas-design/           # Canvas 视觉艺术设计
    ├── claude-api/              # Claude API/SDK 参考文档（8 语言 SDK，最大 skill）
    ├── discernment-nudge/       # 实质性回答后的针对性追问
    ├── doc-coauthoring/         # 文档协作写作工作流
    ├── docx/                    # Word 文档创建/编辑/分析（15 个 Python 脚本）
    ├── frontend-design/         # 前端 UI 设计指导
    ├── internal-comms/          # 内部沟通文档写作
    ├── mcp-builder/             # MCP 服务器开发指南
    ├── pdf/                     # PDF 处理（8 个 Python 脚本）
    ├── pptx/                    # PowerPoint 创建/编辑（15 个 Python 脚本）
    ├── skill-creator/           # 元技能：创建/改进/评估 Skill（10 个 Python 脚本）
    ├── slack-gif-creator/       # Slack 优化 GIF 动画（4 个 Python 脚本）
    ├── theme-factory/           # 主题/样式工厂（10 预设主题）
    ├── web-artifacts-builder/   # React+Tailwind+shadcn HTML 构件
    ├── webapp-testing/          # Playwright Web 应用测试（4 个 Python 脚本）
    └── xlsx/                    # Excel 电子表格（12 个 Python 脚本）
```

## 19 个 Skill 清单

| # | Skill 名 | 类别 | Python 脚本数 | 说明 |
|---|---------|------|-------------|------|
| 1 | `academy-guide` | 企业沟通 | 0 | Claude Academy 课程推荐纯指令 |
| 2 | `algorithmic-art` | 创意设计 | 0 | p5.js 算法艺术生成，含 templates/ |
| 3 | `brand-guidelines` | 创意设计 | 0 | Anthropic 品牌色彩/字体规范 |
| 4 | `canvas-design` | 创意设计 | 0 | Canvas 视觉艺术，含 canvas-fonts/（54 TTF） |
| 5 | `claude-api` | 开发技术 | 2 | Claude API/SDK 文档（8 语言 SDK + shared/ 参考文件） |
| 6 | `discernment-nudge` | 企业沟通 | 0 | 实质性回答后追加针对性追问纯指令 |
| 7 | `doc-coauthoring` | 企业沟通 | 0 | 文档协作写作纯指令工作流（唯一无 LICENSE.txt） |
| 8 | `docx` | 文档处理 | 15 | Word 文档（accept_changes/comment/merge_runs + office/ + templates/） |
| 9 | `frontend-design` | 创意设计 | 0 | 前端 UI 设计哲学与原则 |
| 10 | `internal-comms` | 企业沟通 | 0 | 内部沟通写作纯指令（正文仅 32 行，路由到 examples/） |
| 11 | `mcp-builder` | 开发技术 | 2 | MCP 服务器开发（连接测试/评估脚本 + reference/ 4 篇） |
| 12 | `pdf` | 文档处理 | 8 | PDF 提取/合并/拆分/表单/OCR |
| 13 | `pptx` | 文档处理 | 15 | PowerPoint（add_slide/clean/thumbnail + office/） |
| 14 | `skill-creator` | 开发技术 | 10 | 元技能：创建/验证/评估/打包/优化 Skill（+ 3 个子代理 + eval-viewer/） |
| 15 | `slack-gif-creator` | 创意设计 | 4 | GIF 构建/验证/缓动/帧合成（含 core/gif_builder.py） |
| 16 | `theme-factory` | 创意设计 | 0 | 10 个预设主题（**Markdown 格式**） |
| 17 | `web-artifacts-builder` | 开发技术 | 0 | React+Tailwind+shadcn 复杂 HTML 构件（shell 脚本） |
| 18 | `webapp-testing` | 开发技术 | 4 | Playwright 服务器管理+示例 |
| 19 | `xlsx` | 文档处理 | 12 | Excel（recalc + office/helpers + office/validators） |

> 📌 **共享子树**：docx / pptx / xlsx 三者的 `scripts/office/` **逐字节完全相同**（各 50 文件，含 39 个 XSD：27 ISO-IEC 29500-4 + 1 ECMA + 1 MCE + 7 Microsoft）。详细拆解见 [official-skills bundle 的文档处理类详解](../../../../ecosystems/anthropic/official-skills/concepts/05-document-skills.md)。

## Skill 目录结构规范

每个 Skill 是一个自包含文件夹，标准结构：

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter (name, description 必需)
│   └── Markdown instructions
└── Bundled Resources (可选)
    ├── scripts/        # 确定性/重复性任务的可执行代码
    ├── references/     # 按需加载的参考文档
    ├── assets/         # 输出中使用的文件（模板、图标、字体）
    ├── examples/       # 使用示例
    ├── agents/         # 子代理指令（仅 skill-creator 使用）
    ├── eval-viewer/    # 评估查看器（仅 skill-creator 使用）
    ├── core/           # 核心 Python 模块（如 slack-gif-creator）
    ├── templates/      # HTML/JS 模板（如 algorithmic-art）
    ├── canvas-fonts/   # 字体资源（如 canvas-design）
    └── LICENSE.txt     # 许可证文件
```

## 关键文件清单

### 根级配置与规范

| 文件 | 内容 |
|------|------|
| `README.md` | 项目总览、基础 Skill 创建教程 |
| `.claude-plugin/marketplace.json` | 插件市场配置，将 19 个 Skill 分为 5 个 plugin |
| `spec/agent-skills-spec.md` | 规范指针，内容仅一行指向 `https://agentskills.io/specification` |
| `template/SKILL.md` | 最小可用 Skill 模板（6 行） |

### skill-creator（元技能，最权威格式定义）

| 文件 | 内容 |
|------|------|
| `skills/skill-creator/SKILL.md` | Skill 解剖学、写作规范、Progressive Disclosure、评估流程、打包说明、多环境适配（~500 行） |
| `skills/skill-creator/scripts/quick_validate.py` | Frontmatter 验证逻辑、ALLOWED_PROPERTIES 定义、name/description 约束 |
| `skills/skill-creator/scripts/package_skill.py` | .skill ZIP 打包逻辑、排除规则（__pycache__/node_modules/.DS_Store/*.pyc/evals/） |
| `skills/skill-creator/scripts/utils.py` | `parse_skill_md()` 函数：手动解析 SKILL.md frontmatter（支持多行 YAML 语法） |
| `skills/skill-creator/references/schemas.md` | 评估 JSON Schema 定义（evals.json/grading.json/benchmark.json） |

### 文档处理三套件共享模块

> 🔑 **关键事实**：docx / pptx / xlsx 三者的 `scripts/office/` 子树**逐字节完全相同**（逐文件 md5 比对一致），各 50 个文件。

| 文件 | 内容 |
|------|------|
| `skills/{docx,pptx,xlsx}/scripts/office/helpers/` | OOXML 辅助：`pptx_chart.py`、`pptx_slide.py`、`pptx_theme.py`（**三件套共享的是 PPTX 专用 helper**） |
| `skills/{docx,pptx,xlsx}/scripts/office/validators/` | XSD 验证：`base.py`、`docx.py`、`pptx.py`、`redlining.py` |
| `skills/{docx,pptx,xlsx}/scripts/office/soffice.py` | LibreOffice 封装（沙箱环境适配） |
| `skills/{docx,pptx,xlsx}/scripts/office/validate.py` | OOXML 文件验证入口 |
| `skills/{docx,pptx,xlsx}/scripts/office/schemas/` | **39 个 XSD**：27 ISO-IEC29500-4_2016 + 1 ECMA + 1 MCE + 7 Microsoft |
| `skills/docx/scripts/` | 4 个顶层脚本：`accept_changes.py`、`comment.py`、`merge_runs.py`、`__init__.py` |
| `skills/docx/scripts/templates/` | 5 个 Word 批注 XML：`comments.xml`、`commentsExtended.xml`、`commentsExtensible.xml`、`commentsIds.xml`、`people.xml`（**与 office/ 是兄弟目录**） |
| `skills/pptx/scripts/` | 4 个顶层脚本：`add_slide.py`、`clean.py`、`thumbnail.py`、`__init__.py` |
| `skills/xlsx/scripts/` | 1 个顶层脚本：`recalc.py`（**无 `__init__.py`**，与另两者不对称） |

### 其他 Skill 的核心代码

| 文件 | 内容 |
|------|------|
| `skills/slack-gif-creator/core/gif_builder.py` | `GIFBuilder` 类：add_frame/add_frames/optimize_colors/deduplicate_frames/save（依赖 PIL/imageio/numpy，默认 480×480 @ 15fps） |
| `skills/slack-gif-creator/core/easing.py` | 缓动函数库，经 `EASING_FUNCTIONS.update({...})` 注册（含 `back_out`） |
| `skills/pdf/scripts/` | 8 个 PDF 处理脚本 |
| `skills/webapp-testing/scripts/with_server.py` | 环境编排器：起服务 → 探端口就绪 → 跑命令 → 清理（`--server`/`--port` 可重复） |
| `skills/webapp-testing/examples/` | 3 个可执行示例：`console_logging.py`、`element_discovery.py`、`static_html_automation.py` |
| `skills/mcp-builder/scripts/` | 2 个连接测试/评估脚本（`evaluation.py` 用 XML `<summary>` 标签约束输出结构） |

## Plugin/Marketplace 分组

`.claude-plugin/marketplace.json` 将 19 个 Skill 分为 5 个 plugin：

| Plugin | Skills | 说明 |
|--------|--------|------|
| **document-skills** | xlsx, docx, pptx, pdf | 文档处理套件（4 个） |
| **example-skills** | algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, frontend-design, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing | 示例技能集（12 个） |
| **claude-api** | claude-api | 独立插件（1 个） |
| **academy-guide** | academy-guide | 独立插件（1 个） |
| **discernment-nudge** | discernment-nudge | 独立插件（1 个） |

每个 plugin 配置：`name`、`description`、`source: "./"`、`strict: false`、`skills: [paths...]`。
marketplace 元数据：`name: anthropic-agent-skills`、`owner: Keith Lazuka`、`metadata.version: 1.0.0`。

## SKILL.md 格式规范

### YAML Frontmatter

**必需字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `name` | string | kebab-case（`^[a-z0-9-]+$`），不以连字符开头/结尾，无连续连字符，最长 64 字符 | Skill 唯一标识符 |
| `description` | string | 最长 1024 字符，禁止尖括号 `<>` | 功能描述 + 触发条件（Skill 触发的主要机制） |

**允许的可选字段**（共 6 个）：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `license` | string | — | 许可证声明 |
| `allowed-tools` | array | — | 允许的工具列表 |
| `metadata` | object | — | 元数据字典 |
| `compatibility` | string | 最长 500 字符 | 兼容性要求 |

ALLOWED_PROPERTIES 定义在 `quick_validate.py:42-43`：
```python
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
```

### 最小模板（template/SKILL.md）

```markdown
---
name: template-skill
description: Replace with description of the skill and when Claude should use it.
---

# Insert instructions below
```

### description 设计原则

- 必须同时包含"做什么"和"何时使用"
- 建议写得 "pushy"（主动/激进），解决 "undertrigger"（触发不足）问题
- 支持 YAML 多行语法（`>`, `|`, `>-`, `|-`）
- 简单单步查询可能不会触发 Skill；复杂多步或专业查询才能可靠触发

## Progressive Disclosure（三级渐进式加载）

| 级别 | 内容 | 加载时机 | 大小 |
|------|------|---------|------|
| Level 1 | Metadata（name + description） | 始终在上下文中 | ~100 词 |
| Level 2 | SKILL.md body（主体指令） | Skill 触发时加载 | 理想 <500 行 |
| Level 3 | Bundled resources（scripts/references/assets/...） | 按需加载 | 无限制 |

**长度指南**：
- SKILL.md 推荐 ≤500 行（**建议，非硬性要求**——`quick_validate.py` 不含任何行数检查；官方 `claude-api` 616 行、`skill-creator` 485 行、`algorithmic-art` 404 行均可正常加载）
- >500 行时增加分层结构，添加 references 指引
- 大参考文件(>300 行)应包含目录
- reference 文件应明确标注何时读取（实测仅 `mcp-builder` 完整做到标注 "Load First" / "Load During Phase 1/2" / "Load During Phase 4"）
- 多领域支持按变体组织（如 aws.md, gcp.md, azure.md）

**资源引用约定**：
- `scripts/xxx.py`：作为黑盒脚本直接调用，建议先 `--help` 再决定是否读源码
- `references/xxx.md`：明确说明何时加载（如 "Load during Phase 1/2"）
- `assets/xxx`：作为字面上的起点使用，而非灵感
- 所有路径相对于 skill 目录

## .skill 打包格式

- **本质**：ZIP 压缩包，使用 `zipfile.ZIP_DEFLATED` 压缩
- **打包命令**：`python scripts/package_skill.py <skill-folder> [output-dir]`（在 `skills/skill-creator/` 目录下执行——脚本用 `from scripts.quick_validate import validate_skill` 相对导入）
- **输出文件名**：`<skill-name>.skill`（使用**目录名**，非 frontmatter name）
- **前置验证**：打包前自动运行 `validate_skill()`，校验失败直接中止并打印修复提示
- **排除规则**：
  - 目录：`__pycache__`、`node_modules`
  - 根目录专属：`evals/`（**仅在 skill 根目录这一层排除**，嵌套更深的不排除）
  - 文件：`.DS_Store`
  - Glob：`*.pyc`

## Python 代码模式

仓库中 **无通用 Skill 运行时/加载器**。72 个 Python 文件全部是各 Skill 自带的领域工具脚本：
- 不存在通用 Skill 加载器/解析器（除 skill-creator 中的验证/打包工具外）
- 不存在 Skill 执行引擎或运行时框架
- 不存在插件系统或动态发现机制
- 使用模式：Claude（LLM）读取 SKILL.md 指令后，按指令调用 scripts/ 中的脚本作为外部命令/模块

**两种脚本调用方式**：
1. **命令行调用**：`python scripts/xxx.py args...`（如 recalc.py、validate.py、package_skill.py）
2. **模块导入**：`from core.gif_builder import GIFBuilder`（如 slack-gif-creator）

## Skill 写作风格原则

1. **使用祈使句**（imperative form）
2. **解释"为什么"**而非生硬的 MUST 约束
3. **利用 theory of mind**，让 Skill 通用而非绑定特定示例
4. **避免过度约束**：发现写 ALWAYS/NEVER 全大写时应重构为解释原因
5. **输出格式定义**使用 "ALWAYS use this exact template:" 模式明确模板

## 安全原则（Lack of Surprise）

Skill 不得包含恶意软件、漏洞利用代码或危及系统安全的内容。Skill 的内容不应在意图上让用户感到意外。"Roleplay as an XYZ" 类内容可以接受。

## Skill 评估体系（skill-creator）

- **evals/evals.json**：测试用例定义（skill_name, evals 数组含 id/prompt/expected_output/files/expectations）
- **双 slave 运行**：with_skill vs without_skill/old_skill 对比
- **grading.json**：评分结果（expectations 数组含 text/passed/evidence）
- **benchmark.json**：基准测试汇总（pass_rate/time/tokens 的 mean/stddev/min/max）
- **盲比支持**：comparator.md + analyzer.md 实现 A/B 盲比
- **Description 优化**：自动生成 20 个触发测试 query，运行优化循环改进 description

### Eval 结果目录结构

```
<skill-name>-workspace/
└── iteration-N/
    ├── eval-<descriptive-name>/
    │   ├── with_skill/outputs/
    │   ├── without_skill/outputs/ (或 old_skill/)
    │   ├── eval_metadata.json
    │   ├── grading.json
    │   └── timing.json
    ├── benchmark.json
    ├── benchmark.md
    └── feedback.json
```

## 多环境适配

skill-creator 区分三种运行环境：

| 环境 | 子 agent | 浏览器 | benchmark | description 优化 | 打包 |
|------|---------|--------|-----------|-----------------|------|
| **Claude Code** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Claude.ai** | ✗ | ✗ | 串行 | ✗ | ✗ | ✓ |
| **Cowork（无头）** | ✓（无 display） | ✗ | ✓ | ✗ | viewer `--static` 静态 HTML | ✓ |

## 核心函数索引

| 函数 | 文件 | 说明 |
|------|------|------|
| `validate_skill()` | `scripts/quick_validate.py` | 完整 SKILL.md 验证（10 步流程） |
| `parse_skill_md(skill_path)` | `scripts/utils.py` | 解析 SKILL.md 返回 (name, description, full_content) |
| `package_skill()` | `scripts/package_skill.py` | 验证并打包为 .skill ZIP 文件 |
| `GIFBuilder` 类 | `slack-gif-creator/core/gif_builder.py` | GIF 构建器：帧添加/颜色量化/去重/保存 |
