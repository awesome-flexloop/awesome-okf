# .agents/ 规范目录索引

本目录包含 awesome-okf-xs 文档库 AI 智能体协作的所有规范文件。所有文件按需读取，不要一次性加载全部。

## 规范文件列表

| 文件 | 用途 | 适用场景 |
|---|---|---|
| [ONBOARDING.md](ONBOARDING.md) | 入门指南 | 第一次接触文档库、快速上手 |
| [global-core-rules.md](global-core-rules.md) | 全局核心规则 | 所有任务必须遵守的基础规则 |
| [context-routing.md](context-routing.md) | 上下文路由表 | 根据任务类型确定需要读取哪些规范 |
| [rules/frontmatter.md](rules/frontmatter.md) | 文档元数据规范 | 编写 Markdown 文档、处理元数据时 |

## 目录结构

```
.agents/
├── README.md              # 本文件 - 规范目录索引
├── ONBOARDING.md          # 入门指南
├── global-core-rules.md   # 全局核心规则
├── context-routing.md     # 上下文路由表
└── rules/                 # 具体规则目录
    └── frontmatter.md     # 文档元数据（OKF frontmatter）规范
```

## 使用方式

1. 从根目录 `AGENTS.md` 启动，遵循启动协议
2. 根据任务类型查阅 `context-routing.md`
3. 按需读取对应的规范文件
4. 涉及具体知识文档时，先确认其目标目录（doc/bundles/ 或 doc/）

## 注意事项

- 所有规范文件均为中文编写
- 内容精简实用，只包含 OKF 文档库必需的规范
- 规范继承自 xuanspace 的 `.agents/` 结构，保持轻量
- 规范更新请遵循 Conventional Commits 提交规范