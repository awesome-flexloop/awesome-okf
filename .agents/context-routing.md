# 上下文路由表

根据任务类型确定需要读取的规范文件。**按需读取，不要一次加载全部。**

## 必读基础规范

所有任务必读：
- [../AGENTS.md](../AGENTS.md) - 根目录智能体入口（步骤 1 已读取）
- [global-core-rules.md](global-core-rules.md) - 全局核心规则

## 任务类型→规范映射

| 任务类型 | 必读规范 | 可选参考 |
|---|---|---|
| **了解文档库/快速开始** | [ONBOARDING.md](ONBOARDING.md) | - |
| **新增/修改知识文档** | [rules/frontmatter.md](rules/frontmatter.md) | [../README.md](../README.md) |
| **组织 OKF bundle** | [rules/frontmatter.md](rules/frontmatter.md) | [../doc/bundles/](../doc/bundles/) |
| **添加外部参考资料** | - | [../references/](../references/) |
| **修改 .agents/ 规范本身** | [README.md](README.md) | - |
| **来自 xuanspace 的知识沉淀** | [global-core-rules.md](global-core-rules.md) | [上游 xuanspace](https://github.com/xinetzone/xuanspace) |

## 不需要额外读取规范的场景

以下简单任务可在读取完基础规范后直接执行：
- 修改单个文档的错别字
- 更新文档索引中的条目
- 补充文档的 sources 字段

## 需要完整规划的场景

以下任务建议先规划再执行：
- 新增 OKF bundle 结构
- 重构 doc/ 或 doc/bundles/ 的目录组织
- 批量迁移外部知识到 OKF 格式