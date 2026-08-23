---
type: Reference
title: cppzmq 源码事实采集（R 阶段）
description: 基于 cppzmq 4.11.0 的 zmq.hpp / zmq_addon.hpp 逐行采集的编号事实，零推测
sources:
  - id: zmq-hpp
    resource: /external/libs/remote/cppzmq/zmq.hpp
    title: zmq.hpp（cppzmq 核心头文件，4.11.0）
  - id: zmq-addon
    resource: /external/libs/remote/cppzmq/zmq_addon.hpp
    title: zmq_addon.hpp（cppzmq 扩展头文件）
tags: [cppzmq, zeromq, facts, RAII]
status: stable
---

# cppzmq 源码事实采集（R 阶段）

> 研究对象：cppzmq **4.11.0**（`CPPZMQ_VERSION_MAJOR/MINOR/PATCH = 4/11/0`），header-only ZeroMQ C++ 绑定。
> 方法：完整通读 `zmq.hpp`（3010 行）与 `zmq_addon.hpp`（859 行），辅以 `demo/`、`tests/` 用法验证。
> 原则：**零推测**——每条事实均标注源码行号，仅陈述代码实际所是。

## 一、版本、宏与全局设施

### F-001：版本宏定义为 4.11.0，通过 ZMQ_MAKE_VERSION 合成
**信源**：`zmq.hpp` L160-L167

```cpp
#define CPPZMQ_VERSION_MAJOR 4
#define CPPZMQ_VERSION_MINOR 11
#define CPPZMQ_VERSION_PATCH 0
#define CPPZMQ_VERSION \
    ZMQ_MAKE_VERSION(CPPZMQ_VERSION_MAJOR, CPPZMQ_VERSION_MINOR, CPPZMQ_VERSION_PATCH)
```

### F-002：通过 CPPZMQ_LANG 检测 C++ 标准并派生 ZMQ_CPP11/14/17 兼容宏
**信源**：`zmq.hpp` L47-L116

`CPPZMQ_LANG` 综合 `_MSVC_LANG`/`__cplusplus` 与 MSVC `_HAS_CXX14/17` 判定；据此定义 `ZMQ_CPP11/14/17`，并派生 `ZMQ_DEPRECATED`、`ZMQ_NODISCARD`、`ZMQ_NOTHROW`、`ZMQ_EXPLICIT`、`ZMQ_OVERRIDE`、`ZMQ_NULLPTR`、`ZMQ_CONSTEXPR_FN/VAR`、`ZMQ_INLINE_VAR`、`ZMQ_CONSTEXPR_IF` 等跨标准垫片。在 C++11 之前这些宏退化为空/`throw()`/`0`。

### F-003：zmq.hpp 是 header-only，首行包含 <zmq.h>，用 __ZMQ_HPP_INCLUDED__ 作包含守卫
**信源**：`zmq.hpp` L26-L45

Windows 下预定义 `NOMINMAX` 并临时保存/恢复 `min`/`max` 宏，避免与 `std::min/max` 冲突。

### F-004：error_t 继承自 std::exception（非 std::system_error），持有 zmq_errno
**信源**：`zmq.hpp` L302-L315

```cpp
class error_t : public std::exception
{
  public:
    error_t() ZMQ_NOTHROW : errnum(zmq_errno()) {}
    explicit error_t(int err) ZMQ_NOTHROW : errnum(err) {}
    virtual const char *what() const ZMQ_NOTHROW ZMQ_OVERRIDE
    { return zmq_strerror(errnum); }
    int num() const ZMQ_NOTHROW { return errnum; }
  private:
    int errnum;
};
```

> 校正：任务描述称其继承 `std::system_error`，**实际继承 `std::exception`**；`num()` 返回底层 `zmq_errno` 错误码。

### F-005：detail::ranges 提供 ADL 形式的 begin/end，detail::is_range 以 SFINAE 检测范围
**信源**：`zmq.hpp` L242-L285

