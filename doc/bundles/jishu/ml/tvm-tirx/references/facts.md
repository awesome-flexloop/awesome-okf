---
type: Facts
title: tvm-tirx 事实清单（F-001 ~ F-135）
description: 从两代 TIRx 的知乎专栏、Apache 官方博客、apache/tvm-tirx 与 apache/tvm 仓库、官方文档站与 PyPI 采集的编号事实，逐条标注来源与置信等级
tags: [tvm-tirx, facts, 事实清单, 信源, 核验]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: zhihu-article
    resource: https://zhuanlan.zhihu.com/p/2101651274798196721
  - id: apache-blog
    resource: https://tvm.apache.org/2026/11/03/rethinking-abstractions-in-the-agentic-era
  - id: tvm-tirx-repo
    resource: https://github.com/apache/tvm-tirx
  - id: tvm-tirx-docs
    resource: https://tvm.apache.org/tirx/
  - id: pypi
    resource: https://pypi.org/project/apache-tvm-tirx/
---

# tvm-tirx 事实清单

> 采集日 2026-11-09。每条事实后标注来源代码与置信等级：
> **[A]** 官方一手（仓库/文档/PyPI/官方博客）；**[B]** 作者专栏（与官方博客同源）；**[C]** 本次核验观察（非源文陈述）；**[D]** 未能核验的主张。

## 1. 仓库与元信息

- **F-001** [A] 仓库 `apache/tvm-tirx` 存在，描述为 *Open ML Compiler Foundation for the Agentic Era*，许可证 Apache-2.0，默认分支 `main`，创建时间 `2026-10-13T22:07:20Z`（GitHub API）。
- **F-002** [A] README 标题为 *TVM TIRx: ML Compiler Foundation for the Agentic Era*（README.md）。
- **F-003** [A] README 表述其信念：未来所有 GPU kernel 都将由 AI Agent 开发、优化与验证（README.md）。
- **F-004** [A] README 列出五项特征：最小稳定核心 IR、可预测工具、动态扩展、Python/C++/Rust 一等跨语言支持、构建于稳定工具链（README.md）。
- **F-041** [A] 仓库根目录包含 `include/`、`src/`、`python/`、`rust/`、`docs/`、`examples/`、`3rdparty/`、`AGENTS.md`、`pyproject.toml`、`CMakeLists.txt`、`LICENSE`、`NOTICE`（GitHub contents API）。
- **F-045** [A] 仓库 topics 为 `compiler`、`gpu`、`tirx`（GitHub API）。
- **F-062** [A] 仓库根目录存在 `AGENTS.md`，即项目自身提供了面向 Agent 的协作入口文件（GitHub contents API）。
- **F-051** [A] 文档站设有 *Extending TIRx: everything is a plugin* 专章（文档站导航）。
- **F-052** [A] 文档站设有 *CUDA Backend Development*、*Build from Source*、*Reproduce CI/CD*、*Release Process* 等开发者手册页面（文档站导航）。

## 2. 版本、安装与环境

- **F-005** [A] PyPI 包名 `apache-tvm-tirx`，最新版本 `0.1.0b1`，`requires-python >= 3.10`（PyPI JSON API）。
- **F-006** [A] 官方博客在跨语言一节把 Rust 标为 **work in progress**（官方博客）。
- **F-007** [A] Quick Start 前置要求：Python 3.10+、PyTorch、CUDA 13+（仅 CUDA 示例）（文档站 Quick Start）。
- **F-047** [A] 安装命令为 `pip install --upgrade --force-reinstall apache-tvm-tirx`；CUDA 额外依赖为 `apache-tvm-tirx[cuda]`（文档站首页与 Quick Start）。
- **F-048** [A] Quick Start 声明其全部代码位于仓库 `examples/quick_start` 目录（文档站 Quick Start）。

## 3. 文章与官方博客

