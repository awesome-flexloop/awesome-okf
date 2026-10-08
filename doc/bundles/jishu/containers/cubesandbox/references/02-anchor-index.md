---
type: Reference
title: CubeSandbox 事实锚点索引（F-001 ~ F-244）
description: 244 条源码事实的编号-锚点逐条索引，按 14 主题面分组，供全束引用回源验证
tags: [CubeSandbox, anchor-index, F-001, 溯源]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-10-04" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04" }
status: stable
stale_after: 2027-10-04
sources:
  - id: S1
    resource: https://github.com/TencentCloud/CubeSandbox
    title: TencentCloud/CubeSandbox v0.7.2
  - id: S2
    resource: https://github.com/TencentCloud/CubeSandbox/tree/v0.7.2/hypervisor
    title: hypervisor / guest-init
  - id: S3
    resource: https://github.com/TencentCloud/CubeSandbox/tree/v0.7.2/agent
    title: agent / CubeShim / cubecow
  - id: S4
    resource: https://github.com/TencentCloud/CubeSandbox/tree/v0.7.2/Cubelet
    title: Cubelet / CubeMaster / CubeNet
  - id: S5
    resource: https://github.com/TencentCloud/CubeSandbox/tree/v0.7.2
    title: CubeAPI / CubeEgress / CubeProxy / CubeOps / CLM / sdk
---

# CubeSandbox 事实锚点索引（F-001 ~ F-244）

> 全部事实基于 release tag v0.7.2（commit `f1aaa737`）。锚点格式 `<相对路径>:<行号>`。内容为极简摘要，完整表述以源码与官方文档原文为准。

## ① 项目定位与核心指标（F-001 ~ F-009）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-001 | 基于 RustVMM + KVM、兼容 E2B SDK、60ms 创建、内存开销 <5MB、单机/集群 | README_zh.md:45 |
| F-002 | 单并发 60ms；50 并发均值 67/P95 90/P99 137ms | README_zh.md:241 |
| F-003 | 运行需支持 KVM 的 x86_64 Linux | README_zh.md:280 |
| F-004 | 冷启动 <60ms、额外内存 <5MB、腾讯云生产规模化验证 | docs/zh/guide/introduction.md:3 |
| F-005 | Docker 200ms vs CubeSandbox 亚 60ms | docs/zh/guide/introduction.md:38 |
| F-006 | 跨机暂停与恢复（Preview）+ S3 快照后端 | docs/zh/guide/introduction.md:19 |
| F-007 | 开源 80 天破万 Star、11 版本、近 70 贡献者、560+ commits | docs/zh/guide/cube100.md:9 |
| F-008 | 三方式对比：Docker 共享内核 200ms/高密度；传统 VM 独立内核秒级/低密度；Cube 独立内核+eBPF <60ms/数千实例 | README_zh.md:233-240 |
| F-009 | 启动基于裸金属实测；内存基于 ≤32GB 规格实测 | README_zh.md:241 |

## ② 架构总览（F-010 ~ F-013）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-010 | 冷启动 <100ms；控制面 CubeAPI/CubeMaster/WebUI/Redis；数据面 Cubelet/CubeShim/CubeHypervisor/CubeCoW/CubeVS/CubeEgress/CubeProxy | docs/zh/architecture/overview.md:11 |
| F-011 | 七组件架构表（CubeAPI/CubeMaster/CubeProxy/Cubelet/CubeVS/CubeEgress/Hypervisor&Shim） | README_zh.md:388-397 |
| F-012 | 三个 eBPF 程序：from_cube（TAP TC ingress）、from_world（主机网卡 TC ingress）、from_envoy（cube-dev TC egress） | docs/zh/architecture/overview.md:166 |
| F-013 | 鸣谢：Cloud Hypervisor、Kata Containers、virtiofsd、containerd-shim-rs、ttrpc-rust | README_zh.md:449 |

