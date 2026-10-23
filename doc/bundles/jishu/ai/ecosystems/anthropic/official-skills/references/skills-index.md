---
type: reference
title: "Anthropic 官方 Skills 完整索引"
description: "19 个官方 Skills 的功能、真实资源路径、触发条件与体量速查；资源路径均经本地实测校正，可直接用于命令示例。"
tags: [skills, index, reference, official-skills, claude-code]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-verification", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# Anthropic 官方 Skills 完整索引

本文档列出 Anthropic 官方提供的全部 **19 个 Skills**。每条包含：功能描述、**实测真实**的资源路径、触发场景。

> 💡 Skills 由 Claude **自动触发**——不必记住名字，只需正常描述需求。
>
> 📌 **资源路径已按本地镜像 `external/libs/anthropics/skills` 逐一实测校正**。命令示例中的路径可直接复制使用。事实底账见 [facts.md](facts.md)。

---

## 一、API 与开发工具类（4 个）

| Skill | 一句话功能 | 真实资源路径 | 触发场景 |
|-------|-----------|-------------|---------|
| **claude-api** | Claude API/SDK 权威参考，覆盖 8 种语言 + cURL，含 Managed Agents、流式、工具调用、缓存、token 计数 | `python/claude-api/` `typescript/claude-api/` `java/claude-api/` `go/claude-api/` `csharp/claude-api/` `php/claude-api/` `ruby/claude-api/` `curl/` `shared/` | 提到 Claude/Anthropic 模型选型与定价、问 LLM 任务该怎么做、工具调用、报错排查、模型迁移 |
| **mcp-builder** | MCP 服务器开发指南，四阶段流程 + 双语言实现 + 评估脚本 | `reference/mcp_best_practices.md` `reference/python_mcp_server.md` `reference/node_mcp_server.md` `reference/evaluation.md` `scripts/evaluation.py` `scripts/connections.py` `scripts/example_evaluation.xml` `scripts/requirements.txt` | 构建 MCP server、把外部 API 接成工具、MCP 调试、评估工具描述质量 |
| **skill-creator** | 元技能：创建/改进/评估 Skill，含 3 个评估子代理、eval 脚本、description 优化器 | `agents/analyzer.md` `agents/comparator.md` `agents/grader.md` `scripts/quick_validate.py` `scripts/run_eval.py` `scripts/run_loop.py` `scripts/improve_description.py` `scripts/package_skill.py` `scripts/aggregate_benchmark.py` `scripts/generate_report.py` `scripts/utils.py` `eval-viewer/generate_review.py` `eval-viewer/viewer.html` `references/schemas.md` `assets/eval_review.html` | 从零写 Skill、改进现有 Skill、触发不准要调 description、跑评估基准、打包 .skill |
| **webapp-testing** | Playwright 驱动本地 Web 应用测试，含服务编排器与三种用法示例 | `scripts/with_server.py` `examples/console_logging.py` `examples/element_discovery.py` `examples/static_html_automation.py` | 测试网页、UI 回归、抓控制台报错、点击填表、检查页面元素 |

---

## 二、文档处理类（5 个）

