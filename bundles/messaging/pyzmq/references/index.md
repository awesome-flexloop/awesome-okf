# References

pyzmq 源码信源登记文档，提供 API 签名、类层次、枚举值的详细参考。

| 文档 | 说明 |
|------|------|
| [constants-enums.md](constants-enums.md) | constants.py 全量枚举：Errno/ContextOption/SocketType/SocketOption（含 _opt_type）/MessageOption/Flag/PollEvent/DeviceType/SecurityMechanism/Event |
| [error-hierarchy.md](error-hierarchy.md) | 异常类层次：ZMQBaseError→ZMQError/ContextTerminated/Again/InterruptedSystemCall，_check_rc 决策表 |
| [cffi-internals.md](cffi-internals.md) | CFFI 后端内部：ffi/lib 加载、Context/Socket/Frame 实现、_opt_type 指针分派、zero-copy GC 回调 |
| [attrsettr-options.md](attrsettr-options.md) | 选项访问三层模型：set/get、setsockopt 别名、属性动态访问，Context/Socket 分流 |
