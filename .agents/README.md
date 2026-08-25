# .agents/ 规范目录索引

本目录包含 awesome-okf-xs 文档库 AI 智能体协作的所有规范文件。所有文件按需读取，不要一次性加载全部。

## 规范文件列表

| 文件 | 用途 | 适用场景 |
|---|---|---|
| [ONBOARDING.md](ONBOARDING.md) | 入门指南 | 第一次接触文档库、快速上手、命令速查 |
| [global-core-rules.md](global-core-rules.md) | 全局核心规则 | 所有任务必须遵守的基础规则（启动协议、内容敏感度、OKF组织、构建CI、修复验证） |
| [context-routing.md](context-routing.md) | 上下文路由表 | 根据任务类型确定需要读取哪些规范 |
| [rules/frontmatter.md](rules/frontmatter.md) | 文档元数据规范 | 编写 Markdown 文档、处理 YAML frontmatter、Sphinx 构建兼容性 |

## 目录结构

```
.agents/
├── README.md              # 本文件 - 规范目录索引
├── ONBOARDING.md          # 入门指南（快速开始、命令速查）
├── global-core-rules.md   # 全局核心规则（9节）
├── context-routing.md     # 上下文路由表（任务→规范映射）
└── rules/                 # 具体规则目录
    └── frontmatter.md     # 文档元数据（OKF v0.2 frontmatter + Sphinx兼容性）
```

## 使用方式

1. 从根目录 [`AGENTS.md`](../AGENTS.md) 启动，遵循启动协议（步骤 1-4）
2. 根据任务类型查阅 [`context-routing.md`](context-routing.md)
3. 按需读取对应的规范文件
4. 涉及具体知识文档时，先确认其目标目录（`doc/bundles/` 或 `doc/`）
5. 新增/修改 bundle 后运行 `invoke gates.toctrees` 验证完整性
6. 修改构建配置后运行 `invoke build` 验证构建通过

## 设计原则

- **轻量定位**：所有规范文件均为中文编写，内容精简实用，只包含 OKF 文档库协作必需的规范
- **按需读取**：不一次性加载全部规范，通过路由表按任务类型引导
- **嵌套兼容**：作为 SpecWeave projects/ 区域的子项目，启动协议与上层路由兼容（含内容敏感度预检），但不复制主项目的复杂子命令体系
- **事实准确**：规范描述必须与项目实际目录结构和代码一致
- **规范更新**：修改本目录下的规范文件时，确保 `AGENTS.md` 的入口表与 `context-routing.md` 同步更新，遵循 Conventional Commits 提交规范
