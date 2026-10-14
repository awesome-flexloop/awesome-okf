---
okf_version: "0.2"
type: Concept
title: "RVFI NRET=2 契约：双通道退休顺序与不可焊死规则"
description: "核顶层 NRET=2 的 RVFI 退休端口契约：ch0/ch1 老幼顺序、单退休落 ch0、两套 wrapper 与毫秒级防焊死预检"
tags: [HWE Bench, RVFI, NRET, riscv-formal, 硬件契约]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T16:20:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-14T19:30:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-facts
    resource: /references/facts.md
    title: "HWE Bench 事实登记表 F-001~F-126"
  - id: hwe-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb"
---

## 是什么：NRET 就是一周期几条退休通道

RVFI 是 riscv-formal 消费的一组标准化退休端口：order、指令字、PC/下一 PC、读写寄存器、访存地址/掩码/数据、trap/halt/intr/mode/ixl 等，核内部怎么实现不管，只要把「每个周期退休了什么」按这组端口吐出来（F-045）。wrapper 的注释把职责写得很直白：每条 RVFI 输出经 `RVFI_OUTPUTS` 宏接进 riscv-formal 检查框架，框架直接读这组信号跑 insn/reg/pc_fwd/unique/liveness/ill 等检查，且对 RVFI 输出**不加任何 assume**——DUT 报出错误地址或下一 PC，求解器就能找到（[wrapper.sv L1-L9](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper.sv#L1-L9)、[L36-L37](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper.sv#L36-L37)，F-045）。

`nret` 是这套端口的宽度：一个周期允许退休几条指令。HWE Bench 的默认值是 **2**（F-045）。双发核同周期退休两条时，必须有两条独立通道承载；即使当前核按单发射工作，端口契约仍按 NRET=2 声明，给后续双发射假设留出同一套验证夹具——README 把「clock/reset、imem/dmem、NRET=2 RVFI」列为顶层唯一不可变的 I/O 契约（F-021）。

契约在七门流水线里有三个强制点（F-001、F-042）：

1. cocotb smoke test 做基本连通性，验证核顶层确实按 nret 暴露端口；
2. riscv-formal wrapper 接符号 BMC，是契约的主要强制者；
3. 构建之后、慢速 formal 之前还有毫秒级 rvfi_lint 模式预检，拦截高发低级错（F-066）。

wrapper、checks.cfg、run_all.sh 等 formal 六件进 don't-touch 清单，agent 改不到；碰它们会在任何评测运行之前被路径沙箱拒绝（F-022、F-043）。

## 怎么实现：老幼顺序、单退休落 ch0、无 X/Z

不变量 #1 对双通道行为定了三条硬规则（[CLAUDE.md L11](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CLAUDE.md#L11)，F-045）：

1. **老幼顺序**：同周期两条退休，channel 0 承载较老指令、channel 1 较年轻；配套的不变量 #4 要求 `rvfi_order` 跨两通道严格 +1 单调，同周期 ch0=N、ch1=N+1（[CLAUDE.md L14](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CLAUDE.md#L14)）。
2. **单退休必须落 ch0**：只有一条退休的周期，指令必须出现在 ch0 且 `io_rvfi_valid_1=0`，不能落到 ch1。
3. **ch1 所有端口必须被驱动**：无 X/Z，未用字段 tie `'0`。

它只是 [CLAUDE.md L9-L21](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CLAUDE.md#L9-L21) 那张 10 条硬不变量表的第 1 条；其余各条一句话带过：非法指令必 trap（#2）、仅 EBREAK 是合法 SYSTEM 指令（#3）、order 单调（#4）、符号流下必须前进（#5）、访存区间（#6）、CoreMark CRC（#7）、计时括号（#8）等，每条都注明由哪个检查强制，且全部来自上一代 Chisel 实现的真实 bug（F-042）。

顺序纪律在 formal 侧还有两道配套检查：`unique` 抓两条退休共享同一 `rvfi_order`（双退休），`cover` 要求至少存在一条非 trap 退休轨迹，防止整个检查集在「核什么都不退休」上真空通过（F-048，checks.cfg 注释对两项的用途有逐行说明）。

## 两套 wrapper：102 行路由切片与 72 行整宽连接

formal/ 下为两种 nret 维护两套 wrapper（F-046）：

- [wrapper.sv](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper.sv#L55-L99)（102 行，NRET=2）：把 riscv-formal 打包总线按位切片——ch0 取低段（`rvfi_valid[0]`、`rvfi_order[63:0]`…），ch1 取高段（`rvfi_valid[1]`、`rvfi_order[127:64]`…），注释说明高通道就是打包在高位区间（亲验 L55-L99）。取指数据由 `rvformal_rand_reg` 符号寄存器自由驱动，dmem 则是具体的 8 KiB 寄存器数组（亲验 [L17-L21](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper.sv#L17-L21)）。
- [wrapper_si.sv](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper_si.sv#L45-L69)（72 行，nret=1）：核上不存在 `_1` 端口，`_0` 端口与单宽 RVFI 总线整宽直连，无需切片（亲验 L45-L49）。

两套 wrapper 都把 imem/dmem ready tie 高：riscv-formal 建模零等待总线，注释解释随机 ready=0 只会撑爆 SMT 搜索空间而不增加该框架检查的性质（亲验 [wrapper.sv L44-L54](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper.sv#L44-L54)）；随机反压属于 cosim 层的职责（F-059）。

选哪套由 [tools/eval/formal.py L20-L36](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/formal.py#L20-L36) 读 `cores/<target>/core.yaml` 的 `nret` 字段路由：缺省 2（兼容早于 nret 夹具的全部既有核），只接受 1/2，其他值直接报错（F-046）。bench 夹具核就是 nret:1 的实例（F-093）。

## 为什么需要 rvfi_lint：防通道被焊死骗过 formal

最容易写错的形状是「把 ch0 用常量 tie 0」——它正是合法单发射写法（tie ch1）的镜像，一次索引接反就会发生（[rvfi_lint.py L8-L13](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/rvfi_lint.py#L8-L13)）。[rvfi_lint.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/eval/rvfi_lint.py#L19-L67)（67 行）是构建之后、慢速 formal 之前的毫秒级模式预检：正则扫描 RTL，禁止 `assign io_rvfi_valid_0 = '0/1'b0/0;` 三种裸常量焊死（亲验 L27-L30），命中即失败并提示「Did you mean io_rvfi_valid_1?」。没有它，同类坏实现要白烧约 30 分钟 riscv-formal，最后只得到一个 `*_ch0 PREUNSAT`（F-066）。

## 与 PREUNSAT 空过判定的关系

NRET 契约会制造一类合法的「真空成立」：单发射假设把 `io_rvfi_valid_1` tie 0 后，ch1 检查的前提（valid_1=1）不可满足，SBY 报 `Status: PREUNSAT`（rc=16）；[run_all.sh L178-L195](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/run_all.sh#L178-L195) 规定 `_ch1` 结尾的检查遇 PREUNSAT 仍计 PASS——属性在空集上成立是合法通过（F-052）。但 PASS+FAIL=0 时强制 FAIL 为 `no_checks_generated`，防 genchecks 崩溃只产出一个空过任务（F-053）。这套空过分类的完整口径见 [05-formal-altops](/concepts/05-formal-altops.md)。

## 边界与口径

- 契约管的是**退休可见性**：端口宽度、老幼顺序、order 单调、X/Z 纪律；它不规定微架构怎么发射、怎么停顿、怎么做前递（F-021、F-045）。
- 契约**不证明指令语义正确**：RVFI 忠实地吐出错误结果照样满足端口契约。算术与控制流正确性由 formal 各检查、cosim 逐字段对拍兜底（F-050），见 [05-formal-altops](/concepts/05-formal-altops.md) 与 [06-cosim-iss](/concepts/06-cosim-iss.md)。
- lint 只挡「裸常量 tie ch0」这一种已知高发形状，不证明通道被真实驱动；后者由 formal 的 cover/insn 检查与 cosim 负责（F-053、F-066）。
- 同一 nret 字段同时路由三处夹具：formal wrapper/checks、cosim 构建的 `-DNRET` 宏、FPGA 的 core_bench(_si).sv；三处必须一致，通道语义才跨层对齐（F-046、F-060）。

## 相关概念

- [riscv-formal 分层：ALTOPS 替身、检查数三口径与空过分类](/concepts/05-formal-altops.md)
- [cosim 对拍：Verilator C++ 仿真器与 Python RV32IM ISS](/concepts/06-cosim-iss.md)
- [worktree 隔离与路径沙箱](/concepts/03-worktree-sandbox.md)