## ③ 部署形态与环境要求（F-014 ~ F-036）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-014 | 部署四步、无需本地构建 | docs/zh/guide/quickstart.md:3 |
| F-015 | 二进制基于 Ubuntu 20.04（glibc 2.31），系统 glibc ≥2.31 | docs/zh/guide/quickstart.md:31 |
| F-016 | OpenCloudOS 9/TencentOS 4 推荐；Ubuntu 20.04/22.04/24.04 已测 | docs/zh/guide/quickstart.md:35 |
| F-017 | `/data/cubelet` ≥50GB，多模板建议 ≥200GB | docs/zh/guide/quickstart.md:44 |
| F-018 | 功能体验 ≥4 核/8GB/50GB；推荐 32 核/64GB/≥200GB | docs/zh/guide/quickstart.md:57 |
| F-019 | 在线安装 `curl ... online-install.sh \| CUBE_PVM_ENABLE=1 MIRROR=cn bash` | docs/zh/guide/quickstart.md:176 |
| F-020 | 跳过预检：`ONE_CLICK_SKIP_PRECHECK=1` 或 `--skip-precheck` | docs/zh/guide/quickstart.md:181 |
| F-021 | E2B REST API :3000；CubeMaster/Cubelet/CubeShim 宿主进程；MySQL/Redis 走 Compose | docs/zh/guide/quickstart.md:193 |
| F-022 | CubeProxy 提供 mkcert TLS + CoreDNS 路由，域名 `cube.app` | docs/zh/guide/quickstart.md:196 |
| F-023 | 制模板命令 cubemastercli tpl create-from-image（--writable-layer-size/--expose-port/--probe） | docs/zh/guide/quickstart.md:205 |
| F-024 | 环境变量 E2B_API_URL/E2B_API_KEY=e2b_000000/SSL_CERT_FILE(rootCA.pem) | docs/zh/guide/quickstart.md:256 |
| F-025 | install.sh=控制节点、install-compute.sh=计算节点；路径 `/usr/local/services/cubetoolbox` | deploy/one-click/README.md:16 |
| F-026 | systemd 目标 cube-sandbox-control.target / cube-sandbox-compute.target | deploy/one-click/README.md:197 |
| F-027 | smoke.sh 18 行，执行 quickcheck.sh | deploy/one-click/smoke.sh:17 |
| F-028 | release-assets pin：kernel_bm_amd64/arm64/kernel_pvm=kernel-release-260921-1；guest_image=guest-image-260820-1 | deploy/release-assets.yaml:20 |
| F-029 | Helm chart name cube，version/appVersion 0.7.2 | deploy/kubernetes/chart/Chart.yaml:5 |
| F-030 | 默认构建镜像 cube-sandbox-builder:ubuntu2004 | Makefile:4 |
| F-031 | 六个 Rust 工作区；BINARIES 含 agent/cube-init/cube-volume-s3/cubeapi/cubelet/cubemaster/cubeops/cubevsmapdump/shim | Makefile:50 |
| F-032 | 整包 cube-sandbox-one-click-<ver>-<arch>.tar.gz；发布于 cnb.cool releases | docs/zh/guide/downloads.md:23 |
| F-033 | guest 内核 tag 示例如 kernel-release-260812-1；guest 镜像 guest-image-260820-1 | docs/zh/guide/downloads.md:54 |
| F-034 | pvm_setup.sh 三步：并行构建 host 内核+guest vmlinux；装 host 接 GRUB；放 guest 资产 | deploy/pvm/pvm_setup.sh:6 |
| F-035 | WebUI 地址 http://<控制节点 IP>:12088 | README_zh.md:358 |
| F-036 | configs 含 kernel-oc9 config 与 single-node 三 yaml | configs/single-node/cubemaster.yaml:1 |

## ④ CubeAPI（F-037 ~ F-059）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-037 | crate cube-api v0.1.0 edition 2021，bin cube-api | CubeAPI/Cargo.toml:5-12 |
| F-038 | 模块 config/constants/cubemaster/error/handlers/logging/middleware/models/openapi/routes/services/state | CubeAPI/src/main.rs:5-16 |
| F-039 | Cli：--bind 默认 0.0.0.0:3000、--cubemaster-url 默认 :8089、--rate-limit-per-sec 100、--instance-type cubebox、--sandbox-domain cube.app 等 | CubeAPI/src/main.rs:39-120 |
| F-040 | 超时常量：默认 30s、pause/resume 120s、snapshot 240s | CubeAPI/src/routes.rs:26-36 |
| F-041 | GET /health、GET/POST /sandboxes、GET /v2/sandboxes | CubeAPI/src/routes.rs:72-90 |
| F-042 | GET/DELETE /sandboxes/:id；GET /sandboxes/:id/logs（含 v2） | CubeAPI/src/routes.rs:91-100 |
| F-043 | PUT /sandboxes/:id/network、POST /timeout、/refreshes、GET /snapshots | CubeAPI/src/routes.rs:101-113 |
| F-044 | POST /sandboxes/:id/pause、/resume、/connect、/snapshots、/rollback | CubeAPI/src/routes.rs:122-148 |
| F-045 | 模板路由族：/templates、/compat、alias、builds 等 | CubeAPI/src/routes.rs:155-184 |
| F-046 | DELETE /templates/:id；卷路由 /volumes | CubeAPI/src/routes.rs:191-205 |
| F-047 | AppState：rate_limiter/http_client/services/logger/config | CubeAPI/src/state.rs:16-31 |
| F-048 | ServerConfig 字段及环境变量 CUBE_API_BIND/CUBE_MASTER_ADDR/CUBE_API_SANDBOX_DOMAIN/CUBE_API_KEY | CubeAPI/src/config/mod.rs:8-137 |
| F-049 | ENVD_VERSION_FALLBACK "0.2.0"、注解 cube.master.components.envd.version | CubeAPI/src/constants.rs:10-14 |
| F-050 | enum SandboxState（Running/Paused/Pausing）；SandboxNetworkConfig（allowPublicTraffic/allowOut/denyOut/maskRequestHost/rules） | CubeAPI/src/models/mod.rs:36-52 |
| F-051 | EgressRule/Match（sni/host/method/path/scheme/port）/Action（allow/audit/inject）；NewSandbox/Sandbox/SandboxDetail | CubeAPI/src/models/mod.rs:182-238 |
| F-052 | AppError 变体（含 ServiceUnavailable{retry_after}、TooManyRequests 等） | CubeAPI/src/error/mod.rs:14-85 |
| F-053 | LogLevel/LogEvent/Logger；File/Multi/Filtered/Http/Otlp/Noop Logger | CubeAPI/src/logging/mod.rs:42-140 |
| F-054 | CubeMasterClient 异步方法族；中间件 unified_auth、rate_limit | CubeAPI/src/cubemaster/mod.rs:43-551 |
| F-055 | AppServices（sandboxes/snapshots/templates/volumes）；DENY_ALL_IPV4_CIDR 0.0.0.0/0；SandboxService 方法族 | CubeAPI/src/services/mod.rs:16-89 |
| F-056 | Python 示例设 E2B_API_URL；Go 示例 POST /sandboxes | CubeAPI/examples/create.py:8；examples/go/client.go:91 |
| F-057 | openapi 3.1.0、title CubeAPI、前缀 /cubeapi/v1 | openapi.yml:5 |
| F-058 | openapi.yml 2458 行、26 paths（V 阶段勘误，R 阶段误记 25） | openapi.yml（v0.7.2 tag blob） |
| F-059 | openapi info.version 仍为 0.1.0（信源瑕疵） | openapi.yml:11 |

