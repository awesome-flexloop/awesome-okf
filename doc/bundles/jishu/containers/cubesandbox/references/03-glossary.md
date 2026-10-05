---
type: Reference
title: CubeSandbox 术语表
description: 阅读 CubeSandbox 知识包所需的核心术语——虚拟化、容器生态、eBPF 网络、存储、网关五类
tags: [CubeSandbox, 术语表, glossary]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-10-04" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04" }
status: stable
stale_after: 2027-10-04
sources:
  - id: S1
    resource: /references/01-source-map.md
    title: CubeSandbox v0.7.2 源码信源地图
---

# CubeSandbox 术语表

## 一、虚拟化与硬件

| 术语 | 解释 |
|---|---|
| **KVM**（Kernel-based Virtual Machine） | Linux 内核模块，将 Linux 变为 type-1 hypervisor；通过 `/dev/kvm` 提供 VM/vCPU 创建接口。CubeSandbox 硬性要求宿主支持 KVM。 |
| **RustVMM** | Rust 编写的 VMM 组件生态（vm-memory、kvm-ioctls、vhost 等一组 crate）。CubeSandbox 的 VMM 与 cloud-hypervisor 均构建其上。 |
| **VMM**（Virtual Machine Monitor） | 虚拟机监控器：负责 vCPU 调度、设备模拟、guest 内存管理。CubeSandbox 中为 cube-hypervisor（cloud-hypervisor fork，crate v28.0.0）。 |
| **MicroVM** | 微型虚拟机：极简设备模型、极小内存开销、毫秒级启动的轻量 VM，代表为 Firecracker、cloud-hypervisor。 |
| **cloud-hypervisor** | Intel/开源社区的 RustVMM 项目，CubeSandbox 的 hypervisor 组件为其 fork（鸣谢清单 F-013）。 |
| **vCPU** | 虚拟 CPU，guest 视角的处理器；由宿主内核线程承载（Cubelet cgroup 插件含 vCPU 内存估算系数）。 |
| **PMEM / dax** | 持久内存设备及其直接访问（Direct Access）挂载模式。guest 内 cube-init 以 `dax` 选项只读挂载 `/dev/pmem1`。 |
| **virtio** | 半虚拟化设备标准（virtio-net/blk/fs/vsock），guest 与宿主共享队列（virtqueue），减少模拟开销。 |
| **vsock** | guest↔宿主的套接字地址族（CID:PORT）。CID 约定：-1 随机、0 hypervisor、1 loopback、2 宿主。cube-agent ttrpc 在 vsock :1024。 |
| **PVM** | CubeSandbox 的定制宿主内核形态（`CUBE_PVM_ENABLE=1`；kernel_pvm 资产），经 pvm_setup.sh 构建接入 GRUB。 |
| **ARM64/aarch64** | 64 位 ARM 架构；CubeSandbox 全栈支持 amd64/arm64，就绪通知在 aarch64 走 MMIO。 |

## 二、容器生态

| 术语 | 解释 |
|---|---|
| **containerd** | 工业级容器运行时管理器，kubelet 的默认 CRI 后端；Cubelet 依赖 containerd/v2 v2.2.2 的任务模型。 |
| **Shim（v2）** | containerd 与真实运行时之间的适配进程契约（Create/Start/Exec/Kill 等 ttrpc API），每个容器任务一个 shim。实现新运行时只需写 shim，无需改 containerd。 |
| **runtime_type** | containerd 选择 shim 的标识，如 `io.containerd.cube.v2`/`io.containerd.cube.rs`（CubeSandbox）、`io.containerd.runc.v2`。 |
| **containerd-shim-rs** | Rust 的 shim v2 框架（containerd-shim crate 0.9.0），CubeShim 与 Kata 均基于它。 |
| **OCI**（Open Container Initiative） | 容器镜像与运行时规范；cube-agent 以 OCI 选项（standard-oci-runtime feature）在 guest 内运行容器。 |
| **runc** | 标准 OCI 容器运行时；Cubelet images 配置中作为并存 runtime。 |
| **ttrpc** | 容器生态的精简 RPC 协议（基于 protobuf，非 HTTP）。cube-agent 提供 ttrpc AgentService；shim↔containerd 也走 ttrpc。 |
| **rustjail** | cube-agent 内的 Rust OCI 容器 jail（源自 kata agent），在 guest 内创建 namespace/cgroup 并执行用户进程。 |
| **namespace（ns）** | Linux 资源隔离机制（mnt/pid/uts/ipc/net…）；cube-agent 支持共享 UTS/IPC/PID ns（`/var/run/sandbox-ns`）。 |
| **cgroup** | Linux 资源控制组（v1/v2）；cube-init 自动挂载，cube-agent 据此限制容器资源。 |
| **envd** | E2B 沙箱内的守护进程（默认 :49983，/health 返回 204），SDK 的进程/文件操作经其完成；CubeMaster 将 envd 二进制嵌入发布。 |
| **E2B** | 开源沙箱平台及其 SDK 协议；CubeSandbox 的 CubeAPI 对外兼容 E2B SDK（E2B_API_URL 指向 :3000）。 |

