---
type: concept
title: "Skill Creator 工具详解"
tags: [skills, skill-creator, meta-skill, evals, agents, skill-development]
sources:
  - id: anthropic-skill-creator
    title: Anthropic Skill Creator Official Skill
---

# Skill Creator 工具详解

**skill-creator** 是 Anthropic 官方提供的**元技能（meta-skill）**——它是一个用于创建、迭代、评估其他 Skills 的 Skill。如果你想开发自己的自定义 Skill，skill-creator 是你的首选工具，它提供了系统化的工作流程、专门的评估代理、自动化测试脚本，帮助你高质量地完成 Skill 开发。

> 💡 **核心理念**：创建好的 Skill 不是一次性写作，而是一个**迭代优化**的过程——通过结构化的 evals（评估）发现问题，然后针对性改进，直到 Skill 在各种场景下都能正确触发并有效工作。

## skill-creator 是什么

skill-creator 将 Skill 开发从"凭感觉写提示词"转变为**工程化的开发流程**。它提供：

- 📋 **标准化创建流程**：5 步工作流引导你从需求到成品
- 🤖 **3 个专业评估代理**：analyzer、comparator、grader 各司其职
- 📊 **定量评估体系**：evals 脚本测量触发准确率、执行成功率
- 🔧 **实用工具脚本**：快速验证、评估运行、描述优化等
- 📝 **最佳实践内置**：避免常见陷阱，直接复用官方经验

简单来说：skill-creator 就是"教你如何创建 Skills 的 Skill"。

## Skill 创建标准流程

skill-creator 推荐以下 5 阶段开发流程：

```
Capture Intent → Interview and Research → Write SKILL.md → Test & Eval → Iterate
    ↓                  ↓                    ↓              ↓            ↓
  捕捉意图         访谈与调研           编写初版        测试评估      迭代优化
```

### 阶段 1：Capture Intent（捕捉意图）

首先明确你要解决的核心问题：

**需要回答的问题**：
1. 这个 Skill 要解决什么具体问题？（避免过于宽泛）
2. 目标用户是谁？他们在什么场景下会遇到这个问题？
3. 成功的标准是什么？——怎么判断这个 Skill 工作得好？
4. 触发场景有哪些？——用户会说什么话、上传什么文件、执行什么任务？
5. 边界在哪里？——什么情况下**不应该**使用这个 Skill？

**反模式要避免**：
- ❌ "一个通用的编程助手"——太宽泛，没有聚焦
- ❌ "处理数据的工具"——不具体，无法明确触发条件
- ✅ "从 PDF 表单中提取字段并填充数据的工具"——具体、可评估

### 阶段 2：Interview and Research（访谈与调研）

深入理解领域知识，收集必要的参考资料：

**调研内容**：
1. **领域专家知识**：这个领域的最佳实践是什么？有哪些常见陷阱？
2. **现有解决方案**：人们现在是怎么解决这个问题的？有什么工具？
3. **参考文档**：需要哪些 API 文档、规范、教程作为 references/？
4. **脚本工具**：需要哪些辅助脚本？用什么语言实现？
5. **失败模式**：通常哪些地方会出错？如何预防或处理？

**产出物**：
- references/ 目录下的参考文档
- scripts/ 目录下的辅助脚本（如果需要）
- 工作流程的详细步骤清单

### 阶段 3：Write SKILL.md（编写初版）

基于前面的调研，按照 SKILL.md 格式规范编写第一版：

**编写重点**：
1. 先写 `name`——简洁的 kebab-case 标识符
2. **重点打磨 `description`**——这是触发的关键，参考 [SKILL.md 格式规范](01-skill-format.md) 中的最佳实践
3. 组织 Markdown 正文：When to Use → Key Resources → Workflow → Best Practices → Common Pitfalls
4. 确保所有脚本和参考文档的路径引用正确

> 💡 可以使用 skill-creator 内置的 **description improver** 脚本帮助优化 description 质量。

### 阶段 4：Test & Eval（测试与评估）

这是最关键的阶段——通过系统化的 evals 验证 Skill 质量，而不是"感觉应该可以"。

**两层评估**：
1. **定量 evals**：运行自动化测试用例，测量触发准确率和任务成功率
2. **定性 review**：人工检查实际触发场景中的表现，发现自动化测试遗漏的问题

