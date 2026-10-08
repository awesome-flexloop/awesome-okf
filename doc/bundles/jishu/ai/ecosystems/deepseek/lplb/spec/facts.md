---
type: spec
title: "LPLB 事实清单"
---

# LPLB 事实清单

## 项目元信息

F-001: 文件 `pyproject.toml` 第6-10行，项目名称为 `lplb`，版本 `0.1.0`，描述为 "Linear-programming-based expert parallelism load balancing."，作者为 Huanqi Cao (caohuanqi@deepseek.com)，依赖 `torch`，要求 Python >= 3.8。

F-002: 文件 `pyproject.toml` 第22-23行，可选依赖组 `dev` 包含 `setuptools`、`wheel`、`torch`、`deep_ep`。

F-003: 文件 `pyproject.toml` 第32-38行，包数据包含 `resources/csrc-tmpl/*`、`resources/mathdx/lib/libcusolverdx.fatbin`、`resources/mathdx/include/**/*`、`resources/mathdx/external/**/*`。

## 公共 API（lplb/__init__.py）

F-004: 文件 `lplb/__init__.py` 第1-4行，从 `lplb.planner` 导入 `Planner` 类，`__all__` 列表仅包含 `['Planner']`。

## Planner 类（lplb/planner.py）

F-005: 文件 `lplb/planner.py` 第17-35行，模块级函数 `_get_solver(n_group: int, group_size: int, dup_per_rank: int, n_local_experts: int, n_combined_experts: int, ep_group: torch.distributed.ProcessGroup) -> CompiledSolver`，使用 `@functools.lru_cache(maxsize=None)` 装饰。函数体调用 `CompiledSolver(str(Path(__file__).parent / 'resources'), n_group, group_size, dup_per_rank, 256, n_local_experts, n_combined_experts, ep_group)`。

F-006: 文件 `lplb/planner.py` 第38-102行，类 `Planner` 的 `__init__(self, redundant_to_original: torch.Tensor, n_routed_experts: int, n_logical_routed_experts: int, ep_size: int | None = None, group: torch.distributed.ProcessGroup | None = None) -> None`。参数 `redundant_to_original` 形状为 `[group_size, num_redundants]`，类型 `int32`，存储在 CUDA 上。实例属性包括：`self.r2o`、`self.o2r`（r2o 的 argsort）、`self.group_size`、`self.num_redundants`、`self.n_routed_experts`、`self.n_logical_routed_experts`、`self.ep_size`、`self.n_group = ep_size // group_size`、`self.n_local_routed_experts = n_routed_experts // ep_size`、`self.n_local_logical_routed_experts = n_logical_routed_experts // ep_size`、`self.combined_redundant_experts = (n_local_routed_experts - n_local_logical_routed_experts) // num_redundants`、`self.ep_group`、`self.deep_ep_initialized = False`、`self.solver`（通过 `_get_solver` 获取的 `CompiledSolver` 实例）。

F-007: 文件 `lplb/planner.py` 第104-113行，方法 `Planner.init_from_deep_ep(self, buffer: Buffer) -> None`。当 `self.deep_ep_initialized` 为 True 时直接返回。否则设置 `self.deep_ep_initialized = True` 并调用 `self.solver.init_comm(torch.device('cuda'), not buffer.low_latency_mode, buffer.num_rdma_bytes == 0)`。类型提示中 `Buffer` 来自 `deep_ep`（TYPE_CHECKING 条件导入）。

F-008: 文件 `lplb/planner.py` 第115-182行，方法 `Planner.update_redundancy_mapping(self, workload: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]`。当 `workload is None` 时，`nored_phy2log` 为 `torch.arange(n_logical_routed_experts, device='cuda', dtype=torch.int32)`。否则调用 `rebalance_experts(workload.unsqueeze(0), n_logical_routed_experts, n_group, max(1, ep_size // torch.cuda.device_count()), ep_size)` 获取结果。返回值为 `(phy2log, log2phy, logcnt)` 三元组，其中 `phy2log` 形状 `(n_routed_experts,)`、`log2phy` 形状 `(n_logical_routed_experts, max_logcnt)`（填充 -1）、`logcnt` 形状 `(n_logical_routed_experts,)` 类型 `int32`。方法同时设置 `self.phy2log = phy2log`。

