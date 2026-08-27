---
type: Concept
title: 编写自定义 Skill
description: 基于 _template 模板创建自定义 Skill 的完整指南，包括 frontmatter 填写、触发条件设计、指令编写、脚本集成、子技能复用、测试验证和提交 PR 全流程。
tags: [trae-skills, custom-skill, how-to-write, _template, contribution]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 编写前的决策

在创建新 Skill 之前，先回答以下问题确定模式选择：

1. **需要脚本吗？** Agent 仅靠文件读写、Shell、WebFetch 等内置能力就能完成 → 纯 Prompt 型
2. **需要多阶段流程和子技能吗？** 任务涉及多个独立阶段且有可复用指令片段 → Workflow 编排型
3. **否则** → 脚本辅助型（仅在纯 Prompt 无法完成时引入脚本）

决策路径：纯 Prompt 型 → 验证触发逻辑 → 按需引入脚本 → 按需拆分 subskills。

## 使用 _template 模板

`skills/_template/SKILL.md` 是所有技能的起点。模板定义了标准结构：

```markdown
---
name: your-skill-name
description: 描述做什么以及何时使用这是agent决定是否加载的依据
---

# Your Skill Name

## Description

描述技能的核心功能。

## Usage Scenario

明确触发条件和排除条件。

## Instructions

1. 步骤一
2. 步骤二
3. 步骤三

## Examples (Optional)

示例输入输出。
```

### 第一步：命名技能

- 使用小写英文字母
- 单词间用连字符（`-`）连接
- 命名保持稳定，发布后不随意更改
- 目录名必须与 frontmatter 中的 `name` 一致

### 第二步：编写 description

description 是技能被正确触发的唯一依据，必须包含双重信息：

1. **功能**：这个技能能做什么
2. **触发场景**：什么时候应该加载这个技能

好的 description 示例：
> 在用户要求生成 git commit message、询问改了什么、或需要为代码变更提议提交信息时使用。基于 git diff 分析变更，生成符合 Conventional Commits 规范的标准化提交信息。

差的 description 示例：
> Git 工具。（太模糊，无法判断何时触发）

详见 [触发条件设计示例](../examples/trigger-condition-design.md)。

### 第三步：填充章节

按模板结构填充各章节：

**Description 章节**：简明描述核心功能、角色定位、关键约束。

**Usage Scenario 章节**：
- 穷举正面触发词/场景
- 明确反面排除条件
- 声明能力边界

**Instructions 章节**：
- 按执行顺序编号
- 每步使用明确的动作动词（确认、执行、生成、输出等）
- 复杂步骤可分子步骤
- 明确输入来源和输出去向
- Workflow 型可用 Phase 划分大阶段

**Examples 章节**（可选）：提供输入输出参考样例。

## 触发条件设计

触发条件是 Skill 最重要的设计部分——步骤写得粗略 Agent 还能推理，触发条件模糊则 Agent 根本不会加载。

### 正面触发词设计

参考社区技能的触发词设计：

| 技能 | 触发词/场景 |
|------|------------|
| daily-hot-news | "今日热搜""新闻热榜""今天有什么热点""全网热搜""热门新闻""今日新闻""热榜" |
| git-commit-generator | 用户要求"写 commit message"/"生成 commit"、用户问"我改了什么" |
| video-to-keyframes | "抽帧""拆帧""关键帧""候选关键帧""镜头拆分""转场点""分段""分镜初筛" |
| wechat-mini-program-development | "创建微信小程序""小程序开发帮助""HTTP 请求封装""API 管理" |

原则：穷举用户可能使用的各种表达方式。

### 反面排除条件

明确声明什么场景**不适用**：

- daily-hot-news："不适用于历史新闻或特定领域深度分析"
- kz-article-deep-analysis："不适用于学术论文或书籍"

### 约束条款

明确什么**不能做**，防止越界：

- cloudbase："不得编造 CloudBase API 路径或 MCP 工具参数""不得暴露 API key"
- trae-claw-install："不写入真实密钥""复用仓库脚本，不创建并行流程"

## 脚本集成

当纯 Prompt 无法完成任务时（需外部 API、复杂计算、二进制处理），引入脚本。

### 脚本放置位置

```
skills/<your-skill>/
├── SKILL.md
└── resources/
    └── scripts/
        └── your_script.py
```

### 脚本设计原则

1. **标准库优先**：像 `fetch_news.py` 一样仅用 Python 标准库，零依赖
2. **一键命令**：提供类似 `run_video_workflow.py` 的编排入口
3. **结构化输出**：输出 JSON/CSV，由 SKILL.md 指导格式化
4. **合理默认值**：命令行参数都有默认值，减少 Agent 决策
5. **降级容错**：多数据源或错误重试确保健壮