**评估维度**：
| 维度 | 评估内容 | 合格标准 |
|------|---------|---------|
| **触发准确率** | 应该触发时是否触发？不该触发时是否不触发？ | ≥ 90% precision 和 recall |
| **指令遵循** | 代理是否遵循 Skill 中的工作流程？ | 关键步骤无遗漏 |
| **资源使用** | 是否正确引用和使用 scripts/references？ | 路径正确，使用方法无误 |
| **任务成功率** | 端到端任务是否成功完成？ | ≥ 80% 测试用例通过 |
| **错误处理** | 遇到异常情况是否能优雅处理？ | 不崩溃，给出有用提示 |

### 阶段 5：Iterate（迭代优化）

根据评估结果进行针对性改进：

- 如果**漏触发（undertrigger）**：在 description 中增加更多触发关键词和场景
- 如果**误触发（overtrigger）**：收窄 description，增加排除条件，明确"不使用"场景
- 如果**指令不清晰**：重写 Markdown body，使用更直接的指令式语言，增加示例
- 如果**缺少工具**：补充必要的脚本或参考文档
- 如果**工作流有误**：调整步骤顺序，增加校验点

每次迭代后重新运行 evals，直到质量达标。

## 关键组件详解

skill-creator 包含以下核心组件，这些都在它自己的目录结构中：

### 3 个专业评估 Agents

skill-creator 的 `agents/` 目录下包含三个专门的子代理，分别负责评估的不同环节：

#### 1. analyzer（分析器）

**职责**：分析用户请求与 Skill 的匹配度，诊断触发问题。

**使用场景**：
- 你发现 Skill 应该触发但没触发
- 你想知道某个用户输入是否会触发该 Skill
- 你需要诊断触发失败的原因

**工作方式**：analyzer 会逐字分析用户请求与 Skill description 的语义匹配，给出：
- 匹配/不匹配的判断
- 具体匹配了哪些关键词或语义
- 如果不匹配，为什么不匹配
- 改进建议（应该在 description 中增加什么内容）

#### 2. comparator（比较器）

**职责**：对比两个版本的 Skill 在相同测试用例上的表现差异。

**使用场景**：
- 你修改了 Skill 后想知道是否有改进
- 你想对比不同 description 写法的效果
- 你想确认某次修改没有引入回归问题

**工作方式**：在同一组测试用例上分别运行两个版本的 Skill，给出：
- 哪些用例从失败变成功（改进）
- 哪些用例从成功变失败（回归）
- 哪些用例在两个版本中都失败（待改进）
- 量化的指标对比

#### 3. grader（评分器）

**职责**：对 Skill 的输出质量进行多维度打分和详细反馈。

**使用场景**：
- 你想全面评估 Skill 的整体质量
- 你需要具体的改进建议
- 你想在发布前做质量验收

**评分维度**：
- 指令清晰度（1-10 分）
- 资源引用准确性（1-10 分）
- 工作流完整性（1-10 分）
- 错误处理完备性（1-10 分）
- 最佳实践遵循度（1-10 分）
- description 质量（1-10 分）

grader 会给出每个维度的具体得分、扣分原因、改进建议，以及总体质量等级。

### eval-viewer 报告生成器

`scripts/eval-viewer` 是一个可视化报告生成工具，将 evals 的运行结果整理为易读的 HTML 或 Markdown 报告：

**报告内容**：
- 总体通过率统计
- 失败用例详情（输入、预期输出、实际输出、错误原因）
- 触发结果分布（正确触发/漏触发/误触发）
- 历史趋势对比（多次迭代的质量变化）

**使用方式**：运行完 evals 后，执行：
```bash
python "$SKILL_DIR/scripts/eval-viewer.py" results.json --output report.html
```

### description improver 脚本

`scripts/improve_description.py` 是一个专门优化 `description` 字段的工具：

**功能**：
1. 分析当前 description 的优缺点
2. 识别缺失的触发场景
3. 发现模糊或弱表述
4. 生成多个改进版本供你选择
5. 给出具体的修改理由

**使用方式**：
```bash
python "$SKILL_DIR/scripts/improve_description.py" path/to/SKILL.md
```

它会输出 3 个不同风格的改进版本：
- **Conservative（保守版）**：最小改动，只修复明显问题
- **Balanced（平衡版）**：推荐版本，在现有基础上优化
- **Aggressive（激进版）**：重写，最大化触发准确率

### 实用运行脚本

skill-creator 提供了三个便捷脚本：

#### 1. `scripts/quick_validate.py` — 快速验证

快速检查 SKILL.md 的格式正确性和基本问题：

```bash
python "$SKILL_DIR/scripts/quick_validate.py" path/to/your/skill/
```