F-009: 文件 `lplb/planner.py` 第184-194行，方法 `Planner.count_workload(self, idx: torch.Tensor, n_sms: int) -> tuple[torch.Tensor, torch.Tensor]`。参数 `idx` 值范围为 `[-1, n_logical_routed_experts)`，包含 -1 表示忽略。返回值第一个元素形状 `(n_logical_routed_experts,)`，第二个元素形状 `(n_sms, n_logical_routed_experts)`。内部调用 `self.solver.count_idx(idx, n_sms, 256)`。

F-010: 文件 `lplb/planner.py` 第196-217行，方法 `Planner.solve_probs(self, workload: torch.Tensor, avail_counter: torch.Tensor) -> torch.Tensor`。参数 `workload` numel 等于 `n_experts`，`avail_counter` numel 等于 1。返回值形状 `(num_redundants, combined_redundant_experts)`。内部先将 workload reshape 为 `(n_group, group_size, n_local_logical_routed_experts)`，当 `ep_group is not None and not deep_ep_initialized` 时执行 `torch.distributed.all_reduce(workload, group=ep_group)`，然后调用 `self.solver.solve(workload, self.r2o, self.phy2log, avail_counter)`。

F-011: 文件 `lplb/planner.py` 第219-243行，方法 `Planner.weighted_select_target(self, idx: torch.Tensor, o_weight: torch.Tensor, local_workload_by_sm: torch.Tensor, n_sms: int) -> torch.Tensor`。参数 `idx` 值范围 `[-1, n_logical_routed_experts)`，`o_weight` 形状 `(num_redundants, combined_redundant_experts)`，`local_workload_by_sm` 来自 `count_idx`，`n_sms` 为 CUDA SM 数量。返回值形状与 `idx` 相同，值范围 `[-1, n_routed_experts)`。内部调用 `self.solver.map_idx(idx, o_weight, local_workload_by_sm, self.o2r, self.phy2log, n_sms, 256)`。

F-012: 文件 `lplb/planner.py` 第245-266行，方法 `Planner.run(self, idx: torch.Tensor, avail_counter: torch.Tensor, n_sms: int | None = None) -> torch.Tensor`。当 `n_sms is None` 时取 `torch.cuda.get_device_properties(torch.cuda.current_device()).multi_processor_count`。方法依次调用 `self.count_workload(idx, n_sms)`、`self.solve_probs(local_workload, avail_counter)`、`self.weighted_select_target(idx, o_weight, local_workload_by_sm, n_sms)`，返回映射后的物理专家索引。

## EPLB 模块（lplb/eplb.py）

F-013: 文件 `lplb/eplb.py` 第6-46行，函数 `balanced_packing(weight: torch.Tensor, num_packs: int) -> tuple[torch.Tensor, torch.Tensor]`。参数 `weight` 形状 `[X, n]`，`num_packs` 为整数。返回值 `pack_index` 形状 `[X, n]`（每项所属 pack 索引，int64），`rank_in_pack` 形状 `[X, n]`（项在 pack 内的 rank，int64）。当 `groups_per_pack == 1` 时直接返回 `arange` 和全零张量。否则对每层按权重降序排列，贪心选择当前权重最小且未满的 pack。

F-014: 文件 `lplb/eplb.py` 第49-77行，函数 `replicate_experts(weight: torch.Tensor, num_phy: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]`。参数 `weight` 形状 `[X, num_log]`，`num_phy` 为复制后的总专家数。返回值 `phy2log` 形状 `[X, num_phy]`（每个物理专家对应的逻辑专家 ID，int64）、`rank` 形状 `[X, num_phy]`（副本序号，int64）、`logcnt` 形状 `[X, num_log]`（每个逻辑专家的副本数，int64）。算法从 `num_log` 个专家开始，逐个复制 `weight/logcnt` 最大的专家直到 `num_phy`。

