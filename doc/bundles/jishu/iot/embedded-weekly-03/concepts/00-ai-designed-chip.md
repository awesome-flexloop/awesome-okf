---
type: concept
title: "openTPU：让 AI agent 去设计一颗跑 AI 的芯片"
description: "openTPU 的六层执行链、位精确数值契约、Python/RTL/FPGA 分级验证、device/wall 性能口径与可迁移验证方法"
tags: [openTPU, AI芯片, 硬件设计, AI agent, 推理加速器, Kintex-7, FPGA, 位精确验证, 量化]
generated:
  by: "seven-concepts-cmd"
  at: "2026-10-13T11:14:27+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: mp-weekly-03
    resource: "https://mp.weixin.qq.com/s/yD0epaC9Xm16UVZYojqWOA"
    title: "嵌入式周报·第三期"
  - id: fanweibin-opentpu
    resource: "https://fanweibin.cn/posts/2026-10-09-opentpu-ai-accelerator-fpga-verification"
    title: "openTPU：AI 写出的加速器，怎样证明自己真的在 FPGA 上跑"
  - id: opentpu-readme-pinned
    resource: "https://github.com/FeSens/openTPU/blob/8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25/README.md"
    title: "openTPU README，固定提交 8eaa4806"
  - id: opentpu-isa-pinned
    resource: "https://github.com/FeSens/openTPU/blob/8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25/docs/isa.md"
    title: "openTPU ISA v1 数值与指令契约"
  - id: opentpu-fixmath
    resource: "https://github.com/FeSens/openTPU/commit/8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25"
    title: "数值与量化修复提交，2026-10-08"
  - id: hn-opentpu-api
    resource: "https://hacker-news.firebaseio.com/v0/item/49980715.json"
    title: "HN 讨论 49980715 官方 API，2026-10-13 观测"
---

# openTPU：让 AI agent 去设计一颗跑 AI 的芯片

openTPU 将 Python 内核、编译器、指令集、ISA 模拟器、SystemVerilog RTL 与 PCIe 板卡运行时放在同一个项目中。学习它可以沿着一次矩阵乘法，从软件表达读到数据搬运、数值规则和硬件实现（F-001、F-053～F-056）。

> **证据范围**：本文于 2026-10-13 增量学习范维斌的技术博文，并对照固定提交 `8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25` 的 README、ISA 文档和提交记录。博主报告的是 Python 层复现；项目报告的是 RTL/板卡验证与性能。本次未运行 openTPU 测试、未构建位流、未使用 FPGA，也未逐行审阅全仓源码。不同层级的证据不能互相替代。

## 项目定位与硬件

项目署名 FeSens，沿用其此前 `auto-arch-tournament` 的硬件设计探索，许可为 Apache-2.0（F-002、F-006）。它自述由 AI 开发，但公开仓库不能独立证明每一行代码的生成者。阅读时应把“AI 开发”的归属主张与可检查的工程产物分开（F-072）。

当前形态是运行在 Inspur YPCB-00338 板卡上的开放式推理加速器架构，FPGA 为 Xilinx Kintex-7 xc7k480t。它不等于已流片 ASIC，也不能由名称推断为 Google TPU 兼容实现。固定提交的 README 报告双通道 DDR3-1066、4 GiB 板载内存、133.33 MHz 核心频率与 17.1 GB/s 理论带宽（F-004、F-066）；这些是项目文档口径，本次未实测板卡。

## 六层执行链

| 层 | 输入与产物 | 阅读时需要确认的约定 |
|----|------------|----------------------|
| 模型内核 | Python `ol` 内核语言与 `@ol.jit` | attention、MLP 如何组合加载、量化和矩阵乘法 |
| 编译器 | 布局、循环、寄存器和融合后的指令 | 张量布局如何转为地址、指令与数据搬运 |
| ISA | 每条指令为 8 个 32 位字 | 编码、存储语义、数值行为是否明确 |
| ISA 模拟器 | Python 位精确参考实现 | 同一程序应写出哪些位模式 |
| RTL | SystemVerilog 电路 | 是否实现相同指令与数值契约 |
| 板卡运行时 | 位流、权重、PCIe 与观测工具 | 主机和真实设备如何加载、执行与诊断 |

