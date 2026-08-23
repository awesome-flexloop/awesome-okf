# 实战示例

本目录包含 jupyter_server_terminals 的实用代码示例，覆盖常见使用场景。

* [基础终端操作](basic-operations.md) — 通过 REST API 完成终端的创建、列表查询、信息获取和删除的完整 CRUD 操作，提供 Python requests、curl、JavaScript fetch 三种实现。
* [WebSocket 实时通信](websocket-interaction.md) — 通过 WebSocket 连接终端、发送命令、接收输出，包含浏览器 JavaScript、Python websockets、Tornado 客户端三种实现，以及消息协议详解。
* [配置自动清理与指定工作目录](culler-and-cwd.md) — 配置闲置终端自动回收（Culling）、创建终端时指定初始工作目录（cwd）的完整配置与验证示例。