`is_range<T>` 通过 `ranges::begin(t) == ranges::end(t)` 表达式是否合法来判定；同时提供 `iter_value_t`、`range_iter_t`、`range_value_t` 别名。

### F-006：free_fn/pollitem_t 为 C 类型别名，fd_t 按平台位宽定义
**信源**：`zmq.hpp` L288-L300

`typedef zmq_free_fn free_fn;`、`typedef zmq_pollitem_t pollitem_t;`；Win64 下 `fd_t = unsigned __int64`，Win32 下 `unsigned int`，其他平台 `int`。

### F-007：poll() 自由函数是 zmq_poll 的薄封装，提供多组重载
**信源**：`zmq.hpp` L317-L395

`detail::poll` 在 `zmq_poll` 返回 `<0` 时抛 `error_t()`。对外重载接受 `(pollitem_t*, size_t, long)`、`(vector<zmq_pollitem_t>&, chrono::milliseconds)`、`(array<...>&, chrono::milliseconds)` 等；多个旧重载（const items、long 超时）标记 `ZMQ_DEPRECATED`。

### F-008：version() 同时提供 C 风格出参和 C++11 tuple 两种形式
**信源**：`zmq.hpp` L398-L409

`void version(int*,int*,int*)` 直接调 `zmq_version`；`std::tuple<int,int,int> version()`（C++11）把三段版本写入 tuple 返回。

## 二、message_t：ZeroMQ 消息封装

### F-009：message_t 默认构造调用 zmq_msg_init 且不抛异常
**信源**：`zmq.hpp` L429-L433

```cpp
message_t() ZMQ_NOTHROW {
    int rc = zmq_msg_init(&msg);
    ZMQ_ASSERT(rc == 0);
}
```

### F-010：message_t(size_t) 调用 zmq_msg_init_size，失败抛 error_t
**信源**：`zmq.hpp` L435-L440

### F-011：迭代器区间构造模板按 distance*sizeof(value_t) 分配并 std::copy
**信源**：`zmq.hpp` L442-L453

### F-012：(const void*, size_t) 构造在 size_==0 时跳过 memcpy，允许 (nullptr,0)
**信源**：`zmq.hpp` L455-L465

注释明确：`memcpy` 空指针是 UB，故 `size_` 为 0 时不复制。

### F-013：(void*, size_t, free_fn*, hint*) 构造包装 zmq_msg_init_data，支持零拷贝释放回调
**信源**：`zmq.hpp` L467-L472

### F-014：C++11 下提供 Range/字符串/string_view 构造，但显式删除部分歧义重载
**信源**：`zmq.hpp` L475-L511

- `template<class Range> explicit message_t(const Range&)` 要求 `is_range`、元素 `trivially copyable`，且排除 `message_t`/`std::string`/`std::string_view`；
- `explicit message_t(const std::string&)`、`explicit message_t(std::string_view)`；
- 字符数组字面量构造（含终止符）已 `ZMQ_DEPRECATED`（from 4.7.0）。

### F-015：message_t 支持移动构造/移动赋值，但移动构造会把源重置为空消息
**信源**：`zmq.hpp` L513-L525

移动构造复制 `rhs.msg` 后立即 `zmq_msg_init(&rhs.msg)`；移动赋值用 `std::swap(msg, rhs.msg)`。

### F-016：析构函数调用 zmq_msg_close，拷贝构造与拷贝赋值被删除
**信源**：`zmq.hpp` L527-L531、L757-L765

```cpp
~message_t() ZMQ_NOTHROW {
    int rc = zmq_msg_close(&msg);
    ZMQ_ASSERT(rc == 0);
}
// 私有：
message_t(const message_t &) ZMQ_DELETED_FUNCTION;
void operator=(const message_t &) ZMQ_DELETED_FUNCTION;
```

注释说明：禁用隐式拷贝是为了避免用户在不知情时使用共享消息（效率较低）。