F-015: 文件 `lplb/eplb.py` 第80-148行，函数 `rebalance_experts_hierarchical(weight: torch.Tensor, num_physical_experts: int, num_groups: int, num_nodes: int, num_gpus: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]`。参数 `weight` 形状 `[num_moe_layers, num_logical_experts]`。内部定义嵌套函数 `inverse(perm: torch.Tensor) -> torch.Tensor`，使用 `scatter_` 计算置换逆。三步流程：Step1 调用 `balanced_packing` 将 groups 打包到 nodes；Step2 调用 `replicate_experts` 在节点内构造冗余专家；Step3 调用 `balanced_packing` 将物理专家打包到 GPUs。返回值 `pphy2log`、`pphyrank`、`logcnt`。

F-016: 文件 `lplb/eplb.py` 第151-190行，函数 `rebalance_experts(weight: torch.Tensor, num_replicas: int, num_groups: int, num_nodes: int, num_gpus: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]`。参数 `weight` 形状 `[layers, num_logical_experts]`。当 `num_groups % num_nodes == 0` 时调用 `rebalance_experts_hierarchical(weight, num_replicas, num_groups, num_nodes, num_gpus)`，否则退化为 `rebalance_experts_hierarchical(weight, num_replicas, 1, 1, num_gpus)`。返回值 `phy2log` 形状 `[layers, num_replicas]`（int64）、`log2phy` 形状 `[layers, num_logical_experts, maxlogcnt]`（填充 -1，int64）、`logcnt` 形状 `[layers, num_logical_experts]`（int64）。

## C++ 扩展（csrc/plugin.cpp）

F-017: 文件 `csrc/plugin.cpp` 第122-661行，结构体 `compiled_solver`。成员变量：`cudaKernel_t kernel_solve`、`kernel_map_idx`、`kernel_count_idx`（均初始化为 nullptr）；`cudaLibrary_t module`（初始化为 nullptr）；`int n_group`、`group_size`、`dup_per_rank`、`block_dim`、`smem_size`（初始值 -1）；`int n_nodes = 1`、`node_size = 1`、`self_node = 0`、`self_device = 0`；条件编译 `USE_NVSHMEM` 下的 `nvshmem_team_t cpu_rdma_team = NVSHMEM_TEAM_INVALID`；`float *workload_buf_internode = nullptr`；`uint64_t *workload_sig_internode = nullptr`；`float **workload_buf_intranode = nullptr`；`uint32_t **workload_sig_intranode = nullptr`；`std::vector<float *> workload_buf_intranode_cpu`；`std::vector<uint32_t *> workload_sig_intranode_cpu`；`int n_experts`、`n_local_experts`、`n_combined_experts`；`c10::intrusive_ptr<c10d::ProcessGroup> pg`；`bool init_comm_done = false`。

F-018: 文件 `csrc/plugin.cpp` 第149-327行，方法 `std::string compiled_solver::compile_cubin(const std::string &resource_path)`。动态检测当前 GPU 架构 `arch = prop.major * 10 + prop.minor`。读取 `resource_path + "/csrc-tmpl/minilp.cu"` 作为内核源码。NVRTC 编译选项包含 `-dlto`、`--relocatable-device-code=true`、mathdx include 路径、`-DGROUP_SIZE=`、`-DDUP_PER_RANK=`、`-DSM_Ver=`、`-DBLOCK_DIM=`、`-arch=sm_<arch>` 等。使用 nvJitLink 链接在线生成的 LTO IR 与离线 fatbin（`libcusolverdx.fatbin`），条件编译下链接 `libnvshmem_device.a`。编译结果缓存到 `LPLB_CACHE_PATH` 环境变量指定路径或 `DEFAULT_CACHE_DIR`，缓存键为源码和编译选项的哈希值。返回 cubin 文件路径。