## ⑤ CubeMaster（F-060 ~ F-068）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-060 | common 键：http_port 8089、cube_ops_addr :3010、sync 间隔 1s 等 | CubeMaster/conf.yaml:1-18 |
| F-061 | log 键：path /data/log/CubeMaster-dev、level info | CubeMaster/conf.yaml:20-25 |
| F-062 | cubelet_conf：grpc 9999、default_timeout_insec -1、create_concurrent_limit 100、exposed_port ["80"] | CubeMaster/conf.yaml:27-42 |
| F-063 | auth.enable false；req_template（network_type tap、TZ Asia/Shanghai、denyOut 四 CIDR） | CubeMaster/conf.yaml:44-56 |
| F-064 | MySQL：127.0.0.1:3306、cube/cube_pass、db cube_mvp | CubeMaster/conf.yaml:58-68 |
| F-065 | Redis：127.0.0.1:6379、db 0、max_active 32 | CubeMaster/conf.yaml:70-80 |
| F-066 | scheduler：filter cpu/mem/template_locality/realtime_create_num | CubeMaster/conf.yaml:82-98 |
| F-067 | APPS cubemaster/cubemastercli；ENVD 嵌入（ELF 校验、16MB 上限）；go 1.25.7 | CubeMaster/Makefile:17-145；go.mod:1-50 |
| F-068 | single-node cubemaster.yaml：:8089/:9999、driver mysql | configs/single-node/cubemaster.yaml:48 |

## ⑥ Cubelet（F-069 ~ F-093）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-069 | module github.com/tencentcloud/CubeSandbox/Cubelet，go 1.25.7 | Cubelet/go.mod:1-3 |
| F-070 | config.toml：root /data/cubelet/root、state /data/cubelet/state、version 3 | Cubelet/config/config.toml:1-8 |
| F-071 | http :9998；grpc unix cubelet.sock + tcp :9999；debug :9966；cubetap.sock | Cubelet/config/config.toml:10-40 |
| F-072 | 插件 io.cubelet.controller.config.v1.cubelet（node_status 1s、cubeops） | Cubelet/config/config.toml:42-47 |
| F-073 | cgroup 插件：pool_size 3000、vm_memory_overhead_base 42Mi、coefficient 64 | Cubelet/config/config.toml:58-65 |
| F-074 | network 插件：tap_init_num 500、cidr 192.168.0.0/18、沙箱 IP 169.254.68.6、网关 .5、MTU 1500 | Cubelet/config/config.toml:78-101 |
| F-075 | storage 插件：backend cubecow、data_path /data/cubelet/storage；s3 socket /var/run/s3lvol.sock | Cubelet/config/config.toml:102-135 |
| F-076 | images 插件 runtime io.containerd.cube.v2；runtimes cube=io.containerd.cube.rs、runc=io.containerd.runc.v2 | Cubelet/config/config.toml:148-157 |
| F-077 | workflow 插件：flows init/create/destroy/cleanup，concurrent 100，actions 十余项 | Cubelet/config/config.toml:172-183 |
| F-078 | runtime.v2.task platforms amd64/arm64；vsocket-manager proxyPort 1032；docker.io 腾讯云 mirror | Cubelet/config/config.toml:207-218 |
| F-079 | plugin.conf：start_cmd 带 config.toml、is_fork、start_secs 180 | Cubelet/config/plugin.conf:1-28 |
| F-080 | Makefile：APPS cubelet/cubecli、PROTO 四服务、CONF_VERSION 1.1.7、ldflags 注入 | Cubelet/Makefile:1-62 |
| F-081 | Dockerfile：cargo build -p cubecow 得 libcubecow.a；运行时 ubuntu:22.04；EXPOSE 9999/9998/9966 | Cubelet/Dockerfile:17-157 |
| F-082 | 依赖 cilium/ebpf v0.17.3、containerd/v2 v2.2.2、k8s.io/kubernetes v1.34.1 等 | Cubelet/go.mod:5-207 |
| F-083 | replace grpc v1.67.1、CubeNet/cubevs、pkgs 本地路径 | Cubelet/go.mod:209-219 |
| F-084 | cdp.DeleteOption、DeleteProtectionHook（Name/PreDelete/PostDelete） | Cubelet/pkg/cdp/types.go:11-25 |
| F-085 | cubecow 包注释：cubecow_last_error/Init/InitFromJSON/CowError；命名 tpl-/sb-gen | Cubelet/pkg/cubecow/doc.go:5-44 |
| F-086 | NUMA：NumaInfo/NumaNode、GetNumaInfo 等，读 /sys/devices/system/node/ | Cubelet/pkg/numa/local.go:24-130 |
| F-087 | GC：bucket sandbox/v1、tmpfs 100m、meta.db | Cubelet/services/gc/gc.go:35-138 |
| F-088 | storage/plugin.go：backend 常量、reflinkExt4InitCommands、BuildCowInitJSON/BuildS3CowInitJSON | Cubelet/storage/plugin.go:39-593 |
| F-089 | local 存储：poolSize 500/poolWorkers 8、formatSize 1Gi、base.raw、bucket emptydir/nfs | Cubelet/storage/local.go:52-148 |
| F-090 | hostdir /data/cubelet/hostdir；s3 重试 5s；池类型 copy/copy_reflink | Cubelet/storage/hostdir.go:25-41；s3_init.go:18-26；pool.go:30-34 |
| F-091 | network plugin：delegateNetworkManager、bucket network/v1 | Cubelet/network/plugin.go:34-88 |
| F-092 | Cubelet 结构（nodeReadyGracePeriod 120s）；versioninfo collector 组件与文件名常量 | Cubelet/pkg/cubelet/cubelet.go:35-121；versioninfo/collector.go:35-62 |
| F-093 | cloud.go：CUBE_SANDBOX_NODE_ID/IP 环境变量、HostIdentity；ValidateBDF | Cubelet/pkg/utils/cloud.go:18-200；bdf.go:10-14 |