### F-017：rebuild() 提供多重重置重载，先 close 再重新 init
**信源**：`zmq.hpp` L533-L573

重载包括空、`size_t`、`(const void*,size_t)`、`(const std::string&)`、`(void*,size_t,free_fn*,hint*)`；`close` 失败抛 `error_t`。

### F-018：move()/copy() 包装 zmq_msg_move/zmq_msg_copy，旧指针形参版本已废弃
**信源**：`zmq.hpp` L575-L603

### F-019：more() 包装 zmq_msg_more，data()/size()/empty() 包装 zmq_msg_data/zmq_msg_size
**信源**：`zmq.hpp` L605-L630

`data()` 有非 const/const 两个返回 `void*`/`const void*` 的版本，以及模板 `data<T>()` 做类型强转；`empty()` 为 `size()==0`。

### F-020：operator== 先比 size 再 memcmp，equal() 已废弃
**信源**：`zmq.hpp` L632-L644

### F-021：get(int) 包装 zmq_msg_get（3.2+），gets(const char*) 包装 zmq_msg_gets（4.1+）
**信源**：`zmq.hpp` L646-L664

返回 `-1`/`nullptr` 时抛 `error_t`。

### F-022：Draft API 提供 routing_id/group 的 get/set（4.2+）
**信源**：`zmq.hpp` L666-L690

`routing_id()`/`set_routing_id(uint32_t)`、`group()`/`set_group(const char*)`，由 `ZMQ_BUILD_DRAFT_API` 守护。

### F-023：to_string()/to_string_view()/str() 提供文本与调试输出
**信源**：`zmq.hpp` L692-L746

`str(size_t max_size=1000)` 把可打印 ASCII 原样输出、其余以两位大写十六进制输出，超限追加 `... too big to print`。

### F-024：swap() 与自由 swap() 交换底层 zmq_msg_t；handle() 返回 zmq_msg_t*
**信源**：`zmq.hpp` L748-L770

`handle()` 带 `ZMQ_NODISCARD`，注释假设 `zmq::msg_t`（libzmq）可平凡重定位（trivially relocatable）。

## 三、context_t：上下文 RAII

### F-025：enum class ctxopt 强类型映射 ZMQ 上下文选项
**信源**：`zmq.hpp` L773-L814

包括 `blocky/io_threads/thread_sched_policy/thread_priority/thread_affinity_cpu_add/remove/thread_name_prefix/max_msgsz/zero_copy_recv/max_sockets/socket_limit/ipv6/msg_t_size`，全部用 `#ifdef` 按 libzmq 版本条件编译。

### F-026：context_t 默认构造调 zmq_ctx_new，(io_threads, max_sockets) 构造额外 set 两个选项
**信源**：`zmq.hpp` L820-L839

```cpp
explicit context_t(int io_threads_, int max_sockets_ = ZMQ_MAX_SOCKETS_DFLT) {
    ptr = zmq_ctx_new();
    if (ptr == ZMQ_NULLPTR) throw error_t();
    int rc = zmq_ctx_set(ptr, ZMQ_IO_THREADS, io_threads_);
    ZMQ_ASSERT(rc == 0);
    rc = zmq_ctx_set(ptr, ZMQ_MAX_SOCKETS, max_sockets_);
    ZMQ_ASSERT(rc == 0);
}
```

### F-027：context_t 支持移动构造/移动赋值，移动赋值先 close() 再 swap
**信源**：`zmq.hpp` L841-L849、L924-L929

拷贝构造与拷贝赋值被删除。

### F-028：析构调用 close()；close() 循环 zmq_ctx_term 直到非 EINTR；shutdown() 调 zmq_ctx_shutdown
**信源**：`zmq.hpp` L851、L885-L908

```cpp
void close() ZMQ_NOTHROW {
    if (ptr == ZMQ_NULLPTR) return;
    int rc;
    do { rc = zmq_ctx_term(ptr); } while (rc == -1 && errno == EINTR);
    ZMQ_ASSERT(rc == 0);
    ptr = ZMQ_NULLPTR;
}
```