## 三、eBPF 网络

| 术语 | 解释 |
|---|---|
| **eBPF** | 内核可编程虚拟机，可在安全检查点运行经校验的程序。CubeNet 用 Go（cilium/ebpf）加载 C 编写的程序。 |
| **TC**（Traffic Control） | Linux 流量控制子系统；eBPF 可挂为 TC 分类器（clsact qdisc 的 ingress/egress hook）。 |
| **clsact** | 提供 ingress/egress 两个伪 hook 的 qdisc；CubeSandbox 在 TAP/网桥上挂 clsact + bpf 程序。 |
| **from_cube / from_world / from_envoy** | 三个 TC 程序：沙箱 TAP 出向、宿主/节点网卡入向、cube-dev 网桥 egress。 |
| **BPF map** | 内核键值存储，用户态与程序共享数据。关键 map：mvmip_to_ifindex、port_mapping、allow_out/deny_out、sessions。 |
| **LPM_TRIE** | 最长前缀匹配 trie map，用于 CIDR 策略（allow_out_v3 内层）。 |
| **HASH_OF_MIPS** | map-in-map：外层沙箱 IP → 内层策略 map，实现每沙箱独立策略集。 |
| **tail call** | 程序间无返回跳转（PROG_ARRAY）；DNS 解析拆为 5 个 tail-call 阶段。 |
| **SNAT/DNAT** | 源/目标网络地址转换。出向 SNAT 池 ≤4 IP、源端口 30000 起；到网关/端口映射走 DNAT。 |
| **conntrack/会话表** | 连接/会话跟踪。CubeSandbox 在 BPF map 自管 ingress/egress 会话（ESTABLISHED 3h，reaper 5s）。 |
| **TAP** | 二层虚拟网卡；沙箱 TAP 预创建成池（tap_init_num 500）。 |
| **L7 mark** | eBPF 对 HTTP/HTTPS 流量打的 skb mark（0xCE010000/0xCE020000），供后续路径识别七层协议。 |

## 四、存储

| 术语 | 解释 |
|---|---|
| **CoW**（Copy-on-Write） | 写时复制：快照/克隆共享数据块，修改时才复制。CubeCoW 是其卷引擎实现。 |
| **reflink** | 文件级 CoW 克隆原语：`ioctl(FICLONE)` 只复制文件元数据、共享数据块（XFS/btrfs 支持）。CubeCoW 默认后端。 |
| **FICLONE** | reflink ioctl 号 `0x40049409`。 |
| **卷/快照（Volume/Snapshot）** | CubeCoW 核心对象；trait Engine 定义 create/list/activate 等操作。 |
| **lvstore / lvol** | SPDK 逻辑卷存储与逻辑卷；CubeS3lvol 经 rcow_create_lvstore/lvol RPC 创建。 |
| **SPDK** | Intel 存储性能开发套件（用户态、轮询式 NVMe 驱动）。s3lvol_tgt 基于 SPDK/DPDK。 |
| **DPDK** | 数据面开发套件（用户态网卡/轮询），SPDK 的网络/内存基础。 |
| **NVMe/TCP（NVMe-oF）** | 经 TCP 传输的 NVMe  fabrics；s3lvol_tgt 对外提供 NVMe/TCP 卷。 |
| **s3fs** | 把 S3 桶挂为本地文件系统的 FUSE 进程；S3 卷以引用计数挂载/卸载。 |
| **UDS**（Unix Domain Socket） | `/var/run/s3lvol.sock`，CubeCoW S3 引擎与 s3lvol target 的 JSON-RPC 通道。 |

## 五、网关与运维

| 术语 | 解释 |
|---|---|
| **OpenResty** | nginx + LuaJIT 可编程 Web 平台；CubeEgress/CubeProxy 基于它。 |
| **透明代理（tproxy）** | 不改变报文三元组的代理模式；CubeEgress 以 transparent 监听拦截沙箱出向。 |
| **L7 策略** | 七层出向规则：按 SNI/Host/Method/Path/Scheme/Port 匹配，动作为 allow/audit/inject。 |
| **SNI**（Server Name Indication） | TLS ClientHello 中的目标域名，用于 HTTPS 放行判定（无需解密）。 |
| **CubeProxy** | 沙箱入口网关（域名 cube.app）：域名路由、HTTP↔gRPC 桥接、暂停沙箱自动唤醒。 |
| **mkcert** | 本地 CA 工具；CubeProxy 用其签发本地可信证书（rootCA.pem）。 |
| **CoreDNS** | 域名服务器；一键部署中提供 cube.app 域名解析。 |
| **Redis Stream** | Redis 日志型消息流；CLM 用其汇聚生命周期事件（cube:v1:shared: 前缀）。 |
| **选主（Leader Lease）** | 多实例中保证单活跃控制器；CLM 用 Redis lease 实现，避免重复暂停/恢复。 |
| **reconciler** | 声明式控制循环：对照期望状态纠正实际状态；CLM 的暂停/恢复/清扫即 reconciler。 |
