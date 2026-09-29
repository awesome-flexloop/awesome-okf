---
type: Example
title: "场景决策矩阵"
description: "通过持续时间、架构和数据要求判断 AI Shell、正式 VPS 或本地环境。"
tags: [example, ai-shell, vps, decision-matrix]
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

# 场景决策矩阵

| 场景 | 首选 | 进入前检查 | 不要做什么 |
|---|---|---|---|
| 学 Shell、Git、Python | AI Shell | 架构、释放时间、文件保存位置 | 不保存就离开 |
| 快速验证 Python/脚本 | AI Shell | ARM 依赖、网络权限、输入数据 | 把临时环境当正式 CI |
| 体验 Agent 编程 | AI Shell | 模型、技能、授权范围 | 盲目执行生成命令 |
| 临时批处理 | AI Shell 或本地脚本 | 数据敏感性、任务时长、输出备份 | 上传敏感数据 |
| 网站/API/数据库长期运行 | VPS/云服务器 | 备份、监控、网络、安全组 | 依赖临时容器保活 |
| x86-only 二进制构建 | x86 CI/VPS | 是否有 ARM 版本或多架构镜像 | 在 ARM 上反复硬编译 |

## 一个三问决策法

1. **会不会在环境释放后仍需要服务继续运行？** 如果会，选择正式基础设施。
2. **是否依赖 x86-only 软件或二进制？** 如果是，先选 x86 环境或验证多架构支持。
3. **是否包含长期凭据或敏感数据？** 如果是，先完成数据与密钥边界设计。

三个问题都回答“否”时，AI Shell 适合作为低成本实验入口；任一回答“是”，都需要额外的架构和安全评审。