`shutdown()` 使所有阻塞 socket 操作以 `ETERM` 返回，为 `close()` 做准备。

### F-029：set(ctxopt,int)/get(ctxopt) 为类型安全包装；handle() 返回 void*；提供 operator bool/void*
**信源**：`zmq.hpp` L853-L922

旧 `setctxopt(int,int)`/`getctxopt(int)` 已废弃；`get` 在 `rc==-1` 时抛 `error_t`（注释承认部分选项默认值即 -1，可能产生无意义错误）。

## 四、结果类型、标志枚举与 buffer 抽象

### F-030：recv_buffer_size 记录写入字节数与未截断原始大小；send/recv 结果用 optional 表达
**信源**：`zmq.hpp` L938-L1018

- `struct recv_buffer_size { size_t size; size_t untruncated_size; bool truncated() const noexcept; }`；
- `send_result_t = optional<size_t>`、`recv_result_t = optional<size_t>`、`recv_buffer_result_t = optional<recv_buffer_size>`；
- 无 `<optional>` 时用 `detail::trivial_optional<T>`（要求 `T` trivial）兜底。

### F-031：send_flags/recv_flags 是 enum class 位掩码，none=0，dontwait=ZMQ_DONTWAIT
**信源**：`zmq.hpp` L1020-L1095

`send_flags` 额外有 `sndmore = ZMQ_SNDMORE`；通过 `detail::enum_bit_or/and/xor/not` 实现 `| & ^ ~`，注释称“部分满足 BitmaskType 命名要求”。

### F-032：mutable_buffer/const_buffer 仅持有 (指针, 长度)，支持指针前移与隐式可变→只读转换
**信源**：`zmq.hpp` L1102-L1177

二者均有 `constexpr` 默认/带参构造；`const_buffer(const mutable_buffer&)` 实现隐式只读转换；`operator+=`/自由 `operator+` 按 `min(n, size)` 前移指针、缩减长度。

### F-033：buffer() 自由函数重载覆盖裸指针、C 数组、std::array、std::vector、std::basic_string、string_view
**信源**：`zmq.hpp` L1181-L1367

`detail::is_pod_like<T>` 要求 `trivially copyable && standard layout`，并在 `buffer_contiguous_sequence` 中 `static_assert`；非 const 容器产生 `mutable_buffer`，const 容器产生 `const_buffer`。

### F-034：str_buffer() 从字符数组构造不含终止符的 const_buffer；_zbuf 用户定义字面量同理
**信源**：`zmq.hpp` L1369-L1400

```cpp
template<class Char, size_t N>
constexpr const_buffer str_buffer(const Char (&data)[N]) noexcept {
    static_assert(detail::is_pod_like<Char>::value, "Char must be POD");
    return const_buffer(static_cast<const Char*>(data), (N - 1) * sizeof(Char));
}
```

`literals::operator""_zbuf` 支持 `char/wchar_t/char16_t/char32_t`。

## 五、socket_type、sockopt 与 socket 层

### F-035：enum class socket_type:int 强类型映射所有 ZMQ 套接字类型
**信源**：`zmq.hpp` L1403-L1432

稳定类型：`req/rep/dealer/router/pub/sub/xpub/xsub/push/pull/stream/pair`；Draft 类型：`server/client/radio/dish/gather/scatter/dgram`（4.2+）、`peer/channel`（4.3.3+）。

### F-036：sockopt 命名空间用 integral_option/array_option 标签类型编码选项名与值类型
**信源**：`zmq.hpp` L1435-L1759

```cpp
template<int Opt, class T, bool BoolUnit = false> struct integral_option {};
template<int Opt, int NullTerm = 1> struct array_option {}; // 0:binary 1:string 2:bin-or-Z85
```

