# 信源登记簿

本目录包含 Enterprise Gateway 源码的关键信源登记文档，为 concepts/ 和 examples/ 中的溯源引用提供目标。

## 信源清单

* [主应用入口源码](app-entry-source.md) — EnterpriseGatewayApp初始化流程、HTTP服务器启动、动态配置、内核关闭生命周期、SSL与安全。
* [配置Mixin与Handler Mixin源码](config-mixin-source.md) — EnterpriseGatewayConfigMixin的50+配置项、CORSMixin/TokenAuthorizationMixin/JSONErrorsMixin三个横切关注点Mixin。
* [ProcessProxy进程代理体系源码](process-proxy-source.md) — BaseProcessProxyABC抽象基类、LocalProcessProxy、RemoteProcessProxy及8种具体实现（K8s/YARN/Docker/SSH/Conductor/CRD/Spark Operator）。
* [内核管理器源码](kernel-manager-source.md) — RemoteMappingKernelManager多内核管理、RemoteKernelManager单内核生命周期、ProcessProxy集成、HA恢复。
* [ResponseManager加密通信源码](response-manager-source.md) — RSA+AES加密的连接信息回传通道、Response事件机制、KernelChannel枚举。
* [HTTP Handler源码](handlers-source.md) — API端点路由、Handler动态Mixin替换机制、Swagger文档服务。
* [会话管理与KernelSpec缓存源码](session-manager-source.md) — SessionManager内存会话、FileKernelSessionManager/WebhookKernelSessionManager持久化、KernelSpecCache文件监控缓存。

```{toctree}
:hidden:

app-entry-source
config-mixin-source
handlers-source
kernel-manager-source
process-proxy-source
response-manager-source
session-manager-source
```
