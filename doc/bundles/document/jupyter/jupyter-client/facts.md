---
type: Facts
okf_version: '0.2'
title: jupyter-client 源码事实清单
tags:
- jupyter
- kernel
- zmq
- client
- protocol
- python
generated: '2026-08-22'
sources:
- ../../../../../external/libs/jupyter/jupyter_client/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/_version.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/channels.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/multikernelmanager.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/launcher.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/restarter.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/jsonutil.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/connect.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/client.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/blocking/client.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/asynchronous/client.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/manager.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/ioloop/manager.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/kernelspec.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/session.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/provisioning/provisioner_base.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/provisioning/local_provisioner.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/provisioning/factory.py
- ../../../../../external/libs/jupyter/jupyter_client/jupyter_client/__init__.py
---

# jupyter-client Facts

## 项目元数据

- F-001: pyproject.toml:6 — 包名称为 `jupyter_client`
- F-002: pyproject.toml:8 — 包描述为 "Jupyter protocol implementation and client libraries"
- F-003: pyproject.toml:21 — 要求 Python 版本 `>=3.10`
- F-004: pyproject.toml:22-29 — 运行时依赖：jupyter_core>=5.1, python-dateutil>=2.8.2, pyzmq>=25.0, tornado>=6.4.1, typing-extensions>=4.13.0, traitlets>=5.3
- F-005: pyproject.toml:2-3 — 构建系统使用 hatchling>=1.5，build-backend 为 "hatchling.build"
- F-006: jupyter_client/_version.py:6 — 版本号为 `8.9.1`
- F-007: jupyter_client/_version.py:20-21 — Jupyter 协议版本为 `5.4`（protocol_version_info = (5, 4)）
- F-008: pyproject.toml:79-82 — CLI 入口点：jupyter-kernelspec → kernelspecapp:KernelSpecApp.launch_instance；jupyter-run → runapp:RunApp.launch_instance；jupyter-kernel → kernelapp:main
- F-009: pyproject.toml:84-85 — 注册 entry point group `jupyter_client.kernel_provisioners`，默认 `local-provisioner` 指向 `jupyter_client.provisioning:LocalProvisioner`
- F-010: pyproject.toml:77 — 可选依赖 `orjson`：安装后用于更快的 JSON pack/unpack

## 目录结构

- F-013: jupyter_client/ — 主包目录，包含核心模块
- F-014: jupyter_client/asynchronous/ — 异步客户端子包，含 __init__.py 和 client.py
- F-015: jupyter_client/blocking/ — 阻塞式子包子包，含 __init__.py 和 client.py
- F-016: jupyter_client/ioloop/ — Tornado IOLoop 管理器子包，含 __init__.py、manager.py、restarter.py
- F-017: jupyter_client/provisioning/ — 内核供给工厂子包，含 __init__.py、factory.py、local_provisioner.py、provisioner_base.py
- F-018: jupyter_client/ssh/ — SSH 隧道子包，含 __init__.py、forward.py、tunnel.py
- F-019: jupyter_client/channels.py — ZMQ 通道实现（HBChannel, ZMQSocketChannel, AsyncZMQSocketChannel）
- F-020: jupyter_client/multikernelmanager.py — 多内核管理器（MultiKernelManager, AsyncMultiKernelManager）
- F-021: jupyter_client/launcher.py — 内核进程启动工具（launch_kernel 函数）
- F-022: jupyter_client/restarter.py — 内核自动重启监控基类（KernelRestarter）
- F-024: jupyter_client/jsonutil.py — JSON 日期/二进制处理工具

## 核心类/接口