通过宏 `ZMQ_DEFINE_INTEGRAL_OPT`、`ZMQ_DEFINE_INTEGRAL_BOOL_UNIT_OPT`、`ZMQ_DEFINE_ARRAY_OPT`、`ZMQ_DEFINE_ARRAY_OPT_BINARY`、`ZMQ_DEFINE_ARRAY_OPT_BIN_OR_Z85` 声明约 80 个选项标签，例如 `events` 为 `integral_option<ZMQ_EVENTS,int>`、`fd` 为 `integral_option<ZMQ_FD,::zmq::fd_t>`、`linger` 为 `int`、`routing_id` 为 binary array、curve 密钥为 bin-or-Z85。

### F-037：detail::socket_base 用模板 set/get 实现类型安全选项访问
**信源**：`zmq.hpp` L1765-L1912

- `set(integral_option<Opt,T,BoolUnit>, const T&)` 对 `T` 做 `is_integral` 静态断言；`BoolUnit=true` 时额外提供接受 `bool` 的重载（内部转为 `T`）；
- `set(array_option, const char*|const_buffer|const string&|string_view)`；
- `get(integral_option)` 返回 `T`（`is_scalar` 断言）；`get(array_option, mutable_buffer)` 返回字节数；`get(array_option, init_size=1024)` 返回 `std::string`，按 `NullTerm` 去除终止符（`NullTerm==2` 默认 41 字节 Z85）；
- 旧 `setsockopt(int,...)`/`getsockopt(int,...)` 全部标记废弃。

### F-038：socket_base::bind/unbind/connect/disconnect 同时接受 std::string 和 const char*
**信源**：`zmq.hpp` L1914-L1948

失败即抛 `error_t`。

### F-039：socket_base::send 现代重载返回 send_result_t，以 nullopt 表示 EAGAIN
**信源**：`zmq.hpp` L1953-L2049

- `send(const_buffer, send_flags=none)` 调 `zmq_send`；
- `send(message_t&, send_flags)` 调 `zmq_msg_send`；
- `send(message_t&&, send_flags)` 转发到左值引用版本；
- `send_static(const_buffer)` 调 `zmq_send_const`（零拷贝常量缓冲），另有 `string_view` 重载；
- 旧的裸指针/迭代器/`int flags` 重载均已废弃。

### F-040：socket_base::recv 现代重载返回 optional，buffer 版本附带截断信息
**信源**：`zmq.hpp` L2051-L2105

- `recv(mutable_buffer, recv_flags)` 返回 `recv_buffer_result_t`，其中 `size=min(nbytes, buf.size())`、`untruncated_size=nbytes`；
- `recv(message_t&, recv_flags)` 返回 `recv_result_t` 并 `assert(msg.size()==nbytes)`；
- 旧 `recv(void*,size_t,int)`/`recv(message_t*,int)` 已废弃。

### F-041：Draft join/leave、handle()、explicit operator bool 由 socket_base 提供
**信源**：`zmq.hpp` L2107-L2129

### F-042：socket_ref 是非拥有的可空套接字引用，可与 nullptr 比较并可作 std::hash 键
**信源**：`zmq.hpp` L2151-L2240

通过 `from_handle_t`（含私有 `_private` 标记类型）限制只能用 `zmq::from_handle` 构造；`zmq` 命名空间内定义 `socket_ref` 的 `==/!=`（与 `nullptr_t`），以及对 `detail::socket_base` 的 `==/!=/</>/<=/>=`（基于句柄指针）；`std::hash<zmq::socket_ref>` 被特化为哈希 `handle()`。

### F-043：socket_t 是拥有句柄的 RAII 类，额外保存 ctxptr，友元 monitor_t
**信源**：`zmq.hpp` L2244-L2322

- 构造：`socket_t(context_t&, int type)` / `socket_t(context_t&, socket_type)` / 默认空构造；
- 移动构造/赋值（赋值先 `close()` 再 swap）；
- 析构调 `close()`；`close()` 调 `zmq_close` 并清空 `_handle/ctxptr`；
- 拷贝删除；
- 私有构造 `socket_t(void* context_, int type_)` 仅供 `monitor_t` 创建 PAIR 监控套接字；
- `operator socket_ref()` 隐式转换为非拥有引用。

