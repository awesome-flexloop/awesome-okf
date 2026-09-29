---
type: Changelog
scope: pi-cli
name: log
version: "0.1.0"
---

# Changelog

## [0.1.0] - 2026-08-23

### Added

- 初始 OKF v0.2 wiki bundle 生成
- `spec/facts.md`：51条带精确文件路径和行号引用的源码事实（F-001 ~ F-051）
- `spec/insights.md`：5条核心洞察，涵盖 Provider/Models 分层、compat 垫片消亡、TUI 差分渲染机制、内置 prompt 工作流、供应链安全
- `concepts/00-introduction.md`：项目简介，三个核心包和辅助包概览
- `concepts/01-monorepo-architecture.md`：包职责、构建顺序、路径别名、锁步版本控制
- `concepts/02-ai-package.md`：models.ts 模型管理、oauth.ts 类型、cli.ts 命令、compat.ts 兼容层、images.ts 图片生成、types.ts 类型系统
- `concepts/03-tui-system.md`：Component 接口、差分渲染引擎、overlay 系统、模糊搜索、LaTeX、键绑定、终端图片
- `concepts/04-builtin-prompts.md`：cl/is/pr/sa/wr 五个内置 prompt 的用途、流程和约束
- `examples/01-basic-usage.md`：环境要求、源码安装构建、pi-ai CLI 登录、Agent API 对话示例
- `references/source.md`：源码信源索引，文件角色与事实 ID 映射
- 根 `index.md`（type: bundle, okf_version: 0.2）和子目录索引文件
