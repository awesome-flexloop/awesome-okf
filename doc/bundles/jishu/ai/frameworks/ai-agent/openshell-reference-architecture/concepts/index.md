# 架构学习路径

先区分产品与设计范围，再学习软件执行边界、企业工作区和硬件治理。部署页给出验收目标；洞察页的迁移模式按单案例记录。

| 章节 | 学习结果 |
|---|---|
| [范围与术语](00-scope-and-terms.md) | 区分 OpenShell 软件、参考架构和 Sentry |
| [软件执行边界](01-runtime-trust-boundary.md) | 解释 Supervisor、fence、策略和凭证生命周期 |
| [企业工作区](02-enterprise-workspace.md) | 定位七平面及 Phase 0/I/II |
| [Sentry 硬件治理](03-sentry-hardware-governance.md) | 区分网络授权、带外证据与响应时序 |
| [部署与验收](04-deployment-and-acceptance.md) | 分开评估隔离、控制和硬件放置 |
| [洞察与迁移](05-insights-and-pattern.md) | 用证据约束治理判断，识别可证伪条件 |

```{toctree}
:hidden:
:maxdepth: 2

00-scope-and-terms
01-runtime-trust-boundary
02-enterprise-workspace
03-sentry-hardware-governance
04-deployment-and-acceptance
05-insights-and-pattern
```
