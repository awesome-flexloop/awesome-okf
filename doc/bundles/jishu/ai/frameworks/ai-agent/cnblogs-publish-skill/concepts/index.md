# Concepts 索引

本目录是 cnblogs-publish 的概念文档，按"先轮廓、再机制、后工程化"的顺序组织。

## 文档清单

| 文档 | 内容 |
|---|---|
| [00 项目概览](/concepts/00-overview.md) | 定位、仓库结构、三项设计原则与关键数字 |
| [01 架构设计](/concepts/01-architecture.md) | 四模块分层、发布数据流、设计取舍 |
| [02 安全模型](/concepts/02-security-model.md) | 凭据资产、三层控制、五条禁止事项 |
| [03 首次配置](/concepts/03-credentials-setup.md) | setup 状态机、三平台对话框、失败处置 |
| [04 发布流水线](/concepts/04-publishing-pipeline.md) | frontmatter、标题/分类、AI 声明、图片、输出契约 |
| [05 可见性与审核](/concepts/05-visibility-and-review.md) | 默认非公开、审核语义、首页推荐、update 风险 |
| [06 CLI 参考](/concepts/06-cli-reference.md) | 12 个命令、选项矩阵、6 个退出码 |
| [07 跨平台与测试](/concepts/07-cross-platform-and-tests.md) | 四后端、50 项测试、真实主机边界 |

## 建议阅读顺序

1. 00 → 06 → 示例 01：先能跑通一次非公开草稿。
2. 01 → 04 → 05：理解发布机制与可见性语义。
3. 02 → 03 → references/security-design：安全敏感场景。
4. 07 → references/source-code：移植或二次开发。

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-architecture
02-security-model
03-credentials-setup
04-publishing-pipeline
05-visibility-and-review
06-cli-reference
07-cross-platform-and-tests
```