- F-028: jupyter_client/connect.py:346 — `ConnectionFileMixin` 继承自 `LoggingConfigurable`，封装连接文件读写逻辑
- F-029: jupyter_client/connect.py:39 — `KernelConnectionInfo` 是 TypedDict，包含 shell_port、iopub_port、stdin_port、control_port、hb_port、ip、key、transport、signature_scheme、kernel_name、session、curve_publickey、curve_secretkey 字段
- F-030: jupyter_client/client.py:74 — `KernelClient` 继承自 `ConnectionFileMixin`，通过五个 ZMQ 通道与内核通信
- F-031: jupyter_client/blocking/client.py:33 — `BlockingKernelClient` 继承自 `KernelClient`，提供阻塞式 API
- F-032: jupyter_client/asynchronous/client.py:30 — `AsyncKernelClient` 继承自 `KernelClient`，使用 `zmq.asyncio.Context`
- F-033: jupyter_client/manager.py:121 — `KernelManager` 继承自 `ConnectionFileMixin`，管理单个内核子进程生命周期
- F-034: jupyter_client/manager.py:801 — `AsyncKernelManager` 继承自 `KernelManager`，使用 `zmq.asyncio.Context`，所有管理方法为 coroutine
- F-035: jupyter_client/ioloop/manager.py:36 — `IOLoopKernelManager` 继承自 `KernelManager`，将 socket 包装为 ZMQStream
- F-036: jupyter_client/ioloop/manager.py:77 — `AsyncIOLoopKernelManager` 继承自 `AsyncKernelManager`，将 socket 包装为 ZMQStream
- F-037: jupyter_client/kernelspec.py:25 — `KernelSpec` 继承自 `HasTraits`，包含 argv、name、mimetype、display_name、language、kernel_protocol_version、env、resource_dir、interrupt_mode、metadata 字段
- F-038: jupyter_client/kernelspec.py:125 — `KernelSpecManager` 继承自 `LoggingConfigurable`，管理内核规格发现与安装
- F-039: jupyter_client/session.py:337 — `Session` 继承自 `Configurable`，处理消息序列化、HMAC 签名与发送
- F-040: jupyter_client/multikernelmanager.py:52 — `MultiKernelManager` 继承自 `LoggingConfigurable`，管理多个内核实例
- F-041: jupyter_client/multikernelmanager.py:598 — `AsyncMultiKernelManager` 继承自 `MultiKernelManager`，支持 pending kernels 模式
- F-042: jupyter_client/channels.py:35 — `HBChannel` 继承自 `Thread`，以守护线程方式监控心跳
- F-043: jupyter_client/channels.py:214 — `ZMQSocketChannel` 封装同步 ZMQ socket 的消息收发
- F-044: jupyter_client/channels.py:291 — `AsyncZMQSocketChannel` 继承自 `ZMQSocketChannel`，使用 `zmq.asyncio.Socket` 提供 async 方法
- F-045: jupyter_client/provisioning/provisioner_base.py:18 — `KernelProvisionerBase` 是 ABC，元类为 KernelProvisionerMeta（ABCMeta + LoggingConfigurable 的 metaclass）
- F-046: jupyter_client/provisioning/local_provisioner.py:20 — `LocalProvisioner` 继承自 `KernelProvisionerBase`，使用 subprocess.Popen 启动本地内核
- F-047: jupyter_client/provisioning/factory.py:17 — `KernelProvisionerFactory` 继承自 `SingletonConfigurable`，单例模式创建 provisioner 实例
- F-048: jupyter_client/restarter.py:20 — `KernelRestarter` 继承自 `LoggingConfigurable`，监控内核状态并自动重启
- F-049: jupyter_client/session.py:244 — `SessionFactory` 继承自 `LoggingConfigurable`，持有 context、session、loop 属性
- F-050: jupyter_client/session.py:277 — `Message` 类将 dict 键映射为属性访问，支持嵌套 dict 递归转换

## 关键函数/API