### F-044：proxy/proxy_steerable 自由函数接受 socket_ref，包装 zmq_proxy*
**信源**：`zmq.hpp` L2329-L2365

旧 `void*` 版本已废弃；`proxy_steerable` 仅在 `ZMQ_HAS_PROXY_STEERABLE`（4.1+）可用。

## 六、monitor_t 与 poller_t

### F-045：monitor_t 通过内部 PAIR socket 接收事件，以虚函数 on_event_* 分发
**信源**：`zmq.hpp` L2367-L2674

- `init()` 调 `zmq_socket_monitor`，再用私有 `socket_t(void* ctx, ZMQ_PAIR)` 连接到监控地址，回调 `on_monitor_started()`；
- `monitor()` 在 `init` 后 `while(true) check_event(-1)`；
- `check_event(timeout)` 用 `zmq::poll` 等待 `ZMQ_POLLIN`，再调 `process_event`；
- `process_event` 接收两帧（`zmq_event_t` + 地址字符串），按 `event->event` switch 到 `on_event_connected/connect_delayed/.../handshake_*/unknown`；
- `abort()` 传 `nullptr` 停止监控；虚析构调 `close()`；拷贝删除。

### F-046：event_flags 是 poller 事件位掩码枚举，poller_event<T> 与 zmq_poller_event_t 布局兼容
**信源**：`zmq.hpp` L2676-L2714

```cpp
enum class event_flags : short {
    none=0, pollin=ZMQ_POLLIN, pollout=ZMQ_POLLOUT,
    pollerr=ZMQ_POLLERR, pollpri=ZMQ_POLLPRI
};
template<class T = no_user_data> struct poller_event {
    socket_ref socket;
    ::zmq::fd_t fd;
    T *user_data;
    event_flags events;
};
```

`tests/poller.cpp` L12-L18 用 `static_assert` 验证 `sizeof`/`alignof` 与 C 结构体一致。

### F-047：poller_t<T> 用 unique_ptr<void,destroy_poller_t> 管理 zmq_poller 生命周期
**信源**：`zmq.hpp` L2716-L2863

- `add(socket_ref/fd_t, event_flags[, T* user_data])`：带 `user_data` 的重载用 `enable_if<!is_same<T,no_user_data>>` SFINAE 守卫；
- `remove`/`modify` 分别包装 `zmq_poller_remove[_fd]`/`zmq_poller_modify[_fd]`；
- `wait(chrono::milliseconds)` 返回 `optional<event_type>`，EAGAIN 返回空；
- `wait_all(Sequence&, timeout)` 要求 `Sequence::value_type == event_type`，返回就绪数；
- `size()`（4.3.3+）包装 `zmq_poller_size`；
- 因成员 `unique_ptr` 不可拷贝、可移动（测试 L20-L23 静态断言不可拷贝构造/赋值）。

## 七、timers、curve、z85

### F-048：timers 类包装 zmq_timers_*，提供 add/cancel/set_interval/reset/timeout/execute
**信源**：`zmq.hpp` L2871-L2948

由 `ZMQ_HAVE_TIMERS` 守护；`id_t = int`、`fn_t = zmq_timer_fn`；`timeout()` 返回 `optional<chrono::milliseconds>`；拷贝删除。

### F-049：curve_keypair() 返回 Z85 公私钥对；curve_public() 由私钥推导公钥
**信源**：`zmq.hpp` L2950-L2971

缓冲区为 41 字节；私钥尺寸非 40 抛 `std::runtime_error`。

### F-050：z85_encode/z85_decode 自由函数实现 Z85 编解码
**信源**：`zmq.hpp` L2975-L2995

`z85_encode` 按 `n*6/5+1` 分配缓冲并去除尾部 `'\0'`；`z85_decode` 按 `n*4/5` 输出；失败抛 `error_t`。

