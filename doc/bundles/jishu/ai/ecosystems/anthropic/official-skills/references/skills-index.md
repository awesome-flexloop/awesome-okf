---
type: reference
title: "Anthropic 官方 Skills 完整索引"
tags: [skills, index, reference, official-skills, claude-code]
---

# Anthropic 官方 Skills 完整索引

本文档列出 Anthropic 官方提供的全部 **19 个 Skills**，按功能分类组织。每个 Skill 包含：名称、一句话功能描述、主要资源目录、典型触发场景。

> 💡 Skills 会被 Claude Code **自动触发**——你不需要记住它们的名字，只需正常描述你的需求，匹配的 Skill 会自动加载。

---

## 一、API 与开发工具类（4 个）

此类 Skills 专注于 API 集成、开发工具、测试自动化、元能力（创建其他 Skill）。

| Skill 名称 | 一句话功能描述 | 主要资源 | 触发关键词/场景 |
|------------|---------------|---------|----------------|
| **claude-api** | Claude API/SDK 多语言权威参考，覆盖 Python/TS/Java/Go/C#/PHP/Ruby/cURL，含 Managed Agents、流式、工具调用、MCP、缓存、token 计数、模型迁移指南 | `references/python/`、`references/typescript/`、`references/java/`、`references/go/`、`references/csharp/`、`references/php/`、`references/ruby/`、`references/curl/` | 询问如何调用 Claude API、写 SDK 代码、工具调用、流式传输、API 报错排查、从旧版本迁移、提到 anthropic SDK 导入 |
| **mcp-builder** | MCP（Model Context Protocol）服务器构建工具，提供 Python/Node.js 参考实现、最佳实践、评估脚本 | `references/python-mcp.md`、`references/node-mcp.md`、`scripts/eval_mcp.py`、`examples/` | 写 MCP 服务器、构建 Model Context Protocol 工具、添加自定义工具到 Claude、MCP 调试、提到 MCP server 开发 |
| **skill-creator** | 创建/修改/评估 Skills 的元技能，含 analyzer/comparator/grader 三个子代理、eval 脚本、description 优化器 | `agents/analyzer.md`、`agents/comparator.md`、`agents/grader.md`、`scripts/quick_validate.py`、`scripts/run_eval.py`、`scripts/run_loop.py`、`scripts/improve_description.py`、`scripts/eval-viewer.py` | 创建新 Skill、改进 Skill、调试 Skill 触发问题、评估 Skill 质量、写 SKILL.md |
| **webapp-testing** | Web 应用测试自动化，基于 Playwright 实现元素发现、控制台日志捕获、静态 HTML 测试 | `scripts/`、`references/playwright-patterns.md`、`examples/` | 测试网页、测试 Web 应用、Playwright 自动化、UI 测试、点击按钮、填写表单、捕获控制台错误、检查页面元素 |

---

## 二、文档处理类（5 个）

此类 Skills 专注于各种办公文档格式的读写、处理、生成，基于成熟的 Python 库实现可靠的文档操作。