- F-052: jupyter_client/connect.py:55-203 — `write_connection_file()` 生成 JSON 连接文件，支持 tcp/ipc 传输，随机端口分配，写入 secure_write 文件
- F-053: jupyter_client/connect.py:206-267 — `find_connection_file()` 搜索连接文件，支持 glob 模式，按访问时间返回最新匹配
- F-054: jupyter_client/connect.py:270-328 — `tunnel_to_kernel()` 通过 SSH 建立五个端口的隧道
- F-055: jupyter_client/launcher.py:14-184 — `launch_kernel()` 使用 subprocess.Popen 启动内核进程，Windows 上创建中断事件和 CREATE_NEW_PROCESS_GROUP，Unix 上设置 start_new_session=True
- F-056: jupyter_client/manager.py:843-858 — `start_new_kernel()` 同步便捷函数：创建 KernelManager → start_kernel → client → start_channels → wait_for_ready
- F-057: jupyter_client/manager.py:861-876 — `start_new_async_kernel()` 异步版本便捷函数
- F-058: jupyter_client/manager.py:879-894 — `run_kernel()` 是 context manager，退出时自动 stop_channels 和 shutdown_kernel(now=True)
- F-059: jupyter_client/client.py:601-666 — `KernelClient.execute()` 发送 execute_request 到 shell 通道，content 包含 code、silent、store_history、user_expressions、allow_stdin、stop_on_error
- F-060: jupyter_client/client.py:668-689 — `KernelClient.complete()` 发送 complete_request（tab 补全）
- F-061: jupyter_client/client.py:691-720 — `KernelClient.inspect()` 发送 inspect_request（对象内省），支持 detail_level 0-2
- F-062: jupyter_client/client.py:722-766 — `KernelClient.history()` 发送 history_request，支持 range/tail/search 三种访问类型
- F-063: jupyter_client/client.py:768-777 — `KernelClient.kernel_info()` 发送 kernel_info_request
- F-064: jupyter_client/client.py:779-789 — `KernelClient.comm_info()` 发送 comm_info_request
- F-065: jupyter_client/client.py:801-810 — `KernelClient.is_complete()` 发送 is_complete_request（代码完整性检查）
- F-066: jupyter_client/client.py:812-824 — `KernelClient.input()` 在 stdin 通道发送 input_reply
- F-067: jupyter_client/client.py:826-845 — `KernelClient.shutdown()` 在 control 通道发送 shutdown_request
- F-068: jupyter_client/client.py:445-598 — `KernelClient._async_execute_interactive()` 使用 zmq.asyncio.Poller 同时监听 iopub 和 stdin 通道，实现交互式执行
- F-069: jupyter_client/session.py:655-679 — `Session.msg()` 构建嵌套消息 dict：header、msg_id、msg_type、parent_header、content、metadata
- F-070: jupyter_client/session.py:760-878 — `Session.send()` 构建并发送消息，支持 track（零拷贝跟踪）、buffers、PID 检查
- F-071: jupyter_client/session.py:917-958 — `Session.recv()` 接收并解包消息，处理 zmq.EAGAIN 返回 None
- F-072: jupyter_client/session.py:696-758 — `Session.serialize()` 将消息 dict 序列化为 wire format：[idents..., DELIM, HMAC, p_header, p_parent, p_metadata, p_content]
- F-073: jupyter_client/session.py:1026-1101 — `Session.deserialize()` 反序列化 wire format 为消息 dict，验证 HMAC 签名和重播攻击
- F-074: jupyter_client/session.py:681-694 — `Session.sign()` 使用 HMAC 对 [p_header, p_parent, p_metadata, p_content] 计算签名，无 key 时返回空 bytes
- F-075: jupyter_client/session.py:589-605 — `Session.clone()` 创建 Session 副本，fork digest_history 集合
- F-076: jupyter_client/client.py:291-319 — `KernelClient.start_channels()` 启动 shell、iopub、stdin、hb、control 五个通道的线程
- F-077: jupyter_client/client.py:321-338 — `KernelClient.stop_channels()` 停止所有通道并销毁 context（如果自己创建的）
- F-078: jupyter_client/manager.py:335-348 — `KernelManager.client()` 创建配置好的客户端实例，传入 session=True 的连接信息
- F-079: jupyter_client/kernelspec.py:205-231 — `KernelSpecManager.find_kernel_specs()` 遍历 kernel_dirs 发现内核，支持 ensure_native_kernel 自动注册 python3
- F-080: jupyter_client/kernelspec.py:275-289 — `KernelSpecManager.get_kernel_spec()` 根据名称获取 KernelSpec，找不到抛出 NoSuchKernel
- F-081: jupyter_client/kernelspec.py:352-410 — `KernelSpecManager.install_kernel_spec()` 将内核目录复制到目标位置
- F-082: jupyter_client/blocking/client.py:19-30 — `wrapped()` 装饰器函数实现 reply=True 时发送消息后自动等待对应回复
- F-083: jupyter_client/blocking/client.py:61-72 — BlockingKernelClient 通过 `reqrep(wrapped, ...)` 将 execute、complete、inspect、history、kernel_info、comm_info、shutdown 等方法包装为支持 reply 参数
- F-084: jupyter_client/client.py:39-71 — `reqrep()` 装饰器工厂为请求方法添加 reply/timeout 参数文档和自动回复等待逻辑

## 内核管理机制

