# awesome-okf-xs 入门指南

## 快速开始

### 前置条件

- Git
- 任意支持 Markdown 与 YAML frontmatter 的编辑器

### 环境准备

1. 克隆仓库：

   ```bash
   git clone git@github.com:awesome-flexloop/awesome-okf.git
   ```

2. 查看目录结构，了解 doc/ 与 doc/bundles/ 的用途

3. 阅读根目录 `AGENTS.md` 与 `context-routing.md`，了解协作规范

## 能力速查表

| 能力 | 方式 | 说明 |
|---|---|---|
| 了解文档库结构 | 阅读本文件「目录结构速览」 | 掌握 doc/bundles 分工 |
| 查找知识文档 | 进入 `doc/index.md` 或 `doc/bundles/` | 按 bundle 索引定位 |
| 新增知识文档 | 按 `context-routing.md` 确定存放目录 | 遵循 frontmatter 规范 |
| AI 协作 | 阅读 `AGENTS.md` | 遵循启动协议 |

## 目录结构速览

```
awesome-okf-xs/
├── doc/                # Sphinx 文档工程
│   └── bundles/        # OKF bundle 文档（结构化知识束）
├── .agents/            # AI 智能体规范
├── AGENTS.md           # 智能体入口
└── README.md           # 项目说明
```

## 第一次任务？

如果你是第一次在本文档库中执行任务，请：

1. 已读取根目录 `AGENTS.md`
2. 根据任务类型查阅 `context-routing.md`
3. 涉及具体知识文档时，先确认其目标目录（doc/bundles/ 或 doc/）
4. 简单任务可直接执行，复杂任务先规划再动手

## 文档规范

- 语言：正文中文，文件名 kebab-case 纯英文
- 格式：Markdown + OKF v0.2 YAML frontmatter
- 路径引用：相对路径，禁止 file:/// 绝对路径

详细规范见 [rules/frontmatter.md](rules/frontmatter.md)。