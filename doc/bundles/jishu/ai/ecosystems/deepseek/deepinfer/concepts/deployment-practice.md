---
type: concept
scope: deepinfer
name: DeepInfer 大规模部署实践
version: "0.1.0"
source: 知乎技术报告《DeepSeek V4.1 Flash 大规模推理部署实践》
description: 生产推理系统架构——四层负载均衡、KVCache 存储（Block/SWA 双轨）、自动扩缩容与容错
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践（DeepSeek 官方技术报告，2026-10-20）
  - id: dualpath-paper
    title: "DualPath: Accelerating Agentic LLM Inference by Harvesting Disaggregated KV-Cache Storage I/O（ACM SIGCOMM 2026，ISBN 979-8-4007-2467-1）"
  - id: 3fs-github
    resource: https://github.com/deepseek-ai/3FS
    title: 3FS 分布式文件系统
  - id: v41-report
    resource: https://arxiv.org/abs/2609.19969
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
---

# 大规模部署实践（生产视角）

> 本章内容源自 DeepSeek 官方知乎技术报告，描述的是**生产系统**（含未开源的 KVCache 存储与负载均衡组件）的设计。开源版 DeepInfer 未包含这些组件，但理解其设计是从"离线引擎"走向"生产服务"的关键。

---

## 一、生产运营数据

- 单一集群服务吞吐：**155 万亿 Tokens/天**
- 整体收入：**每卡每小时 38 美金**（按谷价）

## 二、系统架构总览

```
用户请求 ──→ DeepSeek Recipe（协议↔token 编解码）
              │
              ▼
   ┌───────────────────────────────┐
   │  VE / Prefill / Decode 分离部署  │ ← 三阶段独立扩缩容
   │  Prefill: EP2~8/DP2~8 (8卡机)   │
   │  Decode:  EP64~128 (超节点)      │
   │  VE:      单卡（最便宜的卡）       │
   └───────┬───────────────────────┘
           │ KVCache 复用
           ▼
   ┌───────────────────────────────┐
   │  KVCache Storage               │
   │  Block KVCache → 3FS 集群       │
   │  SWA KVCache  → 本机内存         │
   └───────────────────────────────┘
   四个负载均衡器：Prefill LB / Decode LB / VE LB / Expert-Parallel LB
```

ATTN 部分使用数据并行 DP（#DP = #EP），继承 V3/R1 推理系统；不同 DP/EP 之间由四个负载均衡器调度；KVCache Storage 节省重复 prefill 成本。

## 三、四层负载均衡

### 3.1 Prefill Load Balancer（4 层机制）

围绕**拟合的注意力子层计算量**（compute-quota，二次代价模型 `cost(q, c)`，q = 序列未命中 token 数，c = 已算完的前缀长度）路由：

1. **分桶**：输入总长分 4 档（<16K / 16-64K / 64-256K / ≥256K），每档引擎台数按上一轮 compute-quota 需求占比动态重分；
2. **DP 组间**：按剩余 compute-quota 拉取；任何引擎都能命中任何前缀，**不做前缀亲和路由**；
3. **DP 组内**：请求到达即分发到当前 compute-quota 负载最低的 DP rank；
4. **单卡内**：FIFO 出队，chunk size 不固定、由预算反解——每步有时间预算（纳秒），用 `cost(q, c)` 预测耗时，对 q 反解二次方程取正好满足剩余预算的最大 q。

### 3.2 Decode Load Balancer

对所有 decode 实例的所有卡**统一路由**，同时均衡两个维度：请求数（决定每步批大小）与 KVCache 总长度（决定注意力代价）。启发式：短请求发给并发较小且 KVCache 总长偏大的卡，长请求发给 KVCache 总长较小的卡（组内调度参考 DualPath）。

### 3.3 Vision Encoder Load Balancer

图片路由以**单台机器**为单位：prefill 机器随机选一台部署 vision encoder 的机器，机器内把图片交给当前处理图片 patch 数最少的卡（patch 数由 `(width/patch_size) × (height/patch_size)` 直接算出）。

### 3.4 Expert-Parallel Load Balancer

- **机制**：每卡常驻专家之外多备冗余专家放热门专家副本；统计最近 N 步各专家负载，每 M 步重排专家到卡；专家权重经 `symm_mem` 在 scale-up network 并行组内转移。
- **Prefill 参数**：每卡 4 冗余专家起步；统计窗 100 步，每 1000 步重排；线上 moe_lb = 1.0320（EP2/DP2）/ 1.0618（EP4/DP4）。
- **Decode 参数**：每卡 1 冗余专家起步（EP64 取整后每卡共 7 个专家，不含共享专家）；统计窗 1000 步，每 10000 步重排；线上 moe_lb = 1.090。

## 四、KVCache 存储（双轨）

### 4.1 双轨结构

| 轨道 | 存储 | 内容 | 生命周期 |
|---|---|---|---|
| **Block KVCache** | 独立 3FS 存储集群 | 128 token 一 block 分页；存 4 层 main KV + indexer K | agent TTL 3 天 / chatbot 7 天 |
| **SWA KVCache** | 产出它的机器内存（单副本） | 前 20 层各一个 134 token ring（窗口 128 + 投机回退 6） | TTL 约 180 秒，命中率 98%+ |

### 4.2 为什么 Block KVCache 落 3FS

