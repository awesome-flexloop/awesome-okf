---
okf_version: "0.2"
type: Concept
title: "机器模型：slice、三层存储与顺序完成语义"
description: "slice 私有资源与 collective；D/MCOLS/ACT_ROWS 参数与 replay 透明性；三层存储、顺序完成语义与 16 个寄存器"
tags: [openTPU, 机器模型, slice, 存储层次, 寄存器, 顺序语义]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T16:00:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-facts
    resource: /references/facts.md
    title: "openTPU 事实登记表 F-001~F-123"
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

## slice：私有的一整套核，collective 是唯一共享面

机器由 `S` 个 **slice** 组成。每个 slice 私有一整套资源：一个 sequencer（含 16 个 32-bit 寄存器，R0 读为 0）、指令存储器 IMEM、私有 DRAM、TMEM、ACT RAM、矩阵单元 MXU、向量单元 VPU 和量化器。slice 之间**不共享任何东西**，唯一的跨片机制是 collective 单元，对应 `GATHER`（all-gather）与 `BAR`（栅栏）两条指令（[isa.md L9-L11](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L9-L11)）。

生产板卡是 **S=1**；多 slice 主要属于旧设计点与其他 target。换言之，读单 slice 的行为就能读懂生产机器，collective 只是为扩展预留的语义面。

## 形状参数：D、MCOLS、ACT_ROWS、ACT_BLOCKS、LANES

[docs/isa.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L12-L16) 与模拟器 `Config`（[isasim.py L18-L36](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L18-L36)）定义了这些参数：

- **D**：MXU 深度，同时也是量化块大小（按字节/按 int8 元素）。生产板卡 **D=128**，测试小点默认 32。
- **MCOLS**：MXU 列数。生产板卡 **MCOLS=4**。
- **ACT_ROWS**：ACT RAM 行数，即一次 MM 最多能驻留的静态（权重侧）行数；要求 ≥ MCOLS，默认等于 MCOLS。生产板卡 **ACT_ROWS=16**。
- **ACT_BLOCKS**：ACT RAM 按块计的深度，生产板卡为 128（K 方向最多 16384）。
- **LANES**：VPU 通道数，等于 TMEM bank 数，生产板卡为 **8**；纯时序参数，程序与结果都不依赖它。

### replay：硬件可以重复流数据，但结果必须透明

当 `ACT_ROWS > MCOLS` 时，MXU 对每 MCOLS 行组成一组，把每个流操作数 chunk 重复消费（"replay"）：一次 DRAM 遍历服务全部 M 行，每 chunk 花费 ceil(M/MCOLS) 个周期。关键契约是：**结果不依赖 MCOLS 与 ACT_ROWS**（[isa.md L12-L16](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L12-L16)）。同理 LANES 只影响快慢。因此形状参数是微架构参数，不是 ISA 语义参数——换一个列数不同的实现，同一份程序的位结果不变。

模拟器里有三套参数点需要区分（[isasim.py L39-L72](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L39-L72)）：代码默认（S=1 D=32 MCOLS=8，测试用）、`design_config()`（S=2 D=128 MCOLS=8 LANES=16 的**旧 Kintex 设计点**，现主要供参数化测试）、`board_config()`（读 target，生产点 S=1 D=128 MCOLS=4 ACT_ROWS=16 LANES=8）。引用参数时应以生产 target 为准，旧点只作演进对照。

## 三层存储，三种编址与访问规则

**DRAM——字节编址的外部存储器。** 小端，按 32-bit 字访问；所有字访问与所有 MXU chunk 读必须 **4 字节对齐**。全机器只有 `QST` 指令写字节（量化后把 int8 行写回 DRAM），其他访问都是字（[isa.md L17-L18](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L17-L18)）。生产板卡每 slice 4 GiB，64 字节为一个 DRAM beat。

**TMEM——32-bit 字编址的片上张量存储器。** 存放 fp32 值，按 raw IEEE bits 保存（[isa.md L19](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L19)）。VOP 向量运算、LD/ST、softmax/归一化等都以 TMEM tile 为操作对象；生产配置 65536 字。

**ACT RAM——量化激活的驻留区。** 容量为 `ACT_ROWS × ACT_BLOCKS × D` 个 int8，并且每个（行，块）附带一份尺度记录：行尺度 `Sa[r][k]`（fp32）加 4 个 8-bit 偏移 `da[r][k][b]`（每个 D/4 子块一个，子块尺度为 `Sa * 2^-da`）。它**只由 QACT 写、只由 MM 读**（[isa.md L20-L23](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L20-L23)）：

```text
ACT RAM:  int8 激活值 [ACT_ROWS][ACT_BLOCKS][D]
尺度记录:  Sa[r][k]            fp32 行尺度
          da[r][k][0..3]      每 D/4 子块一个 8-bit 偏移
```

尺度不是外挂的元数据，而是驻在硬件里、由指令字段和累加器移位消费的一等数据。量化器如何计算 Sa/da、MM 如何使用它们，见 [08-quantization-unit](/concepts/08-quantization-unit.md) 与 [06-mm-and-mxu](/concepts/06-mm-and-mxu.md)。

## 顺序完成语义：唯一允许的「提前」是预取

ISA 的执行模型是严格顺序的：**每条指令的全部写入都可见后，下一条才开始**（[isa.md L25-L26](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L25-L26)）。这是程序员可见的语义，也是模拟器的执行方式。

硬件在此语义下只保留一个例外口子：**MXU 内部可以从 DRAM 预取流操作数**。sequencer 还维护一个 WIN=16 的内存足迹窗口，让不同单元在不破坏依赖的前提下填空冒泡——但它只做依赖跟踪，不做乱序重排，可见结果与顺序执行逐位相同。这是容易误读的一点：预取/窗口/replay 都不是隐藏缓存层。派发与窗口机制详见 [03-sequencer-and-chaining](/concepts/03-sequencer-and-chaining.md)。

## 16 个寄存器与运行参数

每个 slice 有 16 个 32-bit 通用寄存器 R0-R15。**R0 读为 0**；一次 run 启动时 R0-R7=0，**R8-R15=ARG0-ARG7**，即主机在 RUN 前写入的 8 个参数字（[isa.md L30-L34](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L30-L34)）：

- 板卡上：控制寄存器 0x060 起的 4k 区（能力位 CAPS bit25 公告该机制）；
- ISA 模拟器：`Machine(..., args)` 或 `load(programs, args)`；
- RTL 模拟器：`+arg0=..+arg7=`；未写的参数为 0。

所有地址都采取 **`R[x] + imm`** 形式，循环次数也可以是 `R[ra] + 立即数`。于是同一份程序能服务不同输入：主机算出实际地址/步长放进参数，设备上没有地址乘法。编译器把第 k 个不同的运行时量 `(var, c)` 放在 R15-k，地址寄存器从 R1 往上长（详见 [03](/concepts/03-sequencer-and-chaining.md)）。设备自己算出的值要回到寄存器（地址、循环计数、条件），唯一通道是 `RLD` 指令，见 [02-instruction-set](/concepts/02-instruction-set.md)。

## 相关概念

- [指令系统：17 条指令、8×32-bit 字编码与寄存器约定](/concepts/02-instruction-set.md)
- [sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序](/concepts/03-sequencer-and-chaining.md)
- [量化器：QACT/QST、行尺度 Sa/da 与 q8 公式](/concepts/08-quantization-unit.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
