---
okf_version: "0.2"
type: Reference
title: "openTPU 事实登记表 F-001~F-123（ffe997e）"
description: "对固定提交 ffe997e 静态取证的 123 条编号事实：六层链、ISA、fp32 契约、量化、软件栈、RTL、板卡、ASIC 与验证体系"
tags: [openTPU, 事实登记, F-xxx, 位精确契约, ISA, 量化]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T15:20:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-source-map
    resource: /references/source-code-map.md
    title: "openTPU 源码地图与信源固定"
  - id: opentpu-pinned-tree
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

# openTPU 事实登记表 F-001~F-123

- 全部事实对固定提交 `ffe997e9a8b8607b07b3d1bb3c1132db0faf044e` 静态取证（读码 + 对固定 blob 的脚本计数），无推断性表述；性能数字均标注「作者报告」。
- 链接为 pinned 行段；取证时间 2026-10-13。规模计数台账（C01-C32）见[源码地图](/references/source-code-map.md#规模计数台账对-ffe997e-脚本计数口径与-v-阶段复核见-verificationmd)。

## A. 项目定位与六层链（F-001~F-010）

| F | 事实 | 锚点 |
|---|---|---|
| F-001 | README 定位 "An open-source AI accelerator, developed by AI."；两问：AI agents 做硬件能走多远、能否造出运行自身推理的芯片 | [README L3-L7](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L3-L7) |
| F-002 | 学习定位：可端到端读完的小 monorepo——SystemVerilog 硬件、ISA、位精确模拟器、内核语言与编译器、驱动真实 PCIe 卡的主机软件；"from a matmul in Python down to the wires" | [README L14-L20](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L14-L20) |
| F-003 | 六层链：ol 内核→language+compiler（布局/仿射寻址/融合）→ISA（8×32-bit 字）→ISA 模拟器(Python)↔RTL(SystemVerilog)「same bits, checked by the tests」→Vivado 位流→Kintex-7→PCIe 主机 | [README L129-L142](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L129-L142) |
| F-004 | 机器刻意简单：sequencer 每周期发射一条指令给少数单元（DMA/矩阵/向量/量化器）；无 cache、无隐藏调度；每次搬运一条指令，trace 可解释周期去向 | [README L144-L148](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L144-L148) |
| F-005 | 官方阅读路径 7 步：isa.md→kernels+compiler.md→isasim.py（"the simulator, which is the spec"）→rtl/top/otpu_top.sv→模型文档→board.md→targets.md | [README L311-L322](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L311-L322) |
| F-006 | 复现入口：`pip install -e .` + pytest/torch/transformers；模拟器 chat：`otpu-chat --model lfm2 --backend isa`；RTL 测试需 Verilator 5 | [README L180-L187](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L180-L187) |
| F-007 | 板卡路线：`make bit`（boards/ypcb-00338）、JTAG、`sudo otpu-setup`、`otpu-chat --backend board` | [README L189-L191](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L189-L191) |
| F-008 | 许可 Apache License 2.0 | [README L345-L347](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L345-L347) |
| F-009 | 贡献契约：ISA/模拟器/RTL 变更必须保持 `python3 -m pytest -q` 通过；性能声明必须说明测量方法 | [README L341-L343](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L341-L343) |
| F-010 | isa.md 自我定位：compiler.py、isasim.py、rtl/ 三者之间的契约；"All three must agree on every bit written to TMEM or DRAM." | [isa.md L1-L5](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L1-L5) |

## B. 机器模型与 ISA（F-011~F-030）

| F | 事实 | 锚点 |
|---|---|---|
| F-011 | S 个 slice；每 slice 含 sequencer（16×32-bit 寄存器，R0 读为 0）、指令存储器、私有 DRAM、TMEM、ACT RAM、MXU、VPU、quantizer；slice 间除 collective（GATHER/BAR）外不共享 | [isa.md L9-L11](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L9-L11) |
| F-012 | D=MXU 深度=量化块大小；MCOLS=列数；ACT_ROWS=一次 MM 最大驻留行（≥MCOLS，默认=MCOLS）；ACT_ROWS>MCOLS 时 MXU 对每 MCOLS 行组 replay 流数据；结果不依赖 MCOLS/ACT_ROWS | [isa.md L12-L16](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L12-L16) |
| F-013 | DRAM 字节编址、小端；字访问与 MXU chunk 读须 4 字节对齐；只有 QST 写字节 | [isa.md L17-L18](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L17-L18) |
| F-014 | TMEM 32-bit 字编址，存 fp32（raw IEEE bits） | [isa.md L19](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L19) |
| F-015 | ACT RAM 每行每块存 Sa[r][k]（fp32）与 4 个 8-bit 偏移 da[r][k][b]（每 D/4 子块一个，子块尺度 Sa*2^-da）；只由 QACT 写、只由 MM 读 | [isa.md L20-L23](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L20-L23) |
| F-016 | 顺序执行：每条指令全部写可见后下一条才开始；MXU 内部预取流操作数 | [isa.md L25-L26](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L25-L26) |
| F-017 | 启动时 R0-R7=0，R8-R15=ARG0-ARG7（板卡控制寄存器 0x060+4k，CAPS bit25；模拟器 Machine(args)/load；RTL +arg 生成参数）；地址形式 R[x]+imm | [isa.md L30-L34](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L30-L34) |
| F-018 | 17 opcode：0x00 NOP/01 HALT/02 LI/03 ADDI/04 LOOP/05 BAR/06 RLD/07 WAITW；0x10 LD/11 ST/12 DSTEP/13 STREAM；0x20 MM/21 QACT/22 QST；0x30 VOP；0x40 GATHER | [isa.py L8-L17](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L8-L17) |
| F-019 | w0 位段：opcode[7:0]｜ra[11:8]｜rb[15:12]｜rc[19:16]｜rd[23:20]｜flags[31:24]；计数/形状/步长是立即数 | [isa.md L154-L158](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L154-L158) |
| F-020 | LOOP：body=随后 w1 条指令，执行 R[ra]+w2 次（0 跳过）；嵌套深度 4 | [isa.md L166](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L166) |
| F-021 | RLD：R[rd]=f2i(T[R[ra]+w1])，是设备算出的值到达地址/循环计数/条件的唯一途径；RAW 取原始位；MUL 乘 R[rb]+w2 取低 32 位 | [isa.md L416-L430](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L416-L430) |
| F-022 | f2i 向零截断；|x|<1（含 ±0 与冲洗的非规格数）→0；|x|≥2^31/inf/NaN→0x80000000；≤24 有效位整数精确 | [isa.py L167-L178](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L167-L178) |
| F-023 | WAITW：DMA 轮询 M32[R[ra]+w1]&w4 与 R[rc]+w3 比较（EQ/NE/GE，w5 间隔、w6 超时），成立后写 T[R[rb]+w2]；超时→HALTED+ERROR+WAIT_TO（bit8）；MoE 专家流以它做 fence/目录/槽位标签 | [isa.md L432-L486](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L432-L486) |
| F-024 | HALT CHAIN：排空窗口、store 落地后，从 DRAM 字节地址 R[ra] 载入 R[rb] 条指令到 IMEM 并启动；R0-R7=0、R8-R15 用新参数；TMEM/ACT/DRAM 保持；主机视角仍是一次 run；decode 按 attention bucket 链接 | [isa.md L488-L496](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L488-L496) |
| F-025 | GATHER：所有 slice 以相同 dst/rows/cols/drs/seg 执行；每片分片写入所有片 TMEM（all-gather）；源/目的不得重叠 | [isa.md L498-L505](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L498-L505) |
| F-026 | BAR：等待所有 slice 到达（E 阶段勘误：bar() 定义锚点为 isa.py L133，非 R 阶段误记的 L167——该处实为 f2i） | [isa.py L133](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L133)、[isa.md BAR 节](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L167) |
| F-027 | STREAM（0x13）泛化 DSTEP：float-safe TMEM 描述符编程一遍行处理（A 行点积→每行 ≤15 个 SCALAR op→U：Y=S*G+D*B→Q：Y 的点积）；5 固定字+操作区，驻 TMEM 顶部 64 字 | [isa.md L386-L414](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L386-L414) |
| F-028 | STREAM 标量算子 11 种（码 0-10）：SC_ADD/SUB/MUL/MAX/MIN/MOV/RSQRT/RECIP/EXP2/LOG2/EXP2SUB；操作数 r0-r7、行 A、行标量 X[r]、常量 K0-K3、+0、+1 | [isa.py L220-L223](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L220-L223) |
| F-029 | 板卡 STREAM 子集由 stream_hw_cfg 裁决（DRAM 状态、行≤256、列 64-256、状态步模式），CAPS bit26 公告；编译器 ol.state_step 否则回退 VOP；DSTEP=STREAM 取 isa.gdn_desc | [isa.py L352-L380](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L352-L380) |
| F-030 | DSTEP（0x12）：DMA 对留在 DRAM 的 fp32 状态做一次 Gated DeltaNet head step（状态不进 TMEM）；rows 1..256，cols∈{64,128,192,256}；语义与 VOP 序列 RDOT,MUL,SUB,MUL,OUTER,RDOT 位一致；CAPS bit6；无 DSTEP 位流视其为非法指令 | [isa.md L352-L384](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L352-L384) |

## C. fp32 数值契约（F-031~F-043）

| F | 事实 | 锚点 |
|---|---|---|
| F-031 | RNE+FTZ：add/sub/mul 按 roundTiesToEven，非规格输入按带符号 0、非规格结果替换为带符号 0；乘到 2^-126 的上舍入保留 | [isa.md L59-L63](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L59-L63) |
| F-032 | 零和符号：精确抵消为 +0；(-0)+(-0)=(-0)-(+0)=-0；x+(-0)=x（单元用 v*1+-0 做恒等） | [isa.md L64-L67](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L64-L67) |
| F-033 | 明确非一致性 IEEE 754：仅 RNE 单一方向、denormals flush、无异常标志（overflow→±inf、非法操作→canonical NaN）、除法/开方为下述近似而非正确舍入 | [isa.md L68-L73](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L68-L73) |
| F-034 | canonical NaN=0x7FC00000；add/mul 对 NaN 给 canonical；ftz/max/min/abs/COPY/FILL 保留 NaN 位；比较按 sign-magnitude 位全序；exp2(NaN)=+inf；q8(NaN)=0 | [isa.md L72-L79](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L72-L79) |
| F-035 | exp2=7 阶 minimax（C0=1，系数 3F800000…37B3C7D6），f 精确区 1.26 ulp、x+1 舍入区 1.61 ulp，整数点精确、单调 | [isa.md L82-L92](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L82-L92) |
| F-036 | recip：魔数 0x7EF311C3 种子+两次 Newton y=y*(2-a*y)+校正步 e=1-a*y;y=y*e+y（无 FMA 时纯 Newton 驻点低 1 ulp，recip(1) 曾为 0.99999994）；1.16 ulp；2 的幂精确；|x|≥2^126 返回带符号 0 | [isa.md L93-L104](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L93-L104) |
| F-037 | rsqrt：魔数 0x5F3759DF+两次 Newton（1.5-h*y²）+校正步；指数域缩放 16x/x16；1.03 ulp；4 的幂精确；x≤0/+inf→+0 | [isa.md L105-L112](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L105-L112) |
| F-038 | log2：按 sqrt(2) 分奇偶指数（阈值 0x3504F3），t=m-1 精确，9 系数 minimax；2.3 ulp；±0→-inf，x<0/NaN→canonical NaN | [isa.md L113-L121](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L113-L121) |
| F-039 | 全序比较：-inf<…<-0<+0<…<+inf<NaN（sign-magnitude 位）；max/min 归约与求值顺序无关 | [isa.md L122-L124](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L122-L124) |
| F-040 | 行和面向流水线加法器：isum_P（P=64，左到右部分和+折叠树，+0 填充）；MM 为精确整数和 | [isa.md L125-L131](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L125-L131) |
| F-041 | q8：half-to-even 取整、饱和 [-127,127]、NaN→0 | [isa.md L132-L133](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L132-L133) |
| F-042 | 行量化公式（QACT/QST）：amax=行 max|x|；S=amax*1/127；inv=127*recip(amax)；组 d_g=最大 d≤31 使 a_g*2^d≤amax；q=q8(x*(inv*2^d_g))，两次舍入乘法 | [isa.md L135-L150](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L135-L150) |
| F-043 | RTL fp 实现声明与 fp32.py 位精确：otpu_fp.sv 组合函数，复合函数是 fp_add/fp_mul 固定序列 | [otpu_fp.sv L3-L4](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu/otpu_fp.sv#L3-L4) |

## D. MM/MXU/权重格式（F-044~F-057）

| F | 事实 | 锚点 |
|---|---|---|
| F-044 | MM 字段：sa 流操作数行（字节）、ssa 权重 scale 行、out TMEM、N/KB/k0、rs/ors/M/ab/srs；flags UNIT/ACC/RMAX/ASCALE/WF[5:4]/PAIR(bit6)/RSC(bit7) | [isa.py L381-L406](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L381-L406) |
| F-045 | MM 精确整数累加：每块每组乘积和 c，按权重/激活偏移给位移 B，acc 精确（|acc|<2^47）；每输出一次 fp32 epilogue y=(i2f(acc)*Sw[n])*(Sa[j][ab]*2^-W)，三次舍入乘法 | [isa.md L200-L219](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L200-L219) |
| F-046 | 累加界防护：组 |c|<2^19（int8；4-bit <2^16）、B<2^17、每 int8 MM 至多 4*255 组；sh<0 的组不计入（扫描实测至多 7e-5 组） | [isa.md L221-L224](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L221-L224) |
| F-047 | RMAX：MM epilogue 免费随行最大；ASCALE 需 UNIT+ACC（先 y=T[out]*T[ssa+j]+y，flash-attention 重缩放）；RMAX/ASCALE/PAIR 需 M≤MCOLS（PAIR 2M≤MCOLS） | [isa.md L186-L198](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L186-L198) |
| F-048 | 四种权重格式 WF=0 int8 / 1 int4 / 2 FP4(E2M1) / 3 NVFP4；4-bit 两元素/字节；E2M1 码值 {0,1,2,3,4,6,8,12}×2 含符号位，矩阵自带一半尺度 | [isa.py L25-L27](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L25-L27) |
| F-049 | scale 行布局：int8=Sw+每块 1 字节 dw；int4/fp4=Sw+保留字+每块 1 字（dw 与 4 个 6-bit m）；nvfp4=Sw+3 保留字+每块 2 字（8 个 E4M3 尺度）；权重值=w*m*2^-dw*Sw[n] | [isa.md L238-L255](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L238-L255) |
| F-050 | RSC：scale 行只有 Sw[n]（K cache，每 token 一个尺度）；不能与 NVFP4 同用 | [isa.md L250](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L250) |
| F-051 | PAIR 列复用（仅 4-bit、2M≤MCOLS、k0 偶）：闲置列 M..2M-1 取奇 K 块，输出行 j 偶块取 ACT 行 j、奇块取 j+M（QACT DUP 同周期复制）；一 chunk 进两块满速 | [isa.md L257-L267](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L257-L267) |
| F-052 | QACT：把 TMEM 行量化进 ACT RAM；CSCALE 逐列尺度、RSCALE 逐行尺度（即 RMSNorm 的 x*r*gamma 折叠进量化器，免单独向量遍）；ROW 全 d=0；DUP 为 PAIR 复制行 | [isa.md L269-L281](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L269-L281) |
| F-053 | QST：量化 TMEM 行写入 DRAM 字节；ROW 模式写 fp32 尺度 S（供 RSC）否则写 int8 scale 行；64 字节 beat 部分写由 native_dram 合并；HALF（仅 ROW）只写每行前半 | [isa.md L283-L297](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L283-L297) |
| F-054 | 4-bit 声称 4.25 bits/weight（FP4 值+两级块尺度，作者报告），LM head 保 int8；每 token 字节降约 1/3，decode +40%（Qwen3.5）~45%（Qwen3、LFM2） | [README L115-L118](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L115-L118) |
| F-055 | quant.py 关键 API：quantize/quantize_mxu(W,fmt,D)->(rows,srows)/dequantize_mxu/pack4/unpack4/e2m1_code/e4m3/import_nvfp4/import_mxfp4/MXAct/MXW/mx_matmul；NSUB=4 | [quant.py L208-L817](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py#L208-L817) |
| F-056 | MXU RTL：四列脉动阵列（生产 MXU_IMPL=2），权重 N 行×KB 块自 DRAM port B 经 FIFO 预取，scale 走 port A；链式 CLS=min(CL,D/8) 个 DSP48 积（cascade），每列 8 组和经移位/级联/第 9 颗 DSP 累加行；48-bit 精确；E=4 条 epilogue lane（i2f48 RNE+两次乘法） | [otpu_mxu.sv L1-L30](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mxu/otpu_mxu.sv#L1-L30) |
| F-057 | xc7k480t 用 DSP48E1（rtl/tech/xilinx7）；VU9P 用 DSP48E2（xilinxus）；ASIC 用 generic 单元 | [tech 目录](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/tech) |

## E. VOP（F-058~F-063）

| F | 事实 | 锚点 |
|---|---|---|
| F-058 | VOP 字段：dst/a/b（TMEM）、rows/cols、drs/ars/brs、func(w6[23:16])、bmode(w6[25:24])、imm=R[rd]+w7；B 四广播模式 B_FULL/B_ROW/B_COL/B_SCALAR | [isa.py L431-L441](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L431-L441) |
| F-059 | 20 功能码：0 ADD/1 SUB/2 RSUB/3 MUL/4 MAX/5 MIN/6 OUTER；8 COPY/9 EXP2/10 RECIP/11 RSQRT/12 ABS/13 FILL/14 EXP2SUB/15 LOG2；16 RSUM/17 RMAX/18 RSSQ/19 RDOT/20 ARGMAX（码 7 跳用） | [isa.py L39-L46](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L39-L46) |
| F-060 | EXP2SUB=exp2(A-B) 融合 softmax 步；ARGMAX 每行写 (RMAX, i2f(首个最大列+base)) 对（base 有符号整数，LM head 分块传首词表行使索引=token id） | [isa.py L437-L449](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L437-L449) |
| F-061 | OUTER（线性循环状态更新：Gated DeltaNet/Mamba2-SSD/GLA/RWKV/linear attention）：原位 T=T*Dv(c)+B(r)*Cv(c)，两次舍入积+一次舍入加；B 须 per-row；cols≤256；Cv/Dv 先读后写可与 dst 重叠 | [isa.py L452-L463](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L452-L463) |
| F-062 | isasim VOP 分派（E 阶段勘误：ops 字典实为 **14** 个条目，非 R 阶段误记的 13——ADD/SUB/RSUB/MUL/MAX/MIN 六个算术 + COPY/EXP2/RECIP/RSQRT/ABS/FILL/EXP2SUB/LOG2 八个）；OUTER（码 6）、ARGMAX、RSUM/RSSQ/RDOT 归约在字典外单独路径处理 | [isasim.py L649-L656](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L649-L656) |
| F-063 | VPU RTL 7 文件：otpu_vpu/otpu_fp/otpu_fpipe/otpu_quant/otpu_se_comp/otpu_se_tail/otpu_vtree.sv | [rtl/vpu/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/vpu) |

## F. ol 内核语言与编译器（F-064~F-074）

| F | 事实 | 锚点 |
|---|---|---|
| F-064 | ol 定位：triton.language/Gluon 风格，slice 间 SPMD；"Everything the hardware does is visible here: each call lowers to one or a few instructions." | [language.py L1-L18](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L1-L18) |
| F-065 | ol `__all__` 共 **38** 名（V 阶段勘误：R 阶段误记 36 且错列 5 个非导出名）= 36 个原语/类（jit/program_id/num_programs/block_size/tmem_words/mxu_columns；load/store/dot/quantize/stationary/quantize_into/exp2/log2/recip/rsqrt/abs/maximum/minimum/max/sum/sumsq/outer/full/zeros/empty/all_gather/all_reduce/range/static_range/kv_append；Tensor/QTensor/KVDesc/Tile/CompileError）+ 常量 **LOG2E/LN2**。release/deltanet_step/state_step/has_dstep/has_stream 是模块内真实函数但**不在** `__all__`（编译器经内部路径调用） | [language.py L29-L34](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L29-L34) |
| F-066 | ol.dot：a[M,K]@w[N,K]^T，块尺度 int8 操作数+fp32 累加；a 可即时量化或 quantize() 结果；acc 原位累加/out 覆写；ol.max(dot,axis=1) 由 MM RMAX 免费；acc_scale 做 flash-attention 重缩放 | [language.py L105-L117](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L105-L117) |
| F-067 | ol.quantize：行只量化一次进 ACT RAM 作驻留操作数；quantize(a*v[None,:]) 把列尺度折叠进 QACT CSCALE；rscale/cscale 折叠 RMSNorm | [language.py L79-L90](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L79-L90) |
| F-068 | ol.range 是硬件循环（body 只 trace 一次，跨迭代用 .set() 传值）；static_range 展开；release(var) 归还运行时参数寄存器 | [language.py L330-L351](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L330-L351) |
| F-069 | ol.kv_append：K token-major 每 token 一行 scale（QST ROW fp32→MM RSC；否则 int8 scale 行）；V 转置写；半宽头只写真行 | [language.py L355-L387](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L355-L387) |
| F-070 | ol.deltanet_step/has_dstep/state_step：DSTEP/STREAM 的 ol 入口；state_step 映射 Gated DeltaNet/DeltaNet/KDA/GLA/RetNet/Mamba2/mLSTM 等（mode delta/delta1/scale/dot × gate const/col/one）；不支持时按同舍入语义回退 VOP | [language.py L240-L326](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py#L240-L326) |
| F-071 | kernels 7 业务模块：attention（attention_decode/attention_layer + Bucket/Blocks/RowMasks/RowTiles/TileSeq）、mlp（swiglu_down/mlp）、lib（rmsnorm/sigmoid/silu/gelu_tanh/softcap/softplus/rope/rope_rows）、layouts（head_parallel_attention_weights）、mailbox（wait_served/post）、gather（onehot/table/gather_row/gather_record）、deltanet（gated_deltanet_step/head_step） | [kernels/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels) |
| F-072 | compiler.py 1929 行：CompileError/Loop/RunVar/DevVar/Affine/Tensor/QTensor/KVDesc/Tile/Bcast/Stationary/LoopBlock/Builder/Compiled/Kernel；布局即 API、仿射循环寻址、融合（量化折叠、EXP2SUB、RDOT/RSSQ peephole） | [compiler.py L32-L1928](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L32-L1928) |
| F-073 | @ol.jit 即 compiler.jit 装饰器；trace_fit(kernel,cfg,sid,bound) 产出 Builder；Kernel/Compiled 为编译产物 | [compiler.py L1884-L1928](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py#L1884-L1928) |
| F-074 | 参数寄存器分配：第 k 个不同 (var,c) 占 R15-k（arg_reg/arg_words），地址寄存器从 R1 增长；ol.release 归还；仅在将不够时才复用/搬运（fit 的程序位不变） | [isa.md L36-L55](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L36-L55) |

## G. 模拟器/RTL/板卡/主机（F-075~F-090）

| F | 事实 | 锚点 |
|---|---|---|
| F-075 | isasim.py 结构：Config（S/D/MCOLS/ACT_BLOCKS/TMEM_WORDS/DRAM_BYTES/IMEM_WORDS/LANES/PAIR/DSTEP/STREAM/ACT_ROWS）、SimError、Slice（dram/tmem/act/ascale/adoff/R16/pc/stack/chain/waiting/polling）、Machine(programs,drams,args)/load/run；IMEM 容量 ≤IMEM_WORDS/8 条 | [isasim.py L18-L130](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L18-L130) |
| F-076 | 三种 Config：代码默认（S=1 D=32 MCOLS=8 ACT_BLOCKS=64，测试小点）；design_config()（旧 Kintex 设计点 S=2 D=128 MCOLS=8 LANES=16 ACT_BLOCKS=64，现主要供参数化测试）；board_config()（读 target.current()：S=1 D=128 MCOLS=4 ACT_BLOCKS=128 LANES=8；OTPU_MCOLS/OTPU_LANES/OTPU_ACT_ROWS/OTPU_PAIR/OTPU_DSTEP/OTPU_STREAM 环境覆盖） | [isasim.py L39-L72](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L39-L72) |
| F-077 | 模拟器是 RTL golden：同程序同 DRAM 映像后每 slice 的 TMEM/DRAM 必须逐位相同 | [isasim.py L1-L5](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py#L1-L5) |
| F-078 | rtlsim.py：Verilator 构建/运行 RTL；RTL_SOURCES 20 个 .sv（generic tech）；--binary -O3；构建目录 build/verilator；依赖 fcntl（Unix/WSL） | [rtlsim.py L1-L40](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/rtlsim.py#L1-L40) |
| F-079 | RTL 顶层：otpu_top.sv（多 slice）、otpu_slice.sv（seq+dma+mxu+vpu+mem）、otpu_coll.sv（GATHER/BAR）、otpu_pkg.sv；otpu_seq.sv 每周期按程序序向 WIN（参数默认 16）窗口派发并记录内存足迹（sdep/sdepd/soh 等） | [rtl/top/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/top)、[otpu_seq.sv L39](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/seq/otpu_seq.sv#L39) |
| F-080 | mem 4 文件：otpu_tmem（LANES 个 bank）/otpu_actram/otpu_dram/otpu_native_dram（64B beat、QST 部分写合并、CHASH 通道交织、port-A flush） | [rtl/mem/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/mem) |
| F-081 | shell 6 文件：otpu_board/otpu_ctrl（控制寄存器）/otpu_mem_ch（XDMA 与核的交汇点，保 WAITW 顺序）/otpu_axi_split2/otpu_afifo/otpu_trace | [rtl/shell/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/shell) |
| F-082 | tech 映射：generic/xilinx7(DSP48E1)/xilinxus(DSP48E2)/asic(1R1W macro)；boards：ypcb-00338（otpu_fpga_top_ld LiteDRAM 版+otpu_native_sys）、bcu1525（fpga_top_bcu+bcu_sys）；asic 顶=单 slice+collective，存储端口在边界 | [rtl/tech/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/tech) |
| F-083 | 板卡：浪潮 YPCB-00338，Kintex-7 xc7k480tffg1156-2，2×DDR3-1066（LiteDRAM WL7DDRPHY，核内小 CPU 上电 12 秒自校准两通道），XDMA Gen2 x8，133.33MHz，17.1GB/s 峰值，每 slice 4GiB，64B beat；主机 opentpu（Intel i7-4790） | [ypcb-00338.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/ypcb-00338.toml)、[README L24-L26](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L24-L26) |
| F-084 | 生产镜像 deploy_champ_e698dcd7（2026-09-29 晚起；133.33MHz、LiteDRAM+四列脉动 MXU+stream engine、D=128 MCOLS=4 LANES=8、WNS+0.032/WHS+0.016）；build B deploy_fused133c_79c5707a（09-30 起生产；LFM2-2.6B/SmolLM3/Phi 快 8-9%、E2B 快 10%，DRAM 91-94%）（作者报告） | [README L49-L57](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L49-L57) |
| F-085 | 旧镜像 se-cand3（Xilinx MIG、两列 MXU、120.755MHz）：decode 差 ≤2.3%（DRAM bound，两版都 82-85% 峰值）；prefill 快 1.3x(Qwen3.5)-2.0x(LFM2 4-bit)（作者报告） | [README L87-L95](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L87-L95) |
| F-086 | 主机工具链 11 CLI：otpu-chat/serve/smi/lens/selftest/diag/lock/setup/i2c/memcal/ddr4 | [pyproject.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/pyproject.toml) |
| F-087 | host 29+ 文件：board/offload/chat/chat_tui/smi/diag/selftest/checks/opchecks/ddrcal/selfcal/memcal/streamed/hwlens + litedram/litedram4/pcie 子目录 | [host/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/host) |
| F-088 | 主机几乎不挡路：LFM2/Qwen3 用一次编译的常驻 decode 程序（从寄存器读 position、自找 embedding/RoPE 行，logits 卡运行时流式回传）；主机每 token 仅加 0.17-0.30ms（omarchy；opentpu 0.45-1.3ms）（作者报告） | [README L120-L125](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L120-L125) |
| F-089 | otpu-serve：OpenAI 风格 API（/v1/chat/completions、/v1/completions、流式、SGLang /generate），多客户端上下文留卡/主机 RAM/磁盘，Qwen3 与 Llama 类卡上批量 decode、每 token 卡上选取；Qwen3-0.6B 4 客户端 78 tok/s、单独 25 tok/s（作者报告） | [README L196](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L196) |
| F-090 | Lens：profiler，.otpuprof gzip JSON；kind=rtl（周期精确 trace）/isa（分析串行时序）/board（卡计数器）；浏览器应用 roofline+时间线+逐指令表（busy/等 DRAM/等指令着色）；lens_app.html 随包 | [lens.py L1-L12](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/lens.py#L1-L12) |

## H. 验证体系与性能口径（F-091~F-110）

| F | 事实 | 锚点 |
|---|---|---|
| F-091 | validate.py（1005 行）：CPU golden=同 checkpoint 的 HF transformers fp32 + openTPU 量化；golden 权重=矩阵单元实际相乘值（镜像量化器与所选格式），激活每 128 值在设备量化处 round int8 | [validate.py L100-L322](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py#L100-L322) |
| F-092 | device 可选 isa/rtl(Verilator)/board；--against 加第二设备要求 token 相同+logits 位一致；模型 Qwen3-0.6B/LFM2.5-230M/Qwen3.5-0.8B/Gemma4 E2B(base+instruct)，MoE 不支持 | [README L208-L211](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L208-L211) |
| F-093 | 四行汇总：device vs W+A（主检查）/device vs fp32/W+A vs fp32（纯量化代价）/W+A~ vs W+A（输入拨 1 fp32 ulp 的自对照地板） | [README L236-L241](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L236-L241) |
| F-094 | 指标：top-1 一致率、mean/largest KL（nats/token）、最大 logit 差、最低 cosine；通过判据 top-1≥80% 且 mean KL≤3×floor（--min-top1/--kl-ratio）；PASS=0/FAIL=1；--json/--weights-only/--no-fp32/--save | [README L231-L234](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L231-L234) |
| F-095 | 实测（作者报告）：ISA 模拟器 8 默认 prompt×16 token，设备 KL 为 floor 的 0.70-1.16 倍；一 run 2-14 分钟（16 核），峰值内存 2.5GB(LFM2)-16GB(Gemma4 E2B)；11 行 KL 表 | [README L247-L268](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L247-L268) |
| F-096 | 板卡对拍（build 1025907f，2026-10-07，--no-golden --save 加锁+构建主机 --against）：3 模型 int8 与 4bit-int8head 共 6 run，全部 token 相同+logits 位一致（103-128 step，0 ulp）；卡对量化 golden KL 为 floor 0.94-1.39 倍、top-1 94.5%-97.7% | [README L304-L309](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L304-L309) |
| F-097 | RTL 对 ISA：`validate.py --model lfm2 --backend rtl --against isa --tokens 3`，16 核主机含 Verilator 构建约 4 分钟（作者报告） | [README L218-L220](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L218-L220) |
| F-098 | WAITW 顺序 qual 测试 tools/qual/waitw.py（qual.sh、otpu-diag waitw-host、host/checks.py）：旧数据+失败 flag→启卡等→写新数据再写 flag→LD 必须读新（1-32768 字、EQ/NE/GE/masked、间隔 0/64/1000）；超时须 ERROR 停下 | [isa.md L478-L486](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L478-L486) |
| F-099 | scoreboard 工具：四类等权工作负载（单用户 decode/prefill/多用户批量 decode/MoE，2026-10-11 口径）的硬件 what-if 模型；子命令 report/compare/whatifs/validate/boards/models/fit；参数 --mcols/--act-rows/--mxu-pump/--tmem-words/--rows/-S/--mhz/--mem | [scoreboard.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/scoreboard.py) |
| F-100 | 测试金字塔 78 文件：纯 Python（test_isa/test_compiler/test_fp/test_quant/test_vops/test_kernels…）、Verilator RTL（test_fp_rtl/test_quant_rtl/test_rtl/test_stream_rtl/test_waitw_rtl/test_se_*）、板卡/主机（test_board/test_host*/test_models_on_board_rtl）、serve 7、模型 15 | [tests/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tests) |
| F-101 | 修复配反例文化：recip 校正步针对 recip(1)=0.99999994 驻点；exp2 文档明记 Taylor 系数曾在 f=1 附近偏 13 ulp；Q K smoothing 给出前后 KL（0.042→0.012）；WAITW port-A flush 指向 35B back-to-back embed 失败场景 | [isa.md L92-L100](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L92-L100)、[README L276-L286](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L276-L286) |
| F-102 | 测量口径 tools/qual/perf.py：64 greedy token after 512-token prompt，主机 argmax 在环（不流式）；device 只计加速器周期，wall 加主机；prefill 为 512-token prompt 在设备上；DRAM 流量来自卡自身计数器 | [README L59-L62](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L59-L62) |
| F-103 | 主结果表 18 配置/10 模型（作者报告，2026-09-29~10-01 两镜像）：跨度 LFM2.5-230M int8 59.0/52.3（device/wall tok/s）→Gemma4 E4B 混合 4bit 3.78/3.75；DRAM 82%-94%；E2B PLE 表驻卡（3.5-3.6GiB 镜像，int8 放不下）；E4B 表 2.95GB 留主机每 token 拷 11KB 行进卡 | [README L30-L47](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L30-L47) |
| F-104 | logits 流式口径（tools/decode_profile.py，96 token，4bit device/wall，作者报告）：LFM2 89.5/84.5、Qwen3 33.7/33.3、Qwen3.5 24.6/24.2、LFM2-2.6B 11.07/11.02、SmolLM3 8.92/8.89、Phi 6.69/6.67 | [README L78-L85](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L78-L85) |
| F-105 | MoE 超标称 offload（docs/offload.md §10，2026-10-01 build B，卡自选 token，4-bit 专家 int8 head，作者报告）：LFM2.5-8B-A1B(8.5B/1.7B active) 10.6 tok/s×160 token、98.5% 命中、5.2MB/token；Qwen3.5-35B-A3B(34.7B/3.0B) 3.95 tok/s、HF 16 greedy tokens 一致、62% 命中、153MB/token@1.41GB/s；两者与模拟器逐位一致 | [README L97-L108](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L97-L108) |
| F-106 | chat 支持的 MoE 别名：lfm2-8b/qwen35-35b/gemma4-26b；专家一次性打包到 checkpoint 旁 pool 文件，chat 加载前检查 pool | [README L110-L113](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L110-L113) |
| F-107 | 模型适配 5 模型族（qwen3/qwen35/gemma4/lfm2/llama）+ moe.py/mtp.py；generate.py 为 decode 主循环；prefill/tiled/batch/snapshot/formats/rtl_backend 基础设施 | [opentpu/llm/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/llm) |
| F-108 | Q K smoothing：q/k_norm 增益有 outlier 通道（Qwen3-0.6B 达中位 42 倍），K 按每 token/head/128 量化时其他通道只剩几级；修复把 outlier 幅度以 2 的幂/通道从 K 移入 q（q·K 不变）；配对文本 int8 W+A KL 0.059→0.015、4-bit 0.221→0.179（作者报告） | [README L276-L286](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L276-L286) |
| F-109 | Gemma4 特殊处理：PLE（per-layer embedding）表，golden 从 LM head 取 embedding 行、设备从 PLE 记录取每层嵌入、soft cap 后比 logits；E2B fp32 约 20GB，bf16 权重保 bf16；E4B-it 2026-10-09 起默认头+前 12 层 gate/up 4-bit（同字节数、困惑度差 0.01% 而非 +3.2%、prompt 2 行而非 3-4） | [README L63-L72](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L63-L72)、[README L288-L295](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L288-L295) |
| F-110 | 未来工作：DRAM 最后几个百分点、时序余量与面积（133.33MHz WNS+0.032 仅勉强收敛）、更快 prefill（四列阵列已上，受乘率限）、更多 target | [README L324-L337](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md#L324-L337) |

## I. 多 target 与 ASIC（F-111~F-118）

| F | 事实 | 锚点 |
|---|---|---|
| F-111 | target 体系：每构建一个 targets/*.toml，target.py 单加载器（Target/load/by_platform/current/config/rtl_params/sources/build_config），OTPU_TARGET 选择（默认 ypcb-00338），派生 RTL 参数/Vivado generics/模拟器配置/主机期望；platform_id 经 CFG_PLATFORM 寄存器 | [target.py L82-L292](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/target.py#L82-L292) |
| F-112 | target 四段：[target] name/kind(fpla|asic)/platform_id；[arch] 程序可见参数；[uarch] 仅时序 RTL 参数（MXU_IMPL/CL/E、VPU_CL、ULANES、TMEM_IMPL、RPB/WPB、WIN、FIFO_DEPTH、TRACE_DEPTH、PQ_WIN、CHASH）；[tech]；[platform] board/core_mhz/mem/channel | [targets/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets) |
| F-113 | bcu1525（bring-up 计划，尚未通）：Virtex UltraScale+ xcvu9p-fsgd2104-2L-e（VU9P），4×DDR4 RDIMM（单条 16GiB MTA18ASF2G72PZ），XDMA Gen3 x16；架构 S=2（4 通道）D=128 MCOLS=4；开发构建先 100MHz（DDR4-1600；条为 DDR4-2400） | [bcu1525.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/bcu1525.toml) |
| F-114 | nangate45：FreePDK45 预测工艺包（不可制造，PPA 参考/流片排练）；架构=板卡架构（S=1 D=128 MCOLS=4），故 token-exact 同一套测试；TMEM 用 LANES 个 1R1W macro（TMEM_IMPL=1），MXU generic；目标 400MHz | [nangate45.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/nangate45.toml) |
| F-115 | nangate45-small：shuttle 尺寸小核 D=32×MCOLS=2、4 lanes、64KiB TMEM、1K 指令、256MiB DRAM、268MB 通道；VPU_CL=1、FIFO 64 | [nangate45-small.toml](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/nangate45-small.toml) |
| F-116 | ASIC 流程：OpenROAD-flow-scripts（OpenROAD/OpenSTA/yosys+slang/KLayout + nangate45/fakeram45），参考固定修订 f395e4b6；native（Ubuntu 26.04，ORFS 构建约 20 分钟/20 核）或 Docker 6.5GB；rtl/asic/otpu_asic_top.sv=单 slice+collective、存储端口在边界 | [asic/nangate45/README.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/asic/nangate45/README.md) |
| F-117 | PPA（作者报告，E 阶段据 asic.md 原表勘误归属）：**nangate45-small 已布线签收**——reg-reg 2.39ns=419MHz（2.5ns 无违例）、含端口 2.95ns=339MHz（sw_req 单点）、400MHz vectorless 0.79W（时序 0.28/时钟 0.20/组合 0.15/macro 0.16，漏电 21mW）、0 DRC，die 2.65×2.65mm=7.02mm²；同日 native ORFS（f395e4b6）复跑 422/341MHz 同值在工具噪声内，报告在 results/small/。**板卡架构大核（nangate45）仅到 CTS、未布线**——reg-reg 5.60ns=178MHz（clock skew 2.7ns）、含端口 6.40ns=156MHz，400MHz 假设 vectorless 3.34W（时序 1.09/时钟 0.93/macro 0.87/组合 0.46，漏电 82mW），die 5.53×5.53mm=30.6mm²。R 阶段曾把 419/339 误归大核、误记结果目录 cand2_3p3ns/，均已更正 | [asic.md L58-L71](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/asic.md#L58-L71) |
| F-118 | 多 target 设计决策文档 docs/superpowers/specs/2026-10-10-multi-target-design.md（D1-D8）；as-built 设计规格 2026-09-23-opentpu-design.md（其中 S=2/MCOLS=8/WIN=32 是 09-23 时点，已被 target 体系取代） | [docs/superpowers/specs/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/superpowers/specs) |

## J. 文档生态与能力位（F-119~F-123）

| F | 事实 | 锚点 |
|---|---|---|
| F-119 | docs 36 篇：isa/compiler/quant/formats/mx_mxu/mxu_study/mxu_systolic/stream/scoreboard/offload/mtp/prefill/tiled_prefill/autodecode/flash/board/host/targets/bcu1525/asic/lens/observability/benchmarks/serve/status/tourney/vpu_pump/wide_dram/litedram + 模型文档 lfm2/qwen35/llama/gemma4/gemma4_e4b；img/ 与 data/ 资源 | [docs/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs) |
| F-120 | CAPS 能力位：bit6=DSTEP、bit25=运行参数（控制寄存器 0x060+4k）、bit26=STREAM、bit27=主机校准、bit31=WAITW(RTL)；完整位表在 docs/observability.md 寄存器表 | [isa.md L31-L373](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L31-L373) |
| F-121 | 控制/观测：otpu_ctrl.sv 控制寄存器；hwtrace.py/profile.py/hwlens；TRACE_DEPTH 生产 16384 | [docs/observability.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/observability.md) |
| F-122 | 构建：`make -C boards/ypcb-00338 bit`，可覆写 MCOLS/VPU_CL/DDR/BUILD_ID/CORE_MHZ；Vivado 2026.1 需覆盖 xc7k480t 的许可；一次 1.5-3h，先看 build/vivado/reports/SUMMARY.txt 的 WNS/WHS | [board.md L31-L58](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/board.md#L31-L58) |
| F-123 | 部署支持 BPI flash 镜像；boards/ 含 ypcb-00338 与 bcu1525 两目录 | [boards/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/boards) |

## 相关概念

- [源码地图与基线对账](source-code-map.md)
- [架构洞察四元组](insights.md)
- [V 阶段验证报告](verification.md)