## ⑦ CubeHypervisor 与 guest-init（F-094 ~ F-140）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-094 | cube-hypervisor v28.0.0、edition 2021、authors Cloud Hypervisor Authors | hypervisor/Cargo.toml:2-5 |
| F-095 | default-run cube-hypervisor、rust-version 1.77.0、KVM VMM；release lto + opt-level "s" | hypervisor/Cargo.toml:6-18 |
| F-096 | 依赖 clap/seccompiler/vmm-sys-util 等 | hypervisor/Cargo.toml:20-47 |
| F-097 | features：default kvm、guest_debug、mshv、tdx、lib_support | hypervisor/Cargo.toml:62-70 |
| F-098 | workspace 登记 29 members（api_client…virtiofsd，含 block_util） | hypervisor/Cargo.toml（v0.7.2 tag blob） |
| F-099 | workspace.deps：linux-loader 0.13、vm-memory 0.16.1；vfio-ioctls/vhost-user git rev pin | hypervisor/Cargo.toml:105-117 |
| F-100 | lib.rs：模块导出；enum Error（ReviverChannel/StartVmm 等） | hypervisor/src/lib.rs:1-64 |
| F-101 | VmmInstance：new/send_request/join；Drop 时 VmmShutdown，失败 kill SIGTERM | hypervisor/src/lib.rs:69-349 |
| F-102 | create_app：cube-hypervisor 命令、参数组 vm-config/vmm-config/logging | hypervisor/src/main.rs:104-113 |
| F-103 | vm-config 参数：--cpus/--memory/--kernel/--disk/--net/--pmem/--vsock 等 | hypervisor/src/main.rs:114-337 |
| F-104 | logging：-v 计数对应 Warn/Info/Debug/Trace、--log-file/--sandbox-id | hypervisor/src/main.rs:301-452 |
| F-105 | --api-socket/--restore/--tpm/--pvpanic/--sgx-epc（x86）/--gdb、snapshot-version | hypervisor/src/main.rs:339-422 |
| F-106 | --seccomp：true/false/log/process（默认），对应 Trap/Allow/Log/KillProcess | hypervisor/src/main.rs:359-644 |
| F-107 | start_vmm：socket dup2 到 512；payload 分支 parse/create/boot；--restore 分支 restore | hypervisor/src/main.rs:439-734 |
| F-108 | common.rs：默认日志 /data/log/CubeVmm/vmm.log；coredump_filter 0x33、limit 2GB | hypervisor/src/common.rs:15-29 |
| F-109 | Logger 结构与日志格式串 | hypervisor/src/common.rs:36-252 |
| F-110 | vmm crate：gdbstub/micro-http/tokio/linux-loader/zerocopy 依赖 | hypervisor/vmm/Cargo.toml:1-65 |
| F-111 | vmm lib.rs 模块；EpollDispatch；LOG_REOPEN_INTERVAL 60 分钟 | hypervisor/vmm/src/lib.rs:69-228 |
| F-112 | start_vmm_thread 参数（含 hypervisor trait object、sandbox_id） | hypervisor/vmm/src/lib.rs:340-355 |
| F-113 | 线程内 apply seccomp、spawn "vmm" 线程、control_loop；HTTP socket/fd 分支 | hypervisor/vmm/src/lib.rs:367-422 |
| F-114 | Vmm 结构与方法（vm_create/boot/pause/snapshot/restore/shutdown 等）；HANDLED_SIGNALS TERM/INT | hypervisor/vmm/src/lib.rs:449-1094 |
| F-115 | VmState 五态（Created/Running/Shutdown/Paused/BreakPoint）+ valid_transition | hypervisor/vmm/src/vm.rs:324-368 |
| F-116 | VmOpsHandler/VmOps（guest_mem/mmio/pio 读写） | hypervisor/vmm/src/vm.rs:370-461 |
| F-117 | physical_bits：KvmPvm guest 取 min(max,43) | hypervisor/vmm/src/vm.rs:463-478 |
| F-118 | Vm 结构（initramfs/device_manager/config/state/cpu_manager/memory_manager 等） | hypervisor/vmm/src/vm.rs:480-503 |
| F-119 | Vm 方法（boot/shutdown/add_*/resize/counters/balloon）；SIGWINCH | hypervisor/vmm/src/vm.rs:506-2488 |
| F-120 | VmSnapshot（clock/common_cpuid）；Snapshottable（snapshot/restore/dirty_log/migration） | hypervisor/vmm/src/vm.rs:2648-2926 |
| F-121 | cpu.rs 结构（LocalApic/Ioapic/Gic* 等） | hypervisor/vmm/src/cpu.rs:102-303 |
| F-122 | Vcpu：new/configure/run→VmExit；Snapshottable | hypervisor/vmm/src/cpu.rs:324-518 |
| F-123 | aarch64 vcpu init：PSCI/POWER_OFF/PMU_V3，PMU 失败去特性重试 | hypervisor/vmm/src/cpu.rs:419-452 |
| F-124 | CpuManager：create_boot_vcpus/start_boot_vcpus/resize/create_madt/pptt | hypervisor/vmm/src/cpu.rs:520-1475 |
| F-125 | gdb.rs：Debuggable trait、GdbRequest/Response 类型 | hypervisor/vmm/src/gdb.rs:42-122 |
| F-126 | GdbStub：impl Target/MultiThreadBase/Breakpoints；gdb_thread | hypervisor/vmm/src/gdb.rs:124-495 |
| F-127 | arch crate：arch_memory_regions/configure_*/get_host_cpu_phys_bits；x86 generate_common_cpuid | hypervisor/arch/src/lib.rs:54-91 |
| F-128 | NumaNode/NumaNodes、InitramfsConfig、DeviceType、PAGE_SIZE 4096 | hypervisor/arch/src/lib.rs:101-139 |
| F-129 | pci crate：模块 bus/configuration/device/msi/msix/vfio；PciInterruptPin；PCI_CONFIG_IO_PORT 0xcf8 | hypervisor/pci/src/lib.rs:9-177 |
| F-130 | pci/bus.rs：PciRoot/PciBus/PciConfigIo/Mmio、NUM_DEVICE_IDS 32 | hypervisor/pci/src/bus.rs:17-470 |
| F-131 | msi.rs（MsiCap/MsiConfig）；msix.rs（MAX 2048、entry 16 字节、enable bit 15） | hypervisor/pci/src/msi.rs:18-178；msix.rs:19-101 |
| F-132 | vfio.rs：UserMemoryRegion、VfioPciDevice、Vfio trait | hypervisor/pci/src/vfio.rs:37-1217 |
| F-133 | qcow：magic 0x5146_49fb、cluster_bits 16、max 1<<44；QcowHeader 19 字段；ImageType | hypervisor/qcow/src/qcow.rs:32-1702 |
| F-134 | vhdx：VhdxError、Vhdx::new/virtual_disk_size/impl Read | hypervisor/vhdx/src/vhdx.rs:17-88 |
| F-135 | tpm：CRB_BUFFER_MAX 3968、enum Commands 17 变体、Ptm trait | hypervisor/tpm/src/lib.rs:9-315 |
| F-136 | docs：api socket 默认路径、/vmm.* endpoints；vsock CID 表；Differences 章节 | hypervisor/docs/api.md；vsock.md:5；README.md:29-312 |
| F-137 | cube-init v0.1.0，deps nix 0.26 等 | guest-init/Cargo.toml:1-17 |
| F-138 | main：PID 1 校验；PMEM_DEV /dev/pmem1；挂 ext4 MS_RDONLY+dax；拉起 cube-agent | guest-init/src/main.rs:28-70 |
| F-139 | init_env：13 条 cgroup v1 挂载；INIT_ROOTFS_MOUNTS（proc/sysfs/tmpfs/devpts） | guest-init/src/init_env.rs:23-304 |
| F-140 | init()：mount_sys/unified cgroup/mount_cgroup/rc.local；cgroup2 分支；wrapper_mode=on | guest-init/src/init_env.rs:23-304 |