六层划分来自博文，并与固定 README 的执行链对照（F-053、F-054）。`ol.load` 对应 DRAM→片上 TMEM 的 `LD`，`ol.quantize` 对应 `QACT`，`ol.dot` 对应 `MM`（F-055）。因此，布局变化会落实为可观察的数据搬运，而不是仅停留在高层张量表达式。

机器由 sequencer、DMA、矩阵单元、向量单元与量化器组成。矩阵路径使用 int8 激活及 int8/4 位权重，向量路径处理 fp32 运算，量化器再把结果压回 int8（F-056）。README 描述无 cache、无隐藏调度，数据搬运由指令表达（F-057）。这有利于从 trace 定位等待 DRAM、计算单元或指令依赖的时间，但也要求编译器与内核显式安排搬运。

Lens profiler 可记录 ISA、RTL 或板卡运行，并展示 roofline、时间线及逐指令状态（F-071）。Roofline 用算力与带宽上限帮助判断瓶颈；观测结果仍需绑定具体配置，不能凭一张图推出所有模型的性能。

## 三种参照与两类正确性

一个 token 相同并不足以证明底层运算一致：logits（词表各候选 token 的分数）已经偏移时，最大值仍可能指向同一个 token。反过来，设备与原始浮点模型存在数值差异，也不一定是硬件实现错误，量化本身就会改变输出。

| 比较 | 回答的问题 | 不能据此推出的结论 |
|------|------------|--------------------|
| 量化 golden 与原始 HF fp32 模型 | 量化带来多少模型质量偏差 | 硬件是否实现了 ISA |
| 设备与量化 golden | 设备输出是否落在约定误差范围 | 两个实现每一位都相同 |
| RTL/板卡与 ISA 模拟器 | 同程序、同配置的 token 与 logits 是否位级一致 | 量化质量等同 fp32、或任意输入均已验证 |

博文把 HF 浮点模型、ISA 模拟器和 RTL/FPGA 分为三种参照；README 进一步区分原始 fp32 与按设备权重/激活格式构造的量化 golden（F-058、F-059）。Golden 是用于对照的参考计算，不必天然与设备逐位一致；ISA 模拟器则承担精确设备行为参考的角色。

固定版本 `tools/validate.py` 在相同上下文中比较 token、KL 散度、logit 差异等。它还用对量化 golden 输入施加一个 fp32 ulp 扰动的结果估计误差底线。默认通过条件包括设备与量化 golden 的 top-1 一致率至少 80%、平均 KL 不超过底线的 3 倍；加 `--against` 后，两个设备还须给出相同 token 和位级一致 logits（F-060）。ulp 是浮点表示中用于衡量末位精度的单位。上述阈值属于这个版本的验收约定，不是通用模型质量标准。

位精确对照是已执行测试上的证据，不等于形式化证明。有限提示词、测试样本和支持模型不能证明全部输入、全部硬件状态都正确。

## 数值契约与修复案例

ISA 不仅定义 `LD`、`QACT`、`MM` 的功能，还明确零的符号、次正规数、舍入方式、近似函数的运算顺序与权重编码（F-061）。硬件与模拟器如果各自选择“差不多”的浮点实现，误差可能在量化舍入边界变成不同整数，并继续传播。

固定 ISA 使用 roundTiesToEven 舍入，将次正规输入和结果 flush to zero，不提供完整舍入模式或异常标志；文档明确声明它不是完整符合 IEEE 754 的实现（F-061）。这里的“精确”指精确遵循项目自己的契约，不是所有运算都正确舍入到数学真值。

2026-10-08 的 `8eaa4806` 提交同时调整 `exp2` 七阶近似系数、`recip`/`rsqrt` 最后一步牛顿校正、量化审计及 Qwen3 的 K smoothing，并更新 Python 数值模型、RTL、ISA 文档和测试（F-062）。提交还记录零符号反例测试：故意改坏负零行为的 mutant 会被测试拦截。这比只记录“测试全绿”多了一层证据，说明测试确实能发现某类缺陷。

README 与提交记录报告 Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B 的 int8/4 位配置共 6 组板卡对照，每组 103～128 步，板卡与 ISA logits 差异为 0 ulp（F-063）。这些文件构成可审计的项目测试记录，**仍不是本次或博主的独立 FPGA 复现**。

## 分级复现与阅读路径

