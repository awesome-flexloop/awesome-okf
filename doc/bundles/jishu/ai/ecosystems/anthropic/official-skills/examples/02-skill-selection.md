---
type: example
title: "场景到 Skill 的选型决策树"
description: "把 19 个官方 Skill 按真实工作场景组织成决策树，含边界场景的排除判断、可直接复用的调用示例与常见误选对照。"
tags: [skills, decision, workflow, selection, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# 场景到 Skill 的选型决策树

前一篇讲**怎么造**，本篇讲**怎么用**——面对一个真实需求，该选哪个 skill，以及哪些"看起来像但不是"的情况容易误选。

---

## 一、主决策树

```
我的需求是什么？
│
├─ 要调用 Claude API / 写 SDK 代码 / 问模型选型与定价
│  └→ claude-api                          （8 语言 + cURL，含 Managed Agents）
│
├─ 要把外部服务接成 AI 可调的工具
│  └→ mcp-builder                          （MCP server，四阶段）
│
├─ 要写/改/分析 Word 文档 (.docx/.dotx)
│  └→ docx
│
├─ 要处理 PDF（提到 .pdf 即可）
│  └→ pdf
│
├─ 要做幻灯片 (提到 .pptx/.potx/"deck"/"slides")
│  └→ pptx
│
├─ 要处理表格 (提到 .xlsx/.csv/.tsv/"表格")
│  └→ xlsx
│
├─ 要写一份需要打磨的文档（提案/规格/决策文档）
│  └→ doc-coauthoring                     （三阶段 + 读者测试）
│
├─ 要生成创意作品（艺术/海报/静态设计）
│  ├─ 交互式/生成式/参数可探索 → algorithmic-art
│  └─ 静态视觉稿 (PNG/PDF)          → canvas-design
│
├─ 要统一视觉风格 / 选配色 / 给图表定色
│  └→ theme-factory                       （10 套主题）
│
├─ 要做前端 UI 的视觉方向（不是写代码）
│  └→ frontend-design
│
├─ 要用 Anthropic 品牌规范
│  └→ brand-guidelines
│
├─ 要做动图 / Slack GIF
│  └→ slack-gif-creator
│
├─ 要做复杂 HTML 构件（多组件/状态管理/路由）
│  └→ web-artifacts-builder
│
├─ 要写内部沟通（3P/通讯/FAQ/通知）
│  └→ internal-comms
│
├─ 要学怎么用 Claude / 要培训材料
│  └→ academy-guide
│
├─ 刚给出重要建议/方案/分析，想让用户自查
│  └→ discernment-nudge
│
├─ 要写/改/评估一个 Skill 本身
│  └→ skill-creator
│
└─ 要测本地 Web 应用
   └→ webapp-testing
```

---

## 二、边界场景：容易误选的六组

### 1. `claude-api` vs `mcp-builder` —— 写代码 vs 建工具

| | claude-api | mcp-builder |
|---|---|---|
| 产出 | 调用 Claude 的代码 | 一个 MCP server |
| 关键词 | 模型 id、定价、streaming、tool use、缓存 | MCP server、工具定义、外部 API 集成 |
| 关系 | mcp-builder 的产出**可以**用 claude-api 的方式调用 | — |

**误选典型**：想把某个内部 REST API 接成 AI 工具 → 选 `claude-api`。错。要接外部服务，应该用 `mcp-builder` 建 server。

### 2. `docx` vs `doc-coauthoring` —— 文件格式 vs 写作流程

| | docx | doc-coauthoring |
|---|---|---|
| 交付物 | 一个 `.docx` 文件 | 文档内容（Markdown/文本） |
| 关键动作 | XML 编辑、批注、修订、校验 | 上下文收集、六步精炼、读者测试 |

**误选典型**：用户说"帮我写一份产品需求文档" → 直接用 `docx` 生成了 .docx，跳过了内容打磨阶段。

**正解**：先用 `doc-coauthoring` 打磨内容，需要 .docx 交付时再走 `docx`。两者可串联。

### 3. `pptx` vs `theme-factory` —— 载体 vs 风格

`theme-factory` 提供**风格**（10 套主题的色板与字体），`pptx` 提供**载体能力**（建页、清理、缩略图、QA）。

**误选典型**：想做一份好看的 PPT → 只用 theme-factory，结果拿到的只是配色建议，不是幻灯片。

### 4. `canvas-design` vs `algorithmic-art` —— 静态 vs 交互

| | canvas-design | algorithmic-art |
|---|---|---|
| 输出 | PNG / PDF 静态稿 | 可交互的生成艺术（JS） |
| 关键资源 | 54 个字体 | 生成器模板 + 查看器 |
| 交互参数探索 | ❌ | ✅ |

### 5. `internal-comms` vs `academy-guide` —— 内部产出 vs 外部学习资源

| | internal-comms | academy-guide |
|---|---|---|
| 产出 | 你公司的内部沟通文档 | Claude Academy 的课程推荐 |
| 场景 | "写周报/3P/FAQ" | "怎么教团队用 Claude" |

### 6. `web-artifacts-builder` vs `frontend-design`

| | web-artifacts-builder | frontend-design |
|---|---|---|
| 交付 | 可运行的单文件 HTML artifact | 设计方向（指导性文本） |
| 适用 | 需要状态管理/路由/shadcn | 要审美方向、不要实现 |

> ⚠️ `web-artifacts-builder` 的 description 明确写了 **"not for simple single-file HTML/JSX artifacts"**——简单单文件场景不该触发它。

---

## 三、可直接复用的调用示例

### 文档类

```bash
# PDF：提取表单结构（位置参数：输入 PDF + 输出 JSON）
python skills/pdf/scripts/extract_form_structure.py input.pdf out.json

# PDF：PDF 转图片做视觉检查（位置参数：输入 PDF + 输出目录）
python skills/pdf/scripts/convert_pdf_to_images.py input.pdf out/

# docx：接受所有修订（位置参数：输入 + 输出）
python skills/docx/scripts/accept_changes.py input.docx clean.docx

# docx：加批注（位置参数：输入 + 批注文本；可选 --author / --initials / -o）
python skills/docx/scripts/comment.py input.docx "此处需补充数据来源" --author "张三" --initials "ZS"

# xlsx：写完公式必须重算（位置参数：文件 + 可选超时秒数 + 可选 --force）
python skills/xlsx/scripts/recalc.py output.xlsx

# pptx：生成缩略图网格做视觉 QA（位置参数：输入 + 可选输出前缀）
python skills/pptx/scripts/thumbnail.py deck.pptx thumbnails
```

### 开发类

```bash
# MCP server 评估（位置参数：评估 XML；stdio 模式需 -c 启动命令）
python skills/mcp-builder/scripts/evaluation.py tests.xml -c "python server.py" --model claude-opus-5-5

# Playwright：起服务 → 跑测试 → 清理
python skills/webapp-testing/scripts/with_server.py \
  --server "npm run dev" --port 5173 -- python tests/e2e.py

# 起两个服务
python skills/webapp-testing/scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python tests/e2e.py
```

### Skill 工程类

```bash
# 校验
cd skills/skill-creator && python scripts/quick_validate.py D:/path/to/my-skill

# 打包
cd skills/skill-creator && python scripts/package_skill.py D:/path/to/my-skill ./dist

# 评估（--eval-set 指向 evals.json，--skill-path 指向 skill 目录）
cd skills/skill-creator && python scripts/run_eval.py --skill-path D:/path/to/my-skill --eval-set D:/path/to/evals/evals.json
```

### 设计类

```bash
# Web artifact：初始化 → 打包成单文件
bash skills/web-artifacts-builder/scripts/init-artifact.sh my-artifact
bash skills/web-artifacts-builder/scripts/bundle-artifact.sh my-artifact
```

---

## 四、组合使用：三个高频组合

### 组合 1：文档从想法到交付

```
doc-coauthoring  （打磨内容）
   ↓
docx / pptx / xlsx  （落到目标格式）
   ↓
（可选）theme-factory  （统一视觉风格）
```

### 组合 2：把内部系统接成 AI 工具

```
mcp-builder  （建 MCP server + 写评估）
   ↓
claude-api  （确认调用方式与模型选型）
```

### 组合 3：教团队用 Claude

```
claude-api  （答"这个功能怎么用"——基于文档）
   ↓
academy-guide  （再补一个匹配的课程/教程）
```

`academy-guide` 的 description 明确要求这个组合：*"after consulting product documentation to answer how a Claude feature works, also check here for a matching course or tutorial — a docs-grounded answer and an Academy recommendation belong together."*

---

## 五、最容易被忽略的两个 skill

| skill | 为什么容易被忽略 | 什么时候用 |
|-------|----------------|-----------|
| **discernment-nudge** | 它不产出内容，只追加 2-3 个追问 | 刚给出重要建议/方案/分析之后——帮用户校验事实与前提。**每次对话最多一次** |
| **brand-guidelines** | 名字像是"品牌手册"，容易以为只对 Anthropic 自己的物料有效 | 任何需要 Anthropic 官方品牌色与排版的产出物 |

---

## 六、选型时的三条自检

在动手前问自己：

1. **产出物是什么格式？** —— 有明确文件格式（.docx/.pdf/.pptx/.xlsx）走对应格式 skill；没有格式、纯内容走流程型 skill。
2. **有没有现成的"工程资产"？** —— 需要脚本/模板/库（GIF、artifact、主题、字体）走资产型 skill；纯知识走指令型。
3. **边界在哪？** —— 每个 skill 的 description 都写了"何时不用"。**先读那句**。误触发多数是因为没读 Skip 条件。

---

## 相关文档

- [全部Skills索引](../references/skills-index.md) — 19 个 skill 功能与真实路径
- [Skill 编写规范与可复用模式](../concepts/04-authoring-patterns.md) — 骨架选择决策表
- [从零造一个 Skill](../examples/01-author-a-skill.md) — 造 skill 的实操
