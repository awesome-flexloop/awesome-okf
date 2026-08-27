---
type: Reference
title: 社区讨论仓库资源索引
description: trae-discussions 仓库源码位置、3 文件极简结构、GitHub Discussions 分类引导和 Quick Links 的信源登记簿
tags: [discussions, community, github-discussions, minimal-hub, source-index, trae-discussions]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/discussions-source.md
    title: "Trae Discussions 源码信源"
---

# 社区讨论仓库资源索引

本文档汇总 trae-discussions 仓库的极简导航枢纽设计、讨论分类体系和社区引导机制。

## 仓库基本信息

| 项目 | 内容 |
|------|------|
| 仓库地址 | `trae-community/trae-discussions`（GitHub） |
| 许可证 | MIT License |
| 定位 | TRAE 社区技术讨论和知识分享的导向枢纽（reference point） |
| 语言支持 | 中英双语（README.md / README.zh-CN.md） |

## 仓库文件结构（仅 3 个文件）

```
trae-discussions/
├── README.md          # 英文导航页
├── README.zh-CN.md    # 中文导航页
└── LICENSE            # MIT 许可证
```

> ⚠️ **事实记录**：
> - 仓库**无** `assets/` 目录、**无** `.github/` 目录、**无**任何其他源码文件
> - README 中横幅图片引用 `./assets/images/Discussions.gif`（英文）和 `./assets/images/Friends.gif`（中文），但 `assets/images/` 目录**不存在**——图片路径引用失效
> - 整个仓库只有 3 个文件，是真正的"空仓库做枢纽"

## 讨论平台

- **唯一互动平台**：GitHub 组织级 Discussions
- **入口链接**：https://github.com/orgs/trae-community/discussions
- **注意**：使用的是组织级（orgs/trae-community）Discussions，而非仓库级 Discussions

## 5 个讨论分类

| 分类 | Emoji | 用途 |
|------|-------|------|
| General | 📚 | 欢迎介绍、社区公告、离题对话 |
| Ideas & Suggestions | 💡 | 功能请求、改进建议、社区倡议 |
| Q&A | ❓ | 帮助支持、操作问题、故障排除 |
| Knowledge Sharing | 📖 | 最佳实践、案例研究、提示技巧 |
| Collaboration | 🤝 | 项目配对、寻找贡献者、团队组建 |

## 4 步参与指南

1. 访问 GitHub Discussions 页面
2. 点击顶部 "Discussions" 标签
3. 浏览现有讨论或创建新讨论
4. 评论、添加反应（emoji）、贡献内容

## 4 条社区指南

1. **Be Respectful（尊重他人）**：欢迎新人、建设性反馈、无攻击言论
2. **Stay On Topic（保持主题）**：使用适当分类、链接相关讨论
3. **Search First（先搜索）**：发帖前搜索是否已有相同讨论、避免重复
4. **Quality Content（质量内容）**：清晰标题、提供背景信息、正确格式

## Quick Links（快速链接）

| 链接 | 目标 |
|------|------|
| 组织主页 | trae-community GitHub Organization |
| 所有讨论 | github.com/orgs/trae-community/discussions |
| 贡献指南 | .github/profile/CONTRIBUTING.md |
| 行为准则 | .github/profile/CODE_OF_CONDUCT.md（英文）/ CODE_OF_CONDUCT.zh-CN.md（中文） |

> 💡 Quick Links 指向的 `.github/profile/` 目录不在本仓库中，而是在 GitHub Organization 的 `.github` 仓库中。

## 相关链接

- [GitHub Discussions 作为社区论坛](../concepts/00-introduction.md)
- [讨论分类与使用指南](../concepts/01-discussion-categories.md)
- [社区礼仪与有效提问](../concepts/02-community-etiquette.md)
- [发起讨论示例](../examples/start-discussion.md)