F-019: 文件 `csrc/plugin.cpp` 第329-352行，方法 `void compiled_solver::prepare_module(const std::string &cubin)`。调用 `cudaLibraryLoadFromFile` 加载 cubin，通过 `cudaLibraryGetKernel` 获取 `kernel_solve`、`kernel_map_idx`、`kernel_count_idx`、`get_solve_smem_size` 四个内核句柄。启动一次 `get_solve_smem_size` 内核获取动态共享内存大小，设置到 `smem_size` 成员，并通过 `cudaKernelSetAttributeForDevice` 为 `kernel_solve` 设置 `cudaFuncAttributeMaxDynamicSharedMemorySize`。

F-020: 文件 `csrc/plugin.cpp` 第357-456行，条件编译方法 `void compiled_solver::init_comm(const c10::Device &device, bool nvshmem_multiplane, bool do_nvshmem_init)`（仅 `USE_NVSHMEM` 下可用）。当 `init_comm_done` 为 true 时直接返回。当 `do_nvshmem_init` 为 true 时调用 `nvshmemx_init_attr` 初始化 NVSHMEM。通过 `sync_current_to_module` 同步三个 NVSHMEM 全局符号。根据 `nvshmem_multiplane` 决定使用 `NVSHMEM_TEAM_WORLD` 还是 `deep_ep::internode::cpu_rdma_team`。分配 internode 和 intranode 的 workload 缓冲区和信号量，通过 CUDA IPC 在节点内共享内存。输出 `n_nodes`、`node_size`、`nvshmem_multiplane` 信息。

F-021: 文件 `csrc/plugin.cpp` 第459-470行，构造函数 `compiled_solver(const std::string &resource_path, int n_group, int group_size, int dup_per_rank, int block_dim, int n_local_experts, int n_combined_experts, c10::intrusive_ptr<c10d::ProcessGroup> pg)`。初始化列表设置 `n_group`、`group_size`、`dup_per_rank`、`block_dim`、`n_experts = (n_local_experts - dup_per_rank * n_combined_experts) * group_size * n_group`、`n_local_experts`、`n_combined_experts`、`pg`。函数体调用 `prepare_module(compile_cubin(resource_path))`。

F-022: 文件 `csrc/plugin.cpp` 第491-578行，方法 `std::pair<at::Tensor, at::Tensor> compiled_solver::solve(at::Tensor local_workload, at::Tensor r2o, at::Tensor phy2log, at::Tensor avail_num)`。断言 `local_workload` 维度为 3、dtype 为 kInt32、连续存储；`r2o` 维度为 2、shape[0]==group_size、shape[1]==dup_per_rank、dtype kInt32；`phy2log` 维度为 1、size(0) 可被 n_pes 整除、dtype kInt32；`avail_num` numel==1、dtype kInt32。创建 `global_workload`（Float32，与 local_workload 同形状）和 `result`（形状 {n_group, group_size, dup_per_rank}，Float32）。通过 `cudaLaunchCooperativeKernel` 启动 `kernel_solve`（非 NVSHMEM 模式）或 `nvshmemx_collective_launch`（NVSHMEM 模式），grid 维度为 {n_group, 1, 1}，block 维度为 {block_dim, 1, 1}，动态共享内存大小为 `smem_size`。返回 `{result, global_workload}`。

F-023: 文件 `csrc/plugin.cpp` 第580-600行，方法 `std::pair<at::Tensor, at::Tensor> compiled_solver::count_idx(at::Tensor idx, int n_sms, int block_dim)`。断言 `idx` dtype kInt64、CUDA 设备、连续存储。创建 `out` 张量形状 `{n_sms, n_experts}`，dtype kInt32。通过 `cudaLaunchCooperativeKernel` 启动 `kernel_count_idx`，grid {n_sms, 1, 1}，block {block_dim, 1, 1}，共享内存大小 `(16 + n_experts) * sizeof(int)`。返回 `{out.index({-1}), out}`（最后一行是汇总结果）。

