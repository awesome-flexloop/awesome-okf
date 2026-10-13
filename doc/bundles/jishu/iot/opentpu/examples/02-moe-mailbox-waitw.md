---
okf_version: "0.2"
type: Example
title: "示例：MoE 专家流的 WAITW + mailbox fence 协议"
description: "读 kernels/mailbox.py 的 wait_served/post 全文，走读 MoE 专家按需入卡的槽位标签协议、WAITW 字段、port-A flush 修复与 qual 反例"
tags: [openTPU, 示例, MoE, WAITW, mailbox, offload, fence, 专家流]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T17:20:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-facts
    resource: /references/facts.md
    title: "openTPU 事实登记表 F-001~F-123"
  - id: opentpu-source-map
    resource: /references/source-code-map.md
    title: "openTPU 源码地图与信源固定"
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

当专家总大小超过卡上 4GiB（LFM2.5-8B-A1B、Qwen3.5-35B-A3B 这类 MoE），openTPU 的策略是：卡自己路由出本 token 需要的专家，缺谁让主机按槽位 DMA 进来，命中的直接算。卡与主机之间没有中断、没有门铃寄存器，只有 DRAM 里的几个字和一条 WAITW 指令。本示例读 [kernels/mailbox.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mailbox.py#L1-L37) 全文走通这套 fence 协议，对应事实 F-023、F-098、F-105、F-071。本文为静态走读，不连板卡、不运行 qual。

## 邮箱布局：三个不共享 64 字节 beat 的字行

主机侧布局常量在 [host/offload.py L88](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/offload.py#L88-L98)：`LINE = 64`（64 个 fp32 字）。一个邮箱就是三个间隔 64 字（256 字节）的位置，各自不与对方共享 64 字节 beat：`mbox` 放 `seq`（卡最近一次请求号），`mbox + LINE` 是请求行（k 个专家 id），`mbox + 2*LINE` 是 `served`（主机已完成到第几号请求），构造逻辑见 [`Layout`](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/offload.py#L446-L463)。

## 卡侧全部代码：wait_served 与 post

整个邮箱的卡侧只有 37 行（[mailbox.py L16-L37](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mailbox.py#L16-L37)）：

```python
TIMEOUT = 1 << 30       # cycles (8 s at 133.33 MHz)

def wait_served(mbox: int, comment: str = "fence: served >= seq", timeout: int = TIMEOUT):
    b = current()
    seq = ol.load(Tensor(Affine(mbox), (1,), (1,)))
    word = ol.empty((1,))
    r = b.scratch()
    b.rld(r, seq, raw=True, comment="seq (bits)")
    b.waitw(word, mbox + 2 * LINE, 0, I.C_GE, rc=r, timeout=timeout, comment=comment)
    b.unscratch(r)
    return seq

def post(mbox: int, ids) -> None:
    seq = wait_served(mbox)                       # 先 fence：主机的请求行已空
    ol.store(Tensor(Affine(mbox + LINE), (ids.rows * ids.cols,), (1,)), ids)
    seq.set(seq + 1.0)
    ol.store(Tensor(Affine(mbox), (1,), (1,)), seq)
```

逐句读：`wait_served` 先把 `seq` 取进 TMEM，用 `RLD` 的 RAW 形式把它的原始位搬进暂存寄存器 `r`（f2i 会改值，这里要的是位）；随后一条 WAITW 在 `mbox + 2*LINE`（即 `served`）上轮询，条件是 `served & mask >= r`（GE，比较的是 32 位有符号差）。`post` 严格分两次 ST：先写 id 行、再写 `seq + 1`，主机永远看不到半截请求。seq/served 用 fp32 存：非负浮点的位序与数值序一致，所以 GE 直接可用；fp32 只精确数到 2^24，主机在 `SEQ_REBASE = 1<<23` 时于两次 run 之间把两者归零（[offload.py L89-L90](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/offload.py#L88-L98)）。超时取 `1<<30` 周期——133.33MHz 下约 8 秒，主机停止服务时卡以 WAIT_TO 报错停下，而不是把 run 永久挂起。

## WAITW 字段如何表达这个 fence

指令构造器 [isa.waitw](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py#L145-L154) 的签名即字段表：

```python
def waitw(dram, tmem, ref, cmp, ra=0, rb=0, rc=0, mask=0xFFFFFFFF, interval=0, timeout=0, ...)
```

DMA 反复读 `M32[R[ra]+dram]`，直到 `cmp(v & mask, R[rc] + ref)` 成立（EQ/NE/GE 在 flags[1:0]，常量 `C_EQ/C_NE/C_GE = 0/1/2`），成立后把该字的位写入 `T[R[rb]+tmem]`；`interval` 是两次读取的间隔周期（首次立即读），`timeout` 为超时周期（0 表示不限）。邮箱 fence 用上的只是 `dram = 2*LINE`、`cmp = C_GE`、`ref = 0`、`rc` 指向 seq。文档语义见 [isa.md L432-L486](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L432-L486)（F-023）。

## 协议全景：卡路由，主机服务

[docs/offload.md §5.2](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/offload.md#L387-L455) 把每层 MoE 的协作定为七步：路由（router MM + VPU 规则 + k 次 ARGMAX 选出专家 id）→ fence（`served >= seq`）→ post（id 行后写 seq+1）→ 查目录（每项 8 字节，RLD 取偏移、LD 读 present flag）→ 命中先算 → 缺失再算 → 按路由序加权合并。主机守护进程只搬数据：轮询 seq、读 id、对缺失项选 LRU 受害者、写 `{0,0}`、DMA 专家进槽、写 `{槽地址,1.0}`，最后 `served = seq`。

两个细节值得专门看：其一，槽位地址**绝不经过 VPU**——它会被当非规格数冲掉；命中项的 WAITW（`NE 0`）把目录项的地址字直接复制进 TMEM，RLD RAW 再搬进寄存器，专家 MM 以「该寄存器 + 固定偏移」运行。其二，无竞争靠的是时序窗口：fence 通过后，主机对该层槽位唯一的写操作就是卡即将发出的这个请求，而请求里点名的专家不会被驱逐；每层独立槽池，卡只在两次 fence 之间使用该层槽位。

## port-A flush 修复与 qual 反例

这套协议对硬件的要求是：WAITW 看到主机在 h2c DMA 完成后写的字，则其后所有年轻的 MM/LD 必须读到这次 DMA 的新数据。主机按「数据先、flag 后」排序，卡按「flag 先、读后」排序，两者在 `otpu_mem_ch` 与 LiteDRAM 交汇。曾有过真实失败：板卡 DRAM 适配保留了 port A 的最后一拍与读串（MXU 的 scale 读在这条端口上），主机写达不到它；没有 port-A flush 的位流（生产镜像至 g2fix `0885d436`）在「35B 背靠背 embed」场景下，WAITW 之后第一条 scale 读会拿到旧数据（[isa.md L448-L456](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md#L448-L456)）。修复后，WAITW 成立时与 run 启动/程序加载一样丢弃这些保留拍（`otpu_native_dram` 的 `a_flush`）。

反例固化在 [tools/qual/waitw.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/qual/waitw.py#L26-L45)，先查 CAPS bit31 再跑三组检查。参数来自 [host/checks.py L202-L241](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/checks.py#L200-L241)：每轮先写**旧数据 + 让比较失败的 flag**、启卡并确认它在等、再写**新数据、最后写 flag**，随后卡的 LD 必须读到新数据；数据规模 `W_SIZES=(16,17,1000,4096,32768)` 字、起始字偏移 0..15，比较覆盖 EQ/NE/GE/掩码 EQ 四种（`W_KINDS`），轮询间隔 0/64/1000 周期，flag 落在两个通道；`waitw_timeout` 验证永不成立的 WAITW 在超时点以 HALTED+ERROR+WAIT_TO(bit8) 停下且下一 run 正常。`--tag-rounds` 还复现 §10.11 的更难场景：tag 位于承载 1-4MiB 数据的 DMA 最后一拍（[L300-L381](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/checks.py#L300-L381)），检查 tag 前后各通道采样拍必须是新数据。

## 为什么「token 相同 + logits 位一致」是最终验收

fence 协议的正确性不能只靠「程序逻辑看起来对」：模拟器把 WAITW 按序执行，并在所有能跑的 slice 都等待时回调主机（`Machine.host`），因此同一份 MoE 程序可以在模拟器与卡之间做逐位对拍——主机服务顺序、槽位替换、目录项时序的任何偏差，都会在某一步的 logits 上翻位。README 记录的作者报告（docs/offload.md §10，2026-10-01 build B，F-105）：LFM2.5-8B-A1B（8.5B 总参/1.7B 激活）10.6 tok/s、98.5% 命中、5.2MB/token；Qwen3.5-35B-A3B（34.7B/3.0B）3.95 tok/s、62% 命中、153MB/token@1.41GB/s、HF 16 个 greedy token 一致；**两者均与模拟器逐位一致**。协议、修复与反例，最终都收敛到这一条位级验收上。

## 相关概念

- [/concepts/12-stream-dstep-caps.md](/concepts/12-stream-dstep-caps.md)：WAITW 字段细节与 CAPS bit31 能力位
- [/concepts/13-host-stack-serve-moe.md](/concepts/13-host-stack-serve-moe.md)：主机软件栈、常驻 decode 与 MoE offload 全貌
- [/examples/01-bitexact-crosscheck.md](/examples/01-bitexact-crosscheck.md)：validate 的位级对拍方法（MoE 不在其模型面内）
- [/references/facts.md](/references/facts.md)：F-023、F-071、F-098、F-105 事实条目