## ⑧ CubeAgent 与 CubeShim（F-141 ~ F-165）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-141 | cube-agent v0.1.0：ttrpc 0.8.4 async、tokio-vsock 0.7.2 | agent/Cargo.toml:2-34,97-99 |
| F-142 | workspace members rustjail/cube；features seccomp、standard-oci-runtime | agent/Cargo.toml:86-95 |
| F-143 | Makefile：SECCOMP yes、MUSL yes | agent/Makefile:8-53 |
| F-144 | SubCommand：Init、Exec | agent/src/main.rs:84-113,300-305 |
| F-145 | Init→rustjail::container::init_child；Exec→cube::rootfs::do_exec_mount | agent/src/main.rs:300-305 |
| F-146 | start_sandbox：rpc::start、passfd listener、notify ready，结束 POWER_OFF | agent/src/main.rs:397-412 |
| F-147 | VSOCK_ADDR vsock://-1、:1024；AgentConfig 字段 | agent/src/config.rs:31-81 |
| F-148 | Default server vsock://-1:1024；supports_seccomp 探测 | agent/src/config.rs:145-162 |
| F-149 | Sandbox：containers map、shared uts/ipc ns、setup_shared_namespaces、online_cpu_memory | agent/src/sandbox.rs:36-257 |
| F-150 | PERSISTENT_NS_DIR /var/run/sandbox-ns；NamespaceType Ipc/Uts/Pid | agent/src/namespace.rs:19-159 |
| F-151 | MOUNT_GUEST_TAG cubeShared；STORAGE_HANDLER_LIST 9 项（blk/virtio-fs/overlayfs…） | agent/src/mount.rs:37-143 |
| F-152 | 存储驱动常量 virtio-fs/blk/blk-cube/mmioblk/scsi/nvdimm/overlayfs | agent/src/device.rs:37-53 |
| F-153 | passfd：:1027、timeout 5s、MAX_PENDING 256 | agent/src/passfd_io.rs:13-15 |
| F-154 | rpc start 注册 AgentService + Health 两个 ttrpc service | agent/src/rpc.rs:1938-1945 |
| F-155 | 就绪通知：x86 写 IO 端口 0x680 值 0x8；aarch64 写 MMIO 0x09030000 | agent/src/rpc.rs:1957-1978 |
| F-156 | AgentService：CreateContainer/StartContainer/RemoveContainer/ExecProcess/SignalProcess/WaitProcess/GetVolumeStats/ResizeVolume | agent/libs/protocols/protos/agent.proto:21-73 |
| F-157 | do_exec_mount：setns 到 /proc/<pid>/ns/mnt、BIND 挂载、umount2 DETACH | agent/cube/src/rootfs.rs:14-209 |
| F-158 | CubeShim：Shim v2、runtime_type io.containerd.cube.v2 | CubeShim/README.md:3-86 |
| F-159 | shim main：no_reaper/logger/sub_reaper 均 true；shim_run "io.containerd.cube.rs" | CubeShim/shim/src/main.rs:17-54 |
| F-160 | set_process：coredump_filter 0x33、RLIMIT_CORE 2GB、dummy socket dup2 512 | CubeShim/shim/src/main.rs:93-138 |
| F-161 | 依赖 containerd-shim/protos 0.9.0、ttrpc 0.5.8、cube-hypervisor lib_support | CubeShim/shim/Cargo.toml:17-32 |
| F-162 | shim 模块 common/container/cube/hypervisor/log/sandbox/service/snapshot | CubeShim/shim/src/lib.rs:5-12 |
| F-163 | SHIM_VERSION 取 env；注解 cube.rootfs.wlayer.path/cube.propagation.mounts/log_forwarding | CubeShim/shim/src/common/mod.rs:17-37 |
| F-164 | PAUSE_VM_SNAPSHOT_BASE /data/cubelet/root/pausevm；GUEST_PROPAGATION_DIR /run/propagation | CubeShim/shim/src/common/mod.rs:27-41 |
| F-165 | protoc crate 模块；csi VolumeUsage（Unit/BYTES/INODES） | CubeShim/protoc/src/lib.rs:7-14；csi.rs:258-518 |

