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
| **组织 OKF bundle** | [rules/frontmatter.md](rules/frontmatter.md)、[global-core-rules.md](global-core-rules.md) §3 | [../doc/bundles/](../doc/bundles/) 现有 bundle 实例 |
| **构建文档/本地预览** | [global-core-rules.md](global-core-rules.md) §7 | [../tasks/docs.py](../tasks/docs.py) |
| **运行质量门/CI 检查** | [global-core-rules.md](global-core-rules.md) §3、§7 | [../scripts/](../scripts/) 检查脚本 |
| **修复构建错误** | [rules/frontmatter.md](rules/frontmatter.md) §14 | [../doc/conf.py](../doc/conf.py) |
| **修改 doc/conf.py** | [rules/frontmatter.md](rules/frontmatter.md) §14、[global-core-rules.md](global-core-rules.md) §5.1 | - |
| **修改 .agents/ 规范本身** | [README.md](README.md)、[global-core-rules.md](global-core-rules.md) §9 | - |
| **来自 xuanspace 的知识沉淀** | [global-core-rules.md](global-core-rules.md) | [上游 xuanspace](https://github.com/xinetzone/xuanspace) |

## 不需要额外读取规范的场景

以下简单任务可在读取完基础规范后直接执行：
- 修改单个文档的错别字
- 更新文档索引中的条目
- 补充文档的 sources 字段
- 运行 `invoke build` 或 `invoke gates.*` 命令（前提是不修改构建配置）

## 需要完整规划的场景

以下任务建议先规划再执行：
- 新增 OKF bundle 结构（含子目录）
- 重构 `doc/` 或 `doc/bundles/` 的目录组织
- 批量迁移外部知识到 OKF 格式
- 修改 `doc/conf.py` 构建配置
- 修改 `.agents/` 规范体系本身

## 规范快速索引

| 规范 | 核心内容 | 何时查阅 |
|---|---|---|
| [ONBOARDING.md](ONBOARDING.md) | 快速开始、命令速查、目录结构 | 第一次接触项目、忘记命令 |
| [global-core-rules.md](global-core-rules.md) | 启动协议、内容敏感度、OKF组织、构建验证、三阶段递进 | 所有任务必读基础 |
| [rules/frontmatter.md](rules/frontmatter.md) | OKF v0.2 YAML frontmatter 完整规范、Sphinx 兼容性 | 编写/修改 Markdown 文档时 |
| [README.md](README.md) | .agents/ 目录结构与文件清单 | 修改规范本身时 |
