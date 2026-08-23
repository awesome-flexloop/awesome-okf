# TRAE Co-Creation Projects 核心洞察与知识地图

## 核心洞察（四元组）

### 洞察 1：Issue 模板化的共创项目贡献流程

**陈述**：项目采用 GitHub Issue 作为唯一投稿入口，提供中英双语 Markdown Issue 模板（project-submission.md / project-submission-zh.md），要求投稿者填写 4 类结构化信息：项目基本信息（名称/仓库/演示/类型）、描述（一句话+详细描述）、协作细节（团队规模/协作类型/TRAE 使用场景）、技术细节（技术栈/核心功能/截图）。审核通过后项目才会被展示，整个流程是 Issue 驱动而非 PR 驱动——投稿者无需克隆仓库或编写 Markdown，只需填表单即可。

**证据**：F-005（README 无已收录项目列表，处于初始化阶段）、F-008（投稿流程：检查→创建 Issue→确认→审核→展示）、F-010（4 类投稿信息要求）、F-012（2 个 Markdown 格式 Issue 模板，中英双语）、F-013（三种联系方式：Issues/Discussions/Discord）

**反常识**：多数资源索引/展示类项目要求贡献者 Fork 仓库、编写 Markdown、提交 PR，这对非开发者社区成员是较高门槛。本项目采用 Issue 表单投稿模式，贡献者只需在 GitHub 网页上填写模板字段即可提交，维护者审核通过后由维护者添加到展示列表，大幅降低了贡献摩擦。

**行动**：理解 Issue 驱动 vs PR 驱动的贡献门槛差异；分析 Markdown Issue 模板的字段设计如何确保收集到审核所需的关键信息；复刻"投稿者填表单/维护者整合展示"的分工模式。

---

### 洞察 2：以"协作"为核心维度的差异化审核体系

**陈述**：与 trae-demos 以"TRAE Usage（40%）"为核心不同，本项目审核权重将 Collaboration（协作）设为 30% 的第二高权重（TRAE Usage 40% + Collaboration 30% + Code Quality 20% + Documentation 10%），且 Must Have 标准明确要求"展示有意义的协作（团队/结对编程等）"，甚至接受个人项目投稿但需展示 AI 结对编程如何体现协作——这体现了"共创"（co-creation）与"演示"（demos）的本质定位差异。

**证据**：F-006（6 个项目分类包含 Web Apps/Tools/AI/Libraries/Learning/Other）、F-007（4 项 Must Have 中含"展示有意义的协作"）、F-009（Collaboration 30% 权重，仅次于 TRAE Usage 40%）、F-011（接受个人项目但需展示 AI 协作场景）

**反常识**："共创"常被理解为"多人合作项目"，但本项目将 AI 结对编程也视为协作形式，将"人与 AI 协作"纳入共创定义，这在 AI 编程社区是一个前瞻性的定位拓展——个人开发者用 TRAE 编程本身就是一种"人机共创"。

**行动**：理解 6 项目分类如何覆盖从全栈应用到艺术装置的广泛场景；分析 Collaboration 维度的审核标准如何区分"用了 TRAE"和"用 TRAE 共创"；复刻"平台定位差异化"的权重设计方法。

## 知识地图

### 学习路径

```
阶段1：共创项目贡献模式
  ├─ issue-driven-submission.md → Issue 表单驱动的低门槛投稿模式
  └─ collaboration-centric-curation.md → 以协作为核心的差异化审核体系
```

### 概念-事实映射

| 概念文档 | 核心事实 | 关键文件 |
|---------|---------|---------|
| issue-driven-submission.md | F-005, F-008, F-010, F-012 | `.github/ISSUE_TEMPLATE/project-submission.md` |
| collaboration-centric-curation.md | F-006, F-007, F-009, F-011 | `README.md`, `CONTRIBUTING.md` |

### 示例/引用规划

| 示例文件 | 来源 | 说明 |
|---------|------|------|
| 项目投稿 Issue 模板 | `.github/ISSUE_TEMPLATE/project-submission.md` | 4 类结构化信息的投稿表单 |
| 共创分类与审核标准 | `CONTRIBUTING.md` | Collaboration 30% 权重的差异化审核 |