博主固定 `8eaa4806`，使用 Python 3.12、pytest、numpy 与 textual，选择 `test_isa.py`、`test_compiler.py`、`test_fp.py`、`test_quant.py`、`test_kernels.py` 并以 `-k 'not rtl'` 排除 RTL，报告 `116 passed, 1 deselected`（F-064）。这支持第三方报告的 Python 参考实现与编译器测试自洽；测试数量与结果本次没有重新运行，不能直接升级为 RTL 或板卡已独立验证。

| 层级 | 前置条件与工作 | 结果应如何解读 |
|------|----------------|----------------|
| Python | 固定提交、Python 环境、上述五组测试 | ISA/编译器/数值/量化/内核测试，不覆盖 RTL |
| RTL | 另需 Verilator 5；模型级对照还需权重与相关依赖 | 检查仿真电路与 ISA，不能替代物理板卡 |
| FPGA | 特定板卡、Vivado 位流构建、JTAG、PCIe 与驱动环境 | 检查实际位流、存储与主机协作 |

在已检出固定版本并准备好依赖的环境中，博主的 Python 测试选择如下。这是其复现命令的核心部分，**本次未执行**：

```bash
python -m pytest -q -k 'not rtl' \
  tests/test_isa.py tests/test_compiler.py tests/test_fp.py \
  tests/test_quant.py tests/test_kernels.py
```

继续验证 RTL 时，固定 README 给出的一个短模型对照是：

```bash
python3 tools/validate.py --model lfm2 --backend rtl --against isa \
  --tokens 3 "The capital of France is"
```

该命令还需模型权重、相关 Python 依赖与 Verilator 5。固定 README 说明验证工具当时支持 Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B、Gemma 4 E2B，未支持 MoE；模型验证示例用 16 核主机，Gemma 4 E2B 可达 16 GB 内存峰值，并建议主机有 22 GB 可用内存（F-065）。因此，“除板卡外可在笔记本运行”不能被理解为所有步骤都低成本。

建议从固定版本的 `docs/isa.md` 开始，再读 `opentpu/kernels/` 与 `docs/compiler.md`，随后读 `opentpu/isasim.py`、`rtl/top/otpu_top.sv`，最后查模型文档与 `docs/board.md`（F-071）。每次跨层阅读都选同一个算子、同一组输入，检查其指令与中间结果，避免只看各层独立演示。

## 性能口径与 HN 勘误

固定 README 的主性能表采用 512-token 提示词，贪心生成 64 个 token；device decode 只算加速器运行周期，wall decode 包含主机开销（F-067）。不能将它与流式回传、板卡自行选 token 或另一位流的结果混在一起。

| 模型 | 权重配置 | device decode | wall decode |
|------|----------|---------------|-------------|
| LFM2.5-230M | int8 | 59.0 tok/s | 52.3 tok/s |
| LFM2.5-230M | 4 位权重、int8 head | 85.8 tok/s | 82.1 tok/s |
| Qwen3-0.6B | int8 | 21.6 tok/s | 21.3 tok/s |
| Qwen3-0.6B | 4 位权重、int8 head | 31.3 tok/s | 30.7 tok/s |
| Qwen3.5-0.8B | 4 位权重、int8 head | 24.5 tok/s | 23.3 tok/s |
| Qwen3.5-2B | 4 位权重、int8 head | 12.09 tok/s | 12.03 tok/s |
| Gemma 4 E2B | 4 位权重、4 位 head | 12.14 tok/s | 12.09 tok/s |

表中数据均为项目作者报告（F-068），不是第三方性能基准。旧页把 82.1 与 85.8 写成“第三方观测口径不一”不准确：同一固定 README 已同时给出它们，差异是 wall/device 计时边界。量化配置也须保留 head 格式，不能一律简写成“全模型 4bit”。

4 位权重减少存储流量，可能提高带宽受限解码的吞吐，同时带来可测量的量化质量损失（F-069）。Qwen3.5-35B-A3B 的 3.95 tok/s 属于另一组 MoE 实验：专家从主机存储流入板卡槽位，README 报告每 token 153 MB 流量、PCIe 约 1.41 GB/s（F-070）。模型计算在卡上执行不等于全量权重驻留 4 GiB 板存。性能比较还应保持模型、量化质量、提示词、批量、计时和整机功耗条件一致。

