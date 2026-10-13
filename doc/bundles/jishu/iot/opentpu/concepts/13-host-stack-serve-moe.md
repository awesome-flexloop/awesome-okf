---
okf_version: "0.2"
type: Concept
title: "主机软件栈：chat/serve、卡上批量与 MoE 专家流 offload"
description: "11 个 CLI 驱动真实 PCIe 卡：常驻 decode 程序让主机几乎不挡路，otpu-serve 做卡上批量，MoE 大模型靠 WAITW 邮箱把专家按缺失从主机池流式拷入。"
tags: [openTPU, host, otpu-chat, otpu-serve, MoE, offload, mailbox]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T17:00:00+08:00"
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

## 主机在这套架构里的位置

openTPU 的主机软件不是「演示脚本」，而是六层链的最外层：它装载程序、喂 run 参数、在 decode 进行中流式读回 logits、在 MoE 场景下还充当按需取数的专家服务器。代码集中在 [host/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host)（29+ 文件，含 litedram/litedram4/pcie 子目录）、[opentpu/serve/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/serve)（api/batching/scheduler/kvio/store）与 [opentpu/llm/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/llm)（15 个文件）。全部入口在 [pyproject.toml L13-L24](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/pyproject.toml#L13-L24)，共 **11 个 CLI**：

```text
otpu-chat      对话/跑 greedy 生成        otpu-serve    OpenAI 风格 API 服务
otpu-smi       温度/功耗/带宽/利用率      otpu-lens     profiler 记录与浏览
otpu-selftest  卡自检                     otpu-diag     诊断（含 waitw-host 组）
otpu-lock      独占卡（跨进程验证加锁）   otpu-setup    PCIe 设备 setup
otpu-i2c       I2C（温度传感器等）        otpu-memcal   DDR3 主机校准
otpu-ddr4      BCU1525 的 DDR4 LiteDRAM 校准
```

host/ 内部按职责分：`board.py` 是逻辑地址的 DRAM 访问、程序装载与 run/计数器/ trace 抽象；`offload.py` 是专家服务器；`chat.py/chat_tui.py` 是对话；`smi.py/diag.py/selftest.py/checks.py/opchecks.py` 是观测与诊断；`ddrcal.py/selfcal.py/memcal.py/streamed.py/hwlens.py` 是校准、流式 logits 与 profiler 接线。模型侧 15 个文件覆盖五个适配族 `qwen3/qwen35/gemma4/lfm2/llama`，加 `moe.py/mtp.py`，以及 `generate/prefill/tiled/batch/snapshot/formats/rtl_backend` 与 `__init__.py` 共八个基础设施文件；decode 主循环就是 [opentpu/llm/generate.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/llm/generate.py)。

## 常驻 decode 程序：主机为什么几乎不挡路

对 LFM2 与 Qwen3，卡上运行的是**一次编译、常驻 IMEM 的 decode 程序**：位置不通过立即数传入，而由程序在运行时从寄存器（R8..R15 的 run 参数，CAPS bit25）读取；embedding 行与 RoPE 行由卡自己查找；logits 在卡仍在运行时流式回传主机。HALT CHAIN（见 [sequencer 概念](/concepts/03-sequencer-and-chaining.md)）让 attention 各 bucket 程序互相链接，主机视角始终是一次 run。

作者报告（README，omarchy 主机）：这条路径主机每 token 只增加 **0.17-0.30 ms**；另一台主机（opentpu，Intel i7-4790）为 0.45-1.3 ms。注意区分两套计时口径：`tools/qual/perf.py` 的 512 prompt+64 greedy 把主机 argmax 放在环内、非流式，device/wall 分列；`tools/decode_profile.py` 的 96 token 口径则是卡自选取、logits 流式。Qwen3.5 的 decode 同样常驻，但 prefill 仍由主机提前逐 chunk 编译程序。

## otpu-serve：OpenAI 风格 API 与卡上批量

[serve/api.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/serve/api.py) 基于标准库 `ThreadingHTTPServer` 实现，端点包括 `POST /v1/chat/completions`、`POST /v1/completions`（支持流式与非流式、n choices、stop）、SGLang 原生的 `POST /generate`，以及 `GET /v1/models`、`/health`、`/v1/stats`。多客户端的上下文保留在卡上、主机 RAM 与磁盘三级存储（scheduler/kvio/store），接续已保存上下文只喂剩余部分；Qwen3 与 Llama 类模型把多个客户端的 decode step **批量放在卡上**，每个 token 仍由卡选取。作者报告：Qwen3-0.6B 在 4 客户端时合计 **78 tok/s**，单客户端 25 tok/s。

## MoE 专家流：卡路由、卡算全部专家、主机只搬缺失块

卡的每 slice DRAM 为 4 GiB，装不下 LFM2.5-8B-A1B、Qwen3.5-35B-A3B 这类 MoE。方案（[docs/offload.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/offload.md) §10、[host/offload.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/host/offload.py)）的分工刻意不对称：

- **卡上做路由**：router MM 出 E 个分数，VOP 上按模型规则选择（LFM2 为 sigmoid 加专家偏置，Gemma4 为 softmax），`LOOP` 内 k 次 ARGMAX 加「淘汰位填 -3e38」得到按序的 k 个专家 id；
- **卡上算全部专家**：每层在卡 DRAM 里有固定的专家槽位，命中的立刻算，未命中的等到主机 DMA 落地后立刻算，其余专家继续流式；
- **主机只搬数据**：守护进程轮询邮箱，对目录中缺失的专家，从 checkpoint 旁一次性打包好的 **pool 文件**（卡槽位格式，`PoolFile`；缺页由 page cache 兜底）按 LRU 选一个本请求未点名的受害者槽，清目录项，DMA 专家，再写回 `{槽地址, 1.0}`，最后置 `served = seq`。

卡侧的同步原语是一个 fp32 字邮箱，实现在 [kernels/mailbox.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/mailbox.py)，全文很短：

```python
TIMEOUT = 1 << 30       # 周期（133.33 MHz 下约 8 秒）：停服的主机应表现为 WAIT_TO 错误

def wait_served(mbox, comment="fence: served >= seq", timeout=TIMEOUT):
    seq = ol.load(Tensor(Affine(mbox), (1,), (1,)))
    word = ol.empty((1,))
    r = b.scratch()
    b.rld(r, seq, raw=True, comment="seq (bits)")
    b.waitw(word, mbox + 2 * LINE, 0, I.C_GE, rc=r, timeout=timeout, comment=comment)
    ...
    return seq

def post(mbox, ids):
    seq = wait_served(mbox)                       # 先 fence：主机已服完此前所有请求
    ol.store(Tensor(Affine(mbox + LINE), ...), ids)  # 再写请求行
    seq.set(seq + 1.0)
    ol.store(Tensor(Affine(mbox), (1,), (1,)), seq)  # 最后写 seq：主机不会读到撕裂请求
```

`LINE = 64`（单位是 fp32 **字**，即每段间距 256 字节）：seq、请求行、served 各占一个 64 字段落，且互不与对方共享 64 字节 beat（上游注释的 "their own 64-byte lines" 即指此）。正 fp32 的位序即数值序，所以 `served >= seq` 可以直接用 WAITW 的 GE 比较。seq 只在 2^24 内精确递增，因此到 `SEQ_REBASE = 1<<23` 后主机会在两次 run 之间把 seq/served 归零（`ExpertServer.rebase`）。槽地址是原始 32 位，绝不能过 VPU（会被当非规格数冲洗）：WAITW 把它从目录复制到 TMEM，RLD RAW 整位取进寄存器。协议为什么无竞争：每层有自己的槽，fence 之后主机对该层槽唯一可能的写就是本次请求点名的专家，而卡只在本层两次 fence 之间使用槽。

作者报告（2026-10-01，build B `deploy_fused133c_79c5707a`，卡自选取，4-bit 专家、int8 头）：**LFM2.5-8B-A1B**（8.5B 参数、1.7B 激活）160 token 上 10.6 tok/s，98.5% 的专家使用命中槽位，每 token 流式传输 5.2 MB；**Qwen3.5-35B-A3B**（34.7B、3.0B 激活）3.95 tok/s，与 Hugging Face 的 16 个 greedy token 一致，命中率 62%，每 token 153 MB、PCIe 实测 1.41 GB/s。两者都与模拟器**逐位一致**。chat 的 MoE 别名是 `lfm2-8b`、`qwen35-35b`、`gemma4-26b`；chat 加载前检查 pool 是否已打包。

## 边界与验证口径

位精确验证工具 `tools/validate.py` 明确**不支持 MoE**（模型集为 Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B、Gemma4 E2B base/instruct）；MoE 的正确性走 chat/offload 路径与模拟器对拍。静态阅读这一软件栈时还应注意：所有吞吐数字均为作者报告、绑定镜像与日期；本教程未运行 CLI、未连接 FPGA。

## 相关概念

- [sequencer：顺序派发、WIN=16 足迹窗口与 HALT CHAIN 常驻程序](/concepts/03-sequencer-and-chaining.md)
- [STREAM/DSTEP 状态引擎、WAITW 轮询与 CAPS 能力位](/concepts/12-stream-dstep-caps.md)
- [位精确验证体系：validate 四行表、KL 判据与 78 文件测试金字塔](/concepts/16-verification-system.md)
- [板卡与多 target：YPCB-00338、镜像演进、bcu1525、Lens 与 scoreboard](/concepts/14-board-and-targets.md)
- [示例：MoE 专家流的 WAITW + mailbox fence 协议](/examples/02-moe-mailbox-waitw.md)
- [openTPU 事实登记表 F-001~F-123](/references/facts.md)