- F-085: jupyter_client/manager.py:65-77 — `_ShutdownStatus` 枚举：Unset、ShutdownRequest、SigtermRequest、SigkillRequest
- F-086: jupyter_client/manager.py:93-118 — `in_pending_state` 装饰器：为被装饰方法创建 `_ready` Future，方法完成后 set_result 或 set_exception
- F-087: jupyter_client/manager.py:240-252 — `shutdown_wait_time` 默认 5.0 秒，关闭流程：SIGINT → shutdown_request → 等待 waittime/2 → SIGTERM → 等待 waittime/2 → SIGKILL
- F-088: jupyter_client/manager.py:452-490 — `_async_pre_start_kernel()` 流程：设置 shutting_down=False → 生成/获取 kernel_id → 保存 _launch_args → 检查 CurveZMQ 加密策略 → 创建 provisioner → 调用 provisioner.pre_launch()
- F-089: jupyter_client/manager.py:423-437 — `_async_launch_kernel()` 调用 provisioner.launch_kernel()，然后 _reconcile_connection_info()
- F-090: jupyter_client/manager.py:494-507 — `_async_post_start_kernel()` 调用 start_restarter()、_connect_control_socket()、provisioner.post_launch()
- F-091: jupyter_client/manager.py:532-543 — `_async_request_shutdown()` 通过 control socket 发送 shutdown_request，调用 provisioner.shutdown_requested()
- F-092: jupyter_client/manager.py:545-584 — `_async_finish_shutdown()` 等待 waittime/2 后 SIGTERM，再等待 waittime/2 后 SIGKILL
- F-093: jupyter_client/manager.py:586-601 — `_async_cleanup_resources()` 清理连接文件、IPC 文件、control socket、context、provisioner 资源
- F-094: jupyter_client/manager.py:603-643 — `_async_shutdown_kernel()` 完整关闭流程：stop_restarter → interrupt_kernel → request_shutdown 或 kill → finish_shutdown → cleanup_resources
- F-095: jupyter_client/manager.py:645-686 — `_async_restart_kernel()` 关闭当前内核（可选 newports），用保存的 _launch_args 重新启动
- F-096: jupyter_client/manager.py:297-299 — `autorestart` 默认 True，内核死亡后自动重启
- F-097: jupyter_client/manager.py:728-759 — `_async_interrupt_kernel()` 支持两种中断模式：signal（发送 SIGINT）和 message（通过 control 通道发送 interrupt_request）
- F-098: jupyter_client/manager.py:140 — `_owns_kernel` 通过构造参数 `owns_kernel` 控制，默认 True；不拥有内核时 shutdown_kernel 直接返回
- F-099: jupyter_client/manager.py:380-421 — `format_kernel_cmd()` 使用正则替换模板变量 {connection_file}、{prefix}、{resource_dir}，将 argv[0] 中的 python/python3 替换为 sys.executable
- F-100: jupyter_client/manager.py:609-613 — `_reconcile_connection_info()` 比较 provisioner 返回的连接信息与现有文件，不匹配时重写文件
- F-101: jupyter_client/manager.py:162-172 — `transport_encryption` 支持三档策略：disabled（默认）、auto、required，控制 CurveZMQ 加密
- F-102: jupyter_client/restarter.py:42-46 — `restart_limit` 默认 5，连续重启超过此次数后内核被判定死亡并触发 'dead' 回调
- F-103: jupyter_client/restarter.py:36-40 — `stable_start_time` 默认 10 秒，内核连续存活超过此时长才认为启动稳定
- F-104: jupyter_client/restarter.py:115-163 — `poll()` 方法检查 is_alive()，死亡时计数重启，稳定后重置 _restarting 和 _initial_startup

## 消息协议