- **容量**：3FS 为 KVCache 提供约 **100 PiB** SSD 存储；chatbot 长尾命中严重（少量 KVCache 极多次读取），3 天 TTL 会造成命中率下降 0.5%-1%；
- **带宽**：针对 KVCache block 粒度（约 112 KiB）随机读写优化，峰值聚合读带宽 **10 TiB/s**、写约 850 GiB/s；
- **解耦**：所有 prefill 机器能命中任何前缀（避免前缀亲和与负载均衡路由冲突）；存储与计算节点自动扩缩容解耦；KVCache 不受计算节点故障影响（计算节点故障率比存储高数量级以上）；
- **3FS 可靠性**：纠删码（10+2 EC）存放，每个 EC 组容忍 2 节点同时故障；读取同时向组内 11 台 Storage 节点发起请求，任意 10 个响应即可解码返回；GC Worker 按 LRU 周期淘汰最久未访问的 KVCache，磁盘占用控制在水位线以下。

### 4.3 命中路径三段（只有第一段在关键路径）

1. **匹配**：Entrypoint 在本机 CHECK 角色的 kvcache-store 上做哈希链前缀匹配，只查元数据（命中长度须在路由前计算，无法掩盖）；
2. **取 KV**：独立进程异步把 KVCache 从 3FS 搬进宿主机 shm；
3. **换入**：engine 进程内线程从 shm 到 HBM，目标是逐层 H2D 与前向计算重叠——由于 CUDA copy engine 对 block 细粒度拷贝性能不佳，换入用 **GDR**（GPUDirect RDMA）实现，用 RDMA 网卡打满 PCIe 带宽且不占 SM。

### 4.4 SWA KVCache 细节

- 逻辑统一、实际按 key 分散存放在各台 Entrypoint 上的**内存目录**记录位置，命中时本机没有就跨机取回（400G VLAN）；
- 只在 128 token 整数倍位置存储：prefill 结束后取序列末尾留一个 token 后向下对齐到 128 的位置；chunked prefill 中途不存、只有最后一个 chunk 才存；decode 在显存副本区每跨一个 128 边界拷贝一次，请求结束时从最近完成拷贝的位置存储（拷贝位置最多越界 5 token，由 ring 多出的 6 个位置吸收）；
- **命中原则**：命中长度由 Block KVCache 决定，最后一个 block 是否重算由 SWA KVCache 决定——SWA 未命中就退一块重算。输入长度 L 的最大命中长度为 L − 134（窗口 128 + 投机回退 6）；先查 Block 得 L1（128 整数倍），若 [L1−128, L1) 区间存在 SWA KVCache 则命中 L1，否则命中 L1−128。

## 五、SWA Bounded Replay（V4 → V4.1 的关键反转）

| 代际 | 方案 | 代价 |
|---|---|---|
| V4 | 落盘 + 精确重算：SWA KVCache 两处写入持久存储，未命中时重算"层数 × 窗口"个 token 完整前向逐层精确恢复 | SWA KVCache 占去持久 KVCache 近一半容量却只换分钟级复用收益；多轮短对话尤其不划算 |
| V4.1 | **SWA Bounded Replay**：只重算最近 128 token，注意力窗口截断在重算段内（位置 i 的 query 只和 max(s, i−127)～i 的 key 计算），近似恢复 | 重算代价降为与上下文长度和层数无关的**常数** |

> V4 技术报告提出的 Zero SWA Caching（完全不落盘、仅精确重算）因生产代价过高**未实际采用**——论文方案 ≠ 生产方案。

两处应用：

1. **Encoder SWA Bounded Replay**：前缀缓存命中长度从此只依赖 Block KVCache；SWA 缺失时重算命中前缀的最后 128 token 与未命中后缀一同前向；重算段只重建 SWA KVCache，Block KVCache 原样复用、不重算不覆写。
2. **Decoder SWA Bounded Replay**：prefill 计算仅在 encoder 层进行；CED 架构下 decoder 层 Block KVCache 由 encoder 末层 hidden state 投影得到，仅 decoder SWA KVCache 需各层自算——改为每次 prefill 在 decoder 层只重算 prompt 末尾 128 token（产出仅供 decode、不进前缀缓存），**总 prefill 计算量近乎减半**。

开源版对应开关：`DEEPINFER_YOCO_PREFILL_TRUNCATION_MODE=compact` + `DEEPINFER_YOCO_PREFILL_KEEP_TOKENS=140`（保留后缀须 ≥ SWA 窗口 + 最大回退长度）。

## 六、自动扩缩容与容错

- **扩缩容依据**：Prefill 按未命中 token 数、Decode 按在算请求数判断所需实例数；调整有限速与上下界。
- **长尾处理**：大 EP 部署下长尾请求导致资源浪费——decode 实例收到下线通知后进入 **1 分钟宽限期**，宽限期结束仍未完成的请求及其 KVCache 一次性全部转发给其他实例继续计算。
- **冗余配额**：①池子里留 ready 机器作为扩容库存；②永远比算出的需求多留实例在线——配额占用率高于 0.8 时禁止缩容。
- **容错**：错误重启在分钟量级，容错依赖"配额冗余 + 请求级重新路由"组合而非缩短重启时间。大 EP 部署下实例全部卡构成单一通信域，任一卡故障即整实例不可用；重启时按当前健康卡数重新确定 EP 大小，实例以实际拿到的卡数作为 EP 规模。

## 七、结构化输出的生产部署

- 编译阶段在**独立 SO 机器**上将格式约束编译为语法自动机；
- 运行时每步 decode 更新自动机、判断合法 token 集合、生成 mask 作用于采样；
- 编译与推理解耦，SO 编译异步进行，请求进入 engine 前取回编译结果。

> 开源版 DeepInfer 的 SO 实现见[结构化输出](structured-output.md)；本节补充的是生产侧"独立编译机器"的部署形态。