| Skill | 一句话功能 | 真实资源路径 | 触发场景 |
|-------|-----------|-------------|---------|
| **docx** | Word 文档创建/编辑/分析：接受修订、加批注、合并 run、OOXML 校验 | `scripts/accept_changes.py` `scripts/comment.py` `scripts/merge_runs.py` `scripts/templates/comments.xml` `scripts/templates/commentsExtended.xml` `scripts/templates/commentsExtensible.xml` `scripts/templates/commentsIds.xml` `scripts/templates/people.xml` `scripts/office/` | 处理 .docx/.dotx、接受修订、添加批注、生成带目录/页眉的 Word 文档 |
| **pdf** | PDF 读写全流程：提取、合并、拆分、旋转、水印、表单填充、OCR | `scripts/check_bounding_boxes.py` `scripts/check_fillable_fields.py` `scripts/convert_pdf_to_images.py` `scripts/create_validation_image.py` `scripts/extract_form_field_info.py` `scripts/extract_form_structure.py` `scripts/fill_fillable_fields.py` `scripts/fill_pdf_form_with_annotations.py` `forms.md` `reference.md` | 任何提到 .pdf 的任务、提取 PDF 表单字段、填充表单、PDF 转图片、扫描件 OCR |
| **pptx** | PowerPoint 创建/编辑/分析：加页、清理、缩略图、设计规范与三层 QA | `scripts/add_slide.py` `scripts/clean.py` `scripts/thumbnail.py` `scripts/office/` | 提到 .pptx/.potx、做幻灯片、读演示文稿文本、套模板、加演讲者备注 |
| **xlsx** | 电子表格创建/编辑/分析：公式重算、选型可验证的公式、财务模型约定 | `scripts/recalc.py` `scripts/office/` | 提到 .xlsx/.xlsm/.csv/.tsv、清洗脏表格、建报表、算公式、数据透视 |
| **doc-coauthoring** | 结构化文档协作工作流：三阶段（上下文收集 → 精炼结构 → 读者测试） | 无（**纯指令 skill**，仅 SKILL.md） | 写提案/技术规格/决策文档、要大纲再成稿、需要读者视角验收 |

> 🔗 **docx / pptx / xlsx 共享同一套 `scripts/office/` 子树**（各 50 文件，逐字节相同，含 39 个 XSD）。详见 [facts.md](facts.md) F-044 ~ F-050。

---

## 三、设计与创意类（7 个）

| Skill | 一句话功能 | 真实资源路径 | 触发场景 |
|-------|-----------|-------------|---------|
| **algorithmic-art** | p5.js 算法艺术：种子随机 + 交互参数探索，生成器/查看器分离 | `templates/generator_template.js` `templates/viewer.html` | 生成艺术、creative coding、流场、粒子系统、交互式算法作品 |
| **canvas-design** | 海报/静态视觉设计（PNG/PDF），自带 54 个开源字体 | `canvas-fonts/`（54 TTF + 27 OFL，29 家族） | 做海报、生成静态设计稿、视觉作品、要用可商用字体 |
| **theme-factory** | 主题工厂：10 套预设主题，可套用到幻灯片/文档/落地页 | `themes/arctic-frost.md` `themes/botanical-garden.md` `themes/desert-rose.md` `themes/forest-canopy.md` `themes/golden-hour.md` `themes/midnight-galaxy.md` `themes/modern-minimalist.md` `themes/ocean-depths.md` `themes/sunset-boulevard.md` `themes/tech-innovation.md` `theme-showcase.pdf` | 选配色方案、统一视觉风格、给图表定色、生成新主题 |
| **frontend-design** | 前端视觉方向指导：字体、排版、克制原则，规避"模板感"默认输出 | 无（纯指令 skill） | 做 UI、重塑现有界面、要设计方向而非实现代码 |
| **brand-guidelines** | 应用 Anthropic 官方品牌色与排版规范 | 无（纯指令 skill） | 用 Anthropic 品牌色、品牌排版、对外物料统一规范 |
| **slack-gif-creator** | 生成适配 Slack 规格的动图：缓动、帧合成、GIF 构建、校验 | `core/easing.py` `core/frame_composer.py` `core/gif_builder.py` `core/validators.py` `requirements.txt` | 做 Slack GIF、动图、帧动画、表情包 |
| **web-artifacts-builder** | 复杂多组件 HTML artifact：React + Tailwind + shadcn/ui 打包成单文件 | `scripts/init-artifact.sh` `scripts/bundle-artifact.sh` `scripts/shadcn-components.tar.gz` | 需要状态管理/路由的复杂 artifact（单文件 HTML 不适用） |

---

## 四、沟通与写作类（3 个）