- F-105: jupyter_client/connect.py:335-341 — `channel_socket_types` 映射：hb→zmq.REQ，shell→zmq.DEALER，iopub→zmq.SUB，stdin→zmq.DEALER，control→zmq.DEALER
- F-106: jupyter_client/connect.py:343 — `port_names` 列表为 ["shell_port", "stdin_port", "iopub_port", "hb_port", "control_port"]
- F-107: jupyter_client/session.py:173 — 消息分隔符常量 `DELIM = b"<IDS|MSG>"`
- F-108: jupyter_client/channels.py:26 — `major_protocol_version = protocol_version_info[0]`（值为 5）
- F-109: jupyter_client/session.py:308-314 — 消息头包含 msg_id、msg_type、username、session、date、version 字段
- F-110: jupyter_client/session.py:737-742 — 签名覆盖四部分：[p_header, p_parent, p_metadata, p_content]，buffers 不参与签名
- F-111: jupyter_client/session.py:466-471 — 默认签名方案为 "hmac-sha256"，必须以 "hmac-" 开头
- F-112: jupyter_client/session.py:498-506 — `digest_history` 集合记录已见签名防止重放攻击，默认大小 2^16（65536）
- F-113: jupyter_client/session.py:1013-1024 — `_cull_digest_history()` 超限时随机移除 10% 的历史记录
- F-114: jupyter_client/session.py:95-120 — 默认 JSON packer 使用 `json.dumps(ensure_ascii=False, allow_nan=False)`，失败时回退到 json_clean 并发出 DeprecationWarning
- F-115: jupyter_client/session.py:130-152 — orjson 可选支持：检测到 orjson 时使用 orjson_packer/orjson_unpacker，异常时回退到 json
- F-116: jupyter_client/session.py:155-162 — msgpack 可选支持：检测到 msgpack 时提供 msgpack_packer/msgpack_unpacker
- F-117: jupyter_client/session.py:165-170 — pickle_packer 使用 squash_dates 预处理，PICKLE_PROTOCOL = pickle.DEFAULT_PROTOCOL
- F-118: jupyter_client/session.py:31 — 使用 `hmac.compare_digest` 防止时序攻击
- F-119: jupyter_client/client.py:791-799 — `_handle_kernel_info_reply()` 根据回复的 protocol_version 设置 session.adapt_version 进行协议适配
- F-120: jupyter_client/client.py:79-83 — 五个通道功能：shell（请求/回复）、iopub（发布结果）、hb（心跳监控）、stdin（raw_input 回复）、control（内核管理）
- F-121: jupyter_client/connect.py:367 — 传输层支持 tcp 和 ipc 两种，默认 tcp
- F-122: jupyter_client/connect.py:716 — iopub 通道连接后设置 `zmq.SUBSCRIBE, b""` 订阅所有消息
- F-123: jupyter_client/connect.py:699 — socket linger 设置为 1000ms（1秒）防止退出挂起
- F-124: jupyter_client/channels.py:48 — HBChannel `time_to_dead` 默认 1.0 秒，发送 ping 后超时则判定心跳失败

## 会话管理

- F-125: jupyter_client/session.py:182-193 — `new_id()` 使用 os.urandom(16) 生成随机 ID，格式为 hex 编码分两段用 "-" 分隔
- F-126: jupyter_client/session.py:609-613 — `msg_id` 属性格式：`"{session}_{pid}_{message_number}"`，每次访问自增 message_count
- F-127: jupyter_client/session.py:457-460 — Session.key 默认值为 `new_id_bytes()`（随机字节）
- F-128: jupyter_client/session.py:380-387 — `check_pid` 默认 True，检测 fork 后发送消息发出警告
- F-129: jupyter_client/session.py:440-444 — username 默认从环境变量 USER 获取，回退为 "username"
- F-130: jupyter_client/session.py:519-535 — 三个阈值：copy_threshold=2^16（零拷贝阈值）、buffer_threshold=1024（buffer 提取阈值）、item_threshold=64（容器内省阈值）
- F-131: jupyter_client/session.py:582 — Session 初始化时记录 `self.pid = os.getpid()`
- F-132: jupyter_client/session.py:584-587 — key 为空时发出警告 "Message signing is disabled. This is insecure and not recommended!"
- F-133: jupyter_client/session.py:426-435 — session ID 默认通过 new_id() 生成，bsession 为其 ASCII 字节版本

## Kernel Spec

- F-135: jupyter_client/kernelspec.py:22 — `NATIVE_KERNEL_NAME = "python3"`
- F-136: jupyter_client/kernelspec.py:36 — KernelSpec.interrupt_mode 是 CaselessStrEnum，值为 "message" 或 "signal"，默认 "signal"
- F-137: jupyter_client/kernelspec.py:40-48 — `KernelSpec.from_resource_dir()` 从 resource_dir/kernel.json 读取并创建 KernelSpec 实例
- F-138: jupyter_client/kernelspec.py:72 — 内核名称正则 `^[a-z0-9._\-]+$`（不区分大小写），仅允许字母数字和 -._ 分隔符
- F-139: jupyter_client/kernelspec.py:87-89 — `_is_kernel_dir()` 判断目录是否包含 kernel.json 文件
- F-140: jupyter_client/kernelspec.py:192-203 — 默认搜索路径为 `jupyter_path("kernels")`，另追加 IPython kernels 目录
- F-141: jupyter_client/kernelspec.py:136-142 — `ensure_native_kernel` 默认 True：当无 python3 spec 且 ipykernel 可用时自动添加
- F-142: jupyter_client/kernelspec.py:159-165 — `allowed_kernelspecs` 白名单集合（原 whitelist 已 deprecated）
- F-143: jupyter_client/kernelspec.py:114-122 — `NoSuchKernel` 异常继承自 KeyError，包含 name 属性
- F-144: jupyter_client/provisioning/factory.py:142-149 — provisioner 配置从 kernel_spec.metadata["kernel_provisioner"] 读取，无配置时使用 default_provisioner_name
- F-145: jupyter_client/provisioning/factory.py:35-45 — 默认 provisioner 名称可通过环境变量 `JUPYTER_DEFAULT_PROVISIONER_NAME` 设置，默认 "local-provisioner"
- F-146: jupyter_client/provisioning/factory.py:32 — entry point group 名为 `jupyter_client.kernel_provisioners`
- F-147: jupyter_client/kernelspec.py:257-262 — KernelSpecManager.get_kernel_spec() 将 kernel_name 转为小写查找

