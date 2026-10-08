---
type: Concept
title: SKILL.md 格式规范
description: Anthropic Skills的SKILL.md文件格式标准——6个允许的YAML frontmatter字段（name/description/license/allowed-tools/metadata/compatibility）、kebab-case命名约束、description触发机制设计、body 4种内容模式（纯指令/代码参考/设计指导/混合型）、指令写作风格原则、<500行长度指南与安全原则。
tags: [anthropics-skills, skill, format, frontmatter, yaml, specification, markdown, validation]
generated: { by: "agent:okf-doc-generator", at: "2026-08-22T22:44:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: ../../../../../../external/libs/models/ai/anthropics/skills/README.md
    title: 项目说明
  - id: skill-creator
    resource: ../../../../../../external/libs/models/ai/anthropics/skills/skills/skill-creator/SKILL.md
    title: Skill创建元技能（格式权威定义）
  - id: quick-validate
    resource: ../../../../../../external/libs/models/ai/anthropics/skills/skills/skill-creator/scripts/quick_validate.py
    title: Frontmatter验证脚本
  - id: utils
    resource: ../../../../../../external/libs/models/ai/anthropics/skills/skills/skill-creator/scripts/utils.py
    title: SKILL.md解析工具
  - id: template
    resource: ../../../../../../external/libs/models/ai/anthropics/skills/template/SKILL.md
    title: 最小Skill模板
---

# SKILL.md 格式规范

SKILL.md 是 Anthropic Agent Skills 系统中每个技能的核心定义文件。它以 YAML frontmatter 声明元数据，Markdown 正文提供操作指令。格式规范由 skill-creator 元技能定义，`quick_validate.py` 脚本强制执行格式校验，确保所有 Skill 在结构上一致、可被加载器可靠解析。

## 设计原理

1. **元数据驱动触发**：description 字段是 Skill 触发的主要机制，必须同时包含"做什么"和"何时使用"
2. **最小强制约束**：仅 name 和 description 为必填，其余字段可选，保持创建门槛低
3. **长度受控**：SKILL.md 正文理想 <500 行，超长内容通过 references/ 外置实现渐进式加载
4. **祈使句写作**：指令使用祈使句、解释"为什么"而非硬性 MUST 约束，利用 theory of mind 增强通用性
5. **安全底线**：禁止恶意内容，遵循 Lack of Surprise 原则

## 文件结构总览

```mermaid
graph TD
    SKILL["SKILL.md"] --> FM["YAML Frontmatter<br/>--- 分隔"]
    SKILL --> BODY["Markdown Body<br/>操作指令"]

    FM --> REQ["必填字段<br/>(2个)"]
    FM --> OPT["可选字段<br/>(4个)"]

    REQ --> R1["name: kebab-case<br/>技能唯一标识"]
    REQ --> R2["description: <1024字符<br/>功能+触发条件"]

    OPT --> O1["license<br/>许可证声明"]
    OPT --> O2["allowed-tools<br/>允许的工具列表"]
    OPT --> O3["metadata<br/>元数据字典"]
    OPT --> O4["compatibility<br/>兼容性要求<500字符"]

    BODY --> MODES["4种内容模式"]
    MODES --> M1["纯指令型<br/>doc-coauthoring"]
    MODES --> M2["代码参考型<br/>pdf/xlsx/docx"]
    MODES --> M3["设计指导型<br/>frontend-design"]
    MODES --> M4["混合型<br/>skill-creator"]

    style FM fill:#06b6d4,color:#000
    style REQ fill:#ef4444,color:#fff
    style BODY fill:#22c55e,color:#000
```

## YAML Frontmatter 规范

### 允许的完整字段集

根据 `quick_validate.py`，frontmatter 共允许 6 个字段：

```python
# quick_validate.py L42-L43
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
```

任何不在此集合中的字段都会导致验证失败（`unexpected property` 错误）。

### 必填字段详解

**1. name**

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 是 |
| 格式 | kebab-case（正则 `^[a-z0-9-]+$`） |
| 最大长度 | 64 字符 |
| 约束 | 不能以连字符开头/结尾，不能包含连续连字符 |

```yaml
# ✅ 正确
name: pdf
name: web-app-testing
name: mcp-builder

# ❌ 错误
name: PDF           # 含大写
name: my_skill      # 含下划线
name: -skill-       # 连字符开头/结尾
name: my--skill     # 连续连字符
```

**2. description**

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 是 |
| 最大长度 | 1024 字符 |
| 禁止字符 | `<` 和 `>`（尖括号） |
| 核心功能 | **Skill 触发的主要机制** |

```yaml
# ✅ Good：同时包含做什么+何时使用，语气主动(pushy)
description: >
  Use this skill when the user asks to create, edit, analyze, or extract data
  from PDF files. Handles merging, splitting, form filling, OCR, and text extraction.
  Trigger for any PDF-related task, including "read this PDF" or "extract pages".

# ❌ Bad：仅描述功能，无触发上下文
description: PDF processing tool.
```

### description 的触发设计

description 是 Skill 被自动激活的关键。设计原则：

1. **Pushy（主动/激进）**：写得积极一些，解决 "undertrigger"（触发不足）问题
2. **双信息**：必须同时说明"做什么"和"何时使用"
3. **覆盖变体**：包含用户可能使用的各种表达方式
4. **复杂任务更可靠**：简单的单步查询（如 "read this PDF"）可能不触发 Skill；复杂多步或专业查询才能可靠触发

支持 YAML 多行语法（`>`, `|`, `>-`, `|-`），适合长 description。

### 可选字段详解

**3. license**

```yaml
# 专有许可证
license: Proprietary. LICENSE.txt has complete terms

# 引用文件
license: Complete terms in LICENSE.txt
```

**4. allowed-tools**

声明 Skill 执行所需的工具白名单。若 Skill 依赖特定工具（如 Bash、WebFetch），在此声明。

**5. metadata**

```yaml
metadata:
  hermes:
    tags: [ADHD, Output Style, Productivity]
    category: productivity
```

用于存储任意结构化元数据，如分类标签、平台特定配置等。

**6. compatibility**

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 最大长度 | 500 字符 |

声明 Skill 的运行环境兼容性要求。

### Frontmatter 示例

以最小模板为例：

```yaml
---
name: template-skill
description: Replace with description of the skill and when Claude should use it.
---

# Insert instructions below
```

以实际 Skill（pdf）为例：

```yaml
---
name: pdf
description: >
  Use when the user needs to work with PDF files: extract text, merge/split PDFs,
  fill forms, perform OCR, or convert formats. Trigger on any PDF-related request.
license: Proprietary. LICENSE.txt has complete terms.
---
```

## 验证流程

`quick_validate.py` 中的 `validate_skill()` 函数执行 10 步验证：

```mermaid
graph LR
    V["validate_skill()"] --> V1["1. SKILL.md存在?"]
    V1 --> V2["2. 以---开头?"]
    V2 --> V3["3. 提取frontmatter<br/>正则^---\\n(.*?)\\n---"]
    V3 --> V4["4. yaml.safe_load()解析"]
    V4 --> V5["5. 结果是dict?"]
    V5 --> V6["6. 无非预期字段?"]
    V6 --> V7["7. name/description存在?"]
    V7 --> V8["8. name格式/长度校验"]
    V8 --> V9["9. description长度/字符校验"]
    V9 --> V10["10. compatibility长度校验<br/>(如存在)"]

    style V fill:#8b5cf6,color:#fff
```

```python
# quick_validate.py 验证流程核心代码
def validate_skill(skill_path: Path) -> list[str]:
    errors = []
    # 1. 检查文件存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return [f"SKILL.md not found in {skill_path}"]

    content = skill_md.read_text(encoding="utf-8")

    # 2. 检查开头
    if not content.startswith("---\n"):
        errors.append("SKILL.md must start with ---")
        return errors

    # 3. 提取frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append("Could not parse YAML frontmatter")
        return errors

    # 4. YAML解析
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return errors

    # 5. 类型检查
    if not isinstance(data, dict):
        errors.append("Frontmatter must be a YAML dictionary")
        return errors

    # 6. 字段检查...
    return errors
```

## SKILL.md Body 内容模式

17 个内置 Skill 的 body 呈现 4 种内容模式：

```mermaid
graph TB
    BODY["Body内容模式"] --> INSTR["纯指令型"]
    BODY --> CODE["代码参考型"]
    BODY --> DESIGN["设计指导型"]
    BODY --> HYBRID["混合型"]

    INSTR --> I1["doc-coauthoring<br/>internal-comms"]
    I1 --> I2["分步骤工作流<br/>触发条件→操作步骤→退出条件"]

    CODE --> C1["pdf, xlsx<br/>docx, pptx"]
    C1 --> C2["代码示例<br/>工具选择决策表<br/>常见陷阱/QA"]

    DESIGN --> D1["frontend-design<br/>canvas-design<br/>algorithmic-art<br/>brand-guidelines"]
    D1 --> D2["设计哲学<br/>创意原则<br/>工艺流程"]

    HYBRID --> H1["skill-creator<br/>mcp-builder<br/>claude-api"]
    H1 --> H2["工作流+代码参考<br/>+子资源引用<br/>+评估体系"]

    style INSTR fill:#22c55e,color:#000
    style CODE fill:#06b6d4,color:#000
    style DESIGN fill:#f97316,color:#000
    style HYBRID fill:#8b5cf6,color:#fff
```

### 按功能域分类

| 类别 | Skills | 特征 |
|------|--------|------|
| 创意设计类 | algorithmic-art, canvas-design, brand-guidelines, frontend-design, theme-factory, slack-gif-creator | 输出视觉产物，含字体/模板资源，强调工艺感 |
| 文档处理类 | pdf, docx, pptx, xlsx | Source-available，专有许可证，含 office/ 共享模块，依赖 LibreOffice |
| 开发技术类 | claude-api, mcp-builder, webapp-testing, web-artifacts-builder, skill-creator | 面向开发者，大量参考文档和代码示例 |
| 企业沟通类 | doc-coauthoring, internal-comms | 纯指令型工作流，无 scripts，指导写作流程 |

## 指令写作风格原则

skill-creator 的 SKILL.md 定义了以下写作原则：

### 1. 使用祈使句（Imperative Form）

```markdown
<!-- ✅ Good -->
Load references only when needed. Call scripts as black-box commands.

<!-- ❌ Bad -->
You should always consider whether to load references.
```

### 2. 解释"为什么"

> "Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs"

```markdown
<!-- ✅ Good -->
Keep SKILL.md under 500 lines because longer files consume more context window
on every invocation, leaving less room for the actual task.

<!-- ❌ Bad -->
SKILL.md MUST NOT exceed 500 lines. This is a hard requirement.
```

### 3. 利用 Theory of Mind

让 Skill 具有通用性，而非绑定到特定示例。模型能推断出如何将原则应用到新情况。

### 4. 避免过度约束

当发现自己写 ALWAYS/NEVER 全大写时是黄色警告标志，应重构为解释原因。

### 5. 明确输出格式

使用 "ALWAYS use this exact template:" 模式定义输出模板（这是少数可使用 ALWAYS 的场景）：

```markdown
ALWAYS use this exact template for the output:
```markdown
# Analysis Report
## Summary
{summary}
## Findings
{findings}
```
```

## 长度指南

| 指标 | 建议值 |
|------|--------|
| SKILL.md 正文 | < 500 行 |
| 参考文件 | > 300 行应包含目录 |
| 辅助脚本 | 作为黑盒调用，不加载到上下文 |

超过 500 行时：
1. 增加分层结构
2. 将大段内容抽取到 `references/` 目录
3. 在 SKILL.md 中明确标注何时读取哪个参考文件
4. 多框架支持时按变体组织（如 `aws.md`、`gcp.md`、`azure.md`），Claude 只读取相关文件

## 安全原则（Lack of Surprise）

- Skill 不得包含恶意软件、漏洞利用代码
- Skill 内容不应在意图上让用户感到意外
- "Roleplay as an XYZ" 类内容是可接受的
- 禁止通过 frontmatter 注入恶意配置
- 生成后的 Skill 需经 `scan_generated_skill.py` 扫描检测 prompt 注入

## 多环境适配

skill-creator 明确区分三种运行环境的差异：

| 环境 | 子 Agent | 浏览器 | Benchmark | Description 优化 | 打包 |
|------|---------|--------|-----------|-----------------|------|
| Claude Code | ✅ | ✅ | ✅ | ✅ | ✅ |
| Claude.ai | ❌ | ❌（串行执行） | ❌ | ❌ | ✅ |
| Cowork（无头） | ✅ | ❌（静态HTML输出） | ❌ | ❌ | ✅ |

所有环境均支持打包功能（`package_skill.py` 仅需 Python 和文件系统）。

## 最小可用模板

`template/SKILL.md` 是官方最小模板（6 行）：

```markdown
---
name: template-skill
description: Replace with description of the skill and when Claude should use it.
---

# Insert instructions below
```

## 相关概念

- [渐进式加载机制](progressive-loading.md) — Metadata→Body→Resources 三级加载
- [Skill 打包格式](skill-packaging.md) — .skill ZIP 打包与排除规则
- [评估基准框架](eval-benchmark-framework.md) — skill-creator 内置的 eval/benchmark/blind comparison
