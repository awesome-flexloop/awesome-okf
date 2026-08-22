---
type: Example
title: 添加资源条目示例
description: 向 awesome-trae 提交 PR 添加资源条目的完整流程示例，包含条目格式、双语更新和 PR 描述模板
tags: [example, contribution, pr, add-resource, awesome-trae, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/awesome-source.md
    title: "Awesome TRAE 源码信源"
---

# 添加资源条目示例

本示例演示如何向 awesome-trae 提交一个新的资源条目。

## 场景假设

假设你开发了一个基于 TRAE 构建的 Markdown 编辑器 Web 应用，仓库地址为 `https://github.com/yourname/trae-md-editor`，有在线演示，现在想将它提交到 awesome-trae 的 Projects & Demos 分类下。

## 步骤一：确认准入标准

提交前自检是否满足 4 项 Must Have：

- ✅ **TRAE Related**：项目使用 TRAE 作为核心开发工具
- ✅ **Accessible**：GitHub 仓库公开，有在线演示链接
- ✅ **Quality**：功能完整，可正常使用
- ✅ **Documented**：有 README 说明功能和使用方法

## 步骤二：确定分类和子类

- 一级分类：Projects & Demos
- 子类：Web Applications
- 提交类别：Projects

## 步骤三：更新英文 README

在 `README.md` 的 Projects & Demos → Web Applications 小节下添加条目，格式为：

```markdown
- [TRAE MD Editor](https://github.com/yourname/trae-md-editor) - A Markdown editor built with TRAE, featuring live preview and AI-assisted writing. ([Demo](https://yourname.github.io/trae-md-editor/))
```

条目格式规范：
- 使用 `- [名称](链接) - 描述。` 格式
- 描述使用英文，简洁说明项目核心功能
- 如有在线演示，在描述后附 `([Demo](url))`
- 按字母顺序插入到对应子类中

## 步骤四：更新中文 README

在 `README_zh.md` 的对应位置添加中文条目：

```markdown
- [TRAE MD Editor](https://github.com/yourname/trae-md-editor) - 基于 TRAE 构建的 Markdown 编辑器，支持实时预览和 AI 辅助写作。([演示](https://yourname.github.io/trae-md-editor/))
```

## 步骤五：提交 PR

创建 PR 时使用以下描述模板：

```markdown
## Resource Submission

**Category**: Projects
**Subcategory**: Web Applications
**Name**: TRAE MD Editor
**Link**: https://github.com/yourname/trae-md-editor
**Demo**: https://yourname.github.io/trae-md-editor/

### Description
A Markdown editor built with TRAE, featuring live preview and AI-assisted writing.

### Checklist
- [x] Resource is TRAE related
- [x] Repository/demo is publicly accessible
- [x] Project is polished and functional
- [x] Has basic documentation (README)
- [x] Updated both README.md and README_zh.md
```

## 步骤六：等待审核

- 24 小时内收到维护者确认
- 3-5 个工作日内完成审核
- 可能收到修改建议，按建议调整后重新提交
- 审核通过后 PR 被合并，资源正式收录

## 条目书写要点

1. **描述简洁**：一句话说清项目是什么、有什么特色
2. **避免营销语**：不使用"最好的"、"革命性的"等夸张描述
3. **链接有效**：确保所有链接可访问，不提交 404 链接
4. **字母序排列**：在子类中按项目名称字母顺序插入
5. **双语一致**：英文和中文条目指向相同链接，描述内容对应

## 不被收录的常见原因

| 原因 | 说明 |
|------|------|
| 不满足 Must Have | 缺少文档、仓库私有、与 TRAE 无关 |
| 质量不达标 | 半成品、功能不可用、代码质量差 |
| 描述不清 | 无法判断项目用途和价值 |
| 重复提交 | 资源已在列表中或在姊妹仓库收录 |
| 格式错误 | 未按格式添加、未更新双语 README |

## 相关链接

- [Awesome List 定位与双层分类](/concepts/00-introduction.md)
- [贡献指南与权重评分](/concepts/01-contribution-guide.md)
- [资源分类详解](/concepts/02-resource-categories.md)
- [Awesome TRAE 仓库资源索引](/references/awesome-source.md)