F-024: 文件 `csrc/plugin.cpp` 第602-660行，方法 `at::Tensor compiled_solver::map_idx(at::Tensor mapping_idx, at::Tensor o_weight, at::Tensor local_workload_split_by_sm, at::Tensor o2r, at::Tensor phy2log, int n_sms, int block_dim)`。断言 `mapping_idx` dtype kInt64、CUDA、连续；`o_weight` dtype kFloat32、CUDA、连续、维度 3、shape {n_group, group_size, dup_per_rank}；`o2r` dtype kInt32、CUDA、连续、维度 2、shape {group_size, dup_per_rank}；`phy2log` dtype kInt32、CUDA、连续、维度 1、size(0) == group_size * n_group * n_local_experts。创建 `mapping_idx_out`（与 mapping_idx 同形状）。通过 `cudaLaunchKernel` 启动 `kernel_map_idx`，grid {n_sms, 1, 1}，block {block_dim, 1, 1}，共享内存大小 `5 * n_logical_experts * sizeof(int)`。返回 `mapping_idx_out`。

F-025: 文件 `csrc/plugin.cpp` 第663-678行，PYBIND11_MODULE 绑定：将 `compiled_solver` 类暴露为 Python 类 `CompiledSolver`，绑定构造函数（8个参数）、`init_comm`（条件编译，3个关键字参数：device, nvshmem_multiplane, do_nvshmem_init）、`solve`（4个关键字参数：local_workload, r2o, phy2log, avail_num）、`count_idx`（3个关键字参数：idx, n_sms, block_dim）、`map_idx`（7个关键字参数：mapping_idx, o_weight, local_workload_split_by_sm, o2r, phy2log, n_sms, block_dim）。

F-026: 文件 `csrc/plugin.cpp` 第92-104行，函数 `void sync_current_to_module(cudaLibrary_t module, const char *symbol_name)`。通过 `dlopen(DEEP_EP_SO, RTLD_LAZY | RTLD_LOCAL)` 加载 deep_ep 动态库，`dlsym` 获取符号地址，`cudaGetSymbolAddress` 获取当前 CUDA context 中符号的设备地址，`cudaLibraryGetGlobal` 获取模块中符号的设备地址，然后 `cudaMemcpy(..., cudaMemcpyDeviceToDevice)` 将当前 context 的符号数据复制到模块中。

## DeepEP RT Slim 头文件（csrc/deepep_rt_slim.h）

F-027: 文件 `csrc/deepep_rt_slim.h` 第1-10行，头文件内容：`#include <nvshmem.h>` 和 `#include <nvshmemx.h>`，声明命名空间 `deep_ep::internode`，其中包含 `extern nvshmem_team_t cpu_rdma_team;`。

## CUDA 内核模板（lplb/resources/csrc-tmpl/minilp.cu）

F-028: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第21-26行，编译期宏默认值：`GROUP_SIZE` 默认 8，`DUP_PER_RANK` 默认 2，`SM_Ver` 默认 900，`BLOCK_DIM` 默认 128。注释标注为 "Default parameters for Cube8P2E on Hopper"。

F-029: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第28-39行，模板函数 `template <int N> __device__ void gaussian_elimination_solve(float a[N][N], float b[N])`。使用 cuSolverDx 配置：`Size<N>()`、`Function<cusolverdx::function::posv>()`（Cholesky 求解正定线性方程组）、`Arrangement<row_major, row_major>()`、`SM<SM_Ver>()`、`Block()`、`FillMode<lower>()`、`BlockDim<BLOCK_DIM>()`。调用 `.execute(a[0], b, &status)` 求解。

F-030: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第41-49行，模板函数 `template <int M, int N, int K> __device__ void matmulNT(float *a, float *b, float *c)`。使用 cublasDx 配置：`Size<M, N, K>()`、`Function<cublasdx::function::MM>()`、`Arrangement<row_major, col_major>()`（A 行主序、B 列主序，即 C = A * B^T）、`SM<SM_Ver>()`、`Block()`、`BlockDim<BLOCK_DIM>()`。调用 `.execute(1.f, a, b, 0.f, c)`。