| Skill 名称 | 一句话功能描述 | 主要资源 | 触发关键词/场景 |
|------------|---------------|---------|----------------|
| **docx** | Word 文档处理：接受修订（accept_changes）、添加评论（comment）、合并运行（merge_runs）、OOXML schema 验证、LibreOffice 集成转换 | `scripts/docx-*.py`、`references/ooxml-schema.md`、`references/libreoffice.md` | 处理 Word 文档、.docx 文件、接受修订、添加批注、合并文档、OOXML 验证、格式转换 |
| **pdf** | PDF 处理：表单字段提取/填充、PDF 转图片、边界框检查、标注填充，基于 pypdf 和 pdfplumber | `scripts/extract_fields.py`、`scripts/fill_form.py`、`scripts/pdf_to_images.py`、`scripts/inspect_bbox.py`、`references/` | 处理 PDF 文件、提取 PDF 表单、填充 PDF、PDF 转图片、查看 PDF 标注、上传 .pdf 文件要求处理 |
| **pptx** | PowerPoint 处理：添加幻灯片（add_slide）、清理（clean）、生成缩略图（thumbnail），提供图表/主题/幻灯片辅助类 | `scripts/pptx-*.py`、`references/pptx-patterns.md`、`references/themes.md` | 处理 PowerPoint、.pptx 文件、添加幻灯片、生成 PPT、PPT 转图片、图表、主题应用 |
| **xlsx** | Excel 电子表格处理：读写单元格、公式计算、数据透视表、样式设置、图表生成，基于 openpyxl | `scripts/xlsx-*.py`、`references/openpyxl-patterns.md`、`examples/` | 处理 Excel 文件、.xlsx/.xls 文件、读写表格、数据导出、生成报表、公式、数据透视表 |
| **doc-coauthoring** | 文档协作编写：提供结构化文档工作流，引导从大纲到成稿的协作过程 | `references/workflow.md`、`templates/`、`scripts/` | 协作写文档、结构化写作、文档大纲、技术文档撰写、报告协作、需要按流程写长文档 |

---

## 三、设计与创意类（7 个）

此类 Skills 专注于视觉设计、创意生成、前端 UI、品牌规范，帮助创建美观且专业的视觉产出。

| Skill 名称 | 一句话功能描述 | 主要资源 | 触发关键词/场景 |
|------------|---------------|---------|----------------|
| **algorithmic-art** | 算法艺术生成：基于 p5.js 模板，提供生成器+查看器模式，创建带种子随机性的交互式生成艺术 | `templates/p5js-template.html`、`scripts/generate.js`、`examples/` | 生成艺术、算法艺术、creative coding、p5.js、粒子系统、流场、交互式艺术 |
| **canvas-design** | Canvas 设计系统：用于创建海报、艺术作品、静态设计，内置大量开源字体支持 | `references/design-system.md`、`fonts/`（大量开源字体）、`scripts/export.py` | 设计海报、创建视觉设计、生成艺术图片、Canvas 绘图、需要字体、打印设计、PNG/PDF 设计稿 |
| **theme-factory** | 主题工厂：提供 10 个精心设计的预设主题，可快速应用到 UI、文档、图表 | `themes/arctic-frost.json`、`themes/botanical-garden.json`、`themes/desert-rose.json`、`themes/forest-canopy.json`、`themes/golden-hour.json`、`themes/midnight-galaxy.json`、`themes/modern-minimalist.json`、`themes/ocean-depths.json`、`themes/sunset-boulevard.json`、`themes/tech-innovation.json`、`scripts/apply-theme.py` | 选择配色方案、应用主题、UI 主题、颜色搭配、设计系统主题、图表配色 |
| **frontend-design** | 前端设计指导：帮助创建生产级 UI，避免"AI 美学"陷阱，提供现代前端设计原则和组件模式 | `references/design-principles.md`、`references/component-patterns.md`、`examples/` | 做前端 UI、设计网页界面、避免 AI 风格、生产级 UI、组件设计、CSS 布局、响应式设计 |
| **brand-guidelines** | Anthropic 品牌指南：应用 Anthropic 官方品牌色彩和排版规范到各类产出物 | `references/colors.md`、`references/typography.md`、`assets/` | 使用 Anthropic 品牌色、符合品牌规范、Anthropic 风格设计、品牌排版 |
| **slack-gif-creator** | Slack GIF 创建：包含缓动函数库、帧合成工具、GIF 构建器、验证器，生成适合 Slack 尺寸的 GIF | `scripts/easing.py`、`scripts/compose-frames.py`、`scripts/build-gif.py`、`scripts/validate-gif.py`、`references/slack-specs.md` | 创建 Slack GIF、制作动图、帧动画、缓动动画、Slack 表情包、GIF 生成 |
| **web-artifacts-builder** | Web 制品构建器：支持 shadcn/ui 组件打包、artifact 初始化/打包脚本，创建可独立运行的单文件 Web 应用 | `scripts/init-artifact.py`、`scripts/build-artifact.py`、`references/shadcn-components.md`、`templates/` | 创建单文件 HTML 应用、打包 Web artifact、shadcn 组件、可分享的网页 demo、零依赖 Web 应用 |