检查项：
- YAML frontmatter 是否有效
- 必填字段（name、description）是否存在
- name 是否符合 kebab-case 规范
- description 是否包含 "TRIGGER when"
- 引用的文件路径是否存在
- 基本格式问题检测

#### 2. `scripts/run_eval.py` — 运行评估

在指定的测试用例集上运行评估：

```bash
# 运行全部 evals
python "$SKILL_DIR/scripts/run_eval.py" path/to/your/skill/ path/to/evals/

# 运行特定类别的 evals
python "$SKILL_DIR/scripts/run_eval.py" path/to/your/skill/ path/to/evals/ --category trigger
```

支持的 eval 类别：
- `trigger`：触发准确率测试
- `end-to-end`：端到端任务执行测试
- `edge-cases`：边界情况测试

#### 3. `scripts/run_loop.py` — 迭代优化循环

自动化"评估→改进→再评估"的迭代循环：

```bash
python "$SKILL_DIR/scripts/run_loop.py" path/to/your/skill/ path/to/evals/ --iterations 5
```

它会自动：
1. 运行 evals 收集当前问题
2. 调用 analyzer 和 grader 分析问题
3. 生成改进建议
4. 应用改进到 SKILL.md
5. 重新运行 evals
6. 重复直到达到目标准确率或用完迭代次数

> ⚠️ 注意：自动迭代生成的内容需要人工 review，不要盲目接受所有修改。

## 评估方法论

skill-creator 推荐的评估方法结合了**定量测试**和**定性审查**。

### 定量 evals 的结构

evals 目录下的测试用例采用标准 JSON 或 YAML 格式：

```yaml
# evals/trigger-cases.yaml
cases:
  - id: trigger-001
    input: "帮我从这个 PDF 中提取所有表单字段"
    expected_trigger: true
    files: ["document.pdf"]
    category: trigger
    
  - id: trigger-002
    input: "写一个快速排序算法"
    expected_trigger: false
    category: trigger
    
  - id: e2e-001
    input: "填充这个 PDF 表单，姓名填张三，邮箱填YA9RfmB0@dTdpwNO.TAM"
    expected_trigger: true
    files: ["empty-form.pdf"]
    expected_outcome:
      fields_extracted: true
      form_filled: true
      output_valid: true
    category: end-to-end
```

**推荐的测试用例构成**：
- **正面用例（expected_trigger: true）**：应该触发的场景，覆盖各种表述方式
- **负面用例（expected_trigger: false）**：不应该触发的场景，避免 overtrigger
- **边界用例**：模糊场景，验证 Skill 的判断是否合理
- **端到端用例**：完整任务流程，验证实际执行效果

### 定性 review 检查清单

除了自动化测试，还需要人工审查以下方面：

- [ ] 代理是否真正理解了 Skill 的意图？
- [ ] 工作流程是否符合领域最佳实践？
- [ ] 给出的建议是否实用、可执行？
- [ ] 错误提示是否有帮助？
- [ ] 有没有产生误导性的指令？
- [ ] 在复杂场景下是否仍然表现良好？

## 何时使用 skill-creator

以下场景强烈建议使用 skill-creator 辅助开发：

### ✅ 应该使用的场景

1. **创建新的自定义 Skill**——从零开始时，它会引导你走完整流程
2. **Skill 触发有问题**——漏触发或误触发，analyzer 可以帮你诊断
3. **迭代优化现有 Skill**——想提升 Skill 质量但不知道从何下手
4. **准备发布 Skill**——发布前用 grader 做全面质量验收
5. **学习 Skill 开发**——它本身就是最好的 Skill 开发教程

### ❌ 不需要使用的场景

1. **简单的一次性 Skill**——只是临时用一下，不需要高质量
2. **修改已有的官方 Skill**——官方 Skill 已经经过充分测试
3. ** trivial 场景**——比如只是加载一个固定的参考文档，不需要复杂评估

## 相关概念

- [SKILL.md 格式规范](01-skill-format.md) — Skill 文件的完整格式定义，在编写初版时参考
- [Skills 生态概览](00-overview.md) — Skills 的整体生态和触发机制
- [Claude API Skill 详解](03-claude-api-skill.md) — 高质量官方 Skill 案例学习
- [全部 Skills 索引](../references/skills-index.md) — 查看其他官方 Skill 的实现参考
- [Claude Code 插件体系](../../claude-code/concepts/01-plugin-system.md) — 了解如何将你创建的 Skill 打包为插件