## ⑨ CubeNet/eBPF 网络数据面（F-166 ~ F-184）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-166 | 三条 go:generate bpf2go：localgw/mvmtap/nodenic | CubeNet/cubevs/cubevs.go:12-14 |
| F-167 | Params：MVM IP/MAC/GW、Egress MAC/redirect flags、L7 mark/mask | CubeNet/cubevs/cubevs.go:17-47 |
| F-168 | TAPDevice（IP/ID/Ifindex）；mvmMetadata（Version/IP/UUID[64]/DNSPolicy） | CubeNet/cubevs/cubevs.go:49-71 |
| F-169 | TCDirection、BPFRedirectFlagIngress 1、MVMPort | CubeNet/cubevs/cubevs.go:73-91 |
| F-170 | BPF 结构体：l7PortEntry、netPolicyValueV2/V3、dnsAllow*/dnsQueryTrack* | CubeNet/cubevs/cubevs.go:93-177 |
| F-171 | 常量：maxDNSAllow 1024、dnsNameLen 256、L7 flag/required、L7Scheme、netPolicyValueStatic | CubeNet/cubevs/cubevs.go:179-202 |
| F-172 | 程序名 from_envoy/from_cube/from_world；DNS 五 tail-call slot（dns_tail_calls） | CubeNet/cubevs/cubevs.go:203-219 |
| F-173 | map 名：mvmip_to_ifindex、remote/local_port_mapping、allow_out V2/V3、deny_out、dns_* | CubeNet/cubevs/cubevs.go:221-234 |
| F-174 | 全局变量名；TC clsact/bpf attr、priority/handle | CubeNet/cubevs/cubevs.go:235-274 |
| F-175 | bpfFSPath /sys/fs/bpf、pinPath/loadPinnedMap；port mapping CRUD | CubeNet/cubevs/map.go:13-29；port.go:17-359 |
| F-176 | SNAT：snat_iplist、maxSNATIPs 4、端口起点 30000、SetSNATIPs | CubeNet/cubevs/snat.go:11-49 |
| F-177 | 会话：ingress/egress_sessions、reaper 5s、maxSessions 1048576/80% 告警；ESTABLISHED 3h | CubeNet/cubevs/reaper.go:14-141 |
| F-178 | L7 mark 0xCE010000/0xCE020000、mask 0xFFFF0000；rewriteConstants/pinProgs/populateDNSTailCalls | CubeNet/cubevs/miscs.go:38-40 |
| F-179 | Init：load 三对象 + attach TC（envoy egress/world egress/world ingress/cube ingress） | CubeNet/cubevs/miscs.go:311-405 |
| F-180 | map.h：SEC maps + pin by name；allow_out_v3 HASH_OF_MAPS/LPM_TRIE；dns_tail_calls PROG_ARRAY 16 | CubeNet/src/map.h:13-238 |
| F-181 | TC 程序：from_envoy（dnat/snat/redirect）、from_cube、from_world + DNS chunk 程序 | CubeNet/src/localgw.bpf.c:67-117；mvmtap.bpf.c:848-955；nodenic.bpf.c:479-567 |
| F-182 | 沙箱固定 IP 169.254.68.6、网关 169.254.68.5 | docs/zh/architecture/network.md:75 |
| F-183 | 会话超时：SYN 1m/ESTABLISHED 3h/FIN 2m/TW 2m（主动关闭 10s）/UDP 30·180/ICMP 30；reaper 5s；80% 告警 | docs/zh/architecture/network.md:140-144 |
| F-184 | SNAT 最多 4 IP（jhash%4）、源端口 30000 起；拒绝段；节点端口三段；mapping 仅用 20000–29999 | docs/zh/architecture/network.md:162-267 |

