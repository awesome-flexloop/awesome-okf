# Examples

本组示例文档给出基于官方文档编写的参考流程。**所有示例均未在真实云托管环境部署验证**，代码块为按官方文档描述自行编写的非官方示例。

| 文档 | 内容 |
|---|---|
| [第一次部署：从零到可用服务](01-first-deploy.md) | 开通前提、模板部署与自定义部署、端口与规格配置、构建超时与时区 |
| [从小程序调用服务并透传用户身份](02-call-and-identity.md) | init 时序、callContainer 参数与身份头读取、公网与微信链路差异 |
| [发布单、灰度与回滚实操](03-release-gray-rollback.md) | 发布三步流程、测试与灰度配置、回退语义、发布前检查清单 |
| [从传统服务迁移到云托管并核对成本](04-migration-and-cost.md) | 迁移前检查清单、运行时假设改造、按刊例价估算月度成本 |

```{toctree}
:hidden:
:maxdepth: 2

01-first-deploy
02-call-and-identity
03-release-gray-rollback
04-migration-and-cost
```