- **F-039** [B] 知乎专栏文章标题《构建 Agent 时代的机器学习编译基础层》，作者陈天奇，编辑于 2026-11-05 20:58，收录于专栏 `tvm`；页面显示 452 人赞同（采集时点值）。
- **F-043** [A] Apache TVM 官方博客文章标题 *Rethinking Abstractions in the Agentic Era: Towards a DSL and Compiler Foundation for Agentic Kernel Development*，发布日期 2026-11-03，署名 Apache TVM Community。
- **F-053** [A] 官方博客致谢段说明：文章由人类撰写，GenAI 模型协助语法与风格编辑。
- **F-016** [B] 文章对「是否还需要编译器」的回答是「编译器本身依然重要，但必须以不一样的形态出现」。
- **F-055** [A] 官方博客以第一性问题开篇：*Do We Still Need Compilers at All?*
- **F-056** [A] 官方博客表述：未来可能不再需要「真正编译任何东西」的编译器，但仍需要编译基础设施来理解与验证程序。
- **F-017** [A] 官方博客给出两项刚性需求：**分析**（结构化表示 + 高效算法，尽早发现错误）与**验证**（独立于 Agent 判断，需要精确定义的语义）。
- **F-018** [A] 官方博客提到可用 Lean 等形式化 IR 语义做正确性证明检查，并提到已构建 checkers 做早期检查。
- **F-019** [A] 官方博客点名七项自动化 GPU kernel 工作：KernelAgent、CUDA Agent、Cursor’s multi-agent system、CAKE、TIRx Harness、KDAgent、EAT。
- **F-020** [A] 官方博客引用两篇讨论：DeepSeek 工程师 Shengyu Liu 的《I Have No Choice but to Bury My Talent in Yesterday》，以及 Stanford 的 *Retire the Abstractions*。
- **F-038** [B] 中文文章含「今年是 Agent 元年」「Agent 开发 kernel 的水平超越人类基本是必然」等判断性表述（属作者判断，非可核验事实）。
- **F-021** [B] 中文文章说明路线：去年介绍 TVM-FFI；TVM-FFI 发布后持续模块化 TVM 核心；一年后拆分并面向 Agent 重新设计。
- **F-030** [D] 中文文章称其「应该是世界上第一个比较完美支持 Rust 和 C++ 直接混动开发机器学习编译器的尝试」；「世界第一」无法穷举验证。
- **F-031** [B] 中文文章指出常见 visitor pattern 需要提前知道所有可能类型节点，这也是 Rust enum 与 LLVM/MLIR 需要静态编译的原因。
- **F-022** [A] 官方博客说明 `tirx.compile` **不施加额外启发式优化**，程序直接交给 LLVM 生成 CPU 代码。
- **F-023** [A] 官方博客说明：Agent 迭代速度受开发环境限制；改代码→重编译→跑测试的循环中，构建与测试占比会上升，构建缓存只能部分缓解。文中演示形状约束错误：`expected A.shape[0] to be divisible by 2`。
- **F-024** [A] 官方博客提出按稳定性与变化速率分层：kernel 可在分钟级生成并丢弃，底层则需要稳定与更近的人类监督。
- **F-025** [A] 官方博客强调与成熟工具链集成（CUDA 与 host LLVM 的基础代码生成），而非在自有流水线重造一切。
- **F-026** [A] 官方博客说明：编译每个阶段都可打印为 Python 脚本语法，供 Agent 与开发者检查中间程序。
- **F-046** [A] 官方博客称上一次社区工作已能用 Claude/Codex 产出生产级 B200 kernel 并显著优于既有基线（源文主张，本次未独立复现）。
- **F-044** [A] 官方博客文末链接到 TIRx 文档与 `apache/tvm-tirx` 仓库。

## 4. IR 与工具

