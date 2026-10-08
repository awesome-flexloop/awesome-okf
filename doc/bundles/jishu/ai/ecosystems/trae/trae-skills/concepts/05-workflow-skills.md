---
type: Concept
title: Workflow 编排型技能
description: Workflow 编排型技能通过多 Phase 工作流、subskills 子技能复用和多脚本/模板协同完成复杂任务。社区中 daily-trend-writer（6 Phase 公众号内容流水线）、kz-article-deep-analysis（4 步深度分析）、trae-claw-install（5 步跨平台部署）是典型代表。
tags: [trae-skills, workflow, daily-trend-writer, kz-article-deep-analysis, trae-claw-install, subskills]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## Workflow 编排型的特征

Workflow 编排型技能是三种模式中最复杂的，用于处理单一线性指令无法完成的复杂任务。核心特征：

1. **多阶段划分**：工作流分为多个 Phase 或编号步骤，每个阶段有明确目标
2. **subskills 复用**：通过 `subskills/` 目录存放可复用的子技能指令
3. **多资源协同**：同时使用脚本、模板、参考文件、资产模板等多种资源
4. **输入输出契约**：每个 Phase 有明确的输入来源和输出去向
5. **归档约定**：定义输出文件的路径格式和命名规范

## daily-trend-writer：六阶段内容生产流水线

daily-trend-writer 是最典型的 Workflow 编排型技能，实现了全自动化公众号内容生产流水线。

### 工作流总览

Phase 0 时间同步 → Phase 1 热点发现与榜单生成 → Phase 2 选题与深挖 → Phase 3 内容打磨（调用 subskills/doc-coauthoring）→ Phase 4 多风格文章写作（咪蒙风格 + 技术干货）→ Phase 5 归档与交付。

### Phase 0：时间同步

执行 `date "+%Y-%m-%d %H:%M:%S %Z"` 获取系统时间，格式化为 `YYYY-MM-DD`（搜索用）和 `YYYYMMDDHHMMSS`（归档目录用）。

### Phase 1：热点发现与榜单生成

输出 4 类分类热点榜：实用工具榜、社区热点榜、教程经验榜、行业动态榜。

### Phase 2-3：选题深挖与内容打磨

从榜单中选择"小而美"选题，收集资料后调用 `subskills/doc-coauthoring` 协作打磨内容。

### Phase 4：多风格文章写作

- **任务 A**：调用 `subskills/mimeng-writing` 撰写咪蒙风格爆款文（5 个标题候选、短句、情绪词、故事化叙事）
- **任务 B**：调用 `subskills/wechat-article-writer` 撰写技术干货文（背景→核心功能→原理/教程→总结）

### Phase 5：归档与交付

归档路径格式：
```
./YYYYMMDDHHMMSS/
├── mimeng_{topic_slug}.md
├── tech_{topic_slug}.md
└── brief_{topic_slug}.md（可选）
```

### 技能目录资源

```
skills/daily-trend-writer/
├── examples/{input,output}.md
├── resources/trend-sources.md
├── subskills/{doc-coauthoring,mimeng-writing,wechat-article-writer}.md
└── templates/{topic-brief,trend-board}.md
```

## kz-article-deep-analysis：结构化深度分析

kz-article-deep-analysis（K叔，v1.0.3）实现非学术类文章深度解读，采用 `@步骤` 结构化标签标记流程。

### 工作流总览

步骤 1 获取与预处理 → 步骤 2 深度解构 → 步骤 3 认知增量 → 步骤 4 生成报告。

### 步骤标记系统

| 标签 | 用途 |
|------|------|
| `@动作:` | 该步骤要执行的动作 |
| `@类型:` | 步骤类型 |
| `@优先级:` | 执行优先级 |
| `@验证点:` | 需要验证的检查点 |
| `@验证方式:` | 验证方法 |

### 深度解构环节

包含核心议题下探、核心主张提炼、论证骨架梳理（≤3 论据）、ASCII 推理拓扑图绘制。

### 认知增量环节

定位观点与读者既有认知的差异点，绘制 ASCII Art 认知卡片。

### 版本管理

- v1.0.3：增加使用示例
- v1.0.2：术语专业化
- v1.0.1：添加作者元数据
- v1.0.0：初始版本

资源清单：`assets/template.md`（报告模板）、`references/methodology.md`（方法论）、`scripts/verify.py`（结构验证）。

## trae-claw-install：跨平台部署工作流

trae-claw-install 实现仓库驱动的 OpenClaw 部署，核心特点是跨平台自动路由。

### 平台路由

| 平台 | 脚本路径 | 特殊要求 |
|------|----------|----------|
| Windows | `scripts/windows/wsl/*.sh` | WSL2 Linux 文件系统内执行 |
| macOS | `scripts/macos/*.sh` | 原生执行 |
| Linux | `scripts/linux/*.sh` | 原生执行 |

### 五步流程

1. 检测平台并路由脚本
2. 验证基线（node >=22、npm 可用、openclaw 状态）
3. 执行标准流程（setup → start → check）
4. 运行最低验收（openclaw doctor/status/dashboard）
5. 失败时故障排除工作流

### 输出契约

- **成功**：报告平台、执行步骤、验收结果、服务可访问性
- **失败**：报告首个错误、已执行诊断、下一步可操作修复

### 约束条款

- 复用仓库脚本和文档，不创建并行流程
- 不写入真实密钥
- Windows 优先在 WSL2 内执行

## Workflow 设计模式总结

### Phase 分解对比

| 要素 | daily-trend-writer | kz-article-deep-analysis | trae-claw-install |
|------|-------------------|-------------------------|-------------------|
| 阶段数 | 6 Phase | 4 步骤 | 5 步骤 |
| 子技能 | 3 个 subskills | 方法论参考 | 无 |
| 模板 | 2 个 templates | assets/template.md | 无 |
| 验证 | 输出归档 | verify.py 脚本 | 验收检查 |

### subskills 复用模式

- 每个子技能是独立 Markdown 文件
- 主 SKILL.md 通过文件名引用
- 子技能可被多个 Workflow 共享
- 避免主文件过长

### 归档路径约定

- 时间戳目录名（`YYYYMMDDHHMMSS`）
- 文件命名带主题标识（`{topic_slug}`）
- 区分不同风格/类型产出

### 错误处理

- 约束条款明确禁止事项
- 故障排除流程（trae-claw-install 步骤 5）
- 成功/失败分别定义输出契约
- 前置条件检查

## 相关概念

- [技能分类与模板模式](02-skill-categories.md)
- [纯 Prompt 型技能](03-prompt-only-skills.md)
- [脚本辅助型技能](04-script-assisted-skills.md)
- [社区积分机制](06-community-points.md)
- [编写自定义 Skill](07-write-skill.md)

## 相关内容

- [源码信源索引](../references/skills-source.md)
- [带 Python 脚本的 Skill 示例](../examples/skill-with-python-script.md)