### SKILL.md 中的脚本调用

在 Instructions 中明确给出运行命令：

```markdown
## Instructions

1. 确认用户需求（平台和数量）
2. 执行以下命令获取热榜数据：
   ```bash
   python skills/daily-hot-news/resources/scripts/fetch_news.py --platforms weibo,baidu --top 10
   ```
3. 将输出格式化为 Markdown 热榜报告
```

详见 [带 Python 脚本的 Skill 示例](../examples/skill-with-python-script.md)。

## 子技能复用（Workflow 型）

当工作流复杂、单 SKILL.md 过长时，拆分 subskills。

### 子技能放置位置

```
skills/<your-skill>/
├── SKILL.md
└── subskills/
    ├── sub-step-a.md
    └── sub-step-b.md
```

### 子技能设计原则

1. **单一职责**：每个子技能负责一个独立任务
2. **可复用**：子技能可被多个 Phase 或多个技能调用
3. **独立可读**：子技能文件本身是完整的指令集

参考 daily-trend-writer 的 3 个 subskills：
- `doc-coauthoring.md`：文档协作
- `mimeng-writing.md`：咪蒙风格写作
- `wechat-article-writer.md`：技术文章写作

## 可选资源文件

根据需要添加以下资源：

| 资源 | 路径 | 用途 | 参考技能 |
|------|------|------|----------|
| 示例 | `examples/input.md`、`examples/output.md` | 输入输出样例 | git-commit-generator、daily-trend-writer |
| 模板 | `templates/*.md`/`*.txt` | 输出格式模板 | git-commit-generator、daily-trend-writer |
| 参考 | `resources/*.md` | 规范参考 | git-commit-generator（conventional-commits-types.md） |
| 报告模板 | `assets/template.md` | 结构化输出模板 | kz-article-deep-analysis |
| 方法论 | `references/methodology.md` | 分析方法论 | kz-article-deep-analysis |
| 验证脚本 | `scripts/verify.py` | 结构自检 | kz-article-deep-analysis |

## 测试验证

### 本地测试步骤

1. 将技能目录复制到项目级 `.trae/skills/<name>/` 或全局级 `~/.trae/skills/<name>/`
2. 在 TRAE 中新开会话
3. 使用触发词测试技能是否正确加载
4. 测试正面场景：触发词是否能正确激活技能
5. 测试反面场景：不相关的请求是否不会误触发
6. 测试完整流程：执行端到端任务，验证输出质量
7. 测试约束条款：尝试越界操作，确认 Agent 会拒绝

### 结构验证

如果技能包含 verify.py 脚本，运行：
```bash
python skills/<name>/scripts/verify.py --skill skills/<name>
```

检查项包括：SKILL.md 存在、frontmatter 完整、必需章节存在、引用文件存在。

### 验证清单

- [ ] `name` 字段符合小写连字符规范
- [ ] `description` 包含功能+触发场景双重信息
- [ ] 正面触发词穷举充分
- [ ] 反面排除条件明确
- [ ] 步骤编号清晰、动作明确
- [ ] 脚本命令可直接运行
- [ ] 脚本依赖在 SKILL.md 中说明
- [ ] 输出格式有明确约定
- [ ] 约束条款覆盖主要风险点
- [ ] 端到端测试通过

## 提交 PR

1. Fork 仓库
2. 创建特性分支：`git checkout -b feature/your-skill-name`
3. 在 `skills/` 目录下添加技能
4. 更新根目录 `README.md` 的技能目录表格
5. 确保技能目录结构规范
6. 提交变更（可使用 git-commit-generator 技能生成 commit message）
7. 推送分支并创建 Pull Request
8. PR 合并后自动触发社区积分（+1 分）

## 扩展字段

除了必填的 `name` 和 `description`，可按需添加扩展字段：

```yaml
---
name: kz-article-deep-analysis
description: ...
version: 1.0.3
metadata:
  author: K叔
tags: [article, analysis, deep-read]
---
```

扩展字段不破坏核心结构，但建议保持简洁，只添加确实需要的元数据。

## 相关概念

- [SKILL.md 格式规范](01-skill-format.md)
- [技能分类与模板模式](02-skill-categories.md)
- [纯 Prompt 型技能](03-prompt-only-skills.md)
- [脚本辅助型技能](04-script-assisted-skills.md)
- [Workflow 编排型技能](05-workflow-skills.md)
- [社区积分机制](06-community-points.md)

## 相关内容

- [源码信源索引](../references/skills-source.md)
- [创建第一个 Skill](../examples/create-first-skill.md)
- [带 Python 脚本的 Skill 示例](../examples/skill-with-python-script.md)
- [触发条件设计示例](../examples/trigger-condition-design.md)
- [社区积分贡献示例](../examples/points-contribution.md)