---

## 四、沟通与写作类（3 个）

此类 Skills 专注于书面沟通、内部文档、写作引导，提供模板和结构化指引。

| Skill 名称 | 一句话功能描述 | 主要资源 | 触发关键词/场景 |
|------------|---------------|---------|----------------|
| **internal-comms** | 内部沟通模板包：包含 3P 更新、公司通讯、FAQ、通用沟通模板，按场景提供写作结构 | `templates/3p-update.md`、`templates/company-newsletter.md`、`templates/faq.md`、`templates/general.md`、`references/communication-principles.md` | 写内部更新、3P 更新、公司通讯、团队通知、FAQ 文档、内部沟通邮件、周报/更新 |
| **academy-guide** | 学院指南：提供教学内容、教程、课程材料的结构化编写指引 | `templates/lesson.md`、`templates/tutorial.md`、`references/teaching-patterns.md` | 写教程、教学材料、课程内容、培训文档、指南、Academy 风格内容、如何做 X 教程 |
| **discernment-nudge** | 辨别力提示：在信息处理、决策判断、观点评估时提供批判性思考引导 | `references/thinking-frames.md`、`templates/` | 需要辨别信息、批判性思考、评估观点、决策辅助、信息验证、避免误导 |

---

## 10 个预设主题（theme-factory）

theme-factory Skill 提供以下 10 个开箱即用的主题：

| 主题名称 | 风格 | 适用场景 |
|---------|------|---------|
| **arctic-frost** | 冷色调、冰蓝灰白、简洁干净 | 科技产品、数据仪表板、专业工具 |
| **botanical-garden** | 自然绿色系、植物色调 | 环保主题、健康应用、自然相关内容 |
| **desert-rose** | 暖沙色、玫瑰粉、温暖质感 | 生活方式、时尚、温暖主题 |
| **forest-canopy** | 深绿系、森林色调、沉稳 | 户外、探险、深度内容、环保 |
| **golden-hour** | 黄金时刻、暖橙金色、柔和 | 摄影、创意、温暖舒适的界面 |
| **midnight-galaxy** | 深空蓝紫、星光色、暗色模式 | 开发者工具、暗色主题、科幻/科技 |
| **modern-minimalist** | 黑白灰、高对比、极简主义 | 极简设计、作品集、现代品牌 |
| **ocean-depths** | 深海蓝、青色调、深邃 | 金融、企业应用、专业工具、海洋相关 |
| **sunset-boulevard** | 日落紫红橙、活力渐变 | 娱乐、创意、营销、活力品牌 |
| **tech-innovation** | 科技蓝、亮青、未来感 | 科技产品、AI、创新项目、开发者平台 |

---

## Skills 统计

| 分类 | 数量 |
|------|------|
| API 与开发工具 | 4 |
| 文档处理 | 5 |
| 设计与创意 | 7 |
| 沟通与写作 | 3 |
| **总计** | **19** |

---

## 相关资源

- [Skills 生态概览](../concepts/00-overview.md) — 了解 Skills 的基本概念和触发机制
- [SKILL.md 格式规范](../concepts/01-skill-format.md) — 如果你想创建自己的自定义 Skill
- [Skill Creator 工具详解](../concepts/02-skill-creator.md) — 使用官方元技能创建高质量 Skills
- [Claude API Skill 详解](../concepts/03-claude-api-skill.md) — claude-api Skill 的详细使用指南
- [Claude Code 插件体系](../../claude-code/concepts/01-plugin-system.md) — 了解 Skills 在插件生态中的位置