- **F-009** [A] 文档 IR 指南：TIRx 的主要设计目标之一是让开发者与 Agent 访问编译的每个阶段，而不只是输入输出；程序表示为 IR 节点树。
- **F-008** [A] Quick Start 示例：`T.dynamic("n")` 声明动态长度；CPU 版本用 `for i in range(n)`，CUDA 版本用 `T.device_entry` + `block_idx`/`thread_idx` + 越界判断。
- **F-010** [A] IR 命名空间分三层：`ir`（通用节点）、`ir.prim`（标量/向量原语）、`tirx`（张量程序特有）。
- **F-011** [A] IR 对象不可变；分析读取树，变换构造新树并共享未变部分。
- **F-049** [A] IR 类层级根为 `ffi.Object`，下含 `ir.Expr`、`ir.Type`、`ir.Stmt`、`ir.Location`、`ir.IRModule`；`ir.BaseFunc` 的子类是 `tirx.Function`。
- **F-013** [A] 基础层提供的可预测工具包括：TVM-FFI 桥接生成、符号整数分析、结构遍历与映射、CUDA/host LLVM 最小代码生成（README 与博客）。
- **F-050** [A] 符号整数分析支持符号约束上下文与更强的 Z3 证明（官方博客，源自 TileLang 社区反馈）。
- **F-029** [A] 官方博客说明每个 AST 节点都是 TVM-FFI 支撑的跨语言对象，可从 Python、C++、Rust 直接访问。
- **F-063** [A] 文档 IR 指南：`ir.format_tree` 可把 IR 对象与字段显示为文本树，支持 `expand` / `fold` 控制显示粒度。
- **F-064** [A] 官方博客与 Quick Start：`tvm_ffi.structural_map` 遍历程序并对每个匹配节点调用函数替换，用于结构特化等改写。

## 5. 跨语言与扩展

- **F-012** [A] 官方博客解释跨语言动机：实验性分析偏好 Python（可复用 NumPy/PyTorch），高频 Pass 偏好 C++/Rust；单语言重写会浪费 token。
- **F-014** [A] 扩展入口：新类型（可继承类型节点，如 `tirx.TensorMapType` 支持 TMA）、新算子（`Call` 或 `RegionStmt`，如 `device_entry`、`T.ptx.add.rn.f32`）。
- **F-015** [A] 类型与算子注册通过按字符串键索引的运行时表；扩展可作为下游包存在，无需重编译或重新打包原项目。
- **F-027** [A] 扩展指南给出 Python 与 Rust 两版同名包（`my_ext`）；Python 无需构建，适合试用；Rust 快且内存安全，适合 Agent 探索；示例安装命令为 `uv pip install --no-deps ./examples/extension_guides/python`。
- **F-058** [A] 文档站编程指南覆盖元编程三类需求：被捕获值参数化、可复用代码片段、编译期特化。
- **F-059** [A] 文档站编程指南覆盖控制流：条件、循环、线程提前退出。
- **F-060** [A] 文档站编程指南覆盖数据布局：张量元素到线程与内存的映射。
- **F-036** [A] 文档站提供 *Profiling with IKET* 指南。
- **F-061** [A] Quick Start 推荐 *Modern GPU Programming for MLSys* 一书作为用 TIRx 写 GPU kernel 的学习材料。

## 6. 编程模型

- **F-032** [A] 编程指南说明设计哲学：TIRx 选择更低、更显式的边界；新指令/内存空间/协作模式常先于编译器支持出现；Agent 偏好直接可预测的行为。
- **F-033** [A] TIRx 程序读作结构化 native kernel：循环、分支、张量、同步、流水线状态、后端 intrinsic、硬件角色都直接写出。
- **F-034** [A] 便利层由三个构造组成：执行域（execution scope）、张量布局（tensor layout）、tile 算子派发（tile operation dispatch）；该层可选，任何位置可回落到原生原语。
- **F-035** [A] 编程指南目录覆盖：CUDA 函数与启动、控制流、类型/张量/内存、元编程、CUDA/PTX 接口、数据布局、tile 算子、编译与检查、IKET 剖析。

## 7. 编译、部署与运行时

- **F-028** [A] Quick Start：`export_library` 导出标准 TVM-FFI 模块；运行只需 `libtvm_runtime.so` / `libtvm_runtime_cuda.so`，各自小于 1 MB；C++ 通过 `Module::LoadFromFile` 与 `GetFunction` 加载；kernel 要求张量 64 字节对齐。
- **F-037** [A] Quick Start 排错：CUDA 编译报 `requires an explicit backend_config arch or Target arch` 时，通常是找不到 `libcudart.so.13`；需安装 CUDA 13 版 PyTorch 或 CUDA 13 toolkit 并配置 `LD_LIBRARY_PATH`。
- **F-057** [A] 官方博客说明 TIRx 提供生成符合 TVM-FFI ABI 的 host 代码工具，尤其用于高效的编译期张量检查。