| Skill | 一句话功能 | 真实资源路径 | 触发场景 |
|-------|-----------|-------------|---------|
| **internal-comms** | 内部沟通写作路由器，按场景分派到 4 种文风模板 | `examples/3p-updates.md` `examples/company-newsletter.md` `examples/faq-answers.md` `examples/general-comms.md` | 写 3P 更新、公司通讯、FAQ、团队通知、事故报告 |
| **academy-guide** | Claude Academy 课程/教程推荐器，仅在强匹配时推荐，禁止编造 | 无（纯指令 skill） | 用户在学怎么用 Claude、要培训材料、问怎么给团队做推广 |
| **discernment-nudge** | 实质性回答后追加 2-3 个针对性追问，帮助用户校验事实与前提 | 无（纯指令 skill） | 给出建议/方案/分析/草稿之后、用户即将据此行动之前 |

---

## 五、体量速查

| Skill | SKILL.md 行数 | 目录文件数 | .py 数 |
|-------|------------|-----------|-------|
| claude-api | 616 | 96 | 2 |
| skill-creator | 485 | 18 | 10 |
| algorithmic-art | 404 | 4 | 0 |
| doc-coauthoring | 375 | 1 | 0 |
| pdf | 314 | 12 | 8 |
| slack-gif-creator | 254 | 7 | 4 |
| pptx | 238 | 56 | 15 |
| mcp-builder | 236 | 10 | 2 |
| discernment-nudge | 209 | 2 | 0 |
| academy-guide | 147 | 2 | 0 |
| canvas-design | 129 | 83 | 0 |
| xlsx | 99 | 53 | 12 |
| webapp-testing | 95 | 6 | 4 |
| docx | 91 | 61 | 15 |
| web-artifacts-builder | 73 | 5 | 0 |
| brand-guidelines | 73 | 2 | 0 |
| frontend-design | 71 | 2 | 0 |
| theme-factory | 59 | 13 | 0 |
| internal-comms | 32 | 6 | 0 |
| **合计** | **≈4000** | **482** | **72** |

---

## 六、10 个预设主题（theme-factory）

主题文件为 **Markdown**（非 JSON），结构统一为：标题 → 一句话定位 → `## Color Palette`（命名色 + hex + 用途）→ `## Typography` → `## Best Used For`。

| 主题 | 风格 | 适用场景 |
|------|------|---------|
| **arctic-frost** | 冷色调冰蓝灰白、清晰专业 | 医疗、科技方案、冬季运动、制药 |
| **botanical-garden** | 自然绿色植物调 | 环保、健康应用、自然主题 |
| **desert-rose** | 暖沙玫瑰粉、温暖质感 | 生活方式、时尚 |
| **forest-canopy** | 深绿沉稳 | 户外、探险、环保 |
| **golden-hour** | 黄金暖橙、柔和 | 摄影、创意、舒适界面 |
| **midnight-galaxy** | 深空蓝紫、暗色 | 开发者工具、暗色主题 |
| **modern-minimalist** | 黑白灰高对比极简 | 极简设计、作品集 |
| **ocean-depths** | 深海蓝青、深邃 | 金融、企业应用 |
| **sunset-boulevard** | 日落紫红橙、活力渐变 | 娱乐、营销、活力品牌 |
| **tech-innovation** | 科技蓝亮青、未来感 | AI、创新项目、开发者平台 |

---

## 七、插件市场分组

`.claude-plugin/marketplace.json` 将 19 个 skill 组织为 **5 个 plugin**：

| Plugin | Skill 数 | Skills |
|--------|---------|--------|
| **document-skills** | 4 | xlsx, docx, pptx, pdf |
| **example-skills** | 12 | algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, frontend-design, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing |
| **claude-api** | 1 | claude-api |
| **academy-guide** | 1 | academy-guide |
| **discernment-nudge** | 1 | discernment-nudge |

安装方式：

```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

---

## 相关文档

- [事实登记表](facts.md) — F-001~F-098 逐条实测底账
- [社区视角与勘误](community-view.md) — 知乎社区口径对照（单源）
- [Skills生态概览](../concepts/00-overview.md) — 概念、触发机制与生态定位
- [SKILL.md格式规范](../concepts/01-skill-format.md) — frontmatter 字段与编写规范
