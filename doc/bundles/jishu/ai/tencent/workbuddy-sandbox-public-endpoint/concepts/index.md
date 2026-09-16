# Concepts：公网端点机制与使用边界

> 4 篇概念文档。本束是技术综述/操作提示，非经完整版本实测的 examples 教程。

| 序号 | 文档 | 核心问题 | 关键事实 |
|------|------|----------|----------|
| 00 | [公网端点机制](00-public-endpoint-mechanism.md) | 沙箱服务如何获得公网 HTTPS 入口？哪些链路已被证实？ | F-005~F-011、F-028~F-039 |
| 01 | [临时服务的适用场景与边界](01-temporary-service-use-cases.md) | Demo、Webhook、静态页、Agent API 分别能否使用？ | F-012~F-014、F-019~F-022、F-034~F-039 |
| 02 | [会话保活、生产边界与提示词改写](02-lifecycle-and-operations.md) | 如何保活、何时切换到正式托管？怎样安全提示 Agent？ | F-015~F-023、F-030~F-033、F-039 |
| 03 | [横向对标 WorkBuddy、TraeCode、TraeWork 与豆包工作](03-platform-comparison.md) | 四类产品分别通过什么底座公网化？临时链接与正式托管如何取舍？ | F-034~F-052 |

```{toctree}
:hidden:
:maxdepth: 2

00-public-endpoint-mechanism
01-temporary-service-use-cases
02-lifecycle-and-operations
03-platform-comparison
```
