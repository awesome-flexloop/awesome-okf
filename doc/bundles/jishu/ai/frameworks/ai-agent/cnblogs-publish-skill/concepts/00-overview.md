---
type: Concept
title: "项目概览：把 Agent 的协作经验发布到博客园"
description: "cnblogs-publish 的定位、仓库结构、三项设计原则与关键事实：12 个文件、12 个命令、4 个 Python 模块、50 项测试。"
tags: ["cnblogs", "overview", "agent-skill", "publishing"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
---

# 项目概览：把 Agent 的协作经验发布到博客园

`cnblogs-skills` 是博客园官方维护的 Agent Skills 仓库，根目录每个文件夹是一个独立 skill；当前仓库里只有 `cnblogs-publish` 一个 skill。它解决的问题很具体：让 Agent 把一次对话里形成的经验整理成 Markdown，然后直接发布、更新、查询或删除博客园文章，而不必让用户手工复制粘贴。

本束以源码为权威事实来源，按 OKF v0.2 规范组织。固定版本与文件哈希见[源码登记](/references/source-code.md)。

## 它提供什么

| 能力 | 入口 | 说明 |
|---|---|---|
| 首次配置 | `setup` | 在系统对话框中录入用户名、博客名、令牌并加密保存 |
| 发布 | `publish` | 默认非公开；`--publish` 才公开 |
| 更新 | `update` | 默认非公开；可保留原文章元数据 |
| 读取/列表 | `get` / `list` | 读取单篇或最近文章 |
| 删除 | `delete` | 必须显式 `--yes` |
| 分类 | `categories` | 列出博客分类 |
| 图片 | `upload` | 上传图片/文件到博客园图床 |
| 本地预览 | `render` | Markdown→HTML，不联网 |
| 状态/鉴权 | `status` / `check` | 不输出身份与令牌 |
| 清除凭据 | `forget` | 可同时删除配置文件 |

完整参数见 [CLI 参考](/concepts/06-cli-reference.md)。

## 仓库结构

仓库只有 12 个文件、3,775 行，其中 4 个 Python 模块合计 2,316 行：

```text
cnblogs-skills/
├── README.md
└── cnblogs-publish/
    ├── SKILL.md                  # Skill 定义（240 行）
    ├── README.md                 # 产品介绍（91 行）
    ├── references/               # MetaWeblog API 与安全设计
    ├── scripts/                  # 4 个 Python 模块
    └── tests/                    # 50 个测试方法
```

代码没有第三方运行时依赖，平台差异被收敛到 `secretstore.py` 与 `dialogs.py` 两个模块。

## 三项设计原则

1. **凭据不进入 Agent 可达通道。** 用户名、博客名、令牌只存在操作系统凭据库，只在脚本进程内展开；配置文件只放偏好。详见[安全模型](/concepts/02-security-model.md)。
2. **默认非公开。** `publish` / `update` 默认写草稿/私有，公开是显式动作，且公开可能进入人工审核。详见[可见性与审核](/concepts/05-visibility-and-review.md)。
3. **Markdown 原生。** 默认把 Markdown 原文提交，并自动附加 `[Markdown]` 分类让博客园按 Markdown 渲染；`--format html` 只是兜底。详见[发布流水线](/concepts/04-publishing-pipeline.md)。

## 关键数字

| 指标 | 值 | 口径 |
|---|---|---|
| 仓库文件数 | 12 | 含根 README 与 .gitignore |
| 总行数 | 3,775 | `splitlines()` |
| Python 模块 | 4 | scripts/ 下 |
| Python 行数 | 2,316 | 4 个模块合计 |
| CLI 命令 | 12 | argparse 子命令 |
| XML-RPC 方法（实际调用） | 8 | 参考文献列 9 个，`wp.newCategory` 未调用 |
| 测试方法 | 50（15 类） | 实测 50 项，Windows 跳过 1 项 |
| 配置键 | 7 | 全部为偏好，无凭据 |

## 建议阅读路径

1. 先读本章与 [CLI 参考](/concepts/06-cli-reference.md)，建立"能做什么"的轮廓。
2. 再读[架构设计](/concepts/01-architecture.md)与[发布流水线](/concepts/04-publishing-pipeline.md)，理解一次发布经过哪些步骤。
3. 安全敏感场景补读[安全模型](/concepts/02-security-model.md)与[首次配置](/concepts/03-credentials-setup.md)。
4. 需要判断"发布成功是否等于已公开"时读[可见性与审核](/concepts/05-visibility-and-review.md)。
5. 工程化/移植时读[跨平台与测试](/concepts/07-cross-platform-and-tests.md)。

## 相关概念

- [架构设计](/concepts/01-architecture.md)
- [CLI 参考](/concepts/06-cli-reference.md)
- [源码登记](/references/source-code.md)