F-031: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第51-59行，模板函数 `template <int M, int N, int K> __device__ void matmulNN(float *a, float *b, float *c)`。使用 cublasDx 配置：`Size<M, N, K>()`、`Function<cublasdx::function::MM>()`、`Arrangement<row_major, row_major>()`（C = A * B）、`SM<SM_Ver>()`、`Block()`、`BlockDim<BLOCK_DIM>()`。调用 `.execute(1.f, a, b, 0.f, c)`。

F-032: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第61-62行，编译期常量：`constexpr int NC = GROUP_SIZE + GROUP_SIZE * DUP_PER_RANK`（约束数量），`constexpr int NV = GROUP_SIZE * DUP_PER_RANK * 2 + GROUP_SIZE + 2`（变量数量）。

F-033: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第64-77行，共享内存结构体 `struct smem_variables`，成员包括：`float dup_workload[GROUP_SIZE][DUP_PER_RANK]`、`float b[NC]`、`float a[NC][NV]`、`float c[NV]`、`float ax2[NC][NV]`、`float ax2a[NC][NC]`、`float x[NV]`、`float ax2c[NC]`、`float r[NV]`、`float d[NV]`、`float alpha`、`bool avail_flag`。

F-034: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第79-81行，全局内核 `extern "C" __global__ void get_solve_smem_size(int *size_output)`，将 `sizeof(smem_variables)` 写入 `*size_output`。

F-035: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第83-402行，全局内核 `extern "C" __global__ void kernel_solve(const int *workload, float *global_workload, const int *r2o, const int *phy2log, int n_experts_per_var, int n_experts_fixed, int *avail_num, float *result, ...)`。参数还包括 NVSHMEM 条件编译参数：`float *workload_buf_inter`、`uint64_t *workload_sig_inter`、`float **workload_buf_intra`、`cuda::atomic<uint32_t, cuda::thread_scope_system> **workload_sig_intra`、`nvshmem_team_t internode_team`、`int self_device`、`int node_size`。内核逻辑：(1) NVSHMEM 模式下进行跨节点 allreduce（putmem_signal_nbi + signal_wait_until）和节点内 allreduce（IPC + atomic signal），非 NVSHMEM 模式下仅做归一化缩放；(2) 计算 `dup_workload`（冗余专家组负载）；(3) 构建 LP 约束矩阵 `a` 和右端向量 `b`，包含 GROUP_SIZE 个负载约束和 GROUP_SIZE*DUP_PER_RANK 个副本分配约束，以及松弛变量、最大值变量和 Big M 人工变量列；(4) 设置目标函数系数 `c`（最大值变量系数 1，人工变量系数 1000）；(5) 执行 5 步内点法迭代：计算 ax2 = a * x^2、ax2a = ax2 @ a^T、ax2c = ax2 @ c、调用 gaussian_elimination_solve 求解、计算残差 r、计算步长 d 和 alpha、更新 x；(6) 计算残差判断可行（`d_max < 0.1 && 0 <= x[NV-1] && x[NV-1] < 1e-4 && max_residual < 0.05`），可行则输出 x 的前 GROUP_SIZE*DUP_PER_RANK 个分量到 result，不可行则输出 0.5。

F-036: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第404-408行，设备函数 `__device__ int split_and_align(int n, int par_rank, int par_size, int align)`。计算 `n_per_rank = ceil(n / par_size)` 并对齐到 `align`，返回 `min(n, n_per_rank * par_rank)`，将 n 个元素按 par_size 份切分并对齐。

F-037: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第410-443行，全局内核 `extern "C" __global__ void kernel_count_idx(const long *idx, const int n_elements, const int n_experts, int *counts)`。使用共享内存 `smem_buffer`（前16个 int 为偏移区，后续为 smem_counts）。每个 block 处理 `[start, end)` 范围的 idx 元素，使用 atomicAdd 在共享内存中计数。同步后将 smem_counts 写入全局 counts 的对应行，然后通过 grid-wide sync 和 warp 级前缀和累加各 SM 的计数结果。