## 8. 核验观察与未证实项

- **F-040** [C] 针对**第二代**（2026-11 中文文章、官方博客、README、独立文档站），本次核验未找到「相对基线编译器/纯 Agent 流程」的对照基准或性能数据；第一代基准见 F-081~F-086，但不可外推到第二代。
- **F-042** [C] 本次核验未逐篇核验 F-019 点名的七项 Agent 工作；仅确认其被官方博客点名。
- **F-054** [C] 本次核验未对 tvm-tirx 做独立安装与运行实测；示例代码以官方文档为准，beta 版本 API 可能变化。

## 9. 第一代 TIRx：2026-06 在 Apache TVM 内发布

- **F-065** [A] Apache TVM 官方博客 *TIRx: An Open Compiler Stack for Evolving Frontier ML Kernels*，发布日期 2026-06-22，署名 Apache TVM Community（官方博客）。
- **F-066** [A] 第一代 TIRx 的定位：构建在 Apache TVM 之上的开源、硬件原生 ML kernel DSL 与编译器，面向 GPU 与专用 AI accelerator，并为后续硬件世代预留扩展（官方博客）。
- **F-067** [A] 同一套设计服务三类用户：专家手写调优的 production kernel、Agent 生成 kernel、megakernel 系统（官方博客）。
- **F-068** [A] 首发材料包含 PyPI wheel 与 Python frontend，支持 `@T.jit` / `@T.prim_func` 风格编写，提供 parser、IR builder 与 Python API（官方博客）。
- **F-069** [A] 首发 kernel library 与 benchmark 覆盖 FP16/BF16 GEMM、FlashAttention-4 forward、Blackwell GPU 上的低精度算子（官方博客）。
- **F-070** [A] 配套开放课程 *Modern GPU Programming for ML Systems*，曾作为 CMU machine learning systems 课程的一部分讲授，并用 TIRx 教学生在 Blackwell 上写高性能算子（官方博客）。
- **F-071** [A] 第一代首发链接：仓库 `apache/tvm`、文档 `tvm.apache.org/docs/tirx/overview.html`、PyPI `apache-tvm` 0.25.0、kernel library `mlc-ai/tirx-kernels`、课程 `mlc.ai/modern-gpu-programming-for-mlsys/`（官方博客）。
- **F-072** [A] 设计围绕三件事：orchestration 留在硬件原生源码；反复出现的 tile primitives 暴露给编译器；新硬件先作为 intrinsic、稳定后晋升为 tile primitive（官方博客）。
- **F-073** [A] 第一代 TIRx 的抽象层位于 TileLang 之下；官方表示正与 TileLang 社区合作，把 TIRx 作为新的最小基础（中文文章明确写「取代原 TensorIR」）（官方博客 + 知乎文章）。
- **F-074** [A] Execution scope：未限定的 `Tx.*` 为 thread 粒度，`Tx.wg.*` 为 warpgroup 粒度，`T.ptx.elect_sync()` 等谓词可收窄到单个 issuing thread（官方博客）。
- **F-075** [A] Tensor layout 采用 storage-first 接口：tile 可位于 global memory、shared memory、registers、tensor memory 或 accelerator SRAM；用户声明存储位置与元素在 lane/warp/register 上的分布（官方博客）。
- **F-076** [A] Tile primitive dispatch 依据 operand layouts、execution scope、target 或显式 `dispatch=` 选择实现：global→shared 为 TMA，shared→register 为 ldmatrix（一定条件下），tensor memory→register 为 `tcgen05.ld`；矩阵乘为 WGMMA、tcgen05 或 systolic-array 指令（官方博客）。
- **F-077** [A] Layout 模型由 D（Shard）、R（Replica）、O（Offset）三部分构成；使用具名硬件轴（laneid、warpid、tid_in_wg、Col、Lane、P、F、pid）；从设计上支持非 2 的幂等一般形状（官方博客）。
- **F-078** [A] Layout 是存储契约而非任务切分/循环变换接口；与 CuTe 的「layout 作为可编程划分接口」形成明确边界（官方博客）。
- **F-079** [A] 具体示例：逻辑坐标 (3, 9) 的元素 57 映射到 `6@warpid, 12@laneid, 1@m`，经 replica 得到两个 owner：`warpid=6 laneid=12` 与 `warpid=10 laneid=12`（官方博客）。
- **F-080** [A] 轻量编译器后端：解析后得到「硬件原生 IR + 未解析的 tile primitive calls」，逐调用局部 dispatch 为原生 IR 片段，随后直接翻译为 CUDA C++/PTX；自动 warp specialization、layout 推断、调度变换、自动 tensor 分配、流水线搜索、cost-model 调优均为可选层（官方博客）。
- **F-081** [A] 性能实验：54 个配置，4×NVIDIA B200（SM100），driver 595.58.03，CUDA 13.2，PyTorch 2.12.0+cu132；Proton 计时（warmup 100，repeat 30，5 轮平均）（官方博客）。
- **F-082** [A] Dense GEMM：BF16 8192³ 达 1517 TFLOPS，FP16 8192³ 达 1404 TFLOPS，分别为最佳 baseline 的 0.96× 与 0.95×（官方博客）。
- **F-083** [A] FP8 blockwise GEMM：4096×4096×7168 上 2895 TFLOPS，为 DeepGEMM 的 0.99×（官方博客）。
- **F-084** [A] NVFP4 8192³：5930 TFLOPS，距最佳 baseline 不到 2%（官方博客）。
- **F-085** [A] FlashAttention-4：s4096/s8192、32 heads、non-causal 下 1340/1328 TFLOPS，对 CuTeDSL 的 1330/1327（0.99×/1.00×）；causal s4096 为 1236 TFLOPS（0.97×）（官方博客）。
- **F-086** [A] 32 个 FA4 配置中，non-causal 吞吐 580–1358 TFLOPS（中位 1277），causal 277–1326 TFLOPS（中位 1075）；s1024 causal 433 TFLOPS 归因于 S² FLOP 缩放（官方博客）。
- **F-087** [A] Megakernel 方向：未来算子库可暴露 device-side tile tasks；TIRx task 以 compiler IR 形式存在，可被上层 megakernel compiler 重新分配 smem、重命名 barrier、重排 warp role、交织流水线；TIRx 本身不是完整 megakernel compiler（官方博客）。
- **F-088** [A] Event Tensor（MLSys ’26，arXiv 2604.13327）是在 TIRx 之上探索动态 megakernel 的工作；官方计划在后续 release 推进集成（官方博客）。
- **F-089** [A] Agentic kernel 编程需要两层支持：编译器可工具化（构造/检查/遍历/改写/分析 IR），以及 DSL 暴露结构化搜索空间；后者被分为 L1–L4 四级（官方博客）。
- **F-090** [A] L1 = Agent 局部调优专家 kernel；L2 = 从人类定义的结构化搜索空间采样后局部调优；L3 = 根据人类 meta-rules 生成或修改搜索空间；L4 = 从硬件文档、primitive 实验与编译器反馈中 bootstrap 搜索空间（官方博客）。
- **F-091** [A] 结构化 TIRx 程序可在编译/运行前提供更密集的反馈信号：well-formed、同步合法性、race-free、数值模拟、资源/性能模型（官方博客）。
- **F-092** [A] 致谢与思想来源：构建在 TVM 基础设施之上，设计受 NumPy、CuTe、Triton、ThunderKittens、TileLang 影响；感谢 FlashInfer、FlashInfer-Bench、TileLang 团队与 Apache TVM 社区（官方博客）。
- **F-093** [B] 中文文章《TIRx：面向持续演进的前沿 ML Kernel 的开放编译器栈》，作者侯博涵，编辑于 2026-06-23 10:18，首发于专栏「TVM and TensorIR」并收录于「tvm」；正文约 14,623 字符（浏览器提取）。
- **F-094** [A] 中文文章明确 TIRx 读作 “tier-ex”（知乎文章）。
- **F-095** [A] 第一代 PyPI 包为 `apache-tvm` 0.25.0（`pip install apache-tvm==0.25.0`），与第二代的 `apache-tvm-tirx` 0.1.0b1 是两个不同包（官方博客 + PyPI）。
- **F-096** [A] 第一代文档位于 `tvm.apache.org/docs/tirx/overview.html`，第二代独立文档位于 `tvm.apache.org/tirx/`，路径不同（官方博客 + 文档站）。