## ⑩ CubeEgress/CubeProxy（F-185 ~ F-196）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-185 | Egress 透明监听 192.168.0.1:8080/:8443 ssl | CubeEgress/nginx.conf:109-141 |
| F-186 | lua_shared_dict：cert_cache 64m/policy_store 128m | CubeEgress/nginx.conf:24-28 |
| F-187 | init：cert_signer（leaf 7 天）+ audit（access.jsonl）；access_phase.decide() | CubeEgress/nginx.conf:32-116 |
| F-188 | policy.lua：STORE/INDEX_KEY/MAX_L7_PORTS 8；CIDR/identity/match 校验 | CubeEgress/lua/policy.lua:26-220 |
| F-189 | 导出 list_ips/get/put/delete/patch/dump/count/bulk_load；fingerprint fp- | CubeEgress/lua/policy.lua:249-447 |
| F-190 | 管理 server 127.0.0.1:9091；admin 路由 /admin/v1/* | CubeEgress/nginx.conf:212-223；lua/admin.lua:187-195 |
| F-191 | redact secret；audit 事件 http_request/security_event/tls_handshake | CubeEgress/lua/admin.lua:45-63；audit.lua:34-359 |
| F-192 | CubeProxy utils：gRPC 状态映射表（400→3 等） | CubeProxy/lua/utils.lua:13-102 |
| F-193 | CubeProxy 监听 8081/8080 ssl/9090 http2；balancer_by_lua | CubeProxy/nginx.conf:104-396 |
| F-194 | location 正则（Start/Connect/WatchDir）；/_sidecar_resume→/internal/resume；shared_dict meta/state/last_active | CubeProxy/nginx.conf:130-196 |
| F-195 | start.sh：CIDR 默认 192.168.0.0/18、admin 9091；gen-ca prime256v1/3650 天 | CubeEgress/start.sh:66-257；gen-ca.sh:4-32 |
| F-196 | Egress 镜像 openresty-tproxy:1.29.2.5；Proxy openresty:1.21.4.1 alpine-fat | CubeEgress/Dockerfile:1-39；CubeProxy/Dockerfile:5-25 |

## ⑪ CubeCoW 与 CubeS3lvol（F-197 ~ F-214）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-197 | cubecow v0.1.0，crate-type lib/cdylib/staticlib；bin cubecow-cli | cubecow/Cargo.toml:2-23 |
| F-198 | Volume：name/size_bytes/device_path/snapshot_count/export_*/deletable | cubecow/src/lib.rs:52-80 |
| F-199 | Snapshot：name/size_bytes/origin_volume/export_*/deletable | cubecow/src/lib.rs:83-136 |
| F-200 | initialize 按 BackendKind Reflink/S3 分支 | cubecow/src/lib.rs:158 |
| F-201 | trait Engine：create/delete/resize volume、snapshot/from snapshot、list、activate、metrics | cubecow/src/engine/mod.rs:36-140 |
| F-202 | BackendKind reflink(default)/s3；S3Config socket /var/run/s3lvol.sock；ReflinkConfig root_dir | cubecow/src/config/mod.rs:55-151 |
| F-203 | ReflinkEngine：REFLINK_BLOCK_SIZE 512、FICLONE 0x40049409、name_index | cubecow/src/engine/reflink.rs:78-128 |
| F-204 | initialize_with_config：建 volumes 目录、probe_reflink_support、scan_and_rebuild_index | cubecow/src/engine/reflink.rs:150-185 |
| F-205 | create_volume create_new+set_len；不允许缩容；snapshot 调 ficlone | cubecow/src/engine/reflink.rs:386-715 |
| F-206 | ficlone：ioctl(dst, FICLONE, src) | cubecow/src/engine/reflink.rs:1083-1092 |
| F-207 | FFI：COW_OK 0/NOT_FOUND -1/ALREADY -2/PANIC -99；extern cubecow_* | cubecow/src/ffi.rs:47-1173 |
| F-208 | S3 引擎：UDS s3lvol.sock JSON-RPC 11 个 rcow_*、index.json | cubecow/src/engine/s3.rs |
| F-209 | s3lvol_tgt=NVMe/TCP target；make_release 参数 | CubeS3lvol/README.md:3-16 |
| F-210 | Makefile 目标 all/shared/static/app/check-* | CubeS3lvol/Makefile:51-100 |
| F-211 | scripts/rpc.py：_existing/find_upstream_rpc_py；S3LVOL_RPC_DISABLE_FALLBACKS | CubeS3lvol/scripts/rpc.py:14-39 |
| F-212 | C 侧注册 30 个 rcow_* RPC（R 阶段登记的 9 个为核心卷管理子集：lvstore attach/create、lvol/snapshot/clone、resize/delete、get/active_bdev） | CubeS3lvol/module/bdev/s3lvol/vbdev_s3lvol_rpc.c（v0.7.2 tag blob） |
| F-213 | S3 卷后端 AWS S3/COS/R2/MinIO；pip install cubesandbox>=0.6.0；Volume.create(driver=s3) | docs/zh/guide/s3-volume.md:3-28 |
| F-214 | s3fs 引用计数挂载/卸载，数据保留；destroy 删 volumes/<id>/ 前缀 | docs/zh/guide/s3-volume.md:174 |