HN 也存在时点勘误。博文记录 2026-10-09 清晨仓库 534 Star、讨论 340 分和 399 条评论；本次于 2026-10-13 查询 [讨论 49980715 官方 API](https://hacker-news.firebaseio.com/v0/item/49980715.json)，返回 348 分、405 条评论（F-072）。因此，旧页及旧核验台账将约 144 称为“峰值”、将 250+ 判作未证实，已被更晚的直接观测推翻。340/399 是博文历史快照，本次 API 不能独立证明那个时点的精确值；348/405 也不是未来恒定值。关注度不能证明生产采用。

## 工程洞察与迁移

以下是基于证据的教程性归纳，不是已经跨项目验证的普遍定律。

| 洞察 | 现象与证据 | 机制假设与影响 | 工程建议 |
|------|------------|----------------|----------|
| 分开质量与实现正确性 | HF、量化 golden、ISA 与板卡有不同比较目标（F-058～F-061） | 量化误差与实现偏差混在一起时，可能误判硬件或掩盖质量下降 | 分别记录质量指标和位级对照；不能只验最终 token |
| 限制隐式行为 | 搬运显式，trace 能展示等待状态（F-057、F-071） | 较少隐藏状态可能缩小诊断与优化搜索空间，但不保证任何 agent 都能设计成功 | 先明确数值、布局与状态契约，再优化流水与搬运 |
| 让修复有反例 | 数值规则、Python、RTL、测试和板卡记录一起更新（F-062、F-063） | 只改一层可能留下跨层漂移；能拦截故意改坏实现的测试提供额外辨别力 | 每次契约变更同时更新实现、边界测试和对应层级的证据 |

可迁移的“契约对拍”方法适用于有明确输入、参考行为和可重复观测的多实现系统。对于尚无可判定标准的开放式任务，不能直接套用位精确要求。

1. 固定源码提交、输入、数值格式和执行配置，避免比较过程中基线漂移。
2. 把参考契约与实现分开，注明每个参考能回答的问题。
3. 先从小算子对照，再扩展到模型或完整业务流程。
4. 加入舍入边界、零符号和量化编码等反例；检查故意改坏的实现会不会被拒绝。
5. 按 Python→RTL→真实设备逐层提升验证强度，保留输出与环境记录。
6. 通过正确性后再比较性能，并说明计时边界与质量代价。

三类反模式是：只凭同一个 token 宣称数值正确；把 Python 测试通过当作 FPGA 已验证；混用 device/wall 或不同量化配置宣称提速。作为尚未实测的迁移示例，序列化库也可固定数据模型与字节格式，对拍 Python/C++ 编码器，再用往返与畸形输入测试检查边界；不适合逐位一致的计算，应预先定义误差容忍规则。

## 增量事实登记与来源

既有 F-001～F-052 保留在 [信源登记](../references/source-manifest.md)，旧核验结论见 [核验报告](../references/verification.md)。本次用户指定单页更新，因此 F-053～F-072 在本页登记，不重编号旧事实、不改写其他页面的历史台账。引用新结论应以本页及固定来源为准。

| F | 内容 | 类型与证据边界 | 来源与定位 |
|---|------|----------------|------------|
| F-053 | 博文将执行链分为内核、编译器、ISA、模拟器、RTL、板卡运行时六层 | 文档描述，README 架构图交叉核对 | 博文“完整路径”；README How it works |
| F-054 | ISA 每条指令固定为 8 个 32 位字 | 项目契约，已读取 | ISA Encoding |
| F-055 | 博文给出 `ol.load→LD`、`ol.quantize→QACT`、`ol.dot→MM` 映射 | 博文转述，指令语义与 ISA 对照；未全面审计编译器 | 博文“完整路径”；ISA 编码与 QACT/MM |
| F-056 | 机器含 sequencer、DMA、矩阵、向量与量化单元；使用 int8 激活、int8/4 位权重及 fp32 向量运算 | 项目文档描述，非硬件实测 | README How it works；ISA Machine model/MM |
| F-057 | README 声明无 cache、无隐藏调度，每次数据搬运有指令表达 | 项目声明，未全面审计 RTL | README How it works |
| F-058 | 博文区分 HF 浮点模型、ISA 参考和 RTL/FPGA 三种参照 | 博文描述，与 README 验证章节对照 | 博文“位精确”；README Validating against Hugging Face |
| F-059 | README 区分原始 fp32、量化 W+A golden 与设备；`--against` 增加第二设备对照 | 项目工具文档，非本次执行结果 | README Validating against Hugging Face |
| F-060 | 默认验收为 top-1 至少 80%、KL 至多误差底线 3 倍；第二设备要求 token/logits 位精确一致 | 固定版本工具约定，非通用质量标准 | README 验收条件 |
| F-061 | ISA 定义零符号、FTZ、roundTiesToEven、近似运算顺序，明确不完整符合 IEEE 754 | 已读取的数值契约 | ISA Arithmetic (fp32) |
| F-062 | 10-08 提交修改 exp2、recip、rsqrt、量化/K smoothing，并联动 Python、RTL、文档及反例测试 | 提交说明与文件列表已核对；未重新运行测试 | 8eaa4806 提交说明、变更列表 |
| F-063 | 项目报告 6 组板卡验证，每组 103～128 步，ISA/板卡 logits 为 0 ulp 差异 | 项目作者自测，不是独立 FPGA 复现 | README 板卡验证段；提交说明 |
| F-064 | 博主报告固定提交、Python 3.12、五组测试、`116 passed, 1 deselected`，排除 RTL | 第三方复现报告；本次未重跑 | 博文“我实际复现了什么” |
| F-065 | RTL 需 Verilator 5；固定模型验证工具未支持 MoE；Gemma 4 E2B 峰值 16 GB、建议 22 GB 可用内存 | README 环境与资源口径，非本次测量 | README Try it / Validating |
| F-066 | 板卡为 YPCB-00338/xc7k480t，双通道 DDR3-1066、4 GiB、133.33 MHz、17.1 GB/s 峰值 | 项目规格/自测口径 | README Results |
| F-067 | 性能主表使用 512-token prompt、64-token greedy decode；device 不含主机，wall 含主机 | 固定基准方法 | README Results，Method |
| F-068 | 本页性能表的 7 个配置及 device/wall 数字来自固定 README，LFM2 4 位为 85.8/82.1 | 项目自测；两数是不同计时边界 | README Results 表 |
| F-069 | README 报告 4 位权重减少流量、提高部分模型吞吐并带来可测量困惑度损失 | 项目自报，未独立评测质量或性能 | README 4-bit weights 段 |
| F-070 | Qwen3.5-35B-A3B 专家主机流入，3.95 tok/s、153 MB/token、PCIe 1.41 GB/s | 项目 MoE 自测；非全权重驻留 | README MoE 段 |
| F-071 | Lens 记录 ISA/RTL/板卡，提供 roofline、时间线、指令表；README 给出 ISA→编译器→模拟器→RTL→模型→板卡阅读路径 | 项目工具与阅读指南描述 | README How it works / Where to start reading |
| F-072 | 博文记录 10-09 534 Star、HN 340/399；10-13 官方 API 返回 348/405；博文也提示 AI 生成归属与生产采用未被证明 | 历史数字为博文单源；348/405 为本次直接观测；不能据此推断逐行作者或生产采用 | 博文开头/结尾；HN 官方 API |

以上 README 与 ISA 均固定到 `8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25`，不以持续变化的 main 分支代替基准：[技术博文](https://fanweibin.cn/posts/2026-10-09-opentpu-ai-accelerator-fpga-verification)、[固定 README](https://github.com/FeSens/openTPU/blob/8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25/README.md)、[固定 ISA](https://github.com/FeSens/openTPU/blob/8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25/docs/isa.md)、[修复提交](https://github.com/FeSens/openTPU/commit/8eaa48064f6f408eae9df6a0d3c58b3c7e66ea25)。

## 适用范围与维护

openTPU 适合学习软硬件契约、量化、数据搬运和 agent 生成硬件的验证方法。博文在其观测时点报告尚无正式 Release 或稳定标签；这一判断属于历史快照，本次未重新核对发布列表。生产采用仍需评估模型/算子覆盖、工具与板卡依赖、稳定性、功耗、成本及独立性能对照，不能仅由 Star、测试数或项目名称推断。

本页保留 `status: draft`。独立板卡复现、数值契约变更、新位流/基准方法或正式版本发布均触发复核；`stale_after` 为 2027-04-30。旧周报作者的“验证前移”“朴素设计利于迭代”等判断（F-007、F-008、F-010、F-011）可作为研究假设，不构成“增加 cache 后 AI 方法必然失灵”的证据。