F-038: 文件 `lplb/resources/csrc-tmpl/minilp.cu` 第445-515行，全局内核 `extern "C" __global__ void kernel_map_idx(const long *mapping_idx, const float *o_weight, const int *local_workload_by_sm, const int *o2r, const int *phy2log, const int n_elements, const int n_group, const int n_combined_experts, const int n_local_experts, long *mapping_idx_out)`。共享内存包含 smem_total_count、smem_expected_count、smem_current_count、smem_log2r（每个逻辑专家两个槽位）。初始化阶段将原始专家和冗余专家映射写入共享内存。主循环中对每个 idx 使用 atomicAdd 递增当前计数，通过 `(computed_count * 499 + 41) % smem_total_count[idx]` 哈希决定分配到原始还是副本，阈值为 `smem_expected_count[logical_expert]`（即 o_weight * total_count）。idx=-1 映射为 -1。

## 拓扑配置（tests/utils.py）

F-039: 文件 `tests/utils.py` 第97-102行，常量 `CUBE_8P2E = torch.tensor([[3,0,1,2,7,4,5,6],[6,7,4,5,0,1,2,3]]).T`，形状 (8, 2)，表示 8 个 rank、每个 rank 2 个冗余专家的 Cube 拓扑。

F-040: 文件 `tests/utils.py` 第103-107行，常量 `RING_8P = torch.tensor([[1,2,3,4,5,6,7,0]]).T`，形状 (8, 1)，表示 8 个 rank、每个 rank 1 个冗余专家的 Ring 拓扑。

F-041: 文件 `tests/utils.py` 第108-113行，常量 `HYPERCUBE_16P2E = torch.tensor([[3,0,1,2,7,4,5,6,11,8,9,10,15,12,13,14],[12,13,14,15,0,1,2,3,4,5,6,7,8,9,10,11]]).T`，形状 (16, 2)，表示 16 个 rank、每个 rank 2 个冗余专家的 Hypercube 拓扑。

F-042: 文件 `tests/utils.py` 第116-119行，函数 `torus_2d(m: int, n: int) -> torch.Tensor`，返回形状 (m*n, 2) 的张量，第 i*m+j 个元素为 `[(i+1)%m*n+j, i*n+(j+1)%n]`，表示 m×n 二维 Torus 拓扑中每个 rank 的两个冗余邻居。

## 测试文件

F-043: 文件 `tests/test_solve.py` 第13-23行，`test_planner_solve` 的参数化配置包含6组测试用例：(CUBE_8P2E, 256, 32, 2, True, 1.07)、(CUBE_8P2E, 256, 32, 4, False, 1.07)、(CUBE_8P2E, 256, 64, 2, True, 1.1)、(RING_8P, 256, 32, 1, True, 1.07)、(HYPERCUBE_16P2E, 256, 16, 2, True, 1.03)、(torus_2d(8,4), 256, 32, 2, False, 1.01)。

F-044: 文件 `tests/test_solve.py` 第24-89行，函数 `test_planner_solve(r2o, n_logical_experts, ep_size, n_redundants_per_rank, with_reorder, tolerance)`。验证 `avail_counter == planner.n_group`，并计算负载均衡系数 `actual_workload.max() / actual_workload.mean()`，断言其小于 tolerance。

F-045: 文件 `tests/test_idx_processing.py` 第12-48行，函数 `test_count_workload(r2o, n_logical_experts, ep_size, n_redundants_per_rank)`。验证返回的 workload 形状为 (n_logical_experts,)、最小值 >= 0、总和等于 (idx != -1).sum()，并与 torch 的 scatter_add 实现对比完全一致。

F-046: 文件 `tests/test_idx_processing.py` 第55-138行，函数 `test_weighted_select_target(r2o, n_logical_experts, ep_size, n_redundants_per_rank)`。验证 mapped_idx 形状与 idx 相同、值范围 [-1, n_routed_experts)、-1 映射保持一致、每个映射结果都在 log2phy 的两个槽位之一、权重分配误差小于 5e-2。