## 依赖关系

- F-148: jupyter_client/connect.py:23 — connect.py 依赖 jupyter_core.paths（jupyter_data_dir, jupyter_runtime_dir, secure_write）
- F-149: jupyter_client/connect.py:24 — connect.py 依赖 traitlets（Bool, Bytes, CaselessStrEnum, Instance, Integer, Type, Unicode, observe）
- F-150: jupyter_client/session.py:33 — session.py 依赖 tornado.ioloop.IOLoop
- F-151: jupyter_client/session.py:56 — session.py 依赖 .jsonutil（extract_dates, json_clean, json_default, squash_dates）
- F-152: jupyter_client/session.py:52 — session.py 依赖 zmq.eventloop.zmqstream.ZMQStream
- F-153: jupyter_client/channels.py:13 — channels.py 依赖 jupyter_core.utils.ensure_async
- F-154: jupyter_client/manager.py:20 — manager.py 依赖 jupyter_core.utils.run_sync 将 async 方法暴露为同步方法
- F-155: jupyter_client/client.py:15 — client.py 依赖 jupyter_core.utils.ensure_async
- F-156: jupyter_client/provisioning/local_provisioner.py:14 — LocalProvisioner 依赖 .connect.LocalPortCache 进行端口缓存
- F-157: jupyter_client/multikernelmanager.py:62 — MultiKernelManager 默认 kernel_manager_class 为 "jupyter_client.ioloop.IOLoopKernelManager"
- F-158: jupyter_client/manager.py:157-158 — KernelManager 默认 client_class 为 "jupyter_client.blocking.BlockingKernelClient"
- F-159: jupyter_client/manager.py:805-807 — AsyncKernelManager 默认 client_class 为 "jupyter_client.asynchronous.AsyncKernelClient"
- F-161: jupyter_client/multikernelmanager.py:114 — MultiKernelManager.external_connection_dir 支持从外部目录扫描连接文件加载非自有内核（owns_kernel=False）
- F-162: jupyter_client/provisioning/provisioner_base.py:245-248 — `_finalize_env()` 对 Python 内核移除 PYTHONEXECUTABLE 环境变量防止路径混乱
- F-163: jupyter_client/provisioning/local_provisioner.py:82-86 — Windows 平台 SIGINT 中断通过 win_interrupt.send_interrupt 使用 Win32 事件实现
- F-164: jupyter_client/manager.py:824-837 — AsyncKernelManager 将所有 _async_* 方法直接赋值为公开 async 方法（start_kernel、shutdown_kernel 等），不经 run_sync 包装
- F-165: jupyter_client/client.py:429-443 — `_async_is_alive()` 在 parent 是 KernelManager 时委托给 manager，否则通过 hb_channel.is_beating() 判断存活，无心跳时返回 True
- F-166: jupyter_client/channels.py:106-124 — HBChannel._create_socket() 创建新的 zmq.REQ socket 并注册到 poller，心跳失败时调用此方法重建 socket 以打破 REQ/REP 状态机死锁
- F-167: jupyter_client/ioloop/manager.py:16-33 — `as_zmqstream()` 装饰器在 connect_* 方法中临时将 context._socket_class 替换为 ZMQStream，创建后立即恢复，使通道返回 Tornado ZMQStream 对象
- F-168: jupyter_client/asynchronous/client.py:47-52 — AsyncKernelClient 将 KernelClient 的 `_async_get_shell_msg`/`_async_get_iopub_msg`/`_async_get_stdin_msg`/`_async_get_control_msg`/`_async_wait_for_ready` 直接赋值为公开方法
- F-169: jupyter_client/asynchronous/client.py:64-76 — AsyncKernelClient 使用 reqrep(wrapped, ...) 将 execute/history/complete/inspect/kernel_info/comm_info/shutdown 包装为支持 reply 参数的 async 方法
