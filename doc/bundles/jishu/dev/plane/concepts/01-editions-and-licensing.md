---
okf_version: "0.2"
type: Concept
title: "三套自托管版本与许可边界"
description: "Community / Commercial / Airgapped 三套独立代码库的差异、12 座席免费档、发版节奏、AGPL 与付费档能力边界"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/KCjLFr72qwngPyyI1b2ENg
  - id: official-editions
    resource: https://developers.plane.so/self-hosting/editions-and-versions
---

# 01 · 三套自托管版本与许可边界

> 这是 Plane 自托管**最容易踩的第一个坑**：它不是「一套代码 + 功能开关」，而是**三套各自独立的代码库**，换版本等于换库（F-005 / V3）。

## 1. 三套版本对照

| 维度 | Community | Commercial | Airgapped |
|------|-----------|-----------|-----------|
| 源码 | **开源**（AGPL v3.0） | 闭源 | 闭源（Commercial 的离线形态） |
| 代码库 | 独立 | 独立 | 独立 |
| 费用 | 免费 | 内置免费档 + 付费 License Key | 仅最高档企业方案 |
| 人数 | **不封顶** | 免费档 **12 座席/工作区**（F-007 / V5） | 需商务渠道（F-011 / V9） |
| 功能面 | 对齐**云端免费档** | 与**云端完全拉平** | 与 Commercial 一致 |
| License Key | 不需要 | 付费档需要（从 Prime 门户获取） | 离线激活 |
| 更新来源 | GitHub Release | 官方通道 | **自己的 Docker 镜像仓库**（F-008 / V6） |

Plane 的许可有**两层**，官方明确提示「混淆这两层是自托管新手最常见的错误」：

- **Edition（版本）**：你运行的代码库 —— Community / Commercial / Airgapped
- **Plan（方案）**：License Key 解锁的功能集 —— Free / Pro / Business / Enterprise Grid

## 2. 发版与迁移：为什么「换版本等于换库」

官方说明三条发版节奏（F-009 / V7）：

```text
新功能先在 Plane Cloud 跑通 → 再进 Commercial → 最后到 Community
```

因此同一功能在三套版本上的可用时点不同，版本号也**不互通**。官方同时给出两条保证（F-010 / V8）：

- 社区版里**没有隐藏的限制代码**
- 版本之间**没有强制迁移**（想升级到 Commercial 走官方升级流程，不想升可一直停在 Community）

## 3. 社区版的能力边界

| 能力 | 社区版 | 出处 |
|------|--------|------|
| 项目 / 任务 / 成员数量 | **不封顶** | F-012 / V4 |
| REST API | 开放 | F-012 / V10 |
| Webhook | 开放 | F-012 / V10 |
| 五种视图布局 | **全部开放** | F-024 / V14 |
| Pro 及以上能力（部分 SSO、审计日志、SCIM 等） | ❌ 需转 Commercial | F-050 / V23 |

> 付费能力的具体分档（官方口径）：SAML / OIDC SSO 在 **Pro 及以上**；审计日志、SCIM、高级认证在 **Business Plus**；LDAP、IdP 组同步、细粒度权限控制在 **Enterprise Grid**。

## 4. 三个决策问题

选型时按此顺序问：

1. **要不要开源可审可改？** 要 → Community；只要功能不要源码 → Commercial
2. **能不能接受出网做 License 校验？** 不能（隔离网/合规环境）→ Airgapped
3. **人数会不会超过 12？** 会且需要付费能力 → Commercial + License Key；不超过且只要免费档能力 → Community 或 Commercial 免费档均可

## 5. 已知边界与复核点

- Airgapped 对应 Enterprise Grid，官方曾于 2026-04 公告拟对**新购**自托管商用设 10 座席、Airgapped 设 100 座席门槛，随后公告延期（V9）→ **采购前须向官方确认当期条款**
- 12 座席为 Commercial **内置免费档**口径，与 Community「无人数上限」是两条不同规则，不要混用

下一篇 → [02 工作模型：三种时间尺度](02-work-model-three-scales.md)
