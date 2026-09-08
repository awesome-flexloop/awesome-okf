# 更新日志

## 2026-09-08

**七概念知识沉淀**：基于微信公众号文章《微软 WSL Containers 来了！》生成OKF概念文档

* 新增 `concepts/11-wsl-containers-cli.md`（R→I→E→V完整链路）
  - R阶段：40个概念事实，含安装步骤、CLI对照表、性能基准、预览限制
  - I阶段：3条四元组洞察（授权费窗口 / 共享vs独立VM架构 / 生态兼容优先）
  - E阶段："轻量替代方案评估框架"模式（6维度评估+6步决策流程+4反模式+4跨场景迁移）
  - V阶段：4视角对抗审查（魔鬼代言人/新人/老板/未来），17项补强检查全通过
  - G1-G5质量门全部通过
* 更新 `concepts/index.md`：toctree新增`11-wsl-containers-cli`
* 更新 `index.md`：文档数量从13篇改为14篇
* session: `sc-20260908-wsl-containers-okf`
* 来源：微信公众号文章（三级来源），待GA后补充官方文档作为一级来源交叉验证

## 2026-09-02

**Migration**: 从 SpecWeave docs/knowledge/learning/ 迁入 awesome-okf-xs（08 分类）

* 章节文档 frontmatter 重写为 OKF v0.2（type/title/description/tags/sources/generated/status/stale_after）
* 隐私清洗：个人文件系统路径替换为占位符；中文内嵌引号转全角
* 舍弃：源侧 README.md/index.md（导航）、log.md、seven-concepts-report.md、retrospective*/verification-report*（隐私元数据）
