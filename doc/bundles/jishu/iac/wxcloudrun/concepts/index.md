# Concepts

本组概念文档按「平台模型 → 发布与调用 → 生态集成 → 计费 → 安全与迁移 → 方法论抽象」的顺序组织，逐篇对应官方文档的一个主题域。

| 文档 | 内容 |
|---|---|
| [平台定位与资源模型](00-platform-model.md) | 与云开发/腾讯云托管的边界、环境—服务—版本—实例四级模型、配额与运行边界 |
| [发布单、灰度与回滚](01-release-and-rollback.md) | 发布单三子流程、灰度粒度与流量粘滞、回退语义、流水线与 CLI |
| [调用链路与身份透传](02-call-and-identity.md) | 微信链路与公网链路、callContainer 参数、X-WX-* 身份头与解析风险 |
| [微信生态集成](03-wechat-ecosystem.md) | 开放接口服务、微信支付封装与回调契约、消息推送、对象存储与 COS-SDK |
| [计费模型与成本核算](04-billing-and-cost.md) | 按量计费与资源包、刊例价全表、产生用量条件、抵扣顺序与欠费处置 |
| [安全边界与迁移陷阱](05-security-and-migration.md) | DDoS 防护三段链条、不支持清单、迁移检查清单、异步任务与静默回收 |
| [可迁移模式](06-transferable-patterns.md) | 三条跨平台可复用模式：封板发布单、能力边界清单化、静默销毁风险治理 |

```{toctree}
:hidden:
:maxdepth: 2

00-platform-model
01-release-and-rollback
02-call-and-identity
03-wechat-ecosystem
04-billing-and-cost
05-security-and-migration
06-transferable-patterns
```