## 10. 两代关系与核验观察（2026-11-09 补充）

- **F-097** [C] 第一代（2026-06，`apache-tvm` 0.25.0，`@T.jit`/`@T.prim_func`、`Tx.*` 命名空间）与第二代（2026-11，`apache-tvm-tirx` 0.1.0b1，`@T.function`、`tvm_tirx.script.tirx`）在包名、文档路径、API 与 IR 对象集合上均不同，示例不可混用。
- **F-098** [C] 第二代官方博客称「拆分并面向 Agent 重新设计」，与第一代「构建在 Apache TVM 之上」构成演进关系；两代之间的源码级对应关系未在本次核验中逐文件比对。
- **F-099** [C] 第一代 54 配置性能数据（F-081~F-086）测于 `apache-tvm` 0.25.0 与 B200，不能外推到第二代 `apache-tvm-tirx` 0.1.0b1；本次未独立复现。

## 11. 源码仓核验（本地检出 cdc7a377，2026-11-08）

- **F-100** [A] 本地检出 `d:\spaces\SpecWeave\external\dev\libs\TIRx\tvm-tirx` 的 HEAD 为 `cdc7a37793e449917faa2dcaa66df1bb61df2ba5`，提交日期 2026-11-08，提交信息以 `[Rust] Bump tvm-ffi ...` 开头，工作树干净（`git rev-parse`/`git log`/`git status`）。
- **F-101** [A] 仓内 `AGENTS.md` 将项目定义为 "a compiler foundation for development of ML compilers and agentic compiler harnesses"，并给出目录布局、uv 构建、C++/Python/Rust 测试、pre-commit 与 CI 命令。
- **F-102** [A] `include/tvm/` 下分 `ir/`、`sym/`、`tirx/`、`target/`、`runtime/`、`codegen/`、`backend/`；`src/` 为对应 C++ 实现（目录清单）。
- **F-103** [A] Python 模块职责：`ir`（共享表达式/类型/语句/函数/模块/位置）、`tirx`（张量程序、layout、分析、lowering）、`sym`（化简与符号推理）、`script`（解析/打印 + 方言 builder）、`backend`（目标相关算子/变换/codegen/runtime）、`runtime` 与 TVM-FFI（对象/反射/packed function）。
- **F-104** [A] Rust crate `rust/tvm-tirx`：IR 对象定义由 `tvm-ffi-stubgen` 从 `libtvm_tirx_compiler` 的反射生成（begin/end 标记内）；`#[repr(C)]` 与 C++ 字段偏移一致，编译期检查 size/alignment；编辑安装可产出 `libtvm_tirx_rust`，`import tvm_tirx` 时加载并注册静态初始化块中的算子/类型。
- **F-105** [A] `docs/` 使用 Sphinx + RST + autosummary，构建命令 `sphinx -b html -W docs docs/_build/html`（警告即错误）。
- **F-106** [A] `cmake/modules/` 含 `CUDA.cmake`、`LLVM.cmake`、`Metal.cmake`、`ROCM.cmake`、`Vulkan.cmake`、`OpenCL.cmake`、`OpenMP.cmake`、`Rust.cmake`、`Git.cmake`、`Logging.cmake` 与 `contrib/Z3.cmake`。
- **F-107** [A] `3rdparty/tvm-ffi/` 是 TVM-FFI 子模块，提供对象、反射、packed function、ABI 与运行时。
- **F-108** [A] CI：GitHub Actions 跑 macOS/Windows 检查与独立 lint；Jenkins 用 `ci/jenkins/jenkinsfile.groovy` 并行 ARM/GPU/EXTRA 分支；GPU 构建一个 CUDA wheel 供 CPU 测试、GPU 测试与文档使用；EXTRA 构建备选 GPU 后端但不跑测试。
- **F-109** [A] `python/tvm_tirx/tirx/layout.py` 定义 `Layout`、`TileLayout`、`ComposeLayout`、`Axis`、`Iter`，以及 `S = _SpecBuilder("shard")`、`R = _SpecBuilder("replica")`。
- **F-110** [A] `compilation_pipeline.py` 的默认顺序：bind target → `TileDispatch` →（可选 `PrintIR`）→ `LowerTensorLayouts` → `StmtSimplify` → `FlattenTensor` → `NarrowDataType(32)` → `VectorizeLoop` → `UnrollLoop` → `StmtSimplify` → `CommonSubexprElim` → `VerifyMemory` → `LowerThreadAllreduce` → finalize；`prepare_only=True` 可停在 finalize 前；`tirx.disable_vectorize`、`tirx.disable_cse_tir` 可关闭对应 pass。
- **F-111** [A] `codegen/executable.py`：`Executable` 支持 `jit()`（把未可运行的 c/static_library 模块编译链接成可加载模块）、`__call__`、`__getitem__`、`export_library()`；运行时只读模式下调用 `export_library` 会抛 `RuntimeError`。
- **F-112** [A] `backend/_autoload_backends.py` 的内置后端元组为 `cuda, metal, rocm, trn, opencl, vulkan, webgpu, hexagon, adreno, rust`；并扫描 `tvm_tirx.backends` entry point 自动加载第三方后端；`TVM_TIRX_DEVICE_BACKEND_AUTOLOAD=0` 可关闭。
- **F-113** [A] `pyproject.toml`：发行名 `apache-tvm-tirx`，版本 `0.1.0b1`，`requires-python >=3.10`，Development Status 4 - Beta，classifier 覆盖 Python 3.10–3.13。
- **F-114** [A] 构建后端为 `scikit-build-core>=0.11`；`[tool.scikit-build]` 指定 `wheel.packages = ["python/tvm_tirx"]`、`build-dir = "build"`、`install.components = ["tvm_tirx", "tvm_tirx_llvm_backend"]`。
- **F-115** [A] 运行时依赖：`apache-tvm-ffi>=0.1.15.post1`、`apache-tvm-ffi-orcjit>=0.1.3`、`ml_dtypes`、`numpy`。
- **F-116** [A] 构建期依赖含 `mlc-llvm-static[all]==23.1.1.post0` 与 `mlc-z3-static==5.3.1.post1`。
- **F-117** [A] wheel 只安装 `tvm_tirx` 与 `tvm_tirx_llvm_backend` 两个组件（`install.components`）。
- **F-118** [A] CMake 开关与默认值：`TVM_TIRX_USE_LLVM=ON`、`TVM_TIRX_USE_Z3=AUTO`、`TVM_TIRX_USE_CUDA=AUTO`、`TVM_TIRX_USE_OPENCL=OFF`、`TVM_TIRX_USE_VULKAN=OFF`、`TVM_TIRX_USE_ROCM=OFF`、`TVM_TIRX_USE_METAL=OFF`、`TVM_TIRX_USE_RUST=AUTO`、`TVM_TIRX_USE_OPENMP=OFF`、`TVM_TIRX_BUILD_TESTS=OFF`。
- **F-119** [A] 文档参考页覆盖 `backend.cuda`、`backend.metal`、`backend.opencl`、`backend.rocm`、`backend.vulkan`、`backend.webgpu`、`backend.hexagon`、`backend.adreno`、`backend.trn`、`backend.rust`，以及 `tirx.layout`、`tirx.tile`、`tirx.compilation_pipeline`。
- **F-120** [A] CMake 目标：`tvm_runtime`（shared）、`tvm_runtime_static`（static）、`tvm_tirx_compiler`（shared）；设备运行时追加到 `TVM_RUNTIME_BACKEND_LIBS`，LLVM 后端单独为 `TVM_LLVM_BACKEND_LIB`；另有 `runtime` 自定义目标。
- **F-121** [A] `docs/programming_guides/compiling.rst`：`Target({"kind":"cuda","arch":"sm_75","backend_config":{"cuda":{"nvrtc":["--use_fast_math"]}}})`；CUDA 默认 NVRTC；`device_entry(..., backend_config=...)` 覆盖 target 且参数列表整体替换；`script()`/`show()` 打印 IR，`ex.mod.imports[0].inspect_source("cuda")` 查看生成 CUDA。
- **F-122** [A] 文档 `tile/index.rst`：TIRx 提供两个 CUDA tile 操作 `T.cuda.tile.apply` 与 `T.cuda.tile.ewise`；指南覆盖 data movement、arithmetic、async copies、TMA、warp matrix、Blackwell tensor cores。
- **F-123** [A] `examples/quick_start/add_one_cpu.py` 与 `add_one_cuda.py` 实际使用 `@T.function`、`T.dynamic`、`T.device_entry`、`T.cuda.LaunchConfig`、`tvm_tirx.compile`、`export_library`，与文档一致。
- **F-124** [A] `docs/programming_guides/data_layout.rst`：`TileLayout(S[(32, 4) : (1 @ laneid, 1)])`；`apply(3, 2, shape=(32, 4))` 返回 `{"laneid": 3, "m": 2}`；`T.alloc_local(..., layout=...)` 挂载布局；`fragment.view(4, layout="default")` 暴露本地视图。
- **F-125** [A] `tvm_ffi.structural_map` 在 `examples/quick_start/inspect_and_transform.py`、`examples/ir_guides/structural_utilities.py` 与扩展示例中使用；`tvm_tirx.tirx.structural.py` 另有 `structural_map_with_constraint_context`。
- **F-126** [A] `pyproject.toml` 可选依赖：`torch`、`cuda`（`cuda-bindings`）、`popen-pool`（psutil/cloudpickle）、`all`；依赖组含 `build`、`torch`、`cuda`、`test`、`lint`、`dev`、`docs`。
- **F-127** [A] pytest 标记：`gpu` 与 `cuda_arch(*arches, device='cuda0')`；测试路径 `tests/`。
- **F-128** [A] `import tvm_tirx` 会在构建了 Rust crate 时加载 `libtvm_tirx_rust` 并注册其静态初始化块中的算子与类型。
- **F-129** [A] `examples/extension_guides` 同时提供 Python 与 Rust 两版同名包 `my_ext`，安装命令 `uv pip install --no-deps ./examples/extension_guides/python`，运行 `python examples/extension_guides/run_example.py`。
- **F-130** [A] 仓内 `AGENTS.md` 是项目自带的智能体入口；`3rdparty/tvm-ffi/` 也带 `AGENTS.md` 与 `CLAUDE.md`。
- **F-131** [A] `docs/` 的 Sphinx 构建使用 `-W`（warning as error），即文档警告会阻断构建。
- **F-132** [A] `CMakeLists.txt` 定义 `tvm_tirx_option` 宏统一管理开关；`TVM_TIRX_USE_THREADS` 默认 ON、`TVM_TIRX_USE_CUSTOM_LOGGING` 默认 OFF。
- **F-133** [A] 源码含 `include/tvm/tirx/object_functor_with_constraint_context.h`、`stmt_functor_with_constraint_context.h`、`structural_mutate_with_constraint_context.h`、`structural_visit_with_constraint_context.h`，对应「带约束上下文的结构遍历/改写」。
- **F-134** [A] `python/tvm_tirx/tirx/__init__.py` 导出 `structural_map_with_constraint_context`，说明带约束的结构改写是公开 API。
- **F-135** [A] `examples/quick_start/` 还包含 `inspect_and_transform.py`、`load_add_one_cpu.py`、`load_add_one_cuda.py`、`load_cpp.cc`、`run_all_cpu.*`、`run_all_cuda.sh`，覆盖检查、变换、加载全流程。
