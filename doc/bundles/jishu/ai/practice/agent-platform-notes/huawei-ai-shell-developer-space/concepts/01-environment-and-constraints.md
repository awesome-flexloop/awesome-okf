---
type: Concept
title: "环境形态与约束"
description: "区分体验型和持久化型环境，理解 ARM 架构、临时凭据、保存和配额边界。"
tags: [concept, ai-shell, arm, cloud-development, constraints]
sources:
  - id: blog
    resource: "/references/article-source.md"
  - id: verification
    resource: "/references/verification.md"
generated: { by: process:seven-concepts-e, at: "2026-09-20T00:00:00Z" }
verified: [{ by: process:seven-concepts-v, at: "2026-09-20T00:00:00Z" }]
status: stable
stale_after: "2026-12-31"
---

# 环境形态与约束

## 体验型与持久化型

原文把环境分为体验版和持久化版（F-005）。体验版的释放时长、持久化版的核时扣减和自动关机行为属于作者实测，不能当作长期固定政策（F-006、F-007、F-019；见[核验报告](../references/verification.md)）。

因此，使用时应遵循两个动作：

1. **进入后先看控制台提示**：确认当前环境类型、剩余时间、额度和关机规则。
2. **退出前保存产物**：代码、配置、日志和报告不要只放在临时容器里。

## ARM 不是“免费机器”的附注，而是选型条件

文章展示的是 aarch64/ARM 环境（F-009、F-011）。ARM 对 Python、Shell、Git 等常见工具通常影响较小，但预编译包、闭源 CLI、容器基础镜像和二进制扩展可能存在架构差异。

建议在项目开始时记录：

```bash
uname -m
cat /etc/os-release
df -h
free -h
```

这些命令是通用 Linux 探查命令，示例不代表华为云官方固定初始化脚本。若发现依赖只提供 x86 构建，应优先选择多架构版本、替代工具或在本地/正式 CI 环境构建。

## 凭据与数据边界

官方流程包含把临时访问凭据同步到 AI Shell 的授权步骤（F-004、F-023）。因此：

- 不要把长期 AK/SK 粘贴到对话中。
- 对生成的命令逐条审阅，尤其是删除、创建、授权和公网暴露操作。
- 任何需要长期保存的数据都应复制到受控仓库或对象存储。