## 八、zmq_addon.hpp 扩展

### F-051：poller_ref_t 是 socket/fd 的带标签可哈希联合，用作 active_poller 的 map 键
**信源**：`zmq_addon.hpp` L41-L92

内部为 `tuple<int, socket_ref, fd_t>`，`enum RefType{RT_SOCKET,RT_FD}`；`hash_combine` 用 boost 风格魔数 `0x9e3779b9`；特化 `std::hash<poller_ref_t>`。

### F-052：recv_multipart/recv_multipart_n 用输出迭代器收集多部分消息
**信源**：`zmq_addon.hpp` L98-L201

`detail::recv_multipart_n<CheckN>` 循环 `s.recv(msg)`，每帧 `*out++ = std::move(msg)`，直到 `!msg.more()`；返回 `recv_result_t`（帧数或 nullopt）。`CheckN=true` 且帧数超过 `n` 时抛 `std::runtime_error`。

### F-053：send_multipart 接受 message_t/const_buffer/mutable_buffer 的 ForwardRange
**信源**：`zmq_addon.hpp` L215-L245

对除最后一帧外的所有部分自动加 `send_flags::sndmore`；返回发送帧数或 nullopt（EAGAIN）；模板约束 `is_range<Range>` 且元素为 `message_t` 或 buffer 类型。

### F-054：encode/decode 实现 CZMQ zmsg 兼容的单帧编码（RFC 50）
**信源**：`zmq_addon.hpp` L266-L357

小于 255 字节的部分用 1 字节长度，否则用 `0xFF` + 4 字节网络序 uint32；`encode` 对超过 uint32 上限的部分抛 `std::range_error`，`decode` 越界抛 `std::out_of_range`。

### F-055：multipart_t 以 std::deque<message_t> 持有多帧，禁用拷贝、使用移动语义
**信源**：`zmq_addon.hpp` L371-L731

- 构造：默认、`socket_ref`（立即 `recv`）、`(const void*,size_t)`、`(const string&)`、`(message_t&&)`、移动构造；
- 迭代器：`begin/end/cbegin/cend/rbegin/rend`，`operator[]/at`；
- 收发：`recv(socket_ref, flags=0)` 清空后循环收至 `!more()`；`send(socket_ref)` 逐帧 pop 并对非末帧加 `SNDMORE`，发送后 `clear()`；
- 部件操作：`push/add/pushmem/addmem/pushstr/addstr/pushtyp/addtyp`（前插/后插）、`pop/remove/popstr/poptyp`、`front/back/peek/peekstr/peektyp`；
- `clone()` 深拷贝所有帧；`str()` 调试输出；`operator==` 逐帧比较；
- C++11 下 `encode()`/`decode_append()`/静态 `decode()` 委托给自由函数。

### F-056：active_poller_t 在 poller_t 之上以 std::function 回调自动分发事件
**信源**：`zmq_addon.hpp` L740-L853

```cpp
using handler_type = std::function<void(event_flags)>;
void add(zmq::socket_ref socket, event_flags events, handler_type handler);
```

- `add` 拒绝空 handler（抛 `std::invalid_argument`），重复注册抛 `error_t(EINVAL)`；用 `shared_ptr<handler_type>` 作 `poller_t` 的 `user_data`，异常时回滚 `handlers` map；
- `wait(timeout)` 在 `need_rebuild` 时重建事件/handler 向量，调 `base_poller.wait_all`，再对每个就绪事件执行 `(*event.user_data)(event.events)`；
- 提供 `empty()/size()`；拷贝删除、移动默认。

## 事实统计

- 总计 **56** 条编号事实（F-001 ~ F-056）。
- 覆盖：版本/宏（4）、error_t（1）、message_t（16）、context_t（5）、结果类型/标志/buffer（5）、socket_type/sockopt/socket（12）、monitor_t（1）、poller_t（2）、timers/curve/z85（3）、zmq_addon（6）。
