# 信源登记簿

本目录登记 jupyter_client Wiki 所引用的核心源码模块，作为概念文档中 `sources` 字段的指向目标。

| 信源文件 | 覆盖源码 | 说明 |
|---------|---------|------|
| [client-source.md](client-source.md) | `jupyter_client/client.py` | KernelClient 基类：五通道管理、消息发送方法、execute_interactive |
| [manager-source.md](manager-source.md) | `jupyter_client/manager.py` | KernelManager/AsyncKernelManager：内核生命周期、Provisioner 委托 |
| [session-source.md](session-source.md) | `jupyter_client/session.py` | Session 消息协议：序列化、HMAC签名、ZMQ收发、Message包装 |
| [provisioning-source.md](provisioning-source.md) | `jupyter_client/provisioning/` | Provisioner 框架：KernelProvisionerBase、LocalProvisioner、工厂模式 |
| [channels-connect-source.md](channels-connect-source.md) | `jupyter_client/channels.py` + `connect.py` | 通道实现、连接文件管理、Socket创建、心跳监控 |
