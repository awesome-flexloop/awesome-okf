---
okf_version: "0.2"
---

# cnblogs-publish Skill

博客园官方 Agent Skills 仓库中唯一 skill `cnblogs-publish` 的源码教程——把 Markdown 一键发布/更新/查询/删除到博客园，默认非公开，凭据只存操作系统凭据库。

本束基于固定 commit 的源码与仓库自带参考文档，按 OKF v0.2 规范组织；覆盖 CLI、发布流水线、安全模型、可见性与审核、跨平台实现与测试基线。

* [concepts/](concepts/index.md) — 概念文档（概览、架构、安全、配置、发布、可见性、CLI、跨平台）
* [examples/](examples/index.md) — 示例（草稿发布、公开与首页推荐、维护与图片）
* [references/](references/index.md) — 信源（源码登记、MetaWeblog 约定、安全设计）

## 快速入口

| 你想… | 先读 |
|---|---|
| 知道这个 skill 能做什么 | [项目概览](/concepts/00-overview.md) |
| 马上发一篇不公开的文章 | [示例 01](/examples/01-publish-draft.md) |
| 判断"发布成功但首页没有" | [可见性与审核](/concepts/05-visibility-and-review.md) |
| 审核凭据是否安全 | [安全模型](/concepts/02-security-model.md) |
| 查命令与退出码 | [CLI 参考](/concepts/06-cli-reference.md) |
| 复核源码版本 | [源码登记](/references/source-code.md) |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