## ⑫ CubeOps/CLM/TemplateCenter（F-215 ~ F-225）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-215 | CubeOps module、go 1.25.7；gin/gorm/pgx/redigo/go-containerregistry | CubeOps/go.mod:1-25 |
| F-216 | CubeOps :3010；API 组 auth/cluster/agenthub/store/config/warehouse/sdk/internal | CubeOps/README.md:12-30 |
| F-217 | auth login/refresh/session/change-password；cluster overview/versions/nodes、labels/isolation | CubeOps/internal/auth/handler.go:35-44；handler/cluster.go:41-49 |
| F-218 | agenthub instances CRUD/restart；nodemanagement register/status | CubeOps/internal/handler/agenthub.go:90-95；nodemanagement/handler/agent.go:26-34 |
| F-219 | sdkV2 /sandboxes、logs；Dockerfile alpine:3.20 EXPOSE 3010 | CubeOps/internal/server/server.go:138-198；Dockerfile:10-45 |
| F-220 | CLM module、go 1.25.7；redis v9.20、zap、backoff/v7、miniredis | cube-lifecycle-manager/go.mod:1-12 |
| F-221 | main：stream/client/registry/lease/resumer/sweeper/httpapi；goroutine 组 | cube-lifecycle-manager/cmd/cube-lifecycle-manager/main.go:67-255 |
| F-222 | POST /internal/resume（WriteTimeout 35s、resume context 25s）、healthz/readyz | cube-lifecycle-manager/internal/httpapi/server.go:66-120 |
| F-223 | eventbus Publish/Wait；schema 前缀 cube:v1:shared:、Stream max 100000；Op/State 常量 | cube-lifecycle-manager/internal/eventbus/bus.go:29-47；lifecycle/schema.go:24-107 |
| F-224 | TemplateCenter module、go 1.25.7；replace CubeMaster/cubedb/Cubelet | CubeTemplateCenter/go.mod:1-144 |
| F-225 | TemplateCenter：/metrics//health；internal build/artifact delete/upload | CubeTemplateCenter/pkg/httpservice/server.go:130-131；api/internal.go:338-340 |

## ⑬ SDK 三端与 pkgs（F-226 ~ F-233）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-226 | sdk/go module、go 1.22；Client/NewClient、Create/Connect/List/Health | sdk/go/go.mod:1-3；client.go:22-108 |
| F-227 | Sandbox：GetHost/GetInfo/Pause/Resume/SetTimeout/UpdateNetwork/Kill/RunCode/Commands/Files | sdk/go/sandbox.go:25-257 |
| F-228 | Commands.Run；Files ForUser/Read/Write/List/Stat/Exists/Remove/Rename/MakeDir/WatchDir | sdk/go/commands.go:15-19；files.go:61-154 |
| F-229 | snapshot Snapshot*/Rollback/Clone；template Build*/Alias；volume CRUD | sdk/go/snapshot.go:88-175；template.go:94-166；volume.go:69-113 |
| F-230 | policy Match/Inject/Action/Rule；connect envelope；transport http client；envd default root、Watcher | sdk/go/policy.go:29-102；connect.go:23-64；envd.go:24-506 |
| F-231 | sdk/node @cubesandbox/sdk 0.3.0、node ≥18、undici；13 个 ts 文件 | sdk/node/package.json:2-51 |
| F-232 | sdk/python cubesandbox 0.7.0；导出 Sandbox/NEVER_TIMEOUT/Config/Execution/Pty/Template/Volume | sdk/python/pyproject.toml:1-3；__init__.py:5-16 |
| F-233 | pkgs：CubeLog/blobstore(minio-go)/cubeddb(goose,gorm)/proto | pkgs/*/go.mod |

## ⑭ 生命周期/模板/日志与版本（F-234 ~ F-244）

| 编号 | 摘要 | 锚点 |
|---|---|---|
| F-234 | 五状态 running/pausing/paused/resuming/terminated | docs/zh/guide/lifecycle.md:13 |
| F-235 | timeout 单位秒（e2b 毫秒）；on_timeout kill(默认)/pause；NEVER_TIMEOUT -1、0 立即超时 | docs/zh/guide/lifecycle.md:21-29 |
| F-236 | 删除持锁沙箱：503 + Retry-After: 2 | docs/zh/guide/lifecycle.md:129 |
| F-237 | 默认超时键 default_timeout_insec=-1；paused_resource_release_ratio [0,1] 默认 0 | docs/zh/guide/lifecycle.md:237-257 |
| F-238 | 恢复被拒链：Cubelet 130409 → CubeAPI 409 → WebUI | docs/zh/guide/lifecycle.md:281 |
| F-239 | 探针 2xx 后快照；必填 --expose-port/--probe；envd :49983 /health 204；两种制模板方式；tpl merge/redo | docs/zh/guide/templates.md:15-61 |
| F-240 | 沙箱日志 io.containerd.runtime.v2.task/default/<id>/stdout；模板日志 /data/log/template/；转发需 shim ≥v0.4.0 | docs/zh/guide/sandbox-logs.md:59-86 |
| F-241 | 版本线：v0.1.0 04-20 → v0.7.0 08-28 → v0.7.1 09-11 → v0.7.2（标题 09-23） | docs/zh/changelog/v0.7.2.md:2 |
| F-242 | v0.2.2：默认暴露端口改 49999/49983 | docs/zh/changelog/v0.2.2.md:21 |
| F-243 | v0.4.0：基础镜像 ubuntu:20.04、glibc 降至 2.31 | docs/zh/changelog/v0.4.0.md:7 |
| F-244 | WebUI：19 个 .tsx、main.tsx 18 路由（主导航 15 页面为 Overview…Warehouse） | web/src/main.tsx、web/src/pages/ |
